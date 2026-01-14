"""Integration tests for API endpoints."""

import pytest
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash, create_access_token


@pytest.mark.asyncio
async def test_create_user_as_admin(client, db_session: AsyncSession):
    """Test admin can create user."""
    # Create admin
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    
    # Login as admin
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Create estudiante
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "newest@example.com",
            "password": "password123",
            "nombre": "Nuevo",
            "apellido": "Estudiante",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
            "programa_academico": "Ingeniería",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newest@example.com"
    assert data["role"] == "Estudiante"


@pytest.mark.asyncio
async def test_create_user_unauthorized(client, db_session: AsyncSession):
    """Test non-admin cannot create user."""
    # Create estudiante
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(estudiante)
    await db_session.commit()
    await db_session.refresh(estudiante)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.post(
        "/api/v1/users",
        json={
            "email": "new@example.com",
            "password": "password123",
            "nombre": "New",
            "apellido": "User",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_users_as_admin(client, db_session: AsyncSession):
    """Test admin can get all users."""
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_create_subject_as_admin(client, db_session: AsyncSession):
    """Test admin can create subject."""
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    await db_session.commit()
    await db_session.refresh(profesor)
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.post(
        "/api/v1/subjects",
        json={
            "nombre": "Nueva Materia",
            "codigo_institucional": "NUE-101",
            "numero_creditos": 3,
            "horario": "Lunes 8:00-10:00",
            "profesor_id": profesor.id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["nombre"] == "Nueva Materia"


@pytest.mark.asyncio
async def test_create_enrollment_as_admin(client, db_session: AsyncSession):
    """Test admin can create enrollment."""
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(estudiante)
    
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    await db_session.commit()
    await db_session.refresh(estudiante)
    await db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.post(
        "/api/v1/enrollments",
        json={
            "estudiante_id": estudiante.id,
            "subject_id": subject.id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["estudiante_id"] == estudiante.id
    assert data["subject_id"] == subject.id


@pytest.mark.asyncio
async def test_create_grade_as_profesor(client, db_session: AsyncSession):
    """Test profesor can create grade."""
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(estudiante)
    await db_session.commit()
    await db_session.refresh(profesor)
    await db_session.refresh(estudiante)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)
    
    response = await client.post(
        f"/api/v1/grades?subject_id={subject.id}",
        json={
            "enrollment_id": enrollment.id,
            "nota": 4.5,
            "periodo": "2024-1",
            "fecha": str(date.today()),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    # Decimal is serialized as string in JSON
    assert float(data["nota"]) == 4.5


@pytest.mark.asyncio
async def test_get_grades_as_estudiante(client, db_session: AsyncSession):
    """Test estudiante can get own grades."""
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(estudiante)
    
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="prof@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.PROFESOR,
        nombre="Prof",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    await db_session.commit()
    await db_session.refresh(estudiante)
    await db_session.refresh(profesor)
    
    subject = Subject(
        nombre="Matemáticas",
        codigo_institucional="MAT-101",
        numero_creditos=3,
        horario="Lunes 8:00",
        profesor_id=profesor.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)
    
    grade = Grade(
        enrollment_id=enrollment.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(estudiante)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_generate_report_as_admin(client, db_session: AsyncSession):
    """Test admin can generate student report."""
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Est",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
    )
    db_session.add(estudiante)
    await db_session.commit()
    await db_session.refresh(estudiante)
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    # JSON response should be valid
    data = response.json()
    assert "estudiante" in data


@pytest.mark.asyncio
async def test_update_profile(client, db_session: AsyncSession):
    """Test user can update own profile."""
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="est@example.com",
        password_hash=get_password_hash("pass"),
        role=UserRole.ESTUDIANTE,
        nombre="Original",
        apellido="Name",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        numero_contacto="1234567890",
    )
    db_session.add(estudiante)
    await db_session.commit()
    await db_session.refresh(estudiante)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.put(
        "/api/v1/profile",
        json={
            "nombre": "Updated",
            "numero_contacto": "0987654321",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Updated"
    assert data["numero_contacto"] == "0987654321"

