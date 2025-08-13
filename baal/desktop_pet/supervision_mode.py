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


class SupervisionMode(QObject):
    """监督模式管理器
    
    定期检查用户活动，如果偏离设定目标则发出提醒
    """
    
    # 信号：需要提醒用户时发出
    reminder_needed = pyqtSignal(dict)  # 传递提醒信息
    # 信号：监督模式状态改变
    mode_changed = pyqtSignal(bool)  # True为开启，False为关闭
    
    def __init__(self):
        """初始化监督模式"""
        super().__init__()
        self.stats_processor = StatsProcessor()
        self.config_manager = ConfigManager()
        
        # 初始化LLM助手（需要配置）
        self.llm_assistant = None
        self._init_llm_assistant()
        
        self.is_active = False
        self.long_term_goal = ""  # 长期目标
        self.short_term_goals = []  # 短期目标列表
        self.check_thread: Optional[threading.Thread] = None
        # 检查间隔（秒）- 可以通过环境变量调整，便于测试
        import os
        self.check_interval = int(os.environ.get('SUPERVISION_CHECK_INTERVAL', '300'))  # 默认5分钟
        if self.check_interval != 300:
            print(f"[监督模式] 检查间隔设置为 {self.check_interval} 秒")
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
                    model=config.get('model', 'deepseek-v3-250324'),
                    temperature=0.1,
                    stats_processor=self.stats_processor
                )
        except Exception as e:
            print(f"初始化LLM助手失败: {e}")
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
        except Exception as e:
            print(f"加载监督设置失败: {e}")
    
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
        except Exception as e:
            print(f"保存监督设置失败: {e}")
    
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
                print("错误：监督模式需要配置API密钥才能正常工作")
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
        print(f"监督模式已启动 - 长期目标: {self.long_term_goal}")
        return True
    
    def stop_supervision(self):
        """停止监督模式"""
        self.is_active = False
        self.mode_changed.emit(False)
        print("监督模式已停止")
    
    def _check_loop(self):
        """检查循环"""
        print(f"[监督模式] 检查线程已启动，每{self.check_interval}秒检查一次")
        
        # 首次启动后立即进行一次检查（可选，用于测试）
        # 如果不想立即检查，可以注释掉这部分
        if self.is_active:
            print("[监督模式] 执行首次检查...")
            try:
                self._check_activity()
            except Exception as e:
                print(f"[监督模式] 首次检查出错: {e}")
        
        while self.is_active:
            # 等待指定间隔
            for i in range(self.check_interval):
                if not self.is_active:
                    print("[监督模式] 检查线程已停止")
                    return
                time.sleep(1)
            
            if not self.is_active:
                break
            
            print(f"[监督模式] 执行定期检查... (时间: {datetime.now().strftime('%H:%M:%S')})")
            try:
                self._check_activity()
            except Exception as e:
                print(f"[监督模式] 检查活动时出错: {e}")
        
        print("[监督模式] 检查循环已退出")
    
    def _check_activity(self):
        """检查用户活动是否符合目标"""
        # 获取过去5分钟的活动数据
        current_time = datetime.now()
        print(f"[监督模式] 开始检查活动... (时间: {current_time.strftime('%H:%M:%S')})")
        
        # 首先检查AFK状态
        if self._is_user_afk():
            print("[监督模式] 用户处于AFK状态，跳过监督检查")
            self.last_check_time = current_time
            return
        
        print("[监督模式] 用户活跃，获取活动统计...")
        # 获取多时段的活动统计
        stats = self._get_comprehensive_activity_stats()
        
        if stats:
            print("[监督模式] 统计数据获取成功，进行LLM评估...")
            # 使用增强的LLM评估
            evaluation_result = self._evaluate_activity_enhanced(stats)
            
            if evaluation_result:
                print(f"[监督模式] 评估结果: should_remind={evaluation_result.get('should_remind')}, "
                      f"deviation_level={evaluation_result.get('deviation_level', '未知')}")
                
                if evaluation_result.get('should_remind'):
                    print("[监督模式] 需要提醒用户！")
                    # 生成增强的提醒内容
                    reminder_context = self._create_enhanced_reminder_context(stats, evaluation_result)
                    self.reminder_needed.emit(reminder_context)
                    print("[监督模式] 提醒信号已发送")
                else:
                    print("[监督模式] 用户活动符合目标，无需提醒")
            else:
                print("[监督模式] 评估结果为空")
        else:
            print("[监督模式] 无法获取统计数据")
        
        self.last_check_time = current_time
    
    def _is_user_afk(self) -> bool:
        """检查用户是否处于AFK状态
        
        Returns:
            True如果用户在过去5分钟完全AFK，False否则
        """
        try:
            with self.stats_processor as sp:
                # 获取AFK时长（空闲时间）
                afk_stats = sp.get_afk_time_5m()
                # 如果AFK时间超过4分钟（240秒），认为用户完全AFK
                return afk_stats and afk_stats.get('afk_seconds', 0) > 240
        except Exception as e:
            print(f"检查AFK状态失败: {e}")
            return False
    
    def _get_comprehensive_activity_stats(self) -> Dict[str, Any]:
        """获取多时段的综合活动统计
        
        Returns:
            包含5分钟、2小时和当日活动统计的字典
        """
        try:
            with self.stats_processor as sp:
                # 5分钟数据
                stats_5m = sp.get_stats_5m()
                
                # 2小时数据
                stats_2h = sp.get_stats_2h()
                
                # 当日数据（从凌晨4点开始）
                stats_today = sp.get_stats_today()
                
                return {
                    'stats_5m': stats_5m,
                    'stats_2h': stats_2h,
                    'stats_today': stats_today,
                    'timestamp': datetime.now().isoformat()
                }
        except Exception as e:
            print(f"获取综合活动统计失败: {e}")
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
            print("警告：监督模式需要配置LLM才能正常工作")
            return None
        
        try:
            # 获取当前人设
            from .core.persona_manager import PersonaManager
            persona_manager = PersonaManager()
            current_persona = persona_manager.get_current_persona_info()
            
            # 构建增强的评估提示
            prompt = f"""你是巴利（Baal），一个监督用户生产力的桌面宠物助手。
当前人设模式：{current_persona['name']}
人设特点：{current_persona['description']}

用户设定的目标：
长期目标：{self.long_term_goal if self.long_term_goal else '未设定'}
短期目标：{', '.join(self.short_term_goals) if self.short_term_goals else '未设定'}

用户的电脑使用情况：

过去5分钟：
{stats.get('stats_5m', '无数据')[:500]}

过去2小时：
{stats.get('stats_2h', '无数据')[:500]}

今日总体（从凌晨4点开始）：
{stats.get('stats_today', '无数据')[:500]}

请分析用户的活动是否符合其设定的目标，并按照以下JSON格式回答：
{{
    "should_remind": true或false（是否需要提醒用户）,
    "deviation_level": "严重"或"中度"或"轻微"（偏离程度）,
    "reminder_message": "根据人设特点的提醒内容，使用中文",
    "analysis": "简短的分析说明"
}}

注意：
1. 如果用户正在做与目标相关的事情，不要提醒
2. 只有当用户明显偏离目标时才提醒
3. 提醒内容必须符合当前人设的语言风格
"""
            
            # 使用LLM评估
            response = self.llm_assistant.chat(prompt)
            
            # 解析JSON响应
            import json
            # 尝试提取JSON部分
            if '{' in response and '}' in response:
                json_start = response.index('{')
                json_end = response.rindex('}') + 1
                json_str = response[json_start:json_end]
                return json.loads(json_str)
            else:
                # 如果无法解析JSON，默认不提醒
                return {'should_remind': False}
            
        except Exception as e:
            print(f"增强评估活动时出错: {e}")
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
        return {
            'type': 'supervision_reminder',
            'long_term_goal': self.long_term_goal,
            'short_term_goals': self.short_term_goals,
            'activity_stats': stats,
            'evaluation': evaluation,
            'reminder_message': evaluation.get('reminder_message', '你似乎偏离了目标，请回到正轨。'),
            'deviation_level': evaluation.get('deviation_level', '未知'),
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