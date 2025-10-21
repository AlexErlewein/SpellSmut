@echo off
REM DDS to PNG Converter - Batch Script for Windows
REM Converts all DDS files in ExtractedAssets/Textures to PNG format

echo ============================================
echo DDS to PNG Converter
echo ============================================
echo.

REM Change to the repository root directory
cd /d "%~dp0..\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.7 or higher
    pause
    exit /b 1
)

echo Checking dependencies...
python -c "import PIL" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Pillow library not found. Installing...
    pip install Pillow
    if errorlevel 1 (
        echo ERROR: Failed to install Pillow
        pause
        exit /b 1
    )
)

echo.
echo Select conversion mode:
echo 1. Convert all DDS files in ExtractedAssets/Textures
echo 2. Convert specific directory (you will be prompted)
echo 3. Convert single file (you will be prompted)
echo.

set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo Converting all DDS files in ExtractedAssets/Textures...
    echo Output will be saved to: ExtractedAssets/Textures_png
    echo.
    python src/helper_tools/convert_dds_to_png.py ExtractedAssets/Textures ExtractedAssets/Textures_png
) else if "%choice%"=="2" (
    echo.
    set /p input_dir="Enter input directory path: "
    set /p output_dir="Enter output directory path (or press Enter for auto): "
    if "!output_dir!"=="" (
        python src/helper_tools/convert_dds_to_png.py "!input_dir!"
    ) else (
        python src/helper_tools/convert_dds_to_png.py "!input_dir!" "!output_dir!"
    )
) else if "%choice%"=="3" (
    echo.
    set /p input_file="Enter DDS file path: "
    python src/helper_tools/convert_dds_to_png.py "!input_file!"
) else (
    echo Invalid choice
    pause
    exit /b 1
)

echo.
echo ============================================
echo Conversion complete!
echo ============================================
pause
