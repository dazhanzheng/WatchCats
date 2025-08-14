@echo off
echo ====================================
echo Baal 宠物助手 - 开发模式
echo ====================================

REM 激活虚拟环境并直接运行 Python 脚本
if exist "venv\Scripts\activate.bat" (
    echo 激活虚拟环境...
    call venv\Scripts\activate.bat
    echo 启动应用程序（Python 模式）...
    python run_desktop_pet.py
) else (
    echo 错误：找不到虚拟环境！
    echo 请先运行 build_windows.bat 创建虚拟环境
    pause
)