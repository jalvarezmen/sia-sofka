"""Subject service with business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.subject_repository import SubjectRepository
from app.repositories.user_repository import UserRepository
from app.schemas.subject import SubjectCreate, SubjectUpdate
from app.models.subject import Subject
from app.models.user import UserRole


class SubjectService:
    """Service for subject business logic."""
    
    def __init__(self, db: AsyncSession):
        """Initialize subject service.
        
        Args:
            db: Database session
        """
        self.repository = SubjectRepository(db)
        self.user_repository = UserRepository(db)
        self.db = db
    
    def _validate_credits(self, credits: int) -> None:
        """Validate number of credits.
        
        Args:
            credits: Number of credits to validate
        
        Raises:
            ValueError: If credits are invalid
        """
        if credits <= 0 or credits > 10:
            raise ValueError("Number of credits must be between 1 and 10")
    
    async def _validate_profesor(self, profesor_id: int) -> None:
        """Validate that profesor exists and is a Profesor.
        
        Args:
            profesor_id: Profesor user ID
        
        Raises:
            ValueError: If profesor not found or invalid
        """
        profesor = await self.user_repository.get_by_id(profesor_id)
        if not profesor:
            raise ValueError("Profesor not found")
        if profesor.role != UserRole.PROFESOR:
            raise ValueError("User is not a Profesor")
    
    async def create_subject(self, subject_data: SubjectCreate) -> Subject:
        """Create a new subject with business logic.
        
        Args:
            subject_data: Subject creation data
        
        Returns:
            Created subject
        
        Raises:
            ValueError: If invalid data or profesor not found
        """
        # Validate credits
        self._validate_credits(subject_data.numero_creditos)
        
        # Validate profesor
        await self._validate_profesor(subject_data.profesor_id)
        
        # Generate codigo_institucional if not provided
        from app.utils.codigo_generator import generar_codigo_materia
        codigo_institucional = subject_data.codigo_institucional
        if not codigo_institucional:
            codigo_institucional = await generar_codigo_materia(self.db, subject_data.nombre)
        else:
            # Check if provided codigo_institucional already exists
            existing = await self.repository.get_by_codigo_institucional(codigo_institucional)
            if existing:
                raise ValueError("Subject code already exists")
        
        # Create subject
        subject_dict = subject_data.model_dump(exclude={'codigo_institucional'})
        subject_dict['codigo_institucional'] = codigo_institucional
        return await self.repository.create(subject_dict)
    
    async def get_subject_by_id(self, subject_id: int) -> Subject | None:
        """Get subject by ID.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            Subject or None
        """
        return await self.repository.get_by_id(subject_id)
    
    async def update_subject(
        self, subject_id: int, subject_data: SubjectUpdate
    ) -> Subject | None:
        """Update subject with business logic.
        
        Args:
            subject_id: Subject ID
            subject_data: Subject update data
        
        Returns:
            Updated subject or None
        
        Raises:
            ValueError: If invalid data
        """
        # Validate credits if provided
        if subject_data.numero_creditos is not None:
            self._validate_credits(subject_data.numero_creditos)
        
        # Validate profesor if provided
        if subject_data.profesor_id is not None:
            await self._validate_profesor(subject_data.profesor_id)
        
        update_dict = subject_data.model_dump(exclude_unset=True)
        return await self.repository.update(subject_id, update_dict)
    
    async def delete_subject(self, subject_id: int) -> bool:
        """Delete subject.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            True if deleted, False if not found
        """
        return await self.repository.delete(subject_id)
    
    async def get_subjects_by_profesor(
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
        return await self.repository.get_by_profesor(profesor_id, skip, limit)


