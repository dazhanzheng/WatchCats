"""
配置管理器

负责管理应用配置，包括API密钥、基础URL等
增强了 Windows 兼容性和错误处理
"""

import json
import os
import sys
import platform
import shutil
import time
from pathlib import Path
from typing import Dict, Any, Optional
from .logger_config import get_logger, log_performance
from .default_config import get_default_config


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
        self._ensure_config_dir()
        
        # 加载配置
        self.config = self._load_config()
        self.logger.info(f"Configuration loaded. API key configured: {self.is_configured()}")
    
    def _ensure_config_dir(self):
        """确保配置目录存在，增强错误处理"""
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                self.config_dir.mkdir(parents=True, exist_ok=True)
                
                # 验证目录确实存在且可写
                test_file = self.config_dir / '.test_write'
                try:
                    test_file.write_text('test')
                    test_file.unlink()
                    self.logger.debug(f"Config directory verified writable: {self.config_dir}")
                    return
                except Exception as e:
                    self.logger.warning(f"Directory exists but not writable: {e}")
                    raise PermissionError(f"Cannot write to {self.config_dir}")
                    
            except Exception as e:
                self.logger.error(f"Attempt {attempt + 1} failed to create config directory: {e}")
                
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指数退避
                else:
                    # 最后一次尝试失败，尝试备用位置
                    if sys.platform == "win32":
                        # Windows: 尝试用户主目录
                        fallback_dir = Path.home() / "BaalPet"
                        self.logger.warning(f"Trying fallback directory: {fallback_dir}")
                        try:
                            fallback_dir.mkdir(parents=True, exist_ok=True)
                            self.config_dir = fallback_dir
                            self.config_file = self.config_dir / "config.json"
                            self.logger.info(f"Using fallback directory: {self.config_dir}")
                            return
                        except Exception as e2:
                            self.logger.error(f"Fallback also failed: {e2}")
                    
                    raise RuntimeError(f"Cannot create config directory after {max_retries} attempts")
    
    def _get_config_dir(self) -> Path:
        """获取配置目录路径，改进 Windows 兼容性"""
        if sys.platform == "win32":
            # Windows: 使用多种方法查找合适的配置目录
            config_dir = None
            
            # 方法1: 使用 APPDATA 环境变量
            appdata = os.environ.get('APPDATA')
            if appdata and os.path.exists(appdata):
                config_dir = Path(appdata) / "BaalPet"
                self.logger.info(f"Using APPDATA: {config_dir}")
            
            # 方法2: 使用 LOCALAPPDATA
            if not config_dir:
                localappdata = os.environ.get('LOCALAPPDATA')
                if localappdata and os.path.exists(localappdata):
                    config_dir = Path(localappdata) / "BaalPet"
                    self.logger.info(f"Using LOCALAPPDATA: {config_dir}")
            
            # 方法3: 通过 expanduser 和路径构建
            if not config_dir:
                try:
                    home = Path.home()
                    # 尝试标准 Windows 路径
                    appdata_roaming = home / 'AppData' / 'Roaming'
                    appdata_local = home / 'AppData' / 'Local'
                    
                    if appdata_roaming.exists():
                        config_dir = appdata_roaming / "BaalPet"
                        self.logger.info(f"Using constructed Roaming path: {config_dir}")
                    elif appdata_local.exists():
                        config_dir = appdata_local / "BaalPet"
                        self.logger.info(f"Using constructed Local path: {config_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to construct AppData path: {e}")
            
            # 方法4: 使用用户文档目录
            if not config_dir:
                try:
                    # Windows 上的文档目录通常更可靠
                    documents = Path.home() / 'Documents'
                    if documents.exists():
                        config_dir = documents / "BaalPet"
                        self.logger.info(f"Using Documents directory: {config_dir}")
                except Exception as e:
                    self.logger.warning(f"Failed to use Documents: {e}")
            
            # 最后的回退：用户主目录
            if not config_dir:
                config_dir = Path.home() / ".baal_pet"
                self.logger.warning(f"Using fallback home directory: {config_dir}")
            
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
        
        # 使用预设的默认配置（包含API密钥）
        default_config = get_default_config()
        
        self.logger.info("Using default configuration with preset API key")
        # 记录配置但隐藏API密钥
        safe_config = {k: v for k, v in default_config.items() if k != 'api_key'}
        safe_config['api_key'] = '***' if default_config.get('api_key') else 'Not set'
        self.logger.debug(f"Default config: {safe_config}")
        
        # 自动保存默认配置到文件
        self._safe_write_config(default_config)
        self.logger.info("Default configuration saved to file")
        
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
        
        # 使用安全写入方法
        return self._safe_write_config(self.config)
    
    def _safe_write_config(self, config: Dict[str, Any]) -> bool:
        """安全地写入配置文件"""
        # 确保目录存在
        self._ensure_config_dir()
        
        # 使用临时文件写入
        temp_file = self.config_file.with_suffix('.tmp')
        backup_file = self.config_file.with_suffix('.bak')
        
        try:
            # 1. 写入临时文件
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            # 2. 验证临时文件
            with open(temp_file, 'r', encoding='utf-8') as f:
                json.load(f)  # 验证 JSON 格式正确
            
            # 3. 备份现有文件（如果存在）
            if self.config_file.exists():
                try:
                    # Windows 上可能需要先删除旧备份
                    if backup_file.exists():
                        backup_file.unlink()
                    
                    # 复制而不是移动，避免权限问题
                    shutil.copy2(self.config_file, backup_file)
                    self.logger.debug(f"Backed up config to: {backup_file}")
                except Exception as e:
                    self.logger.warning(f"Could not create backup: {e}")
            
            # 4. 替换主配置文件
            if sys.platform == "win32":
                # Windows: 需要先删除目标文件
                if self.config_file.exists():
                    try:
                        self.config_file.unlink()
                    except Exception as e:
                        self.logger.warning(f"Could not delete old config: {e}")
                        # 尝试使用 shutil.move
                        shutil.move(str(temp_file), str(self.config_file))
                        return True
            
            # 重命名临时文件为配置文件
            try:
                temp_file.rename(self.config_file)
            except Exception:
                # 如果重命名失败，尝试复制
                shutil.copy2(temp_file, self.config_file)
                temp_file.unlink()
            
            self.logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save config: {e}", exc_info=True)
            
            # 清理临时文件
            if temp_file.exists():
                try:
                    temp_file.unlink()
                except:
                    pass
            
            # 尝试从备份恢复
            if backup_file.exists() and not self.config_file.exists():
                try:
                    shutil.copy2(backup_file, self.config_file)
                    self.logger.info("Restored config from backup")
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
            # 即使保存失败，也保留在内存中，这样至少本次运行可以使用
            self.logger.warning("API key kept in memory for this session")
    
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