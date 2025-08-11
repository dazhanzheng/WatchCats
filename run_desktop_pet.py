#!/usr/bin/env python
"""
Baal 桌宠启动脚本

使用方法：
    python run_desktop_pet.py
    
或者:
    python -m baal.desktop_pet
"""

import os
import sys
import ssl
import warnings
import time

# 处理 SSL 错误
try:
    # 忽略 SSL 相关警告
    warnings.filterwarnings('ignore', category=DeprecationWarning)
    warnings.filterwarnings('ignore', message='urllib3 v2 only supports OpenSSL')
    warnings.filterwarnings('ignore', message='NotOpenSSLWarning')
    
    # 设置环境变量
    os.environ['PYTHONWARNINGS'] = 'ignore:Unverified HTTPS request'
    
    # 创建未验证的 SSL 上下文（仅在开发环境使用）
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    pass

# 初始化日志系统
try:
    from baal.desktop_pet.core.logger_config import init_logging, get_logger
    init_logging(console_level='INFO')
    logger = get_logger('run_desktop_pet')
    logger.info("Starting Baal Desktop Pet application")
except Exception as e:
    print(f"Warning: Could not initialize logging system: {e}")
    logger = None

# 导入主程序
try:
    from baal.desktop_pet import main
    if logger:
        logger.info("Successfully imported main module")
except ImportError as e:
    error_msg = f"Failed to import main module: {e}"
    print(error_msg)
    if logger:
        logger.error(error_msg)
    sys.exit(1)

if __name__ == "__main__":
    startup_time = time.time()
    print("Baal Desktop Pet v1.0 - Starting...")
    
    if logger:
        logger.info("=" * 50)
        logger.info("Baal Desktop Pet v1.0 - Application Starting")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Script path: {__file__}")
        logger.info("=" * 50)
    
    try:
        main()
    except KeyboardInterrupt:
        if logger:
            logger.info("Application interrupted by user (Ctrl+C)")
        print("\nApplication interrupted by user")
        sys.exit(0)
    except Exception as e:
        error_msg = f"Fatal error during startup: {e}"
        print(error_msg)
        if logger:
            logger.critical(error_msg, exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if logger:
            elapsed = time.time() - startup_time
            logger.info(f"Application session ended after {elapsed:.2f} seconds") 