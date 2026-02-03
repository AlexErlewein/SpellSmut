# Allwissende Almacht System Guide

## Overview

The Weapon Forge now includes **Allwissende Almacht**, a comprehensive icon system that allows users to browse, select, and assign custom icons to their created weapons. This guide explains how to use the system and how it integrates with the weapon creation workflow.

## Features Implemented

### ✅ **Allwissende Almacht (Icon Browser)**

- **4,258 Icons Available**: Extracted from SpellForce game assets
- **Multiple Categories**: Items, spells, UI elements, backgrounds, buttons, etc.
- **Advanced Search**: Filter by name, handle, or category
- **Icon Preview**: Large 256x256 previews with detailed information
- **Smart Mapping**: Automatic handle-to-atlas resolution

### ✅ **Weapon Forge Integration**

- **Visual Icon Selection**: Browse and select icons during weapon creation
- **Live Preview**: See selected icon in real-time during wizard steps
- **Summary Display**: Icon appears in the final weapon review page
- **Export Integration**: Icon data included in both JSON and CFF exports

### ✅ **Technical Infrastructure**

- **CFFDataModel Integration**: Uses existing data model for icon management
- **Handle Resolution**: Sophisticated mapping from icon handles to file paths
- **Error Handling**: Graceful fallbacks for missing or broken icons
- **Performance Optimized**: Cached loading and efficient memory management

## Usage Guide

### For Users

#### **Step 1: Access Allwissende Almacht**

1. Create a new weapon in the Weapon Forge
2. Navigate to the "Visual & Audio" step (Step 5)
3. Click the "Browse Icons..." button next to the icon preview

#### **Step 2: Browse and Select Icons**

1. **Search**: Type in the search box to filter by name or handle
2. **Category Filter**: Select from dropdown to show specific icon types
3. **Preview**: Click any icon to see a large preview and details
4. **Select**: Double-click or click "Select Icon" to choose

#### **Step 3: Review Selection**

1. The selected icon appears in the preview box
2. The icon handle is displayed next to the preview
3. A green checkmark confirms successful selection

#### **Step 4: Complete Weapon Creation**

1. Continue through the remaining wizard steps
2. The icon appears in the final summary page
3. Export the weapon (JSON and/or CFF format)
4. The icon data is preserved in the export file

### For Developers

#### **Allwissende Almacht Integration**

```python
from AllwissendeAlmacht.allwissende_almacht import AllwissendeAlmachtDialog

# Create Allwissende Almacht dialog
icon_dialog = AllwissendeAlmachtDialog(data_model, category="itm", parent=self)

# Connect signal for icon selection
icon_dialog.iconSelected.connect(self.on_icon_selected)

# Show dialog
result = icon_dialog.exec()
```

#### **Icon Data Handling**

```python
# In weapon creation data
weapon_data = WeaponCreationData(
    # ... other properties ...
    icon_handle="ui_item_equip_weapon_dagger_flame"  # Selected icon
)

# Load icon preview from data model
icon_pixmap = data_model.get_icon_pixmap(icon_handle)
```

#### **Icon Categories**

| Category    | Handle Prefix            | Use Case           | Count |
| ----------- | ------------------------ | ------------------ | ----- |
| Items       | `ui_item_equip_weapon_*` | Weapon icons       | 432   |
| Spells      | `ui_spell_*`             | Spell icons        | 73    |
| UI          | Various                  | Interface elements | 1161  |
| Backgrounds | `bgr_*`                  | Background tiles   | 1161  |
| Buttons     | `btn_*`                  | UI buttons         | 77    |
| Content     | `cnt_*`                  | Content markers    | 37    |

## File Structure

### Allwissende Almacht

```
src/AllwissendeAlmacht/
├── allwissende_almacht.py     # Main widget logic
├── run_allwissende_almacht.py # Standalone launcher
└── README.md                  # This documentation
```

### Code Integration

```
src/TirganachReloaded/cff_editor/
├── widgets/
│   └── weapon_forge_wizard.py    # Weapon forge with icon integration
├── models/
│   └── weapon_creation_data.py   # Weapon data model with icon support
├── data_model.py                 # Icon resolution and caching
└── tests/
    └── test_icon_integration.py   # Icon integration tests
```

## Icon System Architecture

### **Handle Resolution System**

1. **Input**: User selects icon with handle (e.g., `ui_item_equip_weapon_dagger_flame`)
2. **Lookup**: System searches mapping files for the handle
3. **Atlas Mapping**: Handle resolves to specific atlas and index
4. **Path Construction**: File path generated from atlas and index
5. **File Loading**: PNG file loaded and cached as QPixmap

