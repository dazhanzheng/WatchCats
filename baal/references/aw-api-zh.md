# ActivityWatch Python API 使用指南

## 总结

这份文档介绍了ActivityWatch的Python API，可以帮助开发者创建Python程序来访问和分析ActivityWatch收集的时间追踪数据。主要用途包括：

### 核心功能
1. **数据访问**：通过 `aw_client.ActivityWatchClient` 连接到ActivityWatch服务器，读取和写入事件数据
2. **数据存储**：使用桶（bucket）来组织不同类型的活动数据（如窗口活动、AFK状态等）
3. **数据查询**：使用强大的查询语言（aw_query）来分析和聚合时间数据
4. **数据转换**：使用 `aw_transform` 包提供的函数来处理和转换事件数据

### 典型使用场景
- 创建自定义的活动监视器（watcher）
- 分析个人时间使用情况
- 生成定制化的时间报告
- 将ActivityWatch数据导出到其他系统
- 开发时间管理和生产力工具

### 快速开始示例
```python
from aw_client import ActivityWatchClient
from datetime import datetime, timezone

# 创建客户端连接
client = ActivityWatchClient("my-client")

# 创建一个桶来存储数据
bucket_id = "my-bucket"
client.create_bucket(bucket_id, event_type="app.usage")

# 发送心跳事件
from aw_core import Event
event = Event(
    timestamp=datetime.now(timezone.utc),
    data={"app": "VSCode", "title": "coding"}
)
client.heartbeat(bucket_id, event, pulsetime=60)

# 查询数据
events = client.get_events(bucket_id, limit=100)
```

---

# API 参考（Python）

这里是 aw_core、aw_client 和 aw_server 中一些最核心组件的API参考。这些是ActivityWatch中最重要的包。虽然目前很多部分还缺少适当的文档字符串，但这是一个开始。

## 目录

- API 参考（Python）
  - aw_core
  - aw_core.models
  - aw_core.log
  - aw_core.dirs
  - aw_client
  - aw_transform
  - aw_query
  - aw_server
  - aw_server.api

## aw_core

### class aw_core.Event
`Event(id: Optional[Union[int, str]] = None, timestamp: Optional[Union[datetime.datetime, str]] = None, duration: Union[datetime.timedelta, int, float] = 0, data: Optional[Dict[str, Any]] = None)`

用于表示一个事件。

#### 属性

**property data: dict**  
事件的数据字典

**property duration: datetime.timedelta**  
事件的持续时间

**property id: Optional[Union[int, str]]**  
事件的唯一标识符

**property timestamp: datetime.datetime**  
事件的时间戳

#### 方法

**to_json_dict() → dict**  
在通过网络发送数据时很有用。任何mongodb互操作都不应该使用这个方法，因为它直接接受datetime对象。

**to_json_str() → str**  
将事件转换为JSON字符串

## aw_core.models

### class aw_core.models.Event
`Event(id: Optional[Union[int, str]] = None, timestamp: Optional[Union[datetime.datetime, str]] = None, duration: Union[datetime.timedelta, int, float] = 0, data: Optional[Dict[str, Any]] = None)`

用于表示一个事件。

#### 属性

**property data: dict**  
事件的数据字典

**property duration: datetime.timedelta**  
事件的持续时间

**property id: Optional[Union[int, str]]**  
事件的唯一标识符

**property timestamp: datetime.datetime**  
事件的时间戳

#### 方法

**to_json_dict() → dict**  
在通过网络发送数据时很有用。任何mongodb互操作都不应该使用这个方法，因为它直接接受datetime对象。

**to_json_str() → str**  
将事件转换为JSON字符串

## aw_core.log

**get_latest_log_file(name, testing=False) → Optional[str]**  
返回指定名称的最新日志文件的文件名。当你想要读取另一个ActivityWatch服务的日志文件时很有用。

**get_log_file_path() → Optional[str]**  
已废弃：请使用 get_latest_log_file 代替。

**setup_logging(name: str, testing=False, verbose=False, log_stderr=True, log_file=False)**  
设置日志记录

## aw_core.dirs

**ensure_path_exists(path: str) → None**  
确保路径存在

**get_cache_dir(module_name: Optional[str] = None) → str**  
获取缓存目录

