# Spell Forge - GUI Version

A graphical wizard interface for creating custom spells, following the same pattern as the Weapon and Armor forges.

## Features

- **7-Page Wizard Interface**: Step-by-step guided spell creation
- **Advanced Spell Browser**: Filter by school, type, and search by name with live preview
- **Visual Design**: Color-coded schools, real-time validation feedback
- **Edit & Duplicate**: Load existing spells to modify or copy
- **Balance Metrics**: See DPS, damage per mana, and power ratings
- **Validation**: Built-in checks with error and warning display
- **Auto-Export**: Saves to JSON automatically

## Installation

### Requirements

```bash
pip install PySide6
```

The Spell Forge GUI requires:
- Python 3.7+
- PySide6 (Qt for Python)
- TirganachReloaded spell models (included in this project)

### Quick Setup

```bash
cd /path/to/SpellSmut/src
pip install PySide6

# Populate template spells (first time only)
python populate_spell_templates.py

# Launch the wizard
python spell_forge_wizard.py
```

**First Time Setup:**
Run `populate_spell_templates.py` to create 6 example spells:
- **Fireball** (Fire Attack) - ID 301
- **Ice Blast** (Ice Attack) - ID 302
- **Holy Heal** (White Heal) - ID 303
- **Chain Lightning** (Earth AOE) - ID 304
- **Regeneration Aura** (White Buff) - ID 305
- **Summon Wolf** (Black Summon) - ID 306

These templates provide a great starting point for browsing, learning, and duplication!

## Usage

### Launching the Wizard

```bash
python spell_forge_wizard.py
```

Or integrate into your application:

```python
from spell_forge_wizard import SpellForgeWizard
from PySide6.QtWidgets import QApplication

app = QApplication([])
wizard = SpellForgeWizard()
wizard.show()
app.exec()
```

## Wizard Pages

### Page 1: Mode Selection & ID Assignment

**Choose how to create your spell:**

- **Create New Spell**: Start with a blank slate
- **Edit Existing Spell**: Load and modify an existing spell
- **Duplicate & Modify**: Copy an existing spell with a new ID

**ID Assignment:**
- Spell IDs start at 300 (custom spell range)
- Automatically suggests next available ID
- Can manually specify ID if needed

**Spell Browser:**
- Click "Browse Spells..." to open the advanced browser
- Filter by Magic School (FIRE, ICE, WHITE, BLACK, MENTAL, EARTH)
- Filter by Spell Type (ATTACK, HEAL, BUFF, DEBUFF, etc.)
- Search by name (live filtering)
- Preview spell details before selection
- Color-coded schools for easy identification

### Page 2: Basic Properties

**Define spell identity:**

- **Spell Name**: Display name (e.g., "Inferno Blast")
- **Internal Name**: Code-friendly name, no spaces (e.g., "InfernoBlast")
- **Description**: Flavor text describing the spell
- **Magic School**:
  - WHITE (0) - Holy/Life magic
  - FIRE (1) - Fire elemental
  - ICE (2) - Ice elemental
  - BLACK (3) - Necromancy/Dark
  - MENTAL (4) - Mind/Illusion
  - EARTH (5) - Earth elemental
  - CUSTOM (99) - User-defined
- **Spell Type**: ATTACK, HEAL, BUFF, DEBUFF, SUMMON, AOE, UTILITY

### Page 3: Target & Mechanics

**Configure spell behavior:**

- **Target Type**:
  - SINGLE: Single target attack/heal
  - AOE: Area of effect
  - SELF: Self-cast only
  - CONE: Cone-shaped area
  - CHAIN: Bounces between targets

- **Projectile**: Check if spell fires a projectile
- **Base Range**: Distance spell can reach (0-100 units)
- **AOE Radius**: Area of effect size (0-50 units)
- **Duration**: How long effects last (0-300 seconds)

### Page 4: Level Progression & Scaling

**Configure power across 1-15 levels:**

**Number of Levels:**
- Choose 1-15 spell levels

**Level 1 Base Stats:**
- **Minimum Damage**: Lower damage bound
- **Maximum Damage**: Upper damage bound
- **Mana Cost**: Mana required to cast
- **Cooldown**: Seconds before spell can be recast
- **Cast Time**: Seconds to complete casting

**Scaling Mode:**

- **Linear**: Steady, predictable growth
  - Damage: +10/+12 per level
  - Mana: +3 per level
  - Cooldown: -0.1s per level

- **Exponential**: Accelerating power (1.15x factor)
  - Damage: ×1.15 per level
  - Mana: ×1.12 per level
  - Best for ultimate spells

