@echo off
echo ==========================================
echo      MR OG TOOL - BUILD SCRIPT
echo ==========================================
echo.
set PYTHON_EXE="%LOCALAPPDATA%\Programs\Python\Python312\python.exe"

echo [*] Generating Icon...
%PYTHON_EXE% convert_icon.py

echo [*] Cleaning up previous builds...
rmdir /s /q build dist
del /q *.spec

echo.
echo [*] Installing PyInstaller (if missing)...
%PYTHON_EXE% -m pip install pyinstaller
%PYTHON_EXE% -m pip install pillow
%PYTHON_EXE% -m pip install requests

echo.
echo [*] Building Executable...
:: --noconsole: Hides the black command window (GUI only)
:: --onefile: Bundles everything into a single .exe
:: --name: Sets the output name
:: --add-data: Includes assets and config files
:: --icon: (Optional) You can add --icon=assets/icon.ico if you have one

%PYTHON_EXE% -m PyInstaller --noconsole --onefile --name "MR_OG_TOOL" ^
    --add-data "ui;ui" ^
    --add-data "core;core" ^
    --add-data "assets;assets" ^
    --add-data "config.json;." ^
    --hidden-import="PIL" ^
    --hidden-import="PIL._tkinter_finder" ^
    --hidden-import="customtkinter" ^
    --icon "assets\logo.ico" ^
    main.py

echo.
echo [*] Copying to Desktop...
copy "dist\MR_OG_TOOL.exe" "%USERPROFILE%\Desktop\MR_OG_TOOL.exe"

echo.
echo ==========================================
echo      BUILD COMPLETE!
echo      File copied to: %USERPROFILE%\Desktop\MR_OG_TOOL.exe
echo ==========================================
echo.
pause
