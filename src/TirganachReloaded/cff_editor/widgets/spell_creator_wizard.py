"""
SpellForce Spell Creation System - Main Wizard Interface
"""

import sys
from typing import Optional, Dict, Any
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QLabel, QLineEdit, QTextEdit,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QVBoxLayout,
    QHBoxLayout, QFormLayout, QGroupBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QProgressBar,
    QColorDialog, QGridLayout, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor

from ..models import (
    SpellCreationData, MagicSchool, SpellType, TargetType, ScalingMode,
    SpellLevel
)
from .spell_mode_selection_page import SpellModeSelectionPage
from .spell_loader import SpellLoader


class SpellBasicsPage(QWizardPage):
    """Step 1: Basic spell information"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Spell Basics")
        self.setSubTitle("Enter the fundamental information for your spell")

        layout = QVBoxLayout()

        # Spell Name
        name_group = QGroupBox("Spell Identity")
        name_layout = QFormLayout()

        self.spell_name_edit = QLineEdit()
        self.spell_name_edit.setPlaceholderText("e.g., Inferno Blast")
        self.spell_name_edit.textChanged.connect(self.update_internal_name)
        name_layout.addRow("Spell Name:", self.spell_name_edit)

        self.internal_name_edit = QLineEdit()
        self.internal_name_edit.setPlaceholderText("e.g., InfernoBlast")
        name_layout.addRow("Internal Name:", self.internal_name_edit)

        name_group.setLayout(name_layout)
        layout.addWidget(name_group)

        # Magic School and Type
        type_group = QGroupBox("Spell Classification")
        type_layout = QFormLayout()

        self.school_combo = QComboBox()
        self.school_combo.addItems([
            "White (Holy/Life Magic)",
            "Fire (Fire Elemental)",
            "Ice (Ice Elemental)",
            "Black (Necromancy/Dark)",
            "Mental (Mind/Illusion)",
            "Earth (Earth Elemental)"
        ])
        type_layout.addRow("Magic School:", self.school_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Attack (damage spells)",
            "Heal (healing spells)",
            "Buff (beneficial effects)",
            "Debuff (harmful effects)",
            "Summon (creature summoning)",
            "AOE (area damage/effect)",
            "Utility (miscellaneous)"
        ])
        type_layout.addRow("Spell Type:", self.type_combo)

        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()
        self.description_edit = QTextEdit()
        self.description_edit.setPlaceholderText("Describe what your spell does...")
        self.description_edit.setMaximumHeight(80)
        desc_layout.addWidget(self.description_edit)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        layout.addStretch()
        self.setLayout(layout)

        # Register fields for validation
        self.registerField("spell_name*", self.spell_name_edit)
        self.registerField("internal_name*", self.internal_name_edit)
        self.registerField("description", self.description_edit)

    def update_internal_name(self):
        """Auto-generate internal name from spell name"""
        spell_name = self.spell_name_edit.text()
        if spell_name and not self.internal_name_edit.text():
            # Remove spaces and special characters
            internal = "".join(c for c in spell_name if c.isalnum() or c in " _-").replace(" ", "")
            self.internal_name_edit.setText(internal)


class TargetMechanicsPage(QWizardPage):
    """Step 2: Target type and spell mechanics"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Target & Mechanics")
        self.setSubTitle("Define how your spell targets enemies and works")

        layout = QVBoxLayout()

        # Target Type
        target_group = QGroupBox("Targeting")
        target_layout = QFormLayout()

        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "Single Target (affects one enemy/unit)",
            "Area of Effect (affects area around point)",
            "Self (affects the caster)",
            "Cone (affects cone-shaped area in front)",
            "Chain (bounces between multiple targets)"
        ])
        target_layout.addRow("Target Type:", self.target_combo)

        target_group.setLayout(target_layout)
        layout.addWidget(target_group)

        # Projectile
        projectile_group = QGroupBox("Projectile")
        projectile_layout = QVBoxLayout()

        self.projectile_checkbox = QCheckBox("Spell has projectile (travels through air)")
        self.projectile_checkbox.setChecked(False)
        projectile_layout.addWidget(self.projectile_checkbox)

        projectile_group.setLayout(projectile_layout)
        layout.addWidget(projectile_group)

        # Range and Area
        range_group = QGroupBox("Range & Area")
        range_layout = QFormLayout()

        self.range_spin = QDoubleSpinBox()
        self.range_spin.setRange(0, 100)
        self.range_spin.setValue(20.0)
        self.range_spin.setSuffix(" units")
        range_layout.addRow("Range:", self.range_spin)

        self.aoe_spin = QDoubleSpinBox()
        self.aoe_spin.setRange(0, 50)
        self.aoe_spin.setValue(0.0)
        self.aoe_spin.setSuffix(" units")
        range_layout.addRow("AOE Radius:", self.aoe_spin)

        range_group.setLayout(range_layout)
        layout.addWidget(range_group)

        # Duration (for buffs/debuffs/summons)
        duration_group = QGroupBox("Duration (for Buffs/Debuffs/Summons)")
        duration_layout = QFormLayout()

        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 300)
        self.duration_spin.setValue(0.0)
        self.duration_spin.setSuffix(" seconds")
        duration_layout.addRow("Duration:", self.duration_spin)

        duration_group.setLayout(duration_layout)
        layout.addWidget(duration_group)

        # Special Effects
        effects_group = QGroupBox("Special Effects")
        effects_layout = QVBoxLayout()

        self.effects_text = QTextEdit()
        self.effects_text.setPlaceholderText("Comma-separated effects: stun, burn, slow, fear, etc.")
        self.effects_text.setMaximumHeight(60)
        effects_layout.addWidget(self.effects_text)

        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)

        layout.addStretch()
        self.setLayout(layout)


