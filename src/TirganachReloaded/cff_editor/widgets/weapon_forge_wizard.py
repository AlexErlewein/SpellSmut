from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWizard,
    QWizardPage,
)
from PySide6.QtCore import QDir
import json
from pathlib import Path
from datetime import datetime

from ..exporters.weapon_loader import WeaponLoader
from ..models.weapon_creation_data import (
    DamageCategory,
    DamageType,
    Rarity,
    WeaponHands,
    WeaponCreationData,
    WeaponRequirements,
)
from ..shared.id_manager import ContentType, IDManager
from .weapon_sound_manager import create_sound_selector_widget, auto_assign_weapon_sounds
from .weapon_validation import WeaponValidator


class WeaponForgeWizard(QWizard):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.weapon_data = None
        self.weapon_id = None

        self.setWindowTitle("Weapon Forge Wizard")

        self.addPage(ModeSelectionPage(self.id_manager))
        self.addPage(BasicPropertiesPage())
        self.addPage(CombatStatsPage())
        self.addPage(RequirementsValuePage())
        self.addPage(VisualAudioPage())
        self.addPage(ReviewExportPage())

    def done(self, result):
        if result == QDialog.DialogCode.Accepted:
            # Export weapon data when user clicks Finish
            if self.weapon_data:
                success = self.export_weapon()
                if not success:
                    # Export failed, don't close wizard yet
                    return
        elif result == QDialog.DialogCode.Rejected and self.weapon_id:
            # Release ID if cancelled
            self.id_manager.release_id(ContentType.WEAPON, self.weapon_id)
        super().done(result)

    def export_weapon(self) -> bool:
        """Export weapon to JSON (and eventually CFF)"""
        try:
            # Get export page to check options
            export_page = self.page(5)  # ReviewExportPage

            # For now, we only support JSON export
            if export_page.export_json_radio.isChecked():
                return self.export_to_json()
            else:
                QMessageBox.warning(
                    self,
                    "Export Not Available",
                    "CFF export is not yet implemented. Please use JSON export."
                )
                return False
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export weapon:\n{str(e)}"
            )
            return False

    def export_to_json(self) -> bool:
        """Export weapon data to JSON file"""
        try:
            # Create weapons directory if it doesn't exist
            weapons_dir = Path("custom_weapons")
            weapons_dir.mkdir(exist_ok=True)

            # Generate filename from weapon name
            safe_name = "".join(
                c if c.isalnum() or c in (' ', '-', '_') else '_'
                for c in self.weapon_data.weapon_name
            )
            safe_name = safe_name.replace(' ', '_').lower()
            filename = f"weapon_{self.weapon_data.weapon_id}_{safe_name}.json"
            filepath = weapons_dir / filename

            # Add metadata
            self.weapon_data.created_date = datetime.now().isoformat()
            self.weapon_data.modified_date = datetime.now().isoformat()
            self.weapon_data.author = "CFF Editor - Weapon Forge"

            # Convert weapon data to dict
            weapon_dict = {
                "weapon_id": self.weapon_data.weapon_id,
                "creation_mode": self.weapon_data.creation_mode,
                "source_weapon_id": self.weapon_data.source_weapon_id,
                "weapon_name": self.weapon_data.weapon_name,
                "weapon_type_id": self.weapon_data.weapon_type_id,
                "weapon_type_name": self.weapon_data.weapon_type_name,
                "weapon_material_id": self.weapon_data.weapon_material_id,
                "weapon_material_name": self.weapon_data.weapon_material_name,
                "hands": self.weapon_data.hands.value,
                "damage_category": self.weapon_data.damage_category.value,
                "description": self.weapon_data.description,
                "min_damage": self.weapon_data.min_damage,
                "max_damage": self.weapon_data.max_damage,
                "damage_type": self.weapon_data.damage_type.value,
                "attack_speed": self.weapon_data.attack_speed,
                "min_range": self.weapon_data.min_range,
                "max_range": self.weapon_data.max_range,
                "attack_arc": self.weapon_data.attack_arc,
                "critical_chance": self.weapon_data.critical_chance,
                "armor_penetration": self.weapon_data.armor_penetration,
                "knockback_chance": self.weapon_data.knockback_chance,
                "requirements": {
                    "strength": self.weapon_data.requirements.strength,
                    "dexterity": self.weapon_data.requirements.dexterity,
                    "intelligence": self.weapon_data.requirements.intelligence,
                    "level": self.weapon_data.requirements.level
                },
                "sell_value": self.weapon_data.sell_value,
                "buy_value": self.weapon_data.buy_value,
                "rarity": self.weapon_data.rarity.value,
                "effects": [
                    {
                        "effect_id": e.effect_id,
                        "effect_name": e.effect_name,
                        "value": e.value,
                        "duration": e.duration
                    }
                    for e in self.weapon_data.effects
                ],
                "item_set_id": self.weapon_data.item_set_id,
                "icon_handle": self.weapon_data.icon_handle,
                "hit_sound": self.weapon_data.hit_sound,
                "miss_sound": self.weapon_data.miss_sound,
                "equip_sound": self.weapon_data.equip_sound,
                "model_file": self.weapon_data.model_file,
                "trail_effect": self.weapon_data.trail_effect,
                "impact_effect": self.weapon_data.impact_effect,
                "created_date": self.weapon_data.created_date,
                "modified_date": self.weapon_data.modified_date,
                "author": self.weapon_data.author,
                "version": self.weapon_data.version
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(weapon_dict, f, indent=2, ensure_ascii=False)

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Weapon exported successfully!\n\n"
                f"File: {filepath}\n"
                f"Weapon ID: {self.weapon_data.weapon_id}\n"
                f"Name: {self.weapon_data.weapon_name}\n\n"
                f"DPS: {self.weapon_data.calculate_dps():.1f}\n"
                f"Balance Rating: {self.weapon_data.get_balance_rating()}/100"
            )

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export weapon to JSON:\n{str(e)}"
            )
            return False


