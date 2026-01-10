"""Grade endpoints - Refactored to use repository pattern."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.grade import Grade
from app.models.subject import Subject
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.services.grade_service import GradeService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.repositories.grade_repository import GradeRepository
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import SubjectRepository
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin_or_profesor,
)

router = APIRouter()


# ==================== Helper Functions ====================

async def _verify_profesor_subject_permission(
    db: AsyncSession, current_user: User, enrollment_id: int
) -> None:
    """Verify that a profesor has permission to access a subject via enrollment."""
    enrollment_repo = EnrollmentRepository(db)
    enrollment = await enrollment_repo.get_by_id(enrollment_id)
    
    if not enrollment:
        raise NotFoundError("Enrollment", enrollment_id)
    
    subject_repo = SubjectRepository(db)
    subject = await subject_repo.get_by_id(enrollment.subject_id)
    
    if not subject or subject.profesor_id != current_user.id:
        raise ForbiddenError("Cannot access grade for unassigned subject")


async def _verify_profesor_can_access_subject(
    db: AsyncSession, current_user: User, subject_id: int
) -> None:
    """Verify that a profesor has access to a subject."""
    profesor_service = ProfesorService(db, current_user)
    subjects = await profesor_service.get_assigned_subjects()
    subject_ids = [s.id for s in subjects]
    
    if subject_id not in subject_ids:
        raise ForbiddenError("Subject is not assigned to this profesor")


# ==================== Endpoints ====================


@router.post("", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    grade_data: GradeCreate,
    subject_id: int = Query(..., description="Subject ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Create a new grade (Profesor or Admin only).
    
    Profesores can only create grades for their assigned subjects.
    """
    try:
        if current_user.role == UserRole.PROFESOR:
            profesor_service = ProfesorService(db, current_user)
            grade = await profesor_service.create_grade(grade_data, subject_id)
        else:
            # Admin can create grades for any subject
            service = GradeService(db)
            grade = await service.create_grade(grade_data)
        
        # Load grade with enrollment using repository
        grade_repo = GradeRepository(db)
        grade_with_enrollment = await grade_repo.get_with_relations(grade.id)
        
        if not grade_with_enrollment:
            raise NotFoundError("Grade", grade.id)
        
        # Serialize single grade (use batch function for consistency)
        responses = await _serialize_grades_batch([grade_with_enrollment], db)
        return responses[0] if responses else None
    except ValueError as e:
        error_type = ForbiddenError if current_user.role == UserRole.PROFESOR else NotFoundError
        raise error_type("Grade", str(e))


async def _serialize_grades_batch(grades: List[Grade], db: AsyncSession) -> List[GradeResponse]:
    """Serialize a batch of grades with efficient batch loading of relationships.
    
    This function loads all estudiante and subject relationships in batches
    to avoid N+1 queries.
    """
    from app.schemas.grade import EnrollmentInfo, EstudianteBasicInfo, SubjectBasicInfo
    
    if not grades:
        return []
    
    # Collect all unique estudiante_ids and subject_ids
    unique_estudiante_ids = set()
    unique_subject_ids = set()
    
    for grade in grades:
        if grade.enrollment:
            unique_estudiante_ids.add(grade.enrollment.estudiante_id)
            unique_subject_ids.add(grade.enrollment.subject_id)
    
    # Batch load all estudiantes
    estudiantes_map = {}
    if unique_estudiante_ids:
        estudiantes_stmt = select(User).where(User.id.in_(list(unique_estudiante_ids)))
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
    
    # Serialize each grade using batch-loaded maps
    responses = []
    for grade in grades:
        response_data = {
            "id": grade.id,
            "enrollment_id": grade.enrollment_id,
            "nota": grade.nota,
            "periodo": grade.periodo,
            "fecha": grade.fecha,
            "observaciones": grade.observaciones,
        }
        
        enrollment_info = None
        if grade.enrollment:
            # Get estudiante from batch-loaded map
            estudiante_info = None
            if grade.enrollment.estudiante_id in estudiantes_map:
                estudiante = estudiantes_map[grade.enrollment.estudiante_id]
                estudiante_info = EstudianteBasicInfo(
                    id=estudiante.id,
                    nombre=estudiante.nombre,
                    apellido=estudiante.apellido,
                    email=estudiante.email,
                )
            
            # Get subject from batch-loaded map
            subject_info = None
            if grade.enrollment.subject_id in subjects_map:
                subject = subjects_map[grade.enrollment.subject_id]
                subject_info = SubjectBasicInfo(
                    id=subject.id,
                    nombre=subject.nombre,
                    codigo_institucional=subject.codigo_institucional,
                )
            
            enrollment_info = EnrollmentInfo(
                id=grade.enrollment.id,
                estudiante_id=grade.enrollment.estudiante_id,
                subject_id=grade.enrollment.subject_id,
                estudiante=estudiante_info,
                subject=subject_info,
            )
        
        responses.append(GradeResponse(**response_data, enrollment=enrollment_info))
    
    return responses


