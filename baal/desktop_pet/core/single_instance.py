"""
单实例管理器 - 确保应用只运行一个实例

支持 Windows、macOS 和 Linux
"""

import os
import sys
import platform
import time
import atexit
from pathlib import Path

class SingleInstance:
    """
    确保应用程序只运行一个实例的管理器
    
    使用文件锁或系统特定的机制来防止多个实例运行
    """
    
    def __init__(self, app_name="BaalPetAssistant"):
        """
        初始化单实例管理器
        
        Args:
            app_name: 应用程序名称，用于创建唯一标识
        """
        self.app_name = app_name
        self.is_running = False
        self.lock_file = None
        self.system = platform.system()
        
        # 根据系统选择不同的实现
        if self.system == "Windows":
            self._init_windows()
        else:
            self._init_unix()
    
    def _init_windows(self):
        """Windows 平台初始化"""
        try:
            import win32event
            import win32api
            import winerror
            self.use_win32 = True
            # 创建一个命名的互斥体
            self.mutex_name = f"Global\\{self.app_name}_mutex"
            self.mutex = None
        except ImportError:
            # 如果没有 pywin32，退回到文件锁方式
            self.use_win32 = False
            self._init_file_lock()
    
    def _init_unix(self):
        """Unix/Linux/macOS 平台初始化"""
        self._init_file_lock()
    
    def _init_file_lock(self):
        """初始化基于文件的锁机制"""
        # 获取临时目录
        if self.system == "Windows":
            temp_dir = Path(os.environ.get('TEMP', os.environ.get('TMP', '/tmp')))
        else:
            temp_dir = Path('/tmp')
        
        # 创建锁文件路径
        self.lock_file_path = temp_dir / f".{self.app_name}.lock"
    
    def check(self):
        """
        检查是否已有实例在运行
        
        Returns:
            bool: 如果获取锁成功（没有其他实例运行）返回 True，否则返回 False
        """
        if self.system == "Windows" and hasattr(self, 'use_win32') and self.use_win32:
            return self._check_windows()
        else:
            return self._check_file_lock()
    
    def _check_windows(self):
        """Windows 平台检查（使用互斥体）"""
        try:
            import win32event
            import win32api
            import winerror
            
            # 尝试创建互斥体
            self.mutex = win32event.CreateMutex(None, False, self.mutex_name)
            
            # 检查是否已存在
            if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
                # 已有实例在运行
                if self.mutex:
                    win32api.CloseHandle(self.mutex)
                    self.mutex = None
                return False
            
            # 成功获取锁
            self.is_running = True
            atexit.register(self.release)
            return True
            
        except Exception as e:
            print(f"Windows mutex check failed: {e}")
            # 退回到文件锁
            return self._check_file_lock()
    
    def _check_file_lock(self):
        """基于文件的锁检查"""
        try:
            # 检查锁文件是否存在
            if self.lock_file_path.exists():
                # 读取 PID
                try:
                    with open(self.lock_file_path, 'r') as f:
                        pid = int(f.read().strip())
                    
                    # 检查进程是否仍在运行
                    if self._is_process_running(pid):
                        # 进程仍在运行
                        return False
                    else:
                        # 进程已结束，删除旧锁文件
                        self.lock_file_path.unlink()
                except (ValueError, IOError):
                    # 锁文件损坏，删除它
                    self.lock_file_path.unlink()
            
            # 创建新的锁文件
            with open(self.lock_file_path, 'w') as f:
                f.write(str(os.getpid()))
            
            self.is_running = True
            atexit.register(self.release)
            return True
            
        except Exception as e:
            print(f"File lock check failed: {e}")
            # 如果无法创建锁文件，假设可以运行
            return True
    
    def _is_process_running(self, pid):
        """
        检查指定 PID 的进程是否在运行
        
        Args:
            pid: 进程 ID
            
        Returns:
            bool: 进程是否在运行
        """
        if self.system == "Windows":
            try:
                import psutil
                return psutil.pid_exists(pid)
            except ImportError:
                # 没有 psutil，使用基本方法
                try:
                    import subprocess
                    result = subprocess.run(
                        ['tasklist', '/FI', f'PID eq {pid}'],
                        capture_output=True,
                        text=True
                    )
                    return str(pid) in result.stdout
                except:
                    return False
        else:
            # Unix/Linux/macOS
            try:
                os.kill(pid, 0)
                return True
            except (OSError, ProcessLookupError):
                return False
    
    def release(self):
        """释放锁"""
        if not self.is_running:
            return
        
        self.is_running = False
        
        if self.system == "Windows" and hasattr(self, 'use_win32') and self.use_win32:
            # 释放 Windows 互斥体
            if hasattr(self, 'mutex') and self.mutex:
                try:
                    import win32api
                    win32api.CloseHandle(self.mutex)
                    self.mutex = None
                except:
                    pass
        
        # 删除锁文件
        if hasattr(self, 'lock_file_path') and self.lock_file_path and self.lock_file_path.exists():
            try:
                self.lock_file_path.unlink()
            except:
                pass
    
    def __del__(self):
        """析构函数，确保释放锁"""
        self.release()


def bring_window_to_front():
    """
    尝试将已存在的应用窗口带到前台
    
    这是一个辅助函数，可以在检测到已有实例时使用
    """
    system = platform.system()
    
    if system == "Windows":
        try:
            import win32gui
            import win32con
            
            # 查找窗口
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if "Baal" in window_title or "巴利" in window_title:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if windows:
                # 将找到的第一个窗口带到前台
                hwnd = windows[0]
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                win32gui.SetForegroundWindow(hwnd)
                return True
        except:
            pass
    
    return False


def check_single_instance(app_name="BaalPetAssistant"):
    """
    便捷函数：检查单实例并处理
    
    Args:
        app_name: 应用名称
        
    Returns:
        SingleInstance: 如果成功获取锁，返回实例管理器；否则返回 None
    """
    instance = SingleInstance(app_name)
    
    if not instance.check():
        # 已有实例在运行
        print("检测到应用程序已在运行！")
        print("Another instance is already running!")
        
        # 在 Windows 上显示消息框
        if platform.system() == "Windows":
            try:
                from baal.desktop_pet.core.windows_utils import (
                    show_already_running_message,
                    bring_existing_window_to_front
                )
                
                # 尝试将已有窗口带到前台
                if bring_existing_window_to_front():
                    print("已将现有窗口激活到前台。")
                    print("Existing window brought to front.")
                else:
                    # 显示消息框
                    show_already_running_message()
            except ImportError:
                # 如果无法导入 Windows 工具，使用基本方法
                if bring_window_to_front():
                    print("已将现有窗口激活到前台。")
                    print("Existing window brought to front.")
                else:
                    print("请检查系统托盘或任务栏。")
                    print("Please check system tray or taskbar.")
        else:
            # 非 Windows 平台
            if bring_window_to_front():
                print("已将现有窗口激活到前台。")
                print("Existing window brought to front.")
            else:
                print("请检查系统托盘或任务栏。")
                print("Please check system tray or taskbar.")
        
        return None
    
    return instance