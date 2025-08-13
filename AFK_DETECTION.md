# AFK 检测机制说明

## 概述

监督模式的 AFK（Away From Keyboard）检测用于判断用户是否离开电脑，避免在用户不在时进行无意义的提醒。

## 检测机制

### 1. 数据源
- **ActivityWatch AFK Watcher**: 使用 `aw-watcher-afk` 监视器的数据
- **检测窗口**: 过去5分钟的活动数据

### 2. 判断标准

用户被认为处于 AFK 状态的条件（满足任一即可）：

1. **持续 AFK**: 用户连续超过 4 分钟没有任何活动
2. **最近无活动**: 距离最后一次活动超过 4 分钟
3. **累计 AFK**: 过去 5 分钟内累计 AFK 时间超过 4.5 分钟（270秒）

### 3. 实现细节

```python
def _is_user_afk(self) -> bool:
    """检查用户是否处于持续AFK状态"""
    
    # 从 ActivityWatch 获取 AFK 统计
    afk_stats = sp.get_afk_time_5m()
    
    # 判断条件
    continuous_afk = afk_stats.get('continuous_afk', False)  # 持续AFK标记
    last_active_seconds = afk_stats.get('last_active_seconds_ago', 0)  # 距离最后活动的秒数
    afk_seconds = afk_stats.get('afk_seconds', 0)  # 总AFK秒数
    
    # 满足任一条件即判定为AFK
    is_afk = continuous_afk or last_active_seconds > 240 or afk_seconds > 270
```

## 关键改进（2025-08-13）

### 之前的问题
- 只计算 AFK 事件的总时长，没有考虑连续性
- 用户可能在 5 分钟内有多次短暂的 AFK，但仍在活跃使用电脑

### 改进方案
1. **增加持续性检查**: 不仅计算总 AFK 时间，还要检查是否持续 AFK
2. **追踪最后活动时间**: 记录用户最后一次活动的时间点
3. **多重判断标准**: 综合多个指标判断用户是否真正离开

## 测试方法

### 1. 运行 AFK 检测测试
```bash
./venv/bin/python test_afk_detection_simple.py
```

### 2. 测试场景

#### 场景 A：用户活跃
- 正常使用电脑
- 预期结果：监督模式正常执行检查

#### 场景 B：短暂离开
- 离开 2-3 分钟
- 预期结果：监督模式仍执行检查（未达到 4 分钟阈值）

#### 场景 C：持续 AFK
- 离开超过 4 分钟
- 预期结果：监督模式跳过检查，避免打扰

#### 场景 D：间歇性活动
- 每 2-3 分钟活动一次
- 预期结果：监督模式正常执行检查（非持续 AFK）

## 日志输出

监督模式会输出详细的 AFK 检测日志：

```
INFO - AFK检查结果: afk_seconds=220.9s, continuous_afk=False, last_active=222.9s ago, is_afk=False
```

- `afk_seconds`: 过去 5 分钟的总 AFK 时间
- `continuous_afk`: 是否持续 AFK
- `last_active`: 距离最后一次活动的时间
- `is_afk`: 最终判断结果

## 配置调整

### 修改检查间隔（用于测试）
```bash
# 设置为 30 秒间隔（默认 300 秒）
SUPERVISION_CHECK_INTERVAL=30 ./venv/bin/python run_desktop_pet.py
```

### 调整 AFK 阈值
如需调整 AFK 判断阈值，修改 `supervision_mode.py` 中的常量：

```python
# 当前设置
AFK_THRESHOLD = 240  # 4 分钟
AFK_TOTAL_THRESHOLD = 270  # 4.5 分钟
```

## 注意事项

1. **确保 ActivityWatch 运行**: AFK 检测依赖 `aw-watcher-afk` 服务
2. **时区处理**: 所有时间计算使用 UTC 时区，确保一致性
3. **容错机制**: 如果无法获取 AFK 数据，默认认为用户活跃

## 相关文件

- `/baal/desktop_pet/supervision_mode.py`: 监督模式主逻辑
- `/baal/aw_stats/stats_processor.py`: ActivityWatch 数据处理
- `/test_afk_detection_simple.py`: AFK 检测测试脚本

## 更新历史

- **2025-08-13**: 改进 AFK 检测机制
  - 添加持续 AFK 检查
  - 追踪最后活动时间
  - 增强日志输出