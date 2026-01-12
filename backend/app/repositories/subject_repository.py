"""Subject repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.subject import Subject
from app.repositories.base import AbstractRepository


class SubjectRepository(AbstractRepository[Subject]):
    """Repository for Subject model."""
    
    def __init__(self, db: AsyncSession):
        """Initialize subject repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, Subject)
    
    async def get_by_codigo_institucional(
        self, codigo: str
    ) -> Optional[Subject]:
        """Get subject by institutional code.
        
        Args:
            codigo: Institutional code
        
        Returns:
            Subject instance or None
        """
        stmt = select(Subject).where(Subject.codigo_institucional == codigo)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_profesor(
        self, profesor_id: int, skip: int = 0, limit: int = 100
    ) -> list[Subject]:
        """Get subjects by profesor.
        
        Args:
            profesor_id: Profesor user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of subjects
        """
        stmt = (
            select(Subject)
            .where(Subject.profesor_id == profesor_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())


