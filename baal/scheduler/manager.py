"""
日程管理器

提供日程的增删改查功能，并自动持久化到存储。
"""

from typing import List, Optional, Dict, Any, Callable
from datetime import datetime
import logging

from .models import Schedule
from .storage import ScheduleStorage


class ScheduleManager:
    """日程管理器
    
    提供简洁的API进行日程的增删改查操作，并自动处理持久化。
    """
    
    def __init__(self, storage_path: Optional[str] = None, auto_save: bool = True):
        """初始化管理器
        
        Args:
            storage_path: 存储文件路径，默认使用系统默认路径
            auto_save: 是否在每次操作后自动保存
        """
        self.storage = ScheduleStorage(storage_path)
        self.auto_save = auto_save
        self.schedules: Dict[str, Schedule] = {}
        self.logger = logging.getLogger(__name__)
        
        # 从存储加载现有日程
        self._load_from_storage()
    
    def _load_from_storage(self):
        """从存储加载日程"""
        loaded_schedules = self.storage.load_schedules()
        for schedule in loaded_schedules:
            self.schedules[schedule.id] = schedule
        self.logger.info(f"从存储加载了 {len(loaded_schedules)} 个日程")
    
    def _save_to_storage(self):
        """保存日程到存储"""
        if self.auto_save:
            schedules_list = list(self.schedules.values())
            success = self.storage.save_schedules(schedules_list)
            if not success:
                self.logger.error("自动保存失败")
    
    def add(self, 
            title: str, 
            details: str, 
            start_time: datetime, 
            duration_minutes: int,
            trigger_percentages: Optional[List[float]] = None,
            callbacks: Optional[Dict[float, Callable]] = None,
            metadata: Optional[Dict[str, Any]] = None) -> Schedule:
        """添加新日程
        
        Args:
            title: 事项标题
            details: 事项详情
            start_time: 开始时间
            duration_minutes: 持续时间（分钟）
            trigger_percentages: 触发百分比列表，默认[100.0]
            callbacks: 回调函数字典
            metadata: 额外元数据
            
        Returns:
            创建的日程对象
        """
        # 创建日程
        schedule = Schedule(
            title=title,
            details=details,
            start_time=start_time,
            duration_minutes=duration_minutes,
            trigger_percentages=trigger_percentages or [100.0],
            metadata=metadata or {}
        )
        
        # 设置回调
        if callbacks:
            for percentage, callback in callbacks.items():
                schedule.set_callback(percentage, callback)
        
        # 添加到管理器
        self.schedules[schedule.id] = schedule
        self._save_to_storage()
        
        self.logger.info(f"添加日程: {schedule.title} (ID: {schedule.id})")
        return schedule
    
    def update(self, 
               schedule_id: str,
               title: Optional[str] = None,
               details: Optional[str] = None,
               start_time: Optional[datetime] = None,
               duration_minutes: Optional[int] = None,
               trigger_percentages: Optional[List[float]] = None,
               is_active: Optional[bool] = None,
               metadata: Optional[Dict[str, Any]] = None) -> Optional[Schedule]:
        """更新日程
        
        Args:
            schedule_id: 日程ID
            title: 新标题（可选）
            details: 新详情（可选）
            start_time: 新开始时间（可选）
            duration_minutes: 新持续时间（可选）
            trigger_percentages: 新触发百分比列表（可选）
            is_active: 是否激活（可选）
            metadata: 新元数据（可选）
            
        Returns:
            更新后的日程对象，如果未找到则返回None
        """
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            self.logger.warning(f"未找到日程: {schedule_id}")
            return None
        
        # 更新字段
        if title is not None:
            schedule.title = title
        if details is not None:
            schedule.details = details
        if start_time is not None:
            schedule.start_time = start_time.replace(second=0, microsecond=0)
        if duration_minutes is not None:
            schedule.duration_minutes = duration_minutes
        if trigger_percentages is not None:
            schedule.trigger_percentages = trigger_percentages
            # 确保100%在列表中
            if 100.0 not in schedule.trigger_percentages:
                schedule.trigger_percentages.append(100.0)
        if is_active is not None:
            schedule.is_active = is_active
        if metadata is not None:
            schedule.metadata.update(metadata)
        
        # 更新时间戳
        schedule.updated_at = datetime.now()
        
        self._save_to_storage()
        self.logger.info(f"更新日程: {schedule.title} (ID: {schedule_id})")
        return schedule
    
    def delete(self, schedule_id: str) -> bool:
        """删除日程
        
        Args:
            schedule_id: 日程ID
            
        Returns:
            是否删除成功
        """
        if schedule_id in self.schedules:
            schedule = self.schedules.pop(schedule_id)
            self._save_to_storage()
            self.logger.info(f"删除日程: {schedule.title} (ID: {schedule_id})")
            return True
        else:
            self.logger.warning(f"未找到日程: {schedule_id}")
            return False
    
    def get(self, schedule_id: str) -> Optional[Schedule]:
        """获取单个日程
        
        Args:
            schedule_id: 日程ID
            
        Returns:
            日程对象，如果未找到则返回None
        """
        return self.schedules.get(schedule_id)
    
    def list(self, 
             active_only: bool = False,
             include_past: bool = True,
             include_future: bool = True,
             sort_by: str = 'start_time',
             date_from: Optional[datetime] = None,
             date_to: Optional[datetime] = None) -> List[Schedule]:
        """列出日程
        
        Args:
            active_only: 仅返回激活的日程
            include_past: 包含过去的日程
            include_future: 包含未来的日程
            sort_by: 排序字段 ('start_time', 'created_at', 'title')
            date_from: 开始日期（包含）
            date_to: 结束日期（包含）
            
        Returns:
            符合条件的日程列表
        """
        schedules = list(self.schedules.values())
        current_time = datetime.now()
        
        # 过滤
        if active_only:
            schedules = [s for s in schedules if s.is_active]
        
        if not include_past:
            schedules = [s for s in schedules if not s.has_ended(current_time)]
        
        if not include_future:
            schedules = [s for s in schedules if s.has_started(current_time)]
        
        # 日期范围过滤
        if date_from is not None:
            schedules = [s for s in schedules if s.start_time >= date_from]
        
        if date_to is not None:
            # 如果 date_to 只有日期没有时间，设置为当天的 23:59:59
            if date_to.hour == 0 and date_to.minute == 0 and date_to.second == 0:
                date_to = date_to.replace(hour=23, minute=59, second=59)
            schedules = [s for s in schedules if s.start_time <= date_to]
        
        # 排序
        if sort_by == 'start_time':
            schedules.sort(key=lambda s: s.start_time)
        elif sort_by == 'created_at':
            schedules.sort(key=lambda s: s.created_at)
        elif sort_by == 'title':
            schedules.sort(key=lambda s: s.title)
        
        return schedules
    
    def get_current(self) -> List[Schedule]:
        """获取当前正在进行的日程
        
        Returns:
            正在进行的日程列表
        """
        current_time = datetime.now()
        return [s for s in self.schedules.values() 
                if s.is_active and s.is_in_progress(current_time)]
    
    def get_upcoming(self, hours: int = 24) -> List[Schedule]:
        """获取即将开始的日程
        
        Args:
            hours: 查看未来多少小时内的日程
            
        Returns:
            即将开始的日程列表
        """
        from datetime import timedelta
        current_time = datetime.now()
        future_time = current_time + timedelta(hours=hours)
        
        upcoming = []
        for schedule in self.schedules.values():
            if (schedule.is_active and 
                not schedule.has_started(current_time) and
                current_time <= schedule.start_time <= future_time):  # 修复：确保开始时间在指定范围内
                upcoming.append(schedule)
        
        # 按开始时间排序
        upcoming.sort(key=lambda s: s.start_time)
        return upcoming
    
    def get_schedules_for_date(self, date: datetime) -> List[Schedule]:
        """获取特定日期的所有日程
        
        Args:
            date: 目标日期（只使用日期部分，忽略时间）
            
        Returns:
            该日期的所有日程列表
        """
        # 获取日期的开始和结束时间
        date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        date_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        schedules = []
        for schedule in self.schedules.values():
            # 检查日程是否在这一天开始
            if date_start <= schedule.start_time <= date_end:
                schedules.append(schedule)
        
        # 按开始时间排序
        schedules.sort(key=lambda s: s.start_time)
        return schedules
    
    def set_callback(self, schedule_id: str, percentage: float, callback: Callable) -> bool:
        """为日程设置回调函数
        
        Args:
            schedule_id: 日程ID
            percentage: 触发百分比
            callback: 回调函数
            
        Returns:
            是否设置成功
        """
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            self.logger.warning(f"未找到日程: {schedule_id}")
            return False
        
        schedule.set_callback(percentage, callback)
        self._save_to_storage()
        return True
    
    def clear_triggered(self, schedule_id: str) -> bool:
        """清除已触发的百分比记录（用于重新触发）
        
        Args:
            schedule_id: 日程ID
            
        Returns:
            是否清除成功
        """
        schedule = self.schedules.get(schedule_id)
        if not schedule:
            return False
        
        schedule.triggered_percentages.clear()
        self._save_to_storage()
        return True
    
    def save(self) -> bool:
        """手动保存到存储
        
        Returns:
            是否保存成功
        """
        schedules_list = list(self.schedules.values())
        return self.storage.save_schedules(schedules_list)
    
    def reload(self):
        """从存储重新加载"""
        self.schedules.clear()
        self._load_from_storage()
    
    def backup(self) -> bool:
        """创建备份
        
        Returns:
            是否备份成功
        """
        return self.storage.backup()
    
    def export(self) -> Dict[str, Any]:
        """导出所有日程数据
        
        Returns:
            包含所有日程的字典
        """
        schedules_list = list(self.schedules.values())
        return self.storage.export_to_dict(schedules_list)
    
    def import_schedules(self, data: Dict[str, Any], merge: bool = False) -> int:
        """导入日程数据
        
        Args:
            data: 包含日程数据的字典
            merge: 是否合并（True）或替换（False）现有日程
            
        Returns:
            导入的日程数量
        """
        imported_schedules = self.storage.import_from_dict(data)
        
        if not merge:
            self.schedules.clear()
        
        count = 0
        for schedule in imported_schedules:
            # 如果是合并模式且ID已存在，则跳过
            if merge and schedule.id in self.schedules:
                continue
            
            self.schedules[schedule.id] = schedule
            count += 1
        
        self._save_to_storage()
        return count 