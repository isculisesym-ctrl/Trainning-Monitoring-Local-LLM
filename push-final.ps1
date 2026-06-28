# Push final rapido
$username = "isculisesym-ctrl"
Write-Host "Push al repo: AI-Platform-Local"

# Pedir token una sola vez
$token = Read-Host "Pega tu token (ghp_...)"

$authUrl = "https://${username}:${token}@github.com/$username/AI-Platform-Local.git"

Write-Host "Haciendo push..."
& git push -u $authUrl master

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nEXITO! Cambios en GitHub" -ForegroundColor Green
} else {
    Write-Host "`nError" -ForegroundColor Red
}
