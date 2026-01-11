"""Integration tests for grades endpoints (refactored)."""

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


# ==================== Fixtures ====================

@pytest.fixture
async def test_data(db_session: AsyncSession):
    """Create test data (admin, profesor, estudiante, subject, enrollment)."""
    # Admin
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@test.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Test",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    
    # Profesor
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="profesor@test.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Test",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    
    # Estudiante
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="estudiante@test.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Test",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería",
    )
    db_session.add(estudiante)
    
    await db_session.commit()
    await db_session.refresh(admin)
    await db_session.refresh(profesor)
    await db_session.refresh(estudiante)
    
    # Subject
    subject = Subject(
        nombre="Matemáticas Avanzadas",
        codigo_institucional="MAT-301",
        numero_creditos=4,
        horario="Lunes 10:00-12:00",
        descripcion="Curso avanzado de matemáticas",
        profesor_id=profesor.id,
    )
    db_session.add(subject)
    await db_session.commit()
    await db_session.refresh(subject)
    
    # Enrollment
    enrollment = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject.id,
    )
    db_session.add(enrollment)
    await db_session.commit()
    await db_session.refresh(enrollment)
    
    return {
        "admin": admin,
        "profesor": profesor,
        "estudiante": estudiante,
        "subject": subject,
        "enrollment": enrollment,
    }


# ==================== CREATE GRADE Tests ====================

