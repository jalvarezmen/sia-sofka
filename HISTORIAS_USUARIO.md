# Historias de Usuario - SIA SOFKA U

Este documento contiene las historias de usuario del sistema SIA SOFKA U, siguiendo los principios **INVEST** (Independent, Negotiable, Valuable, Estimable, Small, Testable). Todas las historias están basadas en funcionalidades **ya implementadas** en el backend.

---

## Índice

1. [Autenticación](#autenticación)
2. [Gestión de Usuarios (Administrador)](#gestión-de-usuarios-administrador)
3. [Gestión de Materias (Administrador)](#gestión-de-materias-administrador)
4. [Gestión de Inscripciones (Administrador)](#gestión-de-inscripciones-administrador)
5. [Gestión de Notas](#gestión-de-notas)
6. [Reportes](#reportes)
7. [Perfil de Usuario](#perfil-de-usuario)

---

## Autenticación

### HU-001: Iniciar Sesión
**Como** usuario del sistema (Administrador, Profesor o Estudiante)  
**Quiero** iniciar sesión con mi email y contraseña  
**Para** acceder a las funcionalidades del sistema según mi rol

**Criterios de Aceptación:**
- El usuario puede iniciar sesión proporcionando email y contraseña válidos
- El sistema valida las credenciales y genera un token JWT
- El token incluye el rol del usuario para autorización
- Si las credenciales son incorrectas, se muestra un error 401
- El token tiene un tiempo de expiración configurable

**Prioridad:** Crítica  
**Estimación:** 3 puntos  
**Rol:** Todos los usuarios

---

### HU-002: Registrar Nuevo Usuario
**Como** administrador  
**Quiero** registrar nuevos usuarios (estudiantes o profesores) en el sistema  
**Para** gestionar el acceso y los datos de los usuarios de la institución

**Criterios de Aceptación:**
- Solo los administradores pueden registrar usuarios
- Se puede crear un estudiante o un profesor
- El sistema genera automáticamente un código institucional único
- Se valida que el email no esté duplicado
- Se calcula automáticamente la edad del usuario
- La contraseña se almacena de forma segura (hash)

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Administrador

---

### HU-003: Ver Mi Información de Perfil
**Como** usuario autenticado  
**Quiero** ver mi información personal actual  
**Para** verificar mis datos en el sistema

**Criterios de Aceptación:**
- El usuario puede ver su información personal después de autenticarse
- Se muestra: nombre, apellido, email, código institucional, rol, edad, etc.
- Solo se puede acceder a la propia información

**Prioridad:** Media  
**Estimación:** 2 puntos  
**Rol:** Todos los usuarios

---

## Gestión de Usuarios (Administrador)

### HU-004: Crear Estudiante
**Como** administrador  
**Quiero** crear un nuevo estudiante en el sistema  
**Para** registrar estudiantes que se inscribirán a materias

**Criterios de Aceptación:**
- Se puede crear un estudiante con todos sus datos personales
- El sistema genera automáticamente un código institucional único (formato: EST-XXXX)
- Se valida que el email no esté duplicado
- Se calcula automáticamente la edad basada en la fecha de nacimiento
- Se puede especificar programa académico y ciudad de residencia

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Administrador

---

### HU-005: Crear Profesor
**Como** administrador  
**Quiero** crear un nuevo profesor en el sistema  
**Para** asignar profesores a las materias

**Criterios de Aceptación:**
- Se puede crear un profesor con todos sus datos personales
- El sistema genera automáticamente un código institucional único (formato: PRO-XXXX)
- Se valida que el email no esté duplicado
- Se puede especificar área de enseñanza del profesor
- Se calcula automáticamente la edad basada en la fecha de nacimiento

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Administrador

---

### HU-006: Listar Todos los Usuarios
**Como** administrador  
**Quiero** ver una lista de todos los usuarios (estudiantes y profesores)  
**Para** tener una visión general de los usuarios del sistema

**Criterios de Aceptación:**
- Se muestran todos los estudiantes y profesores
- La lista es paginable (skip y limit)
- Se muestra información relevante: nombre, apellido, email, código institucional, rol
- Solo los administradores pueden acceder a esta funcionalidad

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-007: Ver Detalles de un Usuario
**Como** administrador  
**Quiero** ver los detalles completos de un usuario específico  
**Para** revisar o editar su información

**Criterios de Aceptación:**
- Se puede buscar un usuario por su ID
- Se muestra toda la información del usuario
- Si el usuario no existe, se muestra un error 404
- Solo los administradores pueden acceder a esta funcionalidad

**Prioridad:** Media  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

### HU-008: Actualizar Usuario
**Como** administrador  
**Quiero** actualizar la información de un usuario  
**Para** corregir datos o actualizar información personal

**Criterios de Aceptación:**
- Se puede actualizar cualquier campo del usuario (excepto email y código institucional)
- Los campos son opcionales (solo se actualizan los proporcionados)
- Se valida que el usuario exista
- Si el usuario no existe, se muestra un error 404
- Solo los administradores pueden actualizar usuarios

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-009: Eliminar Usuario
**Como** administrador  
**Quiero** eliminar un usuario del sistema  
**Para** remover usuarios que ya no son necesarios

**Criterios de Aceptación:**
- Se puede eliminar un usuario por su ID
- Si el usuario no existe, se muestra un error 404
- Solo los administradores pueden eliminar usuarios
- La operación retorna un código 204 (No Content) si es exitosa

**Prioridad:** Baja  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

## Gestión de Materias (Administrador)

### HU-010: Crear Materia
**Como** administrador  
**Quiero** crear una nueva materia en el sistema  
**Para** ofrecer materias a los estudiantes

**Criterios de Aceptación:**
- Se puede crear una materia con: nombre, código institucional, número de créditos, horario, descripción
- Se debe asignar un profesor a la materia
- El sistema genera automáticamente un código institucional único (formato: MAT-XXXX)
- Se valida que el profesor exista y sea de rol PROFESOR
- Solo los administradores pueden crear materias

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Administrador

---

### HU-011: Listar Todas las Materias
**Como** administrador  
**Quiero** ver una lista de todas las materias  
**Para** gestionar el catálogo de materias disponibles

**Criterios de Aceptación:**
- Se muestran todas las materias con su información
- La lista incluye información del profesor asignado
- La lista es paginable (skip y limit)
- Solo los administradores pueden acceder a esta funcionalidad

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-012: Ver Detalles de una Materia
**Como** administrador  
**Quiero** ver los detalles completos de una materia específica  
**Para** revisar o editar su información

**Criterios de Aceptación:**
- Se puede buscar una materia por su ID
- Se muestra toda la información de la materia, incluyendo el profesor asignado
- Si la materia no existe, se muestra un error 404
- Solo los administradores pueden acceder a esta funcionalidad

**Prioridad:** Media  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

### HU-013: Actualizar Materia
**Como** administrador  
**Quiero** actualizar la información de una materia  
**Para** modificar horarios, descripciones o asignar otro profesor

**Criterios de Aceptación:**
- Se puede actualizar cualquier campo de la materia (excepto código institucional)
- Los campos son opcionales (solo se actualizan los proporcionados)
- Se valida que la materia exista
- Si se cambia el profesor, se valida que el nuevo profesor exista y sea de rol PROFESOR
- Si la materia no existe, se muestra un error 404
- Solo los administradores pueden actualizar materias

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-014: Eliminar Materia
**Como** administrador  
**Quiero** eliminar una materia del sistema  
**Para** remover materias que ya no se ofrecen

**Criterios de Aceptación:**
- Se puede eliminar una materia por su ID
- Si la materia no existe, se muestra un error 404
- Solo los administradores pueden eliminar materias
- La operación retorna un código 204 (No Content) si es exitosa

**Prioridad:** Baja  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

## Gestión de Inscripciones (Administrador)

### HU-015: Inscribir Estudiante a una Materia
**Como** administrador  
**Quiero** inscribir un estudiante a una materia  
**Para** permitir que el estudiante reciba calificaciones en esa materia

**Criterios de Aceptación:**
- Se puede crear una inscripción relacionando un estudiante con una materia
- Se valida que el estudiante exista y sea de rol ESTUDIANTE
- Se valida que la materia exista
- No se puede inscribir dos veces al mismo estudiante en la misma materia (error 409)
- Solo los administradores pueden crear inscripciones

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Administrador

---

### HU-016: Listar Todas las Inscripciones
**Como** administrador  
**Quiero** ver una lista de todas las inscripciones  
**Para** tener un registro de qué estudiantes están inscritos en qué materias

**Criterios de Aceptación:**
- Se muestran todas las inscripciones con información del estudiante y la materia
- La lista incluye: ID de inscripción, datos del estudiante, datos de la materia, fecha de creación
- La lista es paginable (skip y limit)
- Solo los administradores pueden acceder a esta funcionalidad

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-017: Ver Detalles de una Inscripción
**Como** administrador  
**Quiero** ver los detalles completos de una inscripción específica  
**Para** revisar la información de la inscripción

**Criterios de Aceptación:**
- Se puede buscar una inscripción por su ID
- Se muestra toda la información de la inscripción, incluyendo datos del estudiante y la materia
- Si la inscripción no existe, se muestra un error 404
- Solo los administradores pueden acceder a esta funcionalidad

**Prioridad:** Baja  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

### HU-018: Eliminar Inscripción
**Como** administrador  
**Quiero** eliminar una inscripción  
**Para** cancelar la inscripción de un estudiante a una materia

**Criterios de Aceptación:**
- Se puede eliminar una inscripción por su ID
- Si la inscripción no existe, se muestra un error 404
- Solo los administradores pueden eliminar inscripciones
- La operación retorna un código 204 (No Content) si es exitosa

**Prioridad:** Media  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

## Gestión de Notas

### HU-019: Crear Nota (Profesor)
**Como** profesor  
**Quiero** crear una nota para un estudiante en una de mis materias asignadas  
**Para** registrar el desempeño académico del estudiante

**Criterios de Aceptación:**
- El profesor solo puede crear notas para materias que le están asignadas
- Se valida que el estudiante esté inscrito en la materia
- La nota debe estar entre 0 y 5
- Se puede incluir: nota, período, fecha, observaciones
- Si el profesor intenta crear una nota para una materia no asignada, se muestra un error 403

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Profesor

---

### HU-020: Crear Nota (Administrador)
**Como** administrador  
**Quiero** crear una nota para cualquier estudiante en cualquier materia  
**Para** gestionar las calificaciones del sistema

**Criterios de Aceptación:**
- El administrador puede crear notas para cualquier materia
- Se valida que el estudiante esté inscrito en la materia
- La nota debe estar entre 0 y 5
- Se puede incluir: nota, período, fecha, observaciones

**Prioridad:** Alta  
**Estimación:** 5 puntos  
**Rol:** Administrador

---

### HU-021: Ver Mis Notas (Estudiante)
**Como** estudiante  
**Quiero** ver mis notas en una materia específica  
**Para** conocer mi desempeño académico

**Criterios de Aceptación:**
- El estudiante solo puede ver sus propias notas
- Se debe especificar el ID de la materia
- Se valida que el estudiante esté inscrito en la materia
- Se muestran todas las notas con: valor, período, fecha, observaciones
- Si el estudiante intenta ver notas de otra materia o no está inscrito, se muestra un error 403

**Prioridad:** Alta  
**Estimación:** 3 puntos  
**Rol:** Estudiante

---

### HU-022: Ver Notas de una Materia (Profesor)
**Como** profesor  
**Quiero** ver las notas de todos los estudiantes en una de mis materias asignadas  
**Para** revisar el desempeño de los estudiantes

**Criterios de Aceptación:**
- El profesor solo puede ver notas de materias que le están asignadas
- Se debe especificar el ID de la materia
- Se puede filtrar por inscripción específica (enrollment_id)
- Se muestran todas las notas con información del estudiante
- Si el profesor intenta ver notas de una materia no asignada, se muestra un error 403

**Prioridad:** Alta  
**Estimación:** 3 puntos  
**Rol:** Profesor

---

### HU-023: Ver Todas las Notas (Administrador)
**Como** administrador  
**Quiero** ver todas las notas del sistema  
**Para** tener una visión completa de las calificaciones

**Criterios de Aceptación:**
- El administrador puede ver todas las notas
- Se puede filtrar por materia (subject_id) o por inscripción (enrollment_id)
- Se muestran todas las notas con información completa
- Solo los administradores pueden acceder a esta funcionalidad sin restricciones

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-024: Ver Detalles de una Nota
**Como** usuario autenticado  
**Quiero** ver los detalles completos de una nota específica  
**Para** revisar la información completa de la calificación

**Criterios de Aceptación:**
- El estudiante solo puede ver sus propias notas
- El profesor puede ver notas de sus materias asignadas
- El administrador puede ver cualquier nota
- Se muestra: ID, nota, período, fecha, observaciones, información de la inscripción
- Si la nota no existe, se muestra un error 404
- Si el usuario no tiene permiso, se muestra un error 403

**Prioridad:** Media  
**Estimación:** 2 puntos  
**Rol:** Todos los usuarios (con restricciones)

---

### HU-025: Actualizar Nota (Profesor)
**Como** profesor  
**Quiero** actualizar una nota que he creado en una de mis materias  
**Para** corregir errores o actualizar calificaciones

**Criterios de Aceptación:**
- El profesor solo puede actualizar notas de materias que le están asignadas
- Se pueden actualizar: nota, período, fecha, observaciones
- Los campos son opcionales (solo se actualizan los proporcionados)
- Se valida que la nota exista
- Si el profesor intenta actualizar una nota de una materia no asignada, se muestra un error 403

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Profesor

---

### HU-026: Actualizar Nota (Administrador)
**Como** administrador  
**Quiero** actualizar cualquier nota del sistema  
**Para** corregir errores o actualizar calificaciones

**Criterios de Aceptación:**
- El administrador puede actualizar cualquier nota
- Se pueden actualizar: nota, período, fecha, observaciones
- Los campos son opcionales (solo se actualizan los proporcionados)
- Se valida que la nota exista
- Si la nota no existe, se muestra un error 404

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Administrador

---

### HU-027: Eliminar Nota (Profesor)
**Como** profesor  
**Quiero** eliminar una nota que he creado en una de mis materias  
**Para** corregir errores en el registro de calificaciones

**Criterios de Aceptación:**
- El profesor solo puede eliminar notas de materias que le están asignadas
- Se valida que la nota exista
- Si el profesor intenta eliminar una nota de una materia no asignada, se muestra un error 403
- La operación retorna un código 204 (No Content) si es exitosa

**Prioridad:** Baja  
**Estimación:** 2 puntos  
**Rol:** Profesor

---

### HU-028: Eliminar Nota (Administrador)
**Como** administrador  
**Quiero** eliminar cualquier nota del sistema  
**Para** corregir errores en el registro de calificaciones

**Criterios de Aceptación:**
- El administrador puede eliminar cualquier nota
- Se valida que la nota exista
- Si la nota no existe, se muestra un error 404
- La operación retorna un código 204 (No Content) si es exitosa

**Prioridad:** Baja  
**Estimación:** 2 puntos  
**Rol:** Administrador

---

## Reportes

### HU-029: Generar Reporte de Estudiante (PDF/HTML/JSON)
**Como** administrador  
**Quiero** generar un reporte de notas de un estudiante en formato PDF, HTML o JSON  
**Para** tener un documento oficial con el desempeño académico del estudiante

**Criterios de Aceptación:**
- Se puede generar un reporte para cualquier estudiante
- El reporte incluye: información del estudiante, todas sus materias, notas por materia, promedio por materia, promedio general del semestre (ponderado por créditos)
- Se puede elegir el formato: PDF, HTML o JSON
- El reporte PDF/HTML se descarga como archivo
- El reporte JSON se retorna como respuesta JSON
- Solo los administradores pueden generar reportes de estudiantes

**Prioridad:** Alta  
**Estimación:** 8 puntos  
**Rol:** Administrador

---

### HU-030: Generar Reporte de Materia (PDF/HTML/JSON)
**Como** profesor  
**Quiero** generar un reporte de notas de una de mis materias en formato PDF, HTML o JSON  
**Para** tener un documento con el desempeño de todos los estudiantes en la materia

**Criterios de Aceptación:**
- El profesor solo puede generar reportes de materias que le están asignadas
- El reporte incluye: información de la materia, lista de estudiantes, notas de cada estudiante, promedio de cada estudiante
- Se puede elegir el formato: PDF, HTML o JSON
- El reporte PDF/HTML se descarga como archivo
- El reporte JSON se retorna como respuesta JSON
- Si el profesor intenta generar un reporte de una materia no asignada, se muestra un error 403

**Prioridad:** Alta  
**Estimación:** 8 puntos  
**Rol:** Profesor

---

### HU-031: Generar Reporte General (PDF/HTML/JSON)
**Como** estudiante  
**Quiero** generar un reporte general con todas mis materias y notas en formato PDF, HTML o JSON  
**Para** tener un documento completo con mi desempeño académico del semestre

**Criterios de Aceptación:**
- El estudiante solo puede generar su propio reporte general
- El reporte incluye: información del estudiante, todas sus materias, notas por materia, promedio por materia, promedio general del semestre (ponderado por créditos)
- Se puede elegir el formato: PDF, HTML o JSON
- El reporte PDF/HTML se descarga como archivo
- El reporte JSON se retorna como respuesta JSON
- Solo los estudiantes pueden generar su propio reporte general

**Prioridad:** Alta  
**Estimación:** 8 puntos  
**Rol:** Estudiante

---

## Perfil de Usuario

### HU-032: Ver Mi Perfil
**Como** usuario autenticado  
**Quiero** ver mi información de perfil  
**Para** verificar mis datos personales en el sistema

**Criterios de Aceptación:**
- El usuario puede ver su propia información después de autenticarse
- Se muestra: nombre, apellido, email, código institucional, rol, edad, fecha de nacimiento, número de contacto, etc.
- Solo se puede acceder a la propia información

**Prioridad:** Media  
**Estimación:** 2 puntos  
**Rol:** Todos los usuarios

---

### HU-033: Actualizar Mi Perfil
**Como** usuario autenticado  
**Quiero** actualizar mi información personal  
**Para** mantener mis datos actualizados en el sistema

**Criterios de Aceptación:**
- El usuario puede actualizar su propia información
- Se pueden actualizar: nombre, apellido, fecha de nacimiento, número de contacto, programa académico (estudiantes), ciudad de residencia (estudiantes), área de enseñanza (profesores)
- No se puede cambiar: email, código institucional, rol
- Los campos son opcionales (solo se actualizan los proporcionados)
- Si se actualiza la fecha de nacimiento, se recalcula automáticamente la edad

**Prioridad:** Media  
**Estimación:** 3 puntos  
**Rol:** Todos los usuarios

---

## Funcionalidades Adicionales del Sistema

### HU-034: Cálculo Automático de Promedio por Materia
**Como** sistema  
**Quiero** calcular automáticamente el promedio de notas de un estudiante en una materia  
**Para** proporcionar información precisa del desempeño académico

**Criterios de Aceptación:**
- El promedio se calcula como la media aritmética de todas las notas de la materia
- El resultado se redondea a 2 decimales
- Si no hay notas, el promedio es None
- El cálculo se realiza automáticamente cuando se solicitan reportes o promedios

**Prioridad:** Alta  
**Estimación:** 3 puntos  
**Rol:** Sistema (automático)

---

### HU-035: Cálculo Automático de Promedio General del Semestre
**Como** sistema  
**Quiero** calcular automáticamente el promedio general del semestre de un estudiante  
**Para** proporcionar un indicador del desempeño académico general

**Criterios de Aceptación:**
- El promedio general se calcula ponderando por número de créditos de cada materia
- Solo se consideran materias con promedio calculado (que tengan notas)
- El resultado se redondea a 2 decimales
- Si no hay materias con notas, el promedio general es None
- El cálculo se realiza automáticamente en los reportes generales

**Prioridad:** Alta  
**Estimación:** 3 puntos  
**Rol:** Sistema (automático)

---

### HU-036: Generación Automática de Códigos Institucionales
**Como** sistema  
**Quiero** generar automáticamente códigos institucionales únicos para usuarios y materias  
**Para** mantener un sistema de identificación consistente

**Criterios de Aceptación:**
- Los estudiantes reciben códigos con formato: EST-XXXX (donde XXXX es un número secuencial)
- Los profesores reciben códigos con formato: PRO-XXXX (donde XXXX es un número secuencial)
- Las materias reciben códigos con formato: MAT-XXXX (donde XXXX es un número secuencial)
- Los códigos son únicos y secuenciales
- La generación es automática al crear un nuevo usuario o materia

**Prioridad:** Alta  
**Estimación:** 3 puntos  
**Rol:** Sistema (automático)

---

## Resumen de Historias por Rol

### Administrador
- HU-002, HU-004, HU-005, HU-006, HU-007, HU-008, HU-009 (Gestión de Usuarios)
- HU-010, HU-011, HU-012, HU-013, HU-014 (Gestión de Materias)
- HU-015, HU-016, HU-017, HU-018 (Gestión de Inscripciones)
- HU-020, HU-023, HU-024, HU-026, HU-028 (Gestión de Notas)
- HU-029 (Reportes)
- HU-001, HU-003, HU-032, HU-033 (Autenticación y Perfil)

**Total: 25 historias**

### Profesor
- HU-019, HU-022, HU-024, HU-025, HU-027 (Gestión de Notas)
- HU-030 (Reportes)
- HU-001, HU-003, HU-032, HU-033 (Autenticación y Perfil)

**Total: 9 historias**

### Estudiante
- HU-021, HU-024 (Visualización de Notas)
- HU-031 (Reportes)
- HU-001, HU-003, HU-032, HU-033 (Autenticación y Perfil)

**Total: 6 historias**

### Sistema (Automático)
- HU-034, HU-035, HU-036 (Funcionalidades Automáticas)

**Total: 3 historias**

---

## Notas sobre el Formato INVEST

Todas las historias de usuario en este documento cumplen con los principios **INVEST**:

- **Independent (Independiente)**: Cada historia puede ser implementada y probada de forma independiente
- **Negotiable (Negociable)**: Los detalles pueden ser discutidos y ajustados según las necesidades
- **Valuable (Valiosa)**: Cada historia aporta valor al usuario final o al sistema
- **Estimable (Estimable)**: Se puede estimar el esfuerzo requerido (puntos de historia)
- **Small (Pequeña)**: Cada historia es lo suficientemente pequeña para completarse en un sprint
- **Testable (Testeable)**: Cada historia tiene criterios de aceptación claros y verificables

---

**Última actualización:** Diciembre 2024  
**Versión del documento:** 1.0

