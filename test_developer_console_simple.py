#!/usr/bin/env python3
"""
简单测试开发者控制台功能
"""

import sys
import logging
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from baal.desktop_pet.ui.developer_console import DeveloperConsole

def test_console_standalone():
    """独立测试开发者控制台"""
    print("=== 测试开发者控制台（独立模式）===")
    
    # 配置日志
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 创建应用
    app = QApplication(sys.argv)
    
    # 创建并显示控制台
    console = DeveloperConsole()
    console.show()
    
    # 生成测试日志
    def generate_logs():
        # 主日志
        logger = logging.getLogger('main')
        for i in range(5):
            logger.info(f"主日志消息 #{i+1}")
        
        # 监督模式日志
        supervision_logger = logging.getLogger('supervision')
        supervision_logger.info("监督模式已启动")
        supervision_logger.debug("检查间隔设置为 300 秒")
        supervision_logger.debug("执行首次检查...")
        supervision_logger.info("开始检查活动... (时间: 14:30:00)")
        supervision_logger.debug("用户活跃，获取活动统计...")
        supervision_logger.debug("统计数据获取成功: ['stats_5m', 'stats_2h', 'stats_today']")
        supervision_logger.info("评估结果: should_remind=True, deviation_level=高")
        supervision_logger.warning("需要提醒用户！")
        supervision_logger.debug("提醒内容: 检测到您偏离了设定的目标...")
        
        # 性能日志
        perf_logger = logging.getLogger('performance')
        perf_logger.info("Response time: 125ms")
        perf_logger.info("Memory usage: 45MB")
        perf_logger.debug("Cache hit rate: 89%")
        
        # UI日志
        ui_logger = logging.getLogger('ui')
        ui_logger.info("UI Event: chat_bubble_show")
        ui_logger.debug("Window position updated: (100, 200)")
        
        # 错误日志
        error_logger = logging.getLogger('error_test')
        error_logger.error("测试错误: 无法连接到服务器")
        error_logger.critical("严重错误: 内存不足")
        
        print("✅ 测试日志已生成")
        print("📊 检查控制台的以下功能：")
        print("  1. 主日志选项卡 - 应显示所有日志")
        print("  2. 监督模式选项卡 - 应只显示supervision模块的日志")
        print("  3. 性能监控选项卡 - 应显示性能相关日志")
        print("  4. 统计信息选项卡 - 应显示日志统计")
        print("  5. 日志级别过滤 - 选择不同级别应过滤日志")
        print("  6. 模块过滤 - 选择supervision应只显示监督模式日志")
        print("  7. 搜索功能 - 输入关键词应过滤相关日志")
        print("  8. 导出功能 - 应能导出日志到文件")
    
    # 延迟生成日志，让控制台有时间初始化
    QTimer.singleShot(500, generate_logs)
    
    # 定期生成新日志
    def generate_periodic_logs():
        import random
        loggers = ['supervision', 'performance', 'ui', 'core']
        levels = [logging.DEBUG, logging.INFO, logging.WARNING]
        
        logger_name = random.choice(loggers)
        level = random.choice(levels)
        logger = logging.getLogger(logger_name)
        
        messages = [
            "定期检查活动状态",
            "更新UI组件",
            "处理用户输入",
            "同步配置文件",
            "清理临时缓存"
        ]
        
        logger.log(level, f"[定期] {random.choice(messages)}")
    
    # 每2秒生成一条新日志
    timer = QTimer()
    timer.timeout.connect(generate_periodic_logs)
    timer.start(2000)
    
    # 运行应用
    sys.exit(app.exec())

if __name__ == "__main__":
    test_console_standalone()