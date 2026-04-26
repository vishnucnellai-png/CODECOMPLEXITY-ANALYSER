@echo off
setlocal
echo ==============================================
echo   Code Complexity Analyser - Offline Edition
echo ==============================================
echo.

echo [1/3] Cleaning up any old instances on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "') do (
    if "%%a" neq "0" (
        echo Found process PID: %%a - terminating...
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo Done.
echo.

echo [2/3] Starting Django Backend Server...
cd /d "%~dp0\backend"
if not exist "..\.venv\Scripts\python.exe" (
    echo Error: Virtual environment .venv\Scripts\python.exe not found in project root folder.
    pause
    exit /b
)

start "Code Complexity Backend" /min cmd /c "..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000"
echo Server starting in background...

echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul
echo.

echo [3/3] Opening App in Browser...
start "" "http://127.0.0.1:8000/"

echo.
echo ==============================================
echo   Done! App is running at:
echo   http://127.0.0.1:8000/
echo   (Keep this window open)
echo ==============================================
timeout /t 5 >nul
