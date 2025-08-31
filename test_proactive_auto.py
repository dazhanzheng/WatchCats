#!/usr/bin/env python3
"""
自动测试主动对话功能
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from baal.desktop_pet.core.proactive_dialogue_manager import get_dialogue_manager, DialogueType


def test_all_features():
    """自动测试所有主动对话功能"""
    print("\n" + "="*60)
    print("自动测试主动对话功能")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    # 获取对话管理器
    dialogue_manager = get_dialogue_manager()
    
    # 连接信号以打印触发的对话
    triggered_dialogues = []
    
    def on_dialogue_triggered(dialogue_type, message):
        print(f"\n✅ [{datetime.now().strftime('%H:%M:%S')}] {dialogue_type}:")
        print(f"   {message}")
        triggered_dialogues.append((dialogue_type, message))
    
    dialogue_manager.trigger_dialogue.connect(on_dialogue_triggered)
    
    print("\n开始测试序列...")
    
    # 测试1: 定时问候
    def test_greeting():
        print("\n1. 测试定时问候...")
        dialogue_manager._check_greeting()
    
    # 测试2: 闲置关怀
    def test_idle():
        print("\n2. 测试闲置关怀（短期5-15分钟）...")
        dialogue_manager.last_active_time = time.time() - 360  # 6分钟前
        dialogue_manager._check_idle()
        
        print("\n3. 测试闲置关怀（中期15-30分钟）...")
        dialogue_manager.last_active_time = time.time() - 1200  # 20分钟前
        dialogue_manager.idle_notified_levels.clear()  # 清除已通知级别
        dialogue_manager._check_idle()
        
        print("\n4. 测试闲置关怀（长期30分钟以上）...")
        dialogue_manager.last_active_time = time.time() - 2400  # 40分钟前
        dialogue_manager.idle_notified_levels.clear()
        dialogue_manager._check_idle()
    
    # 测试3: AFK回归
    def test_afk_return():
        print("\n5. 测试AFK回归（之前在工作）...")
        dialogue_manager.is_afk = True
        dialogue_manager.afk_start_time = time.time() - 600  # 10分钟前
        dialogue_manager.last_activity_type = "productive"
        dialogue_manager.on_user_activity()
        
        print("\n6. 测试AFK回归（之前在浏览）...")
        dialogue_manager.is_afk = True
        dialogue_manager.afk_start_time = time.time() - 300
        dialogue_manager.last_activity_type = "browsing"
        dialogue_manager.on_user_activity()
    
    # 测试4: 状态转换
    def test_state_transition():
        print("\n7. 测试状态转换通知...")
        from baal.desktop_pet.core.state_awareness import TimeOfDay
        
        # 测试不同时间段的转换
        transitions = [
            (TimeOfDay.NIGHT, TimeOfDay.MORNING),
            (TimeOfDay.MORNING, TimeOfDay.NOON),
            (TimeOfDay.NOON, TimeOfDay.AFTERNOON),
        ]
        
        for old_segment, new_segment in transitions:
            dialogue_manager.last_time_segment = old_segment
            # 临时修改获取时间段的方法返回值
            original_method = dialogue_manager.state_system.get_time_of_day
            dialogue_manager.state_system.get_time_of_day = lambda: new_segment
            dialogue_manager._check_state_transition()
            dialogue_manager.state_system.get_time_of_day = original_method
    
    # 测试5: 随机互动
    def test_random_chat():
        print("\n8. 测试随机互动（多次尝试触发）...")
        dialogue_manager.random_chat_cooldown = 0
        dialogue_manager.last_interaction_time = time.time() - 400
        
        # 尝试多次直到触发（20%概率）
        attempts = 0
        max_attempts = 20
        while attempts < max_attempts:
            dialogue_manager._check_random_chat()
            if dialogue_manager.random_chat_cooldown > 0:
                print(f"   在第{attempts + 1}次尝试时触发")
                break
            attempts += 1
        
        if attempts == max_attempts:
            print(f"   {max_attempts}次尝试均未触发（概率问题）")
    
    # 显示测试结果
    def show_results():
        print("\n" + "="*60)
        print("测试完成！")
        print(f"共触发了 {len(triggered_dialogues)} 个主动对话")
        print("="*60)
        
        # 清理并退出
        dialogue_manager.cleanup()
        app.quit()
    
    # 执行测试序列
    QTimer.singleShot(100, test_greeting)
    QTimer.singleShot(500, test_idle)
    QTimer.singleShot(1500, test_afk_return)
    QTimer.singleShot(2500, test_state_transition)
    QTimer.singleShot(3500, test_random_chat)
    QTimer.singleShot(4500, show_results)
    
    # 运行应用
    app.exec()


if __name__ == "__main__":
    test_all_features()