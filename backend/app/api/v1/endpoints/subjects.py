"""Subject endpoints - Refactored to use repository pattern and serializers."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.models.subject import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.services.admin_service import AdminService
from app.services.subject_service import SubjectService
from app.api.v1.dependencies import require_admin, get_current_active_user
from app.api.v1.serializers.subject_serializer import SubjectSerializer

router = APIRouter()


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
async def create_subject(
    subject_data: SubjectCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new subject (Admin only)."""
    admin_service = AdminService(db, current_user)
    
    try:
        subject = await admin_service.create_subject(subject_data)
        return subject
    except ValueError as e:
        raise ValidationError(str(e))


@router.get("", response_model=List[SubjectResponse])
async def get_subjects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get subjects.
    
    - Admin: can see all subjects
    - Profesor: can see only their assigned subjects
    """
    from app.models.user import UserRole
    from app.services.profesor_service import ProfesorService
    from app.core.exceptions import ForbiddenError
    
    if current_user.role == UserRole.PROFESOR:
        # Profesor: solo sus materias asignadas
        profesor_service = ProfesorService(db, current_user)
        subjects = await profesor_service.get_assigned_subjects()
        # Cargar relación profesor si es necesario
        for subject in subjects:
            await db.refresh(subject, ["profesor"])
        return SubjectSerializer.serialize_batch(subjects)
    
    elif current_user.role == UserRole.ADMIN:
        # Admin: todas las materias (comportamiento actual)
        stmt = (
            select(Subject)
            .options(selectinload(Subject.profesor))
            .offset(skip)
            .limit(limit)
        )
        result = await db.execute(stmt)
        subjects = result.scalars().all()
        return SubjectSerializer.serialize_batch(subjects)
    
    else:
        # Estudiante u otro rol: no permitido
        raise ForbiddenError("Not enough permissions")


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get subject by ID (Admin only)."""
    service = SubjectService(db)
    subject = await service.get_subject_by_id(subject_id)
    
    if not subject:
        raise NotFoundError("Subject", subject_id)
    
    return subject


@router.put("/{subject_id}", response_model=SubjectResponse)
async def update_subject(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update subject (Admin only)."""
    admin_service = AdminService(db, current_user)
    subject = await admin_service.update_subject(subject_id, subject_data)
    
    if not subject:
        raise NotFoundError("Subject", subject_id)
    
    return subject


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete subject (Admin only)."""
    admin_service = AdminService(db, current_user)
    deleted = await admin_service.delete_subject(subject_id)
    
    if not deleted:
        raise NotFoundError("Subject", subject_id)

