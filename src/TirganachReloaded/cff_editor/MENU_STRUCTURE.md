# TirganachReloaded CFF Editor - Menu Structure

## Complete Menu Hierarchy

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                    SpellForce GameData.cff Editor                             ║
╠═══════════════════════════════════════════════════════════════════════════════╣
║ File | Edit | Language | View | Tools | Help                                  ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## 📁 File Menu

```
File
├─ Open CFF...                    [Ctrl+O]
├─ Save                           [Ctrl+S]
├─ Save As...                     [Ctrl+Shift+S]
├─ ─────────────────────────────────────
└─ Exit                           [Ctrl+Q]
```

**Purpose:** File operations for loading and saving GameData.cff files

---

## ✏️ Edit Menu

```
Edit
└─ Refresh                        [F5]
```

**Purpose:** Content editing and refresh operations

---

## 🌐 Language Menu

```
Language
├─ English                        [⚪ Radio button]
├─ German                         [⚪ Radio button]
├─ Polish                         [⚪ Radio button]
└─ French                         [⚪ Radio button]
```

**Purpose:** Switch between different language versions of game text

---

## 👁️ View Menu

```
View
└─ (Empty - Reserved for future features)
```

**Purpose:** Reserved for view-related features like:
- Zoom controls
- Panel visibility
- Layout presets
- Theme switching
- Font size adjustments

---

## 🛠️ Tools Menu

```
Tools
├─ Quest Editor                   [Ctrl+Q, E] 🪟 New Window
│  └─ Opens: Separate dialog window (1000x700)
│     ├─ Quest Tree Editor
│     ├─ Dialog Editor
│     └─ Quest Creator
│
├─ Spell Wizard                   [Ctrl+W]    🧙 Modal Dialog
│  └─ Opens: Step-by-step wizard
│     ├─ Spell Basics
│     ├─ Spell Mechanics
│     ├─ Visual Effects
│     ├─ Sound Effects
│     └─ Advanced Properties
│
├─ ─────────────────────────────────────────────
│
├─ Building Wizard                             🏰 Modal Dialog
│  └─ Opens: Building creation wizard
│
├─ ─────────────────────────────────────────────
│
├─ Armor Forge                    [Ctrl+A, F] 🛡️ Modal Dialog
│  └─ Opens: Armor creation interface
│
├─ Weapon Forge                   [Ctrl+W, F] ⚔️ Modal Dialog
│  └─ Opens: Weapon creation interface
│
├─ ─────────────────────────────────────────────
│
├─ NPC Creator                    [Ctrl+N, C] 👤 Modal Dialog
│  └─ Opens: NPC creation wizard
│
└─ ID Manager                     [Ctrl+I, M] 🆔 Modal Dialog
   └─ Opens: Unique ID management interface
```

**Purpose:** All content creation and editing tools

### Tool Categories:

#### 🎯 Content Editors
- **Quest Editor** - Edit quests, dialogs, and quest chains

#### ✨ Creation Wizards
- **Spell Wizard** - Create custom spells
- **Building Wizard** - Design buildings
- **NPC Creator** - Create NPCs and units

#### ⚒️ Item Forges
- **Armor Forge** - Craft armor pieces
- **Weapon Forge** - Craft weapons

#### 🔧 Utilities
- **ID Manager** - Manage unique identifiers

---

## ❓ Help Menu

```
Help
└─ About
   └─ Shows: Application information and credits
```

**Purpose:** Help and about information

---

## Window Behavior

### 🪟 Separate Window (Non-Modal)
- **Quest Editor**
  - Opens in its own dialog window
  - Main interface remains accessible
  - Can be kept open while working on other tasks
  - Window is reused if reopened

### 🧙 Modal Dialog
- **Spell Wizard**
- **Building Wizard**
- **Armor Forge**
- **Weapon Forge**
- **NPC Creator**
- **ID Manager**
  - Blocks main interface while open
  - Must be completed or canceled
  - Follows wizard/dialog pattern

---

## Keyboard Shortcuts Quick Reference

