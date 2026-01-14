# GUÍA COMPLETA DE HERRAMIENTAS - PROYECTO SIA SOFKA U
## Explicación Profunda de Cada Herramienta con Ejemplos

---

## ÍNDICE

1. Backend - Framework y Runtime
2. Backend - Base de Datos y ORM
3. Backend - Validación y Configuración
4. Backend - Seguridad
5. Backend - Generación de Reportes
6. Backend - Testing
7. Backend - Calidad de Código
8. Frontend - Framework y Build
9. Frontend - HTTP y Estado
10. Frontend - Estilos
11. Frontend - Testing
12. DevOps
13. Resumen Completo

---

## 1. BACKEND - FRAMEWORK Y RUNTIME

### 1.1 Python 3.11+

**¿Qué es?**
Python es un lenguaje de programación de alto nivel, interpretado y orientado a objetos.

**¿Para qué sirve?**
Es el lenguaje base del backend. Todas las herramientas backend están escritas en Python.

**Ejemplo en el proyecto:**n
# backend/app/main.py
from fastapi import FastAPI

# Python permite:
# - Type hints (mejora legibilidad)
# - Async/await (programación asíncrona)
# - Decoradores (para middleware, validación, etc.)**¿Por qué esta versión?**
- Soporte nativo de async/await
- Mejoras de rendimiento
- Type hints más robustos

---

### 1.2 FastAPI 0.104.1

**¿Qué es?**
FastAPI es un framework web moderno, rápido y asíncrono para construir APIs REST con Python.

**¿Para qué sirve?**
- Crear endpoints HTTP (GET, POST, PUT, DELETE)
- Validación automática de datos
- Documentación automática (Swagger/OpenAPI)
- Manejo de autenticación y autorización

**Ejemplo en el proyecto:**
# backend/app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint."""
    # FastAPI automáticamente:
    # 1. Valida el form_data (OAuth2PasswordRequestForm)
    # 2. Inyecta la dependencia get_db
    # 3. Serializa la respuesta usando Token schema
    # 4. Genera documentación en /docs
    user = await user_service.get_user_by_email(form_data.username)
    # ...
    return {"access_token": access_token, "token_type": "bearer"}**Características usadas:**
- Dependency Injection (`Depends()`)
- Validación automática con Pydantic
- Documentación automática en `/docs`
- Async/await nativo
- Type hints para validación

**Ejemplo de documentación automática:**
Al acceder a `http://localhost:8000/docs`, FastAPI genera una interfaz Swagger con todos los endpoints, parámetros y respuestas.

---

### 1.3 Uvicorn 0.24.0

**¿Qué es?**
Uvicorn es un servidor ASGI (Asynchronous Server Gateway Interface) ultra rápido.

**¿Para qué sirve?**
Ejecutar la aplicación FastAPI en producción y desarrollo.

**Ejemplo en el proyecto:**
# backend/entrypoint.sh (probablemente)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload**¿Qué hace?**
- Escucha en el puerto 8000
- Maneja requests HTTP asíncronos
- Soporta hot-reload en desarrollo (`--reload`)
- Gestiona workers para producción

**¿Por qué Uvicorn?**
- Rápido (basado en uvloop)
- Soporta async/await
- Compatible con ASGI
- Ideal para FastAPI

---

## 2. BACKEND - BASE DE DATOS Y ORM

### 2.1 PostgreSQL 15

**¿Qué es?**
PostgreSQL es un sistema de gestión de bases de datos relacional de código abierto.

**¿Para qué sirve?**
Almacenar todos los datos del sistema (usuarios, materias, inscripciones, notas).

**Ejemplo en el proyecto:**
# docker-compose.yml
services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: sia_sofka_db
    ports:
      - "5432:5432"**Estructura de datos:**
-- Tablas principales:
users (id, email, password_hash, role, nombre, apellido, ...)
subjects (id, nombre, codigo_institucional, profesor_id, ...)
enrollments (id, estudiante_id, subject_id, ...)
grades (id, enrollment_id, nota, periodo, fecha, ...)

-- Relaciones:
users.id → subjects.profesor_id (Foreign Key)
users.id → enrollments.estudiante_id (Foreign Key)
subjects.id → enrollments.subject_id (Foreign Key)
enrollments.id → grades.enrollment_id (Foreign Key)**¿Por qué PostgreSQL?**
- ACID (transacciones seguras)
- Foreign Keys (integridad referencial)
- Índices (mejor rendimiento)
- Escalable
- JSON nativo (si se necesita)

---

### 2.2 SQLAlchemy 2.0.23

**¿Qué es?**
SQLAlchemy es un ORM (Object-Relational Mapping) para Python.

**¿Para qué sirve?**
Interactuar con la base de datos usando objetos Python en lugar de SQL directo.

**Ejemplo en el proyecto:**
# backend/app/models/user.py
from sqlalchemy import Column, Integer, String, Date, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.core.database import Base

