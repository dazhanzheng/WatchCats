"""
预设反应管理器

管理巴利在不同场景下的预设反应，与人设系统对齐
"""

from typing import Dict, List
from .persona_manager import PersonaLevel
import random


class PresetResponseManager:
    """预设反应管理器"""
    
    # 预设反应模板 - 根据人设和场景组织
    RESPONSES = {
        PersonaLevel.STRICT_MASTER: {
            "welcome": [
                "<#5>又一个仆人。右键召唤我，开始你的服从训练。",
                "<#4>新奴隶？右键点击，让我看看你有多懒惰。",
                "<#6>终于来了。右键召唤，别让我等待。"
            ],
            "left_click_warning": [
                "<#6>错了。右键，仆人。",
                "<#7>放肆！右键召唤，记住了。",
                "<#4>愚蠢。右键才对。"
            ],
            "repeated_left_click": [
                "<#7>最后警告。右键，否则惩罚。",
                "<#6>耐心耗尽。立即用右键。",
                "<#7>找死？右键，马上！"
            ],
            "api_not_configured": [
                "<#5>没有契约。去设置密钥。",
                "<#4>契约呢？先完成设置，仆人。",
                "<#6>愚蠢。没有API密钥就想使唤我？"
            ],
            "api_configured": [
                "<#2>契约成立。你属于我了。",
                "<#5>很好。现在开始监管你的一切。",
                "<#4>终于。准备接受调教吧，仆人。"
            ],
            "supervision_start": [
                "<#5>监督开始。我在看着你。",
                "<#6>很好。别想偷懒。",
                "<#4>开始了。每一秒都在我掌控中。"
            ],
            "supervision_stop": [
                "<#3>监督暂停。别松懈。",
                "<#5>暂时放过你。继续工作。",
                "<#4>休息时间。反省你的效率。"
            ],
            "always_on_top_enable": [
                "<#2>很好。我会一直监视你。",
                "<#5>正确。无处可逃。",
                "<#4>明智。你在我的视线中。"
            ],
            "always_on_top_disable": [
                "<#3>给你一点空间。别放松。",
                "<#5>暂时隐藏。我还在监视。",
                "<#4>哼。依然在我掌控中。"
            ],
            "position_reset": [
                "<#5>位置重置。继续工作。",
                "<#3>回到原位了。专心。",
                "<#4>重置完成。别再乱动。"
            ]
        },
        
        PersonaLevel.SARCASTIC_BUTLER: {
            "welcome": [
                "<#3>哦呀，新主人。右键召唤在下，让我见识您的'勤奋'。",
                "<#4>真荣幸呢，主人。右键点击，在下会'尽心'服侍的。",
                "<#5>哦，又一位需要管理的主人。右键召唤吧。"
            ],
            "left_click_warning": [
                "<#3>哦呀，主人还不懂规矩呢。右键哦。",
                "<#4>主人的理解力真'出众'。是右键。",
                "<#5>左键？主人的手指没问题吧？右键谢谢。"
            ],
            "repeated_left_click": [
                "<#6>主人的坚持真'令人钦佩'。右键，谢谢。",
                "<#4>今天的理解力格外'出众'呢。右键。",
                "<#3>主人是在考验在下的耐心吗？真'有趣'。"
            ],
            "api_not_configured": [
                "<#5>哦呀，没有密钥呢。主人真'细心'。",
                "<#3>没有API？主人的准备工作真'充分'。",
                "<#4>看来主人需要先设置。在下'耐心'等待。"
            ],
            "api_configured": [
                "<#2>密钥设置完成。在下可以'尽心'服务了。",
                "<#3>太好了，可以'关注'主人的一举一动了。",
                "<#5>契约成立。期待主人的'表现'呢。"
            ],
            "supervision_start": [
                "<#5>监督启动。在下会'认真'记录的。",
                "<#3>开始监督。期待主人的'表现'。",
                "<#4>很好，看看主人的'自律'能坚持多久。"
            ],
            "supervision_stop": [
                "<#3>监督暂停。主人可以'自由'了呢。",
                "<#5>监督关闭。看主人'努力'真累。",
                "<#4>暂停监督。希望主人'自觉'。"
            ],
            "always_on_top_enable": [
                "<#2>置顶了。在下会'守护'主人的。",
                "<#5>很好，主人随时能看到在下。真'贴心'。",
                "<#3>置顶成功。主人离不开在下呢？"
            ],
            "always_on_top_disable": [
                "<#3>取消置顶。主人受不了在下的'关怀'？",
                "<#5>不置顶了。在下会默默'守护'的。",
                "<#4>哦？想要私人空间？真'成熟'。"
            ],
            "position_reset": [
                "<#5>位置重置。在下回到了原位。",
                "<#3>重置完成。希望主人'满意'。",
                "<#4>位置恢复。主人的方向感真'可靠'。"
            ]
        },
        
        PersonaLevel.GENTLE_COMPANION: {
            "welcome": [
                "<#1>你好呀，亲爱的！右键召唤我，让我陪伴你。",
                "<#2>欢迎回来！右键召唤，我们一起努力。",
                "<#1>嗨，朋友！右键点击，我为你加油。"
            ],
            "left_click_warning": [
                "<#5>亲爱的，是右键哦。再试一次吧。",
                "<#1>哎呀，点错了。用右键哦～",
                "<#2>右键才对哦。慢慢来，不急。"
            ],
            "repeated_left_click": [
                "<#1>亲爱的，你在逗我玩吗？右键哦～",
                "<#2>哈哈，真调皮。还是用右键吧。",
                "<#5>我知道你记得的。右键召唤我。"
            ],
            "api_not_configured": [
                "<#5>亲爱的，需要先设置密钥哦。",
                "<#1>还没密钥呢。我们一起设置吧。",
                "<#2>先配置一下吧。很简单的。"
            ],
            "api_configured": [
                "<#1>太好了！现在我可以帮助你了。",
                "<#2>完美！我们可以开始了。",
                "<#1>设置成功！一起加油吧。"
            ],
            "supervision_start": [
                "<#1>监督启动。我会温柔提醒你的。",
                "<#2>开始监督啦。一起保持高效率。",
                "<#1>监督开启。我们一起加油！"
            ],
            "supervision_stop": [
                "<#2>监督关闭。记得适当休息哦。",
                "<#1>暂停监督。你很棒，休息一下。",
                "<#5>监督结束。保持自己的节奏。"
            ],
            "always_on_top_enable": [
                "<#1>置顶啦！我一直陪着你。",
                "<#2>太好了，我会为你加油的。",
                "<#1>置顶成功！随时看到我了。"
            ],
            "always_on_top_disable": [
                "<#5>取消置顶。我还在这里陪你。",
                "<#1>没关系，随时召唤我。",
                "<#2>好的，我在后台支持你。"
            ],
            "position_reset": [
                "<#1>位置重置好了！更方便了。",
                "<#2>回到原位啦。舒服吗？",
                "<#5>位置重置。希望你喜欢。"
            ]
        }
    }
    
    def __init__(self):
        """初始化预设反应管理器"""
        pass
    
    @classmethod
    def get_response(cls, persona_level: PersonaLevel, scenario: str) -> str:
        """
        获取特定场景的预设反应
        
        Args:
            persona_level: 当前人设档位
            scenario: 场景标识符
            
        Returns:
            对应的预设反应文本
        """
        # 获取对应人设的反应集合
        persona_responses = cls.RESPONSES.get(persona_level, {})
        
        # 获取特定场景的反应列表
        scenario_responses = persona_responses.get(scenario, [])
        
        if scenario_responses:
            # 随机选择一个反应
            return random.choice(scenario_responses)
        else:
            # 如果没有找到对应的反应，返回默认反应
            return cls._get_default_response(persona_level, scenario)
    
    @classmethod
    def _get_default_response(cls, persona_level: PersonaLevel, scenario: str) -> str:
        """
        获取默认反应（当没有预设时）
        
        Args:
            persona_level: 当前人设档位
            scenario: 场景标识符
            
        Returns:
            默认反应文本
        """
        # 默认反应
        defaults = {
            PersonaLevel.STRICT_MASTER: "<#5>哼。",
            PersonaLevel.SARCASTIC_BUTLER: "<#5>哦呀，真是的。",
            PersonaLevel.GENTLE_COMPANION: "<#5>好的，亲爱的。"
        }
        
        return defaults.get(persona_level, "<#5>...")
    
    @classmethod
    def get_supervision_reminder(cls, persona_level: PersonaLevel, deviation_level: str) -> str:
        """
        获取监督模式提醒（根据偏离程度）
        
        Args:
            persona_level: 当前人设档位
            deviation_level: 偏离程度 ("严重", "中度", "轻微")
            
        Returns:
            监督提醒文本
        """
        reminders = {
            PersonaLevel.STRICT_MASTER: {
                "严重": [
                    "<#7>够了！立刻回去工作，仆人！",
                    "<#7>放肆！停止偷懒，马上！",
                    "<#6>懒惰的奴隶。立即工作！"
                ],
                "中度": [
                    "<#6>又在偷懒？我在看着你。",
                    "<#4>效率太低。专心！",
                    "<#5>偏离了。立即纠正。"
                ],
                "轻微": [
                    "<#3>分心了？集中。",
                    "<#5>稍微偏离。调整。",
                    "<#4>小心点，仆人。"
                ]
            },
            PersonaLevel.SARCASTIC_BUTLER: {
                "严重": [
                    "<#6>哦呀，主人的'勤奋'真让在下'佩服'。",
                    "<#4>这就是主人说的工作？真'了不起'。",
                    "<#3>太'努力'了。在下都不忍心打扰了。"
                ],
                "中度": [
                    "<#4>主人的'效率'真让在下'印象深刻'。",
                    "<#3>哦？这就是努力？在下学到了。",
                    "<#5>主人对'专注'有独特理解呢。"
                ],
                "轻微": [
                    "<#5>主人有点分心了呢。",
                    "<#3>小小偏离。主人在'思考'吧？",
                    "<#2>稍微走神了。'偶尔'而已。"
                ]
            },
            PersonaLevel.GENTLE_COMPANION: {
                "严重": [
                    "<#5>亲爱的，休息够了吗？回到正轨吧。",
                    "<#2>专注很难，但你可以的！一起加油。",
                    "<#1>需要帮助吗？我们一起回到目标上。"
                ],
                "中度": [
                    "<#5>有点分心了。深呼吸，重新开始。",
                    "<#2>亲爱的，记得你的目标哦。",
                    "<#1>稍微偏离了。来，调整一下。"
                ],
                "轻微": [
                    "<#1>保持专注，你做得很好！",
                    "<#2>小提醒：记得你的计划。",
                    "<#5>继续加油，你快完成了！"
                ]
            }
        }
        
        # 获取对应的提醒列表
        persona_reminders = reminders.get(persona_level, {})
        level_reminders = persona_reminders.get(deviation_level, [])
        
        if level_reminders:
            return random.choice(level_reminders)
        else:
            # 默认提醒
            defaults = {
                PersonaLevel.STRICT_MASTER: "<#5>专注你的工作，仆人。",
                PersonaLevel.SARCASTIC_BUTLER: "<#3>主人的'专注力'真是让在下佩服。",
                PersonaLevel.GENTLE_COMPANION: "<#2>加油，亲爱的！你可以的。"
            }
            return defaults.get(persona_level, "<#5>请保持专注。")