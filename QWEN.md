# SpellSmut - SpellForce Modding Project Context

## Project Overview

SpellSmut is a comprehensive modding project and documentation repository for **SpellForce: The Order of Dawn - Platinum Edition**, a fantasy RTS/RPG hybrid released in 2005. The project provides tools, documentation, and resources for creating custom content and modifications for the game.

**Project Type**: Game modding ecosystem with documentation, tools, and extraction utilities
**Primary Game**: SpellForce Platinum Edition (Steam AppID: 39540)
**Last Updated**: October 2025

## Project Architecture

### Technology Stack
- **Core Engine**: C++ (Windows executable)
- **Scripting Layer**: Lua 4.0 for game logic extensibility
- **Video Codec**: Bink Video Technology (RAD Game Tools)
- **Audio Engine**: Miles Sound System (RAD Game Tools)
- **Compression**: zlib for asset compression
- **Networking**: GameSpy multiplayer infrastructure
- **Standard Library**: STLport (portable STL implementation)
- **Smart Pointers**: Boost Smart Pointer Library

### Directory Structure
```
SpellSmut/
├── docs/                          # Comprehensive modding documentation
├── OriginalGameFiles/             # Reference game files
├── ModdedGameFiles/               # Modified game files
├── ExtractedAssets/               # Assets extracted from game PAK files
├── ModdingTools/                  # Third-party modding utilities
├── ProjectPlanning/               # Project plans and roadmaps
├── src/                           # Python scripts and modding utilities
│   ├── helper_tools/              # Asset extraction and organization scripts
│   └── TirganachReloaded/          # CFF editing library and tools
├── .claude/                       # Claude-specific settings
├── .crush/                        # Database files
├── README.md                      # Project overview
├── RULES.md                       # File organization conventions
├── CLAUDE.md                      # Codebase analysis
├── _config.yml                    # Jekyll/GitHub Pages configuration
└── ...
```

## Key Components

### Documentation System (docs/)
Contains comprehensive guides for:
- Quest System - Create quests, dialogue, and interactive storytelling
- Spell System - Design custom spells and magic systems
- Sound System - Add audio, music, and voice acting
- Race Creation - Build entirely new playable races
- Campaign System - Craft story-driven campaign experiences
- Multiplayer & FreeGame - Design skirmish and multiplayer maps

### Game Files
- **OriginalGameFiles/**: Untouched game files used as pristine reference
- **ModdedGameFiles/**: Modified game files for testing and custom content

### Asset Extraction (ExtractedAssets/)
- Extracted UI elements, audio, textures, and models from game PAK files
- Organized by asset type for easy access and modification

### Modding Tools (src/)
#### TirganachReloaded
A comprehensive CFF (Configuration File Format) editing library with:
- CFF Editor (GUI and command-line)
- JSON and XML export capabilities
- Game data analysis tools
- Mod creation utilities

#### Helper Tools
Python and batch scripts for:
- PAK file extraction (bulk and individual)
- UI asset extraction
- Audio asset extraction
- File organization and categorization
- Lua mappings extraction

## Development Process

### File Organization Rules
The project follows strict organization conventions documented in RULES.md:
1. Planning files go in `ProjectPlanning/`
2. Documentation files go in `docs/`
3. Source code goes in `src/`
4. Extracted assets go in `ExtractedAssets/`
5. Modding tools go in `ModdingTools/`
6. Original game files remain in `OriginalGameFiles/` (never modified)
7. Modified files go in `ModdedGameFiles/`

### Building and Running
The project is primarily a documentation and tooling effort rather than a compiled application. For using the modding tools:

1. **Python Scripts**: Most tools are Python-based and can be run directly
   ```bash
   python TirganachReloaded/run_cff_editor.py
   python src/helper_tools/batch_extract_ui.py
   ```

2. **Documentation Site**: Built using Jekyll with the cayman theme
   - Hosted at: https://alexerlewein.github.io/SpellSmut/
   - Configured via `_config.yml`

3. **Asset Extraction**: Use the various batch and Python scripts in `src/helper_tools/`
   - PAK extraction utilities
   - UI asset extraction
   - Audio extraction tools

## Development Conventions

### Documentation Standards
- All documentation is in Markdown format
- Clear headings and table of contents
- Cross-referenced related documents
- Descriptive filenames with context

### Code Organization
- Python scripts in `src/` or `src/helper_tools/`
- Clear module names with descriptive functionality
- Related functionality grouped in subfolders
- Usage documented in appropriate guides

### Asset Management
- Maintained clear folder hierarchy for extracted assets
- Original and modified assets kept separate
- README files explaining asset organization

## Modding Capabilities

Based on game architecture analysis, SpellSmut supports:
1. **Quest System**: Create quests, dialogue, and interactive storytelling
2. **Spell System**: Design custom spells across 8 magic schools (White, Black, Fire, Ice, Earth, Air, Mental, Elemental)
3. **Sound System**: Add custom audio, music, and voice acting
4. **Race Creation**: Build entirely new playable races
5. **Campaign System**: Craft story-driven experiences
6. **Multiplayer & FreeGame**: Design skirmish and multiplayer maps

### CFF File Modding
The TirganachReloaded library provides tools to:
- Edit game configuration files
- Export data to JSON/XML formats
- Create new game content
- Modify existing game mechanics

## Key Features

### Game Engine Architecture
- Data-driven design with Lua scripting for game logic
- PAK archive system for asset packaging
- Mod directory system for content replacement
- Comprehensive sound system with 3D positional audio
- Support for 6 playable races with unique unit rosters
- 8 schools of magic with distinct mechanics

### Modding Infrastructure
- Bidirectional Lua-C++ bindings
- Asset merging system allowing multiple mods
- Automatic mod detection and loading
- Non-destructive asset replacement
- Cross-platform mod compatibility

## Usage Instructions

### For Documentation
- Visit: https://alexerlewein.github.io/SpellSmut/
- Start with quest system guide for beginners
- Progress to advanced topics like spell creation

### For Tools
1. Ensure Python 3.x is installed
2. Navigate to the project directory
3. Run desired Python scripts from `src/`
4. Use the TirganachReloaded editor for CFF files

### For Asset Extraction
1. Place original game files in `OriginalGameFiles/`
2. Use scripts in `src/helper_tools/` for extraction
3. Organize extracted assets in `ExtractedAssets/`
4. Use extracted assets in custom mods

## Contributing

The project welcomes contributions to documentation and tools. See the README.md for contribution guidelines:
- Submit issues for documentation errors
- Propose new guides or sections
- Share modding discoveries
- Contribute tools and utilities

## Important Notes

- This project is for educational and modding purposes
- SpellForce and related trademarks belong to THQ Nordic and Grimlore Games
- The game is Steam-enabled with AppID: 39540
- Original game files are required for modding (not included in this repository)

## Quick References

### Documentation Categories
- Quest System Guide
- Spell System Guide 
- Sound System Guide
- Race Creation Guide
- Campaign System Guide
- Multiplayer & FreeGame Guide

### Key Scripts in src/
- `TirganachReloaded/` - CFF editor and game data tools
- `helper_tools/` - Asset extraction and organization utilities
- Various batch files for automation

This project represents a professional approach to game modding with comprehensive documentation, robust tooling, and clear organization principles.