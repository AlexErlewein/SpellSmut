# The Spell Forge

A standalone, interactive spell creation system for SpellForce with browser capabilities, level progression, and validation.

## Features

- **Multi-Phase Creation System**: 7 organized phases for comprehensive spell design
- **Advanced Spell Browser**: Filter by school, type, and search by name
- **Level Progression**: Support for 1-15 spell levels with multiple scaling modes
- **Validation System**: Built-in checks for balance and consistency
- **Multiple Modes**: Create new, edit existing, or duplicate spells
- **Export Options**: Save spells to JSON format

## Installation

The Spell Forge is standalone but requires the TirganachReloaded spell models:

```bash
# Ensure you're in the src directory
cd /path/to/SpellSmut/src

# The forge uses these models from TirganachReloaded:
# - spell_creation_data.py
# - spell_level.py
# - spell_enums.py
```

## Quick Start

### First Time Setup

Populate template spells to have examples for browsing:

```bash
# Populate 6 example template spells
python populate_spell_templates.py
```

This creates:
- **Fireball** (Fire Attack) - ID 301
- **Ice Blast** (Ice Attack) - ID 302
- **Holy Heal** (White Heal) - ID 303
- **Chain Lightning** (Earth AOE) - ID 304
- **Regeneration Aura** (White Buff) - ID 305
- **Summon Wolf** (Black Summon) - ID 306

### Running the Spell Forge

```bash
python spell_forge.py
```

### Basic Workflow

1. **Phase 1**: Choose creation mode (New/Edit/Duplicate)
2. **Phase 2**: Set basic properties (Name, School, Type)
3. **Phase 3**: Configure mechanics (Target, Range, AOE)
4. **Phase 4**: Define level progression and scaling
5. **Phase 5**: Add visual effects
6. **Phase 6**: Add sound effects
7. **Phase 7**: Review, validate, and export

## Detailed Usage

### Phase 1: Mode Selection

Three creation modes available:

#### Create New Spell
Start with a blank slate and define everything from scratch.

#### Edit Existing Spell
Browse and select an existing spell to modify. Your changes will update the original spell.

#### Duplicate & Modify
Copy an existing spell and create a new version with a new ID.

#### Browse Spells
Use the advanced browser to:
- Filter by magic school (FIRE, ICE, WHITE, etc.)
- Filter by spell type (ATTACK, HEAL, BUFF, etc.)
- Search by name
- View detailed spell information

**Browser Commands:**
- Enter spell ID to select
- Type `filter` to change filters
- Type `clear` to clear all filters
- Type `back` to cancel

### Phase 2: Basic Properties

Define your spell's identity:

- **Spell Name**: Display name (e.g., "Inferno Blast")
- **Internal Name**: Code-friendly name without spaces (e.g., "InfernoBlast")
- **Description**: Flavor text for the spell
- **Magic School**: Choose from:
  - WHITE (0) - Holy/Life magic
  - FIRE (1) - Fire elemental
  - ICE (2) - Ice elemental
  - BLACK (3) - Necromancy/Dark magic
  - MENTAL (4) - Mind/Illusion magic
  - EARTH (5) - Earth elemental
  - CUSTOM (99) - User-defined
- **Spell Type**: ATTACK, HEAL, BUFF, DEBUFF, SUMMON, AOE, UTILITY

### Phase 3: Target & Mechanics

Configure how your spell works:

- **Target Type**:
  - SINGLE: Single target
  - AOE: Area of effect
  - SELF: Self-cast only
  - CONE: Cone-shaped area
  - CHAIN: Bounces between targets

- **Projectile**: Whether the spell fires a projectile
- **Base Range**: Distance the spell can reach (units)
- **AOE Radius**: Area of effect radius (0 for single target)
- **Duration**: How long effects last (0 for instant)

### Phase 4: Level Progression & Scaling

Configure spell power across 15 levels:

#### Base Stats (Level 1)
- **Minimum Damage**: Lower bound of damage range
- **Maximum Damage**: Upper bound of damage range
- **Mana Cost**: Mana required to cast
- **Cooldown**: Seconds before spell can be cast again
- **Cast Time**: Seconds to complete casting

