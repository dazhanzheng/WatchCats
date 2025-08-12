"""
现代化日历对话框

采用苹果设计语言的日程管理界面，支持日、周、月三种视图。
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QCalendarWidget,
    QPushButton, QLabel, QListWidget, QListWidgetItem,
    QWidget, QSplitter, QGroupBox, QMessageBox,
    QToolBar, QComboBox, QStackedWidget, QScrollArea,
    QFrame, QGridLayout, QSizePolicy, QButtonGroup
)
from PyQt6.QtCore import (
    Qt, QDate, QDateTime, pyqtSignal, QTimer,
    QPropertyAnimation, QEasingCurve, QRect, QPoint,
    QSize, QTime
)
from PyQt6.QtGui import (
    QAction, QIcon, QTextCharFormat, QColor, QBrush,
    QPainter, QPen, QFont, QFontMetrics, QPalette,
    QLinearGradient, QRadialGradient
)
from datetime import datetime, timedelta, date
from typing import Optional, List, Dict, Tuple
import logging
import math

from ...scheduler.manager import ScheduleManager
from ...scheduler.models import Schedule


class ModernCalendarDialog(QDialog):
    """现代化日历对话框主窗口"""
    
    schedule_changed = pyqtSignal()
    
    def __init__(self, schedule_manager: ScheduleManager, parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.logger = logging.getLogger(__name__)
        self.selected_date = QDate.currentDate()
        self.current_view = "月"  # 默认视图
        
        self.init_ui()
        self.load_schedules()
        
        # 定时刷新
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_current_time)
        self.refresh_timer.start(60000)  # 60秒
    
    def init_ui(self):
        """初始化UI - 苹果设计风格"""
        self.setWindowTitle("日程")
        self.resize(1100, 750)
        self.setModal(False)
        
        # 设置圆角和阴影
        self.setStyleSheet("""
            QDialog {
                background-color: #f6f6f6;
                border-radius: 12px;
            }
        """)
        
        # 主布局
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # 顶部工具栏
        toolbar_widget = self.create_modern_toolbar()
        layout.addWidget(toolbar_widget)
        
        # 内容区域
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # 视图堆栈
        self.view_stack = QStackedWidget()
        self.view_stack.setStyleSheet("background: transparent;")
        
        # 创建三种视图
        self.day_view = DayView(self.schedule_manager, self)
        self.week_view = WeekView(self.schedule_manager, self)
        self.month_view = MonthView(self.schedule_manager, self)
        
        # 连接信号
        for view in [self.day_view, self.week_view, self.month_view]:
            view.schedule_changed.connect(self.schedule_changed.emit)
            view.date_selected.connect(self.on_date_selected)
        
        # 添加到堆栈
        self.view_stack.addWidget(self.day_view)
        self.view_stack.addWidget(self.week_view)
        self.view_stack.addWidget(self.month_view)
        
        # 默认显示月视图并初始化
        self.view_stack.setCurrentWidget(self.month_view)
        self.month_view.set_month(self.selected_date)  # 初始化月视图数据
        
        content_layout.addWidget(self.view_stack)
        layout.addWidget(content_widget)
    
    def create_modern_toolbar(self) -> QWidget:
        """创建现代化工具栏"""
        toolbar = QWidget()
        toolbar.setFixedHeight(60)
        toolbar.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #fafafa, stop:1 #f0f0f0);
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # 今天按钮
        self.today_btn = self.create_toolbar_button("今天")
        self.today_btn.clicked.connect(self.go_to_today)
        layout.addWidget(self.today_btn)
        
        # 导航按钮
        self.prev_btn = self.create_nav_button("◀")
        self.prev_btn.clicked.connect(self.go_previous)
        layout.addWidget(self.prev_btn)
        
        self.next_btn = self.create_nav_button("▶")
        self.next_btn.clicked.connect(self.go_next)
        layout.addWidget(self.next_btn)
        
        # 当前日期标签
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #333;
                padding: 0 20px;
            }
        """)
        layout.addWidget(self.date_label)
        
        layout.addStretch()
        
        # 视图切换按钮组
        view_widget = QWidget()
        view_widget.setStyleSheet("""
            QWidget {
                background: #e5e5e5;
                border-radius: 8px;
            }
        """)
        view_layout = QHBoxLayout(view_widget)
        view_layout.setContentsMargins(2, 2, 2, 2)
        view_layout.setSpacing(2)
        
        self.view_buttons = QButtonGroup()
        for view_name in ["日", "周", "月"]:
            btn = QPushButton(view_name)
            btn.setCheckable(True)
            btn.setFixedSize(60, 32)
            btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-radius: 6px;
                    font-size: 14px;
                    font-weight: 500;
                    color: #666;
                }
                QPushButton:checked {
                    background: white;
                    color: #007AFF;
                    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
                }
                QPushButton:hover:!checked {
                    background: rgba(255,255,255,0.5);
                }
            """)
            if view_name == "月":
                btn.setChecked(True)
            btn.clicked.connect(lambda checked, v=view_name: self.switch_view(v))
            self.view_buttons.addButton(btn)
            view_layout.addWidget(btn)
        
        layout.addWidget(view_widget)
        
        layout.addSpacing(20)
        
        # 添加日程按钮
        self.add_btn = self.create_toolbar_button("+ 添加")
        self.add_btn.setStyleSheet("""
            QPushButton {
                background: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #0051D5;
            }
            QPushButton:pressed {
                background: #004494;
            }
        """)
        self.add_btn.clicked.connect(self.add_schedule)
        layout.addWidget(self.add_btn)
        
        return toolbar
    
    def create_toolbar_button(self, text: str) -> QPushButton:
        """创建工具栏按钮"""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 8px 16px;
                font-size: 14px;
                font-weight: 500;
                color: #333;
            }
            QPushButton:hover {
                background: #f8f8f8;
                border-color: #007AFF;
                color: #007AFF;
            }
            QPushButton:pressed {
                background: #e8e8e8;
            }
        """)
        return btn
    
    def create_nav_button(self, text: str) -> QPushButton:
        """创建导航按钮"""
        btn = QPushButton(text)
        btn.setFixedSize(36, 36)
        btn.setStyleSheet("""
            QPushButton {
                background: white;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                font-size: 16px;
                color: #333;
            }
            QPushButton:hover {
                background: #f8f8f8;
                border-color: #007AFF;
                color: #007AFF;
            }
            QPushButton:pressed {
                background: #e8e8e8;
            }
        """)
        return btn
    
    def switch_view(self, view_name: str):
        """切换视图"""
        self.current_view = view_name
        
        if view_name == "日":
            self.view_stack.setCurrentWidget(self.day_view)
            self.day_view.set_date(self.selected_date)
        elif view_name == "周":
            self.view_stack.setCurrentWidget(self.week_view)
            self.week_view.set_week(self.selected_date)
        elif view_name == "月":
            self.view_stack.setCurrentWidget(self.month_view)
            self.month_view.set_month(self.selected_date)
        
        self.update_date_label()
    
    def update_date_label(self):
        """更新日期标签"""
        if self.current_view == "日":
            self.date_label.setText(self.selected_date.toString("yyyy年M月d日"))
        elif self.current_view == "周":
            # 显示周范围
            week_start = self.selected_date.addDays(-(self.selected_date.dayOfWeek() - 1))
            week_end = week_start.addDays(6)
            if week_start.month() == week_end.month():
                self.date_label.setText(f"{week_start.year()}年{week_start.month()}月 {week_start.day()}-{week_end.day()}日")
            else:
                self.date_label.setText(f"{week_start.toString('M月d日')} - {week_end.toString('M月d日')}")
        elif self.current_view == "月":
            self.date_label.setText(f"{self.selected_date.year()}年{self.selected_date.month()}月")
    
    def go_to_today(self):
        """跳转到今天"""
        self.selected_date = QDate.currentDate()
        self.switch_view(self.current_view)
    
    def go_previous(self):
        """导航到上一个周期"""
        if self.current_view == "日":
            self.selected_date = self.selected_date.addDays(-1)
        elif self.current_view == "周":
            self.selected_date = self.selected_date.addDays(-7)
        elif self.current_view == "月":
            self.selected_date = self.selected_date.addMonths(-1)
        self.switch_view(self.current_view)
    
    def go_next(self):
        """导航到下一个周期"""
        if self.current_view == "日":
            self.selected_date = self.selected_date.addDays(1)
        elif self.current_view == "周":
            self.selected_date = self.selected_date.addDays(7)
        elif self.current_view == "月":
            self.selected_date = self.selected_date.addMonths(1)
        self.switch_view(self.current_view)
    
    def on_date_selected(self, date: QDate):
        """处理日期选择"""
        # 只在来自当前视图的选择时更新
        sender = self.sender()
        current_widget = self.view_stack.currentWidget()
        
        # 只有当信号来自当前显示的视图时才更新选中日期
        if sender == current_widget:
            self.selected_date = date
            self.update_date_label()
    
    def load_schedules(self):
        """加载日程数据"""
        # 各视图自行加载
        pass
    
    def refresh_current_time(self):
        """刷新当前时间"""
        current_widget = self.view_stack.currentWidget()
        if hasattr(current_widget, 'refresh'):
            current_widget.refresh()
    
    def add_schedule(self):
        """添加日程"""
        from .schedule_edit_dialog import ModernScheduleEditDialog
        dialog = ModernScheduleEditDialog(
            self.schedule_manager,
            default_date=self.selected_date,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_current_time()
            self.schedule_changed.emit()


class DayView(QWidget):
    """日视图 - 24小时时间线"""
    
    schedule_changed = pyqtSignal()
    date_selected = pyqtSignal(QDate)
    
    def __init__(self, schedule_manager: ScheduleManager, parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.current_date = QDate.currentDate()
        self.hour_height = 60  # 每小时的高度
        self.init_ui()
    
    def init_ui(self):
        """初始化日视图UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建滚动区域
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: white;
            }
            QScrollBar:vertical {
                background: #f0f0f0;
                width: 10px;
                border-radius: 5px;
            }
            QScrollBar::handle:vertical {
                background: #c0c0c0;
                border-radius: 5px;
                min-height: 30px;
            }
            QScrollBar::handle:vertical:hover {
                background: #a0a0a0;
            }
        """)
        
        # 时间线容器
        self.timeline_widget = TimelineWidget(self.schedule_manager)
        self.timeline_widget.schedule_clicked.connect(self.on_schedule_clicked)
        scroll.setWidget(self.timeline_widget)
        
        layout.addWidget(scroll)
        
        # 滚动到当前时间
        QTimer.singleShot(100, self.scroll_to_current_time)
    
    def set_date(self, date: QDate):
        """设置日期"""
        self.current_date = date
        self.timeline_widget.set_date(date)
        self.date_selected.emit(date)
    
    def scroll_to_current_time(self):
        """滚动到当前时间"""
        current_hour = QTime.currentTime().hour()
        scroll = self.findChild(QScrollArea)
        if scroll:
            scroll.verticalScrollBar().setValue(current_hour * self.hour_height - 100)
    
    def refresh(self):
        """刷新视图"""
        self.timeline_widget.update()
    
    def on_schedule_clicked(self, schedule_id: str):
        """处理日程点击"""
        schedule = self.schedule_manager.get(schedule_id)
        if schedule:
            from .schedule_edit_dialog import ModernScheduleEditDialog as ScheduleEditDialog
            dialog = ScheduleEditDialog(
                self.schedule_manager,
                schedule=schedule,
                parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh()
                self.schedule_changed.emit()


class TimelineWidget(QWidget):
    """时间线组件"""
    
    schedule_clicked = pyqtSignal(str)
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.current_date = QDate.currentDate()
        self.hour_height = 60
        self.time_width = 80
        self.setMinimumHeight(24 * self.hour_height)
        self.schedules = []
        
    def set_date(self, date: QDate):
        """设置日期"""
        self.current_date = date
        self.load_schedules()
        self.update()
    
    def load_schedules(self):
        """加载当日日程"""
        target_date = datetime(
            self.current_date.year(),
            self.current_date.month(),
            self.current_date.day()
        )
        self.schedules = self.schedule_manager.get_schedules_for_date(target_date)
    
    def paintEvent(self, event):
        """绘制时间线"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor(255, 255, 255))
        
        # 绘制时间刻度
        for hour in range(24):
            y = hour * self.hour_height
            
            # 时间文本
            painter.setPen(QPen(QColor(150, 150, 150), 1))
            painter.setFont(QFont("SF Pro Display", 12))
            time_text = f"{hour:02d}:00"
            painter.drawText(10, y + 20, time_text)
            
            # 水平线
            painter.setPen(QPen(QColor(230, 230, 230), 1))
            painter.drawLine(self.time_width, y, self.width(), y)
            
            # 半小时线
            painter.setPen(QPen(QColor(240, 240, 240), 1, Qt.PenStyle.DotLine))
            painter.drawLine(self.time_width, y + self.hour_height // 2, 
                           self.width(), y + self.hour_height // 2)
        
        # 当前时间线
        if self.current_date == QDate.currentDate():
            current_time = QTime.currentTime()
            current_y = (current_time.hour() * 60 + current_time.minute()) * self.hour_height / 60
            painter.setPen(QPen(QColor(255, 59, 48), 2))
            painter.drawLine(self.time_width, current_y, self.width(), current_y)
            
            # 时间标签
            painter.fillRect(self.time_width - 5, current_y - 10, 60, 20, QColor(255, 59, 48))
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("SF Pro Display", 10, QFont.Weight.Bold))
            painter.drawText(self.time_width, current_y - 10, 50, 20, 
                           Qt.AlignmentFlag.AlignCenter, current_time.toString("HH:mm"))
        
        # 绘制日程
        self.draw_schedules(painter)
    
    def draw_schedules(self, painter: QPainter):
        """绘制日程块"""
        for schedule in self.schedules:
            # 计算位置
            start_hour = schedule.start_time.hour
            start_minute = schedule.start_time.minute
            y = (start_hour * 60 + start_minute) * self.hour_height / 60
            
            # 计算高度 - 对于短时间日程，设置更明显的最小高度
            height = max(30, schedule.duration_minutes * self.hour_height / 60)
            
            # 绘制日程块
            x = self.time_width + 20
            width = self.width() - x - 40
            
            # 渐变背景
            gradient = QLinearGradient(x, y, x + width, y)
            if schedule.is_in_progress(datetime.now()):
                gradient.setColorAt(0, QColor(0, 122, 255, 180))
                gradient.setColorAt(1, QColor(0, 122, 255, 120))
            else:
                gradient.setColorAt(0, QColor(52, 199, 89, 180))
                gradient.setColorAt(1, QColor(52, 199, 89, 120))
            
            # 圆角矩形
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(x, y, width, height, 8, 8)
            
            # 标题
            painter.setPen(Qt.GlobalColor.white)
            painter.setFont(QFont("SF Pro Display", 13, QFont.Weight.Bold))
            text_rect = QRect(x + 10, int(y + 5), width - 20, 20)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft, schedule.title)
            
            # 时间 - 增加与标题的间距
            if height > 40:
                painter.setFont(QFont("SF Pro Display", 11))
                time_text = f"{schedule.start_time.strftime('%H:%M')} - {(schedule.start_time + timedelta(minutes=schedule.duration_minutes)).strftime('%H:%M')}"
                painter.drawText(x + 10, y + 30, time_text)  # 从 y+25 改为 y+30
            
            # 存储位置用于点击检测
            schedule.draw_rect = QRect(x, int(y), width, int(height))
    
    def mousePressEvent(self, event):
        """处理鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            for schedule in self.schedules:
                if hasattr(schedule, 'draw_rect') and schedule.draw_rect.contains(event.pos()):
                    self.schedule_clicked.emit(schedule.id)
                    break


class WeekView(QWidget):
    """周视图 - 7天时间线网格"""
    
    schedule_changed = pyqtSignal()
    date_selected = pyqtSignal(QDate)
    
    def __init__(self, schedule_manager: ScheduleManager, parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.current_week_start = None
        self.selected_date = QDate.currentDate()  # 周视图独立的选中日期
        self.init_ui()
    
    def init_ui(self):
        """初始化周视图UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 星期标题
        self.header_widget = WeekHeaderWidget()
        layout.addWidget(self.header_widget)
        
        # 时间网格
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: white;
            }
        """)
        
        self.grid_widget = WeekGridWidget(self.schedule_manager)
        self.grid_widget.schedule_clicked.connect(self.on_schedule_clicked)
        scroll.setWidget(self.grid_widget)
        
        layout.addWidget(scroll)
    
    def set_week(self, date: QDate):
        """设置周"""
        # 计算周一
        self.current_week_start = date.addDays(-(date.dayOfWeek() - 1))
        self.header_widget.set_week(self.current_week_start)
        self.grid_widget.set_week(self.current_week_start)
        self.date_selected.emit(date)
    
    def refresh(self):
        """刷新视图"""
        if self.current_week_start:
            self.grid_widget.set_week(self.current_week_start)
    
    def on_schedule_clicked(self, schedule_id: str):
        """处理日程点击"""
        schedule = self.schedule_manager.get(schedule_id)
        if schedule:
            from .schedule_edit_dialog import ModernScheduleEditDialog as ScheduleEditDialog
            dialog = ScheduleEditDialog(
                self.schedule_manager,
                schedule=schedule,
                parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh()
                self.schedule_changed.emit()


class WeekHeaderWidget(QWidget):
    """周视图标题栏"""
    
    def __init__(self):
        super().__init__()
        self.setFixedHeight(50)
        self.week_start = QDate.currentDate()
        
    def set_week(self, week_start: QDate):
        """设置周开始日期"""
        self.week_start = week_start
        self.update()
    
    def paintEvent(self, event):
        """绘制星期标题"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), QColor(248, 248, 248))
        
        # 时间列宽度
        time_width = 80
        day_width = (self.width() - time_width) / 7
        
        # 绘制星期标题
        weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
        today = QDate.currentDate()
        
        for i in range(7):
            x = time_width + i * day_width
            current_date = self.week_start.addDays(i)
            
            # 高亮今天 - 使用非常淡的背景
            if current_date == today:
                painter.fillRect(x, 0, day_width, self.height(), QColor(250, 250, 250))
            
            # 星期文本
            painter.setPen(QColor(100, 100, 100))
            painter.setFont(QFont("SF Pro Display", 12))
            painter.drawText(QRect(int(x), 10, int(day_width), 20), 
                           Qt.AlignmentFlag.AlignCenter, weekdays[i])
            
            # 日期
            painter.setPen(QColor(50, 50, 50))
            painter.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
            painter.drawText(QRect(int(x), 25, int(day_width), 20), 
                           Qt.AlignmentFlag.AlignCenter, str(current_date.day()))
            
            # 分隔线
            if i < 6:
                painter.setPen(QPen(QColor(230, 230, 230), 1))
                painter.drawLine(x + day_width, 0, x + day_width, self.height())


class WeekGridWidget(QWidget):
    """周视图时间网格"""
    
    schedule_clicked = pyqtSignal(str)
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.week_start = QDate.currentDate()
        self.hour_height = 40
        self.time_width = 80
        self.setMinimumHeight(24 * self.hour_height)
        self.week_schedules = {}  # 按日期存储日程
        
    def set_week(self, week_start: QDate):
        """设置周开始日期"""
        self.week_start = week_start
        self.load_schedules()
        self.update()
    
    def load_schedules(self):
        """加载一周的日程"""
        self.week_schedules = {}
        for i in range(7):
            date = self.week_start.addDays(i)
            target_date = datetime(date.year(), date.month(), date.day())
            self.week_schedules[i] = self.schedule_manager.get_schedules_for_date(target_date)
    
    def paintEvent(self, event):
        """绘制周网格"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        
        day_width = (self.width() - self.time_width) / 7
        
        # 绘制时间刻度和网格
        for hour in range(24):
            y = hour * self.hour_height
            
            # 时间文本
            painter.setPen(QColor(150, 150, 150))
            painter.setFont(QFont("SF Pro Display", 10))
            painter.drawText(10, y + 15, f"{hour:02d}:00")
            
            # 横线
            painter.setPen(QPen(QColor(230, 230, 230), 1))
            painter.drawLine(self.time_width, y, self.width(), y)
        
        # 绘制垂直分隔线
        for i in range(8):
            x = self.time_width + i * day_width
            painter.setPen(QPen(QColor(230, 230, 230), 1))
            painter.drawLine(x, 0, x, self.height())
        
        # 当前时间线
        if self.week_start <= QDate.currentDate() <= self.week_start.addDays(6):
            current_time = QTime.currentTime()
            current_day = QDate.currentDate().dayOfWeek() - self.week_start.dayOfWeek()
            if current_day < 0:
                current_day += 7
            
            x = self.time_width + current_day * day_width
            y = (current_time.hour() * 60 + current_time.minute()) * self.hour_height / 60
            
            painter.setPen(QPen(QColor(255, 59, 48), 2))
            painter.drawLine(x, y, x + day_width, y)
        
        # 绘制日程
        for day, schedules in self.week_schedules.items():
            x = self.time_width + day * day_width + 5
            width = day_width - 10
            
            for schedule in schedules:
                if schedule.duration_minutes >= 1440:  # 全天事件
                    continue
                    
                start_hour = schedule.start_time.hour
                start_minute = schedule.start_time.minute
                y = (start_hour * 60 + start_minute) * self.hour_height / 60
                height = max(25, schedule.duration_minutes * self.hour_height / 60)
                
                # 绘制日程块
                color = QColor(0, 122, 255) if schedule.is_in_progress(datetime.now()) else QColor(52, 199, 89)
                painter.fillRect(x, y, width, height, color.lighter(150))
                
                # 边框
                painter.setPen(QPen(color, 1))
                painter.drawRect(x, y, width, height)
                
                # 标题（如果空间足够）
                if height > 15:
                    painter.setPen(Qt.GlobalColor.black)
                    painter.setFont(QFont("SF Pro Display", 9))
                    text_rect = QRect(int(x + 2), int(y + 2), int(width - 4), int(height - 4))
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop, 
                                   schedule.title[:20])
                
                # 存储位置
                schedule.draw_rect = QRect(int(x), int(y), int(width), int(height))
    
    def mousePressEvent(self, event):
        """处理鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            for schedules in self.week_schedules.values():
                for schedule in schedules:
                    if hasattr(schedule, 'draw_rect') and schedule.draw_rect.contains(event.pos()):
                        self.schedule_clicked.emit(schedule.id)
                        return


class MonthView(QWidget):
    """月视图 - 日历格子"""
    
    schedule_changed = pyqtSignal()
    date_selected = pyqtSignal(QDate)
    
    def __init__(self, schedule_manager: ScheduleManager, parent=None):
        super().__init__(parent)
        self.schedule_manager = schedule_manager
        self.current_month = QDate.currentDate()
        self.selected_date = QDate.currentDate()
        self.init_ui()
    
    def init_ui(self):
        """初始化月视图UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 月历网格
        self.calendar_grid = MonthGridWidget(self.schedule_manager)
        self.calendar_grid.date_clicked.connect(self.on_date_clicked)
        self.calendar_grid.schedule_clicked.connect(self.on_schedule_clicked)
        
        # 初始化时设置当前月份，确保日程加载
        self.calendar_grid.set_month(self.current_month)
        
        layout.addWidget(self.calendar_grid)
    
    def set_month(self, date: QDate):
        """设置月份"""
        self.current_month = date
        self.calendar_grid.set_month(date)
    
    def on_date_clicked(self, date: QDate):
        """处理日期点击"""
        self.selected_date = date
        self.calendar_grid.selected_date = date  # 更新网格的选中日期
        self.calendar_grid.update()  # 刷新显示
        self.date_selected.emit(date)
    
    def on_schedule_clicked(self, schedule_id: str):
        """处理日程点击"""
        schedule = self.schedule_manager.get(schedule_id)
        if schedule:
            from .schedule_edit_dialog import ModernScheduleEditDialog as ScheduleEditDialog
            dialog = ScheduleEditDialog(
                self.schedule_manager,
                schedule=schedule,
                parent=self
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                self.refresh()
                self.schedule_changed.emit()
    
    def refresh(self):
        """刷新视图"""
        self.calendar_grid.set_month(self.current_month)


class MonthGridWidget(QWidget):
    """月视图日历网格"""
    
    date_clicked = pyqtSignal(QDate)
    schedule_clicked = pyqtSignal(str)
    
    def __init__(self, schedule_manager: ScheduleManager):
        super().__init__()
        self.schedule_manager = schedule_manager
        self.current_month = QDate.currentDate()
        self.selected_date = QDate.currentDate()
        self.month_schedules = {}
        self.cell_rects = {}  # 存储每个日期的矩形区域
        self.schedule_rects = {}  # 存储日程的矩形区域
        
        # 初始化时加载当月日程
        self.load_schedules()
        
    def set_month(self, date: QDate):
        """设置月份"""
        self.current_month = QDate(date.year(), date.month(), 1)
        self.load_schedules()
        self.update()
    
    def load_schedules(self):
        """加载月份日程"""
        # 获取月份第一天和最后一天
        first_day = self.current_month
        if first_day.month() == 12:
            last_day = QDate(first_day.year() + 1, 1, 1).addDays(-1)
        else:
            last_day = QDate(first_day.year(), first_day.month() + 1, 1).addDays(-1)
        
        # 加载日程
        date_from = datetime(first_day.year(), first_day.month(), first_day.day())
        date_to = datetime(last_day.year(), last_day.month(), last_day.day())
        
        all_schedules = self.schedule_manager.list(date_from=date_from, date_to=date_to)
        
        # 按日期分组
        self.month_schedules = {}
        for schedule in all_schedules:
            date_key = schedule.start_time.date()
            if date_key not in self.month_schedules:
                self.month_schedules[date_key] = []
            self.month_schedules[date_key].append(schedule)
    
    def paintEvent(self, event):
        """绘制月历"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 清空矩形记录
        self.cell_rects.clear()
        self.schedule_rects.clear()
        
        # 背景
        painter.fillRect(self.rect(), Qt.GlobalColor.white)
        
        # 计算单元格大小
        cell_width = self.width() / 7
        header_height = 35  # 减小标题高度，给格子更多空间
        cell_height = (self.height() - header_height) / 5.8  # 稍微增加格子高度
        
        # 绘制星期标题
        weekdays = ["一", "二", "三", "四", "五", "六", "日"]
        painter.fillRect(0, 0, self.width(), header_height, QColor(248, 248, 248))
        painter.setPen(QColor(100, 100, 100))
        painter.setFont(QFont("SF Pro Display", 12, QFont.Weight.Bold))
        
        for i, day in enumerate(weekdays):
            x = i * cell_width
            painter.drawText(QRect(int(x), 0, int(cell_width), header_height), 
                           Qt.AlignmentFlag.AlignCenter, day)
        
        # 计算月份第一天是星期几
        first_day_of_week = self.current_month.dayOfWeek() - 1
        
        # 计算月份天数
        days_in_month = self.current_month.daysInMonth()
        
        # 绘制日期格子
        today = QDate.currentDate()
        
        for day in range(1, days_in_month + 1):
            # 计算位置
            pos = first_day_of_week + day - 1
            row = pos // 7
            col = pos % 7
            
            x = col * cell_width
            y = header_height + row * cell_height
            
            current_date = QDate(self.current_month.year(), self.current_month.month(), day)
            date_obj = date(self.current_month.year(), self.current_month.month(), day)
            
            # 存储单元格位置
            self.cell_rects[current_date] = QRect(int(x), int(y), int(cell_width), int(cell_height))
            
            # 绘制选中日期的高亮效果 - 只显示单个选中日期
            if current_date == self.selected_date:
                # 使用浅蓝色背景
                painter.fillRect(x, y, cell_width, cell_height, QColor(0, 122, 255, 20))
                # 加深边框
                painter.setPen(QPen(QColor(0, 122, 255), 2))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(x, y, cell_width, cell_height)
            
            # 绘制普通边框
            painter.setPen(QPen(QColor(230, 230, 230), 1))
            painter.drawRect(x, y, cell_width, cell_height)
            
            # 绘制日期数字
            # 只有当前月份的今天才显示蓝色圆圈
            if current_date == today and current_date.month() == self.current_month.month() and current_date.year() == self.current_month.year():
                # 今天的日期用蓝色圆圈标记
                painter.setBrush(QColor(0, 122, 255))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawEllipse(x + 5, y + 5, 25, 25)
                painter.setPen(Qt.GlobalColor.white)
            else:
                painter.setPen(QColor(50, 50, 50))
            
            painter.setFont(QFont("SF Pro Display", 14, QFont.Weight.Bold))
            painter.drawText(x + 5, y + 5, 25, 25, Qt.AlignmentFlag.AlignCenter, str(day))
            
            # 绘制日程预览
            if date_obj in self.month_schedules:
                schedules = self.month_schedules[date_obj]
                self.draw_day_schedules(painter, x, y + 35, cell_width, cell_height - 40, schedules)
    
    def draw_day_schedules(self, painter: QPainter, x: float, y: float, width: float, height: float, schedules: List[Schedule]):
        """绘制单个日期的日程预览"""
        max_visible = 3  # 最多显示3个日程
        item_height = 20
        padding = 2
        
        visible_count = min(len(schedules), max_visible)
        
        for i in range(visible_count):
            schedule = schedules[i]
            item_y = y + i * (item_height + padding)
            
            # 如果是最后一个且还有更多
            if i == max_visible - 1 and len(schedules) > max_visible:
                # 显示 +n 更多
                painter.setPen(QColor(150, 150, 150))
                painter.setFont(QFont("SF Pro Display", 10))
                more_text = f"+{len(schedules) - max_visible} 更多"
                painter.drawText(x + 5, item_y, width - 10, item_height, 
                               Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, more_text)
            else:
                # 绘制日程条
                rect = QRect(int(x + 5), int(item_y), int(width - 10), item_height)
                
                # 根据状态选择颜色
                if schedule.is_in_progress(datetime.now()):
                    color = QColor(0, 122, 255)
                elif schedule.has_ended(datetime.now()):
                    color = QColor(200, 200, 200)
                else:
                    color = QColor(52, 199, 89)
                
                # 绘制彩色条
                painter.fillRect(rect.x(), rect.y(), 3, rect.height(), color)
                
                # 绘制标题
                painter.setPen(QColor(50, 50, 50))
                painter.setFont(QFont("SF Pro Display", 10))
                text_rect = QRect(rect.x() + 5, rect.y(), rect.width() - 5, rect.height())
                
                # 截断过长的标题
                metrics = QFontMetrics(painter.font())
                title = metrics.elidedText(schedule.title, Qt.TextElideMode.ElideRight, text_rect.width())
                painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, title)
                
                # 存储日程位置
                self.schedule_rects[schedule.id] = rect
    
    def mousePressEvent(self, event):
        """处理鼠标点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            # 检查是否点击了日程
            for schedule_id, rect in self.schedule_rects.items():
                if rect.contains(event.pos()):
                    self.schedule_clicked.emit(schedule_id)
                    return
            
            # 检查是否点击了日期
            for date, rect in self.cell_rects.items():
                if rect.contains(event.pos()):
                    self.selected_date = date
                    self.date_clicked.emit(date)
                    self.update()
                    return