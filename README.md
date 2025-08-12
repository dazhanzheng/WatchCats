# Baal 桌面宠物助手 - 独立版

🐈 **Baal Desktop Pet Assistant** - 一个基于 AI 的桌面伴侣应用程序

这是 Baal 桌面宠物助手的独立版本，以黑猫恶魔“巴利”的形象出现，监控用户的计算机活动并通过自然语言对话提供帮助。该版本已经精简优化，移除了所有不必要的 ActivityWatch 开发组件，专注于桌面宠物功能。

## ✨ 核心特性

- **🤖 AI 驱动对话** - 通过 LangChain 集成 OpenAI 兼容的 LLM（包括火山引擎）
- **📊 ActivityWatch 集成** - 监控和分析用户活动数据，提供生产力洞察
- **😀 动态表情系统** - 7 种不同的面部表情，根据对话内容动态切换
- **🎭 多人格模式** - 3 种可切换的 AI 性格（严格主人/嘲讽管家/温柔伴侣）
- **📅 日程管理** - 内置日历系统，支持任务调度和提醒
- **💻 跨平台支持** - Windows/macOS 统一体验
- **🔒 单实例保护** - 防止多个应用同时运行

## 📁 项目结构

```
baal-standalone/
├── baal/                      # 核心模块
│   ├── desktop_pet/          # 桌面宠物主模块
│   │   ├── core/            # 核心功能（配置、LLM、表情、人格）
│   │   ├── ui/              # UI 组件（窗口、对话框、日历等）
│   │   └── supervision_mode.py # 生产力监督系统
│   ├── llm_assistant/       # LangChain 集成
│   ├── aw_stats/           # ActivityWatch 数据处理
│   └── scheduler/          # 日程管理
├── 动作表情拆分/            # 表情素材（7种表情+动画）
├── scripts/                # 构建和实用脚本
├── venv/                   # Python 虚拟环境
├── requirements.txt        # Python 依赖
├── run_desktop_pet.py      # 主启动脚本
├── build*.sh/ps1/bat       # 跨平台构建脚本
├── baal*.spec              # PyInstaller 配置
└── CLAUDE.md              # 详细项目文档

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
./venv/bin/pip install -r requirements.txt
```

### 2. 运行桌宠

```bash
# 推荐方式
./venv/bin/python run_desktop_pet.py

# 备选方式
./venv/bin/python -m baal.desktop_pet
./venv/bin/python baal/desktop_pet/main.py
```

### 3. 构建应用

#### macOS
```bash
./build.sh           # 基础构建
./build_macos.sh    # 增强构建（带图标和 DMG）
```

#### Windows
```bash
.\build_windows.ps1  # PowerShell 脚本
.\build_windows.bat  # 批处理脚本
```

#### 手动构建
```bash
./venv/bin/pyinstaller --clean --noconfirm baal.spec
```

## 📦 主要依赖

### UI 框架
- **PyQt6 6.5.3** - 桌面 UI 框架

### AI/LLM
- **LangChain 0.3.26** - LLM 集成和工具编排
- **langchain-openai** - OpenAI API 支持
- **volcengine-python-sdk** - 火山引擎 API

### ActivityWatch
- **aw-client** - ActivityWatch 客户端 API
- **aw-core** - 核心数据模型

### 其他
- **python-dateutil** - 日期处理
- **icalendar** - 日历格式支持
- **PyInstaller** - 应用打包

## ⚠️ 注意事项

1. **ActivityWatch 要求** - 运行前需要 ActivityWatch 服务已启动（端口 5600）
2. **API 密钥配置** - 首次运行需要配置 OpenAI 或火山引擎 API 密钥
3. **配置文件位置**:
   - macOS/Linux: `~/.baal_pet/config.json`
   - Windows: `%APPDATA%/BaalPet/config.json`
4. **虚拟环境** - ❗ 必须始终使用虚拟环境中的 Python

## 🎆 最新更新

### 2025-08-12
- 🧙 **新增**: 多人格系统 - 3种可切换的 AI 性格
- 🔒 **新增**: 单实例保护 - 防止重复启动
- 📊 **新增**: 监督模式 - 生产力监控和评估
- 🎯 **改进**: Windows 配置管理和权限处理
- 🔧 **新增**: 跨平台构建脚本支持

### 2025-08-10
- 🔅 **修复**: 日期解析准确性（“今天”、“明天”等）
- 📅 **修复**: 短时长日程显示问题

## 🎮 功能亮点

### 角色设定
- **名称**: 巴利（Baal）
- **形象**: 黑猫恶魔，权威的监督者
- **性格模式**:
  - 👑 严格主人 - 命令式、高标准
  - 🎭 嘲讽管家 - 毒舌、诽刺
  - 💕 温柔伴侣 - 鼓励、关怀

### 技术特色
- 🎨 **7 种动态表情** - 根据对话内容自动切换
- 📝 **流式响应** - 逐字符显示，打字效果
- ⚡ **并行工具调用** - 优化响应速度
- 🗼 **刘海屏适配** - macOS 自动避让
- 🔄 **实时切换** - 性格无需重启

## 📝 更多信息

详细的开发文档、API 参考和构建指南请查看 [CLAUDE.md](./CLAUDE.md)

## 📄 许可

本项目是 ActivityWatch 的修改版本，添加了 AI 桌面宠物功能。遵循原项目的开源许可。

---

*由 Claude Code 维护 - 最后更新: 2025-08-12*