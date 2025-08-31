"""
智能状态更新管理器

负责决定何时以及如何更新动态状态
优化性能的同时保证用户体验
"""

import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Set, Tuple, Any
from enum import Enum
from .state_awareness import get_state_awareness, TimeOfDay


class UpdatePriority(Enum):
    """更新优先级"""
    CRITICAL = 1  # 必须立即更新
    HIGH = 2      # 尽快更新
    MEDIUM = 3    # 适时更新
    LOW = 4       # 可以延迟更新


class StateComponent(Enum):
    """状态组件"""
    TIME = "time"              # 时间状态
    MOOD = "mood"              # 心情状态
    INTERACTION = "interaction"  # 互动状态
    SUPERVISION = "supervision"  # 监督模式
    SPECIAL = "special"        # 特殊事件
    ENVIRONMENT = "environment"  # 环境状态
    MEMORY = "memory"          # 记忆状态


class StateUpdateManager:
    """智能状态更新管理器"""
    
    # 各组件的更新间隔（秒）
    UPDATE_INTERVALS = {
        StateComponent.TIME: 0,         # 实时检查，但只在跨段时更新
        StateComponent.MOOD: 600,       # 10分钟
        StateComponent.INTERACTION: 60,  # 1分钟冷却
        StateComponent.SUPERVISION: 0,   # 立即更新
        StateComponent.SPECIAL: 3600,   # 1小时检查一次
        StateComponent.ENVIRONMENT: 1800, # 30分钟
        StateComponent.MEMORY: 300,     # 5分钟
    }
    
    # 触发立即更新的事件
    TRIGGER_EVENTS = {
        "supervision_toggle",     # 监督模式切换
        "achievement_unlocked",   # 成就达成
        "long_idle",             # 长时间闲置
        "intense_interaction",   # 密集互动
        "time_segment_change",   # 时间段变化
        "special_date",          # 特殊日期
        "mood_shift",           # 情绪重大变化
        "first_interaction",     # 每日首次互动
    }
    
    def __init__(self):
        """初始化更新管理器"""
        self.state_system = get_state_awareness()
        self.last_updates: Dict[StateComponent, float] = {}
        self.cached_states: Dict[str, Tuple[str, float]] = {}  # 缓存的状态和时间戳
        self.pending_updates: Set[StateComponent] = set()
        self.last_time_segment: Optional[TimeOfDay] = None
        self.interaction_count = 0
        self.last_interaction_time = 0
        self.state_hash: Optional[str] = None
        self.last_full_update = 0
        
        # 初始化组件更新时间
        current_time = time.time()
        for component in StateComponent:
            self.last_updates[component] = current_time
    
    def should_update(self, force_check: bool = False) -> Tuple[bool, Set[StateComponent]]:
        """
        判断是否需要更新状态
        
        Args:
            force_check: 是否强制检查所有组件
            
        Returns:
            (是否需要更新, 需要更新的组件集合)
        """
        current_time = time.time()
        components_to_update = set()
        
        # 1. 检查时间段变化（最高优先级）
        current_segment = self.state_system.get_time_of_day()
        if self.last_time_segment != current_segment:
            components_to_update.add(StateComponent.TIME)
            components_to_update.add(StateComponent.MOOD)  # 时间变化影响心情
            self.last_time_segment = current_segment
            
        # 2. 检查定时更新的组件
        for component, interval in self.UPDATE_INTERVALS.items():
            if interval > 0:  # 0表示事件驱动，不定时更新
                last_update = self.last_updates.get(component, 0)
                if current_time - last_update >= interval:
                    components_to_update.add(component)
        
        # 3. 检查待处理的更新
        components_to_update.update(self.pending_updates)
        
        # 4. 智能决策：如果太频繁，过滤低优先级更新
        if not force_check and len(components_to_update) > 0:
            # 如果距离上次完整更新不到30秒，只保留高优先级
            if current_time - self.last_full_update < 30:
                high_priority = {StateComponent.TIME, StateComponent.SUPERVISION, StateComponent.INTERACTION}
                components_to_update &= high_priority
        
        return len(components_to_update) > 0, components_to_update
    
    def trigger_event(self, event: str, **kwargs) -> bool:
        """
        触发事件，可能导致状态更新
        
        Args:
            event: 事件名称
            **kwargs: 事件参数
            
        Returns:
            是否触发了更新
        """
        if event not in self.TRIGGER_EVENTS:
            return False
        
        # 根据事件类型决定更新哪些组件
        if event == "supervision_toggle":
            self.pending_updates.add(StateComponent.SUPERVISION)
            self.pending_updates.add(StateComponent.MOOD)
            
        elif event == "time_segment_change":
            self.pending_updates.add(StateComponent.TIME)
            self.pending_updates.add(StateComponent.MOOD)
            
        elif event == "intense_interaction":
            current_time = time.time()
            # 检查互动频率
            if current_time - self.last_interaction_time < 60:
                self.interaction_count += 1
                if self.interaction_count >= 3:  # 1分钟内3次互动
                    self.pending_updates.add(StateComponent.INTERACTION)
                    self.pending_updates.add(StateComponent.MOOD)
            else:
                self.interaction_count = 1
            self.last_interaction_time = current_time
            
        elif event == "achievement_unlocked":
            self.pending_updates.add(StateComponent.MEMORY)
            self.pending_updates.add(StateComponent.MOOD)
            self.pending_updates.add(StateComponent.SPECIAL)
            
        elif event == "first_interaction":
            # 每日首次互动，全面更新
            for component in StateComponent:
                self.pending_updates.add(component)
        
        return len(self.pending_updates) > 0
    
    def get_updated_state(self, components: Optional[Set[StateComponent]] = None) -> Dict[str, Any]:
        """
        获取更新后的状态
        
        Args:
            components: 要更新的组件，None表示全部更新
            
        Returns:
            更新后的状态字典
        """
        current_time = time.time()
        
        # 如果没有指定组件，检查哪些需要更新
        if components is None:
            _, components = self.should_update()
        
        # 获取当前完整状态
        full_state = self.state_system.get_current_state()
        
        # 更新指定的组件
        updated_state = {}
        
        for component in components:
            if component == StateComponent.TIME:
                updated_state['time'] = full_state.get('time', '')
                updated_state['datetime'] = full_state.get('datetime', '')
                updated_state['weekday'] = full_state.get('weekday', '')
                
            elif component == StateComponent.MOOD:
                updated_state['mood'] = full_state.get('mood', '')
                
            elif component == StateComponent.INTERACTION:
                updated_state['interaction'] = full_state.get('interaction', '')
                
            elif component == StateComponent.SPECIAL:
                if 'special' in full_state:
                    updated_state['special'] = full_state['special']
            
            # 记录更新时间
            self.last_updates[component] = current_time
        
        # 清空待处理更新
        self.pending_updates.clear()
        
        # 如果是完整更新，记录时间
        if len(components) >= 4:
            self.last_full_update = current_time
        
        return updated_state
    
    def get_state_with_cache(self, cache_key: str, generator_func, ttl: int = 300) -> str:
        """
        获取带缓存的状态
        
        Args:
            cache_key: 缓存键
            generator_func: 生成函数
            ttl: 缓存生存时间（秒）
            
        Returns:
            状态字符串
        """
        current_time = time.time()
        
        # 检查缓存
        if cache_key in self.cached_states:
            cached_value, timestamp = self.cached_states[cache_key]
            if current_time - timestamp < ttl:
                return cached_value
        
        # 生成新状态
        new_value = generator_func()
        self.cached_states[cache_key] = (new_value, current_time)
        
        # 清理过期缓存
        self._cleanup_cache()
        
        return new_value
    
    def _cleanup_cache(self):
        """清理过期缓存"""
        current_time = time.time()
        expired_keys = []
        
        for key, (_, timestamp) in self.cached_states.items():
            if current_time - timestamp > 3600:  # 1小时过期
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cached_states[key]
    
    def calculate_state_hash(self, state: Dict[str, Any]) -> str:
        """
        计算状态哈希，用于检测状态变化
        
        Args:
            state: 状态字典
            
        Returns:
            哈希值
        """
        # 只包含关键字段
        key_fields = ['time', 'mood', 'interaction', 'supervision']
        state_str = '|'.join(str(state.get(field, '')) for field in key_fields)
        return hashlib.md5(state_str.encode()).hexdigest()[:8]
    
    def has_significant_change(self, new_state: Dict[str, Any]) -> bool:
        """
        检测是否有显著变化
        
        Args:
            new_state: 新状态
            
        Returns:
            是否有显著变化
        """
        new_hash = self.calculate_state_hash(new_state)
        if self.state_hash != new_hash:
            self.state_hash = new_hash
            return True
        return False
    
    def get_update_report(self) -> Dict[str, Any]:
        """
        获取更新报告（用于调试）
        
        Returns:
            更新统计信息
        """
        current_time = time.time()
        report = {}
        
        for component in StateComponent:
            last_update = self.last_updates.get(component, 0)
            time_since = current_time - last_update
            report[component.value] = {
                'last_update': datetime.fromtimestamp(last_update).strftime('%H:%M:%S'),
                'seconds_ago': int(time_since),
                'needs_update': time_since >= self.UPDATE_INTERVALS[component]
            }
        
        report['pending_updates'] = [c.value for c in self.pending_updates]
        report['cache_size'] = len(self.cached_states)
        
        return report


# 单例模式
_update_manager_instance = None

def get_update_manager() -> StateUpdateManager:
    """获取更新管理器单例"""
    global _update_manager_instance
    if _update_manager_instance is None:
        _update_manager_instance = StateUpdateManager()
    return _update_manager_instance