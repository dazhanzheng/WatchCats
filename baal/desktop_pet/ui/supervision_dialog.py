"""
监督模式设置对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QTextEdit, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QGroupBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SupervisionDialog(QDialog):
    """监督模式设置对话框"""
    
    # 信号：当用户确认设置时发出
    supervision_started = pyqtSignal(str, list)  # long_term_goal, short_term_goals
    
    def __init__(self, parent=None, current_goal="", current_tasks=None):
        """初始化对话框
        
        Args:
            parent: 父窗口
            current_goal: 当前的长期目标
            current_tasks: 当前的短期目标列表
        """
        super().__init__(parent)
        self.long_term_goal = current_goal
        self.short_term_goals = current_tasks or []
        self.init_ui()
        
        # 如果有现有设置，加载它们
        if self.long_term_goal:
            self.long_term_edit.setText(self.long_term_goal)
        for goal in self.short_term_goals:
            self.short_term_list.addItem(goal)
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("👁 监督模式设置")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        # 设置对话框样式
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #cccccc;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QLabel {
                color: #333333;
            }
            QTextEdit, QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QListWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
        """)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 标题和说明
        header_layout = QVBoxLayout()
        title_label = QLabel("🎯 设定您的目标")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 10px;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(title_label)
        
        intro_label = QLabel(
            "监督模式将每5分钟检查您的活动，帮助您保持专注。\n"
            "巴利会根据您的目标和当前人设提供个性化提醒。"
        )
        intro_label.setWordWrap(True)
        intro_label.setStyleSheet("""
            color: #7f8c8d;
            padding: 0 20px 10px 20px;
        """)
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(intro_label)
        layout.addLayout(header_layout)
        
        # 长期目标设置组
        long_term_group = QGroupBox("🏆 长期目标")
        long_term_layout = QVBoxLayout()
        
        long_term_label = QLabel("您的最终目标是什么？（一段话描述）")
        long_term_layout.addWidget(long_term_label)
        
        self.long_term_edit = QTextEdit()
        self.long_term_edit.setPlaceholderText(
            "例如：完成我的毕业论文，保持高效的学习状态，避免被娱乐内容分散注意力"
        )
        self.long_term_edit.setMaximumHeight(80)
        long_term_layout.addWidget(self.long_term_edit)
        
        long_term_group.setLayout(long_term_layout)
        layout.addWidget(long_term_group)
        
        # 短期目标列表组
        short_term_group = QGroupBox("✅ 短期目标")
        short_term_layout = QVBoxLayout()
        
        short_term_label = QLabel("今天要完成的具体任务：")
        short_term_layout.addWidget(short_term_label)
        
        # 短期目标输入
        goal_input_layout = QHBoxLayout()
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("输入一个短期目标，然后点击添加")
        self.goal_input.returnPressed.connect(self.add_goal)
        goal_input_layout.addWidget(self.goal_input)
        
        self.add_button = QPushButton("➕ 添加")
        self.add_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        self.add_button.clicked.connect(self.add_goal)
        goal_input_layout.addWidget(self.add_button)
        
        short_term_layout.addLayout(goal_input_layout)
        
        # 短期目标列表
        self.short_term_list = QListWidget()
        self.short_term_list.setMaximumHeight(120)
        short_term_layout.addWidget(self.short_term_list)
        
        # 删除按钮
        self.remove_button = QPushButton("🗑 删除选中的目标")
        self.remove_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.remove_button.clicked.connect(self.remove_goal)
        short_term_layout.addWidget(self.remove_button)
        
        short_term_group.setLayout(short_term_layout)
        layout.addWidget(short_term_group)
        
        # 按钮栏
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("❌ 取消")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.start_button = QPushButton("🚀 开始监督")
        self.start_button.clicked.connect(self.start_supervision)
        self.start_button.setDefault(True)
        
        # 设置开始按钮样式
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 30px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_goal(self):
        """添加短期目标到列表"""
        goal = self.goal_input.text().strip()
        if goal:
            # 限制短期目标数量
            if self.short_term_list.count() >= 5:
                QMessageBox.information(self, "提示", "短期目标最多5个，请保持简洁")
                return
            self.short_term_list.addItem(goal)
            self.goal_input.clear()
    
    def remove_goal(self):
        """从列表中删除选中的短期目标"""
        current_item = self.short_term_list.currentItem()
        if current_item:
            self.short_term_list.takeItem(self.short_term_list.row(current_item))
    
    # 兼容旧方法名
    def add_task(self):
        self.add_goal()
    
    def remove_task(self):
        self.remove_goal()
    
    def start_supervision(self):
        """开始监督"""
        long_term_goal = self.long_term_edit.toPlainText().strip()
        
        if not long_term_goal:
            QMessageBox.warning(self, "提示", "请输入长期目标")
            return
        
        # 获取所有短期目标
        short_term_goals = []
        for i in range(self.short_term_list.count()):
            short_term_goals.append(self.short_term_list.item(i).text())
        
        if not short_term_goals:
            reply = QMessageBox.question(
                self, "确认",
                "您没有添加短期目标，建议添加一些具体任务。\n确定要继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 发出信号并关闭对话框
        self.supervision_started.emit(long_term_goal, short_term_goals)
        self.accept()


class SupervisionStatusWidget(QGroupBox):
    """监督模式状态显示组件"""
    
    # 信号：停止监督
    stop_requested = pyqtSignal()
    # 信号：修改设置
    modify_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        """初始化状态组件"""
        super().__init__("监督模式", parent)
        self.init_ui()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 状态标签
        self.status_label = QLabel("未激活")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        font = QFont()
        font.setBold(True)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)
        
        # 目标显示
        self.goal_label = QLabel("")
        self.goal_label.setWordWrap(True)
        self.goal_label.setMaximumHeight(60)
        layout.addWidget(self.goal_label)
        
        # 按钮栏
        button_layout = QHBoxLayout()
        
        self.modify_button = QPushButton("修改")
        self.modify_button.clicked.connect(self.modify_requested.emit)
        self.modify_button.setEnabled(False)
        button_layout.addWidget(self.modify_button)
        
        self.stop_button = QPushButton("停止")
        self.stop_button.clicked.connect(self.stop_requested.emit)
        self.stop_button.setEnabled(False)
        button_layout.addWidget(self.stop_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.setMaximumHeight(150)
    
    def update_status(self, is_active: bool, long_term_goal: str = "", short_term_goals: list = None):
        """更新状态显示
        
        Args:
            is_active: 是否激活
            long_term_goal: 长期目标
            short_term_goals: 短期目标列表
        """
        if is_active:
            self.status_label.setText("✅ 监督中")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            
            # 显示长期目标
            display_text = f"长期目标: {long_term_goal[:50]}"
            if len(long_term_goal) > 50:
                display_text += "..."
            
            # 显示短期目标数量
            if short_term_goals:
                display_text += f"\n短期目标: {len(short_term_goals)}项"
            
            self.goal_label.setText(display_text)
            self.modify_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        else:
            self.status_label.setText("⏸ 未激活")
            self.status_label.setStyleSheet("color: gray;")
            self.goal_label.setText("")
            self.modify_button.setEnabled(False)
            self.stop_button.setEnabled(False)