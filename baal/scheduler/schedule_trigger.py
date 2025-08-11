"""
日程触发管理器
负责检测日程触发时间并执行相应动作
"""

import threading
from datetime import datetime, timedelta
from typing import Optional, Callable, Dict, Any
from PyQt6.QtCore import QObject, pyqtSignal
from .manager import ScheduleManager
from .models import Schedule
from .goals import GoalsManager
from ..aw_stats.stats_processor import StatsProcessor
import time


class ScheduleTriggerManager(QObject):
    """日程触发管理器
    
    负责监控日程并在适当的时间触发回调
    """
    
    # 信号：当日程需要触发时发出
    schedule_triggered = pyqtSignal(dict)  # 传递触发信息字典
    
    def __init__(self, schedule_manager: ScheduleManager = None):
        """初始化触发管理器
        
        Args:
            schedule_manager: 日程管理器实例
        """
        super().__init__()
        self.schedule_manager = schedule_manager or ScheduleManager()
        self.goals_manager = GoalsManager()
        self.stats_processor = StatsProcessor()
        
        self.is_running = False
        self.check_thread: Optional[threading.Thread] = None
        self.check_interval = 30  # 检查间隔（秒）
        
        # 记录已触发的日程和百分比，避免重复触发
        self.triggered_records: Dict[str, list] = {}
    
    def start(self):
        """启动触发监控"""
        if not self.is_running:
            self.is_running = True
            self.check_thread = threading.Thread(target=self._check_loop, daemon=True)
            self.check_thread.start()
            print("日程触发管理器已启动")
    
    def stop(self):
        """停止触发监控"""
        self.is_running = False
        if self.check_thread:
            self.check_thread.join(timeout=2)
            self.check_thread = None
        print("日程触发管理器已停止")
    
    def _check_loop(self):
        """检查循环"""
        while self.is_running:
            try:
                self._check_schedules()
            except Exception as e:
                print(f"检查日程时出错: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_schedules(self):
        """检查所有活动日程"""
        current_time = datetime.now()
        
        # 获取当前正在进行的日程
        current_schedules = self.schedule_manager.get_current()
        
        # 获取即将开始的日程（接下来1小时内）
        upcoming_schedules = self.schedule_manager.get_upcoming(hours=1)
        
        # 合并两个列表（去重）
        all_schedules = current_schedules.copy()
        current_ids = {s.id for s in current_schedules}
        for schedule in upcoming_schedules:
            if schedule.id not in current_ids:
                all_schedules.append(schedule)
        
        for schedule in all_schedules:
            # 检查日程是否应该触发
            progress = schedule.get_progress_percentage(current_time)
            
            # 如果日程还没开始但有0%触发点，检查是否到达开始时间
            if progress == 0 and 0 in schedule.trigger_percentages:
                # 检查是否接近开始时间（提前1分钟触发）
                time_to_start = (schedule.start_time - current_time).total_seconds()
                if 0 <= time_to_start <= 60:  # 1分钟内开始
                    if not self._is_already_triggered(schedule.id, 0):
                        self._trigger_schedule(schedule, 0, current_time)
                        self._mark_as_triggered(schedule.id, 0)
            
            # 检查进行中的日程
            elif schedule.is_in_progress(current_time):
                # 检查每个触发百分比
                for trigger_percentage in schedule.trigger_percentages:
                    if progress >= trigger_percentage:
                        # 检查是否已经触发过
                        if not self._is_already_triggered(schedule.id, trigger_percentage):
                            self._trigger_schedule(schedule, trigger_percentage, current_time)
                            self._mark_as_triggered(schedule.id, trigger_percentage)
    
    def _is_already_triggered(self, schedule_id: str, percentage: float) -> bool:
        """检查是否已经触发过"""
        if schedule_id not in self.triggered_records:
            return False
        return percentage in self.triggered_records[schedule_id]
    
    def _mark_as_triggered(self, schedule_id: str, percentage: float):
        """标记为已触发"""
        if schedule_id not in self.triggered_records:
            self.triggered_records[schedule_id] = []
        self.triggered_records[schedule_id].append(percentage)
    
    def _trigger_schedule(self, schedule: Schedule, percentage: float, current_time: datetime):
        """触发日程
        
        Args:
            schedule: 日程对象
            percentage: 触发百分比
            current_time: 当前时间
        """
        # 收集上下文信息
        context = self._collect_context(schedule, percentage)
        
        # 发出信号
        trigger_info = {
            'schedule': schedule,
            'percentage': percentage,
            'context': context,
            'timestamp': current_time.isoformat()
        }
        
        self.schedule_triggered.emit(trigger_info)
    
    def _collect_context(self, schedule: Schedule, percentage: float) -> Dict[str, Any]:
        """收集触发上下文
        
        Args:
            schedule: 日程对象
            percentage: 触发百分比
            
        Returns:
            包含所有相关上下文信息的字典
        """
        context = {}
        
        # 1. 获取过去24小时的活动统计
        try:
            stats_24h = self.stats_processor.get_activity_summary(hours=24)
            context['activity_24h'] = stats_24h
        except Exception as e:
            print(f"获取24小时活动统计失败: {e}")
            context['activity_24h'] = None
        
        # 2. 日程进度信息
        context['schedule_info'] = {
            'title': schedule.title,
            'details': schedule.details,
            'progress_percentage': percentage,
            'start_time': schedule.start_time.isoformat(),
            'end_time': schedule.get_end_time().isoformat(),
            'duration_minutes': schedule.duration_minutes
        }
        
        # 3. 用户目标信息
        context['goals'] = self.goals_manager.get_goals_summary()
        
        # 4. 相关目标（如果有）
        if schedule.related_goals:
            context['related_goals'] = schedule.related_goals
        
        return context
    
    def clear_triggered_records(self):
        """清除触发记录（每天调用一次）"""
        self.triggered_records.clear()
    
    def get_next_trigger_time(self) -> Optional[datetime]:
        """获取下一个触发时间"""
        current_time = datetime.now()
        next_trigger = None
        
        # 获取所有日程
        all_schedules = self.schedule_manager.list()
        
        for schedule in all_schedules:
            if not schedule.is_active or schedule.has_ended(current_time):
                continue
            
            for percentage in schedule.trigger_percentages:
                if self._is_already_triggered(schedule.id, percentage):
                    continue
                
                # 计算触发时间
                trigger_minutes = schedule.duration_minutes * (percentage / 100)
                trigger_time = schedule.start_time + timedelta(minutes=trigger_minutes)
                
                if trigger_time > current_time:
                    if next_trigger is None or trigger_time < next_trigger:
                        next_trigger = trigger_time
        
        return next_trigger