class ModeSelectionPage(QWizardPage):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.selected_weapon_data = None
        self.weapon_loader = WeaponLoader()
        self.setTitle("Mode Selection & ID Assignment")
        self.setSubTitle("Choose how to create your weapon and assign a unique ID.")

        layout = QVBoxLayout()

        # Creation Mode
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()
        self.new_weapon_radio = QRadioButton("Create New Weapon (blank slate)")
        self.edit_weapon_radio = QRadioButton(
            "Edit Existing Weapon (load from 719 weapons)"
        )
        self.duplicate_weapon_radio = QRadioButton(
            "Duplicate & Modify (copy existing, new ID)"
        )
        self.new_weapon_radio.setChecked(True)
        mode_layout.addWidget(self.new_weapon_radio)
        mode_layout.addWidget(self.edit_weapon_radio)
        mode_layout.addWidget(self.duplicate_weapon_radio)

        # Browse button for edit/duplicate modes
        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse Weapons...")
        self.browse_button.clicked.connect(self.browse_weapons)
        self.browse_button.setEnabled(False)
        browse_layout.addWidget(self.browse_button)
        browse_layout.addStretch()
        mode_layout.addLayout(browse_layout)

        # Selected weapon display
        self.selected_weapon_label = QLabel("No weapon selected")
        self.selected_weapon_label.setStyleSheet("color: gray; font-style: italic;")
        mode_layout.addWidget(self.selected_weapon_label)

        # Enable browse button when edit/duplicate modes are selected
        self.edit_weapon_radio.toggled.connect(self.on_mode_changed)
        self.duplicate_weapon_radio.toggled.connect(self.on_mode_changed)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # ID Assignment
        id_group = QGroupBox("ID Assignment")
        id_layout = QVBoxLayout()
        self.auto_id_radio = QRadioButton("Auto-assign next available ID (recommended)")
        self.manual_id_radio = QRadioButton("Manual ID entry (with validation)")
        self.auto_id_radio.setChecked(True)
        id_layout.addWidget(self.auto_id_radio)
        id_layout.addWidget(self.manual_id_radio)

        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(10000, 19999)
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(self.manual_id_spin.setEnabled)
        id_layout.addWidget(self.manual_id_spin)

        available_count = self.id_manager.get_available_count(ContentType.WEAPON)
        id_status_label = QLabel(f"{available_count} available in range 10000-19999")
        id_layout.addWidget(id_status_label)

        id_group.setLayout(id_layout)
        layout.addWidget(id_group)

        self.setLayout(layout)

    def on_mode_changed(self):
        """Enable/disable browse button based on mode selection"""
        is_edit_or_duplicate = (
            self.edit_weapon_radio.isChecked()
            or self.duplicate_weapon_radio.isChecked()
        )
        self.browse_button.setEnabled(is_edit_or_duplicate)

        # Clear selection if switching back to new mode
        if not is_edit_or_duplicate:
            self.selected_weapon_data = None
            self.selected_weapon_label.setText("No weapon selected")
            self.selected_weapon_label.setStyleSheet("color: gray; font-style: italic;")

    def browse_weapons(self):
        """Open weapon browser dialog"""
        dialog = WeaponBrowserDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            weapon_dict = dialog.get_selected_weapon()
            if weapon_dict:
                try:
                    # Load the weapon using WeaponLoader with GameData path
                    gamedata_path = Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "data" / "GameData.cff"
                    gamedata_path_str = str(gamedata_path) if gamedata_path.exists() else None
                    self.selected_weapon_data = self.weapon_loader.load_weapon(
                        weapon_dict["item_id"],
                        gamedata_path=gamedata_path_str
                    )

                    # Update the display label
                    self.selected_weapon_label.setText(
                        f"Selected: {weapon_dict['name']} (ID: {weapon_dict['item_id']})"
                    )
                    self.selected_weapon_label.setStyleSheet(
                        "color: green; font-weight: bold;"
                    )

                except Exception as e:
                    QMessageBox.warning(
                        self, "Load Error", f"Failed to load weapon: {str(e)}"
                    )
                    self.selected_weapon_data = None
                    self.selected_weapon_label.setText("Error loading weapon")
                    self.selected_weapon_label.setStyleSheet("color: red;")

    def validatePage(self):
        """Validate the page before moving to next"""
        # Check if edit/duplicate mode requires a weapon selection
        if (
            self.edit_weapon_radio.isChecked()
            or self.duplicate_weapon_radio.isChecked()
        ):
            if self.selected_weapon_data is None:
                QMessageBox.warning(
                    self,
                    "No Weapon Selected",
                    "Please select a weapon to edit or duplicate by clicking 'Browse Weapons...'",
                )
                return False

        # Store data in wizard for other pages to access
        wizard = self.wizard()

        # Determine creation mode
        if self.new_weapon_radio.isChecked():
            wizard.creation_mode = "new"
            wizard.source_weapon = None
        elif self.edit_weapon_radio.isChecked():
            wizard.creation_mode = "edit"
            wizard.source_weapon = self.selected_weapon_data
        else:  # duplicate
            wizard.creation_mode = "duplicate"
            wizard.source_weapon = self.selected_weapon_data

        # Allocate or validate ID
        if self.auto_id_radio.isChecked():
            try:
                wizard.weapon_id = self.id_manager.allocate_id(ContentType.WEAPON)
            except ValueError as e:
                QMessageBox.critical(self, "ID Allocation Error", str(e))
                return False
        else:
            requested_id = self.manual_id_spin.value()
            if not self.id_manager.is_valid_id(ContentType.WEAPON, requested_id):
                QMessageBox.warning(
                    self,
                    "Invalid ID",
                    f"ID {requested_id} is outside the valid range (10000-19999)",
                )
                return False

            if self.id_manager.is_id_used(ContentType.WEAPON, requested_id):
                QMessageBox.warning(
                    self,
                    "ID Already In Use",
                    f"ID {requested_id} is already allocated. Please choose another ID.",
                )
                return False

            try:
                wizard.weapon_id = self.id_manager.allocate_id(
                    ContentType.WEAPON, requested_id
                )
            except ValueError as e:
                QMessageBox.critical(self, "ID Allocation Error", str(e))
                return False

        return True


class BasicPropertiesPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Basic Properties")
        self.setSubTitle("Define the fundamental characteristics of your weapon.")

        layout = QFormLayout()
        self.weapon_name_edit = QLineEdit()
        layout.addRow("Weapon Name:", self.weapon_name_edit)

        self.weapon_type_combo = QComboBox()
        # This would be populated with existing and new weapon types
        self.weapon_type_combo.addItems(["1H Sword", "2H Axe", "Dagger"])  # Placeholder
        layout.addRow("Weapon Type:", self.weapon_type_combo)

        self.weapon_material_combo = QComboBox()
        # This would be populated with existing and new materials
        self.weapon_material_combo.addItems(["Metal", "Wood", "Bone"])  # Placeholder
        layout.addRow("Weapon Material:", self.weapon_material_combo)

        self.hands_combo = QComboBox()
        self.hands_combo.addItems([h.value for h in WeaponHands])
        layout.addRow("Hands Required:", self.hands_combo)

        self.damage_category_combo = QComboBox()
        self.damage_category_combo.addItems([c.value for c in DamageCategory])
        layout.addRow("Damage Category:", self.damage_category_combo)

        self.description_edit = QTextEdit()
        layout.addRow("Description:", self.description_edit)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source weapon if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_weapon") and wizard.source_weapon is not None:
            weapon = wizard.source_weapon

            # Populate basic properties from source weapon
            self.weapon_name_edit.setText(weapon.weapon_name)

            # Find and select the weapon type
            type_text = weapon.weapon_type_name
            index = self.weapon_type_combo.findText(type_text)
            if index >= 0:
                self.weapon_type_combo.setCurrentIndex(index)

            # Find and select the material
            material_text = weapon.weapon_material_name
            index = self.weapon_material_combo.findText(material_text)
            if index >= 0:
                self.weapon_material_combo.setCurrentIndex(index)

            # Set hands
            index = self.hands_combo.findText(weapon.hands.value)
            if index >= 0:
                self.hands_combo.setCurrentIndex(index)

            # Set damage category
            index = self.damage_category_combo.findText(weapon.damage_category.value)
            if index >= 0:
                self.damage_category_combo.setCurrentIndex(index)

            # Set description
            self.description_edit.setPlainText(weapon.description)


class CombatStatsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Combat Stats")
        self.setSubTitle("Set the damage, speed, and other combat-related statistics.")

        layout = QFormLayout()

        self.min_damage_spin = QSpinBox()
        self.min_damage_spin.setRange(0, 1000)
        layout.addRow("Minimum Damage:", self.min_damage_spin)

        self.max_damage_spin = QSpinBox()
        self.max_damage_spin.setRange(0, 1000)
        layout.addRow("Maximum Damage:", self.max_damage_spin)

        self.damage_type_combo = QComboBox()
        self.damage_type_combo.addItems([t.value for t in DamageType])
        layout.addRow("Damage Type:", self.damage_type_combo)

        self.attack_speed_spin = QSpinBox()
        self.attack_speed_spin.setRange(1, 200)
        layout.addRow("Attack Speed (lower is faster):", self.attack_speed_spin)

        self.min_range_spin = QSpinBox()
        layout.addRow("Minimum Range:", self.min_range_spin)

        self.max_range_spin = QSpinBox()
        layout.addRow("Maximum Range:", self.max_range_spin)

        self.attack_arc_spin = QSpinBox()
        self.attack_arc_spin.setRange(0, 360)
        layout.addRow("Attack Arc (degrees):", self.attack_arc_spin)

        self.crit_chance_spin = QDoubleSpinBox()
        self.crit_chance_spin.setSuffix(" %")
        layout.addRow("Critical Hit Chance:", self.crit_chance_spin)

        self.armor_pen_spin = QDoubleSpinBox()
        self.armor_pen_spin.setSuffix(" %")
        layout.addRow("Armor Penetration:", self.armor_pen_spin)

        self.knockback_spin = QDoubleSpinBox()
        self.knockback_spin.setSuffix(" %")
        layout.addRow("Knockback Chance:", self.knockback_spin)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source weapon if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_weapon") and wizard.source_weapon is not None:
            weapon = wizard.source_weapon

            # Populate combat stats from source weapon
            self.min_damage_spin.setValue(weapon.min_damage)
            self.max_damage_spin.setValue(weapon.max_damage)

            # Set damage type
            index = self.damage_type_combo.findText(weapon.damage_type.value)
            if index >= 0:
                self.damage_type_combo.setCurrentIndex(index)

            self.attack_speed_spin.setValue(weapon.attack_speed)
            self.min_range_spin.setValue(weapon.min_range)
            self.max_range_spin.setValue(weapon.max_range)
            self.attack_arc_spin.setValue(weapon.attack_arc)
            self.crit_chance_spin.setValue(weapon.critical_chance)
            self.armor_pen_spin.setValue(weapon.armor_penetration)
            self.knockback_spin.setValue(weapon.knockback_chance)


class RequirementsValuePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Requirements & Value")
        self.setSubTitle(
            "Define what is needed to use the weapon and its economic value."
        )

        layout = QFormLayout()

        self.strength_spin = QSpinBox()
        layout.addRow("Strength Required:", self.strength_spin)

        self.dexterity_spin = QSpinBox()
        layout.addRow("Dexterity Required:", self.dexterity_spin)

        self.intelligence_spin = QSpinBox()
        layout.addRow("Intelligence Required:", self.intelligence_spin)

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        layout.addRow("Level Required:", self.level_spin)

        self.sell_value_spin = QSpinBox()
        self.sell_value_spin.setRange(0, 1000000)
        layout.addRow("Sell Value (gold):", self.sell_value_spin)

        self.buy_value_spin = QSpinBox()
        self.buy_value_spin.setRange(0, 1000000)
        layout.addRow("Buy Value (gold):", self.buy_value_spin)

        self.rarity_combo = QComboBox()
        self.rarity_combo.addItems([r.value for r in Rarity])
        layout.addRow("Rarity:", self.rarity_combo)

        # Effects and Item Set would be more complex widgets
        layout.addRow("Effects:", QLabel("Effect list placeholder"))
        layout.addRow("Item Set:", QLabel("Item set placeholder"))

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source weapon if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_weapon") and wizard.source_weapon is not None:
            weapon = wizard.source_weapon

            # Populate requirements
            self.strength_spin.setValue(weapon.requirements.strength)
            self.dexterity_spin.setValue(weapon.requirements.dexterity)
            self.intelligence_spin.setValue(weapon.requirements.intelligence)
            self.level_spin.setValue(weapon.requirements.level)

            # Populate values
            self.sell_value_spin.setValue(weapon.sell_value)
            self.buy_value_spin.setValue(weapon.buy_value)

            # Set rarity
            index = self.rarity_combo.findText(weapon.rarity.value)
            if index >= 0:
                self.rarity_combo.setCurrentIndex(index)

            # Note: Effects would need to be populated in a more complex way
            # since they're in a list. For now, we'll skip that.


class VisualAudioPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Visual & Audio")
        self.setSubTitle("Assign an icon, sounds, and other visual properties.")

        layout = QFormLayout()
        layout.addRow("Icon:", QLabel("Icon browser placeholder"))
        
        # Sound selection widgets (will be populated in initializePage)
        self.sound_selector_widget = None
        layout.addRow(self.sound_selector_widget)
        
    def _setup_sound_selection(self):
        """Setup sound selection based on current weapon data"""
        wizard = self.wizard()
        
        # Get weapon data from previous pages
        mode_page = wizard.page(0)  # ModeSelectionPage
        basic_page = wizard.page(1)  # BasicPropertiesPage
        
        if hasattr(mode_page, 'selected_weapon_data') and mode_page.selected_weapon_data:
            source_weapon = mode_page.selected_weapon_data
            weapon_type = basic_page.weapon_type_combo.currentText().lower()
            hands = basic_page.hands_combo.currentText()
            
            # Auto-assign sounds based on weapon type
            auto_sounds = auto_assign_weapon_sounds(weapon_type, source_weapon.weapon_type_name if hasattr(source_weapon, 'weapon_type_name') else weapon_type, hands)
            
            # Create sound selector widget
            self.sound_selector_widget = create_sound_selector_widget(
                weapon_type,
                hands,
                auto_sounds.get('hit', ''),
                auto_sounds.get('miss', '')
            )
            
            # Replace placeholder with our widget
            # Note: This is a simple replacement - for a real implementation,
            # we'd need to restructure the layout more carefully
            if self.sound_selector_widget:
                self.current_hit_sound = self.sound_selector_widget.hit_sound
                self.current_miss_sound = self.sound_selector_widget.miss_sound
        
        # Call the parent initialization
        if hasattr(super(), 'initializePage'):
            super().initializePage()
        
    def initializePage(self):
        """Initialize visual and audio page with data from previous wizard pages"""
        self._setup_sound_selection()
        layout.addRow("3D Model:", QLabel("Model browser placeholder"))
        layout.addRow("Trail Effect:", QLineEdit())
        layout.addRow("Impact Effect:", QLineEdit())
        self.setLayout(layout)


class ReviewExportPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Review & Export")
        self.setSubTitle("Review the final weapon and export it to the game data.")

        layout = QVBoxLayout()

        # Weapon Summary Section
        layout.addWidget(QLabel("Weapon Summary:"))
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(200)
        layout.addWidget(self.summary_text)

        # Validation Results Section
        layout.addWidget(QLabel("Validation Results:"))
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMinimumHeight(120)
        layout.addWidget(self.validation_text)

        # Export Options Section
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()

        self.export_json_radio = QRadioButton("Export to JSON only")
        self.export_cff_radio = QRadioButton("Export to CFF only (not yet implemented)")
        self.export_both_radio = QRadioButton("Export to both JSON and CFF")

        self.export_json_radio.setChecked(True)
        self.export_cff_radio.setEnabled(False)  # Disable until CFF export is implemented
        self.export_both_radio.setEnabled(False)

        export_layout.addWidget(self.export_json_radio)
        export_layout.addWidget(self.export_cff_radio)
        export_layout.addWidget(self.export_both_radio)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        self.setLayout(layout)

    def initializePage(self):
        """Gather all weapon data, display summary and validation results"""
        wizard = self.wizard()

        # Build weapon data from all pages
        weapon_data = self.build_weapon_data_from_wizard()

        # Store in wizard for export
        wizard.weapon_data = weapon_data

        # Display summary
        summary_html = self.format_weapon_summary(weapon_data)
        self.summary_text.setHtml(summary_html)

        # Run validation and display results
        validator = WeaponValidator(wizard.id_manager)
        errors, warnings = validator.validate(weapon_data)
        validation_html = self.format_validation(errors, warnings)
        self.validation_text.setHtml(validation_html)

    def build_weapon_data_from_wizard(self) -> WeaponCreationData:
        """Gather data from all wizard pages and build WeaponCreationData object"""
        wizard = self.wizard()

        # Get references to all pages
        mode_page = wizard.page(0)  # ModeSelectionPage
        basic_page = wizard.page(1)  # BasicPropertiesPage
        combat_page = wizard.page(2)  # CombatStatsPage
        req_page = wizard.page(3)    # RequirementsValuePage
        visual_page = wizard.page(4)  # VisualAudioPage

        # Determine creation mode
        if mode_page.new_weapon_radio.isChecked():
            creation_mode = "new"
            source_weapon_id = None
        elif mode_page.edit_weapon_radio.isChecked():
            creation_mode = "edit"
            source_weapon_id = getattr(wizard, 'source_weapon', None)
            source_weapon_id = source_weapon_id.weapon_id if source_weapon_id else None
        else:
            creation_mode = "duplicate"
            source_weapon_id = getattr(wizard, 'source_weapon', None)
            source_weapon_id = source_weapon_id.weapon_id if source_weapon_id else None

        # Build requirements
        requirements = WeaponRequirements(
            strength=req_page.strength_spin.value(),
            dexterity=req_page.dexterity_spin.value(),
            intelligence=req_page.intelligence_spin.value(),
            level=req_page.level_spin.value()
        )

        # Build weapon data
        weapon_data = WeaponCreationData(
            # Step 1: Mode & ID
            weapon_id=wizard.weapon_id,
            creation_mode=creation_mode,
            source_weapon_id=source_weapon_id,

            # Step 2: Basic Properties
            weapon_name=basic_page.weapon_name_edit.text(),
            weapon_type_id=basic_page.weapon_type_combo.currentIndex() + 1,  # Adjust for 0-based index
            weapon_type_name=basic_page.weapon_type_combo.currentText(),
            weapon_material_id=basic_page.weapon_material_combo.currentIndex() + 1,
            weapon_material_name=basic_page.weapon_material_combo.currentText(),
            hands=WeaponHands(basic_page.hands_combo.currentText()),
            damage_category=DamageCategory(basic_page.damage_category_combo.currentText()),
            description=basic_page.description_edit.toPlainText(),

            # Step 3: Combat Stats
            min_damage=combat_page.min_damage_spin.value(),
            max_damage=combat_page.max_damage_spin.value(),
            damage_type=DamageType(combat_page.damage_type_combo.currentText()),
            attack_speed=combat_page.attack_speed_spin.value(),
            min_range=combat_page.min_range_spin.value(),
            max_range=combat_page.max_range_spin.value(),
            attack_arc=combat_page.attack_arc_spin.value(),
            critical_chance=combat_page.crit_chance_spin.value(),
            armor_penetration=combat_page.armor_pen_spin.value(),
            knockback_chance=combat_page.knockback_spin.value(),

            # Step 4: Requirements & Value
            requirements=requirements,
            sell_value=req_page.sell_value_spin.value(),
            buy_value=req_page.buy_value_spin.value(),
            rarity=Rarity(req_page.rarity_combo.currentText()),
            effects=[],  # TODO: Populate from effects widget when implemented

            # Step 5: Visual & Audio (enhanced with sound selection)
            icon_handle="",
            hit_sound=visual_page.current_hit_sound if hasattr(visual_page, 'current_hit_sound') else 'battle_hit_1hsword',
            miss_sound=visual_page.current_miss_sound if hasattr(visual_page, 'current_miss_sound') else 'battle_miss_sword',
            equip_sound=visual_page.current_equip_sound if hasattr(visual_page, 'current_equip_sound') else '',
            model_file="",
            trail_effect="",
            impact_effect=""
        )

        return weapon_data

    def format_weapon_summary(self, weapon: WeaponCreationData) -> str:
        """Format weapon data as HTML summary"""
        dps = weapon.calculate_dps()
        balance = weapon.get_balance_rating()

        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">{weapon.weapon_name}</h2>

            <h3 style="color: #34495e;">Basic Information</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>ID:</b></td><td>{weapon.weapon_id}</td></tr>
                <tr><td><b>Type:</b></td><td>{weapon.weapon_type_name} ({weapon.hands.value})</td></tr>
                <tr><td><b>Material:</b></td><td>{weapon.weapon_material_name}</td></tr>
                <tr><td><b>Category:</b></td><td>{weapon.damage_category.value.capitalize()}</td></tr>
                <tr><td><b>Rarity:</b></td><td style="color: {self._get_rarity_color(weapon.rarity)};">
                    {weapon.rarity.value.capitalize()}</td></tr>
            </table>

            <h3 style="color: #34495e;">Combat Stats</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Damage:</b></td><td>{weapon.min_damage} - {weapon.max_damage}
                    ({weapon.damage_type.value})</td></tr>
                <tr><td><b>Attack Speed:</b></td><td>{weapon.attack_speed}
                    ({self._speed_rating(weapon.attack_speed)})</td></tr>
                <tr><td><b>Range:</b></td><td>{weapon.min_range} - {weapon.max_range}</td></tr>
                <tr><td><b>Attack Arc:</b></td><td>{weapon.attack_arc}°</td></tr>
                <tr><td><b>DPS:</b></td><td style="color: #e74c3c; font-weight: bold;">
                    {dps:.1f}</td></tr>
            </table>

            <h3 style="color: #34495e;">Special Properties</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Critical Chance:</b></td><td>{weapon.critical_chance}%</td></tr>
                <tr><td><b>Armor Penetration:</b></td><td>{weapon.armor_penetration}%</td></tr>
                <tr><td><b>Knockback Chance:</b></td><td>{weapon.knockback_chance}%</td></tr>
            </table>

            <h3 style="color: #34495e;">Requirements</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Strength:</b></td><td>{weapon.requirements.strength}</td></tr>
                <tr><td><b>Dexterity:</b></td><td>{weapon.requirements.dexterity}</td></tr>
                <tr><td><b>Intelligence:</b></td><td>{weapon.requirements.intelligence}</td></tr>
                <tr><td><b>Level:</b></td><td>{weapon.requirements.level}</td></tr>
            </table>

            <h3 style="color: #34495e;">Economy</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Sell Value:</b></td><td>{weapon.sell_value} gold</td></tr>
                <tr><td><b>Buy Value:</b></td><td>{weapon.buy_value} gold</td></tr>
            </table>

            <h3 style="color: #34495e;">Balance Assessment</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Balance Rating:</b></td><td>{balance} / 100</td></tr>
                <tr><td><b>Assessment:</b></td><td>{self._balance_assessment(balance)}</td></tr>
            </table>
        </body>
        </html>
        """

        return html

    def format_validation(self, errors: list[str], warnings: list[str]) -> str:
        """Format validation results as HTML"""
        if not errors and not warnings:
            html = """
            <html>
            <body style="font-family: Arial, sans-serif;">
                <p style="color: #27ae60; font-size: 14pt; font-weight: bold;">
                    ✓ Weapon is valid and ready for export!
                </p>
            </body>
            </html>
            """
            return html

        html = "<html><body style='font-family: Arial, sans-serif;'>"

        if errors:
            html += "<h3 style='color: #e74c3c;'>❌ Errors (must fix before export):</h3><ul>"
            for error in errors:
                html += f"<li style='color: #e74c3c;'>{error}</li>"
            html += "</ul>"

        if warnings:
            html += "<h3 style='color: #f39c12;'>⚠️ Warnings (review recommended):</h3><ul>"
            for warning in warnings:
                html += f"<li style='color: #f39c12;'>{warning}</li>"
            html += "</ul>"

        html += "</body></html>"
        return html

    def _get_rarity_color(self, rarity: Rarity) -> str:
        """Get color code for rarity"""
        colors = {
            Rarity.COMMON: "#95a5a6",
            Rarity.UNCOMMON: "#2ecc71",
            Rarity.RARE: "#3498db",
            Rarity.EPIC: "#9b59b6",
            Rarity.LEGENDARY: "#f39c12"
        }
        return colors.get(rarity, "#000000")

    def _speed_rating(self, speed: int) -> str:
        """Convert speed value to rating"""
        if speed < 50:
            return "Very Fast"
        elif speed < 80:
            return "Fast"
        elif speed < 120:
            return "Normal"
        elif speed < 160:
            return "Slow"
        else:
            return "Very Slow"

    def _balance_assessment(self, rating: int) -> str:
        """Get balance assessment text"""
        if rating < 20:
            return "Underpowered"
        elif rating < 40:
            return "Weak"
        elif rating < 60:
            return "Balanced"
        elif rating < 80:
            return "Strong"
        else:
            return "Overpowered"
