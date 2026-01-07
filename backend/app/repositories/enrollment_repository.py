"""Enrollment repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.enrollment import Enrollment
from app.repositories.base import AbstractRepository


class EnrollmentRepository(AbstractRepository[Enrollment]):
    """Repository for Enrollment model."""
    
    def __init__(self, db: AsyncSession):
        """Initialize enrollment repository.
        
        Args:
            db: Database session
        """
        super().__init__(db, Enrollment)
    
    async def get_by_estudiante(
        self, estudiante_id: int, skip: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        """Get enrollments by estudiante.
        
        Args:
            estudiante_id: Estudiante user ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments
        """
        stmt = (
            select(Enrollment)
            .where(Enrollment.estudiante_id == estudiante_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_subject(
        self, subject_id: int, skip: int = 0, limit: int = 100
    ) -> list[Enrollment]:
        """Get enrollments by subject.
        
        Args:
            subject_id: Subject ID
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            List of enrollments
        """
        stmt = (
            select(Enrollment)
            .where(Enrollment.subject_id == subject_id)
            .offset(skip)
            .limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_by_estudiante_and_subject(
        self, estudiante_id: int, subject_id: int
    ) -> Optional[Enrollment]:
        """Get enrollment by estudiante and subject.
        
        Args:
            estudiante_id: Estudiante user ID
            subject_id: Subject ID
        
        Returns:
            Enrollment instance or None
        """
        stmt = select(Enrollment).where(
            Enrollment.estudiante_id == estudiante_id,
            Enrollment.subject_id == subject_id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

