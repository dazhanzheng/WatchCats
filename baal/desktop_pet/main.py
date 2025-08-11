"""
Baal 桌宠主程序

直接运行此文件启动桌宠
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from baal.desktop_pet.ui import PetWindow


def main():
    """主函数"""
    # PyQt6 默认启用高DPI支持，不需要手动设置
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Baal Desktop Pet")
    app.setQuitOnLastWindowClosed(False)  # 关闭窗口时不退出应用
    
    # 创建桌宠窗口（但不立即显示）
    pet = PetWindow()
    
    # 检查是否需要启动时显示窗口（可通过配置控制）
    config = pet.config_manager.get_config()
    start_minimized = config.get('start_minimized', False)
    
    if not start_minimized:
        pet.show()
    else:
        # 启动时仅显示托盘图标
        if hasattr(pet, 'tray_icon') and pet.tray_icon:
            try:
                pet.tray_icon.showMessage(
                    "巴利监管者",
                    "本座已在暗中监视。点击托盘图标召唤本座。",
                    pet.tray_icon.MessageIcon.Information,
                    3000
                )
            except Exception as e:
                print(f"[WARNING] 无法显示托盘消息: {e}")
    
    # 设置应用退出时的处理
    app.aboutToQuit.connect(pet._quit_application)
    
    # 运行应用
    sys.exit(app.exec())


if __name__ == "__main__":
    main() 