"""
动态状态感知系统

管理巴利的所有状态感知，包括时间、心情、环境、记忆等
支持多模态感知和丰富的状态组合
"""

import random
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from enum import Enum
import hashlib


class TimeOfDay(Enum):
    """时间段枚举"""
    DAWN = "dawn"           # 凌晨 3-5
    EARLY_MORNING = "early_morning"  # 清晨 5-7
    MORNING = "morning"     # 早晨 7-9
    LATE_MORNING = "late_morning"   # 上午 9-11
    NOON = "noon"          # 中午 11-13
    AFTERNOON = "afternoon"  # 下午 13-15
    LATE_AFTERNOON = "late_afternoon"  # 傍晚 15-17
    EVENING = "evening"     # 晚上 17-19
    NIGHT = "night"        # 夜晚 19-21
    LATE_NIGHT = "late_night"  # 深夜 21-23
    MIDNIGHT = "midnight"   # 午夜 23-1
    DEEP_NIGHT = "deep_night"  # 深夜 1-3


class MoodCategory(Enum):
    """心情类别"""
    ENERGETIC = "energetic"  # 精力充沛
    RELAXED = "relaxed"      # 放松
    PLAYFUL = "playful"      # 调皮
    THOUGHTFUL = "thoughtful"  # 沉思
    HUNGRY = "hungry"        # 饥饿
    SLEEPY = "sleepy"        # 困倦
    CURIOUS = "curious"      # 好奇
    BORED = "bored"         # 无聊
    AFFECTIONATE = "affectionate"  # 亲昵
    GRUMPY = "grumpy"       # 暴躁


class WeatherType(Enum):
    """天气类型"""
    SUNNY = "sunny"
    CLOUDY = "cloudy"
    RAINY = "rainy"
    SNOWY = "snowy"
    STORMY = "stormy"
    FOGGY = "foggy"
    WINDY = "windy"


