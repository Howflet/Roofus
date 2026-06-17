@echo off
REM ============================================================
REM  Roofus Hapeville - one-click launcher
REM  Starts the backend API + frontend map, then opens browser.
REM ============================================================
cd /d "%~dp0"

set PY=.venv\Scripts\python.exe

if not exist "%PY%" (
  echo [ERROR] Virtual environment not found at %PY%
  echo Run setup first:  py -m venv .venv  ^&^&  .venv\Scripts\python -m pip install -r backend\requirements.txt
  pause
  exit /b 1
)

echo Starting backend API on http://localhost:8000 ...
start "Roofus Backend" "%PY%" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000

echo Starting frontend on http://localhost:5173 ...
start "Roofus Frontend" "%PY%" -m http.server 5173 --directory frontend

echo Waiting for servers to warm up ...
timeout /t 3 /nobreak >nul

echo Opening browser ...
start "" "http://localhost:5173"

echo.
echo ============================================================
echo  Roofus is running!
echo    App:      http://localhost:5173
echo    API docs: http://localhost:8000/docs
echo.
echo  Two server windows just opened. To STOP everything,
echo  close those two windows (or press Ctrl+C in each).
echo ============================================================
echo.
pause
