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
    supervision_started = pyqtSignal(str, list)  # goal, tasks
    
    def __init__(self, parent=None, current_goal="", current_tasks=None):
        """初始化对话框
        
        Args:
            parent: 父窗口
            current_goal: 当前的监督目标
            current_tasks: 当前的任务列表
        """
        super().__init__(parent)
        self.current_goal = current_goal
        self.current_tasks = current_tasks or []
        self.init_ui()
        
        # 如果有现有设置，加载它们
        if self.current_goal:
            self.goal_edit.setText(self.current_goal)
        for task in self.current_tasks:
            self.task_list.addItem(task)
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("监督模式设置")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        # 说明文字
        intro_label = QLabel(
            "监督模式会每5分钟检查您的电脑使用情况，\n"
            "如果发现您偏离了设定的目标，巴利会提醒您。"
        )
        intro_label.setWordWrap(True)
        layout.addWidget(intro_label)
        
        # 目标设置组
        goal_group = QGroupBox("监督目标")
        goal_layout = QVBoxLayout()
        
        goal_label = QLabel("请描述您此次使用监督模式的目的：")
        goal_layout.addWidget(goal_label)
        
        self.goal_edit = QTextEdit()
        self.goal_edit.setPlaceholderText(
            "例如：专注完成项目报告，不要分心看视频或社交媒体"
        )
        self.goal_edit.setMaximumHeight(80)
        goal_layout.addWidget(self.goal_edit)
        
        goal_group.setLayout(goal_layout)
        layout.addWidget(goal_group)
        
        # 任务列表组
        tasks_group = QGroupBox("预期任务")
        tasks_layout = QVBoxLayout()
        
        tasks_label = QLabel("您打算做哪些具体的事情？")
        tasks_layout.addWidget(tasks_label)
        
        # 任务输入
        task_input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("输入一个任务，然后点击添加")
        self.task_input.returnPressed.connect(self.add_task)
        task_input_layout.addWidget(self.task_input)
        
        self.add_button = QPushButton("添加")
        self.add_button.clicked.connect(self.add_task)
        task_input_layout.addWidget(self.add_button)
        
        tasks_layout.addLayout(task_input_layout)
        
        # 任务列表
        self.task_list = QListWidget()
        self.task_list.setMaximumHeight(150)
        tasks_layout.addWidget(self.task_list)
        
        # 删除按钮
        self.remove_button = QPushButton("删除选中的任务")
        self.remove_button.clicked.connect(self.remove_task)
        tasks_layout.addWidget(self.remove_button)
        
        tasks_group.setLayout(tasks_layout)
        layout.addWidget(tasks_group)
        
        # 按钮栏
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.start_button = QPushButton("开始监督")
        self.start_button.clicked.connect(self.start_supervision)
        self.start_button.setDefault(True)
        
        # 设置开始按钮样式
        self.start_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        button_layout.addWidget(self.start_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def add_task(self):
        """添加任务到列表"""
        task = self.task_input.text().strip()
        if task:
            self.task_list.addItem(task)
            self.task_input.clear()
    
    def remove_task(self):
        """从列表中删除选中的任务"""
        current_item = self.task_list.currentItem()
        if current_item:
            self.task_list.takeItem(self.task_list.row(current_item))
    
    def start_supervision(self):
        """开始监督"""
        goal = self.goal_edit.toPlainText().strip()
        
        if not goal:
            QMessageBox.warning(self, "提示", "请输入监督目标")
            return
        
        # 获取所有任务
        tasks = []
        for i in range(self.task_list.count()):
            tasks.append(self.task_list.item(i).text())
        
        if not tasks:
            reply = QMessageBox.question(
                self, "确认",
                "您没有添加具体任务，确定要继续吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return
        
        # 发出信号并关闭对话框
        self.supervision_started.emit(goal, tasks)
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
    
    def update_status(self, is_active: bool, goal: str = "", tasks: list = None):
        """更新状态显示
        
        Args:
            is_active: 是否激活
            goal: 监督目标
            tasks: 任务列表
        """
        if is_active:
            self.status_label.setText("监督中")
            self.status_label.setStyleSheet("color: green;")
            self.goal_label.setText(f"目标: {goal[:100]}...")  # 限制显示长度
            self.modify_button.setEnabled(True)
            self.stop_button.setEnabled(True)
        else:
            self.status_label.setText("未激活")
            self.status_label.setStyleSheet("color: gray;")
            self.goal_label.setText("")
            self.modify_button.setEnabled(False)
            self.stop_button.setEnabled(False)