# CLAUDE.md

此文件为 Claude Code (claude.ai/code) 在处理此代码库时提供指导。

## 项目概述

Baal 桌面宠物助手（Baal Desktop Pet Assistant）是一个基于 AI 的桌面伴侣应用程序。它以黑猫恶魔"巴利"的形象出现，监控用户的计算机活动并通过自然语言对话提供帮助。这是一个精简的独立版本，移除了所有不必要的 ActivityWatch 开发组件，只保留桌面宠物功能所需的最小依赖。

### 核心特性
- **AI 驱动的对话**: 通过 LangChain 集成 OpenAI 兼容的 LLM（包括火山引擎）
- **ActivityWatch 集成**: 监控和分析用户活动数据，提供生产力洞察
- **动态表情系统**: 7 种不同的面部表情和基础动画，根据对话内容动态切换
- **流式响应**: 逐字符显示文本，带有标点符号延迟，营造打字效果
- **并行工具调用**: 优化的并发数据查询，提高复杂请求的响应速度
- **日程管理**: 内置日历系统，支持任务调度和提醒
- **系统托盘集成**: 始终置顶的浮动窗口，带系统托盘图标
- **刘海屏适配**: macOS 上自动检测并避开刘海屏区域（顶部90像素安全区）
- **人格系统**: 3种可切换的性格模式（严格主人、嘲讽管家、温柔伴侣）
- **单实例保护**: 防止多个应用实例同时运行
- **跨平台配置**: Windows/macOS 统一的配置管理系统

### 角色设定
- **名称**: 巴利（Baal）
- **形象**: 黑猫恶魔，权威的监督者
- **性格**: 严格、命令式、略带傲慢
- **语言风格**: 使用中文，简洁有力的命令语气
- **角色定位**: 用户的"主人"，监督并评判其生产力

## ⚠️ 极其重要：必须始终使用虚拟环境

**所有 Python 命令都必须在虚拟环境中执行！**
```bash
# 永远使用虚拟环境中的 Python
./venv/bin/python  # 而不是 python
./venv/bin/pip     # 而不是 pip
./venv/bin/pyinstaller  # 而不是 pyinstaller

# 或者先激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

## 项目结构

```
baal-standalone/
├── baal/                      # 核心模块
│   ├── desktop_pet/          # 桌面宠物主模块
│   │   ├── core/            # 核心功能（配置、LLM、表情）
│   │   │   ├── config_manager.py     # API 密钥和设置管理（跨平台支持）
│   │   │   ├── llm_handler.py        # LLM 交互和流式响应
│   │   │   ├── emotion_manager.py    # 表情状态管理
│   │   │   ├── persona_manager.py    # 人格系统管理
│   │   │   └── single_instance.py    # 单实例运行保护
│   │   ├── ui/              # UI 组件
│   │   │   ├── pet_window.py         # 主宠物窗口
│   │   │   ├── chat_bubble.py        # 对话气泡
│   │   │   ├── settings_dialog.py    # 设置对话框
│   │   │   ├── supervision_dialog.py # 监督模式对话框
│   │   │   ├── goals_dialog.py       # 目标管理对话框
│   │   │   └── calendar_dialog_modern.py # 现代化日历界面
│   │   ├── main.py          # 主入口点
│   │   └── supervision_mode.py # 生产力监督系统
│   ├── llm_assistant/       # LangChain 集成
│   │   ├── assistant.py    # 完整功能的 LLM 助手
│   │   ├── binary_intent_classifier.py # 意图分类器
│   │   └── parsers.py       # 结构化命令解析器
│   ├── aw_stats/           # ActivityWatch 数据处理
│   │   └── stats_processor.py # 活动数据分析
│   ├── scheduler/          # 日程管理
│   │   └── schedule_manager.py # 日历和任务管理
│   ├── references/         # API 文档和示例
│   └── resources/          # 图标和资源文件
├── 动作表情拆分/            # 表情素材
│   ├── 巴力2.gif           # 基础动画
│   └── *.png               # 7 种表情图片
├── scripts/                # 构建和实用脚本
│   ├── dmgbuild-settings.py # DMG 创建配置
│   └── create_multisize_ico.py # 多尺寸图标生成
├── installer/              # Windows 安装程序
│   └── baal_installer.iss # Inno Setup 配置
├── venv/                   # Python 3.9 虚拟环境
├── run_desktop_pet.py      # 主入口脚本
├── build.sh               # macOS 自动化构建脚本
├── build_macos.sh         # 增强 macOS 构建脚本
├── build_windows.ps1      # Windows PowerShell 构建脚本（推荐）
├── fix_app.sh             # 应用修复脚本
├── baal.spec              # 通用 PyInstaller 配置
├── baal_macos.spec        # macOS 专用配置
├── baal_windows.spec      # Windows 专用配置
├── requirements.txt       # Python 依赖
├── Info.plist            # macOS 应用元数据
└── CLAUDE.md             # 本文档
```

## 常用开发命令

### 环境设置
```bash
# 创建虚拟环境（如果不存在）
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
./venv/bin/pip install -r requirements.txt
```

### 运行命令
```bash
# 运行桌面宠物（推荐方式）
./venv/bin/python run_desktop_pet.py

