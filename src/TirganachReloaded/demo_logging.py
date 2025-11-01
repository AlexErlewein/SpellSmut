#!/usr/bin/env python3
"""
Demonstration of the new Loguru-based logging system
Run this script to see the structured, colored logging in action
"""

import sys
import time
from pathlib import Path

# Add the project to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

def demo_logging():
    """Demonstrate the new logging system"""
    
    # Import the logging configuration
    from TirganachReloaded.cff_editor.logging_config import (
        configure_logging, 
        get_logger, 
        performance_logger,
        info, debug, warning, error, critical
    )
    
    # Configure logging with debug mode
    print("🚀 Starting SpellForce CFF Editor Logging Demo")
    print("=" * 60)
    
    configure_logging(debug_mode=True, project_root=project_root)
    
    # Get different types of loggers
    main_logger = get_logger("demo_main")
    ui_logger = get_logger("demo_ui")
    data_logger = get_logger("demo_data")
    
    # Basic logging examples
    main_logger.info("Application started successfully")
    main_logger.debug("Debug information - detailed system state")
    ui_logger.info("UI components initialized")
    data_logger.info("Data models loaded")
    
    # Performance logging examples
    perf_logger = performance_logger("data_loading")
    perf_logger.info("Starting data loading operation")
    
    # Simulate some work
    time.sleep(0.5)
    perf_logger.info("Data loading completed in 0.50s")
    
    # Performance logging for another operation
    cache_perf = performance_logger("cache_operations")
    cache_perf.info("Building cache indices")
    time.sleep(0.2)
    cache_perf.info("Cache built successfully in 0.20s")
    
    # Warning and error examples
    ui_logger.warning("Deprecated API used - consider updating")
    data_logger.error("Failed to load optional data file")
    
    # Exception logging
    try:
        # Simulate an error
        raise ValueError("This is a demonstration error")
    except Exception as e:
        main_logger.exception(f"Caught exception: {e}")
    
    # Structured logging with extra context
    main_logger.info(
        "User action completed", 
        extra={
            "user_id": "demo_user", 
            "action": "load_file",
            "file_path": "/path/to/demo.cff",
            "duration_ms": 150
        }
    )
    
    # Show different log levels
    debug("This is a debug message")
    info("This is an info message")
    warning("This is a warning message")
    error("This is an error message")
    critical("This is a critical message")
    
    print("\n" + "=" * 60)
    print("✅ Logging demonstration completed!")
    print("\n📁 Log files created in:")
    print(f"   {project_root}/logs/")
    print("   ├── cff_editor.log (all logs)")
    print("   ├── errors.log (errors only)")
    print("   └── performance.log (performance metrics)")
    print("\n🎯 Features demonstrated:")
    print("   ✓ Colored console output with timestamps")
    print("   ✓ Structured logging with module/function/line info")
    print("   ✓ Performance logging with operation tracking")
    print("   ✓ Exception logging with full tracebacks")
    print("   ✓ Multiple log files with rotation")
    print("   ✓ Debug mode toggle")


if __name__ == "__main__":
    demo_logging()
