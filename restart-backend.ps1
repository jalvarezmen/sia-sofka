# Script para reiniciar el backend de SIA SOFKA U
Write-Host "🔄 Reiniciando backend..." -ForegroundColor Yellow

# Encontrar y detener procesos Python relacionados con uvicorn
$pythonProcesses = Get-Process python -ErrorAction SilentlyContinue | Where-Object {
    $_.Id -in @(35536, 36652) -or 
    ($_.CommandLine -like "*uvicorn*") -or 
    ($_.CommandLine -like "*app.main*")
}

if ($pythonProcesses) {
    Write-Host "Deteniendo procesos del backend..." -ForegroundColor Cyan
    foreach ($proc in $pythonProcesses) {
        Write-Host "  - Deteniendo PID $($proc.Id)" -ForegroundColor Gray
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
    Start-Sleep -Seconds 2
    Write-Host "✅ Procesos detenidos" -ForegroundColor Green
} else {
    Write-Host "ℹ️  No se encontraron procesos del backend corriendo" -ForegroundColor Yellow
}

# Navegar al directorio del backend
Set-Location "$PSScriptRoot\backend"

Write-Host ""
Write-Host "🚀 Iniciando backend en modo desarrollo..." -ForegroundColor Green
Write-Host "   URL: http://localhost:8000" -ForegroundColor Cyan
Write-Host "   Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "Presiona Ctrl+C para detener el servidor" -ForegroundColor Yellow
Write-Host ""

# Iniciar uvicorn en modo desarrollo
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
