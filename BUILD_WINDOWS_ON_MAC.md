# 在 Mac 上为 Windows 打包

由于 PyInstaller 不支持交叉编译，在 Mac 上无法直接构建 Windows 可执行文件。以下是几种可行的解决方案：

## 方案对比

| 方案 | 难度 | 成本 | 推荐度 | 说明 |
|------|------|------|--------|------|
| GitHub Actions | ⭐ | 免费 | ⭐⭐⭐⭐⭐ | 最推荐，自动化CI/CD |
| Docker | ⭐⭐ | 免费 | ⭐⭐⭐⭐ | 本地构建，需要Docker Desktop |
| 虚拟机 | ⭐⭐⭐ | 免费 | ⭐⭐⭐ | 需要Windows许可证和较多资源 |
| Wine | ⭐⭐⭐⭐ | 免费 | ⭐⭐ | 配置复杂，可能不稳定 |
| 云服务器 | ⭐ | 付费 | ⭐⭐⭐ | 简单但需要付费 |

## 方案一：GitHub Actions（推荐）

### 优点
- 完全免费
- 自动化构建
- 真实的Windows环境
- 可以同时构建多个平台版本

### 使用方法

1. 将代码推送到 GitHub 仓库
2. 添加 `.github/workflows/build-windows.yml` 文件（已创建）
3. 推送代码后自动触发构建
4. 从 Actions 页面下载构建好的 exe 文件

### 触发构建
```bash
# 推送到 GitHub
git add .
git commit -m "Build Windows executable"
git push

# 或手动触发（如果配置了 workflow_dispatch）
# 在 GitHub 网页上 Actions 标签页点击 "Run workflow"
```

## 方案二：Docker（本地构建）

### 安装 Docker Desktop
```bash
# 使用 Homebrew 安装
brew install --cask docker

# 或从官网下载
# https://www.docker.com/products/docker-desktop
```

### 构建步骤
```bash
# 构建 Docker 镜像
docker build -f Dockerfile.windows -t baal-windows-builder .

# 运行构建
docker run -v $(pwd)/dist-windows:/app/dist baal-windows-builder

# 构建完成后，exe 文件在 dist-windows 目录
```

## 方案三：使用虚拟机

### 1. 安装虚拟机软件

选择其一：
- **Parallels Desktop**（付费，性能最好）
- **VMware Fusion**（有免费版）
- **VirtualBox**（免费开源）
- **UTM**（免费，支持 Apple Silicon）

### 2. 安装 Windows

1. 下载 Windows 11 ISO：https://www.microsoft.com/software-download/windows11
2. 在虚拟机中安装 Windows
3. 安装 Python 3.9+

### 3. 传输文件并构建

```bash
# 在 Mac 上压缩项目
zip -r baal-project.zip . -x "*.git*" -x "*venv*" -x "*build*" -x "*dist*"

# 传输到虚拟机（通过共享文件夹或网络）
# 在 Windows 虚拟机中解压并运行
build_windows.bat
```

## 方案四：Wine（不推荐）

### 安装 Wine
```bash
# Intel Mac
brew install --cask wine-stable

# Apple Silicon Mac (需要 Rosetta 2)
softwareupdate --install-rosetta
brew install --cask wine-crossover
```

### 配置 Python
```bash
# 下载 Windows Python 安装程序
curl -O https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe

# 使用 Wine 安装
wine python-3.9.13-amd64.exe

# 安装依赖并构建
wine pip install -r requirements.txt
wine pyinstaller --clean --noconfirm baal_windows.spec
```

⚠️ **注意**：Wine 方案可能遇到兼容性问题，不保证成功

## 方案五：云服务器

### AWS EC2
1. 创建 Windows Server 实例（t2.micro 免费套餐）
2. 通过 RDP 连接
3. 安装 Python 并构建

### GitHub Codespaces
1. 创建 Windows 容器的 Codespace
2. 在云端构建

## 快速开始指南

### 最简单的方法（GitHub Actions）

1. **Fork 或创建 GitHub 仓库**
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/baal-standalone.git
git push -u origin main
```

2. **创建 Personal Access Token**（如果是私有仓库）
   - 访问 GitHub Settings → Developer settings → Personal access tokens
   - 生成新 token，勾选 `repo` 权限

3. **触发构建**
   - 推送代码自动触发
   - 或在 Actions 页面手动触发

4. **下载构建结果**
   - 进入 Actions 页面
   - 点击最新的 workflow run
   - 在 Artifacts 部分下载 `Baal-Windows-Build`

## 故障排除

### 问题：Docker 构建失败
- 确保 Docker Desktop 正在运行
- 检查磁盘空间（需要至少 5GB）
- 尝试清理 Docker 缓存：`docker system prune`

### 问题：GitHub Actions 构建失败
- 检查 requirements.txt 中的依赖版本
- 查看 Actions 日志中的错误信息
- 确保所有文件路径使用正斜杠 `/`

### 问题：虚拟机性能差
- 分配更多 RAM（至少 4GB）
- 启用虚拟化加速
- 使用 Parallels Desktop（性能最好）

## 推荐工作流程

1. **开发阶段**：在 Mac 上正常开发和测试
2. **构建阶段**：推送到 GitHub，使用 Actions 自动构建
3. **测试阶段**：下载构建的 exe，在虚拟机或实体 Windows 机器上测试
4. **发布阶段**：使用 GitHub Releases 自动发布

## 有用的工具

- **Parallels Desktop** - 最好的 Mac 虚拟机软件
- **Microsoft Remote Desktop** - 连接 Windows 云服务器
- **GitHub Desktop** - 简化 Git 操作
- **act** - 本地测试 GitHub Actions：`brew install act`

---

*提示：对于持续开发，强烈推荐使用 GitHub Actions，它免费、可靠且易于设置。*