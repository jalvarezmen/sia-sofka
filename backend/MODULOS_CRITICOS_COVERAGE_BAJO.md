# 🔍 Análisis de Módulos Críticos con Coverage Bajo

**Fecha**: 2026-01-10  
**Objetivo**: Identificar módulos con lógica de negocio crítica que requieren mayor cobertura de tests

---

## 📊 Resumen Ejecutivo

| Módulo | Coverage Actual | Líneas Sin Cubrir | Prioridad | Lógica de Negocio |
|--------|----------------|-------------------|-----------|-------------------|
| **`app.api.v1.endpoints.reports.py`** | **40.68%** | 35 líneas | 🔴 **CRÍTICA** | Generación de reportes (PDF, HTML, JSON) |
| **`app.api.v1.endpoints.grades.py`** | **49.06%** | 81 líneas | 🔴 **CRÍTICA** | Gestión de notas, validaciones de permisos |
| **`app.api.v1.endpoints.enrollments.py`** | **52.17%** | 44 líneas | 🔴 **CRÍTICA** | Inscripciones, validaciones de negocio |
| **`app.api.v1.endpoints.auth.py`** | **67.50%** | 13 líneas | 🟡 **ALTA** | Registro de usuarios, autenticación |
| **`app.api.v1.endpoints.users.py`** | **67.35%** | 16 líneas | 🟡 **ALTA** | CRUD de usuarios, validaciones de roles |
| **`app.api.v1.endpoints.subjects.py`** | **64.29%** | 20 líneas | 🟡 **ALTA** | CRUD de materias, asignación de profesores |
| **`app.api.v1.dependencies.py`** | **86.84%** | 5 líneas | 🟢 **MEDIA** | Autorización y validación de roles |

---

## 🔴 MÓDULOS CRÍTICOS (Coverage < 60%)

### 1. `app.api.v1.endpoints.reports.py` - **40.68% Coverage**

#### 📋 Lógica de Negocio Crítica:
- ✅ Generación de reportes en múltiples formatos (PDF, HTML, JSON)
- ✅ Validación de permisos por rol (Admin, Profesor, Estudiante)
- ✅ Manejo de errores y excepciones de negocio
- ✅ Serialización de contenido según formato

#### ❌ Líneas Sin Cubrir (35 líneas):
- **Líneas 34-54**: Manejo de formato JSON en `get_student_report`
  - Validación de contenido bytes vs string
  - Parsing de JSON
  - Manejo de errores `ValueError` → `NotFoundError`
- **Líneas 70-90**: Manejo de formato JSON en `get_subject_report`
  - Validación de contenido bytes vs string
  - Parsing de JSON
  - Manejo de errores `ValueError` → `ForbiddenError`
- **Líneas 104-112**: Manejo de formato JSON en `get_general_report`
  - Validación de contenido bytes vs string
  - Parsing de JSON
  - Respuesta para formatos PDF/HTML

#### 🎯 Tests Faltantes:
1. **`get_student_report` con formato JSON**:
   - Test con contenido bytes
   - Test con contenido string
   - Test con error `ValueError` → `NotFoundError`
   - Test con error genérico → `ValidationError`

2. **`get_subject_report` con formato JSON**:
   - Test con contenido bytes
   - Test con contenido string
   - Test con error `ValueError` → `ForbiddenError`
   - Test con error genérico → `ValidationError`

3. **`get_general_report` con formato JSON**:
   - Test con contenido bytes
   - Test con contenido string
   - Test con respuesta PDF/HTML

#### 📈 Impacto:
- **Alto**: Los reportes son funcionalidad core del sistema
- **Riesgo**: Errores en serialización pueden causar 500 errors
- **Prioridad**: **ALTA** - Debe alcanzar >80% coverage

---

### 2. `app.api.v1.endpoints.grades.py` - **49.06% Coverage**

#### 📋 Lógica de Negocio Crítica:
- ✅ Creación de notas con validación de permisos
- ✅ Obtención de notas por rol (Admin, Profesor, Estudiante)
- ✅ Validación de asignación de materias a profesores
- ✅ Serialización batch de relaciones anidadas
- ✅ Actualización y eliminación de notas

#### ❌ Líneas Sin Cubrir (81 líneas):
- **Líneas 36-43**: `_verify_profesor_subject_permission`
  - Validación de enrollment no encontrado
  - Validación de subject no asignado al profesor
- **Líneas 52-55**: `_verify_profesor_can_access_subject`
  - Validación de subject no asignado
- **Líneas 82-95**: `create_grade` (casos edge)
  - Manejo de errores `ValueError` → `ForbiddenError` (profesor)
  - Manejo de errores `ValueError` → `NotFoundError` (admin)
  - Serialización de grade creado
