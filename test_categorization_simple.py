#!/usr/bin/env python3
"""
测试 ActivityWatch 应用分类功能（独立版本）
"""

from datetime import datetime, timedelta, timezone
from collections import defaultdict
import logging

from aw_client import ActivityWatchClient
from aw_core import Event
from aw_transform import (
    categorize,
    sum_durations
)
from aw_transform.classify import Rule

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 定义分类规则
CATEGORIES = [
    # 开发工具
    (["工作", "编程开发"], Rule({"app": {"regex": r"(?i)(code|vscode|visual studio|pycharm|intellij|eclipse|atom|sublime|vim|neovim|emacs|xcode|android studio)"}})),
    (["工作", "编程开发"], Rule({"title": {"regex": r"(?i)(github|gitlab|bitbucket|\.py$|\.js$|\.java$|\.cpp$|\.c$|\.h$|\.go$|\.rs$)"}})),
    
    # 终端
    (["工作", "命令行"], Rule({"app": {"regex": r"(?i)(terminal|iterm|konsole|cmd|powershell|bash|zsh|fish)"}})),
    
    # 通讯工具
    (["通讯", "即时消息"], Rule({"app": {"regex": r"(?i)(slack|teams|discord|telegram|whatsapp|微信|wechat|qq|钉钉|dingtalk|飞书|feishu|lark)"}})),
    
    # 浏览器
    (["浏览器", "工作相关"], Rule({"app": {"regex": r"(?i)(chrome|safari|firefox|edge)"}, "title": {"regex": r"(?i)(stackoverflow|github|docs|documentation|api)"}})),
    (["浏览器", "娱乐"], Rule({"app": {"regex": r"(?i)(chrome|safari|firefox|edge)"}, "title": {"regex": r"(?i)(youtube|netflix|bilibili)"}})),
    (["浏览器", "其他"], Rule({"app": {"regex": r"(?i)(chrome|safari|firefox|edge)"}})),
    
    # 娱乐
    (["娱乐", "游戏"], Rule({"app": {"regex": r"(?i)(steam|epic|game|minecraft)"}})),
    (["娱乐", "视频"], Rule({"app": {"regex": r"(?i)(vlc|mpv|quicktime|爱奇艺|腾讯视频)"}})),
]

def format_duration(duration):
    """格式化时长"""
    total_seconds = int(duration.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    parts = []
    if hours > 0:
        parts.append(f"{hours}小时")
    if minutes > 0:
        parts.append(f"{minutes}分钟")
    if seconds > 0 or not parts:
        parts.append(f"{seconds}秒")
    
    return "".join(parts)

def test():
    """测试分类功能"""
    
    print("=" * 60)
    print("ActivityWatch 分类功能测试")
    print("=" * 60)
    
    try:
        # 连接 ActivityWatch
        client = ActivityWatchClient("test-categorization", testing=False)
        
        # 获取窗口监视器桶
        buckets = client.get_buckets()
        window_bucket = None
        
        for bucket_id in buckets:
            if "window" in bucket_id and "watcher" in bucket_id:
                window_bucket = bucket_id
                break
        
        if not window_bucket:
            print("未找到窗口监视器桶")
            return
        
        print(f"\n使用桶: {window_bucket}")
        
        # 获取最近1小时的事件
        end_time = datetime.now(timezone.utc)
        start_time = end_time - timedelta(hours=1)
        
        print(f"时间范围: {start_time.strftime('%H:%M')} - {end_time.strftime('%H:%M')}")
        
        events = client.get_events(
            window_bucket,
            start=start_time,
            end=end_time,
            limit=500
        )
        
        print(f"获取到 {len(events)} 个事件")
        
        if not events:
            print("没有事件数据")
            return
        
        # 对事件进行分类
        categorized = categorize(events, CATEGORIES)
        
        # 统计分类
        category_durations = defaultdict(timedelta)
        app_categories = defaultdict(set)  # 记录每个应用的分类
        
        for event in categorized:
            app = event.data.get("app", "未知")
            # 检查 $category 字段是否存在
            if "$category" in event.data:
                category = event.data["$category"]
            else:
                category = ["未分类"]
            category_str = " > ".join(category)
            
            category_durations[category_str] += event.duration
            app_categories[app].add(category_str)
        
        # 计算总时长
        total_duration = sum_durations(events)
        
        # 显示分类统计
        print(f"\n总活跃时长: {format_duration(total_duration)}")
        print("\n" + "=" * 60)
        print("分类统计:")
        print("-" * 60)
        
        sorted_categories = sorted(category_durations.items(), key=lambda x: x[1], reverse=True)
        
        for i, (category, duration) in enumerate(sorted_categories, 1):
            percentage = (duration.total_seconds() / total_duration.total_seconds() * 100)
            print(f"{i:2d}. {category:<30} {format_duration(duration):>15} ({percentage:>5.1f}%)")
        
        # 显示应用分类映射
        print("\n" + "=" * 60)
        print("应用分类映射（前10个应用）:")
        print("-" * 60)
        
        sorted_apps = sorted(app_categories.items())[:10]
        for app, categories in sorted_apps:
            cat_list = ", ".join(sorted(categories))
            print(f"- {app}: {cat_list}")
        
        # 生产力分析
        print("\n" + "=" * 60)
        print("生产力分析:")
        print("-" * 60)
        
        productive_time = timedelta(0)
        unproductive_time = timedelta(0)
        neutral_time = timedelta(0)
        
        productive_keywords = ["工作", "编程", "命令行"]
        unproductive_keywords = ["娱乐", "游戏", "视频"]
        
        for category, duration in category_durations.items():
            if any(kw in category for kw in productive_keywords):
                productive_time += duration
            elif any(kw in category for kw in unproductive_keywords):
                unproductive_time += duration
            else:
                neutral_time += duration
        
        prod_pct = (productive_time.total_seconds() / total_duration.total_seconds() * 100) if total_duration.total_seconds() > 0 else 0
        
        print(f"生产性活动: {format_duration(productive_time)} ({prod_pct:.1f}%)")
        print(f"非生产性活动: {format_duration(unproductive_time)}")
        print(f"中性活动: {format_duration(neutral_time)}")
        
        if prod_pct >= 70:
            print("评价: 非常高效！")
        elif prod_pct >= 50:
            print("评价: 效率良好")
        elif prod_pct >= 30:
            print("评价: 效率一般")
        else:
            print("评价: 效率较低")
        
        client.disconnect()
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)

if __name__ == "__main__":
    test()