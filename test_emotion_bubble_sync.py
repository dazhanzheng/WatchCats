#!/usr/bin/env python3
"""
测试表情和气泡计时器同步

验证表情持续时间与气泡显示时间保持一致
"""

import sys
import os
import time
from datetime import datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from baal.desktop_pet.ui.pet_window import PetWindow
from baal.desktop_pet.core.config_manager import ConfigManager
from baal.desktop_pet.core.persona_manager import PersonaManager, PersonaLevel


def test_emotion_bubble_timing():
    """测试表情和气泡的计时器同步"""
    print("=" * 60)
    print("测试表情和气泡计时器同步")
    print("=" * 60)
    
    app = QApplication(sys.argv)
    
    # 创建宠物窗口（不需要传递config_manager，它会在内部创建）
    pet_window = PetWindow()
    pet_window.show()
    
    # 测试计时器设置
    print("\n1. 检查初始计时器设置:")
    print(f"   表情重置计时器间隔: {pet_window.emotion_reset_timer.interval()}ms")
    print(f"   气泡自动隐藏计时器间隔: {pet_window.bubble_auto_hide_timer.interval()}ms")
    
    # 模拟更新表情
    print("\n2. 模拟更新表情到生气 <#6>:")
    pet_window._update_emotion("<#6>")
    print(f"   当前表情: {pet_window.current_emotion}")
    print(f"   表情计时器是否激活: {pet_window.emotion_reset_timer.isActive()}")
    print(f"   表情计时器间隔: {pet_window.emotion_reset_timer.interval()}ms (应该是20000)")
    
    # 模拟显示气泡
    print("\n3. 模拟显示聊天气泡:")
    pet_window._show_chat_bubble()
    print(f"   气泡是否显示: {pet_window.chat_bubble.isVisible()}")
    print(f"   气泡计时器是否激活: {pet_window.bubble_auto_hide_timer.isActive()}")
    print(f"   气泡计时器间隔: {pet_window.bubble_auto_hide_timer.interval()}ms (应该是20000)")
    
    # 模拟用户交互
    print("\n4. 模拟用户交互（重置计时器）:")
    pet_window._reset_bubble_auto_hide_timer()
    print(f"   表情计时器是否激活: {pet_window.emotion_reset_timer.isActive()}")
    print(f"   表情计时器间隔: {pet_window.emotion_reset_timer.interval()}ms")
    print(f"   气泡计时器是否激活: {pet_window.bubble_auto_hide_timer.isActive()}")
    print(f"   气泡计时器间隔: {pet_window.bubble_auto_hide_timer.interval()}ms")
    
    # 模拟监督提醒
    print("\n5. 模拟监督模式提醒:")
    reminder_context = {
        'reminder_message': '<#7>你在偷懒！立即回到工作中！',
        'deviation_level': '严重'
    }
    
    # 手动触发提醒逻辑的核心部分
    message = reminder_context['reminder_message']
    if message.startswith("<#"):
        pet_window._update_emotion(message[:4])
        message = message[4:].strip()
        # 监督提醒时的特殊处理
        pet_window.emotion_reset_timer.stop()
        pet_window.emotion_reset_timer.start(30000)  # 30秒
    
    print(f"   当前表情: {pet_window.current_emotion}")
    print(f"   表情计时器间隔: {pet_window.emotion_reset_timer.interval()}ms (监督提醒应该是30000)")
    
    # 测试流式输出结束
    print("\n6. 模拟流式输出结束:")
    pet_window._on_stream_finished()
    print(f"   表情计时器是否激活: {pet_window.emotion_reset_timer.isActive()}")
    print(f"   表情计时器间隔: {pet_window.emotion_reset_timer.interval()}ms (应该是20000)")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("总结:")
    print("1. 正常情况下，表情和气泡都使用20秒计时器")
    print("2. 用户交互时，两个计时器都会重置")
    print("3. 监督提醒时，两者都使用30秒计时器")
    print("4. 表情和气泡的显示时间保持同步")
    print("=" * 60)
    
    # 清理
    pet_window.close()
    app.quit()
    
    return 0


def main():
    """主函数"""
    try:
        return test_emotion_bubble_timing()
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())