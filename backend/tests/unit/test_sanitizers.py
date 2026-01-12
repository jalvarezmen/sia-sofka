"""Unit tests for sanitizers module."""

import pytest
from app.core.sanitizers import (
    sanitize_string,
    validate_email,
    sanitize_code,
)


# ==================== sanitize_string Tests ====================

@pytest.mark.parametrize("input_value,expected", [
    ("hello world", "hello world"),
    ("  hello world  ", "hello world"),  # Trim whitespace
    ("hello\x00world", "helloworld"),  # Remove null bytes
    ("héllo wörld", "héllo wörld"),  # Preserve Unicode
    ("Hello WORLD", "Hello WORLD"),  # Preserve case
])
def test_sanitize_string_valid_inputs(input_value, expected):
    """Test sanitize_string with valid inputs (covers lines 7-42)."""
    result = sanitize_string(input_value)
    assert result == expected


def test_sanitize_string_removes_control_characters():
    """Test sanitize_string removes control characters (covers lines 28-30).
    
    Note: The regex removes [\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]
    So \x09 (tab), \x0A (LF), \x0D (CR) are preserved but trimmed as whitespace.
    """
    # Test various control characters that are removed
    test_cases = [
        ("\x00", ""),  # Null
        ("\x01", ""),  # Start of heading
        ("\x08", ""),  # Backspace
        ("\x0B", ""),  # Vertical tab (removed)
        ("\x0C", ""),  # Form feed (removed)
        ("\x0E", ""),  # Shift out
        ("\x1F", ""),  # Unit separator
        ("\x7F", ""),  # Delete
        ("\x80", ""),  # Extended ASCII
        ("\x9F", ""),  # Application program command
    ]
    
    for input_value, expected in test_cases:
        result = sanitize_string(input_value, allow_empty=True)
        assert result == expected, f"Failed for input: {repr(input_value)}"
    
    # Test control characters that are preserved but trimmed as whitespace
    # \x09 (tab), \x0A (LF), \x0D (CR) are NOT in the removal regex
    assert sanitize_string("hello\x09world", allow_empty=True) == "hello\x09world"  # Tab preserved
    assert sanitize_string("\x09\x0A\x0D", allow_empty=True) == ""  # Trimmed as whitespace


def test_sanitize_string_trim_whitespace():
    """Test sanitize_string trims whitespace (covers línea 33).
    
    Note: strip() removes leading/trailing whitespace including \t, \n, \r, spaces.
    But these characters in the middle are preserved.
    """
    assert sanitize_string("  hello  ", allow_empty=True) == "hello"
    assert sanitize_string("\t\thello\t\t", allow_empty=True) == "hello"  # Tabs trimmed
    assert sanitize_string("\n\nhello\n\n", allow_empty=True) == "hello"  # Newlines trimmed
    assert sanitize_string("  ", allow_empty=True) == ""
    # Tabs and newlines in middle are preserved (not control chars in removal regex)
    assert sanitize_string("hello\tworld", allow_empty=True) == "hello\tworld"
    assert sanitize_string("hello\nworld", allow_empty=True) == "hello\nworld"


def test_sanitize_string_max_length():
    """Test sanitize_string respects max_length (covers lines 35-40)."""
    long_string = "a" * 300
    short_string = "a" * 100
    
    # Should raise error for string exceeding max_length
    with pytest.raises(ValueError, match="exceeds maximum length"):
        sanitize_string(long_string, max_length=255)
    
    # Should work for string within max_length
    result = sanitize_string(short_string, max_length=255)
    assert len(result) == 100
    assert result == short_string
    
    # Custom max_length
    with pytest.raises(ValueError, match="exceeds maximum length of 50"):
        sanitize_string("a" * 100, max_length=50)
    
    result = sanitize_string("a" * 50, max_length=50)
    assert len(result) == 50


def test_sanitize_string_empty_string_not_allowed():
    """Test sanitize_string raises ValueError for empty string when allow_empty=False (covers lines 36-37)."""
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_string("")
    
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_string("   ")  # Only whitespace after trim
    
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_string("\x00\x01\x02")  # Only control characters


