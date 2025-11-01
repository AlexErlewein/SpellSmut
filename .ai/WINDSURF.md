# SpellForce Modding Project - Windsurf AI Assistant Rules

## 📍 Project Overview

This is the **SpellForce Platinum Edition modding project** - a comprehensive toolkit for creating and modifying game content. The project includes a GUI CFF editor, content creators (weapons, armor, spells, quests, NPCs), asset extraction systems, and extensive documentation.

## 🎯 Current Project Status (November 2025)

### ✅ **COMPLETED SYSTEMS** (Production Ready)
- **GUI Editor**: PySide6-based CFF editor with multilingual support
- **Content Creator Suite**: Weapon Forge, Armor Forge, Spell Wizard, NPC Creator, Race Creator, Quest Editor
- **ID Management System**: Centralized conflict-free ID allocation
- **Asset Extraction**: 59,500+ files extracted from all game archives
- **Documentation**: 15+ comprehensive guides and technical documentation

### ⚠️ **ACTIVE CHALLENGE**
- **Icon System**: Handle-to-atlas mapping resolution (critical priority)

---

## 🏗️ Project Architecture

### Core Components
```
SpellSmut/
├── src/TirganachReloaded/     # Main GUI application (PySide6)
│   ├── cff_editor/           # CFF file editor
│   ├── creators/             # Content creation tools
│   └── data/                 # Accelerated data layer (SQLite + Pickle)
├── src/helper_tools/         # Standalone utilities
├── src/tests/               # Test suite (pytest)
├── docs/                    # User documentation & guides
├── ProjectPlanning/         # Development planning & status
├── ModdingTools/            # Third-party tools & references
├── ExtractedAssets/         # Extracted game assets
└── .ai/                     # AI assistant instructions (this folder)
```

### Technology Stack
- **Primary Language**: Python 3.11+
- **Package Manager**: **UV** (MANDATORY - never use pip)
- **GUI Framework**: PySide6 (Qt6)
- **Data Processing**: Pandas, SQLite, Pickle caching
- **Testing**: Pytest with comprehensive coverage
- **File Formats**: CFF (custom), Lua (game scripts), JSON, CSV

---

## 📁 Critical File Organization Rules

### 🚨 **MANDATORY RULES - NO EXCEPTIONS**

#### **Python Environment**
- **ALWAYS** use `uv run` for executing Python scripts
- **ALWAYS** use `uv pip install` for dependencies
- **NEVER** use plain `pip` or `python` commands
- **NEVER** install packages globally

#### **Test Files** → `src/tests/` ONLY
```
src/tests/
├── test_*.py               # Test files
├── conftest.py            # Pytest configuration
├── test_data/             # Test fixtures and data
└── test_outputs/          # Test results and artifacts
```

#### **Documentation** → `docs/` ONLY
```
docs/
├── Guides/                # User guides and tutorials
├── Extraction/            # Asset extraction documentation
├── Project/               # Technical documentation
└── Tools/                 # Development tool documentation
```

#### **Source Code** → `src/` ONLY
```
src/
├── TirganachReloaded/     # Main application
├── helper_tools/          # Standalone utilities
└── tests/                 # ALL test files
```

#### **Root Directory** → Config Files ONLY
- **NEVER** place source code, tests, or documentation in root
- **ONLY** configuration files (pyproject.toml, uv.lock, .gitignore)

---

## 🔧 Development Standards

### Code Style & Quality
- **PEP 8 compliance** for all Python code
- **Type hints** required for function signatures
- **Comprehensive docstrings** for all modules and functions
- **Error handling** with proper exception management
- **Logging** using Python's logging module

### Testing Requirements
- **Test coverage** minimum 80% for new code
- **Integration tests** for complex workflows
- **Performance tests** for data processing operations
- **UI tests** for critical GUI functionality

### Data Management
- **SQLite + Pickle dual cache** for performance
- **Validation layers** for all data imports/exports
- **Backup systems** for critical operations
- **Progress indicators** for long-running operations

---

## 🎮 Game-Specific Knowledge

### SpellForce Data Structures
- **CFF Files**: GameData.cff contains all game entities
- **Entity Types**: Items, weapons, armor, spells, units, buildings, quests
- **ID Systems**: 32-bit entity IDs with category prefixes
- **Localization**: 6 languages (English, German, French, Spanish, Italian, Polish)

