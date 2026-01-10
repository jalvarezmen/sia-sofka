"""Enrollment endpoints - Refactored to use repository pattern."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError, ConflictError
from app.core.logging import logger
from app.models.user import User
from app.models.enrollment import Enrollment
from app.models.subject import Subject
from app.schemas.enrollment import EnrollmentCreate, EnrollmentResponse
from app.services.enrollment_service import EnrollmentService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.user_repository import UserRepository
from app.repositories.subject_repository import SubjectRepository
from app.api.v1.dependencies import require_admin

router = APIRouter()


async def _serialize_enrollments_batch(
    enrollments: List[Enrollment], db: AsyncSession
) -> List[EnrollmentResponse]:
    """Serialize a batch of enrollments with efficient batch loading of relationships.
    
    This function loads all estudiante and subject relationships in batches
    to avoid N+1 queries.
    """
    from app.schemas.enrollment import EstudianteInfo, SubjectInfo
    
    if not enrollments:
        return []
    
    # Collect all unique estudiante_ids and subject_ids
    unique_estudiante_ids = set()
    unique_subject_ids = set()
    
    for enrollment in enrollments:
        unique_estudiante_ids.add(enrollment.estudiante_id)
        unique_subject_ids.add(enrollment.subject_id)
    
    # Batch load all estudiantes
    estudiantes_map = {}
    if unique_estudiante_ids:
        from app.models.user import User as UserModel
        estudiantes_stmt = select(UserModel).where(UserModel.id.in_(list(unique_estudiante_ids)))
        estudiantes_result = await db.execute(estudiantes_stmt)
        estudiantes_list = estudiantes_result.scalars().all()
        estudiantes_map = {est.id: est for est in estudiantes_list}
    
    # Batch load all subjects
    subjects_map = {}
    if unique_subject_ids:
        subjects_stmt = select(Subject).where(Subject.id.in_(list(unique_subject_ids)))
        subjects_result = await db.execute(subjects_stmt)
        subjects_list = subjects_result.scalars().all()
        subjects_map = {subj.id: subj for subj in subjects_list}
    
    # Serialize each enrollment using batch-loaded maps
    responses = []
    for enrollment in enrollments:
        # Get estudiante from batch-loaded map
        estudiante_info = None
        if enrollment.estudiante_id in estudiantes_map:
            estudiante = estudiantes_map[enrollment.estudiante_id]
            estudiante_info = EstudianteInfo(
                id=estudiante.id,
                nombre=estudiante.nombre,
                apellido=estudiante.apellido,
                codigo_institucional=estudiante.codigo_institucional,
                email=estudiante.email,
            )
        
        # Get subject from batch-loaded map
        subject_info = None
        if enrollment.subject_id in subjects_map:
            subject = subjects_map[enrollment.subject_id]
            subject_info = SubjectInfo(
                id=subject.id,
                nombre=subject.nombre,
                codigo_institucional=subject.codigo_institucional,
            )
        
        responses.append(
            EnrollmentResponse(
                id=enrollment.id,
                estudiante_id=enrollment.estudiante_id,
                subject_id=enrollment.subject_id,
                created_at=enrollment.created_at,
                estudiante=estudiante_info,
                subject=subject_info,
            )
        )
    
    return responses


@router.post("", response_model=EnrollmentResponse, status_code=status.HTTP_201_CREATED)
async def create_enrollment(
    enrollment_data: EnrollmentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new enrollment (Admin only)."""
    service = EnrollmentService(db)
    
    try:
        enrollment = await service.create_enrollment(enrollment_data)
        await db.commit()
        await db.refresh(enrollment)
        
        # Load enrollment with relations using repository
        enrollment_repo = EnrollmentRepository(db)
        enrollment_with_relations = await enrollment_repo.get_with_relations(
            enrollment.id,
            relations=['estudiante', 'subject']
        )
        
        if not enrollment_with_relations:
            raise NotFoundError("Enrollment", enrollment.id)
        
        # Serialize single enrollment (use batch function for consistency)
        responses = await _serialize_enrollments_batch([enrollment_with_relations], db)
        return responses[0] if responses else None
    except ValueError as e:
        await db.rollback()
        if "already enrolled" in str(e).lower() or "duplicate" in str(e).lower():
            raise ConflictError(str(e))
        raise ValidationError(str(e))
    except Exception as e:
        await db.rollback()
        logger.error(f"Error creating enrollment: {str(e)}", exc_info=True)
        raise ValidationError(f"Error creating enrollment: {str(e)}")


@router.get("", response_model=List[EnrollmentResponse])
async def get_enrollments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all enrollments (Admin only)."""
    # Use repository to load enrollments with relations
    enrollment_repo = EnrollmentRepository(db)
    enrollments = await enrollment_repo.get_many_with_relations(
        relations=['estudiante', 'subject'],
        skip=skip,
        limit=limit
    )
    
    # Serialize enrollments with batch loading
    return await _serialize_enrollments_batch(enrollments, db)


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get enrollment by ID (Admin only)."""
    # Use repository to load enrollment with relations
    enrollment_repo = EnrollmentRepository(db)
    enrollment = await enrollment_repo.get_with_relations(
        enrollment_id,
        relations=['estudiante', 'subject']
    )
    
    if not enrollment:
        raise NotFoundError("Enrollment", enrollment_id)
    
    # Serialize single enrollment (use batch function for consistency)
    responses = await _serialize_enrollments_batch([enrollment], db)
    return responses[0] if responses else None


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

