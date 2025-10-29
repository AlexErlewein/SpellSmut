> **⚠️ OUTDATED PLAN ⚠️**
> 
> This document outlines the original icon integration plan, which was based on the assumption that re-extracting assets with original filenames would be sufficient. **This assumption was proven incomplete.**
> 
> **The primary blocker is now the handle-to-atlas mapping.** We need to discover how the game links an item's UI handle to a specific texture atlas file.
> 
> For the current status and plan, please see **[ICON_SYSTEM.md](./ICON_SYSTEM.md)**.

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

**Current Directory Structure** (numbered names):
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

**Target Directory Structure** (after re-extraction with original names):
```
UI/extracted/
├── items/
│   ├── ui_item_equip_weapon_dagger_flame.png
│   ├── ui_item_equip_armor_chest_chain.png
│   └── ... (original filenames)
├── spells/
│   ├── ui_spell_EM_Fire_FireBurst.png
│   ├── ui_spell_WM_Life_Healing.png
│   └── ... (original filenames)
├── cursors/
├── backgrounds/
└── ... (preserved existing categories)
```

**Note**: After re-extraction, files will be named by their UI handles, eliminating the need for mapping!

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

**Step 1.2b**: Rotate PNGs by 180 degrees
```python
# In src/helper_tools/rotate_ui_pngs.py
from PIL import Image
from pathlib import Path

def rotate_pngs_180(input_dir):
    """
    Rotate all UI PNGs by 180 degrees (SpellForce uses inverted Y-axis).
    Modifies files in-place.
    """
    for png_file in Path(input_dir).rglob("*.png"):
        if png_file.name.startswith("ui_"):
            print(f"Rotating: {png_file.name}")
            with Image.open(png_file) as img:
                rotated = img.rotate(180)
                rotated.save(png_file)
```

**Step 1.3**: Organize by Category (Preserve Existing Structure)
```python
def organize_ui_assets(source_dir, target_dir):
    """
    Organize UI assets into categories while preserving existing folder structure.
    The existing ExtractedAssets/UI/extracted/ structure should be maintained.
    """
    # Since we're re-extracting with original names, we can use the existing
    # categorization logic but ensure it matches the current structure:
    # ExtractedAssets/UI/extracted/
    # ├── items/ (ui_item_* files)
    # ├── spells/ (ui_spell_* files)
    # ├── cursors/ (ui_cursor_* files)
    # ├── backgrounds/ (ui_bgr_* files)
    # └── etc.

    categories = {
        "items": ["ui_item_", "ui_itm_"],
        "spells": ["ui_spell_"],
        "cursors": ["ui_cursor_"],
        "backgrounds": ["ui_bgr_"],
        "buttons": ["ui_btn_"],
        "mainmenu": ["ui_mainmenu_"],
        "containers": ["ui_cnt_"],
        "logos": ["ui_logo_"],
        "fonts": ["font_"],
        "other": ["ui_"]  # Catch-all for ui_ files
    }

    for png_file in Path(source_dir).rglob("*.png"):
        if not png_file.name.startswith("ui_") and not png_file.name.startswith("font_"):
            continue

        # Determine category based on filename prefix
        categorized = False
        for category, prefixes in categories.items():
            if any(png_file.name.startswith(p) for p in prefixes):
                target = target_dir / category / png_file.name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(png_file, target)
                categorized = True
                break

        # If not categorized, put in "other"
        if not categorized:
            target = target_dir / "other" / png_file.name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy(png_file, target)
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

**After Re-extraction with Original Names** (No mapping needed):

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

┌─────────────────────────────────────────────────────┐
│ExtractedAssets/UI/extracted/items/ui_item_equip_weapon_dagger_flame.png│
└─────────────────────────────┬───────────────────────┘
                              │
                              └─→ Displayed in GUI (direct lookup!)
```

**Legacy Data Flow** (if using existing numbered files):

```
┌─────────────┐
│ GameData.cff│
└──────┬──────┘
        │
        ├─→ item_ui table (handle: "ui_item_equip_weapon_dagger_flame")
        │
        └─→ Lookup in mapping

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
└── tirganach/
    └── gamedata.py                # MODIFY: Add icon methods

src/helper_tools/
├── extract_ui_with_names.py       # NEW: Re-extract UI assets with original names
├── convert_ui_textures.py         # NEW: DDS → PNG conversion
├── rotate_ui_pngs.py              # NEW: 180° rotation for PNGs
└── organize_ui_assets.py          # NEW: Organize by category

ExtractedAssets/UI/
├── fallback_icons/                # NEW: Default icons
│   ├── ui_item_unknown.png
│   ├── ui_spell_unknown.png
│   └── ui_weapon_unknown.png
├── extracted/                     # PRESERVE: Existing structure
│   ├── items/                     # ui_item_* files
│   ├── spells/                    # ui_spell_* files
│   ├── cursors/                   # ui_cursor_* files
│   └── ...                        # Other existing categories
└── raw_reextraction/              # NEW: Raw QuickBMS output with original names
```

