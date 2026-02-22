# SpellForce Data Editor

A comprehensive C# editor and modding tool for SpellForce games, built with .NET 8.0 and WinForms. This tool allows you to edit game data, maps, scripts, and assets from the SpellForce game series.

## Quick Links

- [Documentation](./docs/) - Complete documentation
- [For Modders](./docs/user/README.md) - User guides for modding SpellForce games
- [For Developers](./docs/development/README.md) - Developer documentation and contribution guide
- [Architecture Overview](./docs/architecture/README.md) - System architecture and design
- [Data Formats](./docs/formats/README.md) - Game file format specifications

## Project Overview

The SpellForce Data Editor is a multi-purpose tool that enables:
- **Game Data Editing** - Modify GameData.cff database with 66+ data categories
- **Map Editing** - Create and modify game maps with full 3D visualization
- **Asset Management** - View and extract game assets (models, textures, sounds)
- **Script Decompilation** - Decompile Lua 4.01 game scripts
- **Save Game Editing** - Modify saved game files

## Getting Started

### Quick Start

1. **Specify Game Directory** - Click "Specify Game Directory" and select your SpellForce installation
2. **Open Game Data Editor** - Click "Game Data Editor" to modify game database
3. **Open Map Editor** - Click "Map Editor" to create/edit maps
4. **Open Asset Viewer** - Click "Asset Viewer" to browse game assets

### How It Works

You need the `GameData.cff` file from your SpellForce installation:
- Open it with the program
- Edit data using the intuitive interface
- Save your changes wherever you want

For more detailed instructions, see the [Getting Started Guide](./docs/user/README.md).

## Project Structure

```
spellforce_data_editor/
├── SpellforceDataEditor/    # Main WinForms GUI application
│   ├── SFCFF/               # GameData.cff editor components
│   ├── SFMap/               # Map editor UI components
│   ├── SFLua/               # Lua editor UI components
│   └── special_forms/       # Main editor windows
├── SFEngine/                # Core engine library
│   ├── SFCFF/               # GameData.cff parser and categories
│   ├── SFMap/               # Map loading, editing, and rendering
│   ├── SF3D/                # 3D rendering engine (OpenGL)
│   ├── SFLua/               # Lua decompiler and parser
│   ├── SFUnPak/             # PAK archive extraction
│   ├── SFChunk/             # Chunk-based file format parser
│   ├── SFResources/         # Resource management system
│   └── SFSound/             # Audio engine (NAudio)
└── MapViewerNetNative/      # Lightweight standalone map viewer
```

## Documentation

### Comprehensive Documentation Available

The project includes extensive documentation in the `docs/` directory:

- **User Guides** - For modders and users
  - [Getting Started](./docs/user/README.md) - Installation and first steps
  - [Game Data Editor](./docs/user/gamedata-editor.md) - Editing game database
  - [Map Editor](./docs/user/map-editor.md) - Creating and editing maps
  - [Asset Management](./docs/user/assets.md) - Working with game assets
  - [Script Editing](./docs/user/scripts.md) - Decompiling and editing Lua scripts

- **Developer Guides** - For contributors
  - [Development Guide](./docs/development/README.md) - Setup and contribution
  - [API Reference](./docs/development/api.md) - Core APIs and interfaces
  - [Adding Features](./docs/development/adding-features.md) - Extending the editor

- **Architecture** - Technical details
  - [Architecture Overview](./docs/architecture/README.md) - System architecture
  - [Category System](./docs/architecture/categories.md) - GameData.cff category system
  - [Map System](./docs/architecture/map-system.md) - Map loading and editing
  - [3D Engine](./docs/architecture/3d-engine.md) - OpenGL rendering pipeline
  - [Lua System](./docs/architecture/lua-system.md) - Lua bytecode decompilation

- **File Formats** - Format specifications
  - [Format Overview](./docs/formats/README.md) - Game file format specifications
  - [Chunk Format](./docs/formats/chunk-format.md) - Binary chunk format details

## Building

### Prerequisites

- .NET 8.0 SDK
- Windows OS (x86)
- Visual Studio 2022 or later (recommended)

### Steps

1. Clone the repository
2. Open `SpellforceDataEditor.sln` in Visual Studio
3. Restore NuGet packages
4. Build the solution (Release configuration recommended)

## Key Features

### Game Data Editor (GameData.cff)

- Edit 66+ data categories including:
  - Spells and effects
  - Units and creatures
  - Items and equipment
  - Buildings and structures
  - Skills and abilities
  - Quest and dialogue text

### Map Editor

- Full 3D visualization of game maps
- Terrain editing with heightmap support
- Entity placement (buildings, units, objects)
- Terrain texture painting
- Portal and spawn point management
- Weather and environment effects

### Lua Script Decompiler

- Decompile Lua 4.01 bytecode to readable source
- Parse and analyze game scripts
- Edit and recompile scripts (limited)

### Asset Manager

- View 3D models with animations
- Preview textures and materials
- Extract assets for external editing
- Audio playback for sounds and music

## Development Status

- **GameData Editor**: ✅ Complete
- **Map Editor**: ✅ Complete with advanced features
- **Asset Viewer**: ✅ Complete
- **Lua Decompiler**: ✅ Functional (Lua 4.01)
- **Save Editor**: ✅ Basic functionality

## Contributing

See [Development Guide](./docs/development/README.md) for contribution guidelines.

## License

See LICENSE file for details.

## Credits

Original project by leszekd25 - https://github.com/leszekd25/spellforce_data_editor

## Support

For issues and questions:
- GitHub Issues: https://github.com/leszekd25/spellforce_data_editor/issues
- Documentation: See the [docs](./docs/) folder

## Existing Documentation

This repository also contains additional documentation:
- [CODEBASE_ARCHITECTURE.md](./CODEBASE_ARCHITECTURE.md) - Deep technical architecture details
- [GAMEDATA_EXPORT_PLAN.md](./GAMEDATA_EXPORT_PLAN.md) - Export/import implementation plan
- [CLAUDE.md](./CLAUDE.md) - Project-specific notes
- [SUMMARY.md](./SUMMARY.md) - Project summary
