"""
现代化日程编辑对话框

采用苹果设计风格的日程编辑界面
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QTextEdit,
    QDateTimeEdit, QSpinBox, QCheckBox, QPushButton, QLabel,
    QWidget, QFrame, QSlider, QButtonGroup, QRadioButton
)
from PyQt6.QtCore import Qt, QDate, QDateTime, QTime, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QPalette, QColor, QFont, QFontMetrics
from datetime import datetime, timedelta
from typing import Optional

from ...scheduler.models import Schedule
from ...scheduler.manager import ScheduleManager


class ModernScheduleEditDialog(QDialog):
    """现代化日程编辑对话框"""
    
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
        """初始化UI - 苹果设计风格"""
        self.setWindowTitle("编辑日程" if self.schedule else "新建日程")
        self.setFixedSize(580, 720)  # 增加高度到720
        self.setModal(True)
        
        # 设置对话框样式
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
        
        # 标题栏
        title_bar = self.create_title_bar()
        layout.addWidget(title_bar)
        
        # 内容区域
        content = self.create_content()
        layout.addWidget(content)
        
        # 底部按钮栏
        button_bar = self.create_button_bar()
        layout.addWidget(button_bar)
    
    def create_title_bar(self) -> QWidget:
        """创建标题栏"""
        widget = QWidget()
        widget.setFixedHeight(60)
        widget.setStyleSheet("""
            QWidget {
                background: white;
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
                border-bottom: 1px solid #e0e0e0;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 0, 20, 0)
        
        title = QLabel("编辑日程" if self.schedule else "新建日程")
        title.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: 600;
                color: #1c1c1e;
            }
        """)
        layout.addWidget(title)
        
        layout.addStretch()
        
        return widget
    
    def create_content(self) -> QWidget:
        """创建内容区域"""
        widget = QWidget()
        widget.setStyleSheet("""
            QWidget {
                background: white;
            }
        """)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # 标题输入
        title_section = self.create_section("标题")
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("输入日程标题...")
        self.title_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 16px;
                font-size: 16px;
                border: 2px solid #e5e5e7;
                border-radius: 10px;
                background: #f2f2f7;
                color: #1c1c1e;
            }
            QLineEdit:focus {
                border-color: #007AFF;
                background: white;
                color: #1c1c1e;
                outline: none;
            }
        """)
        title_section.layout().addWidget(self.title_edit)
        layout.addWidget(title_section)
        
        # 详情输入
        details_section = self.create_section("详情")
        self.details_edit = QTextEdit()
        self.details_edit.setPlaceholderText("添加日程详情...")
        self.details_edit.setMaximumHeight(120)
        self.details_edit.setStyleSheet("""
            QTextEdit {
                padding: 12px 16px;
                font-size: 14px;
                border: 2px solid #e5e5e7;
                border-radius: 10px;
                background: #f2f2f7;
                color: #1c1c1e;
            }
            QTextEdit:focus {
                border-color: #007AFF;
                background: white;
                color: #1c1c1e;
                outline: none;
            }
        """)
        details_section.layout().addWidget(self.details_edit)
        layout.addWidget(details_section)
        
        # 全天事件开关
        all_day_widget = QWidget()
        all_day_layout = QHBoxLayout(all_day_widget)
        all_day_layout.setContentsMargins(0, 0, 0, 0)
        
        all_day_label = QLabel("全天事件")
        all_day_label.setStyleSheet("font-size: 15px; color: #1c1c1e;")
        all_day_layout.addWidget(all_day_label)
        
        all_day_layout.addStretch()
        
        self.all_day_switch = ModernSwitch()
        self.all_day_switch.toggled.connect(self.on_all_day_toggled)
        all_day_layout.addWidget(self.all_day_switch)
        
        layout.addWidget(all_day_widget)
        
        # 分隔线
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background: #e5e5e7; max-height: 1px;")
        layout.addWidget(separator)
        
        # 时间选择
        time_section = self.create_section("时间")
        
        # 开始时间
        start_widget = QWidget()
        start_layout = QHBoxLayout(start_widget)
        start_layout.setContentsMargins(0, 0, 0, 0)
        
        start_label = QLabel("开始")
        start_label.setFixedWidth(60)
        start_label.setStyleSheet("font-size: 14px; color: #3c3c43;")
        start_layout.addWidget(start_label)
        
        self.start_datetime = QDateTimeEdit()
        self.start_datetime.setCalendarPopup(True)
        self.start_datetime.setDateTime(
            QDateTime(self.default_date, QTime.currentTime())
        )
        self.start_datetime.setDisplayFormat("yyyy-MM-dd HH:mm")
        self.start_datetime.setStyleSheet("""
            QDateTimeEdit {
                padding: 10px 14px;
                font-size: 15px;
                min-height: 20px;
                border: 2px solid #e5e5e7;
                border-radius: 8px;
                background: #f2f2f7;
                color: #1c1c1e;
            }
            QDateTimeEdit:focus {
                border-color: #007AFF;
                background: white;
                color: #1c1c1e;
            }
            QDateTimeEdit::drop-down {
                border: none;
                width: 20px;
            }
            QDateTimeEdit::down-arrow {
                image: none;
                border-left: 5px solid transparent;
                border-right: 5px solid transparent;
                border-top: 5px solid #007AFF;
                margin-right: 5px;
            }
        """)
        start_layout.addWidget(self.start_datetime)
        
        time_section.layout().addWidget(start_widget)
        
        # 持续时间
        duration_widget = QWidget()
        duration_layout = QHBoxLayout(duration_widget)
        duration_layout.setContentsMargins(0, 0, 0, 0)
        
        duration_label = QLabel("持续")
        duration_label.setFixedWidth(60)
        duration_label.setStyleSheet("font-size: 14px; color: #3c3c43;")
        duration_layout.addWidget(duration_label)
        
        self.duration_spin = QSpinBox()
        self.duration_spin.setRange(5, 1440 * 7)
        self.duration_spin.setValue(60)
        self.duration_spin.setSuffix(" 分钟")
        self.duration_spin.setStyleSheet("""
            QSpinBox {
                padding: 10px 14px;
                font-size: 15px;
                min-height: 20px;
                min-width: 120px;
                border: 2px solid #e5e5e7;
                border-radius: 8px;
                background: #f2f2f7;
                color: #1c1c1e;
            }
            QSpinBox:focus {
                border-color: #007AFF;
                background: white;
                color: #1c1c1e;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
                background: transparent;
            }
            QSpinBox::up-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 4px solid #007AFF;
            }
            QSpinBox::down-arrow {
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 4px solid #007AFF;
            }
        """)
        duration_layout.addWidget(self.duration_spin)
        
        time_section.layout().addWidget(duration_widget)
        
        # 快捷时长按钮
        quick_duration = QWidget()
        quick_layout = QHBoxLayout(quick_duration)
        quick_layout.setContentsMargins(0, 8, 0, 0)
        quick_layout.setSpacing(8)  # 设置按钮之间的间距
        
        for text, minutes in [("30分钟", 30), ("1小时", 60), ("2小时", 120), ("半天", 720)]:
            btn = QPushButton(text)
            btn.setFixedHeight(36)  # 固定高度
            btn.setStyleSheet("""
                QPushButton {
                    padding: 0px 20px;
                    font-size: 14px;
                    min-width: 80px;
                    border: 1px solid #007AFF;
                    border-radius: 8px;
                    color: #007AFF;
                    background: white;
                }
                QPushButton:hover {
                    background: #007AFF;
                    color: white;
                }
                QPushButton:pressed {
                    background: #0051D5;
                }
            """)
            btn.clicked.connect(lambda checked, m=minutes: self.duration_spin.setValue(m))
            quick_layout.addWidget(btn)
        
        quick_layout.addStretch()
        time_section.layout().addWidget(quick_duration)
        
        layout.addWidget(time_section)
        
        layout.addStretch()
        
        return widget
    
    def create_section(self, title: str) -> QWidget:
        """创建一个区域"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        label = QLabel(title)
        label.setStyleSheet("""
            QLabel {
                font-size: 15px;
                font-weight: 500;
                color: #1c1c1e;
            }
        """)
        layout.addWidget(label)
        
        return widget
    
    def create_button_bar(self) -> QWidget:
        """创建底部按钮栏"""
        widget = QWidget()
        widget.setFixedHeight(70)
        widget.setStyleSheet("""
            QWidget {
                background: white;
                border-top: 1px solid #e0e0e0;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setFixedSize(100, 36)
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: 500;
                border: 1px solid #d1d1d6;
                border-radius: 8px;
                color: #007AFF;
                background: white;
            }
            QPushButton:hover {
                background: #f2f2f7;
            }
            QPushButton:pressed {
                background: #e5e5ea;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        layout.addWidget(cancel_btn)
        
        layout.addStretch()
        
        # 保存按钮
        save_btn = QPushButton("保存")
        save_btn.setFixedSize(100, 36)
        save_btn.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                font-weight: 500;
                border: none;
                border-radius: 8px;
                color: white;
                background: #007AFF;
            }
            QPushButton:hover {
                background: #0051D5;
            }
            QPushButton:pressed {
                background: #004494;
            }
        """)
        save_btn.clicked.connect(self.save_schedule)
        layout.addWidget(save_btn)
        
        return widget
    
    def on_all_day_toggled(self, checked: bool):
        """处理全天事件切换"""
        if checked:
            self.start_datetime.setDisplayFormat("yyyy-MM-dd")
            self.start_datetime.setTime(QTime(0, 0))
            self.duration_spin.setValue(1440)
            self.duration_spin.setEnabled(False)
        else:
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
            self.all_day_switch.setChecked(True)
    
    def save_schedule(self):
        """保存日程"""
        from PyQt6.QtWidgets import QMessageBox
        
        # 验证输入
        title = self.title_edit.text().strip()
        if not title:
            QMessageBox.warning(self, "提示", "请输入日程标题")
            self.title_edit.setFocus()
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
        
        try:
            if self.schedule:
                # 更新现有日程
                self.schedule_manager.update(
                    self.schedule.id,
                    title=title,
                    details=details,
                    start_time=start_time,
                    duration_minutes=duration_minutes,
                    is_active=True
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
            QMessageBox.critical(self, "错误", f"保存失败：{str(e)}")


class ModernSwitch(QWidget):
    """现代化开关控件"""
    
    toggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(51, 31)
        self._checked = False
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def paintEvent(self, event):
        """绘制开关"""
        from PyQt6.QtGui import QPainter, QBrush, QPen
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 背景
        if self._checked:
            painter.setBrush(QBrush(QColor(52, 199, 89)))
        else:
            painter.setBrush(QBrush(QColor(229, 229, 234)))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 15, 15)
        
        # 滑块
        painter.setBrush(QBrush(Qt.GlobalColor.white))
        if self._checked:
            painter.drawEllipse(self.width() - 28, 3, 25, 25)
        else:
            painter.drawEllipse(3, 3, 25, 25)
    
    def mousePressEvent(self, event):
        """处理点击"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._checked = not self._checked
            self.toggled.emit(self._checked)
            self.update()
    
    def isChecked(self) -> bool:
        return self._checked
    
    def setChecked(self, checked: bool):
        self._checked = checked
        self.update()