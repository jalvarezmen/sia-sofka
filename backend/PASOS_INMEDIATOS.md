# 🚀 Pasos Inmediatos Recomendados - Refactorización Backend

## 📊 Estado Actual

✅ **Completado (60%)**:
- Tests integración mixins (coverage → 64.29%)
- Refactorización endpoints (grades.py -40%, enrollments.py -35%)
- Registry Pattern en Report Factory
- Constantes en Settings

📊 **Coverage Actual**: 39.51% → **Objetivo**: > 85%

---

## 🎯 PLAN DE ACCIÓN PRIORIZADO (Por Impacto)

### **PRIORIDAD 1: VERIFICACIÓN Y FIXES** (1 hora) 🔥

#### ✅ Paso 1.1: Verificar Tests Actuales (30 min)
**Comando**:
```powershell
cd backend
$env:DATABASE_URL="sqlite+aiosqlite:///:memory:"
$env:DATABASE_URL_SYNC="sqlite:///:memory:"
$env:SECRET_KEY="test-secret-key-for-pytest-only-min-length-32-characters"
pytest tests/ -v --tb=short
```

**Objetivo**: Asegurar que refactorización no rompió nada

---

#### ⏳ Paso 1.2: Testear Report Factory Registry (30 min)
**Archivo Creado**: `tests/unit/test_report_factory_registry.py` ✅

**Comando**:
```powershell
pytest tests/unit/test_report_factory_registry.py -v
```

**Objetivo**: Verificar que Registry Pattern funcione correctamente

---

### **PRIORIDAD 2: TESTS REPOSITORIES** (2.5 horas) 🔥 **ALTA PRIORIDAD**

**Impacto**: Coverage repositories → 85%+ (mayor impacto)

#### ⏳ Paso 2.1: Tests GradeRepository (1.5 horas)

**Crear**: `tests/unit/test_grade_repository_advanced.py`

**Template Base**:
```python
"""Advanced tests for GradeRepository."""
import pytest
from app.repositories.grade_repository import GradeRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.models.user import User, UserRole
from app.models.subject import Subject
from decimal import Decimal
from datetime import date
from app.utils.codigo_generator import generar_codigo_institucional


@pytest.mark.asyncio
async def test_get_with_relations_loads_enrollment(db_session):
    """Test that get_with_relations loads enrollment relationship."""
    # Setup: crear estudiante, profesor, subject, enrollment, grade
    codigo_estudiante = await generar_codigo_institucional(db_session, "Estudiante")
    # ... crear datos ...
    
    repo = GradeRepository(db_session)
    grade = await repo.get_with_relations(grade_id, relations=['enrollment'])
    
    assert grade is not None
    assert grade.enrollment is not None


@pytest.mark.asyncio
async def test_get_many_with_relations_by_subject(db_session):
    """Test get_many_with_relations filters by subject."""
    # ...

# Agregar 6-8 tests más siguiendo este patrón
```

**Impacto**: Coverage `grade_repository.py` → 85%+ (de 31.88%)

---

#### ⏳ Paso 2.2: Tests EnrollmentRepository (1 hora)

**Crear**: `tests/unit/test_enrollment_repository_advanced.py`

**Similar a GradeRepository**, enfocado en métodos:
- `get_with_relations()`
- `get_many_with_relations()`

**Impacto**: Coverage `enrollment_repository.py` → 85%+ (de 38.78%)

---

### **PRIORIDAD 3: TESTS DECORATORS** (2 horas) 🔥 **ALTA PRIORIDAD**

**Archivo**: `tests/unit/test_decorators.py` (ya existe, completar)

