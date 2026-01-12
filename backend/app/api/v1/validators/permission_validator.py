"""Permission validators for role-based access control."""

from typing import List
from app.models.user import User, UserRole
from app.core.exceptions import ForbiddenError


class PermissionValidator:
    """Validator for permission checks."""

    @staticmethod
    def require_roles(user: User, allowed_roles: List[UserRole]) -> None:
        """Verify that user has one of the allowed roles.
        
        Args:
            user: User to check
            allowed_roles: List of allowed roles
            
        Raises:
            ForbiddenError: If user role is not in allowed roles
        """
        if user.role not in allowed_roles:
            raise ForbiddenError("Not enough permissions")

