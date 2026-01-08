"""Subject schemas."""

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class SubjectBase(BaseModel):
    """Base subject schema."""
    nombre: str = Field(..., min_length=1, max_length=200)
    codigo_institucional: str = Field(..., min_length=1, max_length=50)
    numero_creditos: int = Field(..., gt=0, le=10)
    horario: Optional[str] = None
    descripcion: Optional[str] = None


class SubjectCreate(SubjectBase):
    """Schema for creating a subject."""
    profesor_id: int


class SubjectUpdate(BaseModel):
    """Schema for updating a subject."""
    nombre: Optional[str] = Field(None, min_length=1, max_length=200)
    codigo_institucional: Optional[str] = Field(None, min_length=1, max_length=50)
    numero_creditos: Optional[int] = Field(None, gt=0, le=10)
    horario: Optional[str] = None
    descripcion: Optional[str] = None
    profesor_id: Optional[int] = None


# Schema anidado simplificado para el profesor
class ProfesorInfo(BaseModel):
    """Información básica del profesor."""
    id: int
    nombre: str
    apellido: str
    codigo_institucional: str
    email: str
    
    model_config = ConfigDict(from_attributes=True)


class SubjectResponse(SubjectBase):
    """Schema for subject response."""
    id: int
    profesor_id: int
    
    # Nested model
    profesor: Optional[ProfesorInfo] = None
    
    model_config = ConfigDict(from_attributes=True)


