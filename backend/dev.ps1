# SIA SOFKA U - Scripts de Desarrollo
# Uso: .\dev.ps1 <comando>

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

function Show-Help {
    Write-Host "=== SIA SOFKA U - Comandos de Desarrollo ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Instalación:" -ForegroundColor Yellow
    Write-Host "  install          - Instalar dependencias de producción"
    Write-Host "  install-dev      - Instalar dependencias de desarrollo"
    Write-Host ""
    Write-Host "Testing:" -ForegroundColor Yellow
    Write-Host "  test             - Ejecutar pruebas"
    Write-Host "  test-cov         - Ejecutar pruebas con cobertura"
    Write-Host "  test-unit        - Ejecutar solo pruebas unitarias"
    Write-Host "  test-integration - Ejecutar solo pruebas de integración"
    Write-Host ""
    Write-Host "Calidad de Código:" -ForegroundColor Yellow
    Write-Host "  lint             - Ejecutar flake8"
    Write-Host "  format           - Formatear código con black e isort"
    Write-Host "  format-check     - Verificar formateo sin modificar"
    Write-Host "  type-check       - Verificar tipos con mypy"
    Write-Host "  quality          - Ejecutar todas las verificaciones"
    Write-Host ""
    Write-Host "Docker:" -ForegroundColor Yellow
    Write-Host "  docker-up        - Levantar servicios"
    Write-Host "  docker-down      - Detener servicios"
    Write-Host "  docker-logs      - Ver logs"
    Write-Host "  docker-build     - Construir imagen"
    Write-Host ""
    Write-Host "Base de Datos:" -ForegroundColor Yellow
    Write-Host "  migrate          - Ejecutar migraciones"
    Write-Host "  migrate-create   - Crear nueva migración"
    Write-Host ""
    Write-Host "Aplicación:" -ForegroundColor Yellow
    Write-Host "  run              - Ejecutar en desarrollo"
    Write-Host "  run-prod         - Ejecutar en producción"
    Write-Host ""
    Write-Host "Utilidades:" -ForegroundColor Yellow
    Write-Host "  clean            - Limpiar archivos temporales"
    Write-Host "  pre-commit       - Ejecutar pre-commit en todos los archivos"
    Write-Host "  ci               - Simular pipeline de CI localmente"
    Write-Host ""
}

function Install-Dependencies {
    Write-Host "📦 Instalando dependencias de producción..." -ForegroundColor Green
    pip install -r requirements.txt
}

function Install-DevDependencies {
    Write-Host "📦 Instalando todas las dependencias..." -ForegroundColor Green
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
    Write-Host "🔧 Configurando pre-commit hooks..." -ForegroundColor Green
    pre-commit install
}

function Run-Tests {
    Write-Host "🧪 Ejecutando pruebas..." -ForegroundColor Green
    $env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    $env:DATABASE_URL_SYNC = "sqlite:///:memory:"
    $env:SECRET_KEY = "test-secret-key-for-development-only"
    pytest -v --ignore=tests/integration/test_api.py
}

function Run-TestsWithCoverage {
    Write-Host "🧪 Ejecutando pruebas con cobertura..." -ForegroundColor Green
    $env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    $env:DATABASE_URL_SYNC = "sqlite:///:memory:"
    $env:SECRET_KEY = "test-secret-key-for-development-only"
    pytest --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml --ignore=tests/integration/test_api.py
    Write-Host "📊 Reporte HTML generado en htmlcov/index.html" -ForegroundColor Cyan
}

function Run-UnitTests {
    Write-Host "🧪 Ejecutando pruebas unitarias..." -ForegroundColor Green
    $env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    $env:DATABASE_URL_SYNC = "sqlite:///:memory:"
    $env:SECRET_KEY = "test-secret-key-for-development-only"
    pytest tests/unit/ -v
}

function Run-IntegrationTests {
    Write-Host "🧪 Ejecutando pruebas de integración..." -ForegroundColor Green
    $env:DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    $env:DATABASE_URL_SYNC = "sqlite:///:memory:"
    $env:SECRET_KEY = "test-secret-key-for-development-only"
    pytest tests/integration/ -v --ignore=tests/integration/test_api.py
}

