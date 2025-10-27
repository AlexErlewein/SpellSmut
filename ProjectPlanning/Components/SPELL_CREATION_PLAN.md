# Spell Creation System Plan
## 🧙 The Spell Wizard (Pun Intended!)

## Overview

This plan defines a comprehensive **Spell Creation System** - a wizard-style interface (pun absolutely intended!) for creating custom SpellForce spells with full level progression (1-15 levels). Modders can design spells with visual effects, sound effects, and stat scaling without writing a single line of Lua code.

**Status**: 🟡 Planning Phase  
**Priority**: High  
**Dependencies**: Quest Editor/Creator (for reference architecture)

---

## System Goals

### Primary Objectives

1. **Spell Wizard Interface**: Guided spell creation in 6 intuitive steps
2. **Level Progression System**: Configure 1-15 spell levels with automatic stat scaling
3. **Visual Effect Builder**: Drag-drop VFX components (cast, projectile, resolve, target, overtime)
4. **Sound Integration**: Select from existing sounds or add custom audio
5. **Export to Lua**: Generate production-ready Lua scripts and spell data

### Secondary Objectives

- Template-based spell creation (Fireball, Healing, Buff, Summon, etc.)
- Spell validation (detect invalid combinations)
- Balance calculator (estimate damage/healing per mana cost)
- Visual preview (see VFX in action before export)
- Import existing spells for modification

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                  Spell Creation Workflow                        │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Spell      │─▶│   Level      │─▶│   Visual &   │         │
│  │   Wizard     │  │  Progression │  │   Audio      │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│        │                  │                  │                 │
│        ▼                  ▼                  ▼                 │
│  Basic Info          Stats Scaling       VFX + SFX            │
│  Magic School        Per-Level Data      Effect Builder       │
│  Spell Type          Auto-Scaling        Sound Selection      │
│        │                  │                  │                 │
│        └──────────────────┴──────────────────┘                 │
│                           │                                    │
│                           ▼                                    │
│                  ┌──────────────┐                              │
│                  │   Export &   │                              │
│                  │   Testing    │                              │
│                  └──────────────┘                              │
│                           │                                    │
│                           ▼                                    │
│                   Lua Scripts                                  │
│                   Test Spell Book                              │
│                   In-Game Test                                 │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Spell System Fundamentals

### Spell Structure in SpellForce

Every spell in SpellForce consists of:

1. **Spell Line** (kGdSpellLine*): Unique identifier for the spell
2. **Magic School**: White, Black, Fire, Ice, Earth, Mental
3. **Spell Type**: Attack, Heal, Buff, Debuff, Summon, Utility
4. **Level Progression**: 1-15 levels with scaling stats
5. **Visual Effects**: Cast, Projectile, Resolve, Target, Overtime
6. **Sound Effects**: Cast sound, travel sound, impact sound
7. **Stats**: Damage/healing, mana cost, cooldown, range, AOE radius

### Stat Scaling Example

**FireBurst Spell** (Levels 1-15):

| Level | Damage | Mana Cost | Range | Cooldown |
|-------|--------|-----------|-------|----------|
| 1 | 20-25 | 10 | 20 | 3s |
| 5 | 45-55 | 18 | 22 | 3s |
| 10 | 80-100 | 30 | 25 | 2.5s |
| 15 | 140-170 | 50 | 28 | 2s |

**Key Insight**: Most stats scale linearly or logarithmically with level.

---

## Phase 1: Spell Wizard Interface

### 1.1 Wizard Design

**Implementation**: Separate window from existing editors (accessed via `Tools → Spell Wizard`)

**Wizard Steps**:

```
Step 1: Spell Basics
  ├─ Spell Name (e.g., "Inferno Blast")
  ├─ Internal Name (e.g., "InfernoBlast" - no spaces)
  ├─ Magic School (White, Black, Fire, Ice, Earth, Mental)
  ├─ Spell Type (Attack, Heal, Buff, Debuff, Summon, AOE, Utility)
  └─ Description (player-visible tooltip text)

Step 2: Target & Mechanics
  ├─ Target Type (Single, AOE, Self, Cone, Chain)
  ├─ Projectile (Yes/No - does it travel or instant?)
  ├─ Range (Base range at level 1)
  ├─ AOE Radius (if applicable)
  ├─ Duration (for buffs/debuffs/summons)
  └─ Special Effects (Stun, Slow, DOT, etc.)

Step 3: Level Progression (1-15 levels)
  ├─ Number of Levels (1-15)
  ├─ Base Stats (Level 1)
  │   ├─ Damage/Healing (min-max range)
  │   ├─ Mana Cost
  │   ├─ Cooldown
  │   └─ Cast Time
  ├─ Scaling Mode
  │   ├─ Linear (same increase per level)
  │   ├─ Exponential (accelerating growth)
  │   ├─ Logarithmic (diminishing returns)
  │   └─ Custom (manual per-level editing)
  └─ Preview Table (shows all 15 levels)

Step 4: Visual Effects
  ├─ Cast Effect (VFX at caster)
  ├─ Projectile Effect (VFX during travel)
  ├─ Resolve Effect (VFX at impact/target)
  ├─ Target Effect (VFX on hit target)
  ├─ Overtime Effect (persistent VFX for buffs/debuffs)
  └─ Effect Templates (Fire, Ice, Lightning, Holy, Dark, etc.)

Step 5: Sound Effects
  ├─ Cast Sound (spell_*_cast)
  ├─ Projectile Sound (spell_*_travel)
  ├─ Impact Sound (spell_*_resolve)
  ├─ Hit Sound (spell_*_hit)
  └─ Sound Browser (preview existing game sounds)

Step 6: Review & Export
  ├─ Spell Summary (all configured data)
  ├─ Stats Table (all 15 levels)
  ├─ VFX Preview (animated preview if possible)
  ├─ Validation Results (errors/warnings)
  ├─ Balance Score (estimated power level)
  └─ Export Options (Lua scripts, test spell book)
```

