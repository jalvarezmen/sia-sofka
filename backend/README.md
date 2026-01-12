# SIA SOFKA U - Backend

[![CI Pipeline](https://github.com/YOUR_USERNAME/sia-sofka/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/sia-sofka/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Coverage](https://img.shields.io/badge/coverage-80%25+-green.svg)](https://github.com/YOUR_USERNAME/sia-sofka)

Sistema de Información Académica SOFKA U - Backend API

## Configuración

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```env
# Database Configuration
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/sia_sofka_db
DATABASE_URL_SYNC=postgresql://postgres:postgres@db:5432/sia_sofka_db

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Application
APP_NAME=SIA SOFKA U
APP_VERSION=1.0.0
DEBUG=True

# Server
HOST=0.0.0.0
PORT=8000
```

## Docker

### Levantar el servicio

```bash
docker-compose up -d
```

### Ver logs

```bash
docker-compose logs -f api
```

### Detener el servicio

```bash
docker-compose down
```

## Desarrollo Local

### Instalar dependencias

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Configurar pre-commit hooks (opcional)

```bash
pip install pre-commit
pre-commit install
```

### Ejecutar migraciones

```bash
alembic upgrade head
```

### Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

## Testing

### Ejecutar todas las pruebas

```bash
pytest
```

### Ejecutar pruebas con cobertura

```bash
pytest --cov=app --cov-report=html --cov-report=term-missing
```

### Ver reporte de cobertura en HTML

```bash
# El reporte se genera en htmlcov/index.html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

## Calidad de Código

### Formatear código con black

```bash
black app tests
```

### Verificar código con flake8

```bash
flake8 app tests
```

### Type checking con mypy

```bash
mypy app
```

### Ejecutar todas las verificaciones de calidad

```bash
black --check app tests && flake8 app tests && mypy app && pytest --cov=app
```

## 🛠️ Scripts de Desarrollo

Para facilitar el desarrollo, se incluyen scripts auxiliares:

### Linux/macOS - Makefile

```bash
# Ver todos los comandos disponibles
make help

# Instalar dependencias de desarrollo
make install-dev

# Ejecutar pruebas con cobertura
make test-cov

# Ejecutar todas las verificaciones de calidad
make quality

# Simular pipeline de CI localmente
make ci
```

### Windows - PowerShell

```powershell
# Ver todos los comandos disponibles
.\dev.ps1 help

# Instalar dependencias de desarrollo
.\dev.ps1 install-dev

# Ejecutar pruebas con cobertura
.\dev.ps1 test-cov

# Ejecutar todas las verificaciones de calidad
.\dev.ps1 quality

# Simular pipeline de CI localmente
.\dev.ps1 ci
```

## 📊 CI/CD

El proyecto utiliza **GitHub Actions** para automatizar:
- Linting y formateo de código
- Type checking
- Ejecución de pruebas
- Verificación de cobertura (mínimo 80%)
- Build de imagen Docker

Ver [CI_CD.md](CI_CD.md) para más detalles sobre el pipeline.

## Estructura del Proyecto

```
backend/
├── app/
│   ├── api/           # API endpoints
│   ├── core/          # Configuración core
│   ├── models/        # Modelos SQLAlchemy
│   ├── schemas/       # Schemas Pydantic
│   ├── services/      # Lógica de negocio
│   ├── repositories/  # Acceso a datos
│   └── factories/     # Factory patterns
├── tests/             # Pruebas
└── alembic/           # Migraciones


