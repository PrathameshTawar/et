# SatyaSetu Setup Script for Windows
# PowerShell script to set up the development environment

param(
    [string]$Environment = "development"
)

Write-Host "🚀 Setting up SatyaSetu environment: $Environment" -ForegroundColor Green

# Check prerequisites
Write-Host "🔍 Checking prerequisites..." -ForegroundColor Yellow

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.9+" -ForegroundColor Red
    exit 1
}

# Check Node.js
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✅ Node.js found: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Node.js not found. Please install Node.js 18+" -ForegroundColor Red
    exit 1
}

# Check Docker (optional)
try {
    $dockerVersion = docker --version 2>&1
    Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
    $hasDocker = $true
} catch {
    Write-Host "⚠️ Docker not found. Docker deployment will not be available." -ForegroundColor Yellow
    $hasDocker = $false
}

# Setup backend
Write-Host "🔧 Setting up backend..." -ForegroundColor Yellow

Set-Location backend

# Create virtual environment
if (!(Test-Path "venv")) {
    Write-Host "📦 Creating Python virtual environment..." -ForegroundColor Cyan
    python -m venv venv
}

# Activate virtual environment
Write-Host "🔌 Activating virtual environment..." -ForegroundColor Cyan
& "venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "📥 Installing Python dependencies..." -ForegroundColor Cyan
pip install -r requirements.txt

# Setup environment file
if (!(Test-Path ".env")) {
    Write-Host "📝 Creating backend .env file..." -ForegroundColor Cyan
    Copy-Item ".env.example" ".env"
    Write-Host "⚠️ Please edit backend/.env with your API keys" -ForegroundColor Yellow
}

Set-Location ..

# Setup frontend
Write-Host "🔧 Setting up frontend..." -ForegroundColor Yellow

Set-Location frontend

# Install dependencies
Write-Host "📥 Installing Node.js dependencies..." -ForegroundColor Cyan
npm install

# Setup environment file
if (!(Test-Path ".env.local")) {
    Write-Host "📝 Creating frontend .env.local file..." -ForegroundColor Cyan
    Copy-Item ".env.local.example" ".env.local"
}

Set-Location ..

# Create startup scripts
Write-Host "📝 Creating startup scripts..." -ForegroundColor Yellow

# Backend startup script
@"
@echo off
echo Starting SatyaSetu Backend...
cd backend
call venv\Scripts\activate.bat
uvicorn main:app --reload --port 8000
pause
"@ | Out-File -FilePath "start-backend.bat" -Encoding ASCII

# Frontend startup script
@"
@echo off
echo Starting SatyaSetu Frontend...
cd frontend
npm run dev
pause
"@ | Out-File -FilePath "start-frontend.bat" -Encoding ASCII

# Combined startup script
@"
@echo off
echo Starting SatyaSetu (Full Stack)...
start "Backend" cmd /k "start-backend.bat"
timeout /t 5 /nobreak
start "Frontend" cmd /k "start-frontend.bat"
echo Both services are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
pause
"@ | Out-File -FilePath "start-all.bat" -Encoding ASCII

Write-Host "✅ Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "🚀 To start the application:" -ForegroundColor Cyan
Write-Host "   Full stack: .\start-all.bat" -ForegroundColor White
Write-Host "   Backend only: .\start-backend.bat" -ForegroundColor White
Write-Host "   Frontend only: .\start-frontend.bat" -ForegroundColor White
Write-Host ""
Write-Host "🌐 Application URLs:" -ForegroundColor Cyan
Write-Host "   Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor White
Write-Host "   API Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "⚠️ Important:" -ForegroundColor Yellow
Write-Host "   1. Edit backend/.env with your API keys" -ForegroundColor White
Write-Host "   2. Edit frontend/.env.local if needed" -ForegroundColor White

if ($hasDocker) {
    Write-Host ""
    Write-Host "🐳 Docker deployment:" -ForegroundColor Cyan
    Write-Host "   docker-compose up -d" -ForegroundColor White
}