### Quest System Architecture
- **State Machine**: 5 states (Unknown → Known → Active → Solved/Unsolvable)
- **Condition-Action Paradigm**: `Conditions = {}` and `Actions = {}`
- **Dialogue System**: Branching conversations with player choices
- **Integration**: Quests linked to items, entities, and global flags

### Asset Pipeline
- **PAK Archives**: 23 archives containing 59,500+ files
- **Icon Atlases**: Multi-part weapon icons, spell icons with rotation
- **Audio Assets**: Sound effects, music, voice files
- **3D Models**: Buildings, units, props with animations

---

## 🛠️ Current Development Tools

### GUI Editor (TirganachReloaded)
- **CFF Editor**: Main data editing interface
- **Multilingual Support**: Real-time language switching
- **Performance**: 17x faster loading with dual cache system
- **Validation**: Real-time data validation and error reporting

### Content Creators
- **Weapon Forge**: Create/edit 719+ weapons with custom types
- **Armor Forge**: Design armor for all equipment slots
- **Spell Wizard**: Create spells with 1-15 progression levels
- **NPC Creator**: Custom NPCs with stats and appearance
- **Race Creator**: New playable races with units/buildings
- **Quest Editor**: Visual quest tree with dialogue editor

### Helper Tools
- **Asset Extraction**: QuickBMS integration with Python automation
- **Data Validation**: Comprehensive data integrity checking
- **Export Utilities**: CFF export with validation
- **Performance Profiling**: Cache optimization tools

---

## 📋 Development Guidelines

### When Working on GUI Components
1. **Use PySide6** for all UI development
2. **Follow Qt best practices** for signal/slot connections
3. **Implement proper MVC** separation
4. **Add comprehensive error handling** for file operations
5. **Test with multiple screen resolutions**

### When Working on Data Processing
1. **Always use the cache system** (SQLite + Pickle)
2. **Validate data integrity** before processing
3. **Provide progress feedback** for long operations
4. **Handle large datasets** efficiently with chunking
5. **Implement proper cleanup** for temporary files

### When Working on Quest System
1. **Follow state machine patterns** established in game
2. **Use condition-action paradigm** for quest logic
3. **Implement dialogue trees** with proper branching
4. **Validate quest dependencies** to prevent circular references
5. **Export proper Lua format** for game integration

### When Working on Asset Pipeline
1. **Respect file naming conventions** from original game
2. **Maintain directory structure** compatibility
3. **Handle binary formats** with proper endianness
4. **Validate checksums** for critical assets
5. **Document extraction processes** thoroughly

---

## 🚨 Common Mistakes to Avoid

### ❌ **Never Do These**
- Use `pip` instead of `uv`
- Place test files outside `src/tests/`
- Put documentation in root directory
- Modify files in `OriginalGameFiles/`
- Create temporary files in project root
- Use hardcoded paths instead of relative paths
- Skip error handling for file operations
- Commit sensitive data or API keys

### ✅ **Always Do These**
- Use `uv run script.py` for execution
- Follow the established folder structure
- Write comprehensive tests for new features
- Document complex algorithms and data structures
- Validate all user inputs and file data
- Use proper logging for debugging
- Follow PEP 8 and type hints
- Update documentation when adding features

---

## 🎯 Current Priorities (November 2025)

1. **Icon System Mapping**: Resolve handle-to-atlas mapping challenge
2. **Performance Optimization**: Continue optimizing data layer performance
3. **Documentation Maintenance**: Keep guides updated with new features
4. **Testing**: Expand test coverage for edge cases
5. **User Experience**: Polish UI/UX based on user feedback

---

## 📞 Getting Help & Resources

### Internal Documentation
- **Project Planning**: `ProjectPlanning/` for development status
- **Technical Guides**: `docs/` for comprehensive documentation
- **API Reference**: Inline docstrings and type hints
- **Architecture**: `docs/Project/` for system overviews

### Development Workflow
- **Issue Tracking**: Use GitHub Issues for bug reports
- **Feature Requests**: Document in `ProjectPlanning/Components/`
- **Code Review**: All changes require review and testing
- **Release Process**: Follow semantic versioning in pyproject.toml

---

**Last Updated**: November 2025  
**Maintained By**: SpellSmut Development Team  
**AI Assistant**: Windsurf (this file)  

---

🎯 **Remember**: This is a mature, production-ready project with established patterns and high quality standards. Follow the existing conventions and prioritize stability and performance when making changes.
