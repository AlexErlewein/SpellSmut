"""
Test logging configuration for TirganachReloaded tests
Simplified logging setup for test environments
"""

import sys
from pathlib import Path

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from loguru import logger
    
    # Remove default logger
    logger.remove()
    
    # Simple console format for tests
    test_format = (
        "<green>{time:HH:mm:ss}</green> | "
        "<level>{level: <7}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan> | "
        "<level>{message}</level>"
    )
    
    # Add console handler for tests
    logger.add(
        sys.stdout,
        format=test_format,
        level="INFO",
        colorize=True,
        filter=lambda record: "test" in record["name"].lower() or "weapon_forge" in record["name"]
    )
    
    def get_test_logger(name: str = None):
        """Get a logger for testing"""
        if name:
            return logger.bind(name=name)
        return logger
    
    # Test-specific logging functions
    def test_info(message: str, **kwargs):
        """Log test info"""
        logger.info(f"TEST: {message}", **kwargs)
    
    def test_success(message: str, **kwargs):
        """Log test success"""
        logger.success(f"✓ {message}", **kwargs)
    
    def test_error(message: str, **kwargs):
        """Log test error"""
        logger.error(f"✗ {message}", **kwargs)
    
    def test_header(message: str, **kwargs):
        """Log test header"""
        logger.info(f"{'='*60}")
        logger.info(f"TEST: {message}")
        logger.info(f"{'='*60}")
    
    LOGGING_AVAILABLE = True
    
except ImportError:
    # Fallback to basic print statements if loguru not available
    LOGGING_AVAILABLE = False
    
    def get_test_logger(name: str = None):
        """Fallback logger"""
        return None
    
    def test_info(message: str, **kwargs):
        print(f"TEST: {message}")
    
    def test_success(message: str, **kwargs):
        print(f"✓ {message}")
    
    def test_error(message: str, **kwargs):
        print(f"✗ {message}")
    
    def test_header(message: str, **kwargs):
        print("=" * 60)
        print(f"TEST: {message}")
        print("=" * 60)
