"""
记忆清除确认对话框

提供多重确认机制确保用户真的想要清除所有记忆
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QLineEdit, QCheckBox, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor


class MemoryClearDialog(QDialog):
    """记忆清除确认对话框"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.confirmed = False
        self.setup_ui()
        
    def setup_ui(self):
        """设置UI"""
        self.setWindowTitle("⚠️ 危险操作警告")
        self.setFixedSize(450, 380)
        self.setModal(True)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                border: 2px solid #ff4444;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 警告标题
        warning_label = QLabel("⚠️ 即将清除所有记忆 ⚠️")
        warning_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        warning_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 20px;
                font-weight: bold;
                padding: 10px;
                background-color: rgba(255, 68, 68, 0.1);
                border: 2px solid #ff4444;
                border-radius: 5px;
            }
        """)
        layout.addWidget(warning_label)
        
        # 警告说明
        warning_text = QLabel(
            "此操作将永久删除巴利的所有对话记忆！\n\n"
            "包括：\n"
            "• 所有历史对话记录\n"
            "• 对话总结信息\n"
            "• 你们之间建立的关系记忆\n\n"
            "⚠️ 此操作不可撤销！"
        )
        warning_text.setWordWrap(True)
        warning_text.setStyleSheet("""
            QLabel {
                color: #ffaaaa;
                font-size: 14px;
                padding: 10px;
                background-color: rgba(255, 0, 0, 0.05);
                border: 1px solid #ff6666;
                border-radius: 3px;
            }
        """)
        layout.addWidget(warning_text)
        
        # 第一个确认：复选框
        self.confirm_checkbox = QCheckBox("☐ 我已了解此操作的后果（必须勾选）")
        self.confirm_checkbox.setStyleSheet("""
            QCheckBox {
                color: #ffcccc;
                font-size: 14px;
                font-weight: bold;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #ff6666;
                border-radius: 3px;
                background-color: #3a3a3a;
            }
            QCheckBox::indicator:checked {
                background-color: #ff4444;
            }
        """)
        layout.addWidget(self.confirm_checkbox)
        
        # 第二个确认：手动输入
        input_label = QLabel("请手动输入以下文字以确认删除：")
        input_label.setStyleSheet("QLabel { color: #ff8888; font-size: 13px; }")
        layout.addWidget(input_label)
        
        confirm_text_label = QLabel("我确定清除巴利的全部记忆")
        confirm_text_label.setStyleSheet("""
            QLabel {
                color: #ff4444;
                font-size: 14px;
                font-weight: bold;
                padding: 5px;
                background-color: rgba(255, 68, 68, 0.1);
                border: 1px solid #ff4444;
                border-radius: 3px;
            }
        """)
        confirm_text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(confirm_text_label)
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("在此输入上述文字...")
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: #ffffff;
                border: 2px solid #666666;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #ff6666;
            }
        """)
        layout.addWidget(self.input_field)
        
        # 添加间隔
        layout.addStretch()
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 取消按钮（安全的默认选项）
        cancel_btn = QPushButton("取消")
        cancel_btn.setDefault(True)  # 设为默认按钮
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #4a4a4a;
                color: #ffffff;
                border: 1px solid #666666;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 14px;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #5a5a5a;
                border-color: #888888;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        # 确认删除按钮（危险操作）
        self.delete_btn = QPushButton("⚠️ 确认删除")
        self.delete_btn.setEnabled(False)  # 初始禁用
        self.delete_btn.setToolTip("需要：1.勾选复选框 2.输入确认文字")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff4444;
                color: #ffffff;
                border: 2px solid #ff2222;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover:enabled {
                background-color: #ff6666;
                border-color: #ff4444;
            }
            QPushButton:pressed:enabled {
                background-color: #cc2222;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #999999;
                border-color: #555555;
            }
        """)
        self.delete_btn.clicked.connect(self.confirm_delete)
        button_layout.addWidget(self.delete_btn)
        
        layout.addLayout(button_layout)
        
        # 连接信号以检查是否可以启用删除按钮
        self.confirm_checkbox.stateChanged.connect(self.check_enable_delete)
        self.input_field.textChanged.connect(self.check_enable_delete)
        
    def check_enable_delete(self):
        """检查是否可以启用删除按钮"""
        checkbox_checked = self.confirm_checkbox.isChecked()
        text_correct = self.input_field.text() == "我确定清除巴利的全部记忆"
        
        # 更新删除按钮状态和提示
        can_delete = checkbox_checked and text_correct
        self.delete_btn.setEnabled(can_delete)
        
        # 更新按钮提示文字
        if not checkbox_checked and not text_correct:
            self.delete_btn.setToolTip("需要：1.勾选复选框 2.输入确认文字")
        elif not checkbox_checked:
            self.delete_btn.setToolTip("请先勾选复选框")
        elif not text_correct:
            self.delete_btn.setToolTip("请输入正确的确认文字")
        else:
            self.delete_btn.setToolTip("点击确认删除所有记忆")
        
        # 如果文本不正确，显示红色边框
        if self.input_field.text() and not text_correct:
            self.input_field.setStyleSheet("""
                QLineEdit {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: 2px solid #ff4444;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                }
            """)
        else:
            self.input_field.setStyleSheet("""
                QLineEdit {
                    background-color: #3a3a3a;
                    color: #ffffff;
                    border: 2px solid #666666;
                    border-radius: 4px;
                    padding: 8px;
                    font-size: 14px;
                }
                QLineEdit:focus {
                    border-color: #ff6666;
                }
            """)
    
    def confirm_delete(self):
        """确认删除"""
        self.confirmed = True
        self.accept()
    
    def was_confirmed(self):
        """返回是否确认删除"""
        return self.confirmed