### 1.2 UI Components

**SpellCreatorWizard Class** (new file: `spell_creator_wizard.py`)

```python
class SpellCreatorWizard(QWizard):
    """Multi-step wizard for spell creation"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SpellForce Spell Wizard 🧙")
        self.setWizardStyle(QWizard.ModernStyle)
        
        # Add wizard pages
        self.addPage(SpellBasicsPage())
        self.addPage(TargetMechanicsPage())
        self.addPage(LevelProgressionPage())  # KEY PAGE!
        self.addPage(VisualEffectsPage())
        self.addPage(SoundEffectsPage())
        self.addPage(ReviewExportPage())
```

### 1.3 Data Collection

**Spell Data Model**:

```python
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional
from enum import Enum

class MagicSchool(Enum):
    WHITE = 0    # Holy/Life
    FIRE = 1     # Fire Elemental
    ICE = 2      # Ice Elemental
    BLACK = 3    # Necromancy/Dark
    MENTAL = 4   # Mind/Illusion
    EARTH = 5    # Earth Elemental

class SpellType(Enum):
    ATTACK = "attack"
    HEAL = "heal"
    BUFF = "buff"
    DEBUFF = "debuff"
    SUMMON = "summon"
    AOE = "aoe"
    UTILITY = "utility"

class TargetType(Enum):
    SINGLE = "single"
    AOE = "aoe"
    SELF = "self"
    CONE = "cone"
    CHAIN = "chain"

class ScalingMode(Enum):
    LINEAR = "linear"
    EXPONENTIAL = "exponential"
    LOGARITHMIC = "logarithmic"
    CUSTOM = "custom"

@dataclass
class SpellLevel:
    """Stats for a single spell level"""
    level: int  # 1-15
    damage_min: int
    damage_max: int
    mana_cost: int
    cooldown: float  # seconds
    cast_time: float  # seconds
    range: float
    aoe_radius: float  # 0 if not AOE
    duration: float  # seconds (for buffs/debuffs/summons)

@dataclass
class SpellCreationData:
    """Complete spell definition"""
    
    # Step 1: Basics
    spell_name: str  # "Inferno Blast"
    internal_name: str  # "InfernoBlast"
    magic_school: MagicSchool
    spell_type: SpellType
    description: str
    
    # Step 2: Mechanics
    target_type: TargetType
    has_projectile: bool
    base_range: float
    aoe_radius: float
    duration: float
    special_effects: List[str]  # ["stun", "burn", etc.]
    
    # Step 3: Level Progression
    num_levels: int  # 1-15
    levels: List[SpellLevel]  # One for each level
    scaling_mode: ScalingMode
    
    # Step 4: Visual Effects
    vfx_cast: str  # Effect name or template
    vfx_projectile: str
    vfx_resolve: str
    vfx_target: str
    vfx_overtime: str
    
    # Step 5: Sound Effects
    sfx_cast: str  # Sound file name
    sfx_projectile: str
    sfx_resolve: str
    sfx_hit: str
    
    # Metadata
    spell_line_id: int  # Auto-assigned (300+)
    created_date: str
    author: str
```

---

## Phase 2: Level Progression System

### 2.1 The Level Progression Page (CORE FEATURE)

**LevelProgressionPage Widget** - The heart of the Spell Wizard!