async def _get_grades_as_estudiante(
    db: AsyncSession, current_user: User, subject_id: int
) -> List[GradeResponse]:
    """Get grades for an estudiante."""
    estudiante_service = EstudianteService(db, current_user)
    grades = await estudiante_service.get_grades_by_subject(subject_id)
    
    # Load grades with enrollment relationships using repository
    grade_repo = GradeRepository(db)
    grade_ids = [grade.id for grade in grades]
    grades_with_enrollment = await grade_repo.get_many_with_relations(
        grade_ids=grade_ids,
        relations=['enrollment']
    )
    # Serialize grades with batch loading
    return await _serialize_grades_batch(grades_with_enrollment, db)


async def _get_grades_as_profesor(
    db: AsyncSession, current_user: User, subject_id: int, enrollment_id: Optional[int]
) -> List[GradeResponse]:
    """Get grades for a profesor."""
    await _verify_profesor_can_access_subject(db, current_user, subject_id)
    
    # Use repository to load grades with relations
    grade_repo = GradeRepository(db)
    grades = await grade_repo.get_many_with_relations(
        enrollment_id=enrollment_id,
        subject_id=subject_id,
        relations=['enrollment']
    )
    # Serialize grades with batch loading
    return await _serialize_grades_batch(grades, db)


async def _get_grades_as_admin(
    db: AsyncSession, subject_id: Optional[int], enrollment_id: Optional[int]
) -> List[GradeResponse]:
    """Get grades for an admin."""
    grade_repo = GradeRepository(db)
    grades = await grade_repo.get_many_with_relations(
        enrollment_id=enrollment_id,
        subject_id=subject_id,
        relations=['enrollment']
    )
    # Serialize grades with batch loading
    return await _serialize_grades_batch(grades, db)


@router.get("", response_model=List[GradeResponse])
async def get_grades(
    subject_id: int = Query(None, description="Filter by subject ID"),
    enrollment_id: int = Query(None, description="Filter by enrollment ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get grades.
    
    - Estudiante: can only see their own grades
    - Profesor: can see grades for their assigned subjects
    - Admin: can see all grades
    """
    if current_user.role == UserRole.ESTUDIANTE:
        if not subject_id:
            raise ForbiddenError("Subject ID is required for estudiantes")
        try:
            return await _get_grades_as_estudiante(db, current_user, subject_id)
        except ValueError as e:
            raise ForbiddenError(str(e))
    
    elif current_user.role == UserRole.PROFESOR:
        if not subject_id:
            raise ForbiddenError("Subject ID is required for profesores")
        return await _get_grades_as_profesor(db, current_user, subject_id, enrollment_id)
    
    else:  # Admin
        return await _get_grades_as_admin(db, subject_id, enrollment_id)


@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get grade by ID."""
    grade_repo = GradeRepository(db)
    grade = await grade_repo.get_with_relations(grade_id)
    
    if not grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify permissions
    if current_user.role == UserRole.ESTUDIANTE:
        enrollment_repo = EnrollmentRepository(db)
        enrollment = await enrollment_repo.get_by_id(grade.enrollment_id)
        if enrollment and enrollment.estudiante_id != current_user.id:
            raise ForbiddenError("Cannot access other student's grades")
    
    # Serialize single grade (use batch function for consistency)
    responses = await _serialize_grades_batch([grade], db)
    return responses[0] if responses else None


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Update grade (Profesor or Admin only)."""
    grade_repo = GradeRepository(db)
    
    # Get existing grade to verify permissions
    existing_grade = await grade_repo.get_by_id(grade_id)
    if not existing_grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify profesor permissions
    if current_user.role == UserRole.PROFESOR:
        await _verify_profesor_subject_permission(
            db, current_user, existing_grade.enrollment_id
        )
    
    # Update grade using service (business logic)
    service = GradeService(db)
    await service.update_grade(grade_id, grade_data)
    
    # Load updated grade with enrollment relationship
    grade = await grade_repo.get_with_relations(grade_id)
    if not grade:
        raise NotFoundError("Grade", grade_id)
    
    # Serialize single grade (use batch function for consistency)
    responses = await _serialize_grades_batch([grade], db)
    return responses[0] if responses else None


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Delete grade (Profesor or Admin only)."""
    grade_repo = GradeRepository(db)
    
    # Get existing grade to verify permissions
    existing_grade = await grade_repo.get_by_id(grade_id)
    if not existing_grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify profesor permissions
    if current_user.role == UserRole.PROFESOR:
        await _verify_profesor_subject_permission(
            db, current_user, existing_grade.enrollment_id
        )
    
    # Delete grade using service (business logic)
    service = GradeService(db)
    deleted = await service.delete_grade(grade_id)
    if not deleted:
        raise NotFoundError("Grade", grade_id)


