# Quest Editor Quick Start Guide

## 🚀 Getting Started in 3 Steps

### Step 1: Load Your CFF File
```
File → Open CFF...
```
Select your `GameData.cff` file and wait for it to load.

### Step 2: Load Quest Scripts (Optional but Recommended)
```
Tools → Load Lua Quest Scripts...
```
- Navigate to: `OriginalGameFiles/modding/Original Scripts/script/`
- Select the **script** folder
- Click "Select Folder"
- ✅ You'll see: "Successfully loaded quest data from X quest(s)"

### Step 3: Open Quest Editor
```
Tools → Quest Editor    (or press Ctrl+Q, E)
```

---

## 📊 Quest Editor Tabs

### Tab 1: Quest Hierarchy
**What it shows**: Tree view of all quests with parent-child relationships

**How to use**:
- Browse main quests and sub-quests
- Click any quest to select it
- Use "Expand All" / "Collapse All" buttons

**Tip**: The tree loads automatically now! No need to click around.

### Tab 2: Quest Details ⭐ Most Useful
**What it shows**: Complete quest information

**Sections**:
- 📋 **Basic Info**: Quest name, description, IDs
- 🎯 **Quest Giver**: NPC who gives the quest (from Lua)
- ⚠️ **Requirements**: What player needs to accept quest (from Lua)
- ✅ **Objectives**: What player must do (from Lua)
- 🎁 **Rewards**: XP, money, items (from Lua)
- 💬 **Dialogues**: Related dialogue text
- 🔗 **Relationships**: Parent/child quests

**What to look for**:
- `[Lua]` prefix = Data from Lua scripts ✨
- `(check Lua scripts)` = Data might be in Lua but not loaded

### Tab 3: Dialog Editor
**What it shows**: Dialogue branching editor

**Use for**: Viewing and editing complex dialogue trees

### Tab 4: Quest Creator
**What it shows**: Create new quests

**Use for**: Building custom quests from scratch

---

## 🔍 Reading Quest Data

### Understanding Quest Objectives (from Lua)

```
[Lua] Defeat 5 Goblins (Type: Kill) - Target: Goblin - Count: 5
```
- **Defeat 5 Goblins** = Player-readable description
- **Type: Kill** = Objective category
- **Target: Goblin** = What to kill
- **Count: 5** = How many

### Understanding Quest Rewards (from Lua)

```
XP: 500 XP [from Lua]
Money: 5 Gold, 10 Silver, 25 Copper [from Lua]
Items: [Lua] Item ID: 626
```
- Look up Item IDs in the Items table to see what item it is

### Understanding Requirements (from Lua)

```
[Lua] Player must be level 10 or higher (Type: Level) - Value: 10
```
- Player must meet this before accepting the quest

---

## 🎯 Common Tasks

### Finding a Specific Quest
1. Open Quest Editor
2. Go to **Quest Hierarchy** tab
3. Use Ctrl+F (if search is available) or scroll through tree
4. Click on quest name

### Viewing Quest Rewards
1. Select quest in hierarchy
2. Switch to **Quest Details** tab
3. Scroll to **Rewards** section
4. Check for `[from Lua]` indicator

### Checking Quest Prerequisites
1. Select quest in hierarchy
2. Go to **Quest Details** tab
3. Look at **Requirements to Accept** section
4. Also check **Quest Relationships** → Parent Quest

### Exporting Quest Information
1. Select quest
2. View details in **Quest Details** tab
3. Copy/paste from text fields as needed
4. *(Note: Full export feature planned for future)*

---

## ⚙️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Q, E` | Open Quest Editor |
| `Ctrl+L, Q` | Load Lua Quest Scripts |
| `Ctrl+O` | Open CFF File |
| `Ctrl+S` | Save Changes |
| `F5` | Refresh View |

---

## 🐛 Troubleshooting

### Tree View is Empty
**Solution**: 
- Make sure a CFF file is loaded
- Check if "quests" category has data
- Try F5 to refresh

### No Lua Data Showing
**Symptom**: No `[Lua]` prefixes in Quest Details

**Solutions**:
1. Load Lua scripts: `Tools → Load Lua Quest Scripts...`
2. Verify you selected the correct directory (should contain P1, P2, etc.)
3. Some quests genuinely have no Lua data (check original files)

### "Lua Data Manager Not Available"
**Solution**: This means the Lua parser module has an import error
- Check console for detailed error message
- Verify `lua_parser` directory exists in `cff_editor/`

### Quest Details Shows "Unknown (check Lua scripts)"
**Meaning**: This data is typically in Lua, but either:
- Lua scripts weren't loaded
- Quest ID doesn't match between CFF and Lua
- Parser couldn't extract the data

**Solution**: Load Lua scripts and check if data appears

---

## 💡 Pro Tips

### Tip 1: Load Lua Scripts First
For best experience, load Lua scripts immediately after loading CFF. This gives you complete quest information from the start.

### Tip 2: Keep Quest Editor Open
The Quest Editor window can stay open while you work. It updates automatically when you select different quests.

### Tip 3: Use Both CFF and Lua Data
- CFF has the quest structure and text
- Lua has the game mechanics
- Together they give you the complete picture

### Tip 4: Cache is Your Friend
After first Lua load (slow), subsequent loads are fast because data is cached. You don't need to reload Lua scripts every time you open the editor.

### Tip 5: Platform IDs
- P1 = Liannon
- P2 = Eloni
- P3 = Leafshade
- P5 = Shiel
- P7 = Greyfell

Helps you know which map the quest is on!

---

## 📚 Need More Help?

- **Full Documentation**: See `LUA_QUEST_INTEGRATION.md`
- **Technical Details**: See `QUEST_EDITOR_FIXES.md`
- **Issues/Questions**: Check console output for error details

---

## ✨ New Features Summary

### What's New
✅ **Auto-loading tree view** - No more clicking around!  
✅ **Lua quest data integration** - See objectives, requirements, and rewards  
✅ **Smart caching** - Fast loading after first parse  
✅ **Clear data sources** - `[Lua]` tags show where data comes from  

### What's Next
🔜 Edit Lua data directly from editor  
🔜 Generate new quest Lua scripts  
🔜 Quest template library  
🔜 Dependency graph visualization  

---

**Happy Quest Editing! 🎮**