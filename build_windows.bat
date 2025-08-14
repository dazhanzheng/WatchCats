@echo off
echo ====================================
echo Baal宠物助手 Windows 构建脚本
echo ====================================

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未找到Python，请先安装Python 3.9或更高版本
    pause
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo 创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo 激活虚拟环境...
call venv\Scripts\activate.bat

REM 升级pip
echo 升级pip...
python -m pip install --upgrade pip

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 安装PyInstaller（如果尚未安装）
pip install pyinstaller==6.11.1

REM 生成.ico图标（如果不存在）
if not exist "baal\resources\cat.ico" (
    echo 注意: 未找到cat.ico图标文件
    echo 请使用图像编辑软件将cat.png转换为cat.ico格式
    echo 或使用在线转换工具: https://convertio.co/png-ico/
)

REM 清理旧的构建文件
echo 清理旧的构建文件...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM 使用PyInstaller打包
echo 开始打包...
pyinstaller --clean --noconfirm baal_windows.spec

REM 检查构建结果
if exist "dist\WatchCats.exe" (
    echo.
    echo ====================================
    echo 构建成功！
    echo ====================================
    echo 可执行文件位置: dist\WatchCats.exe
    echo.
    echo 您可以：
    echo 1. 直接运行 start.bat 启动程序
    echo 2. 或直接运行 dist\WatchCats.exe
    echo 3. 将 dist 文件夹复制到其他电脑使用
) else (
    echo.
    echo ====================================
    echo 构建失败！
    echo ====================================
    echo 请检查错误信息并重试
)

pause