#!/usr/bin/env python3
"""
测试监督模式（5秒间隔）

用于调试监督模式，每5秒执行一次检查
"""

import sys
import time
import logging
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from baal.desktop_pet.ui.pet_window import PetWindow

# 配置详细日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

def main():
    """主函数"""
    print("\n" + "="*60)
    print("监督模式测试（5秒间隔）")
    print("="*60)
    print("\n说明：")
    print("1. 监督模式将每5秒检查一次用户活动")
    print("2. 如果你处于AFK状态，会跳过检查")
    print("3. 如果你在活动，会进行评估")
    print("4. 观察日志输出了解监督模式的工作情况")
    print("\n⚠️ 注意：需要先配置API密钥和设置监督目标")
    print("="*60 + "\n")
    
    # 创建应用
    app = QApplication(sys.argv)
    app.setApplicationName("Baal Supervision Test")
    app.setQuitOnLastWindowClosed(False)
    
    # 创建桌宠窗口
    pet = PetWindow()
    
    # 确保监督模式已配置
    if not pet.supervision_mode.long_term_goal:
        print("\n📝 设置测试目标...")
        pet.supervision_mode.long_term_goal = "专注工作，提高生产力"
        pet.supervision_mode.short_term_goals = ["完成代码调试", "修复监督模式"]
    
    # 自动启动监督模式
    def start_supervision():
        print(f"\n🚀 启动监督模式 (时间: {datetime.now().strftime('%H:%M:%S')})")
        success = pet.supervision_mode.start_supervision()
        if success:
            print("✅ 监督模式已成功启动")
            print(f"   长期目标: {pet.supervision_mode.long_term_goal}")
            print(f"   短期目标: {pet.supervision_mode.short_term_goals}")
            print(f"   检查间隔: {pet.supervision_mode.check_interval}秒")
        else:
            print("❌ 监督模式启动失败（可能未配置API）")
    
    # 定期输出状态
    check_count = 0
    def print_status():
        nonlocal check_count
        check_count += 1
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] 状态检查 #{check_count}")
        print(f"  监督模式活跃: {pet.supervision_mode.is_active}")
        if pet.supervision_mode.last_check_time:
            elapsed = (datetime.now() - pet.supervision_mode.last_check_time).total_seconds()
            print(f"  距离上次检查: {elapsed:.1f}秒前")
    
    # 监听监督提醒
    def on_reminder(reminder_context):
        print("\n" + "!"*60)
        print("🔔 收到监督提醒！")
        print(f"   时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   消息: {reminder_context.get('message', '无消息')[:100]}...")
        print(f"   偏离等级: {reminder_context.get('deviation_level', '未知')}")
        print("!"*60)
    
    # 连接信号
    pet.supervision_mode.reminder_needed.connect(on_reminder)
    
    # 显示窗口
    pet.show()
    
    # 延迟启动监督模式
    QTimer.singleShot(1000, start_supervision)
    
    # 定期输出状态（每10秒）
    status_timer = QTimer()
    status_timer.timeout.connect(print_status)
    status_timer.start(10000)
    
    # 添加退出提示
    print("\n💡 提示：")
    print("  - 监督模式正在运行，每5秒检查一次")
    print("  - 观察日志了解AFK检测和活动评估")
    print("  - 按 Ctrl+C 退出程序")
    
    # 运行应用
    try:
        sys.exit(app.exec())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
        sys.exit(0)

if __name__ == "__main__":
    main()