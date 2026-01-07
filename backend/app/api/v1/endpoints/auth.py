"""Authentication endpoints."""

from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.config import settings
from app.models.user import User, UserRole
from app.schemas.token import Token
from app.schemas.user import UserCreate, UserResponse
from app.api.v1.dependencies import (
    get_current_active_user,
    require_admin,
)
from app.utils.codigo_generator import generar_codigo_institucional
from datetime import date

router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """Login endpoint.
    
    Args:
        form_data: OAuth2 password request form (username=email, password)
        db: Database session
    
    Returns:
        Access token
    
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email (username in OAuth2 form)
    stmt = select(User).where(User.email == form_data.username)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.email, "role": user.role.value},
        expires_delta=access_token_expires,
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Register a new user (Admin only).
    
    Args:
        user_data: User creation data
        db: Database session
        current_user: Current admin user (from dependency)
    
    Returns:
        Created user
    
    Raises:
        HTTPException: If email already exists
    """
    # Check if user already exists
    stmt = select(User).where(User.email == user_data.email)
    result = await db.execute(stmt)
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    
    # Generate institutional code
    codigo = await generar_codigo_institucional(db, user_data.role.value)
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        role=user_data.role,
        nombre=user_data.nombre,
        apellido=user_data.apellido,
        codigo_institucional=codigo,
        fecha_nacimiento=user_data.fecha_nacimiento,
        numero_contacto=user_data.numero_contacto,
        programa_academico=user_data.programa_academico,
        ciudad_residencia=user_data.ciudad_residencia,
        area_ensenanza=user_data.area_ensenanza,
    )
    
    # Calculate age
    user.edad = user.calcular_edad()
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.get("/me", response_model=UserResponse)
async def read_users_me(
    current_user: User = Depends(get_current_active_user),
):
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
    
    Returns:
        Current user data
    """
    return current_user


