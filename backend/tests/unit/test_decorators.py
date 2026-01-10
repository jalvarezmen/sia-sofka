"""Tests for core decorators."""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.decorators import (
    handle_service_errors,
    handle_repository_errors,
    log_execution_time,
    retry_on_db_lock,
    validate_not_none,
)
from app.core.exceptions import ValidationError, NotFoundError, ConflictError


class TestHandleServiceErrors:
    """Tests for @handle_service_errors decorator."""

    @pytest.mark.asyncio
    async def test_converts_value_error_to_validation_error(self):
        """Test that ValueError is converted to ValidationError."""
        @handle_service_errors
        async def failing_function():
            raise ValueError("Invalid input data")

        with pytest.raises(ValidationError) as exc_info:
            await failing_function()
        
        assert "Invalid input data" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_converts_lookup_error_to_not_found(self):
        """Test that LookupError is converted to NotFoundError."""
        @handle_service_errors
        async def failing_function():
            raise KeyError("user_id")

        with pytest.raises(NotFoundError):
            await failing_function()

    @pytest.mark.asyncio
    async def test_successful_execution_passes_through(self):
        """Test that successful execution works normally."""
        @handle_service_errors
        async def successful_function():
            return "success"

        result = await successful_function()
        assert result == "success"

    @pytest.mark.asyncio
    async def test_logs_unexpected_errors(self):
        """Test that unexpected errors are logged."""
        @handle_service_errors
        async def failing_function():
            raise RuntimeError("Unexpected error")

        with pytest.raises(ValidationError) as exc_info:
            await failing_function()
        
        assert "unexpected error occurred" in str(exc_info.value.detail).lower()


class TestHandleRepositoryErrors:
    """Tests for @handle_repository_errors decorator."""

    @pytest.mark.asyncio
    async def test_converts_unique_constraint_to_conflict(self):
        """Test that unique constraint violations become ConflictError."""
        @handle_repository_errors
        async def failing_function():
            # Simulate IntegrityError with unique constraint message
            orig = Mock()
            orig.__str__ = Mock(return_value="UNIQUE constraint failed")
            error = IntegrityError("statement", "params", orig)
            raise error

        with pytest.raises(ConflictError) as exc_info:
            await failing_function()
        
        assert "already exists" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_converts_foreign_key_to_validation(self):
        """Test that foreign key violations become ValidationError."""
        @handle_repository_errors
        async def failing_function():
            orig = Mock()
            orig.__str__ = Mock(return_value="FOREIGN KEY constraint failed")
            error = IntegrityError("statement", "params", orig)
            raise error

        with pytest.raises(ValidationError) as exc_info:
            await failing_function()
        
        assert "does not exist" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_handles_general_sqlalchemy_error(self):
        """Test that general SQLAlchemy errors are handled."""
        @handle_repository_errors
        async def failing_function():
            raise SQLAlchemyError("Database connection failed")

        with pytest.raises(ValidationError) as exc_info:
            await failing_function()
        
        assert "database error" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_successful_execution_passes_through(self):
        """Test that successful execution works normally."""
        @handle_repository_errors
        async def successful_function():
            return {"id": 1, "name": "test"}

        result = await successful_function()
        assert result["id"] == 1


class TestLogExecutionTime:
    """Tests for @log_execution_time decorator."""

    @pytest.mark.asyncio
    async def test_logs_slow_operations(self):
        """Test that slow operations are logged as warnings."""
        @log_execution_time
        async def slow_function():
            await asyncio.sleep(1.1)
            return "done"

        with patch('app.core.decorators.logger') as mock_logger:
            result = await slow_function()
            assert result == "done"
            # Should log warning for operations > 1 second
            assert mock_logger.warning.called

    @pytest.mark.asyncio
    async def test_logs_fast_operations_as_debug(self):
        """Test that fast operations are logged as debug."""
        @log_execution_time
        async def fast_function():
            return "quick"

        with patch('app.core.decorators.logger') as mock_logger:
            result = await fast_function()
            assert result == "quick"
            assert mock_logger.debug.called

    @pytest.mark.asyncio
    async def test_logs_errors_with_execution_time(self):
        """Test that errors are logged with execution time."""
        @log_execution_time
        async def failing_function():
            raise ValueError("Test error")

        with patch('app.core.decorators.logger') as mock_logger:
            with pytest.raises(ValueError):
                await failing_function()
            assert mock_logger.error.called


class TestRetryOnDbLock:
    """Tests for @retry_on_db_lock decorator."""

    @pytest.mark.asyncio
    async def test_retries_on_deadlock(self):
        """Test that function retries on database lock errors."""
        call_count = 0

        @retry_on_db_lock(max_retries=3, delay=0.01)
        async def function_with_lock():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise SQLAlchemyError("database is locked")
            return "success"

        result = await function_with_lock()
        assert result == "success"
        assert call_count == 2

    @pytest.mark.asyncio
    async def test_gives_up_after_max_retries(self):
        """Test that function gives up after max retries."""
        @retry_on_db_lock(max_retries=2, delay=0.01)
        async def always_fails():
            raise SQLAlchemyError("deadlock detected")

        with pytest.raises(SQLAlchemyError):
            await always_fails()

    @pytest.mark.asyncio
    async def test_does_not_retry_non_lock_errors(self):
        """Test that non-lock errors are not retried."""
        call_count = 0

        @retry_on_db_lock(max_retries=3, delay=0.01)
        async def function_with_other_error():
            nonlocal call_count
            call_count += 1
            raise SQLAlchemyError("syntax error")

        with pytest.raises(SQLAlchemyError):
            await function_with_other_error()
        
        assert call_count == 1  # Should not retry

    @pytest.mark.asyncio
    async def test_successful_on_first_try(self):
        """Test that successful execution doesn't retry."""
        call_count = 0

        @retry_on_db_lock(max_retries=3, delay=0.01)
        async def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = await successful_function()
        assert result == "success"
        assert call_count == 1


class TestValidateNotNone:
    """Tests for @validate_not_none decorator."""

    @pytest.mark.asyncio
    async def test_raises_error_when_param_is_none(self):
        """Test that error is raised when parameter is None."""
        @validate_not_none('user_id', 'email')
        async def function_with_params(user_id: int, email: str):
            return f"{user_id}:{email}"

        with pytest.raises(ValueError) as exc_info:
            await function_with_params(None, "test@example.com")
        
        assert "user_id" in str(exc_info.value)
        assert "cannot be None" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_passes_when_all_params_valid(self):
        """Test that function executes when all params are valid."""
        @validate_not_none('user_id', 'email')
        async def function_with_params(user_id: int, email: str):
            return f"{user_id}:{email}"

        result = await function_with_params(123, "test@example.com")
        assert result == "123:test@example.com"

    @pytest.mark.asyncio
    async def test_checks_multiple_params(self):
        """Test that multiple parameters are validated."""
        @validate_not_none('a', 'b', 'c')
        async def function_with_many_params(a, b, c):
            return a + b + c

        # Should work with valid params
        result = await function_with_many_params(1, 2, 3)
        assert result == 6

        # Should fail with None in middle
        with pytest.raises(ValueError) as exc_info:
            await function_with_many_params(1, None, 3)
        assert "b" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_allows_optional_params_not_in_list(self):
        """Test that params not in validation list can be None."""
        @validate_not_none('required_param')
        async def function_with_optional(required_param, optional_param=None):
            return f"{required_param}:{optional_param}"

        # Should work with None optional param
        result = await function_with_optional("test", None)
        assert result == "test:None"

        # Should fail with None required param
        with pytest.raises(ValueError):
            await function_with_optional(None, "optional")
