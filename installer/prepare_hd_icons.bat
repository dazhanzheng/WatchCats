@echo off
REM 准备高质量 Windows 图标
REM Prepare high-quality Windows icons

echo ======================================
echo 准备高质量图标 / Preparing HD Icons
echo ======================================
echo.

REM 确保在 installer 目录
cd /d "%~dp0"

REM 检查 Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python！请先安装 Python 3
    echo [ERROR] Python not found! Please install Python 3
    pause
    exit /b 1
)

REM 安装 Pillow（如果需要）
echo 检查 Pillow 库... / Checking Pillow library...
python -c "import PIL" >nul 2>&1
if %errorlevel% neq 0 (
    echo 安装 Pillow... / Installing Pillow...
    pip install Pillow
)

REM 运行图标创建脚本
echo.
echo 创建高质量图标... / Creating high-quality icons...
python create_hd_icon.py

if %errorlevel% equ 0 (
    echo.
    echo ======================================
    echo 成功！/ Success!
    echo ======================================
    echo.
    echo 图标已创建在 / Icons created in: icons\
    echo.
    dir icons\*.* /b
) else (
    echo.
    echo [错误] 图标创建失败！
    echo [ERROR] Icon creation failed!
)

echo.
pause