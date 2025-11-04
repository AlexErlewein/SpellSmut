# TirganachReloaded Components Documentation

This directory contains detailed planning and implementation documentation for all major components of the TirganachReloaded modding toolkit.

## Directory Structure

### 📁 CoreSystems/
Fundamental systems that power the editor and modding tools:
- **ASSET_EXTRACTION.md** - Asset extraction from game files
- **DATA_EXTRACTION_PLAN.md** - Data extraction strategies
- **EDITOR_DATA_LAYER_ACCELERATION_PLAN.md** - Performance optimization with caching
- **ID_MANAGEMENT_SYSTEM.md** - Unique ID generation and tracking
- **SAVEFILE_SYSTEM.md** - Save file handling and manipulation
- **UTILITY_TOOLS.md** - General utility tools and helpers

### 🎨 IconSystem/
Complete icon extraction, processing, and integration system:
- **ICON_SYSTEM.md** - Overview of the icon system
- **ICON_SYSTEM_NEXT_STEPS.md** - Future improvements
- **ICON_ENHANCEMENT_SUMMARY.md** - Summary of icon enhancements
- **ICON_EXTRACTION_STATUS.md** - Current extraction status
- **ICON_EXTRACTION_BEFORE_AFTER.md** - Comparison of extraction methods
- **ICON_EXTRACTION_FINDINGS_2025-10-25.md** - Detailed findings
- **ICON_EXTRACTION_SUMMARY_2025-10-25.md** - Extraction summary
- **SOURCE_CODE_ANALYSIS_UI_ICONS.md** - UI icon source code analysis

### ⚔️ ItemCreators/
Tools for creating and managing game items:
- **ARMOR_CREATOR_PLAN.md** - Armor creation system
- **WEAPON_CREATION_PLAN.md** - Weapon creation system
- **WEAPON_FORGE_IMPROVEMENTS.md** - Enhanced weapon forge features
- **CFF_EDITOR_ITM_IMPLEMENTATION.md** - ITM (Item Texture Mapping) integration

### 🧙 EntityCreators/
Systems for creating game entities and structures:
- **NPC_CREATOR_PLAN.md** - NPC creation and management
- **RACE_CREATOR_PLAN.md** - Custom race creation
- **BUILDING_CREATOR_PLAN.md** - Building/structure creation
- **BUILDING_WIZARD_IMPLEMENTATION_PLAN.md** - Building wizard implementation

### 📜 QuestSystem/
Quest creation and editing tools:
- **QUEST_CREATION_PLAN.md** - Quest creation wizard
- **QUEST_EDITOR.md** - Quest editor implementation

### ✨ SpellSystem/
Spell and magic system tools:
- **SPELL_CREATION_PLAN.md** - Spell creation and management

### 🖥️ Editor/
Main editor interface and launcher:
- **GUI_EDITOR.md** - GUI editor documentation
- **GUI_EDITOR_PLAN.md** - GUI editor planning
- **LAUNCHING_TIRGANACH.md** - Editor launcher and startup

## Root Files

### MODDING_PLAN.md
High-level modding strategy and overall project planning.

## How to Use This Documentation

1. **Starting a New Component**: Check if there's existing documentation in the relevant subfolder
2. **Understanding the System**: Start with the main file (e.g., `ICON_SYSTEM.md`) then review supporting documents
3. **Implementation**: Follow the `*_PLAN.md` files which contain step-by-step implementation guides
4. **Status Updates**: Look for `*_STATUS.md` files to understand current progress

## Documentation Standards

All component documentation should include:
- **Overview**: What the component does
- **Architecture**: How it's structured
- **Dependencies**: What it relies on
- **Implementation Status**: Current state (Planned/In Progress/Complete)
- **Usage Examples**: How to use the component
- **Future Work**: Planned improvements

## Related Directories

- **../Archive/** - Deprecated or superseded documentation
- **../Research/** - Research notes and investigations
- **../Status/** - Project-wide status reports
- **../../docs/** - User-facing documentation and guides

## Contributing

When adding new component documentation:
1. Place it in the appropriate subfolder (or create a new one if needed)
2. Follow the naming convention: `COMPONENT_NAME.md` or `COMPONENT_NAME_PURPOSE.md`
3. Include cross-references to related components
4. Update this README with a brief description

---

*Last Updated: 2024-11-04*
*Structure: Organized by component type for better navigation*