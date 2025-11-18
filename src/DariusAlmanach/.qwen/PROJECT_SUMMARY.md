# Project Summary

## Overall Goal
Fix the Darius Almanach application to handle missing default CFF file gracefully by prompting the user to select a custom CFF file when the default one is not found at the expected path.

## Key Knowledge
- **Technology Stack**: PySide6 GUI application written in Python, part of the SpellSmut modding tools
- **Default Path**: Application looks for CFF file at `OriginalGameFiles/data/GameData.cff`
- **Architecture**: The application already had functionality to load custom CFF files via a "Load CFF File" button, but needed better handling for first-run scenarios when default file is missing
- **Build Command**: `uv run darius_almanach.py`
- **File Patterns**: CFF files are game data files containing quest information, typically named GameData.cff

## Recent Actions
### [COMPLETED] Core Implementation
- Modified the `load_data()` method to detect when the default CFF file doesn't exist
- Added a QMessageBox dialog to ask users if they want to select a CFF file manually when default is missing
- Implemented file selection functionality using QFileDialog when user chooses to select a file
- Maintained graceful exit option when user chooses not to select a file

### [COMPLETED] Testing
- Successfully tested the fix by temporarily renaming the default CFF file
- Verified that the application prompts the user when the default file is missing
- Confirmed that application loads successfully with user-selected CFF file
- Restored the original CFF file and verified normal operation continues to work

## Current Plan
All tasks are completed. The application now properly handles the scenario when the default GameData.cff file is not found by prompting the user to select a file manually. Users can now run the application even if the default CFF file doesn't exist at the expected location.

---

## Summary Metadata
**Update time**: 2025-11-18T09:06:42.144Z 
