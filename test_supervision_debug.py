#!/usr/bin/env python3
"""
调试监督模式问题
"""

import sys
import os
import time
import threading
from pathlib import Path
from datetime import datetime

# 设置更短的检查间隔用于测试（10秒）
os.environ['SUPERVISION_CHECK_INTERVAL'] = '10'

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from baal.desktop_pet.supervision_mode import SupervisionMode


def test_thread_status():
    """测试线程状态"""
    print("=== 监督模式线程调试 ===\n")
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    
    # 设置测试目标
    supervision.long_term_goal = "测试目标"
    supervision.short_term_goals = ["任务1"]
    
    print("1. 启动前的线程状态")
    print(f"   线程对象: {supervision.check_thread}")
    print(f"   监督激活: {supervision.is_active}")
    
    # 启动监督
    print("\n2. 启动监督模式")
    success = supervision.start_supervision()
    print(f"   启动结果: {success}")
    
    # 检查线程状态
    print("\n3. 启动后的线程状态")
    print(f"   线程对象: {supervision.check_thread}")
    if supervision.check_thread:
        print(f"   线程存活: {supervision.check_thread.is_alive()}")
        print(f"   线程守护: {supervision.check_thread.daemon}")
        print(f"   线程名称: {supervision.check_thread.name}")
    print(f"   监督激活: {supervision.is_active}")
    
    # 列出所有活动线程
    print("\n4. 当前所有活动线程")
    for thread in threading.enumerate():
        print(f"   - {thread.name}: {'守护' if thread.daemon else '非守护'}")
    
    # 等待一段时间观察
    print("\n5. 等待20秒观察输出...")
    for i in range(20):
        time.sleep(1)
        print(f"   [{i+1}/20秒]", end="\r")
    
    print("\n\n6. 停止监督模式")
    supervision.stop_supervision()
    
    # 再次检查线程
    time.sleep(2)
    print("\n7. 停止后的线程状态")
    if supervision.check_thread:
        print(f"   线程存活: {supervision.check_thread.is_alive()}")
    print(f"   监督激活: {supervision.is_active}")
    
    print("\n=== 调试完成 ===")


def test_direct_check():
    """直接测试检查功能"""
    print("=== 直接测试检查功能 ===\n")
    
    supervision = SupervisionMode()
    supervision.long_term_goal = "保持专注"
    supervision.short_term_goals = ["写代码"]
    
    print("直接调用 _check_activity()...")
    try:
        supervision._check_activity()
        print("检查完成")
    except Exception as e:
        print(f"检查失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    print("选择测试模式:")
    print("1. 测试线程状态")
    print("2. 直接测试检查功能")
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        test_thread_status()
    elif choice == "2":
        test_direct_check()
    else:
        print("无效选择")