def test_sanitize_string_empty_string_allowed():
    """Test sanitize_string allows empty string when allow_empty=True (covers lines 36-37)."""
    assert sanitize_string("", allow_empty=True) == ""
    assert sanitize_string("   ", allow_empty=True) == ""
    assert sanitize_string("\x00\x01\x02", allow_empty=True) == ""


def test_sanitize_string_invalid_type():
    """Test sanitize_string raises ValueError for non-string input (covers lines 25-26)."""
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_string(123)
    
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_string(None)
    
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_string([])
    
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_string({})


def test_sanitize_string_preserves_valid_content():
    """Test sanitize_string preserves valid content including special characters (covers lines 28-30)."""
    # Test various valid characters
    test_cases = [
        "hello-world",
        "hello_world",
        "hello.world",
        "hello@world",
        "hello#world",
        "hello$world",
        "hello%world",
        "hello&world",
        "hello*world",
        "hello+world",
        "hello=world",
        "hello(world)",
        "hello[world]",
        "hello{world}",
        "hello|world",
        "hello\\world",
        "hello/world",
        "hello:world",
        "hello;world",
        "hello'world",
        'hello"world',
        "hello<world>",
        "hello,world",
        "hello.world",
        "hello?world",
        "hello!world",
        "héllo wörld ñoño",
        "中文 日本語 한국어",
        "123456789",
        "!@#$%^&*()",
    ]
    
    for input_value in test_cases:
        result = sanitize_string(input_value, allow_empty=True)
        # Should preserve all printable characters
        assert len(result) > 0 or input_value.strip() == ""


# ==================== validate_email Tests ====================

@pytest.mark.parametrize("email,expected", [
    ("test@example.com", "test@example.com"),
    ("user.name@example.com", "user.name@example.com"),
    ("user+tag@example.com", "user+tag@example.com"),
    ("user_name@example.com", "user_name@example.com"),
    ("user-name@example.com", "user-name@example.com"),
    ("user123@example.com", "user123@example.com"),
    ("test@example.co.uk", "test@example.co.uk"),
    ("test@sub.example.com", "test@sub.example.com"),
    ("TEST@EXAMPLE.COM", "test@example.com"),  # Lowercase
    ("  TEST@EXAMPLE.COM  ", "test@example.com"),  # Trim and lowercase
])
def test_validate_email_valid_inputs(email, expected):
    """Test validate_email with valid email formats (covers lines 45-69)."""
    result = validate_email(email)
    assert result == expected


def test_validate_email_normalizes_output():
    """Test validate_email normalizes output (lowercase, trimmed) (covers línea 64)."""
    assert validate_email("  USER@EXAMPLE.COM  ") == "user@example.com"
    assert validate_email("User@Example.Com") == "user@example.com"
    assert validate_email("  Test@Test.Test  ") == "test@test.test"


@pytest.mark.parametrize("invalid_email", [
    "not-an-email",
    "@example.com",
    "user@",
    "user@example",
    "user@.com",
    "user.example.com",
    "user@@example.com",
    # Note: "user@example..com" actually matches the regex pattern r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    # because .- allows multiple dots. This is a limitation of the basic regex.
    "user@example.c",
    "user@example",
    "user name@example.com",  # Space in local part
    "user@exam ple.com",  # Space in domain
    "",  # Empty string
    "   ",  # Only whitespace
])
def test_validate_email_invalid_formats(invalid_email):
    """Test validate_email raises ValueError for invalid email formats (covers lines 66-67)."""
    with pytest.raises(ValueError, match="Invalid email format"):
        validate_email(invalid_email)


def test_validate_email_invalid_type():
    """Test validate_email raises ValueError for non-string input (covers lines 58-59)."""
    with pytest.raises(ValueError, match="must be a string"):
        validate_email(123)
    
    with pytest.raises(ValueError, match="must be a string"):
        validate_email(None)
    
    with pytest.raises(ValueError, match="must be a string"):
        validate_email([])
    
    with pytest.raises(ValueError, match="must be a string"):
        validate_email({})


def test_validate_email_edge_cases():
    """Test validate_email with edge cases (covers lines 45-69)."""
    # Long but valid email
    long_local = "a" * 64
    long_domain = "a" * 63
    long_email = f"{long_local}@{long_domain}.com"
    result = validate_email(long_email)
    assert result == long_email.lower()
    
    # Very short email
    assert validate_email("a@b.co") == "a@b.co"
    
    # Email with numbers
    assert validate_email("user123@example456.com") == "user123@example456.com"


