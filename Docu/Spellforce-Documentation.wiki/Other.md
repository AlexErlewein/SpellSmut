# Limitations

### Items
Item name can be at maximum 41 characters long.

### Rune Army
- Spells and Weapon Spell effects given to Workers, rune army units, titans and swarms do not care about the level and instead the game adjusts the spell level according to the Worker Level. So a level 28 Worker would cause Rune Army spells to scale to lvl 12.
- Different Unit Cost for the Base and Upgraded version of units can behave in a weird way such as the cost not being what you expected and the UI for the upgraded unit not being correct.

## Player character identifier in different tables.
* NpcId = Avatar (or 0),
* FigureType = FigureAvatar,

# Items and Objects

### Adding new Items
It's important that after creating your new item, to go into the editor SQL Modifier and sql_item.lua and add the item model, otherwise it'll be invisible ingame.

### Adding new Map Objects
Same as the items section, it's necessary to go into SQL Modifier and sql_object.lua and add the model for the object.


### Race Flags
- 1 = Undead
- 2 = Breathing
- 4 = Huntable
- 8 = Animal
- 16 = Has Soul (Unsure on what this implies)
- 32 = Attack Buildings
- 64 = Bleeds
- 128 = (not used)

### AI Flags
- 1 = Default
- 2 = Idle
- 4 = Stroll Along
- 8 = Nomadic
- 16 = Aggressive
- 32 = Defensive
- 64 = Script
- 128 = (not used)