**get_config_dir(module_name: Optional[str] = None) → str**  
获取配置目录

**get_data_dir(module_name: Optional[str] = None) → str**  
获取数据目录

**get_log_dir(module_name: Optional[str] = None) → str**  
获取日志目录

## aw_client

aw_client 包包含了一个对程序员友好的服务器REST API封装。

### class aw_client.ActivityWatchClient
`ActivityWatchClient(client_name: str = 'unknown', testing=False, host=None, port=None, protocol='http')`

#### 方法

**connect()**  
连接到服务器

**create_bucket(bucket_id: str, event_type: str, queued=False)**  
创建一个桶

**delete_bucket(bucket_id: str, force: bool = False)**  
删除一个桶

**delete_event(bucket_id: str, event_id: int) → None**  
删除一个事件

**disconnect()**  
断开与服务器的连接

**export_all() → dict**  
导出所有数据

**export_bucket(bucket_id) → dict**  
导出指定桶的数据

**get_buckets() → dict**  
获取所有桶的列表

**get_event(bucket_id: str, event_id: int) → Optional[aw_core.models.Event]**  
获取单个事件

**get_eventcount(bucket_id: str, limit: int = -1, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None) → int**  
获取事件数量

**get_events(bucket_id: str, limit: int = -1, start: Optional[datetime.datetime] = None, end: Optional[datetime.datetime] = None) → List[aw_core.models.Event]**  
获取事件列表

**get_info()**  
返回一个字典，当前包含 'hostname' 和 'testing' 键。

**get_setting(key: Optional[str] = None) → dict**  
获取设置

**heartbeat(bucket_id: str, event: aw_core.models.Event, pulsetime: float, queued: bool = False, commit_interval: Optional[float] = None) → None**  
发送心跳事件

参数：
- bucket_id: 要发送心跳的桶ID
- event: 实际的心跳事件
- pulsetime: 自上次心跳以来的最大时间（秒），在此时间内的心跳将与前一个心跳合并
- queued: 使用aw-client队列功能，在客户端与服务器失去连接时将事件加入队列
- commit_interval: 覆盖默认的预合并提交间隔

注意：此端点可以使用失败请求重试队列。这使得请求本身是非阻塞的，因此在这种情况下函数总是返回None。

**import_bucket(bucket: dict) → None**  
导入一个桶

**insert_event(bucket_id: str, event: aw_core.models.Event) → None**  
插入单个事件

**insert_events(bucket_id: str, events: List[aw_core.models.Event]) → None**  
插入多个事件

**query(query: str, timeperiods: List[Tuple[datetime.datetime, datetime.datetime]], name: Optional[str] = None, cache: bool = False) → List[Any]**  
执行查询

**set_setting(key: str, value: str) → None**  
设置配置项

**setup_bucket(bucket_id: str, event_type: str)**  
设置桶（如果不存在则创建）

**wait_for_start(timeout: int = 10) → None**  
通过尝试获取服务器信息来等待服务器启动。

## aw_transform

aw_transform 包包含了查询语言中使用的转换函数。

注意：它们的函数签名和返回类型可能与查询语言中的实际实现有所不同。更多详情请参见 aw_query.functions

### class aw_transform.Rule
`Rule(rules: Dict[str, Any])`

分类规则类

**ignore_case: bool**  
是否忽略大小写

**match(e: aw_core.models.Event) → bool**  
检查事件是否匹配规则

**regex: Optional[Pattern]**  
正则表达式模式

**select_keys: Optional[List[str]]**  
选择的键列表

### 转换函数

**categorize(events: List[Event], classes: List[Tuple[List[str], Rule]]) → List[Event]**  
对事件进行分类

**chunk_events_by_key(events: List[Event], key: str, pulsetime: float = 5.0) → List[Event]**  
根据键值将相邻的事件"分块"在一起，具有相同键值的相邻事件会被合并，原始事件存储在新事件的subevents键中。

**concat(events1, events2) → List[Event]**  
连接两个事件列表

**filter_keyvals(events: List[Event], key: str, vals: List[str], exclude=False) → List[Event]**  
根据键值过滤事件