## Implementation Status

### ✅ Phase 1: Asset Re-extraction (Scripts Created)
- **extract_ui_with_names.py**: QuickBMS extraction with original filenames
- **convert_ui_textures.py**: DDS to PNG conversion
- **rotate_ui_pngs.py**: 180° PNG rotation for SpellForce Y-axis
- **organize_ui_assets.py**: Category-based organization
- **run_ui_icon_integration.bat**: Complete pipeline batch script

### ✅ Phase 2: Code Integration (Completed)
- **Extended CFFDataModel** with icon lookup methods (`get_icon_path`, `get_icon_pixmap`, etc.)
- **Added icon column** to ElementTableWidget (32x32 icons)
- **Added icon display** to PropertyEditorWidget (128x128 icons)
- **Implemented caching** for performance
- **Added fallback system** for missing icons

### 🔄 Phase 3: Testing & Polish (Ready for Testing)
1. **CRITICAL: Run extraction pipeline on Windows** - PAK files are Windows-only format, must use Windows machine to extract with original filenames
2. **Test icon loading** for items, spells, weapons
3. **Verify performance** with icon caching
4. **Test fallback icons** for missing assets

### Windows Extraction Requirement

**IMPORTANT**: The current icon system uses hash-based mapping to numbered PNG files because the PAK files cannot be properly extracted on macOS. To get correctly named icons (e.g., `ui_item_equip_weapon_dagger_flame.png`), the extraction must be done on Windows.

**Action Required**:
- Use Windows machine with SpellForce installed
- Run the extraction scripts in `src/helper_tools/`
- Copy the properly named assets back to the project
- This will eliminate the need for hash-based mapping and provide direct filename lookup

## Windows Execution Instructions

1. **Copy scripts to Windows**:
   ```bash
   # From macOS/Linux, copy to Windows machine:
   scp src/helper_tools/extract_ui_with_names.py windows_machine:
   scp src/helper_tools/convert_ui_textures.py windows_machine:
   scp src/helper_tools/rotate_ui_pngs.py windows_machine:
   scp src/helper_tools/organize_ui_assets.py windows_machine:
   scp src/helper_tools/run_ui_icon_integration.bat windows_machine:
   ```

2. **Install dependencies on Windows**:
   ```cmd
   pip install Pillow
   # Install ImageMagick from: https://imagemagick.org/script/download.php#windows
   ```

3. **Run the complete pipeline**:
   ```cmd
   run_ui_icon_integration.bat
   ```

4. **Copy results back**:
   ```bash
   # Copy ExtractedAssets/UI/extracted/ back to your project
   ```

## File Locations (Final)

### Scripts Created
```
src/helper_tools/
├── extract_ui_with_names.py       # QuickBMS extraction with original names
├── convert_ui_textures.py         # DDS → PNG conversion
├── rotate_ui_pngs.py              # 180° PNG rotation
├── organize_ui_assets.py          # Category organization
└── run_ui_icon_integration.bat    # Complete pipeline runner
```

### Modified Files
```
TirganachReloaded/cff_editor/
├── data_model.py                   # Added icon methods
├── widgets/
│   ├── element_table.py            # Added icon column
│   └── property_editor.py          # Added icon display
```

### Output Locations
```
ExtractedAssets/UI/
├── extracted/                      # Final organized assets
│   ├── items/                      # ui_item_* files
│   ├── spells/                     # ui_spell_* files
│   ├── cursors/                    # ui_cursor_* files
│   └── ...                         # Other categories
├── fallback_icons/                 # Default icons for missing assets
└── raw_reextraction/               # Raw QuickBMS output (temporary)
```

## Implementation Decisions Made

1. **Icon Sizes**: 
   - Table view: 32x32 pixels (compact display)
   - Property editor: 128x128 pixels (detailed view)
   - Both use aspect ratio preservation

2. **Categories Supported**:
   - Items (weapons, armor, consumables)
   - Spells (all magic schools)
   - Cursors, backgrounds, buttons, etc.
   - Extensible for buildings/creatures if needed

3. **Caching Strategy**:
   - Lazy loading on demand
   - Per-element caching with size-specific keys
   - Memory-efficient (clears on category change)

4. **PNG Rotation**:
   - 180° rotation applied to all UI PNGs
   - Compensates for SpellForce's inverted Y-axis
   - Applied after DDS conversion

## Testing Checklist

- [ ] Run extraction pipeline on Windows
- [ ] Verify DDS → PNG conversion works
- [ ] Check PNG rotation is correct
- [ ] Test icon display in table view
- [ ] Test icon display in property editor
- [ ] Verify fallback icons for missing assets
- [ ] Test performance with large item lists
- [ ] Check icon caching functionality

## Estimated Effort

- Mapping generation: 2-3 hours
- GameData integration: 1-2 hours  
- GUI integration: 2-3 hours
- Testing & polish: 1-2 hours

**Total**: 6-10 hours
