# SpellForce CFF Editor - Loguru Logging System

## Overview

The SpellForce CFF Editor now uses **Loguru** for structured, colored logging with advanced features like file rotation, performance tracking, and debug mode toggling.

## 🚀 Quick Start

### Running the Editor

```bash
# Normal mode - INFO level logging
uv run src/TirganachReloaded/tirganach.py

# Debug mode - DEBUG level logging with more detail
uv run src/TirganachReloaded/tirganach.py --debug
```

### Running the Demo

```bash
# See the logging system in action
uv run src/TirganachReloaded/demo_logging.py
```

## 📁 Log Files

All logs are automatically created in the `logs/` directory:

```
logs/
├── cff_editor.log      # All application logs (rotates at 10MB, keeps 7 days)
├── errors.log          # Error and critical logs only (rotates at 5MB, keeps 30 days)
└── performance.log     # Performance metrics and timing (rotates at 5MB, keeps 3 days)
```

## 🎯 Features

### 1. **Colored Console Output**
```
2025-01-15 14:30:25 | INFO     | main:main:25 | Starting SpellForce CFF Editor
2025-01-15 14:30:25 | DEBUG    | data_model:_load_icon_data:533 | Starting icon data loading
2025-01-15 14:30:26 | SUCCESS  | id_manager:test_id_manager:31 | Next weapon ID: 10000
```

### 2. **Performance Logging**
Track operation timing automatically:
```python
from .logging_config import performance_logger

perf_logger = performance_logger("data_loading")
perf_logger.info("Starting operation")
# ... do work ...
perf_logger.info("Operation completed in 0.45s")
```

### 3. **Structured Logging**
Add context to your log messages:
```python
logger.info("User action completed", extra={
    "user_id": "admin",
    "action": "load_file", 
    "duration_ms": 150
})
```

### 4. **Exception Logging**
Full tracebacks with context:
```python
try:
    risky_operation()
except Exception as e:
    logger.exception(f"Operation failed: {e}")
```

## 🛠️ Usage in Code

### Import the logging system
```python
from .logging_config import get_logger, performance_logger
```

### Get a logger for your module
```python
class MyClass:
    def __init__(self):
        self.logger = get_logger("my_class")
        self.logger.info("Initialized")
```

### Performance tracking
```python
def load_data():
    perf_logger = performance_logger("data_loading")
    start_time = time.time()
    
    # Load data...
    
    perf_logger.info(f"Data loaded in {time.time() - start_time:.2f}s")
```

### Different log levels
```python
logger.debug("Detailed debugging info")
logger.info("General information")
logger.warning("Something unusual happened")
logger.error("Something went wrong")
logger.critical("Critical system failure")
```

## 🧪 Testing with Logging

Test files use a simplified logging system:

```python
from test_logging import test_header, test_success, test_error

def test_something():
    test_header("Testing Component...")
    test_success("Component works correctly")
    test_error("Component failed")
```

## 🔧 Configuration

### Debug Mode
Enable debug logging for more detailed output:
```python
from .logging_config import configure_logging

configure_logging(debug_mode=True)
```

### Custom Logger
Get a logger with a custom name:
```python
from .logging_config import get_logger

logger = get_logger("custom_module_name")
```

## 📊 Log Format

### Console Format (Colored)
```
<green>{time:YYYY-MM-DD HH:mm:ss}</green> | 
<level>{level: <8}</level> | 
<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | 
<level>{message}</level>
```

### File Format (Plain Text)
```
2025-01-15 14:30:25 | INFO     | main:main:25 | Starting SpellForce CFF Editor
2025-01-15 14:30:25 | DEBUG    | data_model:_load_icon_data:533 | Starting icon data loading
```

## 🎨 Benefits Over Standard Logging

| Feature | Standard Logging | Loguru (New) |
|---------|------------------|--------------|
| **Colors** | ❌ No | ✅ Automatic |
| **File Rotation** | ❌ Manual setup | ✅ Built-in |
| **Performance Tracking** | ❌ Manual | ✅ Built-in |
| **Exception Handling** | Basic | ✅ Enhanced |
| **Structured Logging** | ❌ Limited | ✅ Full support |
| **Debug Mode** | ❌ Manual | ✅ Built-in toggle |
| **Multiple Outputs** | ❌ Complex setup | ✅ Easy configuration |

## 🚨 Migration Notes

- **Old**: `import logging` and `logging.getLogger()`
- **New**: `from .logging_config import get_logger`
- **Old**: `print("Debug info")`  
- **New**: `logger.info("Structured info")`
- **Old**: Manual file handling
- **New**: Automatic rotation and compression

## 📝 Best Practices

1. **Use descriptive logger names** that match your module structure
2. **Log at appropriate levels** - DEBUG for detailed info, INFO for general flow
3. **Use performance logging** for operations that might be slow
4. **Include context** with structured logging when helpful
5. **Log exceptions** with `logger.exception()` for full tracebacks
6. **Use debug mode** during development, normal mode in production

---

**Result**: Your debugging output is now structured, colored, and automatically organized into rotating log files! 🎯