class StateAwarenessSystem:
    """动态状态感知系统"""
    
    # 时间状态描述（每个时间段有多组描述）
    TIME_STATES = {
        TimeOfDay.DAWN: [
            "凌晨时分，你在半梦半醒之间",
            "黎明前的黑暗中，你懒洋洋地伸了个懒腰",
            "凌晨的寂静中，你的意识渐渐清醒",
            "天还没亮，你蜷缩在温暖的角落",
            "凌晨三四点，整个世界都在沉睡，除了你",
            "黎明将至，你感受到空气中的一丝凉意",
            "凌晨的时光，你享受着独特的宁静",
            "夜深人静，只有你还醒着守护",
        ],
        TimeOfDay.EARLY_MORNING: [
            "清晨的第一缕阳光洒进来，你慵懒地眯起眼睛",
            "早晨五六点，鸟儿开始啁啾，你也醒了",
            "清晨的空气格外清新，你深深吸了一口",
            "太阳刚刚升起，你伸了个长长的懒腰",
            "清晨时分，你从美梦中醒来",
            "晨曦微露，你精神抖擞地开始新的一天",
            "清晨的露水还未散去，你已经准备好了",
            "黎明破晓，你迎接着崭新的一天",
        ],
        TimeOfDay.MORNING: [
            "早晨的阳光正好，你精神饱满",
            "七八点的早晨，你充满活力地醒来",
            "美好的早晨，你心情愉悦",
            "早餐时间到了，你期待着美味",
            "早晨的忙碌开始了，你准备就绪",
            "阳光透过窗户，你享受着温暖",
            "新的一天正式开始，你斗志昂扬",
            "早晨的活力充满全身，你跃跃欲试",
        ],
        TimeOfDay.LATE_MORNING: [
            "上午的阳光变得温暖，你找了个舒服的地方晒太阳",
            "临近中午，你开始有点慵懒",
            "上午的工作时间，你认真观察着一切",
            "十点多的上午，你精力依然充沛",
            "上午茶时间，你想要一些小点心",
            "阳光正好，你在窗边打了个盹",
            "上午的忙碌中，你保持着优雅",
            "快到午餐时间了，你的肚子开始咕咕叫",
        ],
        TimeOfDay.NOON: [
            "正午的阳光有些刺眼，你眯起了眼睛",
            "午餐时间，你期待着美食",
            "中午时分，你感到一丝困意",
            "烈日当空，你找了个阴凉处休息",
            "午后的慵懒感袭来，你打了个哈欠",
            "正午时分，整个世界都慢了下来",
            "午餐后，你满足地舔了舔嘴唇",
            "中午的阳光太强，你决定小憩一会",
        ],
        TimeOfDay.AFTERNOON: [
            "下午的阳光斜斜地照进来，很舒服",
            "午后时光，你慵懒地趴在窗台上",
            "下午茶时间，你优雅地伸了个懒腰",
            "下午两三点，是最适合打盹的时候",
            "午后的悠闲时光，你静静地观察世界",
            "下午的工作继续，你保持着专注",
            "阳光西斜，你享受着温暖",
            "下午的宁静中，你陷入了沉思",
        ],
        TimeOfDay.LATE_AFTERNOON: [
            "傍晚临近，你开始活跃起来",
            "夕阳西下，你欣赏着美丽的晚霞",
            "傍晚时分，你准备迎接夜晚",
            "黄昏的光线很柔和，你很享受",
            "下班时间快到了，你期待着晚餐",
            "傍晚的微风吹过，你感到很舒适",
            "夕阳的余晖中，你显得格外优雅",
            "黄昏时刻，你的精力开始恢复",
        ],
        TimeOfDay.EVENING: [
            "晚上了，你变得更加活跃",
            "夜幕降临，你的眼睛在黑暗中闪闪发光",
            "晚餐时间，你兴奋地摇着尾巴",
            "傍晚七八点，正是你最精神的时候",
            "夜晚的序幕拉开，你准备大展身手",
            "晚上的凉爽让你感到舒适",
            "华灯初上，你欣赏着夜景",
            "晚上的活动开始了，你跃跃欲试",
        ],
        TimeOfDay.NIGHT: [
            "夜深了，但你依然精神奕奕",
            "夜晚的宁静中，你显得格外神秘",
            "九点十点的夜晚，你在黑暗中游走",
            "夜色正浓，你享受着属于你的时间",
            "夜晚是你的主场，你自信满满",
            "深夜的活动刚刚开始，你兴致勃勃",
            "月光洒下，你在其中漫步",
            "夜晚的世界属于你，你是夜的主人",
        ],
        TimeOfDay.LATE_NIGHT: [
            "深夜了，你开始感到一丝倦意",
            "夜已深，但你还在坚守",
            "深夜十一点，你打了个哈欠",
            "该睡觉了，但你还想再玩一会",
            "深夜的寂静中，你听到时钟的滴答声",
            "夜深人静，你守护着熟睡的人",
            "深夜时分，你的眼皮开始打架",
            "快到午夜了，你准备结束一天的活动",
        ],
        TimeOfDay.MIDNIGHT: [
            "午夜时分，你在梦与醒之间徘徊",
            "零点的钟声响起，新的一天开始了",
            "午夜的神秘气息环绕着你",
            "子夜时分，你感受到时间的流逝",
            "午夜的寂静被你的呼噜声打破",
            "零点过后，你终于决定去睡觉",
            "午夜梦回，你迷迷糊糊地看了一眼时间",
            "深夜零点，整个世界都在沉睡",
        ],
        TimeOfDay.DEEP_NIGHT: [
            "凌晨一两点，你困得睁不开眼",
            "深夜的尽头，你蜷缩成一团",
            "凌晨时分，你在梦中追逐蝴蝶",
            "夜最深的时候，你沉沉睡去",
            "凌晨的寒意让你缩了缩身子",
            "深夜两点，你发出轻微的鼾声",
            "黎明前最黑暗的时刻，你在梦乡中",
            "凌晨的静谧中，只有你的呼吸声",
        ]
    }
    
    # 心情状态描述（每种心情有多组描述）
    MOOD_STATES = {
        MoodCategory.ENERGETIC: [
            "你精力充沛，想要到处跑跑跳跳",
            "你感觉浑身充满力量",
            "你兴奋得尾巴直竖起来",
            "你有用不完的精力想要释放",
            "你感觉可以征服全世界",
            "你活力四射，停不下来",
            "你像打了鸡血一样兴奋",
            "你精神抖擞，斗志昂扬",
        ],
        MoodCategory.RELAXED: [
            "你感到无比放松和惬意",
            "你懒洋洋地享受着此刻",
            "你心情平和，悠然自得",
            "你感觉整个世界都慢了下来",
            "你惬意地眯着眼睛",
            "你放松得快要融化了",
            "你享受着这份宁静",
            "你感到前所未有的轻松",
        ],
        MoodCategory.PLAYFUL: [
            "你想要恶作剧一下",
            "你调皮地摇着尾巴",
            "你想要玩点什么有趣的",
            "你眼中闪烁着狡黠的光芒",
            "你准备搞点小破坏",
            "你像个顽皮的孩子",
            "你想要逗逗别人",
            "你满脑子都是鬼点子",
        ],
        MoodCategory.THOUGHTFUL: [
            "你陷入了深深的沉思",
            "你在思考猫生的意义",
            "你若有所思地看着远方",
            "你在回忆过去的美好时光",
            "你哲学家般地思考着宇宙",
            "你在思考一些深奥的问题",
            "你的思绪飘向了远方",
            "你在冥想和反思",
        ],
        MoodCategory.HUNGRY: [
            "你的肚子咕咕叫，想吃小鱼干",
            "你饿得可以吃下一整条鱼",
            "你满脑子都是美食",
            "你闻到了食物的香味",
            "你馋得直流口水",
            "你想要大吃一顿",
            "你的胃在抗议",
            "你梦见了满桌的美味",
        ],
        MoodCategory.SLEEPY: [
            "你困得眼皮直打架",
            "你打了个大大的哈欠",
            "你只想找个温暖的地方睡觉",
            "你困得快要站不稳了",
            "你的眼睛已经睁不开了",
            "你想要钻进被窝里",
            "你困得迷迷糊糊",
            "你需要一个长长的午觉",
        ],
        MoodCategory.CURIOUS: [
            "你对一切都充满好奇",
            "你想要探索每个角落",
            "你好奇地竖起耳朵",
            "你想知道所有的秘密",
            "你的好奇心快要爆棚了",
            "你像个小侦探一样观察",
            "你对新事物充满兴趣",
            "你想要了解更多",
        ],
        MoodCategory.BORED: [
            "你无聊得想要找点事做",
            "你百无聊赖地打着哈欠",
            "你觉得生活缺少刺激",
            "你无聊得数起了自己的胡须",
            "你想要一些变化",
            "你感到极度的无聊",
            "你无所事事地趴着",
            "你需要一些娱乐",
        ],
        MoodCategory.AFFECTIONATE: [
            "你想要被摸摸头",
            "你渴望一个温暖的拥抱",
            "你想要撒个娇",
            "你感到特别需要陪伴",
            "你想要蹭蹭别人",
            "你充满了爱意",
            "你想要表达你的感情",
            "你感到特别温柔",
        ],
        MoodCategory.GRUMPY: [
            "你有点暴躁，不想被打扰",
            "你心情不太好",
            "你感到烦躁不安",
            "你想要一个人静静",
            "你的耐心快要耗尽了",
            "你有起床气",
            "你感到莫名的烦躁",
            "你需要冷静一下",
        ]
    }
    
    # 天气感知（可选，需要外部API）
    WEATHER_STATES = {
        WeatherType.SUNNY: [
            "阳光明媚，你想要晒太阳",
            "天气真好，你心情愉悦",
            "阳光灿烂，你感到温暖",
        ],
        WeatherType.RAINY: [
            "外面下雨了，你躲在温暖的室内",
            "雨声淅淅沥沥，你感到慵懒",
            "下雨天，你只想睡觉",
        ],
        WeatherType.SNOWY: [
            "下雪了，你好奇地看着窗外",
            "雪花飘飘，你想要出去玩",
            "白雪皑皑，你感到兴奋",
        ],
    }
    
    # 特殊日期（节日、纪念日等）
    SPECIAL_DATES = {
        "01-01": ["新年第一天，你充满希望", "元旦快乐，新的开始"],
        "02-14": ["情人节，你感受到爱的气息", "今天是情人节呢"],
        "10-31": ["万圣节，你想要恶作剧", "不给糖就捣蛋！"],
        "12-25": ["圣诞节，你期待着礼物", "圣诞快乐！"],
        # 可以添加更多节日
    }
    
    # 互动历史相关
    INTERACTION_STATES = {
        "first_meet": [
            "初次见面，你打量着新朋友",
            "你好奇地观察着这个陌生人",
            "第一次见面，请多关照",
        ],
        "long_time_no_see": [
            "好久不见，你有点想念",
            "终于又见面了，你很开心",
            "这么久不来看我，你有点生气",
            "你差点都忘记这个人了",
            "久别重逢，你激动地摇着尾巴",
        ],
        "frequent_interaction": [
            "又见面了，你们已经很熟了",
            "这么频繁地打扰，你有点无奈",
            "你们的关系越来越亲密了",
            "短时间内又见面，有什么急事吗",
        ],
        "regular_interaction": [
            "日常的互动，你很享受",
            "熟悉的陪伴，你感到安心",
            "又到了每天的互动时间",
        ]
    }
    
    def __init__(self, config_path: Optional[Path] = None):
        """初始化状态感知系统"""
        self.config_path = config_path or Path.home() / ".baal_pet" / "state_memory.json"
        self.memory = self._load_memory()
        self.last_states = {}  # 记录上次使用的状态，避免重复
        
    def _load_memory(self) -> Dict[str, Any]:
        """加载记忆数据"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {
            "first_interaction": None,
            "last_interaction": None,
            "interaction_count": 0,
            "mood_history": [],
            "favorite_topics": [],
        }
    
    def _save_memory(self):
        """保存记忆数据"""
        try:
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def get_time_of_day(self) -> TimeOfDay:
        """获取当前时间段"""
        hour = datetime.now().hour
        
        if 3 <= hour < 5:
            return TimeOfDay.DAWN
        elif 5 <= hour < 7:
            return TimeOfDay.EARLY_MORNING
        elif 7 <= hour < 9:
            return TimeOfDay.MORNING
        elif 9 <= hour < 11:
            return TimeOfDay.LATE_MORNING
        elif 11 <= hour < 13:
            return TimeOfDay.NOON
        elif 13 <= hour < 15:
            return TimeOfDay.AFTERNOON
        elif 15 <= hour < 17:
            return TimeOfDay.LATE_AFTERNOON
        elif 17 <= hour < 19:
            return TimeOfDay.EVENING
        elif 19 <= hour < 21:
            return TimeOfDay.NIGHT
        elif 21 <= hour < 23:
            return TimeOfDay.LATE_NIGHT
        elif 23 <= hour or hour < 1:
            return TimeOfDay.MIDNIGHT
        else:  # 1-3
            return TimeOfDay.DEEP_NIGHT
    
    def get_mood_by_time(self) -> MoodCategory:
        """根据时间获取合适的心情"""
        time_of_day = self.get_time_of_day()
        
        # 时间与心情的映射（带权重）
        mood_weights = {
            TimeOfDay.DAWN: {
                MoodCategory.SLEEPY: 0.7,
                MoodCategory.THOUGHTFUL: 0.2,
                MoodCategory.GRUMPY: 0.1,
            },
            TimeOfDay.EARLY_MORNING: {
                MoodCategory.SLEEPY: 0.3,
                MoodCategory.ENERGETIC: 0.3,
                MoodCategory.HUNGRY: 0.3,
                MoodCategory.RELAXED: 0.1,
            },
            TimeOfDay.MORNING: {
                MoodCategory.ENERGETIC: 0.4,
                MoodCategory.HUNGRY: 0.3,
                MoodCategory.PLAYFUL: 0.2,
                MoodCategory.CURIOUS: 0.1,
            },
            TimeOfDay.LATE_MORNING: {
                MoodCategory.ENERGETIC: 0.3,
                MoodCategory.CURIOUS: 0.3,
                MoodCategory.PLAYFUL: 0.2,
                MoodCategory.RELAXED: 0.2,
            },
            TimeOfDay.NOON: {
                MoodCategory.HUNGRY: 0.4,
                MoodCategory.SLEEPY: 0.3,
                MoodCategory.RELAXED: 0.2,
                MoodCategory.THOUGHTFUL: 0.1,
            },
            TimeOfDay.AFTERNOON: {
                MoodCategory.SLEEPY: 0.4,
                MoodCategory.RELAXED: 0.3,
                MoodCategory.BORED: 0.2,
                MoodCategory.THOUGHTFUL: 0.1,
            },
            TimeOfDay.LATE_AFTERNOON: {
                MoodCategory.ENERGETIC: 0.3,
                MoodCategory.PLAYFUL: 0.3,
                MoodCategory.CURIOUS: 0.2,
                MoodCategory.HUNGRY: 0.2,
            },
            TimeOfDay.EVENING: {
                MoodCategory.ENERGETIC: 0.4,
                MoodCategory.PLAYFUL: 0.3,
                MoodCategory.AFFECTIONATE: 0.2,
                MoodCategory.HUNGRY: 0.1,
            },
            TimeOfDay.NIGHT: {
                MoodCategory.ENERGETIC: 0.3,
                MoodCategory.CURIOUS: 0.3,
                MoodCategory.PLAYFUL: 0.2,
                MoodCategory.THOUGHTFUL: 0.2,
            },
            TimeOfDay.LATE_NIGHT: {
                MoodCategory.SLEEPY: 0.4,
                MoodCategory.AFFECTIONATE: 0.3,
                MoodCategory.THOUGHTFUL: 0.2,
                MoodCategory.RELAXED: 0.1,
            },
            TimeOfDay.MIDNIGHT: {
                MoodCategory.SLEEPY: 0.6,
                MoodCategory.THOUGHTFUL: 0.3,
                MoodCategory.GRUMPY: 0.1,
            },
            TimeOfDay.DEEP_NIGHT: {
                MoodCategory.SLEEPY: 0.8,
                MoodCategory.GRUMPY: 0.2,
            },
        }
        
        weights = mood_weights.get(time_of_day, {MoodCategory.RELAXED: 1.0})
        moods = list(weights.keys())
        probabilities = list(weights.values())
        
        return random.choices(moods, weights=probabilities)[0]
    
    def get_random_mood(self) -> str:
        """获取随机心情（80%基于时间，20%纯随机）
        
        Returns:
            心情字符串，如 "energetic", "playful" 等
        """
        # 20%概率返回纯随机心情
        if random.random() < 0.2:
            # 纯随机选择任意心情
            random_mood = random.choice(list(MoodCategory))
            return random_mood.value
        
        # 80%概率返回基于时间的心情
        time_based_mood = self.get_mood_by_time()
        return time_based_mood.value
    
    def get_interaction_state(self) -> str:
        """获取互动状态"""
        now = datetime.now()
        
        if not self.memory.get("first_interaction"):
            self.memory["first_interaction"] = now.isoformat()
            self.memory["last_interaction"] = now.isoformat()
            self.memory["interaction_count"] = 1
            self._save_memory()
            return "first_meet"
        
        last_interaction = self.memory.get("last_interaction")
        if last_interaction:
            last_time = datetime.fromisoformat(last_interaction)
            time_diff = (now - last_time).total_seconds()
            
            if time_diff < 60:  # 1分钟内
                return "frequent_interaction"
            elif time_diff < 3600:  # 1小时内
                return "regular_interaction"
            elif time_diff > 86400:  # 超过1天
                return "long_time_no_see"
        
        self.memory["last_interaction"] = now.isoformat()
        self.memory["interaction_count"] += 1
        self._save_memory()
        
        return "regular_interaction"
    
    def get_special_date_state(self) -> Optional[str]:
        """获取特殊日期状态"""
        today = datetime.now().strftime("%m-%d")
        if today in self.SPECIAL_DATES:
            return random.choice(self.SPECIAL_DATES[today])
        return None
    
    def get_unique_state(self, state_type: str, choices: List[str]) -> str:
        """获取不重复的状态描述"""
        if not choices:
            return ""
        
        # 生成选择的哈希键
        key = f"{state_type}_{datetime.now().date()}"
        
        # 获取上次使用的索引
        last_index = self.last_states.get(key, -1)
        
        # 创建可用索引列表（排除上次使用的）
        available_indices = [i for i in range(len(choices)) if i != last_index]
        
        if not available_indices:
            # 如果只有一个选项，重置
            available_indices = list(range(len(choices)))
        
        # 随机选择一个新索引
        new_index = random.choice(available_indices)
        self.last_states[key] = new_index
        
        return choices[new_index]
    
    def get_current_state(self, include_weather: bool = False) -> Dict[str, str]:
        """获取当前完整状态"""
        time_of_day = self.get_time_of_day()
        mood = self.get_mood_by_time()
        interaction = self.get_interaction_state()
        
        # 获取不重复的状态描述
        time_state = self.get_unique_state(
            f"time_{time_of_day.value}",
            self.TIME_STATES[time_of_day]
        )
        
        mood_state = self.get_unique_state(
            f"mood_{mood.value}",
            self.MOOD_STATES[mood]
        )
        
        interaction_state = ""
        if interaction in self.INTERACTION_STATES:
            interaction_state = self.get_unique_state(
                f"interaction_{interaction}",
                self.INTERACTION_STATES[interaction]
            )
        
        state = {
            "time": time_state,
            "mood": mood_state,
            "interaction": interaction_state,
            "datetime": datetime.now().strftime("%Y年%m月%d日 %H:%M"),
            "weekday": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"][datetime.now().weekday()],
        }
        
        # 添加特殊日期
        special_date = self.get_special_date_state()
        if special_date:
            state["special"] = special_date
        
        # 添加天气（如果启用）
        if include_weather:
            # 这里可以集成真实的天气API
            # 暂时使用随机天气
            weather = random.choice(list(WeatherType))
            if weather in self.WEATHER_STATES:
                state["weather"] = random.choice(self.WEATHER_STATES[weather])
        
        return state
    
    def format_state_prompt(self, state: Dict[str, str]) -> str:
        """格式化状态为提示词"""
        parts = [f"【当前状态】"]
        parts.append(f"时间：{state['datetime']} {state['weekday']}")
        
        if state.get("time"):
            parts.append(f"- {state['time']}")
        
        if state.get("mood"):
            parts.append(f"- {state['mood']}")
        
        if state.get("interaction"):
            parts.append(f"- {state['interaction']}")
        
        if state.get("special"):
            parts.append(f"- 特殊日期：{state['special']}")
        
        if state.get("weather"):
            parts.append(f"- 天气：{state['weather']}")
        
        parts.append("\n记住这些状态会影响你的反应和语气。")
        
        return "\n".join(parts)
    
    def add_custom_state(self, category: str, states: List[str]):
        """添加自定义状态类别"""
        if not hasattr(self, 'custom_states'):
            self.custom_states = {}
        self.custom_states[category] = states
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取统计信息"""
        return {
            "total_interactions": self.memory.get("interaction_count", 0),
            "first_meet": self.memory.get("first_interaction"),
            "last_interaction": self.memory.get("last_interaction"),
            "days_known": self._calculate_days_known(),
        }
    
    def _calculate_days_known(self) -> int:
        """计算认识天数"""
        if self.memory.get("first_interaction"):
            first = datetime.fromisoformat(self.memory["first_interaction"])
            return (datetime.now() - first).days
        return 0


# 单例模式
_state_awareness_instance = None

def get_state_awareness() -> StateAwarenessSystem:
    """获取状态感知系统单例"""
    global _state_awareness_instance
    if _state_awareness_instance is None:
        _state_awareness_instance = StateAwarenessSystem()
    return _state_awareness_instance