#!/usr/bin/env python3
"""
测试监督模式的保护机制
确保用户在使用工作软件时不会被错误批评
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baal.desktop_pet.supervision_mode import SupervisionMode
from baal.desktop_pet.core.category_manager import CategoryManager
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_work_app_protection():
    """测试工作软件保护机制"""
    print("\n" + "="*60)
    print("测试监督模式的工作软件保护机制")
    print("="*60)
    
    # 初始化类别管理器
    category_manager = CategoryManager()
    print(f"\n当前配置的工作软件：")
    for app in category_manager.get_work_apps():
        print(f"  - {app}")
    
    # 模拟不同的活动数据场景
    test_scenarios = [
        {
            "name": "使用VSCode编程",
            "stats": {
                "stats_5m": "当前时间是2025年08月29日，过去5分钟统计数据：\n1. Visual Studio Code（4分30秒，占比90%）\n2. Chrome（30秒，占比10%）",
                "stats_2h": "过去2小时主要使用VSCode和Chrome",
                "productivity_analysis": {
                    "productive_percentage": 85.0,
                    "analysis": "非常高效！大部分时间用于生产性活动"
                }
            },
            "expected": "不应该提醒"
        },
        {
            "name": "使用飞书办公",
            "stats": {
                "stats_5m": "当前时间是2025年08月29日，过去5分钟统计数据：\n1. 飞书（5分钟，占比100%）",
                "stats_2h": "过去2小时主要使用飞书",
                "productivity_analysis": {
                    "productive_percentage": 60.0,
                    "analysis": "效率良好，保持平衡的工作状态"
                }
            },
            "expected": "不应该提醒"
        },
        {
            "name": "看视频摸鱼",
            "stats": {
                "stats_5m": "当前时间是2025年08月29日，过去5分钟统计数据：\n1. Chrome - Bilibili（4分钟，占比80%）\n2. 微信（1分钟，占比20%）",
                "stats_2h": "过去2小时主要在看视频",
                "productivity_analysis": {
                    "productive_percentage": 10.0,
                    "analysis": "效率较低，大量时间用于非生产性活动"
                }
            },
            "expected": "应该提醒"
        },
        {
            "name": "混合活动但生产力高",
            "stats": {
                "stats_5m": "当前时间是2025年08月29日，过去5分钟统计数据：\n1. PyCharm（3分钟，占比60%）\n2. 微信（2分钟，占比40%）",
                "stats_2h": "过去2小时编程和聊天混合",
                "productivity_analysis": {
                    "productive_percentage": 55.0,
                    "analysis": "效率良好，保持平衡的工作状态"
                }
            },
            "expected": "不应该提醒（生产力>50%）"
        }
    ]
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    supervision.category_manager = category_manager
    
    # 设置目标
    supervision.long_term_goal = "完成项目开发"
    supervision.short_term_goals = ["写代码", "看文档", "开会"]
    
    print(f"\n监督目标设置：")
    print(f"  长期目标：{supervision.long_term_goal}")
    print(f"  短期目标：{supervision.short_term_goals}")
    
    # 测试每个场景
    for scenario in test_scenarios:
        print(f"\n\n场景：{scenario['name']}")
        print("-" * 40)
        
        # 调用评估方法
        result = supervision._evaluate_activity_enhanced(scenario['stats'])
        
        if result:
            should_remind = result.get('should_remind', False)
            deviation_level = result.get('deviation_level', '未知')
            analysis = result.get('analysis', '')
            
            print(f"评估结果：")
            print(f"  - 是否提醒：{'是' if should_remind else '否'}")
            print(f"  - 偏离等级：{deviation_level}")
            print(f"  - 分析：{analysis[:100]}...")
            print(f"  - 预期结果：{scenario['expected']}")
            
            # 验证结果是否符合预期
            if "不应该提醒" in scenario['expected']:
                if should_remind:
                    print(f"  ❌ 错误：不应该提醒但系统判断要提醒")
                else:
                    print(f"  ✅ 正确：系统正确判断不需要提醒")
            elif "应该提醒" in scenario['expected']:
                if not should_remind:
                    print(f"  ❌ 错误：应该提醒但系统判断不提醒")
                else:
                    print(f"  ✅ 正确：系统正确判断需要提醒")
        else:
            print(f"  ⚠️ 评估返回None（可能没有配置LLM）")

if __name__ == "__main__":
    test_work_app_protection()