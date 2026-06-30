# Local Development Setup Script for Windows
# Run in PowerShell as Administrator (or at least with appropriate permissions)

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Training Dashboard - Local Setup (Windows)" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Create required directories
if (-not (Test-Path "data\logs")) {
    New-Item -ItemType Directory -Path "data\logs" -Force | Out-Null
}
if (-not (Test-Path "tests")) {
    New-Item -ItemType Directory -Path "tests" -Force | Out-Null
}
Write-Host "✓ Required directories created" -ForegroundColor Green

# Create local config if needed
if (-not (Test-Path ".env.local")) {
    @"
# Local development configuration
DEBUG=true
LOG_LEVEL=INFO
DASHBOARD_PORT=3000
"@ | Out-File -Encoding UTF8 ".env.local"
    Write-Host "✓ Created .env.local (add your local secrets here)" -ForegroundColor Green
}

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Setup complete!" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. You are already in the virtual environment"
Write-Host ""
Write-Host "  2. Start dashboard (Terminal 1):"
Write-Host "     python src\server\app.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  3. Run example (Terminal 2, activate venv first):"
Write-Host "     .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "     python community\examples\training_simulator.py" -ForegroundColor Cyan
Write-Host ""
Write-Host "  4. Open dashboard:"
Write-Host "     http://localhost:3000" -ForegroundColor Cyan
Write-Host ""
