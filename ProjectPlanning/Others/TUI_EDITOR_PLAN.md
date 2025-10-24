# TUI Editor Development Plan

## Overview
Plan for the Textual-based Terminal UI editor as a lightweight alternative to the GUI version.

## Current Status ⏳ PENDING

### Phase 1: Core Functionality - PENDING
- ⏳ File loading with progress
- ⏳ Category list view
- ⏳ Basic table display

### Phase 2: Navigation - PENDING
- ⏳ Search/filter functionality
- ⏳ Pagination for large tables
- ⏳ Element selection

### Phase 3: Editing - PENDING
- ⏳ Property display/edit
- ⏳ Type validation
- ⏳ Save modifications

## Rationale for TUI Version

### Advantages
- ✅ **Lightweight**: No GUI dependencies (~5MB vs ~50MB)
- ✅ **SSH-Friendly**: Works over remote connections
- ✅ **Keyboard-Centric**: Fast for power users
- ✅ **Scriptable**: Can be automated easily

### Disadvantages
- ❌ **Limited Visual Appeal**: Terminal-based interface
- ❌ **Mouse Support**: Primarily keyboard navigation
- ❌ **Complex Forms**: Harder to implement rich editing

## Technical Approach

### Framework: Textual
- Modern Python TUI framework
- Component-based architecture
- CSS-like styling
- Good performance for data display

### UI Layout (Planned)
```
╭─────────────────────────────────────────────────────────────────╮
│ SpellForce CFF Editor (TUI)                               v1.0 │
├─────────────────────────────────────────────────────────────────┤
│ File: GameData.cff                         [Open] [Save] [Quit] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ╭─Categories───╮ ╭─Elements─────────────╮ ╭─Properties──────╮ │
│ │              │ │                      │ │                 │ │
│ │ ▶ Spells     │ │  ID    Name     Type │ │ item_id: 531   │ │
│ │ ▼ Items      │ │ ─────────────────── │ │ name: Sword    │ │
│ │   ▶ Armor    │ │  531   Sword     W │ │                │ │
│ │   ▶ Weapons  │ │  532   Armor     A │ │ item_type:     │ │
│ │ ▶ Creatures  │ │  537   Ring      R │ │  WEAPON        │ │
│ │ ▶ Buildings  │ │  ...                │ │                │ │
│ │ ...          │ │                     │ │ health: 10     │ │
│ │              │ │ Search: ________    │ │ mana: 0        │ │
│ │ [43 total]   │ │                     │ │ ...            │ │
│ │              │ │ Page 1/15           │ │                │ │
│ │              │ │                     │ │ [Save] [Cancel]│ │
│ │ ╰──────────────╯ ╰─────────────────────╯ │                 │ │
│                                           ╰─────────────────╯ │
│                                                                 │
│ Status: Ready                                    Memory: 45 MB │
╰─────────────────────────────────────────────────────────────────╯
```

## Development Priority

### Recommendation: LOW PRIORITY
- GUI version should be completed first
- TUI can be developed as a "nice to have" for specific use cases
- Share data model with GUI for consistency

## Dependencies
- Textual: ⏳ Not installed yet
- Shared data model: ✅ Available from GUI version

## Next Steps
1. Complete GUI Phase 3 (Editing) first
2. Extract shared data model components
3. Implement TUI as simplified version of GUI
4. Add TUI-specific optimizations (keyboard shortcuts, etc.)