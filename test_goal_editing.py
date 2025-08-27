#!/usr/bin/env python3
"""
测试监督目标编辑功能
"""

import sys
import time
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel, QTextEdit
from PyQt6.QtCore import Qt
from baal.desktop_pet.ui.supervision_dialog import SupervisionDialog

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.current_goal = ""
        self.current_tasks = []
        self.is_supervision_active = False
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("测试监督目标编辑")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("监督模式：未激活")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)
        
        # 当前目标显示
        self.goal_display = QTextEdit()
        self.goal_display.setReadOnly(True)
        self.goal_display.setPlaceholderText("尚未设置目标")
        self.goal_display.setMaximumHeight(150)
        layout.addWidget(self.goal_display)
        
        # 按钮：开始/编辑监督
        self.edit_button = QPushButton("设置监督目标")
        self.edit_button.clicked.connect(self.show_supervision_dialog)
        layout.addWidget(self.edit_button)
        
        # 按钮：切换监督状态
        self.toggle_button = QPushButton("启动监督模式")
        self.toggle_button.clicked.connect(self.toggle_supervision)
        self.toggle_button.setEnabled(False)
        layout.addWidget(self.toggle_button)
        
        self.setLayout(layout)
    
    def show_supervision_dialog(self):
        """显示监督设置对话框"""
        dialog = SupervisionDialog(
            self,
            current_goal=self.current_goal,
            current_tasks=self.current_tasks,
            is_supervision_active=self.is_supervision_active
        )
        dialog.supervision_started.connect(self.update_goals)
        dialog.exec()
    
    def update_goals(self, long_term_goal, short_term_goals):
        """更新目标"""
        self.current_goal = long_term_goal
        self.current_tasks = short_term_goals
        
        # 更新显示
        display_text = f"长期目标：\n{long_term_goal}\n\n"
        if short_term_goals:
            display_text += "短期目标：\n"
            for i, goal in enumerate(short_term_goals, 1):
                display_text += f"{i}. {goal}\n"
        else:
            display_text += "短期目标：无"
        
        self.goal_display.setText(display_text)
        
        # 如果有目标，启用切换按钮
        if long_term_goal:
            self.toggle_button.setEnabled(True)
        
        # 如果监督模式正在运行，显示更新成功消息
        if self.is_supervision_active:
            print(f"✅ 监督目标已更新（监督模式运行中）")
            print(f"   长期目标: {long_term_goal[:50]}...")
            print(f"   短期目标: {len(short_term_goals)}项")
    
    def toggle_supervision(self):
        """切换监督状态"""
        self.is_supervision_active = not self.is_supervision_active
        
        if self.is_supervision_active:
            self.status_label.setText("监督模式：✅ 运行中")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.toggle_button.setText("停止监督模式")
            self.edit_button.setText("编辑监督目标（运行中）")
            print("🚀 监督模式已启动")
        else:
            self.status_label.setText("监督模式：⏸ 未激活")
            self.status_label.setStyleSheet("color: gray;")
            self.toggle_button.setText("启动监督模式")
            self.edit_button.setText("设置监督目标")
            print("⏹ 监督模式已停止")

def main():
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle("Fusion")
    
    window = TestWindow()
    window.show()
    
    print("=" * 50)
    print("监督目标编辑功能测试")
    print("=" * 50)
    print("测试步骤：")
    print("1. 点击'设置监督目标'，添加长期和短期目标")
    print("2. 点击'启动监督模式'")
    print("3. 再次点击'编辑监督目标'，测试运行时编辑")
    print("4. 双击短期目标列表项或点击编辑按钮来修改目标")
    print("=" * 50)
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()