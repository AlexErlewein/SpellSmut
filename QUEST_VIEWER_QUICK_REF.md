# Quest Viewer - Quick Reference

## 🚀 Launch

```bash
cd "cleanup TirganachReloaded"
uv run python simple_quest_viewer.py
```

## 📊 Current Data

- **1040 Quests** - All from CFF with German names
- **450 Rewards** - XP, items, money from Lua
- **197 Mapped** - Rewards linked to quest IDs
- **47 Platforms** - All game areas covered

## 🎨 UI Features

### Tree View
- **Bold** = Main quest
- `Name [ID]` = Format
- ▶/▼ = Expand/collapse
- Right-click context menu

### Search & Filter
- Search box: Name or ID
- Location dropdown: Filter by platform
- Quest giver: Filter by NPC

### Details Panel
- Description (dark box)
- Location & Quest Giver
- Requirements
- Objectives
- **Rewards** (XP, Items, Money) ⭐
- **Dialogues** (German + English) ⭐
- Quest Relationships

## 💎 Rewards Display

### What Shows
- ✅ **XP**: 449 quests (formatted: 1,200)
- ✅ **Items**: 47 quests (item IDs)
- ✅ **Money**: 21 quests (Gold/Silver/Copper)
- ✅ **Reward Type**: Quest flag name

### Example
```
Rewards:
• XP: 1,200
• Gold: 2
• Silver: 50
• Items: 626, 707
• Reward Type: Geist In Der Mine
```

## 🗣️ Dialogues Display

### What Shows
- German text (original)
- English translation (when available)
- Speaker: Player (blue) or NPC (green)
- Type: [Story] marker for special dialogues

### Example
```
[Story] NPC: Ich suche nach Amras Rüstung!
(I'm searching for Amra's armor!)
```

## 🎯 Best Quests to View

| Quest ID | Name | Highlights |
|----------|------|-----------|
| 380-391 | Amra & Lea | Dialogues + translations |
| 357 | Wundtinktur | 30 XP |
| 36 | Geist in Mine | XP + money |
| 402 | Blut Adhira | 4000 XP |
| 279 | Steinbrecher | 800 XP |

## ⌨️ Keyboard Shortcuts

- `Ctrl+F` - Focus search box
- `Ctrl+E` - Export quest
- `Ctrl+R` - Reload data
- `↑/↓` - Navigate tree
- `←/→` - Collapse/expand node

## 🔧 Debug Mode

```bash
uv run python simple_quest_viewer.py --debug
```

Shows:
- Loading statistics
- Data source info
- Enhancement counts
- Missing data warnings

## 📁 Data Files

### Input Files
- `OriginalGameFiles/data/GameData.cff` - Quest data
- `ModdingTools/SpellForceLUASources/script/GdsQuestRewards.lua` - Rewards

### Output Files
- `src/TirganachReloaded/data/quest_rewards_complete.json` - Rewards DB
- `src/TirganachReloaded/data/quest_rewards_complete.csv` - Human readable

## 🔄 Extract Fresh Data

```bash
# Re-extract rewards from Lua files
python src/helper_tools/quest_extraction/extract_gds_quest_rewards.py
```

## 🎨 Theme Colors

- Background: `#2b2b2b` (dark gray)
- Text: `#e0e0e0` (light gray)
- Quest names: `#6fb3d2` (light blue)
- Rewards: `#4ec9b0` (green)
- Dialogues: `#c586c0` (purple)
- Requirements: `#f48771` (red)

## 📤 Export Options

### JSON Export
- Full quest data structure
- Includes all sub-quests (optional)
- Machine-readable format

### Markdown Export
- Human-readable format
- Formatted sections
- Easy to share/document

## 🐛 Common Issues

### No quests showing
→ Check `OriginalGameFiles/data/GameData.cff` exists

### No rewards showing
→ Run extraction script first

### "UNMAPPED" rewards
→ Need manual mapping (see CSV file)

### White background
→ Restart app, theme should auto-apply

## 📈 Stats at a Glance

```
Total Quests:     1040 (100%)
With XP:          449  (43%)
With Items:       47   (4.5%)
With Money:       21   (2%)
With Dialogues:   ~50  (special)
Mapped Rewards:   197  (43.8%)
Platforms:        47   (all)
```

## 🔗 Related Docs

- `QUEST_VIEWER_COMPLETE_V2.md` - Full user guide
- `QUEST_DATA_EXTRACTION_GUIDE.md` - Technical details
- `README.md` - Project overview

## ⚡ Quick Tips

1. Use **Expand All** to see full quest tree
2. **Search by ID** is fastest way to find specific quest
3. **Dark theme** is always on - no white backgrounds!
4. **Export** before making changes to quest data
5. **Debug mode** helps diagnose data issues
6. **Subquests** show under parent quests automatically

## 🎉 Version Info

**Quest Viewer V2** - Enhanced Edition
- ✅ Dark theme
- ✅ Full reward data (XP, items, money)
- ✅ Dialogues with translations
- ✅ Professional UI (no emojis)
- ✅ 450 quests with rewards
- ✅ Export functionality
- ✅ Search & filter

---

**Last Updated**: November 2024
**Status**: Production Ready
**Data Coverage**: 1040 quests, 450 rewards, 197 mapped