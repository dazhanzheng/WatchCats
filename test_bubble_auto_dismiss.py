#!/usr/bin/env python3
"""
测试所有气泡的30秒自动消失功能
Test all bubble types for 30-second auto-dismiss functionality
"""

import sys
import time
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from baal.desktop_pet.ui.pet_window import PetWindow
from baal.desktop_pet.core.preset_responses import PresetResponseManager
from baal.desktop_pet.core.persona_manager import PersonaLevel

def test_bubble_auto_dismiss():
    """测试各种气泡类型的自动消失功能"""
    
    app = QApplication(sys.argv)
    pet_window = PetWindow()
    pet_window.show()
    
    test_cases = [
        {
            "name": "欢迎消息气泡",
            "action": lambda: pet_window._show_welcome_message(),
            "expected_timer": 30000
        },
        {
            "name": "双击招呼气泡",
            "action": lambda: simulate_double_click(pet_window),
            "expected_timer": 20000  # 双击默认是20秒
        },
        {
            "name": "API未配置提示气泡",
            "action": lambda: show_api_not_configured(pet_window),
            "expected_timer": 30000
        },
        {
            "name": "人设切换提示气泡",
            "action": lambda: show_persona_change(pet_window),
            "expected_timer": 30000
        },
        {
            "name": "位置重置提示气泡",
            "action": lambda: pet_window._reset_position(),
            "expected_timer": 30000
        },
        {
            "name": "置顶切换提示气泡",
            "action": lambda: pet_window._toggle_always_on_top(True),
            "expected_timer": 30000
        },
        {
            "name": "监督模式提醒气泡",
            "action": lambda: simulate_supervision_reminder(pet_window),
            "expected_timer": 30000
        }
    ]
    
    print("=" * 60)
    print("测试所有气泡的自动消失功能")
    print("=" * 60)
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        
        # 执行动作
        test_case['action']()
        
        # 检查气泡是否显示
        if pet_window.chat_bubble.isVisible():
            print(f"  ✓ 气泡已显示")
            
            # 检查自动隐藏计时器是否启动
            if pet_window.bubble_auto_hide_timer.isActive():
                remaining = pet_window.bubble_auto_hide_timer.remainingTime()
                print(f"  ✓ 自动隐藏计时器已启动")
                print(f"  ✓ 剩余时间: {remaining/1000:.1f}秒")
                
                # 验证计时器时间是否正确
                if abs(remaining - test_case['expected_timer']) < 1000:  # 允许1秒误差
                    print(f"  ✓ 计时器时间正确 ({test_case['expected_timer']/1000}秒)")
                else:
                    print(f"  ✗ 计时器时间不正确 (期望: {test_case['expected_timer']/1000}秒, 实际: {remaining/1000:.1f}秒)")
            else:
                print(f"  ✗ 自动隐藏计时器未启动!")
        else:
            print(f"  ✗ 气泡未显示")
        
        # 隐藏气泡，准备下一个测试
        pet_window.chat_bubble.hide()
        time.sleep(0.5)
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)
    
    # 让窗口保持5秒后关闭
    QTimer.singleShot(5000, app.quit)
    
    return app.exec()

def simulate_double_click(pet_window):
    """模拟双击事件"""
    from PyQt6.QtCore import Qt, QPointF
    from PyQt6.QtGui import QMouseEvent
    
    # 创建一个双击事件
    event = QMouseEvent(
        QMouseEvent.Type.MouseButtonDblClick,
        QPointF(50, 50),
        QPointF(pet_window.x() + 50, pet_window.y() + 50),
        Qt.MouseButton.LeftButton,
        Qt.MouseButton.LeftButton,
        Qt.KeyboardModifier.NoModifier
    )
    pet_window.mouseDoubleClickEvent(event)

def show_api_not_configured(pet_window):
    """显示API未配置提示"""
    response = PresetResponseManager.get_response(
        pet_window.persona_manager.current_level,
        "api_not_configured"
    )
    if response.startswith("<#"):
        pet_window._update_emotion(response[:4])
        response = response[4:].strip()
    pet_window.chat_bubble.show_message(response)
    pet_window._reset_bubble_auto_hide_timer()

def show_persona_change(pet_window):
    """显示人设切换提示"""
    response = PresetResponseManager.get_response(
        pet_window.persona_manager.current_level,
        "api_configured"
    )
    if response.startswith("<#"):
        pet_window._update_emotion(response[:4])
        response = response[4:].strip()
    pet_window.chat_bubble.show_message(response)
    pet_window._start_bubble_auto_hide_timer(30000)

def simulate_supervision_reminder(pet_window):
    """模拟监督模式提醒"""
    context = {
        'reminder_message': '你似乎偏离了目标，请回到正轨。',
        'deviation_level': '中度'
    }
    pet_window._on_supervision_reminder(context)

if __name__ == "__main__":
    sys.exit(test_bubble_auto_dismiss())