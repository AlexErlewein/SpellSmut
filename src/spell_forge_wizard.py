"""
Spell Forge Wizard - GUI Version

Multi-page wizard for creating custom spells with full GUI support.
"""

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QRadioButton, QGroupBox, QPushButton, QLabel, QMessageBox,
    QFileDialog, QCheckBox
)
from PySide6.QtCore import Qt
from typing import Optional
from pathlib import Path
from datetime import datetime
import json

try:
    from TirganachReloaded.cff_editor.models.spell_creation_data import SpellCreationData
    from TirganachReloaded.cff_editor.models.spell_enums import (
        MagicSchool, SpellType, TargetType, ScalingMode
    )
    from spell_browser_dialog import SpellBrowserDialog
    from spell_validator import SpellValidator
except ImportError as e:
    print(f"Import error: {e}")


class SpellForgeWizard(QWizard):
    """Main wizard for spell creation"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell_data = None
        self.spell_id = None
        self.creation_mode = None
        self.source_spell = None

        self.setWindowTitle("Spell Forge Wizard")
        self.setMinimumSize(800, 600)

        # Add pages
        self.addPage(ModeSelectionPage())
        self.addPage(BasicPropertiesPage())
        self.addPage(MechanicsPage())
        self.addPage(LevelProgressionPage())
        self.addPage(VisualEffectsPage())
        self.addPage(SoundEffectsPage())
        self.addPage(ReviewExportPage())

    def done(self, result):
        """Handle wizard completion"""
        if result == QWizard.DialogCode.Accepted:
            if self.spell_data:
                success = self.export_spell()
                if success:
                    # Ask if user wants to create another
                    reply = QMessageBox.question(
                        self,
                        "Create Another?",
                        "Spell created successfully! Would you like to create another spell?",
                        QMessageBox.Yes | QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        # Reset wizard
                        self.spell_data = None
                        self.creation_mode = None
                        self.source_spell = None
                        self.spell_id = None
                        self.restart()
                        return

        super().done(result)

    def export_spell(self) -> bool:
        """Export spell to JSON"""
        try:
            # Create directory
            spells_dir = Path(__file__).parent / 'custom_spells'
            spells_dir.mkdir(exist_ok=True)

            # Load existing spells
            spells_file = spells_dir / 'spells.json'
            spells = []
            if spells_file.exists():
                with open(spells_file, 'r', encoding='utf-8') as f:
                    spells = json.load(f)

            # Update or add spell
            spell_dict = self.spell_data.to_dict()

            # Find and replace if editing
            found = False
            for i, s in enumerate(spells):
                if s.get('spell_line_id') == self.spell_data.spell_line_id:
                    spells[i] = spell_dict
                    found = True
                    break

            if not found:
                spells.append(spell_dict)

            # Save all spells
            with open(spells_file, 'w', encoding='utf-8') as f:
                json.dump(spells, f, indent=2)

            # Export individual file
            individual_dir = spells_dir / 'individual'
            individual_dir.mkdir(exist_ok=True)

            safe_name = "".join(c if c.isalnum() or c in " -_" else "_"
                                for c in self.spell_data.spell_name).replace(" ", "_").lower()
            filename = f"spell_{self.spell_data.spell_line_id}_{safe_name}.json"
            individual_file = individual_dir / filename

            with open(individual_file, 'w', encoding='utf-8') as f:
                json.dump(spell_dict, f, indent=2)

            QMessageBox.information(
                self,
                "Export Successful",
                f"Spell exported successfully!\n\n"
                f"Name: {self.spell_data.spell_name}\n"
                f"ID: {self.spell_data.spell_line_id}\n"
                f"File: {individual_file}"
            )

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export spell:\n{str(e)}"
            )
            return False


class ModeSelectionPage(QWizardPage):
    """Page 1: Mode Selection & ID Assignment"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_spell = None

        self.setTitle("Mode Selection & ID Assignment")
        self.setSubTitle("Choose how to create your spell and assign a unique ID.")

        layout = QVBoxLayout()

        # Mode selection
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()

        self.new_spell_radio = QRadioButton("Create New Spell (blank slate)")
        self.edit_spell_radio = QRadioButton("Edit Existing Spell")
        self.duplicate_spell_radio = QRadioButton("Duplicate & Modify")
        self.new_spell_radio.setChecked(True)

        mode_layout.addWidget(self.new_spell_radio)
        mode_layout.addWidget(self.edit_spell_radio)
        mode_layout.addWidget(self.duplicate_spell_radio)

        # Browse button
        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse Spells...")
        self.browse_button.clicked.connect(self.browse_spells)
        self.browse_button.setEnabled(False)
        browse_layout.addWidget(self.browse_button)
        browse_layout.addStretch()
        mode_layout.addLayout(browse_layout)

        # Selection label
        self.selected_label = QLabel("No spell selected")
        self.selected_label.setStyleSheet("color: gray; font-style: italic;")
        mode_layout.addWidget(self.selected_label)

        # Enable browse when edit/duplicate selected
        self.edit_spell_radio.toggled.connect(self.on_mode_changed)
        self.duplicate_spell_radio.toggled.connect(self.on_mode_changed)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # ID selection
        id_group = QGroupBox("ID Assignment")
        id_layout = QFormLayout()

        self.spell_id_spin = QSpinBox()
        self.spell_id_spin.setRange(300, 9999)
        self.spell_id_spin.setValue(300)
        id_layout.addRow("Spell ID (300+):", self.spell_id_spin)

        id_group.setLayout(id_layout)
        layout.addWidget(id_group)

        layout.addStretch()
        self.setLayout(layout)

    def on_mode_changed(self):
        """Enable/disable browse button based on mode"""
        is_edit_or_dup = self.edit_spell_radio.isChecked() or self.duplicate_spell_radio.isChecked()
        self.browse_button.setEnabled(is_edit_or_dup)

        if not is_edit_or_dup:
            self.selected_spell = None
            self.selected_label.setText("No spell selected")
            self.selected_label.setStyleSheet("color: gray; font-style: italic;")

    def browse_spells(self):
        """Open spell browser"""
        dialog = SpellBrowserDialog(self)
        if dialog.exec():
            spell_dict = dialog.get_selected_spell_data()
            if spell_dict:
                self.selected_spell = SpellCreationData.from_dict(spell_dict)
                self.selected_label.setText(
                    f"Selected: {self.selected_spell.spell_name} (ID: {self.selected_spell.spell_line_id})"
                )
                self.selected_label.setStyleSheet("color: green; font-weight: bold;")

                # Update ID for duplicate mode
                if self.duplicate_spell_radio.isChecked():
                    # Find next available ID
                    self.spell_id_spin.setValue(self.selected_spell.spell_line_id + 1)

    def validatePage(self):
        """Validate before moving to next page"""
        wizard = self.wizard()

        # Check if edit/duplicate requires selection
        if (self.edit_spell_radio.isChecked() or self.duplicate_spell_radio.isChecked()):
            if self.selected_spell is None:
                QMessageBox.warning(
                    self,
                    "No Spell Selected",
                    "Please select a spell to edit or duplicate."
                )
                return False

        # Store mode and data
        if self.new_spell_radio.isChecked():
            wizard.creation_mode = "new"
            wizard.source_spell = None
            wizard.spell_id = self.spell_id_spin.value()
        elif self.edit_spell_radio.isChecked():
            wizard.creation_mode = "edit"
            wizard.source_spell = self.selected_spell
            wizard.spell_id = self.selected_spell.spell_line_id
        else:  # duplicate
            wizard.creation_mode = "duplicate"
            wizard.source_spell = self.selected_spell
            wizard.spell_id = self.spell_id_spin.value()

        return True


