# GameData Format Comparison

Quick reference for choosing between JSON, XML, and CFF formats.

---

## File Statistics

| Format | File Size | Load Time | Created |
|--------|-----------|-----------|---------|
| **GameData.cff** | 19 MB | 30-60s | Original |
| **GameData.xml** | 63 MB | 10-15s | Via `export_to_xml.py` |
| **GameData.json** | 73 MB | 2-3s | Via `export_to_json.py` |

---

## Format Comparison

### JSON Format

**Pros:**
- ⚡ **Fastest loading** (2-3 seconds)
- 🐍 **Native Python support** - no extra libraries
- 🔍 **Easy querying** - list comprehensions work great
- 📊 **Best for data analysis**
- 🤖 **Machine-readable** - perfect for scripts

**Cons:**
- 📦 **Largest file** (73 MB)
- 📖 **Less human-readable** than XML
- ❌ **Read-only** - can't modify and save back to .cff

**Best For:**
- Data analysis and statistics
- Automated scripts
- Building tools (databases, spreadsheets)
- Quick queries and filters
- Web applications

**Example:**
```json
{
  "spell_id": 1,
  "mana": 15,
  "req1_class": {
    "_type": "enum",
    "class": "School",
    "name": "FIRE"
  }
}
```

---

### XML Format

**Pros:**
- 📖 **Most human-readable** structure
- 🔍 **Easy to search** in text editors
- 📝 **Good for documentation**
- 🌳 **Clear hierarchy** with tags

**Cons:**
- 🐢 **Slower loading** than JSON (10-15s)
- 📦 **Medium file size** (63 MB)
- 🔧 **Requires XML parser** for queries
- ❌ **Read-only** - can't save back to .cff

**Best For:**
- Documentation and reference
- Manual data inspection
- Creating wikis/guides
- Human review

**Example:**
```xml
<spell>
  <spell_id>1</spell_id>
  <mana>15</mana>
  <req1_class>School.FIRE</req1_class>
</spell>
```

---

### CFF Format (via tirganach)

**Pros:**
- ✅ **Only format that can modify** game data
- 💾 **Can save changes** back to .cff
- 📦 **Smallest file** (19 MB, compressed)
- 🎮 **What the game actually uses**

**Cons:**
- 🐌 **Slowest loading** (30-60 seconds)
- 🔒 **Binary format** - not human-readable
- 🐍 **Python library required** (tirganach)
- 🔧 **Complex API** to learn

**Best For:**
- Actually modding the game
- Making permanent changes
- Creating mod files
- Production modding workflow

**Example:**
```python
from tirganach import GameData

gd = GameData('GameData.cff')
spell = gd.spells[0]
spell.mana = 100
gd.save('GameData_modded.cff')
```

---

## When to Use Each Format

### Use JSON when:
- 🔍 Searching for specific data
- 📊 Analyzing game statistics
- 🤖 Building automated tools
- ⚡ Speed is important
- 🐍 Working in Python/JavaScript

### Use XML when:
- 📖 Reading documentation
- 👀 Manually browsing data
- 📝 Creating game guides
- 🔍 Using text editor search
- 📋 Need hierarchical view

### Use CFF (tirganach) when:
- ✏️ Actually modding the game
- 💾 Need to save changes
- 🎮 Creating playable mods
- 🔧 Developing mod tools

---

## Recommended Workflow

### Research Phase
1. **Export to JSON** for fast analysis
   ```bash
   python3 export_to_json.py
   ```

2. **Query data** with Python
   ```python
   import json
   data = json.load(open('GameData.json'))
   fire_spells = [s for s in data['spells'] if ...]
   ```

3. **Identify changes** you want to make

### Development Phase
4. **Use tirganach** to implement changes
   ```python
   from tirganach import GameData
   gd = GameData('GameData.cff')
   # Make modifications
   gd.save('GameData_mod.cff')
   ```

5. **Test in-game** with modified .cff

### Documentation Phase
6. **Export to XML** for documentation
   ```bash
   python3 export_to_xml.py
   ```

7. **Reference XML** when writing guides

---

## Quick Commands

```bash
# Export to JSON (fast loading)
python3 export_to_json.py

# Export to XML (readable)
python3 export_to_xml.py

# Use example scripts
python3 example_use_json.py

# Modify game data
python3 cff_modding_examples.py
```

---

## Data Coverage

All formats include the same data:

| Category | Records |
|----------|---------|
| Spells | 3,455 |
| Items | 7,101 |
| Creatures | 2,617 |
| Buildings | 207 |
| Armor | 635 |
| Weapons | 721 |
| Localization | 176,318 |
| **Total** | **~190,000** |

Plus: quests, maps, NPCs, skills, and more (40+ tables).

---

## Performance Tips

### JSON
```python
# ✅ Fast: Create index once
spell_by_id = {s['spell_id']: s for s in data['spells']}
spell = spell_by_id[42]

# ❌ Slow: Linear search every time
spell = next(s for s in data['spells'] if s['spell_id'] == 42)
```

### XML
```python
# ✅ Use XPath for queries
import xml.etree.ElementTree as ET
tree = ET.parse('GameData.xml')
spells = tree.findall('.//spell[mana>100]')
```

### CFF
```python
# ✅ Use tirganach's query methods
fire_spells = gd.spells.where(req1_class=School.FIRE)

# ❌ Don't iterate manually
fire_spells = [s for s in gd.spells if s.req1_class == School.FIRE]
```

---

## Memory Usage

| Format | Memory (Loaded) | Disk Space |
|--------|----------------|------------|
| JSON | ~300 MB | 73 MB |
| XML | ~400 MB | 63 MB |
| CFF | ~500 MB | 19 MB |

**Note:** CFF uses more memory because tirganach creates Python objects for everything.

---

## Summary

| Task | Best Format |
|------|-------------|
| Quick lookup | 🥇 JSON |
| Data analysis | 🥇 JSON |
| Building tools | 🥇 JSON |
| Reading docs | 🥇 XML |
| Manual browsing | 🥇 XML |
| Actually modding | 🥇 CFF (tirganach) |
| Saving changes | 🥇 CFF (tirganach) |

**The Bottom Line:**
- **JSON** = Read-only, super fast queries
- **XML** = Read-only, human-friendly
- **CFF** = Read/write, slow but only way to mod

---

**See Also:**
- [JSON Export Guide](JSON_EXPORT_GUIDE.md)
- [XML Export Guide](XML_EXPORT_GUIDE.md)
- [CFF Editor README](CFF_EDITOR_README.md)