# Reload Cache Crash Fix

## Problem Description

When attempting to reload the CFF file to refresh the cache in TirganachReloaded, the program would quit unexpectedly. This was caused by a **Qt threading violation**.

## Root Cause

The issue was located in `src/TirganachReloaded/cff_editor/main_window.py` in the `reload_and_rebuild_cache()` method.

### The Threading Violation

```python
def rebuild_operation(progress_callback=None, step_callback=None):
    """Background operation to rebuild cache"""
    # ... parsing code ...
    
    success = self.data_model.load_file(self.data_model.file_path, force_parse=True)
    
    if success:
        # ⚠️ CRITICAL BUG: Calling UI methods from worker thread!
        self.refresh_view()  # This runs in the background thread
        
    return success
```

**The Problem:**
- The `rebuild_operation` function runs in a **background worker thread** (via `WorkerThread`)
- Inside this function, `self.refresh_view()` was being called
- `refresh_view()` updates GUI widgets (category tree, element table, property editor, etc.)
- **Qt rule:** All GUI operations MUST happen on the main thread
- Calling GUI methods from a worker thread causes undefined behavior:
  - Program crashes
  - Program quits unexpectedly
  - UI freezes
  - Data corruption

## The Solution

The fix involved two changes:

### 1. Remove UI Refresh from Worker Thread

Remove the `refresh_view()` call from the background operation:

```python
def rebuild_operation(progress_callback=None, step_callback=None):
    """Background operation to rebuild cache"""
    if step_callback:
        step_callback("Parsing CFF file")
    if progress_callback:
        progress_callback(10, "Parsing CFF file...")

    success = self.data_model.load_file(
        self.data_model.file_path, force_parse=True
    )

    if success:
        if progress_callback:
            progress_callback(100, "Cache rebuilt successfully")
    else:
        raise Exception("Failed to rebuild cache")

    return success
```

### 2. Add Completion Handler in Main Thread

Connect a completion handler that runs in the main thread:

```python
# Create progress dialog
progress_dialog = ProgressDialog(
    "Rebuilding Cache",
    f"Rebuilding cache for {self.data_model.file_path}",
    self,
)

# Create worker thread first (without starting it)
progress_dialog.worker_thread = progress_dialog._create_worker(
    rebuild_operation
)

# Connect completion handler to refresh UI in main thread
def on_rebuild_complete(result):
    """Called in main thread when rebuild completes"""
    if result:
        # Now safely refresh UI in main thread
        self.refresh_view()
        self.on_data_loaded()

progress_dialog.worker_thread.operation_completed.connect(on_rebuild_complete)

# Now start the operation
progress_dialog._start_worker()
```

### 3. Enhanced ProgressDialog

Modified `ProgressDialog` to support custom signal connections before starting:

```python
def _create_worker(self, operation_func: Callable, *args, **kwargs):
    """Create worker thread without starting it (for custom signal connections)"""
    worker = WorkerThread(operation_func, *args, **kwargs)
    
    # Connect default signals
    worker.progress_updated.connect(self.on_progress_updated)
    worker.step_started.connect(self.on_step_started)
    worker.operation_completed.connect(self.on_operation_completed)
    worker.operation_failed.connect(self.on_operation_failed)
    
    return worker

def _start_worker(self):
    """Start the worker thread and show dialog"""
    if self.worker_thread:
        self.worker_thread.start()
        self.exec()
```

## How It Works Now

1. **Background Thread:** Parses the CFF file and rebuilds the cache
2. **Signal Emission:** When complete, the worker thread emits `operation_completed` signal
3. **Main Thread Handler:** Qt's signal system ensures the `on_rebuild_complete` handler runs on the main thread
4. **Safe UI Update:** `refresh_view()` is called from the main thread, updating the UI safely

## Thread Safety in Qt

### Key Rules:
1. ✅ **DO:** Perform heavy computation in worker threads
2. ✅ **DO:** Emit signals from worker threads
3. ✅ **DO:** Update GUI from signal handlers (Qt routes them to main thread)
4. ❌ **DON'T:** Call GUI methods directly from worker threads
5. ❌ **DON'T:** Access QWidget objects from non-main threads

### Qt's Signal-Slot Threading

Qt's signal-slot mechanism is thread-safe because:
- When a signal is emitted from a worker thread
- And connected to a slot in a main thread object
- Qt automatically queues the signal
- And executes the slot on the main thread

This is why our fix works: `operation_completed.connect(on_rebuild_complete)` ensures `on_rebuild_complete` runs on the main thread, even though the signal was emitted from the worker thread.

## Testing the Fix

To verify the fix works:

1. Open TirganachReloaded
2. Load a GameData.cff file
3. Go to **Tools → Reload and Rebuild Cache**
4. The progress dialog should appear
5. The cache should rebuild without crashing
6. The UI should refresh properly after completion
7. The program should remain running

## Related Files Modified

- `src/TirganachReloaded/cff_editor/main_window.py` - Fixed threading violation
- `src/TirganachReloaded/cff_editor/widgets/progress_dialog.py` - Added worker creation methods

## Lessons Learned

1. **Always respect Qt's threading model** - GUI operations on main thread only
2. **Use signals for thread communication** - Let Qt handle the thread synchronization
3. **Test background operations thoroughly** - Threading bugs can be intermittent
4. **Comment misleading code** - The comment said "in main thread" but wasn't actually
5. **Separate worker creation from execution** - Allows for custom signal connections

## References

- [Qt Thread Basics](https://doc.qt.io/qt-6/thread-basics.html)
- [Qt Threads and QObjects](https://doc.qt.io/qt-6/threads-qobject.html)
- [Signals and Slots Across Threads](https://doc.qt.io/qt-6/threads-qobject.html#signals-and-slots-across-threads)