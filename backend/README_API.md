# Guía para Verificar que la API está Funcionando

## 1. Levantar el Servicio con Docker

### Paso 1: Ir al directorio backend
```bash
cd backend
```

### Paso 2: Levantar los servicios
```bash
docker-compose up -d
```

Esto levantará:
- **PostgreSQL** en el puerto 5432
- **FastAPI** en el puerto 8000

### Paso 3: Verificar que los contenedores están corriendo
```bash
docker-compose ps
```

Deberías ver dos contenedores:
- `sia_sofka_db` (PostgreSQL)
- `sia_sofka_api` (FastAPI)

### Paso 4: Ver los logs
```bash
docker-compose logs -f api
```

## 2. Verificar que la API está Funcionando

### Opción A: Usar el script de prueba (Recomendado)

```bash
# Instalar requests si no lo tienes
pip install requests

# Ejecutar el script de prueba
python test_api.py
```

### Opción B: Probar manualmente

#### 1. Health Check
```bash
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "healthy"}
```

#### 2. Endpoint Raíz
```bash
curl http://localhost:8000/
```

Respuesta esperada:
```json
{
  "message": "Welcome to SIA SOFKA U",
  "version": "1.0.0",
  "docs": "/docs"
}
```

#### 3. Documentación Interactiva
Abre en tu navegador:
```
http://localhost:8000/docs
```

Aquí podrás:
- Ver todos los endpoints disponibles
- Probar los endpoints directamente desde el navegador
- Ver los schemas de request/response

#### 4. Documentación Alternativa (ReDoc)
```
http://localhost:8000/redoc
```

## 3. Probar Endpoints de la API

### Crear un Usuario Administrador

Primero necesitas crear un usuario administrador. Puedes hacerlo directamente en la base de datos o usando el endpoint de registro (si ya tienes un admin).

#### Opción 1: Usando Python (Recomendado)

Crea un script `create_admin.py`:

```python
import asyncio
from app.core.database import AsyncSessionLocal
from app.models.user import User, UserRole
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash
from datetime import date

async def create_admin():
    async with AsyncSessionLocal() as session:
        codigo = await generar_codigo_institucional(session, "Admin")
        admin = User(
            email="admin@sofka.edu.co",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            nombre="Administrador",
            apellido="Sistema",
            codigo_institucional=codigo,
            fecha_nacimiento=date(1980, 1, 1),
        )
        session.add(admin)
        await session.commit()
        print(f"Admin creado: {admin.email}")

asyncio.run(create_admin())
```

Ejecuta:
```bash
python create_admin.py
```

#### Opción 2: Usando la Documentación Interactiva

1. Ve a http://localhost:8000/docs
2. Busca el endpoint `POST /api/v1/auth/register`
3. Necesitarás un token de admin (si ya existe uno)

### Probar Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sofka.edu.co&password=admin123"
```

Respuesta esperada:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Probar Endpoints Protegidos

Usa el token obtenido del login:

```bash
TOKEN="tu_token_aqui"

# Obtener información del usuario actual
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

## 4. Verificar desde el Navegador

### Documentación Interactiva (Swagger UI)
```
http://localhost:8000/docs
```

Aquí puedes:
- Ver todos los endpoints
- Probar cada endpoint directamente
- Ver ejemplos de request/response
- Autenticarte y probar endpoints protegidos

### Documentación Alternativa (ReDoc)
```
http://localhost:8000/redoc
```

## 5. Verificar Estado de los Servicios

### Ver logs en tiempo real
```bash
docker-compose logs -f api
```

### Verificar estado de los contenedores
```bash
docker-compose ps
```

### Verificar salud de la base de datos
```bash
docker-compose exec db pg_isready -U postgres
```

## 6. Detener los Servicios

```bash
docker-compose down
```

Para detener y eliminar los volúmenes:
```bash
docker-compose down -v
```

## 7. Solución de Problemas

### El servicio no inicia
1. Verifica los logs: `docker-compose logs api`
2. Verifica que el puerto 8000 no esté en uso
3. Verifica que PostgreSQL esté corriendo: `docker-compose ps`

### Error de conexión a la base de datos
1. Verifica que el contenedor de DB esté corriendo
2. Verifica las variables de entorno en `docker-compose.yml`
3. Espera unos segundos para que la DB esté lista

### Error 500 en los endpoints
1. Verifica los logs: `docker-compose logs -f api`
2. Verifica que las migraciones se hayan ejecutado
3. Verifica que la base de datos tenga las tablas creadas

## Endpoints Principales

- `GET /` - Endpoint raíz
- `GET /health` - Health check
- `GET /docs` - Documentación interactiva
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro (solo Admin)
- `GET /api/v1/auth/me` - Usuario actual
- `GET /api/v1/users` - Listar usuarios (Admin)
- `POST /api/v1/users` - Crear usuario (Admin)
- `GET /api/v1/subjects` - Listar materias (Admin)
- `GET /api/v1/grades` - Listar notas
- `GET /api/v1/reports/student/{id}` - Generar reporte de estudiante

