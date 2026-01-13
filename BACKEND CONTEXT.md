# Plan de Implementación Backend - SIA SOFKA U

---

## 📋 Arquitectura General

El backend seguirá una **arquitectura en capas** con separación de responsabilidades:

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/        # Endpoints por recurso
│   │       └── dependencies.py   # Dependencias compartidas
│   ├── core/
│   │   ├── config.py            # Configuración (pydantic-settings)
│   │   ├── security.py          # JWT y hashing
│   │   └── database.py          # Conexión SQLAlchemy
│   ├── models/                   # Modelos SQLAlchemy
│   ├── schemas/                  # Pydantic schemas
│   ├── services/                 # Lógica de negocio
│   ├── repositories/             # Acceso a datos (Repository Pattern)
│   ├── factories/                # Factory Method para reportes
│   └── main.py                   # Aplicación FastAPI
├── tests/
│   ├── unit/                     # Pruebas unitarias
│   ├── integration/              # Pruebas de integración
│   └── conftest.py               # Fixtures pytest
├── alembic/                      # Migraciones
├── .github/
│   └── workflows/
│       └── ci.yml                # GitHub Actions pipeline
├── Dockerfile                    # Imagen Docker del servicio
├── docker-compose.yml            # Orquestación de servicios (API + PostgreSQL)
├── .dockerignore                 # Archivos a excluir de Docker
├── requirements.txt
├── requirements-dev.txt
└── pytest.ini
```

---

## 🚀 Etapas de Implementación

### **Etapa 1: Configuración Inicial del Proyecto**

**🎯 Objetivo:** Establecer la estructura base del proyecto con todas las herramientas necesarias, incluyendo configuración de Docker para containerización del servicio.

#### 📝 Tareas:

**Configuración Base:**
- Crear estructura de carpetas siguiendo la arquitectura propuesta
- Configurar `requirements.txt` con FastAPI, SQLAlchemy, PostgreSQL, Pydantic, pytest, etc.
- Configurar `requirements-dev.txt` con herramientas de desarrollo (black, flake8, mypy, coverage)
- Crear `pytest.ini` con configuración de pruebas
- Configurar `.env.example` con variables de entorno (incluyendo variables para Docker)
- Crear `app/core/config.py` usando pydantic-settings para gestión de configuración
- Configurar `app/core/database.py` con SQLAlchemy (async)
- Crear `app/main.py` básico con FastAPI
- Configurar Alembic para migraciones
- Crear `.gitignore` apropiado para Python

**Configuración Docker:**

*Crear Dockerfile para el servicio FastAPI:*
- Imagen base Python (slim-buster o alpine)
- Instalación de dependencias del sistema necesarias
- Copia de requirements y instalación de dependencias Python
- Copia del código de la aplicación
- Exposición del puerto (ej: 8000)
- Comando para ejecutar uvicorn

*Crear docker-compose.yml para orquestar servicios:*
- Servicio api: build desde Dockerfile, variables de entorno, puertos, dependencias
- Servicio db: imagen PostgreSQL oficial, volúmenes para persistencia, variables de entorno de BD
- Red Docker para comunicación entre servicios
- Healthchecks para ambos servicios
- Crear `.dockerignore` para excluir archivos innecesarios (tests, .git, pycache, etc.)
- Verificar que el servicio se levante correctamente con `docker-compose up`

#### 📂 Archivos clave:

- `backend/app/core/config.py` - Configuración centralizada
- `backend/app/core/database.py` - Sesión de base de datos
- `backend/pytest.ini` - Configuración de pruebas
- `backend/Dockerfile` - Imagen Docker del servicio FastAPI
- `backend/docker-compose.yml` - Orquestación de servicios
- `backend/.dockerignore` - Archivos excluidos de Docker

---

### **Etapa 2: Modelos de Base de Datos y Migraciones (TDD)**

**🎯 Objetivo:** Definir el esquema de base de datos siguiendo TDD con modelos detallados según requerimientos de negocio.

#### 📝 Tareas:

- **TDD:** Escribir pruebas unitarias para modelos (User, Subject, Grade, Enrollment)

**Crear modelos SQLAlchemy en `app/models/`:**

**User (modelo base para todos los roles):**
- Campos base: `id`, `email` (correo electrónico institucional), `password_hash`, `role` (Admin/Profesor/Estudiante), `created_at`, `updated_at`
- Campos comunes: `nombre`, `apellido`, `fecha_nacimiento`, `edad` (calculada o almacenada), `numero_contacto`
- ID Institucional: `codigo_institucional` (auto-generado al crear usuario, único por rol)
- Campos específicos Estudiante (opcionales): `programa_academico`, `ciudad_residencia`
- Campos específicos Profesor (opcionales): `area_ensenanza`

**Subject (Materia):**
- `id`, `nombre`, `codigo_institucional` (código institucional único), `numero_creditos`, `horario`, `descripcion`, `profesor_id` FK, `created_at`, `updated_at`
- Relación many-to-many con User (estudiantes) a través de Enrollment

**Enrollment (Inscripción Estudiante-Materia):**
- `id`, `estudiante_id` FK, `subject_id` FK, `created_at`, `updated_at`
- Unique constraint en (estudiante_id, subject_id)

**Grade (Nota):**
- `id`, `enrollment_id` FK, `nota` (valor numérico), `periodo` (trimestre/semestre), `fecha`, `observaciones`, `created_at`, `updated_at`

**Implementar lógica de generación automática de `codigo_institucional`:**
- Para Estudiante: formato `"EST-{año}-{secuencial}"` (ej: EST-2024-0001)
- Para Profesor: formato `"PROF-{año}-{secuencial}"` (ej: PROF-2024-0001)
- Para Admin: formato `"ADM-{año}-{secuencial}"` (ej: ADM-2024-0001)

**Implementar relaciones entre modelos:**
- User (Profesor) → Subject (one-to-many)
- User (Estudiante) ↔ Subject (many-to-many a través de Enrollment)
- Enrollment → Grade (one-to-many)

**Crear schemas Pydantic en `app/schemas/` para validación:**
- UserCreate, UserUpdate, UserResponse (con variantes por rol)
- SubjectCreate, SubjectUpdate, SubjectResponse
- EnrollmentCreate, EnrollmentResponse
- GradeCreate, GradeUpdate, GradeResponse

- Crear migración inicial con Alembic
- Ejecutar migraciones y verificar que las pruebas pasen

#### 📂 Archivos clave:

- `backend/app/models/user.py` - Modelo User con campos detallados por rol
- `backend/app/models/subject.py` - Modelo Subject con créditos y horario
- `backend/app/models/enrollment.py` - Modelo Enrollment
- `backend/app/models/grade.py` - Modelo Grade
- `backend/app/utils/codigo_generator.py` - Utilidad para generar códigos institucionales
- `backend/tests/unit/test_models.py`

---

### **Etapa 3: Autenticación y Autorización JWT (TDD)**

**🎯 Objetivo:** Implementar sistema de autenticación con JWT y control de acceso basado en roles.

#### 📝 Tareas:

- **TDD:** Escribir pruebas para autenticación y autorización

**Implementar `app/core/security.py` con:**
- Función de hash de contraseñas (bcrypt)
- Creación y verificación de JWT tokens
- Decodificación de tokens

- Crear `app/schemas/token.py` para schemas de tokens

**Implementar `app/api/v1/dependencies.py` con:**
- Dependency para obtener usuario actual
- Dependency para verificar roles (Admin, Profesor, Estudiante)

**Crear endpoints de autenticación:**
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/register` - Registro (solo Admin)
- `GET /api/v1/auth/me` - Usuario actual

