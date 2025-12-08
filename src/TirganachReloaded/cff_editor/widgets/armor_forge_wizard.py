"""
GUI-based Armor Forge Wizard - Enhanced with ID Management and Better UX
"""

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
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QTabWidget
)
from PySide6.QtCore import QDir
import json
from pathlib import Path
from datetime import datetime
import os

from ..systems.armor_system.armor_model import Armor, ARMOR_TYPES, MATERIAL_CATEGORIES, QUALITY_TIERS, CLASS_RESTRICTIONS, SLOT_HEAD, SLOT_CHEST, SLOT_LEGS, SLOT_FEET, SLOT_RIGHT_RING, SLOT_LEFT_RING, SLOT_LEFT_HAND
from ..shared.id_manager import ContentType, IDManager


class ArmorForgeWizard(QWizard):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.armor_data = None
        self.armor_id = None

        self.setWindowTitle("Armor Forge Wizard")

        self.addPage(ModeSelectionPage(self.id_manager))
        self.addPage(BasicPropertiesPage())
        self.addPage(CoreStatsPage())
        self.addPage(ResistanceDefensePage())
        self.addPage(SpeedMobilityPage())
        self.addPage(VisualPropertiesPage())
        self.addPage(AdvancedFeaturesPage())
        self.addPage(ReviewExportPage())

    def done(self, result):
        if result == QDialog.DialogCode.Accepted:
            # Export armor data when user clicks Finish
            if self.armor_data:
                success = self.export_armor()
                if not success:
                    # Export failed, don't close wizard yet
                    return
        elif result == QDialog.DialogCode.Rejected and self.armor_id:
            # Release ID if cancelled
            self.id_manager.release_id(ContentType.ARMOR, self.armor_id)
        super().done(result)

    def export_armor(self) -> bool:
        """Export armor to JSON (and eventually CFF)"""
        try:
            # For now, we only support JSON export
            return self.export_to_json()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export armor:\n{str(e)}"
            )
            return False

    def export_to_json(self) -> bool:
        """Export armor data to JSON file"""
        try:
            # Create armors directory if it doesn't exist
            armors_dir = Path("custom_armors")
            armors_dir.mkdir(exist_ok=True)

            # Generate filename from armor name
            safe_name = "".join(
                c if c.isalnum() or c in (' ', '-', '_') else '_'
                for c in self.armor_data.name
            )
            safe_name = safe_name.replace(' ', '_').lower()
            filename = f"armor_{self.armor_data.id}_{safe_name}.json"
            filepath = armors_dir / filename

            # Add metadata
            self.armor_data.created_date = datetime.now().isoformat()
            self.armor_data.modified_date = datetime.now().isoformat()
            self.armor_data.author = "CFF Editor - Armor Forge"

            # Convert armor data to dict
            armor_dict = {
                "id": self.armor_data.id,
                "name": self.armor_data.name,
                "display_name": self.armor_data.display_name,
                "description": self.armor_data.description,
                
                # Classification
                "slot": self.armor_data.slot,
                "armor_type": self.armor_data.armor_type,
                "material": self.armor_data.material,
                "tier": self.armor_data.tier,
                "level_requirement": self.armor_data.level_requirement,
                "class_restriction": self.armor_data.class_restriction,
                
                # Core stats
                "strength": self.armor_data.strength,
                "stamina": self.armor_data.stamina,
                "agility": self.armor_data.agility,
                "dexterity": self.armor_data.dexterity,
                "intelligence": self.armor_data.intelligence,
                "wisdom": self.armor_data.wisdom,
                "charisma": self.armor_data.charisma,
                "health": self.armor_data.health,
                "mana": self.armor_data.mana,
                "armor_value": self.armor_data.armor_value,
                
                # Resists
                "resist_fire": self.armor_data.resist_fire,
                "resist_ice": self.armor_data.resist_ice,
                "resist_black": self.armor_data.resist_black,
                "resist_mind": self.armor_data.resist_mind,
                "physical_resist": self.armor_data.physical_resist,
                "magic_resist": self.armor_data.magic_resist,
                "critical_resist": self.armor_data.critical_resist,
                
                # Speed modifiers
                "run_speed": self.armor_data.run_speed,
                "fight_speed": self.armor_data.fight_speed,
                "cast_speed": self.armor_data.cast_speed,
                "stealth_bonus": self.armor_data.stealth_bonus,
                "swimming_speed": self.armor_data.swimming_speed,
                "jump_height": self.armor_data.jump_height,
                
                # Visual properties
                "icon_id": self.armor_data.icon_id,
                "model_ref": self.armor_data.model_ref,
                "texture": self.armor_data.texture,
                "normal_map": self.armor_data.normal_map,
                
                # Advanced features
                "set_id": self.armor_data.set_id,
                "set_bonus": self.armor_data.set_bonus,
                "special_abilities": self.armor_data.special_abilities,
                "enchantment_slots": self.armor_data.enchantment_slots,
                "stat_balance_rating": self.armor_data.stat_balance_rating,
                
                # Metadata
                "created_date": self.armor_data.created_date,
                "modified_date": self.armor_data.modified_date,
                "author": self.armor_data.author
            }

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(armor_dict, f, indent=2, ensure_ascii=False)

            # Show success message
            QMessageBox.information(
                self,
                "Export Successful",
                f"Armor exported successfully!\n\n"
                f"File: {filepath}\n"
                f"Armor ID: {self.armor_data.id}\n"
                f"Name: {self.armor_data.name}\n\n"
                f"Balance Rating: {self.armor_data.stat_balance_rating:.2f}%"
            )

            return True

        except Exception as e:
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export armor to JSON:\n{str(e)}"
            )
            return False


