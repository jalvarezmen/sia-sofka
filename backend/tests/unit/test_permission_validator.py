"""Unit tests for PermissionValidator."""

import pytest
from app.models.user import User, UserRole
from app.api.v1.validators.permission_validator import PermissionValidator
from app.core.exceptions import ForbiddenError


def test_require_roles_success():
    """Test successful role verification."""
    user = User(
        id=1,
        email="admin@test.com",
        role=UserRole.ADMIN,
    )
    
    # Should not raise any exception
    PermissionValidator.require_roles(user, [UserRole.ADMIN])


def test_require_roles_multiple_allowed():
    """Test role verification with multiple allowed roles."""
    user = User(
        id=1,
        email="profesor@test.com",
        role=UserRole.PROFESOR,
    )
    
    # Should not raise any exception
    PermissionValidator.require_roles(user, [UserRole.ADMIN, UserRole.PROFESOR])


def test_require_roles_failure():
    """Test role verification fails when user role not in allowed roles."""
    user = User(
        id=1,
        email="estudiante@test.com",
        role=UserRole.ESTUDIANTE,
    )
    
    with pytest.raises(ForbiddenError) as exc_info:
        PermissionValidator.require_roles(user, [UserRole.ADMIN, UserRole.PROFESOR])
    
    assert "Not enough permissions" in str(exc_info.value)


def test_require_roles_empty_allowed_list():
    """Test role verification fails when allowed roles list is empty."""
    user = User(
        id=1,
        email="admin@test.com",
        role=UserRole.ADMIN,
    )
    
    with pytest.raises(ForbiddenError):
        PermissionValidator.require_roles(user, [])


def test_require_roles_single_allowed():
    """Test role verification with single allowed role."""
    user = User(
        id=1,
        email="estudiante@test.com",
        role=UserRole.ESTUDIANTE,
    )
    
    # Should not raise any exception
    PermissionValidator.require_roles(user, [UserRole.ESTUDIANTE])


def test_require_roles_all_roles_allowed():
    """Test role verification when all roles are allowed."""
    user = User(
        id=1,
        email="profesor@test.com",
        role=UserRole.PROFESOR,
    )
    
    # Should not raise any exception
    PermissionValidator.require_roles(
        user, [UserRole.ADMIN, UserRole.PROFESOR, UserRole.ESTUDIANTE]
    )