```python
class LevelProgressionPage(QWizardPage):
    """Configure spell stats across 1-15 levels"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Level Progression")
        self.setSubTitle("Configure how your spell scales from level 1 to 15")
        
        layout = QVBoxLayout()
        
        # Number of levels selector
        level_group = QGroupBox("Spell Levels")
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Number of Levels:"))
        self.level_spinbox = QSpinBox()
        self.level_spinbox.setRange(1, 15)
        self.level_spinbox.setValue(15)  # Default to max
        level_layout.addWidget(self.level_spinbox)
        level_group.setLayout(level_layout)
        layout.addWidget(level_group)
        
        # Base stats (Level 1)
        base_group = QGroupBox("Base Stats (Level 1)")
        base_layout = QFormLayout()
        self.damage_min_spin = QSpinBox()
        self.damage_max_spin = QSpinBox()
        self.mana_cost_spin = QSpinBox()
        self.cooldown_spin = QDoubleSpinBox()
        self.cast_time_spin = QDoubleSpinBox()
        base_layout.addRow("Damage Min:", self.damage_min_spin)
        base_layout.addRow("Damage Max:", self.damage_max_spin)
        base_layout.addRow("Mana Cost:", self.mana_cost_spin)
        base_layout.addRow("Cooldown (sec):", self.cooldown_spin)
        base_layout.addRow("Cast Time (sec):", self.cast_time_spin)
        base_group.setLayout(base_layout)
        layout.addWidget(base_group)
        
        # Scaling mode
        scaling_group = QGroupBox("Scaling Mode")
        scaling_layout = QVBoxLayout()
        self.scaling_combo = QComboBox()
        self.scaling_combo.addItems(["Linear", "Exponential", "Logarithmic", "Custom"])
        scaling_layout.addWidget(self.scaling_combo)
        scaling_layout.addWidget(QLabel("Linear: Same increase per level\n"
                                        "Exponential: Accelerating growth\n"
                                        "Logarithmic: Diminishing returns\n"
                                        "Custom: Edit each level manually"))
        scaling_group.setLayout(scaling_layout)
        layout.addWidget(scaling_group)
        
        # Preview table
        preview_group = QGroupBox("Level Preview")
        preview_layout = QVBoxLayout()
        self.preview_table = QTableWidget(15, 6)
        self.preview_table.setHorizontalHeaderLabels([
            "Level", "Damage", "Mana", "Cooldown", "Cast Time", "Range"
        ])
        preview_layout.addWidget(self.preview_table)
        
        # Recalculate button
        recalc_btn = QPushButton("Recalculate Scaling")
        recalc_btn.clicked.connect(self.update_level_preview)
        preview_layout.addWidget(recalc_btn)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Edit individual level button
        edit_btn = QPushButton("Edit Individual Levels (Custom Mode)")
        edit_btn.clicked.connect(self.open_level_editor)
        layout.addWidget(edit_btn)
        
        self.setLayout(layout)
    
    def update_level_preview(self):
        """Recalculate and display all level stats"""
        scaling_mode = self.scaling_combo.currentText().lower()
        num_levels = self.level_spinbox.value()
        
        base_damage_min = self.damage_min_spin.value()
        base_damage_max = self.damage_max_spin.value()
        base_mana = self.mana_cost_spin.value()
        base_cooldown = self.cooldown_spin.value()
        
        for level in range(1, num_levels + 1):
            # Apply scaling formula
            if scaling_mode == "linear":
                damage_min = base_damage_min + (level - 1) * 10
                damage_max = base_damage_max + (level - 1) * 12
                mana = base_mana + (level - 1) * 3
                cooldown = max(1.0, base_cooldown - (level - 1) * 0.1)
            
            elif scaling_mode == "exponential":
                damage_min = int(base_damage_min * (1.15 ** (level - 1)))
                damage_max = int(base_damage_max * (1.15 ** (level - 1)))
                mana = int(base_mana * (1.12 ** (level - 1)))
                cooldown = max(1.0, base_cooldown * (0.95 ** (level - 1)))
            
            elif scaling_mode == "logarithmic":
                import math
                factor = 1 + math.log(level) / 2
                damage_min = int(base_damage_min * factor)
                damage_max = int(base_damage_max * factor)
                mana = int(base_mana * factor)
                cooldown = base_cooldown
            
            # Update table
            row = level - 1
            self.preview_table.setItem(row, 0, QTableWidgetItem(str(level)))
            self.preview_table.setItem(row, 1, QTableWidgetItem(f"{damage_min}-{damage_max}"))
            self.preview_table.setItem(row, 2, QTableWidgetItem(str(mana)))
            self.preview_table.setItem(row, 3, QTableWidgetItem(f"{cooldown:.1f}s"))
            # ... fill other columns
    
    def open_level_editor(self):
        """Open dialog to manually edit each level"""
        dialog = LevelEditorDialog(self.get_current_levels(), self)
        if dialog.exec() == QDialog.Accepted:
            self.set_levels(dialog.get_levels())
            self.update_preview_from_custom_levels()
```

### 2.2 Level Scaling Formulas

**Linear Scaling**:
```python
def linear_scale(base_value, level, per_level_increase):
    return base_value + (level - 1) * per_level_increase
```

**Exponential Scaling**:
```python
def exponential_scale(base_value, level, growth_rate=1.15):
    return int(base_value * (growth_rate ** (level - 1)))
```

**Logarithmic Scaling**:
```python
import math

def logarithmic_scale(base_value, level):
    factor = 1 + math.log(level) / 2
    return int(base_value * factor)
```

### 2.3 Per-Level Editing Dialog

For users who want full control:

```python
class LevelEditorDialog(QDialog):
    """Edit stats for each individual level"""
    
    def __init__(self, levels: List[SpellLevel], parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Individual Levels")
        self.setModal(True)
        
        layout = QVBoxLayout()
        
        # Tabbed interface - one tab per level
        self.tabs = QTabWidget()
        
        for level in range(1, 16):
            level_widget = LevelEditWidget(levels[level - 1])
            self.tabs.addTab(level_widget, f"Level {level}")
        
        layout.addWidget(self.tabs)
        
        # Buttons
        btn_layout = QHBoxLayout()
        copy_btn = QPushButton("Copy Level →")
        copy_btn.clicked.connect(self.copy_level_to_next)
        paste_btn = QPushButton("Paste to All")
        paste_btn.clicked.connect(self.paste_to_all_levels)
        btn_layout.addWidget(copy_btn)
        btn_layout.addWidget(paste_btn)
        btn_layout.addStretch()
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
```

---

## Phase 3: Visual Effects System

### 3.1 VFX Component Types

SpellForce spells have 5 VFX component slots:

1. **effectscast**: Visual at caster during cast
2. **effectsprojectile**: Visual during projectile travel (if applicable)
3. **effectsresolve**: Visual at impact/resolution point
4. **effectstarget**: Visual on the target (hit effect)
5. **effectsovertime**: Persistent visual (buffs/debuffs/auras)

### 3.2 VFX Template Library

**VisualEffectsPage Widget**:

```python
class VisualEffectsPage(QWizardPage):
    """Configure visual effects for spell"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Visual Effects")
        self.setSubTitle("Design how your spell looks")
        
        layout = QVBoxLayout()
        
        # Cast Effect
        cast_group = QGroupBox("Cast Effect (at caster)")
        cast_layout = QHBoxLayout()
        self.cast_combo = QComboBox()
        self.cast_combo.addItems([
            "Fire Cast (flames from hands)",
            "Ice Cast (frost swirl)",
            "White Cast (holy light)",
            "Black Cast (dark lightning)",
            "Mental Cast (psionic rings)",
            "Custom..."
        ])
        cast_layout.addWidget(self.cast_combo)
        preview_cast_btn = QPushButton("Preview")
        preview_cast_btn.clicked.connect(lambda: self.preview_vfx("cast"))
        cast_layout.addWidget(preview_cast_btn)
        cast_group.setLayout(cast_layout)
        layout.addWidget(cast_group)
        
        # Projectile Effect
        projectile_group = QGroupBox("Projectile Effect (during travel)")
        projectile_layout = QHBoxLayout()
        self.projectile_combo = QComboBox()
        self.projectile_combo.addItems([
            "Fireball (flame projectile)",
            "Ice Shard (ice projectile)",
            "Lightning Bolt (electric arc)",
            "Dark Bolt (shadowy missile)",
            "None (instant spell)",
            "Custom..."
        ])
        projectile_layout.addWidget(self.projectile_combo)
        preview_proj_btn = QPushButton("Preview")
        preview_proj_btn.clicked.connect(lambda: self.preview_vfx("projectile"))
        projectile_layout.addWidget(preview_proj_btn)
        projectile_group.setLayout(projectile_layout)
        layout.addWidget(projectile_group)
        
        # Resolve Effect
        resolve_group = QGroupBox("Resolve Effect (at impact)")
        resolve_layout = QHBoxLayout()
        self.resolve_combo = QComboBox()
        self.resolve_combo.addItems([
            "Fire Explosion (burst of flames)",
            "Ice Shatter (crystalline break)",
            "Holy Flash (white burst)",
            "Dark Implosion (void collapse)",
            "Smoke Puff (generic impact)",
            "Custom..."
        ])
        resolve_layout.addWidget(self.resolve_combo)
        preview_resolve_btn = QPushButton("Preview")
        preview_resolve_btn.clicked.connect(lambda: self.preview_vfx("resolve"))
        resolve_layout.addWidget(preview_resolve_btn)
        resolve_group.setLayout(resolve_layout)
        layout.addWidget(resolve_group)
        
        # Target Effect
        target_group = QGroupBox("Target Effect (on hit target)")
        target_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Burn Effect (flames on target)",
            "Freeze Effect (ice crystals)",
            "Heal Glow (white particles)",
            "Curse Aura (dark smoke)",
            "None",
            "Custom..."
        ])
        target_layout.addWidget(self.target_combo)
        target_group.setLayout(target_layout)
        layout.addWidget(target_group)
        
        # Overtime Effect (buffs/debuffs)
        overtime_group = QGroupBox("Overtime Effect (persistent)")
        overtime_layout = QHBoxLayout()
        self.overtime_combo = QComboBox()
        self.overtime_combo.addItems([
            "Fire Aura (continuous flames)",
            "Ice Aura (frost particles)",
            "Buff Glow (white sparkles)",
            "Debuff Cloud (dark mist)",
            "None",
            "Custom..."
        ])
        overtime_layout.addWidget(self.overtime_combo)
        overtime_group.setLayout(overtime_layout)
        layout.addWidget(overtime_group)
        
        # Color customization
        color_group = QGroupBox("Color Customization")
        color_layout = QFormLayout()
        self.color1_btn = QPushButton("Primary Color")
        self.color1_btn.clicked.connect(lambda: self.choose_color("primary"))
        self.color2_btn = QPushButton("Secondary Color")
        self.color2_btn.clicked.connect(lambda: self.choose_color("secondary"))
        color_layout.addRow("Primary:", self.color1_btn)
        color_layout.addRow("Secondary:", self.color2_btn)
        color_group.setLayout(color_layout)
        layout.addWidget(color_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def preview_vfx(self, effect_type):
        """Show animated preview of VFX"""
        # TODO: Implement VFX preview window
        QMessageBox.information(self, "VFX Preview", 
                                f"Preview for {effect_type} effect\n"
                                f"(Animation preview coming soon!)")
```

### 3.3 VFX Templates

**Pre-built Effect Templates**:

| Template | Cast | Projectile | Resolve | School |
|----------|------|-----------|---------|--------|
| **Fireball** | Flames from hands | Flame trail | Fire explosion | Fire |
| **Ice Shard** | Frost swirl | Ice projectile | Ice shatter | Ice |
| **Holy Heal** | White glow | None (instant) | Holy sparkles | White |
| **Dark Bolt** | Black lightning | Shadow missile | Dark implosion | Black |
| **Lightning** | Electric hands | Lightning arc | Thunder burst | Elemental |
| **Earth Spike** | Rock particles | None (ground) | Stone eruption | Earth |
| **Mind Blast** | Psionic rings | Mental wave | Psionic explosion | Mental |