- **Logarithmic**: Diminishing returns
  - Slower growth at higher levels
  - Good for utility spells

- **Custom**: Manual configuration
  - Define each level individually
  - Complete control over progression

### Page 5: Visual Effects

**Assign visual effect names:**

- **Cast Effect**: Played when casting begins (e.g., "CastFire")
- **Projectile Effect**: Visual for projectile (e.g., "ProjectileFireBall")
- **Resolve Effect**: Impact/hit effect (e.g., "ResolveFireExplosion")
- **Target Effect**: Effect on target
- **Over Time Effect**: Continuous visual for DoT/HoT spells

### Page 6: Sound Effects

**Assign sound effect names:**

- **Cast Sound**: Sound when casting (e.g., "spell_fire_cast")
- **Projectile Sound**: Sound during projectile flight
- **Resolve Sound**: Sound on impact
- **Hit Sound**: Sound when damage is dealt (e.g., "spell_hit_fireburst")

### Page 7: Review & Export

**Final review and validation:**

**Spell Summary:**
- Complete overview of all properties
- Level 1 vs Max Level stat comparison
- Balance metrics display

**Balance Metrics:**
- **Damage per Mana**: Efficiency rating
- **DPS**: Damage per second at max level
- **Power Rating**: Overall power score (0-100+)
- **Balance Category**: Weak / Balanced / Strong / Overpowered

**Validation Results:**

✓ **Valid**: Green checkmark, ready to export

❌ **Errors** (must fix):
- Empty spell name
- Spaces in internal name
- Negative values
- Invalid damage ranges
- Missing required fields

⚠️ **Warnings** (recommended to address):
- Very high/low DPS
- Overpowered balance rating
- Missing visual/sound effects
- Unusual stat progressions

**Export:**
- Click "Finish" to export spell
- Saves to `custom_spells/spells.json`
- Creates individual file in `custom_spells/individual/`
- Option to create another spell after completion

## Spell Browser Details

The browser provides powerful filtering and preview capabilities:

### Filtering

**School Filter:**
- Dropdown with all magic schools
- "All Schools" to show everything
- Live filtering as you select

**Type Filter:**
- Dropdown with all spell types
- "All Types" to show everything
- Filters ATTACK, HEAL, BUFF, etc.

**Name Search:**
- Live text search
- Partial matching
- Case-insensitive

**Clear Filters:**
- One-click filter reset
- Shows all spells again

### Table Display

Columns:
- **ID**: Spell identifier (300+)
- **Name**: Spell display name
- **School**: Color-coded magic school
- **Type**: Spell type (capitalized)
- **Levels**: Number of levels (1-15)
- **Max DPS**: DPS at highest level
- **Range**: Base casting range