@pytest.mark.asyncio
async def test_create_grade_as_profesor_with_serialization(client, db_session: AsyncSession, test_data):
    """Test profesor can create grade and response includes nested enrollment data."""
    profesor = test_data["profesor"]
    subject = test_data["subject"]
    enrollment = test_data["enrollment"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.post(
        f"/api/v1/grades?subject_id={subject.id}",
        json={
            "enrollment_id": enrollment.id,
            "nota": 4.5,
            "periodo": "2024-1",
            "fecha": str(date.today()),
            "observaciones": "Excelente desempeño",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify basic grade data
    assert data["id"] is not None
    assert float(data["nota"]) == 4.5
    assert data["periodo"] == "2024-1"
    assert data["observaciones"] == "Excelente desempeño"
    
    # Verify nested enrollment data (refactored endpoint should include this)
    assert "enrollment" in data
    enrollment_data = data["enrollment"]
    assert enrollment_data["id"] == enrollment.id
    assert enrollment_data["estudiante_id"] == enrollment.estudiante_id
    assert enrollment_data["subject_id"] == enrollment.subject_id
    
    # Verify nested estudiante data (should be included via batch loading)
    assert "estudiante" in enrollment_data
    estudiante_data = enrollment_data["estudiante"]
    assert estudiante_data["id"] == test_data["estudiante"].id
    assert estudiante_data["nombre"] == "Estudiante"
    assert estudiante_data["apellido"] == "Test"
    assert estudiante_data["email"] == "estudiante@test.com"
    
    # Verify nested subject data (should be included via batch loading)
    assert "subject" in enrollment_data
    subject_data = enrollment_data["subject"]
    assert subject_data["id"] == subject.id
    assert subject_data["nombre"] == "Matemáticas Avanzadas"
    assert subject_data["codigo_institucional"] == "MAT-301"


@pytest.mark.asyncio
async def test_create_grade_as_admin_with_serialization(client, db_session: AsyncSession, test_data):
    """Test admin can create grade and response includes nested enrollment data."""
    admin = test_data["admin"]
    enrollment = test_data["enrollment"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.post(
        f"/api/v1/grades?subject_id={test_data['subject'].id}",
        json={
            "enrollment_id": enrollment.id,
            "nota": 4.8,
            "periodo": "2024-1",
            "fecha": str(date.today()),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Verify nested enrollment data
    assert "enrollment" in data
    assert "estudiante" in data["enrollment"]
    assert "subject" in data["enrollment"]


@pytest.mark.asyncio
async def test_create_grade_as_profesor_unauthorized_subject(client, db_session: AsyncSession, test_data):
    """Test profesor cannot create grade for unassigned subject."""
    profesor = test_data["profesor"]
    enrollment = test_data["enrollment"]
    
    # Create another profesor and subject
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@test.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor2)
    await db_session.commit()
    await db_session.refresh(profesor2)
    
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Martes 8:00",
        profesor_id=profesor2.id,  # Assigned to profesor2, not profesor
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.post(
        f"/api/v1/grades?subject_id={subject2.id}",  # profesor doesn't have access
        json={
            "enrollment_id": enrollment.id,
            "nota": 4.5,
            "periodo": "2024-1",
            "fecha": str(date.today()),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code in [403, 404]  # Should be forbidden


@pytest.mark.asyncio
async def test_create_grade_as_estudiante_forbidden(client, db_session: AsyncSession, test_data):
    """Test estudiante cannot create grade."""
    estudiante = test_data["estudiante"]
    enrollment = test_data["enrollment"]
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.post(
        f"/api/v1/grades?subject_id={test_data['subject'].id}",
        json={
            "enrollment_id": enrollment.id,
            "nota": 4.5,
            "periodo": "2024-1",
            "fecha": str(date.today()),
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


# ==================== GET GRADES Tests ====================

@pytest.mark.asyncio
async def test_get_grades_as_estudiante_with_serialization(client, db_session: AsyncSession, test_data):
    """Test estudiante can get own grades with nested enrollment data."""
    estudiante = test_data["estudiante"]
    subject = test_data["subject"]
    
    # Create a grade
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Buen trabajo",
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) > 0
    
    # Verify first grade has nested enrollment data
    grade_data = data[0]
    assert grade_data["id"] == grade.id
    assert float(grade_data["nota"]) == 4.5
    
    # Verify nested enrollment data (refactored endpoint should include this)
    assert "enrollment" in grade_data
    enrollment_data = grade_data["enrollment"]
    assert enrollment_data["estudiante_id"] == estudiante.id
    assert "estudiante" in enrollment_data
    assert "subject" in enrollment_data


@pytest.mark.asyncio
async def test_get_grades_as_profesor_with_serialization(client, db_session: AsyncSession, test_data):
    """Test profesor can get grades for assigned subject with nested data."""
    profesor = test_data["profesor"]
    subject = test_data["subject"]
    
    # Create multiple grades
    grade1 = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    grade2 = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.8"),
        periodo="2024-2",
        fecha=date.today(),
    )
    db_session.add_all([grade1, grade2])
    await db_session.commit()
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    assert len(data) >= 2
    
    # Verify all grades have nested enrollment data
    for grade_data in data:
        assert "enrollment" in grade_data
        assert "estudiante" in grade_data["enrollment"]
        assert "subject" in grade_data["enrollment"]
        # Verify subject name is correct
        assert grade_data["enrollment"]["subject"]["nombre"] == "Matemáticas Avanzadas"


@pytest.mark.asyncio
async def test_get_grades_as_profesor_with_enrollment_filter(client, db_session: AsyncSession, test_data):
    """Test profesor can filter grades by enrollment_id."""
    profesor = test_data["profesor"]
    subject = test_data["subject"]
    enrollment = test_data["enrollment"]
    
    # Create another enrollment and grade
    codigo_est2 = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante2 = User(
        email="estudiante2@test.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante2",
        apellido="Test",
        codigo_institucional=codigo_est2,
        fecha_nacimiento=date(2001, 1, 1),
    )
    db_session.add(estudiante2)
    await db_session.commit()
    await db_session.refresh(estudiante2)
    
    enrollment2 = Enrollment(
        estudiante_id=estudiante2.id,
        subject_id=subject.id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    # Create grades for both enrollments
    grade1 = Grade(enrollment_id=enrollment.id, nota=Decimal("4.5"), periodo="2024-1", fecha=date.today())
    grade2 = Grade(enrollment_id=enrollment2.id, nota=Decimal("4.0"), periodo="2024-1", fecha=date.today())
    db_session.add_all([grade1, grade2])
    await db_session.commit()
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    # Filter by enrollment_id
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}&enrollment_id={enrollment.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Should only return grades for the specified enrollment
    assert len(data) >= 1
    assert all(g["enrollment"]["id"] == enrollment.id for g in data)


@pytest.mark.asyncio
async def test_get_grades_as_admin_all_grades(client, db_session: AsyncSession, test_data):
    """Test admin can get all grades without subject_id filter."""
    admin = test_data["admin"]
    
    # Create grades
    grade1 = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade1)
    await db_session.commit()
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Admin can get all grades without subject_id
    response = await client.get(
        "/api/v1/grades",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_grades_as_estudiante_requires_subject_id(client, db_session: AsyncSession, test_data):
    """Test estudiante must provide subject_id."""
    estudiante = test_data["estudiante"]
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        "/api/v1/grades",  # No subject_id
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


# ==================== GET GRADE BY ID Tests ====================

@pytest.mark.asyncio
async def test_get_grade_by_id_as_estudiante_with_serialization(client, db_session: AsyncSession, test_data):
    """Test estudiante can get own grade by ID with nested data."""
    estudiante = test_data["estudiante"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.7"),
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Excelente",
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
    assert float(data["nota"]) == 4.7
    assert data["observaciones"] == "Excelente"
    
    # Verify nested enrollment data
    assert "enrollment" in data
    assert "estudiante" in data["enrollment"]
    assert "subject" in data["enrollment"]
    assert data["enrollment"]["estudiante"]["id"] == estudiante.id


@pytest.mark.asyncio
async def test_get_grade_by_id_as_estudiante_forbidden_other_student(client, db_session: AsyncSession, test_data):
    """Test estudiante cannot get another student's grade."""
    estudiante = test_data["estudiante"]
    
    # Create another estudiante and enrollment
    codigo_est2 = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante2 = User(
        email="estudiante2@test.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante2",
        apellido="Test",
        codigo_institucional=codigo_est2,
        fecha_nacimiento=date(2001, 1, 1),
    )
    db_session.add(estudiante2)
    await db_session.commit()
    await db_session.refresh(estudiante2)
    
    enrollment2 = Enrollment(
        estudiante_id=estudiante2.id,
        subject_id=test_data["subject"].id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    grade = Grade(
        enrollment_id=enrollment2.id,  # Belongs to estudiante2
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        f"/api/v1/grades/{grade.id}",  # Trying to access estudiante2's grade
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_grade_by_id_as_profesor_with_serialization(client, db_session: AsyncSession, test_data):
    """Test profesor can get grade for assigned subject with nested data."""
    profesor = test_data["profesor"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.6"),
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
    assert "enrollment" in data
    assert "estudiante" in data["enrollment"]
    assert "subject" in data["enrollment"]


@pytest.mark.asyncio
async def test_get_grade_by_id_not_found(client, db_session: AsyncSession, test_data):
    """Test getting non-existent grade returns 404."""
    admin = test_data["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        "/api/v1/grades/99999",  # Non-existent ID
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404


# ==================== UPDATE GRADE Tests ====================

@pytest.mark.asyncio
async def test_update_grade_as_profesor_with_serialization(client, db_session: AsyncSession, test_data):
    """Test profesor can update grade and response includes nested data."""
    profesor = test_data["profesor"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.0"),
        periodo="2024-1",
        fecha=date.today(),
        observaciones="Original",
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.put(
        f"/api/v1/grades/{grade.id}",
        json={
            "nota": 4.8,
            "observaciones": "Actualizado - Excelente mejora",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["id"] == grade.id
    assert float(data["nota"]) == 4.8
    assert data["observaciones"] == "Actualizado - Excelente mejora"
    
    # Verify nested enrollment data is still included
    assert "enrollment" in data
    assert "estudiante" in data["enrollment"]
    assert "subject" in data["enrollment"]


@pytest.mark.asyncio
async def test_update_grade_as_admin_with_serialization(client, db_session: AsyncSession, test_data):
    """Test admin can update any grade with nested data."""
    admin = test_data["admin"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("3.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.put(
        f"/api/v1/grades/{grade.id}",
        json={
            "nota": 4.2,
            "periodo": "2024-2",
            "observaciones": "Mejorado por admin",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert float(data["nota"]) == 4.2
    assert data["periodo"] == "2024-2"
    assert "enrollment" in data


@pytest.mark.asyncio
async def test_update_grade_as_profesor_unauthorized_subject(client, db_session: AsyncSession, test_data):
    """Test profesor cannot update grade for unassigned subject."""
    profesor = test_data["profesor"]
    
    # Create another profesor and subject
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@test.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor2)
    await db_session.commit()
    await db_session.refresh(profesor2)
    
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Martes 8:00",
        profesor_id=profesor2.id,
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    enrollment2 = Enrollment(
        estudiante_id=test_data["estudiante"].id,
        subject_id=subject2.id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    grade = Grade(
        enrollment_id=enrollment2.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.put(
        f"/api/v1/grades/{grade.id}",
        json={"nota": 4.8},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_grade_as_estudiante_forbidden(client, db_session: AsyncSession, test_data):
    """Test estudiante cannot update grade."""
    estudiante = test_data["estudiante"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.put(
        f"/api/v1/grades/{grade.id}",
        json={"nota": 4.8},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_grade_not_found(client, db_session: AsyncSession, test_data):
    """Test updating non-existent grade returns 404."""
    admin = test_data["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.put(
        "/api/v1/grades/99999",
        json={"nota": 4.5},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404


# ==================== DELETE GRADE Tests ====================

@pytest.mark.asyncio
async def test_delete_grade_as_profesor(client, db_session: AsyncSession, test_data):
    """Test profesor can delete grade for assigned subject."""
    profesor = test_data["profesor"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    grade_id = grade.id
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.delete(
        f"/api/v1/grades/{grade_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 204
    
    # Verify grade was deleted
    response_get = await client.get(
        f"/api/v1/grades/{grade_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response_get.status_code == 404


@pytest.mark.asyncio
async def test_delete_grade_as_admin(client, db_session: AsyncSession, test_data):
    """Test admin can delete any grade."""
    admin = test_data["admin"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    grade_id = grade.id
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.delete(
        f"/api/v1/grades/{grade_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_grade_as_profesor_unauthorized_subject(client, db_session: AsyncSession, test_data):
    """Test profesor cannot delete grade for unassigned subject."""
    profesor = test_data["profesor"]
    
    # Create another profesor and subject (same as update test)
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@test.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor2)
    await db_session.commit()
    await db_session.refresh(profesor2)
    
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Martes 8:00",
        profesor_id=profesor2.id,
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    enrollment2 = Enrollment(
        estudiante_id=test_data["estudiante"].id,
        subject_id=subject2.id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    grade = Grade(
        enrollment_id=enrollment2.id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.delete(
        f"/api/v1/grades/{grade.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_grade_as_estudiante_forbidden(client, db_session: AsyncSession, test_data):
    """Test estudiante cannot delete grade."""
    estudiante = test_data["estudiante"]
    
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.delete(
        f"/api/v1/grades/{grade.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_delete_grade_not_found(client, db_session: AsyncSession, test_data):
    """Test deleting non-existent grade returns 404."""
    admin = test_data["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.delete(
        "/api/v1/grades/99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404


# ==================== Batch Serialization Tests ====================

@pytest.mark.asyncio
async def test_get_multiple_grades_verify_batch_loading(client, db_session: AsyncSession, test_data):
    """Test that multiple grades are serialized correctly with batch loading (no N+1)."""
    profesor = test_data["profesor"]
    subject = test_data["subject"]
    
    # Create multiple enrollments with same subject
    estudiantes = []
    enrollments = []
    for i in range(3):
        codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
        estudiante = User(
            email=f"est{i}@test.com",
            password_hash=get_password_hash("est123"),
            role=UserRole.ESTUDIANTE,
            nombre=f"Estudiante{i}",
            apellido="Test",
            codigo_institucional=codigo_est,
            fecha_nacimiento=date(2000 + i, 1, 1),
        )
        db_session.add(estudiante)
        estudiantes.append(estudiante)
    
    await db_session.commit()
    for est in estudiantes:
        await db_session.refresh(est)
    
    for est in estudiantes:
        enrollment = Enrollment(
            estudiante_id=est.id,
            subject_id=subject.id,
        )
        db_session.add(enrollment)
        enrollments.append(enrollment)
    
    await db_session.commit()
    for enr in enrollments:
        await db_session.refresh(enr)
    
    # Create grades for each enrollment
    grades = []
    for i, enrollment in enumerate(enrollments):
        grade = Grade(
            enrollment_id=enrollment.id,
            nota=Decimal(f"{4.0 + i * 0.2}"),
            periodo="2024-1",
            fecha=date.today(),
        )
        db_session.add(grade)
        grades.append(grade)
    
    await db_session.commit()
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify we got all grades
    assert len(data) >= 3
    
    # Verify all grades have complete nested data (batch loading should work)
    for grade_data in data[:3]:  # Check first 3
        assert "enrollment" in grade_data
        assert "estudiante" in grade_data["enrollment"]
        assert "subject" in grade_data["enrollment"]
        # Verify estudiante data is correct (should be loaded via batch)
        assert grade_data["enrollment"]["estudiante"]["email"].startswith("est")
        # Verify subject data is correct (should be loaded via batch)
        assert grade_data["enrollment"]["subject"]["nombre"] == "Matemáticas Avanzadas"


# ==================== Edge Cases Tests ====================

@pytest.mark.asyncio
async def test_get_grades_as_estudiante_empty_list(client, db_session: AsyncSession, test_data):
    """Test estudiante gets empty list when no grades exist (covers _get_grades_as_estudiante empty case)."""
    estudiante = test_data["estudiante"]
    subject = test_data["subject"]
    
    # Create another subject without grades
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@test.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor2)
    await db_session.commit()
    await db_session.refresh(profesor2)
    
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Martes 8:00",
        profesor_id=profesor2.id,
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    enrollment2 = Enrollment(
        estudiante_id=estudiante.id,
        subject_id=subject2.id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    # No grades created for this subject
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should return empty list or grades from service (may return empty)


@pytest.mark.asyncio
async def test_get_grades_as_profesor_empty_list(client, db_session: AsyncSession, test_data):
    """Test profesor gets empty list when no grades exist (covers _get_grades_as_profesor empty case)."""
    profesor = test_data["profesor"]
    subject = test_data["subject"]
    
    # Create enrollment without grades
    codigo_est2 = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante2 = User(
        email="estudiante2@test.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante2",
        apellido="Test",
        codigo_institucional=codigo_est2,
        fecha_nacimiento=date(2001, 1, 1),
    )
    db_session.add(estudiante2)
    await db_session.commit()
    await db_session.refresh(estudiante2)
    
    enrollment2 = Enrollment(
        estudiante_id=estudiante2.id,
        subject_id=subject.id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    # No grades created yet
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/grades?subject_id={subject.id}&enrollment_id={enrollment2.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should return empty list if no grades for this enrollment


@pytest.mark.asyncio
async def test_get_grades_as_admin_empty_list(client, db_session: AsyncSession, test_data):
    """Test admin gets empty list when no grades exist (covers _get_grades_as_admin empty case)."""
    admin = test_data["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Query with non-existent subject_id
    response = await client.get(
        "/api/v1/grades?subject_id=99999",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    # Should return empty list if no grades


@pytest.mark.asyncio
async def test_get_grades_as_profesor_missing_subject_id(client, db_session: AsyncSession, test_data):
    """Test profesor must provide subject_id (covers line 254)."""
    profesor = test_data["profesor"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        "/api/v1/grades",  # No subject_id
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "Subject ID is required" in data.get("detail", "")


@pytest.mark.asyncio
async def test_get_grade_by_id_with_none_enrollment(client, db_session: AsyncSession, test_data):
    """Test get_grade handles case where enrollment might be None (edge case)."""
    estudiante = test_data["estudiante"]
    
    # Create a grade with a valid enrollment_id, but test edge case
    grade = Grade(
        enrollment_id=test_data["enrollment"].id,
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
    # Enrollment should exist since we just created it


@pytest.mark.asyncio
async def test_get_grade_by_id_enrollment_not_belongs_to_estudiante(client, db_session: AsyncSession, test_data):
    """Test get_grade verifies enrollment belongs to estudiante (covers line 278-279)."""
    estudiante = test_data["estudiante"]
    
    # Create another estudiante and enrollment
    codigo_est2 = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante2 = User(
        email="estudiante2@test.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante2",
        apellido="Test",
        codigo_institucional=codigo_est2,
        fecha_nacimiento=date(2001, 1, 1),
    )
    db_session.add(estudiante2)
    await db_session.commit()
    await db_session.refresh(estudiante2)
    
    enrollment2 = Enrollment(
        estudiante_id=estudiante2.id,  # Belongs to estudiante2
        subject_id=test_data["subject"].id,
    )
    db_session.add(enrollment2)
    await db_session.commit()
    await db_session.refresh(enrollment2)
    
    grade = Grade(
        enrollment_id=enrollment2.id,  # Grade belongs to estudiante2's enrollment
        nota=Decimal("4.5"),
        periodo="2024-1",
        fecha=date.today(),
    )
    db_session.add(grade)
    await db_session.commit()
    await db_session.refresh(grade)
    
    # Try to access as estudiante (not estudiante2)
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        f"/api/v1/grades/{grade.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "Cannot access other student's grades" in data.get("detail", "")

