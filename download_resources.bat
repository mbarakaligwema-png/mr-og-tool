@echo off
cd /d "%~dp0"
echo ==================================================
echo   DOWNLOADING MR OG TOOL RESOURCES
echo ==================================================
echo.
echo   [1/1] Downloading Test DPC (MDM Bypass Agent)...

:: Ensure assets folder exists
if not exist "assets" mkdir "assets"

:: PowerShell Download Command
powershell -Command "Invoke-WebRequest -Uri 'https://github.com/googlesamples/android-testdpc/releases/download/9.0.12/TestDPC_9.0.12.apk' -OutFile 'assets/test_dpc.apk'"

if exist "assets/test_dpc.apk" (
    echo.
    echo   [SUCCESS] test_dpc.apk downloaded successfully!
    echo   Path: assets/test_dpc.apk
) else (
    echo.
    echo   [ERROR] Download failed. Check internet connection.
)

echo.
echo ==================================================
pause
