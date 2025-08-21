#!/usr/bin/env python3
"""
测试带有开机自启动功能的设置对话框
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from baal.desktop_pet.core.config_manager import ConfigManager
from baal.desktop_pet.ui.settings_dialog import SettingsDialog


def test_settings_dialog():
    """测试设置对话框"""
    app = QApplication(sys.argv)
    
    # 创建配置管理器
    config_manager = ConfigManager()
    
    # 创建测试窗口
    window = QWidget()
    window.setWindowTitle("测试设置对话框（含开机自启动）")
    window.setGeometry(100, 100, 400, 200)
    layout = QVBoxLayout(window)
    
    # 添加说明
    info = QLabel(f"当前平台: {sys.platform}")
    layout.addWidget(info)
    
    if sys.platform == "win32":
        layout.addWidget(QLabel("✅ Windows 平台 - 将显示开机自启动选项"))
    else:
        layout.addWidget(QLabel("⚠️ 非 Windows 平台 - 不显示开机自启动选项"))
    
    # 添加测试按钮
    test_btn = QPushButton("打开设置对话框")
    layout.addWidget(test_btn)
    
    def show_settings():
        dialog = SettingsDialog(config_manager, window)
        result = dialog.exec()
        
        if result:
            print("✅ 设置已保存")
        else:
            print("❌ 设置已取消")
    
    test_btn.clicked.connect(show_settings)
    
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    test_settings_dialog()