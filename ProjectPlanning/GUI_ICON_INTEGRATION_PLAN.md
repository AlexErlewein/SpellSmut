# GUI Editor - Icon Integration Plan

## Problem Statement
We need to display item/weapon/spell icons in the GUI editor alongside the data being edited, so users can visually identify what they're modifying.

## Data Structure Analysis

### 1. The Link: `item_ui` Table
**Location**: `GameData.json` → `item_ui` category (8,311 entries)

**Structure**:
```json
{
  "item_id": 27,
  "item_ui_index": 1,
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame",
  "scaled_down": 0
}
```

**Key Fields**:
- `item_id`: Links to items/weapons/armor tables
- `item_ui_handle`: The UI asset name (without extension)
- `item_ui_index`: Multiple icons per item (1=main, 2=overlay/spell)
- `scaled_down`: Whether icon should be scaled (0=no, 1=yes)

### 2. Spell UI Links
**Location**: `GameData.json` → `spell_names` category (235 entries)

**Structure**:
```json
{
  "spell_name_id": 1,
  "text_id": 1234,
  "spell_ui_handle": "ui_spell_EM_Fire_FireBurst",
  "magic_type": "Fire",
  ...
}
```

**Key Field**:
- `spell_ui_handle`: Direct reference to spell icon

### 3. Extracted UI Assets
**Location**: `ExtractedAssets/UI/extracted/`

**Directory Structure**:
```
UI/extracted/
├── items/
│   ├── png/
│   │   ├── ui_item0.png
│   │   ├── ui_item1.png
│   │   └── ...
│   └── dds/
│       └── (original DDS files)
├── spells/
│   ├── png/
│   │   ├── ui_spell0.png
│   │   ├── ui_spell1.png
│   │   └── ...
│   └── dds/
└── other categories...
```

**Note**: Files are numbered (ui_item0.png) NOT named by handle. We need a mapping!

## The Missing Link Problem

### Issue
The `item_ui_handle` contains names like:
- `ui_item_equip_weapon_dagger_flame`
- `ui_spell_EM_Fire_FireBurst`

But extracted files are named:
- `ui_item0.png`, `ui_item1.png`, etc.
- `ui_spell0.png`, `ui_spell1.png`, etc.

### CRITICAL FINDING from SpellForce Data Editor Source Code

**How the game engine loads icons:**

From analyzing `spellforce_data_editor` C# source:

1. **UIHandle is the filename** (without extension)
2. **Path construction**: `texture\{UIHandle}.dds` or `texture\{UIHandle}.tga`
3. **Example**: `ui_item_equip_weapon_dagger_flame` → `texture\ui_item_equip_weapon_dagger_flame.dds`
4. **PAK search order**: sf35.pak → sf32.pak → sf25.pak → sf22.pak → sf1.pak → sf0.pak

**Code Reference** (SFResourceContainer.cs):
```csharp
// Constructs full path: prefix_path + "\\" + rname + extension
full_res_name = prefix_path + "\\" + res_to_load;
// For textures: "texture\\" + "ui_item_equip_weapon_dagger_flame" + ".dds"
```

**This means**: The UIHandle IS the asset name! We just need to extract with original names.

### Solution: Re-extract with Original Names (REQUIRED)

The numbered files (`ui_item0.png`) are useless - we need to re-extract preserving PAK filenames.

**Action Items**:
1. Use QuickBMS or custom extractor to preserve original filenames
2. Extract as: `ui_item_equip_weapon_dagger_flame.dds` → convert to `.png`
3. No mapping file needed - direct lookup by UIHandle

**Pros**: Direct lookup, no mapping overhead, matches game engine behavior
**Cons**: Need to re-extract all UI assets (one-time cost)

## Implementation Plan

### Phase 1: Re-extract UI Assets with Original Names

**Step 1.1**: Extract from PAK with QuickBMS
```bash
# Use QuickBMS with SpellForce script
cd ModdingTools/quickbms
quickbms spellforce.bms ../../OriginalGameFiles/pak/sf*.pak ../../ExtractedAssets/UI_reextracted/

# This should preserve original filenames:
# texture/ui_item_equip_weapon_dagger_flame.dds
# texture/ui_spell_EM_Fire_FireBurst.dds
```

**Step 1.2**: Convert DDS to PNG
```python
# In src/helper_tools/convert_ui_textures.py
import os
from PIL import Image
from pathlib import Path

def convert_dds_to_png(input_dir, output_dir):
    """
    Convert all DDS files to PNG, preserving names.
    """
    for dds_file in Path(input_dir).rglob("*.dds"):
        if dds_file.stem.startswith("ui_"):
            png_path = output_dir / f"{dds_file.stem}.png"
            # Use ImageMagick or Pillow with DDS plugin
            os.system(f'magick convert "{dds_file}" "{png_path}"')
```