| Shortcut         | Action                    | Menu Location  |
|------------------|---------------------------|----------------|
| `Ctrl+O`         | Open CFF File             | File           |
| `Ctrl+S`         | Save                      | File           |
| `Ctrl+Shift+S`   | Save As                   | File           |
| `Ctrl+Q`         | Exit Application          | File           |
| `F5`             | Refresh View              | Edit           |
| `Ctrl+Q, E`      | Open Quest Editor         | Tools          |
| `Ctrl+W`         | Open Spell Wizard         | Tools          |
| `Ctrl+A, F`      | Open Armor Forge          | Tools          |
| `Ctrl+W, F`      | Open Weapon Forge         | Tools          |
| `Ctrl+N, C`      | Open NPC Creator          | Tools          |
| `Ctrl+I, M`      | Open ID Manager           | Tools          |

---

## Status Bar Tooltips

Each menu item has helpful status bar tooltips:

| Menu Item          | Tooltip                                              |
|--------------------|------------------------------------------------------|
| Quest Editor       | Edit quests with the integrated Quest Editor        |
| Spell Wizard       | Create custom spells with the Spell Wizard          |
| Building Wizard    | Create and edit custom buildings                    |
| Armor Forge        | Create and edit custom armor pieces                 |
| Weapon Forge       | Create and edit custom weapons                      |
| NPC Creator        | Create and edit custom NPCs with the NPC Creator    |
| ID Manager         | Manage unique IDs for all content types             |

---

## Design Rationale

### Why Tools Menu?
1. **Logical Grouping** - All creation and editing tools in one place
2. **Discoverability** - Easier for users to find content creation features
3. **Scalability** - Room to add more tools without cluttering other menus
4. **Industry Standard** - Follows UI conventions (e.g., Photoshop, Blender)

### Why Separate Window for Quest Editor?
1. **Non-Destructive** - Doesn't replace main interface
2. **Multi-Tasking** - Work on quests while referencing main data
3. **Flexibility** - Can be positioned on second monitor
4. **Workflow** - Matches how quest editing is typically done

### Why Modal for Wizards?
1. **Focused Workflow** - Step-by-step process needs attention
2. **Data Integrity** - Prevents conflicts from simultaneous editing
3. **User Guidance** - Linear progression through creation steps
4. **Consistent Pattern** - All wizards behave the same way

---

## Future Expansion Plans

### View Menu Ideas
```
View (Future)
├─ Zoom
│  ├─ Zoom In        [Ctrl++]
│  ├─ Zoom Out       [Ctrl+-]
│  └─ Reset Zoom     [Ctrl+0]
├─ ───────────────────────
├─ Panels
│  ├─ Category Tree  [☑ Toggle]
│  ├─ Element Table  [☑ Toggle]
│  └─ Properties     [☑ Toggle]
├─ ───────────────────────
├─ Layout
│  ├─ Default
│  ├─ Quest Editing
│  └─ Item Creation
└─ ───────────────────────
└─ Theme
   ├─ Dark
   └─ Light
```

### Tools Menu Additions
```
Tools (Future Additions)
├─ ... (existing tools)
├─ ───────────────────────
├─ Item Creator          [Advanced item editor]
├─ Creature Designer     [Creature/NPC designer]
├─ Effect Editor         [Visual effects editor]
├─ ───────────────────────
├─ Map Tools
│  ├─ Import Map
│  └─ Export Map
├─ ───────────────────────
└─ Batch Operations
   ├─ Bulk Edit
   ├─ Find & Replace
   └─ ID Reassignment
```

---

## Visual Comparison

### Before (Old Structure)
```
View: Quest Editor, Spell Wizard
Tools: Building Wizard, Armor Forge, Weapon Forge, NPC Creator, ID Manager
```

### After (New Structure)  
```
View: (Empty - Reserved)
Tools: Quest Editor, Spell Wizard, Building Wizard, Armor Forge, 
       Weapon Forge, NPC Creator, ID Manager
```

**All content creation tools now unified under Tools! 🎉**

---

**Version:** 1.0  
**Last Updated:** 2025  
**Status:** ✅ Implemented