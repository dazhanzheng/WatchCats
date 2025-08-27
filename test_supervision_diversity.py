#!/usr/bin/env python3
"""
测试监督模式提醒的多样性和自然度
模拟不同场景，验证提醒消息的变化
"""

import sys
import json
from datetime import datetime
from baal.desktop_pet.supervision_mode import SupervisionMode

def test_reminder_diversity():
    """测试提醒的多样性"""
    
    print("=" * 60)
    print("监督提醒多样性测试")
    print("=" * 60)
    
    # 模拟不同的活动数据场景
    test_scenarios = [
        {
            "name": "严重偏离 - 大量娱乐",
            "stats": {
                "stats_5m": "过去5分钟活动：\n1. 飞书（4分30秒，占比90%）\n2. Chrome（30秒，占比10%）",
                "stats_2h": "过去2小时活动：\n1. 飞书（1小时45分，占比87.5%）\n2. VS Code（15分钟，占比12.5%）",
                "stats_24h": "过去24小时活动：\n1. 飞书（6小时，占比60%）\n2. Chrome（2小时，占比20%）\n3. VS Code（2小时，占比20%）"
            },
            "persona": {"name": "严厉主人", "description": "巴利是用户的主人，拥有绝对支配权"}
        },
        {
            "name": "中度偏离 - 部分工作",
            "stats": {
                "stats_5m": "过去5分钟活动：\n1. VS Code（3分钟，占比60%）\n2. 飞书（2分钟，占比40%）",
                "stats_2h": "过去2小时活动：\n1. 飞书（1小时，占比50%）\n2. VS Code（50分钟，占比41.7%）\n3. Chrome（10分钟，占比8.3%）",
                "stats_24h": "过去24小时活动：\n1. VS Code（4小时，占比40%）\n2. 飞书（3小时，占比30%）\n3. Chrome（3小时，占比30%）"
            },
            "persona": {"name": "毒舌管家", "description": "巴利是傲娇的管家，表面毒舌内心关心"}
        },
        {
            "name": "轻微偏离 - 基本专注",
            "stats": {
                "stats_5m": "过去5分钟活动：\n1. VS Code（4分30秒，占比90%）\n2. Chrome（30秒，占比10%）",
                "stats_2h": "过去2小时活动：\n1. VS Code（1小时30分，占比75%）\n2. Chrome（20分钟，占比16.7%）\n3. 飞书（10分钟，占比8.3%）",
                "stats_24h": "过去24小时活动：\n1. VS Code（5小时，占比50%）\n2. Chrome（3小时，占比30%）\n3. 飞书（2小时，占比20%）"
            },
            "persona": {"name": "温柔伴侣", "description": "巴利是温柔的伴侣，给予鼓励和支持"}
        }
    ]
    
    # 创建监督模式实例（使用模拟的LLM）
    class MockLLM:
        def __init__(self, scenario_name):
            self.scenario_name = scenario_name
            
        def chat(self, prompt):
            """模拟LLM的多样化回复"""
            import random
            
            # 根据场景生成不同风格的回复
            if "严重" in self.scenario_name:
                responses = [
                    {
                        "should_remind": True,
                        "deviation_level": "严重",
                        "reminder_message": "<#7>喂！你在搞什么？！飞书聊了快2小时了，工作呢？立刻给我关掉！",
                        "analysis": "用户严重偏离目标"
                    },
                    {
                        "should_remind": True,
                        "deviation_level": "严重",
                        "reminder_message": "<#6>...我就静静看着你摸鱼。6个小时的飞书，真有你的。",
                        "analysis": "用户严重偏离目标"
                    },
                    {
                        "should_remind": True,
                        "deviation_level": "严重",
                        "reminder_message": "<#7>（看着屏幕）算了，反正deadline也不重要...是吧？",
                        "analysis": "用户严重偏离目标"
                    }
                ]
            elif "中度" in self.scenario_name:
                responses = [
                    {
                        "should_remind": True,
                        "deviation_level": "中度",
                        "reminder_message": "<#4>哦～原来飞书是新的IDE啊，我都不知道呢～",
                        "analysis": "用户中度偏离"
                    },
                    {
                        "should_remind": True,
                        "deviation_level": "中度",
                        "reminder_message": "<#3>啧啧，工作一半摸鱼一半，很会平衡嘛。",
                        "analysis": "用户中度偏离"
                    },
                    {
                        "should_remind": True,
                        "deviation_level": "中度",
                        "reminder_message": "<#3>所以...你打算什么时候开始认真工作？就问问。",
                        "analysis": "用户中度偏离"
                    }
                ]
            else:
                responses = [
                    {
                        "should_remind": False,
                        "deviation_level": "轻微",
                        "reminder_message": "<#1>很好，继续保持专注哦！偶尔休息一下也没关系的～",
                        "analysis": "用户基本专注"
                    },
                    {
                        "should_remind": True,
                        "deviation_level": "轻微",
                        "reminder_message": "<#2>工作得不错呢！要不要喝点水，休息一下眼睛？",
                        "analysis": "用户基本专注"
                    },
                    {
                        "should_remind": False,
                        "deviation_level": "无",
                        "reminder_message": "<#1>（看着认真工作的你）嗯...这样就对了。",
                        "analysis": "用户专注工作"
                    }
                ]
            
            response = random.choice(responses)
            return json.dumps(response, ensure_ascii=False)
    
    class MockAssistant:
        def __init__(self, scenario_name):
            self.llm = MockLLM(scenario_name)
            self.conversation_history = []
            
        def chat(self, prompt):
            return self.llm.chat(prompt)
    
    # 测试每个场景
    for scenario in test_scenarios:
        print(f"\n场景: {scenario['name']}")
        print(f"人设: {scenario['persona']['name']}")
        print("-" * 40)
        
        # 创建监督模式
        supervision = SupervisionMode()
        supervision.llm_assistant = MockAssistant(scenario['name'])
        supervision.long_term_goal = "完成项目开发"
        supervision.short_term_goals = ["写代码", "测试", "文档"]
        
        # 模拟多次评估，查看提醒的多样性
        print("\n生成3次提醒，观察多样性：")
        for i in range(3):
            result = supervision._evaluate_activity_enhanced(scenario['stats'])
            if result and result.get('should_remind'):
                message = result.get('reminder_message', '无提醒')
                print(f"\n  第{i+1}次: {message}")
            else:
                print(f"\n  第{i+1}次: [不需要提醒]")
        
        print()
    
    print("=" * 60)
    print("测试完成！")
    print("\n观察要点：")
    print("1. 同一场景下，多次生成的提醒应该有所不同")
    print("2. 语言应该更加口语化、自然")
    print("3. 不同人设的语言风格应该明显不同")
    print("4. 避免机械化的格式和表达")
    print("=" * 60)

if __name__ == "__main__":
    test_reminder_diversity()