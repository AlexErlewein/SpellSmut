@echo off
REM Build Script for SpellForce Data Editor
REM Builds the application and copies the exe to the SpellforceDataEditor directory

setlocal enabledelayedexpansion

REM Get script directory
set "SCRIPT_DIR=%~dp0"
set "PROJECT_DIR=%SCRIPT_DIR%SpellforceDataEditor"
set "OUTPUT_DIR=%PROJECT_DIR%\bin\Release\net8.0-windows10.0.17763.0"
set "TARGET_DIR=%PROJECT_DIR%"

echo === SpellForce Data Editor Build Script ===
echo.
echo Project Directory: %PROJECT_DIR%
echo Output Directory: %OUTPUT_DIR%
echo Target Directory: %TARGET_DIR%
echo.

REM Check if dotnet is available
dotnet --version >nul 2>&1
if errorlevel 1 (
    echo X .NET SDK not found. Please install .NET 8.0 SDK.
    exit /b 1
)
for /f "tokens=*" %%v in ('dotnet --version') do set DOTNET_VERSION=%%v
echo √ Found dotnet SDK: %DOTNET_VERSION%
echo.

REM Restore packages
echo Restoring NuGet packages...
dotnet restore "SpellforceDataEditor.sln" --no-build 2>nul
if errorlevel 1 (
    echo X Package restore failed!
    exit /b 1
)
echo √ Packages restored
echo.

REM Build the project
echo Building Release configuration...
dotnet build "SpellforceDataEditor.sln" -c Release -p:Platform=x86 --no-restore
if errorlevel 1 (
    echo X Build failed!
    exit /b 1
)
echo √ Build completed successfully
echo.

REM Copy the exe to the target directory
set "EXE_SOURCE=%OUTPUT_DIR%\SpellforceDataEditor.exe"
set "EXE_TARGET=%TARGET_DIR%\SpellforceDataEditor.exe"

echo Copying exe to target directory...
if exist "%EXE_SOURCE%" (
    REM Remove old exe if exists
    if exist "%EXE_TARGET%" (
        del /F /Q "%EXE_TARGET%"
        echo   Removed old exe
    )

    REM Copy new exe
    copy /Y "%EXE_SOURCE%" "%EXE_TARGET%" >nul
    echo √ Copied SpellforceDataEditor.exe to: %TARGET_DIR%
) else (
    echo X exe not found at: %EXE_SOURCE%
    exit /b 1
)

REM Also copy required DLLs if they don't exist
echo.
echo Checking required dependencies...
set "REQUIRED_FILES=OpenTK.dll OpenTK.WinForms.dll NAudio.dll"

for %%f in (%REQUIRED_FILES%) do (
    set "SOURCE_FILE=%OUTPUT_DIR%\%%f"
    set "TARGET_FILE=%TARGET_DIR%\%%f"

    if not exist "!TARGET_FILE!" (
        if exist "!SOURCE_FILE!" (
            copy /Y "!SOURCE_FILE!" "!TARGET_FILE!" >nul
            echo   √ Copied %%f
        ) else (
            echo   ! Warning: %%f not found
        )
    )
)

echo.
echo === Build Complete! ===
echo You can now run the editor from: %EXE_TARGET%

endlocal
