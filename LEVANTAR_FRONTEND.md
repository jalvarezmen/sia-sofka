# 🚀 Cómo Levantar el Frontend en Docker

## ⚠️ IMPORTANTE: Ejecutar desde la RAIZ del proyecto

El `docker-compose.yml` está en la **raíz** del proyecto, NO en el directorio `backend`.

## 📋 Pasos para Levantar el Frontend

### 1. Ir a la raíz del proyecto

```bash
# Si estás en backend/, sube un nivel
cd ..

# O desde cualquier lugar, ve a la raíz
cd C:\Users\USER\Documents\sia-sofka
```

### 2. Verificar que el docker-compose.yml esté en la raíz

```bash
# Debe existir este archivo:
# C:\Users\USER\Documents\sia-sofka\docker-compose.yml
```

### 3. Levantar solo el frontend

```bash
docker-compose up -d --build frontend
```

### 4. Levantar todos los servicios (recomendado)

```bash
docker-compose up -d --build
```

Esto levantará:
- ✅ Base de datos (db)
- ✅ API Backend (api)
- ✅ Frontend (frontend)

## 🔍 Verificar que Funciona

### Ver logs del frontend

```bash
docker-compose logs -f frontend
```

Deberías ver algo como:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3000/
➜  Network: http://0.0.0.0:3000/
```

### Verificar estado de los servicios

```bash
docker-compose ps
```

Todos los servicios deben estar "Up".

### Acceder al frontend

Abre en tu navegador:
```
http://localhost:3000
```

## 🛠️ Solución de Problemas

### Error: "no such service: frontend"

**Causa**: Estás ejecutando desde el directorio `backend/` en lugar de la raíz.

**Solución**:
```bash
# Ve a la raíz del proyecto
cd C:\Users\USER\Documents\sia-sofka

# Luego ejecuta
docker-compose up -d --build frontend
```

### Error: "Cannot find module"

**Solución**: Reconstruir el contenedor
```bash
docker-compose down frontend
docker-compose up -d --build frontend
```

### El frontend no se conecta a la API

**Verificar**:
1. Que la API esté corriendo: `docker-compose ps api`
2. Que la API responda: `curl http://localhost:8000/health`
3. Los logs del frontend: `docker-compose logs frontend`

### Hot-reload no funciona

El hot-reload está configurado con `CHOKIDAR_USEPOLLING=true`. Si no funciona:
1. Verifica que el volumen esté montado correctamente
2. Reconstruye el contenedor: `docker-compose up -d --build frontend`

## 📝 Comandos Útiles

```bash
# Ver logs en tiempo real
docker-compose logs -f frontend

# Detener el frontend
docker-compose stop frontend

# Reiniciar el frontend
docker-compose restart frontend

# Eliminar y recrear el frontend
docker-compose up -d --force-recreate --build frontend

# Ver todos los servicios
docker-compose ps
```

## 🌐 URLs

- **Frontend**: http://localhost:3000
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