function Run-Lint {
    Write-Host "🔍 Ejecutando flake8..." -ForegroundColor Green
    flake8 app tests
}

function Run-Format {
    Write-Host "✨ Formateando código..." -ForegroundColor Green
    black app tests
    isort app tests
}

function Run-FormatCheck {
    Write-Host "✅ Verificando formato..." -ForegroundColor Green
    black --check app tests
    isort --check app tests
}

function Run-TypeCheck {
    Write-Host "🔎 Verificando tipos..." -ForegroundColor Green
    mypy app
}

function Run-Quality {
    Write-Host "🎯 Ejecutando todas las verificaciones de calidad..." -ForegroundColor Green
    Run-FormatCheck
    Run-Lint
    Run-TypeCheck
    Run-TestsWithCoverage
    Write-Host "✅ Todas las verificaciones pasaron exitosamente" -ForegroundColor Green
}

function Clean-Temp {
    Write-Host "🧹 Limpiando archivos temporales..." -ForegroundColor Green
    Get-ChildItem -Path . -Include __pycache__,*.pyc,*.pyo,.pytest_cache,.mypy_cache,htmlcov,*.egg-info -Recurse -Force | Remove-Item -Recurse -Force
    if (Test-Path coverage.xml) { Remove-Item coverage.xml }
    if (Test-Path .coverage) { Remove-Item .coverage }
}

function Docker-Up {
    Write-Host "🐳 Levantando servicios Docker..." -ForegroundColor Green
    docker-compose up -d
}

function Docker-Down {
    Write-Host "🐳 Deteniendo servicios Docker..." -ForegroundColor Green
    docker-compose down
}

function Docker-Logs {
    Write-Host "📋 Mostrando logs de Docker..." -ForegroundColor Green
    docker-compose logs -f api
}

function Docker-Build {
    Write-Host "🔨 Construyendo imagen Docker..." -ForegroundColor Green
    docker-compose build
}

function Run-Migrate {
    Write-Host "🔄 Ejecutando migraciones..." -ForegroundColor Green
    alembic upgrade head
}

function Create-Migration {
    $message = Read-Host "Ingrese descripción de la migración"
    Write-Host "📝 Creando migración: $message" -ForegroundColor Green
    alembic revision --autogenerate -m "$message"
}

function Run-App {
    Write-Host "🚀 Ejecutando aplicación en modo desarrollo..." -ForegroundColor Green
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
}

function Run-AppProd {
    Write-Host "🚀 Ejecutando aplicación en modo producción..." -ForegroundColor Green
    uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
}

function Run-PreCommit {
    Write-Host "🔧 Ejecutando pre-commit en todos los archivos..." -ForegroundColor Green
    pre-commit run --all-files
}

function Run-CI {
    Write-Host "🔄 Simulando pipeline de CI localmente..." -ForegroundColor Green
    Run-Quality
    Write-Host "✅ Pipeline de CI completado exitosamente" -ForegroundColor Green
}

# Ejecutar comando
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "install" { Install-Dependencies }
    "install-dev" { Install-DevDependencies }
    "test" { Run-Tests }
    "test-cov" { Run-TestsWithCoverage }
    "test-unit" { Run-UnitTests }
    "test-integration" { Run-IntegrationTests }
    "lint" { Run-Lint }
    "format" { Run-Format }
    "format-check" { Run-FormatCheck }
    "type-check" { Run-TypeCheck }
    "quality" { Run-Quality }
    "clean" { Clean-Temp }
    "docker-up" { Docker-Up }
    "docker-down" { Docker-Down }
    "docker-logs" { Docker-Logs }
    "docker-build" { Docker-Build }
    "migrate" { Run-Migrate }
    "migrate-create" { Create-Migration }
    "run" { Run-App }
    "run-prod" { Run-AppProd }
    "pre-commit" { Run-PreCommit }
    "ci" { Run-CI }
    default {
        Write-Host "❌ Comando no reconocido: $Command" -ForegroundColor Red
        Write-Host ""
        Show-Help
    }
}
