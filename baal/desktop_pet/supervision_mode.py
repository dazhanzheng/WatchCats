"""
监督模式管理器
负责监控用户活动并在偏离目标时提醒
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from ..aw_stats.stats_processor import StatsProcessor
from ..llm_assistant.assistant import LLMAssistant
from .core.config_manager import ConfigManager
from .core.constants import SUPERVISION
import json
import logging

# 获取监督模式专用日志记录器
logger = logging.getLogger('supervision')


class SupervisionMode(QObject):
    """监督模式管理器
    
    定期检查用户活动，如果偏离设定目标则发出提醒
    """
    
    # 信号：需要提醒用户时发出
    reminder_needed = pyqtSignal(dict)  # 传递提醒信息
    # 信号：监督模式状态改变
    mode_changed = pyqtSignal(bool)  # True为开启，False为关闭
    
    def __init__(self, persona_manager=None):
        """初始化监督模式
        
        Args:
            persona_manager: 人设管理器实例（可选）
        """
        super().__init__()
        self.stats_processor = StatsProcessor()
        self.config_manager = ConfigManager()
        self.persona_manager = persona_manager  # 保存人设管理器引用
        
        # 初始化工作软件管理器
        try:
            from .core.category_manager import CategoryManager
            self.category_manager = CategoryManager()
            logger.info(f"工作软件管理器已初始化，加载了 {len(self.category_manager.get_work_apps())} 个工作软件")
        except Exception as e:
            logger.warning(f"无法初始化工作软件管理器: {e}")
            self.category_manager = None
        
        # 初始化LLM助手（需要配置）
        self.llm_assistant = None
        self._init_llm_assistant()
        
        self.is_active = False
        self.long_term_goal = ""  # 长期目标
        self.short_term_goals = []  # 短期目标列表
        self.check_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()  # 用于优雅停止线程
        self._goals_lock = threading.RLock()  # 用于保护目标数据的读写锁
        # 检查间隔（秒）- 可以通过环境变量调整，便于测试
        import os
        # 使用常量中的默认值，可通过环境变量覆盖
        self.check_interval = int(os.environ.get('SUPERVISION_CHECK_INTERVAL', str(SUPERVISION['default_check_interval'])))
        logger.info(f"监督模式检查间隔设置为 {self.check_interval} 秒")
        
        logger.debug("监督模式管理器初始化完成")
        self.last_check_time = None
        
        # 加载保存的监督设置
        self._load_supervision_settings()
    
    def _init_llm_assistant(self):
        """初始化LLM助手"""
        try:
            config = self.config_manager.get_config()
            if config.get('base_url') and config.get('api_key'):
                self.llm_assistant = LLMAssistant(
                    base_url=config['base_url'],
                    api_key=config['api_key'],
                    model=config.get('model', 'doubao-seed-1-6-flash-250715'),
                    parse_temperature=SUPERVISION['parse_temperature'],  # 解析温度保持低值，确保JSON格式正确
                    chat_temperature=SUPERVISION['chat_temperature'],   # 提高对话温度，生成更多样化的监督提醒
                    stats_processor=self.stats_processor
                )
                logger.info("LLM助手初始化成功（parse_temp=0.1, chat_temp=0.85）")
        except Exception as e:
            logger.error(f"初始化LLM助手失败: {e}")
            self.llm_assistant = None
    
    def __del__(self):
        """析构函数，确保线程被正确停止"""
        try:
            if self.is_active:
                self.stop_supervision()
        except:
            pass  # 忽略析构时的错误
    
    def _load_supervision_settings(self):
        """加载监督设置"""
        try:
            config_path = self.config_manager.config_dir / 'supervision.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    with self._goals_lock:
                        self.long_term_goal = data.get('long_term_goal', '')
                        self.short_term_goals = data.get('short_term_goals', [])
                    # 兼容旧版本数据
                    if 'goal' in data and not self.long_term_goal:
                        self.long_term_goal = data['goal']
                    if 'tasks' in data and not self.short_term_goals:
                        self.short_term_goals = data['tasks']
                    # 不自动恢复激活状态，需要用户手动开启
                    logger.debug(f"加载监督设置成功: 长期目标={self.long_term_goal}, 短期目标数={len(self.short_term_goals)}")
        except Exception as e:
            logger.warning(f"加载监督设置失败: {e}")
    
    def _save_supervision_settings(self):
        """保存监督设置"""
        try:
            config_path = self.config_manager.config_dir / 'supervision.json'
            with self._goals_lock:
                data = {
                    'long_term_goal': self.long_term_goal,
                    'short_term_goals': self.short_term_goals,
                    'updated_at': datetime.now().isoformat()
                }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logger.debug("监督设置已保存")
        except Exception as e:
            logger.error(f"保存监督设置失败: {e}")
    
    def start_supervision(self, long_term_goal: str = None, short_term_goals: list = None):
        """启动监督模式
        
        Args:
            long_term_goal: 长期目标描述（可选，不提供则使用已保存的）
            short_term_goals: 短期目标列表（可选，不提供则使用已保存的）
        """
        # 检查是否已配置LLM
        if not self.llm_assistant:
            # 尝试重新初始化LLM助手
            self._init_llm_assistant()
            
            # 如果仍然没有LLM助手，说明未配置API
            if not self.llm_assistant:
                logger.error("监督模式需要配置API密钥才能正常工作")
                return False  # 返回False表示启动失败
        
        # 如果提供了新的目标，更新它们
        with self._goals_lock:
            if long_term_goal is not None:
                self.long_term_goal = long_term_goal
            if short_term_goals is not None:
                self.short_term_goals = short_term_goals
        self.is_active = True
        self.last_check_time = datetime.now()
        
        # 保存设置
        self._save_supervision_settings()
        
        # 启动检查线程
        if self.check_thread is None or not self.check_thread.is_alive():
            self.check_thread = threading.Thread(target=self._check_loop, daemon=True)
            self.check_thread.start()
        
        self.mode_changed.emit(True)
        logger.info(f"监督模式已启动 - 长期目标: {self.long_term_goal}")
        logger.debug(f"短期目标: {self.short_term_goals}")
        return True
    
    def stop_supervision(self):
        """停止监督模式，确保正确清理资源（非阻塞）"""
        self.is_active = False
        self._stop_event.set()  # 设置停止事件
        
        # 使用非阻塞方式处理线程结束
        if self.check_thread and self.check_thread.is_alive():
            logger.info("发送停止信号给监督线程...")
            # 启动一个独立线程来清理，避免阻塞UI
            import threading
            def cleanup_thread():
                try:
                    # 给线程一个短暂的时间来自然结束
                    self.check_thread.join(timeout=0.5)  # 只等待0.5秒
                    if self.check_thread.is_alive():
                        logger.info("监督线程仍在运行，将在后台清理")
                    else:
                        logger.info("监督线程已成功结束")
                except Exception as e:
                    logger.error(f"清理监督线程时出错: {e}")
            
            cleanup = threading.Thread(target=cleanup_thread, daemon=True)
            cleanup.start()
        
        # 立即清理线程引用和重置状态
        self.check_thread = None
        self._stop_event.clear()  # 重置事件，为下次使用准备
        
        self.mode_changed.emit(False)
        logger.info("监督模式已停止（非阻塞）")
    
    def _check_loop(self):
        """检查循环，使用短间隔事件检查机制以实现快速响应"""
        logger.info(f"检查线程已启动，每{self.check_interval}秒检查一次")
        
        # 首次启动后立即进行一次检查（可选，用于测试）
        # 如果不想立即检查，可以注释掉这部分
        if self.is_active:
            logger.debug("执行首次检查...")
            try:
                self._check_activity()
            except Exception as e:
                logger.error(f"首次检查出错: {e}")
        
        # 记录下次检查时间
        next_check_time = time.time() + self.check_interval
        
        while self.is_active:
            # 使用短间隔检查，以便快速响应停止信号
            # 每0.1秒检查一次停止事件，但只在到达检查间隔时执行实际检查
            if self._stop_event.wait(timeout=0.1):  # 0.1秒的短间隔
                # 如果事件被设置，说明需要停止
                logger.info("收到停止信号，检查线程立即退出")
                return
            
            if not self.is_active:
                logger.info("检测到is_active=False，退出检查循环")
                break
            
            # 检查是否到达下次检查时间
            current_time = time.time()
            if current_time >= next_check_time:
                logger.debug(f"执行定期检查... (时间: {datetime.now().strftime('%H:%M:%S')})")
                try:
                    # 在执行检查前再次确认是否应该继续
                    if not self.is_active or self._stop_event.is_set():
                        logger.info("检查被取消，监督模式正在停止")
                        break
                    
                    self._check_activity()
                    # 更新下次检查时间
                    next_check_time = current_time + self.check_interval
                except Exception as e:
                    logger.error(f"检查活动时出错: {e}")
                    # 出错后也要更新下次检查时间
                    next_check_time = current_time + self.check_interval
        
        logger.info("检查循环已退出")
    
    def _check_activity(self):
        """检查用户活动是否符合目标（带中断检查）"""
        # 检查是否应该继续
        if not self.is_active or self._stop_event.is_set():
            logger.info("检查活动被中断，监督模式正在停止")
            return
        
        # 获取过去5分钟的活动数据
        current_time = datetime.now()
        logger.info(f"开始检查活动... (时间: {current_time.strftime('%H:%M:%S')})")
        
        # 首先检查AFK状态
        if self._is_user_afk():
            logger.debug("用户处于AFK状态，跳过监督检查")
            self.last_check_time = current_time
            return
        
        # 在获取统计前再次检查
        if not self.is_active or self._stop_event.is_set():
            logger.info("统计获取前检测到停止信号")
            return
        
        logger.debug("用户活跃，获取活动统计...")
        # 获取多时段的活动统计
        stats = self._get_comprehensive_activity_stats()
        
        # 在评估前再次检查
        if not self.is_active or self._stop_event.is_set():
            logger.info("评估前检测到停止信号")
            return
        
        if stats:
            logger.debug(f"统计数据获取成功: {list(stats.keys())}")
            # 使用增强的LLM评估
            evaluation_result = self._evaluate_activity_enhanced(stats)
            
            # 在发送提醒前最后一次检查
            if not self.is_active or self._stop_event.is_set():
                logger.info("发送提醒前检测到停止信号")
                return
            
            if evaluation_result:
                logger.info(f"评估结果: should_remind={evaluation_result.get('should_remind')}, "
                      f"deviation_level={evaluation_result.get('deviation_level', '未知')}")
                
                if evaluation_result.get('should_remind'):
                    logger.warning("需要提醒用户！")
                    # 生成增强的提醒内容
                    reminder_context = self._create_enhanced_reminder_context(stats, evaluation_result)
                    # 最终检查
                    if self.is_active and not self._stop_event.is_set():
                        self.reminder_needed.emit(reminder_context)
                        logger.debug(f"提醒内容: {reminder_context.get('message', '')[:100]}...")
                    else:
                        logger.info("提醒被取消，监督模式已停止")
                else:
                    logger.info("用户活动符合目标，无需提醒")
            else:
                logger.warning("评估结果为空")
        else:
            logger.error("无法获取统计数据")
        
        self.last_check_time = current_time
    
    def _is_user_afk(self) -> bool:
        """检查用户是否处于持续AFK状态
        
        判断标准:
        1. 使用ActivityWatch的AFK监视器数据
        2. 检查用户是否持续AFK超过4分钟
        3. 或者用户在过去5分钟内的总AFK时间超过4分钟且最近是AFK状态
        
        Returns:
            True如果用户持续AFK，False否则
        """
        try:
            with self.stats_processor as sp:
                # 获取AFK统计
                afk_stats = sp.get_afk_time_5m()
                
                if not afk_stats:
                    logger.warning("AFK统计数据为空")
                    return False
                
                # 获取各项指标
                afk_seconds = afk_stats.get('afk_seconds', 0)
                continuous_afk = afk_stats.get('continuous_afk', False)
                last_active_seconds = afk_stats.get('last_active_seconds_ago', 0)
                
                # 判断是否持续AFK
                # 条件1: 明确标记为持续AFK
                # 条件2: 距离最后一次活动超过4分钟
                # 条件3: 总AFK时间超过4.5分钟（给予一定容错）
                is_afk = continuous_afk or last_active_seconds > 240 or afk_seconds > 270
                
                logger.info(f"AFK检查结果: afk_seconds={afk_seconds:.1f}s, "
                          f"continuous_afk={continuous_afk}, "
                          f"last_active={last_active_seconds:.1f}s ago, "
                          f"is_afk={is_afk}")
                
                return is_afk
        except Exception as e:
            logger.error(f"检查AFK状态失败: {e}", exc_info=True)
            return False
    
    def _get_comprehensive_activity_stats(self) -> Dict[str, Any]:
        """获取多时段的综合活动统计（可中断）
        
        Returns:
            包含5分钟、2小时和24小时活动统计的字典
        """
        try:
            with self.stats_processor as sp:
                logger.info("开始获取多时段活动统计...")
                
                # 检查是否应该继续
                if not self.is_active or self._stop_event.is_set():
                    logger.info("统计获取被中断")
                    return {}
                
                # 5分钟数据
                stats_5m = sp.get_stats_5m()
                logger.debug(f"✓ 5分钟数据获取成功 (长度: {len(stats_5m)} 字符)")
                
                # 检查是否应该继续
                if not self.is_active or self._stop_event.is_set():
                    logger.info("统计获取被中断")
                    return {}
                
                # 2小时数据
                stats_2h = sp.get_stats_2h()
                logger.debug(f"✓ 2小时数据获取成功 (长度: {len(stats_2h)} 字符)")
                
                # 检查是否应该继续
                if not self.is_active or self._stop_event.is_set():
                    logger.info("统计获取被中断")
                    return {}
                
                # 24小时数据（获取今日数据作为24小时数据）
                stats_24h = sp.get_stats_today()
                logger.debug(f"✓ 24小时数据获取成功 (长度: {len(stats_24h)} 字符)")
                
                # 额外获取精确的过去24小时数据
                try:
                    if self.is_active and not self._stop_event.is_set():
                        stats_last_24h = sp.get_detailed_stats(24)
                        logger.debug(f"✓ 精确24小时数据获取成功 (长度: {len(stats_last_24h)} 字符)")
                    else:
                        stats_last_24h = stats_24h
                except:
                    stats_last_24h = stats_24h  # 如果失败，使用今日数据作为备份
                
                # 获取分类统计和生产力分析
                category_stats = {}
                productivity_analysis = {}
                try:
                    if self.is_active and not self._stop_event.is_set():
                        # 获取2小时的分类统计
                        cat_stats = sp.get_category_stats(2)
                        if cat_stats and cat_stats.get('categories'):
                            top_categories = cat_stats['categories'][:5]  # 前5个分类
                            category_summary = "主要活动分类: " + ", ".join([
                                f"{cat['name']}({cat['duration_str']})"
                                for cat in top_categories
                            ])
                            category_stats['summary'] = category_summary
                            category_stats['details'] = cat_stats
                            logger.debug(f"✓ 分类统计获取成功")
                        
                        # 获取生产力分析
                        prod_stats = sp.get_productive_vs_unproductive_stats(2)
                        if prod_stats:
                            productivity_analysis = prod_stats
                            logger.debug(f"✓ 生产力分析获取成功: {prod_stats['productive_percentage']:.1f}%生产性活动")
                except Exception as e:
                    logger.warning(f"获取分类统计失败: {e}")
                
                result = {
                    'stats_5m': stats_5m,
                    'stats_2h': stats_2h,
                    'stats_today': stats_24h,  # 今日数据（从凌晨4点）
                    'stats_24h': stats_last_24h,  # 过去24小时数据
                    'category_stats': category_stats,  # 分类统计
                    'productivity_analysis': productivity_analysis,  # 生产力分析
                    'timestamp': datetime.now().isoformat()
                }
                
                logger.info("✓ 所有时段数据获取完成")
                return result
                
        except Exception as e:
            logger.error(f"获取综合活动统计失败: {e}", exc_info=True)
            return {}
    
    def _get_recent_activity_stats(self) -> Dict[str, Any]:
        """获取最近的活动统计
        
        Returns:
            活动统计数据
        """
        try:
            # 使用 StatsProcessor 的实际方法获取过去5分钟的详细活动
            with self.stats_processor as sp:
                raw_stats = sp.get_stats_5m()  # 使用实际存在的方法
            
            # 解析返回的字符串格式数据
            lines = raw_stats.split('\n')
            top_apps = []
            
            # 简单解析应用列表
            for line in lines:
                if '.' in line and '（' in line and '）' in line:
                    # 尝试解析格式如: "1. AppName（5分钟，占比70%）"
                    try:
                        parts = line.split('.')
                        if len(parts) >= 2:
                            app_part = parts[1].strip()
                            app_name = app_part.split('（')[0].strip()
                            if app_name:
                                top_apps.append(app_name)
                    except:
                        pass
            
            # 返回简化的统计信息
            simplified_stats = {
                'total_time': 300,  # 5分钟 = 300秒
                'top_applications': top_apps[:3],  # 前3个应用
                'raw_stats': raw_stats  # 保留原始数据以供参考
            }
            
            return simplified_stats
        except Exception as e:
            print(f"获取活动统计失败: {e}")
            return {}
    
    def _evaluate_activity_enhanced(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """增强的活动评估，包括提醒建议
        
        Args:
            stats: 综合活动统计数据
            
        Returns:
            包含评估结果和提醒建议的字典
        """
        # 必须有LLM助手才能进行评估
        if not self.llm_assistant:
            logger.warning("监督模式需要配置LLM才能正常工作")
            return None
        
        try:
            # 获取当前人设
            if self.persona_manager:
                current_persona = self.persona_manager.get_current_persona_info()
            else:
                # 如果没有人设管理器，使用默认值
                current_persona = {
                    'name': '严厉主人',
                    'description': '巴利是用户的主人，拥有绝对支配权'
                }
            
            # 准备各时段数据（限制长度但保留关键信息）
            stats_5m = stats.get('stats_5m', '无数据')
            stats_2h = stats.get('stats_2h', '无数据')
            stats_24h = stats.get('stats_24h', stats.get('stats_today', '无数据'))  # 优先使用24小时，其次今日
            
            # 智能截断：保留前1000字符（通常包含最重要的应用信息）
            if len(stats_5m) > 1000:
                stats_5m = stats_5m[:1000] + "...(数据已截断)"
            if len(stats_2h) > 1000:
                stats_2h = stats_2h[:1000] + "...(数据已截断)"
            if len(stats_24h) > 1000:
                stats_24h = stats_24h[:1000] + "...(数据已截断)"
            
            # 数据准备完成
            
            # 安全地读取目标数据（创建快照，避免在评估过程中被修改）
            with self._goals_lock:
                current_long_term_goal = self.long_term_goal
                current_short_term_goals = self.short_term_goals.copy()  # 复制列表避免修改
            
            # 生成随机元素增加多样性
            import random
            time_of_day = datetime.now().hour
            time_period = "深夜" if time_of_day < 6 else "早晨" if time_of_day < 12 else "下午" if time_of_day < 18 else "晚上"
            
            # 获取生产力数据用于更精准的评估
            productivity_data = stats.get('productivity_analysis', {})
            productive_percentage = productivity_data.get('productive_percentage', 0)
            category_data = stats.get('category_stats', {})
            
            # 提取当前使用的工作软件列表（重要：用于判断是否在工作）
            work_apps_in_use = []
            if hasattr(self, 'category_manager') and self.category_manager:
                work_apps_list = self.category_manager.get_work_apps()
                # 从5分钟数据中提取正在使用的工作软件
                if stats_5m and work_apps_list:
                    for work_app in work_apps_list:
                        if work_app.lower() in stats_5m.lower():
                            work_apps_in_use.append(work_app)
            
            # 【关键优化】：如果检测到工作软件或生产力高，直接返回不提醒
            if work_apps_in_use or productive_percentage > 50:
                logger.info(f"用户正在使用工作软件 {work_apps_in_use} 或生产力较高 {productive_percentage:.1f}%，不需要提醒")
                return {
                    'should_remind': False,
                    'deviation_level': '无',
                    'reminder_message': '',
                    'analysis': f'用户正在使用工作软件或保持较高生产力（{productive_percentage:.1f}%），无需打扰'
                }
            
            # 随机选择一种对话风格
            dialog_styles = [
                "直接对话",  # 直接和用户说话
                "自言自语",  # 巴利自言自语，假装用户听不到
                "内心独白",  # 巴利的内心想法
                "旁白叙述",  # 像旁白一样描述状况
                "反问质疑",  # 用反问句表达
            ]
            chosen_style = random.choice(dialog_styles)
            
            # 构建增强的评估提示
            prompt = f"""你是巴利（Baal），一只监督用户生产力的黑猫恶魔宠物。现在是{time_period}。