class User(Base):
    """User model for all roles."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    
    # Relationships
    subjects = relationship("Subject", back_populates="profesor")
    enrollments = relationship("Enrollment", back_populates="estudiante")**Ejemplo de uso en repositorio:**n
# backend/app/repositories/base.py
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

class AbstractRepository:
    async def get_by_id(self, id: int) -> Optional[ModelType]:
        # SQLAlchemy genera: SELECT * FROM users WHERE id = ?
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, data: Dict[str, Any]) -> ModelType:
        # SQLAlchemy genera: INSERT INTO users (...) VALUES (...)
        instance = self.model(**data)
        self.db.add(instance)
        await self.db.commit()
        return instance**Ventajas:**
- Queries type-safe
- Protección contra SQL injection
- Migraciones con Alembic
- Relaciones automáticas
- Lazy/Eager loading

---

### 2.3 asyncpg 0.29.0

**¿Qué es?**
asyncpg es un driver asíncrono para PostgreSQL.

**¿Para qué sirve?**
Conectar SQLAlchemy async con PostgreSQL de forma eficiente.

**Ejemplo en el proyecto:**
# backend/app/core/database.py
from sqlalchemy.ext.asyncio import create_async_engine

# Connection string usa asyncpg
DATABASE_URL = "postgresql+asyncpg://postgres:postgres@db:5432/sia_sofka_db"

engine = create_async_engine(
    settings.database_url,  # Usa asyncpg internamente
    echo=settings.debug,
    future=True,
)**¿Qué hace?**
- Conexiones asíncronas (no bloquea el event loop)
- Pool de conexiones eficiente
- Alto rendimiento

**¿Por qué asyncpg?**
- Más rápido que psycopg2 en async
- Escrito en Cython
- Optimizado para async/await

---

### 2.4 psycopg2-binary 2.9.9

**¿Qué es?**
psycopg2 es un driver síncrono para PostgreSQL.

**¿Para qué sirve?**
Alembic y operaciones síncronas.

**Ejemplo en el proyecto:**
# Alembic usa psycopg2 para migraciones
DATABASE_URL_SYNC = "postgresql://postgres:postgres@db:5432/sia_sofka_db"
# ↑ Sin "asyncpg", usa psycopg2**¿Cuándo se usa?**
- Migraciones de Alembic (síncronas)
- Scripts de administración
- Operaciones que no requieren async

---

### 2.5 Alembic 1.12.1

**¿Qué es?**
Alembic es una herramienta de migraciones para SQLAlchemy.

**¿Para qué sirve?**
Versionar y aplicar cambios en el esquema de la base de datos.

**Ejemplo en el proyecto:**
# backend/alembic.ini
[alembic]
script_location = alembic
# Configuración de migraciones**Uso típico:**
# Crear nueva migración
alembic revision --autogenerate -m "Add new column to users"

# Aplicar migraciones
alembic upgrade head

# Revertir migración
alembic downgrade -1**Ejemplo de migración generada:**
# alembic/versions/xxx_add_column.py
def upgrade():
    op.add_column('users', sa.Column('nuevo_campo', sa.String(100)))

def downgrade():
    op.drop_column('users', 'nuevo_campo')**Ventajas:**
- Versionado del esquema
- Rollback seguro
- Migraciones automáticas desde modelos
- Historial de cambios

---

## 3. BACKEND - VALIDACIÓN Y CONFIGURACIÓN

### 3.1 Pydantic 2.5.0

**¿Qué es?**
Pydantic es una biblioteca de validación de datos usando type hints de Python.

**¿Para qué sirve?**
Validar y serializar datos de entrada/salida de la API.

**Ejemplo en el proyecto:**
# backend/app/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, field_validator

class UserCreate(UserBase):
    """Schema for creating a user."""
    password: str = Field(..., min_length=6)  # ✅ Validación: mínimo 6 caracteres
    role: UserRole
    programa_academico: Optional[str] = None
    
    @field_validator('email')
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate and normalize email address."""
        return validate_email(v)  # ✅ Validación personalizada**Ejemplo de uso en endpoint:**
# backend/app/api/v1/endpoints/auth.py
@router.post("/register", response_model=UserResponse)
async def register(
    user_data: UserCreate,  # ✅ Pydantic valida automáticamente
    db: AsyncSession = Depends(get_db),
):
    # Si user_data no cumple validaciones, FastAPI retorna 422 automáticamente
    # Si password tiene menos de 6 caracteres → Error 422
    # Si email es inválido → Error 422
    user = await user_service.create_user(user_data)
    return user**Validaciones automáticas:**
- Tipos de datos
- Longitud de strings
- Rangos numéricos
- Formatos (email, URL, etc.)
- Validadores personalizados

**Ejemplo de respuesta automática:**
// Si envías password: "123" (menos de 6 caracteres)
{
  "detail": [
    {
      "loc": ["body", "password"],
      "msg": "ensure this value has at least 6 characters",
      "type": "value_error.any_str.min_length"
    }
  ]
}---

### 3.2 Pydantic Settings 2.1.0

**¿Qué es?**
Extensión de Pydantic para gestión de configuración.

**¿Para qué sirve?**
Cargar y validar variables de entorno.

**Ejemplo en el proyecto:**
# backend/app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Database
    database_url: str  # ✅ Requerido, se carga de DATABASE_URL
    database_url_sync: str
    
    # Security
    secret_key: str
    
    @field_validator('secret_key')
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Validate secret key strength."""
        if len(v) < 32:
            warnings.warn("SECRET_KEY is too short")
        return v
    
    model_config = SettingsConfigDict(
        env_file=".env",  # ✅ Lee archivo .env automáticamente
        env_file_encoding="utf-8",
        case_sensitive=False,  # ✅ DATABASE_URL = database_url
    )

settings = Settings()  # ✅ Carga automática de .env**Ejemplo de uso:**
# backend/app/core/database.py
from app.core.config import settings

# settings.database_url se carga automáticamente de DATABASE_URL en .env
engine = create_async_engine(settings.database_url)**Ventajas:**
- Validación de configuración
- Type safety
- Carga desde .env
- Valores por defecto
- Validadores personalizados

---

## 4. BACKEND - SEGURIDAD

### 4.1 python-jose[cryptography] 3.3.0

**¿Qué es?**
python-jose es una biblioteca para crear y validar tokens JWT (JSON Web Tokens).

**¿Para qué sirve?**
Autenticación con tokens JWT.

**Ejemplo en el proyecto:**
# backend/app/core/security.py
from jose import JWTError, jwt

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token."""
    to_encode = data.copy()
    
    # Agregar expiración
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    
    # ✅ Crear token JWT firmado con SECRET_KEY
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.secret_key, 
        algorithm=settings.algorithm  # HS256
    )
    return encoded_jwt

