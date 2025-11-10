# SpellForce Modding Project - Master Plan

This document tracks completed tasks and future work for the SpellSmut modding project.

## 🎯 Project Overview

A comprehensive modding toolkit and documentation project for SpellForce: The Order of Dawn - Platinum Edition.

---

## ✅ Completed Tasks

### Phase 1: Documentation & Analysis (Completed)
- ✅ Comprehensive codebase analysis (see CLAUDE.md)
- ✅ Quest System Guide
- ✅ Spell System Guide
- ✅ Sound System Guide
- ✅ Race Creation Guide
- ✅ Campaign System Guide
- ✅ Multiplayer/FreeGame Guide
- ✅ Category system documentation
- ✅ ID mappings and references
- ✅ GitHub Pages site setup

### Phase 2: Asset Extraction & Icon System (Completed)

**Status**: ✅ COMPLETE

**Summary**: Successfully extracted over 59,500 game assets, including a comprehensive icon library. The core challenge is now resolving the mapping between game data and the extracted icons.

**Achievements**:
- **Bulk Extraction**: All 59,500+ files from 23 PAK archives are extracted and categorized.
- **Icon Extraction**: 4096+ ITM icons and 657 spell icons have been extracted from their respective texture atlases.
- **Weapon Reassembly**: A robust system for automatically reassembling multi-part weapon icons is functional.

**Icon System Status**:
- ✅ **Extraction**: The technical process of extracting icons from atlases is complete and works reliably.
- ⚠️ **Mapping Gap**: The critical blocker is the missing link between an item's data (`item_ui_handle`) and the specific texture atlas that holds its icon. The game's data exports do not contain this information.
- 🔍 **Next Step**: The immediate priority is to reverse-engineer the game's logic or find a data file that contains this mapping information.

---

### Phase 3: Quest Creator Development (Recently Completed - November 2025)

**Status**: ✅ **DIALOGUE SYSTEM COMPLETE - WITH INTERACTIVE FLOW CHART**

The Quest Creator's dialogue system has been fully implemented with revolutionary flow chart visualization and interactive connection drawing capabilities.

#### Key Achievements:
- ✅ **Flow Chart Visualization**: Replaced tree view with intuitive color-coded flow chart showing dialogue structure
- ✅ **Interactive Connection Drawing**: Click-and-drag functionality to create connections between dialogue nodes
- ✅ **Vibrant Color System**: High-contrast colors with dark background for excellent visibility
- ✅ **Smart Branching Layout**: Automatic hierarchical positioning that clearly shows player choice branches
- ✅ **Enhanced Step Types**: Including new PLAYER_SPEECH type for single-option player dialogue
- ✅ **Real-time Connection Feedback**: Yellow preview lines and success messages for connection creation
- ✅ **Connection Status Indicators**: Visual feedback showing which choices are connected to responses
- ✅ **Clean UI Design**: Professional appearance with optimized color contrast
- ✅ **Single Launcher System**: Cleaned up multiple confusing launch scripts to single entry point
- ✅ **Error Handling**: Fixed QLabel deletion issues and improved stability

#### Technical Implementation:
- **File**: `src/TirganachReloaded/cff_editor/widgets/simple_dialogue_builder.py`
- **Architecture**: Interactive flow chart with mouse event handling and automatic layout algorithms
- **UI Framework**: PySide6 graphics framework with QGraphicsView/QGraphicsScene
- **Connection Drawing**: Mouse-based interaction with temporary preview lines and smart data structure updates
- **Color System**: Vibrant RGB colors with dark blue background for optimal contrast
- **Launch System**: `quest_creator.py` with uv virtual environment support

#### User Features:
- **Intuitive Workflow**: Click step → edit → add next step → select type
- **Real-time Validation**: Visual feedback for dialogue flow connections
- **Auto-save**: Preserves work progress automatically
- **Branching Support**: Full support for complex dialogue trees with multiple response paths

---

## 🔄 In Progress Tasks

_(Currently no active tasks - Quest Creator dialogue system is complete, focus shifting to full quest wizard implementation.)_

---

## ✅ Recently Completed

### Phase 3: Bulk Asset Extraction (Completed - Oct 18, 2025)

**Status**: ✅ **COMPLETE - ALL ASSETS EXTRACTED!**

**Summary**: Successfully extracted ALL game assets from 23 PAK files using an automated QuickBMS system.

**Results**:
- **Total Files Extracted:** 59,500 files
- **Audio Files:** 15,765 files (MP3 + WAV)
- **UI Assets:** 2,475 files (DDS/TGA)
- **Textures:** 6,602 files
- **3D Models:** 12,136 files (.msb)
- **Animations:** 1,827 files (.bob)
- **Skeletons:** 1,196 files (.bor)
- **Lua Scripts:** 16,730 files
- **Other Assets:** 2,769 files

