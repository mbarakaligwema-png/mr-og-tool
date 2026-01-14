@echo off
echo ===================================================
echo   MR OG TOOL - INSTALLER GENERATOR
echo ===================================================
echo.

:: 1. Build the Main Tool (.exe)
echo [1/3] Building Core Application...
call build.bat
if %errorlevel% neq 0 (
    echo [ERROR] Build Failed! Fix errors above.
    pause
    exit /b
)

:: 2. Check for Inno Setup Compiler
echo.
echo [2/3] Checking for Inno Setup...
set "ISCC_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"

if not exist "%ISCC_PATH%" (
    echo.
    echo [ERROR] Inno Setup NOT FOUND!
    echo Please install Inno Setup 6.
    pause
    exit /b
)

:: 3. Compile the Installer
echo.
echo [3/3] Generating Setup.exe...
"%ISCC_PATH%" "setup_script.iss"

if %errorlevel% neq 0 (
    echo [ERROR] Installer Compilation Failed!
    pause
    exit /b
)

echo.
echo ===================================================
echo   SUCCESS! INSTALLER CREATED.
echo ===================================================
echo.
echo Check the 'Output' folder.
echo.
pause
