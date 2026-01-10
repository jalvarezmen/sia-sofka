"""Grade endpoints - Simplified version."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload, joinedload

from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.grade import Grade
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.services.grade_service import GradeService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import SubjectRepository
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin_or_profesor,
)

router = APIRouter()


# ==================== Helper Functions ====================

def _to_response(grade: Grade) -> GradeResponse:
    """Convert Grade model to response schema."""
    # Build response dict manually to avoid Pydantic serialization issues
    response_data = {
        "id": grade.id,
        "enrollment_id": grade.enrollment_id,
        "nota": float(grade.nota),  # Convert Decimal to float
        "periodo": grade.periodo,
        "fecha": grade.fecha,
        "observaciones": grade.observaciones,
        "enrollment": None
    }
    
    # Add enrollment data with student and subject if it exists
    if grade.enrollment:
        enrollment_data = {
            "id": grade.enrollment.id,
            "estudiante_id": grade.enrollment.estudiante_id,
            "subject_id": grade.enrollment.subject_id,
            "estudiante": None,
            "subject": None
        }
        
        # Add student info
        if grade.enrollment.estudiante:
            enrollment_data["estudiante"] = {
                "id": grade.enrollment.estudiante.id,
                "nombre": grade.enrollment.estudiante.nombre,
                "apellido": grade.enrollment.estudiante.apellido,
                "email": grade.enrollment.estudiante.email
            }
            print(f"✅ DEBUG: Student loaded for grade {grade.id}: {enrollment_data['estudiante']}")  # DEBUG
        else:
            print(f"❌ DEBUG: NO student for grade {grade.id}")  # DEBUG
        
        # Add subject info
        if grade.enrollment.subject:
            enrollment_data["subject"] = {
                "id": grade.enrollment.subject.id,
                "nombre": grade.enrollment.subject.nombre,
                "codigo_institucional": grade.enrollment.subject.codigo_institucional
            }
            print(f"✅ DEBUG: Subject loaded for grade {grade.id}: {enrollment_data['subject']}")  # DEBUG
        else:
            print(f"❌ DEBUG: NO subject for grade {grade.id}")  # DEBUG
        
        response_data["enrollment"] = enrollment_data
    
    return GradeResponse(**response_data)


async def _load_grade(db: AsyncSession, grade_id: int) -> Grade:
    """Load a single grade with enrollment, student and subject data."""
    from app.models.enrollment import Enrollment
    
    result = await db.execute(
        select(Grade)
        .where(Grade.id == grade_id)
        .options(
            selectinload(Grade.enrollment),
        )
    )
    grade = result.scalar_one_or_none()
    if not grade:
        raise NotFoundError("Grade", grade_id)
    
    # Load nested relationships explicitly
    if grade.enrollment:
        await db.execute(
            select(Enrollment)
            .where(Enrollment.id == grade.enrollment.id)
            .options(
                selectinload(Enrollment.estudiante),
                selectinload(Enrollment.subject)
            )
        )
    
    print(f"🔍 DEBUG: Loaded grade {grade_id} with relationships")
    return grade


async def _check_enrollment_exists(db: AsyncSession, enrollment_id: int):
    """Verify that enrollment exists."""
    repo = EnrollmentRepository(db)
    enrollment = await repo.get_by_id(enrollment_id)
    if not enrollment:
        raise NotFoundError("Enrollment", enrollment_id)
    return enrollment


async def _check_profesor_owns_subject(db: AsyncSession, profesor_id: int, subject_id: int):
    """Verify that profesor owns the subject."""
    subject_repo = SubjectRepository(db)
    subject = await subject_repo.get_by_id(subject_id)
    if not subject or subject.profesor_id != profesor_id:
        raise ForbiddenError("You don't have permission for this subject")


# ==================== CREATE GRADE ====================

@router.post("", response_model=GradeResponse, status_code=status.HTTP_201_CREATED)
async def create_grade(
    grade_data: GradeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """
    Create a new grade.
    
    - Profesor: Can only create grades for their own subjects
    - Admin: Can create grades for any subject
    
    Steps:
    1. Verify enrollment exists
    2. If profesor, verify they own the subject
    3. Create the grade
    4. Return grade with enrollment data
    """
    # 1. Check enrollment exists and get subject_id
    enrollment = await _check_enrollment_exists(db, grade_data.enrollment_id)
    
    # 2. If profesor, verify permission
    if current_user.role == UserRole.PROFESOR:
        await _check_profesor_owns_subject(db, current_user.id, enrollment.subject_id)
    
    # 3. Create grade
    service = GradeService(db)
    grade = await service.create_grade(grade_data)
    
    # 4. Load with enrollment and return
    grade = await _load_grade(db, grade.id)
    return _to_response(grade)


# ==================== GET GRADES ====================

@router.get("", response_model=List[GradeResponse])
async def get_grades(
    subject_id: Optional[int] = Query(None, description="Filter by subject ID"),
    enrollment_id: Optional[int] = Query(None, description="Filter by enrollment ID"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get grades based on user role:
    
    - Estudiante: Only their grades (requires subject_id)
    - Profesor: Only their subject's grades (requires subject_id)
    - Admin: All grades (filters optional)
    """
    from app.models.enrollment import Enrollment
    from app.models.subject import Subject
    
    # Use joinedload for all relationships (better for this case)
    query = select(Grade).options(
        joinedload(Grade.enrollment).joinedload(Enrollment.estudiante),
        joinedload(Grade.enrollment).joinedload(Enrollment.subject)
    )
    
    print(f"🔍 DEBUG: Query options configured for grades endpoint")
    
    # ESTUDIANTE: Only their own grades
    if current_user.role == UserRole.ESTUDIANTE:
        if not subject_id:
            raise ForbiddenError("Estudiantes must provide subject_id")
        
        # Get enrollments for this student in this subject
        enrollment_repo = EnrollmentRepository(db)
        enrollments = await enrollment_repo.get_by_estudiante(current_user.id)
        student_enrollment_ids = [
            e.id for e in enrollments if e.subject_id == subject_id
        ]
        
        if not student_enrollment_ids:
            return []
        
        query = query.where(Grade.enrollment_id.in_(student_enrollment_ids))
    
    # PROFESOR: Only their subject's grades
    elif current_user.role == UserRole.PROFESOR:
        if not subject_id:
            raise ForbiddenError("Profesores must provide subject_id")
        
        # Verify profesor owns this subject
        await _check_profesor_owns_subject(db, current_user.id, subject_id)
        
        # Get all enrollments for this subject
        enrollment_repo = EnrollmentRepository(db)
        enrollments = await enrollment_repo.get_by_subject(subject_id)
        subject_enrollment_ids = [e.id for e in enrollments]
        
        if not subject_enrollment_ids:
            return []
        
        query = query.where(Grade.enrollment_id.in_(subject_enrollment_ids))
        
        # Optional: filter by specific enrollment
        if enrollment_id:
            query = query.where(Grade.enrollment_id == enrollment_id)
    
    # ADMIN: All grades with optional filters
    else:
        if subject_id:
            enrollment_repo = EnrollmentRepository(db)
            enrollments = await enrollment_repo.get_by_subject(subject_id)
            enrollment_ids = [e.id for e in enrollments]
            if not enrollment_ids:
                return []
            query = query.where(Grade.enrollment_id.in_(enrollment_ids))
        
        if enrollment_id:
            query = query.where(Grade.enrollment_id == enrollment_id)
    
    # Execute query and return
    result = await db.execute(query)
    grades = result.scalars().all()
    return [_to_response(grade) for grade in grades]


