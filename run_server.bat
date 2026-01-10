@echo off
cd /d "%~dp0"
title MR OG TOOL - WEB SERVER
echo ==================================================
echo   STARTING MR OG TOOL SERVER
echo ==================================================
echo.
echo   [!] Keep this window OPEN while using the tool.
echo   [!] Server Address: http://127.0.0.1:8000
echo   [!] Admin Panel:    http://127.0.0.1:8000/admin
echo.
echo ==================================================
"%LOCALAPPDATA%\Programs\Python\Python312\python.exe" -m uvicorn main:app --reload --app-dir server --host 127.0.0.1 --port 8000
pause
