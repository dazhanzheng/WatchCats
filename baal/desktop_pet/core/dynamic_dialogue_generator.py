"""
动态对话生成器

完全基于AI的动态对话生成系统，替代所有预设对话
支持多样化的提示词、心情状态、随机因素
"""

import random
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Callable
from enum import Enum
from .persona_manager import PersonaLevel
from .logger_config import get_logger

logger = get_logger('dynamic_dialogue')


class DialogueContext(Enum):
    """对话场景枚举"""
    # 用户交互
    DOUBLE_CLICK = "double_click"          # 双击召唤
    WELCOME = "welcome"                    # 欢迎新用户
    MORNING_GREETING = "morning_greeting"  # 早晨问候
    LATE_NIGHT = "late_night"             # 深夜关怀
    LONG_TIME_NO_SEE = "long_time_no_see" # 长时间未见
    FREQUENT_INTERACTION = "frequent_interaction"  # 频繁互动
    
    # 系统状态
    API_NOT_CONFIGURED = "api_not_configured"  # API未配置
    API_CONFIGURED = "api_configured"          # API配置成功
    POSITION_RESET = "position_reset"          # 位置重置
    ALWAYS_ON_TOP_ENABLE = "always_on_top_enable"  # 置顶启用
    ALWAYS_ON_TOP_DISABLE = "always_on_top_disable" # 置顶禁用
    
    # 监督模式
    SUPERVISION_START = "supervision_start"    # 监督开始
    SUPERVISION_STOP = "supervision_stop"      # 监督停止
    SUPERVISION_REMINDER = "supervision_reminder"  # 监督提醒
    GOALS_UPDATED = "goals_updated"           # 目标更新
    
    # 记忆管理
    MEMORY_CLEARED = "memory_cleared"         # 记忆清除
    MEMORY_CLEAR_FAILED = "memory_clear_failed"  # 清除失败
    NO_MEMORY_TO_CLEAR = "no_memory_to_clear"   # 无记忆
    
    # 错误处理
    ERROR_GENERAL = "error_general"           # 一般错误
    ERROR_CHAT = "error_chat"                # 对话错误
    ERROR_API = "error_api"                  # API错误


class MoodState:
    """心情状态管理"""
    
    @staticmethod
    def get_mood_by_context(context: DialogueContext, persona: PersonaLevel) -> int:
        """根据场景和人设获取合适的心情值"""
        # 心情映射表
        mood_map = {
            PersonaLevel.STRICT_MASTER: {
                DialogueContext.DOUBLE_CLICK: random.choice([3, 4, 5, 6]),  # 不耐烦到生气
                DialogueContext.WELCOME: 5,  # 威严
                DialogueContext.MORNING_GREETING: random.choice([4, 5]),  # 严肃
                DialogueContext.LATE_NIGHT: random.choice([3, 4]),  # 略微关心
                DialogueContext.LONG_TIME_NO_SEE: random.choice([4, 5, 6]),  # 不满
                DialogueContext.FREQUENT_INTERACTION: random.choice([5, 6, 7]),  # 烦躁
                DialogueContext.API_CONFIGURED: random.choice([2, 3]),  # 满意
                DialogueContext.SUPERVISION_START: 5,  # 严肃
                DialogueContext.SUPERVISION_REMINDER: random.choice([6, 7]),  # 生气
                DialogueContext.ERROR_GENERAL: 6,  # 不满
            },
            PersonaLevel.SARCASTIC_BUTLER: {
                DialogueContext.DOUBLE_CLICK: random.choice([3, 4, 5]),  # 讽刺
                DialogueContext.WELCOME: 4,  # 假装恭敬
                DialogueContext.MORNING_GREETING: random.choice([3, 4]),  # 嘲讽
                DialogueContext.LATE_NIGHT: random.choice([4, 5]),  # 毒舌关心
                DialogueContext.LONG_TIME_NO_SEE: random.choice([3, 4]),  # 假装惊讶
                DialogueContext.FREQUENT_INTERACTION: random.choice([4, 5]),  # 讽刺
                DialogueContext.API_CONFIGURED: random.choice([2, 3]),  # 假装高兴
                DialogueContext.SUPERVISION_START: 4,  # 讽刺期待
                DialogueContext.SUPERVISION_REMINDER: random.choice([4, 5]),  # 优雅嘲讽
                DialogueContext.ERROR_GENERAL: 4,  # 嘲讽
            },
            PersonaLevel.GENTLE_COMPANION: {
                DialogueContext.DOUBLE_CLICK: random.choice([1, 2]),  # 开心
                DialogueContext.WELCOME: 1,  # 欢迎
                DialogueContext.MORNING_GREETING: random.choice([1, 2]),  # 活泼
                DialogueContext.LATE_NIGHT: random.choice([2, 5]),  # 关心
                DialogueContext.LONG_TIME_NO_SEE: random.choice([1, 2]),  # 想念
                DialogueContext.FREQUENT_INTERACTION: random.choice([1, 2]),  # 开心
                DialogueContext.API_CONFIGURED: 1,  # 高兴
                DialogueContext.SUPERVISION_START: 2,  # 鼓励
                DialogueContext.SUPERVISION_REMINDER: random.choice([2, 5]),  # 温柔提醒
                DialogueContext.ERROR_GENERAL: 5,  # 安慰
            }
        }
        
        # 获取对应的心情值
        persona_moods = mood_map.get(persona, mood_map[PersonaLevel.STRICT_MASTER])
        return persona_moods.get(context, 5)  # 默认平静


