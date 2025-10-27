@echo off
REM Batch script to extract Audio assets using SpellforceDataEditor
REM
REM INSTRUCTIONS:
REM 1. This script will launch SpellforceDataEditor.exe
REM 2. Go to the "Asset Viewer" tab
REM 3. Wait for PAK files to load (may take 5-10 minutes on first run)
REM 4. Use the search box to filter audio files:
REM    - For music: type ".mp3"
REM    - For sounds: type ".wav"
REM    - For specific categories: use extraction lists as reference
REM 5. Select the assets you want to extract
REM 6. Right-click and choose "Extract" or use the Extract button
REM 7. Files will be extracted to: H:\SpellSmut\ExtractedAssets\Audio\extracted
REM
REM Audio Categories (see extraction_lists folder):
REM   Music:
REM     - music_menu.txt (~10 files) - Menu background music
REM     - music_battle.txt (~15 files) - Combat music
REM     - music_location.txt (~80 files) - Location themes
REM     - music_theme.txt (~10 files) - Main themes
REM
REM   Sound Effects:
REM     - ambient.txt (~15 files) - Environmental sounds
REM     - spell_cast.txt (~10 files) - Spell casting
REM     - spell_hit.txt (~100+ files) - Spell impacts
REM     - battle_npc.txt (~200+ files) - Creature combat
REM     - battle_hit.txt (~80 files) - Weapon sounds
REM     - work_build.txt (~15 files) - Construction
REM     - work_gather.txt (~40 files) - Resource gathering
REM     - and many more...
REM
REM Total Audio Files: 1000-1150+ files
REM
REM You can use the extraction lists as a reference for which files to extract.

echo.
echo ===============================================================
echo  SpellForce Audio Asset Extraction Tool
echo ===============================================================
echo.
echo Starting SpellforceDataEditor...
echo.

cd /d "%~dp0..\..\ModdingTools\spellforce_data_editor\bin"

REM Set extract directory in config
echo Updating config.txt with audio extract directory...
powershell -Command "(Get-Content config.txt) -replace '^ExtractDirectory.*', 'ExtractDirectory H:\SpellSmut\ExtractedAssets\Audio\extracted' | Set-Content config.txt"

echo.
echo Config updated. Launching editor...
echo.

REM Start the editor
start SpellforceDataEditor.exe

echo.
echo ===============================================================
echo  SpellforceDataEditor is starting...
echo ===============================================================
echo.
echo EXTRACTION TIPS:
echo   1. Use Asset Viewer tab
echo   2. Filter by extension (.mp3 or .wav)
echo   3. Sort by name to find specific categories
echo   4. Extract in batches to avoid overwhelming the tool
echo   5. Check extraction_lists folder for categorized file lists
echo.
echo PRIORITY EXTRACTIONS:
echo   - Music tracks (all .mp3 files) - ~130 files
echo   - Combat sounds (battle_*.wav) - ~400 files
echo   - Spell effects (spell_*.wav) - ~150 files
echo   - Work sounds (work_*.wav) - ~60 files
echo.
echo Output directory: H:\SpellSmut\ExtractedAssets\Audio\extracted
echo.
echo ===============================================================
pause
