"""Report endpoints."""

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError, ValidationError
from app.models.user import User, UserRole
from app.services.admin_service import AdminService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
    require_profesor,
    require_estudiante,
)

router = APIRouter()


@router.get("/student/{estudiante_id}")
async def get_student_report(
    estudiante_id: int,
    format: str = Query("json", description="Report format: pdf, html, json"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Generate report for a student (Admin only)."""
    admin_service = AdminService(db, current_user)
    
    try:
        report = await admin_service.generate_student_report(estudiante_id, format)
        
        if format.lower() == "json":
            import json
            if isinstance(report["content"], bytes):
                content = json.loads(report["content"].decode("utf-8"))
            else:
                content = json.loads(report["content"])
            return content
        else:
            # For PDF and HTML, return as file download
            content = report["content"]
            if isinstance(content, str):
                content = content.encode("utf-8")
            return Response(
                content=content,
                media_type=report["content_type"],
                headers={"Content-Disposition": f'attachment; filename="{report["filename"]}"'},
            )
    except ValueError as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Student", str(e))
        raise ValidationError(str(e))


@router.get("/subject/{subject_id}")
async def get_subject_report(
    subject_id: int,
    format: str = Query("pdf", description="Report format: pdf, html, json"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_profesor),
):
    """Generate report for a subject (Profesor only, for assigned subjects)."""
    profesor_service = ProfesorService(db, current_user)
    
    try:
        report = await profesor_service.generate_subject_report(subject_id, format)
        
        if format.lower() == "json":
            import json
            if isinstance(report["content"], bytes):
                content = json.loads(report["content"].decode("utf-8"))
            else:
                content = json.loads(report["content"])
            return content
        else:
            # For PDF and HTML, return as file download
            content = report["content"]
            if isinstance(content, str):
                content = content.encode("utf-8")
            return Response(
                content=content,
                media_type=report["content_type"],
                headers={"Content-Disposition": f'attachment; filename="{report["filename"]}"'},
            )
    except ValueError as e:
        if "not found" in str(e).lower() or "not assigned" in str(e).lower():
            raise ForbiddenError(str(e))
        raise ValidationError(str(e))


@router.get("/general")
async def get_general_report(
    format: str = Query("pdf", description="Report format: pdf, html, json"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_estudiante),
):
    """Generate general report with all subjects (Estudiante only)."""
    estudiante_service = EstudianteService(db, current_user)
    
    report = await estudiante_service.generate_general_report(format)
    
    if format.lower() == "json":
        import json
        if isinstance(report["content"], bytes):
            content = json.loads(report["content"].decode("utf-8"))
        else:
            content = json.loads(report["content"])
        return content
    else:
        return Response(
            content=report["content"],
            media_type=report["content_type"],
            headers={"Content-Disposition": f'attachment; filename="{report["filename"]}"'},
        )

