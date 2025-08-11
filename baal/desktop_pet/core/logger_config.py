"""
集中式日志配置模块

提供统一的日志配置和管理，支持：
- 文件和控制台输出
- 日志轮转
- 不同模块的独立日志级别
- 详细的格式化选项
- 性能监控日志
"""

import logging
import logging.handlers
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import json
import traceback
from functools import wraps
import time
import threading

# 默认日志目录
LOG_DIR = Path.home() / '.baal_pet' / 'logs'
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 日志文件路径
MAIN_LOG = LOG_DIR / f'baal_{datetime.now().strftime("%Y%m%d")}.log'
ERROR_LOG = LOG_DIR / 'errors.log'
PERFORMANCE_LOG = LOG_DIR / 'performance.log'
API_LOG = LOG_DIR / 'api_calls.log'
UI_LOG = LOG_DIR / 'ui_events.log'
SCHEDULE_LOG = LOG_DIR / 'schedule.log'
AW_LOG = LOG_DIR / 'activity_watch.log'

# 日志级别映射
LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}

# 模块特定的日志级别
MODULE_LOG_LEVELS = {
    'baal.desktop_pet.core': 'DEBUG',
    'baal.desktop_pet.ui': 'INFO',
    'baal.llm_assistant': 'DEBUG',
    'baal.scheduler': 'INFO',
    'baal.aw_stats': 'INFO',
    'performance': 'DEBUG',
    'api': 'DEBUG'
}


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器（仅用于控制台）"""
    
    COLORS = {
        'DEBUG': '\033[36m',     # 青色
        'INFO': '\033[32m',      # 绿色
        'WARNING': '\033[33m',   # 黄色
        'ERROR': '\033[31m',     # 红色
        'CRITICAL': '\033[35m',  # 紫色
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


class DetailedJSONFormatter(logging.Formatter):
    """JSON格式的详细日志格式化器"""
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'thread': record.thread,
            'thread_name': record.threadName,
            'process': record.process,
        }
        
        # 添加额外的上下文信息
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
            
        # 添加异常信息
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
            
        return json.dumps(log_data, ensure_ascii=False)


class LoggerConfig:
    """日志配置管理器"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self._loggers: Dict[str, logging.Logger] = {}
            self._handlers: Dict[str, logging.Handler] = {}
            self._setup_root_logger()
            self._setup_specialized_loggers()
    
    def _setup_root_logger(self):
        """设置根日志器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # 清除现有的处理器
        root_logger.handlers.clear()
        
        # 控制台处理器（带颜色）
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        self._handlers['console'] = console_handler
        
        # 主日志文件处理器（带轮转）
        file_handler = logging.handlers.RotatingFileHandler(
            MAIN_LOG,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - [%(levelname)s] - %(filename)s:%(lineno)d - %(funcName)s() - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)
        self._handlers['main_file'] = file_handler
        
        # 错误日志文件处理器
        error_handler = logging.handlers.RotatingFileHandler(
            ERROR_LOG,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(DetailedJSONFormatter())
        root_logger.addHandler(error_handler)
        self._handlers['error_file'] = error_handler
    
    def _setup_specialized_loggers(self):
        """设置专门的日志器"""
        
        # 性能日志器
        perf_logger = self.get_logger('performance')
        perf_handler = logging.handlers.RotatingFileHandler(
            PERFORMANCE_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        perf_handler.setFormatter(DetailedJSONFormatter())
        perf_logger.addHandler(perf_handler)
        perf_logger.setLevel(logging.DEBUG)
        perf_logger.propagate = False
        
        # API调用日志器
        api_logger = self.get_logger('api')
        api_handler = logging.handlers.RotatingFileHandler(
            API_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        api_handler.setFormatter(DetailedJSONFormatter())
        api_logger.addHandler(api_handler)
        api_logger.setLevel(logging.DEBUG)
        api_logger.propagate = False
        
        # UI事件日志器
        ui_logger = self.get_logger('ui')
        ui_handler = logging.handlers.RotatingFileHandler(
            UI_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        ui_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        ui_logger.addHandler(ui_handler)
        ui_logger.setLevel(logging.INFO)
        
        # 日程日志器
        schedule_logger = self.get_logger('schedule')
        schedule_handler = logging.handlers.RotatingFileHandler(
            SCHEDULE_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        schedule_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        ))
        schedule_logger.addHandler(schedule_handler)
        schedule_logger.setLevel(logging.INFO)
        
        # ActivityWatch日志器
        aw_logger = self.get_logger('activity_watch')
        aw_handler = logging.handlers.RotatingFileHandler(
            AW_LOG,
            maxBytes=5*1024*1024,
            backupCount=3,
            encoding='utf-8'
        )
        aw_handler.setFormatter(DetailedJSONFormatter())
        aw_logger.addHandler(aw_handler)
        aw_logger.setLevel(logging.INFO)
    
    def get_logger(self, name: str) -> logging.Logger:
        """获取或创建日志器"""
        if name not in self._loggers:
            logger = logging.getLogger(name)
            
            # 设置模块特定的日志级别
            for module_prefix, level_str in MODULE_LOG_LEVELS.items():
                if name.startswith(module_prefix):
                    logger.setLevel(LOG_LEVELS[level_str])
                    break
            
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def set_level(self, logger_name: str, level: str):
        """动态设置日志级别"""
        if logger_name in self._loggers:
            self._loggers[logger_name].setLevel(LOG_LEVELS.get(level, logging.INFO))
    
    def set_console_level(self, level: str):
        """设置控制台日志级别"""
        if 'console' in self._handlers:
            self._handlers['console'].setLevel(LOG_LEVELS.get(level, logging.INFO))
    
    def get_log_files(self) -> Dict[str, Path]:
        """获取所有日志文件路径"""
        return {
            'main': MAIN_LOG,
            'error': ERROR_LOG,
            'performance': PERFORMANCE_LOG,
            'api': API_LOG,
            'ui': UI_LOG,
            'schedule': SCHEDULE_LOG,
            'activity_watch': AW_LOG
        }
    
    def cleanup_old_logs(self, days: int = 7):
        """清理旧日志文件"""
        import time
        current_time = time.time()
        
        for log_file in LOG_DIR.glob('*.log*'):
            if log_file.stat().st_mtime < current_time - (days * 86400):
                try:
                    log_file.unlink()
                    logging.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    logging.error(f"Failed to delete log file {log_file}: {e}")


# 便捷函数
def get_logger(name: str) -> logging.Logger:
    """获取日志器的便捷函数"""
    config = LoggerConfig()
    return config.get_logger(name)


def log_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger('performance')
        start_time = time.time()
        
        # 记录函数调用
        logger.debug(f"Starting {func.__name__}", extra={'extra_data': {
            'function': func.__name__,
            'module': func.__module__,
            'args_count': len(args),
            'kwargs_keys': list(kwargs.keys())
        }})
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            # 记录成功执行
            logger.info(f"Completed {func.__name__} in {elapsed:.3f}s", extra={'extra_data': {
                'function': func.__name__,
                'elapsed_time': elapsed,
                'status': 'success'
            }})
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            
            # 记录异常
            logger.error(f"Failed {func.__name__} after {elapsed:.3f}s: {str(e)}", extra={'extra_data': {
                'function': func.__name__,
                'elapsed_time': elapsed,
                'status': 'error',
                'error_type': type(e).__name__,
                'error_message': str(e)
            }}, exc_info=True)
            
            raise
    
    return wrapper


def log_api_call(service: str, endpoint: str, method: str = 'GET'):
    """API调用日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger('api')
            request_id = datetime.now().strftime('%Y%m%d%H%M%S%f')
            
            # 记录API请求
            logger.info(f"API Request [{request_id}]", extra={'extra_data': {
                'request_id': request_id,
                'service': service,
                'endpoint': endpoint,
                'method': method,
                'function': func.__name__
            }})
            
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                elapsed = time.time() - start_time
                
                # 记录API响应
                logger.info(f"API Response [{request_id}]", extra={'extra_data': {
                    'request_id': request_id,
                    'service': service,
                    'endpoint': endpoint,
                    'elapsed_time': elapsed,
                    'status': 'success'
                }})
                
                return result
                
            except Exception as e:
                elapsed = time.time() - start_time
                
                # 记录API错误
                logger.error(f"API Error [{request_id}]", extra={'extra_data': {
                    'request_id': request_id,
                    'service': service,
                    'endpoint': endpoint,
                    'elapsed_time': elapsed,
                    'status': 'error',
                    'error_type': type(e).__name__,
                    'error_message': str(e)
                }}, exc_info=True)
                
                raise
        
        return wrapper
    return decorator


