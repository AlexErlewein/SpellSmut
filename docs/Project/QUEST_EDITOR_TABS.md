# Quest Editor Tabs - Complete Guide

## Overview

When you open the Quest Editor from the menu (Tools → Quest Editor), you see **four tabs** at the top:

1. **Quest Hierarchy** - Browse all quests in a tree structure
2. **Quest Details** - Comprehensive quest information (NEW!)
3. **Dialog Editor** - Create standalone dialogues
4. **Quest Creator** - Generate Lua quest scripts

This document explains what each tab does and how to use them effectively.

---

## The Four Tabs Explained

### 1. Quest Hierarchy

**Purpose:** Browse and navigate the complete quest structure in a hierarchical tree view.

**Features:**
- Tree view showing all main quests with their sub-quests
- Expandable/collapsible branches
- Columns: Quest Name, Quest ID, Type, Parent ID, Order Index
- Bold formatting for main quests and sub-quests with children
- Quick controls: "Expand All" and "Collapse All" buttons
- Auto-loads when you switch to the tab
- Same efficient view as the main editor

**Status:** ✅ **Fully working** - Auto-loads, no manual refresh needed!

**When to Use:**
- Browsing the complete quest structure
- Understanding quest parent-child relationships
- Finding specific quests by ID
- Viewing the quest hierarchy outside the main editor
- Getting an overview of all quests at once

**How to Use:**
1. Open Quest Editor (menu or from main editor)
2. Click "Quest Hierarchy" tab
3. Quests load automatically
4. Click any quest to see details in other tabs
5. Use "Expand All" / "Collapse All" for navigation

---

### 2. Quest Details (NEW!)

**Purpose:** View comprehensive information about a selected quest in one place.

**Features:**

#### Basic Quest Information
- Quest ID, Name ID, Description ID
- Localized quest name and description
- Full quest text display

#### Quest Giver
- NPC name and ID who gives the quest
- Location/Map where quest starts
- Quest giver information

#### Requirements to Accept Quest
- Minimum level required
- Required previous quest (prerequisites)
- Other special requirements

#### Quest Objectives (Completion Requirements)
- All objectives needed to complete the quest
- Objective types (Kill, Collect, Talk, etc.)
- Target NPCs/items
- Required counts

#### Quest Rewards
- Experience (XP) reward
- Money rewards (Gold, Silver, Copper)
- Item rewards with IDs
- Complete reward breakdown

#### Quest Dialogues
- All dialogues associated with the quest
- Shows both NPC and Player dialogue options
- Player choices displayed in italic
- Full conversation tree related to quest

#### Quest Relationships
- Parent quest (if sub-quest)
- All sub-quests (if parent)
- Quest hierarchy position

**Status:** ✅ **Fully working**

**When to Use:**
- Reviewing all aspects of a quest
- Understanding quest requirements
- Checking quest rewards
- Viewing quest dialogues in context
- Planning quest modifications
- Debugging quest issues

**How to Use:**
1. Select a quest in Quest Hierarchy tab (or main editor)
2. Switch to "Quest Details" tab
3. Scroll through all sections
4. All information auto-updates when you select different quests

---

### 3. Dialog Editor

**Purpose:** Create and edit dialogue trees independent of specific quests.

**Features:**
- Full dialog branching editor
- Create NPC dialogues
- Add player choice options (branching conversations)
- Build multi-level conversation trees
- Preview entire conversations
- Edit dialogue text inline
- Save dialogues to CFF

**Dialog Types:**
- **NPC Dialogues**: What NPCs say (bold text)
- **Player Choices**: Response options for players (italic text)
- **Branching Paths**: Different conversations based on player choices

**Status:** ✅ **Fully working**

**When to Use:**
- Creating generic NPC dialogues
- Building dialogue templates
- Testing dialogue flows
- Working on dialogues before assigning to quests
- Creating complex branching conversations

**How to Use:**
1. Click "Dialog Editor" tab
2. Click "Add Root Dialog"
3. Enter a base name (e.g., "questname")
4. Right-click to add NPC responses or Player choices
5. Build your conversation tree
6. Click "Save Changes"

**Context Menu Options:**
- **Add NPC Response** - NPC's next line
- **Add Player Choice** - Option for player to respond
- **Edit Dialog Text** - Change the dialogue text
- **Delete Dialog** - Remove dialogue and all branches

