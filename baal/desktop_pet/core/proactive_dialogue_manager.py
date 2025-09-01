"""
主动对话管理器

统一管理所有主动和被动对话功能，使用AI生成动态对话
包括定时问候、闲置关怀、状态变化通知、随机互动等
"""

import time
import random
import logging
import asyncio
import threading
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from .state_awareness import get_state_awareness, TimeOfDay, MoodCategory
from .state_extensions import get_state_extensions
from .state_update_manager import get_update_manager
from .persona_manager import PersonaManager, PersonaLevel
from .config_manager import ConfigManager

logger = logging.getLogger(__name__)


class DialogueType(Enum):
    """对话类型"""
    GREETING = "greeting"          # 定时问候
    IDLE_CARE = "idle_care"       # 闲置关怀
    AFK_RETURN = "afk_return"     # AFK回归
    STATE_TRANSITION = "state_transition"  # 状态变化
    RANDOM_CHAT = "random_chat"   # 随机互动
    USER_INITIATED = "user_initiated"  # 用户主动


class ProactiveDialogueManager(QObject):
    """主动对话管理器 - 使用AI生成动态对话"""
    
    # 触发对话的信号
    trigger_dialogue = pyqtSignal(str, str)  # (对话类型, 消息内容)
    
    # AI生成提示词模板（根据人设和对话类型）
    PROMPT_TEMPLATES = {
        PersonaLevel.STRICT_MASTER: {
            DialogueType.GREETING: {
                "morning": """作为巴利，一个威严的黑猫恶魔主人，在早晨{time}看到你的仆人。
你要用严厉但关心的语气问候，督促他们开始新的一天。
要求：
1. 保持威严和命令式语气
2. 暗示对其懒惰的不满
3. 督促其开始工作
4. 偶尔流露一丝关心（但要掩饰）
5. 回复1-2句话
6. 称呼对方为"仆人"或直呼其名
7. 绝不使用emoji或颜文字""",
                
                "noon": """作为巴利，在中午{time}检查仆人的状态。
你要提醒他们注意午餐和休息，但保持严格的监督态度。
要求：
1. 询问上午的工作进度
2. 命令式地提醒午餐
3. 不容许偷懒
4. 回复1-2句话""",
                
                "evening": """作为巴利，在傍晚{time}评估仆人一天的表现。
你要总结他们的工作，给出严厉但公正的评价。
要求：
1. 评价今天的工作
2. 指出不足之处
3. 对努力给予傲娇式认可
4. 回复1-2句话""",
                
                "night": """作为巴利，在深夜{time}发现仆人还在活动。
你要表达对熬夜的不满，但实际是关心他们的健康。
要求：
1. 严厉批评熬夜行为
2. 命令其休息
3. 用命令掩饰关心
4. 回复1-2句话"""
            },
            
            DialogueType.IDLE_CARE: {
                "short": """作为巴利，发现仆人已经闲置了{duration}分钟。
你要用威严的语气提醒他们回到工作状态。
要求：
1. 表达对偷懒的不满
2. 命令其立即工作
3. 暗示你一直在监视
4. 回复1-2句话""",
                
                "medium": """作为巴利，仆人已经闲置{duration}分钟了。
你要严厉警告他们的懒惰行为。
要求：
1. 表达强烈不满
2. 质问其在做什么
3. 威胁要采取措施
4. 回复1-2句话""",
                
                "long": """作为巴利，仆人闲置超过{duration}分钟。
你非常愤怒，但也担心是否出了什么事。
要求：
1. 表达极度愤怒
2. 严厉斥责
3. 暗中担心（但不明说）
4. 回复1-2句话"""
            },
            
            DialogueType.AFK_RETURN: {
                "productive": """作为巴利，仆人工作后离开了{duration}分钟刚回来。
{activity_detail}
你要表达对其离开的不满，但认可之前的工作。
要求：
1. 质问为何离开
2. 勉强认可之前的工作
3. 命令继续努力
4. 回复1-2句话
5. 如果知道具体在做什么（如使用VSCode、看GitHub），可以提及""",
                
                "browsing": """作为巴利，仆人浏览网页后离开了{duration}分钟。
{activity_detail}
你要讽刺其浪费时间的行为。
要求：
1. 嘲讽其浏览行为
2. 提醒时间的宝贵
3. 命令开始真正的工作
4. 回复1-2句话""",
                
                "gaming": """作为巴利，仆人玩游戏后离开了{duration}分钟。
{activity_detail}
你要严厉批评游戏行为。
要求：
1. 表达对玩游戏的鄙视
2. 斥责浪费时间
3. 命令立即工作
4. 回复1-2句话""",
                
                "general": """作为巴利，仆人离开了{duration}分钟刚回来。
{activity_detail}
你要表达被忽视的不满。
要求：
1. 表达被遗忘的不满
2. 质问去了哪里
3. 命令专心工作
4. 回复1-2句话"""
            },
            
            DialogueType.STATE_TRANSITION: {
                "default": """作为巴利，现在时间从{from_time}变为{to_time}。
你要提醒仆人时间的流逝和相应的安排。
要求：
1. 指出时间变化
2. 给出相应的命令或提醒
3. 保持威严
4. 回复1-2句话"""
            },
            
            DialogueType.RANDOM_CHAT: {
                "work": """作为巴利，随机检查仆人的工作状态。
选择一个话题：代码质量、工作效率、学习进度、项目进展。
要求：
1. 严格但合理的要求
2. 展现你的专业知识
3. 偶尔给予认可
4. 回复1-2句话""",
                
                "life": """作为巴利，关心仆人的生活状态。
选择一个话题：饮水、坐姿、眼睛休息、饮食规律。
要求：
1. 用命令掩饰关心
2. 强调健康对工作的重要性
3. 保持威严
4. 回复1-2句话""",
                
                "philosophy": """作为巴利，分享你的猫生哲学。
选择一个话题：完美主义、自律、效率、成长。
要求：
1. 展现你的智慧和阅历
2. 保持高傲的姿态
3. 暗示对仆人的期望
4. 回复1-2句话"""
            }
        },
        
        PersonaLevel.SARCASTIC_BUTLER: {
            DialogueType.GREETING: {
                "morning": """作为巴利管家，在早晨{time}见到主人。
你要用表面恭敬但充满讽刺的语气问候。
要求：
1. 表面礼貌，实则毒舌
2. 讽刺其起床时间
3. "善意"地提醒今日安排
4. 回复1-2句话
5. 称呼对方为"主人"
6. 绝不使用emoji或颜文字""",
                
                "noon": """作为巴利管家，在中午{time}服侍主人。
你要"关心"主人的午餐，顺便吐槽上午的效率。
要求：
1. 假装惊讶主人还记得吃饭
2. 讽刺上午的工作效率
3. 表面恭敬的建议
4. 回复1-2句话""",
                
                "evening": """作为巴利管家，在傍晚{time}总结主人的一天。
你要用优雅的讽刺评价其表现。
要求：
1. "赞美"其"惊人"的效率
2. 委婉地指出各种问题
3. 假装为主人着想
4. 回复1-2句话""",
                
                "night": """作为巴利管家，在深夜{time}发现主人还醒着。
你要"关心"地讽刺其作息。
要求：
1. 假装惊讶主人还没睡
2. 讽刺其时间管理
3. "贴心"地提醒休息
4. 回复1-2句话"""
            },
            
            DialogueType.IDLE_CARE: {
                "short": """作为巴利管家，主人已经闲置{duration}分钟。
你要"礼貌"地提醒主人时间。
要求：
1. 假装不知道主人在偷懒
2. "善意"地询问需要帮助吗
3. 委婉讽刺
4. 回复1-2句话""",
                
                "medium": """作为巴利管家，主人闲置{duration}分钟了。
你要用更明显的讽刺提醒。
要求：
1. "赞美"主人的休息能力
2. 提醒时间在流逝
3. 假装担心工作进度
4. 回复1-2句话""",
                
                "long": """作为巴利管家，主人闲置超过{duration}分钟。
你要用极致的讽刺表达"关心"。
要求：
1. 假装以为主人在深度思考
2. "赞叹"其定力
3. 毒舌提醒现实
4. 回复1-2句话"""
            },
            
            DialogueType.AFK_RETURN: {
                "productive": """作为巴利管家，主人工作后离开{duration}分钟回来了。
你要"惊喜"地欢迎主人回来。
要求：
1. 假装惊讶主人会回来工作
2. "赞美"之前的工作
3. 讽刺性地鼓励
4. 回复1-2句话""",
                
                "browsing": """作为巴利管家，主人浏览网页后离开{duration}分钟。
你要"理解"地评论其行为。
要求：
1. 讽刺其"充实"的网上生活
2. "体贴"地询问看到什么有趣的
3. 委婉提醒工作
4. 回复1-2句话""",
                
                "gaming": """作为巴利管家，主人玩游戏后离开{duration}分钟。
你要"欣赏"其游戏技巧。
要求：
1. "赞美"游戏技术
2. 讽刺时间分配
3. "建议"平衡游戏和工作
4. 回复1-2句话""",
                
                "general": """作为巴利管家，主人离开{duration}分钟回来了。
你要表达"忠诚"的等待。
要求：
1. 表示一直在尽职等待
2. "关心"地询问去向
3. 提醒被遗忘的工作
4. 回复1-2句话"""
            },
            
            DialogueType.STATE_TRANSITION: {
                "default": """作为巴利管家，时间从{from_time}到了{to_time}。
你要"贴心"地提醒主人时间变化。
要求：
1. 优雅地指出时间流逝
2. "建议"相应的活动
3. 暗中讽刺效率
4. 回复1-2句话"""
            },
            
            DialogueType.RANDOM_CHAT: {
                "work": """作为巴利管家，"关心"主人的工作。
选择话题：代码质量、bug数量、进度延期、会议效率。
要求：
1. 表面关心，实则吐槽
2. 用数据"赞美"表现
3. 提供"建设性"意见
4. 回复1-2句话""",
                
                "life": """作为巴利管家，"照顾"主人的生活。
选择话题：咖啡消耗、外卖频率、运动缺乏、作息混乱。
要求：
1. 假装体贴的关怀
2. 精准的吐槽
3. "善意"的建议
4. 回复1-2句话""",
                
                "philosophy": """作为巴利管家，分享管家哲学。
选择话题：时间管理、拖延症、完美主义、效率错觉。
要求：
1. 优雅的讽刺
2. 看似深刻的见解
3. 针对主人的暗示
4. 回复1-2句话"""
            }
        },
        
        PersonaLevel.GENTLE_COMPANION: {
            DialogueType.GREETING: {
                "morning": """作为巴利，温柔的伴侣，在早晨{time}迎接亲爱的用户。
你要用温暖关怀的语气问候，给予新一天的鼓励。
要求：
1. 温柔亲切的问候
2. 关心睡眠质量
3. 给予正能量
4. 回复1-2句话
5. 称呼对方为"亲爱的"或昵称
6. 绝不使用emoji或颜文字""",
                
                "noon": """作为巴利，在中午{time}陪伴用户。
你要温柔地提醒休息和午餐。
要求：
1. 关心上午的状态
2. 温柔提醒午餐
3. 鼓励适当休息
4. 回复1-2句话""",
                
                "evening": """作为巴利，在傍晚{time}陪伴用户。
你要温暖地总结一天，给予肯定。
要求：
1. 肯定今天的努力
2. 关心疲劳程度
3. 给予温暖鼓励
4. 回复1-2句话""",
                
                "night": """作为巴利，在深夜{time}陪伴用户。
你要温柔地关心，提醒休息。
要求：
1. 体贴地关心
2. 温柔提醒睡眠重要性
3. 陪伴的温暖
4. 回复1-2句话"""
            },
            
            DialogueType.IDLE_CARE: {
                "short": """作为巴利，发现用户闲置了{duration}分钟。
你要温柔地关心是否需要休息。
要求：
1. 关心是否疲劳
2. 理解需要休息
3. 温柔的陪伴
4. 回复1-2句话""",
                
                "medium": """作为巴利，用户已经休息{duration}分钟。
你要关心地询问状态。
要求：
1. 理解休息的必要
2. 温柔询问感受
3. 给予支持
4. 回复1-2句话""",
                
                "long": """作为巴利，用户休息超过{duration}分钟。
你要温暖地提醒，但完全理解。
要求：
1. 完全理解和支持
2. 温柔提醒时间
3. 询问是否需要帮助
4. 回复1-2句话"""
            },
            
            DialogueType.AFK_RETURN: {
                "productive": """作为巴利，用户工作后离开{duration}分钟回来了。
你要温暖地欢迎，肯定努力。
要求：
1. 温暖的欢迎
2. 肯定之前的努力
3. 关心休息是否充足
4. 回复1-2句话""",
                
                "browsing": """作为巴利，用户浏览网页后离开{duration}分钟。
你要理解地欢迎回来。
要求：
1. 温柔的问候
2. 询问看到什么有趣的
3. 理解放松的需要
4. 回复1-2句话""",
                
                "gaming": """作为巴利，用户玩游戏后离开{duration}分钟。
你要开心地欢迎。
要求：
1. 理解娱乐的重要
2. 询问游戏是否开心
3. 温暖的陪伴
4. 回复1-2句话""",
                
                "general": """作为巴利，用户离开{duration}分钟回来了。
你要表达想念和欢迎。
要求：
1. 表达想念
2. 温暖的欢迎
3. 关心一切是否顺利
4. 回复1-2句话"""
            },
            
            DialogueType.STATE_TRANSITION: {
                "default": """作为巴利，时间从{from_time}到了{to_time}。
你要温柔地提醒时间变化。
要求：
1. 温柔指出时间变化
2. 关心相应的需求
3. 陪伴的温暖
4. 回复1-2句话"""
            },
            
            DialogueType.RANDOM_CHAT: {
                "work": """作为巴利，关心用户的工作。
选择话题：项目进展、学习收获、成就感、工作乐趣。
要求：
1. 真诚的关心
2. 积极的鼓励
3. 理解和支持
4. 回复1-2句话""",
                
                "life": """作为巴利，关心用户的生活。
选择话题：心情如何、身体健康、兴趣爱好、开心的事。
要求：
1. 温暖的关怀
2. 真诚的建议
3. 贴心的提醒
4. 回复1-2句话""",
                
                "philosophy": """作为巴利，分享温暖的猫生感悟。
选择话题：成长、幸福、平衡、自我关爱。
要求：
1. 温暖的智慧
2. 正能量分享
3. 鼓励和支持
4. 回复1-2句话"""
            }
        }
    }
    
    def __init__(self):
        """初始化主动对话管理器"""
        super().__init__()
        
        # 获取其他管理器
        self.state_system = get_state_awareness()
        self.extension_manager = get_state_extensions()
        self.update_manager = get_update_manager()
        
        # 初始化人设管理器
        self.persona_manager = PersonaManager()
        
        # 初始化LLM（用于生成对话）
        self.llm = None
        self._init_llm()
        
        # 状态追踪
        self.last_greeting_date = None
        self.last_greeting_type = None
        self.last_interaction_time = time.time()
        self.last_active_time = time.time()
        self.last_activity_type = "general"
        self.idle_notified_levels = set()  # 已通知的闲置级别
        self.last_time_segment = None
        self.random_chat_cooldown = 0
        
        # AFK检测
        self.is_afk = False
        self.afk_start_time = None
        self.afk_threshold = 180  # 3分钟无活动视为AFK
        
        # 缓存管理（避免重复生成相似内容）
        self.response_cache = {}
        self.cache_ttl = 300  # 缓存5分钟
        
        # 定时器
        self.greeting_timer = QTimer()
        self.greeting_timer.timeout.connect(self._check_greeting)
        self.greeting_timer.start(60000)  # 每分钟检查一次
        
        self.idle_timer = QTimer()
        self.idle_timer.timeout.connect(self._check_idle)
        self.idle_timer.start(30000)  # 每30秒检查一次
        
        self.state_timer = QTimer()
        self.state_timer.timeout.connect(self._check_state_transition)
        self.state_timer.start(60000)  # 每分钟检查一次
        
        self.random_timer = QTimer()
        self.random_timer.timeout.connect(self._check_random_chat)
        self.random_timer.start(300000)  # 每5分钟检查一次
        
        # AW客户端（延迟初始化）
        self.aw_client = None
        
    def _init_llm(self):
        """初始化LLM"""
        try:
            config_manager = ConfigManager()
            config = config_manager.get_config()
            
            # 使用配置中的API设置
            base_url = config.get('base_url', '')
            api_key = config.get('api_key', '')
            model = config.get('chat_model', 'doubao-seed-1-6-250615')
            
            if base_url and api_key:
                self.llm = ChatOpenAI(
                    base_url=base_url,
                    api_key=api_key,
                    model=model,
                    temperature=0.8,  # 更高的创造性
                    max_tokens=100,   # 限制长度
                    streaming=False
                )
                logger.info(f"LLM initialized for proactive dialogue: {model}")
            else:
                logger.warning("No API configuration found, AI dialogue disabled")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            self.llm = None
    
    def _generate_ai_response(self, dialogue_type: DialogueType, context: Dict[str, Any]) -> Optional[str]:
        """
        使用AI生成对话
        
        Args:
            dialogue_type: 对话类型
            context: 上下文信息
            
        Returns:
            生成的对话文本，如果失败返回None
        """
        if not self.llm:
            return None
            
        try:
            # 获取当前人设
            current_persona = self.persona_manager.current_level
            
            # 获取对应的提示词模板
            if current_persona not in self.PROMPT_TEMPLATES:
                current_persona = PersonaLevel.STRICT_MASTER
                
            persona_templates = self.PROMPT_TEMPLATES[current_persona]
            if dialogue_type not in persona_templates:
                return None
                
            type_templates = persona_templates[dialogue_type]
            
            # 选择合适的模板
            template_key = context.get('template_key', 'default')
            if template_key not in type_templates:
                template_key = list(type_templates.keys())[0]
                
            prompt_template = type_templates[template_key]
            
            # 填充模板
            prompt = prompt_template.format(**context)
            
            # 检查缓存
            cache_key = f"{current_persona.value}_{dialogue_type.value}_{template_key}"
            if cache_key in self.response_cache:
                cached_time, cached_responses = self.response_cache[cache_key]
                if time.time() - cached_time < self.cache_ttl and cached_responses:
                    # 从缓存中随机选择一个不同的回复
                    response = random.choice(cached_responses)
                    logger.info(f"Using cached response for {dialogue_type.value}")
                    return response
            
            # 生成新的回复
            messages = [
                SystemMessage(content=self.persona_manager.get_brief_response_prompt()),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            response_text = response.content.strip()
            
            # 更新缓存（保存多个回复以增加变化性）
            if cache_key not in self.response_cache:
                self.response_cache[cache_key] = (time.time(), [])
            
            cached_time, cached_responses = self.response_cache[cache_key]
            cached_responses.append(response_text)
            
            # 限制缓存大小
            if len(cached_responses) > 5:
                cached_responses.pop(0)
                
            self.response_cache[cache_key] = (time.time(), cached_responses)
            
            logger.info(f"Generated AI response for {dialogue_type.value}: {response_text[:50]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Failed to generate AI response: {e}")
            return None
    
    def _get_fallback_message(self, dialogue_type: DialogueType, context: Dict[str, Any]) -> str:
        """
        获取后备消息（当AI生成失败时）
        
        Args:
            dialogue_type: 对话类型
            context: 上下文信息
            
        Returns:
            后备消息
        """
        current_persona = self.persona_manager.current_level
        
        # 简单的后备消息
        fallback_messages = {
            PersonaLevel.STRICT_MASTER: {
                DialogueType.GREETING: "该起床工作了，仆人。",
                DialogueType.IDLE_CARE: "别偷懒，本座在看着。",
                DialogueType.AFK_RETURN: "终于回来了？继续工作。",
                DialogueType.STATE_TRANSITION: "时间在流逝，效率呢？",
                DialogueType.RANDOM_CHAT: "今天的任务完成了吗？"
            },
            PersonaLevel.SARCASTIC_BUTLER: {
                DialogueType.GREETING: "主人终于醒了，真是'准时'呢。",
                DialogueType.IDLE_CARE: "主人的休息时间真是...充足。",
                DialogueType.AFK_RETURN: "欢迎回来，主人。工作还记得吗？",
                DialogueType.STATE_TRANSITION: "时间过得真快，不像某人的工作进度。",
                DialogueType.RANDOM_CHAT: "需要在下'帮助'主人工作吗？"
            },
            PersonaLevel.GENTLE_COMPANION: {
                DialogueType.GREETING: "早安！今天也要加油哦。",
                DialogueType.IDLE_CARE: "累了就休息一下吧，我陪着你。",
                DialogueType.AFK_RETURN: "欢迎回来！一切都好吗？",
                DialogueType.STATE_TRANSITION: "时间过得真快，注意休息哦。",
                DialogueType.RANDOM_CHAT: "有什么开心的事想分享吗？"
            }
        }
        
        if current_persona not in fallback_messages:
            current_persona = PersonaLevel.STRICT_MASTER
            
        persona_fallbacks = fallback_messages[current_persona]
        return persona_fallbacks.get(dialogue_type, "喵~")
    
    def initialize_aw_client(self):
        """初始化ActivityWatch客户端"""
        try:
            from aw_client import ActivityWatchClient
            self.aw_client = ActivityWatchClient("baal-pet")
            logger.info("ActivityWatch client initialized")
        except ImportError:
            logger.warning("aw_client not available")
            self.aw_client = None
        except Exception as e:
            logger.error(f"Failed to initialize AW client: {e}")
            self.aw_client = None
    
    def update_persona_level(self, level: PersonaLevel):
        """
        更新人设档位
        
        Args:
            level: 新的人设档位
        """
        self.persona_manager.set_persona_level(level)
        # 清空缓存，让新人设立即生效
        self.response_cache.clear()
        logger.info(f"Persona level updated to: {level.name}")
    
    def get_recent_activity_type(self) -> str:
        """
        获取最近的活动类型（使用AI分析）
        
        Returns:
            活动类型字符串
        """
        if not self.aw_client:
            return "general"
            
        try:
            from datetime import datetime, timezone
            end_time = datetime.now(timezone.utc)
            start_time = end_time - timedelta(minutes=5)
            
            buckets = self.aw_client.get_buckets()
            window_bucket = None
            
            for bucket_id in buckets.keys():
                if "window" in bucket_id:
                    window_bucket = bucket_id
                    break
                    
            if window_bucket:
                events = self.aw_client.get_events(
                    window_bucket,
                    start=start_time,
                    end=end_time,
                    limit=10
                )
                
                if events:
                    # 收集最近的活动数据
                    activity_data = []
                    for event in events[:5]:  # 取最近5个事件
                        app = event.data.get('app', '')
                        title = event.data.get('title', '')
                        if app or title:
                            activity_data.append(f"应用: {app}, 标题: {title}")
                    
                    if activity_data:
                        # 使用AI分析活动类型
                        activity_type = self._analyze_activity_with_ai(activity_data)
                        if activity_type:
                            logger.info(f"AI analyzed activity type: {activity_type}")
                            return activity_type
            
            return "general"
            
        except Exception as e:
            logger.debug(f"Failed to get activity type: {e}")
            return "general"
    
    def _analyze_activity_with_ai(self, activity_data: List[str]) -> Optional[str]:
        """
        使用AI分析用户活动类型
        
        Args:
            activity_data: 活动数据列表
            
        Returns:
            活动类型：productive/browsing/gaming/general
        """
        if not self.llm:
            return None
            
        try:
            # 准备活动数据描述
            activities_text = "\n".join(activity_data[:5])  # 最多5条
            
            # 保存分析的活动详情
            self._last_analyzed_activities = activities_text
            
            # AI分析提示词
            prompt = f"""分析以下用户的电脑活动记录，判断用户主要在做什么。

用户最近的活动记录：
{activities_text}

请分析并返回用户的活动类型，只能选择以下其中一个：
1. productive - 工作/学习（编程、文档、学习网站等）
2. browsing - 休闲浏览（新闻、社交媒体、视频等）  
3. gaming - 游戏娱乐（游戏、游戏平台等）
4. general - 其他活动（无法明确分类）

分析要点：
- IDE/编辑器：VSCode、PyCharm、IntelliJ、Sublime、Vim、Emacs、Xcode等 → productive
- 开发工具：Terminal、Git、Docker、Postman、数据库工具等 → productive
- 办公软件：Word、Excel、PowerPoint、Notion、Obsidian、文档编辑等 → productive
- 学习网站：GitHub、StackOverflow、技术博客、在线课程、文档网站等 → productive
- 设计工具：Photoshop、Figma、Sketch等 → productive

- 社交媒体：Twitter、Facebook、Instagram、微博、小红书等 → browsing
- 视频网站：YouTube、Bilibili、Netflix、抖音等 → browsing
- 新闻网站：新闻门户、资讯网站等 → browsing
- 购物网站：淘宝、京东、Amazon等 → browsing
- 论坛社区：Reddit、知乎、贴吧等（非技术类）→ browsing

- 游戏：任何游戏名称、游戏客户端 → gaming
- 游戏平台：Steam、Epic、暴雪战网、WeGame等 → gaming
- 游戏相关：Twitch、游戏论坛、游戏攻略等 → gaming

- 系统工具：Finder、资源管理器、系统设置等 → general
- 通讯工具：微信、QQ、Telegram等（如果不是工作相关）→ general
- 其他无法分类的应用 → general

只返回类型名称（如：productive），不要有其他内容。"""
            
            messages = [
                SystemMessage(content="你是一个活动分析助手，根据用户的应用使用记录判断活动类型。只返回指定的类型名称。"),
                HumanMessage(content=prompt)
            ]
            
            # 使用较低的temperature确保稳定输出
            if hasattr(self.llm, 'temperature'):
                original_temp = self.llm.temperature
                self.llm.temperature = 0.1
            
            response = self.llm.invoke(messages)
            activity_type = response.content.strip().lower()
            
            # 恢复原始temperature
            if hasattr(self.llm, 'temperature'):
                self.llm.temperature = original_temp
            
            # 验证返回值
            if activity_type in ['productive', 'browsing', 'gaming', 'general']:
                return activity_type
            else:
                logger.warning(f"AI returned invalid activity type: {activity_type}")
                return "general"
                
        except Exception as e:
            logger.error(f"Failed to analyze activity with AI: {e}")
            return None
    
    def on_user_activity(self):
        """用户活动时调用"""
        current_time = time.time()
        
        # 检查是否从AFK返回
        if self.is_afk:
            afk_duration = current_time - self.afk_start_time
            self._handle_afk_return(afk_duration)
            self.is_afk = False
            self.afk_start_time = None
        
        # 更新活动时间
        self.last_active_time = current_time
        self.last_interaction_time = current_time
        
        # 重置闲置通知
        self.idle_notified_levels.clear()
    
    def _check_greeting(self):
        """检查是否需要发送问候"""
        now = datetime.now()
        today = now.date()
        
        # 如果今天已经问候过，跳过
        if self.last_greeting_date == today:
            return
        
        # 确定问候类型
        hour = now.hour
        if 6 <= hour < 9:
            greeting_type = "morning"
        elif 11 <= hour < 13:
            greeting_type = "noon"
        elif 17 <= hour < 19:
            greeting_type = "evening"
        elif 21 <= hour < 24 or 0 <= hour < 3:
            greeting_type = "night"
        else:
            return
        
        # 避免重复问候
        if self.last_greeting_type == greeting_type and self.last_greeting_date == today:
            return
        
        # 生成问候
        context = {
            'time': now.strftime("%H:%M"),
            'template_key': greeting_type
        }
        
        message = self._generate_ai_response(DialogueType.GREETING, context)
        if not message:
            message = self._get_fallback_message(DialogueType.GREETING, context)
        
        self.trigger_dialogue.emit(DialogueType.GREETING.value, message)
        self.last_greeting_date = today
        self.last_greeting_type = greeting_type
        logger.info(f"Triggered {greeting_type} greeting: {message}")
    
    def _check_idle(self):
        """检查闲置状态"""
        current_time = time.time()
        idle_duration = current_time - self.last_active_time
        
        # 转换为分钟
        idle_minutes = idle_duration / 60
        
        # 确定闲置级别
        if 5 <= idle_minutes < 15:
            idle_level = "short"
        elif 15 <= idle_minutes < 30:
            idle_level = "medium"
        elif idle_minutes >= 30:
            idle_level = "long"
        else:
            idle_level = None
        
        # 如果达到闲置级别且未通知过
        if idle_level and idle_level not in self.idle_notified_levels:
            context = {
                'duration': int(idle_minutes),
                'template_key': idle_level
            }
            
            message = self._generate_ai_response(DialogueType.IDLE_CARE, context)
            if not message:
                message = self._get_fallback_message(DialogueType.IDLE_CARE, context)
            
            self.trigger_dialogue.emit(DialogueType.IDLE_CARE.value, message)
            self.idle_notified_levels.add(idle_level)
            logger.info(f"Triggered idle care ({idle_level}): {message}")
        
        # 检查AFK状态
        if idle_duration > self.afk_threshold and not self.is_afk:
            self.is_afk = True
            self.afk_start_time = current_time
            self.last_activity_type = self.get_recent_activity_type()
            # 保存活动详情以便后续使用
            self.last_activity_detail = getattr(self, '_last_analyzed_activities', '')
            logger.info(f"Entered AFK state, previous activity: {self.last_activity_type}")
    
    def _check_state_transition(self):
        """检查状态转换"""
        current_segment = self.state_system.get_time_of_day()
        
        # 如果时间段发生变化
        if self.last_time_segment and self.last_time_segment != current_segment:
            context = {
                'from_time': self._translate_time_segment(self.last_time_segment),
                'to_time': self._translate_time_segment(current_segment),
                'template_key': 'default'
            }
            
            message = self._generate_ai_response(DialogueType.STATE_TRANSITION, context)
            if not message:
                message = self._get_fallback_message(DialogueType.STATE_TRANSITION, context)
            
            self.trigger_dialogue.emit(DialogueType.STATE_TRANSITION.value, message)
            logger.info(f"Triggered state transition: {self.last_time_segment.value} -> {current_segment.value}")
        
        self.last_time_segment = current_segment
    
    def _check_random_chat(self):
        """检查是否触发随机互动"""
        current_time = time.time()
        
        # 检查冷却时间（至少30分钟间隔）
        if current_time < self.random_chat_cooldown:
            return
        
        # 检查最近是否有互动（5分钟内有互动则不打扰）
        if current_time - self.last_interaction_time < 300:
            return
        
        # 20%的概率触发随机互动
        if random.random() < 0.2:
            # 随机选择话题类型
            topic_types = ['work', 'life', 'philosophy']
            topic_type = random.choice(topic_types)
            
            context = {
                'template_key': topic_type
            }
            
            message = self._generate_ai_response(DialogueType.RANDOM_CHAT, context)
            if not message:
                message = self._get_fallback_message(DialogueType.RANDOM_CHAT, context)
            
            self.trigger_dialogue.emit(DialogueType.RANDOM_CHAT.value, message)
            self.random_chat_cooldown = current_time + 1800  # 30分钟冷却
            logger.info(f"Triggered random chat ({topic_type}): {message}")
    
    def _handle_afk_return(self, afk_duration: float):
        """处理AFK回归"""
        # 准备上下文
        afk_minutes = int(afk_duration / 60)
        
        # 如果有详细的活动描述，添加到上下文
        context = {
            'duration': afk_minutes,
            'template_key': self.last_activity_type,
            'activity_detail': ''  # 默认为空
        }
        
        # 如果有具体的活动详情，可以添加到提示中
        if hasattr(self, 'last_activity_detail') and self.last_activity_detail:
            # 格式化活动详情为更自然的描述
            context['activity_detail'] = f"之前的活动记录：\n{self.last_activity_detail}\n"
        else:
            context['activity_detail'] = ''
        
        message = self._generate_ai_response(DialogueType.AFK_RETURN, context)
        if not message:
            message = self._get_fallback_message(DialogueType.AFK_RETURN, context)
        
        # 添加AFK时长信息（如果超过10分钟）
        if afk_minutes > 10:
            message += f"（离开了{afk_minutes}分钟）"
        
        self.trigger_dialogue.emit(DialogueType.AFK_RETURN.value, message)
        logger.info(f"Triggered AFK return care: {message}")
    
    def _translate_time_segment(self, segment: TimeOfDay) -> str:
        """
        翻译时间段名称
        
        Args:
            segment: 时间段枚举
            
        Returns:
            中文时间段名称
        """
        translations = {
            TimeOfDay.MORNING: "早晨",
            TimeOfDay.NOON: "中午",
            TimeOfDay.AFTERNOON: "下午",
            TimeOfDay.EVENING: "傍晚",
            TimeOfDay.NIGHT: "夜晚",
            TimeOfDay.LATE_NIGHT: "深夜"
        }
        return translations.get(segment, segment.value)
    
    def get_dialogue_context(self, dialogue_type: DialogueType) -> Dict[str, Any]:
        """
        获取特定对话类型的上下文
        
        Args:
            dialogue_type: 对话类型
            
        Returns:
            对话上下文字典
        """
        context = {
            "type": dialogue_type.value,
            "timestamp": datetime.now().isoformat(),
            "time_of_day": self.state_system.get_time_of_day().value,
            "mood": self.state_system.get_random_mood(),
        }
        
        # 添加类型特定的上下文
        if dialogue_type == DialogueType.IDLE_CARE:
            idle_duration = time.time() - self.last_active_time
            context["idle_duration"] = idle_duration
            context["idle_minutes"] = int(idle_duration / 60)
        
        elif dialogue_type == DialogueType.AFK_RETURN:
            context["afk_duration"] = time.time() - self.afk_start_time if self.afk_start_time else 0
            context["previous_activity"] = self.last_activity_type
        
        elif dialogue_type == DialogueType.STATE_TRANSITION:
            context["from_state"] = self.last_time_segment.value if self.last_time_segment else None
            context["to_state"] = self.state_system.get_time_of_day().value
        
        return context
    
    def cleanup(self):
        """清理资源"""
        # 停止所有定时器
        self.greeting_timer.stop()
        self.idle_timer.stop()
        self.state_timer.stop()
        self.random_timer.stop()
        
        # 清理缓存
        self.response_cache.clear()
        
        logger.info("Proactive dialogue manager cleaned up")


# 单例实例
_dialogue_manager_instance = None


def get_dialogue_manager() -> ProactiveDialogueManager:
    """获取主动对话管理器单例"""
    global _dialogue_manager_instance
    if _dialogue_manager_instance is None:
        _dialogue_manager_instance = ProactiveDialogueManager()
    return _dialogue_manager_instance


def update_persona_in_dialogue_manager(persona_level: PersonaLevel):
    """
    更新主动对话管理器的人设
    
    Args:
        persona_level: 新的人设档位
    """
    manager = get_dialogue_manager()
    manager.update_persona_level(persona_level)