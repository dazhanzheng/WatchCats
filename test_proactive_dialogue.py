#!/usr/bin/env python3
"""
测试主动对话功能

演示定时问候、闲置关怀、状态转换通知和随机互动
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from baal.desktop_pet.core.proactive_dialogue_manager import get_dialogue_manager, DialogueType


def test_proactive_features():
    """测试主动对话功能"""
    print("\n" + "="*60)
    print("测试主动对话功能")
    print("="*60)
    
    app = QApplication(sys.argv)
    
    # 获取对话管理器
    dialogue_manager = get_dialogue_manager()
    
    # 连接信号以打印触发的对话
    def on_dialogue_triggered(dialogue_type, message):
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] {dialogue_type}:")
        print(f"  {message}")
    
    dialogue_manager.trigger_dialogue.connect(on_dialogue_triggered)
    
    print("\n初始化完成，开始监控...")
    print("提示：")
    print("  - 早晚问候会在特定时间自动触发")
    print("  - 闲置5分钟后会触发闲置关怀")
    print("  - 每小时检查状态转换")
    print("  - 随机互动有20%概率触发")
    
    # 手动测试各种对话类型
    def test_greeting():
        print("\n测试定时问候...")
        dialogue_manager._check_greeting()
    
    def test_idle():
        print("\n测试闲置关怀...")
        # 模拟闲置6分钟
        dialogue_manager.last_active_time = time.time() - 360
        dialogue_manager._check_idle()
    
    def test_afk_return():
        print("\n测试AFK回归...")
        # 模拟AFK状态
        dialogue_manager.is_afk = True
        dialogue_manager.afk_start_time = time.time() - 600  # 10分钟前
        dialogue_manager.last_activity_type = "productive"
        dialogue_manager.on_user_activity()
    
    def test_state_transition():
        print("\n测试状态转换...")
        # 强制触发状态转换
        from baal.desktop_pet.core.state_awareness import TimeOfDay
        dialogue_manager.last_time_segment = TimeOfDay.MORNING
        dialogue_manager._check_state_transition()
    
    def test_random_chat():
        print("\n测试随机互动...")
        # 设置条件以触发随机互动
        dialogue_manager.random_chat_cooldown = 0
        dialogue_manager.last_interaction_time = time.time() - 400  # 超过5分钟
        # 多次尝试触发（20%概率）
        for i in range(10):
            dialogue_manager._check_random_chat()
            if dialogue_manager.random_chat_cooldown > 0:
                break
    
    # 创建测试菜单
    print("\n" + "-"*40)
    print("测试菜单：")
    print("1. 测试定时问候")
    print("2. 测试闲置关怀")
    print("3. 测试AFK回归")
    print("4. 测试状态转换")
    print("5. 测试随机互动")
    print("6. 测试所有功能")
    print("7. 开始实时监控（等待真实触发）")
    print("0. 退出")
    print("-"*40)
    
    # 使用定时器处理输入
    def handle_input():
        try:
            choice = input("\n请选择测试项（0-7）: ").strip()
            
            if choice == "1":
                test_greeting()
            elif choice == "2":
                test_idle()
            elif choice == "3":
                test_afk_return()
            elif choice == "4":
                test_state_transition()
            elif choice == "5":
                test_random_chat()
            elif choice == "6":
                print("\n测试所有功能...")
                test_greeting()
                QTimer.singleShot(1000, test_idle)
                QTimer.singleShot(2000, test_afk_return)
                QTimer.singleShot(3000, test_state_transition)
                QTimer.singleShot(4000, test_random_chat)
            elif choice == "7":
                print("\n开始实时监控，等待触发条件...")
                print("按Ctrl+C退出")
                # 不再提示输入，让定时器自动运行
                return
            elif choice == "0":
                print("\n退出测试...")
                dialogue_manager.cleanup()
                app.quit()
                return
            
            # 继续显示菜单
            QTimer.singleShot(100, handle_input)
            
        except KeyboardInterrupt:
            print("\n\n用户中断，退出...")
            dialogue_manager.cleanup()
            app.quit()
        except Exception as e:
            print(f"\n错误: {e}")
            QTimer.singleShot(100, handle_input)
    
    # 启动输入处理
    QTimer.singleShot(100, handle_input)
    
    # 运行应用
    try:
        app.exec()
    except KeyboardInterrupt:
        print("\n\n用户中断，清理资源...")
        dialogue_manager.cleanup()
        sys.exit(0)


if __name__ == "__main__":
    test_proactive_features()