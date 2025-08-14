@echo off
echo ========================================
echo Quick Test Commands for Windows
echo ========================================
echo.

echo 1. Testing with Python directly:
echo    venv\Scripts\python.exe run_desktop_pet.py
echo.

echo 2. Testing with debug script:
echo    venv\Scripts\python.exe run_desktop_pet_debug.py
echo.

echo 3. Testing with debug launcher:
echo    venv\Scripts\python.exe debug_launcher.py
echo.

echo 4. Testing environment:
echo    venv\Scripts\python.exe test_windows_env.py
echo.

echo ========================================
echo Choose an option (1-4):
set /p choice=

if "%choice%"=="1" (
    venv\Scripts\python.exe run_desktop_pet.py
) else if "%choice%"=="2" (
    venv\Scripts\python.exe run_desktop_pet_debug.py
) else if "%choice%"=="3" (
    venv\Scripts\python.exe debug_launcher.py
) else if "%choice%"=="4" (
    venv\Scripts\python.exe test_windows_env.py
) else (
    echo Invalid choice
)

echo.
pause