#### Scaling Modes

**LINEAR** - Consistent growth per level
```
Damage: +10/+12 per level
Mana: +3 per level
Cooldown: -0.1s per level
```

**EXPONENTIAL** - Accelerating growth (1.15x factor)
```
Damage: ×1.15 per level
Mana: ×1.12 per level
Cooldown: ×0.95 per level
```

**LOGARITHMIC** - Diminishing returns
```
Damage: Based on log(level)
Steady but slower growth
```

**CUSTOM** - Manual configuration per level

### Phase 5: Visual Effects

Assign effect names for:
- **Cast Effect**: Played when casting begins
- **Projectile Effect**: Visual for projectile
- **Resolve Effect**: Impact/resolution effect
- **Target Effect**: Effect on target
- **Over Time Effect**: Continuous effect visual

### Phase 6: Sound Effects

Assign sound files for:
- **Cast Sound**: Sound when casting
- **Projectile Sound**: Sound during projectile flight
- **Resolve Sound**: Sound on impact
- **Hit Sound**: Sound when damage is dealt

### Phase 7: Review & Export

Final review shows:
- Complete spell summary
- Level 1 and max level stats comparison
- **Balance Metrics**:
  - Damage per Mana (efficiency)
  - Damage per Second (DPS)
  - Power Rating
  - Balance Category (Weak/Balanced/Strong/Overpowered)
- **Validation Results**:
  - ❌ Errors (must fix)
  - ⚠️ Warnings (recommended to address)
  - ✓ Valid (ready for export)

## Examples

### Example 1: Simple Fire Attack Spell

```
Phase 2 - Basic Properties:
  Name: Fireball
  Internal Name: Fireball
  School: FIRE (1)
  Type: ATTACK

Phase 3 - Mechanics:
  Target: SINGLE
  Has Projectile: Yes
  Range: 25.0
  AOE Radius: 0.0

Phase 4 - Level Progression:
  Levels: 15
  Base Damage: 15-20
  Mana Cost: 10
  Cooldown: 3.0s
  Cast Time: 1.5s
  Scaling: EXPONENTIAL

Result:
  Level 15 Damage: 72-96
  Level 15 DPS: 24.7
  Balance: Strong
```

### Example 2: Healing Spell

```
Phase 2 - Basic Properties:
  Name: Holy Heal
  Internal Name: HolyHeal
  School: WHITE (0)
  Type: HEAL

Phase 3 - Mechanics:
  Target: SINGLE
  Has Projectile: No
  Range: 15.0
  AOE Radius: 0.0

Phase 4 - Level Progression:
  Levels: 10
  Base Damage: 20-25 (healing)
  Mana Cost: 15
  Cooldown: 5.0s
  Cast Time: 2.0s
  Scaling: LINEAR

Result:
  Level 10 Damage: 110-133
  Efficiency: High
  Balance: Balanced
```

### Example 3: AOE Spell

```
Phase 2 - Basic Properties:
  Name: Ice Storm
  Internal Name: IceStorm
  School: ICE (2)
  Type: AOE

Phase 3 - Mechanics:
  Target: AOE
  Has Projectile: No
  Range: 30.0
  AOE Radius: 8.0
  Duration: 5.0s

Phase 4 - Level Progression:
  Levels: 12
  Base Damage: 10-15 (per tick)
  Mana Cost: 40
  Cooldown: 15.0s
  Cast Time: 3.0s
  Scaling: LOGARITHMIC
```

## File Structure

```
custom_spells/
├── spells.json              # All spells database
└── individual/              # Individual spell exports
    ├── spell_300_fireball.json
    ├── spell_301_ice_blast.json
    └── ...
```

## Validation Reference

### Common Errors

- ❌ **Empty spell name**: Spell name is required
- ❌ **Spaces in internal name**: Use camelCase or underscores
- ❌ **Negative values**: Damage, mana, range cannot be negative
- ❌ **Max damage < min damage**: Fix damage range
- ❌ **Missing levels**: Spell must have level definitions

### Common Warnings

