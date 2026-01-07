"""Unit tests for security module."""

import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_access_token,
)
from app.core.config import settings


def test_password_hashing():
    """Test password hashing and verification."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    
    # Should verify correctly
    assert verify_password(password, hashed) is True
    
    # Should fail with wrong password
    assert verify_password("wrong_password", hashed) is False


def test_create_access_token():
    """Test JWT token creation."""
    data = {"sub": "test@example.com", "role": "Estudiante"}
    token = create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "Estudiante"
    assert "exp" in decoded


def test_decode_access_token():
    """Test JWT token decoding."""
    data = {"sub": "test@example.com", "role": "Admin"}
    token = create_access_token(data)
    
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "Admin"


def test_token_expiration():
    """Test that tokens expire correctly."""
    data = {"sub": "test@example.com", "role": "Profesor"}
    
    # Create token with expired timestamp
    expired_time = datetime.utcnow() - timedelta(minutes=1)
    token = jwt.encode(
        {**data, "exp": expired_time},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    # Should raise exception for expired token
    with pytest.raises(Exception):
        decode_access_token(token)


def test_token_with_invalid_secret():
    """Test that tokens with invalid secret fail."""
    data = {"sub": "test@example.com", "role": "Estudiante"}
    token = jwt.encode(
        {**data, "exp": datetime.utcnow() + timedelta(minutes=30)},
        "wrong_secret_key",
        algorithm=settings.algorithm,
    )
    
    with pytest.raises(Exception):
        decode_access_token(token)

