# UI Icon Category Abbreviations

## Overview

This document explains the commonly used abbreviations for UI icon categories in SpellForce Platinum Edition. These abbreviations appear in UI asset filenames and are critical for proper categorization and organization of extracted assets.

## Category Abbreviations

### bgr (Backgrounds)
- **Full Form**: Background
- **Description**: Background images used in UI screens and menus
- **Examples**: Menu backgrounds, panel backgrounds, interface overlays
- **Typical Format**: `ui_bgr_*`

### btn (Buttons)
- **Full Form**: Button
- **Description**: Interactive button elements in the user interface
- **Examples**: Menu buttons, skill buttons, toggle buttons, clickable UI elements
- **Typical Format**: `ui_btn_*`

### oth (Others)
- **Full Form**: Other
- **Description**: Miscellaneous UI elements that don't fit into specific categories
- **Examples**: Decorative elements, separators, small UI components
- **Typical Format**: `ui_oth_*` or catch-all for uncategorized UI assets

### cnt (Contour/Containers)
- **Full Form**: Contour or Container
- **Description**: Frame elements, borders, containers, or panel outlines
- **Examples**: Item slots, panel borders, frame decorations, UI containers
- **Typical Format**: `ui_cnt_*`

### itm (Items)
- **Full Form**: Item
- **Description**: Icons and graphics representing in-game items, including weapons, armor, consumables
- **Examples**: Weapon icons, armor icons, potion icons, equipment graphics
- **Typical Format**: `ui_itm_*` or `ui_item_*`
- **Grid Pattern**: 16x16 grid (as opposed to other categories which may use different grid sizes)
- **Note**: Some items appear longer but not broader, others are square
- **Dimensions**: Needs further investigation to confirm exact grid dimensions and patterns

### logo (Logos)
- **Full Form**: Logo
- **Description**: Logos, emblems, symbols, and other branded graphic elements
- **Examples**: Faction emblems, game logos, UI symbols
- **Typical Format**: `ui_logo_*`

## Additional Notes

Based on recent analysis of the icon system:

1. **Rotation**: All icons are rotated by 180 degrees during extraction to correct for the inverted Y-axis used in SpellForce textures.

2. **Offset**: The same offset used for spells (3,3) is applied for centering, though this may vary by category.

3. **Grid Patterns**: Different categories may use different grid patterns. The `itm` category appears to use a 16x16 grid, but this requires further investigation.

4. **File Naming Convention**: UI assets follow the pattern `ui_[category]_[description].[extension]` where the category abbreviation indicates the type of UI element.

## Related Documentation

- [UI Icon Extraction Solution](UI_ICON_EXTRACTION_SOLUTION.md)
- [Icon System Quick Start](../../QUICK_START_ICON_SYSTEM.md)
- [Icon Extraction Status](../../ProjectPlanning/Internal/ICON_EXTRACTION_STATUS.md)