**filter_keyvals_regex(events: List[Event], key: str, regex: str) → List[Event]**  
使用正则表达式根据键值过滤事件

**filter_period_intersect(events: List[Event], filterevents: List[Event]) → List[Event]**  
过滤掉所有没有与过滤事件时间段相交的事件或事件时间段。

例如，当你想要过滤掉用户AFK期间的事件或部分事件时很有用。

用法：
```python
windowevents_notafk = filter_period_intersect(windowevents, notafkevents)
```

示例：
```
events1   |   =======        ======== |
events2   | ------  ---  ---   ----   |
result    |   ====  =          ====   |
```

**flood(events: List[Event], pulsetime: float = 5) → List[Event]**  
获取事件列表并"填充"事件之间的任何空白空间，通过扩展周围的一个事件来覆盖空白空间。

有关填充的更多详情，请参见此问题：https://github.com/ActivityWatch/activitywatch/issues/124

**heartbeat_merge(last_event: Event, heartbeat: Event, pulsetime: float) → Optional[Event]**  
如果两个事件具有相同的数据且心跳时间戳在脉冲时间窗口内，则合并它们。

**heartbeat_reduce(events: List[Event], pulsetime: float) → List[Event]**  
根据heartbeat_merge的规则将连续事件合并在一起。

**limit_events(events, count) → List[Event]**  
返回事件列表中的前count个事件

**merge_events_by_keys(events, keys) → List[Event]**  
将共享键值的所有事件的持续时间相加，并为每个值返回一个新事件。

**period_union(events1: List[Event], events2: List[Event]) → List[Event]**  
获取两个事件列表，返回一个新的事件列表，覆盖事件列表中包含的时间段的并集，没有重叠事件。

警告：此函数会从事件中剥离所有数据，因为它无法保持数据的一致性。

示例：
```
events1   |   -------       --------- |
events2   | ------  ---  --    ----   |
result    | -----------  -- --------- |
```

**simplify_string(events: List[Event], key: str = 'title') → List[Event]**  
简化字符串

**sort_by_duration(events) → List[Event]**  
按持续时间对事件列表排序

**sort_by_timestamp(events) → List[Event]**  
按时间戳对事件列表排序

**split_url_events(events: List[Event]) → List[Event]**  
分割URL事件

**sum_durations(events) → datetime.timedelta**  
计算给定事件的持续时间总和

**tag(events: List[Event], classes: List[Tuple[str, Rule]]) → List[Event]**  
为事件添加标签

**union(events1: List[Event], events2: List[Event]) → List[Event]**  
连接并排序两个事件列表的并集，并删除重复项。

示例：从备份桶与"活动"桶合并事件。
```python
events = union(events_backup, events_living)
```

**union_no_overlap(events1: List[Event], events2: List[Event]) → List[Event]**  
合并两个事件列表并删除重叠，第一个事件列表具有优先权

示例：
```
events1 | xxx   xx    xxx     |
events2 | ----  ----  --      |
result  | xxx-- xx ---xxx --  |
```

## aw_query

aw_query 包包含查询语言的解释器和注册的标准函数，通常基于 aw_transform 中可用的Python实现。

**query(name: str, query: str, starttime: datetime, endtime: datetime, datastore: Datastore) → Any**  
执行查询

### aw_query.functions

查询语言中可用的函数：

- **q2_categorize(events: list, classes: list)**
- **q2_chunk_events_by_key(events: list, key: str) → List[Event]**
- **q2_concat(events1: list, events2: list) → List[Event]**
- **q2_exclude_keyvals(events: list, key: str, vals: list) → List[Event]**
- **q2_filter_keyvals(events: list, key: str, vals: list) → List[Event]**
- **q2_filter_keyvals_regex(events: list, key: str, regex: str) → List[Event]**
- **q2_filter_period_intersect(events: list, filterevents: list) → List[Event]**
- **q2_find_bucket(datastore: Datastore, filter_str: str, hostname: Optional[str] = None)**  
  使用filter_str查找桶（避免硬编码桶名称）
- **q2_flood(events: list) → List[Event]**
- **q2_limit_events(events: list, count: int) → List[Event]**
- **q2_merge_events_by_keys(events: list, keys: list) → List[Event]**
- **q2_nop()**  
  用于单元测试的无操作函数
