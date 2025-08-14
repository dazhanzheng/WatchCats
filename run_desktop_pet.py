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
    
    # SSL 配置：仅在开发模式或显式设置时禁用验证
    # 生产环境应该使用正确的 SSL 证书
    if os.environ.get('BAAL_DEV_MODE', '').lower() == 'true' or \
       os.environ.get('DISABLE_SSL_VERIFY', '').lower() == 'true':
        print("Warning: SSL verification disabled (development mode)")
        ssl._create_default_https_context = ssl._create_unverified_context
    else:
        # 生产环境：使用默认的 SSL 验证
        pass
except:
    pass

# 修复：延迟初始化日志系统，避免在冻结环境中过早创建文件
logger = None
try:
    # 在冻结环境中确保临时目录存在
    if getattr(sys, 'frozen', False):
        import tempfile
        from pathlib import Path
        temp_dir = Path(tempfile.gettempdir())
        temp_dir.mkdir(exist_ok=True, parents=True)
        
        # 为日志创建一个专用目录
        log_dir = temp_dir / 'BaalPet'
        log_dir.mkdir(exist_ok=True, parents=True)
        os.environ['BAAL_LOG_DIR'] = str(log_dir)
    
    # 现在可以安全地初始化日志系统
    from baal.desktop_pet.core.logger_config import init_logging, get_logger
    init_logging(console_level='INFO')
    logger = get_logger('run_desktop_pet')
    logger.info("Starting Baal Desktop Pet application")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Frozen: {getattr(sys, 'frozen', False)}")
    if hasattr(sys, '_MEIPASS'):
        logger.info(f"Bundle path: {sys._MEIPASS}")
except Exception as e:
    # 不要让日志失败阻止程序启动
    print(f"Warning: Could not initialize logging system: {e}")
    print("Continuing without logging...")
    logger = None

# 运行预检查（仅在 Windows 打包环境或调试模式下）
if getattr(sys, 'frozen', False) or os.environ.get('BAAL_DEBUG', '').lower() == 'true':
    try:
        from baal.desktop_pet.core.preflight_check import run_preflight_check, get_diagnostic_info
        if not run_preflight_check():
            print("\n" + get_diagnostic_info())
            if sys.platform == 'win32' and getattr(sys, 'frozen', False):
                print("\nPress Enter to exit...")
                input()
                sys.exit(1)
    except Exception as e:
        print(f"Warning: Preflight check failed: {e}")

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
    
    # 检查单实例
    from baal.desktop_pet.core.single_instance import check_single_instance
    instance_lock = check_single_instance("BaalPetAssistant")
    
    if instance_lock is None:
        # 已有实例在运行，退出
        if logger:
            logger.info("Another instance is already running, exiting.")
        sys.exit(0)
    
    if logger:
        logger.info("=" * 50)
        logger.info("Baal Desktop Pet v1.0 - Application Starting")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Working directory: {os.getcwd()}")
        logger.info(f"Script path: {__file__}")
        logger.info("Single instance check: PASSED")
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
        # 释放单实例锁
        if instance_lock:
            instance_lock.release()
        
        if logger:
            elapsed = time.time() - startup_time
            logger.info(f"Application session ended after {elapsed:.2f} seconds") 