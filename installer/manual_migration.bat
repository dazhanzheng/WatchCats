@echo off
REM 手动数据迁移脚本
REM Manual data migration script for WatchCats

echo ======================================
echo WatchCats 数据迁移工具
echo WatchCats Data Migration Tool
echo ======================================
echo.

REM 设置路径
set OLD_DIR=%APPDATA%\BaalPet
set NEW_DIR=%LOCALAPPDATA%\WatchCats

echo 旧版本路径 / Old path: %OLD_DIR%
echo 新版本路径 / New path: %NEW_DIR%
echo.

REM 检查旧目录是否存在
if not exist "%OLD_DIR%" (
    echo [错误] 未找到旧版本数据目录！
    echo [ERROR] Old version data directory not found!
    echo.
    echo 请确认 BaalPet 曾经安装在此计算机上。
    echo Please confirm BaalPet was installed on this computer.
    pause
    exit /b 1
)

echo 找到旧版本数据 / Found old version data
echo.

REM 创建新目录
if not exist "%NEW_DIR%" (
    echo 创建新目录... / Creating new directory...
    mkdir "%NEW_DIR%"
)

if not exist "%NEW_DIR%\logs" mkdir "%NEW_DIR%\logs"
if not exist "%NEW_DIR%\data" mkdir "%NEW_DIR%\data"

echo ======================================
echo 开始迁移文件 / Starting file migration
echo ======================================
echo.

REM 迁移配置文件
if exist "%OLD_DIR%\config.json" (
    echo 迁移配置文件... / Migrating config file...
    copy /Y "%OLD_DIR%\config.json" "%NEW_DIR%\config.json" >nul 2>&1
    if exist "%NEW_DIR%\config.json" (
        echo [OK] config.json
    ) else (
        echo [FAIL] config.json
    )
)

REM 迁移聊天记录（注意文件名变化）
if exist "%OLD_DIR%\chat_history.json" (
    echo 迁移聊天记录... / Migrating chat history...
    REM 新版本使用 conversation_history.json
    copy /Y "%OLD_DIR%\chat_history.json" "%NEW_DIR%\conversation_history.json" >nul 2>&1
    if exist "%NEW_DIR%\conversation_history.json" (
        echo [OK] chat_history.json -^> conversation_history.json
    ) else (
        echo [FAIL] chat_history.json
    )
) else if exist "%OLD_DIR%\conversation_history.json" (
    REM 如果已经是新格式
    copy /Y "%OLD_DIR%\conversation_history.json" "%NEW_DIR%\conversation_history.json" >nul 2>&1
    if exist "%NEW_DIR%\conversation_history.json" (
        echo [OK] conversation_history.json
    ) else (
        echo [FAIL] conversation_history.json
    )
)

REM 迁移日程文件
if exist "%OLD_DIR%\schedules.json" (
    echo 迁移日程... / Migrating schedules...
    copy /Y "%OLD_DIR%\schedules.json" "%NEW_DIR%\schedules.json" >nul 2>&1
    if exist "%NEW_DIR%\schedules.json" (
        echo [OK] schedules.json
    ) else (
        echo [FAIL] schedules.json
    )
)

REM 迁移目标文件
if exist "%OLD_DIR%\goals.json" (
    echo 迁移目标... / Migrating goals...
    copy /Y "%OLD_DIR%\goals.json" "%NEW_DIR%\goals.json" >nul 2>&1
    if exist "%NEW_DIR%\goals.json" (
        echo [OK] goals.json
    ) else (
        echo [FAIL] goals.json
    )
)

REM 迁移监督配置
if exist "%OLD_DIR%\supervision_config.json" (
    echo 迁移监督配置... / Migrating supervision config...
    copy /Y "%OLD_DIR%\supervision_config.json" "%NEW_DIR%\supervision_config.json" >nul 2>&1
    if exist "%NEW_DIR%\supervision_config.json" (
        echo [OK] supervision_config.json
    ) else (
        echo [FAIL] supervision_config.json
    )
)

REM 迁移 memory 文件夹
if exist "%OLD_DIR%\memory" (
    echo 迁移记忆文件夹... / Migrating memory folder...
    if not exist "%NEW_DIR%\memory" mkdir "%NEW_DIR%\memory"
    xcopy "%OLD_DIR%\memory\*.*" "%NEW_DIR%\memory\" /E /Y /Q >nul 2>&1
    if exist "%NEW_DIR%\memory" (
        echo [OK] memory folder
    ) else (
        echo [FAIL] memory folder
    )
)

echo.
echo ======================================
echo 迁移完成 / Migration completed
echo ======================================
echo.

REM 显示新目录内容
echo 新目录内容 / New directory contents:
dir "%NEW_DIR%" /B
echo.

echo ======================================
echo 重要提示 / Important Notice
echo ======================================
echo.
echo 旧版本数据保留在 / Old data preserved at:
echo %OLD_DIR%
echo.
echo 请确认新版本 WatchCats 正常运行后再删除旧数据。
echo Please delete old data only after confirming WatchCats works properly.
echo.
echo 如果需要恢复，可以删除新目录并重新运行此脚本。
echo If you need to restore, delete the new directory and run this script again.
echo.

pause