# 备用运行方式
./venv/bin/python -m baal.desktop_pet
./venv/bin/python baal/desktop_pet/main.py
```

### 构建命令
```bash
# macOS 构建
./build.sh                   # 基础构建脚本
./build_macos.sh            # 增强构建（带图标和 DMG）

# Windows 构建
.\build_windows.ps1         # PowerShell 脚本（推荐）

# 手动 PyInstaller 构建
./venv/bin/pyinstaller --clean --noconfirm baal.spec        # 通用
./venv/bin/pyinstaller --clean --noconfirm baal_macos.spec  # macOS
./venv/bin/pyinstaller --clean --noconfirm baal_windows.spec # Windows

# 创建 DMG（macOS 分发）
dmgbuild -s scripts/dmgbuild-settings.py -D app=dist/Watch\ Cats.app "Watch Cats" dist/Watch\ Cats.dmg

# 修复应用（如需要）
./fix_app.sh
```


## 技术架构

### 关键技术栈
- **Python 3.9+**: 主要编程语言
- **PyQt6 6.5.3**: 桌面 UI 框架（注意：与 ActivityWatch 的 PyQt5 分离）
- **LangChain 0.3.26**: LLM 集成和工具编排
- **aw-client/aw-core**: ActivityWatch API 客户端
- **PyInstaller**: 应用打包工具
- **dmgbuild**: macOS DMG 创建

### 核心组件

#### 1. 桌面宠物 UI（PyQt6）
- **PetWindow**: 可拖动的浮动主窗口，显示猫咪头像
- **ChatBubble**: 可调整大小的对话气泡，支持滚动
- **SettingsDialog**: API 密钥配置界面
- **SupervisionDialog**: 高级监控设置
- **GoalsDialog**: 长期目标管理
- **CalendarDialogModern**: 现代化日历界面
  - 月/周/日三种视图模式
  - 拖拽调整日程时间
  - 最小高度保证短时长日程可见

#### 2. LLM 集成
- **LLMHandler**: 管理流式聊天和响应生成
- **LLMAssistant**: 具有工具访问权限的完整助手
- **BinaryIntentClassifier**: 判断查询是否需要数据访问
- **并行工具调用**: 优化的并发查询执行
- **ScheduleCommandParser**: 自然语言到日程命令的精确解析
  - 动态日期注入：实时获取系统日期避免 LLM 幻觉
  - 相对日期映射：今天/明天/后天的明确定义
- **StatsCommandParser**: ActivityWatch 查询命令解析

#### 3. 数据处理
- **StatsProcessor**: 分析 ActivityWatch 活动数据
  - 应用使用统计
  - 活动模式分析
  - 生产力评估
- **ScheduleManager**: 管理日程和任务
  - iCalendar 格式支持
  - 持久化存储
  - 事件提醒

#### 4. 表情系统
- **EmotionManager**: 管理 7 种表情状态
  - 正常（normal）
  - 开心（happy）
  - 生气（angry）
  - 困惑（confused）
  - 悲伤（sad）
  - 兴奋（excited）
  - 疲倦（tired）
- **动态切换**: 基于对话内容自动切换表情
- **基础动画**: GIF 循环动画作为默认状态

#### 5. 人格系统
- **PersonaManager**: 管理 3 种可切换的性格模式
  - **严格主人（Strict Master）**: 命令式、严厉、高标准
  - **嘲讽管家（Sarcastic Butler）**: 讽刺、幽默、毒舌
  - **温柔伴侣（Gentle Companion）**: 鼓励、关怀、支持
- **运行时切换**: 无需重启即可改变性格
- **持久化保存**: 性格选择在会话间保持

#### 6. 监督模式
- **SupervisionMode**: 生产力监控和评估系统
  - 实时活动跟踪
  - 生产力评分算法
  - 定期提醒和警告
  - 详细的活动报告

### 关键实现细节

#### 流式响应系统
```python
# 逐字符显示，带标点符号延迟
async def stream_response():
    for char in text:
        yield char
        if char in '，。！？':
            await asyncio.sleep(0.3)  # 标点停顿
        else:
            await asyncio.sleep(0.05)  # 普通字符延迟