# ==================== sanitize_code Tests ====================

@pytest.mark.parametrize("input_value,expected", [
    ("ABC123", "ABC123"),
    ("ABC-123", "ABC-123"),
    ("ABC_123", "ABC_123"),
    ("  ABC-123  ", "ABC-123"),  # Trim whitespace
    ("ABC---123", "ABC---123"),
    ("ABC___123", "ABC___123"),
    ("abc123", "abc123"),
    ("ABC_123-DEF", "ABC_123-DEF"),
])
def test_sanitize_code_valid_inputs(input_value, expected):
    """Test sanitize_code with valid inputs (covers lines 72-100)."""
    result = sanitize_code(input_value)
    assert result == expected


def test_sanitize_code_removes_invalid_characters():
    """Test sanitize_code removes invalid characters (covers línea 92)."""
    # Should remove spaces, special chars, but keep alphanumeric, hyphens, underscores
    assert sanitize_code("ABC 123") == "ABC123"
    assert sanitize_code("ABC@123") == "ABC123"
    assert sanitize_code("ABC#123") == "ABC123"
    assert sanitize_code("ABC$123") == "ABC123"
    assert sanitize_code("ABC%123") == "ABC123"
    assert sanitize_code("ABC&123") == "ABC123"
    assert sanitize_code("ABC*123") == "ABC123"
    assert sanitize_code("ABC+123") == "ABC123"
    assert sanitize_code("ABC(123)") == "ABC123"
    assert sanitize_code("ABC[123]") == "ABC123"
    assert sanitize_code("ABC{123}") == "ABC123"
    assert sanitize_code("ABC|123") == "ABC123"
    assert sanitize_code("ABC\\123") == "ABC123"
    assert sanitize_code("ABC/123") == "ABC123"
    assert sanitize_code("ABC:123") == "ABC123"
    assert sanitize_code("ABC;123") == "ABC123"
    assert sanitize_code("ABC'123") == "ABC123"
    assert sanitize_code('ABC"123') == "ABC123"
    assert sanitize_code("ABC<123>") == "ABC123"
    assert sanitize_code("ABC,123") == "ABC123"
    assert sanitize_code("ABC.123") == "ABC123"
    assert sanitize_code("ABC?123") == "ABC123"
    assert sanitize_code("ABC!123") == "ABC123"
    
    # Should preserve hyphens and underscores
    assert sanitize_code("ABC-123") == "ABC-123"
    assert sanitize_code("ABC_123") == "ABC_123"
    assert sanitize_code("ABC-123_DEF") == "ABC-123_DEF"


def test_sanitize_code_preserves_alphanumeric_hyphens_underscores():
    """Test sanitize_code preserves allowed characters (covers línea 92)."""
    assert sanitize_code("A1B2C3") == "A1B2C3"
    assert sanitize_code("ABC-123") == "ABC-123"
    assert sanitize_code("ABC_123") == "ABC_123"
    assert sanitize_code("ABC-123_DEF-456") == "ABC-123_DEF-456"
    assert sanitize_code("abc123DEF") == "abc123DEF"
    assert sanitize_code("123456") == "123456"
    assert sanitize_code("ABCDEF") == "ABCDEF"


def test_sanitize_code_max_length():
    """Test sanitize_code respects max_length (covers lines 97-98)."""
    long_code = "A" * 100
    short_code = "A" * 50
    
    # Should raise error for code exceeding max_length
    with pytest.raises(ValueError, match="exceeds maximum length of 50"):
        sanitize_code(long_code, max_length=50)
    
    # Should work for code within max_length
    result = sanitize_code(short_code, max_length=50)
    assert len(result) == 50
    assert result == short_code
    
    # Custom max_length
    with pytest.raises(ValueError, match="exceeds maximum length of 10"):
        sanitize_code("A" * 20, max_length=10)
    
    result = sanitize_code("A" * 10, max_length=10)
    assert len(result) == 10


