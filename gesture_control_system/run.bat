@echo off
title GestureLink AI Application Launcher
color 0b

echo ==========================================================
echo               GESTURELINK AI APP LAUNCHER
echo ==========================================================
echo Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not added to your system PATH.
    echo Please install Python and try again.
    pause
    exit /b
)

echo.
echo Installing and verifying dependencies from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [WARNING] Some dependencies failed to install. We will attempt to run anyway...
)

echo.
echo Starting Flask backend server...
echo ----------------------------------------------------------
echo Open your browser and navigate to: http://localhost:5000
echo ----------------------------------------------------------
echo To exit: Press Ctrl+C in this terminal window.
echo.

python app.py

pause
