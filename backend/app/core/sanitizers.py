"""Input sanitization utilities (conservative approach)."""

import re
from typing import Any


def sanitize_string(value: str, max_length: int = 255, allow_empty: bool = False) -> str:
    """
    Sanitize string input conservatively.
    
    Only removes control characters, doesn't modify valid content.
    This is a conservative approach to avoid breaking existing data.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        allow_empty: Whether empty strings are allowed
    
    Returns:
        Sanitized string
    
    Raises:
        ValueError: If value is invalid
    """
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    
    # Only remove control characters (0x00-0x1F, 0x7F-0x9F)
    # This preserves all printable characters including Unicode
    sanitized = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', value)
    
    # Trim whitespace
    sanitized = sanitized.strip()
    
    # Validate length
    if not allow_empty and len(sanitized) == 0:
        raise ValueError("String cannot be empty")
    
    if len(sanitized) > max_length:
        raise ValueError(f"String exceeds maximum length of {max_length}")
    
    return sanitized


def validate_email(email: str) -> str:
    """
    Validate and normalize email address.
    
    Args:
        email: Email address to validate
    
    Returns:
        Normalized email (lowercase, trimmed)
    
    Raises:
        ValueError: If email format is invalid
    """
    if not isinstance(email, str):
        raise ValueError("Email must be a string")
    
    # Basic email validation pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    email = email.strip().lower()
    
    if not re.match(pattern, email):
        raise ValueError("Invalid email format")
    
    return email


def sanitize_code(value: str, max_length: int = 50) -> str:
    """
    Sanitize institutional codes.
    
    Codes should only contain alphanumeric characters, hyphens, and underscores.
    
    Args:
        value: Code to sanitize
        max_length: Maximum allowed length
    
    Returns:
        Sanitized code
    
    Raises:
        ValueError: If code is invalid
    """
    if not isinstance(value, str):
        raise ValueError("Code must be a string")
    
    # Remove all characters except alphanumeric, hyphens, and underscores
    sanitized = re.sub(r'[^a-zA-Z0-9_-]', '', value)
    
    if len(sanitized) == 0:
        raise ValueError("Code cannot be empty")
    
    if len(sanitized) > max_length:
        raise ValueError(f"Code exceeds maximum length of {max_length}")
    
    return sanitized


__all__ = ["sanitize_string", "validate_email", "sanitize_code"]