def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and verify a JWT access token."""
    try:
        # ✅ Verificar firma y expiración
        payload = jwt.decode(
            token, 
            settings.secret_key, 
            algorithms=[settings.algorithm]
        )
        return payload
    except JWTError:
        raise JWTError("Could not validate credentials")**Ejemplo de uso:**on
# backend/app/api/v1/endpoints/auth.py
@router.post("/login")
async def login(...):
    # Crear token con email y rol
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}**Estructura del token:**
{
  "sub": "admin@sofka.edu.co",  // Subject (email del usuario)
  "role": "Admin",              // Rol del usuario
  "exp": 1234567890             // Expiración (timestamp)
}**¿Por qué python-jose?**
- Estándar JWT
- Firma criptográfica
- Validación de expiración
- Múltiples algoritmos (HS256, RS256, etc.)

---

### 4.2 passlib[bcrypt] 1.7.4

**¿Qué es?**
passlib es una biblioteca para hashing de contraseñas. bcrypt es el algoritmo que usa.

**¿Para qué sirve?**
Almacenar contraseñas de forma segura (hash, no texto plano).

**Ejemplo en el proyecto:**
# backend/app/core/security.py
import bcrypt

def get_password_hash(password: str) -> str:
    """Hash a password."""
    password_bytes = password.encode('utf-8')
    # ✅ Generar salt y hash con bcrypt (12 rounds)
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain password against a hashed password."""
    # ✅ Comparar password plano con hash
    return bcrypt.checkpw(
        plain_password.encode('utf-8'), 
        hashed_password.encode('utf-8')
    )**Ejemplo de uso:**
# Al crear usuario
password_hash = get_password_hash("mi_password_123")
# Resultado: "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5K5j5K5j5K5j5K"

# Al verificar login
is_valid = verify_password("mi_password_123", user.password_hash)
# ✅ Compara sin desencriptar (imposible)**¿Por qué bcrypt?**
- Algoritmo seguro (blowfish)
- Salt automático
- Coste configurable (12 rounds = ~250ms)
- Resistente a rainbow tables

**Ejemplo de seguridad:**on
# ❌ NUNCA hacer esto:
user.password = "password123"  # Texto plano

# ✅ SIEMPRE hacer esto:
user.password_hash = get_password_hash("password123")
# Almacenado: "$2b$12$..." (hash irreversible)---

## 5. BACKEND - GENERACIÓN DE REPORTES

### 5.1 ReportLab 4.0.7

**¿Qué es?**
ReportLab es una biblioteca para generar PDFs programáticamente.

**¿Para qué sirve?**
Crear reportes académicos en PDF.

**Ejemplo en el proyecto:**
# backend/app/factories/pdf_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors

@ReportFactory.register('pdf')
class PDFReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # ✅ Crear título con estilo personalizado
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Heading1"],
            fontSize=18,
            textColor=colors.HexColor("#1a237e"),
        )
        story.append(Paragraph("Reporte Académico", title_style))
        story.append(Spacer(1, 0.2 * inch))
        
        # ✅ Crear tabla de notas
        table_data = [["Materia", "Código", "Créditos", "Promedio"]]
        for subject_info in data["subjects"]:
            table_data.append([
                subject_info["subject"]["nombre"],
                subject_info["subject"]["codigo_institucional"],
                str(subject_info["subject"]["numero_creditos"]),
                f"{subject_info['average']:.2f}" if subject_info['average'] else "N/A"
            ])
        
        table = Table(table_data, colWidths=[2*inch, 1.5*inch, 1*inch, 1*inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # Header gris
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Bordes
        ]))
        story.append(table)
        
        # ✅ Construir PDF
        doc.build(story)
        return {
            'content': buffer.getvalue(),
            'filename': f'reporte_{datetime.now().strftime("%Y%m%d")}.pdf',
            'content_type': 'application/pdf'
        }**Características usadas:**
- Páginas con tamaño personalizado
- Estilos de texto
- Tablas con formato
- Colores personalizados
- Espaciado y márgenes

**Resultado:**
PDF profesional con formato estructurado.

---

### 5.2 Jinja2 3.1.2

**¿Qué es?**
Jinja2 es un motor de templates para Python.

**¿Para qué sirve?**
Generar reportes HTML dinámicos.

**Ejemplo en el proyecto:**thon
# backend/app/factories/html_generator.py
from jinja2 import Template

@ReportFactory.register('html')
class HTMLReportGenerator(ReportGenerator):
    def generate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # ✅ Template HTML con variables
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <title>Reporte Académico</title>
</head>
<body>
    <h1>Reporte de {{ estudiante.nombre }} {{ estudiante.apellido }}</h1>
    
    {% for subject_info in subjects %}
    <div class="subject">
        <h2>{{ subject_info.subject.nombre }}</h2>
        <p>Promedio: {{ subject_info.average|round(2) if subject_info.average else 'N/A' }}</p>
        
        <table>
            <tr><th>Nota</th><th>Período</th><th>Fecha</th></tr>
            {% for grade in subject_info.grades %}
            <tr>
                <td>{{ grade.nota }}</td>
                <td>{{ grade.periodo }}</td>
                <td>{{ grade.fecha }}</td>
            </tr>
            {% endfor %}
        </table>
    </div>
    {% endfor %}
