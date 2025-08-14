@echo off
REM Debug build script for Windows with error diagnostics

echo =========================================
echo Building Baal Pet Assistant (Debug Mode)
echo =========================================

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt
pip install pyinstaller==6.11.1
pip install pillow

REM Convert icon
echo Converting icon...
python convert_icon.py
if errorlevel 1 (
    echo Warning: Icon conversion failed
)

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build with debug spec
echo Building executable (debug mode)...
pyinstaller --clean --noconfirm baal_windows_debug.spec
if errorlevel 1 (
    echo Build failed!
    pause
    exit /b 1
)

REM Test the executable
echo Testing executable...
if exist "dist\WatchCats_Debug.exe" (
    echo Executable found: dist\WatchCats_Debug.exe
    echo.
    echo Running test...
    cd dist
    WatchCats_Debug.exe --test
    cd ..
) else (
    echo Executable not found!
    pause
    exit /b 1
)

echo.
echo Build complete! Check dist\WatchCats_Debug.exe
echo If it crashes, check baal_debug.log for details
pause