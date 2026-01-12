# 🔧 Plan de Refactorización por Etapas

## 📋 Estado Actual
- **Coverage**: 43.96% (necesita mejorarse a 85%+)
- **Tests pasando**: 31/31 para decorators y mixins
- **Problemas**: Endpoints complejos, código duplicado, bajo coverage

---

## 🎯 ETAPA 1: Completar Tests de Mixins (Prioridad ALTA)
**Objetivo**: Mejorar coverage de mixins.py de 31.43% a 85%+

### Tareas:
1. ✅ Tests básicos ya existen
2. ⏳ Agregar tests de integración con datos reales para `_get_one_with_relations`
3. ⏳ Agregar tests de integración para `_get_many_with_relations` con nested relations
4. ⏳ Agregar tests para `_get_recent` de TimestampMixin

**Estimado**: 1-2 horas
**Riesgo**: Bajo (solo agregar tests)

---

## 🎯 ETAPA 2: Refactorizar Endpoint grades.py (Prioridad ALTA)
**Objetivo**: Reducir complejidad y usar nuevo repository pattern

### Estado Actual:
- Endpoint tiene ~300 líneas
- Mezcla lógica de negocio, serialización y validación
- Usa funciones helper que duplican lógica del repository

### Cambios Propuestos:
1. Usar `GradeRepository.get_with_relations()` en lugar de `load_grade_with_enrollment()`
2. Usar `GradeRepository.get_many_with_relations()` en lugar de queries manuales
3. Simplificar `_to_response()` usando el repository
4. Mover validación de permisos a dependency/middleware

**Estimado**: 2-3 horas
**Riesgo**: Medio (requiere testing cuidadoso)

---

## 🎯 ETAPA 3: Refactorizar Endpoint enrollments.py (Prioridad MEDIA)
**Objetivo**: Eliminar código duplicado y usar mixins

### Estado Actual:
- Usa `selectinload` directamente en endpoint
- Código duplicado en varios lugares

### Cambios Propuestos:
1. Usar `EnrollmentRepository.get_with_relations()` 
2. Usar `EnrollmentRepository.get_many_with_relations()`
3. Eliminar código duplicado de `selectinload`

**Estimado**: 1-2 horas
**Riesgo**: Bajo

---

## 🎯 ETAPA 4: Implementar Registry Pattern en Report Factory (Prioridad MEDIA)
**Objetivo**: Eliminar switch statement y seguir OCP

### Estado Actual:
- Report Factory probablemente usa if/elif para formatos

### Cambios Propuestos:
1. Crear decorator `@ReportFactory.register(format)`
2. Registrar generadores dinámicamente
3. Eliminar switch statement

**Estimado**: 2-3 horas
**Riesgo**: Medio (requiere testing de todos los formatos)

---

## 🎯 ETAPA 5: Centralizar Constantes (Prioridad BAJA)
**Objetivo**: Eliminar magic numbers

### Cambios Propuestos:
1. Mover DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE a Settings
2. Crear enums para estados
3. Actualizar todos los endpoints

**Estimado**: 1 hora
**Riesgo**: Bajo

---

## 🎯 ETAPA 6: Agregar Tests de Integración Faltantes (Prioridad ALTA)
**Objetivo**: Coverage > 85%

### Tareas:
1. Tests para métodos nuevos en repositories
2. Tests para edge cases en endpoints
3. Tests de performance para queries complejas

**Estimado**: 3-4 horas
**Riesgo**: Bajo

---

## 📊 Métricas de Éxito

### Antes de Refactorización:
- Coverage: 43.96%
- Complejidad endpoints: Alta
- Código duplicado: ~150 líneas

### Después de Refactorización:
- Coverage: > 85% ✅
- Complejidad endpoints: Reducida 40%
- Código duplicado: < 50 líneas ✅
- Tests pasando: 100% ✅

---

## 🚀 Ejecución por Etapas

Cada etapa será:
1. Implementada
2. Testeada (todos los tests deben pasar)
3. Verificada (coverage mejorado o mantenido)
4. Documentada
5. Commit separado

---

**Fecha de inicio**: 2026-01-10
**Duración estimada total**: 10-15 horas
**Prioridad**: Etapa 1 → Etapa 2 → Etapa 6 → Etapa 3 → Etapa 4 → Etapa 5

