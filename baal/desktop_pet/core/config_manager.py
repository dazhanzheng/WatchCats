"""
配置管理器

负责管理应用配置，包括API密钥、基础URL等
"""

import json
import os
import sys
import platform
from pathlib import Path
from typing import Dict, Any, Optional
from .logger_config import get_logger, log_performance


class ConfigManager:
    """配置管理器类"""
    
    DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"  # 固定的base URL
    DEFAULT_MODEL = "deepseek-v3-250324"
    
    def __init__(self):
        """初始化配置管理器"""
        self.logger = get_logger('baal.desktop_pet.core.config_manager')
        self.logger.info("Initializing ConfigManager")
        # 配置文件路径 - Windows使用AppData，其他系统使用用户目录
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        
        self.logger.debug(f"Config directory: {self.config_dir}")
        self.logger.debug(f"Config file: {self.config_file}")
        
        # 确保配置目录存在
        try:
            self.config_dir.mkdir(exist_ok=True)
            self.logger.debug(f"Config directory created/verified: {self.config_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {e}", exc_info=True)
            raise
        
        # 加载配置
        self.config = self._load_config()
        self.logger.info(f"Configuration loaded. API key configured: {self.is_configured()}")
    
    def _get_config_dir(self) -> Path:
        """获取配置目录路径，Windows使用AppData目录"""
        if sys.platform == "win32":
            # Windows: 使用 AppData/Local 目录
            appdata = os.environ.get('LOCALAPPDATA')
            if not appdata:
                # 如果LOCALAPPDATA不存在，尝试APPDATA
                appdata = os.environ.get('APPDATA')
            if not appdata:
                # 如果都不存在，使用用户主目录
                self.logger.warning("Cannot find AppData directory, using home directory")
                return Path.home() / ".baal_pet"
            
            config_dir = Path(appdata) / "BaalPet"
            self.logger.info(f"Using Windows AppData directory: {config_dir}")
            
            # 创建目录时设置完全权限
            try:
                config_dir.mkdir(parents=True, exist_ok=True)
                # Windows上确保有写入权限
                if platform.system() == "Windows":
                    import stat
                    config_dir.chmod(stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
            except Exception as e:
                self.logger.error(f"Failed to create config directory: {e}")
                # 回退到用户目录
                config_dir = Path.home() / ".baal_pet"
                self.logger.warning(f"Falling back to home directory: {config_dir}")
            
            return config_dir
        else:
            # macOS/Linux: 使用用户主目录
            return Path.home() / ".baal_pet"
    
    @log_performance
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_file.exists():
            self.logger.info(f"Loading existing config file: {self.config_file}")
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.logger.debug(f"Raw config loaded: {len(config)} keys")
                    
                    # 确保基础配置存在
                    if 'base_url' not in config:
                        config['base_url'] = self.DEFAULT_BASE_URL
                        self.logger.info(f"Added default base_url: {self.DEFAULT_BASE_URL}")
                    
                    if 'model' not in config:
                        config['model'] = self.DEFAULT_MODEL
                        self.logger.info(f"Added default model: {self.DEFAULT_MODEL}")
                    
                    # 记录加载的配置（不记录敏感信息）
                    safe_config = {k: v for k, v in config.items() if k != 'api_key'}
                    safe_config['api_key'] = '***' if config.get('api_key') else 'Not set'
                    self.logger.debug(f"Config loaded successfully: {safe_config}")
                    
                    return config
            except json.JSONDecodeError as e:
                self.logger.error(f"Config file is corrupted (JSON decode error): {e}", exc_info=True)
                self.logger.warning("Will use default configuration")
            except Exception as e:
                self.logger.error(f"Failed to load config file: {e}", exc_info=True)
                self.logger.warning("Will use default configuration")
        else:
            self.logger.info("Config file does not exist, creating default configuration")
        
        # 返回默认配置
        default_config = {
            'api_key': '',
            'base_url': self.DEFAULT_BASE_URL,
            'model': self.DEFAULT_MODEL,
            'chat_temperature': 0.7,
            'parse_temperature': 0.1,
            'char_delays': {
                'normal': 0.2,       # 普通字符：200ms（原来的10倍）
                'punctuation': 0.8,  # 标点符号：800ms（原来的10倍）
                'newline': 0.5       # 换行符：500ms（原来的10倍）
            },
            'always_on_top': True    # 默认开启始终置顶
        }
        
        self.logger.info("Using default configuration")
        self.logger.debug(f"Default config: {default_config}")
        return default_config
    
    @log_performance
    def save_config(self, config=None):
        """保存配置到文件"""
        if config is not None:
            self.config = config
            self.logger.debug("Using provided config for saving")
        
        # 记录要保存的配置（隐藏敏感信息）
        safe_config = {k: v for k, v in self.config.items() if k != 'api_key'}
        safe_config['api_key'] = '***' if self.config.get('api_key') else 'Not set'
        self.logger.info(f"Saving configuration to {self.config_file}")
        self.logger.debug(f"Configuration to save: {safe_config}")
        
        # 确保目录存在
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            self.logger.debug(f"Ensured config directory exists: {self.config_dir}")
        except Exception as e:
            self.logger.error(f"Failed to create config directory: {e}")
            if sys.platform == "win32":
                self.logger.error("On Windows, try running the application as Administrator")
            return False
        
        # 尝试写入临时文件测试权限
        temp_file = self.config_file.with_suffix('.tmp')
        try:
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # 如果临时文件写入成功，重命名为正式文件
            if self.config_file.exists():
                # 备份旧文件
                backup_file = self.config_file.with_suffix('.bak')
                try:
                    if backup_file.exists():
                        backup_file.unlink()
                    self.config_file.rename(backup_file)
                    self.logger.debug(f"Backed up old config to {backup_file}")
                except Exception as e:
                    self.logger.warning(f"Could not backup old config: {e}")
            
            # 重命名临时文件
            temp_file.rename(self.config_file)
            self.logger.info("Configuration saved successfully")
            return True
            
        except PermissionError as e:
            self.logger.error(f"Permission denied when saving config: {e}", exc_info=True)
            self.logger.error(f"Config directory: {self.config_dir}")
            self.logger.error(f"Config file: {self.config_file}")
            if sys.platform == "win32":
                self.logger.error("Windows permission issue detected!")
                self.logger.error("Solutions:")
                self.logger.error("1. Run the application as Administrator")
                self.logger.error("2. Check if antivirus is blocking file writes")
                self.logger.error("3. Ensure the directory is not read-only")
            # 清理临时文件
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
            return False
        except Exception as e:
            self.logger.error(f"Failed to save config file: {e}", exc_info=True)
            # 清理临时文件
            try:
                if temp_file.exists():
                    temp_file.unlink()
            except:
                pass
            return False
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        api_key = self.config.get('api_key', '')
        has_key = bool(api_key)
        self.logger.debug(f"Getting API key: {'Set' if has_key else 'Not set'}")
        return api_key if api_key else None
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.logger.info(f"Setting new API key (length: {len(api_key)})")
        old_key = self.config.get('api_key', '')
        self.config['api_key'] = api_key
        
        if self.save_config():
            self.logger.info("API key updated successfully")
            if not old_key and api_key:
                self.logger.info("First time API key configuration completed")
        else:
            self.logger.error("Failed to save API key")
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        base_url = self.config.get('base_url', self.DEFAULT_BASE_URL)
        self.logger.debug(f"Getting base URL: {base_url}")
        return base_url
    
    def get_model(self) -> str:
        """获取模型名称"""
        model = self.config.get('model', self.DEFAULT_MODEL)
        self.logger.debug(f"Getting model: {model}")
        return model
    
    def get_window_position(self) -> Dict[str, int]:
        """获取窗口位置"""
        position = self.config.get('window_position', {'x': 100, 'y': 100})
        self.logger.debug(f"Getting window position: x={position['x']}, y={position['y']}")
        return position
    
    def set_window_position(self, x: int, y: int):
        """设置窗口位置"""
        self.logger.debug(f"Setting window position: x={x}, y={y}")
        old_position = self.config.get('window_position', {})
        self.config['window_position'] = {'x': x, 'y': y}
        
        if self.save_config():
            self.logger.debug(f"Window position updated from ({old_position.get('x')}, {old_position.get('y')}) to ({x}, {y})")
        else:
            self.logger.warning("Failed to save window position")
    
    def get_temperature_settings(self) -> Dict[str, float]:
        """获取温度设置"""
        settings = {
            'chat_temperature': self.config.get('chat_temperature', 0.7),
            'parse_temperature': self.config.get('parse_temperature', 0.1)
        }
        self.logger.debug(f"Getting temperature settings: chat={settings['chat_temperature']}, parse={settings['parse_temperature']}")
        return settings
    
    def is_configured(self) -> bool:
        """检查是否已配置API密钥"""
        configured = bool(self.get_api_key())
        self.logger.debug(f"Configuration status: {'Configured' if configured else 'Not configured'}")
        return configured 
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        self.logger.debug("Getting full configuration")
        # 返回配置的副本，避免外部修改
        return self.config.copy() 