# TirganachReloaded Quest Viewer

A standalone application for viewing SpellForce quest data with Lua file integration.

## Features

- **Quest Hierarchy Browser**: Navigate quests in a tree structure
- **Detailed Quest Information**: View comprehensive quest details including:
  - Basic information (ID, name, description)
  - Map locations and quest givers
  - Quest objectives and requirements
  - Quest rewards (XP, gold, items)
  - Quest dialogues with translations
  - Quest relationships (parent/sibling/child quests)
- **Automatic Cache Management**: Uses cached Lua files for fast loading
- **Cache Rebuilding**: Can rebuild cache from Lua source files

## Usage

### Quick Start

```bash
# Launch the quest viewer
./run_quest_viewer.sh

# Or use UV directly
uv run python quest_viewer.py
```

### Command Line Options

```bash
# Enable debug logging
./run_quest_viewer.sh --debug

# Rebuild quest cache from Lua files
./run_quest_viewer.sh --rebuild-cache

# Both options together
./run_quest_viewer.sh --debug --rebuild-cache
```

## Requirements

- Python 3.8+
- UV (recommended) or system Python with PySide6 installed
- SpellForce Lua source files (for cache building)

## Cache Management

The application automatically manages quest data caching:

- **Cache Location**: `src/TirganachReloaded/data/cache/`
- **Lua Cache**: SQLite database for parsed quest data
- **Quest Cache**: Pickle files for merged quest information

### Cache Sources

The application looks for Lua files in these locations:
1. `ModdingTools/SpellForceLUASources/`
2. `OriginalGameFiles/lua/`
3. Additional paths can be added as needed

## Project Structure

```
├── quest_viewer.py              # Main launcher script
├── run_quest_viewer.sh          # Shell launcher (UV aware)
└── src/TirganachReloaded/cff_editor/
    └── quest_viewer_app.py      # Main application code
```

## Data Integration

The viewer integrates multiple data sources:

- **CFF Quest Data**: Basic quest hierarchy and text
- **Lua Quest Files**: Objectives, requirements, rewards, dialogues
- **Enhanced Data**: Extended dialogues for major story quests
- **Reward Mappings**: Quest reward information

## Troubleshooting

### No Quest Data Available

If the viewer shows no quest data:

1. Ensure Lua source files are available in one of the expected locations
2. Try rebuilding the cache: `./run_quest_viewer.sh --rebuild-cache`
3. Check debug output: `./run_quest_viewer.sh --debug`

### Import Errors

If you get import errors:

1. Use the provided shell script (it handles paths correctly)
2. Or use UV: `uv run python quest_viewer.py`
3. Ensure you're in the project root directory

### Performance Issues

If loading is slow:

1. Enable caching (default) - it's much faster than parsing Lua files each time
2. Rebuild cache if data seems outdated: `./run_quest_viewer.sh --rebuild-cache`

## Development

The quest viewer is built using:

- **PySide6**: Qt GUI framework
- **TirganachReloaded**: Internal quest data models and services
- **SQLite**: Lua data caching
- **Loguru**: Debug logging

For debugging, use the `--debug` flag to see detailed logging output.