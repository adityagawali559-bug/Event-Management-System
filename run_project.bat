@echo off
title Community Event Management and Participation System (CEMPS)
echo =====================================================================
echo  Community Event Management and Participation System (CEMPS)
echo  College Community Engagement Project (CEP)
echo =====================================================================
echo.

cd /d "%~dp0\backend"

if not exist "venv\Scripts\python.exe" (
    echo [1/3] Creating Python virtual environment...
    python -m venv venv
    echo [2/3] Installing dependencies...
    venv\Scripts\pip.exe install -r requirements.txt
) else (
    echo [*] Python virtual environment detected.
)

echo [*] Initializing database and running sample data seeder...
venv\Scripts\python.exe seed.py

echo.
echo =====================================================================
echo  Server starting on: http://127.0.0.1:8000
echo  API Documentation:  http://127.0.0.1:8000/docs
echo =====================================================================
echo.

start http://127.0.0.1:8000
venv\Scripts\uvicorn.exe app.main:app --host 127.0.0.1 --port 8000 --reload

pause
