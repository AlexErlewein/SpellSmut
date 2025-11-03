"""
Integration tests for existing TirganachReloaded integration
Tests that existing optimizations work with new engine architecture
"""

import sys
from pathlib import Path

import pytest

# Add src to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from src.engine.adapters.tirganach_adapter import (
    TirganachDataAdapter,
    get_tirganach_adapter,
)
from src.engine.parsers.enhanced_cff_parser import (
    EnhancedCFFParser,
    create_optimized_parser,
)
from src.engine.services.enhanced_data_service import (
    EnhancedDataCache,
    create_enhanced_data_service,
    create_enhanced_validation_service,
)


class TestTirganachIntegration:
    """Test integration with existing TirganachReloaded components"""

    @pytest.fixture
    def adapter(self):
        """Fixture providing TirganachDataAdapter instance"""
        return get_tirganach_adapter()

    def test_adapter_creation(self, adapter):
        """Test that adapter can be created"""
        assert adapter is not None
        assert isinstance(adapter, TirganachDataAdapter)

    def test_cache_creation(self):
        """Test that enhanced cache can be created"""
        cache = EnhancedDataCache()
        assert cache is not None
        assert hasattr(cache, "ttl")
        assert hasattr(cache, "max_size")

    def test_service_creation(self):
        """Test that enhanced services can be created"""
        service = create_enhanced_data_service()
        assert service is not None
        assert hasattr(service, "adapter")
        assert hasattr(service, "cache")

    def test_validation_service_creation(self):
        """Test that enhanced validation service can be created"""
        validator = create_enhanced_validation_service()
        assert validator is not None
        assert hasattr(validator, "adapter")
        assert hasattr(validator, "errors")

    def test_parser_creation(self):
        """Test that enhanced parsers can be created"""
        parser = create_optimized_parser()
        assert parser is not None
        assert isinstance(parser, EnhancedCFFParser)

        numpy_parser = create_optimized_parser("numpy")
        assert numpy_parser is not None
        # Should be enhanced parser with NumPy capabilities
        assert hasattr(numpy_parser, "numpy_arrays")


class TestExistingOptimizationPatterns:
    """Test that existing optimization patterns work"""

    def test_performance_timer_decorator(self):
        """Test that performance timer decorator works"""
        from src.engine.utils.performance import performance_timer

        @performance_timer
        def test_function():
            return "test"

        result = test_function()
        assert result == "test"

    def test_cache_result_decorator(self):
        """Test that cache result decorator works"""
        from src.engine.utils.performance import cache_result

        @cache_result(ttl=10)
        def cached_function(x):
            return x * 2

        result1 = cached_function(5)
        result2 = cached_function(5)  # Should be cached

        assert result1 == 10
        assert result2 == 10

    def test_perf_monitor(self):
        """Test that performance monitor works"""
        from src.engine.utils.performance import perf_monitor

        perf_monitor.start_timer("test_timer")
        perf_monitor.stop_timer("test_timer")

        # Should not crash
        assert True


class TestIntegrationWithNewArchitecture:
    """Test integration between existing components and new architecture"""

    def test_data_model_compatibility(self):
        """Test compatibility between data models"""
        # This would test that existing data models can work with new architecture
        pass

    def test_service_pattern_integration(self):
        """Test that service patterns integrate correctly"""
        service = create_enhanced_data_service()
        assert service is not None

        # Should have access to existing patterns
        assert hasattr(service, "cache")
        assert hasattr(service, "_loaded_categories")

    def test_parser_pattern_integration(self):
        """Test that parser patterns integrate correctly"""
        parser = create_optimized_parser()
        assert parser is not None

        # Should have access to existing optimization patterns
        assert hasattr(parser, "optimization_stats")
        assert hasattr(parser, "file_path")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
