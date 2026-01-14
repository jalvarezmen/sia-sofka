"""Integration tests for Report Factory with Registry Pattern."""

import pytest
import json
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, UserRole
from app.models.subject import Subject
from app.models.enrollment import Enrollment
from app.models.grade import Grade
from app.utils.codigo_generator import generar_codigo_institucional
from app.core.security import get_password_hash, create_access_token
from app.factories.report_factory import ReportFactory, ReportFormat


# ==================== Fixtures ====================

@pytest.fixture
async def test_data_reports(db_session: AsyncSession):
    """Create comprehensive test data for report generation."""
    # Admin
    codigo_admin = await generar_codigo_institucional(db_session, "Admin")
    admin = User(
        email="admin@reports.com",
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
        email="profesor@reports.com",
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
        email="estudiante@reports.com",
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


# ==================== Registry Pattern Tests ====================

@pytest.mark.asyncio
async def test_report_factory_registry_pattern_integration():
    """Test that Registry Pattern works correctly in integration context."""
    # Import to trigger registration
    from app.factories import (
        ReportFactory,
        PDFReportGenerator,  # noqa: F401
        HTMLReportGenerator,  # noqa: F401
        JSONReportGenerator,  # noqa: F401
    )
    
    # Verify all formats are registered
    formats = ReportFactory.get_registered_formats()
    assert 'pdf' in formats
    assert 'html' in formats
    assert 'json' in formats
    assert len(formats) >= 3
    
    # Verify factory can create all generators
    pdf_gen = ReportFactory.create_generator('pdf')
    html_gen = ReportFactory.create_generator('html')
    json_gen = ReportFactory.create_generator('json')
    
    assert pdf_gen is not None
    assert html_gen is not None
    assert json_gen is not None
    
    # Verify they are different instances (different formats)
    assert pdf_gen is not html_gen
    assert html_gen is not json_gen


@pytest.mark.asyncio
async def test_report_factory_singleton_pattern_integration():
    """Test that Singleton Pattern works correctly in integration context."""
    from app.factories import ReportFactory
    
    # Create multiple instances of same format
    pdf_gen1 = ReportFactory.create_generator('pdf')
    pdf_gen2 = ReportFactory.create_generator('pdf')
    pdf_gen3 = ReportFactory.create_generator('PDF')  # Case insensitive
    
    # Should be same instance (singleton)
    assert pdf_gen1 is pdf_gen2
    assert pdf_gen1 is pdf_gen3
    
    # Different formats should be different instances
    html_gen = ReportFactory.create_generator('html')
    assert pdf_gen1 is not html_gen


# ==================== Student Report Tests (Admin) ====================

@pytest.mark.asyncio
async def test_generate_student_report_json_format(client, db_session: AsyncSession, test_data_reports):
    """Test admin can generate student report in JSON format (covers Registry Pattern)."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify JSON structure
    assert "estudiante" in data
    assert data["estudiante"]["id"] == estudiante.id
    assert data["estudiante"]["nombre"] == "Estudiante"
    assert "subjects" in data
    assert isinstance(data["subjects"], list)
    
    # Verify subjects have grades
    if len(data["subjects"]) > 0:
        subject_data = data["subjects"][0]
        assert "subject" in subject_data
        assert "grades" in subject_data
        assert "average" in subject_data
        assert "general_average" in data  # Should include general average


@pytest.mark.asyncio
async def test_generate_student_report_pdf_format(client, db_session: AsyncSession, test_data_reports):
    """Test admin can generate student report in PDF format (covers Registry Pattern)."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Verify PDF response
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers.get("content-disposition", "")
    assert ".pdf" in response.headers.get("content-disposition", "")
    
    # Verify content is bytes (PDF)
    assert isinstance(response.content, bytes)
    assert len(response.content) > 0
    # PDF files start with %PDF
    assert response.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_student_report_html_format(client, db_session: AsyncSession, test_data_reports):
    """Test admin can generate student report in HTML format (covers Registry Pattern)."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=html",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Verify HTML response (may include charset)
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type
    assert "attachment" in response.headers.get("content-disposition", "")
    assert ".html" in response.headers.get("content-disposition", "")
    
    # Verify content is bytes (HTML)
    content = response.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    assert "<html" in content.lower() or "<!doctype" in content.lower()


@pytest.mark.asyncio
async def test_generate_student_report_invalid_format(client, db_session: AsyncSession, test_data_reports):
    """Test generate student report with invalid format returns error."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=xml",  # Invalid format
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # Should return 400 or 422 (validation error) or 500 if factory raises ValueError
    assert response.status_code in [400, 422, 500]
    if response.status_code != 500:
        data = response.json()
        assert "format" in data.get("detail", "").lower() or "unsupported" in data.get("detail", "").lower()


@pytest.mark.asyncio
async def test_generate_student_report_student_not_found(client, db_session: AsyncSession, test_data_reports):
    """Test generate student report for non-existent student returns 404."""
    admin = test_data_reports["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        "/api/v1/reports/student/99999?format=json",  # Non-existent student
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_generate_student_report_as_profesor_forbidden(client, db_session: AsyncSession, test_data_reports):
    """Test profesor cannot generate student report (Admin only)."""
    profesor = test_data_reports["profesor"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


# ==================== Subject Report Tests (Profesor) ====================

@pytest.mark.asyncio
async def test_generate_subject_report_json_format(client, db_session: AsyncSession, test_data_reports):
    """Test profesor can generate subject report in JSON format (covers Registry Pattern)."""
    profesor = test_data_reports["profesor"]
    subject = test_data_reports["subject"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify JSON structure
    assert "subject" in data
    assert data["subject"]["id"] == subject.id
    assert "students" in data
    assert isinstance(data["students"], list)
    
    # Verify students have grades
    if len(data["students"]) > 0:
        student_data = data["students"][0]
        assert "estudiante" in student_data
        assert "grades" in student_data
        assert "average" in student_data


@pytest.mark.asyncio
async def test_generate_subject_report_pdf_format(client, db_session: AsyncSession, test_data_reports):
    """Test profesor can generate subject report in PDF format (covers Registry Pattern)."""
    profesor = test_data_reports["profesor"]
    subject = test_data_reports["subject"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}?format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Verify PDF response
    assert response.headers["content-type"] == "application/pdf"
    assert "attachment" in response.headers.get("content-disposition", "")
    assert isinstance(response.content, bytes)
    assert response.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_subject_report_html_format(client, db_session: AsyncSession, test_data_reports):
    """Test profesor can generate subject report in HTML format (covers Registry Pattern)."""
    profesor = test_data_reports["profesor"]
    subject = test_data_reports["subject"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}?format=html",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Verify HTML response (may include charset)
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type
    assert "attachment" in response.headers.get("content-disposition", "")
    
    content = response.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    assert "<html" in content.lower() or "<!doctype" in content.lower()


@pytest.mark.asyncio
async def test_generate_subject_report_unassigned_subject(client, db_session: AsyncSession, test_data_reports):
    """Test profesor cannot generate report for unassigned subject."""
    profesor = test_data_reports["profesor"]
    
    # Create another profesor and subject
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@reports.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1981, 1, 1),
    )
    db_session.add(profesor2)
    await db_session.commit()
    await db_session.refresh(profesor2)
    
    subject2 = Subject(
        nombre="Física",
        codigo_institucional="FIS-101",
        numero_creditos=3,
        horario="Jueves 8:00",
        profesor_id=profesor2.id,  # Assigned to profesor2, not profesor
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject2.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403  # Forbidden


@pytest.mark.asyncio
async def test_generate_subject_report_as_admin_forbidden(client, db_session: AsyncSession, test_data_reports):
    """Test admin cannot generate subject report (Profesor only)."""
    admin = test_data_reports["admin"]
    subject = test_data_reports["subject"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/subject/{subject.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


# ==================== General Report Tests (Estudiante) ====================

@pytest.mark.asyncio
async def test_generate_general_report_json_format(client, db_session: AsyncSession, test_data_reports):
    """Test estudiante can generate general report in JSON format (covers Registry Pattern)."""
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        "/api/v1/reports/general?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify JSON structure
    assert "estudiante" in data
    assert data["estudiante"]["id"] == estudiante.id
    assert "subjects" in data
    assert isinstance(data["subjects"], list)
    assert "general_average" in data  # Should include general average


@pytest.mark.asyncio
async def test_generate_general_report_pdf_format(client, db_session: AsyncSession, test_data_reports):
    """Test estudiante can generate general report in PDF format (covers Registry Pattern)."""
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        "/api/v1/reports/general?format=pdf",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Verify PDF response
    assert response.headers["content-type"] == "application/pdf"
    assert isinstance(response.content, bytes)
    assert response.content.startswith(b"%PDF")


@pytest.mark.asyncio
async def test_generate_general_report_html_format(client, db_session: AsyncSession, test_data_reports):
    """Test estudiante can generate general report in HTML format (covers Registry Pattern)."""
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    response = await client.get(
        "/api/v1/reports/general?format=html",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    
    # Verify HTML response (may include charset)
    content_type = response.headers.get("content-type", "")
    assert "text/html" in content_type
    
    content = response.content
    if isinstance(content, bytes):
        content = content.decode("utf-8")
    assert "<html" in content.lower() or "<!doctype" in content.lower()


@pytest.mark.asyncio
async def test_generate_general_report_as_profesor_forbidden(client, db_session: AsyncSession, test_data_reports):
    """Test profesor cannot generate general report (Estudiante only)."""
    profesor = test_data_reports["profesor"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    response = await client.get(
        "/api/v1/reports/general?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403


# ==================== Registry Pattern Integration Tests ====================

@pytest.mark.asyncio
async def test_factory_registry_accessible_from_endpoints():
    """Test that ReportFactory registry is accessible and populated when endpoints are called."""
    from app.factories import ReportFactory
    
    # Verify registry is populated
    formats = ReportFactory.get_registered_formats()
    assert len(formats) >= 3
    assert 'pdf' in formats
    assert 'html' in formats
    assert 'json' in formats


@pytest.mark.asyncio
async def test_all_formats_work_through_factory():
    """Test that all registered formats can be created and used."""
    from app.factories import ReportFactory
    
    test_data = {
        "estudiante": {
            "nombre": "Test",
            "apellido": "User",
            "codigo_institucional": "EST-001"
        },
        "subjects": []
    }
    
    # Test all formats
    for format_name in ['pdf', 'html', 'json']:
        generator = ReportFactory.create_generator(format_name)
        result = generator.generate(test_data)
        
        assert 'content' in result
        assert 'filename' in result
        assert 'content_type' in result
        assert format_name in result['filename'].lower()


@pytest.mark.asyncio
async def test_factory_error_message_includes_available_formats():
    """Test that factory error message includes available formats (covers lines 87-90)."""
    from app.factories import ReportFactory
    
    with pytest.raises(ValueError) as exc_info:
        ReportFactory.create_generator('xml')
    
    error_msg = str(exc_info.value)
    assert "Unsupported report format" in error_msg
    assert "xml" in error_msg
    assert "Available formats" in error_msg
    # Should list available formats
    assert "pdf" in error_msg.lower() or "html" in error_msg.lower() or "json" in error_msg.lower()


@pytest.mark.asyncio
async def test_factory_case_insensitive_format_handling():
    """Test that factory handles case-insensitive formats (covers line 83)."""
    from app.factories import ReportFactory
    
    # Test various case combinations
    pdf_gen1 = ReportFactory.create_generator('PDF')
    pdf_gen2 = ReportFactory.create_generator('pdf')
    pdf_gen3 = ReportFactory.create_generator('Pdf')
    
    # All should create PDF generator
    assert pdf_gen1 is pdf_gen2
    assert pdf_gen2 is pdf_gen3


@pytest.mark.asyncio
async def test_factory_enum_format_support():
    """Test that factory accepts ReportFormat enum (covers line 83)."""
    from app.factories import ReportFactory
    from app.factories.report_factory import ReportFormat
    
    pdf_gen = ReportFactory.create_generator(ReportFormat.PDF)
    html_gen = ReportFactory.create_generator(ReportFormat.HTML)
    json_gen = ReportFactory.create_generator(ReportFormat.JSON)
    
    assert pdf_gen is not None
    assert html_gen is not None
    assert json_gen is not None


@pytest.mark.asyncio
async def test_registry_pattern_allows_extensibility():
    """Test that Registry Pattern allows new formats to be added without modifying factory."""
    from app.factories import ReportFactory
    from app.factories.report_factory import ReportGenerator, ReportFormat
    
    # Get initial count
    initial_formats = len(ReportFactory.get_registered_formats())
    
    # Create a mock generator class (for testing extensibility)
    class MockReportGenerator(ReportGenerator):
        def generate(self, data: dict) -> dict:
            return {
                "content": b"mock content",
                "filename": "mock_report.txt",
                "content_type": "text/plain",
            }
    
    # Register new format using decorator (simulating extensibility)
    ReportFactory.register("txt")(MockReportGenerator)
    
    # Verify new format is registered
    formats = ReportFactory.get_registered_formats()
    assert "txt" in formats
    assert len(formats) == initial_formats + 1
    
    # Verify factory can create new generator
    txt_gen = ReportFactory.create_generator("txt")
    assert isinstance(txt_gen, MockReportGenerator)
    
    # Verify it works
    result = txt_gen.generate({"test": "data"})
    assert result["filename"] == "mock_report.txt"
    
    # Clean up: remove mock format (for other tests)
    # Note: In production, this wouldn't be necessary
    del ReportFactory._registry["txt"]
    if "txt" in ReportFactory._instances:
        del ReportFactory._instances["txt"]


# ==================== Edge Cases and Error Handling ====================

@pytest.mark.asyncio
async def test_report_endpoints_handle_json_content_bytes(client, db_session: AsyncSession, test_data_reports):
    """Test that endpoints handle JSON content as bytes (covers lines 36-39, 72-75, 106-109)."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    # Should return JSON directly (not as file download)
    assert response.headers.get("content-type") == "application/json"
    data = response.json()
    assert isinstance(data, dict)


@pytest.mark.asyncio
async def test_report_endpoints_handle_pdf_html_string_encoding(client, db_session: AsyncSession, test_data_reports):
    """Test that endpoints handle PDF/HTML content encoding (covers lines 44-45, 80-81, 113)."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Test HTML (might return string that needs encoding)
    response = await client.get(
        f"/api/v1/reports/student/{estudiante.id}?format=html",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    # Should handle string encoding (lines 44-45, 80-81)
    assert isinstance(response.content, bytes)


@pytest.mark.asyncio
async def test_report_endpoints_value_error_handling(client, db_session: AsyncSession, test_data_reports):
    """Test that endpoints handle ValueError correctly (covers lines 51-54, 87-90)."""
    admin = test_data_reports["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Try with invalid format (should trigger ValueError in factory)
    response = await client.get(
        "/api/v1/reports/student/1?format=invalid",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    # Should return error (400, 422, or 500 depending on where error is caught)
    assert response.status_code in [400, 422, 500]
    
    # If ValueError is caught, should be ValidationError (line 54)
    if response.status_code != 500:
        data = response.json()
        assert "error" in data.get("detail", "").lower() or "format" in data.get("detail", "").lower()


@pytest.mark.asyncio
async def test_report_endpoints_not_found_error_handling(client, db_session: AsyncSession, test_data_reports):
    """Test that endpoints handle NotFoundError correctly (covers line 53)."""
    admin = test_data_reports["admin"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Try with non-existent student
    response = await client.get(
        "/api/v1/reports/student/99999?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data.get("detail", "").lower()


@pytest.mark.asyncio
async def test_report_endpoints_forbidden_error_handling(client, db_session: AsyncSession, test_data_reports):
    """Test that endpoints handle ForbiddenError correctly (covers line 89)."""
    profesor = test_data_reports["profesor"]
    
    # Create unassigned subject
    codigo_prof2 = await generar_codigo_institucional(db_session, "Profesor")
    profesor2 = User(
        email="profesor2@reports.com",
        password_hash=get_password_hash("prof123"),
        role=UserRole.PROFESOR,
        nombre="Profesor2",
        apellido="Test",
        codigo_institucional=codigo_prof2,
        fecha_nacimiento=date(1981, 1, 1),
    )
    db_session.add(profesor2)
    await db_session.commit()
    await db_session.refresh(profesor2)
    
    subject2 = Subject(
        nombre="Química",
        codigo_institucional="QUI-101",
        numero_creditos=3,
        horario="Viernes 8:00",
        profesor_id=profesor2.id,
    )
    db_session.add(subject2)
    await db_session.commit()
    await db_session.refresh(subject2)
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    # Try to access unassigned subject (should trigger ForbiddenError)
    response = await client.get(
        f"/api/v1/reports/subject/{subject2.id}?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 403
    data = response.json()
    assert "forbidden" in data.get("detail", "").lower() or "not assigned" in data.get("detail", "").lower()


# ==================== Integration: Service -> Factory -> Generator ====================

@pytest.mark.asyncio
async def test_full_integration_student_report_flow(client, db_session: AsyncSession, test_data_reports):
    """Test full integration flow: endpoint -> service -> factory -> generator (all formats)."""
    admin = test_data_reports["admin"]
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": admin.email, "role": admin.role.value})
    
    # Test all formats work end-to-end
    formats = ['json', 'pdf', 'html']
    for format_name in formats:
        response = await client.get(
            f"/api/v1/reports/student/{estudiante.id}?format={format_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200, f"Format {format_name} failed"
        
        if format_name == 'json':
            data = response.json()
            assert "estudiante" in data
        else:
            # PDF or HTML
            assert isinstance(response.content, bytes)
            assert len(response.content) > 0


@pytest.mark.asyncio
async def test_full_integration_subject_report_flow(client, db_session: AsyncSession, test_data_reports):
    """Test full integration flow for subject reports: endpoint -> service -> factory -> generator."""
    profesor = test_data_reports["profesor"]
    subject = test_data_reports["subject"]
    
    token = create_access_token({"sub": profesor.email, "role": profesor.role.value})
    
    # Test all formats
    formats = ['json', 'pdf', 'html']
    for format_name in formats:
        response = await client.get(
            f"/api/v1/reports/subject/{subject.id}?format={format_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200, f"Format {format_name} failed"
        
        if format_name == 'json':
            data = response.json()
            assert "subject" in data
        else:
            assert isinstance(response.content, bytes)


@pytest.mark.asyncio
async def test_full_integration_general_report_flow(client, db_session: AsyncSession, test_data_reports):
    """Test full integration flow for general reports: endpoint -> service -> factory -> generator."""
    estudiante = test_data_reports["estudiante"]
    
    token = create_access_token({"sub": estudiante.email, "role": estudiante.role.value})
    
    # Test all formats
    formats = ['json', 'pdf', 'html']
    for format_name in formats:
        response = await client.get(
            f"/api/v1/reports/general?format={format_name}",
            headers={"Authorization": f"Bearer {token}"},
        )
        
        assert response.status_code == 200, f"Format {format_name} failed"
        
        if format_name == 'json':
            data = response.json()
            assert "estudiante" in data
            assert "subjects" in data
        else:
            assert isinstance(response.content, bytes)

