@echo off
REM Start the whole tool with one command: builds the frontend if needed,
REM then serves it and the API from a single backend process on port 8000.
setlocal
cd /d "%~dp0"
if "%INFRA_MONITOR_PORT%"=="" set INFRA_MONITOR_PORT=8000

if not exist "backend\.venv" (
    echo Creating the Python environment...
    python -m venv backend\.venv || goto :fail
    backend\.venv\Scripts\python.exe -m pip install --quiet -r backend\requirements.txt || goto :fail
)

if not exist "frontend\dist" (
    echo Building the frontend...
    pushd frontend
    if not exist "node_modules" call npm install || goto :fail
    call npm run build || goto :fail
    popd
)

echo.
echo Infrastructure Monitor is starting on http://localhost:%INFRA_MONITOR_PORT%
echo Press Ctrl+C to stop.
echo.
cd backend
..\backend\.venv\Scripts\python.exe -m uvicorn src.main:app --port %INFRA_MONITOR_PORT%
goto :eof

:fail
echo.
echo Startup failed. See the messages above.
exit /b 1