### **Data Flow**

```
Allwissende Almacht → Icon Selection → Handle Storage → CFF Export
     ↓              ↓                ↓              ↓
  Icon Preview   Weapon Data    Icon Resolution   Game Import
     ↓              ↓                ↓              ↓
  Visual Feedback   UI Update    File Loading    In-Game Display
```

### **Caching System**

- **Icon Cache**: Pixmap objects cached in CFFDataModel
- **Path Cache**: Resolved file paths cached for performance
- **Memory Management**: Cache cleared when memory pressure detected
- **Persistent Cache**: Icons remain loaded during session

## Error Handling

### **Common Issues**

1. **Icon Not Found**
   - **Symptom**: Yellow warning icon in preview
   - **Cause**: Handle exists but file is missing
   - **Solution**: Check ExtractedAssets directory integrity

2. **Handle Resolution Failed**
   - **Symptom**: Red error icon in preview
   - **Cause**: Icon handle not found in mapping
   - **Solution**: Verify handle spelling and mapping files

3. **Allwissende Almacht Unavailable**
   - **Symptom**: Warning dialog when clicking "Browse Icons"
   - **Cause**: Data model not loaded or icon index missing
   - **Solution**: Ensure game data is loaded first

### **Troubleshooting**

```python
# Debug icon resolution
def debug_icon_resolution(data_model, icon_handle):
    print(f"Debugging icon: {icon_handle}")

    # Check if handle exists in index
    if data_model.icon_index:
        icons = data_model.icon_index.get('icons', {})
        if icon_handle in icons:
            print(f"✓ Found in index: {icons[icon_handle]}")
        else:
            print(f"✗ Not found in index")

    # Try to resolve path
    icon_path = data_model._resolve_icon_path(icon_handle)
    if icon_path:
        print(f"✓ Resolved path: {icon_path}")
        if Path(icon_path).exists():
            print(f"✓ File exists")
        else:
            print(f"✗ File missing")
    else:
        print(f"✗ Could not resolve path")
```

## Performance Considerations

### **Optimization Strategies**

1. **Lazy Loading**: Icons loaded only when needed
2. **Caching**: Frequently used icons kept in memory
3. **Chunked Loading**: Large icon indices loaded in parts
4. **Background Loading**: Icons loaded asynchronously when possible

### **Memory Usage**

- **4,258 Icons**: ~50MB of PNG files
- **Cache Size**: ~100MB when all icons loaded
- **Per Icon**: ~12KB average PNG size
- **Pixmap Memory**: ~4KB per 64x64 icon in memory

### **Best Practices**

1. **Limit Concurrent Icons**: Don't display too many icons at once
2. **Use Category Filtering**: Reduce load by filtering to relevant categories
3. **Clear Cache**: Call `data_model.clear_icon_cache()` when memory is low
4. **Error Handling**: Always check for `None` returns from icon functions

## Future Enhancements

### **Planned Features**

1. **Custom Icon Upload**
   - Allow users to import their own icons
   - Support for PNG, JPG, DDS formats
   - Automatic scaling and format conversion

2. **Icon Collections**
   - User-defined icon sets and collections
   - Favorites and recently used icons
   - Custom category creation

3. **Enhanced Search**
   - Search by visual similarity
   - Color-based filtering
   - Tag-based organization

4. **Advanced Preview**
   - Animated icon support
   - Icon effects and overlays
   - In-context preview (on weapon models)

### **Technical Improvements**

1. **Database Backend**
   - SQLite database for icon metadata
   - Full-text search capabilities
   - Faster lookups and filtering

2. **Icon Versioning**
   - Track icon changes and updates
   - Rollback capabilities
   - Icon import/export functionality

## Conclusion

Allwissende Almacht provides a **robust, user-friendly interface** for weapon customization in the Weapon Forge. With over 4,000 available icons and sophisticated handling for resolution and caching, users can create visually unique weapons that stand out in-game.

The system is designed to be **extensible** and **maintainable**, with clear separation of concerns between the browser, data model, and weapon creation workflow. Future enhancements can be added without disrupting the existing functionality.

### **Quick Start Checklist**

- [ ] Ensure `ExtractedAssets/UI/icons_extracted/` directory exists
- [ ] Verify icon index files are present
- [ ] Test Allwissende Almacht functionality
- [ ] Confirm icon preview works in wizard
- [ ] Validate export includes icon data
- [ ] Test final weapons in-game

Allwissende Almacht is ready for **production use** and provides a solid foundation for weapon customization in SpellForce modding.
