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

echo [STEP 1] Adding Files...
"%GIT_PATH%" add .

echo [STEP 2] Committing...
set /p COMMIT_MSG="Enter commit message (Leave empty for default): "
if "%COMMIT_MSG%"=="" set "COMMIT_MSG=Update v1.7.0 Features: Private DNS Block & Network Reset Fix"
"%GIT_PATH%" commit -m "%COMMIT_MSG%"

echo [STEP 3] Pushing to GitHub...
"%GIT_PATH%" push origin main

echo.
echo ==================================================
echo   IMEMALIZA. KAMA HAMNA ERROR, IPO GITHUB!
echo ==================================================
pause