- Implementar decoradores/helpers para protección de rutas por rol

#### 📂 Archivos clave:

- `backend/app/core/security.py`
- `backend/app/api/v1/endpoints/auth.py`
- `backend/tests/unit/test_auth.py`
- `backend/tests/unit/test_security.py`

---

### **Etapa 4: Repository Pattern y Servicios Base (TDD)**

**🎯 Objetivo:** Implementar capa de repositorio y servicios base siguiendo SOLID.

#### 📝 Tareas:

- **TDD:** Escribir pruebas para repositorios y servicios
- Crear `app/repositories/base.py` con clase base `AbstractRepository`

**Implementar repositorios específicos:**
- `UserRepository` en `app/repositories/user_repository.py`
- `SubjectRepository` en `app/repositories/subject_repository.py`
- `EnrollmentRepository` en `app/repositories/enrollment_repository.py`
- `GradeRepository` en `app/repositories/grade_repository.py`

**Crear servicios base en `app/services/`:**

**UserService** - Lógica de negocio para usuarios:
- Generación automática de código institucional según rol
- Cálculo automático de edad desde fecha_nacimiento
- Validación de campos específicos por rol (programa_academico para estudiantes, area_ensenanza para profesores)

**SubjectService** - Lógica de negocio para materias:
- Validación de número de créditos
- Gestión de horarios
- Asignación de profesor

