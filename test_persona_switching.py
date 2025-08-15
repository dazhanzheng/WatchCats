#!/usr/bin/env python3
"""
测试人设切换功能

验证切换人设时所有预设对话都正确更新
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baal.desktop_pet.core.persona_manager import PersonaManager, PersonaLevel
from baal.desktop_pet.core.preset_dialogues import PresetDialogues
from baal.desktop_pet.core.preset_responses import PresetResponseManager


def test_persona_switching():
    """测试人设切换"""
    print("=" * 60)
    print("测试人设切换功能")
    print("=" * 60)
    
    # 创建人设管理器
    persona_manager = PersonaManager()
    
    # 测试场景列表
    test_scenarios = [
        ("welcome", "system"),
        ("left_click_warning", "system"),
        ("api_configured", "system"),
        ("supervision_start", "system"),
        ("严重", "supervision"),
        ("中度", "supervision"),
        ("轻微", "supervision"),
    ]
    
    # 测试每个人设
    for persona_level in [PersonaLevel.STRICT_MASTER, PersonaLevel.SARCASTIC_BUTLER, PersonaLevel.GENTLE_COMPANION]:
        print(f"\n切换到人设: {persona_level.name}")
        print("-" * 40)
        
        # 切换人设
        persona_manager.set_persona_level(persona_level)
        
        # 获取当前人设信息
        persona_info = persona_manager.get_current_persona_info()
        print(f"当前人设: {persona_info['name']}")
        print(f"描述: {persona_info['description'][:50]}...")
        
        # 测试各种场景的反应
        print("\n场景反应:")
        for scenario, category in test_scenarios:
            if category == "system":
                # 使用 PresetResponseManager（兼容接口）
                response = PresetResponseManager.get_response(persona_manager.current_level, scenario)
            else:
                # 直接使用 PresetDialogues
                response = PresetDialogues.get_dialogue(persona_manager.current_level, category, scenario)
            
            print(f"  {scenario:20} -> {response}")
        
        # 测试错误消息
        print("\n错误消息:")
        for error_type in ["system_error", "chat_error", "api_error", "general_error"]:
            error_msg = PresetDialogues.get_error_message(persona_manager.current_level, error_type)
            print(f"  {error_type:15} -> {error_msg}")


def test_direct_dialogue_access():
    """测试直接访问对话配置"""
    print("\n" + "=" * 60)
    print("测试直接访问对话配置")
    print("=" * 60)
    
    for persona_level in PersonaLevel:
        if persona_level == PersonaLevel.CUSTOM:
            continue  # 跳过自定义人设
        
        print(f"\n{persona_level.name}:")
        
        # 测试系统反应
        welcome = PresetDialogues.get_dialogue(persona_level, "system", "welcome")
        print(f"  欢迎消息: {welcome}")
        
        # 测试监督提醒
        severe_reminder = PresetDialogues.get_dialogue(persona_level, "supervision", "严重")
        print(f"  严重提醒: {severe_reminder}")
        
        # 测试默认反应
        default = PresetDialogues.get_dialogue(persona_level, "default", "default")
        print(f"  默认反应: {default}")
        
        # 测试错误消息
        error = PresetDialogues.get_error_message(persona_level, "system_error")
        print(f"  系统错误: {error}")


def test_consistency():
    """测试一致性：多次调用同一场景应该有变化（随机选择）"""
    print("\n" + "=" * 60)
    print("测试随机性和多样性")
    print("=" * 60)
    
    persona_level = PersonaLevel.STRICT_MASTER
    scenario = "welcome"
    
    print(f"\n人设: {persona_level.name}")
    print(f"场景: {scenario}")
    print("连续10次调用结果:")
    
    responses = []
    for i in range(10):
        response = PresetResponseManager.get_response(persona_level, scenario)
        responses.append(response)
        print(f"  {i+1}. {response}")
    
    unique_responses = set(responses)
    print(f"\n唯一反应数: {len(unique_responses)} / 3")
    
    if len(unique_responses) > 1:
        print("✓ 随机选择功能正常")
    else:
        print("⚠ 可能存在问题：10次调用都返回相同结果")


def test_fallback():
    """测试后备机制：请求不存在的场景"""
    print("\n" + "=" * 60)
    print("测试后备机制")
    print("=" * 60)
    
    for persona_level in [PersonaLevel.STRICT_MASTER, PersonaLevel.SARCASTIC_BUTLER, PersonaLevel.GENTLE_COMPANION]:
        print(f"\n{persona_level.name}:")
        
        # 测试不存在的系统场景
        response = PresetDialogues.get_dialogue(persona_level, "system", "non_existent_scenario")
        print(f"  不存在的系统场景 -> {response}")
        
        # 测试不存在的监督级别
        response = PresetDialogues.get_dialogue(persona_level, "supervision", "超级严重")
        print(f"  不存在的监督级别 -> {response}")
        
        # 测试不存在的类别
        response = PresetDialogues.get_dialogue(persona_level, "unknown_category", "test")
        print(f"  不存在的类别 -> {response}")


def main():
    """主测试函数"""
    try:
        # 运行所有测试
        test_persona_switching()
        test_direct_dialogue_access()
        test_consistency()
        test_fallback()
        
        print("\n" + "=" * 60)
        print("✓ 所有测试完成")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())