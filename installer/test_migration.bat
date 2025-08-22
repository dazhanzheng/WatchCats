@echo off
REM 测试数据迁移的批处理脚本
REM Test script for data migration

echo ======================================
echo 数据迁移测试脚本
echo Data Migration Test Script
echo ======================================
echo.

REM 创建测试数据
echo 创建测试数据... / Creating test data...
echo.

REM 创建旧版本目录和文件
set OLD_DIR=%APPDATA%\BaalPet
set NEW_DIR=%LOCALAPPDATA%\WatchCats

echo 旧版本路径 / Old path: %OLD_DIR%
echo 新版本路径 / New path: %NEW_DIR%
echo.

REM 创建测试数据（如果不存在）
if not exist "%OLD_DIR%" (
    echo 创建测试目录... / Creating test directory...
    mkdir "%OLD_DIR%"
    mkdir "%OLD_DIR%\memory"
    
    echo 创建测试文件... / Creating test files...
    echo {"api_key": "test_key", "model": "gpt-3.5"} > "%OLD_DIR%\config.json"
    echo [{"message": "Hello", "timestamp": "2024-01-01"}] > "%OLD_DIR%\chat_history.json"
    echo {"schedules": []} > "%OLD_DIR%\schedules.json"
    echo {"goals": []} > "%OLD_DIR%\goals.json"
    echo Test memory file > "%OLD_DIR%\memory\test.txt"
    
    echo 测试数据已创建 / Test data created
) else (
    echo 旧版本目录已存在 / Old directory already exists
)

echo.
echo ======================================
echo 检查文件权限... / Checking file permissions...
echo ======================================
echo.

REM 检查权限
icacls "%OLD_DIR%" | findstr /i "%USERNAME%" > nul
if %ERRORLEVEL% EQU 0 (
    echo [OK] 对旧目录有权限 / Have permissions for old directory
) else (
    echo [WARNING] 可能没有旧目录的权限 / May not have permissions for old directory
)

REM 检查新目录权限
if not exist "%NEW_DIR%" (
    mkdir "%NEW_DIR%" 2>nul
    if %ERRORLEVEL% EQU 0 (
        echo [OK] 可以创建新目录 / Can create new directory
        rmdir "%NEW_DIR%"
    ) else (
        echo [ERROR] 无法创建新目录 / Cannot create new directory
    )
) else (
    echo [INFO] 新目录已存在 / New directory already exists
)

echo.
echo ======================================
echo 测试文件复制方法... / Testing file copy methods...
echo ======================================
echo.

REM 创建临时测试文件
set TEST_SRC=%TEMP%\test_src.txt
set TEST_DST=%TEMP%\test_dst.txt
echo Test content > "%TEST_SRC%"

REM 测试方法1: copy命令
echo 测试 copy 命令... / Testing copy command...
copy /Y "%TEST_SRC%" "%TEST_DST%" >nul 2>&1
if exist "%TEST_DST%" (
    echo [OK] copy 命令可用 / copy command works
    del "%TEST_DST%"
) else (
    echo [FAIL] copy 命令失败 / copy command failed
)

REM 测试方法2: xcopy命令
echo 测试 xcopy 命令... / Testing xcopy command...
xcopy "%TEST_SRC%" "%TEST_DST%*" /Y /Q >nul 2>&1
if exist "%TEST_DST%" (
    echo [OK] xcopy 命令可用 / xcopy command works
    del "%TEST_DST%"
) else (
    echo [FAIL] xcopy 命令失败 / xcopy command failed
)

REM 测试方法3: PowerShell
echo 测试 PowerShell... / Testing PowerShell...
powershell -Command "Copy-Item -Path '%TEST_SRC%' -Destination '%TEST_DST%' -Force" >nul 2>&1
if exist "%TEST_DST%" (
    echo [OK] PowerShell 可用 / PowerShell works
    del "%TEST_DST%"
) else (
    echo [FAIL] PowerShell 失败 / PowerShell failed
)

REM 清理测试文件
del "%TEST_SRC%"

echo.
echo ======================================
echo 手动迁移命令 / Manual migration commands:
echo ======================================
echo.
echo 如果安装程序迁移失败，请运行以下命令：
echo If installer migration fails, run these commands:
echo.
echo xcopy "%OLD_DIR%\*.*" "%NEW_DIR%\" /E /I /Y /H
echo.
echo 或者使用 PowerShell / Or use PowerShell:
echo powershell -Command "Copy-Item -Path '%OLD_DIR%' -Destination '%NEW_DIR%' -Recurse -Force"
echo.

pause