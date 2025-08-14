@echo off
echo ========================================
echo Testing Direct Python Execution
echo ========================================

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the application directly with Python
echo.
echo Running application with Python...
echo.
python run_desktop_pet.py

REM Keep window open to see any errors
echo.
echo ========================================
echo Press any key to exit...
pause > nul