---

## Phase 4: Sound Effects Integration

### 4.1 Sound Browser

**SoundEffectsPage Widget**:

```python
class SoundEffectsPage(QWizardPage):
    """Select sound effects for spell"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Sound Effects")
        self.setSubTitle("Choose sounds for your spell")
        
        layout = QVBoxLayout()
        
        # Cast Sound
        cast_group = QGroupBox("Cast Sound (spell initiation)")
        cast_layout = QHBoxLayout()
        self.cast_sound_combo = QComboBox()
        self.populate_cast_sounds()
        cast_layout.addWidget(self.cast_sound_combo)
        play_cast_btn = QPushButton("▶ Play")
        play_cast_btn.clicked.connect(lambda: self.play_sound("cast"))
        cast_layout.addWidget(play_cast_btn)
        cast_group.setLayout(cast_layout)
        layout.addWidget(cast_group)
        
        # Similar for projectile, resolve, hit sounds
        # ...
        
        # Sound browser button
        browse_btn = QPushButton("Browse All Sounds...")
        browse_btn.clicked.connect(self.open_sound_browser)
        layout.addWidget(browse_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def populate_cast_sounds(self):
        """Load cast sounds from game files"""
        cast_sounds = [
            "spell_white_cast",
            "spell_black_cast",
            "spell_fire_cast",
            "spell_ice_cast",
            "spell_earth_cast",
            "spell_mental_cast",
            "spell_melee_berserk",
            "spell_melee_heal",
            # ... (load from extracted audio files)
        ]
        self.cast_sound_combo.addItems(cast_sounds)
    
    def play_sound(self, sound_type):
        """Play selected sound"""
        # TODO: Implement audio playback
        QMessageBox.information(self, "Sound Preview", 
                                f"Playing {sound_type} sound\n"
                                f"(Audio preview coming soon!)")
    
    def open_sound_browser(self):
        """Open comprehensive sound browser"""
        dialog = SoundBrowserDialog(self)
        if dialog.exec() == QDialog.Accepted:
            selected_sounds = dialog.get_selected_sounds()
            # Apply to comboboxes
```

### 4.2 Sound Categories

From `DrwSound.lua`, spells use these sound events:

**Cast Sounds**:
- `spell_white_cast_*` (1-3 variants)
- `spell_black_cast_*` (1-3 variants)
- `spell_fire_cast_*` (1-2 variants)
- `spell_ice_cast_*` (1-2 variants)
- `spell_mental_cast_*` (1-2 variants)

**Resolve Sounds**:
- `spell_hit_default_white`
- `spell_hit_default_black`
- `spell_hit_fireburst`
- `spell_hit_iceburst`
- `spell_hit_explosion`
- `spell_hit_healing`

**Special Sounds**:
- `spell_hit_aura_white` (buff auras)
- `spell_hit_aura_black` (debuff auras)
- `spell_summon_*` (summon creatures)

---

## Phase 5: Lua Script Export

### 5.1 Export System

**SpellLuaExporter Class**:

```python
class SpellLuaExporter:
    """Generate Lua scripts from spell data"""
    
    def export_spell(self, spell_data: SpellCreationData) -> Dict[str, str]:
        """
        Export spell to Lua files
        
        Returns:
            Dict mapping file paths to Lua code content
        """
        
        files = {}
        
        # 1. sql_spellline.lua entry
        files["script/sql_spellline.lua"] = self.generate_spellline_entry(spell_data)
        
        # 2. Visual effects script
        files[f"object/object_effect_{spell_data.internal_name.lower()}.lua"] = \
            self.generate_vfx_script(spell_data)
        
        # 3. Sound event registration
        files["script/DrwSound.lua"] = self.generate_sound_entry(spell_data)
        
        return files
    
    def generate_spellline_entry(self, spell_data: SpellCreationData) -> str:
        """Generate sql_spellline.lua entry"""
        
        lua_code = f"""
-- Custom Spell: {spell_data.spell_name}
-- Generated by SpellForce Spell Wizard
-- Date: {spell_data.created_date}

[{spell_data.spell_line_id}] = {{
    includename="{spell_data.internal_name}",
    player=0,  -- Player can cast
    npc=0,     -- NPC can cast
    flag3=0,   -- Not an aura
    flag4=0,   -- Not a toggle
    flag5=1,
    flag6=0,
    flag7=0,
    flag8=0,
    effectscast={{"{spell_data.vfx_cast}"}},
    effectsresolve={{"{spell_data.vfx_resolve}"}},
    effectsprojectile={{"{spell_data.vfx_projectile}"}},
    effectstarget={{"{spell_data.vfx_target}"}},
    effectsovertime={{"{spell_data.vfx_overtime}"}},
    spelllinebase={spell_data.magic_school.value},
}}
"""
        return lua_code
    
    def generate_vfx_script(self, spell_data: SpellCreationData) -> str:
        """Generate visual effects Lua script"""
        
        lua_code = f"""
-- Visual Effects for {spell_data.spell_name}
-- Auto-generated by Spell Wizard

-- Cast Effect
{self.get_vfx_template(spell_data.vfx_cast, "cast")}
EffectSave("{spell_data.vfx_cast}")

-- Projectile Effect
{self.get_vfx_template(spell_data.vfx_projectile, "projectile")}
EffectSave("{spell_data.vfx_projectile}")

-- Resolve Effect
{self.get_vfx_template(spell_data.vfx_resolve, "resolve")}
EffectSave("{spell_data.vfx_resolve}")

-- Target Effect
{self.get_vfx_template(spell_data.vfx_target, "target")}
EffectSave("{spell_data.vfx_target}")

-- Overtime Effect
{self.get_vfx_template(spell_data.vfx_overtime, "overtime")}
EffectSave("{spell_data.vfx_overtime}")
"""
        return lua_code
    
    def generate_sound_entry(self, spell_data: SpellCreationData) -> str:
        """Generate DrwSound.lua entry"""
        
        internal_lower = spell_data.internal_name.lower()
        
        lua_code = f"""
-- Sound events for {spell_data.spell_name}
spell_{internal_lower}_cast = {{
    File = "{spell_data.sfx_cast}",
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 80,
}}

spell_{internal_lower}_resolve = {{
    File = "{spell_data.sfx_resolve}",
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 90,
}}

spell_{internal_lower}_hit = {{
    File = "{spell_data.sfx_hit}",
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 70,
}}
"""
        return lua_code
```

