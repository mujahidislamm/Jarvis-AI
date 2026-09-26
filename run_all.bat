@echo off
title Jarvis AI - Master Launcher
color 0A
cls

echo =======================================================
echo              JARVIS AI MASTER LAUNCHER
echo =======================================================
echo.
echo  Choose how you want to run Jarvis:
echo.
echo  [1] Web Interface (Website on http://localhost:5000)
echo  [2] Desktop Application (PySide6 GUI)
echo  [3] Launch Both (Web Server + Desktop GUI)
echo  [4] Exit
echo.
echo =======================================================
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto run_web
if "%choice%"=="2" goto run_desktop
if "%choice%"=="3" goto run_both
if "%choice%"=="4" goto end
goto invalid

:run_web
call "%~dp0run_site.bat"
goto end

:run_desktop
call "%~dp0run_desktop_app.bat"
goto end

:run_both
echo Starting Web Server in new window...
start "Jarvis Web Server" cmd /c "%~dp0run_site.bat"
timeout /t 2 >nul
echo Starting Desktop App...
call "%~dp0run_desktop_app.bat"
goto end

:invalid
echo Invalid choice.
pause
goto end

:end
