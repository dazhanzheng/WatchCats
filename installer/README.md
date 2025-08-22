# Baal 宠物助手 Windows 安装包

## 概述
这是一个专业的 Windows 安装向导，使用 Inno Setup 制作，可以自动处理依赖项并解决常见的软件闪退问题。

## 安装包特性

### 自动依赖管理
- ✅ 自动检测并安装 Visual C++ 2015-2022 运行库
- ✅ 正确配置 Qt 插件路径
- ✅ 设置必要的环境变量
- ✅ 创建 qt.conf 配置文件

### 用户友好界面
- 📖 中英文双语支持
- 🎨 专业的安装向导界面
- 📝 详细的安装进度显示
- ⚙️ 自定义安装选项

### 完整功能
- 🚀 创建桌面快捷方式
- 📁 创建开始菜单项
- 🔄 支持开机自启动
- 🗑️ 完整的卸载支持
- 💾 保留用户数据选项

## 构建指南

### 前置要求
1. **Inno Setup 6**
   - 下载地址：https://jrsoftware.org/isdl.php
   - 安装到默认位置

2. **已构建的主程序**
   - 运行 `build_windows.bat` 构建主程序
   - 确保 `dist\WatchCats.exe` 存在

3. **Visual C++ Redistributable 文件**
   - 运行 `installer\download_vcredist.bat` 自动下载
   - 或手动从微软官网下载

### 快速构建

#### 方法一：一键构建（推荐）
```batch
# 在项目根目录运行
build_full_installer.bat
```
这会自动执行所有步骤：构建程序、下载依赖、生成安装包。

#### 方法二：分步构建
```batch
# 1. 构建主程序
build_windows.bat

# 2. 进入 installer 目录
cd installer

# 3. 下载运行库
download_vcredist.bat

# 4. 准备图片资源（可选）
prepare_images.bat

# 5. 编译安装包
build_installer.bat
```

### 输出文件
安装包将生成在：`installer\Output\BaalPetAssistantSetup.exe`

## 文件结构

```
installer/
├── baal_installer.iss      # Inno Setup 主脚本
├── download_vcredist.bat   # 下载 VC++ 运行库
├── build_installer.bat     # 编译安装包
├── prepare_images.bat      # 生成安装向导图片
├── config_template.json    # 配置文件模板
├── vcredist/               # VC++ 运行库存放目录
│   ├── vc_redist.x64.exe
│   └── vc_redist.x86.exe
└── Output/                 # 输出目录
    └── BaalPetAssistantSetup.exe
```

## 自定义配置

### 修改应用信息
编辑 `baal_installer.iss` 文件开头的定义：
```pascal
#define MyAppName "Baal宠物助手"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Baal Project"
```

### 添加额外文件
在 `[Files]` 部分添加：
```pascal
Source: "额外文件.txt"; DestDir: "{app}"; Flags: ignoreversion
```

### 修改安装选项
在 `[Tasks]` 部分自定义：
```pascal
Name: "customtask"; Description: "自定义任务描述"
```

## 解决的问题

### 1. Qt 平台插件缺失
- 自动复制所有必要的 Qt 插件
- 创建 qt.conf 配置文件
- 设置 QT_PLUGIN_PATH 环境变量

### 2. Visual C++ 运行库缺失
- 检测系统是否已安装
- 自动静默安装所需版本
- 同时支持 x64 和 x86

### 3. 权限问题
- 默认安装到用户程序目录
- 不需要管理员权限（可选）
- 正确处理 UAC 提示

### 4. 配置文件
- 自动创建配置目录
- 生成默认配置文件
- 保留用户设置

## 测试建议

### 安装测试
1. 在干净的 Windows 10/11 系统测试
2. 测试没有 VC++ 运行库的情况
3. 测试已有旧版本的升级
4. 测试不同语言设置

### 功能测试
- ✅ 程序能正常启动
- ✅ 所有 UI 元素正常显示
- ✅ API 连接正常
- ✅ 快捷方式正常工作
- ✅ 卸载完全干净

## 故障排除

### 问题：Inno Setup 未找到
**解决**：从官网下载并安装 Inno Setup 6

### 问题：构建失败 - 文件未找到
**解决**：确保先运行 `build_windows.bat` 构建主程序

### 问题：VC++ 运行库下载失败
**解决**：
1. 检查网络连接
2. 手动从微软官网下载
3. 放置到 `installer\vcredist\` 目录

### 问题：安装后程序仍然闪退
**解决**：
1. 检查日志文件：`%APPDATA%\BaalPetAssistant\logs`
2. 尝试以管理员身份运行
3. 检查防病毒软件是否阻止

## 分发说明

### 文件大小
- 基础安装包：约 100-150 MB
- 包含运行库：约 170-200 MB

### 分发渠道
1. **直接下载**：提供 exe 文件
2. **压缩包**：打包为 zip 减小体积
3. **网络安装器**：创建在线下载版本

### 版本管理
- 使用语义化版本号（如 1.0.0）
- 在 Inno Setup 脚本中更新版本
- 保持向后兼容性

## 许可证
本安装包脚本遵循项目主许可证。Visual C++ Redistributable 由微软提供，遵循其各自的许可条款。

---

*最后更新：2025-01-22*