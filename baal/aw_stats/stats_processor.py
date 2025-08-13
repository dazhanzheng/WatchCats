"""
ActivityWatch 统计数据处理模块

该模块负责从 ActivityWatch 获取不同时间范围的统计数据，
并将其处理成自然语言格式供其他模块调用。
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict

from aw_client import ActivityWatchClient
from aw_core import Event
from aw_transform import (
    merge_events_by_keys,
    sort_by_duration,
    sum_durations,
    limit_events,
    filter_keyvals,
    filter_period_intersect
)

from ..desktop_pet.core.logger_config import get_logger, log_performance

logger = logging.getLogger(__name__)


class StatsProcessor:
    """处理 ActivityWatch 统计数据的主类"""
    
    def __init__(self, client_name: str = "aw-stats-processor", testing: bool = False):
        """
        初始化统计处理器
        
        Args:
            client_name: 客户端名称
            testing: 是否使用测试模式
        """
        self.logger = get_logger('baal.aw_stats.stats_processor')
        self.logger.info(f"Initializing StatsProcessor (client_name={client_name}, testing={testing})")
        
        try:
            self.client = ActivityWatchClient(client_name, testing=testing)
            self.logger.info("ActivityWatch client initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize ActivityWatch client: {e}", exc_info=True)
            raise
            
        self._bucket_cache = None
        
    def __enter__(self):
        """上下文管理器入口"""
        self.client.connect()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.client.disconnect()
        
    def _get_window_bucket(self) -> Optional[str]:
        """获取窗口监视器的桶ID"""
        if not self._bucket_cache:
            buckets = self.client.get_buckets()
            self._bucket_cache = buckets
            
        # 查找 window watcher 的桶
        for bucket_id in self._bucket_cache:
            if "window" in bucket_id and "watcher" in bucket_id:
                return bucket_id
        return None
        
    def _get_afk_bucket(self) -> Optional[str]:
        """获取 AFK 监视器的桶ID"""
        if not self._bucket_cache:
            buckets = self.client.get_buckets()
            self._bucket_cache = buckets
            
        # 查找 afk watcher 的桶
        for bucket_id in self._bucket_cache:
            if "afk" in bucket_id and "watcher" in bucket_id:
                return bucket_id
        return None
        
    def _format_duration(self, duration: timedelta) -> str:
        """
        格式化时间长度为人类可读的格式
        
        Args:
            duration: 时间长度
            
        Returns:
            格式化后的字符串，如 "2小时30分钟15秒"
        """
        total_seconds = int(duration.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        parts = []
        if hours > 0:
            parts.append(f"{hours}小时")
        if minutes > 0:
            parts.append(f"{minutes}分钟")
        if seconds > 0 or not parts:  # 如果没有小时和分钟，至少显示秒
            parts.append(f"{seconds}秒")
            
        return "".join(parts)
        
    def _get_events_for_period(self, hours_back: float) -> List[Event]:
        """
        获取指定时间段内的事件，并过滤掉用户不活跃(AFK)的时间段
        
        Args:
            hours_back: 向前追溯的小时数
            
        Returns:
            事件列表（仅包含用户活跃时的事件）
        """
        window_bucket_id = self._get_window_bucket()
        afk_bucket_id = self._get_afk_bucket()
        
        if not window_bucket_id:
            logger.warning("未找到窗口监视器桶")
            return []
            
        if not afk_bucket_id:
            logger.warning("未找到 AFK 监视器桶，将返回所有窗口事件")
            
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=hours_back)
        
        try:
            # 获取窗口事件
            window_events = self.client.get_events(
                window_bucket_id, 
                start=start_time, 
                end=end_time
            )
            
            if not afk_bucket_id:
                # 如果没有 AFK 桶，返回所有窗口事件
                return window_events
                
            # 获取 AFK 事件
            afk_events = self.client.get_events(
                afk_bucket_id,
                start=start_time,
                end=end_time
            )
            
            # 只保留状态为 "not-afk" 的事件
            not_afk_events = [e for e in afk_events if e.data.get("status") == "not-afk"]
            
            if not not_afk_events:
                logger.warning("没有找到用户活跃的时间段")
                return []
                
            # 使用 filter_period_intersect 过滤窗口事件
            # 只保留用户活跃时（not-afk）的窗口事件
            active_events = filter_period_intersect(window_events, not_afk_events)
            
            return active_events
            
        except Exception as e:
            logger.error(f"获取事件失败: {e}")
            return []
            
    def _process_events_to_stats(
        self, 
        events: List[Event], 
        top_n: int = 20
    ) -> Dict[str, Any]:
        """
        处理事件列表生成统计数据
        
        Args:
            events: 事件列表
            top_n: 返回前N个活跃事件
            
        Returns:
            包含统计信息的字典
        """
        if not events:
            return {
                "total_duration": timedelta(0),
                "event_count": 0,
                "top_apps": []
            }
            
        # 按应用程序合并事件
        merged_events = merge_events_by_keys(events, ["app"])
        
        # 按持续时间排序
        sorted_events = sort_by_duration(merged_events)
        
        # 获取前N个
        top_events = limit_events(sorted_events, top_n)
        
        # 计算总时长
        total_duration = sum_durations(events)
        
        # 生成应用统计
        top_apps = []
        for event in top_events:
            app_name = event.data.get("app", "未知应用")
            duration = event.duration
            percentage = (duration.total_seconds() / total_duration.total_seconds() * 100) if total_duration.total_seconds() > 0 else 0
            
            top_apps.append({
                "app": app_name,
                "duration": duration,
                "duration_str": self._format_duration(duration),
                "percentage": round(percentage, 2)
            })
            
        return {
            "total_duration": total_duration,
            "total_duration_str": self._format_duration(total_duration),
            "event_count": len(events),
            "top_apps": top_apps
        }
        
    def get_aggregated_stats(self, days: int) -> str:
        """
        获取聚合统计数据（7日或1日）
        
        Args:
            days: 天数（7或1）
            
        Returns:
            自然语言格式的统计数据
        """
        hours = days * 24
        events = self._get_events_for_period(hours)
        stats = self._process_events_to_stats(events, top_n=20)
        
        # 生成自然语言描述
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        if not events:
            return f"当前时间是{current_time}，近{days}日暂无活动数据。"
            
        # 构建应用列表描述
        app_descriptions = []
        for i, app_info in enumerate(stats["top_apps"], 1):
            app_desc = f"{i}. {app_info['app']}（{app_info['duration_str']}，占比{app_info['percentage']}%）"
            app_descriptions.append(app_desc)
            
        app_list = "\n".join(app_descriptions)
        
        return (
            f"当前时间是{current_time}，"
            f"近{days}日统计数据：\n"
            f"总统计活跃时长{stats['total_duration_str']}，"
            f"共记录{stats['event_count']}个事件。\n"
            f"其中前{len(stats['top_apps'])}个活跃的应用是：\n{app_list}"
        )
        
    def get_detailed_stats(self, hours: float) -> str:
        """
        获取详细统计数据（2小时、30分钟、5分钟）
        
        Args:
            hours: 小时数（支持小数）
            
        Returns:
            自然语言格式的详细数据
        """
        events = self._get_events_for_period(hours)
        
        # 获取原始事件信息
        raw_event_count = len(events)
        
        # 获取聚合统计
        stats = self._process_events_to_stats(events, top_n=5)
        
        # 生成自然语言描述
        current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
        
        # 转换小时数为更友好的格式
        if hours >= 1:
            time_desc = f"{hours}小时"
        else:
            minutes = int(hours * 60)
            time_desc = f"{minutes}分钟"
            
        if not events:
            return f"当前时间是{current_time}，近{time_desc}暂无活动数据。"
            
        # 获取持续时间最长的事件详情（最多10个）
        # 按持续时间倒序排序，获取时间最长的事件
        sorted_by_duration = sorted(events, key=lambda e: e.duration, reverse=True)
        longest_events = sorted_by_duration[:10]
        longest_events_desc = []
        for i, event in enumerate(longest_events, 1):
            app = event.data.get("app", "未知应用")
            title = event.data.get("title", "")
            if title and len(title) > 50:
                title = title[:50] + "..."
            timestamp = event.timestamp.strftime("%H:%M:%S")
            duration = self._format_duration(event.duration)
            
            event_desc = f"{i}. [{timestamp}] {app}"
            if title:
                event_desc += f" - {title}"
            event_desc += f"（{duration}）"
            longest_events_desc.append(event_desc)
            
        longest_events_str = "\n".join(longest_events_desc)
        
        # 构建应用统计描述
        app_descriptions = []
        for i, app_info in enumerate(stats["top_apps"], 1):
            app_desc = f"{i}. {app_info['app']}（{app_info['duration_str']}，占比{app_info['percentage']}%）"
            app_descriptions.append(app_desc)
            
        app_list = "\n".join(app_descriptions)
        
        return (
            f"当前时间是{current_time}，"
            f"近{time_desc}详细数据：\n\n"
            f"【原始事件流】共{raw_event_count}个事件\n"
            f"持续时间最长的{len(longest_events)}个事件：\n{longest_events_str}\n\n"
            f"【聚合统计】\n"
            f"总统计活跃时长{stats['total_duration_str']}，\n"
            f"其中前{len(stats['top_apps'])}个活跃的应用是：\n{app_list}"
        )
        
    def get_stats_7d(self) -> str:
        """获取7日聚合统计数据"""
        return self.get_aggregated_stats(7)
        
    def get_stats_1d(self) -> str:
        """获取1日聚合统计数据"""
        return self.get_aggregated_stats(1)
        
    def get_stats_2h(self) -> str:
        """获取2小时详细统计数据"""
        return self.get_detailed_stats(2)
        
    def get_stats_30m(self) -> str:
        """获取30分钟详细统计数据"""
        return self.get_detailed_stats(0.5)
        
    def get_stats_5m(self) -> str:
        """获取5分钟详细统计数据"""
        return self.get_detailed_stats(5/60)
    
    def get_afk_time_5m(self) -> Dict[str, Any]:
        """获取过去5分钟的AFK时间
        
        Returns:
            包含AFK秒数和是否持续AFK的字典
        """
        try:
            afk_bucket = self._get_afk_bucket()
            if not afk_bucket:
                return {'afk_seconds': 0, 'continuous_afk': False, 'last_active_seconds_ago': 0}
            
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=5)
            
            events = self.client.get_events(
                afk_bucket,
                start=start_time,
                end=end_time
            )
            
            # 按时间排序事件
            events = sorted(events, key=lambda e: e.timestamp)
            
            # 计算AFK时间和检查连续性
            afk_seconds = 0
            last_active_time = None
            continuous_afk = False
            
            # 查找最近的活动时间
            for event in events:
                if event.data.get('status') == 'afk':
                    afk_seconds += event.duration.total_seconds()
                else:  # status == 'not-afk'
                    # 记录最后一次活动的时间
                    last_active_time = event.timestamp + event.duration
            
            # 检查是否持续AFK
            if last_active_time:
                # 计算距离最后一次活动的时间
                seconds_since_active = (end_time - last_active_time).total_seconds()
                # 如果超过4分钟没有活动，认为是持续AFK
                continuous_afk = seconds_since_active > 240
            elif afk_seconds > 240:
                # 如果没有活动记录且AFK时间超过4分钟，认为是持续AFK
                continuous_afk = True
                seconds_since_active = afk_seconds
            else:
                seconds_since_active = 0
            
            self.logger.debug(f"AFK状态: afk_seconds={afk_seconds:.1f}, "
                            f"continuous_afk={continuous_afk}, "
                            f"last_active={seconds_since_active:.1f}s ago")
            
            return {
                'afk_seconds': afk_seconds,
                'continuous_afk': continuous_afk,
                'last_active_seconds_ago': seconds_since_active
            }
        except Exception as e:
            self.logger.error(f"Failed to get AFK time: {e}")
            return {'afk_seconds': 0, 'continuous_afk': False, 'last_active_seconds_ago': 0}
    
    def get_stats_today(self) -> str:
        """获取今日统计数据（从凌晨4点开始）
        
        Returns:
            今日活动的统计摘要
        """
        try:
            now = datetime.now()
            # 确定今日的开始时间（凌晨4点）
            if now.hour < 4:
                # 如果现在是凌晨0-4点，算作昨天
                start_date = now.date() - timedelta(days=1)
            else:
                start_date = now.date()
            
            start_time = datetime.combine(start_date, datetime.min.time().replace(hour=4))
            start_time = start_time.replace(tzinfo=timezone.utc)
            end_time = datetime.now(timezone.utc)
            
            # 计算时长（小时）
            hours = (end_time - start_time).total_seconds() / 3600
            
            # 使用现有的聚合统计方法
            return self.get_aggregated_stats(hours / 24)  # 转换为天数
        except Exception as e:
            self.logger.error(f"Failed to get today stats: {e}")
            return "无法获取今日统计数据" 