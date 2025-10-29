# Examples Directory

This directory contains example scripts and utilities for working with SpellForce GameData.cff files.

## Export Scripts

### `export_to_json.py`
Exports GameData.cff to JSON format (73 MB, 2-3s load time).

**Usage:**
```bash
python export_to_json.py path/to/GameData.cff
```

**Output:** `exports/GameData.json`

---

### `export_to_xml.py`
Exports GameData.cff to XML format (63 MB, 10-15s load time).

**Usage:**
```bash
python export_to_xml.py path/to/GameData.cff
```

**Output:** `exports/GameData.xml`

---

## Example Scripts

### `example_use_json.py`
Demonstrates how to work with the exported JSON data.

**Features:**
- Loading JSON data
- Querying items
- Filtering by properties
- Data analysis examples

**Usage:**
```bash
python example_use_json.py
```

---

### `cff_modding_examples.py`
Collection of modding examples using the tirganach library.

**Examples Include:**
- Reading CFF files
- Modifying game data
- Creating new items
- Exporting modified data

**Usage:**
```bash
python cff_modding_examples.py
```

---

### `create_mod.py`
Template for creating a SpellForce mod.

**Features:**
- Mod structure setup
- Item creation
- Quest modification
- CFF export

**Usage:**
```bash
python create_mod.py
```

---

### `search_xml_data.py`
Search utility for GameData.xml files.

**Usage:**
```bash
python search_xml_data.py "search_term"
```

**Features:**
- Full-text search
- XPath queries
- Export search results

---

## Prerequisites

```bash
# Install dependencies
pip install PySide6 pillow pyyaml

# Or use uv
uv pip install PySide6 pillow pyyaml
```

## Related Documentation

- `../docs/CFF_EDITOR_README.md` - CFF Editor documentation
- `../docs/FORMAT_COMPARISON.md` - Format comparison guide
- `../docs/JSON_EXPORT_GUIDE.md` - JSON export details
- `../docs/XML_EXPORT_GUIDE.md` - XML export details
- `../docs/SCRIPTS_GUIDE.md` - Scripts usage guide

## Tips

1. **Start with JSON exports** for fastest loading and easiest querying
2. **Use XML exports** when you need human-readable diffs
3. **Check examples** before writing new scripts - many common tasks are already implemented
4. **Backup your GameData.cff** before running modification scripts

## Need Help?

- Check the main README: `../README.md`
- Read the installation guide: `../docs/INSTALLATION.md`
- Review the CFF format explanation: `../docs/CFF_FORMAT_EXPLANATION.md`
