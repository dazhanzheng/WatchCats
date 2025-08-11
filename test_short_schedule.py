#!/usr/bin/env python3
"""测试短时间日程的显示"""

import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PyQt6.QtCore import Qt

# 导入日程管理器和对话框
from baal.scheduler.manager import ScheduleManager
from baal.desktop_pet.ui.calendar_dialog_modern import ModernCalendarDialog

def create_test_schedules(manager: ScheduleManager):
    """创建测试日程，包括10分钟的短日程"""
    now = datetime.now()
    
    # 清除现有日程
    for schedule_id in list(manager.schedules.keys()):
        manager.delete(schedule_id)
    
    # 创建10分钟的日程
    manager.add(
        title="10分钟会议",
        details="这是一个10分钟的短会议",
        start_time=now.replace(hour=10, minute=0, second=0, microsecond=0),
        duration_minutes=10
    )
    
    # 创建30分钟的日程
    manager.add(
        title="30分钟讨论",
        details="这是一个30分钟的讨论",
        start_time=now.replace(hour=11, minute=0, second=0, microsecond=0),
        duration_minutes=30
    )
    
    # 创建1小时的日程
    manager.add(
        title="1小时培训",
        details="这是一个1小时的培训",
        start_time=now.replace(hour=14, minute=0, second=0, microsecond=0),
        duration_minutes=60
    )
    
    # 创建2小时的日程
    manager.add(
        title="2小时项目会议",
        details="这是一个2小时的项目会议",
        start_time=now.replace(hour=15, minute=30, second=0, microsecond=0),
        duration_minutes=120
    )
    
    print(f"创建了 {len(manager.schedules)} 个测试日程")
    for schedule in manager.schedules.values():
        print(f"  - {schedule.title}: {schedule.start_time.strftime('%H:%M')} ({schedule.duration_minutes}分钟)")

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.schedule_manager = ScheduleManager()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("测试短时间日程显示")
        self.setGeometry(100, 100, 400, 300)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # 信息标签
        info_label = QLabel("点击按钮创建测试日程并打开日历查看")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)
        
        # 创建测试数据按钮
        create_btn = QPushButton("创建测试日程（包括10分钟日程）")
        create_btn.clicked.connect(self.create_test_data)
        layout.addWidget(create_btn)
        
        # 打开日历按钮
        calendar_btn = QPushButton("打开日历查看")
        calendar_btn.clicked.connect(self.open_calendar)
        layout.addWidget(calendar_btn)
        
        # 结果标签
        self.result_label = QLabel("")
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setWordWrap(True)
        layout.addWidget(self.result_label)
        
    def create_test_data(self):
        create_test_schedules(self.schedule_manager)
        self.result_label.setText("已创建测试日程，包括10分钟的短日程。\n请打开日历查看是否能在日视图、周视图和月视图中看到。")
        
    def open_calendar(self):
        dialog = ModernCalendarDialog(self.schedule_manager, self)
        dialog.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())