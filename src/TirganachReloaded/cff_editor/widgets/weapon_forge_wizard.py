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

from ..exporters.weapon_loader import WeaponLoader
from ..models.weapon_creation_data import (
    DamageCategory,
    DamageType,
    Rarity,
    WeaponHands,
)
from ..shared.id_manager import ContentType, IDManager
from .weapon_browser_dialog import WeaponBrowserDialog


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
        if result == QDialog.DialogCode.Rejected and self.weapon_id:
            self.id_manager.release_id(ContentType.WEAPON, self.weapon_id)
        super().done(result)


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
                    # Load the weapon using WeaponLoader
                    self.selected_weapon_data = self.weapon_loader.load_weapon(
                        weapon_dict["item_id"]
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
            self.str_spin.setValue(weapon.requirements.strength)
            self.dex_spin.setValue(weapon.requirements.dexterity)
            self.int_spin.setValue(weapon.requirements.intelligence)
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
        layout.addRow("Hit Sound:", QComboBox())
        layout.addRow("Miss Sound:", QComboBox())
        layout.addRow("Equip Sound:", QComboBox())
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
        layout.addWidget(QLabel("Weapon Summary:"))
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        layout.addWidget(self.summary_text)

        layout.addWidget(QLabel("Validation Results:"))
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        layout.addWidget(self.validation_text)

        self.setLayout(layout)

    def initializePage(self):
        # In a real implementation, we would gather all data from previous pages
        # and populate the summary and validation text edits.
        self.summary_text.setText("This is a placeholder for the weapon summary.")
        self.validation_text.setText(
            "This is a placeholder for the validation results."
        )
