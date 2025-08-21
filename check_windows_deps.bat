@echo off
chcp 65001 >nul 2>&1
title Watch Cats 依赖检查工具

echo ========================================
echo Watch Cats 依赖检查工具 (简化版)
echo ========================================
echo.

:: 检查 Visual C++ Redistributable
echo 检查 Visual C++ Redistributable...
where /q vcruntime140.dll
if %ERRORLEVEL% EQU 0 (
    echo   √ 找到 VC++ 运行时
) else (
    echo   × 未找到 VC++ 运行时
    echo.
    echo 需要安装 Visual C++ Redistributable 2015-2022
    echo 下载地址：
    echo https://aka.ms/vs/17/release/vc_redist.x64.exe
    echo.
    set /p install="是否打开下载页面? (Y/N): "
    if /i "%install%"=="Y" (
        start https://aka.ms/vs/17/release/vc_redist.x64.exe
    )
)

echo.
echo 检查系统 DLL...
:: 检查关键 DLL
set missing_dll=0
for %%D in (msvcp140.dll vcruntime140.dll vcruntime140_1.dll) do (
    if not exist "%SystemRoot%\System32\%%D" (
        echo   × 缺少 %%D
        set missing_dll=1
    )
)

if %missing_dll%==0 (
    echo   √ 所有关键 DLL 都存在
)

echo.
echo 检查 DirectX...
if exist "%SystemRoot%\System32\d3dcompiler_47.dll" (
    echo   √ DirectX 编译器存在
) else (
    echo   × d3dcompiler_47.dll 未找到
    echo   建议安装最新的 DirectX End-User Runtime
)

echo.
echo ========================================
echo 检查完成！
echo.
echo 如果 Watch Cats 仍然无法启动，请尝试：
echo 1. 以管理员身份运行应用
echo 2. 安装所有 Windows 更新
echo 3. 更新显卡驱动
echo 4. 关闭杀毒软件临时测试
echo ========================================
echo.

pause