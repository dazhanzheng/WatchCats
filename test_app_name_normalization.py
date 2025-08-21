#!/usr/bin/env python3
"""
测试应用名称标准化功能
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from aw_core.models import Event
from baal.aw_stats.stats_processor import StatsProcessor


def test_app_name_normalization():
    """测试应用名称标准化"""
    
    print("=" * 60)
    print("测试应用名称标准化")
    print("=" * 60)
    
    # 创建测试处理器
    processor = StatsProcessor()
    
    # 测试不同的应用名称
    test_cases = [
        "WatchCats.exe",
        "watchcats",
        "WATCHCATS",
        "Baal Desktop Pet",
        "baal",
        "Desktop Pet",
        "Chrome.exe",
        "微信",
        "飞书",
        "Visual Studio Code"
    ]
    
    print("\n应用名称映射测试:")
    print("-" * 40)
    
    for app_name in test_cases:
        normalized = processor._normalize_app_name(app_name)
        print(f"{app_name:30} -> {normalized}")
    
    print("\n" + "=" * 60)
    
    # 测试事件处理
    print("\n模拟事件处理:")
    print("-" * 40)
    
    # 创建模拟事件
    now = datetime.now(timezone.utc)
    test_events = [
        Event(
            id="1",
            timestamp=now - timedelta(hours=2),
            duration=timedelta(minutes=30),
            data={"app": "WatchCats.exe", "title": "Baal Desktop Pet"}
        ),
        Event(
            id="2", 
            timestamp=now - timedelta(hours=1),
            duration=timedelta(minutes=45),
            data={"app": "Chrome.exe", "title": "GitHub"}
        ),
        Event(
            id="3",
            timestamp=now - timedelta(minutes=30),
            duration=timedelta(minutes=15),
            data={"app": "watchcats", "title": "与巴利对话"}
        ),
    ]
    
    # 处理事件
    stats = processor._process_events_to_stats(test_events, top_n=10)
    
    print(f"总时长: {stats['total_duration_str']}")
    print(f"事件数: {stats['event_count']}")
    print("\n应用统计:")
    
    for i, app_info in enumerate(stats['top_apps'], 1):
        print(f"  {i}. {app_info['app']}")
        print(f"     时长: {app_info['duration_str']}")
        print(f"     占比: {app_info['percentage']}%")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_app_name_normalization()