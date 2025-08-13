#!/usr/bin/env python3
"""
简单测试监督模式核心功能
"""

import sys
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

from baal.desktop_pet.supervision_mode import SupervisionMode
from baal.desktop_pet.core.config_manager import ConfigManager


def test_supervision():
    """测试监督模式"""
    print("=== 监督模式功能测试 ===\n")
    
    # 创建监督模式实例
    supervision = SupervisionMode()
    
    # 测试1: 设置长期和短期目标
    print("1. 测试目标设置")
    long_term = "完成项目开发，保持高效工作状态"
    short_term = ["完成代码审查", "编写文档", "修复3个bug"]
    
    supervision.update_goals(long_term, short_term)
    print(f"   长期目标: {supervision.long_term_goal}")
    print(f"   短期目标: {supervision.short_term_goals}")
    print("   ✅ 目标设置成功\n")
    
    # 测试2: 保存和加载
    print("2. 测试保存/加载")
    supervision._save_supervision_settings()
    
    # 创建新实例测试加载
    new_supervision = SupervisionMode()
    if new_supervision.long_term_goal == long_term:
        print("   ✅ 保存/加载成功\n")
    else:
        print("   ❌ 保存/加载失败\n")
    
    # 测试3: AFK检测
    print("3. 测试AFK检测")
    try:
        is_afk = supervision._is_user_afk()
        print(f"   当前AFK状态: {'是' if is_afk else '否'}")
        print("   ✅ AFK检测正常\n")
    except Exception as e:
        print(f"   ⚠️ AFK检测异常: {e}\n")
    
    # 测试4: 获取综合统计
    print("4. 测试活动统计获取")
    try:
        stats = supervision._get_comprehensive_activity_stats()
        if stats:
            print(f"   获取到统计数据: {len(stats)} 个时段")
            for key in stats:
                if key != 'timestamp':
                    print(f"   - {key}: {'有数据' if stats[key] else '无数据'}")
            print("   ✅ 统计获取正常\n")
        else:
            print("   ⚠️ 未获取到统计数据\n")
    except Exception as e:
        print(f"   ⚠️ 统计获取异常: {e}\n")
    
    # 测试5: 状态获取
    print("5. 测试状态获取")
    status = supervision.get_status()
    print(f"   激活状态: {status['is_active']}")
    print(f"   长期目标: {status['long_term_goal'][:30]}..." if status['long_term_goal'] else "   长期目标: 无")
    print(f"   短期目标数: {len(status['short_term_goals'])}")
    print("   ✅ 状态获取正常\n")
    
    # 测试6: 启动监督（不实际运行循环）
    print("6. 测试监督启动")
    config_manager = ConfigManager()
    has_api = bool(config_manager.get_config().get('api_key'))
    
    if has_api:
        success = supervision.start_supervision()
        if success:
            print("   ✅ 监督模式可以启动")
            supervision.stop_supervision()
            print("   ✅ 监督模式已停止")
        else:
            print("   ❌ 监督模式启动失败")
    else:
        print("   ⚠️ 未配置API密钥，跳过启动测试")
    
    print("\n=== 测试完成 ===")


if __name__ == '__main__':
    test_supervision()