当前人设：{current_persona['name']} - {current_persona['description']}

用户目标：
长期：{current_long_term_goal if current_long_term_goal else '无'}
今日任务：{current_short_term_goals if current_short_term_goals else ['无']}

活动数据：
5分钟：{stats_5m}
2小时：{stats_2h}
24小时：{stats_24h}

分类分析：
{stats.get('category_stats', {}).get('summary', '暂无分类数据')}

生产力评估：
{stats.get('productivity_analysis', {}).get('analysis', '暂无生产力数据')}
生产性活动占比：{stats.get('productivity_analysis', {}).get('productive_percentage', 0):.1f}%

【创作指南】
你需要像一个真实的、有个性的宠物那样说话，而不是机器人。这次使用"{chosen_style}"风格。

风格示例：
- 直接对话："喂！你在干什么呢？飞书聊了2小时了，工作呢？"
- 自言自语："唉，这家伙又在摸鱼了...算了，我只是只猫，管不了那么多..."
- 内心独白："（看着屏幕上的飞书）...我就知道会这样，每次都是这样..."
- 旁白叙述："于是，在这个{time_period}，某人又一次背叛了自己的承诺..."
- 反问质疑："所以你觉得刷2小时飞书能写完代码？嗯？"

【重要】生成提醒时：
1. 不要使用"您"这种敬语，根据人设用"你"或其他称呼
2. 可以用省略号、感叹号、问号来表达情绪
3. 可以用一些口语化表达，如"啧啧"、"哎呀"、"算了吧"、"得了吧"
4. 严厉主人可以用命令句："立刻关掉飞书！"、"马上去工作！"
5. 毒舌管家可以阴阳怪气："哦，原来飞书是新的IDE啊～"
6. 温柔伴侣可以委婉关心："要不要休息一下眼睛，然后回到工作上呢？"
7. 可以提到具体时间和应用，但要自然融入对话
8. 偶尔可以不提具体数字，用更生动的描述
9. 可以根据时间段调整语气（深夜更温柔、早晨更有活力等）
10. 表情标记：<#1>开心 <#2>得意 <#3>无语 <#4>鄙视 <#5>平静 <#6>生气 <#7>暴怒

