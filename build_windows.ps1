# Baal宠物助手 Windows 构建脚本 (PowerShell版本)

Write-Host "====================================" -ForegroundColor Cyan
Write-Host "Baal宠物助手 Windows 构建脚本" -ForegroundColor Cyan
Write-Host "====================================" -ForegroundColor Cyan
Write-Host ""

# 运行依赖检查（可选）
if (Test-Path ".\check_windows_deps.ps1") {
    $response = Read-Host "是否运行系统依赖检查? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host ""
        Write-Host "运行依赖检查..." -ForegroundColor Yellow
        & .\check_windows_deps.ps1
        Write-Host ""
        $continue = Read-Host "是否继续构建? (Y/N)"
        if ($continue -ne 'Y' -and $continue -ne 'y') {
            Write-Host "构建已取消" -ForegroundColor Yellow
            exit 0
        }
    }
}
Write-Host ""

# 检查Python是否安装
try {
    $pythonVersion = python --version 2>&1
    Write-Host "找到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "错误: 未找到Python，请先安装Python 3.9或更高版本" -ForegroundColor Red
    Write-Host "下载地址: https://www.python.org/downloads/" -ForegroundColor Yellow
    Read-Host "按Enter键退出"
    exit 1
}

# 创建虚拟环境（如果不存在）
if (!(Test-Path "venv")) {
    Write-Host "创建虚拟环境..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "创建虚拟环境失败" -ForegroundColor Red
        Read-Host "按Enter键退出"
        exit 1
    }
}

# 激活虚拟环境
Write-Host "激活虚拟环境..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# 升级pip
Write-Host "升级pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# 安装依赖
Write-Host "安装依赖..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "安装依赖失败" -ForegroundColor Red
    Read-Host "按Enter键退出"
    exit 1
}

# 安装PyInstaller
Write-Host "安装PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller==6.11.1

# 检查并转换图标
$icoPath = "baal\resources\cat.ico"
$pngPath = "baal\resources\cat.png"

if (!(Test-Path $icoPath)) {
    if (Test-Path $pngPath) {
        Write-Host "尝试使用Pillow转换PNG到ICO..." -ForegroundColor Yellow
        
        # 创建转换脚本
        $convertScript = @"
from PIL import Image
import os

# 打开PNG图片
img = Image.open('$pngPath')

# 确保是RGBA模式
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# 创建多种尺寸的图标
sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
imgs = []

for size in sizes:
    resized = img.resize(size, Image.Resampling.LANCZOS)
    imgs.append(resized)

# 保存为ICO
imgs[0].save('$icoPath', format='ICO', sizes=sizes)
print('图标转换成功！')
"@
        
        # 安装Pillow（如果需要）
        pip install Pillow
        
        # 执行转换
        $convertScript | python
        
        if (Test-Path $icoPath) {
            Write-Host "图标转换成功！" -ForegroundColor Green
        } else {
            Write-Host "警告: 图标转换失败，将使用默认图标" -ForegroundColor Yellow
        }
    } else {
        Write-Host "警告: 未找到图标文件，将使用默认图标" -ForegroundColor Yellow
    }
}

# 清理旧的构建文件
Write-Host "清理旧的构建文件..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
}
if (Test-Path "dist") {
    Remove-Item -Path "dist" -Recurse -Force
}

# 使用PyInstaller打包
Write-Host "开始打包..." -ForegroundColor Yellow
Write-Host "这可能需要几分钟时间，请耐心等待..." -ForegroundColor Cyan

pyinstaller --clean --noconfirm baal_windows.spec

# 检查构建结果
$exePath = "dist\Baal宠物助手.exe"
if (Test-Path $exePath) {
    $fileInfo = Get-Item $exePath
    $sizeInMB = [math]::Round($fileInfo.Length / 1MB, 2)
    
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "构建成功！" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "可执行文件: $exePath" -ForegroundColor Cyan
    Write-Host "文件大小: $sizeInMB MB" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "您可以：" -ForegroundColor Yellow
    Write-Host "1. 直接运行 dist\Baal宠物助手.exe" -ForegroundColor White
    Write-Host "2. 将 dist 文件夹复制到其他电脑使用" -ForegroundColor White
    Write-Host "3. 使用 NSIS 或 Inno Setup 创建安装程序" -ForegroundColor White
    Write-Host ""
    Write-Host "注意：如果程序无法启动，请运行 check_windows_deps.bat 检查依赖" -ForegroundColor Yellow
    Write-Host ""
    
    $runNow = Read-Host "是否立即运行程序？(Y/N)"
    if ($runNow -eq 'Y' -or $runNow -eq 'y') {
        Start-Process $exePath
    }
} else {
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "构建失败！" -ForegroundColor Red
    Write-Host "====================================" -ForegroundColor Red
    Write-Host "请检查错误信息并重试" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "常见问题解决方案：" -ForegroundColor Yellow
    Write-Host "1. 确保所有Python依赖已正确安装" -ForegroundColor White
    Write-Host "2. 检查防病毒软件是否阻止了PyInstaller" -ForegroundColor White
    Write-Host "3. 尝试以管理员权限运行此脚本" -ForegroundColor White
}

Read-Host "按Enter键退出"