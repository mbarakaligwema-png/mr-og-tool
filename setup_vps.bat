@echo off
setlocal
echo ==================================================
echo   MR OG TOOL - VPS SETUP & DEPLOYMENT
echo ==================================================
echo.

set /p HOST=Enter VPS IP Address: 
set USER=root
set KEY_PATH=id_rsa

echo.
echo [1/3] Uploading Server Files to %HOST%...
scp -o StrictHostKeyChecking=no -r server requirements.txt %USER%@%HOST%:/root/
if %errorlevel% neq 0 (
    echo [ERROR] Failed to connect. Check IP and Password.
    pause
    exit /b
)

echo.
echo [2/3] Uploading Setup Script...
(
echo echo "Updating System..."
echo apt-get update -y
echo echo "Installing Python & Pip..."
echo apt-get install -y python3-pip python3-venv nginx
echo echo "Setting up Firewall..."
echo ufw allow OpenSSH
echo ufw allow 8000
echo ufw --force enable
echo echo "Installing Dependencies..."
echo pip3 install -r requirements.txt
echo echo "Starting Server with Gunicorn..."
echo pkill gunicorn
echo gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --daemon
echo echo "DONE! Server is running."
) > remote_setup.sh
scp remote_setup.sh %USER%@%HOST%:/root/

echo.
echo [3/3] Running Setup on VPS...
ssh %USER%@%HOST% "bash remote_setup.sh"

echo.
echo ==================================================
echo   DEPLOYMENT COMPLETE!
echo   Server URL: http://%HOST%:8000
echo ==================================================
pause
