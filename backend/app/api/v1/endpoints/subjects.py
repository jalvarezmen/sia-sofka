"""Subject endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User
from app.schemas.subject import SubjectCreate, SubjectUpdate, SubjectResponse
from app.services.admin_service import AdminService
from app.api.v1.dependencies import require_admin

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
    current_user: User = Depends(require_admin),
):
    """Get all subjects (Admin only)."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.subject import Subject
    from app.schemas.subject import SubjectResponse
    
    stmt = (
        select(Subject)
        .options(selectinload(Subject.profesor))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    subjects = result.scalars().all()
    
    # Serializar manualmente para asegurar que las relaciones se incluyan
    serialized_subjects = []
    for subject in subjects:
        subject_dict = {
            "id": subject.id,
            "nombre": subject.nombre,
            "codigo_institucional": subject.codigo_institucional,
            "numero_creditos": subject.numero_creditos,
            "horario": subject.horario,
            "descripcion": subject.descripcion,
            "profesor_id": subject.profesor_id,
            "profesor": None,
        }
        
        # Incluir profesor si está cargado
        if subject.profesor:
            from app.schemas.subject import ProfesorInfo
            subject_dict["profesor"] = ProfesorInfo(
                id=subject.profesor.id,
                nombre=subject.profesor.nombre,
                apellido=subject.profesor.apellido,
                codigo_institucional=subject.profesor.codigo_institucional,
                email=subject.profesor.email,
            )
        
        serialized_subjects.append(SubjectResponse(**subject_dict))
    
    return serialized_subjects


@router.get("/{subject_id}", response_model=SubjectResponse)
async def get_subject(
    subject_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get subject by ID (Admin only)."""
    from app.services.subject_service import SubjectService
    
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

