"""
Windows 平台特定的工具函数
"""

import sys
import platform


def show_message_box(title, message, icon_type="info"):
    """
    显示 Windows 消息框
    
    Args:
        title: 消息框标题
        message: 消息内容
        icon_type: 图标类型 ("info", "warning", "error")
    """
    if platform.system() != "Windows":
        print(f"{title}: {message}")
        return
    
    try:
        import ctypes
        from ctypes import wintypes
        
        # 消息框图标类型
        MB_ICONINFORMATION = 0x40
        MB_ICONWARNING = 0x30
        MB_ICONERROR = 0x10
        
        # 选择图标
        icon = MB_ICONINFORMATION
        if icon_type == "warning":
            icon = MB_ICONWARNING
        elif icon_type == "error":
            icon = MB_ICONERROR
        
        # 显示消息框
        ctypes.windll.user32.MessageBoxW(
            0,
            message,
            title,
            icon
        )
    except Exception as e:
        # 如果无法显示消息框，回退到控制台输出
        print(f"{title}: {message}")
        print(f"(Could not show message box: {e})")


def show_already_running_message():
    """
    显示"已在运行"的消息
    """
    title = "Baal宠物助手 / Baal Pet Assistant"
    message = (
        "程序已在运行！\n"
        "Application is already running!\n\n"
        "请检查系统托盘或任务栏。\n"
        "Please check the system tray or taskbar.\n\n"
        "如果看不到窗口，可以右键系统托盘图标选择"显示"。\n"
        "If you can't see the window, right-click the tray icon and select 'Show'."
    )
    
    show_message_box(title, message, "info")


def bring_existing_window_to_front():
    """
    将已存在的应用窗口带到前台
    
    Returns:
        bool: 是否成功找到并激活窗口
    """
    if platform.system() != "Windows":
        return False
    
    try:
        import win32gui
        import win32con
        
        # 查找窗口
        def enum_windows_callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                window_title = win32gui.GetWindowText(hwnd)
                class_name = win32gui.GetClassName(hwnd)
                
                # 查找包含特定标题或类名的窗口
                if ("Baal" in window_title or "巴利" in window_title or 
                    "BaalPet" in class_name or "PetWindow" in class_name):
                    windows.append(hwnd)
            return True
        
        windows = []
        win32gui.EnumWindows(enum_windows_callback, windows)
        
        if windows:
            # 将找到的第一个窗口带到前台
            hwnd = windows[0]
            
            # 如果窗口最小化，恢复它
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            
            # 激活并带到前台
            win32gui.SetForegroundWindow(hwnd)
            win32gui.BringWindowToTop(hwnd)
            
            # 闪烁窗口以引起注意
            win32gui.FlashWindow(hwnd, True)
            
            return True
            
    except ImportError:
        # 没有 pywin32
        pass
    except Exception as e:
        print(f"Could not bring window to front: {e}")
    
    return False