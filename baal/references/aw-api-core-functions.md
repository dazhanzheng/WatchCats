# ActivityWatch 核心功能 API 参考

本文档针对以下两个核心功能提取了相关的API：
1. 活动数据自动打标（使用大语言模型）
2. 获取不同时间范围的活动数据分析

## 功能1：活动数据自动打标

### 核心流程
1. 获取未分类的活动数据
2. 使用大语言模型进行分类打标
3. 将分类结果存储回ActivityWatch

### 相关API

#### 数据获取

**client.get_events(bucket_id: str, limit: int = -1, start: Optional[datetime] = None, end: Optional[datetime] = None) → List[Event]**  
获取指定桶中的事件数据

```python
from datetime import datetime, timedelta

# 获取最近的未分类事件
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)  # 最近24小时
events = client.get_events("aw-watcher-window", limit=1000, start=start_time, end=end_time)
```

**client.get_buckets() → dict**  
获取所有可用的数据桶

```python
# 获取所有桶信息，找到需要处理的桶
buckets = client.get_buckets()
window_buckets = [name for name in buckets.keys() if 'window' in name]
```

#### 数据过滤和查询

**client.query(query: str, timeperiods: List[Tuple[datetime, datetime]], name: Optional[str] = None, cache: bool = False) → List[Any]**  
使用查询语言获取和处理数据

```python
# 查询未分类的窗口事件
query_str = """
buckets = query_bucket(find_bucket("aw-watcher-window"));
events = filter_keyvals(buckets, "category", [], exclude=true);  // 获取未分类事件
RETURN events;
"""
timeperiods = [(start_time, end_time)]
uncategorized_events = client.query(query_str, timeperiods)
```

#### 数据分类和打标

**aw_transform.categorize(events: List[Event], classes: List[Tuple[List[str], Rule]]) → List[Event]**  
对事件进行分类

```python
from aw_transform import Rule, categorize

# 根据大语言模型的结果创建分类规则
def create_ai_categories(llm_results):
    rules = []
    for category, patterns in llm_results.items():
        rule = Rule({
            "regex": f"({'|'.join(patterns)})",
            "ignore_case": True
        })
        rules.append(([category], rule))
    return rules

# 应用分类
ai_categories = create_ai_categories(llm_classification_results)
categorized_events = categorize(events, ai_categories)
```

**aw_transform.tag(events: List[Event], classes: List[Tuple[str, Rule]]) → List[Event]**  
为事件添加标签

```python
# 为事件添加AI分类标签
tagged_events = tag(events, ai_tags)
```

#### 数据存储

**client.create_bucket(bucket_id: str, event_type: str, queued=False)**  
创建新桶存储分类结果

```python
# 创建分类结果桶
classified_bucket_id = "aw-ai-classified-activities"
client.create_bucket(classified_bucket_id, event_type="ai.classified")
```

**client.insert_events(bucket_id: str, events: List[Event]) → None**  
批量插入分类后的事件

```python
# 将分类结果存储到新桶中
client.insert_events(classified_bucket_id, categorized_events)
```

### 完整示例：自动分类流程

```python
from aw_client import ActivityWatchClient
from aw_transform import categorize, Rule
from datetime import datetime, timedelta
import openai  # 或其他大语言模型API

def auto_classify_activities():
    client = ActivityWatchClient("ai-classifier")
    
    # 1. 获取未分类的活动数据
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)
    
    # 获取窗口活动数据
    window_events = client.get_events("aw-watcher-window", 
                                    start=start_time, end=end_time)
    
    # 2. 提取应用和标题信息用于AI分类
    activities_to_classify = []
    for event in window_events:
        if 'app' in event.data and 'title' in event.data:
            activities_to_classify.append({
                'app': event.data['app'],
                'title': event.data['title'],
                'duration': event.duration.total_seconds()
            })
    
    # 3. 调用大语言模型进行分类
    llm_results = classify_with_llm(activities_to_classify)
    
    # 4. 创建分类规则
    classification_rules = create_classification_rules(llm_results)
    
    # 5. 应用分类
    classified_events = categorize(window_events, classification_rules)
    
    # 6. 存储分类结果
    client.create_bucket("aw-ai-classified", event_type="ai.classified")
    client.insert_events("aw-ai-classified", classified_events)
    
    return classified_events

def classify_with_llm(activities):
    # 调用大语言模型的逻辑
    # 返回分类结果字典
    pass

def create_classification_rules(llm_results):
    # 根据LLM结果创建ActivityWatch分类规则
    pass
```

## 功能2：获取不同时间范围的活动数据

### 核心需求
- **近7日、1日**：统计数据 + 关键细节
- **近2小时、30分钟、5分钟**：原始使用数据

### 相关API

#### 时间范围查询

**client.get_events(bucket_id: str, limit: int = -1, start: Optional[datetime] = None, end: Optional[datetime] = None) → List[Event]**  
按时间范围获取事件

```python
from datetime import datetime, timedelta

def get_time_range_data(hours_back):
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=hours_back)
    
    return client.get_events("aw-watcher-window", 
                           start=start_time, end=end_time)

# 不同时间范围的数据获取
data_7d = get_time_range_data(24 * 7)      # 近7日
data_1d = get_time_range_data(24)          # 近1日  
data_2h = get_time_range_data(2)           # 近2小时
data_30m = get_time_range_data(0.5)        # 近30分钟
data_5m = get_time_range_data(5/60)        # 近5分钟
```

