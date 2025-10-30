# Quest Editor Tabs - Comparison and Usage

## Overview

When you open the Quest Editor from the menu, you see three tabs at the top:

1. **Quest Hierarchy**
2. **Dialog Editor**
3. **Quest Creator**

This document explains what each one does and when to use them.

## The Three Tabs Explained

### 1. Quest Hierarchy (Same as Main Editor)

**Purpose:** View and browse all quests in a hierarchical tree structure.

**Features:**
- Tree view showing all main quests and sub-quests
- Expandable/collapsible branches
- Shows quest relationships (parent-child)
- Columns: Quest Name, Quest ID, Type, Parent ID, Order Index
- Quick navigation with Expand/Collapse All buttons
- Auto-loads when CFF file is loaded
- Same view as in the main editor

**Current Status:** ✅ **Fully working**

**When to Use:**
- Browsing the complete quest structure
- Understanding quest relationships
- Finding specific quests by ID
- Viewing quest hierarchy outside main editor

**Note:** This provides the same functionality as clicking "quests" in the main editor's category tree.

---

### 2. Dialog Editor (Standalone)

**Purpose:** Create and edit dialogue trees independent of specific quests.

**Features:**
- Full dialog branching editor
- Create NPC dialogues
- Add player choice options
- Build conversation trees
- Preview conversations
- Save dialogues to CFF

**When to Use:**
- Creating generic NPC dialogues
- Building dialogue templates
- Testing dialogue flows
- Working on dialogues before assigning to quests

**Status:** ✅ **Fully working**

**How to Use:**
1. Click "Dialog Editor" tab
2. Click "Add Root Dialog"
3. Build your conversation tree
4. Save changes

---

### 3. Quest Creator (Wizard)

**Purpose:** Generate complete quest Lua scripts from a form-based interface.

**Features:**
- Step-by-step quest creation
- Tabs for different aspects:
  - **Basic Info**: Quest ID, name, description, type, map
  - **Objectives**: Define quest goals
  - **Rewards**: XP, items, money
  - **Requirements**: Prerequisites and conditions
  - **NPCs & Dialog**: Link dialogues
  - **Lua Preview**: See generated script
- Generate complete Lua quest script
- Copy script to clipboard

**When to Use:**
- Creating new quests from scratch
- Generating Lua quest scripts
- Prototyping quest designs
- Learning quest structure

**Status:** ✅ **Fully working**

**Output:** Generates Lua script like:
```lua
Quest.Q1001 = {
    name = "The Lost Sword",
    description = "Find the legendary sword",
    rewards = {
        xp = 1000,
        items = {100, 200},
        gold = 50
    }
}
```

**Note:** This creates Lua scripts but doesn't directly edit CFF quest data.

---

## Which One Should You Use?

### For Viewing and Browsing Quests:

✅ **Use either:**

**Quest Editor → Quest Hierarchy tab**
- Standalone quest tree view
- Same as main editor
- Good for focused quest browsing

**OR Main Editor Quest View**
- Click "quests" in the left category tree
- See quest hierarchy in column 2
- Edit quest properties in column 3
- View dialogues and hierarchy in column 4

### For Creating New Dialogues:

✅ **Use:** Dialog Editor tab
- Standalone dialogue creation
- Works independently of quests

### For Generating Quest Scripts:

✅ **Use:** Quest Creator tab
- Form-based quest design
- Generates Lua scripts
- Good for learning and prototyping

---

## Recommended Workflow

### Editing Existing Quests:

1. **In Main Editor:**
   - Click "quests" category (left column)
   - Browse quest hierarchy (column 2)
   - Select a quest
   - Edit properties (column 3)
   - View/edit dialogues (column 4)

### Creating New Quests:

**Option A - Using Main Editor:**
1. Load your CFF file
2. Navigate to quests
3. Manually add quest entries
4. Link dialogues

**Option B - Using Quest Creator:**
1. Open Quest Editor → Quest Creator tab
2. Fill in quest details
3. Generate Lua script
4. Copy and integrate into your mod

### Working with Dialogues:

1. **Quest Editor → Dialog Editor tab**
2. Create dialogue trees
3. Save to CFF
4. Link to quests in main editor

---

## Known Issues

### None Currently

All quest editor tabs are now working properly. The Quest Hierarchy tab has been updated to use the same efficient view as the main editor.

---

## Recent Improvements

The Quest Editor tabs have been updated:

1. ✅ **Fixed** Quest Hierarchy tab - now uses efficient tree view
2. ✅ **Keep** Dialog Editor (useful standalone tool)
3. ✅ **Keep** Quest Creator (good for Lua generation)
4. ✅ **Enhanced** main editor quest view with hierarchy tree

---

## Quick Reference

| Task | Recommended Tool | Tab/Location |
|------|-----------------|--------------|
| View quest hierarchy | Main Editor OR Quest Editor | Category: quests OR Quest Hierarchy tab |
| Edit quest properties | Main Editor | Column 3 |
| View quest dialogues | Main Editor | Column 4 |
| Create dialogues | Quest Editor | Dialog Editor tab |
| Generate quest Lua | Quest Editor | Quest Creator tab |
| Browse quests | Quest Editor | Quest Hierarchy tab |

---

## Summary

**TL;DR:**
- 🟢 Quest Hierarchy: **Working** - browse quest tree structure
- 🟢 Dialog Editor: **Working** - use for standalone dialogues
- 🟢 Quest Creator: **Working** - use for Lua script generation
- 🟢 Main Editor Quest View: **Working** - full quest editing with hierarchy

**Best Practice:** Use the main editor for quest editing, or use Quest Editor tabs for specialized tasks (browsing, dialogue creation, Lua generation).