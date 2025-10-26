@echo off
REM Batch script to extract UI assets using SpellforceDataEditor
REM
REM INSTRUCTIONS:
REM 1. Open SpellforceDataEditor.exe
REM 2. Go to the "Asset Viewer" tab
REM 3. Wait for PAK files to load (may take a few minutes on first run)
REM 4. In the search box, type "ui_" to filter UI assets
REM 5. Select the assets you want to extract
REM 6. Right-click and choose "Extract" or use the Extract button
REM 7. Files will be extracted to the directory specified in config.txt
REM
REM The following files are categorized in the extraction_lists folder:
REM   - backgrounds.txt (254 files)
REM   - buttons.txt (61 files)
REM   - items.txt (98 files)
REM   - cursors.txt (28 files)
REM   - spells.txt (18 files)
REM   - mainmenu.txt (78 files)
REM   - and more...
REM
REM You can use these lists as a reference for which files to extract.

echo Starting SpellforceDataEditor...
cd /d "%~dp0..\..\ModdingTools\spellforce_data_editor\bin"

REM Set extract directory in config
echo Updating config.txt with extract directory...
powershell -Command "(Get-Content config.txt) -replace '^ExtractDirectory.*', 'ExtractDirectory H:\SpellSmut\ExtractedAssets\UI\extracted' | Set-Content config.txt"

REM Start the editor
start SpellforceDataEditor.exe

echo.
echo SpellforceDataEditor is starting...
echo Please follow the instructions above to extract UI assets.
echo.
pause
