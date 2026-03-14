@echo off
set GIT="C:\Program Files\Git\cmd\git.exe"
echo [1/3] Adding files...
%GIT% add server/main.py server/templates/home.html ui/gui_main.py
echo [2/3] Committing...
%GIT% commit -m "v1.7.3: New download link + fix update dialog bug"
echo [3/3] Pushing to GitHub (Railway auto-deploys)...
%GIT% push origin main
echo.
echo ✅ DONE! Railway itadeploy automatically.
