"""
日历对话框

类似 macOS 日历的日程管理界面，提供月视图和日程的增删改查功能。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCalendarWidget,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QWidget, QSplitter, QGroupBox, QMessageBox,
    QToolBar, QComboBox
)
from PyQt6.QtCore import Qt, QDate, QDateTime, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QIcon, QTextCharFormat, QColor, QBrush
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import logging

from ...scheduler.manager import ScheduleManager
from ...scheduler.models import Schedule


class CalendarDialog(QDialog):
    """日历对话框主窗口"""
    
    # 信号：当日程发生变化时发出
    schedule_changed = pyqtSignal()
    
    def __init__(self, schedule_manager: ScheduleManager, parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.logger = logging.getLogger(__name__)
        self.selected_date = QDate.currentDate()
        self.event_dialogs = {}  # 缓存事件对话框
        
        self.init_ui()
        self.load_schedules()
        
        # 定时刷新（每分钟更新一次）
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_current_time)
        self.refresh_timer.start(60000)  # 60秒
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("日程管理")
        self.resize(900, 600)
        
        # 设置窗口模态性
        self.setModal(False)
        
        # 主布局
        layout = QVBoxLayout(self)
        
        # 工具栏
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # 主分割器（水平）
        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 左侧：日历
        left_widget = self.create_calendar_widget()
        main_splitter.addWidget(left_widget)
        
        # 右侧：日程列表
        right_widget = self.create_schedule_list_widget()
        main_splitter.addWidget(right_widget)
        
        # 设置分割比例
        main_splitter.setSizes([500, 400])
        
        layout.addWidget(main_splitter)
        
        # 底部按钮
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("添加日程")
        self.add_btn.clicked.connect(self.add_schedule)
        button_layout.addWidget(self.add_btn)
        
        self.edit_btn = QPushButton("编辑日程")
        self.edit_btn.setEnabled(False)
        self.edit_btn.clicked.connect(self.edit_schedule)
        button_layout.addWidget(self.edit_btn)
        
        self.delete_btn = QPushButton("删除日程")
        self.delete_btn.setEnabled(False)
        self.delete_btn.clicked.connect(self.delete_schedule)
        button_layout.addWidget(self.delete_btn)
        
        button_layout.addStretch()
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
    
    def create_toolbar(self) -> QToolBar:
        """创建工具栏"""
        toolbar = QToolBar()
        
        # 今天按钮
        today_action = QAction("今天", self)
        today_action.triggered.connect(self.go_to_today)
        toolbar.addAction(today_action)
        
        toolbar.addSeparator()
        
        # 视图选择
        self.view_combo = QComboBox()
        self.view_combo.addItems(["月", "周", "日"])
        self.view_combo.currentTextChanged.connect(self.change_view)
        toolbar.addWidget(QLabel("视图："))
        toolbar.addWidget(self.view_combo)
        
        toolbar.addSeparator()
        
        # 刷新按钮
        refresh_action = QAction("刷新", self)
        refresh_action.triggered.connect(self.load_schedules)
        toolbar.addAction(refresh_action)
        
        return toolbar
    
    def create_calendar_widget(self) -> QWidget:
        """创建日历组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 月份标签
        self.month_label = QLabel()
        self.month_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.month_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        layout.addWidget(self.month_label)
        
        # 日历控件
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.clicked.connect(self.on_date_selected)
        self.calendar.currentPageChanged.connect(self.on_page_changed)
        
        # 设置日历样式
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
            }
            QCalendarWidget QTableView {
                selection-background-color: #007AFF;
                selection-color: white;
            }
            QCalendarWidget QTableView::item:selected {
                background-color: #007AFF;
                color: white;
                border-radius: 4px;
            }
            QCalendarWidget QTableView::item:hover {
                background-color: #E5E5EA;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.calendar)
        
        return widget
    
    def create_schedule_list_widget(self) -> QWidget:
        """创建日程列表组件"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 日期标签
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
                background-color: #F2F2F7;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.date_label)
        
        # 分组：全天事件
        self.all_day_group = QGroupBox("全天")
        all_day_layout = QVBoxLayout()
        self.all_day_list = QListWidget()
        self.all_day_list.itemSelectionChanged.connect(self.on_schedule_selected)
        self.all_day_list.itemDoubleClicked.connect(self.edit_schedule)
        all_day_layout.addWidget(self.all_day_list)
        self.all_day_group.setLayout(all_day_layout)
        layout.addWidget(self.all_day_group)
        
        # 分组：定时事件
        self.timed_group = QGroupBox("日程")
        timed_layout = QVBoxLayout()
        self.timed_list = QListWidget()
        self.timed_list.itemSelectionChanged.connect(self.on_schedule_selected)
        self.timed_list.itemDoubleClicked.connect(self.edit_schedule)
        timed_layout.addWidget(self.timed_list)
        self.timed_group.setLayout(timed_layout)
        layout.addWidget(self.timed_group)
        
        # 设置列表样式
        list_style = """
            QListWidget {
                border: none;
                background-color: white;
                border-radius: 8px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #E5E5EA;
            }
            QListWidget::item:selected {
                background-color: #007AFF;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #F2F2F7;
            }
        """
        self.all_day_list.setStyleSheet(list_style)
        self.timed_list.setStyleSheet(list_style)
        
        return widget
    
    def load_schedules(self):
        """加载日程数据"""
        # 更新月份标签
        self.update_month_label()
        
        # 标记有日程的日期
        self.mark_schedule_dates()
        
        # 加载当前选中日期的日程
        self.load_date_schedules(self.selected_date)
    
    def mark_schedule_dates(self):
        """在日历上标记有日程的日期"""
        # 清除所有标记
        self.calendar.setDateTextFormat(QDate(), QTextCharFormat())
        
        # 获取当前月份的日期范围
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        
        # 获取该月第一天和最后一天
        first_date = QDate(year, month, 1)
        if month == 12:
            last_date = QDate(year + 1, 1, 1).addDays(-1)
        else:
            last_date = QDate(year, month + 1, 1).addDays(-1)
        
        # 转换为 datetime
        date_from = datetime(first_date.year(), first_date.month(), first_date.day())
        date_to = datetime(last_date.year(), last_date.month(), last_date.day())
        
        # 获取该月的所有日程
        schedules = self.schedule_manager.list(
            date_from=date_from,
            date_to=date_to
        )
        
        # 标记每个有日程的日期
        format_with_schedule = QTextCharFormat()
        format_with_schedule.setBackground(QBrush(QColor(0, 122, 255, 30)))  # 浅蓝色背景
        
        marked_dates = set()
        for schedule in schedules:
            date = QDate(
                schedule.start_time.year,
                schedule.start_time.month,
                schedule.start_time.day
            )
            if date not in marked_dates:
                self.calendar.setDateTextFormat(date, format_with_schedule)
                marked_dates.add(date)
    
    def load_date_schedules(self, date: QDate):
        """加载指定日期的日程"""
        # 更新日期标签
        self.date_label.setText(date.toString("yyyy年M月d日 dddd"))
        
        # 清空列表
        self.all_day_list.clear()
        self.timed_list.clear()
        
        # 获取该日期的日程
        target_date = datetime(date.year(), date.month(), date.day())
        schedules = self.schedule_manager.get_schedules_for_date(target_date)
        
        # 分类显示
        for schedule in schedules:
            # 创建列表项
            item = QListWidgetItem()
            
            # 判断是否为全天事件（持续时间 >= 1440分钟即24小时）
            is_all_day = schedule.duration_minutes >= 1440
            
            if is_all_day:
                item.setText(f"● {schedule.title}")
                self.all_day_list.addItem(item)
            else:
                # 格式化时间显示
                start_time = schedule.start_time.strftime("%H:%M")
                end_time = (schedule.start_time + timedelta(minutes=schedule.duration_minutes)).strftime("%H:%M")
                
                # 检查是否正在进行
                current_time = datetime.now()
                if schedule.is_in_progress(current_time):
                    item.setText(f"● {start_time}-{end_time}  {schedule.title} [进行中]")
                    item.setForeground(QColor(0, 122, 255))  # 蓝色文字
                elif schedule.has_ended(current_time):
                    item.setText(f"● {start_time}-{end_time}  {schedule.title}")
                    item.setForeground(QColor(142, 142, 147))  # 灰色文字
                else:
                    item.setText(f"● {start_time}-{end_time}  {schedule.title}")
                
                self.timed_list.addItem(item)
            
            # 存储日程ID
            item.setData(Qt.ItemDataRole.UserRole, schedule.id)
        
        # 显示/隐藏分组
        self.all_day_group.setVisible(self.all_day_list.count() > 0)
        self.timed_group.setVisible(self.timed_list.count() > 0)
        
        # 如果没有日程，显示提示
        if self.all_day_list.count() == 0 and self.timed_list.count() == 0:
            item = QListWidgetItem("暂无日程")
            item.setFlags(Qt.ItemFlag.NoItemFlags)
            item.setForeground(QColor(142, 142, 147))
            self.timed_list.addItem(item)
            self.timed_group.setVisible(True)
    
    def on_date_selected(self, date: QDate):
        """处理日期选择"""
        self.selected_date = date
        self.load_date_schedules(date)
    
    def on_page_changed(self, year: int, month: int):
        """处理月份切换"""
        self.update_month_label()
        self.mark_schedule_dates()
    
    def update_month_label(self):
        """更新月份标签"""
        year = self.calendar.yearShown()
        month = self.calendar.monthShown()
        self.month_label.setText(f"{year}年{month}月")
    
    def on_schedule_selected(self):
        """处理日程选择"""
        # 获取当前选中的项
        current_item = None
        if self.all_day_list.currentItem():
            current_item = self.all_day_list.currentItem()
            # 清除另一个列表的选择
            self.timed_list.clearSelection()
        elif self.timed_list.currentItem():
            current_item = self.timed_list.currentItem()
            # 清除另一个列表的选择
            self.all_day_list.clearSelection()
        
        # 更新按钮状态
        has_selection = current_item is not None and current_item.data(Qt.ItemDataRole.UserRole) is not None
        self.edit_btn.setEnabled(has_selection)
        self.delete_btn.setEnabled(has_selection)
    
    def add_schedule(self):
        """添加日程"""
        dialog = ScheduleEditDialog(
            self.schedule_manager,
            default_date=self.selected_date,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_schedules()
            self.schedule_changed.emit()
    
    def edit_schedule(self):
        """编辑日程"""
        # 获取选中的日程ID
        schedule_id = self.get_selected_schedule_id()
        if not schedule_id:
            return
        
        # 获取日程对象
        schedule = self.schedule_manager.get(schedule_id)
        if not schedule:
            return
        
        dialog = ScheduleEditDialog(
            self.schedule_manager,
            schedule=schedule,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_schedules()
            self.schedule_changed.emit()
    
    def delete_schedule(self):
        """删除日程"""
        # 获取选中的日程ID
        schedule_id = self.get_selected_schedule_id()
        if not schedule_id:
            return
        
        # 获取日程对象
        schedule = self.schedule_manager.get(schedule_id)
        if not schedule:
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除日程 \"{schedule.title}\" 吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.schedule_manager.delete(schedule_id):
                self.load_schedules()
                self.schedule_changed.emit()
    
    def get_selected_schedule_id(self) -> Optional[str]:
        """获取选中的日程ID"""
        current_item = None
        if self.all_day_list.currentItem():
            current_item = self.all_day_list.currentItem()
        elif self.timed_list.currentItem():
            current_item = self.timed_list.currentItem()
        
        if current_item:
            return current_item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def go_to_today(self):
        """跳转到今天"""
        today = QDate.currentDate()
        self.calendar.setSelectedDate(today)
        self.calendar.setCurrentPage(today.year(), today.month())
        self.on_date_selected(today)
    
    def change_view(self, view_type: str):
        """切换视图类型（预留功能）"""
        # 目前只实现了月视图，周视图和日视图留作扩展
        if view_type == "月":
            pass
        elif view_type == "周":
            QMessageBox.information(self, "提示", "周视图功能开发中...")
        elif view_type == "日":
            QMessageBox.information(self, "提示", "日视图功能开发中...")
    
    def refresh_current_time(self):
        """刷新当前时间（更新进行中的日程状态）"""
        # 重新加载当前日期的日程
        self.load_date_schedules(self.selected_date)


class ScheduleEditDialog(QDialog):
    """日程编辑对话框"""
    
    def __init__(self, schedule_manager: ScheduleManager, 
                 schedule: Optional[Schedule] = None,
                 default_date: Optional[QDate] = None,
                 parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.schedule = schedule
        self.default_date = default_date or QDate.currentDate()
        
        self.init_ui()
        
        if schedule:
            self.load_schedule_data()
    
    def init_ui(self):
        """初始化UI"""
        self.setWindowTitle("编辑日程" if self.schedule else "添加日程")
        self.resize(500, 400)
        self.setModal(True)
        
        from PyQt6.QtWidgets import (
            QFormLayout, QLineEdit, QTextEdit, 
            QDateTimeEdit, QSpinBox, QCheckBox,
            QDialogButtonBox
        )
        
        layout = QVBoxLayout(self)
        
        # 表单布局
        form = QFormLayout()
        
        # 标题
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("请输入日程标题...")
        form.addRow("标题:", self.title_edit)
        
        # 详情
        self.details_edit = QTextEdit()
        self.details_edit.setPlaceholderText("请输入日程详情...")
        self.details_edit.setMaximumHeight(100)
        form.addRow("详情:", self.details_edit)
        
        # 全天事件
        self.all_day_check = QCheckBox("全天事件")
        self.all_day_check.toggled.connect(self.on_all_day_toggled)
        form.addRow("", self.all_day_check)
        
        # 开始时间
        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setCalendarPopup(True)
        self.start_datetime.setDateTime(
            QDateTime(self.default_date, QDateTime.currentDateTime().time())
        )
        self.start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        form.addRow("开始时间:", self.start_datetime)
        
        # 持续时间
        self.duration_layout = QHBoxLayout()
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 1440 * 7)  # 5分钟到7天
        self.duration_spin.setValue(60)
        self.duration_spin.setSuffix(" 分钟")
        self.duration_layout.addWidget(self.duration_spin)
        
        # 快捷时长按钮
        for text, minutes in [("30分钟", 30), ("1小时", 60), ("2小时", 120), ("半天", 720), ("全天", 1440)]:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, m=minutes: self.duration_spin.setValue(m))
            self.duration_layout.addWidget(btn)
        
        form.addRow("持续时间:", self.duration_layout)
        
        # 是否激活
        self.active_check = QCheckBox("激活日程")
        self.active_check.setChecked(True)
        form.addRow("", self.active_check)
        
        layout.addLayout(form)
        
        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self.save_schedule)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def on_all_day_toggled(self, checked: bool):
        """处理全天事件切换"""
        if checked:
            # 设置为全天事件
            self.start_datetime.setDisplayFormat("yyyy-MM-dd")
            self.start_datetime.setTime(QDateTime.currentDateTime().time().replace(hour=0, minute=0))
            self.duration_spin.setValue(1440)  # 24小时
            self.duration_spin.setEnabled(False)
        else:
            # 恢复为定时事件
            self.start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
            self.duration_spin.setValue(60)
            self.duration_spin.setEnabled(True)
    
    def load_schedule_data(self):
        """加载日程数据"""
        if not self.schedule:
            return
        
        self.title_edit.setText(self.schedule.title)
        self.details_edit.setPlainText(self.schedule.details)
        
        # 设置时间
        dt = QDateTime(
            self.schedule.start_time.year,
            self.schedule.start_time.month,
            self.schedule.start_time.day,
            self.schedule.start_time.hour,
            self.schedule.start_time.minute
        )
        self.start_datetime.setDateTime(dt)
        
        # 设置持续时间
        self.duration_spin.setValue(self.schedule.duration_minutes)
        
        # 检查是否为全天事件
        if self.schedule.duration_minutes >= 1440:
            self.all_day_check.setChecked(True)
        
        # 设置激活状态
        self.active_check.setChecked(self.schedule.is_active)
    
    def save_schedule(self):
        """保存日程"""
        # 验证输入
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "警告", "请输入日程标题")
            return
        
        details = self.details_edit.toPlainText().strip()
        
        # 获取时间
        dt = self.start_datetime.dateTime()
        start_time = datetime(
            dt.date().year(),
            dt.date().month(),
            dt.date().day(),
            dt.time().hour(),
            dt.time().minute()
        )
        
        duration_minutes = self.duration_spin.value()
        is_active = self.active_check.isChecked()
        
        try:
            if self.schedule:
                # 更新现有日程
                self.schedule_manager.update(
                    self.schedule.id,
                    title=title,
                    details=details,
                    start_time=start_time,
                    duration_minutes=duration_minutes,
                    is_active=is_active
                )
            else:
                # 创建新日程
                self.schedule_manager.add(
                    title=title,
                    details=details,
                    start_time=start_time,
                    duration_minutes=duration_minutes
                )
            
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"保存日程失败：{str(e)}")