</body>
</html>
        """
        
        # ✅ Renderizar template con datos
        template = Template(template_str)
        html_content = template.render(
            estudiante=data.get("estudiante"),
            subjects=data.get("subjects", [])
        )
        
        return {
            'content': html_content.encode('utf-8'),
            'filename': f'reporte_{datetime.now().strftime("%Y%m%d")}.html',
            'content_type': 'text/html'
        }**Características de Jinja2:**
- Variables: `{{ variable }}`
- Loops: `{% for item in list %}`
- Condicionales: `{% if condition %}`
- Filtros: `{{ value|round(2) }}`
- Herencia de templates

**Ventajas:**
- Separación de lógica y presentación
- Templates reutilizables
- Fácil de mantener
- Escapado automático de HTML (seguridad)

---

## 6. BACKEND - TESTING

### 6.1 pytest 7.4.3

**¿Qué es?**
pytest es un framework de testing para Python.

**¿Para qué sirve?**
Ejecutar tests unitarios e integración.

**Ejemplo en el proyecto:**thon
# backend/tests/unit/test_services.py
import pytest
from app.services.user_service import UserService

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Test creating a user."""
    service = UserService(db_session)
    user_data = UserCreate(
        email="test@example.com",
        password="password123",
        nombre="Test",
        apellido="User",
        role=UserRole.ESTUDIANTE,
        fecha_nacimiento=date(2000, 1, 1)
    )
    
    user = await service.create_user(user_data)
    
    # ✅ Assertions
    assert user.email == "test@example.com"
    assert user.role == UserRole.ESTUDIANTE
    assert user.codigo_institucional.startswith("EST-")**Ejecución:**
# Ejecutar todos los tests
pytest

# Ejecutar con verbose
pytest -v

# Ejecutar tests específicos
pytest tests/unit/test_services.py::test_create_user

# Ejecutar con coverage
pytest --cov=app --cov-report=html**Características usadas:**
- Fixtures (`@pytest.fixture`)
- Markers (`@pytest.mark.asyncio`, `@pytest.mark.unit`)
- Parametrización (`@pytest.mark.parametrize`)
- Assertions
- Plugins (pytest-asyncio, pytest-cov)

---

### 6.2 pytest-asyncio 0.21.1

**¿Qué es?**
Plugin de pytest para testing asíncrono.

**¿Para qué sirve?**
Ejecutar tests de funciones async.

**Ejemplo en el proyecto:**ython
# backend/tests/conftest.py
import pytest

@pytest.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",  # ✅ Base de datos en memoria
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ✅ Crear tablas
    
    async_session = async_sessionmaker(engine, class_=AsyncSession)
    
    async with async_session() as session:
        yield session  # ✅ Proporcionar sesión para tests
        await session.rollback()
    
    # ✅ Limpiar después del test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)**Ejemplo de test async:**
# backend/tests/unit/test_services.py
@pytest.mark.asyncio  # ✅ Marca test como async
async def test_get_user_by_email(db_session):
    """Test getting user by email."""
    service = UserService(db_session)
    
    # ✅ Usar await en llamadas async
    user = await service.get_user_by_email("test@example.com")
    
    assert user is not None
    assert user.email == "test@example.com"**¿Por qué pytest-asyncio?**
- Ejecuta funciones async correctamente
- Maneja event loops
- Compatible con FastAPI async

---

### 6.3 pytest-cov 4.1.0

**¿Qué es?**
Plugin de pytest para medir cobertura de código.

**¿Para qué sirve?**
Ver qué porcentaje del código está cubierto por tests.

**Ejemplo en el proyecto:**
# Ejecutar tests con coverage
pytest --cov=app --cov-report=html --cov-report=term

# Resultado:
# Name                          Stmts   Miss  Cover
# -------------------------------------------------
# app/services/user_service.py     137      0   100%
# app/services/grade_service.py    129      0   100%
# ...
# -------------------------------------------------
# TOTAL                           2500    325    87%
**Configuración:**
# backend/pytest.ini
[pytest]
addopts = 
    --cov=app
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=80  # ✅ Falla si coverage < 80%**Reporte HTML:**
Genera `htmlcov/index.html` con visualización interactiva, mostrando líneas cubiertas/no cubiertas.

---

### 6.4 httpx 0.25.2

**¿Qué es?**
Cliente HTTP asíncrono para Python.

**¿Para qué sirve?**
Hacer requests HTTP en tests de integración.

**Ejemplo en el proyecto:**
# backend/tests/conftest.py
from httpx import AsyncClient

