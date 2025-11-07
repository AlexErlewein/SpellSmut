# ProjectPlanning Directory

## Overview
This directory contains all planning, status, and organizational documents for the SpellForce modding project. The structure is designed for clarity and maintainability.

## Directory Structure

```
ProjectPlanning/
├── PROJECT_OVERVIEW.md           # ← Start here: Complete project status
├── DOCS_STRUCTURE_MERMAID.md     # ← Documentation organization
├── REORGANIZATION_PROPOSAL.md    # ← How this structure was created
├── CLEANUP_SUMMARY.md           # ← Previous cleanup documentation
│
├── Components/                   # Component-specific planning
│   ├── CoreSystems/             # Core system planning
│   │   ├── ASSET_EXTRACTION.md  # PAK extraction pipeline
│   │   ├── DATA_EXTRACTION_PLAN.md
│   │   ├── ID_MANAGEMENT_SYSTEM.md
│   │   └── SAVEFILE_SYSTEM.md
│   ├── Editor/                  # GUI Editor planning
│   │   ├── GUI_EDITOR.md        # PySide6 GUI editor status
│   │   └── LAUNCHING_TIRGANACH.md
│   ├── EntityCreators/          # Content creation tools
│   │   ├── BUILDING_CREATOR_PLAN.md
│   │   ├── NPC_CREATOR_PLAN.md
│   │   └── RACE_CREATOR_PLAN.md
│   ├── IconSystem/              # Icon extraction & integration
│   │   ├── ICON_SYSTEM.md       # Main icon system documentation
│   │   └── ICON_EXTRACTION_*.md # Various extraction status files
│   ├── ItemCreators/            # Weapon/Armor creation
│   │   ├── ARMOR_CREATOR_PLAN.md
│   │   └── WEAPON_CREATION_PLAN.md
│   ├── MapViewer/               # Map Viewer component
│   │   ├── MAP_VIEWER_ARCHITECTURE.md
│   │   ├── MAP_VIEWER_STATUS.md
│   │   ├── MAP_VIEWER_ROADMAP.md
│   │   └── MAP_VIEWER_TECHNICAL_SPECS.md
│   ├── QuestSystem/             # Quest system planning
│   │   ├── QUEST_CREATION_PLAN.md
│   │   └── QUEST_EDITOR.md
│   ├── SpellSystem/             # Spell system planning
│   │   └── SPELL_CREATION_PLAN.md
│   └── MODDING_PLAN.md          # Overall modding strategy
│
├── Status/                      # Current status tracking
│   ├── CURRENT_STATUS.md        # Live project status
│   ├── COMPLETED_WORK.md        # Achievement summary
│   ├── BLOCKERS.md              # Current issues & blockers
│   └── Various *_STATUS.md      # Component-specific status
│
├── Research/                    # Research and analysis
│   └── CHARACTER_APPEARANCE_RESEARCH.md
│
├── Archive/                     # Historical files (preserved)
│   ├── IconSystem/              # Old icon system planning
│   ├── Internal/                # Completed plans and analysis
│   │   ├── QUEST_*_PLAN.md      # Completed quest plans
│   │   ├── TEXTURE_*.md         # Completed texture work
│   │   └── *_CSHARP_ANALYSIS.md # Technical analysis docs
│   └── Legacy/                  # Old implementation plans
│       ├── WEEK*_SUMMARY.md     # Old weekly summaries
│       ├── *_ROADMAP.md         # Superseded roadmaps
│       └── EDITOR_PLANNING.md   # Original editor planning
│
└── README.md                    # This file
```

## Quick Start

### New to the Project?
1. **Read** `PROJECT_OVERVIEW.md` - Complete project status and component breakdown
2. **Check** `Status/CURRENT_STATUS.md` - What's happening right now
3. **Browse** `Components/` - Detailed status for specific areas