---

### 4. Quest Creator

**Purpose:** Generate complete quest Lua scripts from a form-based interface.

**Features:**
- Step-by-step quest creation wizard
- Six organized tabs:
  - **Basic Info**: Quest ID, name, description, type, map
  - **Objectives**: Define quest goals and targets
  - **Rewards**: XP, items, money
  - **Requirements**: Prerequisites and conditions
  - **NPCs & Dialog**: Link dialogues
  - **Lua Preview**: See generated script
- Generate complete Lua quest script
- Copy script to clipboard
- Good for prototyping and learning

**Status:** ✅ **Fully working**

**Output Example:**
```lua
Quest.Q1001 = {
    name = "The Lost Sword",
    description = "Find the legendary sword",
    objectives = {
        {type = "Kill", target = "Bandit", count = 10}
    },
    rewards = {
        xp = 1000,
        items = {100, 200},
        gold = 50
    }
}
```

**When to Use:**
- Creating new quests from scratch
- Generating Lua quest scripts for mods
- Prototyping quest designs
- Learning quest structure
- Creating quest templates

**Note:** This generates Lua scripts but doesn't directly edit CFF quest data. Copy the generated script for use in your mod.

---

## Which Tab Should You Use?

### For Browsing Quests:
✅ **Quest Hierarchy tab**
- Quick overview of all quests
- See parent-child relationships
- Navigate quest structure

✅ **Main Editor** (click "quests" category)
- Same hierarchy view plus editing

### For Viewing Complete Quest Information:
✅ **Quest Details tab**
- See everything about a quest in one place
- Giver, requirements, objectives, rewards, dialogues, relationships
- Best for understanding what a quest does

### For Creating/Editing Dialogues:
✅ **Dialog Editor tab**
- Standalone dialogue creation
- Build branching conversations
- Create player choice trees

### For Generating Quest Scripts:
✅ **Quest Creator tab**
- Form-based quest design
- Generates Lua scripts
- Good for learning and prototyping

---

## Recommended Workflows

### Workflow 1: Reviewing an Existing Quest

1. **Quest Hierarchy tab** → Select the quest you want to review
2. **Quest Details tab** → Read all information about the quest
3. Take notes on what needs to be changed

### Workflow 2: Understanding Quest Structure

1. **Quest Hierarchy tab** → See all quests and their relationships
2. Click on a main quest to see its sub-quests
3. **Quest Details tab** → Check requirements and prerequisites
4. Build a mental map of quest flow

### Workflow 3: Creating Dialogues for a Quest

1. **Dialog Editor tab** → Create dialogue tree
2. Add NPC dialogues and player choices
3. Save dialogues
4. Link to quest in main editor

### Workflow 4: Planning a New Quest

1. **Quest Creator tab** → Design quest structure
2. Fill in all details (objectives, rewards, etc.)
3. Generate Lua script
4. Review in **Quest Details tab** format
5. Copy and integrate into mod

### Workflow 5: Finding Quest Dialogues

1. **Quest Hierarchy tab** → Select a quest
2. **Quest Details tab** → Scroll to "Quest Dialogues" section
3. See all dialogues with player choices
4. Italic text = Player choices, Normal text = NPC dialogues

---

## Understanding Quest Information

### Quest Requirements

**Requirements to Accept:**
- What the player needs BEFORE accepting the quest
- Examples: Level requirement, previous quest completed

**Requirements to Complete (Objectives):**
- What the player needs to DO to finish the quest
- Examples: Kill 10 enemies, collect 5 items, talk to NPC

### Quest Dialogues

- **Start Dialogue**: When player first talks to quest giver
- **Progress Dialogue**: During quest
- **Completion Dialogue**: When turning in quest
- **Player Choices**: Options that affect conversation flow

### Quest Hierarchy

```
Main Quest (ID: 1000)
├─ Sub-quest 1 (ID: 1001)
│  └─ Sub-sub-quest (ID: 1002)
└─ Sub-quest 2 (ID: 1003)
```

- **Main Quest**: No parent (root level)
- **Sub-quest**: Has a parent quest
- **Sub-quest with children**: Can be both child and parent

---

## Tab Order and Navigation

