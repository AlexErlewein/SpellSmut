@echo off
REM Batch script to run the complete UI icon integration pipeline
REM This script should be run on Windows where SpellForce is installed
REM
REM Pipeline:
REM 1. Extract UI assets with original names
REM 2. Convert DDS to PNG
REM 3. Rotate PNGs by 180 degrees
REM 4. Organize by category
REM
REM Requirements:
REM - Python 3 installed
REM - ImageMagick installed (for DDS conversion)
REM - Pillow installed (for PNG rotation)
REM - SpellForce game installed

echo ========================================
echo SpellForce UI Icon Integration Pipeline
echo ========================================
echo.

REM Check if we're in the right directory
if not exist "extract_ui_with_names.py" (
    echo ERROR: Please run this script from the src/helper_tools directory
    pause
    exit /b 1
)

echo Step 1: Extracting UI assets with original filenames...
echo.
python extract_ui_with_names.py
if errorlevel 1 (
    echo ERROR: UI asset extraction failed
    pause
    exit /b 1
)
echo.
echo Step 1 completed successfully.
echo.

echo Step 2: Converting DDS files to PNG...
echo.
python convert_ui_textures.py
if errorlevel 1 (
    echo ERROR: DDS to PNG conversion failed
    pause
    exit /b 1
)
echo.
echo Step 2 completed successfully.
echo.

echo Step 3: Rotating PNGs by 180 degrees...
echo.
python rotate_ui_pngs.py
if errorlevel 1 (
    echo ERROR: PNG rotation failed
    pause
    exit /b 1
)
echo.
echo Step 3 completed successfully.
echo.

echo Step 4: Organizing assets by category...
echo.
python organize_ui_assets.py
if errorlevel 1 (
    echo ERROR: Asset organization failed
    pause
    exit /b 1
)
echo.
echo Step 4 completed successfully.
echo.

echo ========================================
echo UI ICON INTEGRATION COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Copy the extracted assets to your project
echo 2. Run the GUI editor to test icon display
echo 3. Verify icons appear in both table and property editor
echo.
echo Extracted assets location:
echo   ExtractedAssets\UI\extracted\
echo.
echo Fallback icons location:
echo   ExtractedAssets\UI\fallback_icons\
echo.

pause