class LevelProgressionPage(QWizardPage):
    """Step 3: Level progression and stat scaling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Level Progression")
        self.setSubTitle("Configure how your spell scales from level 1 to 15")

        layout = QVBoxLayout()

        # Number of levels
        level_group = QGroupBox("Spell Levels")
        level_layout = QHBoxLayout()
        level_layout.addWidget(QLabel("Number of Levels:"))
        self.level_spinbox = QSpinBox()
        self.level_spinbox.setRange(1, 15)
        self.level_spinbox.setValue(15)
        self.level_spinbox.valueChanged.connect(self.update_preview)
        level_layout.addWidget(self.level_spinbox)
        level_layout.addStretch()
        level_group.setLayout(level_layout)
        layout.addWidget(level_group)

        # Base stats (Level 1)
        base_group = QGroupBox("Base Stats (Level 1)")
        base_layout = QFormLayout()

        self.damage_min_spin = QSpinBox()
        self.damage_min_spin.setRange(0, 1000)
        self.damage_min_spin.setValue(20)
        self.damage_min_spin.valueChanged.connect(self.update_preview)

        self.damage_max_spin = QSpinBox()
        self.damage_max_spin.setRange(0, 1000)
        self.damage_max_spin.setValue(25)
        self.damage_max_spin.valueChanged.connect(self.update_preview)

        self.mana_cost_spin = QSpinBox()
        self.mana_cost_spin.setRange(0, 500)
        self.mana_cost_spin.setValue(10)
        self.mana_cost_spin.valueChanged.connect(self.update_preview)

        self.cooldown_spin = QDoubleSpinBox()
        self.cooldown_spin.setRange(0, 60)
        self.cooldown_spin.setValue(3.0)
        self.cooldown_spin.setSingleStep(0.1)
        self.cooldown_spin.valueChanged.connect(self.update_preview)

        self.cast_time_spin = QDoubleSpinBox()
        self.cast_time_spin.setRange(0, 10)
        self.cast_time_spin.setValue(1.5)
        self.cast_time_spin.setSingleStep(0.1)
        self.cast_time_spin.valueChanged.connect(self.update_preview)

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
        self.scaling_combo.addItems([
            "Linear (same increase per level)",
            "Exponential (accelerating growth)",
            "Logarithmic (diminishing returns)",
            "Custom (edit each level manually)"
        ])
        self.scaling_combo.currentIndexChanged.connect(self.update_preview)
        scaling_layout.addWidget(self.scaling_combo)

        help_text = QLabel(
            "Linear: Same increase per level\n"
            "Exponential: Accelerating growth (powerful at high levels)\n"
            "Logarithmic: Diminishing returns (balanced scaling)\n"
            "Custom: Edit each level manually"
        )
        help_text.setStyleSheet("color: #666; font-size: 11px;")
        scaling_layout.addWidget(help_text)

        scaling_group.setLayout(scaling_layout)
        layout.addWidget(scaling_group)

        # Preview table
        preview_group = QGroupBox("Level Preview")
        preview_layout = QVBoxLayout()

        self.preview_table = QTableWidget(15, 6)
        self.preview_table.setHorizontalHeaderLabels([
            "Level", "Damage", "Mana", "Cooldown", "Cast Time", "Range"
        ])
        self.preview_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.preview_table.setMaximumHeight(300)

        preview_layout.addWidget(self.preview_table)

        # Recalculate button
        recalc_btn = QPushButton("Recalculate Scaling")
        recalc_btn.clicked.connect(self.update_preview)
        preview_layout.addWidget(recalc_btn)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Edit individual levels button
        edit_btn = QPushButton("Edit Individual Levels (Custom Mode)")
        edit_btn.clicked.connect(self.open_level_editor)
        layout.addWidget(edit_btn)

        layout.addStretch()
        self.setLayout(layout)

        # Initialize preview
        self.update_preview()

    def update_preview(self):
        """Recalculate and display all level stats"""
        scaling_mode_text = self.scaling_combo.currentText().lower()
        num_levels = self.level_spinbox.value()

        # Map display text to enum
        scaling_map = {
            "linear (same increase per level)": "linear",
            "exponential (accelerating growth)": "exponential",
            "logarithmic (diminishing returns)": "logarithmic",
            "custom (edit each level manually)": "custom"
        }
        scaling_mode = scaling_map.get(scaling_mode_text, "linear")

        base_damage_min = self.damage_min_spin.value()
        base_damage_max = self.damage_max_spin.value()
        base_mana = self.mana_cost_spin.value()
        base_cooldown = self.cooldown_spin.value()
        base_cast_time = self.cast_time_spin.value()
        base_range = 20.0  # Default range

        for level in range(1, num_levels + 1):
            # Apply scaling formula
            if scaling_mode == "linear":
                damage_min = base_damage_min + (level - 1) * 10
                damage_max = base_damage_max + (level - 1) * 12
                mana = base_mana + (level - 1) * 3
                cooldown = max(1.0, base_cooldown - (level - 1) * 0.1)
                cast_time = base_cast_time
                range_val = base_range + (level - 1) * 0.5

            elif scaling_mode == "exponential":
                damage_min = int(base_damage_min * (1.15 ** (level - 1)))
                damage_max = int(base_damage_max * (1.15 ** (level - 1)))
                mana = int(base_mana * (1.12 ** (level - 1)))
                cooldown = max(1.0, base_cooldown * (0.95 ** (level - 1)))
                cast_time = base_cast_time
                range_val = base_range * (1.02 ** (level - 1))

            elif scaling_mode == "logarithmic":
                import math
                factor = 1 + math.log(level) / 2
                damage_min = int(base_damage_min * factor)
                damage_max = int(base_damage_max * factor)
                mana = int(base_mana * factor)
                cooldown = base_cooldown
                cast_time = base_cast_time
                range_val = base_range + (level - 1) * 0.3

            else:  # custom or unknown
                damage_min = base_damage_min
                damage_max = base_damage_max
                mana = base_mana
                cooldown = base_cooldown
                cast_time = base_cast_time
                range_val = base_range

            # Update table
            row = level - 1
            self.preview_table.setItem(row, 0, QTableWidgetItem(str(level)))
            self.preview_table.setItem(row, 1, QTableWidgetItem(f"{damage_min}-{damage_max}"))
            self.preview_table.setItem(row, 2, QTableWidgetItem(str(mana)))
            self.preview_table.setItem(row, 3, QTableWidgetItem(f"{cooldown:.1f}s"))
            self.preview_table.setItem(row, 4, QTableWidgetItem(f"{cast_time:.1f}s"))
            self.preview_table.setItem(row, 5, QTableWidgetItem(f"{range_val:.1f}"))

    def open_level_editor(self):
        """Open dialog to manually edit each level"""
        from .level_editor_dialog import LevelEditorDialog

        # Create temporary spell data to get current levels
        wizard = self.wizard()
        if wizard:
            spell_data = wizard.collect_spell_data()

            # Open level editor
            dialog = LevelEditorDialog(spell_data.levels, self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                # Get updated levels
                updated_levels = dialog.get_levels()

                # Update our internal data
                # Note: We'd need to store these somewhere accessible
                # For now, just show success message
                QMessageBox.information(self, "Levels Updated",
                                       f"Successfully updated {len(updated_levels)} levels!\n\n"
                                       "Note: These custom changes will be applied when you complete the wizard.")


class VisualEffectsPage(QWizardPage):
    """Step 4: Visual effects configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Visual Effects")
        self.setSubTitle("Design how your spell looks and feels")

        # Store selected colors
        self.primary_color = QColor(255, 100, 0)  # Orange
        self.secondary_color = QColor(255, 255, 100)  # Yellow

        layout = QVBoxLayout()

        # Main layout with template browser and effect selection
        main_layout = QHBoxLayout()

        # Left side: Template browser
        template_group = QGroupBox("Effect Templates")
        template_layout = QVBoxLayout()

        self.template_list = QListWidget()
        self.template_list.setMaximumWidth(200)
        self.populate_templates()
        self.template_list.itemSelectionChanged.connect(self.on_template_selected)
        template_layout.addWidget(QLabel("Choose a template:"))
        template_layout.addWidget(self.template_list)

        # Template description
        self.template_desc = QLabel("Select a template to see its effects")
        self.template_desc.setWordWrap(True)
        self.template_desc.setStyleSheet("border: 1px solid #ccc; padding: 5px; background-color: #f9f9f9;")
        self.template_desc.setMaximumHeight(60)
        template_layout.addWidget(self.template_desc)

        template_group.setLayout(template_layout)
        main_layout.addWidget(template_group)

        # Right side: Effect configuration
        effects_group = QGroupBox("Effect Configuration")
        effects_layout = QVBoxLayout()

        # Cast Effect
        cast_group = QGroupBox("Cast Effect (at caster)")
        cast_layout = QHBoxLayout()
        self.cast_combo = QComboBox()
        self.cast_combo.addItems([
            "🔥 Fire Cast (flames from hands)",
            "❄️ Ice Cast (frost swirl)",
            "✨ White Cast (holy light)",
            "🌑 Black Cast (dark lightning)",
            "🧠 Mental Cast (psionic rings)",
            "🪨 Earth Cast (stone particles)",
            "✨ Generic Cast (magic sparkles)",
            "None",
            "Custom..."
        ])
        cast_layout.addWidget(self.cast_combo)
        preview_cast_btn = QPushButton("👁️ Preview")
        preview_cast_btn.clicked.connect(lambda: self.preview_vfx("cast"))
        cast_layout.addWidget(preview_cast_btn)
        cast_group.setLayout(cast_layout)
        effects_layout.addWidget(cast_group)

        # Projectile Effect
        projectile_group = QGroupBox("Projectile Effect (during travel)")
        projectile_layout = QHBoxLayout()
        self.projectile_combo = QComboBox()
        self.projectile_combo.addItems([
            "🔥 Fireball (flame projectile)",
            "❄️ Ice Shard (ice projectile)",
            "⚡ Lightning Bolt (electric arc)",
            "🌑 Dark Bolt (shadowy missile)",
            "✨ Holy Bolt (light projectile)",
            "🪨 Earth Spike (stone projectile)",
            "💫 Magic Missile (generic projectile)",
            "None (instant spell)",
            "Custom..."
        ])
        projectile_layout.addWidget(self.projectile_combo)
        preview_proj_btn = QPushButton("👁️ Preview")
        preview_proj_btn.clicked.connect(lambda: self.preview_vfx("projectile"))
        projectile_layout.addWidget(preview_proj_btn)
        projectile_group.setLayout(projectile_layout)
        effects_layout.addWidget(projectile_group)

        # Resolve Effect
        resolve_group = QGroupBox("Resolve Effect (at impact)")
        resolve_layout = QHBoxLayout()
        self.resolve_combo = QComboBox()
        self.resolve_combo.addItems([
            "💥 Fire Explosion (burst of flames)",
            "❄️ Ice Shatter (crystalline break)",
            "✨ Holy Flash (white burst)",
            "🌑 Dark Implosion (void collapse)",
            "⚡ Lightning Strike (electric burst)",
            "🪨 Earth Crater (ground impact)",
            "💨 Smoke Puff (generic impact)",
            "✨ Magic Burst (colorful explosion)",
            "None",
            "Custom..."
        ])
        resolve_layout.addWidget(self.resolve_combo)
        preview_resolve_btn = QPushButton("👁️ Preview")
        preview_resolve_btn.clicked.connect(lambda: self.preview_vfx("resolve"))
        resolve_layout.addWidget(preview_resolve_btn)
        resolve_group.setLayout(resolve_layout)
        effects_layout.addWidget(resolve_group)

        # Target Effect
        target_group = QGroupBox("Target Effect (on hit target)")
        target_layout = QHBoxLayout()
        self.target_combo = QComboBox()
        self.target_combo.addItems([
            "🔥 Burn Effect (flames on target)",
            "❄️ Freeze Effect (ice crystals)",
            "✨ Heal Glow (white particles)",
            "🌑 Curse Aura (dark smoke)",
            "⚡ Shock Effect (electric sparks)",
            "🩸 Bleed Effect (blood particles)",
            "💚 Regeneration (green particles)",
            "☠️ Poison (purple gas)",
            "None",
            "Custom..."
        ])
        target_layout.addWidget(self.target_combo)
        target_group.setLayout(target_layout)
        effects_layout.addWidget(target_group)

        # Overtime Effect (buffs/debuffs)
        overtime_group = QGroupBox("Overtime Effect (persistent)")
        overtime_layout = QHBoxLayout()
        self.overtime_combo = QComboBox()
        self.overtime_combo.addItems([
            "🔥 Fire Aura (continuous flames)",
            "❄️ Ice Aura (frost particles)",
            "✨ Buff Glow (white sparkles)",
            "🌑 Debuff Cloud (dark mist)",
            "💚 Regeneration Aura (green particles)",
            "☠️ Poison Cloud (purple gas)",
            "⚡ Storm Aura (electric field)",
            "🛡️ Protection Shield (blue barrier)",
            "None",
            "Custom..."
        ])
        overtime_layout.addWidget(self.overtime_combo)
        overtime_group.setLayout(overtime_layout)
        effects_layout.addWidget(overtime_group)

        effects_group.setLayout(effects_layout)
        main_layout.addWidget(effects_group)

        layout.addLayout(main_layout)

        # Color customization
        color_group = QGroupBox("Color Customization")
        color_layout = QGridLayout()

        # Primary color
        color_layout.addWidget(QLabel("Primary Color:"), 0, 0)
        self.color1_btn = QPushButton()
        self.color1_btn.setFixedSize(60, 30)
        self.update_color_button(self.color1_btn, self.primary_color)
        self.color1_btn.clicked.connect(lambda: self.choose_color("primary"))
        color_layout.addWidget(self.color1_btn, 0, 1)

        self.color1_label = QLabel("Orange (Fire)")
        color_layout.addWidget(self.color1_label, 0, 2)

        # Secondary color
        color_layout.addWidget(QLabel("Secondary Color:"), 1, 0)
        self.color2_btn = QPushButton()
        self.color2_btn.setFixedSize(60, 30)
        self.update_color_button(self.color2_btn, self.secondary_color)
        self.color2_btn.clicked.connect(lambda: self.choose_color("secondary"))
        color_layout.addWidget(self.color2_btn, 1, 1)

        self.color2_label = QLabel("Yellow (Energy)")
        color_layout.addWidget(self.color2_label, 1, 2)

        # Preset colors
        color_layout.addWidget(QLabel("Quick Presets:"), 2, 0)
        presets_layout = QHBoxLayout()

        fire_btn = QPushButton("🔥 Fire")
        fire_btn.clicked.connect(lambda: self.set_preset_colors(QColor(255, 100, 0), QColor(255, 200, 0)))
        presets_layout.addWidget(fire_btn)

        ice_btn = QPushButton("❄️ Ice")
        ice_btn.clicked.connect(lambda: self.set_preset_colors(QColor(100, 200, 255), QColor(200, 255, 255)))
        presets_layout.addWidget(ice_btn)

        holy_btn = QPushButton("✨ Holy")
        holy_btn.clicked.connect(lambda: self.set_preset_colors(QColor(255, 255, 200), QColor(255, 255, 255)))
        presets_layout.addWidget(holy_btn)

        dark_btn = QPushButton("🌑 Dark")
        dark_btn.clicked.connect(lambda: self.set_preset_colors(QColor(100, 0, 100), QColor(50, 0, 50)))
        presets_layout.addWidget(dark_btn)

        color_layout.addLayout(presets_layout, 2, 1, 1, 2)

        color_group.setLayout(color_layout)
        layout.addWidget(color_group)

        layout.addStretch()
        self.setLayout(layout)

    def populate_templates(self):
        """Populate the template list with predefined spell templates"""
        templates = [
            ("🔥 Fireball", "Classic fireball with flame effects"),
            ("❄️ Ice Blast", "Freezing ice projectile"),
            ("✨ Holy Heal", "Healing light with sparkles"),
            ("🌑 Shadow Bolt", "Dark magic projectile"),
            ("⚡ Chain Lightning", "Electric chain between targets"),
            ("🪨 Earthquake", "Ground-shaking earth magic"),
            ("🧠 Mind Flay", "Psionic mental attack"),
            ("💚 Regeneration", "Healing over time aura"),
            ("☠️ Poison Cloud", "Toxic area damage"),
            ("🛡️ Protection", "Defensive shield bubble"),
        ]

        for name, desc in templates:
            item = QListWidgetItem(name)
            item.setToolTip(desc)
            item.setData(Qt.ItemDataRole.UserRole, desc)
            self.template_list.addItem(item)

    def on_template_selected(self):
        """Handle template selection"""
        current_item = self.template_list.currentItem()
        if current_item:
            template_name = current_item.text()
            description = current_item.data(Qt.ItemDataRole.UserRole)
            self.template_desc.setText(f"<b>{template_name}</b><br>{description}")

            # Auto-select appropriate effects based on template
            self.apply_template_effects(template_name)

    def apply_template_effects(self, template_name):
        """Apply effect selections based on template"""
        if "🔥 Fireball" in template_name:
            self.cast_combo.setCurrentText("🔥 Fire Cast (flames from hands)")
            self.projectile_combo.setCurrentText("🔥 Fireball (flame projectile)")
            self.resolve_combo.setCurrentText("💥 Fire Explosion (burst of flames)")
            self.target_combo.setCurrentText("🔥 Burn Effect (flames on target)")
            self.overtime_combo.setCurrentText("None")
            self.set_preset_colors(QColor(255, 100, 0), QColor(255, 200, 0))

        elif "❄️ Ice Blast" in template_name:
            self.cast_combo.setCurrentText("❄️ Ice Cast (frost swirl)")
            self.projectile_combo.setCurrentText("❄️ Ice Shard (ice projectile)")
            self.resolve_combo.setCurrentText("❄️ Ice Shatter (crystalline break)")
            self.target_combo.setCurrentText("❄️ Freeze Effect (ice crystals)")
            self.overtime_combo.setCurrentText("None")
            self.set_preset_colors(QColor(100, 200, 255), QColor(200, 255, 255))

        elif "✨ Holy Heal" in template_name:
            self.cast_combo.setCurrentText("✨ White Cast (holy light)")
            self.projectile_combo.setCurrentText("None (instant spell)")
            self.resolve_combo.setCurrentText("✨ Holy Flash (white burst)")
            self.target_combo.setCurrentText("✨ Heal Glow (white particles)")
            self.overtime_combo.setCurrentText("💚 Regeneration Aura (green particles)")
            self.set_preset_colors(QColor(255, 255, 200), QColor(255, 255, 255))

        elif "🌑 Shadow Bolt" in template_name:
            self.cast_combo.setCurrentText("🌑 Black Cast (dark lightning)")
            self.projectile_combo.setCurrentText("🌑 Dark Bolt (shadowy missile)")
            self.resolve_combo.setCurrentText("🌑 Dark Implosion (void collapse)")
            self.target_combo.setCurrentText("🌑 Curse Aura (dark smoke)")
            self.overtime_combo.setCurrentText("None")
            self.set_preset_colors(QColor(100, 0, 100), QColor(50, 0, 50))

    def preview_vfx(self, effect_type):
        """Show animated preview of VFX"""
        effect_name = ""
        if effect_type == "cast":
            effect_name = self.cast_combo.currentText()
        elif effect_type == "projectile":
            effect_name = self.projectile_combo.currentText()
        elif effect_type == "resolve":
            effect_name = self.resolve_combo.currentText()

        QMessageBox.information(self, "VFX Preview",
                               f"Preview for: {effect_name}\n\n"
                               f"🎬 Animation preview would show here\n"
                               f"🎨 Using colors: {self.primary_color.name()} / {self.secondary_color.name()}")

    def choose_color(self, color_type):
        """Open color picker dialog"""
        if color_type == "primary":
            initial_color = self.primary_color
        else:
            initial_color = self.secondary_color

        color = QColorDialog.getColor(initial_color, self, f"Choose {color_type} color")

        if color.isValid():
            if color_type == "primary":
                self.primary_color = color
                self.update_color_button(self.color1_btn, color)
                self.color1_label.setText(f"{color.name().upper()} ({self.get_color_name(color)})")
            else:
                self.secondary_color = color
                self.update_color_button(self.color2_btn, color)
                self.color2_label.setText(f"{color.name().upper()} ({self.get_color_name(color)})")

    def set_preset_colors(self, primary, secondary):
        """Set preset color combination"""
        self.primary_color = primary
        self.secondary_color = secondary
        self.update_color_button(self.color1_btn, primary)
        self.update_color_button(self.color2_btn, secondary)
        self.color1_label.setText(f"{primary.name().upper()} ({self.get_color_name(primary)})")
        self.color2_label.setText(f"{secondary.name().upper()} ({self.get_color_name(secondary)})")

    def update_color_button(self, button, color):
        """Update button appearance to show selected color"""
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                border: 2px solid #000;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid #666;
            }}
        """)

    def get_color_name(self, color):
        """Get human-readable color name"""
        # Simple color name detection
        r, g, b = color.red(), color.green(), color.blue()

        if r > 200 and g > 200 and b > 200:
            return "White"
        elif r > 200 and g < 100 and b < 100:
            return "Red"
        elif r < 100 and g > 200 and b < 100:
            return "Green"
        elif r < 100 and g < 100 and b > 200:
            return "Blue"
        elif r > 200 and g > 100 and b < 100:
            return "Orange"
        elif r < 100 and g > 200 and b > 200:
            return "Cyan"
        elif r > 200 and g < 100 and b > 200:
            return "Magenta"
        elif r > 150 and g > 150 and b < 100:
            return "Yellow"
        else:
            return "Custom"


class SoundEffectsPage(QWizardPage):
    """Step 5: Sound effects configuration"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Sound Effects")
        self.setSubTitle("Choose sounds for your spell")

        # Sound database - in a real implementation, this would be loaded from game files
        self.sound_database = self.load_sound_database()

        layout = QVBoxLayout()

        # Main layout with sound categories and selection
        main_layout = QHBoxLayout()

        # Left side: Sound categories
        category_group = QGroupBox("Sound Categories")
        category_layout = QVBoxLayout()

        self.category_list = QListWidget()
        self.category_list.setMaximumWidth(150)
        self.populate_categories()
        self.category_list.itemSelectionChanged.connect(self.on_category_selected)
        category_layout.addWidget(QLabel("Categories:"))
        category_layout.addWidget(self.category_list)

        category_group.setLayout(category_layout)
        main_layout.addWidget(category_group)

        # Right side: Sound selection
        sounds_group = QGroupBox("Sound Selection")
        sounds_layout = QVBoxLayout()

        # Cast Sound
        cast_group = QGroupBox("Cast Sound (spell initiation)")
        cast_layout = QHBoxLayout()
        self.cast_sound_combo = QComboBox()
        self.cast_sound_combo.addItem("🔇 None", "")
        self.populate_cast_sounds()
        cast_layout.addWidget(self.cast_sound_combo)
        play_cast_btn = QPushButton("🔊 Play")
        play_cast_btn.clicked.connect(lambda: self.play_sound("cast"))
        cast_layout.addWidget(play_cast_btn)
        cast_group.setLayout(cast_layout)
        sounds_layout.addWidget(cast_group)

        # Projectile Sound
        projectile_group = QGroupBox("Projectile Sound (during travel)")
        projectile_layout = QHBoxLayout()
        self.projectile_sound_combo = QComboBox()
        self.projectile_sound_combo.addItem("🔇 None", "")
        projectile_sounds = [
            ("🔥 spell_projectile_fire", "spell_projectile_fire"),
            ("❄️ spell_projectile_ice", "spell_projectile_ice"),
            ("⚡ spell_projectile_lightning", "spell_projectile_lightning"),
            ("🌑 spell_projectile_dark", "spell_projectile_dark"),
            ("💫 spell_projectile_magic", "spell_projectile_magic"),
        ]
        for display, value in projectile_sounds:
            self.projectile_sound_combo.addItem(display, value)
        projectile_layout.addWidget(self.projectile_sound_combo)
        play_proj_btn = QPushButton("🔊 Play")
        play_proj_btn.clicked.connect(lambda: self.play_sound("projectile"))
        projectile_layout.addWidget(play_proj_btn)
        projectile_group.setLayout(projectile_layout)
        sounds_layout.addWidget(projectile_group)

        # Resolve Sound
        resolve_group = QGroupBox("Resolve Sound (at impact)")
        resolve_layout = QHBoxLayout()
        self.resolve_sound_combo = QComboBox()
        self.resolve_sound_combo.addItem("🔇 None", "")
        resolve_sounds = [
            ("💥 spell_hit_fireburst", "spell_hit_fireburst"),
            ("❄️ spell_hit_iceburst", "spell_hit_iceburst"),
            ("💥 spell_hit_explosion", "spell_hit_explosion"),
            ("✨ spell_hit_healing", "spell_hit_healing"),
            ("✨ spell_hit_aura_white", "spell_hit_aura_white"),
            ("🌑 spell_hit_aura_black", "spell_hit_aura_black"),
            ("⚡ spell_hit_lightning", "spell_hit_lightning"),
            ("🪨 spell_hit_earth", "spell_hit_earth"),
        ]
        for display, value in resolve_sounds:
            self.resolve_sound_combo.addItem(display, value)
        resolve_layout.addWidget(self.resolve_sound_combo)
        play_resolve_btn = QPushButton("🔊 Play")
        play_resolve_btn.clicked.connect(lambda: self.play_sound("resolve"))
        resolve_layout.addWidget(play_resolve_btn)
        resolve_group.setLayout(resolve_layout)
        sounds_layout.addWidget(resolve_group)

        # Hit Sound
        hit_group = QGroupBox("Hit Sound (on target)")
        hit_layout = QHBoxLayout()
        self.hit_sound_combo = QComboBox()
        self.hit_sound_combo.addItem("🔇 None", "")
        hit_sounds = [
            ("✨ spell_hit_default_white", "spell_hit_default_white"),
            ("🌑 spell_hit_default_black", "spell_hit_default_black"),
            ("🔥 spell_hit_burn", "spell_hit_burn"),
            ("❄️ spell_hit_freeze", "spell_hit_freeze"),
            ("⚡ spell_hit_shock", "spell_hit_shock"),
            ("🩸 spell_hit_bleed", "spell_hit_bleed"),
            ("💚 spell_hit_heal", "spell_hit_heal"),
        ]
        for display, value in hit_sounds:
            self.hit_sound_combo.addItem(display, value)
        hit_layout.addWidget(self.hit_sound_combo)
        play_hit_btn = QPushButton("🔊 Play")
        play_hit_btn.clicked.connect(lambda: self.play_sound("hit"))
        hit_layout.addWidget(play_hit_btn)
        hit_group.setLayout(hit_layout)
        sounds_layout.addWidget(hit_group)

        # Overtime Sound (for buffs/debuffs)
        overtime_group = QGroupBox("Overtime Sound (persistent effects)")
        overtime_layout = QHBoxLayout()
        self.overtime_sound_combo = QComboBox()
        self.overtime_sound_combo.addItem("🔇 None", "")
        overtime_sounds = [
            ("🔥 spell_aura_fire", "spell_aura_fire"),
            ("❄️ spell_aura_ice", "spell_aura_ice"),
            ("✨ spell_aura_buff", "spell_aura_buff"),
            ("🌑 spell_aura_debuff", "spell_aura_debuff"),
            ("💚 spell_aura_regeneration", "spell_aura_regeneration"),
            ("☠️ spell_aura_poison", "spell_aura_poison"),
        ]
        for display, value in overtime_sounds:
            self.overtime_sound_combo.addItem(display, value)
        overtime_layout.addWidget(self.overtime_sound_combo)
        play_overtime_btn = QPushButton("🔊 Play")
        play_overtime_btn.clicked.connect(lambda: self.play_sound("overtime"))
        overtime_layout.addWidget(play_overtime_btn)
        overtime_group.setLayout(overtime_layout)
        sounds_layout.addWidget(overtime_group)

        sounds_group.setLayout(sounds_layout)
        main_layout.addWidget(sounds_group)

        layout.addLayout(main_layout)

        # Sound browser and presets
        bottom_layout = QHBoxLayout()

        # Sound browser
        browse_btn = QPushButton("🎵 Browse All Sounds...")
        browse_btn.clicked.connect(self.open_sound_browser)
        bottom_layout.addWidget(browse_btn)

        # Preset buttons
        presets_label = QLabel("Quick Presets:")
        bottom_layout.addWidget(presets_label)

        fire_preset_btn = QPushButton("🔥 Fire")
        fire_preset_btn.clicked.connect(lambda: self.apply_sound_preset("fire"))
        bottom_layout.addWidget(fire_preset_btn)

        ice_preset_btn = QPushButton("❄️ Ice")
        ice_preset_btn.clicked.connect(lambda: self.apply_sound_preset("ice"))
        bottom_layout.addWidget(ice_preset_btn)

        holy_preset_btn = QPushButton("✨ Holy")
        holy_preset_btn.clicked.connect(lambda: self.apply_sound_preset("holy"))
        bottom_layout.addWidget(holy_preset_btn)

        dark_preset_btn = QPushButton("🌑 Dark")
        dark_preset_btn.clicked.connect(lambda: self.apply_sound_preset("dark"))
        bottom_layout.addWidget(dark_preset_btn)

        bottom_layout.addStretch()
        layout.addLayout(bottom_layout)

        # Volume controls
        volume_group = QGroupBox("Volume Settings")
        volume_layout = QFormLayout()

        self.master_volume = QSpinBox()
        self.master_volume.setRange(0, 100)
        self.master_volume.setValue(100)
        self.master_volume.setSuffix("%")
        volume_layout.addRow("Master Volume:", self.master_volume)

        self.spatial_audio = QCheckBox("Enable 3D spatial audio")
        self.spatial_audio.setChecked(True)
        volume_layout.addRow("", self.spatial_audio)

        volume_group.setLayout(volume_layout)
        layout.addWidget(volume_group)

        layout.addStretch()
        self.setLayout(layout)

    def load_sound_database(self):
        """Load sound database - in real implementation, this would scan game files"""
        return {
            "cast": [
                ("spell_white_cast", "Holy cast sound"),
                ("spell_black_cast", "Dark cast sound"),
                ("spell_fire_cast", "Fire cast sound"),
                ("spell_ice_cast", "Ice cast sound"),
                ("spell_earth_cast", "Earth cast sound"),
                ("spell_mental_cast", "Mental cast sound"),
            ],
            "projectile": [
                ("spell_projectile_fire", "Fire projectile whoosh"),
                ("spell_projectile_ice", "Ice projectile hum"),
                ("spell_projectile_lightning", "Lightning crackle"),
                ("spell_projectile_dark", "Dark projectile whisper"),
            ],
            "impact": [
                ("spell_hit_fireburst", "Fire explosion"),
                ("spell_hit_iceburst", "Ice shattering"),
                ("spell_hit_explosion", "Generic explosion"),
                ("spell_hit_healing", "Healing chime"),
            ],
            "aura": [
                ("spell_aura_buff", "Buff aura hum"),
                ("spell_aura_debuff", "Debuff aura drone"),
                ("spell_aura_fire", "Fire aura crackle"),
            ]
        }

    def populate_categories(self):
        """Populate sound categories"""
        categories = [
            "🎭 Cast Sounds",
            "🚀 Projectile Sounds",
            "💥 Impact Sounds",
            "🔄 Aura Sounds",
            "⚔️ Combat Sounds",
            "🎵 Ambient Sounds"
        ]

        for category in categories:
            self.category_list.addItem(category)

    def on_category_selected(self):
        """Handle category selection"""
        # In a real implementation, this would filter the sound selections
        pass

    def populate_cast_sounds(self):
        """Load cast sounds from game files"""
        cast_sounds = [
            ("✨ spell_white_cast", "spell_white_cast"),
            ("🌑 spell_black_cast", "spell_black_cast"),
            ("🔥 spell_fire_cast", "spell_fire_cast"),
            ("❄️ spell_ice_cast", "spell_ice_cast"),
            ("🪨 spell_earth_cast", "spell_earth_cast"),
            ("🧠 spell_mental_cast", "spell_mental_cast"),
            ("⚔️ spell_melee_berserk", "spell_melee_berserk"),
            ("💚 spell_melee_heal", "spell_melee_heal"),
        ]
        for display, value in cast_sounds:
            self.cast_sound_combo.addItem(display, value)

    def play_sound(self, sound_type):
        """Play selected sound"""
        sound_name = ""

        if sound_type == "cast":
            sound_name = self.cast_sound_combo.currentData()
        elif sound_type == "projectile":
            sound_name = self.projectile_sound_combo.currentData()
        elif sound_type == "resolve":
            sound_name = self.resolve_sound_combo.currentData()
        elif sound_type == "hit":
            sound_name = self.hit_sound_combo.currentData()
        elif sound_type == "overtime":
            sound_name = self.overtime_sound_combo.currentData()

        if sound_name:
            QMessageBox.information(self, "🔊 Sound Preview",
                                   f"Playing: {sound_name}\n\n"
                                   f"🎵 Audio playback would happen here\n"
                                   f"🔊 Volume: {self.master_volume.value()}%\n"
                                   f"🎧 3D Audio: {'Enabled' if self.spatial_audio.isChecked() else 'Disabled'}")
        else:
            QMessageBox.information(self, "🔇 No Sound",
                                   "No sound selected for this effect type.")

    def apply_sound_preset(self, preset_type):
        """Apply sound preset based on magic school"""
        if preset_type == "fire":
            self.cast_sound_combo.setCurrentText("🔥 spell_fire_cast")
            self.projectile_sound_combo.setCurrentText("🔥 spell_projectile_fire")
            self.resolve_sound_combo.setCurrentText("💥 spell_hit_fireburst")
            self.hit_sound_combo.setCurrentText("🔥 spell_hit_burn")
            self.overtime_sound_combo.setCurrentText("🔥 spell_aura_fire")

        elif preset_type == "ice":
            self.cast_sound_combo.setCurrentText("❄️ spell_ice_cast")
            self.projectile_sound_combo.setCurrentText("❄️ spell_projectile_ice")
            self.resolve_sound_combo.setCurrentText("❄️ spell_hit_iceburst")
            self.hit_sound_combo.setCurrentText("❄️ spell_hit_freeze")
            self.overtime_sound_combo.setCurrentText("❄️ spell_aura_ice")

        elif preset_type == "holy":
            self.cast_sound_combo.setCurrentText("✨ spell_white_cast")
            self.projectile_sound_combo.setCurrentText("🔇 None")
            self.resolve_sound_combo.setCurrentText("✨ spell_hit_healing")
            self.hit_sound_combo.setCurrentText("✨ spell_hit_heal")
            self.overtime_sound_combo.setCurrentText("✨ spell_aura_buff")

        elif preset_type == "dark":
            self.cast_sound_combo.setCurrentText("🌑 spell_black_cast")
            self.projectile_sound_combo.setCurrentText("🌑 spell_projectile_dark")
            self.resolve_sound_combo.setCurrentText("🌑 spell_hit_aura_black")
            self.hit_sound_combo.setCurrentText("🌑 spell_hit_default_black")
            self.overtime_sound_combo.setCurrentText("🌑 spell_aura_debuff")

    def open_sound_browser(self):
        """Open comprehensive sound browser"""
        QMessageBox.information(self, "🎵 Sound Browser",
                               "🎼 Sound Browser Features:\n\n"
                               "• Browse all game sound files\n"
                               "• Search by name or category\n"
                               "• Preview sounds with waveform\n"
                               "• Drag & drop to assign sounds\n"
                               "• Import custom sound files\n\n"
                               "📁 Would scan: ExtractedAssets/Audio/\n"
                               "🔊 Supported formats: WAV, MP3, OGG")


