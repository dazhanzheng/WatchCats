"""
日程数据模型
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Callable, Optional, Dict, Any
import uuid


@dataclass
class Schedule:
    """日程数据模型
    
    Attributes:
        id: 日程唯一标识符
        title: 事项标题
        details: 事项详情
        start_time: 开始时间（精确到分钟）
        duration_minutes: 持续时间（分钟）
        trigger_percentages: 触发回调的进度百分比列表，默认包含100%
        callbacks: 回调函数字典，键为百分比，值为回调函数
        metadata: 额外的元数据
        created_at: 创建时间
        updated_at: 更新时间
        is_active: 是否激活
        triggered_percentages: 已触发的百分比列表，避免重复触发
    """
    
    title: str
    details: str
    start_time: datetime
    duration_minutes: int
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    trigger_percentages: List[float] = field(default_factory=lambda: [100.0])
    callbacks: Dict[float, Optional[Callable]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    related_goals: List[str] = field(default_factory=list)  # 相关目标的标题列表
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True
    triggered_percentages: List[float] = field(default_factory=list)
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保开始时间精确到分钟
        self.start_time = self.start_time.replace(second=0, microsecond=0)
        
        # 确保100%在触发列表中
        if 100.0 not in self.trigger_percentages:
            self.trigger_percentages.append(100.0)
        
        # 为每个触发百分比初始化回调
        for percentage in self.trigger_percentages:
            if percentage not in self.callbacks:
                self.callbacks[percentage] = None
    
    def get_end_time(self) -> datetime:
        """获取结束时间"""
        from datetime import timedelta
        return self.start_time + timedelta(minutes=self.duration_minutes)
    
    def get_progress_percentage(self, current_time: Optional[datetime] = None) -> float:
        """获取当前进度百分比
        
        Args:
            current_time: 当前时间，默认为现在
            
        Returns:
            进度百分比（0-100）
        """
        if current_time is None:
            current_time = datetime.now()
        
        if current_time < self.start_time:
            return 0.0
        
        if current_time >= self.get_end_time():
            return 100.0
        
        elapsed_minutes = (current_time - self.start_time).total_seconds() / 60
        return (elapsed_minutes / self.duration_minutes) * 100
    
    def is_in_progress(self, current_time: Optional[datetime] = None) -> bool:
        """检查日程是否正在进行中"""
        if current_time is None:
            current_time = datetime.now()
        
        return self.start_time <= current_time < self.get_end_time()
    
    def has_started(self, current_time: Optional[datetime] = None) -> bool:
        """检查日程是否已开始"""
        if current_time is None:
            current_time = datetime.now()
        
        return current_time >= self.start_time
    
    def has_ended(self, current_time: Optional[datetime] = None) -> bool:
        """检查日程是否已结束"""
        if current_time is None:
            current_time = datetime.now()
        
        return current_time >= self.get_end_time()
    
    def set_callback(self, percentage: float, callback: Callable):
        """设置特定百分比的回调函数
        
        Args:
            percentage: 触发百分比（0-100）
            callback: 回调函数
        """
        if percentage not in self.trigger_percentages:
            self.trigger_percentages.append(percentage)
            self.trigger_percentages.sort()
        
        self.callbacks[percentage] = callback
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式（用于序列化）"""
        return {
            'id': self.id,
            'title': self.title,
            'details': self.details,
            'start_time': self.start_time.isoformat(),
            'duration_minutes': self.duration_minutes,
            'trigger_percentages': self.trigger_percentages,
            'metadata': self.metadata,
            'related_goals': self.related_goals,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'is_active': self.is_active,
            'triggered_percentages': self.triggered_percentages
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Schedule':
        """从字典创建实例（用于反序列化）"""
        # 转换时间字符串为datetime对象
        data['start_time'] = datetime.fromisoformat(data['start_time'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        
        # 创建实例（不包含callbacks，因为函数不能序列化）
        instance = cls(
            id=data['id'],
            title=data['title'],
            details=data['details'],
            start_time=data['start_time'],
            duration_minutes=data['duration_minutes'],
            trigger_percentages=data.get('trigger_percentages', [100.0]),
            metadata=data.get('metadata', {}),
            related_goals=data.get('related_goals', []),
            created_at=data['created_at'],
            updated_at=data['updated_at'],
            is_active=data.get('is_active', True),
            triggered_percentages=data.get('triggered_percentages', [])
        )
        
        return instance 