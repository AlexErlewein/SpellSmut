# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpellForce Data Editor is an all-in-one modding toolbox for SpellForce: Platinum Edition, a fantasy RTS/RPG hybrid game. The application is a Windows Forms application targeting .NET 8.0 that provides tools for editing game data files (CFF), viewing game assets (PAK files), editing SQL scripts, and map creation/editing.

## Build Commands

Build the solution (requires Visual Studio or .NET 8.0 SDK):
```bash
dotnet build "SpellforceDataEditor.sln" --configuration Release
```

Build individual projects:
```bash
# Build the engine library (must be built before SpellforceDataEditor)
dotnet build "SFEngine\SFEngine.csproj" --configuration Release

# Build the main editor application
dotnet build "SpellforceDataEditor\Spellforce Data Editor.csproj" --configuration Release

# Build the map viewer
dotnet build "MapViewerNetNative\MapViewerNetNative.csproj" --configuration Release
```

Run the application:
```bash
# From bin directory (preferred - contains required assets)
cd bin
.\SpellforceDataEditor.exe

# Or build and run directly
dotnet run --project "SpellforceDataEditor\Spellforce Data Editor.csproj"
```

**Important Notes:**
- The project uses `net8.0-windows10.0.17763.0` framework and requires Windows
- Platform target is x86 (32-bit) for compatibility with game files
- Unsafe code blocks are enabled in SFEngine for performance-critical operations
- The bin directory contains prebuilt executables and required dependencies (NAudio, OpenTK, SDL2.dll)

## Project Structure

The solution consists of three projects:

### 1. **SFEngine** (Core Library)
Engine library containing core functionality for reading/writing SpellForce game files. This is the foundation that other projects depend on.

**Key namespaces:**
- `SFEngine.SFCFF` - CFF (game data) file reading/writing, category management
  - `CTG` namespace contains 50+ category classes (Category2001-Category2072) representing different game data types (units, spells, items, text, etc.)
  - Categories are managed through `SFCategoryManager` and implement `ICategory` interface
- `SFEngine.SFUnPak` - PAK archive extraction and file system abstraction
  - `SFUnPak` - Main PAK manager that queries files from PAK archives or disk
  - `SFPakMap` - Maintains mapping of files within PAK archives
  - Uses `pakdata.dat` for cached PAK file structure
- `SFEngine.SFMap` - Map file (.map) loading/saving and manipulation
  - Core components: heightmap, terrain textures, units, buildings, objects, decorations, portals, lakes, weather, metadata
  - Each component has its own manager class (e.g., `SFMapUnitManager`, `SFMapBuildingManager`)
- `SFEngine.SF3D` - 3D rendering and scene management (OpenGL via OpenTK)
  - Rendering pipeline, physics, scene synchronization, UI
- `SFEngine.SFChunk` - Binary chunk file format reading/writing (maps use chunk format)
- `SFEngine.SFLua` - Lua script parsing, decompiling, tokenizing
  - Supports SQL script editing
- `SFEngine.SFResources` - Resource management for game assets
- `SFEngine.SFSound` - Audio playback (uses NAudio)

**Dependencies:** OpenTK (graphics), NAudio (audio), SDL2.dll (multimedia)

### 2. **SpellforceDataEditor** (Main Application)
WinForms application providing the editor UI. The main entry point initializes logging, loads settings, and handles the application lifecycle.

**Key directories:**
- `SFCFF/category forms/` - Control1-Control49 UserControls for editing different game data categories
  - Each Control corresponds to a category in SFEngine.SFCFF.CTG
  - Controls inherit from `SFControl` base class
- `SFLua/` - Lua script editing UI, SQL form editors
- `SFMap/` - Map editor UI components
  - `MapEdit/` - Core map editing functionality
  - `map_controls/` - Inspector panels for map entities (units, buildings, decorations, portals, etc.)
  - `map_dialog/` - Dialogs for map operations
  - `map_operators/` - Map manipulation operators (terrain, textures, placement)
- `special forms/` - Utility forms and dialogs

**Key files:**
- `MainForm.cs` - Main application window with tabbed interface for different editors
- `Program.cs` - Application entry point, initializes encoding providers and logging
- `config.txt` - Application configuration
- `pakdata.dat` - Cached PAK file structure (2.5MB binary file)

### 3. **MapViewerNetNative** (Standalone Map Viewer)
Standalone executable for viewing SpellForce maps with 3D rendering.

## Architecture Patterns

### CFF Game Data System
The game stores data in CFF files (Chunk File Format). Each category represents a different data type:
- Categories are numbered (2001-2072 with gaps)
- `SFGameDataNew` class contains all category instances as public fields
- Categories implement `ICategory` interface and inherit from `CategoryBase`
- Each category has a corresponding UserControl (Control1-Control49) for editing in the UI

