"""Grade model."""

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Grade(Base):
    """Grade (Nota) model."""
    
    __tablename__ = "grades"
    
    id = Column(Integer, primary_key=True, index=True)
    enrollment_id = Column(Integer, ForeignKey("enrollments.id"), nullable=False)
    nota = Column(Numeric(3, 2), nullable=False)  # Format: 0.00 to 5.00
    periodo = Column(String, nullable=False)  # e.g., "2024-1", "2024-2"
    fecha = Column(Date, nullable=False)
    observaciones = Column(Text, nullable=True)
    
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
    
    # Relationships
    enrollment = relationship(
        "Enrollment",
        back_populates="grades",
        foreign_keys=[enrollment_id]
    )

