# Baal 桌面宠物助手 - 精简版

这是 Baal 桌面宠物助手的精简独立版本，移除了所有不必要的 ActivityWatch 开发组件，只保留运行所需的最小依赖。

## 项目结构

```
baal-standalone/
├── baal/               # Baal 核心模块
├── scripts/            # 构建脚本
├── requirements.txt    # Python 依赖
├── build.sh           # 构建脚本
├── baal.spec          # PyInstaller 配置
└── run_desktop_pet.py # 启动脚本
```

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行桌宠

```bash
python run_desktop_pet.py
```

### 3. 构建应用

```bash
# macOS
./build.sh

# 或手动构建
pyinstaller --clean --noconfirm baal.spec
```

## 依赖说明

本项目只依赖：
- **PyQt6**: UI框架
- **LangChain**: LLM集成
- **aw-client**: ActivityWatch客户端API（通过pip安装）
- **aw-core**: ActivityWatch核心库，提供数据转换功能（通过pip安装）

## 注意事项

1. 运行前需要 ActivityWatch 服务已启动
2. 首次运行需要配置 API 密钥
3. 配置文件保存在 `~/.baal_pet/config.json`

## 与原版差异

- 移除了所有 ActivityWatch 服务器和监视器组件
- 移除了不必要的构建工具和测试文件
- 精简了依赖，专注于桌宠功能
- 构建产物更小，启动更快