**Agregar Tests Faltantes**:
```python
class TestCacheResult:
    """Tests for @cache_result decorator."""
    
    @pytest.mark.asyncio
    async def test_caches_result_for_ttl_seconds():
        """Test that result is cached for specified TTL."""
        call_count = 0
        
        @cache_result(ttl_seconds=1)
        async def cached_function():
            nonlocal call_count
            call_count += 1
            return call_count
        
        result1 = await cached_function()
        result2 = await cached_function()
        assert result1 == result2
        assert call_count == 1
    
    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl():
        """Test that cache expires after TTL."""
        # ...
    
    @pytest.mark.asyncio
    async def test_cache_cleanup_prevents_unbounded_growth():
        """Test that cache cleanup prevents unbounded growth."""
        # ...
```

**Impacto**: Coverage `decorators.py` → 85%+ (de 13.56%)

---

### **PRIORIDAD 4: TESTS ENDPOINTS** (2 horas) 🔥 **ALTA PRIORIDAD**

**Verifica que refactorización funcione**

#### ⏳ Paso 4.1: Tests grades.py refactorizado (1.5 horas)

**Crear**: `tests/integration/test_grades_endpoints_refactored.py`

**Test Crítico** (verifica fix actual):
```python
@pytest.mark.asyncio
async def test_get_grades_includes_estudiante_and_subject_info(client, admin_token):
    """Test that get_grades includes estudiante and subject info.
    
    Este test verifica que el fix actual funcione correctamente.
    """
    # Setup: crear grades con enrollments
    # ...
    
    response = await client.get(
        "/api/v1/grades",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    
    assert response.status_code == 200
    grades = response.json()
    
    assert len(grades) > 0
    grade = grades[0]
    
    # Verificar que enrollment tenga estudiante y subject
    assert "enrollment" in grade
    assert grade["enrollment"]["estudiante"] is not None
    assert grade["enrollment"]["estudiante"]["nombre"] is not None
    assert grade["enrollment"]["subject"] is not None
    assert grade["enrollment"]["subject"]["nombre"] is not None
```

**Impacto**: Verifica funcionalidad crítica

---

#### ⏳ Paso 4.2: Tests enrollments.py refactorizado (30 min)

**Similar a grades.py**, verificar que incluye relaciones

---

### **PRIORIDAD 5: TESTS SERVICIOS** (4 horas)

#### ⏳ Paso 5.1: Tests AdminService Reports (2 horas)
#### ⏳ Paso 5.2: Tests Otros Servicios (2 horas)

---

### **PRIORIDAD 6: TESTS SECURITY/SANITIZERS** (2 horas)

#### ⏳ Paso 6.1: Tests sanitizers.py (1 hora)
#### ⏳ Paso 6.2: Tests security.py (1 hora)

---

## 📋 CHECKLIST DE EJECUCIÓN INMEDIATA

### **HOY (Próximas 3-4 horas)**:

- [ ] ✅ Ejecutar todos los tests y verificar que pasen
  ```bash
  pytest tests/ -v --tb=short
  ```

- [ ] ⏳ Ejecutar test Report Factory Registry
  ```bash
  pytest tests/unit/test_report_factory_registry.py -v
  ```

- [ ] ⏳ Crear tests para GradeRepository (8-10 tests)
- [ ] ⏳ Crear tests para EnrollmentRepository (6-8 tests)
- [ ] ⏳ Ejecutar coverage intermedio
  ```bash
  pytest tests/ -v --cov=app --cov-report=term-missing | Select-Object -Last 30
  ```

**Checkpoint**: Coverage > 55%, todos los tests pasando

---

### **MAÑANA (Próximas 4-5 horas)**:

- [ ] ⏳ Completar tests decorators (@cache_result)
- [ ] ⏳ Crear tests endpoints grades.py refactorizado
- [ ] ⏳ Crear tests endpoints enrollments.py refactorizado
- [ ] ⏳ Ejecutar coverage intermedio

**Checkpoint**: Coverage > 70%, endpoints testeados

---

### **DÍA 3 (Próximas 4-5 horas)**:

- [ ] ⏳ Tests AdminService reports
- [ ] ⏳ Tests otros servicios
- [ ] ⏳ Tests security y sanitizers
- [ ] ⏳ Ejecutar coverage final

