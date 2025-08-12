"""
增强版配置管理器 - 改进 Windows 兼容性

负责管理应用配置，包括API密钥、基础URL等
特别优化了 Windows 平台的文件操作和权限处理
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


class EnhancedConfigManager:
    """增强版配置管理器类"""
    
    DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
    DEFAULT_MODEL = "deepseek-v3-250324"
    
    def __init__(self):
        """初始化配置管理器"""
        self.logger = get_logger('baal.desktop_pet.core.config_manager_enhanced')
        self.logger.info("Initializing EnhancedConfigManager")
        self.logger.info(f"Platform: {sys.platform}, Python: {sys.version}")
        
        # 配置文件路径
        self.config_dir = self._get_config_dir()
        self.config_file = self.config_dir / "config.json"
        
        self.logger.debug(f"Config directory: {self.config_dir}")
        self.logger.debug(f"Config file: {self.config_file}")
        
        # 确保配置目录存在
        self._ensure_config_dir()
        
        # 加载配置
        self.config = self._load_config()
        self.logger.info(f"Configuration loaded. API key configured: {self.is_configured()}")
    
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
    
    @log_performance
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件，增强错误恢复"""
        if self.config_file.exists():
            self.logger.info(f"Loading existing config file: {self.config_file}")
            
            # 尝试读取配置
            for attempt in range(3):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        
                    # 确保基础配置存在
                    if 'base_url' not in config:
                        config['base_url'] = self.DEFAULT_BASE_URL
                    if 'model' not in config:
                        config['model'] = self.DEFAULT_MODEL
                    
                    # 记录加载的配置（隐藏敏感信息）
                    safe_config = {k: v for k, v in config.items() if k != 'api_key'}
                    safe_config['api_key'] = '***' if config.get('api_key') else 'Not set'
                    self.logger.debug(f"Config loaded: {safe_config}")
                    
                    return config
                    
                except json.JSONDecodeError as e:
                    self.logger.error(f"Config file corrupted (attempt {attempt + 1}): {e}")
                    
                    # 尝试从备份恢复
                    backup_file = self.config_file.with_suffix('.bak')
                    if backup_file.exists() and attempt == 0:
                        self.logger.info("Trying to restore from backup...")
                        try:
                            with open(backup_file, 'r', encoding='utf-8') as f:
                                config = json.load(f)
                            # 恢复成功，保存为主配置
                            self._safe_write_config(config)
                            return config
                        except Exception as e2:
                            self.logger.error(f"Backup also corrupted: {e2}")
                    
                    if attempt == 2:
                        # 最后一次尝试，移动损坏的文件并使用默认配置
                        corrupted_file = self.config_file.with_suffix('.corrupted')
                        try:
                            self.config_file.rename(corrupted_file)
                            self.logger.warning(f"Moved corrupted config to: {corrupted_file}")
                        except:
                            pass
                        break
                        
                except Exception as e:
                    self.logger.error(f"Failed to load config (attempt {attempt + 1}): {e}")
                    if attempt < 2:
                        time.sleep(0.5)
        else:
            self.logger.info("Config file does not exist, will create new")
        
        # 返回默认配置
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            'api_key': '',
            'base_url': self.DEFAULT_BASE_URL,
            'model': self.DEFAULT_MODEL,
            'chat_temperature': 0.7,
            'parse_temperature': 0.1,
            'char_delays': {
                'normal': 0.2,
                'punctuation': 0.8,
                'newline': 0.5
            },
            'always_on_top': True
        }
    
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
    
    @log_performance
    def save_config(self, config=None):
        """保存配置到文件"""
        if config is not None:
            self.config = config
        
        # 记录要保存的配置（隐藏敏感信息）
        safe_config = {k: v for k, v in self.config.items() if k != 'api_key'}
        safe_config['api_key'] = '***' if self.config.get('api_key') else 'Not set'
        self.logger.info(f"Saving configuration: {safe_config}")
        
        # 使用安全写入方法
        return self._safe_write_config(self.config)
    
    def get_api_key(self) -> Optional[str]:
        """获取API密钥"""
        api_key = self.config.get('api_key', '')
        return api_key if api_key else None
    
    def set_api_key(self, api_key: str):
        """设置API密钥"""
        self.logger.info(f"Setting new API key (length: {len(api_key)})")
        self.config['api_key'] = api_key
        
        if self.save_config():
            self.logger.info("API key updated successfully")
        else:
            self.logger.error("Failed to save API key to file")
            self.logger.warning("API key kept in memory for this session")
    
    def get_base_url(self) -> str:
        """获取基础URL"""
        return self.config.get('base_url', self.DEFAULT_BASE_URL)
    
    def get_model(self) -> str:
        """获取模型名称"""
        return self.config.get('model', self.DEFAULT_MODEL)
    
    def get_window_position(self) -> Dict[str, int]:
        """获取窗口位置"""
        return self.config.get('window_position', {'x': 100, 'y': 100})
    
    def set_window_position(self, x: int, y: int):
        """设置窗口位置"""
        self.logger.debug(f"Setting window position: x={x}, y={y}")
        self.config['window_position'] = {'x': x, 'y': y}
        
        if not self.save_config():
            self.logger.warning("Failed to save window position")
    
    def get_temperature_settings(self) -> Dict[str, float]:
        """获取温度设置"""
        return {
            'chat_temperature': self.config.get('chat_temperature', 0.7),
            'parse_temperature': self.config.get('parse_temperature', 0.1)
        }
    
    def is_configured(self) -> bool:
        """检查是否已配置API密钥"""
        return bool(self.get_api_key())
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config.copy()
    
    def reset_config(self):
        """重置配置为默认值"""
        self.logger.warning("Resetting configuration to defaults")
        self.config = self._get_default_config()
        self.save_config()
    
    def export_config(self, path: Path) -> bool:
        """导出配置到指定路径"""
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            self.logger.info(f"Config exported to: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export config: {e}")
            return False
    
    def import_config(self, path: Path) -> bool:
        """从指定路径导入配置"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                new_config = json.load(f)
            
            # 验证配置格式
            if not isinstance(new_config, dict):
                raise ValueError("Invalid config format")
            
            self.config = new_config
            self.save_config()
            self.logger.info(f"Config imported from: {path}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to import config: {e}")
            return False


# 为了向后兼容，保留原始类名的别名
ConfigManager = EnhancedConfigManager