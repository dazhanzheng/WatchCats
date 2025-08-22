@echo off
REM 下载 Visual C++ Redistributable 2015-2022
REM Download Visual C++ Redistributable 2015-2022

echo ==========================================
echo 下载 Visual C++ 运行库安装程序
echo Downloading Visual C++ Redistributables
echo ==========================================
echo.

REM 创建 vcredist 目录
if not exist vcredist mkdir vcredist

echo [1/2] 下载 64位 Visual C++ Redistributable...
echo Downloading x64 Visual C++ Redistributable...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x64.exe' -OutFile 'vcredist\vc_redist.x64.exe'}"
if %errorlevel% neq 0 (
    echo 错误：下载 x64 运行库失败！
    echo Error: Failed to download x64 redistributable!
    goto :error
)
echo 成功！Successfully downloaded x64 redistributable!
echo.

echo [2/2] 下载 32位 Visual C++ Redistributable...
echo Downloading x86 Visual C++ Redistributable...
powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://aka.ms/vs/17/release/vc_redist.x86.exe' -OutFile 'vcredist\vc_redist.x86.exe'}"
if %errorlevel% neq 0 (
    echo 错误：下载 x86 运行库失败！
    echo Error: Failed to download x86 redistributable!
    goto :error
)
echo 成功！Successfully downloaded x86 redistributable!
echo.

echo ==========================================
echo 所有运行库下载完成！
echo All redistributables downloaded successfully!
echo ==========================================
echo.
echo 文件位置 Files location:
echo   - vcredist\vc_redist.x64.exe
echo   - vcredist\vc_redist.x86.exe
echo.
pause
exit /b 0

:error
echo.
echo ==========================================
echo 下载失败！请检查网络连接后重试。
echo Download failed! Please check your internet connection and try again.
echo ==========================================
pause
exit /b 1