class BasicPropertiesPage(QWizardPage):
    """Page 2: Basic Properties"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Basic Properties")
        self.setSubTitle("Define the fundamental characteristics of your spell.")

        layout = QFormLayout()

        self.spell_name = QLineEdit()
        layout.addRow("Spell Name:", self.spell_name)

        self.internal_name = QLineEdit()
        self.internal_name.setPlaceholderText("No spaces allowed")
        layout.addRow("Internal Name:", self.internal_name)

        self.description = QTextEdit()
        self.description.setMaximumHeight(80)
        layout.addRow("Description:", self.description)

        self.magic_school = QComboBox()
        for school in MagicSchool:
            self.magic_school.addItem(f"{school.name} ({school.value})", school)
        layout.addRow("Magic School:", self.magic_school)

        self.spell_type = QComboBox()
        for stype in SpellType:
            self.spell_type.addItem(stype.value.capitalize(), stype)
        layout.addRow("Spell Type:", self.spell_type)

        self.setLayout(layout)

    def initializePage(self):
        """Initialize with source spell data if editing/duplicating"""
        wizard = self.wizard()
        if wizard.source_spell:
            spell = wizard.source_spell
            self.spell_name.setText(spell.spell_name)
            self.internal_name.setText(spell.internal_name)
            self.description.setPlainText(spell.description)

            # Set school
            for i in range(self.magic_school.count()):
                if self.magic_school.itemData(i) == spell.magic_school:
                    self.magic_school.setCurrentIndex(i)
                    break

            # Set type
            for i in range(self.spell_type.count()):
                if self.spell_type.itemData(i) == spell.spell_type:
                    self.spell_type.setCurrentIndex(i)
                    break


class MechanicsPage(QWizardPage):
    """Page 3: Target & Mechanics"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Target & Mechanics")
        self.setSubTitle("Configure how your spell works.")

        layout = QFormLayout()

        self.target_type = QComboBox()
        for target in TargetType:
            self.target_type.addItem(target.value.capitalize(), target)
        layout.addRow("Target Type:", self.target_type)

        self.has_projectile = QCheckBox("Spell has a projectile")
        layout.addRow("Projectile:", self.has_projectile)

        self.base_range = QDoubleSpinBox()
        self.base_range.setRange(0, 100)
        self.base_range.setValue(20.0)
        self.base_range.setSuffix(" units")
        layout.addRow("Base Range:", self.base_range)

        self.aoe_radius = QDoubleSpinBox()
        self.aoe_radius.setRange(0, 50)
        self.aoe_radius.setValue(0.0)
        self.aoe_radius.setSuffix(" units")
        layout.addRow("AOE Radius:", self.aoe_radius)

        self.duration = QDoubleSpinBox()
        self.duration.setRange(0, 300)
        self.duration.setValue(0.0)
        self.duration.setSuffix(" seconds")
        layout.addRow("Duration:", self.duration)

        self.setLayout(layout)

    def initializePage(self):
        """Initialize with source spell data if editing/duplicating"""
        wizard = self.wizard()
        if wizard.source_spell:
            spell = wizard.source_spell

            # Set target type
            for i in range(self.target_type.count()):
                if self.target_type.itemData(i) == spell.target_type:
                    self.target_type.setCurrentIndex(i)
                    break

            self.has_projectile.setChecked(spell.has_projectile)
            self.base_range.setValue(spell.base_range)
            self.aoe_radius.setValue(spell.aoe_radius)
            self.duration.setValue(spell.duration)


