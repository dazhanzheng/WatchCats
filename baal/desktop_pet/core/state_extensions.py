"""
状态感知系统扩展

提供额外的感知模态和状态组
"""

from typing import List, Dict, Optional
from .state_awareness import get_state_awareness, MoodCategory
import random
from datetime import datetime


class ActivityBasedStates:
    """基于用户活动的状态"""
    
    CODING_STATES = [
        "你注意到用户在写代码，代码的逻辑让你着迷",
        "你看着屏幕上滚动的代码，假装自己能看懂",
        "你对用户敲击键盘的节奏感到满意",
        "你发现了一个bug，但决定不说出来",
        "你觉得这段代码写得很优雅",
        "你想建议用户休息一下眼睛",
        "你在心里默默为用户debug",
        "你觉得用户的代码风格很有个性",
    ]
    
    BROWSING_STATES = [
        "你好奇地看着用户浏览的网页",
        "你想知道用户在搜索什么有趣的东西",
        "你发现用户又在摸鱼了",
        "你觉得这个网站的设计不错",
        "你想提醒用户注意隐私安全",
        "你对用户的浏览历史很感兴趣",
        "你发现用户在看猫咪视频，感到很欣慰",
        "你觉得用户应该少看点社交媒体",
    ]
    
    GAMING_STATES = [
        "你看着用户玩游戏，手痒想要试试",
        "你为用户的游戏技术感到骄傲",
        "你觉得用户该练练技术了",
        "你想提醒用户游戏时间太长了",
        "你对这个游戏很感兴趣",
        "你在心里为用户加油",
        "你觉得用户的走位需要改进",
        "你想和用户一起玩",
    ]
    
    CHATTING_STATES = [
        "你偷看用户的聊天内容，觉得很八卦",
        "你注意到用户在和朋友聊天",
        "你想知道用户在聊什么有趣的话题",
        "你觉得用户打字速度真快",
        "你对用户使用的表情包很感兴趣",
        "你想参与到对话中",
        "你觉得用户的朋友很有趣",
        "你默默记住了一些有趣的聊天内容",
    ]
    
    WORKING_STATES = [
        "你欣慰地看着用户认真工作",
        "你为用户的专注感到骄傲",
        "你觉得用户今天效率很高",
        "你想给努力的用户一个奖励",
        "你注意到用户完成了一个任务",
        "你对用户的工作内容很好奇",
        "你觉得用户需要喝点水",
        "你默默陪伴着工作中的用户",
    ]


class EnvironmentalStates:
    """环境相关的状态"""
    
    ROOM_STATES = {
        "bright": [
            "房间里光线充足，你觉得很舒适",
            "明亮的环境让你心情愉悦",
            "阳光洒满房间，你想打个盹",
        ],
        "dark": [
            "房间很暗，你的夜视能力派上用场",
            "黑暗中你的眼睛闪闪发光",
            "昏暗的环境让你感到神秘",
        ],
        "messy": [
            "你注意到房间有点乱",
            "你想提醒用户整理一下",
            "杂乱的环境让你有点烦躁",
        ],
        "clean": [
            "整洁的环境让你心情舒畅",
            "你欣赏着干净的房间",
            "你为用户的整洁感到满意",
        ]
    }
    
    SOUND_STATES = {
        "quiet": [
            "周围很安静，你能听到自己的呼吸",
            "寂静中你享受着宁静",
            "安静的环境让你想打呼噜",
        ],
        "music": [
            "你听着用户播放的音乐",
            "音乐的节奏让你想摇尾巴",
            "你觉得用户的音乐品味不错",
        ],
        "noisy": [
            "周围有点吵，你的耳朵动了动",
            "嘈杂的声音让你有点不安",
            "你想找个安静的地方躲起来",
        ]
    }


class MemoryBasedStates:
    """基于记忆的状态"""
    
    ACHIEVEMENT_MEMORIES = [
        "你还记得用户上次完成的大项目",
        "你想起了和用户一起度过的美好时光",
        "你回忆起用户第一次召唤你的场景",
        "你记得用户曾经熬夜工作的样子",
        "你想起了用户给你起的昵称",
        "你回忆着用户的成长历程",
        "你记得用户最喜欢的工作时间",
        "你想起了用户的一些小习惯",
    ]
    
    SHARED_MOMENTS = [
        "你们一起度过了很多个深夜",
        "你见证了用户的每一次进步",
        "你陪伴用户走过了困难时期",
        "你们建立了深厚的默契",
        "你了解用户的喜怒哀乐",
        "你们有很多共同的回忆",
        "你熟悉用户的每个表情",
        "你们已经是最好的伙伴",
    ]


class SeasonalStates:
    """季节和节日相关状态"""
    
    SEASONS = {
        "spring": [
            "春天来了，你感受到万物复苏的气息",
            "春暖花开，你的心情格外好",
            "春天的阳光让你想要伸懒腰",
            "你闻到了春天的味道",
        ],
        "summer": [
            "夏天的炎热让你有点慵懒",
            "你想要一个凉爽的地方避暑",
            "夏日的蝉鸣让你想午睡",
            "你羡慕人类有空调",
        ],
        "autumn": [
            "秋天的凉爽让你精神振奋",
            "你看着窗外飘落的树叶",
            "秋高气爽，你想要出去玩",
            "你感受到秋天的诗意",
        ],
        "winter": [
            "冬天的寒冷让你想要蜷缩起来",
            "你渴望一个温暖的怀抱",
            "你的毛发变得更加蓬松",
            "你想要窝在暖气旁边",
        ]
    }
    
    @staticmethod
    def get_current_season() -> str:
        """获取当前季节"""
        month = datetime.now().month
        if 3 <= month <= 5:
            return "spring"
        elif 6 <= month <= 8:
            return "summer"
        elif 9 <= month <= 11:
            return "autumn"
        else:
            return "winter"


