"""Performance and utility functions following C# SFEngine patterns"""

import logging
import time
from functools import wraps
from typing import Callable, Dict


def performance_timer(func: Callable) -> Callable:
    """
    Decorator to time function execution following C# performance tracking patterns.

    Args:
        func: Function to time

    Returns:
        Function wrapper that logs execution time
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time

        logger = logging.getLogger(func.__module__)
        logger.debug(f"{func.__name__} executed in {execution_time:.4f}s")

        return result

    return wrapper


def cache_result(ttl: int = 300):
    """
    Decorator to cache function results following C# caching patterns.

    Args:
        ttl: Time-to-live in seconds for cached results

    Returns:
        Function wrapper that provides caching
    """

    def decorator(func: Callable) -> Callable:
        cache: Dict[str, tuple] = {}  # Cache: {key: (result, timestamp)}

        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from arguments
            key = str(args) + str(sorted(kwargs.items()))
            current_time = time.time()

            # Check if result is in cache and still valid
            if key in cache:
                result, timestamp = cache[key]
                if current_time - timestamp < ttl:
                    logger = logging.getLogger(func.__module__)
                    logger.debug(f"Cache hit for {func.__name__}")
                    return result

            # Execute function and cache result
            result = func(*args, **kwargs)
            cache[key] = (result, current_time)

            return result

        return wrapper

    return decorator


def measure_memory_usage(func: Callable) -> Callable:
    """
    Decorator to measure approximate memory usage of function execution.
    Note: This is a simplified version as full memory profiling would require additional libraries.

    Args:
        func: Function to measure

    Returns:
        Function wrapper that logs memory information
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        # In a more sophisticated implementation, we might use tracemalloc
        # or other memory profiling tools here
        logger = logging.getLogger(func.__module__)
        logger.debug(f"Executing {func.__name__} (memory measurement placeholder)")

        result = func(*args, **kwargs)
        return result

    return wrapper


def batch_process(items: list, batch_size: int = 100) -> list:
    """
    Process a large list in batches following C# collection processing patterns.

    Args:
        items: List of items to process
        batch_size: Number of items to process at once

    Returns:
        List of results from processing
    """
    logger = logging.getLogger(__name__)
    results = []

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        logger.debug(
            f"Processing batch {i // batch_size + 1}/{(len(items) - 1) // batch_size + 1}"
        )

        # Process the batch - in a real implementation this would be more complex
        batch_results = [item for item in batch]  # Placeholder processing
        results.extend(batch_results)

    logger.info(f"Processed {len(items)} items in batches")
    return results


class PerformanceMonitor:
    """
    Class for monitoring performance metrics following C# SFEngine patterns.
    """

    def __init__(self):
        self._timings: Dict[str, list] = {}
        self._logger = logging.getLogger(self.__class__.__name__)

    def start_timer(self, operation_name: str):
        """Start timing an operation."""
        self._timings[operation_name] = [time.perf_counter()]

    def stop_timer(self, operation_name: str) -> float:
        """Stop timing an operation and return elapsed time."""
        if operation_name in self._timings:
            start_time = self._timings[operation_name][0]
            end_time = time.perf_counter()
            elapsed = end_time - start_time

            # Store timing for potential averaging
            if len(self._timings[operation_name]) == 1:
                self._timings[operation_name].append(elapsed)
            else:
                # Update the last timing
                self._timings[operation_name][1] = elapsed

            self._logger.debug(f"{operation_name} took {elapsed:.4f}s")
            return elapsed
        else:
            self._logger.warning(f"No timer started for {operation_name}")
            return 0.0

    def get_average_time(self, operation_name: str) -> float:
        """Get average time for an operation."""
        if operation_name in self._timings and len(self._timings[operation_name]) > 1:
            return self._timings[operation_name][1]
        return 0.0


# Global performance monitor instance
perf_monitor = PerformanceMonitor()
