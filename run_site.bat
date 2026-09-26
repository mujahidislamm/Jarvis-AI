@echo off
title Jarvis AI - Web Interface Launcher
color 0B
cls

echo =======================================================
echo          JARVIS AI - NEURAL ASSISTANT (WEB)
echo =======================================================
echo.
echo [1/3] Navigating to application root...
cd /d "%~dp0"

echo [2/3] Checking Python environment...
if exist ".venv\Scripts\activate.bat" (
    echo       Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else (
    echo       Using system Python environment...
)

echo [3/3] Opening Brave at http://localhost:5000 ...
set "BRAVE_PATH=C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
if not exist "%BRAVE_PATH%" set "BRAVE_PATH=C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
if exist "%BRAVE_PATH%" (
    start "" "%BRAVE_PATH%" --new-window " "
) else (
    start "" "http://localhost:5000"
)

echo.
echo =======================================================
echo  Jarvis AI Server is starting on http://localhost:5000
echo  Press CTRL+C in this terminal window to stop the server.
echo =======================================================
echo.

python server.py

if errorlevel 1 (
    echo.
    echo [ERROR] Server encountered an error. Press any key to exit.
    pause >nul
)
