"""
默认配置
包含预设的API密钥和其他默认设置
"""

# 默认API配置
DEFAULT_API_KEY = "6be4b0c1-8e71-4530-908a-cbe4b48a9a07"
DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "deepseek-v3-250324"

# 默认配置字典
DEFAULT_CONFIG = {
    'api_key': DEFAULT_API_KEY,
    'base_url': DEFAULT_BASE_URL,
    'model': DEFAULT_MODEL,
    'chat_temperature': 0.7,
    'parse_temperature': 0.1,
    'char_delays': {
        'normal': 0.02,
        'punctuation': 0.08,
        'newline': 0.05
    },
    'always_on_top': True,
    'start_minimized': False,
    'pet_size': 120,
    'persona_level': 1  # 默认严厉主人档
}

def get_default_config():
    """获取默认配置的副本"""
    import copy
    return copy.deepcopy(DEFAULT_CONFIG)