class LevelProgressionPage(QWizardPage):
    """Page 4: Level Progression & Scaling"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Level Progression & Scaling")
        self.setSubTitle("Configure spell power across levels.")

        layout = QVBoxLayout()

        # Number of levels
        num_levels_layout = QFormLayout()
        self.num_levels = QSpinBox()
        self.num_levels.setRange(1, 15)
        self.num_levels.setValue(15)
        num_levels_layout.addRow("Number of Levels:", self.num_levels)
        layout.addLayout(num_levels_layout)

        # Base stats (Level 1)
        base_group = QGroupBox("Level 1 Base Stats")
        base_layout = QFormLayout()

        self.damage_min = QSpinBox()
        self.damage_min.setRange(0, 1000)
        self.damage_min.setValue(15)
        base_layout.addRow("Minimum Damage:", self.damage_min)

        self.damage_max = QSpinBox()
        self.damage_max.setRange(0, 1000)
        self.damage_max.setValue(20)
        base_layout.addRow("Maximum Damage:", self.damage_max)

        self.mana_cost = QSpinBox()
        self.mana_cost.setRange(0, 1000)
        self.mana_cost.setValue(10)
        base_layout.addRow("Mana Cost:", self.mana_cost)

        self.cooldown = QDoubleSpinBox()
        self.cooldown.setRange(0, 60)
        self.cooldown.setValue(3.0)
        self.cooldown.setSuffix(" seconds")
        base_layout.addRow("Cooldown:", self.cooldown)

        self.cast_time = QDoubleSpinBox()
        self.cast_time.setRange(0, 10)
        self.cast_time.setValue(1.5)
        self.cast_time.setSuffix(" seconds")
        base_layout.addRow("Cast Time:", self.cast_time)

        base_group.setLayout(base_layout)
        layout.addWidget(base_group)

        # Scaling mode
        scaling_group = QGroupBox("Scaling Mode")
        scaling_layout = QVBoxLayout()

        self.scaling_mode = QComboBox()
        for mode in ScalingMode:
            self.scaling_mode.addItem(mode.value.capitalize(), mode)
        scaling_layout.addWidget(self.scaling_mode)

        scaling_info = QLabel(
            "Linear: Steady growth\n"
            "Exponential: Accelerating power (1.15x per level)\n"
            "Logarithmic: Diminishing returns\n"
            "Custom: Manual per-level configuration"
        )
        scaling_info.setStyleSheet("color: gray; font-size: 9pt;")
        scaling_layout.addWidget(scaling_info)

        scaling_group.setLayout(scaling_layout)
        layout.addWidget(scaling_group)

        layout.addStretch()
        self.setLayout(layout)

    def initializePage(self):
        """Initialize with source spell data if editing/duplicating"""
        wizard = self.wizard()
        if wizard.source_spell and wizard.source_spell.levels:
            spell = wizard.source_spell
            self.num_levels.setValue(spell.num_levels)

            # Level 1 stats
            lvl1 = spell.levels[0]
            self.damage_min.setValue(lvl1.damage_min)
            self.damage_max.setValue(lvl1.damage_max)
            self.mana_cost.setValue(lvl1.mana_cost)
            self.cooldown.setValue(lvl1.cooldown)
            self.cast_time.setValue(lvl1.cast_time)

            # Scaling mode
            for i in range(self.scaling_mode.count()):
                if self.scaling_mode.itemData(i) == spell.scaling_mode:
                    self.scaling_mode.setCurrentIndex(i)
                    break


class VisualEffectsPage(QWizardPage):
    """Page 5: Visual Effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Visual Effects")
        self.setSubTitle("Assign visual effect names for your spell.")

        layout = QFormLayout()

        self.vfx_cast = QLineEdit()
        self.vfx_cast.setPlaceholderText("e.g., CastFire")
        layout.addRow("Cast Effect:", self.vfx_cast)

        self.vfx_projectile = QLineEdit()
        self.vfx_projectile.setPlaceholderText("e.g., ProjectileFireBall")
        layout.addRow("Projectile Effect:", self.vfx_projectile)

        self.vfx_resolve = QLineEdit()
        self.vfx_resolve.setPlaceholderText("e.g., ResolveFireExplosion")
        layout.addRow("Resolve Effect:", self.vfx_resolve)

        self.vfx_target = QLineEdit()
        layout.addRow("Target Effect:", self.vfx_target)

        self.vfx_overtime = QLineEdit()
        layout.addRow("Over Time Effect:", self.vfx_overtime)

        self.setLayout(layout)

    def initializePage(self):
        """Initialize with source spell data if editing/duplicating"""
        wizard = self.wizard()
        if wizard.source_spell:
            spell = wizard.source_spell
            self.vfx_cast.setText(spell.vfx_cast)
            self.vfx_projectile.setText(spell.vfx_projectile)
            self.vfx_resolve.setText(spell.vfx_resolve)
            self.vfx_target.setText(spell.vfx_target)
            self.vfx_overtime.setText(spell.vfx_overtime)