- **Líneas 123-179**: `_serialize_grades_batch` (casos edge)
  - Batch loading de estudiantes sin IDs únicos
  - Batch loading de subjects sin IDs únicos
  - Serialización con enrollment sin estudiante/subject
  - Serialización con enrollment completo
- **Líneas 190-197**: `_get_grades_as_estudiante`
  - Obtención de notas por estudiante
  - Serialización batch
- **Líneas 207-214**: `_get_grades_as_profesor`
  - Obtención de notas por profesor
  - Validación de permisos
- **Líneas 228**: `_get_grades_as_admin`
  - Obtención de notas por admin
- **Líneas 249-250**: `get_grade` (casos edge)
  - Manejo de grade no encontrado
- **Líneas 271-283**: `update_grade` (casos edge)
  - Actualización por profesor
  - Actualización por admin
  - Validación de permisos
- **Líneas 298-318**: `delete_grade` (casos edge)
  - Eliminación por profesor
  - Eliminación por admin
  - Validación de permisos
- **Líneas 332-345**: `get_grades` (casos edge)
  - Filtros por subject_id, estudiante_id
  - Paginación
  - Obtención por rol

#### 🎯 Tests Faltantes:
1. **`_verify_profesor_subject_permission`**:
   - Test con enrollment no encontrado
   - Test con subject no asignado al profesor

2. **`_verify_profesor_can_access_subject`**:
   - Test con subject no asignado

3. **`create_grade` casos edge**:
   - Test con error `ValueError` (profesor) → `ForbiddenError`
   - Test con error `ValueError` (admin) → `NotFoundError`
   - Test con grade no encontrado después de creación

4. **`_serialize_grades_batch` casos edge**:
   - Test sin estudiantes únicos
   - Test sin subjects únicos
   - Test con enrollment sin estudiante/subject
   - Test con enrollment completo

5. **`_get_grades_as_estudiante`**:
   - Test completo de obtención y serialización

6. **`_get_grades_as_profesor`**:
   - Test completo de obtención y validación

7. **`_get_grades_as_admin`**:
   - Test completo de obtención

8. **`get_grade`, `update_grade`, `delete_grade` casos edge**:
   - Tests de permisos por rol
   - Tests de grade no encontrado

9. **`get_grades` casos edge**:
   - Tests con filtros (subject_id, estudiante_id)
   - Tests de paginación
   - Tests por rol

#### 📈 Impacto:
- **Alto**: Las notas son funcionalidad core del sistema
- **Riesgo**: Errores en validación de permisos pueden causar accesos no autorizados
- **Prioridad**: **ALTA** - Debe alcanzar >80% coverage

---

### 3. `app.api.v1.endpoints.enrollments.py` - **52.17% Coverage**

#### 📋 Lógica de Negocio Crítica:
- ✅ Creación de inscripciones con validaciones
- ✅ Obtención de inscripciones con paginación
- ✅ Serialización batch de relaciones anidadas
- ✅ Eliminación de inscripciones

#### ❌ Líneas Sin Cubrir (44 líneas):
- **Líneas 50-97**: `_serialize_enrollments_batch` (casos edge)
  - Batch loading de estudiantes sin IDs únicos
  - Batch loading de subjects sin IDs únicos
  - Serialización con enrollment sin estudiante/subject
  - Serialización con enrollment completo
- **Líneas 111-135**: `create_enrollment` (casos edge)
  - Manejo de errores `ValueError` → `ValidationError`
  - Manejo de errores `IntegrityError` → `ConflictError`
  - Serialización de enrollment creado
- **Líneas 155**: `get_enrollments` (casos edge)
  - Paginación con límites
- **Líneas 172-177**: `get_enrollment` (casos edge)
  - Manejo de enrollment no encontrado
- **Líneas 190-191**: `delete_enrollment` (casos edge)
  - Manejo de enrollment no encontrado

#### 🎯 Tests Faltantes:
1. **`_serialize_enrollments_batch` casos edge**:
   - Test sin estudiantes únicos
   - Test sin subjects únicos
   - Test con enrollment sin estudiante/subject
   - Test con enrollment completo

2. **`create_enrollment` casos edge**:
   - Test con error `ValueError` → `ValidationError`
   - Test con error `IntegrityError` → `ConflictError`
   - Test con serialización completa

3. **`get_enrollments` casos edge**:
   - Test con paginación (skip, limit)
   - Test con límites máximos

4. **`get_enrollment` casos edge**:
   - Test con enrollment no encontrado

5. **`delete_enrollment` casos edge**:
   - Test con enrollment no encontrado

