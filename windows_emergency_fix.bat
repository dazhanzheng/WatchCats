@echo off
setlocal enabledelayedexpansion
color 0A
title Baal Pet Assistant - Emergency Fix Tool

echo ====================================
echo Windows Emergency Fix Tool
echo For Baal Pet Assistant
echo ====================================
echo.

REM 检查管理员权限并自动提升
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] This script needs Administrator privileges.
    echo.
    echo Attempting to restart with Administrator rights...
    echo.
    
    REM 创建 VBS 脚本以管理员身份运行
    echo Set UAC = CreateObject^("Shell.Application"^) > "%temp%\getadmin.vbs"
    echo UAC.ShellExecute "%~s0", "", "", "runas", 1 >> "%temp%\getadmin.vbs"
    
    "%temp%\getadmin.vbs"
    del "%temp%\getadmin.vbs"
    
    REM 如果用户拒绝了 UAC 提示，显示手动指引
    echo.
    echo If the automatic elevation failed:
    echo   1. Close this window
    echo   2. Right-click on windows_emergency_fix.bat
    echo   3. Select "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [+] Running with Administrator privileges.
echo.

echo [1/5] Setting environment variables...
setx QT_PLUGIN_PATH "%~dp0PyQt6\Qt6\plugins;%~dp0Qt6\plugins;%~dp0plugins" /M
setx QT_QPA_PLATFORM_PLUGIN_PATH "%~dp0PyQt6\Qt6\plugins\platforms;%~dp0Qt6\plugins\platforms;%~dp0plugins\platforms" /M
setx QT_OPENGL "angle" /M
setx QT_QUICK_BACKEND "software" /M
echo Environment variables set globally.
echo.

echo [2/5] Checking Visual C++ Redistributables...
echo This may take a few seconds...
wmic product where "name like '%%Visual C++%%'" get name,version 2>nul | findstr /i "2015 2019 2022" >nul
if %errorlevel% neq 0 (
    color 0E
    echo.
    echo [WARNING] Visual C++ Redistributables not found!
    echo.
    echo The application may crash without these libraries.
    echo.
    echo Do you want to open the download page? (Y/N)
    set /p download_vc=
    if /i "!download_vc!"=="Y" (
        start https://aka.ms/vs/17/release/vc_redist.x64.exe
        echo.
        echo Download page opened in your browser.
        echo Please install the VC++ Redistributables and run this fix again.
    )
    color 0A
    echo.
) else (
    echo [OK] Visual C++ Redistributables found
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
    color 0C
    echo.
    echo [ERROR] qwindows.dll not found!
    echo.
    echo The application WILL crash without this file.
    echo This usually means the package is incomplete.
    echo.
    echo Recommended actions:
    echo   1. Re-download the complete package
    echo   2. Check if antivirus quarantined the file
    echo   3. Extract the ZIP to a folder without special characters
    echo.
    color 0A
    pause
) else (
    echo [OK] Qt plugins found
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
echo Emergency fixes applied successfully!
echo ====================================
echo.
echo What to do next:
echo.
echo   [1] Try Start_Safe.bat (recommended)
echo   [2] Try Debug.bat (shows detailed output)
echo   [3] Run WatchCats.exe directly
echo.
echo If the app still crashes:
echo   - Install Visual C++ Redistributables if not done
echo   - Temporarily disable antivirus/Windows Defender
echo   - Move app to C:\BaalPet\ (avoid special characters)
echo   - Run everything as Administrator
echo.
echo ====================================
echo.

REM 询问是否立即尝试运行
echo Do you want to try running the app now? (Y/N)
set /p run_now=
if /i "!run_now!"=="Y" (
    echo.
    echo Starting Baal Pet Assistant with safe settings...
    call "%~dp0Start_Safe.bat"
    if errorlevel 1 (
        echo.
        color 0C
        echo [!] The application crashed or exited with errors.
        echo [!] Please try Debug.bat to see detailed error messages.
        color 0A
    )
)

echo.
echo Press any key to exit the fix tool...
pause >nul
exit /b 0