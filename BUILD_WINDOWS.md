# Windows 打包指南

## 前置要求

1. **Python 3.9+** - 从 [python.org](https://www.python.org/downloads/) 下载安装
2. **Git** (可选) - 用于版本控制
3. **Windows 10/11** - 推荐使用最新版本

## 快速开始

### 方法一：使用批处理脚本（推荐给初学者）

1. 双击运行 `build_windows.bat`
2. 等待脚本自动完成所有步骤
3. 在 `dist` 文件夹中找到 `Baal宠物助手.exe`

### 方法二：使用PowerShell脚本（推荐）

1. 右键点击 `build_windows.ps1`，选择"使用PowerShell运行"
2. 如果提示权限问题，先运行：
   ```powershell
   Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
   ```
3. 脚本会自动：
   - 创建虚拟环境
   - 安装依赖
   - 转换图标格式
   - 打包应用程序

### 方法三：手动构建

```bash
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
venv\Scripts\activate.bat  # CMD
# 或
.\venv\Scripts\Activate.ps1  # PowerShell

# 3. 安装依赖
pip install -r requirements.txt
pip install pyinstaller==6.11.1

# 4. 转换图标（可选）
python convert_icon.py

# 5. 打包
pyinstaller --clean --noconfirm baal_windows.spec
```

## 输出文件

成功构建后，会在以下位置生成文件：

- `dist/Baal宠物助手.exe` - 独立可执行文件
- `dist/` - 包含所有运行时依赖

## 分发选项

### 1. 单文件分发
直接分发 `dist/Baal宠物助手.exe`（约50-100MB）

### 2. 文件夹分发
压缩整个 `dist` 文件夹为 ZIP 文件

### 3. 创建安装程序（高级）

使用 **Inno Setup** 创建专业的安装程序：

1. 下载 [Inno Setup](https://jrsoftware.org/isdl.php)
2. 使用提供的 `installer_setup.iss` 脚本（如果存在）
3. 或使用向导创建新的安装脚本

## 故障排除

### 问题：防病毒软件报警
- **解决**：将 PyInstaller 和输出文件夹添加到防病毒软件白名单

### 问题：缺少 DLL 文件
- **解决**：安装 [Visual C++ Redistributables](https://support.microsoft.com/en-us/help/2977003/)

### 问题：程序启动后立即关闭
- **解决**：
  1. 从命令行运行查看错误信息
  2. 检查 `~/.baal_pet/logs/` 中的日志文件
  3. 确保已配置 API 密钥

### 问题：图标不显示
- **解决**：运行 `python convert_icon.py` 生成 ICO 文件

### 问题：中文显示乱码
- **解决**：确保系统区域设置支持中文

## 系统要求

### 最低要求
- Windows 10 版本 1903 或更高
- 4GB RAM
- 200MB 可用磁盘空间
- 互联网连接（用于 AI 功能）

### 推荐配置
- Windows 11
- 8GB+ RAM
- SSD 存储
- 稳定的互联网连接

## 开发者说明

### 自定义打包配置

编辑 `baal_windows.spec` 文件来修改：
- 应用名称
- 图标
- 版本信息
- 包含/排除的模块

### 添加版本信息

创建 `version_info.txt` 文件并在 spec 中引用：
```python
exe = EXE(
    ...
    version_file='version_info.txt',
    ...
)
```

### 代码签名

为避免 Windows Defender 警告，考虑购买代码签名证书：
1. 获取证书（如 DigiCert、Sectigo）
2. 使用 signtool.exe 签名：
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com dist\Baal宠物助手.exe
   ```

## 联系支持

如遇到问题，请：
1. 检查本文档的故障排除部分
2. 查看项目 Issues 页面
3. 提交新的 Issue 并附上错误日志

---

*最后更新: 2025-08-11*