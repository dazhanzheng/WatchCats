@echo off
REM Test installer build script - 测试安装程序构建脚本
REM This script tests the Inno Setup compilation locally
REM 此脚本用于本地测试 Inno Setup 编译

echo ======================================
echo Testing Inno Setup Installer Build
echo 测试安装程序构建
echo ======================================
echo.

REM Check if Inno Setup is installed
REM 检查 Inno Setup 是否已安装
set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC_PATH% (
    echo Error: Inno Setup not found at %ISCC_PATH%
    echo 错误：在 %ISCC_PATH% 未找到 Inno Setup
    echo Please install Inno Setup 6 from https://jrsoftware.org/isdl.php
    echo 请从 https://jrsoftware.org/isdl.php 安装 Inno Setup 6
    pause
    exit /b 1
)

REM Navigate to installer directory
REM 导航到安装程序目录
cd /d "%~dp0"

echo Building installer...
echo 正在构建安装程序...
echo.

REM Compile the installer
REM 编译安装程序
%ISCC_PATH% baal_installer.iss

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ======================================
    echo Build successful! 构建成功！
    echo Output file: Output\WatchCats-Setup.exe
    echo 输出文件: Output\WatchCats-Setup.exe
    echo ======================================
    echo.
    echo You can now test the installer.
    echo 您现在可以测试安装程序了。
) else (
    echo.
    echo ======================================
    echo Build failed! 构建失败！
    echo Please check the error messages above.
    echo 请检查上面的错误信息。
    echo ======================================
)

pause