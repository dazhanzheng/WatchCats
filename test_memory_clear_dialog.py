#!/usr/bin/env python3
"""
测试记忆清除对话框
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
from baal.desktop_pet.ui.memory_clear_dialog import MemoryClearDialog


def test_dialog():
    """测试对话框"""
    app = QApplication(sys.argv)
    
    # 创建测试窗口
    window = QWidget()
    window.setWindowTitle("测试记忆清除对话框")
    layout = QVBoxLayout(window)
    
    # 添加测试按钮
    test_btn = QPushButton("测试清除记忆对话框")
    layout.addWidget(test_btn)
    
    def show_dialog():
        dialog = MemoryClearDialog(window)
        result = dialog.exec()
        
        if dialog.was_confirmed():
            print("✅ 用户确认删除")
        else:
            print("❌ 用户取消删除")
    
    test_btn.clicked.connect(show_dialog)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    test_dialog()