# SpellForce Category References Table

This table outlines the key relationships between SpellForce game data categories, focusing on weapons and related systems.

## Category Relationships

| Category | ID | Purpose | References To | Referenced By | Description |
|----------|----|---------|---------------|---------------|-------------|
| **Items** | c2003 | Core item metadata | c2016 (names), c2005 (stats for runes) | c2015, c2014, c2017, c2012 | All items in the game, including weapons, armor, spells |
| **Item Weapon Data** | c2015 | Weapon combat stats | c2063 (types), c2064 (materials) | c2003 (items) | Links weapons to their type and material classifications |
| **Weapon Types** | c2063 | Weapon type lookup | c2016 (names) | c2015 (weapon data) | Defines weapon categories (1H Sword, Bow, etc.) |
| **Weapon Materials** | c2064 | Material lookup | c2016 (names) | c2015 (weapon data) | Defines materials (Iron, Steel, Adamantium, etc.) |
| **Localization** | c2016 | Multilingual text | None | c2003, c2063, c2064, c2024, c2029, etc. | Central text database for all game strings |
| **Item Armor Data** | c2004 | Armor bonuses | c2003 (items) | None | Stat bonuses for armor items |
| **Item UI Data** | c2012 | UI representation | c2003 (items) | None | Icons and handles for items |
| **Item Effects** | c2014 | Weapon effects | c2002 (spells) | c2003 (items) | Spell effects triggered by weapons |
| **Item Requirements** | c2017 | Skill requirements | c2039 (skills) | c2003 (items) | Skills needed to equip items |
| **Spells** | c2002 | Spell mechanics | c2054 (spell lines) | c2014, c2018, c2026 | All spells and effects in the game |
| **Spell Lines** | c2054 | Spell progression | c2016 (names) | c2002 (spells) | Spell leveling and organization |
| **Units** | c2024 | Unit metadata | c2016 (names), c2005 (stats) | c2025, c2026 | Heroes, creatures, and NPCs |
| **Unit Stats** | c2005 | Attributes | c2022 (races) | c2024, c2003 (runes) | Detailed unit attributes and resistances |
| **Races** | c2022 | Race properties | c2016 (names) | c2005, c2029 | Playable and NPC races |
| **Buildings** | c2029 | Building data | c2016 (names), c2022 (races) | c2031, c2030 | All buildings and structures |

## Key Insights

1. **Central Hub**: c2016 (Localization) is referenced by almost every other category for names and text
2. **Item System**: c2003 is the foundation, extended by c2015, c2004, c2012, c2014, c2017
3. **Weapon Chain**: c2003 → c2015 → c2063/c2064 → c2016
4. **Spell Integration**: Weapons can trigger spells via c2014 → c2002
5. **Unit Equipment**: c2025 links units to items from c2003

## Usage for Modding

- **Adding Weapons**: Create entries in c2003, c2015, and reference c2063/c2064
- **New Types/Materials**: Add to c2063/c2064 and provide names in c2016
- **Localization**: All text must exist in c2016 for proper display
- **Balance**: Use c2004 and c2017 to adjust stats and requirements

This table provides a roadmap for understanding and modifying SpellForce's data structure.