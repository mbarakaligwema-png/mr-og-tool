@echo off
echo ==================================================
echo   UPLOADING MR OG TOOL TO GITHUB
echo ==================================================
echo.

:: Set Git Path directly
set "GIT_PATH=C:\Program Files\Git\cmd\git.exe"

if not exist "%GIT_PATH%" (
    echo [ERROR] Git haionekani hapa: "%GIT_PATH%"
    echo Tafadhali install Git kwa uhakika.
    pause
    exit /b
)

echo [STEP 1] Configuring Git Identity (Lazima kwa GitHub)
echo Tafadhali andika Email na Jina lako unalotumia GitHub.
echo.
set "GIT_EMAIL=mbarakaligwema@gmail.com"
set "GIT_NAME=mr-og-tool"

"%GIT_PATH%" config user.email "%GIT_EMAIL%"
"%GIT_PATH%" config user.name "%GIT_NAME%"

echo.
echo [STEP 2] Initializing Git...
"%GIT_PATH%" init

echo [STEP 3] Adding Files...
"%GIT_PATH%" add .

echo [STEP 4] Committing...
"%GIT_PATH%" commit -m "Release v1.6.0 - Setup with Auto-Uninstall"

echo [STEP 5] Setting Branch to Main...
"%GIT_PATH%" branch -M main

echo [STEP 6] Adding Remote Origin...
"%GIT_PATH%" remote remove origin 2>nul
"%GIT_PATH%" remote add origin https://github.com/mbarakaligwema-png/mr-og-tool.git

echo [STEP 7] Pushing to GitHub...
echo.
echo [!] Itakuomba PASSWORD au TOKEN.
echo [!] Kama unatumia Password ya kawaida na inakataa, inabidi utengeneze "Personal Access Token" GitHub.
echo.
"%GIT_PATH%" push -u origin main

echo.
echo ==================================================
echo   IMEMALIZA. KAMA HAMNA ERROR, IPO GITHUB!
echo ==================================================
pause
