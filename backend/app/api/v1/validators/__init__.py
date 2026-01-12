"""Validators for API endpoints."""

from app.api.v1.validators.grade_validator import GradeValidator
from app.api.v1.validators.permission_validator import PermissionValidator

__all__ = [
    "GradeValidator",
    "PermissionValidator",
]

