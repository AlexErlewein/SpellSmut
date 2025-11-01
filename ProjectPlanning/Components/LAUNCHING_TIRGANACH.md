# Launching Tirganach GUI Editor

## Quick Start ✅

**The GUI is now working!** Simply run:

```bash
uv run tirganach
```

The GUI window will appear on your screen. Initial loading takes ~5-7 seconds while it loads icon data.

### Alternative: Launch in new terminal window
```bash
./launch_tirganach.sh
```
This opens the GUI in a separate terminal window.

## What to Expect

When you run `uv run tirganach`, you'll see:
1. Loading icon mapping data (~6200 items)
2. Building handle-to-path mapping
3. Loading icon index (~4200 icons)
4. "MainWindow initialization complete"
5. GUI window appears!

**Note**: The terminal will show logs while the GUI window runs in the background. This is normal behavior.

## Troubleshooting

### GUI doesn't appear after logs stop
- Check if the window is hidden behind other windows
- Look for the "SpellForce CFF Editor" window in your dock/taskbar
- The process should show "Starting Qt event loop" as the last log message

### Import errors
If you see `ModuleNotFoundError: No module named 'TirganachReloaded'`:
```bash
uv sync --reinstall-package tirganachreloaded
```

### NameError: name 'sys' is not defined
This has been fixed. If you still see it, make sure you have the latest code.

## What was fixed

1. **Added script entry point** in `pyproject.toml`:
   - `tirganach` command now available via `uv run`

2. **Fixed import statements**:
   - Changed `from tirganach.` to `from TirganachReloaded.tirganach.`
   - Updated in: `main_window.py`, `data_model.py`, `data_providers.py`

3. **Fixed missing import** in `lua_data_manager.py`:
   - Added `import sys` (was causing NameError)

4. **Created launcher script**:
   - `launch_tirganach.sh` opens GUI in new terminal window
   - Useful if you want to separate the GUI from your current terminal

## Stopping the GUI

- Close the window normally using the close button
- Or press `Ctrl+C` in the terminal where you launched it
