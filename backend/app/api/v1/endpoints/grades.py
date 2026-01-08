"""Grade endpoints."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.grade import Grade
from app.models.enrollment import Enrollment
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse, EnrollmentInfo
from app.services.grade_service import GradeService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin_or_profesor,
    require_estudiante,
)

router = APIRouter()


# ==================== Helper Functions ====================

def serialize_grade_response(grade: Grade) -> GradeResponse:
    """Serialize a Grade object to GradeResponse with enrollment info."""
    grade_dict = {
        "id": grade.id,
        "enrollment_id": grade.enrollment_id,
        "nota": grade.nota,
        "periodo": grade.periodo,
        "fecha": grade.fecha,
        "observaciones": grade.observaciones,
        "enrollment": None,
    }
    
    # Serialize enrollment if it exists
    if grade.enrollment:
        grade_dict["enrollment"] = {
            "id": grade.enrollment.id,
            "estudiante_id": grade.enrollment.estudiante_id,
            "subject_id": grade.enrollment.subject_id,
        }
        grade_dict["enrollment"] = EnrollmentInfo(**grade_dict["enrollment"])
    
    return GradeResponse(**grade_dict)


async def load_grade_with_enrollment(
    db: AsyncSession, grade_id: int
) -> Grade:
    """Load a grade with its enrollment relationship."""
    stmt = (
        select(Grade)
        .where(Grade.id == grade_id)
        .options(selectinload(Grade.enrollment))
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def load_grades_with_enrollment(
    db: AsyncSession, grade_ids: Optional[List[int]] = None, 
    enrollment_id: Optional[int] = None, subject_id: Optional[int] = None
) -> List[Grade]:
    """Load grades with enrollment relationships based on filters."""
    stmt = select(Grade).options(selectinload(Grade.enrollment))
    
    if grade_ids:
        stmt = stmt.where(Grade.id.in_(grade_ids))
    elif enrollment_id:
        stmt = stmt.where(Grade.enrollment_id == enrollment_id)
    elif subject_id:
        from app.repositories.enrollment_repository import EnrollmentRepository
        repo = EnrollmentRepository(db)
        enrollments = await repo.get_by_subject(subject_id)
        enrollment_ids = [e.id for e in enrollments]
        if enrollment_ids:
            stmt = stmt.where(Grade.enrollment_id.in_(enrollment_ids))
        else:
            return []
    # If no filters, return all grades (for admin)
    
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def verify_profesor_subject_permission(
    db: AsyncSession, current_user: User, enrollment_id: int
) -> None:
    """Verify that a profesor has permission to access a subject via enrollment."""
    from app.repositories.enrollment_repository import EnrollmentRepository
    from app.repositories.subject_repository import SubjectRepository
    
    repo = EnrollmentRepository(db)
    enrollment = await repo.get_by_id(enrollment_id)
    
    if not enrollment:
        raise NotFoundError("Enrollment", enrollment_id)
    
    subject_repo = SubjectRepository(db)
    subject = await subject_repo.get_by_id(enrollment.subject_id)
    
    if not subject or subject.profesor_id != current_user.id:
        raise ForbiddenError("Cannot access grade for unassigned subject")


async def verify_profesor_can_access_subject(
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
        
        # Load enrollment relationship and serialize
        grade_with_enrollment = await load_grade_with_enrollment(db, grade.id)
        return serialize_grade_response(grade_with_enrollment)
    except ValueError as e:
        error_type = ForbiddenError if current_user.role == UserRole.PROFESOR else NotFoundError
        raise error_type("Grade", str(e))


async def _get_grades_as_estudiante(
    db: AsyncSession, current_user: User, subject_id: int
) -> List[GradeResponse]:
    """Get grades for an estudiante."""
    estudiante_service = EstudianteService(db, current_user)
    grades = await estudiante_service.get_grades_by_subject(subject_id)
    
    # Load enrollment relationships and serialize
    grade_ids = [grade.id for grade in grades]
    grades_with_enrollment = await load_grades_with_enrollment(db, grade_ids=grade_ids)
    return [serialize_grade_response(grade) for grade in grades_with_enrollment]


async def _get_grades_as_profesor(
    db: AsyncSession, current_user: User, subject_id: int, enrollment_id: Optional[int]
) -> List[GradeResponse]:
    """Get grades for a profesor."""
    await verify_profesor_can_access_subject(db, current_user, subject_id)
    
    grades = await load_grades_with_enrollment(
        db, enrollment_id=enrollment_id, subject_id=subject_id
    )
    return [serialize_grade_response(grade) for grade in grades]


async def _get_grades_as_admin(
    db: AsyncSession, subject_id: Optional[int], enrollment_id: Optional[int]
) -> List[GradeResponse]:
    """Get grades for an admin."""
    grades = await load_grades_with_enrollment(
        db, enrollment_id=enrollment_id, subject_id=subject_id
    )
    return [serialize_grade_response(grade) for grade in grades]


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
    service = GradeService(db)
    grade = await service.get_grade_by_id(grade_id)
    
    if not grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify permissions
    if current_user.role == UserRole.ESTUDIANTE:
        from app.repositories.enrollment_repository import EnrollmentRepository
        repo = EnrollmentRepository(db)
        enrollment = await repo.get_by_id(grade.enrollment_id)
        if enrollment and enrollment.estudiante_id != current_user.id:
            raise ForbiddenError("Cannot access other student's grades")
    
    # Load enrollment relationship and serialize
    grade_with_enrollment = await load_grade_with_enrollment(db, grade_id)
    return serialize_grade_response(grade_with_enrollment)


@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Update grade (Profesor or Admin only)."""
    service = GradeService(db)
    
    # Get existing grade to verify permissions
    existing_grade = await service.get_grade_by_id(grade_id)
    if not existing_grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify profesor permissions
    if current_user.role == UserRole.PROFESOR:
        await verify_profesor_subject_permission(
            db, current_user, existing_grade.enrollment_id
        )
    
    # Update grade
    grade = await service.update_grade(grade_id, grade_data)
    
    # Load enrollment relationship and serialize
    grade_with_enrollment = await load_grade_with_enrollment(db, grade_id)
    return serialize_grade_response(grade_with_enrollment)


@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """Delete grade (Profesor or Admin only)."""
    service = GradeService(db)
    
    # Get existing grade to verify permissions
    existing_grade = await service.get_grade_by_id(grade_id)
    if not existing_grade:
        raise NotFoundError("Grade", grade_id)
    
    # Verify profesor permissions
    if current_user.role == UserRole.PROFESOR:
        await verify_profesor_subject_permission(
            db, current_user, existing_grade.enrollment_id
        )
    
    # Delete grade
    deleted = await service.delete_grade(grade_id)
    if not deleted:
        raise NotFoundError("Grade", grade_id)


