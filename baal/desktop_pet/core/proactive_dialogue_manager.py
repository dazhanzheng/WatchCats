"""
主动对话管理器

统一管理所有主动和被动对话功能
包括定时问候、闲置关怀、状态变化通知、随机互动等
"""

import time
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple, Any
from enum import Enum
from PyQt6.QtCore import QTimer, QObject, pyqtSignal
from .state_awareness import get_state_awareness, TimeOfDay, MoodCategory
from .state_extensions import get_state_extensions
from .state_update_manager import get_update_manager

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
    """主动对话管理器"""
    
    # 触发对话的信号
    trigger_dialogue = pyqtSignal(str, str)  # (对话类型, 消息内容)
    
    # 定时问候配置
    GREETING_TIMES = {
        "morning": {
            "hour_range": (6, 9),
            "messages": [
                "早安！新的一天开始了，准备好征服世界了吗？",
                "喵~太阳升起来了，该起床工作了！",
                "早上好！昨晚睡得怎么样？今天有什么计划？",
                "又是充满希望的一天呢，早安~",
                "晨光熹微，正是奋斗的好时候！",
                "早啊！我已经帮你规划好今天的任务了（其实没有）",
                "新的一天，新的开始，加油！",
                "太阳都晒屁股了，还不起来？",
            ]
        },
        "evening": {
            "hour_range": (20, 23),
            "messages": [
                "晚上好！今天过得怎么样？",
                "夜幕降临，是时候放松一下了",
                "累了一天了吧？要不要聊聊天？",
                "晚安之前，回顾一下今天的成就吧",
                "夜深了，记得早点休息哦",
                "月亮升起来了，今天的任务都完成了吗？",
                "晚上是思考的好时候，有什么想法吗？",
                "星星都出来了，该准备休息了",
            ]
        }
    }
    
    # 闲置关怀消息
    IDLE_MESSAGES = {
        "short": {  # 5-15分钟
            "duration": (5, 15),
            "messages": [
                "怎么不动了？是在思考人生吗？",
                "喂，还在吗？别走神啊",
                "休息一下也好，但别忘了工作",
                "发呆也是一种艺术呢",
                "在想什么呢？能告诉我吗？",
                "是遇到什么难题了吗？",
                "适当的停顿有助于思考",
                "需要我陪你聊聊天吗？",
            ]
        },
        "medium": {  # 15-30分钟
            "duration": (15, 30),
            "messages": [
                "离开这么久，是去喝水了吗？",
                "已经过了{}分钟了，一切还好吗？",
                "是时候回来工作了吧？",
                "我有点想你了...呸，谁会想你！",
                "去哪里了？不会是在摸鱼吧？",
                "这么久不见，是在开会吗？",
                "希望你在做有意义的事",
                "别忘了还有任务要完成哦",
            ]
        },
        "long": {  # 30分钟以上
            "duration": (30, float('inf')),
            "messages": [
                "太久没见了，我都要生锈了",
                "终于想起我了？我还以为你把我忘了",
                "消失了{}分钟，去拯救世界了？",
                "这么长时间不见，肯定是在认真工作吧",
                "欢迎回来！有什么收获吗？",
                "离开这么久，是不是该补偿我一下？",
                "我一个人守着电脑好无聊啊",
                "下次离开记得告诉我一声",
            ]
        }
    }
    
    # AFK回归关怀（基于之前的活动）
    AFK_RETURN_MESSAGES = {
        "productive": [  # 之前在高效工作
            "欢迎回来！之前的工作完成了吗？",
            "休息好了？让我们继续之前的任务吧",
            "回来了！刚才的代码写完了吗？",
            "精神焕发地回来了呢，继续加油！",
            "休息是为了更好的工作，现在继续吧",
        ],
        "browsing": [  # 之前在浏览网页
            "回来了？刚才看到什么有趣的东西了吗？",
            "浏览够了吧？该做点正事了",
            "网上冲浪结束了？分享一下有趣的发现吧",
            "希望刚才不是在看猫片...虽然我不介意",
        ],
        "gaming": [  # 之前在玩游戏
            "游戏打完了？战绩如何？",
            "玩够了吧？该回到现实世界了",
            "赢了还是输了？不管怎样，该工作了",
            "游戏虽好，可不要贪玩哦",
        ],
        "general": [  # 一般情况
            "回来了！准备好继续了吗？",
            "欢迎回来！有什么新想法吗？",
            "终于回来了，我都等着急了",
            "回来就好，让我们开始吧",
        ]
    }
    
    # 状态转换通知
    STATE_TRANSITIONS = {
        TimeOfDay.MORNING: [
            "早晨的阳光洒进来，新的一天开始了！",
            "晨光初现，是时候开始今天的征程了",
            "鸟儿开始歌唱，美好的早晨来临了",
        ],
        TimeOfDay.NOON: [
            "中午了，该考虑吃点什么了",
            "太阳当空照，记得补充能量",
            "午餐时间到！吃饱了才有力气工作",
        ],
        TimeOfDay.AFTERNOON: [
            "下午了，保持专注，效率最高的时段",
            "午后时光，适合处理重要任务",
            "下午的阳光很温暖，但别打瞌睡哦",
        ],
        TimeOfDay.EVENING: [
            "傍晚了，今天的任务完成得怎么样？",
            "夕阳西下，是时候总结今天了",
            "晚霞很美，但别忘了还有工作",
        ],
        TimeOfDay.NIGHT: [
            "夜幕降临，进入深度工作时间",
            "夜晚的宁静适合思考",
            "星星出来了，你还在努力吗？",
        ],
        TimeOfDay.LATE_NIGHT: [
            "夜深了，注意休息哦",
            "深夜工作效率高，但也要保重身体",
            "月亮都困了，你还不睡吗？",
        ],
    }
    
    # 随机互动话题
    RANDOM_TOPICS = [
        # 工作相关
        "最近在忙什么项目？需要我帮忙吗？",
        "今天的代码写得怎么样？有遇到bug吗？",
        "有什么有趣的技术发现想分享吗？",
        "最近学到什么新技能了吗？",
        
        # 生活关怀
        "喝水了吗？程序员要多喝水",
        "眼睛累了吧？看看远处休息一下",
        "坐太久了，起来活动活动？",
        "今天吃了什么好吃的？",
        
        # 轻松话题
        "你知道吗？猫一天要睡16个小时呢",
        "如果我有实体，我想去你的键盘上躺着",
        "其实我也想学编程，但是没有手...",
        "你觉得AI会梦到电子羊吗？",
        
        # 鼓励支持
        "我觉得你今天状态不错！",
        "虽然我总是很严格，但你真的很努力",
        "每天都在进步，真棒！",
        "困难只是暂时的，你一定能解决",
        
        # 哲学思考
        "你觉得代码是艺术还是工程？",
        "如果可以重来，你还会选择这个职业吗？",
        "人生就像编程，总有bug要修",
        "完美的代码存在吗？",
    ]
    
    def __init__(self):
        """初始化主动对话管理器"""
        super().__init__()
        
        # 获取其他管理器
        self.state_system = get_state_awareness()
        self.extension_manager = get_state_extensions()
        self.update_manager = get_update_manager()
        
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
        
    def initialize_aw_client(self):
        """初始化ActivityWatch客户端"""
        try:
            from aw_client import ActivityWatchClient
            self.aw_client = ActivityWatchClient("baal-pet")
            logger.info("ActivityWatch客户端初始化成功")
        except Exception as e:
            logger.warning(f"ActivityWatch客户端初始化失败: {e}")
            self.aw_client = None
    
    def get_afk_status(self) -> Tuple[bool, Optional[float]]:
        """
        获取AFK状态
        
        Returns:
            (是否AFK, AFK持续时间秒数)
        """
        if not self.aw_client:
            # 如果没有AW客户端，使用本地追踪
            current_time = time.time()
            idle_duration = current_time - self.last_active_time
            is_afk = idle_duration > self.afk_threshold
            return is_afk, idle_duration if is_afk else None
        
        try:
            # 尝试从ActivityWatch获取AFK状态
            buckets = self.aw_client.get_buckets()
            afk_bucket = None
            
            # 查找AFK bucket
            for bucket_id in buckets:
                if 'afk' in bucket_id.lower():
                    afk_bucket = bucket_id
                    break
            
            if afk_bucket:
                # 获取最近的AFK事件
                events = self.aw_client.get_events(
                    afk_bucket,
                    limit=1,
                    start=datetime.now() - timedelta(minutes=5)
                )
                
                if events:
                    latest_event = events[0]
                    status = latest_event.data.get('status', 'not-afk')
                    if status == 'afk':
                        duration = latest_event.duration.total_seconds()
                        return True, duration
            
            return False, None
            
        except Exception as e:
            logger.debug(f"获取AFK状态失败: {e}")
            # 降级到本地追踪
            return self.get_afk_status()
    
    def get_recent_activity_type(self) -> str:
        """
        获取最近的活动类型
        
        Returns:
            活动类型: productive/browsing/gaming/general
        """
        if not self.aw_client:
            return self.last_activity_type
        
        try:
            # 获取最近15分钟的活动
            buckets = self.aw_client.get_buckets()
            window_bucket = None
            
            for bucket_id in buckets:
                if 'window' in bucket_id.lower():
                    window_bucket = bucket_id
                    break
            
            if window_bucket:
                events = self.aw_client.get_events(
                    window_bucket,
                    start=datetime.now() - timedelta(minutes=15),
                    limit=10
                )
                
                if events:
                    # 分析最近的应用使用
                    for event in events:
                        app = event.data.get('app', '').lower()
                        title = event.data.get('title', '').lower()
                        
                        # 判断活动类型
                        if any(keyword in app for keyword in ['code', 'pycharm', 'idea', 'vim']):
                            return "productive"
                        elif any(keyword in app for keyword in ['chrome', 'firefox', 'safari']):
                            if any(keyword in title for keyword in ['github', 'stackoverflow', 'docs']):
                                return "productive"
                            else:
                                return "browsing"
                        elif any(keyword in app for keyword in ['game', 'steam']):
                            return "gaming"
            
            return "general"
            
        except Exception as e:
            logger.debug(f"获取活动类型失败: {e}")
            return "general"
    
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
        
        # 检查早晚问候时间
        for greeting_type, config in self.GREETING_TIMES.items():
            hour_range = config["hour_range"]
            if hour_range[0] <= now.hour < hour_range[1]:
                # 避免重复问候
                if self.last_greeting_type != greeting_type or self.last_greeting_date != today:
                    message = random.choice(config["messages"])
                    self.trigger_dialogue.emit(DialogueType.GREETING.value, message)
                    self.last_greeting_date = today
                    self.last_greeting_type = greeting_type
                    logger.info(f"触发{greeting_type}问候: {message}")
                    break
    
    def _check_idle(self):
        """检查闲置状态"""
        current_time = time.time()
        idle_duration = current_time - self.last_active_time
        
        # 转换为分钟
        idle_minutes = idle_duration / 60
        
        # 确定闲置级别
        idle_level = None
        for level, config in self.IDLE_MESSAGES.items():
            duration_range = config["duration"]
            if duration_range[0] <= idle_minutes < duration_range[1]:
                idle_level = level
                break
        
        # 如果达到闲置级别且未通知过
        if idle_level and idle_level not in self.idle_notified_levels:
            messages = self.IDLE_MESSAGES[idle_level]["messages"]
            message = random.choice(messages)
            
            # 格式化消息中的时间占位符
            if "{}" in message:
                message = message.format(int(idle_minutes))
            
            self.trigger_dialogue.emit(DialogueType.IDLE_CARE.value, message)
            self.idle_notified_levels.add(idle_level)
            logger.info(f"触发闲置关怀({idle_level}): {message}")
        
        # 检查AFK状态
        if idle_duration > self.afk_threshold and not self.is_afk:
            self.is_afk = True
            self.afk_start_time = current_time
            self.last_activity_type = self.get_recent_activity_type()
            logger.info(f"进入AFK状态，之前活动类型: {self.last_activity_type}")
    
    def _check_state_transition(self):
        """检查状态转换"""
        current_segment = self.state_system.get_time_of_day()
        
        # 如果时间段发生变化
        if self.last_time_segment and self.last_time_segment != current_segment:
            if current_segment in self.STATE_TRANSITIONS:
                message = random.choice(self.STATE_TRANSITIONS[current_segment])
                self.trigger_dialogue.emit(DialogueType.STATE_TRANSITION.value, message)
                logger.info(f"触发状态转换通知: {current_segment.value} - {message}")
        
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
            message = random.choice(self.RANDOM_TOPICS)
            self.trigger_dialogue.emit(DialogueType.RANDOM_CHAT.value, message)
            self.random_chat_cooldown = current_time + 1800  # 30分钟冷却
            logger.info(f"触发随机互动: {message}")
    
    def _handle_afk_return(self, afk_duration: float):
        """处理AFK回归"""
        # 根据之前的活动类型选择消息
        if self.last_activity_type in self.AFK_RETURN_MESSAGES:
            messages = self.AFK_RETURN_MESSAGES[self.last_activity_type]
        else:
            messages = self.AFK_RETURN_MESSAGES["general"]
        
        message = random.choice(messages)
        
        # 添加AFK时长信息（如果超过10分钟）
        if afk_duration > 600:
            afk_minutes = int(afk_duration / 60)
            message += f"（离开了{afk_minutes}分钟）"
        
        self.trigger_dialogue.emit(DialogueType.AFK_RETURN.value, message)
        logger.info(f"触发AFK回归关怀: {message}")
    
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
            "mood": "normal",  # 默认心情，StateAwarenessSystem暂时没有get_random_mood方法
        }
        
        # 添加类型特定的上下文
        if dialogue_type == DialogueType.IDLE_CARE:
            idle_duration = time.time() - self.last_active_time
            context["idle_duration"] = idle_duration
            context["idle_level"] = self._get_idle_level(idle_duration / 60)
        
        elif dialogue_type == DialogueType.AFK_RETURN:
            context["afk_duration"] = time.time() - self.afk_start_time if self.afk_start_time else 0
            context["previous_activity"] = self.last_activity_type
        
        elif dialogue_type == DialogueType.STATE_TRANSITION:
            context["from_state"] = self.last_time_segment.value if self.last_time_segment else None
            context["to_state"] = self.state_system.get_time_of_day().value
        
        return context
    
    def _get_idle_level(self, idle_minutes: float) -> str:
        """获取闲置级别"""
        for level, config in self.IDLE_MESSAGES.items():
            duration_range = config["duration"]
            if duration_range[0] <= idle_minutes < duration_range[1]:
                return level
        return "long"
    
    def format_message_with_context(self, base_message: str, context: Dict[str, Any]) -> str:
        """
        根据上下文格式化消息
        
        Args:
            base_message: 基础消息
            context: 上下文字典
            
        Returns:
            格式化后的消息
        """
        # 可以根据上下文添加额外信息
        formatted = base_message
        
        # 添加时间相关的修饰
        time_of_day = context.get("time_of_day")
        if time_of_day == "late_night" and random.random() < 0.3:
            formatted += "（*打了个哈欠*）"
        elif time_of_day == "morning" and random.random() < 0.3:
            formatted += "（*伸了个懒腰*）"
        
        # 添加心情相关的修饰
        mood = context.get("mood")
        if mood and random.random() < 0.2:
            if "grumpy" in mood:
                formatted += "（*不耐烦地甩尾巴*）"
            elif "playful" in mood:
                formatted += "（*调皮地眨眼*）"
            elif "affectionate" in mood:
                formatted += "（*蹭了蹭你*）"
        
        return formatted
    
    def should_trigger_dialogue(self, dialogue_type: DialogueType) -> bool:
        """
        判断是否应该触发特定类型的对话
        
        Args:
            dialogue_type: 对话类型
            
        Returns:
            是否应该触发
        """
        current_time = time.time()
        
        # 根据类型判断
        if dialogue_type == DialogueType.GREETING:
            # 每天只问候一次
            return self.last_greeting_date != datetime.now().date()
        
        elif dialogue_type == DialogueType.IDLE_CARE:
            # 闲置超过5分钟
            return current_time - self.last_active_time > 300
        
        elif dialogue_type == DialogueType.RANDOM_CHAT:
            # 冷却时间已过且最近没有互动
            return (current_time > self.random_chat_cooldown and 
                    current_time - self.last_interaction_time > 300)
        
        return True
    
    def cleanup(self):
        """清理资源"""
        self.greeting_timer.stop()
        self.idle_timer.stop()
        self.state_timer.stop()
        self.random_timer.stop()
        
        if self.aw_client:
            try:
                self.aw_client.disconnect()
            except:
                pass


# 单例模式
_dialogue_manager_instance = None

def get_dialogue_manager() -> ProactiveDialogueManager:
    """获取对话管理器单例"""
    global _dialogue_manager_instance
    if _dialogue_manager_instance is None:
        _dialogue_manager_instance = ProactiveDialogueManager()
    return _dialogue_manager_instance