### 5.2 Spell Stats Export

**Generate Spell Book Entry** (for CFF file):

```python
def generate_spell_stats(spell_data: SpellCreationData) -> Dict[str, Any]:
    """Generate spell stats for all levels"""
    
    spell_stats = {
        "spell_name": spell_data.spell_name,
        "spell_line_id": spell_data.spell_line_id,
        "magic_school": spell_data.magic_school.value,
        "levels": []
    }
    
    for level_data in spell_data.levels:
        spell_stats["levels"].append({
            "level": level_data.level,
            "damage_min": level_data.damage_min,
            "damage_max": level_data.damage_max,
            "mana_cost": level_data.mana_cost,
            "cooldown": level_data.cooldown,
            "cast_time": level_data.cast_time,
            "range": level_data.range,
            "aoe_radius": level_data.aoe_radius,
            "duration": level_data.duration,
        })
    
    return spell_stats
```

---

## Phase 6: Testing & Validation

### 6.1 Spell Validation

**SpellValidator Class**:

```python
class SpellValidator:
    """Validate spell data before export"""
    
    def validate(self, spell_data: SpellCreationData) -> List[ValidationError]:
        errors = []
        warnings = []
        
        # Check spell name
        if not spell_data.spell_name:
            errors.append("Spell name is required")
        
        # Check internal name (no spaces)
        if " " in spell_data.internal_name:
            errors.append("Internal name cannot contain spaces")
        
        # Check level progression
        if len(spell_data.levels) != spell_data.num_levels:
            errors.append(f"Level count mismatch: expected {spell_data.num_levels}, got {len(spell_data.levels)}")
        
        # Validate stat scaling
        for i, level in enumerate(spell_data.levels):
            if level.damage_min > level.damage_max:
                errors.append(f"Level {i+1}: Min damage > Max damage")
            
            if level.mana_cost < 1:
                warnings.append(f"Level {i+1}: Mana cost is very low (free spell?)")
            
            if i > 0:
                prev_level = spell_data.levels[i - 1]
                if level.damage_max <= prev_level.damage_max:
                    warnings.append(f"Level {i+1}: Damage not increasing from previous level")
        
        # Check spell line ID uniqueness
        if self.spell_line_id_exists(spell_data.spell_line_id):
            errors.append(f"Spell Line ID {spell_data.spell_line_id} already exists")
        
        # Check VFX references
        for vfx_name in [spell_data.vfx_cast, spell_data.vfx_projectile, 
                         spell_data.vfx_resolve, spell_data.vfx_target, spell_data.vfx_overtime]:
            if vfx_name and not self.vfx_exists(vfx_name):
                warnings.append(f"VFX '{vfx_name}' not found in effect library")
        
        return errors, warnings
    
    def balance_check(self, spell_data: SpellCreationData) -> Dict[str, Any]:
        """Calculate spell balance metrics"""
        
        # Damage per mana (DPM)
        level_15 = spell_data.levels[14] if len(spell_data.levels) >= 15 else spell_data.levels[-1]
        avg_damage = (level_15.damage_min + level_15.damage_max) / 2
        dpm = avg_damage / level_15.mana_cost if level_15.mana_cost > 0 else 0
        
        # Damage per second (DPS) accounting for cooldown
        dps = avg_damage / (level_15.cooldown + level_15.cast_time)
        
        # Power rating (arbitrary scale)
        power_rating = (dpm * 10 + dps * 5) / 2
        
        return {
            "damage_per_mana": round(dpm, 2),
            "damage_per_second": round(dps, 2),
            "power_rating": round(power_rating, 1),
            "balance_category": self.categorize_power(power_rating),
        }
    
    def categorize_power(self, power_rating: float) -> str:
        if power_rating < 20:
            return "Weak"
        elif power_rating < 40:
            return "Balanced"
        elif power_rating < 60:
            return "Strong"
        else:
            return "Overpowered"
```

### 6.2 Test Spell Book

**Create Test Spell Book** (in-game item):

