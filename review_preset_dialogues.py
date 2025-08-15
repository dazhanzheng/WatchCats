#!/usr/bin/env python3
"""
预设对话审查工具

用于查看和审查所有人设的预设对话内容
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baal.desktop_pet.core.persona_manager import PersonaLevel
from baal.desktop_pet.core.preset_dialogues import PresetDialogues
import json


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def print_subsection(title: str):
    """打印子节标题"""
    print(f"\n--- {title} ---\n")


def review_persona_dialogues(persona_level: PersonaLevel, persona_name: str):
    """审查单个人设的所有对话"""
    print_section(f"{persona_name} ({persona_level.name})")
    
    # 获取该人设的所有对话
    all_dialogues = PresetDialogues.get_all_dialogues_for_persona(persona_level)
    
    # 1. 系统反应对话
    if "system_responses" in all_dialogues:
        print_subsection("系统反应对话")
        for scenario, responses in all_dialogues["system_responses"].items():
            if scenario == "error_messages":
                print(f"\n  错误消息:")
                for error_type, message in responses.items():
                    print(f"    {error_type}: {message}")
            else:
                print(f"\n  {scenario}:")
                if isinstance(responses, list):
                    for i, response in enumerate(responses, 1):
                        print(f"    {i}. {response}")
                else:
                    print(f"    {responses}")
    
    # 2. 监督模式提醒
    if "supervision_reminders" in all_dialogues:
        print_subsection("监督模式提醒")
        for level, reminders in all_dialogues["supervision_reminders"].items():
            print(f"\n  偏离程度 - {level}:")
            for i, reminder in enumerate(reminders, 1):
                print(f"    {i}. {reminder}")
    
    # 3. 默认反应
    if "default_responses" in all_dialogues:
        print_subsection("默认反应")
        for scenario, response in all_dialogues["default_responses"].items():
            print(f"  {scenario}: {response}")


def export_to_json(filename: str = "preset_dialogues_export.json"):
    """导出所有对话到JSON文件（便于外部审查）"""
    export_data = {}
    
    for persona_level in PersonaLevel:
        persona_data = PresetDialogues.get_all_dialogues_for_persona(persona_level)
        export_data[persona_level.name] = persona_data
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n所有对话已导出到: {filename}")


def count_dialogues():
    """统计对话数量"""
    print_section("对话统计")
    
    total_count = 0
    for persona_level in PersonaLevel:
        persona_count = 0
        all_dialogues = PresetDialogues.get_all_dialogues_for_persona(persona_level)
        
        # 统计系统反应
        if "system_responses" in all_dialogues:
            for scenario, responses in all_dialogues["system_responses"].items():
                if isinstance(responses, list):
                    persona_count += len(responses)
                elif isinstance(responses, dict):  # error_messages
                    persona_count += len(responses)
        
        # 统计监督提醒
        if "supervision_reminders" in all_dialogues:
            for level, reminders in all_dialogues["supervision_reminders"].items():
                persona_count += len(reminders)
        
        # 统计默认反应
        if "default_responses" in all_dialogues:
            persona_count += len(all_dialogues["default_responses"])
        
        print(f"{persona_level.name}: {persona_count} 条对话")
        total_count += persona_count
    
    print(f"\n总计: {total_count} 条预设对话")


def main():
    """主函数"""
    print("=" * 60)
    print("  Baal 预设对话审查工具")
    print("=" * 60)
    
    # 显示菜单
    print("\n请选择操作:")
    print("1. 查看所有人设的对话")
    print("2. 查看特定人设的对话")
    print("3. 统计对话数量")
    print("4. 导出到JSON文件")
    print("5. 退出")
    
    choice = input("\n请输入选项 (1-5): ").strip()
    
    if choice == "1":
        # 查看所有人设
        for persona_level in PersonaLevel:
            persona_names = {
                PersonaLevel.STRICT_MASTER: "严厉主人",
                PersonaLevel.SARCASTIC_BUTLER: "毒舌管家",
                PersonaLevel.GENTLE_COMPANION: "温柔伴侣"
            }
            review_persona_dialogues(persona_level, persona_names[persona_level])
    
    elif choice == "2":
        # 查看特定人设
        print("\n选择人设:")
        print("1. 严厉主人 (STRICT_MASTER)")
        print("2. 毒舌管家 (SARCASTIC_BUTLER)")
        print("3. 温柔伴侣 (GENTLE_COMPANION)")
        
        persona_choice = input("\n请输入选项 (1-3): ").strip()
        persona_map = {
            "1": (PersonaLevel.STRICT_MASTER, "严厉主人"),
            "2": (PersonaLevel.SARCASTIC_BUTLER, "毒舌管家"),
            "3": (PersonaLevel.GENTLE_COMPANION, "温柔伴侣")
        }
        
        if persona_choice in persona_map:
            persona_level, persona_name = persona_map[persona_choice]
            review_persona_dialogues(persona_level, persona_name)
        else:
            print("无效选项")
    
    elif choice == "3":
        # 统计数量
        count_dialogues()
    
    elif choice == "4":
        # 导出JSON
        export_to_json()
    
    elif choice == "5":
        print("退出")
        return
    
    else:
        print("无效选项")
    
    # 询问是否继续
    if input("\n按Enter键继续..."):
        pass
    main()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已退出")
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()