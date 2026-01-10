"""Grade schemas."""

from pydantic import BaseModel, Field, ConfigDict
from datetime import date
from typing import Optional
from decimal import Decimal


class GradeBase(BaseModel):
    """Base grade schema."""
    nota: Decimal = Field(..., ge=0, le=5, description="Nota entre 0 y 5")
    periodo: str = Field(..., min_length=1, max_length=20)
    fecha: date
    observaciones: Optional[str] = None


class GradeCreate(GradeBase):
    """Schema for creating a grade."""
    enrollment_id: int


class GradeUpdate(BaseModel):
    """Schema for updating a grade."""
    nota: Optional[Decimal] = Field(None, ge=0, le=5, description="Nota entre 0 y 5")
    periodo: Optional[str] = Field(None, min_length=1, max_length=20)
    fecha: Optional[date] = None
    observaciones: Optional[str] = None


# Schemas anidados para relaciones
class EstudianteBasicInfo(BaseModel):
    """Info básica del estudiante."""
    id: int
    nombre: str
    apellido: str
    email: str
    model_config = ConfigDict(from_attributes=True)


class SubjectBasicInfo(BaseModel):
    """Info básica de la materia."""
    id: int
    nombre: str
    codigo_institucional: str
    model_config = ConfigDict(from_attributes=True)


class EnrollmentInfo(BaseModel):
    """Información de la inscripción con relaciones anidadas."""
    id: int
    estudiante_id: int
    subject_id: int
    estudiante: Optional[EstudianteBasicInfo] = None
    subject: Optional[SubjectBasicInfo] = None
    model_config = ConfigDict(from_attributes=True)


class GradeResponse(GradeBase):
    """Schema for grade response."""
    id: int
    enrollment_id: int
    
    # Nested model
    enrollment: Optional[EnrollmentInfo] = None
    
    model_config = ConfigDict(from_attributes=True)