**Step 1.3**: Organize by Category
```python
def organize_ui_assets(source_dir, target_dir):
    """
    Organize UI assets into categories.
    """
    categories = {
        "items": ["ui_item_"],
        "spells": ["ui_spell_"],
        "buildings": ["ui_building_"],
        "other": ["ui_"]
    }
    
    for png_file in Path(source_dir).glob("ui_*.png"):
        for category, prefixes in categories.items():
            if any(png_file.name.startswith(p) for p in prefixes):
                target = target_dir / category / png_file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(png_file, target)
                break
```

**Step 1.4**: Fallback Icon System
```python
# Default icons for missing assets
FALLBACK_ICONS = {
    "items": "ui_item_unknown.png",
    "spells": "ui_spell_unknown.png",
    "weapons": "ui_weapon_unknown.png",
}
```

### Phase 2: Integrate into Data Model

**Step 2.1**: Extend GameData Class
```python
# In TirganachReloaded/tirganach/gamedata.py
class GameData:
    def __init__(self, cff_path):
        self.cff_path = cff_path
        self.data = {}
        self.ui_mapping = self._load_ui_mapping()
        self.icon_cache = {}  # Cache loaded QPixmap objects
    
    def get_icon_path(self, category, item_id):
        """
        Get icon path for an item/spell/etc.
        
        Args:
            category: "items", "spells", "weapons", etc.
            item_id: The item's ID
        
        Returns:
            Path to PNG file or None
        """
        # Look up in item_ui table
        if category in ["items", "weapons", "armor"]:
            ui_entry = self._find_item_ui(item_id)
            if ui_entry:
                handle = ui_entry["item_ui_handle"]
                return self._resolve_icon_path(handle, "items")
        
        # Look up in spell_names table
        elif category == "spells":
            spell = self._find_spell(item_id)
            if spell and spell.get("spell_ui_handle"):
                handle = spell["spell_ui_handle"]
                return self._resolve_icon_path(handle, "spells")
        
        return None
    
    def _find_item_ui(self, item_id):
        """Find item_ui entry by item_id"""
        for entry in self.data.get("item_ui", []):
            if entry["item_id"] == item_id and entry["item_ui_index"] == 1:
                return entry
        return None
    
    def _resolve_icon_path(self, handle, category):
        """
        Convert UI handle to file path.
        SIMPLIFIED: UIHandle IS the filename (no mapping needed!)
        """
        if not handle:
            return None
            
        base_path = Path(__file__).parent.parent.parent
        # Direct lookup: handle + .png
        icon_path = base_path / "ExtractedAssets/UI/extracted" / category / f"{handle}.png"
        
        if icon_path.exists():
            return str(icon_path)
        return None
    
    def get_icon_pixmap(self, category, item_id, size=(64, 64)):
        """
        Get QPixmap for display in GUI.
        Uses cache for performance.
        """
        cache_key = f"{category}_{item_id}_{size}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]
        
        icon_path = self.get_icon_path(category, item_id)
        if icon_path:
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(*size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.icon_cache[cache_key] = pixmap
                return pixmap
        
        # Return fallback icon
        return self._get_fallback_icon(category, size)
```

### Phase 3: GUI Integration

**Step 3.1**: Add Icon Column to Table View
```python
# In TirganachReloaded/gui_editor/widgets/element_table.py
class ElementTableWidget(QWidget):
    def populate_table(self, elements, category):
        """Add icon column as first column"""
        self.table.setColumnCount(len(columns) + 1)
        self.table.setHorizontalHeaderLabels(["Icon"] + columns)
        
        for row, element in enumerate(elements):
            # Icon cell
            icon_label = QLabel()
            pixmap = self.game_data.get_icon_pixmap(category, element["id"])
            if pixmap:
                icon_label.setPixmap(pixmap)
                icon_label.setAlignment(Qt.AlignCenter)
            self.table.setCellWidget(row, 0, icon_label)
            
            # Data cells
            for col, key in enumerate(columns, start=1):
                # ... existing code
```

**Step 3.2**: Add Icon to Property Editor Panel
```python
# In TirganachReloaded/gui_editor/widgets/property_editor.py
class PropertyEditorWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Icon display at top
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(128, 128)
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("border: 2px solid #555; background: #222;")
        layout.addWidget(self.icon_label)
        
        # Element name
        self.name_label = QLabel()
        self.name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(self.name_label)
        
        # Properties scroll area
        # ... existing code
    
    def display_element(self, element, category):
        """Display element with icon"""
        # Load and display icon
        pixmap = self.game_data.get_icon_pixmap(category, element["id"], size=(128, 128))
        if pixmap:
            self.icon_label.setPixmap(pixmap)
        else:
            self.icon_label.setText("No Icon")
        
        # Display name
        name = self._get_element_name(element, category)
        self.name_label.setText(name)
        
        # Display properties
        # ... existing code
```

