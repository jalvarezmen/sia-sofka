"""Subject serializer for API responses."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.subject import Subject
from app.schemas.subject import SubjectResponse, ProfesorInfo


class SubjectSerializer:
    """Serializer for Subject entities with profesor relationship."""

    @staticmethod
    def serialize_batch(subjects: List[Subject]) -> List[SubjectResponse]:
        """Serialize a batch of subjects with profesor relationship.
        
        Args:
            subjects: List of Subject entities to serialize
            
        Returns:
            List of SubjectResponse objects
        """
        serialized_subjects = []
        for subject in subjects:
            subject_dict = {
                "id": subject.id,
                "nombre": subject.nombre,
                "codigo_institucional": subject.codigo_institucional,
                "numero_creditos": subject.numero_creditos,
                "horario": subject.horario,
                "descripcion": subject.descripcion,
                "profesor_id": subject.profesor_id,
                "profesor": None,
            }

            # Include profesor if loaded
            if subject.profesor:
                subject_dict["profesor"] = ProfesorInfo(
                    id=subject.profesor.id,
                    nombre=subject.profesor.nombre,
                    apellido=subject.profesor.apellido,
                    codigo_institucional=subject.profesor.codigo_institucional,
                    email=subject.profesor.email,
                )

            serialized_subjects.append(SubjectResponse(**subject_dict))

        return serialized_subjects