**Checkpoint**: Coverage > 85%, todos los módulos testeados

---

## 🎯 ESTRATEGIA RECOMENDADA

### **Enfoque Incremental** ✅ (Recomendado)

1. **Un módulo a la vez**: Completar tests de un módulo antes de pasar al siguiente
2. **Verificar después de cada módulo**: Ejecutar coverage después de cada cambio
3. **No avanzar hasta > 85%**: No pasar al siguiente módulo hasta que actual esté completo

**Ventajas**:
- ✅ Ver progreso constante
- ✅ Fácil debug (sabes qué módulo rompió)
- ✅ Coverage aumenta gradualmente
- ✅ Menos riesgo de romper funcionalidad

---

## 🔧 COMANDOS DE VERIFICACIÓN

### Verificar Coverage por Módulo:
```powershell
# GradeRepository
pytest tests/unit/test_grade_repository_advanced.py -v --cov=app.repositories.grade_repository --cov-report=term-missing

# EnrollmentRepository
pytest tests/unit/test_enrollment_repository_advanced.py -v --cov=app.repositories.enrollment_repository --cov-report=term-missing

# Decorators
pytest tests/unit/test_decorators.py -v --cov=app.core.decorators --cov-report=term-missing

# Coverage completo
pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing
```

### Ver Líneas Sin Cubrir:
```powershell
pytest tests/ -v --cov=app --cov-report=term-missing | Select-String "^\s+\d+\s+\d+" | Select-Object -Last 20
```

---

## ⚠️ PUNTOS CRÍTICOS DE ATENCIÓN

### 1. **Report Factory Registry** ✅
**Estado**: Test creado, imports ajustados en services  
**Riesgo**: Bajo  
**Acción**: Ejecutar test para verificar

---

### 2. **Batch Loading Funciona** ⚠️
**Verificación Necesaria**: 
- Agregar test que verifique no N+1 queries
- Comparar tiempos antes/después

---

### 3. **Endpoints Refactorizados** ⚠️
**Verificación Necesaria**:
- Test que verifique que `estudiante` y `subject` aparecen en respuesta
- Test que verifique frontend funciona

---

## ✅ CRITERIOS DE ÉXITO POR FASE

| Fase | Coverage Esperado | Tests Nuevos | Tiempo | Estado |
|------|------------------|--------------|--------|--------|
| Fase 1 | 45-50% | 5-10 | 1 hora | ✅ Completado |
| Fase 2 | 60-65% | 15-20 | 2.5 horas | ⏳ Siguiente |
| Fase 3 | 70-75% | 10-15 | 2 horas | ⏳ Pendiente |
| Fase 4 | 75-80% | 15-20 | 2 horas | ⏳ Pendiente |
| Fase 5 | 80-85% | 20-25 | 4 horas | ⏳ Pendiente |
| Fase 6 | 85-88% | 10-15 | 2 horas | ⏳ Pendiente |
| Fase 7 | > 85% | 0 | 1 hora | ⏳ Pendiente |

**Total**: ~14 horas, 75-105 tests nuevos

---

## 🚀 COMENZAR AHORA

### **Paso Inmediato 1** (AHORA - 30 min):
```powershell
# Verificar que todos los tests pasen
cd backend
$env:DATABASE_URL="sqlite+aiosqlite:///:memory:"
$env:DATABASE_URL_SYNC="sqlite:///:memory:"
$env:SECRET_KEY="test-secret-key-for-pytest-only-min-length-32-characters"
pytest tests/ -v --tb=short
```

### **Paso Inmediato 2** (AHORA - 30 min):
```powershell
# Verificar Report Factory Registry
pytest tests/unit/test_report_factory_registry.py -v
```

### **Paso Inmediato 3** (SIGUIENTE - 1.5 horas):
```powershell
# Crear tests para GradeRepository
# Archivo: tests/unit/test_grade_repository_advanced.py
```

---

**Última actualización**: 2026-01-10  
**Próxima revisión**: Después de completar Fase 2

