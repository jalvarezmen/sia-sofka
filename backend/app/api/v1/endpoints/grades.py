"""Grade endpoints."""

from typing import List
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.schemas.grade import GradeCreate, GradeUpdate, GradeResponse
from app.services.grade_service import GradeService
from app.services.profesor_service import ProfesorService
from app.services.estudiante_service import EstudianteService
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin_or_profesor,
    require_estudiante,
)

router = APIRouter()


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
    if current_user.role == UserRole.PROFESOR:
        profesor_service = ProfesorService(db, current_user)
        try:
            grade = await profesor_service.create_grade(grade_data, subject_id)
            return grade
        except ValueError as e:
            raise ForbiddenError(str(e))
    else:
        # Admin can create grades for any subject
        service = GradeService(db)
        try:
            grade = await service.create_grade(grade_data)
            return grade
        except ValueError as e:
            raise NotFoundError("Grade", str(e))


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
    service = GradeService(db)
    
    if current_user.role == UserRole.ESTUDIANTE:
        if not subject_id:
            raise ForbiddenError("Subject ID is required for estudiantes")
        
        estudiante_service = EstudianteService(db, current_user)
        try:
            grades = await estudiante_service.get_grades_by_subject(subject_id)
            return grades
        except ValueError as e:
            raise ForbiddenError(str(e))
    
    elif current_user.role == UserRole.PROFESOR:
        if not subject_id:
            raise ForbiddenError("Subject ID is required for profesores")
        
        profesor_service = ProfesorService(db, current_user)
        # Verify subject is assigned to profesor
        subjects = await profesor_service.get_assigned_subjects()
        subject_ids = [s.id for s in subjects]
        
        if subject_id not in subject_ids:
            raise ForbiddenError("Subject is not assigned to this profesor")
        
        if enrollment_id:
            grades = await service.get_grades_by_enrollment(enrollment_id)
        else:
            from app.repositories.enrollment_repository import EnrollmentRepository
            repo = EnrollmentRepository(db)
            enrollments = await repo.get_by_subject(subject_id)
            all_grades = []
            for enrollment in enrollments:
                grades = await service.get_grades_by_enrollment(enrollment.id)
                all_grades.extend(grades)
            return all_grades
    
    else:  # Admin
        if enrollment_id:
            grades = await service.get_grades_by_enrollment(enrollment_id)
            return grades
        elif subject_id:
            from app.repositories.enrollment_repository import EnrollmentRepository
            repo = EnrollmentRepository(db)
            enrollments = await repo.get_by_subject(subject_id)
            all_grades = []
            for enrollment in enrollments:
                grades = await service.get_grades_by_enrollment(enrollment.id)
                all_grades.extend(grades)
            return all_grades
        else:
            raise ForbiddenError("Enrollment ID or Subject ID is required")


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
    
    return grade


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
    
    if current_user.role == UserRole.PROFESOR:
        from app.repositories.enrollment_repository import EnrollmentRepository
        from app.repositories.subject_repository import SubjectRepository
        
        repo = EnrollmentRepository(db)
        enrollment = await repo.get_by_id(existing_grade.enrollment_id)
        
        if enrollment:
            subject_repo = SubjectRepository(db)
            subject = await subject_repo.get_by_id(enrollment.subject_id)
            
            if not subject or subject.profesor_id != current_user.id:
                raise ForbiddenError("Cannot update grade for unassigned subject")
    
    grade = await service.update_grade(grade_id, grade_data)
    return grade


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
    
    if current_user.role == UserRole.PROFESOR:
        from app.repositories.enrollment_repository import EnrollmentRepository
        from app.repositories.subject_repository import SubjectRepository
        
        repo = EnrollmentRepository(db)
        enrollment = await repo.get_by_id(existing_grade.enrollment_id)
        
        if enrollment:
            subject_repo = SubjectRepository(db)
            subject = await subject_repo.get_by_id(enrollment.subject_id)
            
            if not subject or subject.profesor_id != current_user.id:
                raise ForbiddenError("Cannot delete grade for unassigned subject")
    
    deleted = await service.delete_grade(grade_id)
    if not deleted:
        raise NotFoundError("Grade", grade_id)

