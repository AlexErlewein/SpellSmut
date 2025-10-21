# CRUSH.md - SpellSmut Development Guide

## Build/Test Commands

```bash
# Python (TirganachReloaded CFF editor)
cd TirganachReloaded
python test_cff_extract.py                    # Test CFF loading
python export_to_json.py                      # Export GameData to JSON
python export_to_xml.py                       # Export GameData to XML
python cff_modding_examples.py                # Run modding examples
python run_cff_editor.py                      # Launch GUI editor

# Run single test (no test framework - manual testing only)
python -c "from tirganach import GameData; gd = GameData('path/to/GameData.cff'); print('OK')"
```

## Code Style

### Python
- **Indentation**: 4 spaces (never tabs)
- **Line length**: 100 characters max
- **Imports**: Standard library, third-party, local (separated by blank lines)
- **Types**: Use type hints for function signatures
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Docstrings**: Use triple quotes for module/class/function docs

### Lua (Lua 4.0 - NOT modern Lua!)
- **Indentation**: 4 spaces
- **Functions**: `PascalCase()` for global, `snake_case()` for local
- **Variables**: `snake_case` for local, `PascalCase` for global tables
- **Constants**: `UPPER_SNAKE_CASE`
- **Syntax**: Use `getn(table)` not `#table`, `tremove()` not `table.remove()`
- **Upvalues**: Use `%variable` syntax for closures
- **Comments**: Explain C++ engine interactions and complex logic

### File Organization
- **Planning docs**: `ProjectPlanning/` (never in root or docs/)
- **Documentation**: `docs/` with subfolders by topic
- **Source code**: `src/` with subfolders by module
- **Never modify**: `OriginalGameFiles/` (pristine reference only)

## Common Patterns

### Python CFF Editing
```python
from tirganach import GameData
from tirganach.types import *

gd = GameData('path/to/GameData.cff')
items = gd.items.where(item_type=ItemType.EQUIPMENT)
gd.save('path/to/GameData_modified.cff')
```

### Lua Asset Loading (Lua 4.0)
```lua
local files = dir_readdirectory("path\\*.ext")
local manifest = strsplit("\n", gsub(readfile("manifest.txt"), "\r", ""))
local assets = list_concat(files, manifest)
```

## Critical Rules
- Use Lua 4.0 syntax only (no modern Lua 5.x features)
- Windows paths use backslashes in Lua scripts
- Always backup GameData.cff before modifications
- Test mod compatibility after changes
- Update docs/index.md when adding new guides
- Place planning docs in ProjectPlanning/, not docs/
