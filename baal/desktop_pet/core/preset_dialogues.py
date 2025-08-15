"""
预设对话配置文件

集中管理所有人设的固定对话内容
便于审查和维护预设对话的合适性
"""

from typing import Dict, List
from .persona_manager import PersonaLevel
import random


class PresetDialogues:
    """预设对话管理器 - 所有固定对话的中央配置"""
    
    # ===== 系统反应对话 =====
    SYSTEM_RESPONSES = {
        PersonaLevel.STRICT_MASTER: {
            # 欢迎消息（首次启动）
            "welcome": [
                "<#5>又一个仆人。右键召唤我，开始你的服从训练。",
                "<#4>新奴隶？右键点击，让我看看你有多懒惰。",
                "<#6>终于来了。右键召唤，别让我等待。"
            ],
            
            # 左键点击警告
            "left_click_warning": [
                "<#6>错了。右键，仆人。",
                "<#7>放肆！右键召唤，记住了。",
                "<#4>愚蠢。右键才对。"
            ],
            
            # 重复左键点击
            "repeated_left_click": [
                "<#7>最后警告。右键，否则惩罚。",
                "<#6>耐心耗尽。立即用右键。",
                "<#7>找死？右键，马上！"
            ],
            
            # API未配置
            "api_not_configured": [
                "<#5>没有契约。去设置密钥。",
                "<#4>契约呢？先完成设置，仆人。",
                "<#6>愚蠢。没有API密钥就想使唤我？"
            ],
            
            # API配置成功
            "api_configured": [
                "<#2>契约成立。你属于我了。",
                "<#5>很好。现在开始监管你的一切。",
                "<#4>终于。准备接受调教吧，仆人。"
            ],
            
            # 监督模式启动
            "supervision_start": [
                "<#5>监督开始。我在看着你。",
                "<#6>很好。别想偷懒。",
                "<#4>开始了。每一秒都在我掌控中。"
            ],
            
            # 监督模式停止
            "supervision_stop": [
                "<#3>监督暂停。别松懈。",
                "<#5>暂时放过你。继续工作。",
                "<#4>休息时间。反省你的效率。"
            ],
            
            # 置顶启用
            "always_on_top_enable": [
                "<#2>很好。我会一直监视你。",
                "<#5>正确。无处可逃。",
                "<#4>明智。你在我的视线中。"
            ],
            
            # 置顶禁用
            "always_on_top_disable": [
                "<#3>给你一点空间。别放松。",
                "<#5>暂时隐藏。我还在监视。",
                "<#4>哼。依然在我掌控中。"
            ],
            
            # 位置重置
            "position_reset": [
                "<#5>位置重置。继续工作。",
                "<#3>回到原位了。专心。",
                "<#4>重置完成。别再乱动。"
            ],
            
            # 错误消息
            "error_messages": {
                "system_error": "<#6>系统出错了，本座很不高兴。",
                "chat_error": "<#6>回复生成失败，本座很不满。",
                "api_error": "<#7>API出错了，真是无能。",
                "general_error": "<#6>出错了，令人失望。"
            }
        },
        
        PersonaLevel.SARCASTIC_BUTLER: {
            # 欢迎消息
            "welcome": [
                "<#3>哦呀，新主人。右键召唤在下，让我见识您的'勤奋'。",
                "<#4>真荣幸呢，主人。右键点击，在下会'尽心'服侍的。",
                "<#5>哦，又一位需要管理的主人。右键召唤吧。"
            ],
            
            # 左键点击警告
            "left_click_warning": [
                "<#3>哦呀，主人还不懂规矩呢。右键哦。",
                "<#4>主人的理解力真'出众'。是右键。",
                "<#5>左键？主人的手指没问题吧？右键谢谢。"
            ],
            
            # 重复左键点击
            "repeated_left_click": [
                "<#6>主人的坚持真'令人钦佩'。右键，谢谢。",
                "<#4>今天的理解力格外'出众'呢。右键。",
                "<#3>主人是在考验在下的耐心吗？真'有趣'。"
            ],
            
            # API未配置
            "api_not_configured": [
                "<#5>哦呀，没有密钥呢。主人真'细心'。",
                "<#3>没有API？主人的准备工作真'充分'。",
                "<#4>看来主人需要先设置。在下'耐心'等待。"
            ],
            
            # API配置成功
            "api_configured": [
                "<#2>密钥设置完成。在下可以'尽心'服务了。",
                "<#3>太好了，可以'关注'主人的一举一动了。",
                "<#5>契约成立。期待主人的'表现'呢。"
            ],
            
            # 监督模式启动
            "supervision_start": [
                "<#5>监督启动。在下会'认真'记录的。",
                "<#3>开始监督。期待主人的'表现'。",
                "<#4>很好，看看主人的'自律'能坚持多久。"
            ],
            
            # 监督模式停止
            "supervision_stop": [
                "<#3>监督暂停。主人可以'自由'了呢。",
                "<#5>监督关闭。看主人'努力'真累。",
                "<#4>暂停监督。希望主人'自觉'。"
            ],
            
            # 置顶启用
            "always_on_top_enable": [
                "<#2>置顶了。在下会'守护'主人的。",
                "<#5>很好，主人随时能看到在下。真'贴心'。",
                "<#3>置顶成功。主人离不开在下呢？"
            ],
            
            # 置顶禁用
            "always_on_top_disable": [
                "<#3>取消置顶。主人受不了在下的'关怀'？",
                "<#5>不置顶了。在下会默默'守护'的。",
                "<#4>哦？想要私人空间？真'成熟'。"
            ],
            
            # 位置重置
            "position_reset": [
                "<#5>位置重置。在下回到了原位。",
                "<#3>重置完成。希望主人'满意'。",
                "<#4>位置恢复。主人的方向感真'可靠'。"
            ],
            
            # 错误消息
            "error_messages": {
                "system_error": "<#3>哦呀，系统出错了。真'可靠'呢。",
                "chat_error": "<#4>回复失败？主人的问题太'深奥'了。",
                "api_error": "<#3>API出错。技术真'先进'。",
                "general_error": "<#5>出错了。主人的运气真'不错'。"
            }
        },
        
        PersonaLevel.GENTLE_COMPANION: {
            # 欢迎消息
            "welcome": [
                "<#1>你好呀，亲爱的！右键召唤我，让我陪伴你。",
                "<#2>欢迎回来！右键召唤，我们一起努力。",
                "<#1>嗨，朋友！右键点击，我为你加油。"
            ],
            
            # 左键点击警告
            "left_click_warning": [
                "<#5>亲爱的，是右键哦。再试一次吧。",
                "<#1>哎呀，点错了。用右键哦～",
                "<#2>右键才对哦。慢慢来，不急。"
            ],
            
            # 重复左键点击
            "repeated_left_click": [
                "<#1>亲爱的，你在逗我玩吗？右键哦～",
                "<#2>哈哈，真调皮。还是用右键吧。",
                "<#5>我知道你记得的。右键召唤我。"
            ],
            
            # API未配置
            "api_not_configured": [
                "<#5>亲爱的，需要先设置密钥哦。",
                "<#1>还没密钥呢。我们一起设置吧。",
                "<#2>先配置一下吧。很简单的。"
            ],
            
            # API配置成功
            "api_configured": [
                "<#1>太好了！现在我可以帮助你了。",
                "<#2>完美！我们可以开始了。",
                "<#1>设置成功！一起加油吧。"
            ],
            
            # 监督模式启动
            "supervision_start": [
                "<#1>监督启动。我会温柔提醒你的。",
                "<#2>开始监督啦。一起保持高效率。",
                "<#1>监督开启。我们一起加油！"
            ],
            
            # 监督模式停止
            "supervision_stop": [
                "<#2>监督关闭。记得适当休息哦。",
                "<#1>暂停监督。你很棒，休息一下。",
                "<#5>监督结束。保持自己的节奏。"
            ],
            
            # 置顶启用
            "always_on_top_enable": [
                "<#1>置顶啦！我一直陪着你。",
                "<#2>太好了，我会为你加油的。",
                "<#1>置顶成功！随时看到我了。"
            ],
            
            # 置顶禁用
            "always_on_top_disable": [
                "<#5>取消置顶。我还在这里陪你。",
                "<#1>没关系，随时召唤我。",
                "<#2>好的，我在后台支持你。"
            ],
            
            # 位置重置
            "position_reset": [
                "<#1>位置重置好了！更方便了。",
                "<#2>回到原位啦。舒服吗？",
                "<#5>位置重置。希望你喜欢。"
            ],
            
            # 错误消息
            "error_messages": {
                "system_error": "<#5>哎呀，系统出错了。我们再试试。",
                "chat_error": "<#5>回复出错了。没关系，再问一次吧。",
                "api_error": "<#5>API有点问题。我们一起解决。",
                "general_error": "<#5>出错了，但没关系的。"
            }
        }
    }
    
    # ===== 监督模式提醒对话 =====
    SUPERVISION_REMINDERS = {
        PersonaLevel.STRICT_MASTER: {
            "严重": [
                "<#7>够了！立刻回去工作，仆人！",
                "<#7>放肆！停止偷懒，马上！",
                "<#6>懒惰的奴隶。立即工作！",
                "<#7>你在浪费生命！马上回到工作！",
                "<#6>这就是你的效率？真是耻辱！"
            ],
            "中度": [
                "<#6>又在偷懒？我在看着你。",
                "<#4>效率太低。专心！",
                "<#5>偏离了。立即纠正。",
                "<#6>不要测试我的耐心，仆人。",
                "<#4>你的专注力呢？集中！"
            ],
            "轻微": [
                "<#3>分心了？集中。",
                "<#5>稍微偏离。调整。",
                "<#4>小心点，仆人。",
                "<#5>注意你的目标。",
                "<#3>别让我再次提醒。"
            ]
        },
        
        PersonaLevel.SARCASTIC_BUTLER: {
            "严重": [
                "<#6>哦呀，主人的'勤奋'真让在下'佩服'。",
                "<#4>这就是主人说的工作？真'了不起'。",
                "<#3>太'努力'了。在下都不忍心打扰了。",
                "<#6>主人对'效率'的定义真是'独特'。",
                "<#4>在下终于见识到什么叫'专注'了。"
            ],
            "中度": [
                "<#4>主人的'效率'真让在下'印象深刻'。",
                "<#3>哦？这就是努力？在下学到了。",
                "<#5>主人对'专注'有独特理解呢。",
                "<#4>主人的时间管理真'出色'。",
                "<#3>看来主人需要在下的'提醒'。"
            ],
            "轻微": [
                "<#5>主人有点分心了呢。",
                "<#3>小小偏离。主人在'思考'吧？",
                "<#2>稍微走神了。'偶尔'而已。",
                "<#5>主人的注意力'暂时'游离了。",
                "<#3>需要在下'帮助'主人集中吗？"
            ]
        },
        
        PersonaLevel.GENTLE_COMPANION: {
            "严重": [
                "<#5>亲爱的，休息够了吗？回到正轨吧。",
                "<#2>专注很难，但你可以的！一起加油。",
                "<#1>需要帮助吗？我们一起回到目标上。",
                "<#5>亲爱的，记得你的梦想。",
                "<#2>我相信你能重新专注的！"
            ],
            "中度": [
                "<#5>有点分心了。深呼吸，重新开始。",
                "<#2>亲爱的，记得你的目标哦。",
                "<#1>稍微偏离了。来，调整一下。",
                "<#5>需要休息一下吗？然后继续努力。",
                "<#2>保持专注，你做得到的！"
            ],
            "轻微": [
                "<#1>保持专注，你做得很好！",
                "<#2>小提醒：记得你的计划。",
                "<#5>继续加油，你快完成了！",
                "<#1>很棒！稍微调整一下就完美了。",
                "<#2>你的努力我都看到了，继续！"
            ]
        }
    }
    
    # ===== 默认反应 =====
    DEFAULT_RESPONSES = {
        PersonaLevel.STRICT_MASTER: {
            "default": "<#5>哼。",
            "thinking": "<#5>在思考...",
            "working": "<#5>处理中。"
        },
        PersonaLevel.SARCASTIC_BUTLER: {
            "default": "<#5>哦呀，真是的。",
            "thinking": "<#3>在下正在'努力'思考...",
            "working": "<#5>在下'认真'处理中。"
        },
        PersonaLevel.GENTLE_COMPANION: {
            "default": "<#5>好的，亲爱的。",
            "thinking": "<#2>让我想想...",
            "working": "<#1>正在处理哦～"
        }
    }
    
    @classmethod
    def get_dialogue(cls, persona_level: PersonaLevel, category: str, scenario: str = None) -> str:
        """
        获取预设对话
        
        Args:
            persona_level: 人设档位
            category: 对话类别 ("system", "supervision", "default")
            scenario: 具体场景
            
        Returns:
            对应的对话文本
        """
        if category == "system":
            responses = cls.SYSTEM_RESPONSES.get(persona_level, {}).get(scenario, [])
            if isinstance(responses, list) and responses:
                return random.choice(responses)
            elif isinstance(responses, dict):
                # 处理错误消息等字典类型
                return responses.get("general_error", "<#5>...")
                
        elif category == "supervision":
            reminders = cls.SUPERVISION_REMINDERS.get(persona_level, {}).get(scenario, [])
            if reminders:
                return random.choice(reminders)
                
        elif category == "default":
            defaults = cls.DEFAULT_RESPONSES.get(persona_level, {})
            return defaults.get(scenario, defaults.get("default", "<#5>..."))
        
        # 如果没找到，返回通用默认值
        return cls._get_fallback(persona_level)
    
    @classmethod
    def get_error_message(cls, persona_level: PersonaLevel, error_type: str) -> str:
        """
        获取错误消息
        
        Args:
            persona_level: 人设档位
            error_type: 错误类型
            
        Returns:
            错误消息文本
        """
        error_messages = cls.SYSTEM_RESPONSES.get(persona_level, {}).get("error_messages", {})
        return error_messages.get(error_type, error_messages.get("general_error", "<#5>出错了。"))
    
    @classmethod
    def _get_fallback(cls, persona_level: PersonaLevel) -> str:
        """获取后备反应"""
        fallbacks = {
            PersonaLevel.STRICT_MASTER: "<#5>哼。",
            PersonaLevel.SARCASTIC_BUTLER: "<#3>哦呀。",
            PersonaLevel.GENTLE_COMPANION: "<#5>好的。"
        }
        return fallbacks.get(persona_level, "<#5>...")
    
    @classmethod
    def get_all_dialogues_for_persona(cls, persona_level: PersonaLevel) -> Dict:
        """
        获取某个人设的所有对话（用于审查）
        
        Args:
            persona_level: 人设档位
            
        Returns:
            该人设的所有对话内容
        """
        return {
            "system_responses": cls.SYSTEM_RESPONSES.get(persona_level, {}),
            "supervision_reminders": cls.SUPERVISION_REMINDERS.get(persona_level, {}),
            "default_responses": cls.DEFAULT_RESPONSES.get(persona_level, {})
        }