#!/usr/bin/env python3
"""
测试 ActivityWatch 应用分类功能
"""

import sys
import os
import json
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 直接导入必要的模块，避免循环导入
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Optional, Any
from collections import defaultdict
import logging

from aw_client import ActivityWatchClient
from aw_core import Event
from aw_transform import (
    merge_events_by_keys,
    sort_by_duration,
    sum_durations,
    limit_events,
    filter_keyvals,
    filter_period_intersect,
    categorize
)
from aw_transform.classify import Rule

# 直接使用 StatsProcessor 的代码
from baal.aw_stats.stats_processor import StatsProcessor

def test_categorization():
    """测试分类功能"""
    
    print("=" * 60)
    print("ActivityWatch 应用分类测试")
    print("=" * 60)
    
    try:
        # 创建 StatsProcessor 实例
        with StatsProcessor(client_name="test-categorization") as processor:
            
            # 1. 获取最近2小时的分类统计
            print("\n1. 最近2小时的分类统计：")
            print("-" * 40)
            category_stats = processor.get_category_stats(2)
            
            if category_stats["categories"]:
                print(f"总活跃时长: {category_stats['total_duration_str']}")
                print("\n各分类时间分布:")
                for i, cat in enumerate(category_stats["categories"][:10], 1):
                    print(f"{i:2d}. {cat['name']:<30} {cat['duration_str']:>15} ({cat['percentage']:>5.1f}%)")
            else:
                print("暂无活动数据")
            
            # 2. 获取生产力分析
            print("\n2. 生产力分析：")
            print("-" * 40)
            productivity = processor.get_productive_vs_unproductive_stats(2)
            
            print(f"生产性活动: {productivity['productive_time_str']} ({productivity['productive_percentage']:.1f}%)")
            print(f"非生产性活动: {productivity['unproductive_time_str']}")
            print(f"中性活动: {productivity['neutral_time_str']}")
            print(f"评价: {productivity['analysis']}")
            
            # 3. 测试带分类的聚合统计
            print("\n3. 今日统计（带分类）：")
            print("-" * 40)
            stats = processor.get_aggregated_stats(1, include_categories=True)
            print(stats)
            
            # 4. 测试5分钟详细统计（带分类）
            print("\n4. 最近5分钟详细统计（带分类）：")
            print("-" * 40)
            detailed = processor.get_detailed_stats(5/60, include_categories=True)
            print(detailed)
            
            # 5. 显示默认分类规则
            print("\n5. 当前使用的分类规则概览：")
            print("-" * 40)
            
            # 统计各主分类的规则数
            main_categories = {}
            for category_path, rule in processor.categories:
                main_cat = category_path[0]
                if main_cat not in main_categories:
                    main_categories[main_cat] = []
                if len(category_path) > 1:
                    main_categories[main_cat].append(category_path[1])
                else:
                    main_categories[main_cat].append("")
            
            for main_cat, sub_cats in sorted(main_categories.items()):
                unique_subs = set(sub_cats) - {""}
                if unique_subs:
                    print(f"- {main_cat}: {', '.join(sorted(unique_subs))}")
                else:
                    print(f"- {main_cat}")
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    print("\n注意事项：")
    print("1. 分类规则基于应用名称和窗口标题的正则匹配")
    print("2. 同一个应用可能根据窗口标题被分到不同类别")
    print("3. 浏览器活动会根据网站内容进行细分")
    print("4. 可以通过 custom_categories 参数自定义分类规则")

if __name__ == "__main__":
    test_categorization()