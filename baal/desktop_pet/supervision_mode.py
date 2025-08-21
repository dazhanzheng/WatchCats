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
        
        # 初始化LLM助手（需要配置）
        self.llm_assistant = None
        self._init_llm_assistant()
        
        self.is_active = False
        self.long_term_goal = ""  # 长期目标
        self.short_term_goals = []  # 短期目标列表
        self.check_thread: Optional[threading.Thread] = None
        # 检查间隔（秒）- 可以通过环境变量调整，便于测试
        import os
        # 默认5分钟（300秒），可通过环境变量调整
        self.check_interval = int(os.environ.get('SUPERVISION_CHECK_INTERVAL', '300'))  # 生产环境：5分钟
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
                    parse_temperature=0.1,  # 解析温度保持低值，确保JSON格式正确
                    chat_temperature=0.85,   # 提高对话温度，生成更多样化的监督提醒
                    stats_processor=self.stats_processor
                )
                logger.info("LLM助手初始化成功（parse_temp=0.1, chat_temp=0.85）")
        except Exception as e:
            logger.error(f"初始化LLM助手失败: {e}")
            self.llm_assistant = None
    
    def _load_supervision_settings(self):
        """加载监督设置"""
        try:
            config_path = self.config_manager.config_dir / 'supervision.json'
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
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
        """停止监督模式"""
        self.is_active = False
        self.mode_changed.emit(False)
        logger.info("监督模式已停止")
    
    def _check_loop(self):
        """检查循环"""
        logger.info(f"检查线程已启动，每{self.check_interval}秒检查一次")
        
        # 首次启动后立即进行一次检查（可选，用于测试）
        # 如果不想立即检查，可以注释掉这部分
        if self.is_active:
            logger.debug("执行首次检查...")
            try:
                self._check_activity()
            except Exception as e:
                logger.error(f"首次检查出错: {e}")
        
        while self.is_active:
            # 等待指定间隔
            for i in range(self.check_interval):
                if not self.is_active:
                    logger.info("检查线程已停止")
                    return
                time.sleep(1)
            
            if not self.is_active:
                break
            
            logger.debug(f"执行定期检查... (时间: {datetime.now().strftime('%H:%M:%S')})")
            try:
                self._check_activity()
            except Exception as e:
                logger.error(f"检查活动时出错: {e}")
        
        logger.info("检查循环已退出")
    
    def _check_activity(self):
        """检查用户活动是否符合目标"""
        # 获取过去5分钟的活动数据
        current_time = datetime.now()
        logger.info(f"开始检查活动... (时间: {current_time.strftime('%H:%M:%S')})")
        
        # 首先检查AFK状态
        if self._is_user_afk():
            logger.debug("用户处于AFK状态，跳过监督检查")
            self.last_check_time = current_time
            return
        
        logger.debug("用户活跃，获取活动统计...")
        # 获取多时段的活动统计
        stats = self._get_comprehensive_activity_stats()
        
        if stats:
            logger.debug(f"统计数据获取成功: {list(stats.keys())}")
            # 使用增强的LLM评估
            evaluation_result = self._evaluate_activity_enhanced(stats)
            
            if evaluation_result:
                logger.info(f"评估结果: should_remind={evaluation_result.get('should_remind')}, "
                      f"deviation_level={evaluation_result.get('deviation_level', '未知')}")
                
                if evaluation_result.get('should_remind'):
                    logger.warning("需要提醒用户！")
                    # 生成增强的提醒内容
                    reminder_context = self._create_enhanced_reminder_context(stats, evaluation_result)
                    self.reminder_needed.emit(reminder_context)
                    logger.debug(f"提醒内容: {reminder_context.get('message', '')[:100]}...")
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
        """获取多时段的综合活动统计
        
        Returns:
            包含5分钟、2小时和24小时活动统计的字典
        """
        try:
            with self.stats_processor as sp:
                logger.info("开始获取多时段活动统计...")
                
                # 5分钟数据
                stats_5m = sp.get_stats_5m()
                logger.debug(f"✓ 5分钟数据获取成功 (长度: {len(stats_5m)} 字符)")
                
                # 2小时数据
                stats_2h = sp.get_stats_2h()
                logger.debug(f"✓ 2小时数据获取成功 (长度: {len(stats_2h)} 字符)")
                
                # 24小时数据（获取今日数据作为24小时数据）
                stats_24h = sp.get_stats_today()
                logger.debug(f"✓ 24小时数据获取成功 (长度: {len(stats_24h)} 字符)")
                
                # 额外获取精确的过去24小时数据
                try:
                    stats_last_24h = sp.get_detailed_stats(24)
                    logger.debug(f"✓ 精确24小时数据获取成功 (长度: {len(stats_last_24h)} 字符)")
                except:
                    stats_last_24h = stats_24h  # 如果失败，使用今日数据作为备份
                
                result = {
                    'stats_5m': stats_5m,
                    'stats_2h': stats_2h,
                    'stats_today': stats_24h,  # 今日数据（从凌晨4点）
                    'stats_24h': stats_last_24h,  # 过去24小时数据
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
            
            # 构建增强的评估提示
            prompt = f"""你是巴利（Baal），一个监督用户生产力的桌面宠物助手。
当前人设模式：{current_persona['name']}
人设特点：{current_persona['description']}

用户设定的目标：
长期目标：{self.long_term_goal if self.long_term_goal else '未设定'}
短期目标：{', '.join(self.short_term_goals) if self.short_term_goals else '未设定'}

用户的电脑使用情况（多时段综合分析）：

【过去5分钟 - 即时行为】
{stats_5m}

【过去2小时 - 短期趋势】
{stats_2h}

【过去24小时 - 整体表现】
{stats_24h}

请综合分析以上三个时段的数据：
1. 5分钟数据反映用户当前正在做什么
2. 2小时数据显示短期行为模式
3. 24小时数据展示整体生产力状况

【重要】分析时请注意数据中的绝对值（如"2小时30分"）和相对值（如"占比70%"），两者都要在提醒中体现。

根据分析结果，按照以下JSON格式回答：
{{
    "should_remind": true或false（是否需要提醒用户）,
    "deviation_level": "严重"或"中度"或"轻微"或"无"（偏离程度）,
    "reminder_message": "根据人设特点的提醒内容，使用中文",
    "analysis": "简短的分析说明，包含对三个时段数据的综合判断",
    "time_period_analysis": {{
        "5m": "5分钟行为分析",
        "2h": "2小时趋势分析", 
        "24h": "24小时整体分析"
    }}
}}

生成reminder_message的要求：
1. 必须符合当前人设的语言风格和性格特点
2. 要自然、多样化，避免格式化的表达
3. 同时提及具体时长（绝对值）和占比（相对值），如"你已经在飞书上浪费了2小时（占今天的80%）"
4. 可以引用不同时段的对比，如"虽然过去5分钟在工作，但2小时内你有1.5小时在摸鱼"
5. 根据偏离程度调整语气强度：
   - 严重：强烈批评/命令（严厉主人）、尖锐讽刺（毒舌管家）、担忧焦虑（温柔伴侣）
   - 中度：警告提醒（严厉主人）、嘲讽暗示（毒舌管家）、温和提醒（温柔伴侣）
   - 轻微：冷淡提示（严厉主人）、轻微调侃（毒舌管家）、鼓励支持（温柔伴侣）
6. 每次的表达方式要不同，可以用不同的角度、比喻、语气变化
7. 可以具体指出问题应用和建议应用，如"关掉飞书，打开VS Code"
8. 表情标记要与情绪匹配：<#1>开心 <#2>得意 <#3>无语 <#4>鄙视 <#5>平静 <#6>生气 <#7>暴怒

决策规则：
1. 如果5分钟数据显示用户正在做与目标相关的事情，即使2小时或24小时有偏离，也不要立即提醒
2. 如果5分钟和2小时都显示偏离，应该提醒
3. 如果只是24小时整体偏离但当前正在改善，给予鼓励而非批评
4. 提醒内容必须符合当前人设的语言风格
5. 避免过于频繁的提醒，只在明显偏离时才提醒
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
        return {
            'is_active': self.is_active,
            'long_term_goal': self.long_term_goal,
            'short_term_goals': self.short_term_goals,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None
        }
    
    def update_goals(self, long_term_goal: str, short_term_goals: list):
        """更新监督目标（不重启监督）"""
        self.long_term_goal = long_term_goal
        self.short_term_goals = short_term_goals
        self._save_supervision_settings()
        print(f"监督目标已更新: {long_term_goal}")