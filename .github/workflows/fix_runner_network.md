# 修复 Self-Hosted Runner 网络问题

## 1. 配置 Git 代理（如果您使用代理）

在 runner 机器上运行：

```powershell
# 设置 HTTP 代理
git config --global http.proxy http://your-proxy-server:port
git config --global https.proxy http://your-proxy-server:port

# 如果需要认证
git config --global http.proxy http://username:password@proxy-server:port
```

## 2. 测试网络连接

在 runner 机器上测试：

```powershell
# 测试 DNS
nslookup github.com

# 测试 HTTPS 连接
curl https://github.com

# 测试 Git 连接
git ls-remote https://github.com/dazhanzheng/WatchCats.git
```

## 3. 使用 SSH 替代 HTTPS（如果 HTTPS 被阻止）

```powershell
# 生成 SSH 密钥（如果没有）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"

# 将公钥添加到 GitHub 账户
# 访问 https://github.com/settings/keys

# 配置 Git 使用 SSH
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

## 4. 临时解决方案 - 使用本地代码

修改工作流跳过 checkout：

```yaml
    steps:
    - name: Use local repository
      shell: powershell
      run: |
        # 使用本地已有的代码
        if (Test-Path "D:\WatchCats") {
          Copy-Item -Path "D:\WatchCats\*" -Destination . -Recurse -Force
          Write-Host "Using local repository copy"
        } else {
          Write-Error "Local repository not found"
          exit 1
        }
```

## 5. 配置 Runner 环境变量

在 runner 机器上设置环境变量：

```powershell
# 设置代理环境变量
[System.Environment]::SetEnvironmentVariable("HTTP_PROXY", "http://proxy:port", "Machine")
[System.Environment]::SetEnvironmentVariable("HTTPS_PROXY", "http://proxy:port", "Machine")
[System.Environment]::SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1", "Machine")

# 重启 runner 服务
Restart-Service actions.runner.*
```

## 6. 检查防火墙规则

确保允许以下连接：
- github.com:443 (HTTPS)
- github.com:22 (SSH)
- api.github.com:443
- *.githubusercontent.com:443

## 7. 使用镜像（如果在中国）

```powershell
# 使用 GitHub 镜像
git config --global url."https://github.com.cnpmjs.org/".insteadOf "https://github.com/"
# 或
git config --global url."https://hub.fastgit.xyz/".insteadOf "https://github.com/"
```