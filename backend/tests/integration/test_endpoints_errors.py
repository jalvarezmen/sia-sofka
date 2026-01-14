"""Integration tests for error cases and edge cases."""

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
async def test_register_user_duplicate_email(client, db_session: AsyncSession):
    """Test register fails with duplicate email."""
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@example.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    
    login_response = await client.post(
        "/api/v1/auth/login",
        data={"username": "admin@example.com", "password": "admin123"},
    )
    admin_token = login_response.json()["access_token"]
    
    # Register first user
    response1 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nombre": "Test",
            "apellido": "User",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response1.status_code == 201
    
    # Try to register with same email
    response2 = await client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "nombre": "Test2",
            "apellido": "User2",
            "role": "Estudiante",
            "fecha_nacimiento": "2000-01-01",
        },
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert response2.status_code == 400


@pytest.mark.asyncio
async def test_get_grade_by_id_as_estudiante(client, db_session: AsyncSession):
    """Test estudiante can get own grade by ID."""
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
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        f"/api/v1/grades/{grade.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == grade.id
    assert float(data["nota"]) == 4.5


@pytest.mark.asyncio
async def test_get_grade_by_id_as_profesor(client, db_session: AsyncSession):
    """Test profesor can get grade for assigned subject."""
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
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/grades/{grade.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == grade.id


@pytest.mark.asyncio
async def test_get_grades_as_profesor_with_subject_id(client, db_session: AsyncSession):
    """Test profesor can get grades for assigned subject."""
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
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_grades_as_admin_with_subject_id(client, db_session: AsyncSession):
    """Test admin can get grades for any subject."""
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
    await db_session.refresh(admin)
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
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_enrollments_as_admin(client, db_session: AsyncSession):
    """Test admin can get all enrollments."""
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
    await db_session.refresh(admin)
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
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        "/api/v1/enrollments",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_subjects_as_admin(client, db_session: AsyncSession):
    """Test admin can get all subjects."""
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
    await db_session.refresh(admin)
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
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        "/api/v1/subjects",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_profile(client, db_session: AsyncSession):
    """Test user can get own profile."""
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
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        "/api/v1/profile",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "est@example.com"
    assert data["role"] == "Estudiante"


@pytest.mark.asyncio
async def test_update_grade_as_profesor(client, db_session: AsyncSession):
    """Test profesor can update grade for assigned subject."""
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
        nota=Decimal("4.0"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.put(
        f"/api/v1/grades/{grade.id}",
        json={
            "nota": 4.5,
            "observaciones": "Mejorado",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert float(data["nota"]) == 4.5
    assert data["observaciones"] == "Mejorado"

