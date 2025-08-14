#!/usr/bin/env python
"""
Debug version of Baal 桌宠启动脚本
捕获所有错误并保存到文件
"""

import os
import sys
import ssl
import warnings
import time
import traceback
from datetime import datetime

# 创建错误日志文件
error_log_file = f"baal_crash_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

def log_error(message):
    """写入错误到文件和控制台"""
    with open(error_log_file, 'a', encoding='utf-8') as f:
        f.write(f"{message}\n")
    print(message)

log_error("=" * 60)
log_error(f"Baal Desktop Pet Debug Log - {datetime.now()}")
log_error("=" * 60)
log_error(f"Python version: {sys.version}")
log_error(f"Platform: {sys.platform}")
log_error(f"Working directory: {os.getcwd()}")
log_error(f"Executable: {sys.executable}")

# 处理 SSL 错误
try:
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')
    warnings.filterwarnings('ignore', message='NotOpenSSLWarning')
    os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'
    ssl._create_default_https_context = ssl._create_unverified_context
    log_error("SSL context configured")
except Exception as e:
    log_error(f"SSL configuration warning: {e}")

# 测试 PyQt6 导入
log_error("\nTesting PyQt6 import...")
try:
    from PyQt6 import QtCore, QtGui, QtWidgets
    log_error(f"✓ PyQt6 imported successfully")
    log_error(f"  Qt version: {QtCore.QT_VERSION_STR}")
    log_error(f"  PyQt version: {QtCore.PYQT_VERSION_STR}")
    
    # 测试创建 QApplication
    from PyQt6.QtWidgets import QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
        log_error("✓ QApplication created successfully")
    else:
        log_error("✓ QApplication already exists")
        
except Exception as e:
    log_error(f"✗ PyQt6 error: {e}")
    log_error(traceback.format_exc())
    log_error("\nPyQt6 is required but failed to initialize. Exiting...")
    input("Press Enter to exit...")
    sys.exit(1)

# 初始化日志系统
log_error("\nInitializing logging system...")
try:
    from baal.desktop_pet.core.logger_config import init_logging, get_logger
    init_logging(console_level='DEBUG')  # 使用 DEBUG 级别
    logger = get_logger('run_desktop_pet_debug')
    logger.info("Logging system initialized")
    log_error("✓ Logging system initialized")
except Exception as e:
    log_error(f"✗ Logging initialization failed: {e}")
    log_error(traceback.format_exc())
    logger = None

# 导入主程序
log_error("\nImporting main module...")
try:
    from baal.desktop_pet import main
    log_error("✓ Main module imported successfully")
    if logger:
        logger.info("Successfully imported main module")
except ImportError as e:
    log_error(f"✗ Failed to import main module: {e}")
    log_error(traceback.format_exc())
    log_error("\nModule import failed. Check if all dependencies are installed.")
    input("Press Enter to exit...")
    sys.exit(1)

if __name__ == "__main__":
    startup_time = time.time()
    log_error("\n" + "=" * 60)
    log_error("Starting application...")
    log_error("=" * 60)
    
    # 检查单实例
    log_error("\nChecking single instance...")
    try:
        from baal.desktop_pet.core.single_instance import check_single_instance
        instance_lock = check_single_instance("BaalPetAssistant")
        
        if instance_lock is None:
            log_error("✗ Another instance is already running")
            if logger:
                logger.info("Another instance is already running, exiting.")
            input("Press Enter to exit...")
            sys.exit(0)
        else:
            log_error("✓ Single instance check passed")
    except Exception as e:
        log_error(f"✗ Single instance check failed: {e}")
        log_error(traceback.format_exc())
        instance_lock = None
    
    # 运行主程序
    log_error("\nStarting main application...")
    try:
        main()
    except KeyboardInterrupt:
        log_error("\nApplication interrupted by user (Ctrl+C)")
        if logger:
            logger.info("Application interrupted by user (Ctrl+C)")
    except Exception as e:
        log_error(f"\n✗ FATAL ERROR: {e}")
        log_error(f"Error type: {type(e).__name__}")
        log_error("\nFull traceback:")
        log_error(traceback.format_exc())
        
        if logger:
            logger.critical(f"Fatal error: {e}", exc_info=True)
        
        log_error(f"\nError log saved to: {error_log_file}")
        input("\nPress Enter to exit...")
        sys.exit(1)
    finally:
        # 释放单实例锁
        if instance_lock:
            try:
                instance_lock.release()
                log_error("Single instance lock released")
            except:
                pass
        
        elapsed = time.time() - startup_time
        log_error(f"\nApplication session ended after {elapsed:.2f} seconds")
        log_error(f"Log saved to: {error_log_file}")
        
        if logger:
            logger.info(f"Application session ended after {elapsed:.2f} seconds")