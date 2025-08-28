# Setup Git Proxy for Self-Hosted Runner
# 为自托管 Runner 配置代理

Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Configuring Proxy for GitHub Actions Runner" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

$proxyUrl = "http://127.0.0.1:7890"
$proxyUrlHttps = "http://127.0.0.1:7890"

Write-Host "Setting up proxy: $proxyUrl" -ForegroundColor Yellow

# 1. 配置 Git 全局代理
Write-Host "Configuring Git proxy..." -ForegroundColor Yellow
git config --global http.proxy $proxyUrl
git config --global https.proxy $proxyUrlHttps

# 显示当前配置
Write-Host "Current Git proxy configuration:" -ForegroundColor Green
git config --global --get http.proxy
git config --global --get https.proxy

# 2. 设置系统环境变量（需要管理员权限）
Write-Host ""
Write-Host "Setting system environment variables..." -ForegroundColor Yellow

try {
    # 设置用户级环境变量
    [System.Environment]::SetEnvironmentVariable("HTTP_PROXY", $proxyUrl, "User")
    [System.Environment]::SetEnvironmentVariable("HTTPS_PROXY", $proxyUrlHttps, "User")
    [System.Environment]::SetEnvironmentVariable("http_proxy", $proxyUrl, "User")
    [System.Environment]::SetEnvironmentVariable("https_proxy", $proxyUrlHttps, "User")
    
    # 排除本地地址
    [System.Environment]::SetEnvironmentVariable("NO_PROXY", "localhost,127.0.0.1,*.local", "User")
    [System.Environment]::SetEnvironmentVariable("no_proxy", "localhost,127.0.0.1,*.local", "User")
    
    Write-Host "✓ User environment variables set" -ForegroundColor Green
} catch {
    Write-Host "Warning: Could not set environment variables: $_" -ForegroundColor Yellow
}

# 3. 测试连接
Write-Host ""
Write-Host "Testing connections..." -ForegroundColor Yellow

# 测试 GitHub 连接
Write-Host "Testing GitHub access..." -ForegroundColor Gray
try {
    $response = Invoke-WebRequest -Uri "https://api.github.com" -UseBasicParsing -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "✓ GitHub API accessible" -ForegroundColor Green
    }
} catch {
    Write-Host "✗ GitHub API not accessible: $_" -ForegroundColor Red
}

# 测试 Git 仓库访问
Write-Host "Testing Git repository access..." -ForegroundColor Gray
$testResult = git ls-remote https://github.com/dazhanzheng/WatchCats.git HEAD 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Git repository accessible" -ForegroundColor Green
} else {
    Write-Host "✗ Git repository not accessible" -ForegroundColor Red
    Write-Host "Error: $testResult" -ForegroundColor Red
}

# 4. 为 Actions Runner 服务配置代理
Write-Host ""
Write-Host "Configuring Actions Runner..." -ForegroundColor Yellow

# 查找 runner 配置文件
$runnerPaths = @(
    "D:\actions-runner",
    "C:\actions-runner",
    "$env:USERPROFILE\actions-runner"
)

$runnerPath = $runnerPaths | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($runnerPath) {
    Write-Host "Found runner at: $runnerPath" -ForegroundColor Green
    
    # 创建或更新 .env 文件
    $envFile = Join-Path $runnerPath ".env"
    $envContent = @"
http_proxy=$proxyUrl
https_proxy=$proxyUrlHttps
HTTP_PROXY=$proxyUrl
HTTPS_PROXY=$proxyUrlHttps
NO_PROXY=localhost,127.0.0.1,*.local
no_proxy=localhost,127.0.0.1,*.local
"@
    
    $envContent | Set-Content -Path $envFile -Encoding UTF8
    Write-Host "✓ Created/updated runner .env file" -ForegroundColor Green
    
    # 提示重启服务
    Write-Host ""
    Write-Host "IMPORTANT: Please restart the Actions Runner service:" -ForegroundColor Yellow
    Write-Host "  1. Stop the runner (Ctrl+C if running interactively)" -ForegroundColor Gray
    Write-Host "  2. Start it again with: .\run.cmd" -ForegroundColor Gray
    
    # 如果作为服务运行
    $serviceName = Get-Service -Name "actions.runner.*" -ErrorAction SilentlyContinue
    if ($serviceName) {
        Write-Host ""
        Write-Host "Or restart the service:" -ForegroundColor Yellow
        Write-Host "  Restart-Service '$($serviceName.Name)'" -ForegroundColor Gray
    }
} else {
    Write-Host "Warning: Could not find Actions Runner installation" -ForegroundColor Yellow
    Write-Host "Expected locations:" -ForegroundColor Gray
    $runnerPaths | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }
}

Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host " Proxy Configuration Complete" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor Green
Write-Host "  • Git proxy configured: $proxyUrl" -ForegroundColor Gray
Write-Host "  • Environment variables set" -ForegroundColor Gray
Write-Host "  • Runner configuration updated (if found)" -ForegroundColor Gray
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Ensure your proxy (localhost:7890) is running" -ForegroundColor Gray
Write-Host "  2. Restart the Actions Runner" -ForegroundColor Gray
Write-Host "  3. Trigger a new workflow run" -ForegroundColor Gray