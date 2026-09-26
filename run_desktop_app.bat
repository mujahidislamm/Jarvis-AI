@echo off
title Jarvis AI - Desktop Interface Launcher
color 0D
cls

echo =======================================================
echo        JARVIS AI - DESKTOP APPLICATION (PySide6)
echo =======================================================
echo.
cd /d "%~dp0"

if exist ".venv\Scripts\activate.bat" (
    echo Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
)

echo Starting Jarvis AI Desktop App...
python Frontend/main.py

if errorlevel 1 (
    echo.
    echo [ERROR] Desktop application stopped with error code %errorlevel%.
    pause >nul
)
