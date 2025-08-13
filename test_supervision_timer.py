#!/usr/bin/env python3
"""
测试监督模式的定时提醒功能
可以通过环境变量设置更短的检查间隔进行测试
"""

import sys
import os
import time
from pathlib import Path
from datetime import datetime

# 设置较短的检查间隔用于测试（30秒）
os.environ['SUPERVISION_CHECK_INTERVAL'] = '30'

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from baal.desktop_pet.supervision_mode import SupervisionMode
from baal.desktop_pet.core.config_manager import ConfigManager


def test_supervision_timer():
    """测试监督模式定时器"""
    print("=== 监督模式定时器测试 ===")
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("检查间隔设置为: 30秒")
    print("-" * 50)
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    
    # 设置测试目标
    long_term = "测试长期目标：保持专注工作"
    short_term = ["测试任务1：写代码", "测试任务2：测试功能"]
    
    print("\n1. 设置监督目标")
    supervision.update_goals(long_term, short_term)
    print(f"   长期目标: {supervision.long_term_goal}")
    print(f"   短期目标: {supervision.short_term_goals}")
    
    # 连接信号以捕获提醒
    reminder_count = [0]  # 使用列表以便在闭包中修改
    
    def on_reminder(context):
        reminder_count[0] += 1
        print(f"\n🔔 收到第 {reminder_count[0]} 次提醒!")
        print(f"   时间: {datetime.now().strftime('%H:%M:%S')}")
        print(f"   消息: {context.get('reminder_message', '无消息')}")
        print(f"   偏离程度: {context.get('deviation_level', '未知')}")
    
    supervision.reminder_needed.connect(on_reminder)
    
    # 检查API配置
    config_manager = ConfigManager()
    has_api = bool(config_manager.get_config().get('api_key'))
    
    if not has_api:
        print("\n⚠️ 未配置API密钥，监督模式无法正常工作")
        print("请先配置API密钥后再运行测试")
        return
    
    print("\n2. 启动监督模式")
    success = supervision.start_supervision()
    
    if not success:
        print("   ❌ 监督模式启动失败")
        return
    
    print("   ✅ 监督模式已启动")
    print("\n3. 等待定时检查...")
    print("   首次检查应该立即执行")
    print("   之后每30秒检查一次")
    print("   按 Ctrl+C 停止测试\n")
    
    # 运行测试
    try:
        start_time = time.time()
        last_log_time = time.time()
        
        while True:
            current_time = time.time()
            elapsed = int(current_time - start_time)
            
            # 每10秒打印一次状态
            if current_time - last_log_time >= 10:
                print(f"   [{elapsed}秒] 等待中... (已收到 {reminder_count[0]} 次提醒)")
                last_log_time = current_time
            
            time.sleep(1)
            
            # 测试2分钟后自动停止
            if elapsed > 120:
                print("\n测试时间已到，停止监督模式")
                break
                
    except KeyboardInterrupt:
        print("\n\n用户中断测试")
    
    # 停止监督模式
    supervision.stop_supervision()
    print("\n4. 测试结果")
    print(f"   总共收到提醒: {reminder_count[0]} 次")
    print(f"   测试持续时间: {int(time.time() - start_time)} 秒")
    
    if reminder_count[0] > 0:
        print("   ✅ 定时提醒功能正常")
    else:
        print("   ⚠️ 未收到提醒，可能的原因：")
        print("      - ActivityWatch未运行")
        print("      - 用户处于AFK状态")
        print("      - LLM判断活动符合目标")
        print("      - API调用失败")
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_supervision_timer()