#### 📈 Impacto:
- **Alto**: Las inscripciones son funcionalidad core del sistema
- **Riesgo**: Errores en validación pueden causar inscripciones duplicadas
- **Prioridad**: **ALTA** - Debe alcanzar >80% coverage

---

## 🟡 MÓDULOS CON COVERAGE MEDIO (60-80%)

### 4. `app.api.v1.endpoints.auth.py` - **67.50% Coverage**

#### 📋 Lógica de Negocio Crítica:
- ✅ Autenticación de usuarios (login)
- ✅ Registro de usuarios (solo Admin)
- ✅ Generación de códigos institucionales
- ✅ Validación de credenciales

#### ❌ Líneas Sin Cubrir (13 líneas):
- **Líneas 46-62**: `login` (casos edge)
  - Usuario no encontrado
  - Contraseña incorrecta
  - Creación de token con expiración
- **Líneas 87-120**: `register` (completo)
  - Validación de email duplicado
  - Generación de código institucional
  - Creación de usuario con todos los campos
  - Cálculo de edad

#### 🎯 Tests Faltantes:
1. **`login` casos edge**:
   - Test con usuario no encontrado
   - Test con contraseña incorrecta
   - Test con token expirado

2. **`register` completo**:
   - Test con email duplicado
   - Test con generación de código institucional
   - Test con creación de usuario completo
   - Test con cálculo de edad

#### 📈 Impacto:
- **Alto**: La autenticación es crítica para la seguridad
- **Riesgo**: Errores pueden causar problemas de seguridad
- **Prioridad**: **ALTA** - Debe alcanzar >85% coverage

---

### 5. `app.api.v1.endpoints.users.py` - **67.35% Coverage**

#### 📋 Lógica de Negocio Crítica:
- ✅ CRUD completo de usuarios
- ✅ Validación de roles
- ✅ Obtención de estudiantes y profesores

#### ❌ Líneas Sin Cubrir (16 líneas):
- **Líneas 28-34**: `create_user` (casos edge)
  - Validación de rol inválido
  - Manejo de errores `ValueError` → `ValidationError`
- **Líneas 47-48**: `get_users` (casos edge)
  - Combinación de estudiantes y profesores
- **Líneas 63-66**: `get_user` (casos edge)
  - Manejo de usuario no encontrado
- **Líneas 80-83**: `update_user` (casos edge)
  - Manejo de usuario no encontrado
- **Líneas 96-97**: `delete_user` (casos edge)
  - Manejo de usuario no encontrado

#### 🎯 Tests Faltantes:
1. **`create_user` casos edge**:
   - Test con rol inválido
   - Test con error `ValueError` → `ValidationError`

2. **`get_users` casos edge**:
   - Test con combinación de estudiantes y profesores
   - Test con paginación

3. **`get_user`, `update_user`, `delete_user` casos edge**:
   - Tests con usuario no encontrado

#### 📈 Impacto:
- **Medio-Alto**: La gestión de usuarios es importante
- **Riesgo**: Errores pueden causar problemas de integridad
- **Prioridad**: **MEDIA-ALTA** - Debe alcanzar >80% coverage

---

### 6. `app.api.v1.endpoints.subjects.py` - **64.29% Coverage`

#### 📋 Lógica de Negocio Crítica:
- ✅ CRUD completo de materias
- ✅ Asignación de profesores
- ✅ Serialización de relaciones (profesor)

#### ❌ Líneas Sin Cubrir (20 líneas):
- **Líneas 27-29**: `create_subject` (casos edge)
  - Manejo de errores `ValueError` → `ValidationError`
- **Líneas 52-81**: `get_subjects` (completo)
  - Carga de relaciones (profesor)
  - Serialización manual de subjects
  - Inclusión de profesor en respuesta
- **Líneas 96-99**: `get_subject` (casos edge)
  - Manejo de subject no encontrado
- **Líneas 113-116**: `update_subject` (casos edge)
  - Manejo de subject no encontrado
- **Líneas 129-130**: `delete_subject` (casos edge)
  - Manejo de subject no encontrado

#### 🎯 Tests Faltantes:
1. **`create_subject` casos edge**:
   - Test con error `ValueError` → `ValidationError`

2. **`get_subjects` completo**:
   - Test con carga de relaciones (profesor)
   - Test con serialización manual
   - Test con profesor incluido
   - Test sin profesor asignado

3. **`get_subject`, `update_subject`, `delete_subject` casos edge**:
   - Tests con subject no encontrado

#### 📈 Impacto:
- **Medio-Alto**: La gestión de materias es importante
- **Riesgo**: Errores pueden causar problemas de integridad
- **Prioridad**: **MEDIA-ALTA** - Debe alcanzar >80% coverage

---

## 🟢 MÓDULOS CON COVERAGE BUENO (>80%)