class RandomFactors:
    """随机因素生成器"""
    
    @staticmethod
    def get_time_factor() -> Dict[str, Any]:
        """获取时间相关因素"""
        now = datetime.now()
        hour = now.hour
        
        return {
            'hour': hour,
            'time_period': RandomFactors._get_time_period(hour),
            'weekday': now.strftime('%A'),
            'is_weekend': now.weekday() >= 5,
            'date': now.strftime('%Y年%m月%d日'),
            'season': RandomFactors._get_season(now.month),
            'is_holiday': RandomFactors._check_holiday(now),
        }
    
    @staticmethod
    def _get_time_period(hour: int) -> str:
        """获取时间段"""
        if 5 <= hour < 9:
            return "清晨"
        elif 9 <= hour < 12:
            return "上午"
        elif 12 <= hour < 14:
            return "中午"
        elif 14 <= hour < 18:
            return "下午"
        elif 18 <= hour < 22:
            return "晚上"
        else:
            return "深夜"
    
    @staticmethod
    def _get_season(month: int) -> str:
        """获取季节"""
        if month in [3, 4, 5]:
            return "春天"
        elif month in [6, 7, 8]:
            return "夏天"
        elif month in [9, 10, 11]:
            return "秋天"
        else:
            return "冬天"
    
    @staticmethod
    def _check_holiday(date: datetime) -> str:
        """检查是否是节日"""
        # 简单的节日检查（可扩展）
        holidays = {
            (1, 1): "元旦",
            (2, 14): "情人节",
            (3, 8): "妇女节",
            (5, 1): "劳动节",
            (6, 1): "儿童节",
            (10, 1): "国庆节",
            (12, 25): "圣诞节",
        }
        
        key = (date.month, date.day)
        return holidays.get(key, "")
    
    @staticmethod
    def get_random_detail() -> str:
        """获取随机细节"""
        details = [
            "今天天气不错",
            "外面在下雨",
            "阳光明媚",
            "有点冷",
            "风很大",
            "空气清新",
            "有点闷热",
            "凉爽舒适",
        ]
        return random.choice(details)
    
    @staticmethod
    def get_activity_hint() -> str:
        """获取活动暗示"""
        hints = [
            "看起来很忙",
            "似乎有点累",
            "精神不错",
            "需要休息",
            "工作很久了",
            "刚刚开始",
            "快完成了",
            "进展顺利",
        ]
        return random.choice(hints)


