@echo off
title ARIA Voice Assistant
color 0B

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║         ARIA - Bilingual Voice Assistant          ║
echo  ║              English + Hindi  🎙️                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

:: Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

:: Change to script directory
cd /d "%~dp0"

:: Check if venv exists, create if not
set "NEW_VENV=false"
if not exist "venv\" (
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    echo [SETUP] Virtual environment created.
    set "NEW_VENV=true"
)

:: Activate venv
call venv\Scripts\activate.bat

:: Install / update dependencies if new venv or if force flag is passed
if "%NEW_VENV%"=="true" (
    echo [SETUP] Installing dependencies - this may take a few minutes...
    pip install -r requirements.txt --no-warn-script-location
    pip install pyaudio 2>nul || echo [INFO] PyAudio not installed - mic input uses browser Web Speech API
    echo. > venv\.dependencies_installed
) else (
    if not exist "venv\.dependencies_installed" (
        echo [SETUP] Installing dependencies...
        pip install -r requirements.txt -q --no-warn-script-location
        pip install pyaudio -q 2>nul || echo [INFO] PyAudio not installed - mic input uses browser Web Speech API
        echo. > venv\.dependencies_installed
    ) else (
        echo [INFO] Skipping dependency check - already verified. Use verify.py to check if needed.
    )
)

echo.
echo [OK] Environment is ready!
echo.
echo ─────────────────────────────────────────────────────
echo   Starting ARIA Voice Assistant...
echo   Press Ctrl+C to stop the server
echo ─────────────────────────────────────────────────────
echo.

:: Run the app
python app.py

:: Deactivate on exit
deactivate
pause
