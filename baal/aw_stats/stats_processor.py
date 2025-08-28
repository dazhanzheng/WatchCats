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
    filter_period_intersect,
    categorize  # 添加分类功能
)
from aw_transform.classify import Rule

from ..desktop_pet.core.logger_config import get_logger, log_performance

logger = logging.getLogger(__name__)


class StatsProcessor:
    """处理 ActivityWatch 统计数据的主类"""
    
    # 默认的应用分类规则
    # 注意：Rule 的正则表达式应该直接使用 'regex' 键，不需要嵌套在 'app' 或 'title' 中
    DEFAULT_CATEGORIES = [
        # 开发工具 - 匹配应用名
        (["工作", "编程开发"], Rule({"regex": r"(?i)(code|vscode|visual studio|pycharm|intellij|eclipse|atom|sublime|vim|neovim|emacs|xcode|android studio)"})),
        # 开发工具 - 匹配标题中的代码文件
        (["工作", "编程开发"], Rule({"regex": r"(?i)\.(py|js|java|cpp|c|h|go|rs|tsx?|jsx?|vue|swift|kt|rb|php|cs)(\s|$)"})),
        # 开发工具 - 匹配标题中的开发网站
        (["工作", "编程开发"], Rule({"regex": r"(?i)(github|gitlab|bitbucket|stackoverflow|localhost|127\.0\.0\.1|0\.0\.0\.0)"})),
        
        # 终端和命令行
        (["工作", "命令行"], Rule({"regex": r"(?i)(terminal|iterm|konsole|cmd|powershell|bash|zsh|fish|终端|命令行)"})),
        
        # 文档和笔记
        (["工作", "文档处理"], Rule({"regex": r"(?i)(word|excel|powerpoint|wps|libreoffice|pages|numbers|keynote|google docs|google sheets)"})),
        (["工作", "笔记"], Rule({"regex": r"(?i)(notion|obsidian|roam|evernote|onenote|bear|typora|joplin|语雀|印象笔记)"})),
        
        # 设计工具
        (["工作", "设计"], Rule({"regex": r"(?i)(photoshop|illustrator|figma|sketch|adobe|affinity|canva|blender|maya|c4d)"})),
        
        # 通讯工具
        (["通讯", "即时消息"], Rule({"regex": r"(?i)(slack|teams|discord|telegram|whatsapp|微信|wechat|qq|钉钉|dingtalk|飞书|feishu|lark)"})),
        (["通讯", "邮件"], Rule({"regex": r"(?i)(mail|outlook|thunderbird|gmail|邮件|邮箱)"})),
        (["通讯", "会议"], Rule({"regex": r"(?i)(zoom|meeting|会议|腾讯会议|钉钉会议|飞书会议|teams|meet|webex)"})),
        
        # 浏览器分类 - 需要同时检查应用和标题
        # 工作相关网站
        (["浏览器", "工作相关"], Rule({"regex": r"(?i)(stackoverflow|github|gitlab|docs|documentation|api|tutorial|guide|jira|confluence|jenkins|aws|azure|gcp|docker)"})),
        # 学习网站
        (["浏览器", "学习"], Rule({"regex": r"(?i)(coursera|udemy|edx|khan|学习|教程|course|lecture|tutorial|慕课|网易公开课|极客时间)"})),
        # 娱乐网站
        (["浏览器", "娱乐"], Rule({"regex": r"(?i)(youtube|netflix|bilibili|抖音|douyin|twitch|spotify|网易云|酷狗|qq音乐|b站|哔哩哔哩)"})),
        # 社交媒体
        (["浏览器", "社交媒体"], Rule({"regex": r"(?i)(twitter|facebook|instagram|reddit|知乎|微博|小红书|linkedin|豆瓣)"})),
        # 购物网站
        (["浏览器", "购物"], Rule({"regex": r"(?i)(淘宝|京东|amazon|ebay|拼多多|天猫|shopping|shop|store|商城|购物)"})),
        # 通用浏览器（作为后备）
        (["浏览器", "其他"], Rule({"regex": r"(?i)(chrome|safari|firefox|edge|brave|opera|浏览器|browser)"})),
        
        # 娱乐应用
        (["娱乐", "游戏"], Rule({"regex": r"(?i)(steam|epic|origin|battle\.net|游戏|game|minecraft|league|dota|csgo|valorant|overwatch|原神|王者荣耀)"})),
        (["娱乐", "视频"], Rule({"regex": r"(?i)(爱奇艺|腾讯视频|优酷|netflix|youtube|bilibili|vlc|mpv|quicktime|potplayer|影音|播放器)"})),
        (["娱乐", "音乐"], Rule({"regex": r"(?i)(spotify|apple music|网易云音乐|qq音乐|酷狗|酷我|music|音乐|xiami|虾米)"})),
        
        # 系统工具
        (["系统", "文件管理"], Rule({"regex": r"(?i)(finder|explorer|nautilus|dolphin|访达|文件管理|file manager|资源管理器)"})),
        (["系统", "系统设置"], Rule({"regex": r"(?i)(系统偏好设置|system preferences|settings|控制面板|control panel|设置)"})),
        
        # AI 助手
        (["AI工具"], Rule({"regex": r"(?i)(chatgpt|claude|copilot|cursor|bard|文心一言|通义千问|gemini|poe|perplexity)"})),
        (["AI工具"], Rule({"regex": r"(?i)(openai|anthropic|midjourney|stable diffusion|dall-e)"})),
        
        # macOS 特定应用
        (["系统", "macOS工具"], Rule({"regex": r"(?i)(preview|预览|活动监视器|activity monitor|磁盘工具|disk utility)"})),
    ]
    
    def __init__(self, client_name: str = None, testing: bool = False, custom_categories: List[Tuple] = None, use_user_categories: bool = True):
        # 生成唯一的客户端名称以避免冲突
        if client_name is None:
            import random
            client_name = f"aw-stats-processor-{random.randint(1000, 9999)}"
        """
        初始化统计处理器
        
        Args:
            client_name: 客户端名称
            testing: 是否使用测试模式
            custom_categories: 自定义分类规则（可选），格式同 DEFAULT_CATEGORIES
            use_user_categories: 是否使用用户自定义分类（默认True）
        """
        # 先初始化logger
        self.logger = get_logger('baal.aw_stats.stats_processor')
        
        # 设置分类规则
        if custom_categories:
            self.categories = custom_categories
            self.productivity_map = {}
        elif use_user_categories:
            # 尝试加载用户自定义的工作软件列表
            try:
                from ..desktop_pet.core.category_manager import CategoryManager
                self.category_manager = CategoryManager()
                self.logger.info(f"加载了 {len(self.category_manager.get_work_apps())} 个工作软件")
            except Exception as e:
                self.logger.warning(f"加载工作软件管理器失败: {e}")
                self.category_manager = None
            
            # 使用默认分类规则（简化后不再使用复杂的aw_transform规则）
            self.categories = self.DEFAULT_CATEGORIES
            self.productivity_map = {}
        else:
            self.categories = self.DEFAULT_CATEGORIES
            self.productivity_map = {}
            self.category_manager = None
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
        
    def _get_events_paginated(self, bucket_id: str, start: datetime, end: datetime, limit: int = 5000) -> List[Event]:
        """
        获取事件，带有数量限制以避免内存问题
        
        Args:
            bucket_id: 桶ID
            start: 开始时间
            end: 结束时间
            limit: 最大事件数量
            
        Returns:
            事件列表
        """
        try:
            # 使用limit参数限制返回的事件数量
            events = self.client.get_events(
                bucket_id, 
                start=start, 
                end=end,
                limit=limit  # 限制最大返回数量
            )
            
            if len(events) == limit:
                logger.warning(f"事件数量达到限制 {limit}，可能有更多事件未加载")
            
            return events
        except Exception as e:
            logger.error(f"获取事件失败: {e}")
            return []
    
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
            # 获取窗口事件，限制数量以防止内存问题
            window_events = self._get_events_paginated(
                window_bucket_id, 
                start=start_time, 
                end=end_time,
                limit=2000  # 限制最多2000个窗口事件
            )
            
            if not afk_bucket_id:
                # 如果没有 AFK 桶，返回所有窗口事件
                return window_events
                
            # 获取 AFK 事件，限制数量
            afk_events = self._get_events_paginated(
                afk_bucket_id,
                start=start_time,
                end=end_time,
                limit=1000  # AFK事件通常较少，1000应该足够
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
            
    def _categorize_events(self, events: List[Event]) -> List[Event]:
        """
        对事件进行分类
        
        Args:
            events: 事件列表
            
        Returns:
            带分类信息的事件列表
        """
        if not events:
            return events
            
        try:
            # 使用分类规则对事件进行分类
            categorized = categorize(events, self.categories)
            return categorized
        except Exception as e:
            self.logger.warning(f"分类失败: {e}，返回原始事件")
            return events
    
    def _normalize_app_name(self, app_name: str) -> str:
        """
        标准化应用名称，处理特殊应用
        
        Args:
            app_name: 原始应用名称
            
        Returns:
            标准化后的应用名称
        """
        if not app_name:
            return "未知应用"
            
        # 转换为小写进行比较
        app_lower = app_name.lower()
        
        # 将 WatchCats 或 Watch Cats 识别为巴利自己
        if "watchcats" in app_lower.replace(" ", "") or "watch cats" in app_lower:
            return "巴利桌面宠物（与主人互动）"
        
        # 将 Baal 相关应用识别为巴利自己
        if "baal" in app_lower or "desktop pet" in app_lower or "桌面宠物" in app_name:
            return "巴利桌面宠物（与主人互动）"
            
        # 移除常见的文件扩展名
        if app_name.endswith(".exe"):
            app_name = app_name[:-4]
        elif app_name.endswith(".app"):
            app_name = app_name[:-4]
            
        return app_name
    
    def _process_events_to_stats(
        self, 
        events: List[Event], 
        top_n: int = 20,
        include_categories: bool = True
    ) -> Dict[str, Any]:
        """
        处理事件列表生成统计数据
        
        Args:
            events: 事件列表
            top_n: 返回前N个活跃事件
            include_categories: 是否包含分类信息
            
        Returns:
            包含统计信息的字典
        """
        if not events:
            return {
                "total_duration": timedelta(0),
                "event_count": 0,
                "top_apps": [],
                "category_stats": []
            }
            
        # 按应用程序合并事件，但先标准化应用名称
        normalized_events = []
        for event in events:
            event_copy = Event(
                id=event.id,
                timestamp=event.timestamp,
                duration=event.duration,
                data={
                    **event.data,
                    "app": self._normalize_app_name(event.data.get("app", "未知应用"))
                }
            )
            normalized_events.append(event_copy)
        
        # 按应用程序合并事件
        merged_events = merge_events_by_keys(normalized_events, ["app"])
        
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
        
        # 如果需要分类信息，对事件进行分类
        category_stats = []
        if include_categories:
            # 对原始事件进行分类
            categorized_events = self._categorize_events(events)
            
            # 统计每个分类的时间
            category_durations = defaultdict(timedelta)
            for event in categorized_events:
                category = event.data.get("$category", ["未分类"])
                category_str = " > ".join(category)  # 将层级分类转换为字符串
                category_durations[category_str] += event.duration
            
            # 按时长排序分类
            sorted_categories = sorted(category_durations.items(), key=lambda x: x[1], reverse=True)
            
            # 生成分类统计
            for category_name, duration in sorted_categories[:10]:  # 只取前10个分类
                percentage = (duration.total_seconds() / total_duration.total_seconds() * 100) if total_duration.total_seconds() > 0 else 0
                category_stats.append({
                    "category": category_name,
                    "duration": duration,
                    "duration_str": self._format_duration(duration),
                    "percentage": round(percentage, 2)
                })
            
        return {
            "total_duration": total_duration,
            "total_duration_str": self._format_duration(total_duration),
            "event_count": len(events),
            "top_apps": top_apps,
            "category_stats": category_stats
        }
        
    def get_aggregated_stats(self, days: int, include_categories: bool = True) -> str:
        """
        获取聚合统计数据（7日或1日）
        
        Args:
            days: 天数（7或1）
            include_categories: 是否包含分类统计
            
        Returns:
            自然语言格式的统计数据
        """
        hours = days * 24
        events = self._get_events_for_period(hours)
        stats = self._process_events_to_stats(events, top_n=20, include_categories=include_categories)
        
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
        
        result = (
            f"当前时间是{current_time}，"
            f"近{days}日统计数据：\n"
            f"总统计活跃时长{stats['total_duration_str']}，"
            f"共记录{stats['event_count']}个事件。\n"
            f"其中前{len(stats['top_apps'])}个活跃的应用是：\n{app_list}"
        )
        
        # 如果有分类统计，添加分类信息
        if include_categories and stats.get("category_stats"):
            category_descriptions = []
            for i, cat_info in enumerate(stats["category_stats"][:5], 1):  # 只显示前5个分类
                cat_desc = f"{i}. {cat_info['category']}（{cat_info['duration_str']}，占比{cat_info['percentage']}%）"
                category_descriptions.append(cat_desc)
            
            category_list = "\n".join(category_descriptions)
            result += f"\n\n【活动分类统计】\n{category_list}"
        
        return result
        
    def get_detailed_stats(self, hours: float, include_categories: bool = True) -> str:
        """
        获取详细统计数据（2小时、30分钟、5分钟）
        
        Args:
            hours: 小时数（支持小数）
            include_categories: 是否包含分类统计
            
        Returns:
            自然语言格式的详细数据
        """
        events = self._get_events_for_period(hours)
        
        # 获取原始事件信息
        raw_event_count = len(events)
        
        # 获取聚合统计
        stats = self._process_events_to_stats(events, top_n=5, include_categories=include_categories)
        
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
            app = self._normalize_app_name(event.data.get("app", "未知应用"))
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
        
        result = (
            f"当前时间是{current_time}，"
            f"近{time_desc}详细数据：\n\n"
            f"【原始事件流】共{raw_event_count}个事件\n"
            f"持续时间最长的{len(longest_events)}个事件：\n{longest_events_str}\n\n"
            f"【聚合统计】\n"
            f"总统计活跃时长{stats['total_duration_str']}，\n"
            f"其中前{len(stats['top_apps'])}个活跃的应用是：\n{app_list}"
        )
        
        # 如果有分类统计，添加分类信息
        if include_categories and stats.get("category_stats"):
            category_descriptions = []
            for cat_info in stats["category_stats"][:3]:  # 详细统计只显示前3个分类
                cat_desc = f"- {cat_info['category']}（{cat_info['duration_str']}，占比{cat_info['percentage']}%）"
                category_descriptions.append(cat_desc)
            
            if category_descriptions:
                category_list = "\n".join(category_descriptions)
                result += f"\n\n【活动分类】\n{category_list}"
        
        return result
        
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
    
    def get_category_stats(self, hours: float) -> Dict[str, Any]:
        """
        获取指定时间段内的分类统计数据
        
        Args:
            hours: 小时数
            
        Returns:
            分类统计字典，包含各分类的时间和占比
        """
        events = self._get_events_for_period(hours)
        
        if not events:
            return {"categories": [], "total_duration": timedelta(0)}
        
        # 对事件进行分类
        categorized_events = self._categorize_events(events)
        
        # 统计每个分类的时间
        category_durations = defaultdict(timedelta)
        for event in categorized_events:
            category = event.data.get("$category", ["未分类"])
            category_str = " > ".join(category)
            category_durations[category_str] += event.duration
        
        # 计算总时长
        total_duration = sum_durations(events)
        
        # 按时长排序
        sorted_categories = sorted(category_durations.items(), key=lambda x: x[1], reverse=True)
        
        # 生成结果
        categories = []
        for category_name, duration in sorted_categories:
            percentage = (duration.total_seconds() / total_duration.total_seconds() * 100) if total_duration.total_seconds() > 0 else 0
            categories.append({
                "name": category_name,
                "duration": duration,
                "duration_str": self._format_duration(duration),
                "percentage": round(percentage, 2)
            })
        
        return {
            "categories": categories,
            "total_duration": total_duration,
            "total_duration_str": self._format_duration(total_duration)
        }
    
    def get_productive_vs_unproductive_stats(self, hours: float) -> Dict[str, Any]:
        """
        获取生产力与非生产力活动的统计对比
        
        Args:
            hours: 小时数
            
        Returns:
            生产力分析结果
        """
        # 获取原始事件数据而不是分类统计
        events = self._get_events_for_period(hours)
        
        if not events:
            return {
                "productive_time": timedelta(0),
                "unproductive_time": timedelta(0),
                "neutral_time": timedelta(0),
                "productive_percentage": 0,
                "analysis": "暂无活动数据"
            }
        
        # 加载工作软件列表
        work_apps = []
        if hasattr(self, 'category_manager') and self.category_manager:
            work_apps = self.category_manager.get_work_apps()
        
        # 定义生产力分类关键词（作为默认）
        productive_keywords = ["工作", "编程", "文档", "笔记", "设计", "学习", "AI工具", "code", "vscode", "pycharm", "intellij"]
        unproductive_keywords = ["娱乐", "游戏", "视频", "音乐", "社交媒体", "购物", "bilibili", "youtube", "netflix"]
        
        productive_time = timedelta(0)
        unproductive_time = timedelta(0)
        neutral_time = timedelta(0)
        
        # 遍历事件，根据应用名称判断生产力
        for event in events:
            app_name = event.data.get("app", "")
            duration = event.duration
            
            # 检查是否为工作软件
            is_work_app = False
            if work_apps and app_name:
                app_lower = app_name.lower()
                for work_app in work_apps:
                    if work_app.lower() in app_lower or app_lower in work_app.lower():
                        is_work_app = True
                        break
            
            if is_work_app:
                productive_time += duration
            else:
                # 使用默认关键词判断
                app_lower = app_name.lower()
                is_productive = any(keyword.lower() in app_lower for keyword in productive_keywords)
                is_unproductive = any(keyword.lower() in app_lower for keyword in unproductive_keywords)
                
                if is_productive:
                    productive_time += duration
                elif is_unproductive:
                    unproductive_time += duration
                else:
                    neutral_time += duration
        
        total_time = productive_time + unproductive_time + neutral_time
        productive_percentage = (productive_time.total_seconds() / total_time.total_seconds() * 100) if total_time.total_seconds() > 0 else 0
        
        # 生成分析
        if productive_percentage >= 70:
            analysis = "非常高效！大部分时间用于生产性活动"
        elif productive_percentage >= 50:
            analysis = "效率良好，保持平衡的工作状态"
        elif productive_percentage >= 30:
            analysis = "效率一般，建议增加专注工作时间"
        else:
            analysis = "效率较低，大量时间用于非生产性活动"
        
        return {
            "productive_time": productive_time,
            "productive_time_str": self._format_duration(productive_time),
            "unproductive_time": unproductive_time,
            "unproductive_time_str": self._format_duration(unproductive_time),
            "neutral_time": neutral_time,
            "neutral_time_str": self._format_duration(neutral_time),
            "productive_percentage": round(productive_percentage, 2),
            "analysis": analysis
        }
    
    def get_stats_today(self) -> str:
        """获取今日统计数据（从凌晨4点开始）
        
        Returns:
            今日活动的统计摘要
        """
        try:
            now = datetime.now(timezone.utc)
            # 确定今日的开始时间（凌晨4点）
            if now.hour < 4:
                # 如果现在是凌晨0-4点，算作昨天
                start_date = now.date() - timedelta(days=1)
            else:
                start_date = now.date()
            
            # 设置开始时间为凌晨4点
            start_time = datetime.combine(start_date, datetime.min.time().replace(hour=4))
            start_time = start_time.replace(tzinfo=timezone.utc)
            end_time = now
            
            # 计算时长（小时）
            hours = (end_time - start_time).total_seconds() / 3600
            
            # 获取今天的事件
            events = self._get_events_for_period(hours)
            stats = self._process_events_to_stats(events, top_n=20)
            
            # 生成自然语言描述
            current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
            
            if not events:
                return f"当前时间是{current_time}，今日（从凌晨4点开始）暂无活动数据。"
                
            # 构建应用列表描述
            app_descriptions = []
            for i, app_info in enumerate(stats["top_apps"], 1):
                app_desc = f"{i}. {app_info['app']}（{app_info['duration_str']}，占比{app_info['percentage']}%）"
                app_descriptions.append(app_desc)
                
            app_list = "\n".join(app_descriptions)
            
            return (
                f"当前时间是{current_time}，"
                f"今日（从凌晨4点开始）统计数据：\n"
                f"总统计活跃时长{stats['total_duration_str']}，"
                f"共记录{stats['event_count']}个事件。\n"
                f"其中前{len(stats['top_apps'])}个活跃的应用是：\n{app_list}"
            )
        except Exception as e:
            self.logger.error(f"Failed to get today stats: {e}")
            return "无法获取今日统计数据" 