**Data flow:**
1. User opens a `Gamedata.cff` file
2. `SFCategoryManager` parses the chunk file
3. Each chunk is deserialized into its corresponding Category class
4. UI displays appropriate Control for editing
5. On save, categories are serialized back to chunk format

### PAK File System
SpellForce uses PAK archives for assets (models, textures, sounds, animations):
- PAK files are numbered (sf1.pak, sf2.pak, etc.) with higher numbers taking priority
- `SFUnPak.SpecifyGameDirectory()` loads all PAK files from the game's `/pak` directory
- Files can be loaded from either PAK archives or loose files on disk (`FileSource` enum)
- `pakdata.dat` caches file locations to avoid re-scanning PAK files on each launch

**Resource loading priority:**
1. Loose files in game directory (if matching path)
2. PAK files in descending order (higher numbered PAKs override lower ones)

### Map Architecture
Maps use a chunk-based binary format (.map files):
- Chunk 2: Map size and heightmap tile data
- Chunk 3: Terrain texture definitions (255 tile types with blend weights)
- Additional chunks: units, buildings, decorations, metadata, etc.

**Map components are modular:**
- `SFMap` is the container holding references to all managers
- Each manager handles a specific entity type (units, buildings, etc.)
- Managers expose CRUD operations for their entities
- Coordinate system uses `SFCoord` for map positions

### Logging System
Centralized logging through `SFEngine.LogUtils.Log`:
- `LogSource` enum categorizes log messages by subsystem
- `LogOption` controls verbosity
- Logs are saved to `UserLog.txt` on application exit
- In Release builds, exceptions are caught and logged before exiting

## Working with Game Data

### Opening Game Files
The application requires:
1. A `Gamedata.cff` file to edit game data
2. Game directory path to access PAK files for asset viewing

The first time asset viewing is used, PAK files are scanned and `pakdata.dat` is generated (this takes time but only happens once).

### Editing Categories
When modifying category data:
- Find the appropriate Category class in `SFEngine/SFCFF/CTG/`
- The corresponding UI control is in `SpellforceDataEditor/SFCFF/category forms/`
- Categories contain structured data with fields representing game entities (units, spells, items, etc.)
- Text data is often multilingual (stored with language IDs)

### Map Editing
Map editor features:
- Heightmap editing (terrain elevation)
- Texture painting (terrain textures with blend modes)
- Entity placement (units, buildings, objects, decorations)
- Interactive objects (portals, monuments, bindstones, co-op camps)
- Metadata (map name, description, player count, etc.)

Inspector panels (`map_controls/`) provide per-entity editing when selected.

## Code Conventions

- **Naming:** Snake_case for many variables and properties (legacy C++ style)
- **Logging:** Always log significant operations with `LogUtils.Log.Info()` or `.Error()`
- **Error Handling:** Return integer error codes (0 = success, negative = error), log errors before returning
- **Resource Cleanup:** Dispose of unmanaged resources (BinaryReader, file streams) using `using` statements
- **Unsafe Code:** SFEngine uses unsafe blocks for performance; exercise caution when modifying
- **Threading:** UI operations must be on UI thread; long operations should report progress via delegates

## Dependencies and External Libraries

**NuGet Packages:**
- OpenTK 4.8.2 - OpenGL bindings for 3D rendering
- OpenTK.WinForms 4.0.0-pre.7 - WinForms integration
- NAudio 2.2.1 - Audio playback
- System.Text.Encoding.CodePages 8.0.0 - Required for legacy text encodings

**Native DLLs:**
- SDL2.dll - Multimedia library (must be in output directory)

**Asset Files:**
- `pakdata.dat` - Cached PAK file structure (generated from game files)
- `config.txt` - Application configuration

## Common Pitfalls

1. **Platform target mismatch:** All projects must build for x86, not AnyCPU
2. **Missing SDL2.dll:** Must be in the same directory as the executable
3. **PAK file loading:** First asset access is slow (scanning PAKs); subsequent launches use cached `pakdata.dat`
4. **Encoding issues:** Game uses legacy encodings; `CodePagesEncodingProvider` must be registered in `Program.Main()`
5. **Chunk file format:** Map and CFF files use custom chunk format; use `SFChunkFile` API, not raw file I/O
6. **Category numbering:** Not all category numbers exist (gaps in 2001-2072 range)
7. **Map coordinates:** Map uses grid coordinates, not world space; use `SFCoord` for conversions

## Debugging

Enable debug logging in `Program.Main()`:
```csharp
SFEngine.LogUtils.Log.SetOption(SFEngine.LogUtils.LogOption.ALL);
```

Logs are written to `UserLog.txt` in the application directory. Check this file when investigating issues.

In DEBUG builds, exceptions propagate to the debugger. In RELEASE builds, they're caught and logged.
