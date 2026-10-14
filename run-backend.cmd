@echo off
setlocal
cd /d "%~dp0backend"

echo Starting backend with uv...
uv run --python "%~dp0.venv\Scripts\python.exe" -m uvicorn src:app --host 127.0.0.1 --port 8000 --reload

if errorlevel 1 (
    echo.
    echo Backend stopped with an error.
    pause
)

endlocal
