"""User repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.repositories.base import AbstractRepository


class UserRepository(AbstractRepository[User]):
    """Repository for User model."""
    
    def __init__(self, db: AsyncSession):
        """Initialize user repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, User)
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.
        
        Args:
            email: User email
        
        Returns:
            User instance or None
        """
        stmt = select(User).where(User.email == email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_codigo_institucional(
        self, codigo: str
    ) -> Optional[User]:
        """Get user by institutional code.
        
        Args:
            codigo: Institutional code
        
        Returns:
            User instance or None
        """
        stmt = select(User).where(User.codigo_institucional == codigo)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_role(self, role: str, skip: int = 0, limit: int = 100) -> list[User]:
        """Get users by role.
        
        Args:
            role: User role
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of users
        """
        stmt = (
            select(User)
            .where(User.role == role)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