```python
def generate_test_spell_book(spell_data: SpellCreationData) -> str:
    """Generate item that teaches the custom spell"""
    
    # Item ID for spell book (9800 range for custom items)
    item_id = 9800 + spell_data.spell_line_id - 300
    
    item_def = f"""
-- Test Spell Book: {spell_data.spell_name}
-- Item ID: {item_id}

{{
    item_id = {item_id},
    item_name = "Spell Book: {spell_data.spell_name}",
    item_type = "spell_book",
    icon_id = 1234,  -- Spell book icon
    teaches_spell = {spell_data.spell_line_id},
    spell_levels = {spell_data.num_levels},
    description = "{spell_data.description}",
}}
"""
    return item_def
```

---

## Phase 7: Spell Templates

### 7.1 Pre-built Spell Templates

**Common Spell Patterns**:

| Template | Type | Description | Stats Example |
|----------|------|-------------|---------------|
| **Direct Damage** | Attack | Single-target instant damage | Dmg: 20-25, Mana: 10, CD: 3s |
| **Projectile Attack** | Attack | Ranged projectile spell | Dmg: 30-40, Mana: 15, CD: 4s |
| **AOE Blast** | AOE | Area damage around point | Dmg: 40-50, Mana: 25, Radius: 5m |
| **Direct Heal** | Heal | Single-target instant heal | Heal: 30-40, Mana: 15, CD: 5s |
| **HOT (Heal over Time)** | Heal | Heal over duration | Heal: 10/sec, Mana: 20, Dur: 10s |
| **Buff** | Buff | Increase ally stats | +10 Str, Mana: 15, Dur: 30s |
| **Debuff** | Debuff | Decrease enemy stats | -20% Speed, Mana: 12, Dur: 15s |
| **Summon Creature** | Summon | Spawn allied unit | Summon: Level 5, Mana: 40, Dur: 60s |
| **DOT (Damage over Time)** | Debuff | Damage over duration | Dmg: 5/sec, Mana: 15, Dur: 20s |
| **Chain Lightning** | Attack | Bounces between targets | Dmg: 25-35, Targets: 5, Mana: 30 |

### 7.2 Template Loading System

```python
class SpellTemplate:
    """Pre-configured spell template"""
    
    def __init__(self, name: str, template_type: SpellType):
        self.name = name
        self.template_type = template_type
        self.default_data = {}
    
    @staticmethod
    def load_template(template_name: str) -> SpellCreationData:
        """Load a spell template"""
        
        templates = {
            "Fireball": SpellTemplate.create_fireball_template(),
            "Healing": SpellTemplate.create_healing_template(),
            "Lightning": SpellTemplate.create_lightning_template(),
            "Summon Wolf": SpellTemplate.create_summon_template(),
            # ... more templates
        }
        
        return templates.get(template_name)
    
    @staticmethod
    def create_fireball_template() -> SpellCreationData:
        """Create Fireball template"""
        
        levels = []
        for i in range(1, 16):
            levels.append(SpellLevel(
                level=i,
                damage_min=15 + i * 8,
                damage_max=20 + i * 10,
                mana_cost=10 + i * 2,
                cooldown=3.0 - min(i * 0.05, 1.0),
                cast_time=1.5,
                range=20.0 + i * 0.5,
                aoe_radius=0,
                duration=0
            ))
        
        return SpellCreationData(
            spell_name="Fireball",
            internal_name="Fireball",
            magic_school=MagicSchool.FIRE,
            spell_type=SpellType.ATTACK,
            description="Hurls a ball of fire at the target",
            target_type=TargetType.SINGLE,
            has_projectile=True,
            base_range=20.0,
            aoe_radius=0,
            duration=0,
            special_effects=["burn"],
            num_levels=15,
            levels=levels,
            scaling_mode=ScalingMode.LINEAR,
            vfx_cast="CastFire",
            vfx_projectile="ProjectileFireBall",
            vfx_resolve="ResolveFireBall",
            vfx_target="TargetBurn",
            vfx_overtime="",
            sfx_cast="spell_fire_cast",
            sfx_projectile="",
            sfx_resolve="spell_hit_fireburst",
            sfx_hit="spell_hit_explosion",
            spell_line_id=300,  # Auto-assign
            created_date="",
            author=""
        )
```

---

## Implementation Timeline

### Week 1: Foundation (Phase 1)
- ☐ Create `SpellCreatorWizard` class
- ☐ Implement wizard pages 1-2 (Basics, Mechanics)
- ☐ Build `SpellCreationData` model
- ☐ Add menu integration

### Week 2: Level Progression (Phase 2) **CRITICAL**
- ☐ Implement `LevelProgressionPage` widget
- ☐ Build level preview table
- ☐ Implement scaling formulas (linear, exponential, logarithmic)
- ☐ Create `LevelEditorDialog` for custom editing
- ☐ Test stat scaling calculations

### Week 3: Visual & Sound (Phases 3-4)
- ☐ Build `VisualEffectsPage` widget
- ☐ Create VFX template library
- ☐ Implement `SoundEffectsPage` widget
- ☐ Add sound browser
- ☐ Integrate with extracted audio files

### Week 4: Export System (Phase 5)
- ☐ Build `SpellLuaExporter` class
- ☐ Implement sql_spellline.lua generation
- ☐ Implement VFX script generation
- ☐ Implement sound entry generation
- ☐ Test Lua output

