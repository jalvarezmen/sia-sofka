# SIA SOFKA U - Backend

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

### Ejecutar migraciones

```bash
alembic upgrade head
```

### Ejecutar la aplicación

```bash
uvicorn app.main:app --reload
```

## Testing

```bash
pytest
```

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


