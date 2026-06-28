# Push AI-Platform a GitHub - Script Simple
Write-Host ""
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  PUSH AI-PLATFORM A GITHUB" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que estamos en el repo correcto
if (!(Test-Path ".git")) {
    Write-Host "ERROR: No se encontro .git" -ForegroundColor Red
    exit 1
}

Write-Host "OK: Repositorio Git encontrado" -ForegroundColor Green
Write-Host ""

# Pedir usuario
Write-Host "Tu usuario de GitHub:" -ForegroundColor Yellow
$username = Read-Host

# Pedir token
Write-Host ""
Write-Host "Tu GitHub Personal Access Token:" -ForegroundColor Yellow
Write-Host "(De: https://github.com/settings/tokens)" -ForegroundColor Gray
$token = Read-Host

Write-Host ""
Write-Host "Configurando..." -ForegroundColor Yellow

# Configurar remote
$repoUrl = "https://github.com/$username/AI-Platform-Local.git"

# Remover remote anterior si existe
git remote remove origin 2>$null

# Agregar nuevo remote
git remote add origin $repoUrl

Write-Host "OK: Remote configurado" -ForegroundColor Green

# Crear URL con credenciales para push
$authUrl = "https://${username}:${token}@github.com/$username/AI-Platform-Local.git"

Write-Host ""
Write-Host "Haciendo push a GitHub..." -ForegroundColor Yellow
Write-Host ""

# Hacer push
& git push -u $authUrl master

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  EXITO! Repositorio subido a GitHub" -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Write-Host ""

    Write-Host "Tu repositorio:" -ForegroundColor Cyan
    Write-Host "  https://github.com/$username/AI-Platform" -ForegroundColor Yellow
    Write-Host ""

    Write-Host "Proximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. Abre: START_HERE.md" -ForegroundColor Gray
    Write-Host "  2. Sigue: INSTALLATION.md" -ForegroundColor Gray
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "ERROR: Push fallido" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifica:" -ForegroundColor Yellow
    Write-Host "  - Usuario correcto" -ForegroundColor Gray
    Write-Host "  - Token valido" -ForegroundColor Gray
    Write-Host "  - Repo existe en GitHub" -ForegroundColor Gray
    Write-Host "  - Repo es PRIVADO" -ForegroundColor Gray
    Write-Host ""
}