### Week 5: Validation & Templates (Phases 6-7)
- ☐ Build `SpellValidator` class
- ☐ Implement balance calculator
- ☐ Create spell templates (Fireball, Heal, etc.)
- ☐ Add template loading system
- ☐ Test full create → export → test cycle

### Week 6: Polish & Testing
- ☐ VFX preview system (if time permits)
- ☐ Audio preview system
- ☐ Create user documentation
- ☐ Create tutorial video
- ☐ Test with example spells

---

## Technical Requirements

### Dependencies

**Python Packages**:
- PySide6 (Qt GUI) - ✅ Already installed
- dataclasses - ✅ Python stdlib
- typing - ✅ Python stdlib
- math - ✅ Python stdlib
- json - ✅ Python stdlib

**Game Files Access**:
- Read: `script/sql_spellline.lua`
- Read: `object/object_effect_*.lua`
- Read: `script/DrwSound.lua`
- Read: `ExtractedAssets/Audio/` (sound files)
- Write: Custom spell scripts to `script/` and `object/`

### File Structure

```
src/TirganachReloaded/cff_editor/
├── widgets/
│   ├── spell_creator_wizard.py       # NEW: Main wizard
│   ├── level_progression_page.py     # NEW: Level editor (KEY!)
│   ├── visual_effects_page.py        # NEW: VFX builder
│   ├── sound_effects_page.py         # NEW: Sound browser
│   └── spell_validation.py           # NEW: Validator
├── models/
│   ├── spell_creation_data.py        # NEW: Spell data model
│   ├── spell_level.py                # NEW: Level model
│   └── spell_enums.py                # NEW: Enums (schools, types)
├── exporters/
│   ├── spell_lua_exporter.py         # NEW: Lua generation
│   └── spell_stats_exporter.py       # NEW: Stats export
└── templates/
    ├── fireball_spell.json            # NEW: Spell template
    ├── healing_spell.json
    ├── buff_spell.json
    └── summon_spell.json
```

---

## Success Metrics

### Phase 1-2 Success (Wizard + Levels)
- ✅ All 6 wizard pages functional
- ✅ Level progression table shows 1-15 levels
- ✅ Scaling formulas work correctly
- ✅ Can save/load spell data

### Phase 3-4 Success (VFX + Audio)
- ✅ VFX templates selectable
- ✅ Sound browser works
- ✅ Can preview sounds (audio playback)

### Phase 5 Success (Export)
- ✅ Generates syntactically correct Lua
- ✅ All 15 levels export with proper stats
- ✅ VFX and sound references correct

### Final Success Criteria
- ✅ **Non-programmer creates working spell in < 45 minutes**
- ✅ **Spell exports to clean Lua code**
- ✅ **All 15 levels functional in-game**
- ✅ **VFX and sounds play correctly**
- ✅ **Spell balance is reasonable (not overpowered)**

---

## Risks & Mitigations

### Risk 1: Complex Level Scaling
**Issue**: 15-level progression is complex to configure  
**Mitigation**:
- Provide automatic scaling formulas
- Offer templates as starting points
- Show real-time preview table
- Allow per-level manual editing as fallback

### Risk 2: VFX Complexity
**Issue**: Lua VFX scripts are complicated  
**Mitigation**:
- Use template-based approach
- Provide pre-built effect library
- Generate from high-level descriptions
- Don't expose raw Lua unless "Custom" mode

### Risk 3: Spell Balance
**Issue**: User-created spells may be overpowered  
**Mitigation**:
- Provide balance calculator
- Show power rating/warnings
- Compare to official spells
- Suggest stat adjustments

### Risk 4: In-Game Integration
**Issue**: Generated spells may not work properly  
**Mitigation**:
- Validate all data before export
- Test with simple spells first
- Provide detailed error messages
- Include troubleshooting guide

---

## Future Enhancements

### Post-V1 Features

1. **Visual VFX Editor**:
   - Node-based particle system editor
   - Real-time preview with 3D view
   - Export to Lua automatically

2. **Spell Chains**:
   - Create spell combos (cast A → triggers B)
   - Elemental combinations (Fire + Ice = Steam)
   - Conditional effects

3. **AI Balancing**:
   - ML-based balance suggestions
   - Compare to all official spells
   - Auto-adjust stats for fairness

4. **Spell Lore Generator**:
   - AI-generated spell descriptions
   - Flavor text suggestions
   - Multi-language support

5. **Spell Testing Sandbox**:
   - In-tool spell testing (no need to launch game)
   - Damage calculators
   - DPS simulators

---

## Related Documentation

- [Spell System Guide](../../docs/Guides/SpellForce_Spell_System_Guide.md)
- [Spell IDs Reference](../../docs/Guides/SPELL_IDS_REFERENCE.md)
- [Quest Creator Plan](QUEST_CREATION_PLAN.md) (architecture reference)
- [Modding Master Plan](MODDING_PLAN.md)

---

**Document Version**: 1.0  
**Created**: 2025-10-27  
**Author**: SpellSmut Development Team  
**Status**: 🟡 Planning Complete - Ready for Implementation  
**Pun Level**: 🧙‍♂️🧙‍♂️🧙‍♂️ Maximum Wizardry! 🧙‍♀️🧙‍♀️🧙‍♀️