**EnrollmentService** - Lógica de negocio para inscripciones:
- Validación de que estudiante no esté ya inscrito en la materia
- Validación de capacidad máxima (si aplica)

**GradeService** - Lógica de negocio para notas:
- Validación de rango de notas (ej: 0.0 a 5.0)
- Cálculo de promedios por materia y general

- Implementar validaciones de negocio en servicios
- Aplicar principio de responsabilidad única (SRP)

#### 📂 Archivos clave:

- `backend/app/repositories/base.py`
- `backend/app/repositories/user_repository.py`
- `backend/app/services/user_service.py`
- `backend/tests/unit/test_repositories.py`
- `backend/tests/unit/test_services.py`

---

### **Etapa 5: Lógica de Negocio por Rol (TDD)**

**🎯 Objetivo:** Implementar las funcionalidades específicas de cada rol según el diagrama.

#### 📝 Tareas para Administrador:

- **TDD:** Pruebas para funcionalidades de Admin

**AdminService en `app/services/admin_service.py`:**
- Gestionar estudiantes y profesores (CRUD completo)
- Gestionar materias (CRUD completo)
- Generar promedio automático por estudiante y materia
- Generar reportes por estudiante (PDF, HTML, JSON) - usando Factory Method

#### 📝 Tareas para Profesor:

- **TDD:** Pruebas para funcionalidades de Profesor

**ProfesorService en `app/services/profesor_service.py`:**
- Administrar notas de estudiantes en materias asignadas
- Visualizar materias asignadas con listado de estudiantes
- Generar PDF de reporte de notas por materia
- Visualizar y modificar datos personales

#### 📝 Tareas para Estudiante:

- **TDD:** Pruebas para funcionalidades de Estudiante

**EstudianteService en `app/services/estudiante_service.py`:**
- Visualizar estado de notas por materia inscrita
- Generar reporte general PDF con todas las materias
- Visualizar y editar datos personales

#### 📂 Archivos clave:

- `backend/app/services/admin_service.py`
- `backend/app/services/profesor_service.py`
- `backend/app/services/estudiante_service.py`
- `backend/tests/unit/test_admin_service.py`
- `backend/tests/unit/test_profesor_service.py`
- `backend/tests/unit/test_estudiante_service.py`

---

### **Etapa 6: Factory Method para Reportes (TDD)**

**🎯 Objetivo:** Implementar patrón Factory Method para generación de reportes en múltiples formatos.

#### 📝 Tareas:

- **TDD:** Pruebas para Factory Method y cada tipo de reporte

**Crear `app/factories/report_factory.py`:**
- Clase abstracta `ReportGenerator` (ABC)

**Implementaciones concretas:**
- `PDFReportGenerator` - Genera reportes en PDF (usando reportlab o weasyprint)
- `HTMLReportGenerator` - Genera reportes en HTML
- `JSONReportGenerator` - Genera reportes en JSON
- `ReportFactory` - Factory para crear instancias según formato

