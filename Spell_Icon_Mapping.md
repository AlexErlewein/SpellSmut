# SpellForce Icon Mapping Analysis

## Summary of Findings So Far

### Icon Mapping Systems Identified

#### 1. Spell → Icon (System A)
- **Source**: `SpellName` table in `GameData.cff`
- **Field**: `spell_ui_handle` (e.g., `ui_spell_01`, `ui_spell_02`)
- **Chain**: `Spell.spell_id` → `Spell.spell_name_id` → `SpellName.spell_ui_handle`

#### 2. Item → Icon (System B)
- **Source**: `ItemUI` table in `GameData.cff`
- **Fields**:
  - `item_ui_index=1`: Base item icon (`ui_item_*` handle)
  - `item_ui_index>=2`: Overlay icons (often `ui_spell_*` handles for spell scrolls/runes)
  - `scaled_down` flag for overlay sizing

#### 3. Spell Scroll/Rune Correlation Bridge
- **Source**: `ItemInstall` table in `GameData.cff`
- **Mapping**: `inventory_item_id` (scroll/rune item) → `installed_item_id` (spell item of type `SPELL`)
- This provides the direct link between scroll/rune items and their corresponding spells

#### 4. Atlas Slicing Rules
| Atlas Type | Dimensions | Grid | Icon Size | Notes |
|------------|------------|------|-----------|-------|
| Items (`ui_itemNN.dds`) | 256×256 | 8×8 | 32px | Standard items, weapons, armor |
| Spells (`ui_spellNN.dds`) | 256×256 | 4×4 | 64px | + offset + 180° rotation |
| ITM (`itm/atlas_*.dds`) | 256×256 | 16×16 | 16px | Horizontal pairs/quads for wide weapons |

#### 5. Item Types for Spell-Related Items
| ItemType | Value | Description |
|----------|-------|-------------|
| SCROLL | 40 | Spell scroll with single-use spell |
| BLANK_SCROLL | 41 | Empty scroll for inscription |
| RUNE_INVENTORY | 47 | Rune in inventory (not socketed) |
| RUNE_ADDED | 48 | Rune socketed into equipment |
| SPELL | - | Item representing an actual spell (internal use) |

---

## Current Blockers

We were attempting to extract **correlation data** from `GameData.cff` to find concrete examples of:
1. Which `ui_spell_*` handles are used as overlays on scroll/rune items
2. The `item_id` ↔ `spell_id` mappings via `ItemInstall`

Both **SQLite** and **pickle cache** loading attempts hung (53+ seconds with no output), suggesting either:
- The cached data is corrupted/invalid
- Python execution environment issues
- The data models are incompatible with current code

---

## Next Steps (Blocked)

Per the TODO list, we need to:

1. **Get real correlation data** from `GameData.cff` using existing cached data (SQLite/pickle) or alternative methods
2. **Use correlation results** to implement/adjust icon resolution for scroll/rune spell overlays in the editor/mapper
3. **(Optional)** Leverage `ModdingTools/spellforce_data_editor` export capabilities for faster dumps

---

## What's Blocking Us

We cannot load the cached CFF data to perform the correlation analysis. We need an alternative approach—perhaps using the existing editor tools directly, or a fresh data export.

---

## Relevant Files

- `src/TirganachReloaded/tirganach/entities.py` - Defines `ItemUI`, `SpellName`, `ItemInstall`, `Item` entities
- `src/TirganachReloaded/tirganach/structure.py` - `GameData` class that parses `GameData.cff`
- `src/TirganachReloaded/cff_editor/data_model.py` - `CFFDataModel` with caching and icon resolution logic
- `src/TirganachReloaded/data/cache/db/cff_data.db` - SQLite cache (37MB, currently inaccessible)
- `src/TirganachReloaded/data/cache/GameData_*.pkl` - Pickle cache files (currently inaccessible)

---

*Generated: 2026-02-06*
