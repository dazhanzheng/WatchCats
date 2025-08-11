"""
日程调度器

负责监控日程进度并在特定时间点触发回调。
"""

import threading
import time
from datetime import datetime
from typing import Optional, Callable, Dict, Any
import logging

from .models import Schedule
from .manager import ScheduleManager


class Scheduler:
    """日程调度器
    
    在后台线程中监控日程进度，并在达到指定百分比时触发回调。
    """
    
    def __init__(self, manager: ScheduleManager, check_interval: int = 60):
        """初始化调度器
        
        Args:
            manager: 日程管理器实例
            check_interval: 检查间隔（秒），默认60秒
        """
        self.manager = manager
        self.check_interval = check_interval
        self.is_running = False
        self._thread: Optional[threading.Thread] = None
        self.logger = logging.getLogger(__name__)
        
        # 默认回调函数（占位符）
        self.default_callback: Optional[Callable[[Schedule, float], None]] = None
    
    def start(self):
        """启动调度器"""
        if self.is_running:
            self.logger.warning("调度器已在运行")
            return
        
        self.is_running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.logger.info("调度器已启动")
    
    def stop(self):
        """停止调度器"""
        if not self.is_running:
            return
        
        self.is_running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("调度器已停止")
    
    def _run(self):
        """调度器主循环"""
        while self.is_running:
            try:
                self._check_schedules()
                time.sleep(self.check_interval)
            except Exception as e:
                self.logger.error(f"调度器运行出错: {e}")
                time.sleep(self.check_interval)
    
    def _check_schedules(self):
        """检查所有活动日程"""
        current_time = datetime.now()
        
        # 获取所有活动的日程
        active_schedules = [s for s in self.manager.schedules.values() if s.is_active]
        
        for schedule in active_schedules:
            # 跳过尚未开始或已结束的日程
            if not schedule.has_started(current_time) or schedule.has_ended(current_time):
                continue
            
            # 获取当前进度
            progress = schedule.get_progress_percentage(current_time)
            
            # 检查需要触发的百分比
            for trigger_percentage in schedule.trigger_percentages:
                # 检查是否已触发过
                if trigger_percentage in schedule.triggered_percentages:
                    continue
                
                # 检查是否达到触发点
                if progress >= trigger_percentage:
                    self._trigger_callback(schedule, trigger_percentage)
                    
                    # 记录已触发
                    schedule.triggered_percentages.append(trigger_percentage)
                    self.manager._save_to_storage()
    
    def _trigger_callback(self, schedule: Schedule, percentage: float):
        """触发回调
        
        Args:
            schedule: 日程对象
            percentage: 触发百分比
        """
        self.logger.info(f"触发日程回调: {schedule.title} - {percentage}%")
        
        # 获取对应的回调函数
        callback = schedule.callbacks.get(percentage)
        
        if callback:
            # 执行特定回调
            try:
                callback(schedule, percentage)
            except Exception as e:
                self.logger.error(f"执行回调出错: {e}")
        elif self.default_callback:
            # 执行默认回调
            try:
                self.default_callback(schedule, percentage)
            except Exception as e:
                self.logger.error(f"执行默认回调出错: {e}")
        else:
            # 占位提示（将来可以在这里调用其他模块）
            self.logger.info(f"[占位回调] 日程 '{schedule.title}' 已完成 {percentage}%")
            self.logger.info(f"  - 开始时间: {schedule.start_time}")
            self.logger.info(f"  - 持续时间: {schedule.duration_minutes} 分钟")
            self.logger.info(f"  - 详情: {schedule.details}")
    
    def set_default_callback(self, callback: Callable[[Schedule, float], None]):
        """设置默认回调函数
        
        当日程没有设置特定百分比的回调时，将使用此默认回调。
        
        Args:
            callback: 回调函数，接收参数 (schedule, percentage)
        """
        self.default_callback = callback
        self.logger.info("已设置默认回调函数")
    
    def check_now(self, schedule_id: Optional[str] = None):
        """立即检查日程（用于测试）
        
        Args:
            schedule_id: 指定日程ID，如果为None则检查所有日程
        """
        if schedule_id:
            schedule = self.manager.get(schedule_id)
            if schedule and schedule.is_active:
                current_time = datetime.now()
                progress = schedule.get_progress_percentage(current_time)
                self.logger.info(f"日程 '{schedule.title}' 当前进度: {progress:.1f}%")
                
                # 手动检查触发
                for trigger_percentage in schedule.trigger_percentages:
                    if (trigger_percentage not in schedule.triggered_percentages and 
                        progress >= trigger_percentage):
                        self._trigger_callback(schedule, trigger_percentage)
                        schedule.triggered_percentages.append(trigger_percentage)
                        self.manager._save_to_storage()
        else:
            self._check_schedules()


 