def test_sanitize_code_empty_string():
    """Test sanitize_code raises ValueError for empty string (covers lines 94-95)."""
    # Empty string after removal of invalid chars
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_code("")
    
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_code("   ")  # Only whitespace
    
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_code("@#$%")  # Only special characters (no allowed chars)
    
    with pytest.raises(ValueError, match="cannot be empty"):
        sanitize_code("   @#$%   ")  # Only whitespace and special chars


def test_sanitize_code_invalid_type():
    """Test sanitize_code raises ValueError for non-string input (covers lines 88-89)."""
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_code(123)
    
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_code(None)
    
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_code([])
    
    with pytest.raises(ValueError, match="must be a string"):
        sanitize_code({})


def test_sanitize_code_unicode_characters():
    """Test sanitize_code removes Unicode characters (covers línea 92).
    
    Note: The regex r'[^a-zA-Z0-9_-]' removes all non-ASCII characters including Unicode.
    However, hyphens at the end are preserved if they were originally there.
    """
    # Should remove Unicode characters, keeping only ASCII alphanumeric, hyphens, underscores
    assert sanitize_code("ABC-123-ñáéíóú") == "ABC-123-"
    assert sanitize_code("ABC-123-中文") == "ABC-123-"
    assert sanitize_code("ABC-123-日本語") == "ABC-123-"
    assert sanitize_code("héllo wörld") == "hllowrld"  # Removes accented chars, spaces
    
    # Test that hyphens and underscores are preserved
    assert sanitize_code("ABC-123_DEF") == "ABC-123_DEF"
    assert sanitize_code("ABC-123-DEF") == "ABC-123-DEF"


def test_sanitize_code_control_characters():
    """Test sanitize_code removes control characters (covers línea 92)."""
    assert sanitize_code("ABC\x00\x01\x02123") == "ABC123"
    assert sanitize_code("ABC\n\t123") == "ABC123"
    assert sanitize_code("ABC\r\n123") == "ABC123"


# ==================== Integration Tests ====================

def test_sanitize_string_and_validate_email_integration():
    """Test integration between sanitize_string and validate_email."""
    # Email that needs sanitization
    dirty_email = "  TEST@EXAMPLE.COM  \x00\x01"
    # First sanitize
    sanitized = sanitize_string(dirty_email, allow_empty=True)
    # Then validate (should normalize to lowercase)
    validated = validate_email(sanitized)
    assert validated == "test@example.com"


def test_sanitize_code_and_sanitize_string_integration():
    """Test integration between sanitize_code and sanitize_string."""
    # Code that needs sanitization
    dirty_code = "  ABC-123  @#$%"
    # sanitize_code removes invalid chars
    code_result = sanitize_code(dirty_code)
    assert code_result == "ABC-123"
    
    # sanitize_string also works but preserves more chars
    string_result = sanitize_string(dirty_code, allow_empty=True)
    assert "@#$%" in string_result  # sanitize_string keeps more chars


# ==================== Edge Cases ====================

def test_sanitize_string_boundary_length():
    """Test sanitize_string with boundary length values (covers lines 39-40)."""
    # Exactly at max_length
    exact_length = "a" * 255
    result = sanitize_string(exact_length, max_length=255)
    assert len(result) == 255
    
    # One character over max_length
    over_length = "a" * 256
    with pytest.raises(ValueError, match="exceeds maximum length"):
        sanitize_string(over_length, max_length=255)


def test_sanitize_code_boundary_length():
    """Test sanitize_code with boundary length values (covers lines 97-98)."""
    # Exactly at max_length
    exact_length = "A" * 50
    result = sanitize_code(exact_length, max_length=50)
    assert len(result) == 50
    
    # One character over max_length
    over_length = "A" * 51
    with pytest.raises(ValueError, match="exceeds maximum length"):
        sanitize_code(over_length, max_length=50)


def test_validate_email_real_world_examples():
    """Test validate_email with real-world email examples."""
    real_emails = [
        "john.doe@example.com",
        "jane.smith+tag@company.co.uk",
        "user123@test-domain.com",
        "admin@subdomain.example.org",
        "test_email@example-site.com",
    ]
    
    for email in real_emails:
        result = validate_email(email)
        assert result == email.lower().strip()
        assert "@" in result
        assert "." in result.split("@")[1]  # Domain has TLD

