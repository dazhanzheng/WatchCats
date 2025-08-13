#!/usr/bin/env python3
"""
强制测试监督模式提醒功能
绕过AFK检测，直接测试评估和提醒
"""

import sys
import os
from pathlib import Path
from datetime import datetime

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from baal.desktop_pet.supervision_mode import SupervisionMode
from PyQt6.QtWidgets import QApplication
import json


def test_force_reminder():
    """强制触发提醒进行测试"""
    print("=== 强制测试监督模式提醒 ===\n")
    
    # 创建Qt应用（用于信号）
    app = QApplication(sys.argv)
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    
    # 设置测试目标
    supervision.long_term_goal = "专注编程，完成项目"
    supervision.short_term_goals = ["写代码", "测试功能", "修复bug"]
    
    print("1. 监督目标已设置")
    print(f"   长期目标: {supervision.long_term_goal}")
    print(f"   短期目标: {supervision.short_term_goals}")
    
    # 连接信号
    reminder_received = [False]
    
    def on_reminder(context):
        print("\n✅ 收到监督提醒!")
        print(f"   类型: {context.get('type')}")
        print(f"   消息: {context.get('reminder_message', '无')}")
        print(f"   偏离程度: {context.get('deviation_level', '未知')}")
        reminder_received[0] = True
        app.quit()
    
    supervision.reminder_needed.connect(on_reminder)
    
    # 临时修改AFK检测，强制返回False
    original_is_afk = supervision._is_user_afk
    supervision._is_user_afk = lambda: False
    
    print("\n2. 绕过AFK检测，强制执行评估")
    
    # 构造测试数据
    test_stats = {
        'stats_5m': "过去5分钟的活动:\n1. Chrome（3分钟）\n2. YouTube（2分钟）",
        'stats_2h': "过去2小时：主要在看视频和浏览网页",
        'stats_today': "今日：编程1小时，娱乐3小时",
        'timestamp': datetime.now().isoformat()
    }
    
    # 如果有LLM助手，直接调用评估
    if supervision.llm_assistant:
        print("\n3. 调用LLM评估...")
        try:
            # 直接调用评估
            result = supervision._evaluate_activity_enhanced(test_stats)
            
            if result:
                print(f"\n4. 评估结果:")
                print(f"   需要提醒: {result.get('should_remind')}")
                print(f"   偏离程度: {result.get('deviation_level')}")
                print(f"   分析: {result.get('analysis')}")
                print(f"   提醒消息: {result.get('reminder_message')}")
                
                if result.get('should_remind'):
                    print("\n5. 发送提醒信号...")
                    context = supervision._create_enhanced_reminder_context(test_stats, result)
                    supervision.reminder_needed.emit(context)
                    
                    # 运行事件循环一小段时间
                    import threading
                    timer = threading.Timer(0.5, app.quit)
                    timer.start()
                    app.exec()
                    
                    if reminder_received[0]:
                        print("\n✅ 提醒功能正常工作!")
                    else:
                        print("\n⚠️ 未收到提醒信号")
                else:
                    print("\n⚠️ LLM判断不需要提醒")
            else:
                print("\n❌ 评估返回为空")
                
        except Exception as e:
            print(f"\n❌ 评估出错: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n❌ LLM助手未初始化")
        
        # 手动创建提醒测试
        print("\n6. 手动创建提醒进行测试...")
        test_context = {
            'type': 'supervision_reminder',
            'long_term_goal': supervision.long_term_goal,
            'short_term_goals': supervision.short_term_goals,
            'reminder_message': '测试提醒：你在看视频，赶紧回去写代码！',
            'deviation_level': '严重',
            'timestamp': datetime.now().isoformat()
        }
        
        supervision.reminder_needed.emit(test_context)
        
        # 运行事件循环
        import threading
        timer = threading.Timer(0.5, app.quit)
        timer.start()
        app.exec()
        
        if reminder_received[0]:
            print("\n✅ 手动提醒测试成功!")
    
    # 恢复原始方法
    supervision._is_user_afk = original_is_afk
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_force_reminder()