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
    service = EnrollmentService(db)
    
    try:
        enrollment = await service.create_enrollment(enrollment_data)
        return enrollment
    except ValueError as e:
        if "already enrolled" in str(e).lower() or "duplicate" in str(e).lower():
            raise ConflictError(str(e))
        raise ValidationError(str(e))


@router.get("", response_model=List[EnrollmentResponse])
async def get_enrollments(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all enrollments (Admin only)."""
    from app.repositories.enrollment_repository import EnrollmentRepository
    
    repo = EnrollmentRepository(db)
    enrollments = await repo.get_all(skip, limit)
    return enrollments


@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get enrollment by ID (Admin only)."""
    service = EnrollmentService(db)
    enrollment = await service.get_enrollment_by_id(enrollment_id)
    
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