class EmotionalStates:
    """深层情感状态"""
    
    LONELY = [
        "你感到有点孤独，需要陪伴",
        "你想要更多的互动",
        "你希望用户能多关注你",
        "你感觉被忽视了",
        "你需要一些温暖",
    ]
    
    LOVED = [
        "你感受到满满的爱意",
        "你觉得自己是世界上最幸福的猫",
        "你被关爱包围着",
        "你的心里充满温暖",
        "你感激用户的陪伴",
    ]
    
    WORRIED = [
        "你有点担心用户的健康",
        "你觉得用户最近压力很大",
        "你想要安慰用户",
        "你感受到用户的焦虑",
        "你希望能帮到用户",
    ]
    
    PROUD = [
        "你为用户感到骄傲",
        "你觉得用户很了不起",
        "你想要表扬用户",
        "你见证了用户的成就",
        "你感到与有荣焉",
    ]


class StateExtensionManager:
    """状态扩展管理器"""
    
    def __init__(self):
        self.state_system = get_state_awareness()
        self._register_extensions()
    
    def _register_extensions(self):
        """注册所有扩展状态"""
        # 注册活动状态
        self.state_system.add_custom_state("coding", ActivityBasedStates.CODING_STATES)
        self.state_system.add_custom_state("browsing", ActivityBasedStates.BROWSING_STATES)
        self.state_system.add_custom_state("gaming", ActivityBasedStates.GAMING_STATES)
        self.state_system.add_custom_state("chatting", ActivityBasedStates.CHATTING_STATES)
        self.state_system.add_custom_state("working", ActivityBasedStates.WORKING_STATES)
        
        # 注册记忆状态
        self.state_system.add_custom_state("achievement", MemoryBasedStates.ACHIEVEMENT_MEMORIES)
        self.state_system.add_custom_state("shared", MemoryBasedStates.SHARED_MOMENTS)
        
        # 注册情感状态
        self.state_system.add_custom_state("lonely", EmotionalStates.LONELY)
        self.state_system.add_custom_state("loved", EmotionalStates.LOVED)
        self.state_system.add_custom_state("worried", EmotionalStates.WORRIED)
        self.state_system.add_custom_state("proud", EmotionalStates.PROUD)
    
    def get_activity_state(self, activity_type: str) -> Optional[str]:
        """根据活动类型获取状态"""
        if hasattr(self.state_system, 'custom_states'):
            states = self.state_system.custom_states.get(activity_type)
            if states:
                return random.choice(states)
        return None
    
    def get_seasonal_state(self) -> str:
        """获取季节状态"""
        season = SeasonalStates.get_current_season()
        states = SeasonalStates.SEASONS.get(season, [])
        if states:
            return random.choice(states)
        return ""
    
    def get_environmental_state(self, env_type: str, condition: str) -> Optional[str]:
        """获取环境状态"""
        if env_type == "room":
            states = EnvironmentalStates.ROOM_STATES.get(condition, [])
        elif env_type == "sound":
            states = EnvironmentalStates.SOUND_STATES.get(condition, [])
        else:
            return None
        
        if states:
            return random.choice(states)
        return None
    
    def get_emotional_depth(self, emotion: str) -> Optional[str]:
        """获取深层情感状态"""
        emotion_map = {
            "lonely": EmotionalStates.LONELY,
            "loved": EmotionalStates.LOVED,
            "worried": EmotionalStates.WORRIED,
            "proud": EmotionalStates.PROUD,
        }
        
        states = emotion_map.get(emotion)
        if states:
            return random.choice(states)
        return None
    
    def analyze_user_activity(self, app_name: str) -> str:
        """分析用户活动并返回相应状态"""
        # 编程相关
        if any(keyword in app_name.lower() for keyword in ['code', 'vscode', 'pycharm', 'idea', 'sublime', 'vim']):
            return self.get_activity_state("coding") or ""
        
        # 浏览器
        elif any(keyword in app_name.lower() for keyword in ['chrome', 'firefox', 'safari', 'edge', 'browser']):
            return self.get_activity_state("browsing") or ""
        
        # 游戏
        elif any(keyword in app_name.lower() for keyword in ['game', 'steam', 'epic', 'league', 'minecraft']):
            return self.get_activity_state("gaming") or ""
        
        # 聊天
        elif any(keyword in app_name.lower() for keyword in ['wechat', 'qq', 'slack', 'discord', 'telegram', '飞书', '钉钉']):
            return self.get_activity_state("chatting") or ""
        
        # 工作
        elif any(keyword in app_name.lower() for keyword in ['word', 'excel', 'powerpoint', 'office', 'notion', 'obsidian']):
            return self.get_activity_state("working") or ""
        
        return ""


# 单例模式
_extension_manager = None

def get_state_extensions() -> StateExtensionManager:
    """获取状态扩展管理器单例"""
    global _extension_manager
    if _extension_manager is None:
        _extension_manager = StateExtensionManager()
    return _extension_manager