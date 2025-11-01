"""
Centralized logging configuration for TirganachReloaded using Loguru
Provides structured, colored logging with file output and rotation
"""

import sys
from pathlib import Path
from typing import Optional

from loguru import logger


class CFFLogger:
    """Centralized logger configuration for the CFF Editor"""
    
    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent.parent
        self._configured = False
        
    def configure_logging(self, debug_mode: bool = False) -> None:
        """Configure Loguru logging with structured output"""
        if self._configured:
            return
            
        # Remove default logger
        logger.remove()
        
        # Determine log level
        log_level = "DEBUG" if debug_mode else "INFO"
        
        # Console handler with colors and structured format
        console_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        logger.add(
            sys.stdout,
            format=console_format,
            level=log_level,
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # File handler for logs with rotation
        logs_dir = self.project_root / "logs"
        logs_dir.mkdir(parents=True, exist_ok=True)
        
        file_format = (
            "{time:YYYY-MM-DD HH:mm:ss} | "
            "{level: <8} | "
            "{name}:{function}:{line} | "
            "{message}"
        )
        
        # Main log file with rotation
        logger.add(
            logs_dir / "cff_editor.log",
            format=file_format,
            level="DEBUG",
            rotation="10 MB",
            retention="7 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Error-only log file
        logger.add(
            logs_dir / "errors.log",
            format=file_format,
            level="ERROR",
            rotation="5 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Performance log file
        logger.add(
            logs_dir / "performance.log",
            format=file_format,
            level="INFO",
            rotation="5 MB",
            retention="3 days",
            compression="zip",
            filter=lambda record: "performance" in record["extra"].get("category", "")
        )
        
        self._configured = True
        logger.info("Logging system initialized")
        logger.debug(f"Project root: {self.project_root}")
        logger.debug(f"Log level: {log_level}")
    
    def get_logger(self, name: str = None):
        """Get a logger instance with optional name"""
        if name:
            return logger.bind(name=name)
        return logger
    
    def performance(self, operation: str):
        """Get a performance logger for timing operations"""
        return logger.bind(category="performance", operation=operation)
    
    def debug_mode(self, enabled: bool):
        """Toggle debug mode logging"""
        if enabled:
            logger.remove()
            self.configure_logging(debug_mode=True)
            logger.info("Debug mode enabled")
        else:
            logger.remove()
            self.configure_logging(debug_mode=False)
            logger.info("Debug mode disabled")


# Global logger instance
_cff_logger = CFFLogger()


def configure_logging(debug_mode: bool = False, project_root: Optional[Path] = None):
    """Configure the global logging system"""
    global _cff_logger
    if project_root:
        _cff_logger = CFFLogger(project_root)
    _cff_logger.configure_logging(debug_mode)


def get_logger(name: str = None):
    """Get a logger instance"""
    return _cff_logger.get_logger(name)


def performance_logger(operation: str):
    """Get a performance logger for timing operations"""
    return _cff_logger.performance(operation)


# Convenience functions that match the old logging interface
def info(message: str, **kwargs):
    """Log info message"""
    logger.info(message, **kwargs)


def debug(message: str, **kwargs):
    """Log debug message"""
    logger.debug(message, **kwargs)


def warning(message: str, **kwargs):
    """Log warning message"""
    logger.warning(message, **kwargs)


def error(message: str, **kwargs):
    """Log error message"""
    logger.error(message, **kwargs)


def critical(message: str, **kwargs):
    """Log critical message"""
    logger.critical(message, **kwargs)


def exception(message: str, **kwargs):
    """Log exception with traceback"""
    logger.exception(message, **kwargs)
