#!/usr/bin/env python3
"""
测试表情自动恢复和输入框禁用功能

测试要点：
1. 表情会在对话结束10秒后自动恢复到默认状态
2. AI回复期间输入框会被禁用，防止消息冲突
"""

import sys
import time
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from baal.desktop_pet.ui.pet_window import PetWindow

def test_emotion_reset():
    """测试表情自动恢复功能"""
    print("\n=== 测试表情自动恢复功能 ===")
    
    app = QApplication(sys.argv)
    window = PetWindow()
    window.show()
    
    # 模拟表情变化
    print("1. 设置表情为生气 <#6>")
    window._update_emotion("<#6>")
    print(f"   当前表情: {window.current_emotion}")
    
    # 创建计时器来检查表情状态
    def check_emotion_after_5s():
        print("\n2. 5秒后检查（应该仍是生气）:")
        print(f"   当前表情: {window.current_emotion}")
        assert window.current_emotion == "<#6>", "表情不应该这么快恢复"
        print("   ✓ 表情保持正确")
    
    def check_emotion_after_11s():
        print("\n3. 11秒后检查（应该恢复到默认）:")
        print(f"   当前表情: {window.current_emotion}")
        assert window.current_emotion == "<#5>", "表情应该已恢复到默认"
        print("   ✓ 表情已正确恢复到默认!")
        
        # 测试第二个功能
        test_input_disable(window)
    
    # 设置检查点
    QTimer.singleShot(5000, check_emotion_after_5s)
    QTimer.singleShot(11000, check_emotion_after_11s)
    
    # 15秒后退出
    QTimer.singleShot(15000, app.quit)
    
    app.exec()

def test_input_disable(window):
    """测试输入框禁用功能"""
    print("\n=== 测试输入框禁用功能 ===")
    
    # 显示聊天气泡
    window._show_chat_bubble()
    
    print("1. 初始状态:")
    print(f"   输入框是否启用: {window.chat_bubble.input_field.isEnabled()}")
    print(f"   占位符文本: {window.chat_bubble.input_field.placeholderText()}")
    assert window.chat_bubble.input_field.isEnabled(), "输入框应该是启用的"
    
    print("\n2. 开始流式输出:")
    window.chat_bubble.start_stream()
    print(f"   输入框是否启用: {window.chat_bubble.input_field.isEnabled()}")
    print(f"   占位符文本: {window.chat_bubble.input_field.placeholderText()}")
    assert not window.chat_bubble.input_field.isEnabled(), "输入框应该被禁用"
    assert "正在回复" in window.chat_bubble.input_field.placeholderText(), "应该显示回复中提示"
    
    print("\n3. 模拟接收一些文本:")
    window.chat_bubble.append_text("这是")
    time.sleep(0.1)
    window.chat_bubble.append_text("测试")
    time.sleep(0.1)
    window.chat_bubble.append_text("文本")
    
    print("\n4. 结束流式输出:")
    window.chat_bubble.end_stream()
    print(f"   输入框是否启用: {window.chat_bubble.input_field.isEnabled()}")
    print(f"   占位符文本: {window.chat_bubble.input_field.placeholderText()}")
    assert window.chat_bubble.input_field.isEnabled(), "输入框应该重新启用"
    assert window.chat_bubble.input_field.placeholderText() == "输入消息...", "占位符应该恢复"
    
    print("\n✓ 所有测试通过!")

if __name__ == "__main__":
    print("开始测试Bug修复...")
    print("注意: 此测试需要约15秒完成")
    
    try:
        test_emotion_reset()
        print("\n=== 测试完成 ===")
        print("✓ 表情自动恢复功能正常")
        print("✓ 输入框禁用/启用功能正常")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)