def log_ui_event(event_type: str):
    """UI事件日志装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger('ui')
            
            # 记录UI事件
            logger.info(f"UI Event: {event_type} - {func.__name__}")
            
            try:
                result = func(*args, **kwargs)
                logger.debug(f"UI Event Completed: {event_type} - {func.__name__}")
                return result
                
            except Exception as e:
                logger.error(f"UI Event Failed: {event_type} - {func.__name__}: {str(e)}", exc_info=True)
                raise
        
        return wrapper
    return decorator


# 初始化日志配置
def init_logging(console_level: str = 'INFO', file_level: str = 'DEBUG'):
    """初始化日志系统"""
    config = LoggerConfig()
    config.set_console_level(console_level)
    
    # 清理旧日志
    config.cleanup_old_logs()
    
    # 记录启动信息
    logger = get_logger('baal.desktop_pet')
    logger.info("="*50)
    logger.info("Baal Desktop Pet Starting")
    logger.info(f"Log directory: {LOG_DIR}")
    logger.info(f"Console level: {console_level}")
    logger.info(f"File level: {file_level}")
    logger.info("="*50)
    
    return config


if __name__ == "__main__":
    # 测试日志系统
    init_logging()
    
    # 测试不同级别的日志
    logger = get_logger('test')
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    
    # 测试性能日志
    @log_performance
    def test_function():
        import time
        time.sleep(0.1)
        return "Success"
    
    test_function()
    
    # 测试API日志
    @log_api_call('openai', '/v1/chat/completions', 'POST')
    def test_api():
        return {"response": "test"}
    
    test_api()
    
    print(f"\nLog files created in: {LOG_DIR}")