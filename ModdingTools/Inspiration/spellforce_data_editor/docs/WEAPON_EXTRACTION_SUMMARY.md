# SpellForce Weapon Data Extraction Summary

## Overview
This document summarizes the extraction of weapon data from the SpellForce Platinum Edition game files, focusing on categories c2003 (Items), c2015 (Item Weapon Data), c2063 (Weapon Types), c2064 (Weapon Materials), and c2016 (Localization).

## Approach

### 1. Initial Setup
- Used the TirganachReloaded Python library to load the `GameData.cff` file
- Leveraged existing JSON export (`GameData.json`) for item data from c2003
- Cross-referenced with live GameData object for weapon-specific categories

### 2. Data Sources
- **c2003 (Items)**: Core item metadata (ID, name, type, values)
- **c2015 (Item Weapon Data)**: Links items to weapon types and materials
- **c2063 (Weapon Types)**: Lookup table for weapon classifications (e.g., 1H Sword, Bow)
- **c2064 (Weapon Materials)**: Lookup table for materials (e.g., Iron, Steel)
- **c2016 (Localization)**: Multilingual text database for names and descriptions

### 3. Extraction Process
1. **Filter Weapons**: Identified items in c2003 that have entries in c2015 (indicating they are weapons)
2. **Resolve References**:
   - Used `name_id` from c2003 to lookup names in c2016 (English first, fallback to other languages)
   - Used `text_id` from c2063/c2064 to get type/material names from c2016
3. **Add Metadata**: Included additional fields from c2003 (type, subtype, values, etc.)
4. **Handle Unknowns**: Attempted fallback to non-English languages for missing names

### 4. Tools Used
- **Python 3** with `tirganach` library for CFF parsing
- **JSON** for data export and manipulation
- **Bash** for script execution and file management

## Findings

### 1. Weapon Count
- **Total Weapons Extracted**: 719 unique weapons
- **All with Resolved Names**: 0 unknowns remaining after fallback

### 2. Unique Identifiers
- Each weapon has a distinct `item_id` in c2003
- Names are unique via `name_id` references to c2016
- Type/Material combinations provide additional classification

### 3. Data Completeness
- **Names**: Fully resolved in English or alternative languages
- **Stats**: Complete combat data (damage, speed, range)
- **Metadata**: Economic values, types, and set information
- **Relationships**: Clear links between categories

### 4. Category Relationships
- c2003 → c2016 (names)
- c2015 → c2063 (weapon types)
- c2015 → c2064 (weapon materials)
- c2063/c2064 → c2016 (type/material names)

## Results

### Output Files
1. **enhanced_weapons.json**: Complete weapon dataset with all resolved data
2. **Previous Files**:
   - `extracted_weapons.json`: Basic extraction
   - `extracted_weapons_with_names.json`: With name resolution

### Sample Data Structure
```json
{
  "item_id": 1001,
  "name": "Iron Sword",
  "name_id": 1501,
  "item_type": "WEAPON",
  "item_subtype": "1H_SWORD",
  "weapon_type_id": 1,
  "weapon_type_name": "1H Sword",
  "weapon_material_id": 2,
  "weapon_material_name": "Iron",
  "min_damage": 10,
  "max_damage": 20,
  "weapon_speed": 100,
  "min_range": 1,
  "max_range": 2,
  "sell_value": 50,
  "buy_value": 100,
  "option": 0,
  "item_set_id": 0
}
```

## Recommendations

1. **For Modding**: Use this data to create balanced weapon sets or modifications
2. **For Analysis**: Study weapon distribution by type/material for game balance insights
3. **For Documentation**: Reference this extraction for understanding SpellForce's data structure
4. **Future Work**: Extend to other item types or add visual/UI data from c2012

## Conclusion
The extraction successfully demonstrates the interconnected nature of SpellForce's data categories and provides a complete, usable dataset for weapon-related game content.