- **q2_period_union(events1: list, events2: list) → List[Event]**
- **q2_query_bucket(datastore: Datastore, namespace: Dict[str, Any], bucketname: str) → List[Event]**
- **q2_query_bucket_eventcount(datastore: Datastore, namespace: Dict[str, Any], bucketname: str) → int**
- **q2_simplify_window_titles(events: list, key: str) → List[Event]**
- **q2_sort_by_duration(events: list) → List[Event]**
- **q2_sort_by_timestamp(events: list) → List[Event]**
- **q2_split_url_events(events: list) → List[Event]**
- **q2_sum_durations(events: list) → timedelta**
- **q2_tag(events: list, classes: list)**
- **q2_union_no_overlap(events1: list, events2: list) → List[Event]**

## aw_server

**main()**  
从可执行文件和 __main__.py 调用

## aw_server.api

ServerAPI 类包含基本的API方法，这些方法主要从RPC层调用，例如在 aw_server.rest 中找到的那些。

### class aw_server.api.ServerAPI
`ServerAPI(db, testing)`

#### 方法

**create_bucket(bucket_id: str, event_type: str, client: str, hostname: str, created: Optional[datetime] = None, data: Optional[Dict[str, Any]] = None) → bool**  
创建一个桶。

如果hostname是"!local"，hostname和device_id将从服务器信息中设置。这对于已知/假定在本地运行但可能不知道其主机名的监视器（如aw-watcher-web）很有用。

如果成功返回True，如果具有给定ID的桶已存在则返回False。

**create_events(bucket_id: str, events: List[Event]) → Optional[Event]**  
为桶创建事件。可以处理单个事件和多个事件。

插入单个事件时返回插入的事件，否则返回None。

**delete_bucket(bucket_id: str) → None**  
删除一个桶

**delete_event(bucket_id: str, event_id) → bool**  
从桶中删除单个事件

**export_all() → Dict[str, Any]**  
导出所有桶及其事件到跨版本一致的格式

**export_bucket(bucket_id: str) → Dict[str, Any]**  
将桶导出为跨版本一致的数据格式，包括其中的所有事件。

**get_bucket_metadata(bucket_id: str) → Dict[str, Any]**  
获取桶的元数据。

**get_buckets() → Dict[str, Dict]**  
获取所有桶的字典 {bucket_name: Bucket}

**get_event(bucket_id: str, event_id: int) → Optional[Event]**  
从桶中获取单个事件

**get_eventcount(bucket_id: str, start: Optional[datetime] = None, end: Optional[datetime] = None) → int**  
获取桶中的事件数量

**get_events(bucket_id: str, limit: int = -1, start: Optional[datetime] = None, end: Optional[datetime] = None) → List[Event]**  
从桶中获取事件

**get_info() → Dict[str, Any]**  
获取服务器信息

**get_log()**  
以json格式获取服务器日志

**get_setting(key)**  
获取设置

**heartbeat(bucket_id: str, heartbeat: Event, pulsetime: float) → Event**  
心跳在实现简单跟踪状态、状态持续时间和状态变化的监视器时很有用。单个心跳的持续时间始终为零。

如果心跳与最后一个相同（除了时间戳），则更新最后一个事件的持续时间。如果心跳不同，则创建一个新事件。

例如：
- 活动应用程序和窗口标题 - 示例：aw-watcher-window
- 当前打开的文档/浏览器标签/正在播放的歌曲 
  - 示例：wakatime
  - 示例：aw-watcher-web
  - 示例：aw-watcher-spotify
- 用户是否活跃/不活跃？在某个间隔发送事件指示用户是否活跃。
  - 示例：aw-watcher-afk

灵感来自：https://wakatime.com/developers#heartbeats

**import_all(buckets: Dict[str, Any])**  
导入所有数据

**import_bucket(bucket_data: Any)**  
导入桶数据

**query2(name, query, timeperiods, cache)**  
执行查询

**set_setting(key, value)**  
设置配置项

**update_bucket(bucket_id: str, event_type: Optional[str] = None, client: Optional[str] = None, hostname: Optional[str] = None, data: Optional[Dict[str, Any]] = None) → None**  
更新桶的属性 