@pytest.fixture
async def client(db_session):
    """Create a test client."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # ✅ Cliente HTTP para testear endpoints
    async with AsyncClient(app=app, base_url="http://test") as test_client:
        yield test_client
    
    app.dependency_overrides.clear()**Ejemplo de test de integración:**
# backend/tests/integration/test_endpoints.py
@pytest.mark.asyncio
async def test_login_endpoint(client):
    """Test login endpoint."""
    # ✅ Hacer request HTTP al endpoint
    response = await client.post(
        "/api/v1/auth/login",
        data={
            "username": "admin@sofka.edu.co",
            "password": "admin123"
        }
    )
    
    # ✅ Verificar respuesta
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert response.json()["token_type"] == "bearer"**Ventajas:**
- Async/await
- Compatible con FastAPI
- Soporta cookies, headers, etc.
- Útil para tests E2E

---

### 6.5 aiosqlite 0.19.0

**¿Qué es?**
Driver asíncrono para SQLite.

**¿Para qué sirve?**
Base de datos en memoria para tests (más rápido que PostgreSQL).

**Ejemplo en el proyecto:**
# backend/tests/conftest.py
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def db_session():
    """Create a test database session."""
    engine = create_async_engine(
        TEST_DATABASE_URL,  # ✅ SQLite en memoria (no archivo)
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # ...
**Ventajas:**
- Rápido (en memoria)
- No requiere PostgreSQL en CI
- Aislado por test
- Compatible con SQLAlchemy async

---

## 7. BACKEND - CALIDAD DE CÓDIGO

### 7.1 Black 23.11.0

**¿Qué es?**
Black es un formateador automático de código Python.

**¿Para qué sirve?**
Mantener estilo de código consistente.

**Ejemplo en el proyecto:**
# Antes de Black (inconsistente):
def create_user(self,user_data:UserCreate)->User:
    if user_data.role==UserRole.ESTUDIANTE:
        return await self.user_service.create_user(user_data)

# Después de Black (formateado):
def create_user(self, user_data: UserCreate) -> User:
    if user_data.role == UserRole.ESTUDIANTE:
        return await self.user_service.create_user(user_data)**Configuración:**
# backend/pyproject.toml
[tool.black]
line-length = 120
target-version = ['py311', 'py312']**Uso:**
# Formatear código
black app tests

# Verificar sin modificar
black --check app tests**Características:**
- Formato consistente
- Sin decisiones de estilo
- Integración con pre-commit
- Configurable

---

### 7.2 flake8 6.1.0

**¿Qué es?**
flake8 es un linter para Python (detecta errores y problemas de estilo).

**¿Para qué sirve?**
Encontrar bugs, código problemático y violaciones de estilo.

**Ejemplo en el proyecto:**on
# Código problemático que flake8 detectaría:
def create_user(self, user_data):  # ❌ Sin type hints
    x = 10
    y = 20
    z = x + y  # ❌ Variable no usada
    return user_data  # ❌ Línea muy larga (más de 127 caracteres)**Configuración:**l
# backend/pyproject.toml
[tool.flake8]
max-line-length = 127
max-complexity = 10
extend-ignore = ["E203", "E266", "E501", "W503"]**Errores que detecta:**
- E9: Errores de sintaxis
- F: Pyflakes (código no usado, imports no usados)
- W: Warnings
- C: Complejidad ciclomática

**Ejemplo de uso:**sh
# Ejecutar flake8
flake8 app tests

# Con estadísticas
flake8 app tests --statistics---

### 7.3 mypy 1.7.1

**¿Qué es?**
mypy es un type checker estático para Python.

**¿Para qué sirve?**
Verificar que los type hints sean correctos.

**Ejemplo en el proyecto:**
# backend/app/services/user_service.py
from typing import Optional

class UserService:
    async def get_user_by_id(self, user_id: int) -> Optional[User]:
        # ✅ mypy verifica que:
        # - user_id es int
        # - Retorna Optional[User] (User o None)
        return await self.repository.get_by_id(user_id)**Ejemplo de error que mypy detectaría:**
# ❌ Error de tipo
def create_user(self, user_id: int) -> User:
    return "not a user"  # ❌ mypy: Incompatible return type "str" (expected "User")**Configuración:**
# backend/pyproject.toml
[tool.mypy]
python_version = "3.11"
warn_return_any = true
disallow_untyped_defs = false
ignore_missing_imports = true
plugins = ["pydantic.mypy"]  # ✅ Soporte para Pydantic
**Ventajas:**
- Detecta errores antes de ejecutar
- Mejora la legibilidad
- Facilita refactorización
- Integración con IDEs

---

### 7.4 isort 5.13.2

**¿Qué es?**
isort es una herramienta para ordenar imports.

**¿Para qué sirve?**
Mantener imports organizados y consistentes.

**Ejemplo en el proyecto:**
# Antes de isort (desordenado):
from app.models.user import User
from app.core.database import get_db
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.user import UserCreate

# Después de isort (ordenado):
from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate**Configuración:**ml
# backend/pyproject.toml
[tool.isort]
profile = "black"  # ✅ Compatible con Black
line_length = 120
known_third_party = ["fastapi", "pydantic", "sqlalchemy"]
sections = ["FUTURE", "STDLIB", "THIRDPARTY", "FIRSTPARTY", "LOCALFOLDER"]
**Orden de imports:**
1. Futuros (`from __future__ import ...`)
2. Librería estándar (`import os`, `import sys`)
3. Terceros (`import fastapi`, `import sqlalchemy`)
4. Primera parte (`from app.core import ...`)
5. Local (`from .models import ...`)

---

### 7.5 pre-commit 3.6.0

**¿Qué es?**
pre-commit es un framework para git hooks.

**¿Para qué sirve?**
Ejecutar verificaciones antes de cada commit.

**Ejemplo en el proyecto:**
# backend/.pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.1
    hooks:
      - id: black
        args: ['--line-length=120']
  
  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        args: ['--max-line-length=127', '--max-complexity=10']
  
  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        args: ['--profile=black']**¿Qué hace?**
Antes de cada commit ejecuta:
1. Black (formateo)
2. flake8 (linting)
3. isort (orden de imports)
4. mypy (type checking)

Si algo falla, el commit se bloquea.

**Uso:**ash
# Instalar hooks
pre-commit install

# Ejecutar manualmente
pre-commit run --all-files**Ventajas:**
- Calidad automática
- Estilo consistente
- Menos errores en CI
- Ahorra tiempo

---

## 8. FRONTEND - FRAMEWORK Y BUILD

### 8.1 React 18.3.1

**¿Qué es?**
React es una biblioteca de JavaScript para construir interfaces de usuario.

**¿Para qué sirve?**
Crear la interfaz del sistema.

**Ejemplo en el proyecto:**
// frontend/src/components/dashboard/Users.jsx
import { useState, useEffect } from 'react'
import { userService } from '../../services/apiService'

function Users() {
  // ✅ Estado local con useState
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  
  // ✅ Efecto para cargar datos al montar componente
  useEffect(() => {
    loadUsers()
  }, [])
  
  const loadUsers = async () => {
    try {
      setLoading(true)
      const data = await userService.getAll()
      setUsers(data)  // ✅ Actualizar estado
    } catch (error) {
      console.error('Error loading users:', error)
    } finally {
      setLoading(false)
    }
  }
  
  // ✅ Render condicional
  if (loading) {
    return <div>Cargando...</div>
  }
  
  return (
    <div>
      <h1>Usuarios</h1>
      {users.map(user => (
        <div key={user.id}>{user.nombre} {user.apellido}</div>
      ))}
    </div>
  )
}**Características usadas:**
- Hooks (`useState`, `useEffect`, `useContext`)
- Componentes funcionales
- JSX
- Props
- Estado local y global

---

### 8.2 Vite 5.4.2

**¿Qué es?**
Vite es un build tool y dev server ultra rápido para aplicaciones frontend.

**¿Para qué sirve?**
Desarrollo rápido y builds optimizados.

**Ejemplo en el proyecto:**
// frontend/vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0',  // ✅ Acceso desde Docker
    port: 3000,
    watch: {
      usePolling: true,  // ✅ Hot-reload en Docker
    },
    proxy: {
      '/api': {
        target: 'http://api:8000',  // ✅ Proxy a backend
        changeOrigin: true,
      },
    },
  },
})**Características:**
- Hot Module Replacement (HMR)
- Build rápido (esbuild)
- Optimización automática
- Proxy para desarrollo

**Uso:**
# Desarrollo
npm run dev  # Inicia servidor en http://localhost:3000

# Build producción
npm run build  # Genera archivos optimizados en dist/**Ventajas sobre Webpack:**
- Más rápido (10-100x)
- Configuración simple
- HMR instantáneo
- Optimización automática

---

### 8.3 React Router DOM 6.20.0

**¿Qué es?**
React Router es una librería de enrutamiento para React.

**¿Para qué sirve?**
Navegación entre páginas (SPA).

**Ejemplo en el proyecto:**cript
// frontend/src/App.jsx
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Login from './components/auth/Login'
import DashboardLayout from './components/layout/DashboardLayout'

function App() {
  const { isAuthenticated } = useAuth()
  
  return (
    <BrowserRouter>
      <Routes>
        {/* ✅ Ruta pública */}
        <Route path="/login" element={<Login />} />
        
        {/* ✅ Rutas protegidas */}
        <Route 
          path="/dashboard/*" 
          element={
            isAuthenticated ? (
              <DashboardLayout />
            ) : (
              <Navigate to="/login" />  // ✅ Redirigir si no autenticado
            )
          } 
        />
        
        {/* ✅ Ruta por defecto */}
        <Route path="/" element={<Navigate to="/dashboard" />} />
      </Routes>
    </BrowserRouter>
  )
}**Ejemplo de navegación:**ascript
// frontend/src/components/layout/Sidebar.jsx
import { useNavigate, useLocation } from 'react-router-dom'

function Sidebar() {
  const navigate = useNavigate()
  const location = useLocation()
  
  const handleNavigation = (path) => {
    navigate(path)  // ✅ Navegar programáticamente
  }
  
  return (
    <nav>
      <button 
        onClick={() => handleNavigation('/dashboard/users')}
        className={location.pathname === '/dashboard/users' ? 'active' : ''}
      >
        Usuarios
      </button>
    </nav>
  )
}**Características:**
- Rutas declarativas
- Navegación programática
- Rutas protegidas
- Parámetros de URL
- Nested routes

---

## 9. FRONTEND - HTTP Y ESTADO

### 9.1 Axios 1.6.2

**¿Qué es?**
Axios es un cliente HTTP para JavaScript.

**¿Para qué sirve?**
Hacer requests al backend API.

**Ejemplo en el proyecto:**avascript
// frontend/src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: API_BASE_URL,  // ✅ URL base: http://localhost:8000/api/v1
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000,  // ✅ Timeout de 10 segundos
})

// ✅ Interceptor para agregar token automáticamente
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`  // ✅ JWT automático
    }
    return config
  },
  (error) => Promise.reject(error)
)

// ✅ Interceptor para manejar errores
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // ✅ Redirigir a login si token inválido
      localStorage.removeItem('token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)**Ejemplo de uso:**ipt
// frontend/src/services/apiService.js
import api from './api'

export const userService = {
  // ✅ GET request
  getAll: async () => {
    const response = await api.get('/users')
    return response.data
  },
  
  // ✅ POST request
  create: async (userData) => {
    const response = await api.post('/users', userData)
    return response.data
  },
  
  // ✅ PUT request
  update: async (id, userData) => {
    const response = await api.put(`/users/${id}`, userData)
    return response.data
  },
  
  // ✅ DELETE request
  delete: async (id) => {
    await api.delete(`/users/${id}`)
  },
}**Ventajas:**
- Interceptores (agregar token, manejar errores)
- Timeout automático
- Transformación de datos
- Cancelación de requests
- Mejor que `fetch` nativo

---

### 9.2 React Context API

**¿Qué es?**
Context API es una API nativa de React para estado global.

**¿Para qué sirve?**
Compartir estado entre componentes sin prop drilling.

**Ejemplo en el proyecto:**
// frontend/src/context/AuthContext.jsx
import { createContext, useContext, useState, useEffect } from 'react'

// ✅ Crear contexto
const AuthContext = createContext(null)

// ✅ Hook personalizado para usar contexto
export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}

// ✅ Provider que envuelve la app
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  
  // ✅ Cargar usuario del localStorage al iniciar
  useEffect(() => {
    const token = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (token && savedUser) {
      setUser(JSON.parse(savedUser))
    }
    setLoading(false)
  }, [])
  
  // ✅ Función de login
  const login = async (email, password) => {
    const response = await api.post('/auth/login', formData)
    const { access_token } = response.data
    
    localStorage.setItem('token', access_token)
    
    const userResponse = await api.get('/auth/me')
    setUser(userResponse.data)
    
    return { success: true }
  }
  
  // ✅ Función de logout
  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    setUser(null)
  }
  
  const value = {
    user,
    loading,
    login,
    logout,
    isAuthenticated: !!user,
  }
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}**Ejemplo de uso:**
// frontend/src/components/dashboard/DashboardHome.jsx
import { useAuth } from '../../context/AuthContext'

function DashboardHome() {
  // ✅ Acceder a estado global sin props
  const { user, isAuthenticated, logout } = useAuth()
  
  if (!isAuthenticated) {
    return <div>No autenticado</div>
  }
  
  return (
    <div>
      <h1>Bienvenido, {user.nombre}</h1>
      <button onClick={logout}>Cerrar Sesión</button>
    </div>
  )
}**Ventajas:**
- Estado global sin prop drilling
- Fácil de usar
- Integrado en React
- Alternativa ligera a Redux

---

## 10. FRONTEND - ESTILOS

### 10.1 Tailwind CSS 3.4.1

**¿Qué es?**
Tailwind CSS es un framework CSS utility-first.

**¿Para qué sirve?**
Estilizar componentes con clases utilitarias.

**Ejemplo en el proyecto:**script
// frontend/src/components/dashboard/Users.jsx
function Users() {
  return (
    <div className="p-6 bg-white rounded-lg shadow-md">
      {/* ✅ p-6 = padding: 1.5rem
          ✅ bg-white = background-color: white
          ✅ rounded-lg = border-radius: 0.5rem
          ✅ shadow-md = box-shadow */}
      
      <h1 className="text-2xl font-bold text-gray-800 mb-4">
        {/* ✅ text-2xl = font-size: 1.5rem
            ✅ font-bold = font-weight: bold
            ✅ text-gray-800 = color: gray-800
            ✅ mb-4 = margin-bottom: 1rem */}
        Usuarios
      </h1>
      
      <button className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
        {/* ✅ px-4 = padding-x: 1rem
            ✅ py-2 = padding-y: 0.5rem
            ✅ bg-blue-600 = background: blue-600
            ✅ hover:bg-blue-700 = hover state */}
        Crear Usuario
      </button>
    </div>
  )
}**Configuración:**
// frontend/tailwind.config.js
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",  // ✅ Escanear archivos para purging
  ],
  theme: {
    extend: {
      colors: {
        primary: '#1a237e',  // ✅ Colores personalizados
      },
    },
  },
}**Ventajas:**
- Desarrollo rápido
- Consistencia
- Responsive fácil (`md:`, `lg:`)
- Purging automático (solo CSS usado)
- Sin CSS custom (utility-first)

---

### 10.2 PostCSS 8.4.47

**¿Qué es?**
PostCSS es una herramienta para transformar CSS con plugins.

**¿Para qué sirve?**
Procesar Tailwind CSS y aplicar transformaciones.

**Ejemplo en el proyecto:**cript
// frontend/postcss.config.js
export default {
  plugins: {
    tailwindcss: {},  // ✅ Procesar Tailwind
    autoprefixer: {},  // ✅ Agregar vendor prefixes
  },
}**¿Qué hace?**
1. Tailwind procesa las clases utilitarias
2. Autoprefixer agrega `-webkit-`, `-moz-`, etc.
3. Genera CSS final optimizado

**Ejemplo de transformación:**
/* Input (Tailwind classes) */
.class {
  @apply flex items-center;
}

/* Output (CSS procesado) */
.class {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
  -webkit-box-align: center;
  -ms-flex-align: center;
  align-items: center;
}---

### 10.3 Autoprefixer 10.4.20

**¿Qué es?**
Autoprefixer es un plugin de PostCSS que agrega vendor prefixes.

**¿Para qué sirve?**
Compatibilidad con navegadores antiguos.

**Ejemplo:**
/* Antes de Autoprefixer */
.flex {
  display: flex;
}

/* Después de Autoprefixer */
.flex {
  display: -webkit-box;
  display: -ms-flexbox;
  display: flex;
}**Ventajas:**
- Compatibilidad automática
- Basado en caniuse.com
- Configurable

---

## 11. FRONTEND - TESTING

### 11.1 Playwright 1.57.0

**¿Qué es?**
Playwright es un framework de testing E2E para navegadores.

**¿Para qué sirve?**
Probar la aplicación completa en navegador real.

**Ejemplo en el proyecto:**ipt
// frontend/tests/e2e/auth.spec.js
import { test, expect } from '@playwright/test'

test('should login successfully', async ({ page }) => {
  // ✅ Navegar a la página
  await page.goto('http://localhost:3000/login')
  
  // ✅ Llenar formulario
  await page.fill('input[name="email"]', 'admin@sofka.edu.co')
  await page.fill('input[name="password"]', 'admin123')
  
  // ✅ Hacer click en botón
  await page.click('button[type="submit"]')
  
  // ✅ Esperar redirección
  await page.waitForURL('**/dashboard')
  
  // ✅ Verificar que está en dashboard
  expect(page.url()).toContain('/dashboard')
  
  // ✅ Verificar que se muestra el nombre del usuario
  await expect(page.locator('text=Admin')).toBeVisible()
})**Características:**
- Múltiples navegadores (Chromium, Firefox, WebKit)
- Screenshots automáticos
- Videos de tests fallidos
- Timeout automático
- Selectores potentes

**Uso:**
# Ejecutar tests
npm run test:e2e

# Con UI interactiva
npm run test:e2e:ui

# En modo headed (ver navegador)
npm run test:e2e:headed---

## 12. DEVOPS

### 12.1 Docker

**¿Qué es?**
Docker es una plataforma de containerización.

**¿Para qué sirve?**
Empaquetar la aplicación y sus dependencias en contenedores.

**Ejemplo en el proyecto:**kerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# ✅ Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl

# ✅ Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Copiar código de la aplicación
COPY . .

# ✅ Exponer puerto
EXPOSE 8000

# ✅ Comando para ejecutar
CMD ["./entrypoint.sh"]**Ventajas:**
- Entorno consistente
- Aislamiento
- Portabilidad
- Escalabilidad

---

### 12.2 Docker Compose 3.8

**¿Qué es?**
Docker Compose es una herramienta para orquestar múltiples contenedores.

**¿Para qué sirve?**
Levantar toda la aplicación (backend, frontend, BD) con un comando.

**Ejemplo en el proyecto:**
# docker-compose.yml
version: '3.8'

services:
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: sia_sofka_db
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  api:
    build: ./backend
    depends_on:
      db:
        condition: service_healthy  # ✅ Esperar que BD esté lista
    ports:
      - "8000:8000"

  frontend:
    build: ./frontend
    depends_on:
      - api  # ✅ Esperar que API esté lista
    ports:
      - "3000:3000"**Uso:**
# Levantar todo
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener todo
docker-compose down**Ventajas:**
- Un comando para todo
- Dependencias automáticas
- Red compartida
- Volúmenes persistentes

---

### 12.3 GitHub Actions

**¿Qué es?**
GitHub Actions es una plataforma de CI/CD integrada en GitHub.

**¿Para qué sirve?**
Automatizar tests, linting y despliegues.

**Ejemplo en el proyecto:**aml
# .github/workflows/ci.yml
name: CI Pipeline

on:
  push:
    branches: ['**']
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: pytest --cov=app
    
    - name: Check coverage
      run: coverage report --fail-under=80**¿Qué hace?**
1. Se ejecuta en cada push
2. Instala dependencias
3. Ejecuta tests
4. Verifica coverage
5. Falla si algo no pasa

**Ventajas:**
- Automatización
- Feedback rápido
- Calidad garantizada
- Historial de ejecuciones

---

## 13. RESUMEN COMPLETO DE HERRAMIENTAS

| Categoría | Herramienta | Versión | Propósito Principal |
|-----------|-------------|---------|---------------------|
| **Backend Framework** | FastAPI | 0.104.1 | API REST asíncrona |
| **Backend Runtime** | Uvicorn | 0.24.0 | Servidor ASGI |
| **Base de Datos** | PostgreSQL | 15 | BD relacional |
| **ORM** | SQLAlchemy | 2.0.23 | Mapeo objeto-relacional |
| **Drivers BD** | asyncpg | 0.29.0 | Driver async PostgreSQL |
| **Drivers BD** | psycopg2-binary | 2.9.9 | Driver sync PostgreSQL |
| **Migraciones** | Alembic | 1.12.1 | Migraciones de BD |
| **Validación** | Pydantic | 2.5.0 | Validación de datos |
| **Configuración** | Pydantic Settings | 2.1.0 | Gestión de configuración |
| **Seguridad** | python-jose | 3.3.0 | Tokens JWT |
| **Seguridad** | bcrypt | - | Hashing de contraseñas |
| **Reportes** | ReportLab | 4.0.7 | Generación de PDFs |
| **Reportes** | Jinja2 | 3.1.2 | Templates HTML |
| **Testing** | pytest | 7.4.3 | Framework de tests |
| **Testing** | pytest-asyncio | 0.21.1 | Tests asíncronos |
| **Testing** | pytest-cov | 4.1.0 | Cobertura de código |
| **Testing** | httpx | 0.25.2 | Cliente HTTP para tests |
| **Testing** | aiosqlite | 0.19.0 | BD en memoria para tests |
| **Calidad** | Black | 23.11.0 | Formateo de código |
| **Calidad** | flake8 | 6.1.0 | Linting |
| **Calidad** | mypy | 1.7.1 | Type checking |
| **Calidad** | isort | 5.13.2 | Orden de imports |
| **Calidad** | pre-commit | 3.6.0 | Git hooks |
| **Frontend** | React | 18.3.1 | UI library |
| **Frontend** | Vite | 5.4.2 | Build tool |
| **Frontend** | React Router | 6.20.0 | Enrutamiento |
| **Frontend** | Axios | 1.6.2 | Cliente HTTP |
| **Frontend** | Tailwind CSS | 3.4.1 | Framework CSS |
| **Frontend** | PostCSS | 8.4.47 | Procesador CSS |
| **Frontend** | Autoprefixer | 10.4.20 | Vendor prefixes |
| **Frontend** | Playwright | 1.57.0 | Testing E2E |
| **DevOps** | Docker | - | Containerización |
| **DevOps** | Docker Compose | 3.8 | Orquestación |
| **DevOps** | GitHub Actions | - | CI/CD |

---

## CONCLUSIÓN

El proyecto SIA SOFKA U utiliza un stack tecnológico moderno y probado:
- **Backend**: FastAPI + SQLAlchemy + PostgreSQL
- **Frontend**: React + Vite + Tailwind
- **Testing**: pytest + Playwright
- **Calidad**: Black + flake8 + mypy
- **DevOps**: Docker + GitHub Actions

Cada herramienta cumple un propósito específico y se integra con las demás para formar un sistema completo y funcional.

---

**Fecha de generación**: $(date)
**Proyecto**: SIA SOFKA U
**Versión**: 1.0.0