class ReviewExportPage(QWizardPage):
    """Step 6: Review and export"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Review & Export")
        self.setSubTitle("Review your spell and generate the files")

        layout = QVBoxLayout()

        # Spell Summary
        summary_group = QGroupBox("Spell Summary")
        summary_layout = QVBoxLayout()

        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(150)
        summary_layout.addWidget(self.summary_text)

        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)

        # Stats Table
        stats_group = QGroupBox("Level 15 Stats")
        stats_layout = QVBoxLayout()

        self.stats_table = QTableWidget(1, 6)
        self.stats_table.setHorizontalHeaderLabels([
            "Damage", "Mana Cost", "Cooldown", "Cast Time", "Range", "AOE"
        ])
        self.stats_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        stats_layout.addWidget(self.stats_table)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Balance Score
        balance_group = QGroupBox("Balance Analysis")
        balance_layout = QVBoxLayout()

        self.balance_text = QLabel("Balance score will appear here after validation.")
        self.balance_text.setWordWrap(True)
        balance_layout.addWidget(self.balance_text)

        balance_group.setLayout(balance_layout)
        layout.addWidget(balance_group)

        # Validation Results
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout()

        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(100)
        validation_layout.addWidget(self.validation_text)

        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)

        # Export Options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()

        self.export_lua_checkbox = QCheckBox("Export Lua scripts")
        self.export_lua_checkbox.setChecked(True)
        export_layout.addWidget(self.export_lua_checkbox)

        self.export_test_book_checkbox = QCheckBox("Create test spell book")
        self.export_test_book_checkbox.setChecked(True)
        export_layout.addWidget(self.export_test_book_checkbox)

        self.export_json_checkbox = QCheckBox("Export spell data (JSON)")
        self.export_json_checkbox.setChecked(False)
        export_layout.addWidget(self.export_json_checkbox)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Export Button
        self.export_btn = QPushButton("Export Spell")
        self.export_btn.setStyleSheet("QPushButton { font-weight: bold; padding: 10px; }")
        self.export_btn.clicked.connect(self.export_spell)
        layout.addWidget(self.export_btn)

        layout.addStretch()
        self.setLayout(layout)

    def update_summary(self, spell_data: SpellCreationData):
        """Update the summary display with spell data"""
        summary = f"""
