"""Tests for repository mixins."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.mixins import EagerLoadMixin, PaginationMixin, TimestampMixin


class TestEagerLoadMixin:
    """Tests for EagerLoadMixin - testing mixin logic, not actual DB operations."""

    def test_mixin_can_be_instantiated(self):
        """Test that EagerLoadMixin can be used in a repository."""
        
        class TestRepository(EagerLoadMixin):
            def __init__(self):
                self.db = None  # Mock db
        
        repo = TestRepository()
        assert hasattr(repo, '_get_one_with_relations')
        assert hasattr(repo, '_get_many_with_relations')

    def test_mixin_methods_are_async(self):
        """Test that mixin methods are properly async."""
        import inspect
        
        class TestRepository(EagerLoadMixin):
            def __init__(self):
                self.db = None
        
        repo = TestRepository()
        
        assert inspect.iscoroutinefunction(repo._get_one_with_relations)
        assert inspect.iscoroutinefunction(repo._get_many_with_relations)


class TestPaginationMixin:
    """Tests for PaginationMixin."""

    def test_validate_pagination_with_valid_params(self):
        """Test validation with valid parameters."""
        
        class TestRepository(PaginationMixin):
            pass
        
        repo = TestRepository()
        
        skip, limit = repo._validate_pagination(0, 50)
        assert skip == 0
        assert limit == 50

    def test_validate_pagination_rejects_negative_skip(self):
        """Test that negative skip is rejected."""
        
        class TestRepository(PaginationMixin):
            pass
        
        repo = TestRepository()
        
        with pytest.raises(ValueError) as exc_info:
            repo._validate_pagination(-1, 50)
        
        assert "non-negative" in str(exc_info.value).lower()

    def test_validate_pagination_rejects_zero_limit(self):
        """Test that zero limit is rejected."""
        
        class TestRepository(PaginationMixin):
            pass
        
        repo = TestRepository()
        
        with pytest.raises(ValueError) as exc_info:
            repo._validate_pagination(0, 0)
        
        assert "positive" in str(exc_info.value).lower()

    def test_validate_pagination_rejects_negative_limit(self):
        """Test that negative limit is rejected."""
        
        class TestRepository(PaginationMixin):
            pass
        
        repo = TestRepository()
        
        with pytest.raises(ValueError) as exc_info:
            repo._validate_pagination(0, -10)
        
        assert "positive" in str(exc_info.value).lower()

    def test_validate_pagination_caps_limit_at_max(self):
        """Test that limit is capped at MAX_PAGE_SIZE."""
        
        class TestRepository(PaginationMixin):
            MAX_PAGE_SIZE = 1000
        
        repo = TestRepository()
        
        skip, limit = repo._validate_pagination(0, 5000)
        assert limit == 1000  # Should be capped

    def test_validate_pagination_allows_max_limit(self):
        """Test that MAX_PAGE_SIZE is allowed."""
        
        class TestRepository(PaginationMixin):
            MAX_PAGE_SIZE = 1000
        
        repo = TestRepository()
        
        skip, limit = repo._validate_pagination(0, 1000)
        assert limit == 1000

    def test_validate_pagination_with_large_skip(self):
        """Test validation with large skip value."""
        
        class TestRepository(PaginationMixin):
            pass
        
        repo = TestRepository()
        
        skip, limit = repo._validate_pagination(1000000, 50)
        assert skip == 1000000
        assert limit == 50

    def test_default_page_sizes_are_defined(self):
        """Test that default constants are defined."""
        
        class TestRepository(PaginationMixin):
            pass
        
        repo = TestRepository()
        
        assert hasattr(repo, 'DEFAULT_PAGE_SIZE')
        assert hasattr(repo, 'MAX_PAGE_SIZE')
        assert repo.DEFAULT_PAGE_SIZE == 100
        assert repo.MAX_PAGE_SIZE == 1000


class TestTimestampMixin:
    """Tests for TimestampMixin."""

    def test_timestamp_mixin_has_get_recent_method(self):
        """Test that TimestampMixin provides get_recent method."""
        import inspect
        
        class TestRepository(TimestampMixin):
            def __init__(self):
                self.db = None
        
        repo = TestRepository()
        
        assert hasattr(repo, '_get_recent')
        assert inspect.iscoroutinefunction(repo._get_recent)

    def test_mixin_can_be_combined_with_others(self):
        """Test that mixins can be combined in a repository."""
        
        class TestRepository(EagerLoadMixin, PaginationMixin, TimestampMixin):
            def __init__(self):
                self.db = None
        
        repo = TestRepository()
        
        # Should have methods from all mixins
        assert hasattr(repo, '_get_one_with_relations')
        assert hasattr(repo, '_get_many_with_relations')
        assert hasattr(repo, '_validate_pagination')
        assert hasattr(repo, '_get_recent')
        assert hasattr(repo, 'DEFAULT_PAGE_SIZE')
        assert hasattr(repo, 'MAX_PAGE_SIZE')

