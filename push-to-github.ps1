# Push AI-Platform to GitHub
# Este script configura y hace push del repositorio a GitHub

Write-Host "`n" -ForegroundColor Cyan
Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        PUSH AI-PLATFORM A GITHUB (PRIVADO)                ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# Paso 1: Verificar que estamos en el repo correcto
Write-Host "✓ Verificando repositorio local..." -ForegroundColor Yellow
cd C:\Proyectos\AI-Platform

if (!(Test-Path ".git")) {
    Write-Host "❌ ERROR: No se encontró .git - no estamos en un repositorio Git" -ForegroundColor Red
    exit 1
}

Write-Host "✓ Repositorio Git encontrado en: $(Get-Location)" -ForegroundColor Green
Write-Host ""

# Paso 2: Mostrar estado actual
Write-Host "✓ Estado actual del repositorio:" -ForegroundColor Yellow
git status --short
Write-Host ""

Write-Host "✓ Commits locales:" -ForegroundColor Yellow
git log --oneline
Write-Host ""

# Paso 3: Pedir información de GitHub
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 1: Información de GitHub" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$username = Read-Host "Ingresa tu usuario de GitHub"
$confirm = Read-Host "¿El usuario es correcto? ($username) [S/n]"

if ($confirm -eq "n" -or $confirm -eq "N") {
    Write-Host "❌ Cancelado" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 2: Token de Autenticación" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Necesitas un GitHub Personal Access Token (PAT):" -ForegroundColor Yellow
Write-Host "  1. Ve a: https://github.com/settings/tokens" -ForegroundColor Gray
Write-Host "  2. Click: 'Generate new token (classic)'" -ForegroundColor Gray
Write-Host "  3. Nombre: 'AI-Platform-Local'" -ForegroundColor Gray
Write-Host "  4. Expiration: 90 days (o más)" -ForegroundColor Gray
Write-Host "  5. Scopes: Check 'repo'" -ForegroundColor Gray
Write-Host "  6. Click: 'Generate token'" -ForegroundColor Gray
Write-Host "  7. COPIA el token" -ForegroundColor Gray
Write-Host ""

$token = Read-Host "Pega tu GitHub Personal Access Token (se ocultará)"
Write-Host "(Token recibido)" -ForegroundColor Green
Write-Host ""

# Paso 3: Crear el repositorio remoto
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 3: Configurando Remote de GitHub" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

$repoUrl = "https://github.com/$username/AI-Platform.git"
Write-Host "URL del repositorio: $repoUrl" -ForegroundColor Yellow

# Verificar si el remote ya existe
$existingRemote = git remote get-url origin 2>$null

if ($existingRemote) {
    Write-Host "El remote 'origin' ya existe: $existingRemote" -ForegroundColor Yellow
    $overwrite = Read-Host "¿Deseas sobrescribir? [S/n]"

    if ($overwrite -ne "n" -and $overwrite -ne "N") {
        git remote remove origin
        Write-Host "✓ Remote anterior removido" -ForegroundColor Green
    } else {
        Write-Host "Usando remote existente" -ForegroundColor Yellow
    }
}

# Añadir el remote
git remote add origin $repoUrl
Write-Host "✓ Remote configurado" -ForegroundColor Green
Write-Host ""

# Paso 4: Configurar credenciales temporales
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "PASO 4: Configurando Autenticación" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Crear URL con credenciales
$authUrl = "https://${username}:${token}@github.com/$username/AI-Platform.git"

# Hacer push
Write-Host "Haciendo push de los commits a GitHub..." -ForegroundColor Yellow
Write-Host ""

try {
    # Intentar push con la URL autenticada
    git push -u $authUrl main 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ ÉXITO!" -ForegroundColor Green
        Write-Host ""
        Write-Host "╔════════════════════════════════════════════════════════════╗" -ForegroundColor Green
        Write-Host "║      REPOSITORIO SUBIDO A GITHUB EXITOSAMENTE             ║" -ForegroundColor Green
        Write-Host "╚════════════════════════════════════════════════════════════╝" -ForegroundColor Green
        Write-Host ""
        Write-Host "URL de tu repositorio (PRIVADO):" -ForegroundColor Cyan
        Write-Host "  https://github.com/$username/AI-Platform" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Próximos pasos:" -ForegroundColor Cyan
        Write-Host "  1. Verifica que sea PRIVADO en: https://github.com/$username/AI-Platform/settings" -ForegroundColor Gray
        Write-Host "  2. Empieza con: START_HERE.md" -ForegroundColor Gray
        Write-Host "  3. Sigue: INSTALLATION.md" -ForegroundColor Gray
        Write-Host ""
    } else {
        Write-Host "❌ ERROR durante el push" -ForegroundColor Red
        exit 1
    }

} catch {
    Write-Host "❌ ERROR: $_" -ForegroundColor Red
    exit 1
}

# Paso 5: Verificación
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "VERIFICACIÓN" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host "Git remote:" -ForegroundColor Yellow
git remote -v
Write-Host ""

Write-Host "Rama actual:" -ForegroundColor Yellow
git branch -v
Write-Host ""

Write-Host "✓ Todo completado!" -ForegroundColor Green
Write-Host ""
Write-Host "RECUERDA:" -ForegroundColor Yellow
Write-Host "  • Verifica que el repo es PRIVADO en GitHub Settings" -ForegroundColor Gray
Write-Host "  • Tu token no aparece en Git (está solo en memoria)" -ForegroundColor Gray
Write-Host "  • Para futuros pushes, usa: git push" -ForegroundColor Gray
Write-Host ""
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🚀 ¡Repositorio listo para el siguiente paso!" -ForegroundColor Cyan
Write-Host "═════════════════════════════════════════════════════════════" -ForegroundColor Cyan
