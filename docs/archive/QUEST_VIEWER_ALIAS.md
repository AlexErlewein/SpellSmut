# Quest Viewer Alias Setup

## 🚀 Quick Launch Options

You now have multiple convenient ways to launch the TirganachReloaded Quest Viewer with the Quest Creation Wizard!

### Option 1: Shell Alias (Recommended)

After adding the alias to your `.zshrc`, you can now simply run:

```bash
questview
```

This will:
- Automatically navigate to the project directory
- Launch the quest viewer with the Quest Creation Wizard
- Support any command-line arguments (like `--debug`)

**Usage:**
```bash
questview              # Launch normal mode
questview --debug      # Launch with debug logging
```

### Option 2: Direct Script Execution

You can also run the shell script directly:

```bash
./questview.sh
```

**Usage:**
```bash
./questview.sh         # Launch normal mode
./questview.sh --debug # Launch with debug logging
```

### Option 3: Full Command (Traditional)

If you prefer the full command:

```bash
uv run python src/TirganachReloaded/cff_editor/simple_quest_viewer.py
```

## 📁 Files Created

1. **`~/.zshrc`** (modified) - Added `questview` alias
2. **`questview.sh`** (new) - Executable shell script for direct launch

## 🔄 Setup Instructions

### For New Terminal Sessions

The alias will automatically work in new terminal sessions. If you want to use it immediately:

```bash
source ~/.zshrc
```

### For Current Terminal

Run this to activate the alias in your current session:

```bash
source ~/.zshrc
```

## ✅ Verification

To verify the alias is working:

```bash
alias | grep questview
```

You should see:
```
questview='cd "/Users/alex/Desktop/code/Others/SpellSmut.worktree/cleanup TirganachReloaded" && uv run python src/TirganachReloaded/cff_editor/simple_quest_viewer.py'
```

## 🎯 Features

The Quest Viewer includes:

- ✅ **Quest Creation Wizard** - Click "Create Quest" to launch the 5-page wizard
- ✅ **Quest Tree Navigation** - Browse existing quests hierarchically
- ✅ **Quest Details View** - View comprehensive quest information
- ✅ **Real-time Updates** - Quest tree refreshes when new quests are created
- ✅ **Debug Mode** - Use `questview --debug` for detailed logging

## 🎉 Quick Start

1. Open a new terminal (or run `source ~/.zshrc`)
2. Type `questview` and press Enter
3. Click "Create Quest" to start creating your first quest!
4. Complete the 5-page wizard to create custom quests

Enjoy your new Quest Creation Wizard! 🚀