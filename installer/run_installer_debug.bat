@echo off
REM 以调试模式运行安装程序
REM Run installer in debug mode

echo ======================================
echo 调试模式安装程序
echo Debug Mode Installer
echo ======================================
echo.

REM 检查安装程序是否存在
if not exist "Output\WatchCats-Setup.exe" (
    echo 错误：安装程序不存在！
    echo Error: Installer does not exist!
    echo 请先运行 build_installer.bat 构建安装程序
    echo Please run build_installer.bat first
    pause
    exit /b 1
)

echo 将以调试模式运行安装程序...
echo Running installer in debug mode...
echo.
echo 这将生成详细的日志文件：
echo This will generate detailed log file:
echo   %TEMP%\WatchCats-Setup-Log.txt
echo.
echo 提示：
echo - 如果迁移失败，请查看日志文件
echo - 日志中搜索 "Migration:" 查看迁移详情
echo - 日志中搜索 "SafeCopyFile:" 查看文件复制详情
echo.
echo Tips:
echo - Check log file if migration fails
echo - Search "Migration:" in log for migration details
echo - Search "SafeCopyFile:" in log for file copy details
echo.

REM 运行安装程序并启用日志
Output\WatchCats-Setup.exe /LOG="%TEMP%\WatchCats-Setup-Log.txt"

echo.
echo ======================================
echo 安装完成 / Installation completed
echo ======================================
echo.
echo 日志文件位置 / Log file location:
echo %TEMP%\WatchCats-Setup-Log.txt
echo.
echo 打开日志文件？/ Open log file? (Y/N)
choice /C YN /N /M ">"
if %ERRORLEVEL% EQU 1 (
    notepad "%TEMP%\WatchCats-Setup-Log.txt"
)

pause