"""User endpoints."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.exceptions import NotFoundError, ValidationError
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.services.admin_service import AdminService
from app.api.v1.dependencies import require_admin, get_current_active_user

router = APIRouter()


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new user (Admin only)."""
    admin_service = AdminService(db, current_user)
    
    try:
        if user_data.role == UserRole.ESTUDIANTE:
            user = await admin_service.create_estudiante(user_data)
        elif user_data.role == UserRole.PROFESOR:
            user = await admin_service.create_profesor(user_data)
        else:
            raise ValidationError("Invalid role for user creation")
        return user
    except ValueError as e:
        raise ValidationError(str(e))


@router.get("", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all users (Admin only)."""
    admin_service = AdminService(db, current_user)
    estudiantes = await admin_service.get_all_estudiantes(skip, limit)
    profesores = await admin_service.get_all_profesores(skip, limit)
    return list(estudiantes) + list(profesores)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get user by ID (Admin only)."""
    from app.services.user_service import UserService
    
    user_service = UserService(db)
    user = await user_service.get_user_by_id(user_id)
    
    if not user:
        raise NotFoundError("User", user_id)
    
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update user (Admin only)."""
    admin_service = AdminService(db, current_user)
    user = await admin_service.update_user(user_id, user_data)
    
    if not user:
        raise NotFoundError("User", user_id)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Delete user (Admin only)."""
    admin_service = AdminService(db, current_user)
    deleted = await admin_service.delete_user(user_id)
    
    if not deleted:
        raise NotFoundError("User", user_id)

