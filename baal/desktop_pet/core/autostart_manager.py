"""
开机自启动管理器

用于管理应用程序的开机自启动设置
"""

import sys
import os
from pathlib import Path


class AutostartManager:
    """开机自启动管理器"""
    
    def __init__(self):
        """初始化管理器"""
        self.app_name = "WatchCats"
        self.app_path = self._get_app_path()
    
    def _get_app_path(self):
        """获取应用程序路径"""
        if getattr(sys, 'frozen', False):
            # 打包后的应用
            return sys.executable
        else:
            # 开发环境
            return sys.argv[0]
    
    def is_autostart_enabled(self):
        """
        检查是否已启用开机自启动
        
        Returns:
            bool: 是否已启用
        """
        if sys.platform == "win32":
            return self._is_windows_autostart_enabled()
        elif sys.platform == "darwin":
            # macOS 暂不实现
            return False
        else:
            # Linux 暂不实现
            return False
    
    def enable_autostart(self):
        """
        启用开机自启动
        
        Returns:
            bool: 是否成功
        """
        if sys.platform == "win32":
            return self._enable_windows_autostart()
        elif sys.platform == "darwin":
            # macOS 暂不实现
            return False
        else:
            # Linux 暂不实现
            return False
    
    def disable_autostart(self):
        """
        禁用开机自启动
        
        Returns:
            bool: 是否成功
        """
        if sys.platform == "win32":
            return self._disable_windows_autostart()
        elif sys.platform == "darwin":
            # macOS 暂不实现
            return False
        else:
            # Linux 暂不实现
            return False
    
    # Windows 平台实现
    def _is_windows_autostart_enabled(self):
        """检查 Windows 是否已启用开机自启动"""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            try:
                # 打开注册表键
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_READ
                )
                
                # 尝试读取值
                value, _ = winreg.QueryValueEx(key, self.app_name)
                winreg.CloseKey(key)
                
                # 检查路径是否匹配
                return value == f'"{self.app_path}"'
                
            except FileNotFoundError:
                # 键不存在
                return False
            except WindowsError:
                # 值不存在
                return False
                
        except ImportError:
            # 非 Windows 平台
            return False
        except Exception as e:
            print(f"检查自启动状态失败: {e}")
            return False
    
    def _enable_windows_autostart(self):
        """在 Windows 上启用开机自启动"""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            try:
                # 打开或创建注册表键
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_SET_VALUE
                )
                
                # 设置值（用引号包围路径以处理空格）
                winreg.SetValueEx(
                    key,
                    self.app_name,
                    0,
                    winreg.REG_SZ,
                    f'"{self.app_path}"'
                )
                
                winreg.CloseKey(key)
                print(f"已添加到开机启动: {self.app_path}")
                return True
                
            except Exception as e:
                print(f"添加开机启动失败: {e}")
                return False
                
        except ImportError:
            print("非 Windows 平台，无法设置开机启动")
            return False
    
    def _disable_windows_autostart(self):
        """在 Windows 上禁用开机自启动"""
        try:
            import winreg
            
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            
            try:
                # 打开注册表键
                key = winreg.OpenKey(
                    winreg.HKEY_CURRENT_USER,
                    key_path,
                    0,
                    winreg.KEY_SET_VALUE
                )
                
                # 删除值
                winreg.DeleteValue(key, self.app_name)
                winreg.CloseKey(key)
                
                print(f"已从开机启动中移除")
                return True
                
            except FileNotFoundError:
                # 键不存在，已经没有设置自启动
                return True
            except WindowsError:
                # 值不存在，已经没有设置自启动
                return True
            except Exception as e:
                print(f"移除开机启动失败: {e}")
                return False
                
        except ImportError:
            print("非 Windows 平台")
            return False