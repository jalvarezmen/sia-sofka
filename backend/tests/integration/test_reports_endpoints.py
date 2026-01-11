"""Integration tests for reports endpoints (safety net before refactoring)."""

import pytest
import json
from datetime import date
from decimal import Decimal
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash, create_access_token


# ==================== Fixtures ====================

@pytest.fixture
async def test_data_reports_endpoints(db_session: AsyncSession):
    """Create comprehensive test data for report endpoints."""
    # Admin
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@reports-endpoints.com",
        password_hash=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        nombre="Admin",
        apellido="Reports",
        codigo_institucional=codigo_admin,
        fecha_nacimiento=date(1975, 1, 1),
    )
    db_session.add(admin)
    
    # Profesor
    codigo_prof = await generar_codigo_institucional(db_session, "Profesor")
    profesor = User(
        email="profesor@reports-endpoints.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor",
        apellido="Reports",
        codigo_institucional=codigo_prof,
        fecha_nacimiento=date(1980, 1, 1),
    )
    db_session.add(profesor)
    
    # Estudiante
    codigo_est = await generar_codigo_institucional(db_session, "Estudiante")
    estudiante = User(
        email="estudiante@reports-endpoints.com",
        password_hash=get_password_hash("est123"),
        role=UserRole.ESTUDIANTE,
        nombre="Estudiante",
        apellido="Reports",
        codigo_institucional=codigo_est,
        fecha_nacimiento=date(2000, 1, 1),
        programa_academico="Ingeniería de Sistemas",
    )
    db_session.add(estudiante)
    
    await db_session.commit()
    await db_session.refresh(admin)
    await db_session.refresh(profesor)
    await db_session.refresh(estudiante)
    
    # Subject
    subject = Subject(
        nombre="Cálculo Integral",
        codigo_institucional="CAL-201",
        numero_creditos=4,
        horario="Martes 14:00-16:00",
        descripcion="Curso avanzado de cálculo",
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
    
    # Grades
    grades = []
    for i, periodo in enumerate(["2024-1", "2024-2"], start=1):
        grade = Grade(
            enrollment_id=enrollment.id,
            nota=Decimal(f"{4.0 + i * 0.3}"),  # 4.3, 4.6
            periodo=periodo,
            fecha=date.today(),
            observaciones=f"Nota del período {periodo}",
        )
        db_session.add(grade)
        grades.append(grade)
    
    await db_session.commit()
    for grade in grades:
        await db_session.refresh(grade)
    
    return {
        "admin": admin,
        "profesor": profesor,
        "estudiante": estudiante,
        "subject": subject,
        "enrollment": enrollment,
        "grades": grades,
    }


@pytest.fixture
def admin_token(test_data_reports_endpoints):
    """Create admin JWT token."""
    admin = test_data_reports_endpoints["admin"]
    return create_access_token(data={"sub": admin.email, "role": admin.role.value})


@pytest.fixture
def profesor_token(test_data_reports_endpoints):
    """Create profesor JWT token."""
    profesor = test_data_reports_endpoints["profesor"]
    return create_access_token(data={"sub": profesor.email, "role": profesor.role.value})


@pytest.fixture
def estudiante_token(test_data_reports_endpoints):
    """Create estudiante JWT token."""
    estudiante = test_data_reports_endpoints["estudiante"]
    return create_access_token(data={"sub": estudiante.email, "role": estudiante.role.value})


# ==================== Tests for get_student_report ====================

@pytest.mark.asyncio
async def test_get_student_report_json_format(client: AsyncClient, test_data_reports_endpoints, admin_token):
    """Test get_student_report with JSON format (default)."""
    estudiante = test_data_reports_endpoints["estudiante"]
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "estudiante" in data
    assert data["estudiante"]["id"] == estudiante.id
    assert "subjects" in data
    assert len(data["subjects"]) > 0


@pytest.mark.asyncio
async def test_get_student_report_json_format_default(client: AsyncClient, test_data_reports_endpoints, admin_token):
    """Test get_student_report with JSON format (default, no param)."""
    estudiante = test_data_reports_endpoints["estudiante"]
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "estudiante" in data
    assert data["estudiante"]["id"] == estudiante.id


@pytest.mark.asyncio
async def test_get_student_report_pdf_format(client: AsyncClient, test_data_reports_endpoints, admin_token):
    """Test get_student_report with PDF format."""
    estudiante = test_data_reports_endpoints["estudiante"]
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}",
        params={"format": "pdf"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_student_report_html_format(client: AsyncClient, test_data_reports_endpoints, admin_token):
    """Test get_student_report with HTML format."""
    estudiante = test_data_reports_endpoints["estudiante"]
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}",
        params={"format": "html"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_student_report_not_found(client: AsyncClient, admin_token):
    """Test get_student_report with non-existent student."""
    response = await client.get(
        "/api/v1/reports/student/99999",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_student_report_unauthorized_profesor(client: AsyncClient, test_data_reports_endpoints, profesor_token):
    """Test get_student_report as profesor (should be forbidden)."""
    estudiante = test_data_reports_endpoints["estudiante"]
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_student_report_unauthorized_estudiante(client: AsyncClient, test_data_reports_endpoints, estudiante_token):
    """Test get_student_report as estudiante (should be forbidden)."""
    estudiante = test_data_reports_endpoints["estudiante"]
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {estudiante_token}"},
    )
    
    assert response.status_code == 403


# ==================== Tests for get_subject_report ====================

@pytest.mark.asyncio
async def test_get_subject_report_json_format(client: AsyncClient, test_data_reports_endpoints, profesor_token):
    """Test get_subject_report with JSON format."""
    subject = test_data_reports_endpoints["subject"]
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "subject" in data
    assert data["subject"]["id"] == subject.id
    assert "students" in data


@pytest.mark.asyncio
async def test_get_subject_report_pdf_format(client: AsyncClient, test_data_reports_endpoints, profesor_token):
    """Test get_subject_report with PDF format (default)."""
    subject = test_data_reports_endpoints["subject"]
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}",
        params={"format": "pdf"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_subject_report_html_format(client: AsyncClient, test_data_reports_endpoints, profesor_token):
    """Test get_subject_report with HTML format."""
    subject = test_data_reports_endpoints["subject"]
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}",
        params={"format": "html"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_subject_report_not_assigned(client: AsyncClient, test_data_reports_endpoints, profesor_token, db_session: AsyncSession):
    """Test get_subject_report for subject not assigned to profesor."""
    # Create another profesor and subject
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@reports-endpoints.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Reports",
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
        horario="Lunes 10:00-12:00",
        descripcion="Curso de física",
        profesor_id=profesor2.id,  # Assigned to profesor2, not the original profesor
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    # Try to access with original profesor token
    response = await client.get(
        f"/api/v1/reports/subject/{subject2.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_subject_report_not_found(client: AsyncClient, profesor_token):
    """Test get_subject_report with non-existent subject."""
    response = await client.get(
        "/api/v1/reports/subject/99999",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 403  # Forbidden because subject not assigned


@pytest.mark.asyncio
async def test_get_subject_report_unauthorized_admin(client: AsyncClient, test_data_reports_endpoints, admin_token):
    """Test get_subject_report as admin (should be forbidden)."""
    subject = test_data_reports_endpoints["subject"]
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_subject_report_unauthorized_estudiante(client: AsyncClient, test_data_reports_endpoints, estudiante_token):
    """Test get_subject_report as estudiante (should be forbidden)."""
    subject = test_data_reports_endpoints["subject"]
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {estudiante_token}"},
    )
    
    assert response.status_code == 403


# ==================== Tests for get_general_report ====================

@pytest.mark.asyncio
async def test_get_general_report_json_format(client: AsyncClient, test_data_reports_endpoints, estudiante_token):
    """Test get_general_report with JSON format."""
    response = await client.get(
        "/api/v1/reports/general",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {estudiante_token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "estudiante" in data
    assert "subjects" in data


@pytest.mark.asyncio
async def test_get_general_report_pdf_format(client: AsyncClient, test_data_reports_endpoints, estudiante_token):
    """Test get_general_report with PDF format (default)."""
    response = await client.get(
        "/api/v1/reports/general",
        params={"format": "pdf"},
        headers={"Authorization": f"Bearer {estudiante_token}"},
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/pdf")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_general_report_html_format(client: AsyncClient, test_data_reports_endpoints, estudiante_token):
    """Test get_general_report with HTML format."""
    response = await client.get(
        "/api/v1/reports/general",
        params={"format": "html"},
        headers={"Authorization": f"Bearer {estudiante_token}"},
    )
    
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "attachment" in response.headers.get("content-disposition", "")
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_get_general_report_unauthorized_admin(client: AsyncClient, admin_token):
    """Test get_general_report as admin (should be forbidden)."""
    response = await client.get(
        "/api/v1/reports/general",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_general_report_unauthorized_profesor(client: AsyncClient, test_data_reports_endpoints, profesor_token):
    """Test get_general_report as profesor (should be forbidden)."""
    response = await client.get(
        "/api/v1/reports/general",
        params={"format": "json"},
        headers={"Authorization": f"Bearer {profesor_token}"},
    )
    
    assert response.status_code == 403

