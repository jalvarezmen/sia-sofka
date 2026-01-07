"""Profesor service with profesor-specific business logic."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.models.subject import Subject
from app.services.subject_service import SubjectService
from app.services.grade_service import GradeService
from app.services.user_service import UserService
from app.repositories.enrollment_repository import EnrollmentRepository
from app.repositories.subject_repository import SubjectRepository
from app.schemas.grade import GradeCreate
from app.schemas.user import UserUpdate


class ProfesorService:
    """Service for profesor-specific business logic."""
    
    def __init__(self, db: AsyncSession, profesor_user: User):
        """Initialize profesor service.
        
        Args:
            db: Database session
            profesor_user: Profesor user instance
        """
        self.db = db
        self.profesor_user = profesor_user
        self.subject_service = SubjectService(db)
        self.grade_service = GradeService(db)
        self.user_service = UserService(db)
        self.enrollment_repo = EnrollmentRepository(db)
        self.subject_repo = SubjectRepository(db)
    
    async def get_assigned_subjects(self) -> list[Subject]:
        """Get all subjects assigned to this profesor.
        
        Returns:
            List of assigned subjects
        """
        return await self.subject_repo.get_by_profesor(self.profesor_user.id)
    
    async def get_students_by_subject(self, subject_id: int) -> list[User]:
        """Get all students enrolled in a subject assigned to this profesor.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            List of estudiantes
        
        Raises:
            ValueError: If subject is not assigned to this profesor
        """
        # Verify subject is assigned to this profesor
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        # Get enrollments for this subject
        enrollments = await self.enrollment_repo.get_by_subject(subject_id)
        
        # Get estudiantes
        estudiantes = []
        for enrollment in enrollments:
            estudiante = await self.user_service.get_user_by_id(enrollment.estudiante_id)
            if estudiante:
                estudiantes.append(estudiante)
        
        return estudiantes
    
    async def create_grade(
        self, grade_data: GradeCreate, subject_id: int
    ) -> Grade:
        """Create a grade for a student in an assigned subject.
        
        Args:
            grade_data: Grade creation data
            subject_id: Subject ID (must be assigned to this profesor)
        
        Returns:
            Created grade
        
        Raises:
            ValueError: If subject is not assigned to this profesor or enrollment invalid
        """
        # Verify subject is assigned to this profesor
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        # Verify enrollment exists and is for this subject
        enrollment = await self.enrollment_repo.get_by_id(grade_data.enrollment_id)
        if not enrollment or enrollment.subject_id != subject_id:
            raise ValueError("Invalid enrollment for this subject")
        
        # Create grade
        return await self.grade_service.create_grade(grade_data)
    
    async def get_subject_with_students(self, subject_id: int) -> dict:
        """Get subject with list of enrolled students.
        
        Args:
            subject_id: Subject ID
        
        Returns:
            Dictionary with subject and students
        
        Raises:
            ValueError: If subject is not assigned to this profesor
        """
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        students = await self.get_students_by_subject(subject_id)
        
        return {
            "subject": subject,
            "students": students,
        }
    
    async def generate_subject_report(
        self, subject_id: int, format: str = "pdf"
    ) -> dict:
        """Generate report of grades for a subject (placeholder for Factory Method).
        
        Args:
            subject_id: Subject ID
            format: Report format (pdf, html, json)
        
        Returns:
            Report data (will be implemented with Factory Method)
        """
        # Verify subject is assigned
        subject = await self.subject_repo.get_by_id(subject_id)
        if not subject or subject.profesor_id != self.profesor_user.id:
            raise ValueError("Subject is not assigned to this profesor")
        
        # Get enrollments and grades
        enrollments = await self.enrollment_repo.get_by_subject(subject_id)
        
        report_data = {
            "subject": {
                "id": subject.id,
                "nombre": subject.nombre,
                "codigo_institucional": subject.codigo_institucional,
            },
            "students": [],
            "format": format,
        }
        
        for enrollment in enrollments:
            estudiante = await self.user_service.get_user_by_id(enrollment.estudiante_id)
            if not estudiante:
                continue
            
            grades = await self.grade_service.get_grades_by_enrollment(enrollment.id)
            try:
                average = await self.grade_service.calculate_average(enrollment.id)
            except ValueError:
                average = None
            
            report_data["students"].append({
                "estudiante": {
                    "id": estudiante.id,
                    "nombre": estudiante.nombre,
                    "apellido": estudiante.apellido,
                    "codigo_institucional": estudiante.codigo_institucional,
                },
                "grades": [{"nota": float(g.nota), "periodo": g.periodo} for g in grades],
                "average": float(average) if average else None,
            })
        
        return report_data
    
    async def update_profile(self, user_data: UserUpdate) -> User:
        """Update profesor's own profile.
        
        Args:
            user_data: User update data
        
        Returns:
            Updated profesor
        """
        return await self.user_service.update_user(self.profesor_user.id, user_data)

