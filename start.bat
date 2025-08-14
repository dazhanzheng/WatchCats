@echo off
echo ====================================
echo 启动 Baal 宠物助手
echo ====================================

REM 检查可执行文件是否存在
if exist "dist\WatchCats.exe" (
    echo 启动程序: dist\WatchCats.exe
    start "" "dist\WatchCats.exe"
) else if exist "WatchCats.exe" (
    echo 启动程序: WatchCats.exe
    start "" "WatchCats.exe"
) else if exist "dist\WatchCats_debug.exe" (
    echo 启动调试版本: dist\WatchCats_debug.exe
    "dist\WatchCats_debug.exe"
) else (
    echo ======================================
    echo 错误：找不到可执行文件！
    echo ======================================
    echo.
    echo 请先运行 build_windows.bat 构建程序
    echo 或使用 Python 直接运行：
    echo    venv\Scripts\python.exe run_desktop_pet.py
    echo.
    pause
)