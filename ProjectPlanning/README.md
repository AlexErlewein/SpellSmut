# ProjectPlanning Directory

## Overview
This directory contains all planning, status, and organizational documents for the SpellForce modding project. The structure is designed for clarity and maintainability.

## Directory Structure

```
ProjectPlanning/
├── PROJECT_OVERVIEW.md           # ← Start here: Complete project status
├── DOCS_STRUCTURE_MERMAID.md     # ← Documentation organization
├── REORGANIZATION_PROPOSAL.md    # ← How this structure was created
│
├── Components/                   # Component-specific planning
│   ├── GUI_EDITOR.md            # PySide6 GUI editor status
│   ├── ICON_SYSTEM.md           # Icon extraction & integration
│   ├── QUEST_EDITOR.md          # Quest creation tools
│   ├── ASSET_EXTRACTION.md      # PAK extraction pipeline
│   ├── MAP_VIEWER_ARCHITECTURE.md    # Map Viewer technical architecture
│   ├── MAP_VIEWER_STATUS.md          # Map Viewer current status
│   ├── MAP_VIEWER_ROADMAP.md         # Map Viewer development roadmap
│   └── MAP_VIEWER_TECHNICAL_SPECS.md # Map Viewer detailed specifications
│
├── Status/                      # Current status tracking
│   ├── CURRENT_STATUS.md        # Live project status
│   ├── COMPLETED_WORK.md        # Achievement summary
│   └── BLOCKERS.md              # Current issues & blockers
│
├── Archive/                     # Historical files (preserved)
│   ├── GUI/                     # Old GUI planning files
│   ├── Internal/                # Old internal planning files
│   └── Legacy/                  # Old root-level files
│
└── README.md                    # This file
```

## Quick Start

### New to the Project?
1. **Read** `PROJECT_OVERVIEW.md` - Complete project status and component breakdown
2. **Check** `Status/CURRENT_STATUS.md` - What's happening right now
3. **Browse** `Components/` - Detailed status for specific areas

### Looking for Specific Information?
- **GUI Editor**: `Components/GUI_EDITOR.md`
- **Asset Extraction**: `Components/ASSET_EXTRACTION.md`
- **Icon System**: `Components/ICON_SYSTEM.md`
- **Quest Editor**: `Components/QUEST_EDITOR.md`
- **Map Viewer**: `Components/MAP_VIEWER_ARCHITECTURE.md` (+ STATUS, ROADMAP, TECHNICAL_SPECS)
- **Current Blockers**: `Status/BLOCKERS.md`
- **Completed Work**: `Status/COMPLETED_WORK.md`

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