#### 数据统计和聚合

**aw_transform.merge_events_by_keys(events, keys) → List[Event]**  
按键合并事件（用于统计）

```python
# 按应用名称合并，获得每个应用的总使用时间
app_usage_stats = merge_events_by_keys(events, ['app'])
```

**aw_transform.sum_durations(events) → timedelta**  
计算事件总时长

```python
# 计算总使用时间
total_time = sum_durations(events)
```

**aw_transform.sort_by_duration(events) → List[Event]**  
按持续时间排序

```python
# 按使用时长排序，找出最常用的应用
top_apps = sort_by_duration(app_usage_stats)
```

**aw_transform.limit_events(events, count) → List[Event]**  
限制返回事件数量

```python
# 获取前10个最常用的应用
top_10_apps = limit_events(sort_by_duration(app_usage_stats), 10)
```

#### 数据过滤

**aw_transform.filter_keyvals(events: List[Event], key: str, vals: List[str], exclude=False) → List[Event]**  
按键值过滤事件

```python
# 过滤掉AFK时间
active_events = filter_keyvals(events, "status", ["afk"], exclude=True)

# 只获取特定应用的使用情况
vscode_events = filter_keyvals(events, "app", ["Visual Studio Code"])
```

#### 复杂查询

**client.query()** 支持复杂的数据查询和处理

```python
# 获取近7日的统计数据查询
stats_query_7d = """
events = query_bucket(find_bucket("aw-watcher-window"));
events = merge_events_by_keys(events, ["app"]);
events = sort_by_duration(events);
events = limit_events(events, 20);
RETURN events;
"""

# 获取近5分钟的原始数据查询  
raw_query_5m = """
events = query_bucket(find_bucket("aw-watcher-window"));
events = sort_by_timestamp(events);
RETURN events;
"""

timeperiods_7d = [(datetime.now() - timedelta(days=7), datetime.now())]
timeperiods_5m = [(datetime.now() - timedelta(minutes=5), datetime.now())]

stats_7d = client.query(stats_query_7d, timeperiods_7d)
raw_5m = client.query(raw_query_5m, timeperiods_5m)
```

### 完整示例：多时间范围数据获取

```python
from aw_client import ActivityWatchClient
from aw_transform import *
from datetime import datetime, timedelta

def get_activity_analysis():
    client = ActivityWatchClient("activity-analyzer")
    
    # 定义时间范围
    now = datetime.now()
    time_ranges = {
        '7d': (now - timedelta(days=7), now),
        '1d': (now - timedelta(days=1), now), 
        '2h': (now - timedelta(hours=2), now),
        '30m': (now - timedelta(minutes=30), now),
        '5m': (now - timedelta(minutes=5), now)
    }
    
    results = {}
    
    for period, (start, end) in time_ranges.items():
        # 获取原始数据
        raw_events = client.get_events("aw-watcher-window", 
                                     start=start, end=end)
        
        if period in ['7d', '1d']:
            # 长期数据：提供统计信息
            app_stats = merge_events_by_keys(raw_events, ['app'])
            top_apps = limit_events(sort_by_duration(app_stats), 10)
            
            # 获取关键细节：最长的单次使用会话
            longest_sessions = limit_events(sort_by_duration(raw_events), 5)
            
            results[period] = {
                'type': 'statistical',
                'total_time': sum_durations(raw_events),
                'top_applications': [
                    {
                        'app': event.data.get('app', 'Unknown'),
                        'duration': event.duration,
                        'percentage': event.duration / sum_durations(raw_events) * 100
                    } for event in top_apps
                ],
                'longest_sessions': [
                    {
                        'app': event.data.get('app'),
                        'title': event.data.get('title', '')[:50] + '...',
                        'duration': event.duration,
                        'timestamp': event.timestamp
                    } for event in longest_sessions
                ]
            }
        
        else:
            # 短期数据：提供原始使用数据
            sorted_events = sort_by_timestamp(raw_events)
            
            results[period] = {
                'type': 'raw',
                'total_events': len(sorted_events),
                'total_time': sum_durations(sorted_events),
                'events': [
                    {
                        'timestamp': event.timestamp,
                        'duration': event.duration,
                        'app': event.data.get('app'),
                        'title': event.data.get('title', ''),
                        'url': event.data.get('url', '') if 'url' in event.data else None
                    } for event in sorted_events
                ]
            }
    
    return results

# 使用示例
activity_data = get_activity_analysis()

# 访问不同时间范围的数据
print(f"近7日最常用应用: {activity_data['7d']['top_applications'][0]['app']}")
print(f"近5分钟活动事件数: {activity_data['5m']['total_events']}")
```

## Event 数据结构

```python
class Event:
    id: Optional[Union[int, str]]           # 事件ID
    timestamp: datetime                     # 事件时间戳
    duration: timedelta                     # 事件持续时间
    data: dict                             # 事件数据
    
    # 常见的data字段:
    # - app: 应用程序名称
    # - title: 窗口标题或文档名称  
    # - url: 网页URL（浏览器事件）
    # - category: 分类标签（如果已分类）
```

## 常用数据桶类型

- `aw-watcher-window_{hostname}`: 窗口活动数据
- `aw-watcher-afk_{hostname}`: AFK状态数据  
- `aw-watcher-web-*`: 网页浏览数据
- `aw-server-api-heartbeats_{hostname}`: API心跳数据 