"""Enrollment schemas."""

from pydantic import BaseModel


class EnrollmentBase(BaseModel):
    """Base enrollment schema."""
    estudiante_id: int
    subject_id: int


class EnrollmentCreate(EnrollmentBase):
    """Schema for creating an enrollment."""
    pass


class EnrollmentResponse(EnrollmentBase):
    """Schema for enrollment response."""
    id: int
    
    class Config:
        from_attributes = True