**Color Coding:**
- FIRE: Red-Orange (#FF4500)
- ICE: Deep Sky Blue (#00BFFF)
- WHITE: Gold (#FFD700)
- BLACK: Dark Magenta (#8B008B)
- MENTAL: Medium Purple (#9370DB)
- EARTH: Saddle Brown (#8B4513)

### Preview Panel

Shows detailed spell information:
- Full spell name
- School and type
- Target type and range
- AOE radius
- Projectile status
- Duration
- Level 1 stats (damage, mana, DPS)
- Max level stats
- Description text

### Selection

- **Single-click**: Select and preview
- **Double-click**: Select and close browser
- **Select Button**: Confirm selection
- **Cancel Button**: Close without selecting

## Examples

### Example 1: Creating a Fire Attack Spell

1. **Mode Selection**: Choose "Create New Spell", ID 300
2. **Basic Properties**:
   - Name: "Fireball"
   - Internal Name: "Fireball"
   - School: FIRE (1)
   - Type: ATTACK
3. **Mechanics**:
   - Target: SINGLE
   - Projectile: ✓ Checked
   - Range: 25 units
   - AOE: 0
4. **Level Progression**:
   - Levels: 15
   - Base Damage: 15-20
   - Mana: 10
   - Cooldown: 3.0s
   - Cast Time: 1.5s
   - Scaling: EXPONENTIAL
5. **Visual Effects**:
   - Cast: "CastFire"
   - Projectile: "ProjectileFireBall"
   - Resolve: "ResolveFireExplosion"
6. **Sound Effects**:
   - Cast: "spell_fire_cast"
   - Hit: "spell_hit_fireburst"
7. **Review**: Check balance (should be "Strong"), export

### Example 2: Editing an Existing Spell

1. **Mode Selection**: Choose "Edit Existing Spell"
2. **Browse**: Click "Browse Spells..."
3. **Filter**: Select "FIRE" from School filter
4. **Search**: Type "fireball" in name search
5. **Select**: Double-click the spell to load
6. **Modify**: Change any properties across the pages
7. **Review**: Validate and export (overwrites original)

### Example 3: Duplicating a Spell

1. **Mode Selection**: Choose "Duplicate & Modify"
2. **Browse**: Find the spell you want to copy
3. **Select**: Choose the spell (ID auto-increments)
4. **Modify**: Change name and properties
5. **Review**: Export as new spell with new ID

## File Structure

```
custom_spells/
├── spells.json                      # All spells database
└── individual/                      # Individual exports
    ├── spell_300_fireball.json
    ├── spell_301_ice_blast.json
    └── ...
```

## Integration with Other Tools

The Spell Forge GUI follows the same pattern as:

- **Weapon Forge Wizard**: Similar 6-page wizard
- **Armor Forge**: Similar 7-phase system
- **CFF Editor**: Main game data editor

All use consistent:
- ID management
- Browser interfaces
- Validation systems
- Export formats

## Keyboard Shortcuts

- **Enter**: Advance to next page (when page is valid)
- **Esc**: Cancel wizard
- **Tab**: Navigate between fields
- **Ctrl+F**: Focus name search in browser (when open)

## Tips for Best Results

### Spell Design

1. **Start Simple**: Create basic spells before complex ones
2. **Use Browser**: Duplicate similar spells as templates
3. **Check Balance**: Review the balance category before exporting
4. **Test Scaling**: Compare Level 1 vs Max Level stats
5. **Name Convention**: Keep internal names alphanumeric

### Using the Browser

1. **Filter First**: Narrow down by school and type
2. **Search Second**: Use name search for specific spells
3. **Preview**: Always preview before selecting
4. **Compare**: Use Max DPS column to compare power

### Balance Guidelines

**Attack Spells:**
- Weak: Power Rating < 20
- Balanced: 20-40
- Strong: 40-60
- Overpowered: 60+

**Typical DPS (Max Level):**
- Light: 15-25 DPS
- Medium: 25-40 DPS
- Heavy: 40-60 DPS
- Ultimate: 60+ DPS (long cooldown)

## Troubleshooting

### Wizard Won't Start

**Problem**: ImportError or module not found

**Solution**:
```bash
# Install PySide6
pip install PySide6

# Ensure TirganachReloaded is accessible
cd /path/to/SpellSmut/src
python spell_forge_wizard.py
```

### Browser Shows No Spells

**Problem**: "No spells loaded" message

**Solution**:
1. Create at least one spell first
2. Check that `custom_spells/spells.json` exists
3. Verify JSON is valid

### Validation Errors

**Problem**: Red errors in Review page

**Solution**:
1. Go back to the page with the issue
2. Fix the specific error (shown in message)
3. Return to Review page
4. Errors must be fixed before export

### Spell Won't Export

**Problem**: Export fails silently

**Solution**:
1. Check file permissions on `custom_spells/` directory
2. Verify spell has no validation errors
3. Check that JSON file isn't locked by another program

## Advanced Features

### Custom Schools

When selecting CUSTOM (99) as the magic school:
1. Define your own school name
2. Set custom color code
3. Add school description
4. Appears as custom entry in browser

### Multiple Wizards

You can run multiple wizard instances:
```python
wizard1 = SpellForgeWizard()
wizard2 = SpellForgeWizard()
wizard1.show()
wizard2.show()
```

Each maintains independent state.

## Differences from CLI Version

| Feature | CLI Version | GUI Version |
|---------|-------------|-------------|
| Interface | Text prompts | Visual wizard |
| Navigation | Linear only | Back/forward navigation |
| Browser | Text table | Rich GUI table |
| Filtering | Menu-driven | Live filtering |
| Preview | Text only | HTML preview |
| Validation | End of process | Real-time feedback |
| Platform | Any terminal | Requires Qt |

## Future Enhancements

Potential additions:
- Visual effect preview
- Sound effect playback
- Spell comparison tool
- Import from game files
- Export to CFF format
- Spell stat graphs
- Advanced custom scaling editor
- Spell template library

## Version History

- **v1.0**: Initial GUI release
  - 7-page wizard
  - Advanced browser
  - Validation system
  - JSON export

## License

Part of the SpellSmut / TirganachReloaded project.

## Support

For issues:
1. Check this README
2. Verify PySide6 installation
3. Test CLI version first
4. Check console for error messages
