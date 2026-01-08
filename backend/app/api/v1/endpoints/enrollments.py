"""Enrollment endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.models.user import User
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService
from app.api.v1.dependencies import require_admin

router = APIRouter()


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new enrollment (Admin only)."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.enrollment import Enrollment
    
    service = EnrollmentService(db)
    
    try:
        enrollment = await service.create_enrollment(enrollment_data)
        await db.commit()
        await db.refresh(enrollment)
        
        # Recargar con relaciones
        stmt = (
            select(Enrollment)
            .where(Enrollment.id == enrollment.id)
            .options(
                selectinload(Enrollment.estudiante),
                selectinload(Enrollment.subject)
            )
        )
        result = await db.execute(stmt)
        enrollment_with_relations = result.scalar_one()
        return enrollment_with_relations
    except ValueError as e:
        await db.rollback()
        if "already enrolled" in str(e).lower() or "duplicate" in str(e).lower():
            raise ConflictError(str(e))
        raise ValidationError(str(e))
    except Exception as e:
        await db.rollback()
        raise ValidationError(f"Error creating enrollment: {str(e)}")


@router.get("", response_model=List[EnrollmentResponse])
async def get_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all enrollments (Admin only)."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.enrollment import Enrollment
    from app.models.user import User as UserModel
    from app.models.subject import Subject
    
    stmt = (
        select(Enrollment)
        .options(
            selectinload(Enrollment.estudiante),
            selectinload(Enrollment.subject)
        )
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    enrollments = result.scalars().all()
    
    # Serializar manualmente para asegurar que las relaciones se incluyan
    from app.schemas.enrollment import EnrollmentResponse
    from app.repositories.user_repository import UserRepository
    from app.repositories.subject_repository import SubjectRepository
    
    user_repo = UserRepository(db)
    subject_repo = SubjectRepository(db)
    
    serialized_enrollments = []
    for enrollment in enrollments:
        # Construir el objeto de respuesta con las relaciones
        enrollment_dict = {
            "id": enrollment.id,
            "estudiante_id": enrollment.estudiante_id,
            "subject_id": enrollment.subject_id,
            "created_at": enrollment.created_at,
            "estudiante": None,
            "subject": None,
        }
        
        # Cargar estudiante siempre (hacer query manual para asegurar)
        try:
            estudiante = await user_repo.get_by_id(enrollment.estudiante_id)
            if estudiante:
                enrollment_dict["estudiante"] = {
                    "id": estudiante.id,
                    "nombre": estudiante.nombre,
                    "apellido": estudiante.apellido,
                    "codigo_institucional": estudiante.codigo_institucional,
                    "email": estudiante.email,
                }
        except Exception as e:
            print(f"ERROR loading estudiante {enrollment.estudiante_id}: {e}")
        
        # Cargar subject siempre (hacer query manual para asegurar)
        try:
            subject = await subject_repo.get_by_id(enrollment.subject_id)
            if subject:
                enrollment_dict["subject"] = {
                    "id": subject.id,
                    "nombre": subject.nombre,
                    "codigo_institucional": subject.codigo_institucional,
                }
        except Exception as e:
            print(f"ERROR loading subject {enrollment.subject_id}: {e}")
        
        serialized_enrollments.append(EnrollmentResponse(**enrollment_dict))
    
    return serialized_enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get enrollment by ID (Admin only)."""
    from sqlalchemy.orm import selectinload
    from sqlalchemy import select
    from app.models.enrollment import Enrollment
    
    stmt = (
        select(Enrollment)
        .where(Enrollment.id == enrollment_id)
        .options(
            selectinload(Enrollment.estudiante),
            selectinload(Enrollment.subject)
        )
    )
    result = await db.execute(stmt)
    enrollment = result.scalar_one_or_none()
    
    if not enrollment:
        raise NotFoundError("Enrollment", enrollment_id)
    
    return enrollment


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete enrollment (Admin only)."""
    service = EnrollmentService(db)
    deleted = await service.delete_enrollment(enrollment_id)
    
    if not deleted:
        raise NotFoundError("Enrollment", enrollment_id)