### 7. `app.api.v1.dependencies.py` - **86.84% Coverage**

#### 📋 Lógica de Negocio Crítica:
- ✅ Autorización y validación de roles
- ✅ Obtención de usuario actual
- ✅ Validación de tokens JWT

#### ❌ Líneas Sin Cubrir (5 líneas):
- **Línea 42**: `get_current_user` (casos edge)
  - Email None en token
- **Líneas 49-54**: `get_current_user` (casos edge)
  - Usuario no encontrado en BD
  - Manejo de excepciones

#### 🎯 Tests Faltantes:
1. **`get_current_user` casos edge**:
   - Test con email None en token
   - Test con usuario no encontrado en BD
   - Test con excepciones en decode_access_token

#### 📈 Impacto:
- **Medio**: La autorización es crítica pero ya tiene buen coverage
- **Riesgo**: Bajo (ya cubre casos principales)
- **Prioridad**: **BAJA** - Coverage ya es aceptable

---

## 📊 Priorización de Mejoras

### 🔴 Prioridad CRÍTICA (Coverage < 60%)
1. **`app.api.v1.endpoints.reports.py`** (40.68%) → Objetivo: **>80%**
2. **`app.api.v1.endpoints.grades.py`** (49.06%) → Objetivo: **>80%**
3. **`app.api.v1.endpoints.enrollments.py`** (52.17%) → Objetivo: **>80%**

### 🟡 Prioridad ALTA (Coverage 60-80%)
4. **`app.api.v1.endpoints.auth.py`** (67.50%) → Objetivo: **>85%**
5. **`app.api.v1.endpoints.users.py`** (67.35%) → Objetivo: **>80%**
6. **`app.api.v1.endpoints.subjects.py`** (64.29%) → Objetivo: **>80%**

### 🟢 Prioridad MEDIA (Coverage > 80%)
7. **`app.api.v1.dependencies.py`** (86.84%) → Objetivo: **>90%** (opcional)

---

## 🎯 Plan de Acción Recomendado

### FASE 1: Módulos Críticos (Coverage < 60%)
1. **`reports.py`**: Agregar 15-20 tests para casos edge de JSON, errores, formatos
2. **`grades.py`**: Agregar 25-30 tests para validaciones, serialización, permisos
3. **`enrollments.py`**: Agregar 15-20 tests para validaciones, serialización, edge cases

**Tiempo estimado**: 2-3 días  
**Coverage esperado**: >80% en los 3 módulos

### FASE 2: Módulos con Coverage Medio (60-80%)
4. **`auth.py`**: Agregar 8-10 tests para registro, casos edge de login
5. **`users.py`**: Agregar 10-12 tests para casos edge de CRUD
6. **`subjects.py`**: Agregar 10-12 tests para serialización, casos edge

**Tiempo estimado**: 1-2 días  
**Coverage esperado**: >80% en los 3 módulos

### FASE 3: Optimización (Opcional)
7. **`dependencies.py`**: Agregar 3-5 tests para casos edge de autorización

**Tiempo estimado**: 0.5 días  
**Coverage esperado**: >90%

---

## 📈 Impacto Esperado

### Coverage Actual vs Objetivo:

| Módulo | Actual | Objetivo | Mejora |
|--------|--------|----------|--------|
| `reports.py` | 40.68% | >80% | +39.32% |
| `grades.py` | 49.06% | >80% | +30.94% |
| `enrollments.py` | 52.17% | >80% | +27.83% |
| `auth.py` | 67.50% | >85% | +17.50% |
| `users.py` | 67.35% | >80% | +12.65% |
| `subjects.py` | 64.29% | >80% | +15.71% |
| `dependencies.py` | 86.84% | >90% | +3.16% |

### Coverage General Esperado:
- **Actual**: 82.51%
- **Después de FASE 1**: ~85-86%
- **Después de FASE 2**: ~87-88%
- **Después de FASE 3**: ~88-89%

---

## ✅ Conclusión

Los módulos con **lógica de negocio crítica** y **coverage bajo** son principalmente los **endpoints de la API**, especialmente:

1. **`reports.py`** (40.68%): Generación de reportes
2. **`grades.py`** (49.06%): Gestión de notas
3. **`enrollments.py`** (52.17%): Inscripciones

Estos módulos requieren **tests adicionales** para cubrir:
- ✅ Casos edge de validación
- ✅ Manejo de errores
- ✅ Serialización batch
- ✅ Validación de permisos
- ✅ Formatos de respuesta (JSON, PDF, HTML)

**Recomendación**: Priorizar la **FASE 1** para alcanzar >80% coverage en los módulos críticos.

---

**Última actualización**: 2026-01-10  
**Estado**: Análisis completo, listo para implementación

