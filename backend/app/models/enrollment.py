"""Enrollment model."""

from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Enrollment(Base):
    """Enrollment model (Estudiante-Subject relationship)."""
    
    __tablename__ = "enrollments"
    
    id = Column(Integer, primary_key=True, index=True)
    estudiante_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    
    # Timestamps
    created_at = Column(
        DateTime,
        server_default=func.now(),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Unique constraint: a student can only be enrolled once per subject
    __table_args__ = (
        UniqueConstraint("estudiante_id", "subject_id", name="uq_enrollment"),
    )
    
    # Relationships
    estudiante = relationship(
        "User",
        back_populates="enrollments",
        foreign_keys=[estudiante_id]
    )
    subject = relationship(
        "Subject",
        back_populates="enrollments",
        foreign_keys=[subject_id]
    )
    grades = relationship(
        "Grade",
        back_populates="enrollment",
        cascade="all, delete-orphan"
    )

