# Launch Quest Editor - Quick Start Guide

## 🚀 How to Launch the Quest Editor with Text Mode

The Quest Editor now includes a **Text Mode Overview** that displays dialogue trees in ASCII/text format alongside the visual editor.

### Option 1: Using UV (Recommended)

```bash
# Make sure you're in the project root
cd /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard

# Launch the quest editor
uv run python quest_creator.py
```

### Option 2: Using Python Directly

```bash
# Make sure dependencies are installed
pip install PySide6

# Launch the quest editor
python3 quest_creator.py
```

### Option 3: Direct Python Module Execution

```bash
# From project root
cd /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard

# Run directly
python3 -m TirganachReloaded.cff_editor.widgets.unified_quest_editor
```

## 📋 What You'll See

When the Quest Editor launches, you'll see:

1. **📋 Overview Tab** (NEW!) - Text mode dialogue tree overview
   - ASCII tree visualization
   - Node navigation
   - Search and filter
   - Jump to visual editor

2. **Basic Info Tab** - Quest metadata
3. **Location & NPC Tab** - Quest location and NPC assignment
4. **Objectives Tab** - Quest objectives and requirements
5. **🎨 Dialogue (Visual) Tab** - Visual node-based dialogue editor
6. **Rewards Tab** - Quest rewards configuration
7. **Preview Tab** - Quest preview
8. **Validation Tab** - Quest validation

## 🎯 Key Features

### Text Mode Overview
- **ASCII Tree Display**: See your dialogue tree in text format
- **Real-time Sync**: Changes in text mode reflect in visual editor
- **Search & Filter**: Find nodes quickly by text or speaker
- **Node Management**: Add, edit, delete nodes from text mode
- **Jump to Visual**: Switch to visual editor with one click

### Keyboard Shortcuts (Text Mode)
- `Ctrl+F` - Focus search box
- `Ctrl+J` - Jump to selected node
- `F5` - Refresh view

## 🔧 Troubleshooting

### "ModuleNotFoundError: No module named 'PySide6'"
```bash
# Install dependencies using uv
uv sync

# Or install manually
pip install PySide6
```

### Import Errors
Make sure you're running from the project root directory:
```bash
cd /Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard
```

### Path Issues
The launcher should handle paths automatically, but if you encounter issues:
```bash
# Check Python path
python3 -c "import sys; print(sys.path)"

# Verify project structure
ls -la src/TirganachReloaded/cff_editor/widgets/unified_quest_editor.py
```

## 📝 Quick Test

To verify everything works:

1. Launch the editor: `uv run python quest_creator.py`
2. Click "New Quest" in the quest browser
3. Go to "📋 Overview" tab
4. Click "+ Add Node" to create a dialogue node
5. Switch to "🎨 Dialogue (Visual)" tab to see it in visual mode
6. Make changes in visual mode and switch back to Overview to see sync

## 🎉 Success!

If the editor launches successfully, you should see:
- Quest browser on the left
- Editor tabs on the right
- "📋 Overview" tab as the first tab
- Status bar at the bottom showing "Ready"

---

**Need Help?** Check the documentation in `ProjectPlanning/Components/QuestSystem/` for detailed information about the quest editor features.

