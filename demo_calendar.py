#!/usr/bin/env python
"""
日历功能演示

演示如何使用日历界面进行日程管理。

使用方法：
    ./venv/bin/python demo_calendar.py
"""

import sys
import signal
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from baal.scheduler.manager import ScheduleManager
from baal.desktop_pet.ui.calendar_dialog import CalendarDialog


class CalendarDemo(QMainWindow):
    """日历演示主窗口"""
    
    def __init__(self):
        super().__init__()
        self.schedule_manager = ScheduleManager()
        self.init_ui()
        self.load_sample_data()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Baal 日历功能演示")
        self.resize(400, 300)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 布局
        layout = QVBoxLayout(central_widget)
        
        # 标题
        title = QLabel("📅 日程管理系统")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                padding: 20px;
            }
        """)
        layout.addWidget(title)
        
        # 描述
        desc = QLabel("点击下方按钮打开日历界面\n可以查看、添加、编辑和删除日程")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("padding: 10px; color: #666;")
        layout.addWidget(desc)
        
        layout.addStretch()
        
        # 打开日历按钮
        open_btn = QPushButton("打开日历")
        open_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                padding: 15px 30px;
                background-color: #007AFF;
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #0051D5;
            }
        """)
        open_btn.clicked.connect(self.open_calendar)
        layout.addWidget(open_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 加载示例数据按钮
        load_btn = QPushButton("加载更多示例日程")
        load_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #34C759;
                color: white;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #30A14E;
            }
        """)
        load_btn.clicked.connect(self.load_more_sample_data)
        layout.addWidget(load_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("已加载基础示例日程")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("color: #999; padding: 10px;")
        layout.addWidget(self.status_label)
    
    def load_sample_data(self):
        """加载示例数据"""
        now = datetime.now()
        
        # 今天的日程
        today_10am = now.replace(hour=10, minute=0, second=0, microsecond=0)
        self.schedule_manager.add(
            title="早会",
            details="团队同步进度",
            start_time=today_10am,
            duration_minutes=30
        )
        
        today_2pm = now.replace(hour=14, minute=0, second=0, microsecond=0)
        self.schedule_manager.add(
            title="客户会议",
            details="讨论新需求",
            start_time=today_2pm,
            duration_minutes=60
        )
        
        # 明天的日程
        tomorrow = now + timedelta(days=1)
        tomorrow_9am = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        self.schedule_manager.add(
            title="项目评审",
            details="第一阶段成果展示",
            start_time=tomorrow_9am,
            duration_minutes=120
        )
        
        print(f"已加载 {len(self.schedule_manager.schedules)} 个示例日程")
    
    def load_more_sample_data(self):
        """加载更多示例数据"""
        now = datetime.now()
        count_before = len(self.schedule_manager.schedules)
        
        # 未来一周的日程
        for i in range(2, 8):
            date = now + timedelta(days=i)
            
            # 每天添加1-2个日程
            if i % 2 == 0:
                meeting_time = date.replace(hour=10, minute=30, second=0, microsecond=0)
                self.schedule_manager.add(
                    title=f"部门会议 {i}",
                    details=f"第{i}天的例行会议",
                    start_time=meeting_time,
                    duration_minutes=45
                )
            
            if i % 3 == 0:
                event_time = date.replace(hour=15, minute=0, second=0, microsecond=0)
                self.schedule_manager.add(
                    title=f"培训课程 {i//3}",
                    details=f"技术分享第{i//3}期",
                    start_time=event_time,
                    duration_minutes=90
                )
        
        # 添加一个全天事件
        special_day = now + timedelta(days=5)
        special_day = special_day.replace(hour=0, minute=0, second=0, microsecond=0)
        self.schedule_manager.add(
            title="团队建设日",
            details="全天团队活动",
            start_time=special_day,
            duration_minutes=1440  # 24小时
        )
        
        count_after = len(self.schedule_manager.schedules)
        added = count_after - count_before
        
        self.status_label.setText(f"已添加 {added} 个新日程，总计 {count_after} 个日程")
        print(f"新增 {added} 个日程，当前总计 {count_after} 个日程")
    
    def open_calendar(self):
        """打开日历对话框"""
        dialog = CalendarDialog(self.schedule_manager, self)
        
        # 连接信号
        dialog.schedule_changed.connect(self.on_schedule_changed)
        
        # 显示对话框（非模态）
        dialog.show()
    
    def on_schedule_changed(self):
        """处理日程变化"""
        count = len(self.schedule_manager.schedules)
        self.status_label.setText(f"日程已更新，当前共 {count} 个日程")
        print(f"日程已更新，当前共 {count} 个日程")


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置 Ctrl+C 退出
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 创建并显示主窗口
    demo = CalendarDemo()
    demo.show()
    
    print("=" * 50)
    print("日历功能演示已启动")
    print("=" * 50)
    print("功能说明：")
    print("1. 点击'打开日历'查看日历界面")
    print("2. 在日历上点击日期查看当天日程")
    print("3. 双击日程项可以编辑")
    print("4. 点击'添加日程'创建新日程")
    print("5. 支持全天事件和定时事件")
    print("=" * 50)
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()