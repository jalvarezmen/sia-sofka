"""Grade serializer for API responses."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.grade import Grade
from app.models.user import User
from app.models.subject import Subject
from app.schemas.grade import (
    GradeResponse,
    EnrollmentInfo,
    EstudianteBasicInfo,
    SubjectBasicInfo,
)


class GradeSerializer:
    """Serializer for Grade entities with efficient batch loading."""

    @staticmethod
    async def serialize_batch(
        grades: List[Grade], db: AsyncSession
    ) -> List[GradeResponse]:
        """Serialize a batch of grades with efficient batch loading of relationships.
        
        This method loads all estudiante and subject relationships in batches
        to avoid N+1 queries.
        
        Args:
            grades: List of Grade entities to serialize
            db: Database session
            
        Returns:
            List of GradeResponse objects
        """
        if not grades:
            return []

        # Collect all unique estudiante_ids and subject_ids
        unique_estudiante_ids = set()
        unique_subject_ids = set()

        for grade in grades:
            if grade.enrollment:
                unique_estudiante_ids.add(grade.enrollment.estudiante_id)
                unique_subject_ids.add(grade.enrollment.subject_id)

        # Batch load all estudiantes
        estudiantes_map = {}
        if unique_estudiante_ids:
            estudiantes_stmt = select(User).where(User.id.in_(list(unique_estudiante_ids)))
            estudiantes_result = await db.execute(estudiantes_stmt)
            estudiantes_list = estudiantes_result.scalars().all()
            estudiantes_map = {est.id: est for est in estudiantes_list}

        # Batch load all subjects
        subjects_map = {}
        if unique_subject_ids:
            subjects_stmt = select(Subject).where(Subject.id.in_(list(unique_subject_ids)))
            subjects_result = await db.execute(subjects_stmt)
            subjects_list = subjects_result.scalars().all()
            subjects_map = {subj.id: subj for subj in subjects_list}

        # Serialize each grade using batch-loaded maps
        responses = []
        for grade in grades:
            response_data = {
                "id": grade.id,
                "enrollment_id": grade.enrollment_id,
                "nota": grade.nota,
                "periodo": grade.periodo,
                "fecha": grade.fecha,
                "observaciones": grade.observaciones,
            }

            enrollment_info = None
            if grade.enrollment:
                # Get estudiante from batch-loaded map
                estudiante_info = None
                if grade.enrollment.estudiante_id in estudiantes_map:
                    estudiante = estudiantes_map[grade.enrollment.estudiante_id]
                    estudiante_info = EstudianteBasicInfo(
                        id=estudiante.id,
                        nombre=estudiante.nombre,
                        apellido=estudiante.apellido,
                        email=estudiante.email,
                    )

                # Get subject from batch-loaded map
                subject_info = None
                if grade.enrollment.subject_id in subjects_map:
                    subject = subjects_map[grade.enrollment.subject_id]
                    subject_info = SubjectBasicInfo(
                        id=subject.id,
                        nombre=subject.nombre,
                        codigo_institucional=subject.codigo_institucional,
                    )

                enrollment_info = EnrollmentInfo(
                    id=grade.enrollment.id,
                    estudiante_id=grade.enrollment.estudiante_id,
                    subject_id=grade.enrollment.subject_id,
                    estudiante=estudiante_info,
                    subject=subject_info,
                )

            responses.append(GradeResponse(**response_data, enrollment=enrollment_info))

        return responses