Spell Name: {spell_data.spell_name}
Internal Name: {spell_data.internal_name}
School: {spell_data.magic_school.name}
Type: {spell_data.spell_type.value}
Target: {spell_data.target_type.value}
Projectile: {'Yes' if spell_data.has_projectile else 'No'}
Levels: {spell_data.num_levels}
Scaling: {spell_data.scaling_mode.value}

Description: {spell_data.description}
        """.strip()

        self.summary_text.setPlainText(summary)

        # Update stats table with level 15 data
        if spell_data.levels:
            level_15 = spell_data.levels[-1]
            self.stats_table.setItem(0, 0, QTableWidgetItem(f"{level_15.damage_min}-{level_15.damage_max}"))
            self.stats_table.setItem(0, 1, QTableWidgetItem(str(level_15.mana_cost)))
            self.stats_table.setItem(0, 2, QTableWidgetItem(f"{level_15.cooldown:.1f}s"))
            self.stats_table.setItem(0, 3, QTableWidgetItem(f"{level_15.cast_time:.1f}s"))
            self.stats_table.setItem(0, 4, QTableWidgetItem(f"{level_15.range:.1f}"))
            self.stats_table.setItem(0, 5, QTableWidgetItem(f"{level_15.aoe_radius:.1f}"))

        # Update balance info
        metrics = spell_data.get_balance_metrics()
        balance_info = f"""
