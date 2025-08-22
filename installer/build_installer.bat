@echo off
REM Baal Pet Assistant Installer Build Script
REM 构建 Baal 宠物助手安装包

echo ==========================================
echo Baal 宠物助手安装包构建脚本
echo Baal Pet Assistant Installer Build Script
echo ==========================================
echo.

REM 检查是否在正确的目录
if not exist baal_installer.iss (
    echo 错误：找不到 baal_installer.iss 文件！
    echo Error: Cannot find baal_installer.iss file!
    echo 请在 installer 目录中运行此脚本。
    echo Please run this script from the installer directory.
    pause
    exit /b 1
)

REM 检查 Inno Setup 是否安装
set ISCC_PATH=
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
) else if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" (
    set "ISCC_PATH=%ProgramFiles%\Inno Setup 6\ISCC.exe"
) else (
    echo ==========================================
    echo 错误：未找到 Inno Setup 6！
    echo Error: Inno Setup 6 not found!
    echo ==========================================
    echo.
    echo 请从以下地址下载并安装 Inno Setup 6：
    echo Please download and install Inno Setup 6 from:
    echo https://jrsoftware.org/isdl.php
    echo.
    pause
    exit /b 1
)

echo 找到 Inno Setup: %ISCC_PATH%
echo Found Inno Setup at: %ISCC_PATH%
echo.

REM 检查主程序是否已构建
if not exist ..\dist\WatchCats.exe (
    echo ==========================================
    echo 警告：未找到已构建的程序！
    echo Warning: Built executable not found!
    echo ==========================================
    echo.
    echo 请先运行 build_windows.bat 构建主程序。
    echo Please run build_windows.bat first to build the main program.
    echo.
    set /p CONTINUE=是否继续？(y/n) Continue anyway? (y/n): 
    if /i not "%CONTINUE%"=="y" (
        exit /b 1
    )
)

REM 检查 VC++ 运行库文件
if not exist vcredist\vc_redist.x64.exe (
    echo ==========================================
    echo 未找到 Visual C++ 运行库文件
    echo Visual C++ Redistributable files not found
    echo ==========================================
    echo.
    echo 正在下载运行库文件...
    echo Downloading redistributable files...
    echo.
    call download_vcredist.bat
    if %errorlevel% neq 0 (
        echo 下载失败！Download failed!
        pause
        exit /b 1
    )
)

REM 创建输出目录
if not exist Output mkdir Output

REM 清理旧的安装包
if exist Output\BaalPetAssistantSetup.exe (
    echo 删除旧的安装包...
    echo Removing old installer...
    del /f /q Output\BaalPetAssistantSetup.exe
)

echo.
echo ==========================================
echo 开始编译安装包...
echo Starting installer compilation...
echo ==========================================
echo.

REM 编译安装包
"%ISCC_PATH%" /Q baal_installer.iss

if %errorlevel% equ 0 (
    echo.
    echo ==========================================
    echo 安装包构建成功！
    echo Installer built successfully!
    echo ==========================================
    echo.
    echo 输出文件 Output file:
    echo   Output\BaalPetAssistantSetup.exe
    echo.
    echo 文件大小 File size:
    for %%A in (Output\BaalPetAssistantSetup.exe) do echo   %%~zA bytes
    echo.
    echo 现在可以分发此安装包了！
    echo The installer is ready for distribution!
    echo.
) else (
    echo.
    echo ==========================================
    echo 错误：安装包构建失败！
    echo Error: Installer build failed!
    echo ==========================================
    echo.
    echo 请检查错误信息并重试。
    echo Please check the error messages and try again.
    echo.
)

pause