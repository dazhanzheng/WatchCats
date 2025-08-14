@echo off
echo ========================================
echo Starting Baal Pet Assistant...
echo ========================================

REM Set Qt plugin paths for safety
set QT_PLUGIN_PATH=%~dp0PyQt6\Qt6\plugins;%~dp0Qt6\plugins;%~dp0plugins
set QT_QPA_PLATFORM_PLUGIN_PATH=%~dp0PyQt6\Qt6\plugins\platforms;%~dp0Qt6\plugins\platforms;%~dp0plugins\platforms
set QT_OPENGL=angle
set QT_QUICK_BACKEND=software

REM Check which exe exists and run it
if exist "%~dp0WatchCats.exe" (
    echo Found WatchCats.exe
    start "" "%~dp0WatchCats.exe"
) else if exist "%~dp0Baal宠物助手.exe" (
    echo Found Baal宠物助手.exe
    start "" "%~dp0Baal宠物助手.exe"
) else if exist "%~dp0BaalPetAssistant.exe" (
    echo Found BaalPetAssistant.exe
    start "" "%~dp0BaalPetAssistant.exe"
) else (
    echo [ERROR] No executable found!
    echo.
    echo Please make sure one of these files exists:
    echo   - WatchCats.exe
    echo   - Baal宠物助手.exe
    echo   - BaalPetAssistant.exe
    echo.
    pause
)