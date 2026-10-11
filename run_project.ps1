# CEMPS PowerShell Starter Script
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location -Path "$ScriptDir\backend"

Write-Host "=====================================================================" -ForegroundColor Cyan
Write-Host " Community Event Management and Participation System (CEMPS)" -ForegroundColor Green
Write-Host " College Community Engagement Project (CEP)" -ForegroundColor Cyan
Write-Host "=====================================================================" -ForegroundColor Cyan

if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[1/3] Creating Python virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[2/3] Installing dependencies..." -ForegroundColor Yellow
    & ".\venv\Scripts\pip.exe" install -r requirements.txt
}

Write-Host "[*] Initializing database and running sample data seeder..." -ForegroundColor Yellow
& ".\venv\Scripts\python.exe" seed.py

Write-Host "`nServer launching at: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "API Documentation:   http://127.0.0.1:8000/docs`n" -ForegroundColor Green

Start-Process "http://127.0.0.1:8000"
& ".\venv\Scripts\uvicorn.exe" app.main:app --host 127.0.0.1 --port 8000 --reload
