# 开发者模式使用指南

## 功能概述

开发者模式为 Baal 桌宠应用提供了强大的调试和监控功能，包括：

- **实时日志查看**: 查看所有模块的实时日志输出
- **监督模式调试**: 专门查看监督模式的详细日志
- **性能监控**: 跟踪应用性能指标
- **日志统计**: 查看日志级别和模块分布统计
- **日志过滤和搜索**: 按级别、模块、关键词过滤日志
- **日志导出**: 将日志导出为文本或JSON格式

## 启用/禁用开发者模式

### 方法1：使用切换脚本（推荐）

```bash
# 切换状态（启用变禁用，禁用变启用）
./venv/bin/python toggle_developer_mode.py

# 明确启用
./venv/bin/python toggle_developer_mode.py on

# 明确禁用（发布前执行）
./venv/bin/python toggle_developer_mode.py off
```

### 方法2：手动编辑配置文件

编辑 `developer_config.json` 文件：

```json
{
  "show_developer_mode": true,  // true=显示，false=隐藏
  "developer_mode_comment": "将此设置为false可以隐藏开发者模式菜单选项"
}
```

## 访问开发者控制台

1. 启动 Baal 应用
2. 右键点击系统托盘图标
3. 选择"开发者控制台"菜单项

## 控制台功能说明

### 主界面布局

```
┌─────────────────────────────────────────────────┐
│ 日志级别 [▼] 模块 [▼] 搜索 [_____] □自动滚动 [清空] [导出] │
├─────────────────────────────────────────────────┤
│ ┌──────┬──────────┬──────────┬──────────┐      │
│ │主日志│监督模式  │性能监控  │统计信息  │      │
│ ├──────┴──────────┴──────────┴──────────┤      │
│ │                                        │      │
│ │  [日志内容显示区域]                     │      │
│ │                                        │      │
│ └────────────────────────────────────────┘      │
│ 日志数量: 150 / 10000                           │
└─────────────────────────────────────────────────┘
```

### 选项卡说明

1. **主日志**: 显示所有模块的日志
2. **监督模式**: 仅显示监督模式相关日志
3. **性能监控**: 显示性能相关日志（响应时间、内存使用等）
4. **统计信息**: 显示日志统计（级别分布、模块分布、最近错误）

### 过滤功能

- **日志级别**: ALL, DEBUG, INFO, WARNING, ERROR, CRITICAL
- **模块过滤**: ALL, supervision, llm, ui, core, scheduler
- **搜索**: 输入关键词实时过滤日志

### 日志颜色编码

- 🔵 DEBUG: 灰色
- ⚫ INFO: 黑色
- 🟠 WARNING: 橙色
- 🔴 ERROR: 红色
- 🟣 CRITICAL: 深红色
- 🟢 SUPERVISION: 绿色（监督模式专用）
- 🔷 PERFORMANCE: 蓝色（性能日志专用）

## 监督模式增强日志

监督模式现在包含以下详细日志：

```python
# 启动/停止
logger.info("监督模式已启动 - 长期目标: xxx")
logger.info("监督模式已停止")

# 检查循环
logger.info("检查线程已启动，每300秒检查一次")
logger.debug("执行首次检查...")
logger.debug("执行定期检查... (时间: HH:MM:SS)")

# 活动检查
logger.info("开始检查活动... (时间: HH:MM:SS)")
logger.debug("用户处于AFK状态，跳过监督检查")
logger.debug("用户活跃，获取活动统计...")
logger.debug("统计数据获取成功: [stats_5m, stats_2h, stats_today]")

# 评估结果
logger.info("评估结果: should_remind=True, deviation_level=高")
logger.warning("需要提醒用户！")
logger.info("用户活动符合目标，无需提醒")

# 错误处理
logger.error("首次检查出错: xxx")
logger.error("检查活动时出错: xxx")
logger.error("无法获取统计数据")
```

## 测试命令

```bash
# 测试完整功能（包含桌宠窗口）
./venv/bin/python test_developer_mode.py

# 独立测试控制台（不需要桌宠窗口）
./venv/bin/python test_developer_console_simple.py

# 测试监督模式（快速间隔）
SUPERVISION_CHECK_INTERVAL=30 ./venv/bin/python test_supervision_timer.py
```

## 发布前检查清单

- [ ] 执行 `./venv/bin/python toggle_developer_mode.py off`
- [ ] 确认 `developer_config.json` 中 `show_developer_mode` 为 `false`
- [ ] 构建应用
- [ ] 验证系统托盘菜单中没有"开发者控制台"选项

## 注意事项

1. **性能影响**: 开发者控制台会保存最多10000条日志，可能占用一定内存
2. **隐私考虑**: 日志可能包含敏感信息，发布版本应禁用
3. **日志级别**: 生产环境建议将根日志级别设置为INFO或以上

## 快速调试技巧

1. **监督模式调试**:
   ```bash
   # 设置快速检查间隔（30秒）
   export SUPERVISION_CHECK_INTERVAL=30
   ./venv/bin/python run_desktop_pet.py
   ```

2. **查看特定模块日志**:
   - 在控制台中选择模块过滤器
   - 或在搜索框输入模块名

3. **导出问题日志**:
   - 复现问题
   - 点击"导出日志"
   - 选择JSON格式以保留完整信息

## 更新日志

- 2025-08-13: 初始版本
  - 添加开发者控制台
  - 增强监督模式日志
  - 支持一键隐藏功能