- ⚠️ **Very high DPS**: May be overpowered (>100 DPS)
- ⚠️ **Very low DPS**: May be underpowered (<5 DPS for attacks)
- ⚠️ **Zero mana cost**: Creates a free spell
- ⚠️ **Zero cooldown**: Allows instant recasting
- ⚠️ **Missing visual effects**: Recommended for better gameplay
- ⚠️ **Damage doesn't increase**: Check scaling configuration

## Balance Guidelines

### Attack Spells
- **Weak**: Power Rating < 20
- **Balanced**: Power Rating 20-40
- **Strong**: Power Rating 40-60
- **Overpowered**: Power Rating > 60

### Typical DPS Ranges (Max Level)
- **Light Attack**: 15-25 DPS
- **Medium Attack**: 25-40 DPS
- **Heavy Attack**: 40-60 DPS
- **Ultimate**: 60+ DPS (long cooldown)

### Mana Efficiency
- **Efficient**: 3-7 damage per mana
- **Balanced**: 2-3 damage per mana
- **Costly**: < 2 damage per mana

## Tips & Best Practices

### Spell Design
1. **Start Simple**: Begin with basic spells before complex ones
2. **Use Templates**: Duplicate existing spells as starting points
3. **Test Progression**: Review Level 1 vs Max Level stats
4. **Balance Check**: Aim for "Balanced" or "Strong" ratings
5. **Name Consistency**: Keep internal names alphanumeric

### Scaling Selection
- **Linear**: Best for steady, predictable growth
- **Exponential**: Good for ultimate spells that scale heavily
- **Logarithmic**: Useful for utility spells with diminishing returns
- **Custom**: For unique progression patterns

### Browser Usage
1. Use filters to narrow down large spell lists
2. Review spell details before selecting
3. Compare similar spells for consistency
4. Check DPS column for quick power comparison

### Effect Naming
- Follow existing game effect naming conventions
- Use descriptive names (e.g., "CastFire", "ProjectileFireBall")
- Keep sound file names consistent with game files

## Troubleshooting

### Import Errors

**Problem**: Cannot import spell models

**Solution**:
```bash
# Ensure TirganachReloaded is in Python path
export PYTHONPATH="/path/to/SpellSmut/src:$PYTHONPATH"

# Or run from the src directory
cd /path/to/SpellSmut/src
python spell_forge.py
```

### Validation Failures

**Problem**: Spell fails validation

**Solution**:
1. Check Phase 7 validation output
2. Fix all ❌ errors first
3. Address ⚠️ warnings if possible
4. Use browser to compare with working spells

### Missing Spells

**Problem**: Spells don't appear in browser

**Solution**:
- Check `custom_spells/spells.json` exists
- Verify JSON is valid (use JSON validator)
- Ensure spell IDs are in 300+ range

## Advanced Features

### Spell Templates

Load from TirganachReloaded templates:
```python
from TirganachReloaded.cff_editor.models.spell_templates import SPELL_TEMPLATES

# Fireball template
# Ice Blast template
# Holy Heal template
# Chain Lightning template
# Regeneration Aura template
# Summon Wolf template
```

### Custom Schools

Create custom magic schools in Phase 2:
- Set `CUSTOM` as the magic school
- Define custom school name
- Set color code
- Add description

### Triggered Effects

Advanced spells can have:
- **Auras**: Area effects around caster
- **Projectile Properties**: Bounce, pierce, multiple projectiles
- **Overtime Effects**: Continuous damage/healing

## Integration with Other Tools

The Spell Forge works alongside:
- **Weapon Forge**: Similar interface for weapons
- **Armor Forge**: Similar interface for armor
- **CFF Editor**: Full game data editing

## Contributing

To add new features:
1. Edit `spell_forge.py` for core functionality
2. Update `spell_validator.py` for new validation rules
3. Update this README with documentation

## Version History

- **v1.0**: Initial standalone release
  - 7-phase creation system
  - Advanced browser with filtering
  - Validation system
  - Multiple scaling modes
  - Export to JSON

## License

Part of the SpellSmut / TirganachReloaded project.

## Support

For issues or questions:
1. Check this README
2. Review example spells in `custom_spells/`
3. Compare with weapon/armor forge patterns
4. Check validation output for guidance
