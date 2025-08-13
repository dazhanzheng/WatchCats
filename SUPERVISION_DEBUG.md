# 监督模式调试指南

## 当前设置

✅ **检查间隔已设置为 5 秒**（用于调试）

## 快速操作

### 1. 查看当前间隔
```bash
./venv/bin/python set_supervision_interval.py
```

### 2. 切换间隔设置
```bash
# 调试模式（5秒）
./venv/bin/python set_supervision_interval.py 5

# 正常模式（5分钟）
./venv/bin/python set_supervision_interval.py 300

# 自定义（如30秒）
./venv/bin/python set_supervision_interval.py 30
```

### 3. 使用环境变量临时覆盖
```bash
# 临时使用10秒间隔
SUPERVISION_CHECK_INTERVAL=10 ./venv/bin/python run_desktop_pet.py
```

## 测试脚本

### 完整测试（带UI）
```bash
./venv/bin/python test_supervision_5s.py
```

### AFK检测测试
```bash
./venv/bin/python test_afk_detection_simple.py
```

## 调试技巧

### 1. 开启开发者控制台
- 运行应用
- 右键系统托盘 → 开发者控制台
- 切换到"监督模式"选项卡查看日志

### 2. 监督模式日志关键信息
```
INFO - 监督模式已启动 - 长期目标: xxx
INFO - 检查线程已启动，每5秒检查一次
INFO - 开始检查活动... (时间: HH:MM:SS)
INFO - AFK检查结果: afk_seconds=X, continuous_afk=False, is_afk=False
DEBUG - 用户活跃，获取活动统计...
INFO - 评估结果: should_remind=True/False, deviation_level=高/中/低
```

### 3. 测试场景

#### 场景A：正常活动监督
1. 启动应用
2. 设置监督目标（如"专注编程"）
3. 开启监督模式
4. 正常使用电脑
5. 每5秒查看日志，确认检查执行

#### 场景B：AFK跳过测试
1. 启动监督模式
2. 离开电脑5分钟
3. 查看日志确认显示"用户处于AFK状态，跳过监督检查"

#### 场景C：偏离提醒测试
1. 设置目标为"专注编程"
2. 打开娱乐网站或游戏
3. 等待5-10秒
4. 应该收到偏离提醒

## 重要提示

⚠️ **发布前必须恢复为300秒**
```bash
./venv/bin/python set_supervision_interval.py 300
```

## 当前配置详情

- **文件**: `/baal/desktop_pet/supervision_mode.py`
- **当前值**: 5秒（调试模式）
- **默认值**: 300秒（5分钟）
- **环境变量**: `SUPERVISION_CHECK_INTERVAL`

## 更新记录

- 2025-08-13: 设置为5秒用于调试
- 创建快速切换工具 `set_supervision_interval.py`