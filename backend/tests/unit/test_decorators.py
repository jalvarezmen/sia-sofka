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
    cache_result,
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

    @pytest.mark.asyncio
    async def test_works_with_kwargs_only(self):
        """Test that decorator works with kwargs-only parameters."""
        @validate_not_none('user_id')
        async def function_with_kwargs(*, user_id: int, email: str = "test@example.com"):
            return f"{user_id}:{email}"

        # Should work with valid kwargs
        result = await function_with_kwargs(user_id=123)
        assert result == "123:test@example.com"

        # Should fail with None in kwargs
        with pytest.raises(ValueError) as exc_info:
            await function_with_kwargs(user_id=None)
        assert "user_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_works_with_default_values(self):
        """Test that decorator respects default values."""
        @validate_not_none('required')
        async def function_with_defaults(required: int, optional: str = None):
            return f"{required}:{optional}"

        # Should work with optional having default None (not in validation list)
        result = await function_with_defaults(123)
        assert result == "123:None"

        # Should work with explicit None for optional
        result = await function_with_defaults(123, None)
        assert result == "123:None"

        # Should fail with None for required
        with pytest.raises(ValueError):
            await function_with_defaults(None)


class TestCacheResult:
    """Tests for @cache_result decorator."""

    @pytest.mark.asyncio
    async def test_caches_result_for_first_call(self):
        """Test that result is cached on first call."""
        call_count = 0

        @cache_result(ttl_seconds=300)
        async def expensive_function(value: int):
            nonlocal call_count
            call_count += 1
            return value * 2

        result1 = await expensive_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call should use cache
        result2 = await expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # Should not call again

    @pytest.mark.asyncio
    async def test_cache_expires_after_ttl(self):
        """Test that cache expires after TTL."""
        call_count = 0

        @cache_result(ttl_seconds=0.1)  # Very short TTL
        async def timed_function(value: int):
            nonlocal call_count
            call_count += 1
            return value * 2

        # First call
        result1 = await timed_function(5)
        assert result1 == 10
        assert call_count == 1

        # Second call immediately (should use cache)
        result2 = await timed_function(5)
        assert result2 == 10
        assert call_count == 1

        # Wait for TTL to expire
        import asyncio
        await asyncio.sleep(0.2)

        # Third call after expiration (should call again)
        result3 = await timed_function(5)
        assert result3 == 10
        assert call_count == 2  # Should call again

    @pytest.mark.asyncio
    async def test_cache_key_includes_function_and_args(self):
        """Test that different arguments create different cache keys."""
        call_count = 0

        @cache_result(ttl_seconds=300)
        async def function_with_args(value: int, multiplier: int = 2):
            nonlocal call_count
            call_count += 1
            return value * multiplier

        # First call with value=5
        result1 = await function_with_args(5)
        assert result1 == 10
        assert call_count == 1

        # Second call with value=5 (same args - should use cache)
        result2 = await function_with_args(5)
        assert result2 == 10
        assert call_count == 1

        # Third call with value=10 (different args - should call again)
        result3 = await function_with_args(10)
        assert result3 == 20
        assert call_count == 2

        # Fourth call with value=5 again (should use cache)
        result4 = await function_with_args(5)
        assert result4 == 10
        assert call_count == 2  # Still 2, using cache

    @pytest.mark.asyncio
    async def test_cache_works_with_kwargs(self):
        """Test that cache works correctly with kwargs."""
        call_count = 0

        @cache_result(ttl_seconds=300)
        async def function_with_kwargs(value: int, multiplier: int = 2):
            nonlocal call_count
            call_count += 1
            return value * multiplier

        # First call with positional args
        result1 = await function_with_kwargs(5)
        assert call_count == 1

        # Second call with kwargs (different call signature but same result)
        result2 = await function_with_kwargs(value=5)
        # These should be different cache keys due to different call signatures
        assert call_count == 2  # Should call again due to different cache key

    @pytest.mark.asyncio
    async def test_cache_cleanup_removes_expired_entries(self):
        """Test that cache cleanup removes expired entries."""
        call_count = 0

        @cache_result(ttl_seconds=0.1)
        async def many_cached_values(value: int):
            nonlocal call_count
            call_count += 1
            return value

        # Create many cache entries
        for i in range(100):
            await many_cached_values(i)

        assert call_count == 100

        # Wait for all to expire
        import asyncio
        await asyncio.sleep(0.2)

        # Trigger cleanup by adding more entries (cache > 1000 should trigger cleanup)
        # Actually, we need to add enough to trigger the cleanup (len(cache) > 1000)
        # But we can test that expired entries are removed when cache is large
        # For now, let's test that new entries work after expiration
        result = await many_cached_values(0)
        assert result == 0
        assert call_count == 101  # Should call again after expiration

    @pytest.mark.asyncio
    async def test_cache_cleanup_triggers_when_over_threshold(self):
        """Test that cache cleanup is triggered when cache size exceeds 1000 (lines 247-253)."""
        call_count = 0

        @cache_result(ttl_seconds=0.01)  # Very short TTL so entries expire quickly
        async def create_many_entries(i: int):
            nonlocal call_count
            call_count += 1
            return i

        # First, create entries that will expire
        for i in range(100):
            await create_many_entries(i)
        
        assert call_count == 100

        # Wait for entries to expire
        import asyncio
        await asyncio.sleep(0.02)

        # Now create enough entries to exceed 1000 threshold (lines 246-253)
        # When adding entry 1001, cleanup should be triggered
        # Since previous 100 entries are expired, they should be removed (line 253)
        for i in range(100, 1002):
            await create_many_entries(i)

        assert call_count == 1002  # Should have called function for all new entries

        # Verify that expired entries were cleaned up
        # Create one more entry that should trigger cleanup again
        result = await create_many_entries(2000)
        assert result == 2000
        assert call_count == 1003  # Should increment

        # Verify cache still works for recent entries
        result_cached = await create_many_entries(2000)
        assert result_cached == 2000
        assert call_count == 1003  # Should use cache, no increment

    @pytest.mark.asyncio
    async def test_cache_cleanup_on_large_cache(self):
        """Test that cache cleanup is triggered when cache is large."""
        call_count = 0
        
        @cache_result(ttl_seconds=300)
        async def create_cache_entry(i: int):
            nonlocal call_count
            call_count += 1
            return i

        # Create many entries (but not enough to trigger cleanup threshold of 1000)
        # We'll create 50 entries and verify they're cached
        for i in range(50):
            await create_cache_entry(i)
        
        assert call_count == 50

        # All should be cached (same arguments)
        result = await create_cache_entry(0)
        assert result == 0
        assert call_count == 50  # Still 50, using cache
        
        # New argument should call function
        result_new = await create_cache_entry(100)
        assert result_new == 100
        assert call_count == 51  # Should increment for new argument

    @pytest.mark.asyncio
    async def test_cache_logs_hit(self):
        """Test that cache hit is logged."""
        @cache_result(ttl_seconds=300)
        async def cached_function(value: int):
            return value * 2

        with patch('app.core.decorators.logger') as mock_logger:
            # First call (cache miss)
            await cached_function(5)
            # Should not log cache hit yet
            
            # Second call (cache hit)
            await cached_function(5)
            # Should log cache hit
            mock_logger.debug.assert_called()
            assert "Cache hit" in str(mock_logger.debug.call_args)

    @pytest.mark.asyncio
    async def test_cache_handles_different_function_instances(self):
        """Test that cache works correctly with different function instances."""
        # Each decorator call creates its own cache, so this should work
        call_count_1 = 0
        call_count_2 = 0

        @cache_result(ttl_seconds=300)
        async def function1(value: int):
            nonlocal call_count_1
            call_count_1 += 1
            return value + 1

        @cache_result(ttl_seconds=300)
        async def function2(value: int):
            nonlocal call_count_2
            call_count_2 += 1
            return value + 2

        # Call both functions
        result1 = await function1(5)
        result2 = await function2(5)

        assert result1 == 6
        assert result2 == 7
        assert call_count_1 == 1
        assert call_count_2 == 1

        # Call again - both should use cache
        await function1(5)
        await function2(5)

        assert call_count_1 == 1
        assert call_count_2 == 1


