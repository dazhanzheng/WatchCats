@echo off
echo ====================================
echo Baal 宠物助手 - Windows 调试模式
echo ====================================
echo.

REM 设置调试环境变量
set BAAL_DEBUG=true
set BAAL_DEV_MODE=true
set QT_DEBUG_PLUGINS=1
set QT_LOGGING_RULES=qt.qpa.plugin=true

echo 环境变量已设置：
echo   BAAL_DEBUG=true (启用预检查)
echo   BAAL_DEV_MODE=true (开发模式)
echo   QT_DEBUG_PLUGINS=1 (Qt插件调试)
echo.

REM 检查是否有打包的exe
if exist "dist\WatchCats.exe" (
    echo 运行打包版本（带控制台）...
    echo ====================================
    "dist\WatchCats.exe"
    echo ====================================
    echo 程序已退出
) else if exist "dist\WatchCats_debug.exe" (
    echo 运行调试版本...
    echo ====================================
    "dist\WatchCats_debug.exe"
    echo ====================================
    echo 程序已退出
) else (
    echo 未找到打包的exe文件
    echo 尝试使用Python直接运行...
    echo ====================================
    
    if exist "venv\Scripts\python.exe" (
        venv\Scripts\python.exe run_desktop_pet.py
    ) else (
        python run_desktop_pet.py
    )
    
    echo ====================================
    echo 程序已退出
)

echo.
echo 按任意键退出...
pause > nul