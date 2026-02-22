@echo off
REM Build script for Spellforce Data Editor
REM This script builds the application and moves the executable to the SpellforceDataEditor directory

setlocal EnableDelayedExpansion

REM Set directories
set SOLUTION_DIR=%~dp0
set PROJECT_DIR=%SOLUTION_DIR%SpellforceDataEditor
set OUTPUT_DIR=%PROJECT_DIR%\bin\Release\net8.0-windows10.0.17763.0
set TARGET_DIR=%PROJECT_DIR%

echo ========================================
echo Building Spellforce Data Editor
echo ========================================
echo.

REM Build the solution in Release mode
echo Building solution...
dotnet build "%SOLUTION_DIR%SpellforceDataEditor.sln" -c Release -p:Platform=x86

if %ERRORLEVEL% neq 0 (
    echo.
    echo Build failed with error code %ERRORLEVEL%
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ========================================
echo Build successful!
echo ========================================
echo.

REM Create target directory if it doesn't exist
if not exist "%TARGET_DIR%" mkdir "%TARGET_DIR%"

REM Copy executable and dependencies
echo Copying files to %TARGET_DIR%...

REM Copy main executable
copy /Y "%OUTPUT_DIR%\SpellforceDataEditor.exe" "%TARGET_DIR%\" >nul
if %ERRORLEVEL% neq 0 (
    echo Failed to copy SpellforceDataEditor.exe
    pause
    exit /b 1
)

REM Copy required DLLs
copy /Y "%OUTPUT_DIR%\SDL2.dll" "%TARGET_DIR%\" >nul 2>&1
copy /Y "%OUTPUT_DIR%\SFEngine.dll" "%TARGET_DIR%\" >nul 2>&1
copy /Y "%OUTPUT_DIR%\SpellforceDataEditor.dll" "%TARGET_DIR%\" >nul 2>&1

REM Copy OpenTK DLLs
for %%f in ("%OUTPUT_DIR%\OpenTK*.dll") do copy /Y "%%f" "%TARGET_DIR%\" >nul 2>&1

REM Copy NAudio DLLs
for %%f in ("%OUTPUT_DIR%\NAudio*.dll") do copy /Y "%%f" "%TARGET_DIR%\" >nul 2>&1

REM Copy Windows SDK DLL
copy /Y "%OUTPUT_DIR%\Microsoft.Windows.SDK.NET.dll" "%TARGET_DIR%\" >nul 2>&1
copy /Y "%OUTPUT_DIR%\WinRT.Runtime.dll" "%TARGET_DIR%\" >nul 2>&1

REM Copy config files
copy /Y "%OUTPUT_DIR%\SpellforceDataEditor.dll.config" "%TARGET_DIR%\" >nul 2>&1
copy /Y "%OUTPUT_DIR%\SpellforceDataEditor.runtimeconfig.json" "%TARGET_DIR%\" >nul 2>&1
copy /Y "%OUTPUT_DIR%\SpellforceDataEditor.deps.json" "%TARGET_DIR%\" >nul 2>&1

REM Copy runtimes directory if it exists
if exist "%OUTPUT_DIR%\runtimes" (
    xcopy /E /I /Y "%OUTPUT_DIR%\runtimes" "%TARGET_DIR%\runtimes" >nul 2>&1
)

REM Copy OpenTK config files
copy /Y "%PROJECT_DIR%\OpenTK.dll.config" "%TARGET_DIR%\" >nul 2>&1

echo.
echo ========================================
echo Build and deployment complete!
echo ========================================
echo.
echo Executable location: %TARGET_DIR%\SpellforceDataEditor.exe
echo.

pause
