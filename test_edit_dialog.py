#!/usr/bin/env python
"""
测试日程编辑对话框

使用方法：
    ./venv/bin/python test_edit_dialog.py
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QDate
from baal.scheduler.manager import ScheduleManager
from baal.desktop_pet.ui.schedule_edit_dialog import ModernScheduleEditDialog


def main():
    app = QApplication(sys.argv)
    
    # 创建日程管理器
    schedule_manager = ScheduleManager()
    
    # 创建并显示编辑对话框
    dialog = ModernScheduleEditDialog(
        schedule_manager,
        default_date=QDate.currentDate()
    )
    
    dialog.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()