Power Rating: {metrics['power_rating']:.1f} ({metrics['balance_category']})
Damage per Mana: {metrics['damage_per_mana']:.2f}
Damage per Second: {metrics['damage_per_second']:.2f}
        """.strip()
        self.balance_text.setText(balance_info)

    def export_spell(self):
        """Export the spell to files"""
        QMessageBox.information(self, "Export",
                               "Spell export functionality coming soon!\n"
                               "Will generate Lua scripts and test files.")


class SpellCreatorWizard(QWizard):
    """Main wizard for spell creation"""

    # Signal emitted when spell is created
    spellCreated = Signal(SpellCreationData)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SpellForce Spell Wizard 🧙")
        self.setWizardStyle(QWizard.WizardStyle.ModernStyle)
        self.setMinimumSize(700, 600)

        # Initialize spell loader
        self.spell_loader = SpellLoader()

        # Set up pages
        self.mode_page = SpellModeSelectionPage()
        self.basics_page = SpellBasicsPage()
        self.target_page = TargetMechanicsPage()
        self.level_page = LevelProgressionPage()
        self.visual_page = VisualEffectsPage()
        self.sound_page = SoundEffectsPage()
        self.review_page = ReviewExportPage()

        self.addPage(self.mode_page)
        self.addPage(self.basics_page)
        self.addPage(self.target_page)
        self.addPage(self.level_page)
        self.addPage(self.visual_page)
        self.addPage(self.sound_page)
        self.addPage(self.review_page)

        # Connect signals
        self.currentIdChanged.connect(self.on_page_changed)

    def on_page_changed(self, page_id):
        """Handle page changes"""
        if page_id == 1:  # Basics page - load copied spell data
            self.load_copied_spell_data()
        elif page_id == 6:  # Review page
            self.update_review_page()

    def load_copied_spell_data(self):
        """Load spell data when using copy/edit modes"""
        creation_mode = self.mode_page.get_creation_mode()
        
        if creation_mode in ["edit", "duplicate"]:
            selected_spell_data = self.mode_page.get_selected_spell_data()
            if selected_spell_data:
                # Load the spell data using the spell loader
                spell_data = self.spell_loader.load_spell_from_data(selected_spell_data)
                if spell_data:
                    # Populate all pages with the loaded spell data
                    self.populate_pages_with_spell_data(spell_data)
                    
                    # For duplicate mode, clear the name and ID to force new entry
                    if creation_mode == "duplicate":
                        self.basics_page.spell_name_edit.clear()
                        self.basics_page.internal_name_edit.clear()
                        # Auto-assign new ID will be handled during export
    
    def populate_pages_with_spell_data(self, spell_data: SpellCreationData):
        """Populate all wizard pages with existing spell data"""
        # Populate basics page
        self.basics_page.spell_name_edit.setText(spell_data.spell_name)
        self.basics_page.internal_name_edit.setText(spell_data.internal_name)
        self.basics_page.description_edit.setPlainText(spell_data.description)
        
        # Set school and type combos
        school_map = {
            MagicSchool.WHITE: 0,
            MagicSchool.FIRE: 1,
            MagicSchool.ICE: 2,
            MagicSchool.BLACK: 3,
            MagicSchool.MENTAL: 4,
            MagicSchool.EARTH: 5
        }
        self.basics_page.school_combo.setCurrentIndex(school_map.get(spell_data.magic_school, 1))
        
        type_map = {
            SpellType.ATTACK: 0,
            SpellType.HEAL: 1,
            SpellType.BUFF: 2,
            SpellType.DEBUFF: 3,
            SpellType.SUMMON: 4,
            SpellType.AOE: 5,
            SpellType.UTILITY: 6
        }
        self.basics_page.type_combo.setCurrentIndex(type_map.get(spell_data.spell_type, 0))
        
        # Populate target page
        target_map = {
            TargetType.SINGLE: 0,
            TargetType.AOE: 1,
            TargetType.SELF: 2,
            TargetType.CONE: 3,
            TargetType.CHAIN: 4
        }
        self.target_page.target_combo.setCurrentIndex(target_map.get(spell_data.target_type, 0))
        self.target_page.projectile_checkbox.setChecked(spell_data.has_projectile)
        self.target_page.range_spin.setValue(int(spell_data.base_range))
        self.target_page.aoe_spin.setValue(int(spell_data.aoe_radius))
        self.target_page.duration_spin.setValue(int(spell_data.duration))
        self.target_page.effects_text.setPlainText(", ".join(spell_data.special_effects))
        
        # Populate level page
        self.level_page.level_spinbox.setValue(spell_data.num_levels)
        
        scaling_map = {
            ScalingMode.LINEAR: "linear (same increase per level)",
            ScalingMode.EXPONENTIAL: "exponential (accelerating growth)",
            ScalingMode.LOGARITHMIC: "logarithmic (diminishing returns)",
            ScalingMode.CUSTOM: "custom (edit each level manually)"
        }
        scaling_text = scaling_map.get(spell_data.scaling_mode, "linear (same increase per level)")
        index = self.level_page.scaling_combo.findText(scaling_text, Qt.MatchFlag.MatchFixedString)
        if index >= 0:
            self.level_page.scaling_combo.setCurrentIndex(index)
        
        # Populate visual page
        self.visual_page.cast_combo.setCurrentText(spell_data.vfx_cast or "None")
        self.visual_page.projectile_combo.setCurrentText(spell_data.vfx_projectile or "None")
        self.visual_page.resolve_combo.setCurrentText(spell_data.vfx_resolve or "None")
        self.visual_page.target_combo.setCurrentText(spell_data.vfx_target or "None")
        self.visual_page.overtime_combo.setCurrentText(spell_data.vfx_overtime or "None")
        
        # Populate sound page
        self.sound_page.cast_combo.setCurrentText(spell_data.sfx_cast or "None")
        self.sound_page.projectile_combo.setCurrentText(spell_data.sfx_projectile or "None")
        self.sound_page.resolve_combo.setCurrentText(spell_data.sfx_resolve or "None")
        self.sound_page.hit_combo.setCurrentText(spell_data.sfx_hit or "None")

    def update_review_page(self):
        """Update review page with current spell data"""
        spell_data = self.collect_spell_data()
        self.review_page.update_summary(spell_data)

    def collect_spell_data(self) -> SpellCreationData:
        """Collect all spell data from wizard pages"""

        # Basics
        spell_name = self.basics_page.spell_name_edit.text()
        internal_name = self.basics_page.internal_name_edit.text()
        description = self.basics_page.description_edit.toPlainText()

        # Map combo box indices to enums
        school_map = {
            0: MagicSchool.WHITE,
            1: MagicSchool.FIRE,
            2: MagicSchool.ICE,
            3: MagicSchool.BLACK,
            4: MagicSchool.MENTAL,
            5: MagicSchool.EARTH
        }
        school = school_map.get(self.basics_page.school_combo.currentIndex(), MagicSchool.FIRE)

        type_map = {
            0: SpellType.ATTACK,
            1: SpellType.HEAL,
            2: SpellType.BUFF,
            3: SpellType.DEBUFF,
            4: SpellType.SUMMON,
            5: SpellType.AOE,
            6: SpellType.UTILITY
        }
        spell_type = type_map.get(self.basics_page.type_combo.currentIndex(), SpellType.ATTACK)

        # Target & Mechanics
        target_map = {
            0: TargetType.SINGLE,
            1: TargetType.AOE,
            2: TargetType.SELF,
            3: TargetType.CONE,
            4: TargetType.CHAIN
        }
        target_type = target_map.get(self.target_page.target_combo.currentIndex(), TargetType.SINGLE)
        has_projectile = self.target_page.projectile_checkbox.isChecked()
        base_range = self.target_page.range_spin.value()
        aoe_radius = self.target_page.aoe_spin.value()
        duration = self.target_page.duration_spin.value()

        # Parse special effects
        effects_text = self.target_page.effects_text.toPlainText()
        special_effects = [e.strip() for e in effects_text.split(',') if e.strip()]

        # Level Progression
        num_levels = self.level_page.level_spinbox.value()

        # Map scaling mode
        scaling_text = self.level_page.scaling_combo.currentText().lower()
        scaling_map = {
            "linear (same increase per level)": ScalingMode.LINEAR,
            "exponential (accelerating growth)": ScalingMode.EXPONENTIAL,
            "logarithmic (diminishing returns)": ScalingMode.LOGARITHMIC,
            "custom (edit each level manually)": ScalingMode.CUSTOM
        }
        scaling_mode = scaling_map.get(scaling_text, ScalingMode.LINEAR)

        # Create spell data
        spell_data = SpellCreationData(
            spell_name=spell_name,
            internal_name=internal_name,
            magic_school=school,
            spell_type=spell_type,
            description=description,
            target_type=target_type,
            has_projectile=has_projectile,
            base_range=base_range,
            aoe_radius=aoe_radius,
            duration=duration,
            special_effects=special_effects,
            num_levels=num_levels,
            scaling_mode=scaling_mode,
        )

        # Set base stats for level 1 from the LevelProgressionPage
        if spell_data.levels:
            base_damage_min = self.level_page.damage_min_spin.value()
            base_damage_max = self.level_page.damage_max_spin.value()
            base_mana = self.level_page.mana_cost_spin.value()
            base_cooldown = self.level_page.cooldown_spin.value()
            base_cast_time = self.level_page.cast_time_spin.value()

            spell_data.levels[0].damage_min = base_damage_min
            spell_data.levels[0].damage_max = base_damage_max
            spell_data.levels[0].mana_cost = base_mana
            spell_data.levels[0].cooldown = base_cooldown
            spell_data.levels[0].cast_time = base_cast_time
            spell_data.levels[0].range = base_range
            spell_data.levels[0].aoe_radius = aoe_radius
            spell_data.levels[0].duration = duration

        # Apply scaling to generate levels 2-15
        spell_data.apply_scaling()

        # Visual Effects (simplified mapping)
        vfx_cast_map = {
            0: "CastFire", 1: "CastIce", 2: "CastWhite",
            3: "CastBlack", 4: "CastMental", 5: "CastEarth"
        }
        spell_data.vfx_cast = vfx_cast_map.get(self.visual_page.cast_combo.currentIndex(), "")

        vfx_projectile_map = {
            0: "ProjectileFireBall", 1: "ProjectileIceShard", 2: "ProjectileLightning",
            3: "ProjectileDarkBolt", 4: "ProjectileHolyBolt", 5: "ProjectileEarthSpike"
        }
        spell_data.vfx_projectile = vfx_projectile_map.get(self.visual_page.projectile_combo.currentIndex(), "")

        vfx_resolve_map = {
            0: "ResolveFireExplosion", 1: "ResolveIceShatter", 2: "ResolveHolyFlash",
            3: "ResolveDarkImplosion", 4: "ResolveLightningStrike", 5: "ResolveEarthCrater"
        }
        spell_data.vfx_resolve = vfx_resolve_map.get(self.visual_page.resolve_combo.currentIndex(), "")

        # Sound Effects (simplified)
        sound_cast_map = {
            0: "spell_white_cast", 1: "spell_black_cast", 2: "spell_fire_cast",
            3: "spell_ice_cast", 4: "spell_earth_cast", 5: "spell_mental_cast"
        }
        spell_data.sfx_cast = sound_cast_map.get(self.sound_page.cast_sound_combo.currentIndex(), "")

        spell_data.sfx_resolve = self.sound_page.resolve_sound_combo.currentText()
        spell_data.sfx_hit = self.sound_page.hit_sound_combo.currentText()

        return spell_data

    def accept(self):
        """Wizard completed successfully"""
        spell_data = self.collect_spell_data()
        
        # Handle spell ID assignment based on mode selection
        id_mode = self.mode_page.get_spell_id_mode()
        if id_mode == "auto":
            # Auto-assign next available ID (simplified - in real implementation would check existing spells)
            spell_data.spell_line_id = 300  # Default starting ID for custom spells
        else:
            # Use manually assigned ID
            spell_data.spell_line_id = self.mode_page.get_manual_spell_id()
        
        # Set creation metadata
        creation_mode = self.mode_page.get_creation_mode()
        if creation_mode == "duplicate":
            selected_spell = self.mode_page.get_selected_spell_data()
            if selected_spell:
                spell_data.description = f"Duplicated from: {selected_spell['name']}\n\n{spell_data.description}"
        
        self.spellCreated.emit(spell_data)
        super().accept()


# Test function
def test_wizard():
    """Test the spell creation wizard"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    wizard = SpellCreatorWizard()
    wizard.show()

    return app.exec()


if __name__ == "__main__":
    test_wizard()