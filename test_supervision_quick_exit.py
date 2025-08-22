#!/usr/bin/env python3
"""
测试监督模式快速退出功能
Test supervision mode quick exit functionality
"""

import sys
import time
import threading
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from baal.desktop_pet.supervision_mode import SupervisionMode
from baal.desktop_pet.core.config_manager import ConfigManager
from PyQt6.QtCore import QObject, QCoreApplication
from PyQt6.QtWidgets import QApplication

def test_quick_exit():
    """测试监督模式的快速退出"""
    print("=" * 60)
    print("测试监督模式快速退出功能")
    print("=" * 60)
    
    # 创建Qt应用（必须的，因为SupervisionMode使用Qt信号）
    app = QApplication(sys.argv)
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    
    # 设置较短的检查间隔用于测试（10秒）
    supervision.check_interval = 10
    
    # 设置测试目标
    supervision.long_term_goal = "测试目标"
    supervision.short_term_goals = ["子目标1", "子目标2"]
    
    print(f"\n1. 启动监督模式...")
    print(f"   检查间隔: {supervision.check_interval}秒")
    
    # 启动监督模式
    success = supervision.start_supervision()
    if not success:
        print("   ✗ 监督模式启动失败（可能未配置API）")
        return
    
    print("   ✓ 监督模式已启动")
    print(f"   线程状态: {supervision.check_thread.is_alive() if supervision.check_thread else 'None'}")
    
    # 等待一会儿，让监督模式运行
    print("\n2. 等待2秒，让监督模式正常运行...")
    time.sleep(2)
    
    # 模拟在检查活动时停止
    print("\n3. 测试停止监督模式的响应速度...")
    start_time = time.time()
    
    # 停止监督模式
    supervision.stop_supervision()
    
    stop_time = time.time()
    elapsed = stop_time - start_time
    
    print(f"   ✓ stop_supervision() 返回时间: {elapsed:.3f}秒")
    
    if elapsed < 1.0:
        print(f"   ✓ 优秀！UI不会感到卡顿（<1秒）")
    elif elapsed < 2.0:
        print(f"   ⚠ 良好，但仍有轻微延迟（1-2秒）")
    else:
        print(f"   ✗ 太慢！UI会明显卡顿（>{elapsed:.1f}秒）")
    
    # 检查线程状态
    print("\n4. 检查线程清理状态...")
    if supervision.check_thread is None:
        print("   ✓ 线程引用已清理")
    else:
        print("   ✗ 线程引用未清理")
    
    # 等待一下看线程是否真的结束了
    print("\n5. 等待1秒，检查后台线程状态...")
    time.sleep(1)
    
    # 再次测试启动和停止
    print("\n6. 第二次测试（确保可重复使用）...")
    
    print("   启动监督模式...")
    success = supervision.start_supervision()
    if success:
        print("   ✓ 第二次启动成功")
        
        # 立即停止（最坏情况）
        print("   立即停止...")
        start_time = time.time()
        supervision.stop_supervision()
        elapsed = time.time() - start_time
        
        print(f"   ✓ 立即停止耗时: {elapsed:.3f}秒")
        
        if elapsed < 0.5:
            print(f"   ✓ 完美！即使立即停止也不会卡顿")
        else:
            print(f"   ⚠ 立即停止仍有延迟")
    else:
        print("   ✗ 第二次启动失败")
    
    # 测试在数据获取过程中停止
    print("\n7. 测试在数据获取时停止...")
    
    # 设置非常短的检查间隔以触发检查
    supervision.check_interval = 1
    
    print("   启动监督模式（1秒检查间隔）...")
    success = supervision.start_supervision()
    if success:
        print("   ✓ 启动成功")
        print("   等待1.5秒以确保正在检查...")
        time.sleep(1.5)
        
        print("   在检查过程中停止...")
        start_time = time.time()
        supervision.stop_supervision()
        elapsed = time.time() - start_time
        
        print(f"   ✓ 检查中停止耗时: {elapsed:.3f}秒")
        
        if elapsed < 1.0:
            print(f"   ✓ 即使在检查过程中也能快速退出！")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
    
    # 清理
    app.quit()

if __name__ == "__main__":
    test_quick_exit()