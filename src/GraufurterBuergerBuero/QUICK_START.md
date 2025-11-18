# Quick Start Guide - Graufurter Bürger Büro

## What You'll See On Startup

When you first launch Graufurter Bürger Büro, you'll see:

```
Left Panel: "NPCs (0 loaded)"
  └─ "No NPCs created yet" (in gray)

Right Panel: "NPC Details" (empty)

Status Bar: "Viewing: Default Game Data"
```

This is **normal** - you haven't created any custom NPCs yet!

---

## Your First Steps

### 1. Create Your First NPC

Click the **"Create NPC"** button to launch the NPC Creation Wizard:

- **Page 1**: Choose creation mode (Create New)
- **Page 2**: Enter basic identity (name, type, class, level)
- **Page 3**: Set base stats (7 attributes)
- **Page 4**: Configure combat stats
- **Page 5**: Choose appearance and voice
- **Page 6**: Select equipment
- **Page 7**: Set behavior and AI
- **Page 8**: Review and finish

### 2. Browse Your NPCs

After creating NPCs:
- They appear in the left tree panel
- Organized by type (Hostile, Friendly, Neutral, etc.)
- Click any NPC to view details in the right panel

### 3. Search & Filter

Use the search bar to find NPCs by:
- Name
- Type
- Class

### 4. Edit, Duplicate, Delete

Select an NPC and click:
- **"Browse NPCs"** → Opens enhanced browser with edit/duplicate/delete options
- **Edit**: Modify the NPC's properties
- **Duplicate**: Clone as a template
- **Delete**: Remove custom NPCs

---

## Understanding the Interface

### Tree Panel States

**Empty (0 NPCs):**
```
NPCs (0 loaded)
└─ No NPCs created yet
```

**With Custom NPCs:**
```
NPCs (5 loaded)
├─ Friendly (3 NPCs)
│  ├─ Guard Captain Marcus (Warrior, Level 10)
│  ├─ Healer Elena (Cleric, Level 8)
│  └─ Merchant Tobias (Merchant, Level 5)
├─ Hostile (2 NPCs)
│  ├─ Bandit Leader (Rogue, Level 12)
│  └─ Dark Mage (Mage, Level 15)
```

### Status Bar Messages

- **"Ready - Graufurter Bürger Büro Loaded"** → App initialized
- **"Loading NPC data..."** → Reading custom NPCs from JSON
- **"Building NPC trees..."** → Populating the tree view
- **"Graufurter Bürger Büro Ready"** → Ready to use

### Debug Output (Console)

When you run with `uv run`, you'll see:
```
2025-11-17 16:45:10 | INFO | Logging system initialized
NPC data file is empty - no NPCs have been created yet
2025-11-17 16:45:10 | INFO | ✓ Loaded 0 NPCs from default data
2025-11-17 16:45:10 | INFO | No custom NPCs found. Click 'Create NPC' to create your first NPC!
```

This is **normal** for first-time use!

---

## Data Storage

Your custom NPCs are saved in:
```
src/GraufurterBuergerBuero/npcs/custom_npcs.json
```

Initially this file contains:
```json
[]
```

After creating NPCs, it will look like:
```json
[
  {
    "npc_id": 40000,
    "name": "Guard Captain Marcus",
    "npc_type": "friendly",
    "character_class": "warrior",
    "level": 10,
    ...
  }
]
```

---

## ID Allocation

Custom NPCs use IDs in the range **40000-49999**:
- Your first NPC: `40000`
- Your second NPC: `40001`
- And so on...

The ID Manager ensures no conflicts with game NPCs (1-39999).

---

## Load CFF File Button (Note)

The **"Load CFF File"** button is currently a placeholder. 

For now, it will:
- Show a file picker
- Log a warning: "CFF loading not yet implemented"
- Continue loading custom NPCs from JSON

This feature can be added later with a proper CFF NPC loader.

---

## Common Questions

### Q: Why does it say "0 loaded"?
**A:** You haven't created any custom NPCs yet. Click "Create NPC" to start!

### Q: Where are game NPCs?
**A:** Currently only shows custom NPCs. Game NPC browsing will be added in a future update.

### Q: Can I export to CFF?
**A:** Yes! The NPC creation wizard includes CFF export in the final step.

### Q: What if I close the wizard?
**A:** No problem! Any allocated ID is released automatically if you cancel.

### Q: Can I edit NPCs later?
**A:** Yes! Use "Browse NPCs" → Select NPC → "Edit Selected"

---

## Quick Commands

```bash
# Run the application
uv run graufurter_buerger_buero.py

# Run with debug logging
uv run graufurter_buerger_buero.py --debug

# Test imports (no GUI)
uv run test_imports.py
```

---

## Next Steps

1. **Create your first NPC** using the wizard
2. **Browse and inspect** your NPCs
3. **Edit and refine** NPC properties
4. **Export to CFF** for game integration
5. **Duplicate NPCs** as templates for similar characters

---

## Need Help?

- See `README.md` for full documentation
- Check `SETUP_SUMMARY.md` for technical details
- Review `/docs/` for modding guides

---

**Remember**: The tool is designed for creating **custom NPCs** (ID 40000+). 
Game NPCs can be viewed with the full TirganachReloaded CFF Editor.

Happy NPC creating! 🎭
