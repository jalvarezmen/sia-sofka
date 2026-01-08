# 🐳 Configuración Docker - SIA SOFKA U

## Estructura de Servicios

El proyecto incluye tres servicios Docker:

1. **db** - PostgreSQL (puerto 5432)
2. **api** - FastAPI Backend (puerto 8000)
3. **frontend** - React Frontend (puerto 3000)

## 🚀 Levantar todos los servicios

Desde la raíz del proyecto:

```bash
docker-compose up -d
```

Esto levantará:
- Base de datos PostgreSQL
- API Backend (FastAPI)
- Frontend (React con Vite)

## 📋 Comandos Útiles

### Ver logs de todos los servicios
```bash
docker-compose logs -f
```

### Ver logs de un servicio específico
```bash
docker-compose logs -f api
docker-compose logs -f frontend
docker-compose logs -f db
```

### Detener todos los servicios
```bash
docker-compose down
```

### Detener y eliminar volúmenes (⚠️ borra la BD)
```bash
docker-compose down -v
```

### Reconstruir un servicio específico
```bash
docker-compose up -d --build frontend
docker-compose up -d --build api
```

### Reconstruir todos los servicios
```bash
docker-compose up -d --build
```

### Ver estado de los servicios
```bash
docker-compose ps
```

## 🔧 Configuración

### Variables de Entorno

#### Backend (API)
Las variables están definidas en `docker-compose.yml`:
- `DATABASE_URL` - URL de conexión a PostgreSQL
- `SECRET_KEY` - Clave secreta para JWT
- `DEBUG` - Modo debug

#### Frontend
- `VITE_API_BASE_URL` - URL base de la API (configurada automáticamente)

### Puertos

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **PostgreSQL**: localhost:5432
- **API Docs**: http://localhost:8000/docs

## 🛠️ Desarrollo

### Modo Desarrollo

El frontend está configurado con hot-reload:
- Los cambios en el código se reflejan automáticamente
- No necesitas reconstruir el contenedor

### Crear Usuario Administrador

```bash
docker-compose exec api python create_admin.py
```

Esto creará un admin con:
- Email: `admin@sofka.edu.co`
- Password: `admin123`

## 🏗️ Build de Producción

Para producción, usa el Dockerfile de producción:

```bash
# En docker-compose.yml, cambiar:
# dockerfile: Dockerfile
# por:
# dockerfile: Dockerfile.prod
```

O crear un `docker-compose.prod.yml`:

```bash
docker-compose -f docker-compose.prod.yml up -d
```

## 🔍 Solución de Problemas

### El frontend no se conecta a la API

1. Verifica que la API esté corriendo:
   ```bash
   docker-compose ps api
   ```

2. Verifica los logs:
   ```bash
   docker-compose logs api
   ```

3. Verifica la URL en `frontend/src/config/constants.js`

### El frontend no carga

1. Verifica los logs:
   ```bash
   docker-compose logs frontend
   ```

2. Reconstruye el contenedor:
   ```bash
   docker-compose up -d --build frontend
   ```

### Error de permisos en Docker

En Linux/Mac, puede ser necesario:
```bash
sudo docker-compose up -d
```

## 📝 Notas

- El frontend usa hot-reload en desarrollo
- Los cambios en el código se reflejan sin reconstruir
- La base de datos persiste en un volumen Docker
- Los servicios se comunican a través de la red `sia_sofka_network`

