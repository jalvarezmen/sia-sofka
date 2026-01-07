"""Grade repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.grade import Grade
from app.repositories.base import AbstractRepository


class GradeRepository(AbstractRepository[Grade]):
    """Repository for Grade model."""
    
    def __init__(self, db: AsyncSession):
        """Initialize grade repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, Grade)
    
    async def get_by_enrollment(
        self, enrollment_id: int, skip: int = 0, limit: int = 100
    ) -> list[Grade]:
        """Get grades by enrollment.
        
        Args:
            enrollment_id: Enrollment ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of grades
        """
        stmt = (
            select(Grade)
            .where(Grade.enrollment_id == enrollment_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_average_by_enrollment(self, enrollment_id: int) -> Optional[float]:
        """Get average grade for an enrollment.
        
        Args:
            enrollment_id: Enrollment ID
        
        Returns:
            Average grade or None if no grades exist
        """
        stmt = select(func.avg(Grade.nota)).where(
            Grade.enrollment_id == enrollment_id
        )
        result = await self.db.execute(stmt)
        avg = result.scalar()
        return float(avg) if avg is not None else None


