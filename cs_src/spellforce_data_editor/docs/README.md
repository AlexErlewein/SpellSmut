# SpellForce Data Editor Documentation

Welcome to the comprehensive documentation for the SpellForce Data Editor. This toolset enables modding and content creation for SpellForce games.

## Documentation Index

### For Modders & Users
New to modding? Start here:
- [Getting Started Guide](user/README.md) - Installation and first steps
- [Game Data Editor](user/gamedata-editor.md) - Editing game database
- [Map Editor Guide](user/map-editor.md) - Creating and editing maps
- [Asset Management](user/assets.md) - Working with game assets
- [Script Editing](user/scripts.md) - Decompiling and editing Lua scripts

### For Developers
Want to contribute or extend the editor?
- [Development Guide](development/README.md) - Setup and contribution
- [Architecture Overview](architecture/README.md) - System architecture
- [API Reference](development/api.md) - Core APIs and interfaces
- [Adding Features](development/adding-features.md) - Extending the editor

### Technical Documentation
Deep technical details:
- [File Formats](formats/README.md) - Game file format specifications
- [Chunk Format](formats/chunk-format.md) - Binary chunk format details
- [Category System](architecture/categories.md) - GameData.cff category system
- [3D Rendering](architecture/3d-engine.md) - OpenGL rendering pipeline
- [Lua Decompiler](architecture/lua-system.md) - Lua bytecode decompilation

## Quick Reference

### Project Structure
```
spellforce_data_editor/
├── SpellforceDataEditor/    # Main WinForms GUI application
├── SFEngine/                # Core engine library
│   ├── SFCFF/               # GameData.cff system
│   ├── SFMap/               # Map loading and editing
│   ├── SF3D/                # 3D rendering engine
│   ├── SFLua/               # Lua decompiler
│   ├── SFUnPak/             # PAK archive handling
│   ├── SFChunk/             # Chunk file parser
│   └── SFResources/         # Resource management
└── MapViewerNetNative/      # Standalone map viewer
```

### Key Components

| Component | Description | Documentation |
|-----------|-------------|---------------|
| GameData.cff Editor | Edit game database with 66+ categories | [User Guide](user/gamedata-editor.md) |
| Map Editor | Create/edit game maps with 3D visualization | [User Guide](user/map-editor.md) |
| Asset Viewer | Browse and extract game assets | [User Guide](user/assets.md) |
| Lua Decompiler | Decompile game scripts to readable source | [User Guide](user/scripts.md) |
| SFEngine | Core library for all file operations | [Architecture](architecture/README.md) |

## How the Editor Works

### Data Flow Overview

```
┌─────────────────┐
│  Game Files     │
│  - .cff files   │
│  - .map files   │
│  - .pak files   │
│  - .lua files   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   SFEngine      │  ← Core engine (reads/writes all formats)
│  - SFChunkFile  │     Binary chunk parser
│  - SFUnPak      │     Archive extractor
│  - SFCFF        │     Game data parser
│  - SFMap        │     Map loader/editor
│  - SFLua        │     Lua decompiler
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  GUI (WinForms) │  ← User interface
│  - Data Editor  │     Edit game data
│  - Map Editor   │     Visual map editing
│  - Asset Viewer │     Asset browser
│  - Script Tool  │     Lua decompiler UI
└─────────────────┘
```

### File Format Support

| Format | Purpose | Editor Support |
|--------|---------|----------------|
| `.cff` | Game database (GameData.cff) | ✅ Full read/write |
| `.map` | Game map files | ✅ Full read/write |
| `.pak` | Game asset archives | ✅ Read (extract) |
| `.lua` | Game scripts (Lua 4.01 bytecode) | ✅ Read/Decompile |
| `.msb` | 3D models | ✅ Read (preview) |
| `.bor` | Skeletons | ✅ Read (preview) |
| `.bob` | Animations | ✅ Read (preview) |

## Getting Help

### Documentation Search
- Use the search function in your editor to find specific topics
- Check the [Technical Documentation](#technical-documentation) section for detailed specs

### Common Tasks
- **Edit game data**: See [Game Data Editor Guide](user/gamedata-editor.md)
- **Create a map**: See [Map Editor Guide](user/map-editor.md)
- **Extract assets**: See [Asset Management](user/assets.md)
- **Decompile scripts**: See [Script Editing](user/scripts.md)
- **Understand file formats**: See [File Formats](formats/README.md)

### For Contributors
- See [Development Guide](development/README.md) for setup instructions
- See [Adding Features](development/adding-features.md) for extension guidelines
- See [API Reference](development/api.md) for core interfaces

## Document Version

- **Last Updated**: 2026-02-22
- **Editor Version**: Based on master branch
- **Scope**: Covers all major editor components

---

**Next Steps**: Choose your path:
- New to modding? → [Getting Started Guide](user/README.md)
- Want to contribute? → [Development Guide](development/README.md)
- Need technical details? → [Architecture Overview](architecture/README.md)
