# 📋 Lista Completa de Endpoints - SIA SOFKA U API

## Endpoints Públicos (Sin Autenticación)

### Raíz y Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/` | Información de la API |
| `GET` | `/health` | Health check del servicio |
| `GET` | `/docs` | Documentación Swagger UI |
| `GET` | `/redoc` | Documentación ReDoc |
| `GET` | `/openapi.json` | Schema OpenAPI |

### Autenticación

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/login` | Login de usuario | No |
| `POST` | `/api/v1/auth/register` | Registrar nuevo usuario | Admin |
| `GET` | `/api/v1/auth/me` | Obtener usuario actual | Sí |

---

## Endpoints de Usuarios (`/api/v1/users`)

**Requisito:** Solo Administradores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/users` | Crear nuevo usuario (Estudiante o Profesor) |
| `GET` | `/api/v1/users` | Listar todos los usuarios |
| `GET` | `/api/v1/users/{user_id}` | Obtener usuario por ID |
| `PUT` | `/api/v1/users/{user_id}` | Actualizar usuario |
| `DELETE` | `/api/v1/users/{user_id}` | Eliminar usuario |

**Ejemplo de creación:**
```json
{
  "email": "estudiante@example.com",
  "password": "password123",
  "nombre": "Juan",
  "apellido": "Pérez",
  "role": "Estudiante",
  "fecha_nacimiento": "2000-01-01",
  "programa_academico": "Ingeniería",
  "ciudad_residencia": "Bogotá"
}
```

---

## Endpoints de Materias (`/api/v1/subjects`)

**Requisito:** Solo Administradores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/subjects` | Crear nueva materia |
| `GET` | `/api/v1/subjects` | Listar todas las materias |
| `GET` | `/api/v1/subjects/{subject_id}` | Obtener materia por ID |
| `PUT` | `/api/v1/subjects/{subject_id}` | Actualizar materia |
| `DELETE` | `/api/v1/subjects/{subject_id}` | Eliminar materia |

**Ejemplo de creación:**
```json
{
  "nombre": "Matemáticas I",
  "codigo_institucional": "MAT-101",
  "numero_creditos": 3,
  "horario": "Lunes 8:00-10:00",
  "descripcion": "Fundamentos de matemáticas",
  "profesor_id": 1
}
```

---

## Endpoints de Inscripciones (`/api/v1/enrollments`)

**Requisito:** Solo Administradores

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/v1/enrollments` | Inscribir estudiante en materia |
| `GET` | `/api/v1/enrollments` | Listar todas las inscripciones |
| `GET` | `/api/v1/enrollments/{enrollment_id}` | Obtener inscripción por ID |
| `DELETE` | `/api/v1/enrollments/{enrollment_id}` | Eliminar inscripción |

**Ejemplo de creación:**
```json
{
  "estudiante_id": 1,
  "subject_id": 1
}
```

---

## Endpoints de Notas (`/api/v1/grades`)

### Crear y Obtener Notas

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/grades?subject_id={id}` | Crear nueva nota | Profesor o Admin |
| `GET` | `/api/v1/grades?subject_id={id}` | Obtener notas por materia | Sí |
| `GET` | `/api/v1/grades?enrollment_id={id}` | Obtener notas por inscripción | Sí |
| `GET` | `/api/v1/grades/{grade_id}` | Obtener nota por ID | Sí |

### Actualizar y Eliminar Notas

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `PUT` | `/api/v1/grades/{grade_id}` | Actualizar nota | Profesor o Admin |
| `DELETE` | `/api/v1/grades/{grade_id}` | Eliminar nota | Admin |

**Ejemplo de creación:**
```json
{
  "enrollment_id": 1,
  "nota": 4.5,
  "periodo": "2024-1",
  "fecha": "2024-03-15",
  "observaciones": "Buen desempeño"
}
```

**Notas sobre permisos:**
- **Estudiante**: Solo puede ver sus propias notas
- **Profesor**: Puede crear/actualizar notas solo en sus materias asignadas
- **Admin**: Puede crear/actualizar/eliminar cualquier nota

---

## Endpoints de Reportes (`/api/v1/reports`)

### Reporte de Estudiante

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/reports/student/{estudiante_id}?format={pdf\|html\|json}` | Reporte de estudiante | Admin |

**Formatos disponibles:**
- `json` - JSON con datos del reporte
- `pdf` - PDF descargable
- `html` - HTML descargable

### Reporte de Materia

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/reports/subject/{subject_id}?format={pdf\|html\|json}` | Reporte de materia | Profesor (solo sus materias) |

### Reporte General

| Método | Endpoint | Descripción | Autenticación |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/reports/general?format={pdf\|html\|json}` | Reporte general del estudiante | Estudiante (solo su propio reporte) |

**Ejemplos:**
```
GET /api/v1/reports/student/1?format=json
GET /api/v1/reports/subject/1?format=pdf
GET /api/v1/reports/general?format=html
```

---

## Endpoints de Perfil (`/api/v1/profile`)

**Requisito:** Usuario autenticado (cualquier rol)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/v1/profile` | Obtener perfil del usuario actual |
| `PUT` | `/api/v1/profile` | Actualizar perfil del usuario actual |

**Ejemplo de actualización:**
```json
{
  "nombre": "Nuevo Nombre",
  "numero_contacto": "1234567890",
  "programa_academico": "Nuevo Programa"
}
```

---

## Resumen por Rol

### 👤 Administrador
- ✅ Todos los endpoints de usuarios (CRUD)
- ✅ Todos los endpoints de materias (CRUD)
- ✅ Todos los endpoints de inscripciones (CRUD)
- ✅ Todos los endpoints de notas (CRUD)
- ✅ Generar reportes de estudiantes
- ✅ Gestionar su propio perfil

### 👨‍🏫 Profesor
- ✅ Ver materias asignadas
- ✅ Ver estudiantes de sus materias
- ✅ Crear/actualizar notas en sus materias
- ✅ Ver notas de sus materias
- ✅ Generar reportes de sus materias
- ✅ Gestionar su propio perfil

### 🎓 Estudiante
- ✅ Ver sus propias notas
- ✅ Ver materias en las que está inscrito
- ✅ Generar su reporte general
- ✅ Gestionar su propio perfil

---

## Autenticación

Todos los endpoints protegidos requieren un token JWT en el header:

```
Authorization: Bearer {token}
```

Para obtener el token:
1. Hacer login en `/api/v1/auth/login`
2. Copiar el `access_token` de la respuesta
3. Usarlo en el header `Authorization`

---

## Ejemplos de Uso

### 1. Login
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@sofka.edu.co&password=admin123"
```

### 2. Crear Usuario (como Admin)
```bash
curl -X POST "http://localhost:8000/api/v1/users" \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "estudiante@example.com",
    "password": "password123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "role": "Estudiante",
    "fecha_nacimiento": "2000-01-01",
    "programa_academico": "Ingeniería"
  }'
```

### 3. Ver Usuario Actual
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer {token}"
```

### 4. Generar Reporte
```bash
curl -X GET "http://localhost:8000/api/v1/reports/student/1?format=json" \
  -H "Authorization: Bearer {token}"
```

---

## Documentación Interactiva

La mejor forma de explorar y probar todos los endpoints es usando la documentación interactiva:

**Swagger UI:** http://localhost:8000/docs
**ReDoc:** http://localhost:8000/redoc

En la documentación puedes:
- Ver todos los endpoints organizados por categoría
- Ver los schemas de request/response
- Probar los endpoints directamente
- Autenticarte y probar endpoints protegidos

