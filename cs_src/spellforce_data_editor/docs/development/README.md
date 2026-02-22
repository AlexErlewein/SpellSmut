# Development Guide

Welcome to the SpellForce Data Editor development documentation. This guide is for contributors and developers who want to extend or improve the editor.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Development Environment Setup](#development-environment-setup)
3. [Building the Project](#building-the-project)
4. [Project Structure](#project-structure)
5. [Key Concepts](#key-concepts)
6. [Contributing Guidelines](#contributing-guidelines)
7. [Testing](#testing)
8. [Debugging](#debugging)

## Project Overview

The SpellForce Data Editor is a C# application built with:
- **.NET 8.0** - Latest .NET framework
- **WinForms** - UI framework
- **OpenTK 4.8.2** - OpenGL bindings for 3D rendering
- **NAudio 2.2.1** - Audio playback
- **Unsafe code** - Performance-critical binary parsing

### Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Core | C# / .NET 8.0 | Application logic |
| UI | WinForms | User interface |
| 3D Graphics | OpenTK / OpenGL | Map and model rendering |
| Audio | NAudio | Sound playback |
| Binary I/O | System.IO | File format parsing |

## Development Environment Setup

### Prerequisites

1. **Visual Studio 2022** (recommended) or VS Code
   - .NET desktop development workload
   - C# support

2. **.NET 8.0 SDK**
   ```
   winget install Microsoft.DotNet.SDK.8
   ```

3. **Git** (for cloning)

### Clone the Repository

```bash
git clone https://github.com/leszekd25/spellforce_data_editor.git
cd spellforce_data_editor
```

### Open in Visual Studio

1. Open `SpellforceDataEditor.sln`
2. Wait for NuGet packages to restore
3. Set `SpellforceDataEditor` as startup project

## Building the Project

### Debug Build

```bash
dotnet build --configuration Debug
```

### Release Build

```bash
dotnet build --configuration Release
```

### Build for x86 (Required for Game Compatibility)

The project targets x86 to match the original SpellForce games:

```bash
dotnet build -c Release -r win-x86
```

Output will be in `bin\x86\Release\net8.0-windows\`

## Project Structure

```
spellforce_data_editor/
├── SpellforceDataEditor/        # Main GUI application
│   ├── Program.cs               # Entry point
│   ├── MainForm.cs              # Main window
│   ├── SFCFF/                   # Game data editor UI
│   │   ├── category forms/      # Category-specific controls
│   │   └── helper_forms/        # Dialog windows
│   ├── SFMap/                   # Map editor UI
│   ├── SFLua/                   # Lua editor UI
│   └── special_forms/           # Editor windows
│
├── SFEngine/                    # Core engine library
│   ├── SFCFF/                   # GameData.cff system
│   │   ├── ICategory.cs         # Category interface
│   │   ├── CategoryBase.cs      # Base implementations
│   │   ├── SFCategoryManager.cs # High-level API
│   │   ├── SFGameDataNew.cs     # Container
│   │   └── CTG/                 # Category implementations
│   │       ├── Category2001.cs  # Army building requirements
│   │       ├── Category2002.cs  # Spells
│   │       └── ... (50+ categories)
│   │
│   ├── SFChunk/                 # Chunk file format
│   │   ├── SFChunkFile.cs       # File parser
│   │   └── SFChunkFileChunk.cs  # Chunk representation
│   │
│   ├── SFUnPak/                 # PAK archive system
│   │   ├── SFUnPak.cs           # PAK manager
│   │   ├── SFPakMap.cs          # File index
│   │   └── SFPakFileSystem.cs   # Virtual filesystem
│   │
│   ├── SFMap/                   # Map system
│   │   ├── SFMap.cs             # Map container
│   │   ├── SFMapHeightMap.cs    # Terrain
│   │   ├── SFMapUnitManager.cs  # Units
│   │   ├── SFMapBuildingManager.cs # Buildings
│   │   └── ... (other managers)
│   │
│   ├── SF3D/                    # 3D rendering
│   │   ├── SFRenderEngine.cs    # OpenGL renderer
│   │   ├── SFModel3D.cs         # Model loading
│   │   ├── SFTexture.cs         # Texture loading
│   │   └── SceneSynchro/        # Scene graph
│   │
│   ├── SFLua/                   # Lua system
│   │   ├── LuaDecompiler/       # Bytecode decompiler
│   │   ├── LuaParser/           # Source parser
│   │   ├── LuaTokenizer/        # Lexer
│   │   └── lua_sql/             # SQL interface
│   │
│   ├── SFResources/             # Resource management
│   │   ├── SFResourceManager.cs # Resource containers
│   │   └── SFResourceContainer.cs
│   │
│   ├── Utility.cs               # Utilities
│   ├── Settings.cs              # Configuration
│   └── LogUtils/                # Logging
│
└── MapViewerNetNative/          # Standalone map viewer
    ├── Program.cs
    └── MapViewerWindow.cs
```

## Key Concepts

### 1. Category System

The game data is organized into categories, each implementing `ICategory`:

```csharp
public interface ICategory
{
    string GetName();
    short GetCategoryID();
    int GetNumOfItems();
    bool Load(SFChunkFile file);
    bool Save(SFChunkFile file);
    // ... CRUD operations, search, undo/redo
}
```

**Base Classes**:
- `CategoryBaseSingle<T>` - For one-to-one ID mappings
- `CategoryBaseMultiple<T>` - For one-to-many ID mappings

### 2. Chunk File Format

All game files use a chunk-based binary format:

```
[File Header: 20 bytes]
├── Magic: 0xDD5E5E12
├── Format: varies
├── Type: 1 (map), 0 (gamedata)
├── Version: 0
└── Checksum: 0

[Chunks...]
├── ChunkID (e.g., 2002 for spells)
├── Occurrence ID
├── IsCompressed
├── DataType
├── DataSize
└── Data (raw struct array)
```

### 3. Resource Management

Resources are cached in `SFResourceManager`:

```csharp
SFResourceManager.Models.Get("mesh/unit/hero.msb");
SFResourceManager.Textures.Get("texture/terrain/grass.dds");
```

### 4. 3D Rendering

The 3D engine uses OpenGL via OpenTK:

```csharp
SFRenderEngine.scene.AddSceneNode(parent, mesh_name, node_name);
SFRenderEngine.Render();
```

### 5. Lua Decompilation

Lua 4.01 bytecode is decompiled using a custom decompiler:

```csharp
Decompiler decompiler = new Decompiler();
Chunk ast = decompiler.Decompile(luaFunction);
string source = ast.ToString();
```

## Contributing Guidelines

### Code Style

- Follow C# naming conventions
- Use `PascalCase` for public members
- Use `_camelCase` for private fields
- Add XML documentation for public APIs

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Commit Messages

Use clear commit messages:

```
feat: Add support for Category3000
fix: Correct heightmap scaling in map editor
docs: Update architecture documentation
```

## Testing

### Unit Tests

Currently, the project uses manual testing. Future plans include:

- Unit tests for category operations
- Integration tests for file I/O
- UI automation tests

### Manual Testing Checklist

Before submitting changes:

- [ ] Build succeeds in Debug and Release
- [ ] Can open GameData.cff
- [ ] Can load and save maps
- [ ] 3D rendering works correctly
- [ ] No memory leaks (check Task Manager)

## Debugging

### Debug Logging

The editor uses `LogUtils.Log` for logging:

```csharp
LogUtils.Log.Info(LogUtils.LogSource.SFCFF, "Message");
LogUtils.Log.Warning(LogUtils.LogSource.SFCFF, "Warning");
LogUtils.Log.Error(LogUtils.LogSource.SFCFF, "Error");
```

Logs are saved to `UserLog.txt`.

### Debugging GameData Loading

```csharp
LogUtils.Log.SetOption(LogOption.ALL);  // Enable all logs
// ... load gamedata
LogUtils.Log.SaveLog("debug_log.txt");
```

### Debugging 3D Rendering

For OpenGL issues, check:
1. GL version is 3.0+
2. Shaders compiled successfully
3. VBO/VAO creation succeeded

### Common Issues

**Problem**: Binary data doesn't load correctly

**Solution**: Check struct layout matches game format:
```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public struct MyItem
{
    public ushort ID;      // 2 bytes
    public uint Value;     // 4 bytes
    // Total must match game format exactly
}
```

**Problem**: Performance is slow

**Solution**: Profile and optimize:
- Use spans instead of copying
- Avoid boxing value types
- Use unsafe code for hot paths

## Adding Features

### Adding a New Category

1. Define the struct in `SFEngine/SFCFF/CTG/`:

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category3000Item : ICategoryItem
{
    public ushort ID;
    public uint Value;

    public int GetID() => ID;
    public void SetID(int id) => ID = (ushort)id;
}
```

2. Create the category class:

```csharp
public class Category3000 : CategoryBaseSingle<Category3000Item>
{
    public override string GetName() => "My Category";
    public override short GetCategoryID() => 3000;
    public override short GetCategoryType() => 2;
}
```

3. Add to `SFGameDataNew`:

```csharp
public class SFGameDataNew
{
    public Category3000 c3000 = new();

    public IEnumerable<ICategory> GetCategories()
    {
        // ... existing categories
        yield return c3000;
    }
}
```

4. Create UI control in `SpellforceDataEditor/SFCFF/category forms/`

### Adding a New Map Entity Type

1. Create manager class in `SFEngine/SFMap/`
2. Implement `SFMapEntityManager` pattern
3. Add to `SFMap` class
4. Create UI control

### Extending the 3D Engine

1. Add shader in `SFEngine/SF3D/SFRender/shaders/`
2. Update `SFRenderEngine` for new render pass
3. Add material properties to `SFMaterial`

## Performance Considerations

### Memory Usage

- Use structs (value types) for data items
- Avoid boxing/unboxing
- Use spans for zero-copy operations

### Load Times

- Use memory-mapped I/O where possible
- Lazy-load resources
- Cache frequently accessed data

### Rendering Performance

- Use VBOs/VAOs for geometry
- Minimize state changes
- Use frustum culling

## Next Steps

- [API Reference](api.md) - Core APIs and interfaces
- [Adding Features](adding-features.md) - Detailed extension guide
- [Architecture](../architecture/README.md) - Deep technical details

---

**Ready to contribute?** Check the [GitHub issues](https://github.com/leszekd25/spellforce_data_editor/issues) for open tasks.
