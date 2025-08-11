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
        self.supervision_goal = ""  # 监督目标
        self.supervision_tasks = []  # 预期要做的事情列表
        self.check_thread: Optional[threading.Thread] = None
        self.check_interval = 300  # 检查间隔（5分钟）
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
                    self.supervision_goal = data.get('goal', '')
                    self.supervision_tasks = data.get('tasks', [])
                    # 不自动恢复激活状态，需要用户手动开启
        except Exception as e:
            print(f"加载监督设置失败: {e}")
    
    def _save_supervision_settings(self):
        """保存监督设置"""
        try:
            config_path = self.config_manager.config_dir / 'supervision.json'
            data = {
                'goal': self.supervision_goal,
                'tasks': self.supervision_tasks,
                'updated_at': datetime.now().isoformat()
            }
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存监督设置失败: {e}")
    
    def start_supervision(self, goal: str, tasks: list):
        """启动监督模式
        
        Args:
            goal: 监督目标描述
            tasks: 预期要做的事情列表
        """
        # 检查是否已配置LLM
        if not self.llm_assistant:
            # 尝试重新初始化LLM助手
            self._init_llm_assistant()
            
            # 如果仍然没有LLM助手，说明未配置API
            if not self.llm_assistant:
                print("错误：监督模式需要配置API密钥才能正常工作")
                return False  # 返回False表示启动失败
        
        self.supervision_goal = goal
        self.supervision_tasks = tasks
        self.is_active = True
        self.last_check_time = datetime.now()
        
        # 保存设置
        self._save_supervision_settings()
        
        # 启动检查线程
        if self.check_thread is None or not self.check_thread.is_alive():
            self.check_thread = threading.Thread(target=self._check_loop, daemon=True)
            self.check_thread.start()
        
        self.mode_changed.emit(True)
        print(f"监督模式已启动 - 目标: {goal}")
        return True
    
    def stop_supervision(self):
        """停止监督模式"""
        self.is_active = False
        self.mode_changed.emit(False)
        print("监督模式已停止")
    
    def _check_loop(self):
        """检查循环"""
        while self.is_active:
            time.sleep(self.check_interval)
            
            if not self.is_active:
                break
            
            try:
                self._check_activity()
            except Exception as e:
                print(f"检查活动时出错: {e}")
    
    def _check_activity(self):
        """检查用户活动是否符合目标"""
        # 获取过去5分钟的活动数据
        current_time = datetime.now()
        stats = self._get_recent_activity_stats()
        
        if stats:
            # 使用LLM判断是否偏离目标
            is_on_track = self._evaluate_activity(stats)
            
            if not is_on_track:
                # 生成提醒内容
                reminder_context = self._create_reminder_context(stats)
                self.reminder_needed.emit(reminder_context)
        
        self.last_check_time = current_time
    
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

用户设定的监督目标：{self.supervision_goal}
预期要做的事情：{', '.join(self.supervision_tasks)}

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
            response = self.llm_assistant.ask(prompt)
            
            # 简单判断回复
            return "是" in response or "符合" in response or "yes" in response.lower()
            
        except Exception as e:
            print(f"评估活动时出错: {e}")
            # 出错时默认不打扰用户
            return True
    
    def _create_reminder_context(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """创建提醒上下文
        
        Args:
            stats: 活动统计数据
            
        Returns:
            提醒上下文字典
        """
        return {
            'type': 'supervision_reminder',
            'goal': self.supervision_goal,
            'tasks': self.supervision_tasks,
            'activity_stats': stats,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict[str, Any]:
        """获取监督模式状态"""
        return {
            'is_active': self.is_active,
            'goal': self.supervision_goal,
            'tasks': self.supervision_tasks,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None
        }
    
    def update_goal(self, goal: str, tasks: list):
        """更新监督目标（不重启监督）"""
        self.supervision_goal = goal
        self.supervision_tasks = tasks
        self._save_supervision_settings()
        print(f"监督目标已更新: {goal}")