【多样化技巧】
- 可以从不同角度切入（健康、效率、承诺、时间价值等）
- 可以用比喻（"像冰淇淋在太阳下融化"、"时间像沙子从指缝溜走"）
- 可以引用之前的表现（"昨天你还说要改变的"）
- 可以预测后果（"这样下去deadline要来不及了"）
- 可以用幽默化解（但要符合人设）

返回JSON格式：
{{
    "should_remind": true/false,
    "deviation_level": "严重/中度/轻微/无",
    "reminder_message": "你的提醒内容（自然、口语化、有个性）",
    "analysis": "内部分析（不显示给用户）",
    "time_period_analysis": {{
        "5m": "简短分析",
        "2h": "简短分析",
        "24h": "简短分析"
    }}
}}

【极其重要的判断标准】：
1. **工作软件优先原则**：如果用户正在使用任何已配置的工作软件（{', '.join(work_apps_in_use) if work_apps_in_use else '检测到工作软件'}），则**绝对不应该提醒或批评**，应该鼓励或保持安静
2. **目标匹配原则**：
   - 短期目标只需执行其中**任何一个**即可，不要求同时执行所有
   - 例如：短期目标是["写代码", "看文档", "学习"]，用户只要在做其中任一件事就不应该被批评
   - 长期目标相关的活动也应该被认可
