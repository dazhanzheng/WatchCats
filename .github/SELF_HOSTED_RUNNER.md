# 自托管 Runner 配置指南

## 概述

本项目使用自托管的 GitHub Actions Runner 进行构建，主要在 `DNF-DELLWORKSTA` (Windows) 机器上运行。

## Runner 设置

### Windows Runner (DNF-DELLWORKSTA)

#### 前置要求

1. **Python 3.9+**
   ```powershell
   # 检查 Python 版本
   python --version
   ```

2. **Git**
   ```powershell
   git --version
   ```

3. **PyInstaller 依赖**
   - Visual C++ Redistributable
   - Windows SDK (可选，用于代码签名)

4. **Inno Setup 6** (可选，用于创建安装程序)
   - 下载: https://jrsoftware.org/isdl.php
   - 安装到默认路径: `C:\Program Files (x86)\Inno Setup 6\`

#### 安装 GitHub Actions Runner

1. 进入仓库设置 > Actions > Runners
2. 点击 "New self-hosted runner"
3. 选择 Windows 操作系统
4. 按照指示下载并配置 runner

```powershell
# 创建 runner 目录
mkdir C:\actions-runner
cd C:\actions-runner

# 下载 runner
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.xxx.x/actions-runner-win-x64-2.xxx.x.zip -OutFile actions-runner.zip

# 解压
Expand-Archive -Path actions-runner.zip -DestinationPath .

# 配置 runner
.\config.cmd --url https://github.com/YOUR_USERNAME/baal-standalone --token YOUR_TOKEN --name DNF-DELLWORKSTA --labels DNF-DELLWORKSTA,windows,self-hosted

# 安装为 Windows 服务（推荐）
.\svc.sh install
.\svc.sh start
```

#### Runner 标签

确保 runner 有以下标签：
- `self-hosted`
- `windows`
- `DNF-DELLWORKSTA`

### macOS Runner (可选)

如果你也有 macOS 自托管 runner：

```bash
# 创建 runner 目录
mkdir ~/actions-runner
cd ~/actions-runner

# 下载并解压 runner
curl -o actions-runner-osx-x64-2.xxx.x.tar.gz -L https://github.com/actions/runner/releases/download/v2.xxx.x/actions-runner-osx-x64-2.xxx.x.tar.gz
tar xzf ./actions-runner-osx-x64-2.xxx.x.tar.gz

# 配置
./config.sh --url https://github.com/YOUR_USERNAME/baal-standalone --token YOUR_TOKEN --name YOUR-MAC-NAME --labels macos,self-hosted

# 运行
./run.sh
# 或安装为服务
./svc.sh install
./svc.sh start
```

## 工作流使用

### 自动构建

推送到 `main` 或 `develop` 分支时自动触发构建：

```bash
git push origin main
```

### 手动触发构建

1. 进入 GitHub Actions 页面
2. 选择 "Build on Self-Hosted Runner" 工作流
3. 点击 "Run workflow"
4. 选择构建类型：
   - `windows` - 仅构建 Windows
   - `macos` - 仅构建 macOS
   - `both` - 构建两个平台

### 创建发布版本

创建标签时自动构建并创建 Release：

```bash
git tag v1.0.0
git push origin v1.0.0
```

## 维护

### 清理工作空间

Runner 会自动清理构建文件，但如果需要手动清理：

```powershell
# Windows
cd C:\actions-runner\_work\baal-standalone
Remove-Item -Recurse -Force * -ErrorAction SilentlyContinue
```

```bash
# macOS/Linux
cd ~/actions-runner/_work/baal-standalone
rm -rf *
```

### 更新 Runner

```powershell
# Windows
cd C:\actions-runner
.\svc.sh stop
# 下载新版本并解压
.\config.cmd remove
.\config.cmd # 重新配置
.\svc.sh install
.\svc.sh start
```

### 查看 Runner 日志

```powershell
# Windows 服务日志
Get-EventLog -LogName Application -Source ActionsRunner

# 或查看 runner 目录下的日志
cd C:\actions-runner\_diag
Get-Content *.log -Tail 100
```

## 故障排除

### Runner 离线

1. 检查网络连接
2. 重启 runner 服务：
   ```powershell
   cd C:\actions-runner
   .\svc.sh stop
   .\svc.sh start
   ```

### 构建失败

1. 检查 Python 版本
2. 清理 PyInstaller 缓存：
   ```powershell
   Remove-Item -Recurse -Force $env:APPDATA\pyinstaller
   ```
3. 重新安装依赖：
   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt --force-reinstall
   ```

### 权限问题

确保 runner 服务账户有足够权限：
- 读写工作目录
- 执行 Python 和相关工具
- 访问网络（下载依赖）

## 安全建议

1. **使用专用机器或虚拟机**
   - 不要在生产服务器上运行 runner
   - 考虑使用隔离的环境

2. **限制 Runner 权限**
   - 使用最小权限原则
   - 不要使用管理员账户运行 runner

3. **定期更新**
   - 保持 runner 版本最新
   - 更新系统和依赖

4. **监控**
   - 定期检查 runner 日志
   - 监控资源使用情况

## 联系方式

如有问题，请联系项目维护者或在 GitHub Issues 中报告。