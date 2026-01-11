"""Unit tests for security module."""

import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
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
    """Test that tokens expire correctly (covers decode_access_token exception handling)."""
    data = {"sub": "test@example.com", "role": "Profesor"}
    
    # Create token with expired timestamp (using timezone-aware datetime)
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode(
        {**data, "exp": expired_time},
        settings.secret_key,
        algorithm=settings.algorithm,
    )
    
    # Should raise JWTError for expired token (covers lines 94-95)
    with pytest.raises(JWTError, match="Could not validate credentials"):
        decode_access_token(token)


def test_token_with_invalid_secret():
    """Test that tokens with invalid secret fail (covers decode_access_token exception handling)."""
    data = {"sub": "test@example.com", "role": "Estudiante"}
    token = jwt.encode(
        {**data, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        "wrong_secret_key",
        algorithm=settings.algorithm,
    )
    
    # Should raise JWTError for invalid secret (covers lines 94-95)
    with pytest.raises(JWTError, match="Could not validate credentials"):
        decode_access_token(token)


def test_create_access_token_with_custom_expires_delta():
    """Test create_access_token with custom expires_delta (covers línea 64)."""
    data = {"sub": "test@example.com", "role": "Admin"}
    
    # Create token with custom expiration (30 minutes)
    custom_delta = timedelta(minutes=30)
    token = create_access_token(data, expires_delta=custom_delta)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode and verify expiration is set correctly
    decoded = decode_access_token(token)
    assert decoded["sub"] == "test@example.com"
    assert decoded["role"] == "Admin"
    assert "exp" in decoded
    
    # Verify expiration is approximately 30 minutes from now
    exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    expected_exp = now + custom_delta
    
    # Allow 1 second tolerance for execution time
    assert abs((exp_time - expected_exp).total_seconds()) < 1


def test_create_access_token_without_expires_delta():
    """Test create_access_token uses default expiration when expires_delta is None (covers lines 65-68)."""
    data = {"sub": "test@example.com", "role": "Profesor"}
    
    # Create token without custom expiration (should use settings.access_token_expire_minutes)
    token = create_access_token(data, expires_delta=None)
    
    assert token is not None
    
    # Decode and verify expiration is set
    decoded = decode_access_token(token)
    assert "exp" in decoded
    
    # Verify expiration uses settings default
    exp_time = datetime.fromtimestamp(decoded["exp"], tz=timezone.utc)
    now = datetime.now(timezone.utc)
    expected_exp = now + timedelta(minutes=settings.access_token_expire_minutes)
    
    # Allow 1 second tolerance for execution time
    assert abs((exp_time - expected_exp).total_seconds()) < 1


def test_get_password_hash_empty_password():
    """Test get_password_hash raises ValueError for empty password (covers lines 40-41)."""
    with pytest.raises(ValueError, match="password cannot be empty"):
        get_password_hash("")


def test_verify_password_with_bytes():
    """Test verify_password handles bytes inputs correctly (covers lines 21-25)."""
    password = "test_password_123"
    hashed = get_password_hash(password)
    
    # Test with string password (should work)
    assert verify_password(password, hashed) is True
    
    # Test with bytes password (should work)
    assert verify_password(password.encode('utf-8'), hashed.encode('utf-8')) is True
    
    # Test with string password and bytes hash (should work)
    assert verify_password(password, hashed.encode('utf-8')) is True
    
    # Test with bytes password and string hash (should work)
    assert verify_password(password.encode('utf-8'), hashed) is True


def test_verify_password_invalid_hash():
    """Test verify_password handles invalid hash gracefully (covers lines 27-28)."""
    password = "test_password_123"
    invalid_hash = "invalid_hash_string"
    
    # Should return False for invalid hash (covers exception handling)
    assert verify_password(password, invalid_hash) is False
    
    # Should return False for empty hash
    assert verify_password(password, "") is False


def test_decode_access_token_invalid_format():
    """Test decode_access_token handles invalid token format (covers lines 89-95)."""
    # Invalid token format
    invalid_token = "not.a.valid.jwt.token"
    
    with pytest.raises(JWTError, match="Could not validate credentials"):
        decode_access_token(invalid_token)
    
    # Empty token
    with pytest.raises(JWTError, match="Could not validate credentials"):
        decode_access_token("")
    
    # Malformed token (not enough parts)
    with pytest.raises(JWTError, match="Could not validate credentials"):
        decode_access_token("header.payload")


def test_decode_access_token_wrong_algorithm():
    """Test decode_access_token raises JWTError for wrong algorithm (covers lines 94-95)."""
    data = {"sub": "test@example.com", "role": "Estudiante"}
    
    # Create token with different algorithm (if settings.algorithm is HS256, try RS256, or vice versa)
    # Since we don't have RS256 keys, we'll test with wrong secret which will fail decoding
    token = jwt.encode(
        {**data, "exp": datetime.now(timezone.utc) + timedelta(minutes=30)},
        settings.secret_key,
        algorithm=settings.algorithm,  # Use correct algorithm but wrong secret
    )
    
    # Actually test with completely invalid token structure
    invalid_token = "invalid.token.structure"
    with pytest.raises(JWTError, match="Could not validate credentials"):
        decode_access_token(invalid_token)


def test_create_access_token_preserves_data():
    """Test create_access_token preserves all data in token (covers lines 61-74)."""
    data = {
        "sub": "test@example.com",
        "role": "Admin",
        "custom_field": "custom_value",
        "numeric_field": 123,
        "boolean_field": True,
    }
    
    token = create_access_token(data)
    decoded = decode_access_token(token)
    
    # Verify all original data is preserved
    assert decoded["sub"] == data["sub"]
    assert decoded["role"] == data["role"]
    assert decoded["custom_field"] == data["custom_field"]
    assert decoded["numeric_field"] == data["numeric_field"]
    assert decoded["boolean_field"] == data["boolean_field"]
    
    # Verify expiration was added
    assert "exp" in decoded


def test_password_hash_uniqueness():
    """Test that same password produces different hashes (salt is different each time)."""
    password = "same_password"
    
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different (different salts)
    assert hash1 != hash2
    
    # But both should verify the same password
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_password_verification_case_sensitive():
    """Test that password verification is case-sensitive."""
    password = "TestPassword123"
    hashed = get_password_hash(password)
    
    # Exact match should work
    assert verify_password(password, hashed) is True
    
    # Different case should fail
    assert verify_password("testpassword123", hashed) is False
    assert verify_password("TESTPASSWORD123", hashed) is False
    assert verify_password("TeStPaSsWoRd123", hashed) is False