3. **生产力百分比原则**：如果生产性活动占比超过50%，不应该批评
4. **避免错误批评**：
   - 如果用户在使用VSCode、PyCharm、飞书、钉钉等工作软件，**必须判定为不需要提醒**
   - 如果5分钟数据显示主要是工作相关应用，**必须判定为不需要提醒**
   - 宁可不提醒，也不要错误批评正在工作的用户
5. **改善趋势原则**：如果用户从非生产性活动转向生产性活动，应该鼓励而不是批评
6. **避免频繁打扰**：避免5分钟内重复提醒

【判断流程】：
1. 首先检查是否在使用工作软件 → 是 → 不提醒（可以鼓励）
2. 其次检查是否在执行任一短期目标 → 是 → 不提醒
3. 再检查生产力百分比 → >50% → 不提醒
4. 最后才考虑是否需要提醒

当前检测到的工作软件使用：{work_apps_in_use if work_apps_in_use else '未检测到明确的工作软件'}
生产力百分比：{productive_percentage:.1f}%

【重要提醒】：
- 如果不确定用户是否在工作，选择不提醒
- 如果用户可能在工作但使用了非典型工具，选择不提醒
- 保护用户的专注状态比监督更重要
"""
            
            # 发送评估请求
            # 使用LLM评估
            response = self.llm_assistant.chat(prompt)
            # 收到LLM响应
            
            # 解析JSON响应
            import json
            # 尝试提取JSON部分
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                result = json.loads(json_str)
                
                # 记录评估结果
                logger.info(f"LLM评估完成: should_remind={result.get('should_remind')}, "
                          f"deviation_level={result.get('deviation_level', '未知')}")
                if result.get('time_period_analysis'):
                    logger.debug(f"时段分析: {result['time_period_analysis']}")
                
                return result
            else:
                logger.warning("无法从LLM响应中解析JSON")
                # 如果无法解析JSON，默认不提醒
                return {'should_remind': False}
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析错误: {e}")
            return {'should_remind': False}
        except Exception as e:
            logger.error(f"增强评估活动时出错: {e}", exc_info=True)
            return None
    
    def _evaluate_activity(self, stats: Dict[str, Any]) -> bool:
        """评估活动是否符合目标
        
        Args:
            stats: 活动统计数据
            
        Returns:
            True如果活动符合目标，False如果偏离
        """
        # 必须有LLM助手才能进行评估
        if not self.llm_assistant:
            print("警告：监督模式需要配置LLM才能正常工作")
            # 没有LLM时默认不打扰用户
            return True
        
        try:
            # 构建评估提示
            top_apps = stats.get('top_applications', [])
            apps_str = ', '.join(top_apps) if top_apps else '无应用数据'
            
            prompt = f"""请判断用户的电脑使用情况是否符合其设定的目标。