**Next Steps for Assets**:
1. Analyze and catalog the extracted files.
2. Develop tools for processing assets (e.g., audio conversion, model viewing).
3. Create an interactive asset browser for easy searching and management.

---

## 📋 Planned Tasks

### Phase 3: Asset Extraction & Processing

#### 3D Models & Animations
- ✅ Extract all 3D mesh files from PAK archives (12,136 models extracted!)
- ✅ Extract skeleton/bone files (1,196 .bor files extracted!)
- ✅ Extract animation files (1,827 .bob files extracted!)
- [ ] Document model file formats
- [ ] Create Blender import/export scripts
- [ ] Build asset catalog with preview images

#### Textures & Materials
- ✅ Extract all texture files (6,602 DDS/TGA files extracted!)
- ✅ Complete ITM (item) texture atlas extraction (16 atlases, 4096+ icons)
- ✅ Complete spell texture atlas extraction (18 atlases, 657 icons)
- ✅ Weapon reassembly working (1x2 and 1x4 weapons)
- [ ] **(BLOCKER)** Resolve the handle-to-atlas mapping to link icons to game data.
- [ ] Categorize by type (terrain, units, buildings, effects)
- [ ] Document texture naming conventions
- [ ] Build material/shader documentation

#### Sounds & Music
- ✅ Audio system analysis complete
- ✅ Created extraction tools (extract_audio_assets.py)
- ✅ Documented sound categories and organization
- ✅ Created comprehensive extraction plan
- ✅ **Extracted ALL audio files** (15,765 MP3/WAV files!)
- ✅ Organized by category in ExtractedAssets/Audio/
- [ ] Analyze and catalog audio files (verify counts vs expectations)
- [ ] Convert to modern formats (FLAC, OGG)
- [ ] Create audio catalog and browser
- [ ] Document sound event system integration
- [ ] Create sound replacement guide

### Phase 4: Reverse Engineering

#### File Format Documentation
- [ ] PAK archive format specification
- [ ] CFF (game data) format specification
- [ ] Map file (.map) format specification
- [ ] 3D model format documentation
- [ ] Animation format documentation
- [ ] Texture format documentation

#### Game Systems Analysis
- [ ] **(PRIORITY)** Icon loading and handle-to-atlas mapping logic.
- [ ] UI rendering system
- [ ] Physics and collision system
- [ ] Pathfinding and navigation
- [ ] AI behavior trees
- [ ] Multiplayer networking protocol
- [ ] Save game format

### Phase 5: Modding Tools Development

#### Asset Tools
- [ ] PAK packer/unpacker standalone tool
- [ ] Texture converter (DDS ↔ PNG)
- [ ] Model viewer application
- [ ] Animation preview tool
- [ ] Sound browser and player

#### Content Creation Tools
- ✅ Visual quest editor (with rewards, requirements, dialogues, Lua generation)
- ✅ Dialogue tree editor (branching conversations with visual enhancements)
- ✅ **ID Management System** (shared across all creators) - **COMPLETE** ⭐
- ✅ Quest Creator System (wizard-style quest building with test map) - **COMPLETE**
- ✅ Spell Creator System (Spell Wizard™ for custom spells) - **COMPLETE**
- ✅ Weapon Creator System (Weapon Forge for custom weapons) - **COMPLETE**
- ✅ Armor Creator System (Armor Forge for custom armor) - **COMPLETE**
- ✅ NPC Creator System (NPC Workshop for custom characters) - **COMPLETE**
- 🟡 Building Creator System (Construction Kit for custom structures) - **RESEARCH NEEDED**
- [ ] Race/unit creator wizard
- [ ] Map editor enhancements