class ModeSelectionPage(QWizardPage):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.selected_armor_data = None
        self.setTitle("Mode Selection & ID Assignment")
        self.setSubTitle("Choose how to create your armor and assign a unique ID.")

        layout = QVBoxLayout()

        # Creation Mode
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()
        self.new_armor_radio = QRadioButton("Create New Armor (blank slate)")
        self.edit_armor_radio = QRadioButton("Edit Existing Armor")
        self.duplicate_armor_radio = QRadioButton("Duplicate & Modify (copy existing, new ID)")
        self.new_armor_radio.setChecked(True)
        mode_layout.addWidget(self.new_armor_radio)
        mode_layout.addWidget(self.edit_armor_radio)
        mode_layout.addWidget(self.duplicate_armor_radio)

        # Browse button for edit/duplicate modes
        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse Armors...")
        self.browse_button.clicked.connect(self.browse_armors)
        self.browse_button.setEnabled(False)
        browse_layout.addWidget(self.browse_button)
        browse_layout.addStretch()
        mode_layout.addLayout(browse_layout)

        # Selected armor display
        self.selected_armor_label = QLabel("No armor selected")
        self.selected_armor_label.setStyleSheet("color: gray; font-style: italic;")
        mode_layout.addWidget(self.selected_armor_label)

        # Enable browse button when edit/duplicate modes are selected
        self.edit_armor_radio.toggled.connect(self.on_mode_changed)
        self.duplicate_armor_radio.toggled.connect(self.on_mode_changed)

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
        self.manual_id_spin.setRange(20000, 29999)  # Armor range
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(self.manual_id_spin.setEnabled)
        id_layout.addWidget(self.manual_id_spin)

        available_count = self.id_manager.get_available_count(ContentType.ARMOR)
        id_status_label = QLabel(f"{available_count} available in range 20000-29999")
        id_layout.addWidget(id_status_label)

        id_group.setLayout(id_layout)
        layout.addWidget(id_group)

        self.setLayout(layout)

    def on_mode_changed(self):
        """Enable/disable browse button based on mode selection"""
        is_edit_or_duplicate = (
            self.edit_armor_radio.isChecked()
            or self.duplicate_armor_radio.isChecked()
        )
        self.browse_button.setEnabled(is_edit_or_duplicate)

        # Clear selection if switching back to new mode
        if not is_edit_or_duplicate:
            self.selected_armor_data = None
            self.selected_armor_label.setText("No armor selected")
            self.selected_armor_label.setStyleSheet("color: gray; font-style: italic;")

    def browse_armors(self):
        """Open enhanced armor browser dialog"""
        from .enhanced_armor_browser import EnhancedArmorBrowser
        dialog = EnhancedArmorBrowser(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_data = dialog.get_selected_armor_data()
            if selected_data:
                from ..systems.armor_system.armor_model import Armor
                # Check if the returned data is already an Armor object or a dict
                if isinstance(selected_data, Armor):
                    # It's already an Armor object
                    self.selected_armor_data = selected_data
                    # Update the display label
                    self.selected_armor_label.setText(
                        f"Selected: {self.selected_armor_data.name} (ID: {self.selected_armor_data.id})"
                    )
                else:
                    # It's a dictionary, convert to an Armor object
                    self.selected_armor_data = Armor.from_dict(selected_data)
                    # Update the display label
                    self.selected_armor_label.setText(
                        f"Selected: {selected_data['name']} (ID: {selected_data['id']})"
                    )
                    
                self.selected_armor_label.setStyleSheet(
                    "color: green; font-weight: bold;"
                )
            else:
                self.selected_armor_label.setText("No armor selected")
                self.selected_armor_label.setStyleSheet("color: gray; font-style: italic;")

    def validatePage(self):
        """Validate the page before moving to next"""
        # Check if edit/duplicate mode requires an armor selection
        if (
            self.edit_armor_radio.isChecked()
            or self.duplicate_armor_radio.isChecked()
        ):
            if self.selected_armor_data is None:
                QMessageBox.warning(
                    self,
                    "No Armor Selected",
                    "Please select an armor to edit or duplicate by clicking 'Browse Armors...'",
                )
                return False

        # Store data in wizard for other pages to access
        wizard = self.wizard()

        # Determine creation mode
        if self.new_armor_radio.isChecked():
            wizard.creation_mode = "new"
            wizard.source_armor = None
        elif self.edit_armor_radio.isChecked():
            wizard.creation_mode = "edit"
            wizard.source_armor = self.selected_armor_data
        else:  # duplicate
            wizard.creation_mode = "duplicate"
            wizard.source_armor = self.selected_armor_data

        # Allocate or validate ID
        if self.auto_id_radio.isChecked():
            try:
                wizard.armor_id = self.id_manager.allocate_id(ContentType.ARMOR)
            except ValueError as e:
                QMessageBox.critical(self, "ID Allocation Error", str(e))
                return False
        else:
            requested_id = self.manual_id_spin.value()
            if not self.id_manager.is_valid_id(ContentType.ARMOR, requested_id):
                QMessageBox.warning(
                    self,
                    "Invalid ID",
                    f"ID {requested_id} is outside the valid range (20000-29999)",
                )
                return False

            if self.id_manager.is_id_used(ContentType.ARMOR, requested_id):
                QMessageBox.warning(
                    self,
                    "ID Already In Use",
                    f"ID {requested_id} is already allocated. Please choose another ID.",
                )
                return False

            try:
                wizard.armor_id = self.id_manager.allocate_id(
                    ContentType.ARMOR, requested_id
                )
            except ValueError as e:
                QMessageBox.critical(self, "ID Allocation Error", str(e))
                return False

        return True


class BasicPropertiesPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Basic Properties & Classification")
        self.setSubTitle("Define the fundamental characteristics of your armor.")

        layout = QFormLayout()
        
        # Naming & Identity
        self.armor_name_edit = QLineEdit()
        layout.addRow("Armor Name:", self.armor_name_edit)

        self.display_name_edit = QLineEdit()
        layout.addRow("Display Name (Tooltip):", self.display_name_edit)

        # Classification
        self.slot_combo = QComboBox()
        slot_options = [
            (SLOT_HEAD, "Head/Helmet"),
            (SLOT_CHEST, "Chest/Armor"),
            (SLOT_LEGS, "Legs/Pants"),
            (SLOT_FEET, "Boots/Feet"),
            (SLOT_RIGHT_RING, "Right Ring"),
            (SLOT_LEFT_RING, "Left Ring"),
            (SLOT_LEFT_HAND, "Left Hand/Shield")
        ]
        for slot_id, slot_name in slot_options:
            self.slot_combo.addItem(slot_name, slot_id)
        layout.addRow("Equipment Slot:", self.slot_combo)

        self.armor_type_combo = QComboBox()
        self.armor_type_combo.addItems(ARMOR_TYPES)
        layout.addRow("Armor Type:", self.armor_type_combo)

        self.material_combo = QComboBox()
        self.material_combo.addItems(MATERIAL_CATEGORIES)
        layout.addRow("Material Category:", self.material_combo)

        self.tier_combo = QComboBox()
        self.tier_combo.addItems(QUALITY_TIERS)
        layout.addRow("Quality Tier:", self.tier_combo)

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(1)
        layout.addRow("Level Requirement:", self.level_spin)

        self.class_restriction_combo = QComboBox()
        self.class_restriction_combo.addItems(CLASS_RESTRICTIONS)
        layout.addRow("Class Restriction:", self.class_restriction_combo)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        layout.addRow("Description (Flavor Text):", self.description_edit)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source armor if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_armor") and wizard.source_armor is not None:
            armor = wizard.source_armor

            # Populate basic properties from source armor
            self.armor_name_edit.setText(armor.name)
            self.display_name_edit.setText(armor.display_name)

            # Set slot - find matching slot in combo box
            for i in range(self.slot_combo.count()):
                if self.slot_combo.itemData(i) == armor.slot:
                    self.slot_combo.setCurrentIndex(i)
                    break

            # Set armor type
            index = self.armor_type_combo.findText(armor.armor_type)
            if index >= 0:
                self.armor_type_combo.setCurrentIndex(index)

            # Set material
            index = self.material_combo.findText(armor.material)
            if index >= 0:
                self.material_combo.setCurrentIndex(index)

            # Set tier
            index = self.tier_combo.findText(armor.tier)
            if index >= 0:
                self.tier_combo.setCurrentIndex(index)

            # Set level requirement
            self.level_spin.setValue(armor.level_requirement)

            # Set class restriction
            index = self.class_restriction_combo.findText(armor.class_restriction)
            if index >= 0:
                self.class_restriction_combo.setCurrentIndex(index)

            # Set description
            self.description_edit.setPlainText(armor.description)


class CoreStatsPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Core Stat Bonuses")
        self.setSubTitle("Define the stat bonuses and core defensive values for your armor.")

        layout = QFormLayout()

        # Primary stats
        self.strength_spin = QSpinBox()
        self.strength_spin.setRange(-100, 1000)
        layout.addRow("Strength Bonus:", self.strength_spin)

        self.stamina_spin = QSpinBox()
        self.stamina_spin.setRange(-100, 1000)
        layout.addRow("Stamina Bonus:", self.stamina_spin)

        self.agility_spin = QSpinBox()
        self.agility_spin.setRange(-100, 1000)
        layout.addRow("Agility Bonus:", self.agility_spin)

        self.dexterity_spin = QSpinBox()
        self.dexterity_spin.setRange(-100, 1000)
        layout.addRow("Dexterity Bonus:", self.dexterity_spin)

        self.intelligence_spin = QSpinBox()
        self.intelligence_spin.setRange(-100, 1000)
        layout.addRow("Intelligence Bonus:", self.intelligence_spin)

        self.wisdom_spin = QSpinBox()
        self.wisdom_spin.setRange(-100, 1000)
        layout.addRow("Wisdom Bonus:", self.wisdom_spin)

        self.charisma_spin = QSpinBox()
        self.charisma_spin.setRange(-100, 1000)
        layout.addRow("Charisma Bonus:", self.charisma_spin)

        # Derived stats
        self.health_spin = QSpinBox()
        self.health_spin.setRange(-1000, 10000)
        layout.addRow("Health Bonus:", self.health_spin)

        self.mana_spin = QSpinBox()
        self.mana_spin.setRange(-1000, 10000)
        layout.addRow("Mana Bonus:", self.mana_spin)

        self.armor_value_spin = QSpinBox()
        self.armor_value_spin.setRange(0, 1000)
        layout.addRow("Base Armor Value:", self.armor_value_spin)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source armor if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_armor") and wizard.source_armor is not None:
            armor = wizard.source_armor

            # Populate core stats from source armor
            self.strength_spin.setValue(armor.strength)
            self.stamina_spin.setValue(armor.stamina)
            self.agility_spin.setValue(armor.agility)
            self.dexterity_spin.setValue(armor.dexterity)
            self.intelligence_spin.setValue(armor.intelligence)
            self.wisdom_spin.setValue(armor.wisdom)
            self.charisma_spin.setValue(armor.charisma)
            self.health_spin.setValue(armor.health)
            self.mana_spin.setValue(armor.mana)
            self.armor_value_spin.setValue(armor.armor_value)


class ResistanceDefensePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Resistance & Defense Systems")
        self.setSubTitle("Configure elemental resistances and defensive properties.")

        layout = QFormLayout()

        # Elemental resistances
        self.fire_resist_spin = QSpinBox()
        self.fire_resist_spin.setRange(-100, 100)
        self.fire_resist_spin.setSuffix(" %")
        layout.addRow("Fire Resistance:", self.fire_resist_spin)

        self.ice_resist_spin = QSpinBox()
        self.ice_resist_spin.setRange(-100, 100)
        self.ice_resist_spin.setSuffix(" %")
        layout.addRow("Ice Resistance:", self.ice_resist_spin)

        self.black_resist_spin = QSpinBox()
        self.black_resist_spin.setRange(-100, 100)
        self.black_resist_spin.setSuffix(" %")
        layout.addRow("Black Magic Resistance:", self.black_resist_spin)

        self.mind_resist_spin = QSpinBox()
        self.mind_resist_spin.setRange(-100, 100)
        self.mind_resist_spin.setSuffix(" %")
        layout.addRow("Mind Magic Resistance:", self.mind_resist_spin)

        # Defense mechanics
        self.physical_resist_spin = QSpinBox()
        self.physical_resist_spin.setRange(-100, 100)
        self.physical_resist_spin.setSuffix(" %")
        layout.addRow("Physical Damage Reduction:", self.physical_resist_spin)

        self.magic_resist_spin = QSpinBox()
        self.magic_resist_spin.setRange(-100, 100)
        self.magic_resist_spin.setSuffix(" %")
        layout.addRow("Magic Damage Reduction:", self.magic_resist_spin)

        self.critical_resist_spin = QSpinBox()
        self.critical_resist_spin.setRange(-100, 100)
        self.critical_resist_spin.setSuffix(" %")
        layout.addRow("Critical Hit Reduction:", self.critical_resist_spin)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source armor if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_armor") and wizard.source_armor is not None:
            armor = wizard.source_armor

            # Populate resistances from source armor
            self.fire_resist_spin.setValue(armor.resist_fire)
            self.ice_resist_spin.setValue(armor.resist_ice)
            self.black_resist_spin.setValue(armor.resist_black)
            self.mind_resist_spin.setValue(armor.resist_mind)
            self.physical_resist_spin.setValue(armor.physical_resist)
            self.magic_resist_spin.setValue(armor.magic_resist)
            self.critical_resist_spin.setValue(armor.critical_resist)


class SpeedMobilityPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Speed & Mobility Modifiers")
        self.setSubTitle("Configure how the armor affects movement and mobility.")

        layout = QFormLayout()

        # Speed modifiers
        self.run_speed_spin = QSpinBox()
        self.run_speed_spin.setRange(-100, 100)
        self.run_speed_spin.setSuffix(" %")
        layout.addRow("Run Speed Modifier:", self.run_speed_spin)

        self.fight_speed_spin = QSpinBox()
        self.fight_speed_spin.setRange(-100, 100)
        self.fight_speed_spin.setSuffix(" %")
        layout.addRow("Fight Speed Modifier:", self.fight_speed_spin)

        self.cast_speed_spin = QSpinBox()
        self.cast_speed_spin.setRange(-100, 100)
        self.cast_speed_spin.setSuffix(" %")
        layout.addRow("Cast Speed Modifier:", self.cast_speed_spin)

        # Special movement bonuses
        self.stealth_spin = QSpinBox()
        self.stealth_spin.setRange(-100, 100)
        layout.addRow("Stealth Bonus:", self.stealth_spin)

        self.swimming_speed_spin = QSpinBox()
        self.swimming_speed_spin.setRange(-100, 100)
        layout.addRow("Swimming Speed:", self.swimming_speed_spin)

        self.jump_height_spin = QSpinBox()
        self.jump_height_spin.setRange(-100, 100)
        layout.addRow("Jump Height Bonus:", self.jump_height_spin)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source armor if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_armor") and wizard.source_armor is not None:
            armor = wizard.source_armor

            # Populate speed modifiers from source armor
            self.run_speed_spin.setValue(armor.run_speed)
            self.fight_speed_spin.setValue(armor.fight_speed)
            self.cast_speed_spin.setValue(armor.cast_speed)
            self.stealth_spin.setValue(armor.stealth_bonus)
            self.swimming_speed_spin.setValue(armor.swimming_speed)
            self.jump_height_spin.setValue(armor.jump_height)


class VisualPropertiesPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Visual Properties")
        self.setSubTitle("Configure the visual appearance of your armor.")

        layout = QFormLayout()

        self.icon_id_spin = QSpinBox()
        self.icon_id_spin.setRange(0, 99999)
        layout.addRow("Icon ID:", self.icon_id_spin)

        self.model_ref_edit = QLineEdit()
        layout.addRow("3D Model Reference:", self.model_ref_edit)

        self.texture_edit = QLineEdit()
        layout.addRow("Texture File:", self.texture_edit)

        self.normal_map_edit = QLineEdit()
        layout.addRow("Normal Map File:", self.normal_map_edit)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source armor if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_armor") and wizard.source_armor is not None:
            armor = wizard.source_armor

            # Populate visual properties from source armor
            self.icon_id_spin.setValue(armor.icon_id)
            self.model_ref_edit.setText(armor.model_ref)
            self.texture_edit.setText(armor.texture)
            self.normal_map_edit.setText(armor.normal_map)


class AdvancedFeaturesPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Advanced Features")
        self.setSubTitle("Configure advanced features like sets, enchantments, and special abilities.")

        layout = QVBoxLayout()

        # Item set assignment
        set_group = QGroupBox("Item Set Assignment")
        set_layout = QFormLayout()
        
        self.set_id_spin = QSpinBox()
        self.set_id_spin.setRange(0, 99999)
        set_layout.addRow("Set ID:", self.set_id_spin)
        
        self.set_bonus_edit = QTextEdit()
        self.set_bonus_edit.setMaximumHeight(100)
        set_layout.addRow("Set Bonus (JSON format):", self.set_bonus_edit)
        
        set_group.setLayout(set_layout)
        layout.addWidget(set_group)

        # Enchantments
        enchant_group = QGroupBox("Enchantments & Special Abilities")
        enchant_layout = QFormLayout()
        
        self.enchant_slots_spin = QSpinBox()
        self.enchant_slots_spin.setRange(0, 20)
        enchant_layout.addRow("Enchantment Slots:", self.enchant_slots_spin)
        
        self.special_abilities_edit = QTextEdit()
        self.special_abilities_edit.setMaximumHeight(100)
        enchant_layout.addRow("Special Abilities (JSON format):", self.special_abilities_edit)
        
        enchant_group.setLayout(enchant_layout)
        layout.addWidget(enchant_group)

        self.setLayout(layout)

    def initializePage(self):
        """Populate fields from source armor if in edit/duplicate mode"""
        wizard = self.wizard()

        if hasattr(wizard, "source_armor") and wizard.source_armor is not None:
            armor = wizard.source_armor

            # Populate advanced features from source armor
            self.set_id_spin.setValue(armor.set_id or 0)
            self.set_bonus_edit.setPlainText(json.dumps(armor.set_bonus, indent=2))
            self.enchant_slots_spin.setValue(armor.enchantment_slots)
            self.special_abilities_edit.setPlainText(json.dumps(armor.special_abilities, indent=2))


class ReviewExportPage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Review & Export")
        self.setSubTitle("Review the final armor and export it to the game data.")

        layout = QVBoxLayout()

        # Armor Summary Section
        layout.addWidget(QLabel("Armor Summary:"))
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
        self.export_json_radio.setChecked(True)

        export_layout.addWidget(self.export_json_radio)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        self.setLayout(layout)

    def initializePage(self):
        """Gather all armor data, display summary and validation results"""
        wizard = self.wizard()

        # Build armor data from all pages
        armor_data = self.build_armor_data_from_wizard()

        # Store in wizard for export
        wizard.armor_data = armor_data

        # Display summary
        summary_html = self.format_armor_summary(armor_data)
        self.summary_text.setHtml(summary_html)

        # Run validation and display results
        # (For now, we'll use a simple validation)
        errors, warnings = self.validate_armor(armor_data)
        validation_html = self.format_validation(errors, warnings)
        self.validation_text.setHtml(validation_html)

    def build_armor_data_from_wizard(self) -> Armor:
        """Gather data from all wizard pages and build Armor object"""
        wizard = self.wizard()

        # Get references to all pages
        mode_page = wizard.page(0)  # ModeSelectionPage
        basic_page = wizard.page(1)  # BasicPropertiesPage
        core_stats_page = wizard.page(2)  # CoreStatsPage
        resist_page = wizard.page(3)  # ResistanceDefensePage
        speed_page = wizard.page(4)  # SpeedMobilityPage
        visual_page = wizard.page(5)  # VisualPropertiesPage
        advanced_page = wizard.page(6)  # AdvancedFeaturesPage

        # Determine creation mode
        if mode_page.new_armor_radio.isChecked():
            creation_mode = "new"
            source_armor_id = None
        elif mode_page.edit_armor_radio.isChecked():
            creation_mode = "edit"
            source_armor_id = getattr(wizard, 'source_armor', None)
            source_armor_id = source_armor_id.id if source_armor_id else None
        else:
            creation_mode = "duplicate"
            source_armor_id = getattr(wizard, 'source_armor', None)
            source_armor_id = source_armor_id.id if source_armor_id else None

        # Build armor data
        armor_data = Armor(
            # Set the ID
            armor_id=wizard.armor_id
        )

        # Basic Properties
        armor_data.name = basic_page.armor_name_edit.text()
        armor_data.display_name = basic_page.display_name_edit.text()
        armor_data.description = basic_page.description_edit.toPlainText()
        armor_data.slot = basic_page.slot_combo.itemData(basic_page.slot_combo.currentIndex())
        armor_data.armor_type = basic_page.armor_type_combo.currentText()
        armor_data.material = basic_page.material_combo.currentText()
        armor_data.tier = basic_page.tier_combo.currentText()
        armor_data.level_requirement = basic_page.level_spin.value()
        armor_data.class_restriction = basic_page.class_restriction_combo.currentText()

        # Core Stats
        armor_data.strength = core_stats_page.strength_spin.value()
        armor_data.stamina = core_stats_page.stamina_spin.value()
        armor_data.agility = core_stats_page.agility_spin.value()
        armor_data.dexterity = core_stats_page.dexterity_spin.value()
        armor_data.intelligence = core_stats_page.intelligence_spin.value()
        armor_data.wisdom = core_stats_page.wisdom_spin.value()
        armor_data.charisma = core_stats_page.charisma_spin.value()
        armor_data.health = core_stats_page.health_spin.value()
        armor_data.mana = core_stats_page.mana_spin.value()
        armor_data.armor_value = core_stats_page.armor_value_spin.value()

        # Resistances
        armor_data.resist_fire = resist_page.fire_resist_spin.value()
        armor_data.resist_ice = resist_page.ice_resist_spin.value()
        armor_data.resist_black = resist_page.black_resist_spin.value()
        armor_data.resist_mind = resist_page.mind_resist_spin.value()
        armor_data.physical_resist = resist_page.physical_resist_spin.value()
        armor_data.magic_resist = resist_page.magic_resist_spin.value()
        armor_data.critical_resist = resist_page.critical_resist_spin.value()

        # Speed & Mobility
        armor_data.run_speed = speed_page.run_speed_spin.value()
        armor_data.fight_speed = speed_page.fight_speed_spin.value()
        armor_data.cast_speed = speed_page.cast_speed_spin.value()
        armor_data.stealth_bonus = speed_page.stealth_spin.value()
        armor_data.swimming_speed = speed_page.swimming_speed_spin.value()
        armor_data.jump_height = speed_page.jump_height_spin.value()

        # Visual Properties
        armor_data.icon_id = visual_page.icon_id_spin.value()
        armor_data.model_ref = visual_page.model_ref_edit.text()
        armor_data.texture = visual_page.texture_edit.text()
        armor_data.normal_map = visual_page.normal_map_edit.text()

        # Advanced Features
        set_id = advanced_page.set_id_spin.value()
        armor_data.set_id = set_id if set_id != 0 else None
        
        try:
            armor_data.set_bonus = json.loads(advanced_page.set_bonus_edit.toPlainText()) or {}
        except json.JSONDecodeError:
            armor_data.set_bonus = {}
            
        armor_data.enchantment_slots = advanced_page.enchant_slots_spin.value()
        
        try:
            armor_data.special_abilities = json.loads(advanced_page.special_abilities_edit.toPlainText()) or []
        except json.JSONDecodeError:
            armor_data.special_abilities = []

        # Calculate and set balance rating
        total_positive_stats = (
            armor_data.strength + armor_data.stamina + armor_data.agility + armor_data.dexterity +
            armor_data.intelligence + armor_data.wisdom + armor_data.charisma +
            armor_data.health + armor_data.mana + armor_data.armor_value +
            max(0, armor_data.resist_fire) + max(0, armor_data.resist_ice) +
            max(0, armor_data.resist_black) + max(0, armor_data.resist_mind) +
            max(0, armor_data.physical_resist) + max(0, armor_data.magic_resist) +
            max(0, armor_data.run_speed) + max(0, armor_data.fight_speed) + max(0, armor_data.cast_speed)
        )

        total_negative_stats = (
            abs(min(0, armor_data.resist_fire)) + abs(min(0, armor_data.resist_ice)) +
            abs(min(0, armor_data.resist_black)) + abs(min(0, armor_data.resist_mind)) +
            abs(min(0, armor_data.physical_resist)) + abs(min(0, armor_data.magic_resist)) +
            abs(min(0, armor_data.run_speed)) + abs(min(0, armor_data.fight_speed)) + abs(min(0, armor_data.cast_speed))
        )

        # Calculate a rough balance (this is a very simplified calculation)
        max_possible_stats = 2000  # Arbitrary max for balance calculation
        total_stats = total_positive_stats + total_negative_stats
        balance_rating = min(100.0, (total_stats / max_possible_stats) * 100 if max_possible_stats > 0 else 0)
        armor_data.stat_balance_rating = round(balance_rating, 2)

        return armor_data

    def validate_armor(self, armor: Armor) -> tuple[list, list]:
        """Simple validation for armor data"""
        errors = []
        warnings = []

        # Check for basic issues
        if not armor.name.strip():
            errors.append("Armor must have a name")
        if len(armor.name) > 50:
            warnings.append("Armor name is quite long (consider shortening)")

        # Check stats are reasonable
        if armor.armor_value > 500:
            warnings.append("Armor value is very high - this may be overpowered")
        if abs(armor.run_speed) > 50:
            warnings.append("Movement speed modifier is very high")
        if abs(armor.resist_fire) > 50 or abs(armor.resist_ice) > 50:
            warnings.append("Elemental resistances are very high")

        # Check requirements are reasonable
        if armor.level_requirement > 50:
            warnings.append("Level requirement is very high")
        if armor.level_requirement < 1:
            errors.append("Level requirement must be at least 1")

        return errors, warnings

    def format_armor_summary(self, armor: Armor) -> str:
        """Format armor data as HTML summary"""
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: #2c3e50;">{armor.name}</h2>

            <h3 style="color: #34495e;">Basic Information</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>ID:</b></td><td>{armor.id}</td></tr>
                <tr><td><b>Slot:</b></td><td>{self._get_slot_name(armor.slot)}</td></tr>
                <tr><td><b>Type:</b></td><td>{armor.armor_type}</td></tr>
                <tr><td><b>Material:</b></td><td>{armor.material}</td></tr>
                <tr><td><b>Tier:</b></td><td style="color: {self._get_tier_color(armor.tier)};">
                    {armor.tier}</td></tr>
                <tr><td><b>Class Restriction:</b></td><td>{armor.class_restriction}</td></tr>
                <tr><td><b>Level Requirement:</b></td><td>{armor.level_requirement}</td></tr>
            </table>

            <h3 style="color: #34495e;">Core Stats</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Strength:</b></td><td>{armor.strength}</td></tr>
                <tr><td><b>Stamina:</b></td><td>{armor.stamina}</td></tr>
                <tr><td><b>Agility:</b></td><td>{armor.agility}</td></tr>
                <tr><td><b>Dexterity:</b></td><td>{armor.dexterity}</td></tr>
                <tr><td><b>Intelligence:</b></td><td>{armor.intelligence}</td></tr>
                <tr><td><b>Wisdom:</b></td><td>{armor.wisdom}</td></tr>
                <tr><td><b>Charisma:</b></td><td>{armor.charisma}</td></tr>
                <tr><td><b>Health Bonus:</b></td><td>{armor.health}</td></tr>
                <tr><td><b>Mana Bonus:</b></td><td>{armor.mana}</td></tr>
                <tr><td><b>Base Armor:</b></td><td>{armor.armor_value}</td></tr>
            </table>

            <h3 style="color: #34495e;">Resistances</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Fire:</b></td><td>{armor.resist_fire}%</td></tr>
                <tr><td><b>Ice:</b></td><td>{armor.resist_ice}%</td></tr>
                <tr><td><b>Black Magic:</b></td><td>{armor.resist_black}%</td></tr>
                <tr><td><b>Mind Magic:</b></td><td>{armor.resist_mind}%</td></tr>
                <tr><td><b>Physical DR:</b></td><td>{armor.physical_resist}%</td></tr>
                <tr><td><b>Magic DR:</b></td><td>{armor.magic_resist}%</td></tr>
                <tr><td><b>Critical DR:</b></td><td>{armor.critical_resist}%</td></tr>
            </table>

            <h3 style="color: #34495e;">Mobility Modifiers</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Run Speed:</b></td><td>{armor.run_speed}%</td></tr>
                <tr><td><b>Fight Speed:</b></td><td>{armor.fight_speed}%</td></tr>
                <tr><td><b>Cast Speed:</b></td><td>{armor.cast_speed}%</td></tr>
                <tr><td><b>Stealth Bonus:</b></td><td>{armor.stealth_bonus}</td></tr>
            </table>

            <h3 style="color: #34495e;">Advanced Features</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Set ID:</b></td><td>{armor.set_id if armor.set_id is not None else "None"}</td></tr>
                <tr><td><b>Enchantment Slots:</b></td><td>{armor.enchantment_slots}</td></tr>
                <tr><td><b>Special Abilities:</b></td><td>{len(armor.special_abilities)} abilities</td></tr>
            </table>

            <h3 style="color: #34495e;">Balance Assessment</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <tr><td><b>Balance Rating:</b></td><td>{armor.stat_balance_rating:.2f}%</td></tr>
                <tr><td><b>Assessment:</b></td><td>{self._balance_assessment(armor.stat_balance_rating)}</td></tr>
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
                    ✓ Armor is valid and ready for export!
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

    def _get_slot_name(self, slot_id):
        """Convert slot ID to name"""
        slot_map = {
            SLOT_HEAD: "Head/Helmet",
            SLOT_CHEST: "Chest/Armor",
            SLOT_LEGS: "Legs/Pants",
            SLOT_FEET: "Boots/Feet",
            SLOT_RIGHT_RING: "Right Ring",
            SLOT_LEFT_RING: "Left Ring",
            SLOT_LEFT_HAND: "Left Hand/Shield"
        }
        return slot_map.get(slot_id, "Unknown")

    def _get_tier_color(self, tier: str) -> str:
        """Get color code for tier"""
        colors = {
            "Common": "#95a5a6",
            "Uncommon": "#2ecc71",
            "Rare": "#3498db",
            "Epic": "#9b59b6",
            "Legendary": "#f39c12",
            "Unique": "#e74c3c"
        }
        return colors.get(tier, "#000000")

    def _balance_assessment(self, rating: float) -> str:
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


# This class has been replaced by EnhancedArmorBrowser
# from .enhanced_armor_browser import EnhancedArmorBrowser