- Integrar Factory en servicios (AdminService, ProfesorService, EstudianteService)
- Crear schemas para datos de reportes en `app/schemas/report.py`

#### 📂 Archivos clave:

- `backend/app/factories/report_factory.py`
- `backend/app/factories/pdf_generator.py`
- `backend/app/factories/html_generator.py`
- `backend/app/factories/json_generator.py`
- `backend/tests/unit/test_report_factory.py`

---

### **Etapa 7: Endpoints de API REST (TDD)**

**🎯 Objetivo:** Exponer todas las funcionalidades a través de endpoints RESTful.

#### 📝 Tareas:

- **TDD:** Pruebas de integración para endpoints

**Crear endpoints en `app/api/v1/endpoints/`:**
- `users.py` - CRUD de usuarios (solo Admin)
- `subjects.py` - CRUD de materias (solo Admin)
- `enrollments.py` - Gestión de inscripciones (Admin)
- `grades.py` - Gestión de notas (Profesor, Admin)
- `reports.py` - Generación de reportes (todos los roles según permisos)
- `profile.py` - Perfil de usuario (todos los roles)

- Implementar validación de permisos por rol en cada endpoint
- Crear routers y registrar en `app/main.py`
- Documentación automática con Swagger/OpenAPI
- Manejo de errores centralizado con excepciones personalizadas

#### 📂 Archivos clave:

- `backend/app/api/v1/endpoints/users.py`
- `backend/app/api/v1/endpoints/subjects.py`
- `backend/app/api/v1/endpoints/grades.py`
- `backend/app/api/v1/endpoints/reports.py`
- `backend/tests/integration/test_endpoints.py`

---

### **Etapa 8: GitHub Actions CI/CD Pipeline**

**🎯 Objetivo:** Configurar pipeline automatizado para calidad del software.

#### 📝 Tareas:

**Crear `.github/workflows/ci.yml` con:**
- Checkout del código
- Setup de Python
- Instalación de dependencias
- Ejecución de linter (flake8, black check)
- Ejecución de type checker (mypy)
- Ejecución de pruebas unitarias con coverage
- Generación de reporte de coverage
- Verificación de cobertura mínima (80%+)

- Configurar badges en README para estado del pipeline
- Agregar pre-commit hooks opcionales (black, flake8)

#### 📂 Archivos clave:

- `backend/.github/workflows/ci.yml`
- `backend/.coveragerc` - Configuración de coverage

---

## 🎯 Principios y Patrones Aplicados

### **TDD (Test-Driven Development)**
- Cada funcionalidad se desarrolla escribiendo pruebas primero

### **SOLID**
- **SRP (Single Responsibility Principle):** Servicios y repositorios con responsabilidades únicas
- **OCP (Open/Closed Principle):** Factory Method permite extensión sin modificación
- **LSP (Liskov Substitution Principle):** Implementaciones de reportes intercambiables
- **ISP (Interface Segregation Principle):** Interfaces específicas por rol
- **DIP (Dependency Inversion Principle):** Dependencias hacia abstracciones (repositorios, factories)

### **Clean Code**
- Nombres descriptivos
- Funciones pequeñas
- Comentarios cuando necesario

### **Patrones de Diseño**
- **Repository Pattern:** Abstracción de acceso a datos
- **Factory Method:** Creación de reportes
- **Dependency Injection:** FastAPI dependencies
- **Strategy Pattern:** Diferentes generadores de reportes

---

## 📊 Cobertura de Pruebas

- **Objetivo:** Mantener cobertura mínima del 80%
- **Tipos de pruebas:** Unitarias e Integración
- **Herramientas:** pytest, coverage.py
- **CI/CD:** Verificación automática en cada push
- **Strategy Pattern:** Diferentes generadores de reportes

---

## 📊 Cobertura de Pruebas

- **Objetivo:** Mantener cobertura mínima del 80%
- **Tipos de pruebas:** Unitarias e Integración
- **Herramientas:** pytest, coverage.py
- **CI/CD:** Verificación automática en cada push