class SoundEffectsPage(QWizardPage):
    """Page 6: Sound Effects"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Sound Effects")
        self.setSubTitle("Assign sound effect names for your spell.")

        layout = QFormLayout()

        self.sfx_cast = QLineEdit()
        self.sfx_cast.setPlaceholderText("e.g., spell_fire_cast")
        layout.addRow("Cast Sound:", self.sfx_cast)

        self.sfx_projectile = QLineEdit()
        layout.addRow("Projectile Sound:", self.sfx_projectile)

        self.sfx_resolve = QLineEdit()
        layout.addRow("Resolve Sound:", self.sfx_resolve)

        self.sfx_hit = QLineEdit()
        self.sfx_hit.setPlaceholderText("e.g., spell_hit_fireburst")
        layout.addRow("Hit Sound:", self.sfx_hit)

        self.setLayout(layout)

    def initializePage(self):
        """Initialize with source spell data if editing/duplicating"""
        wizard = self.wizard()
        if wizard.source_spell:
            spell = wizard.source_spell
            self.sfx_cast.setText(spell.sfx_cast)
            self.sfx_projectile.setText(spell.sfx_projectile)
            self.sfx_resolve.setText(spell.sfx_resolve)
            self.sfx_hit.setText(spell.sfx_hit)


class ReviewExportPage(QWizardPage):
    """Page 7: Review & Export"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Review & Export")
        self.setSubTitle("Review the final spell and export it.")

        layout = QVBoxLayout()

        # Summary
        layout.addWidget(QLabel("Spell Summary:"))
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(250)
        layout.addWidget(self.summary_text)

        # Validation
        layout.addWidget(QLabel("Validation Results:"))
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(150)
        layout.addWidget(self.validation_text)

        self.setLayout(layout)

    def initializePage(self):
        """Build spell data and display summary"""
        wizard = self.wizard()

        # Build spell data from all pages
        spell_data = self.build_spell_data()
        wizard.spell_data = spell_data

        # Display summary
        self.display_summary(spell_data)

        # Validate
        self.validate_spell(spell_data)

    def build_spell_data(self) -> SpellCreationData:
        """Build spell data from wizard pages"""
        wizard = self.wizard()

        # Get all pages
        basic_page = wizard.page(1)
        mechanics_page = wizard.page(2)
        level_page = wizard.page(3)
        vfx_page = wizard.page(4)
        sfx_page = wizard.page(5)

        # Create spell data
        spell = SpellCreationData(
            spell_line_id=wizard.spell_id,
            spell_name=basic_page.spell_name.text(),
            internal_name=basic_page.internal_name.text(),
            description=basic_page.description.toPlainText(),
            magic_school=basic_page.magic_school.currentData(),
            spell_type=basic_page.spell_type.currentData(),
            target_type=mechanics_page.target_type.currentData(),
            has_projectile=mechanics_page.has_projectile.isChecked(),
            base_range=mechanics_page.base_range.value(),
            aoe_radius=mechanics_page.aoe_radius.value(),
            duration=mechanics_page.duration.value(),
            num_levels=level_page.num_levels.value(),
            scaling_mode=level_page.scaling_mode.currentData(),
            vfx_cast=vfx_page.vfx_cast.text(),
            vfx_projectile=vfx_page.vfx_projectile.text(),
            vfx_resolve=vfx_page.vfx_resolve.text(),
            vfx_target=vfx_page.vfx_target.text(),
            vfx_overtime=vfx_page.vfx_overtime.text(),
            sfx_cast=sfx_page.sfx_cast.text(),
            sfx_projectile=sfx_page.sfx_projectile.text(),
            sfx_resolve=sfx_page.sfx_resolve.text(),
            sfx_hit=sfx_page.sfx_hit.text(),
        )

        # Set level 1 base stats
        spell.levels[0].damage_min = level_page.damage_min.value()
        spell.levels[0].damage_max = level_page.damage_max.value()
        spell.levels[0].mana_cost = level_page.mana_cost.value()
        spell.levels[0].cooldown = level_page.cooldown.value()
        spell.levels[0].cast_time = level_page.cast_time.value()

        # Apply scaling
        spell.apply_scaling()

        return spell

    def display_summary(self, spell: SpellCreationData):
        """Display spell summary"""
        metrics = spell.get_balance_metrics()

        html = f"""
        <h2>{spell.spell_name}</h2>
        <p><b>ID:</b> {spell.spell_line_id} | <b>Internal Name:</b> {spell.internal_name}</p>

        <h3>Properties</h3>
        <p><b>School:</b> {spell.magic_school.name} | <b>Type:</b> {spell.spell_type.value.capitalize()}</p>
        <p><b>Target:</b> {spell.target_type.value.capitalize()} |
           <b>Range:</b> {spell.base_range} |
           <b>AOE:</b> {spell.aoe_radius}</p>
        <p><b>Projectile:</b> {'Yes' if spell.has_projectile else 'No'} |
           <b>Duration:</b> {spell.duration}s</p>

        <h3>Level Progression</h3>
        <p><b>Levels:</b> {spell.num_levels} | <b>Scaling:</b> {spell.scaling_mode.value.capitalize()}</p>
        """

        if spell.levels:
            lvl1 = spell.levels[0]
            html += f"""
            <p><b>Level 1:</b> Damage {lvl1.damage_min}-{lvl1.damage_max},
               Mana {lvl1.mana_cost}, DPS {lvl1.dps:.1f}</p>
            """

            if len(spell.levels) > 1:
                lvlmax = spell.levels[-1]
                html += f"""
                <p><b>Level {spell.num_levels}:</b> Damage {lvlmax.damage_min}-{lvlmax.damage_max},
                   Mana {lvlmax.mana_cost}, DPS {lvlmax.dps:.1f}</p>
                """

        if metrics:
            html += f"""
            <h3>Balance Metrics</h3>
            <p><b>Damage per Mana:</b> {metrics.get('damage_per_mana', 0):.2f}</p>
            <p><b>DPS:</b> {metrics.get('damage_per_second', 0):.1f}</p>
            <p><b>Power Rating:</b> {metrics.get('power_rating', 0):.1f}</p>
            <p><b>Category:</b> <span style="color: {'red' if metrics.get('balance_category') == 'Overpowered' else 'green'};">
               {metrics.get('balance_category', 'Unknown')}</span></p>
            """

        if spell.description:
            html += f"<h3>Description</h3><p><i>{spell.description}</i></p>"

        self.summary_text.setHtml(html)

    def validate_spell(self, spell: SpellCreationData):
        """Validate the spell"""
        validator = SpellValidator()
        errors, warnings = validator.validate(spell)

        if not errors and not warnings:
            html = '<p style="color: green; font-weight: bold;">✓ Spell is valid and ready for export!</p>'
        else:
            html = ""
            if errors:
                html += '<h4 style="color: red;">❌ Errors:</h4><ul>'
                for error in errors:
                    html += f'<li style="color: red;">{error}</li>'
                html += '</ul>'

            if warnings:
                html += '<h4 style="color: orange;">⚠️ Warnings:</h4><ul>'
                for warning in warnings:
                    html += f'<li style="color: orange;">{warning}</li>'
                html += '</ul>'

        self.validation_text.setHtml(html)


def main():
    """Main entry point for standalone testing"""
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    wizard = SpellForgeWizard()
    wizard.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
