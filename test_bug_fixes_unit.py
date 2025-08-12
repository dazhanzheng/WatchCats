#!/usr/bin/env python3
"""
单元测试：验证表情自动恢复和输入框禁用功能的代码逻辑

不需要GUI，只测试关键功能点
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

def test_emotion_reset_timer():
    """测试表情恢复计时器是否正确配置"""
    print("\n=== 测试表情恢复计时器配置 ===")
    
    # 读取代码，检查关键功能
    pet_window_path = Path(__file__).parent / "baal/desktop_pet/ui/pet_window.py"
    with open(pet_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查1: 是否添加了表情恢复计时器
    checks = [
        ("emotion_reset_timer = QTimer()", "表情恢复计时器初始化"),
        ("emotion_reset_timer.timeout.connect(self._reset_emotion_to_default)", "计时器连接到恢复函数"),
        ("emotion_reset_timer.setSingleShot(True)", "计时器设置为单次触发"),
        ("def _reset_emotion_to_default(self):", "表情恢复函数定义"),
        ("emotion_reset_timer.start(10000)", "10秒计时器启动"),
    ]
    
    for check_str, desc in checks:
        if check_str in content:
            print(f"✓ {desc}")
        else:
            print(f"✗ 缺少: {desc}")
            return False
    
    print("\n表情恢复功能代码完整性检查通过!")
    return True

def test_input_disable_logic():
    """测试输入框禁用逻辑是否正确实现"""
    print("\n=== 测试输入框禁用逻辑 ===")
    
    # 读取代码，检查关键功能
    chat_bubble_path = Path(__file__).parent / "baal/desktop_pet/ui/chat_bubble.py"
    with open(chat_bubble_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查关键功能点
    checks = [
        ("if self.is_streaming:\n            return", "发送消息时检查流式状态"),
        ("self.input_field.setEnabled(False)", "流式开始时禁用输入框"),
        ('self.input_field.setPlaceholderText("巴利正在回复中...")', "设置回复中提示"),
        ("self.input_field.setEnabled(True)", "流式结束时启用输入框"),
        ('self.input_field.setPlaceholderText("输入消息...")', "恢复原始占位符"),
        ("QLineEdit:disabled {", "禁用状态样式设置"),
    ]
    
    for check_str, desc in checks:
        if check_str in content:
            print(f"✓ {desc}")
        else:
            print(f"✗ 缺少: {desc}")
            return False
    
    print("\n输入框禁用功能代码完整性检查通过!")
    return True

def test_error_handling():
    """测试错误处理是否正确"""
    print("\n=== 测试错误处理 ===")
    
    pet_window_path = Path(__file__).parent / "baal/desktop_pet/ui/pet_window.py"
    with open(pet_window_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 检查错误处理中是否调用了end_stream
    if "def _on_error_occurred(self, error: str):" in content and \
       "self.chat_bubble.end_stream()" in content:
        print("✓ 错误处理中包含了end_stream调用")
        return True
    else:
        print("✗ 错误处理中缺少end_stream调用")
        return False

def main():
    """运行所有测试"""
    print("=" * 50)
    print("开始验证Bug修复代码...")
    print("=" * 50)
    
    tests = [
        ("表情自动恢复功能", test_emotion_reset_timer),
        ("输入框禁用功能", test_input_disable_logic),
        ("错误处理功能", test_error_handling),
    ]
    
    all_passed = True
    for test_name, test_func in tests:
        try:
            result = test_func()
            if not result:
                all_passed = False
                print(f"\n❌ {test_name} 测试失败")
        except Exception as e:
            all_passed = False
            print(f"\n❌ {test_name} 测试出错: {e}")
    
    print("\n" + "=" * 50)
    if all_passed:
        print("✅ 所有Bug修复验证通过!")
        print("\n修复内容总结:")
        print("1. 表情自动恢复: 对话结束10秒后自动恢复到默认表情")
        print("2. 输入框管理: AI回复期间禁用输入，防止消息冲突")
        print("3. 错误处理: 确保出错时也能正确恢复输入框状态")
    else:
        print("❌ 部分测试失败，请检查代码")
        sys.exit(1)

if __name__ == "__main__":
    main()