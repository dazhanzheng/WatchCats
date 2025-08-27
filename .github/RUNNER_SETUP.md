# GitHub Actions Self-Hosted Runner 快速设置

## Windows (DNF-DELLWORKSTA) Runner 设置

### 1. 下载 Runner

1. 进入 GitHub 仓库页面
2. 点击 **Settings** → **Actions** → **Runners**
3. 点击 **New self-hosted runner**
4. 选择 **Windows**

### 2. 安装步骤

在 PowerShell (管理员模式) 中执行：

```powershell
# 1. 创建 runner 目录
mkdir C:\actions-runner
cd C:\actions-runner

# 2. 下载 runner (从 GitHub 页面复制最新的下载链接)
# 示例：
Invoke-WebRequest -Uri https://github.com/actions/runner/releases/download/v2.311.0/actions-runner-win-x64-2.311.0.zip -OutFile actions-runner-win-x64-2.311.0.zip

# 3. 解压
Add-Type -AssemblyName System.IO.Compression.FileSystem
[System.IO.Compression.ZipFile]::ExtractToDirectory("$PWD\actions-runner-win-x64-2.311.0.zip", "$PWD")

# 4. 配置 runner (从 GitHub 页面复制配置命令)
# 注意：使用简单的标签配置
.\config.cmd --url https://github.com/dazhanzheng/WatchCats --token YOUR_TOKEN_HERE
```

### 3. 配置时的重要选项

当运行 `config.cmd` 时，会有以下提示：

```
Enter the name of the runner group to add this runner to: [press Enter for Default]
> 直接按 Enter 使用默认

Enter the name of runner: [press Enter for DNF-DELLWORKSTA]
> 可以保持默认或输入自定义名称

This runner will have the following labels: 'self-hosted', 'Windows', 'X64'
Enter any additional labels (ex. label-1,label-2): [press Enter to skip]
> 可以直接按 Enter，或添加 DNF-DELLWORKSTA

Enter name of work folder: [press Enter for _work]
> 直接按 Enter 使用默认
```

### 4. 安装为 Windows 服务

```powershell
# 以管理员身份运行
.\svc.sh install
.\svc.sh start

# 检查服务状态
.\svc.sh status
```

### 5. 验证 Runner

1. 回到 GitHub 仓库的 **Settings** → **Actions** → **Runners**
2. 应该能看到你的 runner 显示为绿色（在线）
3. 查看 runner 的标签（Labels）

### 6. 故障排除

#### Runner 显示离线

```powershell
# 检查服务
.\svc.sh status

# 重启服务
.\svc.sh stop
.\svc.sh start

# 查看日志
Get-Content _diag\*.log -Tail 50
```

#### 手动运行（调试模式）

```powershell
# 停止服务
.\svc.sh stop

# 手动运行
.\run.cmd

# 这样可以在控制台看到实时输出
```

#### 重新配置

```powershell
# 移除现有配置
.\config.cmd remove --token YOUR_TOKEN_HERE

# 重新配置
.\config.cmd --url https://github.com/dazhanzheng/WatchCats --token YOUR_TOKEN_HERE
```

### 7. 验证 Python 环境

```powershell
# 检查 Python
python --version

# 如果 Python 不在 PATH 中，添加到系统环境变量
# 或在 runner 的工作目录创建一个 .path 文件
echo C:\Python39 > .path
```

## 测试 Runner

推送测试工作流后：

1. 进入 **Actions** 标签页
2. 选择 **Test Self-Hosted Runner** 工作流
3. 点击 **Run workflow**
4. 查看运行结果

## 常见问题

### Q: 工作流找不到 runner
**A:** 检查 `runs-on` 标签是否正确。最简单的配置是只用 `runs-on: self-hosted`

### Q: Python 命令找不到
**A:** 确保 Python 在 PATH 中，或在 runner 目录创建 .path 文件

### Q: 权限错误
**A:** 确保 runner 服务账户有足够权限访问工作目录

### Q: 构建失败，提示文件被占用
**A:** 添加清理步骤，确保每次构建前删除旧文件

## 联系支持

如有问题，请在 GitHub Issues 中报告，或查看 [GitHub Actions 文档](https://docs.github.com/en/actions/hosting-your-own-runners)