# ==================== GET SINGLE GRADE ====================

@router.get("/{grade_id}", response_model=GradeResponse)
async def get_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a specific grade by ID.
    
    Permissions:
    - Estudiante: Only their own grades
    - Profesor: Only grades from their subjects
    - Admin: Any grade
    """
    grade = await _load_grade(db, grade_id)
    
    # Load enrollment to check permissions
    enrollment = await _check_enrollment_exists(db, grade.enrollment_id)
    
    # Check permissions based on role
    if current_user.role == UserRole.ESTUDIANTE:
        if enrollment.estudiante_id != current_user.id:
            raise ForbiddenError("You can only view your own grades")
    
    elif current_user.role == UserRole.PROFESOR:
        await _check_profesor_owns_subject(db, current_user.id, enrollment.subject_id)
    
    # Admin can see everything
    return _to_response(grade)


# ==================== UPDATE GRADE ====================

@router.put("/{grade_id}", response_model=GradeResponse)
async def update_grade(
    grade_id: int,
    grade_data: GradeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """
    Update a grade.
    
    - Profesor: Can only update grades for their subjects
    - Admin: Can update any grade
    """
    # 1. Get grade and enrollment
    grade = await _load_grade(db, grade_id)
    enrollment = await _check_enrollment_exists(db, grade.enrollment_id)
    
    # 2. If profesor, verify permission
    if current_user.role == UserRole.PROFESOR:
        await _check_profesor_owns_subject(db, current_user.id, enrollment.subject_id)
    
    # 3. Update grade
    service = GradeService(db)
    updated_grade = await service.update_grade(grade_id, grade_data)
    
    # 4. Return updated grade
    grade = await _load_grade(db, grade_id)
    return _to_response(grade)


# ==================== DELETE GRADE ====================

@router.delete("/{grade_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grade(
    grade_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin_or_profesor),
):
    """
    Delete a grade.
    
    - Profesor: Can only delete grades for their subjects
    - Admin: Can delete any grade
    """
    # 1. Get grade and enrollment
    grade = await _load_grade(db, grade_id)
    enrollment = await _check_enrollment_exists(db, grade.enrollment_id)
    
    # 2. If profesor, verify permission
    if current_user.role == UserRole.PROFESOR:
        await _check_profesor_owns_subject(db, current_user.id, enrollment.subject_id)
    
    # 3. Delete grade
    service = GradeService(db)
    await service.delete_grade(grade_id)


