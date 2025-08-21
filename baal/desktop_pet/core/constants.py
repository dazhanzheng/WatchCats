"""
常量定义模块

集中管理所有硬编码值，便于维护和调整
"""

from typing import Dict, Any

# ============== 时间相关常量 ==============

# 字符延迟设置（秒）
CHAR_DELAYS = {
    'punctuation': 0.3,      # 标点符号延迟
    'normal': 0.05,          # 普通字符延迟
    'fast': 0.02,            # 快速模式延迟
    'ellipsis': 0.5,         # 省略号延迟
    'newline': 0.2,          # 换行延迟
    'emoji': 0.1             # 表情符号延迟
}

# 计时器间隔（毫秒）
TIMERS = {
    'emotion_reset': 5000,           # 表情重置延迟
    'bubble_auto_hide': 30000,       # 气泡自动隐藏时间
    'welcome_delay': 500,            # 欢迎消息延迟
    'settings_open_delay': 1500,     # 设置对话框打开延迟
    'hide_buttons_check': 500,       # 检查隐藏按钮延迟
    'async_response_start': 500      # 开始AI响应延迟
}

# 监督模式设置
SUPERVISION = {
    'default_check_interval': 300,   # 默认检查间隔（秒）- 5分钟
    'min_check_interval': 30,        # 最小检查间隔（秒）
    'max_check_interval': 3600,      # 最大检查间隔（秒）- 1小时
    'thread_join_timeout': 5,        # 线程等待超时（秒）
    'parse_temperature': 0.1,        # LLM解析温度
    'chat_temperature': 0.85         # LLM对话温度
}

# ============== UI相关常量 ==============

# 窗口尺寸
WINDOW_SIZES = {
    'pet': {
        'width': 140,
        'height': 140
    },
    'bubble': {
        'default_width': 300,
        'default_height': 200,
        'min_width': 200,
        'min_height': 100,
        'max_width': 600,
        'max_height': 400
    },
    'settings': {
        'width': 500,
        'height': 650
    }
}

# macOS 刘海屏安全区域
MACOS_NOTCH_SAFE_AREA = 90  # 顶部90像素安全区

# 透明度设置
OPACITY = {
    'window': 0.95,
    'bubble': 0.95,
    'button_hover': 0.8,
    'button_normal': 0.6
}

# ============== 数据处理常量 ==============

# ActivityWatch 事件限制
AW_EVENTS = {
    'window_events_limit': 2000,     # 窗口事件最大数量
    'afk_events_limit': 1000,        # AFK事件最大数量
    'page_size': 500,                # 分页大小
    'query_timeout': 30              # 查询超时（秒）
}

# JSON 解析设置
JSON_PARSE = {
    'max_retry': 3,                  # 最大重试次数
    'validation_timeout': 5          # 验证超时（秒）
}

# ============== 线程和并发 ==============

THREADING = {
    'worker_wait_timeout': 1000,     # 工作线程等待超时（毫秒）
    'config_lock_timeout': 5,        # 配置锁超时（秒）
    'max_concurrent_tasks': 5        # 最大并发任务数
}

# ============== 文件和路径 ==============

FILES = {
    'config_backup_suffix': '.bak',
    'config_temp_suffix': '.tmp',
    'max_backup_size': 10485760,     # 最大备份文件大小（10MB）
    'history_max_entries': 1000      # 历史记录最大条目数
}

# ============== API 配置 ==============

API = {
    'default_timeout': 30,            # 默认API超时（秒）
    'retry_count': 3,                 # 重试次数
    'retry_delay': 1,                 # 重试延迟（秒）
    'max_tokens': 4096,               # 最大token数
    'stream_buffer_size': 1024        # 流式缓冲区大小
}

# ============== 表情系统 ==============

EMOTIONS = {
    'default': 'normal',
    'reset_delay': 5000,              # 表情重置延迟（毫秒）
    'animation_fps': 30,              # 动画帧率
    'transition_duration': 200        # 过渡动画时长（毫秒）
}

# 表情映射
EMOTION_TAGS = {
    1: 'normal',      # 正常
    2: 'happy',       # 开心
    3: 'angry',       # 生气
    4: 'confused',    # 困惑
    5: 'sad',         # 悲伤
    6: 'excited',     # 兴奋
    7: 'tired'        # 疲倦
}

# ============== 人格系统 ==============

PERSONAS = {
    'default': 'strict_master',
    'types': ['strict_master', 'sarcastic_butler', 'gentle_companion']
}

# ============== 日志设置 ==============

LOGGING = {
    'max_file_size': 10485760,       # 最大日志文件大小（10MB）
    'backup_count': 5,                # 保留备份数量
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S'
}

def get_char_delay(char: str) -> float:
    """
    根据字符类型获取延迟时间
    
    Args:
        char: 字符
        
    Returns:
        延迟时间（秒）
    """
    if char in '，。！？；：':
        return CHAR_DELAYS['punctuation']
    elif char in '…':
        return CHAR_DELAYS['ellipsis']
    elif char == '\n':
        return CHAR_DELAYS['newline']
    elif ord(char) >= 0x1F300:  # Unicode表情范围
        return CHAR_DELAYS['emoji']
    else:
        return CHAR_DELAYS['normal']

def get_timer_interval(timer_name: str) -> int:
    """
    获取计时器间隔
    
    Args:
        timer_name: 计时器名称
        
    Returns:
        间隔时间（毫秒）
    """
    return TIMERS.get(timer_name, 1000)  # 默认1秒

def get_window_size(window_type: str) -> Dict[str, int]:
    """
    获取窗口尺寸配置
    
    Args:
        window_type: 窗口类型（pet/bubble/settings）
        
    Returns:
        尺寸配置字典
    """
    return WINDOW_SIZES.get(window_type, WINDOW_SIZES['pet'])