**Step 3.3**: Layout Design
```
┌─────────────────────────────────────────────────────────────┐
│ SpellForce CFF Editor                                       │
├──────────┬──────────────────────────┬───────────────────────┤
│          │                          │  ┌─────────────────┐  │
│ Category │  [Icon] ID   Name  Value │  │   [ICON 128x]   │  │
│ Tree     │  ────────────────────────│  └─────────────────┘  │
│          │   [⚔️]  27  Flame Dagger │  Flame Dagger         │
│ Items    │   [🗡️]  28  Fire Sword   │                       │
│ Weapons  │   [🏹]  29  Ice Bow      │  Min Damage: [10]     │
│ Spells   │   [⚡]  30  Thunder Axe  │  Max Damage: [25]     │
│ ...      │                          │  Speed: [1.2]         │
│          │                          │  Type: [Dagger ▼]     │
│          │                          │                       │
│          │  [< Prev] Page 1 [Next >]│  [Save] [Cancel]      │
└──────────┴──────────────────────────┴───────────────────────┘
```

### Phase 4: Icon Extraction Enhancement

**Step 4.1**: Update Extraction Script
```python
# In src/helper_tools/extract_ui_assets.py
def extract_with_names(pak_file, output_dir):
    """
    Extract UI assets preserving original names.
    Also generate mapping file.
    """
    mapping = {}
    
    for asset in pak_file.list_assets():
        if asset.name.startswith("ui_"):
            # Extract with original name
            output_path = output_dir / f"{asset.name}.dds"
            pak_file.extract(asset, output_path)
            
            # Convert to PNG
            png_path = convert_dds_to_png(output_path)
            
            # Add to mapping
            category = categorize_asset(asset.name)
            mapping[category][asset.name] = png_path.name
    
    # Save mapping
    save_json(mapping, "ui_icon_mapping.json")
```

## Data Flow Diagram

```
┌─────────────┐
│ GameData.cff│
└──────┬──────┘
       │
       ├─→ items table (item_id: 27)
       │
       ├─→ item_ui table (item_id: 27, handle: "ui_item_equip_weapon_dagger_flame")
       │
       └─→ weapons table (item_id: 27, damage: 10-25)

┌──────────────────┐
│ui_icon_mapping.json│
└────────┬──────────┘
         │
         └─→ {"ui_item_equip_weapon_dagger_flame": "ui_item27.png"}

┌─────────────────────────┐
│ExtractedAssets/UI/extracted/items/png/ui_item27.png│
└────────────┬────────────┘
             │
             └─→ Displayed in GUI
```

## Testing Plan

### Test 1: Mapping Generation
- Run extraction script on PAK files
- Verify ui_icon_mapping.json is created
- Check mapping has entries for all UI handles in GameData

### Test 2: Icon Loading
- Load GameData.cff in GUI
- Select item with known icon
- Verify correct icon displays in property panel
- Verify icon displays in table view

### Test 3: Performance
- Load category with 1000+ items
- Measure icon loading time
- Verify cache is working (second load is instant)

### Test 4: Fallback Icons
- Remove an icon file
- Verify fallback icon displays
- Verify no crashes

## File Locations

### New Files to Create
```
TirganachReloaded/
├── ui_icon_mapping.json          # NEW: Handle → filename mapping
└── tirganach/
    └── gamedata.py                # MODIFY: Add icon methods

src/helper_tools/
└── generate_ui_mapping.py         # NEW: Create mapping from PAK

ExtractedAssets/UI/
├── fallback_icons/                # NEW: Default icons
│   ├── ui_item_unknown.png
│   ├── ui_spell_unknown.png
│   └── ui_weapon_unknown.png
└── extracted/
    ├── items/png/                 # EXISTS: Item icons
    └── spells/png/                # EXISTS: Spell icons
```

## Next Steps

1. **Immediate**: Create `generate_ui_mapping.py` script
2. **Then**: Extend GameData class with icon methods
3. **Then**: Add icon display to property editor
4. **Finally**: Add icon column to table view

## Questions to Resolve

1. **Mapping Source**: Can we extract handle→index mapping from PAK headers, or do we need to parse CFF more deeply?
2. **Icon Size**: What sizes do we need? (64x64 for table, 128x128 for panel?)
3. **Categories**: Do buildings/creatures also have UI icons we should support?
4. **Caching**: Should we pre-load all icons or lazy-load on demand?

## Estimated Effort

- Mapping generation: 2-3 hours
- GameData integration: 1-2 hours  
- GUI integration: 2-3 hours
- Testing & polish: 1-2 hours

**Total**: 6-10 hours
