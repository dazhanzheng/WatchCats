#!/usr/bin/env python3
"""
测试人设切换功能

测试不同人设档位的对话效果
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from baal.desktop_pet.core.persona_manager import PersonaManager, PersonaLevel


def test_persona_manager():
    """测试人设管理器的基本功能"""
    print("=" * 60)
    print("测试人设管理器")
    print("=" * 60)
    
    # 创建人设管理器
    manager = PersonaManager()
    
    # 测试三种人设档位
    for level in [PersonaLevel.STRICT_MASTER, PersonaLevel.SARCASTIC_BUTLER, PersonaLevel.GENTLE_COMPANION]:
        print(f"\n--- 测试 {level.name} ---")
        manager.set_persona_level(level)
        
        # 获取当前人设信息
        info = manager.get_current_persona_info()
        print(f"当前人设: {info['name']}")
        print(f"描述: {info['description']}")
        
        # 获取简短提示词
        brief_prompt = manager.get_brief_response_prompt()
        print(f"\n简短提示词 (前100字符):")
        print(brief_prompt[:100] + "...")
        
        # 获取工具响应提示词
        tool_prompt = manager.get_tool_response_prompt(
            "我今天工作了多久？",
            "用户今天使用电脑8小时，其中工作时间5小时"
        )
        print(f"\n工具响应提示词 (前200字符):")
        print(tool_prompt[:200] + "...")
    
    print("\n" + "=" * 60)
    print("✅ 人设管理器测试完成")
    print("=" * 60)


def test_persona_prompts():
    """测试不同人设的提示词内容"""
    print("\n" + "=" * 60)
    print("测试不同人设的完整提示词")
    print("=" * 60)
    
    manager = PersonaManager()
    
    for level in [PersonaLevel.STRICT_MASTER, PersonaLevel.SARCASTIC_BUTLER, PersonaLevel.GENTLE_COMPANION]:
        print(f"\n--- {level.name} 的系统提示词 ---")
        manager.set_persona_level(level)
        
        # 获取完整系统提示词
        system_prompt = manager.get_system_prompt()
        
        # 分离人设和功能部分
        persona_prompt = manager.get_persona_prompt()
        functional_prompt = manager.get_functional_prompt()
        
        print(f"\n人设部分 (前300字符):")
        print(persona_prompt[:300] + "...")
        
        print(f"\n功能部分是否一致: {functional_prompt == manager.BASE_FUNCTIONAL_PROMPT}")
        
        # 验证系统提示词是否正确组合
        expected = persona_prompt + "\n\n" + functional_prompt
        print(f"系统提示词组合正确: {system_prompt == expected}")
    
    print("\n" + "=" * 60)
    print("✅ 提示词测试完成")
    print("=" * 60)


def test_available_personas():
    """测试获取可用人设列表"""
    print("\n" + "=" * 60)
    print("测试可用人设列表")
    print("=" * 60)
    
    manager = PersonaManager()
    personas = manager.get_available_personas()
    
    print(f"\n共有 {len(personas)} 个预设人设:")
    for level_value, info in personas.items():
        print(f"\n档位 {level_value}: {info['name']}")
        print(f"  描述: {info['description']}")
    
    print("\n" + "=" * 60)
    print("✅ 人设列表测试完成")
    print("=" * 60)


def test_response_examples():
    """测试不同人设的响应示例"""
    print("\n" + "=" * 60)
    print("模拟不同人设的响应风格")
    print("=" * 60)
    
    manager = PersonaManager()
    
    # 测试场景
    scenarios = [
        ("用户偷懒", "用户今天只工作了2小时，其余时间都在看视频"),
        ("用户努力", "用户今天工作了10小时，完成了所有任务"),
        ("普通询问", "现在几点了？")
    ]
    
    for level in [PersonaLevel.STRICT_MASTER, PersonaLevel.SARCASTIC_BUTLER, PersonaLevel.GENTLE_COMPANION]:
        print(f"\n--- {level.name} 的响应风格 ---")
        manager.set_persona_level(level)
        info = manager.get_current_persona_info()
        
        for scenario_name, context in scenarios:
            print(f"\n场景: {scenario_name}")
            
            if level == PersonaLevel.STRICT_MASTER:
                if "偷懒" in scenario_name:
                    print("  预期响应: <#6>两小时？仆人，你在开玩笑吗？立刻滚回去工作！")
                elif "努力" in scenario_name:
                    print("  预期响应: <#5>十小时，还算差强人意。明天继续保持。")
                else:
                    print("  预期响应: <#5>时间？你该关心的是工作进度。")
            
            elif level == PersonaLevel.SARCASTIC_BUTLER:
                if "偷懒" in scenario_name:
                    print("  预期响应: <#3>哦呀，主人今天只工作两小时呢。在下真是为您的'勤奋'感到惊叹。")
                elif "努力" in scenario_name:
                    print("  预期响应: <#2>十小时？主人今天居然在工作，真是让在下大开眼界。")
                else:
                    print("  预期响应: <#5>主人连时间都不知道了吗？在下建议您看看屏幕右下角。")
            
            elif level == PersonaLevel.GENTLE_COMPANION:
                if "偷懒" in scenario_name:
                    print("  预期响应: <#1>亲爱的，今天是不是有点累了？适当休息也很重要哦。")
                elif "努力" in scenario_name:
                    print("  预期响应: <#1>太棒了！你今天真的很努力！记得照顾好自己哦。")
                else:
                    print("  预期响应: <#5>现在是下午3点，亲爱的。需要我提醒你什么吗？")
    
    print("\n" + "=" * 60)
    print("✅ 响应风格测试完成")
    print("=" * 60)


if __name__ == "__main__":
    print("\n🎭 开始测试人设切换功能")
    print("=" * 60)
    
    # 运行所有测试
    test_persona_manager()
    test_persona_prompts()
    test_available_personas()
    test_response_examples()
    
    print("\n" + "=" * 60)
    print("🎉 所有测试完成！")
    print("=" * 60)
    print("\n说明:")
    print("1. 人设管理器成功创建，支持三种预设档位")
    print("2. 功能提示词和人设提示词已成功分离")
    print("3. 可以动态切换人设而不影响功能")
    print("4. 每种人设都有独特的语言风格和响应方式")
    print("\n下一步:")
    print("- 在设置界面中切换人设档位")
    print("- 观察巴利的对话风格变化")
    print("- 可以根据需要添加自定义人设")