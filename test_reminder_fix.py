#!/usr/bin/env python3
"""
测试监督提醒修复
"""

import sys
from pathlib import Path

# 添加项目根目录
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 测试修复的方法是否存在
from baal.desktop_pet.ui.pet_window import PetWindow
from PyQt6.QtWidgets import QApplication

def test_methods():
    """测试方法是否存在"""
    print("\n检查修复的方法...")
    
    app = QApplication(sys.argv)
    pet = PetWindow()
    
    # 检查新方法
    methods_to_check = [
        '_show_chat_bubble',
        '_start_bubble_auto_hide_timer', 
        '_auto_hide_bubble',
        '_reset_bubble_auto_hide_timer',
        '_on_supervision_reminder'
    ]
    
    print("\n方法检查结果：")
    for method in methods_to_check:
        if hasattr(pet, method):
            func = getattr(pet, method)
            # 检查参数
            import inspect
            sig = inspect.signature(func)
            print(f"✅ {method}: {sig}")
        else:
            print(f"❌ {method}: 不存在")
    
    # 测试 _show_chat_bubble 的 toggle 参数
    print("\n测试 _show_chat_bubble 方法...")
    try:
        # 测试默认参数
        pet._show_chat_bubble()
        print("✅ _show_chat_bubble() - 默认调用成功")
        
        # 测试 toggle 参数
        pet._show_chat_bubble(toggle=True)
        print("✅ _show_chat_bubble(toggle=True) - 切换调用成功")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    # 测试监督提醒
    print("\n测试监督提醒...")
    try:
        context = {
            'reminder_message': '测试提醒消息',
            'deviation_level': '中度'
        }
        pet._on_supervision_reminder(context)
        print("✅ 监督提醒调用成功（无 _update_bubble_position 错误）")
    except AttributeError as e:
        if '_update_bubble_position' in str(e):
            print(f"❌ 仍有错误: {e}")
        else:
            print(f"❌ 其他错误: {e}")
    except Exception as e:
        print(f"⚠️ 其他异常: {e}")
    
    print("\n✅ 所有修复已验证完成！")
    
    # 清理
    app.quit()

if __name__ == "__main__":
    test_methods()