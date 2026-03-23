@echo off
setlocal
echo ==============================================
echo   Code Complexity Analyzer - Startup
echo ==============================================
echo.

echo [1/3] Cleaning up any old instances on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "') do (
    if "%%a" neq "0" (
        echo Found hanging process PID: %%a - terminating...
        taskkill /F /PID %%a >nul 2>&1
    )
)
echo Done.
echo.

echo [2/3] Starting Django Backend Server...
cd /d "%~dp0\backend"
if not exist ".venv\Scripts\activate.bat" (
    echo Error: Virtual environment .venv not found in backend folder.
    pause
    exit /b
)

:: Start the server in a new minimized window
start "Code Complexity Backend" /min cmd /c "call .venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8000"
echo Server starting in background...

echo Waiting for server to initialize...
timeout /t 3 /nobreak >nul
echo.

echo [3/3] Opening Frontend Website...
cd /d "%~dp0"
start "" "index.html"

echo.
echo ==============================================
echo   Done! Your website should now be open.
echo   Keep the minimized console window open
echo   to keep the backend running.
echo ==============================================
timeout /t 5 >nul
