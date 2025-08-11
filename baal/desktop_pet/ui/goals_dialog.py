"""
目标管理对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QListWidget, QListWidgetItem,
    QPushButton, QLineEdit, QGroupBox,
    QComboBox, QSpinBox, QDateEdit,
    QTabWidget, QWidget, QMessageBox,
    QSlider
)
from PyQt6.QtCore import Qt, pyqtSignal, QDate
from PyQt6.QtGui import QFont
from datetime import datetime
import sys
sys.path.append('../..')
from baal.scheduler.goals import Goal, GoalsManager


class GoalEditWidget(QWidget):
    """目标编辑组件"""
    
    def __init__(self, goal: Goal = None, parent=None):
        """初始化目标编辑组件
        
        Args:
            goal: 要编辑的目标（None表示新建）
            parent: 父窗口
        """
        super().__init__(parent)
        self.goal = goal
        self.init_ui()
        
        if goal:
            self.load_goal()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 标题
        title_layout = QHBoxLayout()
        title_layout.addWidget(QLabel("标题:"))
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入目标标题")
        title_layout.addWidget(self.title_edit)
        layout.addLayout(title_layout)
        
        # 描述
        layout.addWidget(QLabel("描述:"))
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("详细描述您的目标...")
        self.description_edit.setMaximumHeight(100)
        layout.addWidget(self.description_edit)
        
        # 类型和优先级
        type_priority_layout = QHBoxLayout()
        
        type_priority_layout.addWidget(QLabel("类型:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["短期目标", "长期目标"])
        type_priority_layout.addWidget(self.type_combo)
        
        type_priority_layout.addWidget(QLabel("优先级:"))
        self.priority_spin = QSpinBox()
        self.priority_spin.setRange(1, 5)
        self.priority_spin.setValue(3)
        type_priority_layout.addWidget(self.priority_spin)
        
        layout.addLayout(type_priority_layout)
        
        # 截止日期（仅短期目标）
        deadline_layout = QHBoxLayout()
        self.deadline_checkbox = QPushButton("设置截止日期")
        self.deadline_checkbox.setCheckable(True)
        self.deadline_checkbox.toggled.connect(self.toggle_deadline)
        deadline_layout.addWidget(self.deadline_checkbox)
        
        self.deadline_edit = QDateEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDate(QDate.currentDate().addDays(7))
        self.deadline_edit.setEnabled(False)
        deadline_layout.addWidget(self.deadline_edit)
        
        layout.addLayout(deadline_layout)
        
        # 进度
        progress_layout = QHBoxLayout()
        progress_layout.addWidget(QLabel("进度:"))
        self.progress_slider = QSlider(Qt.Orientation.Horizontal)
        self.progress_slider.setRange(0, 100)
        self.progress_slider.setValue(0)
        self.progress_slider.valueChanged.connect(self.update_progress_label)
        progress_layout.addWidget(self.progress_slider)
        
        self.progress_label = QLabel("0%")
        self.progress_label.setMinimumWidth(40)
        progress_layout.addWidget(self.progress_label)
        
        layout.addLayout(progress_layout)
        
        self.setLayout(layout)
    
    def toggle_deadline(self, checked):
        """切换截止日期启用状态"""
        self.deadline_edit.setEnabled(checked)
    
    def update_progress_label(self, value):
        """更新进度标签"""
        self.progress_label.setText(f"{value}%")
    
    def load_goal(self):
        """加载目标数据到UI"""
        if not self.goal:
            return
        
        self.title_edit.setText(self.goal.title)
        self.description_edit.setText(self.goal.description)
        self.type_combo.setCurrentIndex(0 if self.goal.type == "short_term" else 1)
        self.priority_spin.setValue(self.goal.priority)
        self.progress_slider.setValue(int(self.goal.progress))
        
        if self.goal.deadline:
            self.deadline_checkbox.setChecked(True)
            self.deadline_edit.setDate(QDate(
                self.goal.deadline.year,
                self.goal.deadline.month,
                self.goal.deadline.day
            ))
    
    def get_goal(self) -> Goal:
        """从UI获取目标数据"""
        title = self.title_edit.text().strip()
        description = self.description_edit.toPlainText().strip()
        goal_type = "short_term" if self.type_combo.currentIndex() == 0 else "long_term"
        priority = self.priority_spin.value()
        progress = self.progress_slider.value()
        
        deadline = None
        if self.deadline_checkbox.isChecked():
            qdate = self.deadline_edit.date()
            deadline = datetime(qdate.year(), qdate.month(), qdate.day())
        
        if self.goal:
            # 更新现有目标
            self.goal.title = title
            self.goal.description = description
            self.goal.type = goal_type
            self.goal.priority = priority
            self.goal.progress = progress
            self.goal.deadline = deadline
            return self.goal
        else:
            # 创建新目标
            return Goal(
                title=title,
                description=description,
                type=goal_type,
                priority=priority,
                progress=progress,
                deadline=deadline
            )
    
    def validate(self) -> bool:
        """验证输入"""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "提示", "请输入目标标题")
            return False
        
        if not self.description_edit.toPlainText().strip():
            QMessageBox.warning(self, "提示", "请输入目标描述")
            return False
        
        return True


class GoalsDialog(QDialog):
    """目标管理对话框"""
    
    def __init__(self, parent=None):
        """初始化对话框"""
        super().__init__(parent)
        self.goals_manager = GoalsManager()
        self.init_ui()
        self.load_goals()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("目标管理")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("管理您的长期和短期目标")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        title_label.setFont(font)
        layout.addWidget(title_label)
        
        # 选项卡
        self.tab_widget = QTabWidget()
        
        # 目标列表选项卡
        self.list_widget = QWidget()
        self.setup_list_tab()
        self.tab_widget.addTab(self.list_widget, "目标列表")
        
        # 新建/编辑选项卡
        self.edit_widget = GoalEditWidget()
        self.tab_widget.addTab(self.edit_widget, "新建目标")
        
        layout.addWidget(self.tab_widget)
        
        # 按钮栏
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("关闭")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.save_button = QPushButton("保存")
        self.save_button.clicked.connect(self.save_goal)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_list_tab(self):
        """设置列表选项卡"""
        layout = QVBoxLayout()
        
        # 过滤器
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("显示:"))
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["所有目标", "长期目标", "短期目标", "已完成"])
        self.filter_combo.currentIndexChanged.connect(self.filter_goals)
        filter_layout.addWidget(self.filter_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # 目标列表
        self.goals_list = QListWidget()
        self.goals_list.itemDoubleClicked.connect(self.edit_goal)
        layout.addWidget(self.goals_list)
        
        # 操作按钮
        action_layout = QHBoxLayout()
        
        self.edit_button = QPushButton("编辑")
        self.edit_button.clicked.connect(self.edit_goal)
        action_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("删除")
        self.delete_button.clicked.connect(self.delete_goal)
        action_layout.addWidget(self.delete_button)
        
        self.complete_button = QPushButton("标记完成")
        self.complete_button.clicked.connect(self.complete_goal)
        action_layout.addWidget(self.complete_button)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        self.list_widget.setLayout(layout)
    
    def load_goals(self):
        """加载目标列表"""
        self.goals_list.clear()
        goals = self.goals_manager.goals
        
        for i, goal in enumerate(goals):
            item_text = f"[{'短期' if goal.type == 'short_term' else '长期'}] "
            item_text += f"{goal.title} (优先级:{goal.priority}, 进度:{goal.progress:.0f}%)"
            
            if not goal.is_active:
                item_text += " [已完成]"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, i)  # 存储索引
            
            # 根据状态设置颜色
            if not goal.is_active:
                item.setForeground(Qt.GlobalColor.gray)
            elif goal.priority >= 4:
                item.setForeground(Qt.GlobalColor.red)
            
            self.goals_list.addItem(item)
    
    def filter_goals(self):
        """过滤目标显示"""
        filter_type = self.filter_combo.currentIndex()
        
        for i in range(self.goals_list.count()):
            item = self.goals_list.item(i)
            goal_index = item.data(Qt.ItemDataRole.UserRole)
            goal = self.goals_manager.goals[goal_index]
            
            show = True
            if filter_type == 1:  # 长期目标
                show = goal.type == "long_term" and goal.is_active
            elif filter_type == 2:  # 短期目标
                show = goal.type == "short_term" and goal.is_active
            elif filter_type == 3:  # 已完成
                show = not goal.is_active
            
            item.setHidden(not show)
    
    def edit_goal(self):
        """编辑选中的目标"""
        current_item = self.goals_list.currentItem()
        if not current_item:
            return
        
        goal_index = current_item.data(Qt.ItemDataRole.UserRole)
        goal = self.goals_manager.goals[goal_index]
        
        # 切换到编辑选项卡
        self.edit_widget = GoalEditWidget(goal)
        self.tab_widget.removeTab(1)
        self.tab_widget.addTab(self.edit_widget, "编辑目标")
        self.tab_widget.setCurrentIndex(1)
    
    def delete_goal(self):
        """删除选中的目标"""
        current_item = self.goals_list.currentItem()
        if not current_item:
            return
        
        reply = QMessageBox.question(
            self, "确认删除",
            "确定要删除这个目标吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            goal_index = current_item.data(Qt.ItemDataRole.UserRole)
            self.goals_manager.delete_goal(goal_index)
            self.load_goals()
    
    def complete_goal(self):
        """标记目标为完成"""
        current_item = self.goals_list.currentItem()
        if not current_item:
            return
        
        goal_index = current_item.data(Qt.ItemDataRole.UserRole)
        goal = self.goals_manager.goals[goal_index]
        goal.is_active = False
        goal.progress = 100
        self.goals_manager.save_goals()
        self.load_goals()
    
    def save_goal(self):
        """保存当前编辑的目标"""
        if self.tab_widget.currentIndex() != 1:
            return
        
        if not self.edit_widget.validate():
            return
        
        goal = self.edit_widget.get_goal()
        
        # 检查是新建还是更新
        if goal in self.goals_manager.goals:
            # 更新
            self.goals_manager.save_goals()
        else:
            # 新建
            self.goals_manager.add_goal(goal)
        
        self.load_goals()
        
        # 切换回列表选项卡
        self.tab_widget.setCurrentIndex(0)
        
        QMessageBox.information(self, "成功", "目标已保存")