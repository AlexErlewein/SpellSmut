# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SpellForce Data Editor is a comprehensive all-in-one modding toolbox for SpellForce: The Order of Dawn. It provides GUI-based editing capabilities for game data, assets, maps, and scripts. The project consists of three main C# projects targeting .NET 8.0 Windows.

## Build and Development Commands

**Building the entire solution:**
```bash
dotnet build SpellforceDataEditor.sln
```

**Building specific projects:**
```bash
# Build the main editor application
dotnet build SpellforceDataEditor/Spellforce\ Data\ Editor.csproj

# Build the core engine library
dotnet build SFEngine/SFEngine.csproj

# Build the standalone map viewer
dotnet build MapViewerNetNative/MapViewerNetNative.csproj
```

**Running the application:**
```bash
# Run from solution directory
dotnet run --project SpellforceDataEditor/Spellforce\ Data\ Editor.csproj

# Or run from the compiled binary
.\SpellforceDataEditor\bin\Debug\net8.0-windows10.0.17763.0\SpellforceDataEditor.exe
```

**Platform and configuration notes:**
- All projects target `net8.0-windows10.0.17763.0`
- Platform target is `x86` (32-bit) to match the original SpellForce game
- Both Debug and Release configurations support `Any CPU` and `x86` platforms
- SFEngine requires `AllowUnsafeBlocks=true` for low-level memory operations

## Project Architecture

The solution consists of three interconnected projects:

### 1. SFEngine (Library)
Core engine library providing all file format parsing, rendering, and game logic manipulation.

**Key subsystems:**
- **SFCFF**: GameData.cff file parsing and manipulation
  - `SFGameDataNew.cs`: Main class representing the entire GameData.cff file
  - `CTG/Category*.cs`: 66+ category classes, each handling a specific data table (spells, units, items, buildings, etc.)
  - `SFCategoryManager.cs`: Manages all categories and their relationships

- **SFMap**: Map file loading, editing, and rendering
  - `SFMap.cs`: Main map class coordinating all map subsystems
  - Manager classes: `SFMapBuildingManager`, `SFMapUnitManager`, `SFMapObjectManager`, etc.
  - `SFMapHeightMap.cs`: Terrain elevation and geometry
  - `SFMapTerrainTextureManager.cs`: Texture blending and material properties

- **SF3D**: 3D rendering engine built on OpenTK
  - `SFRender/`: OpenGL rendering pipeline, shaders, framebuffers
  - `SceneSynchro/`: Scene graph, node hierarchy, effects management
  - `Physics/`: Collision detection primitives (AABB, frustum culling, raycasting)
  - Model/animation classes: `SFModel3D`, `SFModelSkin`, `SFAnimation`, `SFSkeleton`

- **SFLua**: Lua script parsing and decompilation
  - `LuaDecompiler/`: Converts Lua bytecode to readable source
  - `LuaParser/`: AST parsing for Lua scripts
  - `LuaTokenizer/`: Tokenization for Lua 4.01 (used by SpellForce)
  - `lua_sql/`: SQL-like data structures used in game scripts

- **SFUnPak**: PAK archive extraction and file system
  - `SFUnPak.cs`: Unpacks game's .pak archives
  - `SFPakFileSystem.cs`: Virtual file system for accessing pak contents

- **SFChunk**: Chunk-based file format parsing
  - Used for map files and other chunked SpellForce formats

- **SFResources**: Generic resource management system
- **SFSound**: Audio engine using NAudio

### 2. SpellforceDataEditor (WinForms Application)
Main GUI application providing user-facing editing tools.

**Key features:**
- **GameData Editor**: Browse and edit all 66+ categories in GameData.cff files
  - `SFCFF/category forms/Control*.cs`: 49 custom UI controls, one per editable category
  - Each control handles display and editing for a specific game data table

- **Asset Viewer**: Preview 3D models, animations, sounds, and textures from PAK files
- **SQL Editor**: Edit SQL-like scripts embedded in Lua
- **Map Editor**: Full-featured map creation and editing
  - `SFMap/map_controls/`: Inspector panels for different entity types (units, buildings, bindstones, etc.)
  - `SFMap/map_operators/`: Undo/redo system using the Command pattern
  - `MapOperator.cs`: Defines `IMapOperator` interface and operator clustering

- `MainForm.cs`: Main application window that coordinates all sub-editors

**Map editor operator pattern:**
The map editor uses a sophisticated undo/redo system based on operators. Each editing action creates an `IMapOperator` that stores the before/after state and implements `Apply()` and `Revert()` methods. Operators can be clustered using `MapOperatorCluster` to group related changes.

### 3. MapViewerNetNative (Standalone Console App)
Lightweight standalone map viewer for quick map inspection without the full editor.

## Dependencies

**NuGet packages used across projects:**
- `OpenTK` (4.8.2): OpenGL rendering
- `OpenTK.WinForms` (4.0.0-pre.7): WinForms OpenGL integration (SpellforceDataEditor only)
- `NAudio` (2.2.1): Audio playback
- `System.Text.Encoding.CodePages` (8.0.0): Required for Windows-1252 encoding used in game files

**Native dependencies:**
- `SDL2.dll`: Included in SFEngine, copied to output directory

## Key File Formats

**GameData.cff:**
- Binary relational database with 66+ tables
- Little-endian encoding, Windows-1252 strings
- 20-byte header + 12-byte table headers
- Categories represent: spells, units, items, buildings, skills, localisation, etc.

**Map files (.map):**
- Chunk-based format using `SFChunkFile`
- Chunk IDs: 2 (size/tiles), 3 (tile definitions), 4 (textures), 6 (heightmap rows)
- Contains heightmap, entities, metadata, weather, lakes, portals

**PAK files:**
- Compressed archives containing game assets
- Assets include: 3D models (.msb), textures (.tga), sounds, animations

**Lua scripts:**
- Lua 4.01 bytecode (older version used by SpellForce)
- Tokenizer in `SFLua/LuaTokenizer` handles version-specific syntax

## Development Notes

**Encoding:**
All SpellForce text uses Windows-1252 encoding. Register the encoding provider at startup:
```csharp
System.Text.Encoding.RegisterProvider(System.Text.CodePagesEncodingProvider.Instance);
```

**Unsafe code:**
SFEngine uses unsafe code blocks for performance-critical operations (mesh data, texture processing). Be cautious when modifying code in methods marked `unsafe`.

**Platform target:**
The x86 (32-bit) platform target is required because the original SpellForce game and its DLLs are 32-bit. Do not change this to AnyCPU or x64.

**GameData category numbering:**
Category class names use numeric IDs (e.g., `Category2002`, `Category2054`) that correspond to internal table IDs in the CFF format. These numbers are not sequential and match the original game's table structure.

**Map coordinate system:**
- Maps use a tile-based coordinate system with `SFCoord` (x, y)
- Heightmap resolution is (size+1) × (size+1) vertices for a size × size tile grid
- 3D coordinates use OpenTK's `Vector3` with Y-up convention

**Resource management:**
The `SFResourceManager` requires game directory specification before accessing PAK files. Check `SFUnPak.game_directory_specified` before attempting asset operations.