用户的长期目标：{self.long_term_goal}
用户的短期目标：{', '.join(self.short_term_goals) if self.short_term_goals else '未设定'}

过去5分钟的使用情况：
- 总使用时间：{stats.get('total_time', 0)}秒
- 主要使用的应用：{apps_str}

原始活动数据：
{stats.get('raw_stats', '无数据')[:500]}  # 限制长度

请回答：用户的活动是否基本符合目标？
如果用户在做与目标相关的事情，回答"是"。
如果用户明显在做与目标无关的事情（如看视频、玩游戏、浏览社交媒体等），回答"否"。

只回答"是"或"否"。"""
            
            # 使用LLM判断
            response = self.llm_assistant.chat(prompt)
            
            # 简单判断回复
            return "是" in response or "符合" in response or "yes" in response.lower()
            
        except Exception as e:
            print(f"评估活动时出错: {e}")
            # 出错时默认不打扰用户
            return True
    
    def _create_enhanced_reminder_context(self, stats: Dict[str, Any], evaluation: Dict[str, Any]) -> Dict[str, Any]:
        """创建增强的提醒上下文
        
        Args:
            stats: 活动统计数据
            evaluation: LLM评估结果
            
        Returns:
            增强的提醒上下文字典
        """
        # 如果没有LLM生成的消息，使用预设反应管理器生成后备消息
        reminder_message = evaluation.get('reminder_message')
        deviation_level = evaluation.get('deviation_level', '中度')
        
        if not reminder_message:
            # 获取当前人设并生成合适的提醒
            try:
                from .core.preset_responses import PresetResponseManager
                if self.persona_manager:
                    reminder_message = PresetResponseManager.get_supervision_reminder(
                        self.persona_manager.current_level,
                        deviation_level
                    )
                else:
                    # 使用默认人设
                    from .core.persona_manager import PersonaLevel
                    reminder_message = PresetResponseManager.get_supervision_reminder(
                        PersonaLevel.STRICT_MASTER,
                        deviation_level
                    )
            except:
                # 如果无法加载预设反应，使用默认消息
                reminder_message = '你似乎偏离了目标，请回到正轨。'
        
        return {
            'type': 'supervision_reminder',
            'long_term_goal': self.long_term_goal,
            'short_term_goals': self.short_term_goals,
            'activity_stats': stats,
            'evaluation': evaluation,
            'reminder_message': reminder_message,
            'deviation_level': deviation_level,
            'timestamp': datetime.now().isoformat()
        }
    
    def _create_reminder_context(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """创建提醒上下文
        
        Args:
            stats: 活动统计数据
            
        Returns:
            提醒上下文字典
        """
        return {
            'type': 'supervision_reminder',
            'long_term_goal': self.long_term_goal,
            'short_term_goals': self.short_term_goals,
            'activity_stats': stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取监督模式状态"""
        with self._goals_lock:
            return {
                'is_active': self.is_active,
                'long_term_goal': self.long_term_goal,
                'short_term_goals': self.short_term_goals.copy(),  # 返回副本
                'last_check': self.last_check_time.isoformat() if self.last_check_time else None
            }
    
    def update_goals(self, long_term_goal: str, short_term_goals: list):
        """更新监督目标（可在监督运行时使用）"""
        with self._goals_lock:
            self.long_term_goal = long_term_goal
            self.short_term_goals = short_term_goals
            self._save_supervision_settings()
            logger.info(f"监督目标已更新 - 长期目标: {long_term_goal[:50] if len(long_term_goal) > 50 else long_term_goal}...")
            logger.debug(f"短期目标: {short_term_goals}")