```

#### 动态日期解析
```python
# baal/llm_assistant/parsers.py
def get_system_prompt(self) -> str:
    """获取包含当前日期的系统提示词"""
    now = datetime.now()
    today = now.date()
    tomorrow = today + timedelta(days=1)
    day_after_tomorrow = today + timedelta(days=2)
    
    return self.system_prompt_template.format(
        current_time=now.strftime("%Y-%m-%d %H:%M:%S"),
        today_date=now.strftime("%Y年%m月%d日"),
        tomorrow_date=tomorrow.strftime("%Y年%m月%d日"),
        day_after_tomorrow_date=day_after_tomorrow.strftime("%Y年%m月%d日"),
        format_instructions=self.parser.get_format_instructions()
    )
```

#### 日历视图最小高度
```python
# baal/desktop_pet/ui/calendar_dialog_modern.py
# 日视图 - 确保短时长日程可见
height = max(30, schedule.duration_minutes * self.hour_height / 60)  # 最小30px

# 周视图 - 较小但仍可见
height = max(25, schedule.duration_minutes * self.hour_height / 60)  # 最小25px
```

#### 并行工具调用
- 同时执行多个 ActivityWatch 查询
- 减少复杂请求的响应时间
- 异步结果聚合

#### 配置管理
- **用户配置路径**:
  - macOS/Linux: `~/.baal_pet/config.json`
  - Windows: `%APPDATA%/BaalPet/config.json`
- **配置内容**:
  - API 密钥（OpenAI、火山引擎等）
  - 用户偏好设置
  - 窗口位置和大小
  - 性格模式选择
  - 监督模式设置
- **跨平台兼容**: 自动处理路径和权限差异
- **持久化存储**: JSON 格式的本地存储

### 构建系统

#### PyInstaller 配置（baal.spec）
- **入口点**: `run_desktop_pet.py`
- **资源收集**: 
  - 表情素材（`动作表情拆分/*`）
  - API 参考文档（`baal/references/*`）
  - 应用图标（`baal/resources/*`）
- **隐藏导入**: 60+ 个必要的模块导入
- **排除项**: PyQt5、numpy、matplotlib 等不必要的库
- **macOS 配置**: LSUIElement=1（菜单栏应用，无 Dock 图标）

#### 构建流程

##### macOS 构建
1. **环境准备**: 自动创建/激活虚拟环境
2. **依赖安装**: 从 requirements.txt 安装所有包
3. **图标生成**: 使用 `create_baal_icons.sh` 创建多分辨率图标
4. **PyInstaller 打包**: 使用 baal_macos.spec 创建应用包
5. **macOS App Bundle**: 生成 .app 包含元数据和图标
6. **DMG 创建**: 可选的磁盘映像用于分发

##### Windows 构建
1. **环境准备**: 创建/激活虚拟环境
2. **依赖安装**: 安装所有必要包
3. **图标转换**: 使用 `convert_icon.py` 生成 Windows 图标
4. **PyInstaller 打包**: 使用 baal_windows.spec 创建 exe
5. **ZIP 打包**: 压缩为分发包

## 依赖项详解

### UI 框架
- **PyQt6**: 主 UI 框架（6.5.3）
- **PyQt6-Qt6**: Qt6 运行时（6.5.3）
- **PyQt6-sip**: Python-Qt 绑定层

### LLM 和 AI
- **langchain**: 核心 LLM 框架（0.3.26）
- **langchain-openai**: OpenAI API 支持（0.3.17）
- **langchain-community**: 社区工具和集成
- **volcengine-python-sdk**: 火山引擎 API（1.0.110）

### ActivityWatch 集成
- **aw-client**: ActivityWatch 客户端（>=0.5.13）
- **aw-core**: 核心数据模型（>=0.5.16）

### 数据处理
- **python-dateutil**: 日期解析和处理
- **pytz**: 时区支持
- **icalendar**: 日历格式支持
- **pydantic**: 数据验证

### 网络和 HTTP
- **httpx**: 现代异步 HTTP 客户端
- **requests**: 传统 HTTP 请求
- **urllib3**: HTTP 库基础

### 开发和打包
- **PyInstaller**: 应用打包（6.11.1）
- **dmgbuild**: macOS DMG 创建（可选）

## 常见问题和解决方案

### 1. PyQt 版本冲突
- **问题**: PyQt5 和 PyQt6 冲突
- **解决**: 构建时明确排除 PyQt5，确保只使用 PyQt6

### 2. API 密钥配置
- **问题**: 首次运行时缺少 API 密钥
- **解决**: 通过设置对话框配置，保存在 `~/.baal_pet/config.json`

### 3. ActivityWatch 连接
- **问题**: 无法获取活动数据
- **解决**: 确保 ActivityWatch 服务正在运行（端口 5600）

### 4. 构建失败
- **问题**: PyInstaller 打包错误
- **解决**: 
  - 确保在虚拟环境中运行
  - 清理 build/ 和 dist/ 目录
  - 使用 `--clean` 标志

### 5. 表情素材缺失
- **问题**: 表情图片不显示
- **解决**: 确保 `动作表情拆分/` 目录包含所有必要的素材文件

### 6. macOS 权限问题
- **问题**: 应用无法运行或被阻止
- **解决**: 
  - 系统偏好设置中允许应用
  - 使用 `xattr -cr` 清除隔离属性
  - 考虑代码签名和公证

### 7. 短时长日程显示问题（2025-08-10 已修复）
- **问题**: 10分钟等短时长日程在日历视图中不可见
- **原因**: 日历组件的最小高度限制太小（15-20像素）
- **解决**: 
  - 日视图最小高度从 20px 增加到 30px
  - 周视图最小高度从 15px 增加到 25px
  - 文件: `baal/desktop_pet/ui/calendar_dialog_modern.py`（行 531, 778）

### 8. 日期解析错误（2025-08-10 已修复）
- **问题**: LLM 将"今天"解析为错误日期（如1月15日而非实际日期）
- **原因**: 系统提示词未包含当前系统时间，LLM 使用训练数据中的日期
- **解决**: 
  - 在 `ScheduleCommandParser` 的系统提示词中动态注入当前日期
  - 添加明确的相对日期映射（今天、明天、后天）
  - 文件: `baal/llm_assistant/parsers.py`（行 189-251）
  - 关键改动:
    - 添加 `{current_time}`, `{today_date}`, `{tomorrow_date}`, `{day_after_tomorrow_date}` 占位符
    - `get_system_prompt()` 方法动态计算并填充这些日期

### 9. Windows 配置保存问题（2025-08-11 已修复）
- **问题**: Windows 上配置文件无法保存或读取
- **原因**: 权限问题和路径处理不当
- **解决**:
  - 使用 `%APPDATA%/BaalPet/` 作为配置目录
  - 自动创建目录结构
  - 改进错误处理和回退机制
  - 文件: `baal/desktop_pet/core/config_manager.py`

### 10. 多实例运行问题（2025-08-11 已修复）
- **问题**: 可以同时运行多个应用实例，导致冲突
- **原因**: 缺少实例锁定机制
- **解决**:
  - 实现跨平台的单实例保护
  - 使用文件锁和进程检查
  - 文件: `baal/desktop_pet/core/single_instance.py`

## 开发提示

### 最佳实践
1. **始终使用虚拟环境**: 避免系统 Python 污染
2. **测试流式响应**: 使用 `test_parallel_performance.py` 验证性能
3. **检查 API 兼容性**: 支持 OpenAI 兼容的多种 API
4. **保持依赖最小化**: 只包含必要的包
5. **注意内存管理**: 正确清理 Qt 对象和异步任务

### 调试技巧
1. **启用详细日志**: 在 `llm_handler.py` 中设置 DEBUG=True
2. **测试单个组件**: 使用独立的测试脚本
3. **检查配置文件**: 验证 `~/.baal_pet/config.json` 格式
4. **监控网络请求**: 使用代理工具查看 API 调用

### 扩展开发
1. **添加新表情**: 在 `动作表情拆分/` 添加图片，更新 `emotion_manager.py`
2. **自定义工具**: 在 `llm_assistant/tools.py` 添加新工具
3. **新的 UI 组件**: 在 `desktop_pet/ui/` 创建新的对话框
4. **API 提供商**: 在 `llm_handler.py` 添加新的 LLM 配置

## 发布流程

### 1. 版本准备
- 更新版本号（如需要）
- 运行所有测试套件
- 确保文档更新

### 2. 构建应用
```bash
./build.sh  # 自动化构建
```

### 3. 测试构建
- 运行 `dist/Watch Cats.app`
- 测试所有核心功能
- 验证 API 连接

### 4. 创建分发包
```bash
# 创建 DMG（如果 build.sh 提示）
dmgbuild -s scripts/dmgbuild-settings.py -D app=dist/Watch\ Cats.app "Watch Cats" dist/Watch\ Cats.dmg
```

### 5. macOS 公证（可选）
- 代码签名
- 提交公证
- 装订票据

## 项目特色

### 创新功能
1. **双 PyQt 兼容性管理**: 巧妙处理 PyQt5/PyQt6 共存
2. **流式字符显示**: 带标点延迟的逐字动画
3. **并行工具编排**: 并发 ActivityWatch 查询优化
4. **情感驱动 UI**: 基于对话内容的动态视觉反馈
5. **最小依赖设计**: 专注核心功能的精简版本
6. **多人格系统**: 可切换的 AI 性格模式
7. **智能监督模式**: 生产力监控和实时反馈
8. **跨平台统一**: Windows/macOS 无缝体验

### 生产就绪特性
- **全面的错误处理**: 组件缺失时的优雅降级
- **资源管理**: 正确的清理和内存管理
- **跨平台准备**: Windows/macOS/Linux 兼容性基础
- **日志和调试**: 广泛的调试输出和错误跟踪
- **配置持久化**: 设置和状态的会话间保持

## 许可和归属

本项目是 ActivityWatch 的修改版本，添加了 AI 桌面宠物功能。遵循原项目的开源许可。

## 技术文档

详细的技术实现和架构文档请参阅：[TECHNICAL_REFERENCE.md](./TECHNICAL_REFERENCE.md)

该文档包含：
- 完整的项目架构图
- 所有核心模块的详细API文档
- 关键功能的实现细节
- 性能优化策略
- 错误处理机制
- 构建和部署指南

---

*最后更新: 2025-08-31*
*由 Claude Code 维护*

## 更新日志

### 2025-08-31
- **技术文档创建**: 创建全面的技术参考文档 TECHNICAL_REFERENCE.md
  - 详细的项目架构图和模块关系
  - 所有核心类和函数的API文档
  - 关键功能实现细节（表情系统、流式响应、并行工具调用等）
  - 性能优化要点和内存管理策略
  - 完整的错误处理机制说明
  - PyInstaller配置和构建流程详解
- **文档更新**: 更新 CLAUDE.md 添加技术文档链接

### 2025-08-28
- **大规模代码清理**: 删除40+个垃圾文件，减少项目体积约850KB
  - 移除17个测试文件（test_*.py）
  - 删除13个调试和修复脚本（debug_*.py, *_fix.py等）
  - 整合4个重复的图标转换脚本，保留最完整的版本
  - 清理6个重复的构建脚本（保留PowerShell版本）
  - 删除2个低质量图标文件
- **项目结构优化**: 
  - 简化构建脚本，统一使用PowerShell（Windows）
  - 保留单一的图标生成工具（scripts/create_multisize_ico.py）
  - 移除所有临时和调试相关文件
- **文档更新**: 更新 CLAUDE.md 反映清理后的项目状态

### 2025-08-13
- **代码清理**: 删除12个重复和无用的文件
  - 移除重复的入口文件（run_baal.py, baal/main.py）
  - 移除未使用的模块（config_manager_enhanced.py, windows_utils.py）
  - 清理过时的测试文件（6个不再需要的测试）
  - 删除分发DMG文件
- **文档更新**: 更新 CLAUDE.md 反映当前项目状态
  - 更新项目结构说明
  - 移除对已删除文件的引用
  - 更新测试命令列表
- **代码优化**: 清理无用的代码注释和调试语句

### 2025-08-12
- **清理**: 移除重复的 parsers 2.py 文件
- **文档**: 全面更新 CLAUDE.md，添加最新功能描述
- **文档**: 更新项目结构说明，反映当前代码组织

### 2025-08-11
- **新增**: 人格系统（PersonaManager）- 3种可切换的AI性格
  - 严格主人：命令式、高标准的监督者
  - 嘲讽管家：毒舌、讽刺的助手
  - 温柔伴侣：鼓励、关怀的陪伴者
- **新增**: 单实例保护（SingleInstance）- 防止多个应用同时运行
- **新增**: 监督模式（SupervisionMode）- 生产力监控系统
- **改进**: Windows 配置管理 - 使用 AppData 目录，改进权限处理
- **新增**: 跨平台构建脚本
  - build_macos.sh：增强的 macOS 构建
  - build_windows.ps1：PowerShell Windows 构建
  - build_windows.bat：批处理 Windows 构建
- **新增**: 平台专用 PyInstaller 配置
  - baal_macos.spec：macOS 优化配置
  - baal_windows.spec：Windows 优化配置

### 2025-08-10
- **修复**: 短时长日程（10分钟）在日历视图中不可见的问题
  - 调整日视图和周视图的最小高度限制
  - 确保所有日程都能正确显示
- **修复**: LLM 日期解析错误（将"今天"识别为错误日期）
  - 在系统提示词中动态注入当前系统日期
  - 添加相对日期（今天/明天/后天）的明确映射
  - 防止 LLM 使用训练数据中的过期日期
- **改进**: 更新文档结构，添加详细的问题追踪和解决方案

### 2025-08-07
- 初始版本发布
- 基础功能实现