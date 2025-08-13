#!/usr/bin/env python3
"""
测试开发者模式功能
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from baal.desktop_pet.ui.pet_window import PetWindow
from baal.desktop_pet.ui.developer_console import DeveloperConsole

def test_developer_console():
    """测试开发者控制台"""
    print("=== 测试开发者控制台 ===")
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建桌宠窗口
    pet = PetWindow()
    pet.show()
    
    # 延迟显示开发者控制台
    def show_console():
        print("显示开发者控制台...")
        pet._show_developer_console()
        
        # 生成一些测试日志
        logger = logging.getLogger('test')
        logger.debug("这是一条DEBUG日志")
        logger.info("这是一条INFO日志")
        logger.warning("这是一条WARNING日志")
        logger.error("这是一条ERROR日志")
        
        # 生成监督模式日志
        supervision_logger = logging.getLogger('supervision')
        supervision_logger.info("监督模式已启动")
        supervision_logger.debug("检查用户活动...")
        supervision_logger.warning("用户偏离目标！")
        
        # 生成性能日志
        perf_logger = logging.getLogger('performance')
        perf_logger.info("Response time: 125ms")
        perf_logger.debug("Memory usage: 45MB")
        
        print("测试日志已生成")
    
    # 1秒后显示控制台
    QTimer.singleShot(1000, show_console)
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    test_developer_console()