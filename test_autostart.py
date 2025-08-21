#!/usr/bin/env python3
"""
测试开机自启动功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from baal.desktop_pet.core.autostart_manager import AutostartManager


def test_autostart():
    """测试开机自启动功能"""
    
    print("=" * 60)
    print("测试开机自启动功能")
    print("=" * 60)
    
    manager = AutostartManager()
    
    print(f"\n平台: {sys.platform}")
    print(f"应用名称: {manager.app_name}")
    print(f"应用路径: {manager.app_path}")
    
    # 检查当前状态
    print("\n1. 检查当前状态...")
    is_enabled = manager.is_autostart_enabled()
    print(f"   开机自启动已启用: {is_enabled}")
    
    if sys.platform == "win32":
        # 测试启用
        print("\n2. 测试启用开机自启动...")
        success = manager.enable_autostart()
        print(f"   启用结果: {success}")
        
        # 再次检查
        is_enabled = manager.is_autostart_enabled()
        print(f"   当前状态: {is_enabled}")
        
        # 测试禁用
        print("\n3. 测试禁用开机自启动...")
        success = manager.disable_autostart()
        print(f"   禁用结果: {success}")
        
        # 最终检查
        is_enabled = manager.is_autostart_enabled()
        print(f"   最终状态: {is_enabled}")
    else:
        print("\n⚠️ 当前平台不支持开机自启动功能")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    test_autostart()