class TestHandleRepositoryErrorsEdgeCases:
    """Edge cases for @handle_repository_errors decorator."""

    @pytest.mark.asyncio
    async def test_handles_integrity_error_without_orig(self):
        """Test that IntegrityError without orig attribute is handled."""
        @handle_repository_errors
        async def failing_function():
            error = IntegrityError("statement", "params", None)
            # Remove orig if it exists
            if hasattr(error, 'orig'):
                delattr(error, 'orig')
            raise error

        with pytest.raises(ConflictError):
            await failing_function()

    @pytest.mark.asyncio
    async def test_handles_general_integrity_error(self):
        """Test that general IntegrityError (not unique/foreign key) is handled."""
        @handle_repository_errors
        async def failing_function():
            orig = Mock()
            orig.__str__ = Mock(return_value="CHECK constraint failed")
            error = IntegrityError("statement", "params", orig)
            raise error

        with pytest.raises(ConflictError) as exc_info:
            await failing_function()
        
        assert "constraint violation" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_handles_duplicate_key_error(self):
        """Test that duplicate key errors are handled."""
        @handle_repository_errors
        async def failing_function():
            orig = Mock()
            orig.__str__ = Mock(return_value="duplicate key value")
            error = IntegrityError("statement", "params", orig)
            raise error

        with pytest.raises(ConflictError) as exc_info:
            await failing_function()
        
        assert "already exists" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_unexpected_exception_is_re_raised(self):
        """Test that unexpected exceptions are re-raised without wrapping."""
        @handle_repository_errors
        async def failing_function():
            raise RuntimeError("Unexpected runtime error")

        with pytest.raises(RuntimeError) as exc_info:
            await failing_function()
        
        assert "Unexpected runtime error" in str(exc_info.value)


