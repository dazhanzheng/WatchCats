#!/usr/bin/env python
"""
测试日历界面功能

使用方法：
    ./venv/bin/python test_calendar.py
"""

import sys
from datetime import datetime, timedelta
from PyQt6.QtWidgets import QApplication
from baal.scheduler.manager import ScheduleManager
from baal.desktop_pet.ui.calendar_dialog import CalendarDialog


def main():
    """测试主函数"""
    app = QApplication(sys.argv)
    
    # 创建日程管理器
    schedule_manager = ScheduleManager()
    
    # 添加一些测试日程
    print("添加测试日程...")
    
    # 今天的日程
    today = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    schedule_manager.add(
        title="团队会议",
        details="讨论项目进度和下周计划",
        start_time=today,
        duration_minutes=60
    )
    
    schedule_manager.add(
        title="午餐约会",
        details="和客户共进午餐",
        start_time=today.replace(hour=12, minute=30),
        duration_minutes=90
    )
    
    schedule_manager.add(
        title="代码评审",
        details="评审新功能的代码实现",
        start_time=today.replace(hour=15, minute=0),
        duration_minutes=45
    )
    
    # 明天的日程
    tomorrow = today + timedelta(days=1)
    schedule_manager.add(
        title="晨会",
        details="每日站立会议",
        start_time=tomorrow.replace(hour=9, minute=30),
        duration_minutes=15
    )
    
    schedule_manager.add(
        title="产品演示",
        details="向管理层展示新功能",
        start_time=tomorrow.replace(hour=14, minute=0),
        duration_minutes=120
    )
    
    # 全天事件
    schedule_manager.add(
        title="项目截止日",
        details="第一阶段项目交付",
        start_time=tomorrow.replace(hour=0, minute=0),
        duration_minutes=1440  # 24小时
    )
    
    # 下周的日程
    next_week = today + timedelta(days=7)
    schedule_manager.add(
        title="季度总结会议",
        details="Q4季度业绩回顾",
        start_time=next_week.replace(hour=10, minute=0),
        duration_minutes=180
    )
    
    # 创建并显示日历对话框
    print("打开日历界面...")
    dialog = CalendarDialog(schedule_manager)
    
    # 连接信号（测试用）
    def on_schedule_changed():
        print("日程已更新!")
    
    dialog.schedule_changed.connect(on_schedule_changed)
    
    # 显示对话框
    dialog.show()
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main()