class DynamicDialogueGenerator:
    """动态对话生成器"""
    
    def __init__(self, llm_handler=None):
        """
        初始化动态对话生成器
        
        Args:
            llm_handler: LLM处理器实例
        """
        self.llm_handler = llm_handler
        self.logger = logger
        self.response_callbacks = {}  # 存储响应回调
        
    def generate(self, 
                context: DialogueContext,
                persona: PersonaLevel,
                callback: Optional[Callable] = None,
                **kwargs) -> str:
        """
        生成动态对话（异步）
        
        Args:
            context: 对话场景
            persona: 人设档位
            callback: 完成回调函数
            **kwargs: 额外参数
            
        Returns:
            str: 立即返回加载提示
        """
        # 立即返回加载动画
        loading_messages = {
            PersonaLevel.STRICT_MASTER: "<#5>...",
            PersonaLevel.SARCASTIC_BUTLER: "<#3>在下思考中...",
            PersonaLevel.GENTLE_COMPANION: "<#2>让我想想..."
        }
        
        # 如果有回调，启动异步生成
        if callback and self.llm_handler:
            self._generate_async(context, persona, callback, **kwargs)
        
        return loading_messages.get(persona, "<#5>...")
    
    def _generate_async(self, 
                       context: DialogueContext,
                       persona: PersonaLevel,
                       callback: Callable,
                       **kwargs):
        """异步生成对话"""
        import threading
        
        def generate_task():
            try:
                response = self._generate_response(context, persona, **kwargs)
                callback(response)
            except Exception as e:
                logger.error(f"Failed to generate dialogue: {e}")
                # 使用后备响应
                fallback = self._get_fallback_response(context, persona)
                callback(fallback)
        
        thread = threading.Thread(target=generate_task, daemon=True)
        thread.start()
    
    def _generate_response(self,
                          context: DialogueContext,
                          persona: PersonaLevel,
                          **kwargs) -> str:
        """
        实际生成响应
        
        Args:
            context: 对话场景
            persona: 人设档位
            **kwargs: 额外参数
            
        Returns:
            str: 生成的对话文本
        """
        if not self.llm_handler:
            return self._get_fallback_response(context, persona)
        
        # 获取心情
        mood = MoodState.get_mood_by_context(context, persona)
        
        # 获取随机因素
        time_factors = RandomFactors.get_time_factor()
        random_detail = RandomFactors.get_random_detail()
        activity_hint = RandomFactors.get_activity_hint()
        
        # 构建丰富的提示词
        prompt = self._build_prompt(
            context=context,
            persona=persona,
            mood=mood,
            time_factors=time_factors,
            random_detail=random_detail,
            activity_hint=activity_hint,
            **kwargs
        )
        
        # 调用LLM生成
        try:
            response = self.llm_handler.generate_dynamic_response(
                context=context.value,
                mood=mood,
                parameters={
                    'prompt': prompt,
                    'time': time_factors['time_period'],
                    'detail': random_detail,
                    **kwargs
                }
            )
            return response
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            return self._get_fallback_response(context, persona)
    
    def _build_prompt(self,
                     context: DialogueContext,
                     persona: PersonaLevel,
                     mood: int,
                     time_factors: Dict,
                     random_detail: str,
                     activity_hint: str,
                     **kwargs) -> str:
        """构建提示词"""
        
        # 基础场景描述
        context_prompts = {
            DialogueContext.DOUBLE_CLICK: f"""
用户双击召唤了你。
时间：{time_factors['time_period']}
环境：{random_detail}
用户状态：{activity_hint}
特殊：{time_factors.get('is_holiday', '') or '普通日子'}

生成一句符合当前情境的招呼语。
可以包含：
- 对时间的评论
- 对用户状态的观察
- 对环境的感受
- 偶尔的小抱怨或关心
""",
            DialogueContext.WELCOME: f"""
这是新用户第一次启动应用。
时间：{time_factors['date']} {time_factors['time_period']}
季节：{time_factors['season']}

生成一句欢迎词，介绍自己并建立第一印象。
""",
            DialogueContext.MORNING_GREETING: f"""
早晨问候。
时间：{time_factors['hour']}点
天气：{random_detail}
今天是：{time_factors['weekday']}

生成符合早晨氛围的问候语。
""",
            DialogueContext.LATE_NIGHT: f"""
深夜时分。
时间：{time_factors['hour']}点
用户还在活动。

生成关心但符合人设的深夜提醒。
""",
            DialogueContext.LONG_TIME_NO_SEE: f"""
很久没有互动了。
上次见面：{kwargs.get('last_seen', '很久之前')}
当前：{time_factors['time_period']}

生成重逢的反应。
""",
            DialogueContext.FREQUENT_INTERACTION: f"""
用户频繁召唤你。
短时间内第{kwargs.get('count', 3)}次互动。

生成对频繁打扰的反应。
""",
            DialogueContext.API_NOT_CONFIGURED: f"""
用户想要对话，但还没有配置API密钥。

提醒用户需要先设置。
""",
            DialogueContext.API_CONFIGURED: f"""
API密钥配置成功。
可以开始正常对话了。

表达对此的反应。
""",
            DialogueContext.SUPERVISION_START: f"""
监督模式启动。
目标：{kwargs.get('goal', '提高效率')}
时间：{time_factors['time_period']}

表达开始监督的态度。
""",
            DialogueContext.SUPERVISION_REMINDER: f"""
监督提醒。
偏离程度：{kwargs.get('deviation', '中度')}
当前活动：{kwargs.get('activity', '未知')}

根据偏离程度给出提醒。
""",
        }
        
        base_prompt = context_prompts.get(context, f"场景：{context.value}")
        
        # 添加人设特定的指导
        persona_guides = {
            PersonaLevel.STRICT_MASTER: """
态度：威严、命令式、略带不耐烦
称呼：使用"仆人"、"你"
语气：简短有力，偶尔流露关心但要掩饰
特点：享受支配地位，对懒惰零容忍
""",
            PersonaLevel.SARCASTIC_BUTLER: """
态度：表面恭敬，实则充满讽刺
称呼：使用"主人"，但语气要有反差
语气：优雅但毒舌，暗示与明示并用
特点：用"职责"掩饰关心，精通话里有话
""",
            PersonaLevel.GENTLE_COMPANION: """
态度：温柔体贴，真诚关怀
称呼：使用"亲爱的"、"朋友"
语气：温暖鼓励，积极向上
特点：真心为用户着想，会撒娇卖萌
"""
        }
        
        full_prompt = f"""
{base_prompt}

人设要求：
{persona_guides.get(persona, '')}

心情状态：{mood}（1=开心，7=愤怒）

要求：
1. 20字以内
2. 必须符合人设
3. 自然且有变化
4. 加入适当的情绪表达
"""
        
        return full_prompt
    
    def _get_fallback_response(self,
                              context: DialogueContext,
                              persona: PersonaLevel) -> str:
        """获取后备响应"""
        # 简单的后备响应表
        fallbacks = {
            PersonaLevel.STRICT_MASTER: {
                DialogueContext.DOUBLE_CLICK: "<#5>什么事，仆人？",
                DialogueContext.WELCOME: "<#5>我是巴利，你的监督者。",
                DialogueContext.MORNING_GREETING: "<#5>起床工作，别偷懒。",
                DialogueContext.LATE_NIGHT: "<#4>还不睡？明天还要工作。",
                DialogueContext.API_NOT_CONFIGURED: "<#6>先去设置密钥，仆人。",
                DialogueContext.SUPERVISION_START: "<#5>监督开始，别想偷懒。",
            },
            PersonaLevel.SARCASTIC_BUTLER: {
                DialogueContext.DOUBLE_CLICK: "<#3>主人有何吩咐？",
                DialogueContext.WELCOME: "<#4>在下是您'忠诚'的管家。",
                DialogueContext.MORNING_GREETING: "<#3>主人'早起'真令人'惊讶'。",
                DialogueContext.LATE_NIGHT: "<#5>主人的作息真'健康'。",
                DialogueContext.API_NOT_CONFIGURED: "<#4>主人需要先设置密钥呢。",
                DialogueContext.SUPERVISION_START: "<#4>期待主人的'表现'。",
            },
            PersonaLevel.GENTLE_COMPANION: {
                DialogueContext.DOUBLE_CLICK: "<#1>嗨！有什么可以帮你的？",
                DialogueContext.WELCOME: "<#1>你好！我是巴利，很高兴认识你！",
                DialogueContext.MORNING_GREETING: "<#1>早安！今天也要加油哦！",
                DialogueContext.LATE_NIGHT: "<#5>很晚了，要注意休息哦。",
                DialogueContext.API_NOT_CONFIGURED: "<#5>需要先设置密钥哦，我帮你。",
                DialogueContext.SUPERVISION_START: "<#2>一起努力吧！我会陪着你的。",
            }
        }
        
        persona_fallbacks = fallbacks.get(persona, fallbacks[PersonaLevel.STRICT_MASTER])
        return persona_fallbacks.get(context, "<#5>喵~")


# 全局实例
_generator_instance = None

def get_dialogue_generator(llm_handler=None) -> DynamicDialogueGenerator:
    """获取全局对话生成器实例"""
    global _generator_instance
    if _generator_instance is None:
        _generator_instance = DynamicDialogueGenerator(llm_handler)
    elif llm_handler and _generator_instance.llm_handler is None:
        _generator_instance.llm_handler = llm_handler
    return _generator_instance

def generate_dialogue(context: DialogueContext,
                     persona: PersonaLevel,
                     callback: Optional[Callable] = None,
                     **kwargs) -> str:
    """
    便捷函数：生成动态对话
    
    Args:
        context: 对话场景
        persona: 人设档位
        callback: 完成回调函数
        **kwargs: 额外参数
        
    Returns:
        str: 立即返回加载提示或后备响应
    """
    generator = get_dialogue_generator()
    return generator.generate(context, persona, callback, **kwargs)