#!/usr/bin/env python
"""
现代化日历功能演示

展示具有苹果设计风格的日、周、月三种视图的日历界面。

使用方法：
    ./venv/bin/python demo_modern_calendar.py
"""

import sys
import signal
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from baal.scheduler.manager import ScheduleManager
from baal.desktop_pet.ui.calendar_dialog_modern import ModernCalendarDialog


class ModernCalendarDemo(QMainWindow):
    """现代化日历演示主窗口"""
    
    def __init__(self):
        super().__init__()
        self.schedule_manager = ScheduleManager()
        self.init_ui()
        self.load_sample_data()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle("Baal 现代化日历演示")
        self.resize(500, 400)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        # 中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 布局
        layout = QVBoxLayout(central_widget)
        layout.setSpacing(20)
        
        # 标题
        title = QLabel("📅 现代化日程管理")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: 700;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display";
                color: #1c1c1e;
                padding: 30px;
            }
        """)
        layout.addWidget(title)
        
        # 特性描述
        features = QLabel(
            "✨ 苹果设计风格界面\n"
            "📆 支持日、周、月三种视图\n"
            "⏰ 日视图：24小时时间线\n"
            "📊 周视图：7天并排时间线\n"
            "🗓 月视图：传统日历+日程预览"
        )
        features.setAlignment(Qt.AlignmentFlag.AlignCenter)
        features.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text";
                color: #3a3a3c;
                line-height: 1.5;
                padding: 10px;
            }
        """)
        layout.addWidget(features)
        
        layout.addStretch()
        
        # 打开日历按钮
        open_btn = QPushButton("打开现代化日历")
        open_btn.setStyleSheet("""
            QPushButton {
                font-size: 18px;
                font-weight: 600;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display";
                padding: 16px 32px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #007AFF, stop:1 #0051D5);
                color: white;
                border: none;
                border-radius: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0051D5, stop:1 #004494);
            }
            QPushButton:pressed {
                background: #004494;
            }
        """)
        open_btn.clicked.connect(self.open_calendar)
        layout.addWidget(open_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # 加载数据按钮
        load_btn = QPushButton("生成测试数据")
        load_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                font-weight: 500;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text";
                padding: 10px 20px;
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #34C759, stop:1 #30A14E);
                color: white;
                border: none;
                border-radius: 8px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #30A14E, stop:1 #2A8F43);
            }
        """)
        load_btn.clicked.connect(self.generate_more_data)
        layout.addWidget(load_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        
        layout.addStretch()
        
        # 状态标签
        self.status_label = QLabel("已加载示例日程")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text";
                color: #8e8e93;
                padding: 20px;
            }
        """)
        layout.addWidget(self.status_label)
    
    def load_sample_data(self):
        """加载示例数据"""
        now = datetime.now()
        
        # 今天的详细日程
        schedules_today = [
            (9, 0, 30, "晨会", "团队日常站会"),
            (10, 0, 120, "产品设计评审", "Q4产品路线图讨论"),
            (12, 30, 60, "午餐会议", "与投资人共进午餐"),
            (14, 0, 45, "代码评审", "评审新功能PR"),
            (15, 0, 60, "客户演示", "向客户展示新版本"),
            (16, 30, 30, "1对1会议", "与团队成员沟通"),
            (17, 30, 90, "技术分享会", "微服务架构最佳实践"),
        ]
        
        for hour, minute, duration, title, details in schedules_today:
            start_time = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if start_time > now:  # 只添加未来的日程
                self.schedule_manager.add(
                    title=title,
                    details=details,
                    start_time=start_time,
                    duration_minutes=duration
                )
        
        # 明天的日程
        tomorrow = now + timedelta(days=1)
        schedules_tomorrow = [
            (9, 30, 60, "部门会议", "月度总结"),
            (11, 0, 90, "培训课程", "React Hooks深入"),
            (14, 30, 120, "项目启动会", "新项目kick-off"),
            (17, 0, 60, "团队建设", "团队破冰活动"),
        ]
        
        for hour, minute, duration, title, details in schedules_tomorrow:
            start_time = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            self.schedule_manager.add(
                title=title,
                details=details,
                start_time=start_time,
                duration_minutes=duration
            )
        
        # 本周其他日程
        for i in range(2, 7):
            date = now + timedelta(days=i)
            
            # 每天添加2-3个日程
            if i % 2 == 0:
                meeting_time = date.replace(hour=10, minute=0, second=0, microsecond=0)
                self.schedule_manager.add(
                    title=f"项目同步会 Day{i}",
                    details="项目进度同步",
                    start_time=meeting_time,
                    duration_minutes=60
                )
            
            review_time = date.replace(hour=15, minute=0, second=0, microsecond=0)
            self.schedule_manager.add(
                title=f"设计评审 #{i}",
                details="UI/UX设计方案评审",
                start_time=review_time,
                duration_minutes=45
            )
        
        # 添加几个全天事件
        holiday = now + timedelta(days=14)
        holiday = holiday.replace(hour=0, minute=0, second=0, microsecond=0)
        self.schedule_manager.add(
            title="公司年会",
            details="年度庆典活动",
            start_time=holiday,
            duration_minutes=1440
        )
        
        deadline = now + timedelta(days=21)
        deadline = deadline.replace(hour=0, minute=0, second=0, microsecond=0)
        self.schedule_manager.add(
            title="项目交付截止日",
            details="第二阶段交付",
            start_time=deadline,
            duration_minutes=1440
        )
        
        count = len(self.schedule_manager.schedules)
        self.status_label.setText(f"已加载 {count} 个日程")
        print(f"✅ 已加载 {count} 个示例日程")
    
    def generate_more_data(self):
        """生成更多测试数据"""
        now = datetime.now()
        count_before = len(self.schedule_manager.schedules)
        
        # 生成未来30天的随机日程
        import random
        
        meeting_types = [
            ("技术讨论", "技术方案探讨", 60),
            ("产品规划", "产品路线图规划", 90),
            ("用户访谈", "收集用户反馈", 45),
            ("数据分析", "数据报告分享", 60),
            ("架构评审", "系统架构设计评审", 120),
            ("安全审计", "代码安全审查", 90),
            ("性能优化", "性能瓶颈分析", 75),
            ("市场分析", "竞品分析报告", 60),
        ]
        
        for day_offset in range(1, 31):
            date = now + timedelta(days=day_offset)
            
            # 每天随机添加1-4个日程
            num_events = random.randint(1, 4)
            
            for _ in range(num_events):
                # 随机选择会议类型
                title, details, duration = random.choice(meeting_types)
                
                # 随机时间（9:00 - 18:00）
                hour = random.randint(9, 17)
                minute = random.choice([0, 30])
                
                start_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
                # 避免时间冲突（简单检查）
                conflict = False
                for schedule in self.schedule_manager.schedules.values():
                    if schedule.start_time.date() == start_time.date():
                        if abs((schedule.start_time - start_time).total_seconds()) < 3600:
                            conflict = True
                            break
                
                if not conflict:
                    self.schedule_manager.add(
                        title=f"{title} #{day_offset}",
                        details=details,
                        start_time=start_time,
                        duration_minutes=duration
                    )
        
        count_after = len(self.schedule_manager.schedules)
        added = count_after - count_before
        
        self.status_label.setText(f"新增 {added} 个日程，总计 {count_after} 个")
        print(f"✅ 新增 {added} 个日程，当前总计 {count_after} 个")
    
    def open_calendar(self):
        """打开现代化日历"""
        dialog = ModernCalendarDialog(self.schedule_manager, self)
        
        # 连接信号
        dialog.schedule_changed.connect(self.on_schedule_changed)
        
        # 显示对话框
        dialog.show()
    
    def on_schedule_changed(self):
        """处理日程变化"""
        count = len(self.schedule_manager.schedules)
        self.status_label.setText(f"日程已更新，当前共 {count} 个日程")


def main():
    """主函数"""
    # 创建应用
    app = QApplication(sys.argv)
    
    # 设置应用字体
    app.setFont(QFont("-apple-system, BlinkMacSystemFont, 'SF Pro Display'"))
    
    # 设置 Ctrl+C 退出
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    
    # 创建并显示主窗口
    demo = ModernCalendarDemo()
    demo.show()
    
    print("=" * 60)
    print("🎨 现代化日历功能演示")
    print("=" * 60)
    print("📱 特性：")
    print("  • 苹果设计风格，圆角和渐变效果")
    print("  • 三种视图自由切换：")
    print("    - 日视图：24小时垂直时间线")
    print("    - 周视图：7天并排时间网格")
    print("    - 月视图：传统日历+日程预览")
    print("  • 流畅的视觉过渡动画")
    print("  • 智能日程显示（最多3个+更多）")
    print("=" * 60)
    print("💡 使用提示：")
    print("  1. 点击顶部按钮切换日/周/月视图")
    print("  2. 使用 ◀ ▶ 导航不同时间段")
    print("  3. 点击'今天'快速返回当前日期")
    print("  4. 点击日程可以编辑详情")
    print("  5. 点击'+ 添加'创建新日程")
    print("=" * 60)
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()