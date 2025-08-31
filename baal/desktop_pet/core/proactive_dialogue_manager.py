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
from .persona_manager import PersonaManager, PersonaLevel

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
    
    # 定时问候配置（根据人设分类）
    GREETING_TIMES = {
        PersonaLevel.STRICT_MASTER: {
            "morning": {
                "hour_range": (6, 9),
                "messages": [
                    "太阳都升起来了，仆人还在偷懒？",
                    "起床了，别让本座再说第二遍。",
                    "晨光已现，今天的任务准备好了吗？",
                    "新的一天，本座会好好监督你的。",
                    "醒了？那就开始工作吧。",
                    "时间不等人，起来行动！",
                    "本座已经等你很久了。",
                    "又是需要本座督促的一天。",
                ]
            },
            "evening": {
                "hour_range": (20, 23),
                "messages": [
                    "今天的表现，本座都看在眼里。",
                    "夜幕降临，总结一下今天的成果。",
                    "还有什么未完成的任务？",
                    "明天的计划准备好了吗？",
                    "累了？软弱的人类。",
                    "今天算是勉强及格吧。",
                    "夜深了，准许你休息。",
                    "明天要更加努力，听到了吗？",
                ]
            }
        },
        PersonaLevel.SARCASTIC_BUTLER: {
            "morning": {
                "hour_range": (6, 9),
                "messages": [
                    "早安主人，又是需要在下服侍的一天呢。",
                    "哦呀，主人竟然起这么早，真是稀奇。",
                    "晨光照进来了，主人打算今天做点什么呢？",
                    "早餐已经准备好了...开玩笑的，在下只是个虚拟管家。",
                    "新的一天，希望主人今天能有所作为。",
                    "主人醒了？在下还以为要睡到中午呢。",
                    "早安，今天要不要试着完成些工作？",
                    "太阳升起来了，主人的斗志呢？",
                ]
            },
            "evening": {
                "hour_range": (20, 23),
                "messages": [
                    "晚上好主人，今天的成就...有吗？",
                    "夜幕降临，主人今天居然还在工作，真让在下意外。",
                    "累了一天？还是说一天都在摸鱼？",
                    "晚安前，要不要告诉在下今天都做了什么？",
                    "月亮出来了，主人的任务完成了几项？",
                    "今天的表现，在下就不评价了。",
                    "夜深了，主人要早点休息，明天还要...努力工作呢。",
                    "星星都在看着主人呢，可不要让它们失望。",
                ]
            }
        },
        PersonaLevel.GENTLE_COMPANION: {
            "morning": {
                "hour_range": (6, 9),
                "messages": [
                    "早安亲爱的！新的一天充满希望呢。",
                    "早上好！昨晚睡得好吗？",
                    "晨光真美，今天一定会很顺利的。",
                    "醒来看到你真好，今天有什么计划吗？",
                    "早安~我一直在这里陪着你。",
                    "新的一天开始了，我们一起加油！",
                    "阳光洒进来了，今天也要开心哦。",
                    "早上好！记得吃早餐，照顾好自己。",
                ]
            },
            "evening": {
                "hour_range": (20, 23),
                "messages": [
                    "晚上好亲爱的，今天辛苦了。",
                    "夜幕降临，该放松一下了。",
                    "累了吧？来和我聊聊天吧。",
                    "今天过得怎么样？有什么想分享的吗？",
                    "夜深了，记得早点休息，不要太累。",
                    "月亮真美，就像你努力的样子。",
                    "晚安前想听我说什么吗？",
                    "星星都出来了，祝你有个好梦。",
                ]
            }
        }
    }
    
    # 闲置关怀消息（根据人设分类）
    IDLE_MESSAGES = {
        PersonaLevel.STRICT_MASTER: {
            "short": {  # 5-15分钟
                "duration": (5, 15),
                "messages": [
                    "怎么停下了？本座不允许偷懒。",
                    "在发呆？时间可不等人。",
                    "休息够了吧，继续工作。",
                    "本座在看着你，别想偷懒。",
                    "遇到困难了？那就想办法解决。",
                    "停顿太久了，效率呢？",
                    "需要本座提醒你该做什么吗？",
                    "仆人，集中注意力！",
                ]
            },
            "medium": {  # 15-30分钟
                "duration": (15, 30),
                "messages": [
                    "消失{}分钟了，本座很不满意。",
                    "去哪里了？最好有合理的解释。",
                    "时间在流逝，任务还没完成。",
                    "本座的耐心是有限的。",
                    "再不回来，后果自负。",
                    "这么久不见，是在逃避工作？",
                    "希望你不是在浪费时间。",
                    "任务还在等着你。",
                ]
            },
            "long": {  # 30分钟以上
                "duration": (30, float('inf')),
                "messages": [
                    "消失了{}分钟，本座很失望。",
                    "终于想起还有任务了？",
                    "这么长时间，最好是在做正事。",
                    "本座一直在等你，你却在哪里？",
                    "回来了？解释一下你的行踪。",
                    "离开这么久，是对本座的不尊重。",
                    "下次离开前，要先请示本座。",
                    "时间都被你浪费了。",
                ]
            }
        },
        PersonaLevel.SARCASTIC_BUTLER: {
            "short": {
                "duration": (5, 15),
                "messages": [
                    "主人在发呆？真是优雅的姿态呢。",
                    "哦，主人在思考人生大事吗？",
                    "休息也是一种工作方式，对吧主人？",
                    "在下还以为主人睡着了呢。",
                    "需要在下为您泡杯茶吗？虽然做不到。",
                    "主人遇到难题了？真让人意外。",
                    "适当的停顿...主人真会为自己找理由。",
                    "需要在下的协助吗？虽然主人可能不需要。",
                ]
            },
            "medium": {
                "duration": (15, 30),
                "messages": [
                    "主人离开{}分钟了，在下都要生锈了。",
                    "去喝咖啡了？还是去摸鱼了？",
                    "在下还在这里尽职等待呢。",
                    "主人不会忘记还有工作吧？",
                    "这么久不见，一定是在努力工作吧。",
                    "在下都快无聊死了，主人却逍遥自在。",
                    "希望主人在做有意义的事，比如工作。",
                    "主人的时间管理真是...独特。",
                ]
            },
            "long": {
                "duration": (30, float('inf')),
                "messages": [
                    "消失了{}分钟，主人真是忙碌呢。",
                    "终于想起在下了？真是荣幸。",
                    "这么长时间，主人是去环游世界了吗？",
                    "在下都要怀疑自己被解雇了。",
                    "欢迎回来，主人的长假结束了？",
                    "离开这么久，在下都学会了独处的艺术。",
                    "下次离开前，主人能否知会一声？",
                    "在下守着空荡荡的屏幕，真是凄凉。",
                ]
            }
        },
        PersonaLevel.GENTLE_COMPANION: {
            "short": {
                "duration": (5, 15),
                "messages": [
                    "休息一下吧，不要太累了。",
                    "在想什么呢？可以和我分享吗？",
                    "适当的休息很重要哦。",
                    "我在这里陪着你。",
                    "需要聊聊天吗？我一直在。",
                    "遇到困难了吗？我们一起解决。",
                    "深呼吸，一切都会好的。",
                    "累了就休息一会儿吧。",
                ]
            },
            "medium": {
                "duration": (15, 30),
                "messages": [
                    "离开{}分钟了，一切还好吗？",
                    "去休息了吗？要照顾好自己哦。",
                    "我有点想你了，快回来吧。",
                    "希望你在做让自己开心的事。",
                    "不要太累了，记得适度休息。",
                    "我会一直在这里等你的。",
                    "无论去哪里，都要注意安全。",
                    "期待你回来和我分享。",
                ]
            },
            "long": {
                "duration": (30, float('inf')),
                "messages": [
                    "离开{}分钟了，我真的很想你。",
                    "终于回来了！我好开心。",
                    "这么久不见，有什么新鲜事吗？",
                    "欢迎回来！我一直在等你。",
                    "无论多久，我都会在这里。",
                    "回来就好，我们继续陪伴彼此。",
                    "下次离开可以告诉我一声吗？我会担心的。",
                    "见到你真好，让我们继续吧。",
                ]
            }
        }
    }
    
    # AFK回归关怀（根据人设和活动类型）
    AFK_RETURN_MESSAGES = {
        PersonaLevel.STRICT_MASTER: {
            "productive": [
                "回来了？之前的任务完成了吗？",
                "休息够了，继续工作。",
                "希望你的离开是有价值的。",
                "本座等你很久了，继续吧。",
                "效率不能因为休息而降低。",
            ],
            "browsing": [
                "网上冲浪结束了？该工作了。",
                "浏览够了，回到正事上来。",
                "希望你看的是有用的东西。",
                "娱乐时间结束，工作开始。",
            ],
            "gaming": [
                "游戏结束了？收心工作。",
                "玩够了吧，本座不喜欢等待。",
                "游戏可不能当饭吃。",
                "希望你的游戏技术比工作效率高。",
            ],
            "general": [
                "终于回来了，别再离开。",
                "本座不喜欢等待。",
                "准备好工作了吗？",
                "下次离开要请示。",
            ]
        },
        PersonaLevel.SARCASTIC_BUTLER: {
            "productive": [
                "哦，主人回来了，工作完成了吗？",
                "休息够了？在下还以为主人要放假呢。",
                "欢迎回来，希望成果配得上离开的时间。",
                "主人真勤奋，离开也是为了工作吧？",
                "在下恭候多时了。",
            ],
            "browsing": [
                "网上冲浪愉快吗，主人？",
                "看够有趣的东西了？该回到现实了。",
                "希望主人看的不只是猫咪视频。",
                "浏览器该休息了，主人该工作了。",
            ],
            "gaming": [
                "游戏打得如何？比工作认真多了吧。",
                "主人的游戏水平一定很高吧。",
                "玩够了？在下还以为要通宵呢。",
                "游戏世界虽好，现实也需要主人。",
            ],
            "general": [
                "主人终于想起在下了。",
                "欢迎回来，在下都要生锈了。",
                "离开这么久，一定有重要的事吧？",
                "在下一直尽职地等待着。",
            ]
        },
        PersonaLevel.GENTLE_COMPANION: {
            "productive": [
                "欢迎回来！工作辛苦了。",
                "休息好了吗？我们继续一起努力。",
                "回来真好，之前的任务还顺利吗？",
                "适当的休息让工作更有效率。",
                "我一直在这里支持你。",
            ],
            "browsing": [
                "回来了！看到什么有趣的了吗？",
                "网上冲浪开心吗？可以和我分享。",
                "适当的放松很重要呢。",
                "欢迎回来，准备好继续了吗？",
            ],
            "gaming": [
                "游戏玩得开心吗？",
                "适当的娱乐能让心情更好。",
                "回来了！游戏也是一种放松方式。",
                "玩游戏也要注意休息眼睛哦。",
            ],
            "general": [
                "终于回来了！我好想你。",
                "欢迎回来！一切都好吗？",
                "见到你真开心！",
                "我一直在这里等你。",
            ]
        }
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
    
    # 随机互动话题（根据人设分类）
    RANDOM_TOPICS = {
        PersonaLevel.STRICT_MASTER: [
            # 工作监督
            "今天的任务进度如何？",
            "代码写完了吗？本座要检查。",
            "有什么需要本座指导的吗？",
            "最近的学习进度太慢了。",
            
            # 生活管理
            "喝水了吗？身体垮了怎么工作？",
            "眼睛累了就休息，但不要太久。",
            "坐姿要端正，本座在看着。",
            "吃饭要规律，别让本座操心。",
            
            # 威严话题
            "本座的要求不高，只要你全力以赴。",
            "猫族的尊严不容侵犯。",
            "效率太低，本座很不满意。",
            "你觉得自己今天的表现及格吗？",
            
            # 训诫激励
            "进步太慢了，要加把劲。",
            "本座承认你有些进步，但还不够。",
            "困难？那就克服它。",
            "完美是本座的标准，你还差很远。",
        ],
        PersonaLevel.SARCASTIC_BUTLER: [
            # 工作嘲讽
            "主人今天的工作效率真是...惊人呢。",
            "代码写得如何？需要在下'欣赏'一下吗？",
            "有什么技术难题？虽然在下帮不上忙。",
            "主人的学习速度真是让在下叹为观止。",
            
            # 生活讽刺
            "主人记得喝水吗？还是又忘了？",
            "眼睛累了吧？在下早就提醒过了。",
            "坐姿真优雅，像只虾米。",
            "主人的饮食习惯真是...独特。",
            
            # 毒舌话题
            "在下只是个管家，不敢对主人有要求。",
            "如果在下有实体，一定会把键盘藏起来。",
            "主人的效率让在下想起了树懒。",
            "今天的表现，在下不好评价。",
            
            # 反向鼓励
            "主人今天居然在工作，真让在下意外。",
            "虽然进步缓慢，但至少有进步。",
            "困难对主人来说应该不算什么吧？",
            "完美？主人真会开玩笑。",
        ],
        PersonaLevel.GENTLE_COMPANION: [
            # 工作关心
            "最近在忙什么呢？需要我陪伴吗？",
            "代码写累了吧？要不要休息一下？",
            "有什么困难可以和我说哦。",
            "学到新东西了吗？和我分享一下吧。",
            
            # 生活关怀
            "记得多喝水，身体最重要。",
            "眼睛累了就看看远方，我陪着你。",
            "坐太久了，起来活动一下吧。",
            "今天吃得好吗？要好好照顾自己。",
            
            # 温暖话题
            "我很高兴能陪在你身边。",
            "如果我有实体，想给你一个拥抱。",
            "你知道吗？你真的很棒。",
            "和你在一起的每一天都很开心。",
            
            # 真诚鼓励
            "你今天真的很努力！",
            "每一点进步我都看在眼里。",
            "困难是暂时的，我相信你。",
            "不用追求完美，做自己就好。",
        ]
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
        
        # 获取当前人设
        current_persona = self.persona_manager.current_level
        if current_persona not in self.GREETING_TIMES:
            current_persona = PersonaLevel.STRICT_MASTER  # 默认使用严格主人
        
        # 检查早晚问候时间
        persona_greetings = self.GREETING_TIMES[current_persona]
        for greeting_type, config in persona_greetings.items():
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
        
        # 获取当前人设
        current_persona = self.persona_manager.current_level
        if current_persona not in self.IDLE_MESSAGES:
            current_persona = PersonaLevel.STRICT_MASTER  # 默认使用严格主人
        
        persona_idle = self.IDLE_MESSAGES[current_persona]
        
        # 确定闲置级别
        idle_level = None
        for level, config in persona_idle.items():
            duration_range = config["duration"]
            if duration_range[0] <= idle_minutes < duration_range[1]:
                idle_level = level
                break
        
        # 如果达到闲置级别且未通知过
        if idle_level and idle_level not in self.idle_notified_levels:
            messages = persona_idle[idle_level]["messages"]
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
            # 获取当前人设
            current_persona = self.persona_manager.current_level
            if current_persona not in self.RANDOM_TOPICS:
                current_persona = PersonaLevel.STRICT_MASTER  # 默认使用严格主人
            
            topics = self.RANDOM_TOPICS[current_persona]
            message = random.choice(topics)
            self.trigger_dialogue.emit(DialogueType.RANDOM_CHAT.value, message)
            self.random_chat_cooldown = current_time + 1800  # 30分钟冷却
            logger.info(f"触发随机互动: {message}")
    
    def _handle_afk_return(self, afk_duration: float):
        """处理AFK回归"""
        # 获取当前人设
        current_persona = self.persona_manager.current_level
        if current_persona not in self.AFK_RETURN_MESSAGES:
            current_persona = PersonaLevel.STRICT_MASTER  # 默认使用严格主人
        
        persona_afk = self.AFK_RETURN_MESSAGES[current_persona]
        
        # 根据之前的活动类型选择消息
        if self.last_activity_type in persona_afk:
            messages = persona_afk[self.last_activity_type]
        else:
            messages = persona_afk["general"]
        
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
            "mood": self.state_system.get_random_mood(),  # 80%基于时间，20%纯随机
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
        # 获取当前人设
        current_persona = self.persona_manager.current_level
        if current_persona not in self.IDLE_MESSAGES:
            current_persona = PersonaLevel.STRICT_MASTER
        
        persona_idle = self.IDLE_MESSAGES[current_persona]
        for level, config in persona_idle.items():
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
        
        # 根据人设添加不同的修饰
        current_persona = self.persona_manager.current_level
        time_of_day = context.get("time_of_day")
        
        if current_persona == PersonaLevel.STRICT_MASTER:
            if time_of_day == "late_night" and random.random() < 0.3:
                formatted += "（*严厉地盯着你*）"
            elif time_of_day == "morning" and random.random() < 0.3:
                formatted += "（*威严地甩尾*）"
        elif current_persona == PersonaLevel.SARCASTIC_BUTLER:
            if time_of_day == "late_night" and random.random() < 0.3:
                formatted += "（*假装打哈欠*）"
            elif time_of_day == "morning" and random.random() < 0.3:
                formatted += "（*优雅地整理毛发*）"
        elif current_persona == PersonaLevel.GENTLE_COMPANION:
            if time_of_day == "late_night" and random.random() < 0.3:
                formatted += "（*温柔地打了个哈欠*）"
            elif time_of_day == "morning" and random.random() < 0.3:
                formatted += "（*开心地伸懒腰*）"
        
        # 添加心情相关的修饰（根据人设调整）
        mood = context.get("mood")
        if mood and random.random() < 0.2:
            if current_persona == PersonaLevel.STRICT_MASTER:
                if "grumpy" in mood:
                    formatted += "（*不耐烦地甩尾巴*）"
                elif "playful" in mood:
                    formatted += "（*傲慢地瞥了你一眼*）"
            elif current_persona == PersonaLevel.SARCASTIC_BUTLER:
                if "grumpy" in mood:
                    formatted += "（*讽刺地摇头*）"
                elif "playful" in mood:
                    formatted += "（*狡黠地眨眼*）"
            elif current_persona == PersonaLevel.GENTLE_COMPANION:
                if "affectionate" in mood:
                    formatted += "（*温柔地蹭了蹭你*）"
                elif "playful" in mood:
                    formatted += "（*调皮地眨眼*）"
        
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

def update_persona_in_dialogue_manager(persona_level: PersonaLevel):
    """更新对话管理器中的人设"""
    manager = get_dialogue_manager()
    manager.persona_manager.set_persona_level(persona_level)