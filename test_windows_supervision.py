#!/usr/bin/env python3
"""
测试Windows上的监督模式功能
特别是置顶和自动弹出功能
"""

import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt6.QtCore import QTimer, Qt

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from baal.desktop_pet.ui.pet_window import PetWindow
from baal.desktop_pet.supervision_mode import SupervisionMode


class WindowsTestWindow(QMainWindow):
    """Windows测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Windows监督模式测试")
        self.setGeometry(100, 100, 500, 600)
        
        # 创建UI
        self.init_ui()
        
        # 创建宠物窗口
        self.pet_window = None
        
    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 状态显示
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(300)
        layout.addWidget(self.status_text)
        
        # 测试按钮
        btn1 = QPushButton("🚀 启动宠物窗口")
        btn1.clicked.connect(self.launch_pet_window)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("🔧 测试置顶功能")
        btn2.clicked.connect(self.test_always_on_top)
        layout.addWidget(btn2)
        
        btn3 = QPushButton("📉 最小化宠物窗口")
        btn3.clicked.connect(self.minimize_pet)
        layout.addWidget(btn3)
        
        btn4 = QPushButton("🔔 模拟监督提醒（测试自动弹出）")
        btn4.clicked.connect(self.simulate_reminder)
        layout.addWidget(btn4)
        
        btn5 = QPushButton("🎯 测试SetForegroundWindow")
        btn5.clicked.connect(self.test_foreground)
        layout.addWidget(btn5)
        
        btn6 = QPushButton("📊 检查窗口状态")
        btn6.clicked.connect(self.check_window_state)
        layout.addWidget(btn6)
        
        central_widget.setLayout(layout)
        
        # 初始化日志
        self.log("Windows监督模式测试工具已启动")
        self.log(f"系统平台: {sys.platform}")
        
    def log(self, message):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        
    def launch_pet_window(self):
        """启动宠物窗口"""
        if self.pet_window is None:
            self.log("启动宠物窗口...")
            try:
                self.pet_window = PetWindow()
                self.pet_window.show()
                self.log("✅ 宠物窗口已启动")
                
                # 检查置顶设置
                config = self.pet_window.config_manager.get_config()
                is_topmost = config.get('always_on_top', True)
                self.log(f"置顶设置: {'开启' if is_topmost else '关闭'}")
            except Exception as e:
                self.log(f"❌ 启动失败: {e}")
        else:
            self.log("宠物窗口已存在")
            
    def test_always_on_top(self):
        """测试置顶功能"""
        if not self.pet_window:
            self.log("请先启动宠物窗口")
            return
            
        self.log("测试置顶功能...")
        
        # 获取当前置顶状态
        flags = self.pet_window.windowFlags()
        is_topmost = bool(flags & Qt.WindowType.WindowStaysOnTopHint)
        self.log(f"当前置顶状态: {is_topmost}")
        
        # 切换置顶状态
        self.pet_window._toggle_always_on_top(not is_topmost)
        
        # 检查新状态
        QTimer.singleShot(500, self.check_topmost_after_toggle)
        
    def check_topmost_after_toggle(self):
        """切换后检查置顶状态"""
        flags = self.pet_window.windowFlags()
        is_topmost = bool(flags & Qt.WindowType.WindowStaysOnTopHint)
        self.log(f"切换后置顶状态: {is_topmost}")
        
        # Windows特定检查
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = int(self.pet_window.winId())
                # 使用GetWindowLong检查扩展样式
                GWL_EXSTYLE = -20
                WS_EX_TOPMOST = 0x00000008
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                is_really_topmost = bool(ex_style & WS_EX_TOPMOST)
                self.log(f"Windows API检查: 置顶={is_really_topmost}")
            except Exception as e:
                self.log(f"Windows API检查失败: {e}")
                
    def minimize_pet(self):
        """最小化宠物窗口"""
        if not self.pet_window:
            self.log("请先启动宠物窗口")
            return
            
        self.log("最小化宠物窗口...")
        self.pet_window.showMinimized()
        self.log("窗口已最小化")
        
    def simulate_reminder(self):
        """模拟监督提醒"""
        if not self.pet_window:
            self.log("请先启动宠物窗口")
            return
            
        self.log("模拟监督提醒...")
        
        # 构造测试提醒上下文
        test_context = {
            'type': 'supervision_reminder',
            'long_term_goal': '测试长期目标',
            'short_term_goals': ['测试任务1', '测试任务2'],
            'reminder_message': '这是一条测试提醒消息！请检查窗口是否正确弹出。',
            'deviation_level': '中度',
            'timestamp': time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # 触发提醒
        self.pet_window._on_supervision_reminder(test_context)
        self.log("✅ 提醒已触发")
        
        # 检查窗口状态
        QTimer.singleShot(500, self.check_after_reminder)
        
    def check_after_reminder(self):
        """提醒后检查窗口状态"""
        is_visible = self.pet_window.isVisible()
        is_minimized = self.pet_window.isMinimized()
        is_active = self.pet_window.isActiveWindow()
        
        self.log(f"提醒后状态:")
        self.log(f"  - 可见: {is_visible}")
        self.log(f"  - 最小化: {is_minimized}")
        self.log(f"  - 激活: {is_active}")
        
        if self.pet_window.chat_bubble:
            bubble_visible = self.pet_window.chat_bubble.isVisible()
            self.log(f"  - 气泡可见: {bubble_visible}")
            
    def test_foreground(self):
        """测试SetForegroundWindow"""
        if not self.pet_window:
            self.log("请先启动宠物窗口")
            return
            
        if sys.platform != "win32":
            self.log("此功能仅在Windows上可用")
            return
            
        self.log("测试SetForegroundWindow...")
        
        try:
            import ctypes
            hwnd = int(self.pet_window.winId())
            
            # 尝试将窗口带到前台
            result = ctypes.windll.user32.SetForegroundWindow(hwnd)
            self.log(f"SetForegroundWindow返回: {result}")
            
            # 使用其他方法确保窗口激活
            ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            ctypes.windll.user32.SetForegroundWindow(hwnd)
            ctypes.windll.user32.SetFocus(hwnd)
            
            self.log("✅ 前台设置完成")
            
        except Exception as e:
            self.log(f"❌ 设置失败: {e}")
            
    def check_window_state(self):
        """检查窗口状态"""
        if not self.pet_window:
            self.log("请先启动宠物窗口")
            return
            
        self.log("=== 窗口状态检查 ===")
        self.log(f"可见: {self.pet_window.isVisible()}")
        self.log(f"最小化: {self.pet_window.isMinimized()}")
        self.log(f"最大化: {self.pet_window.isMaximized()}")
        self.log(f"全屏: {self.pet_window.isFullScreen()}")
        self.log(f"激活: {self.pet_window.isActiveWindow()}")
        
        # 检查窗口标志
        flags = self.pet_window.windowFlags()
        self.log(f"置顶标志: {bool(flags & Qt.WindowType.WindowStaysOnTopHint)}")
        self.log(f"无边框: {bool(flags & Qt.WindowType.FramelessWindowHint)}")
        self.log(f"工具窗口: {bool(flags & Qt.WindowType.Tool)}")
        
        # Windows特定信息
        if sys.platform == "win32":
            try:
                import ctypes
                hwnd = int(self.pet_window.winId())
                self.log(f"窗口句柄: {hwnd}")
                
                # 获取窗口样式
                GWL_STYLE = -16
                GWL_EXSTYLE = -20
                style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_STYLE)
                ex_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                
                WS_EX_TOPMOST = 0x00000008
                WS_EX_TOOLWINDOW = 0x00000080
                
                self.log(f"Windows样式: 0x{style:08X}")
                self.log(f"扩展样式: 0x{ex_style:08X}")
                self.log(f"  - TOPMOST: {bool(ex_style & WS_EX_TOPMOST)}")
                self.log(f"  - TOOLWINDOW: {bool(ex_style & WS_EX_TOOLWINDOW)}")
                
            except Exception as e:
                self.log(f"Windows API检查失败: {e}")
                
        self.log("==================")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = WindowsTestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()