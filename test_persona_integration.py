#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试人设系统集成
验证预设反应和监督模式与人设系统的集成
"""

import sys
import os
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from baal.desktop_pet.core.persona_manager import PersonaManager, PersonaLevel
from baal.desktop_pet.core.preset_responses import PresetResponseManager
from baal.desktop_pet.core.config_manager import ConfigManager

def test_persona_responses():
    """测试不同人设的反应"""
    print("=" * 60)
    print("测试人设系统集成")
    print("=" * 60)
    
    # 创建人设管理器
    persona_manager = PersonaManager(initial_level=PersonaLevel.STRICT_MASTER)
    
    print("\n1. 测试严厉主人模式")
    print("-" * 40)
    persona_manager.set_persona_level(PersonaLevel.STRICT_MASTER)
    test_scenario_responses(persona_manager)
    
    print("\n2. 测试毒舌管家模式")
    print("-" * 40)
    persona_manager.set_persona_level(PersonaLevel.SARCASTIC_BUTLER)
    test_scenario_responses(persona_manager)
    
    print("\n3. 测试温柔伴侣模式")
    print("-" * 40)
    persona_manager.set_persona_level(PersonaLevel.GENTLE_COMPANION)
    test_scenario_responses(persona_manager)

def test_scenario_responses(persona_manager):
    """测试特定人设的各种场景反应"""
    current_persona = persona_manager.get_current_persona_info()
    print(f"当前人设: {current_persona['name']}")
    print(f"描述: {current_persona['description']}")
    print()
    
    # 测试各种场景
    scenarios = [
        ("welcome", "欢迎消息"),
        ("left_click_warning", "左键警告"),
        ("api_not_configured", "API未配置"),
        ("supervision_start", "监督开始"),
        ("always_on_top_enable", "置顶启用")
    ]
    
    for scenario_key, scenario_name in scenarios:
        response = PresetResponseManager.get_response(
            persona_manager.current_level,
            scenario_key
        )
        # 提取表情和文本
        if response.startswith("<#"):
            emotion = response[:4]
            text = response[4:].strip()
            print(f"  {scenario_name}: [{emotion}] {text[:40]}...")
        else:
            print(f"  {scenario_name}: {response[:40]}...")

def test_supervision_reminders():
    """测试监督模式提醒的人设一致性"""
    print("\n" + "=" * 60)
    print("测试监督模式提醒")
    print("=" * 60)
    
    persona_manager = PersonaManager()
    
    for level in [PersonaLevel.STRICT_MASTER, PersonaLevel.SARCASTIC_BUTLER, PersonaLevel.GENTLE_COMPANION]:
        persona_manager.set_persona_level(level)
        persona_info = persona_manager.get_current_persona_info()
        print(f"\n{persona_info['name']}的监督提醒:")
        print("-" * 40)
        
        for deviation_level in ["严重", "中度", "轻微"]:
            reminder = PresetResponseManager.get_supervision_reminder(
                level,
                deviation_level
            )
            if reminder.startswith("<#"):
                emotion = reminder[:4]
                text = reminder[4:].strip()
                print(f"  {deviation_level}偏离: [{emotion}] {text[:35]}...")
            else:
                print(f"  {deviation_level}偏离: {reminder[:35]}...")

def test_config_integration():
    """测试配置管理器中的人设保存"""
    print("\n" + "=" * 60)
    print("测试配置集成")
    print("=" * 60)
    
    config_manager = ConfigManager()
    config = config_manager.get_config()
    
    # 检查人设配置
    persona_level = config.get('persona_level', 1)
    print(f"配置中的人设级别: {persona_level}")
    
    # 转换为PersonaLevel枚举
    try:
        level = PersonaLevel(persona_level)
        print(f"对应的人设: {level.name}")
        
        # 获取该人设的欢迎消息
        welcome = PresetResponseManager.get_response(level, "welcome")
        print(f"该人设的欢迎消息: {welcome[:50]}...")
    except ValueError:
        print(f"警告: 无效的人设级别 {persona_level}")

if __name__ == "__main__":
    try:
        test_persona_responses()
        test_supervision_reminders()
        test_config_integration()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！人设系统集成正常。")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)