The tabs are organized by workflow:

1. **Quest Hierarchy** → Browse and select
2. **Quest Details** → Review selected quest
3. **Dialog Editor** → Create/edit dialogues
4. **Quest Creator** → Generate new quests

💡 **Tip:** Select a quest in Quest Hierarchy, then switch to Quest Details to see all information!

---

## Auto-Loading and Refresh

### Automatic Loading:
- ✅ Quest Hierarchy auto-loads when tab is shown
- ✅ Quest Details auto-updates when quest is selected
- ✅ All tabs refresh when language is changed

### Manual Refresh:
- Click "Expand All" / "Collapse All" to refresh Quest Hierarchy
- Select a different quest and back to refresh Quest Details

---

## Common Tasks

### Task: Find what a quest requires
→ Quest Hierarchy → Select quest → Quest Details → "Requirements to Accept Quest" section

### Task: See quest rewards
→ Quest Hierarchy → Select quest → Quest Details → "Quest Rewards" section

### Task: View quest dialogues with player choices
→ Quest Hierarchy → Select quest → Quest Details → "Quest Dialogues" section
(Player choices shown in italic)

### Task: Understand quest objectives
→ Quest Hierarchy → Select quest → Quest Details → "Quest Objectives" section

### Task: Find quest giver NPC
→ Quest Hierarchy → Select quest → Quest Details → "Quest Giver" section

### Task: See sub-quests
→ Quest Hierarchy → Expand main quest to see branches
OR Quest Details → "Quest Relationships" → Sub-quests list

### Task: Create branching dialogue
→ Dialog Editor → Add Root Dialog → Right-click → Add Player Choice → Add NPC Response

---

## Tips and Tricks

1. **Player Choices are Always Italic** - Easy to spot in dialogue trees
2. **Bold = Important** - Main quests and parent sub-quests are bold
3. **Use Quest Details for Overview** - One-stop-shop for all quest info
4. **Quest Creator for Learning** - Generate example quests to understand structure
5. **Select in Hierarchy, View in Details** - Best workflow for reviewing quests

---

## Known Limitations

### Quest Details Tab:
- Some quest data fields may not be in the CFF (depends on game version)
- Dialogue-quest relationships are detected by naming patterns
- NPC names may not always resolve correctly

### Dialog Editor:
- Parent tracking in conversation preview is simplified
- No visual flow diagram (yet)

### Quest Creator:
- Generates Lua scripts, doesn't directly modify CFF
- Manual integration required

---

## Comparison with Main Editor

| Feature | Quest Editor | Main Editor |
|---------|--------------|-------------|
| Quest Hierarchy | ✅ Standalone view | ✅ Column 2 |
| Quest Info | ✅ Comprehensive tab | ✅ Column 3 (basic) |
| Quest Dialogues | ✅ In Quest Details | ✅ Column 4 |
| Quest Properties | ❌ Read-only | ✅ Editable |
| Dialogue Creation | ✅ Dedicated tab | ✅ In quest context |
| Lua Generation | ✅ Quest Creator | ❌ Not available |

**Best Practice:** Use **Main Editor** for editing, **Quest Editor** for reviewing and creating.

---

## Summary

### Quick Reference

| What You Want to Do | Use This Tab |
|---------------------|--------------|
| Browse quest tree | Quest Hierarchy |
| See all quest info | Quest Details |
| Check requirements | Quest Details → Requirements |
| See quest rewards | Quest Details → Rewards |
| View quest dialogues | Quest Details → Dialogues |
| Find player choices | Quest Details → Dialogues (italic) |
| Create dialogues | Dialog Editor |
| Generate Lua script | Quest Creator |

### Tab Status

- 🟢 **Quest Hierarchy**: Working - Auto-loads
- 🟢 **Quest Details**: Working - Comprehensive view
- 🟢 **Dialog Editor**: Working - Full branching support
- 🟢 **Quest Creator**: Working - Lua generation

All tabs are fully functional and ready to use! 🎉

---

## See Also

- [Dialogue System Documentation](DIALOGUE_SYSTEM.md) - Player choices and branching
- [Quest Hierarchy Test Implementation](../tests/quest_hierarchy/README.md) - Technical details
- [Main Editor User Guide](USER_GUIDE.md) - Complete editor documentation