#!/usr/bin/env python3
"""
测试增强的监督模式功能
"""

import sys
import time
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt6.QtCore import QTimer

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from baal.desktop_pet.supervision_mode import SupervisionMode
from baal.desktop_pet.ui.supervision_dialog import SupervisionDialog
from baal.desktop_pet.core.config_manager import ConfigManager


class TestWindow(QMainWindow):
    """测试窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("监督模式测试")
        self.setGeometry(100, 100, 600, 500)
        
        # 初始化监督模式
        self.supervision_mode = SupervisionMode()
        self.supervision_mode.reminder_needed.connect(self.on_reminder)
        self.supervision_mode.mode_changed.connect(self.on_mode_changed)
        
        # 创建UI
        self.init_ui()
        
    def init_ui(self):
        """初始化UI"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # 状态显示
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        layout.addWidget(self.status_text)
        
        # 测试按钮
        btn1 = QPushButton("📝 打开监督设置对话框")
        btn1.clicked.connect(self.open_supervision_dialog)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("🔄 快速切换监督模式")
        btn2.clicked.connect(self.toggle_supervision)
        layout.addWidget(btn2)
        
        btn3 = QPushButton("🧪 模拟5分钟检查")
        btn3.clicked.connect(self.simulate_check)
        layout.addWidget(btn3)
        
        btn4 = QPushButton("📊 查看当前状态")
        btn4.clicked.connect(self.show_status)
        layout.addWidget(btn4)
        
        btn5 = QPushButton("💾 测试保存/加载设置")
        btn5.clicked.connect(self.test_save_load)
        layout.addWidget(btn5)
        
        central_widget.setLayout(layout)
        
        # 初始状态
        self.log("监督模式测试已启动")
        self.show_status()
        
    def log(self, message):
        """记录日志"""
        timestamp = time.strftime("%H:%M:%S")
        self.status_text.append(f"[{timestamp}] {message}")
        
    def open_supervision_dialog(self):
        """打开监督设置对话框"""
        dialog = SupervisionDialog(
            self,
            current_goal=self.supervision_mode.long_term_goal,
            current_tasks=self.supervision_mode.short_term_goals
        )
        dialog.supervision_started.connect(self.start_supervision)
        dialog.exec()
        
    def start_supervision(self, long_term_goal, short_term_goals):
        """启动监督"""
        self.log(f"启动监督模式...")
        self.log(f"长期目标: {long_term_goal}")
        self.log(f"短期目标: {', '.join(short_term_goals)}")
        
        success = self.supervision_mode.start_supervision(long_term_goal, short_term_goals)
        if success:
            self.log("✅ 监督模式启动成功")
        else:
            self.log("❌ 监督模式启动失败（可能需要配置API）")
            
    def toggle_supervision(self):
        """切换监督模式"""
        if self.supervision_mode.is_active:
            self.log("停止监督模式...")
            self.supervision_mode.stop_supervision()
        else:
            if self.supervision_mode.long_term_goal:
                self.log("使用已保存的目标重新启动...")
                success = self.supervision_mode.start_supervision()
                if not success:
                    self.log("启动失败，请先配置API")
            else:
                self.log("没有保存的目标，请先设置")
                self.open_supervision_dialog()
                
    def simulate_check(self):
        """模拟检查"""
        if not self.supervision_mode.is_active:
            self.log("监督模式未激活，请先启动")
            return
            
        self.log("模拟5分钟检查...")
        try:
            # 手动触发检查
            self.supervision_mode._check_activity()
            self.log("检查完成")
        except Exception as e:
            self.log(f"检查出错: {e}")
            
    def show_status(self):
        """显示当前状态"""
        status = self.supervision_mode.get_status()
        self.log("=== 当前状态 ===")
        self.log(f"激活状态: {'是' if status['is_active'] else '否'}")
        self.log(f"长期目标: {status.get('long_term_goal', '未设置')}")
        
        short_goals = status.get('short_term_goals', [])
        if short_goals:
            self.log(f"短期目标 ({len(short_goals)}项):")
            for i, goal in enumerate(short_goals, 1):
                self.log(f"  {i}. {goal}")
        else:
            self.log("短期目标: 未设置")
            
        last_check = status.get('last_check')
        if last_check:
            self.log(f"最后检查: {last_check}")
        self.log("================")
        
    def test_save_load(self):
        """测试保存和加载"""
        self.log("测试保存/加载功能...")
        
        # 设置测试数据
        test_long_term = "测试长期目标：提高工作效率"
        test_short_term = ["完成代码审查", "写文档", "修复bug"]
        
        # 更新目标
        self.supervision_mode.update_goals(test_long_term, test_short_term)
        self.log("已保存测试目标")
        
        # 创建新实例加载
        new_instance = SupervisionMode()
        self.log(f"新实例加载的长期目标: {new_instance.long_term_goal}")
        self.log(f"新实例加载的短期目标: {', '.join(new_instance.short_term_goals)}")
        
        if new_instance.long_term_goal == test_long_term:
            self.log("✅ 保存/加载测试通过")
        else:
            self.log("❌ 保存/加载测试失败")
            
    def on_reminder(self, context):
        """处理提醒"""
        self.log("=== 收到监督提醒 ===")
        self.log(f"提醒消息: {context.get('reminder_message', '无')}")
        self.log(f"偏离程度: {context.get('deviation_level', '未知')}")
        self.log("==================")
        
    def on_mode_changed(self, is_active):
        """监督模式状态变更"""
        self.log(f"监督模式状态变更: {'开启' if is_active else '关闭'}")


def main():
    """主函数"""
    app = QApplication(sys.argv)
    
    # 设置应用样式
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()