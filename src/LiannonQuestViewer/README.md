# Liannon Quest Viewer

A standalone application for browsing and analyzing SpellForce quests with advanced search, filtering, and export capabilities.

## 🚀 Quick Start

### From this directory:
```bash
python simple_quest_viewer.py
```

### Or use the launcher:
```bash
python run_viewer.py
```

### With debug output:
```bash
python simple_quest_viewer.py --debug
```

## 📋 Features

### Quest Browsing
- ✅ View all 1000+ SpellForce quests
- ✅ Hierarchical tree view (main quests and sub-quests)
- ✅ German localized quest names
- ✅ Detailed quest information panel

### Search & Filter
- 🔍 **Search** by quest ID, name, or description
- 🗺️ **Filter by Platform/Location** (Liannon, Eloni, Leafshade, etc.)
- 👤 **Filter by Quest Giver** (NPC ID)
- ⚡ Real-time filtering as you type

### Quest Details
View comprehensive information for each quest:
- Quest name and ID
- Description
- Location/Platform
- Quest Giver (NPC)
- Parent Quest (if sub-quest)
- **Objectives** - What you need to do
- **Requirements** - Prerequisites to start
- **Rewards** - XP, gold, silver, copper, items
- **Dialogues** - NPC conversations

### Export
- 📄 Export to **JSON** format (structured data)
- 📝 Export to **Markdown** format (readable documentation)
- 📦 Export single quest or with all sub-quests

### User Experience
- 🎨 Professional dark theme (easy on the eyes)
- 💾 Persistent preferences (window state, last quest, filters)
- 🔄 Cache rebuild support for data updates

## 📁 Project Structure

```
src/LiannonQuestViewer/
├── README.md                    # This file
├── run_viewer.py                # Convenience launcher
└── simple_quest_viewer.py       # Main application (1450+ lines)
```

## 🗄️ Data Sources

The viewer uses cached data from:
- **Location**: `src/TirganachReloaded/data/cache/`
- **CFF Data**: Quest names, descriptions, hierarchy from GameData.cff
- **Lua Data**: Enhanced data (objectives, rewards, dialogues) from Lua scripts
- **Cache Files**:
  - `lua_quest_cache.db` - SQLite database with quest details
  - `GameData_*.pkl` - Pickled game data for fast loading

**Note**: The cache is shared with other tools in the project. This ensures consistency and avoids duplicate data.

## 🎮 Usage Examples

### Basic Usage
```bash
# Launch the viewer
python simple_quest_viewer.py

# Browse quests in the tree view
# Click on any quest to see details
```

### Search for Specific Quests
1. Use the search box at the top
2. Type quest ID (e.g., "1"), name (e.g., "Wolves"), or description keywords
3. Results filter in real-time

### Filter by Location
1. Use the "Platform" dropdown
2. Select a location (e.g., "Liannon (P1)")
3. Only quests from that location will show

### Export Quest Data
1. Select a quest in the tree
2. Click "Export Quest" button
3. Choose format (JSON or Markdown)
4. Choose whether to include sub-quests
5. Save to file

## 🔧 Advanced Features

### Rebuild Cache
If quest data is outdated or corrupted:
```bash
python simple_quest_viewer.py --rebuild-cache
```

This will:
1. Clear the existing cache
2. Re-parse Lua quest scripts
3. Rebuild the SQLite database

### Debug Mode
See detailed loading information and statistics:
```bash
python simple_quest_viewer.py --debug
```

Shows:
- Loading times for each data source
- Number of quests loaded
- Cache hit/miss statistics
- Performance metrics

## 🛠️ Technical Details

### Dependencies
- **PySide6** - Qt-based GUI framework
- **Python 3.8+** - Modern Python features
- **TirganachReloaded modules** - Data access layer

### Architecture
- **Data Model Layer**: CFFDataModel for game data access
- **Lua Parser**: LuaDataManager for enhanced quest data
- **Service Layer**: QuestDataService for data enrichment
- **UI Layer**: Qt widgets with custom styling

### Performance
- **Startup Time**: ~2-3 seconds (with cache)
- **Quest Loading**: ~1,040 quests in memory
- **Search**: Real-time filtering (< 100ms)
- **Cache Size**: ~130MB (GameData) + ~200KB (Lua cache)

## 🎨 Dark Theme Colors

The viewer uses a professional dark theme:
- Background: `#2b2b2b` (dark gray)
- Text: `#e0e0e0` (light gray)
- Widgets: `#1e1e1e` (darker gray)
- Selection: `#094771` (dark blue)
- Borders: `#3c3c3c` (medium gray)

## 📝 Keyboard Shortcuts

- **Ctrl+F**: Focus search box (planned)
- **Ctrl+E**: Export current quest (planned)
- **Ctrl+R**: Reload data (planned)
- **Esc**: Clear search (planned)

## 🐛 Troubleshooting

### "No quest data loaded"
- Check that `src/TirganachReloaded/data/cache/` exists
- Try running with `--rebuild-cache`
- Ensure GameData.cff is accessible

### "Import error: TirganachReloaded module not found"
- The viewer should be run from its directory or use `run_viewer.py`
- Check that `src/TirganachReloaded/` exists in the project

### "Cache directory created in wrong location"
- This has been fixed! Cache now always uses: `src/TirganachReloaded/data/cache/`
- Delete any `src/LiannonQuestViewer/src/` folders if they exist

### Slow startup
- First load builds cache (slower)
- Subsequent loads use cache (faster)
- Consider using SSD for better performance

## 🔗 Related Tools

- **Quest Editor**: `src/TirganachReloaded/cff_editor/simple_quest_viewer.py` (quest creation)
- **Quest Viewer App**: `quest_viewer.py` (framework version)
- **Quest Data Extraction**: `src/helper_tools/quest_extraction/`

## 📚 Documentation

For more information, see:
- **Project Root**: `docs/README.md`
- **Quest Viewer Guide**: `docs/QUEST_VIEWER_COMPLETE_V2.md`
- **Quest Quick Reference**: `docs/QUEST_VIEWER_QUICK_REF.md`

## 🤝 Contributing

This is part of the TirganachReloaded modding toolkit. For improvements:
1. Keep the cache path pointing to `src/TirganachReloaded/data/cache/`
2. Maintain the dark theme styling
3. Test with the full quest dataset (1000+ quests)
4. Update this README with any new features

---

**Version**: 1.0  
**Last Updated**: 2024-11-04  
**Maintained by**: SpellSmut Modding Tools  
**License**: Part of TirganachReloaded project