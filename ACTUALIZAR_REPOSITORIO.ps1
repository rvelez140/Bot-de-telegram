# Script de Actualización Automática
# Ejecuta este archivo en PowerShell

Write-Host "🚀 Actualizando Bot de Telegram..." -ForegroundColor Green
Write-Host ""

# Verificar que estamos en el directorio correcto
if (-not (Test-Path "bot.py")) {
    Write-Host "❌ Error: No estás en el directorio del proyecto" -ForegroundColor Red
    Write-Host "Ejecuta: cd 'C:\Users\Antuan Velez\VSCODE PROYECTO\Bot-de-telegram'" -ForegroundColor Yellow
    exit
}

Write-Host "📥 Descargando archivos actualizados..." -ForegroundColor Cyan

# URLs de los archivos actualizados en GitHub (raw)
$baseUrl = "https://raw.githubusercontent.com/rvelez140/Bot-de-telegram/main"

# Lista de archivos a actualizar
$files = @(
    "bot.py",
    "requirements.txt",
    "Dockerfile",
    ".gitignore"
)

# Descargar cada archivo
foreach ($file in $files) {
    Write-Host "  Descargando $file..." -ForegroundColor Gray
    try {
        # Hacer backup
        if (Test-Path $file) {
            Copy-Item $file "$file.backup" -Force
        }
        
        # Aquí deberías copiar manualmente o usar los archivos que te proporcioné
        Write-Host "  ✅ $file respaldado" -ForegroundColor Green
    }
    catch {
        Write-Host "  ⚠️ No se pudo respaldar $file" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "📝 Archivos listos para actualizar:" -ForegroundColor Cyan
Write-Host "  - bot.py (soporte para cookies y mejoras)" -ForegroundColor White
Write-Host "  - requirements.txt (yt-dlp actualizado)" -ForegroundColor White
Write-Host "  - Dockerfile (soporte de cookies)" -ForegroundColor White
Write-Host "  - .gitignore (protección de cookies)" -ForegroundColor White
Write-Host "  - .github/workflows/deploy.yml (CI/CD nuevo)" -ForegroundColor White
Write-Host ""

Write-Host "📚 Documentación nueva a agregar:" -ForegroundColor Cyan
Write-Host "  - CI_CD_GITHUB_ACTIONS.md" -ForegroundColor White
Write-Host "  - SETUP_SSH_RAPIDO.md" -ForegroundColor White
Write-Host "  - CONFIGURAR_COOKIES.md" -ForegroundColor White
Write-Host "  - ACTUALIZACION_RAPIDA.md" -ForegroundColor White
Write-Host ""

Write-Host "⚠️  IMPORTANTE:" -ForegroundColor Yellow
Write-Host "1. Extrae telegram_downloader_bot.tar.gz que descargaste" -ForegroundColor White
Write-Host "2. Copia los archivos de telegram_downloader_bot/ a este directorio" -ForegroundColor White
Write-Host "3. Luego ejecuta los comandos de abajo" -ForegroundColor White
Write-Host ""

Write-Host "📤 Comandos para subir a GitHub:" -ForegroundColor Green
Write-Host ""
Write-Host "git add ." -ForegroundColor Cyan
Write-Host 'git commit -m "Agregar CI/CD automático, soporte cuentas privadas y mejoras"' -ForegroundColor Cyan
Write-Host "git push" -ForegroundColor Cyan
Write-Host ""

Write-Host "✅ Sigue las instrucciones de arriba para completar la actualización" -ForegroundColor Green
