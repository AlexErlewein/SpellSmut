# Build Instructions

## Quick Build

### Windows (PowerShell)
```powershell
.\build.ps1
```

### Windows (Batch)
```batch
build.bat
```

### Windows (Git Bash / WSL)
```bash
./build.sh
```

## What the Build Script Does

1. **Checks for .NET SDK** - Verifies .NET 8.0 SDK is installed
2. **Restores packages** - Downloads required NuGet packages
3. **Builds Release configuration** - Compiles the application for x86
4. **Copies exe to SpellforceDataEditor directory** - Places `SpellforceDataEditor.exe` in the main directory
5. **Copies dependencies** - Ensures required DLLs are present

## Build Output

After building, the executable will be at:
```
cs_src\spellforce_data_editor\SpellforceDataEditor\SpellforceDataEditor.exe
```

## Manual Build

If you prefer to build manually:

```bash
# From the cs_src\spellforce_data_editor directory
dotnet restore "Spellforce Data Editor.sln"
dotnet build "Spellforce Data Editor.sln" -c Release -p:Platform=x86

# Copy the exe manually
copy "SpellforceDataEditor\bin\Release\net8.0-windows\SpellforceDataEditor.exe" "SpellforceDataEditor\"
```

## Requirements

- .NET 8.0 SDK (for Windows)
- Windows 10/11 (x86)

## Icon

The application icon is embedded from `382940043477778432.ico` and is configured in the project file:
```xml
<ApplicationIcon>382940043477778432.ico</ApplicationIcon>
```

## Troubleshooting

### Build fails with "SDK not found"
Install the .NET 8.0 SDK from: https://dotnet.microsoft.com/download/dotnet/8.0

### Build fails with "Platform target mismatch"
Make sure you're building for x86 platform (required for game compatibility)

### exe doesn't have icon
The icon is embedded during compilation. If the exe doesn't show the icon:
1. Verify `382940043477778432.ico` exists in `SpellforceDataEditor` directory
2. Clean and rebuild:
   ```bash
   dotnet clean "Spellforce Data Editor.sln"
   dotnet build "Spellforce Data Editor.sln" -c Release -p:Platform=x86
   ```
