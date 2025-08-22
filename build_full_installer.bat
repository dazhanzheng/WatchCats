@echo off
REM 完整的 Windows 安装包构建流程
REM Complete Windows Installer Build Process

echo ==========================================
echo Baal 宠物助手 - 完整安装包构建
echo Baal Pet Assistant - Full Installer Build
echo ==========================================
echo.
echo 此脚本将执行以下步骤：
echo This script will perform the following steps:
echo   1. 构建主程序 (Build main program)
echo   2. 准备安装向导资源 (Prepare installer resources)  
echo   3. 下载运行库 (Download redistributables)
echo   4. 编译安装包 (Compile installer)
echo.
pause

REM Step 1: 构建主程序
echo.
echo [步骤 1/4] 构建主程序...
echo [Step 1/4] Building main program...
echo ==========================================

if exist build_windows.bat (
    call build_windows.bat
    if %errorlevel% neq 0 (
        echo 主程序构建失败！
        echo Main program build failed!
        pause
        exit /b 1
    )
) else if exist build_windows.ps1 (
    powershell -ExecutionPolicy Bypass -File build_windows.ps1
    if %errorlevel% neq 0 (
        echo 主程序构建失败！
        echo Main program build failed!
        pause
        exit /b 1
    )
) else (
    echo 警告：未找到构建脚本，跳过主程序构建。
    echo Warning: Build script not found, skipping main program build.
)

REM Step 2: 准备安装向导资源
echo.
echo [步骤 2/4] 准备安装向导资源...
echo [Step 2/4] Preparing installer resources...
echo ==========================================

cd installer
if exist prepare_images.bat (
    call prepare_images.bat
)

REM Step 3: 下载运行库
echo.
echo [步骤 3/4] 检查和下载运行库...
echo [Step 3/4] Checking and downloading redistributables...
echo ==========================================

if not exist vcredist\vc_redist.x64.exe (
    call download_vcredist.bat
    if %errorlevel% neq 0 (
        echo 运行库下载失败！
        echo Redistributable download failed!
        pause
        exit /b 1
    )
) else (
    echo 运行库文件已存在，跳过下载。
    echo Redistributable files already exist, skipping download.
)

REM Step 4: 编译安装包
echo.
echo [步骤 4/4] 编译安装包...
echo [Step 4/4] Compiling installer...
echo ==========================================

call build_installer.bat
if %errorlevel% neq 0 (
    cd ..
    echo 安装包编译失败！
    echo Installer compilation failed!
    pause
    exit /b 1
)

cd ..

REM 完成
echo.
echo ==========================================
echo 构建完成！Build Complete!
echo ==========================================
echo.
echo 安装包位置 Installer location:
echo   installer\Output\WatchCats-Setup.exe
echo.
echo 安装包特性 Installer features:
echo   ✓ 自动安装 Visual C++ 运行库
echo   ✓ 检测并处理已安装版本
echo   ✓ 创建开始菜单和桌面快捷方式
echo   ✓ 支持开机自启动选项
echo   ✓ 中英文双语界面
echo   ✓ 完整的卸载支持
echo.
echo 下一步 Next steps:
echo   1. 测试安装包 (Test the installer)
echo   2. 分发给用户 (Distribute to users)
echo.

pause