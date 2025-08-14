@echo off
echo ====================================
echo Windows Emergency Fix Tool
echo For Baal Pet Assistant
echo ====================================
echo.

REM 检查管理员权限
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This script needs to run as Administrator.
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/5] Setting environment variables...
setx QT_PLUGIN_PATH "%~dp0PyQt6\Qt6\plugins;%~dp0Qt6\plugins;%~dp0plugins" /M
setx QT_QPA_PLATFORM_PLUGIN_PATH "%~dp0PyQt6\Qt6\plugins\platforms;%~dp0Qt6\plugins\platforms;%~dp0plugins\platforms" /M
setx QT_OPENGL "angle" /M
setx QT_QUICK_BACKEND "software" /M
echo Environment variables set globally.
echo.

echo [2/5] Checking Visual C++ Redistributables...
wmic product where "name like '%%Visual C++%%'" get name,version 2>nul | findstr /i "2015 2019 2022" >nul
if %errorlevel% neq 0 (
    echo WARNING: Visual C++ Redistributables not found!
    echo Please download and install from:
    echo https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
) else (
    echo Visual C++ Redistributables: OK
)

echo [3/5] Checking Qt plugins...
set FOUND_QT=0
if exist "%~dp0PyQt6\Qt6\plugins\platforms\qwindows.dll" (
    echo Found: PyQt6\Qt6\plugins\platforms\qwindows.dll
    set FOUND_QT=1
)
if exist "%~dp0Qt6\plugins\platforms\qwindows.dll" (
    echo Found: Qt6\plugins\platforms\qwindows.dll
    set FOUND_QT=1
)
if exist "%~dp0plugins\platforms\qwindows.dll" (
    echo Found: plugins\platforms\qwindows.dll
    set FOUND_QT=1
)

if %FOUND_QT% equ 0 (
    echo ERROR: qwindows.dll not found!
    echo The application will crash without this file.
    echo Please re-download the complete package.
) else (
    echo Qt plugins: OK
)
echo.

echo [4/5] Creating safe launcher...
(
echo @echo off
echo REM Safe launcher with all fixes applied
echo set QT_PLUGIN_PATH=%%~dp0PyQt6\Qt6\plugins;%%~dp0Qt6\plugins;%%~dp0plugins
echo set QT_QPA_PLATFORM_PLUGIN_PATH=%%~dp0PyQt6\Qt6\plugins\platforms;%%~dp0Qt6\plugins\platforms;%%~dp0plugins\platforms
echo set QT_OPENGL=angle
echo set QT_QUICK_BACKEND=software
echo set QT_LOGGING_RULES=qt.qpa.plugin=true
echo.
echo echo Starting Baal Pet Assistant with fixes...
echo start "" "%%~dp0WatchCats.exe"
echo if errorlevel 1 (
echo     echo.
echo     echo Application crashed! Trying debug mode...
echo     "%%~dp0WatchCats.exe"
echo     pause
echo ^)
) > "%~dp0Start_Safe.bat"
echo Created: Start_Safe.bat
echo.

echo [5/5] Creating debug launcher...
(
echo @echo off
echo REM Debug launcher with console output
echo set QT_PLUGIN_PATH=%%~dp0PyQt6\Qt6\plugins;%%~dp0Qt6\plugins;%%~dp0plugins
echo set QT_QPA_PLATFORM_PLUGIN_PATH=%%~dp0PyQt6\Qt6\plugins\platforms;%%~dp0Qt6\plugins\platforms;%%~dp0plugins\platforms
echo set QT_OPENGL=angle
echo set QT_QUICK_BACKEND=software
echo set QT_DEBUG_PLUGINS=1
echo set QT_LOGGING_RULES=qt.qpa.plugin=true
echo.
echo echo Debug mode - showing all output...
echo "%%~dp0WatchCats.exe"
echo.
echo echo ====================================
echo echo Program exited. Check output above for errors.
echo pause
) > "%~dp0Debug.bat"
echo Created: Debug.bat
echo.

echo ====================================
echo Emergency fixes applied!
echo.
echo Try running the application with:
echo   1. Start_Safe.bat (recommended)
echo   2. Debug.bat (if crashes persist)
echo.
echo If still having issues:
echo   - Install Visual C++ Redistributables
echo   - Run as Administrator
echo   - Disable antivirus temporarily
echo ====================================
echo.
pause