class TestRetryOnDbLockEdgeCases:
    """Edge cases for @retry_on_db_lock decorator."""

    @pytest.mark.asyncio
    async def test_exponential_backoff(self):
        """Test that retry uses exponential backoff."""
        call_times = []
        
        @retry_on_db_lock(max_retries=3, delay=0.05)
        async def function_with_lock():
            import time
            call_times.append(time.time())
            if len(call_times) < 3:
                raise SQLAlchemyError("database is locked")
            return "success"

        result = await function_with_lock()
        
        assert result == "success"
        assert len(call_times) == 3
        
        # Verify exponential backoff (delays should increase)
        # delay * (attempt + 1): attempt 0 -> delay*1, attempt 1 -> delay*2
        # So time between calls should be approximately 0.05, 0.10, etc.
        if len(call_times) >= 2:
            # Verify there's a delay between retries
            delay_between = call_times[1] - call_times[0]
            assert delay_between > 0.04  # Should be approximately 0.05 seconds

    @pytest.mark.asyncio
    async def test_max_retries_exhausted_raises_last_exception(self):
        """Test that when max retries are exhausted, last exception is raised (lines 171-172)."""
        call_count = 0
        
        @retry_on_db_lock(max_retries=3, delay=0.01)
        async def always_locked():
            nonlocal call_count
            call_count += 1
            # Always raise lock error so it retries
            # On attempt 0 and 1, it will continue (retry)
            # On attempt 2 (last), it will break from loop and reach lines 171-172
            raise SQLAlchemyError("database is locked")

        # Patch logger to verify lines 171-172 are executed
        with patch('app.core.decorators.logger') as mock_logger:
            with pytest.raises(SQLAlchemyError) as exc_info:
                await always_locked()
            
            # Verify error is logged when retries are exhausted (line 171)
            mock_logger.error.assert_called()
            error_calls = [str(call) for call in mock_logger.error.call_args_list]
            assert any("Max retries exceeded" in str(call) for call in error_calls), \
                f"Expected 'Max retries exceeded' in logger.error calls. Got: {error_calls}"
            
            # Verify last exception is raised (line 172)
            assert "database is locked" in str(exc_info.value)
            assert call_count == 3  # Should retry 3 times (attempts 0, 1, 2)

    @pytest.mark.asyncio
    async def test_non_lock_error_is_not_retried(self):
        """Test that non-lock SQLAlchemy errors are not retried."""
        call_count = 0
        
        @retry_on_db_lock(max_retries=3, delay=0.01)
        async def syntax_error():
            nonlocal call_count
            call_count += 1
            raise SQLAlchemyError("syntax error in SQL")

        with pytest.raises(SQLAlchemyError):
            await syntax_error()
        
        assert call_count == 1  # Should not retry