#### Development Tools
- [ ] Lua script debugger
- [ ] Live reload system for testing
- [ ] Automated build system for mods
- [ ] Mod packaging tool
- [ ] Version control best practices guide
- ✅ Universal Savefile System (ModSave Framework) - **PLANNING COMPLETE**
- ✅ Utility Tools Suite (Modder's Toolbox) - **PLANNING COMPLETE**

### Phase 6: Example Mods & Tutorials

#### Tutorial Mods
- [ ] "Hello World" - Basic quest mod (will use Quest Creator System)
- [ ] "The Hunter's Request" - Fetch quest example (Quest Creator demo)
- [ ] "Fireball+" - Custom spell mod
- [ ] "Dark Elves Reborn" - Race modification
- [ ] "Mystic Isles" - Custom campaign (3-5 quests, created with Quest Creator)
- [ ] "Arena Master" - Multiplayer map pack

#### Reference Implementations
- [ ] Complete working mod template
- [ ] Asset pipeline example
- [ ] Localization example
- [ ] Complex quest chain example
- [ ] Custom UI skin example

### Phase 7: Community & Distribution

#### Community Resources
- [ ] Mod showcase gallery
- [ ] Tutorial video series
- [ ] Discord/forum community setup
- [ ] Mod compatibility database
- [ ] FAQ and troubleshooting wiki

#### Distribution & Publishing
- [ ] Steam Workshop integration guide
- [ ] Nexus Mods presence
- [ ] GitHub releases for tools
- [ ] Automated update system
- [ ] Mod manager application

---

## 🎨 Icon System - Detailed Roadmap

### ✅ Completed Achievements (2025-10-25)

1.  **ITM Icon Extraction**: 4096+ icons from 16 atlases, with weapon reassembly.
2.  **Spell Icon Extraction**: 657 icons from 18 atlases, with correct rotation.
3.  **Technical Infrastructure**: A complete, automated pipeline for extracting icons from DDS texture atlases is working.

### ⏳ Current Challenges

1.  **Mapping Discovery (CRITICAL BLOCKER)**
    -   **Problem**: We cannot link an item/spell handle (e.g., `ui_item_equip_weapon_dagger_flame`) to its corresponding texture atlas file because this information is missing from the game's data exports.
    -   **Next Step**: Reverse-engineer the game's executable or search game files to find this mapping logic.

2.  **ITM Extraction Refinement**
    -   The current script has minor alignment/offset issues affecting icon quality. This will be addressed after the mapping is resolved.

3.  **Spell Icon GUI Integration**
    -   The data model can now locate spell icons, but GUI testing is needed to confirm they display correctly and are mapped to the right spells.

---

## 🔧 Technical Debt & Infrastructure

### Build System
- [ ] Automate documentation generation
- [ ] Set up CI/CD for tool builds
- [ ] Create automated testing suite
- [ ] Version control for game file formats

### Code Quality
- [ ] Refactor extraction scripts
- [ ] Add error handling and logging
- [ ] Create unit tests for tools
- [ ] Documentation generation automation

### Performance
- [ ] Optimize PAK file reading
- [ ] Cache expensive operations
- [ ] Parallel processing for batch operations
- [ ] Memory usage profiling

---

## 📅 Timeline & Milestones

### Q4 2025
- ✅ Complete all Content Creator tools (Quest, Spell, Weapon, Armor, NPC).
- ✅ Complete all asset extraction.
- ⚠️ **(BLOCKER)** Resolve the Icon System handle-to-atlas mapping issue.

### Q1 2026
- Create visual asset browser.
- Build first tutorial mod using the creator tools.
- Launch community forum.
- Release modding SDK alpha.

### Q2 2026
- Complete utility tool suite.
- Create video tutorial series.
- Prepare for Steam Workshop integration.

---

## 🤝 Collaboration Opportunities

Areas where community help would be valuable:

1.  **Testing**: Test extraction tools on different systems
2.  **Documentation**: Write tutorials and guides
3.  **Modding**: Create example mods and content
4.  **Translation**: Localize documentation
5.  **Design**: Create UI themes and assets
6.  **Programming**: Contribute to tool development

---

## 📝 Notes & Ideas

### UI Modding Possibilities
- Modern UI redesign (flat/minimalist style)
- High-res texture pack
- Color scheme variants (dark mode, colorblind-friendly)
- Custom icon sets
- Animated UI elements
- Widescreen UI fixes

### Future Research Topics
- Lua-C++ binding API reverse engineering
- Network protocol for multiplayer modding
- Save game editor possibilities
- Real-time debugging tools
- Automated mod testing framework

### Community Requests
_(To be filled in as requests come in)_

---

## 📊 Project Statistics

**Documentation Pages**: 30+ (with 8 new system plans)
**Guides Created**: 7 major guides
**Assets Extracted**: 59,500+
**Tools Developed**: 10+ (extraction, categorization, automation)
**Creator Systems Complete**: 6 of 7
**Last Updated**: October 28, 2025

---

## 🔗 Quick Links

- **Documentation Site**: https://alexerlewein.github.io/SpellSmut/
- **UI Assets**: `H:\SpellSmut\ExtractedAssets\UI\`
- **Tools**: `H:\SpellSmut\ModdingTools\`
- **Guides**: `H:\SpellSmut\docs\`

---

**Status**: 🟢 Active Development
**Current Phase**: Phase 5 - Modding Tools Development
**Next Milestone**: Resolve Icon System mapping blocker.

