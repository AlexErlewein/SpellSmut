@echo off
REM Batch launcher for PAK bulk extraction
REM This script runs the Python bulk extractor

echo.
echo ===============================================================
echo  SpellForce PAK Bulk Extractor
echo  Using QuickBMS Automation
echo ===============================================================
echo.
echo This script will:
echo   1. Download QuickBMS if not present
echo   2. Extract all 23 PAK files (~3.2 GB)
echo   3. Organize files into categories (Audio, UI, Textures, etc.)
echo.
echo Estimated time: 15-30 minutes depending on your system
echo Disk space required: ~6-8 GB
echo.
echo ===============================================================
pause

cd /d "%~dp0..\..\"

python src\helper_tools\bulk_extract_paks.py

echo.
echo ===============================================================
pause