### Looking for Specific Information?
- **GUI Editor**: `Components/Editor/GUI_EDITOR.md`
- **Asset Extraction**: `Components/CoreSystems/ASSET_EXTRACTION.md`
- **Icon System**: `Components/IconSystem/ICON_SYSTEM.md`
- **Quest Editor**: `Components/QuestSystem/QUEST_EDITOR.md`
- **Map Viewer**: `Components/MapViewer/MAP_VIEWER_ARCHITECTURE.md` (+ STATUS, ROADMAP, TECHNICAL_SPECS)
- **Weapon/Armor Creation**: `Components/ItemCreators/`
- **Entity Creation**: `Components/EntityCreators/`
- **Spell System**: `Components/SpellSystem/SPELL_CREATION_PLAN.md`
- **Current Blockers**: `Status/BLOCKERS.md`
- **Completed Work**: `Status/COMPLETED_WORK.md`
- **Research**: `Research/CHARACTER_APPEARANCE_RESEARCH.md`

### Technical Details?
- **Documentation Structure**: `DOCS_STRUCTURE_MERMAID.md`
- **Reorganization History**: `REORGANIZATION_PROPOSAL.md`

## File Categories

### 📊 Overview Files
- **PROJECT_OVERVIEW.md**: Executive summary of entire project
- **DOCS_STRUCTURE_MERMAID.md**: Visual guide to documentation organization

### 🔧 Component Files
- **GUI_EDITOR.md**: PySide6-based CFF file editor
- **ICON_SYSTEM.md**: Icon extraction and GUI integration
- **QUEST_EDITOR.md**: Interactive quest creation tools
- **ASSET_EXTRACTION.md**: PAK file extraction pipeline
- **MAP_VIEWER_ARCHITECTURE.md**: 3D map viewer technical architecture
- **MAP_VIEWER_STATUS.md**: Map viewer current status and progress
- **MAP_VIEWER_ROADMAP.md**: Map viewer development roadmap (5 phases)
- **MAP_VIEWER_TECHNICAL_SPECS.md**: Detailed technical specifications

### 📈 Status Files
- **CURRENT_STATUS.md**: Live project status and next steps
- **COMPLETED_WORK.md**: Summary of achievements
- **BLOCKERS.md**: Current issues and mitigation plans

### 📁 Archive
- **Preserved historical files** for reference
- **Consolidated into current structure** to avoid duplication
- **Safe to ignore** for current development

## Maintenance Guidelines

### When Updating Status
1. Update `Status/CURRENT_STATUS.md` for overall project changes
2. Update relevant `Components/*.md` for component-specific changes
3. Update `Status/BLOCKERS.md` when issues are resolved or discovered

### When Adding New Planning
1. Determine if it's a new component (add to `Components/`)
2. Or if it's project-wide (add to root or `Status/`)
3. Update `PROJECT_OVERVIEW.md` to reflect new information

### File Naming Convention
- Use `SCREAMING_SNAKE_CASE.md` for file names
- Use descriptive names that indicate content
- Keep names concise but clear

## Key Principles

### Single Source of Truth
- Each concept has one authoritative document
- Cross-references link related information
- No duplicate information across files

### Current Focus
- Active planning in `Components/` and `Status/`
- Historical information preserved in `Archive/`
- Clear separation between current and historical

### Easy Navigation
- Logical hierarchy: Overview → Components → Details
- Consistent structure across component files
- Clear status indicators (✅ 🔄 📋 ❌)

## Status Indicators

| Icon | Meaning |
|------|---------|
| ✅ | Complete |
| 🔄 | In Progress |
| 📋 | Planned |
| ❌ | Blocked/Issue |
| ⚠️ | Warning/Attention Needed |

## Questions?

- **Can't find something?** Check `Archive/` for historical files
- **Need to add content?** See maintenance guidelines above
- **Confused about structure?** Read `REORGANIZATION_PROPOSAL.md`

---

*This structure was created October 26, 2025 to improve project organization and reduce planning document fragmentation.*

*Map Viewer documentation added November 3, 2024 following Phase 1 completion.*