"""
Armor Forge Wizard - 7-phase guided armor creation interface
"""

from PySide6.QtWidgets import (QWizard, QWizardPage, QLabel, QLineEdit, QComboBox,
                               QSpinBox, QDoubleSpinBox, QTextEdit, QVBoxLayout,
                               QHBoxLayout, QFormLayout, QGroupBox, QRadioButton,
                               QButtonGroup, QCheckBox, QListWidget, QPushButton,
                               QColorDialog, QMessageBox, QTableWidget, QTableWidgetItem,
                               QHeaderView)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor

from ..shared.id_manager import IDManager, ContentType
from ..models.armor_creation_data import (ArmorCreationData, ArmorSlot, ArmorType,
                                         ArmorTier, ArmorRequirements)


class ArmorForgeWizard(QWizard):
    """7-phase wizard for creating custom armor"""

    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.armor_data = ArmorCreationData()

        self.setWindowTitle("🛡️ Armor Forge - Create Custom Armor")
        self.setWizardStyle(QWizard.ModernStyle)
        self.resize(800, 600)

        # Add pages
        self.addPage(ModeSelectionPage(self.id_manager, self.armor_data))
        self.addPage(BasicPropertiesPage(self.armor_data))
        self.addPage(CoreStatsPage(self.armor_data))
        self.addPage(ResistanceDefensePage(self.armor_data))
        self.addPage(SpeedMobilityPage(self.armor_data))
        self.addPage(VisualMaterialsPage(self.armor_data))
        self.addPage(AdvancedFeaturesPage(self.armor_data))
        self.addPage(ReviewExportPage(self.armor_data, self.id_manager))

        # Connect signals
        self.currentIdChanged.connect(self.on_page_changed)

    def on_page_changed(self, page_id):
        """Handle page changes"""
        if page_id == 7:  # Review page
            # Update the review page with current data
            review_page = self.page(page_id)
            if hasattr(review_page, 'update_review'):
                review_page.update_review()

    def done(self, result):
        """Handle wizard completion"""
        if result == QWizard.Rejected and hasattr(self.armor_data, 'armor_id'):
            # User canceled - release the allocated ID if any
            if self.armor_data.armor_id >= 20000:  # Only release custom IDs
                self.id_manager.release_id(ContentType.ARMOR, self.armor_data.armor_id)

        super().done(result)


class ModeSelectionPage(QWizardPage):
    """Phase 1: Mode Selection & ID Assignment"""

    def __init__(self, id_manager: IDManager, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 1: Mode Selection & ID Assignment")
        self.setSubTitle("Choose how to create your armor and assign a unique ID")

        layout = QVBoxLayout()

        # Mode selection
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()

        self.mode_buttons = QButtonGroup(self)

        self.new_armor_radio = QRadioButton("Create New Armor (blank slate)")
        self.new_armor_radio.setChecked(True)
        self.mode_buttons.addButton(self.new_armor_radio, 0)

        self.edit_armor_radio = QRadioButton("Edit Existing Armor")
        self.mode_buttons.addButton(self.edit_armor_radio, 1)

        self.duplicate_armor_radio = QRadioButton("Duplicate Existing Armor")
        self.mode_buttons.addButton(self.duplicate_armor_radio, 2)

        mode_layout.addWidget(self.new_armor_radio)
        mode_layout.addWidget(self.edit_armor_radio)
        mode_layout.addWidget(self.duplicate_armor_radio)

        # Browse button for edit/duplicate modes
        self.browse_btn = QPushButton("Browse Existing Armor...")
        self.browse_btn.setEnabled(False)
        self.browse_btn.clicked.connect(self.browse_armor)
        mode_layout.addWidget(self.browse_btn)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # ID assignment
        id_group = QGroupBox("ID Assignment")
        id_layout = QFormLayout()

        self.id_buttons = QButtonGroup(self)

        self.auto_id_radio = QRadioButton("Auto-assign next available ID (recommended)")
        self.auto_id_radio.setChecked(True)
        self.id_buttons.addButton(self.auto_id_radio, 0)

        self.manual_id_radio = QRadioButton("Manually specify ID")
        self.id_buttons.addButton(self.manual_id_radio, 1)

        id_layout.addRow(self.auto_id_radio)
        id_layout.addRow(self.manual_id_radio)

        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(20000, 29999)
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(lambda checked: self.manual_id_spin.setEnabled(checked))
        id_layout.addRow("Custom ID:", self.manual_id_spin)

        # ID status
        self.id_status_label = QLabel("Next available ID: 20000")
        self.id_status_label.setStyleSheet("color: blue; font-weight: bold;")
        id_layout.addRow("Status:", self.id_status_label)

        id_group.setLayout(id_layout)
        layout.addWidget(id_group)

        # Mode change connections
        self.mode_buttons.buttonClicked.connect(self.on_mode_changed)

        self.setLayout(layout)
        self.update_id_status()

    def on_mode_changed(self, button):
        """Handle mode selection change"""
        mode_id = self.mode_buttons.id(button)
        self.browse_btn.setEnabled(mode_id in [1, 2])  # Edit or duplicate

    def browse_armor(self):
        """Open armor browser dialog"""
        # TODO: Implement armor browser
        QMessageBox.information(self, "Browse Armor", "Armor browser not yet implemented")

    def update_id_status(self):
        """Update ID status display"""
        try:
            next_id = self.id_manager.get_next_id(ContentType.ARMOR)
            self.id_status_label.setText(f"Next available ID: {next_id}")
            self.id_status_label.setStyleSheet("color: blue; font-weight: bold;")
        except ValueError as e:
            self.id_status_label.setText(f"Error: {str(e)}")
            self.id_status_label.setStyleSheet("color: red; font-weight: bold;")

    def validatePage(self):
        """Validate page before proceeding"""
        # Allocate ID
        try:
            if self.auto_id_radio.isChecked():
                armor_id = self.id_manager.allocate_id(ContentType.ARMOR)
            else:
                requested_id = self.manual_id_spin.value()
                armor_id = self.id_manager.allocate_id(ContentType.ARMOR, requested_id)

            self.armor_data.armor_id = armor_id

            # Set creation mode
            mode_map = {0: "new", 1: "edit", 2: "duplicate"}
            self.armor_data.creation_mode = mode_map[self.mode_buttons.checkedId()]

            return True

        except ValueError as e:
            QMessageBox.warning(self, "ID Allocation Failed", str(e))
            return False


class BasicPropertiesPage(QWizardPage):
    """Phase 2: Basic Properties & Classification"""

    def __init__(self, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 2: Basic Properties & Classification")
        self.setSubTitle("Define the fundamental properties of your armor")

        layout = QVBoxLayout()

        # Naming section
        naming_group = QGroupBox("Naming & Identity")
        naming_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("e.g., Dragon Scale Helmet")
        naming_layout.addRow("Armor Name:", self.name_edit)

        self.display_name_edit = QLineEdit()
        self.display_name_edit.setPlaceholderText("Optional display name")
        naming_layout.addRow("Display Name:", self.display_name_edit)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("Flavor text description")
        naming_layout.addRow("Description:", self.description_edit)

        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)

        # Classification section
        class_group = QGroupBox("Slot & Type Classification")
        class_layout = QFormLayout()

        self.slot_combo = QComboBox()
        self.slot_combo.addItems([
            "Helmet (Head)",
            "Chest Armor (Chest)",
            "Leg Armor (Legs)",
            "Boots (Feet)",
            "Right Ring",
            "Left Ring",
            "Shield (Left Hand)"
        ])
        class_layout.addRow("Equipment Slot:", self.slot_combo)

        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "Cloth (light, magic)",
            "Leather (medium, stealth)",
            "Chain (medium, balanced)",
            "Plate (heavy, defense)",
            "Magic (special, unique)"
        ])
        class_layout.addRow("Armor Type:", self.type_combo)

        self.material_edit = QLineEdit()
        self.material_edit.setPlaceholderText("e.g., Iron, Mithril, Dragon Scale")
        class_layout.addRow("Material:", self.material_edit)

        class_group.setLayout(class_layout)
        layout.addWidget(class_group)

        # Quality section
        quality_group = QGroupBox("Quality & Rarity")
        quality_layout = QFormLayout()

        self.tier_combo = QComboBox()
        self.tier_combo.addItems([
            "Common",
            "Uncommon",
            "Rare",
            "Epic",
            "Legendary",
            "Unique"
        ])
        quality_layout.addRow("Tier:", self.tier_combo)

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(1)
        quality_layout.addRow("Level Requirement:", self.level_spin)

        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)

        self.setLayout(layout)

    def validatePage(self):
        """Validate and save data"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Armor name is required")
            return False

        # Save data
        self.armor_data.armor_name = self.name_edit.text().strip()
        self.armor_data.display_name = self.display_name_edit.text().strip()
        self.armor_data.description = self.description_edit.toPlainText().strip()

        # Slot mapping
        slot_map = {
            0: ArmorSlot.HEAD,
            1: ArmorSlot.CHEST,
            2: ArmorSlot.LEGS,
            3: ArmorSlot.FEET,
            4: ArmorSlot.RIGHT_RING,
            5: ArmorSlot.LEFT_RING,
            6: ArmorSlot.LEFT_HAND
        }
        self.armor_data.slot = slot_map[self.slot_combo.currentIndex()]

        # Type mapping
        type_map = {
            0: ArmorType.CLOTH,
            1: ArmorType.LEATHER,
            2: ArmorType.CHAIN,
            3: ArmorType.PLATE,
            4: ArmorType.MAGIC
        }
        self.armor_data.armor_type = type_map[self.type_combo.currentIndex()]

        self.armor_data.material_name = self.material_edit.text().strip()

        # Tier mapping
        tier_map = {
            0: ArmorTier.COMMON,
            1: ArmorTier.UNCOMMON,
            2: ArmorTier.RARE,
            3: ArmorTier.EPIC,
            4: ArmorTier.LEGENDARY,
            5: ArmorTier.UNIQUE
        }
        self.armor_data.tier = tier_map[self.tier_combo.currentIndex()]

        return True


class CoreStatsPage(QWizardPage):
    """Phase 3: Core Stat Bonuses"""

    def __init__(self, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 3: Core Stat Bonuses")
        self.setSubTitle("Define the primary and derived stat bonuses")

        layout = QVBoxLayout()

        # Primary stats
        primary_group = QGroupBox("Primary Stats")
        primary_layout = QFormLayout()

        self.strength_spin = QSpinBox()
        self.strength_spin.setRange(-50, 50)
        primary_layout.addRow("Strength:", self.strength_spin)

        self.stamina_spin = QSpinBox()
        self.stamina_spin.setRange(-50, 50)
        primary_layout.addRow("Stamina:", self.stamina_spin)

        self.agility_spin = QSpinBox()
        self.agility_spin.setRange(-50, 50)
        primary_layout.addRow("Agility:", self.agility_spin)

        self.dexterity_spin = QSpinBox()
        self.dexterity_spin.setRange(-50, 50)
        primary_layout.addRow("Dexterity:", self.dexterity_spin)

        self.intelligence_spin = QSpinBox()
        self.intelligence_spin.setRange(-50, 50)
        primary_layout.addRow("Intelligence:", self.intelligence_spin)

        self.wisdom_spin = QSpinBox()
        self.wisdom_spin.setRange(-50, 50)
        primary_layout.addRow("Wisdom:", self.wisdom_spin)

        self.charisma_spin = QSpinBox()
        self.charisma_spin.setRange(-50, 50)
        primary_layout.addRow("Charisma:", self.charisma_spin)

        primary_group.setLayout(primary_layout)
        layout.addWidget(primary_group)

        # Derived stats
        derived_group = QGroupBox("Derived Stats")
        derived_layout = QFormLayout()

        self.health_spin = QSpinBox()
        self.health_spin.setRange(0, 1000)
        derived_layout.addRow("Health Bonus (+HP):", self.health_spin)

        self.mana_spin = QSpinBox()
        self.mana_spin.setRange(0, 1000)
        derived_layout.addRow("Mana Bonus (+MP):", self.mana_spin)

        self.armor_spin = QSpinBox()
        self.armor_spin.setRange(0, 200)
        derived_layout.addRow("Base Armor (physical defense):", self.armor_spin)

        derived_group.setLayout(derived_layout)
        layout.addWidget(derived_group)

        self.setLayout(layout)

    def validatePage(self):
        """Save stat data"""
        self.armor_data.strength = self.strength_spin.value()
        self.armor_data.stamina = self.stamina_spin.value()
        self.armor_data.agility = self.agility_spin.value()
        self.armor_data.dexterity = self.dexterity_spin.value()
        self.armor_data.intelligence = self.intelligence_spin.value()
        self.armor_data.wisdom = self.wisdom_spin.value()
        self.armor_data.charisma = self.charisma_spin.value()
        self.armor_data.health_bonus = self.health_spin.value()
        self.armor_data.mana_bonus = self.mana_spin.value()
        self.armor_data.base_armor = self.armor_spin.value()

        return True


class ResistanceDefensePage(QWizardPage):
    """Phase 4: Resistance & Defense Systems"""

    def __init__(self, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 4: Resistance & Defense Systems")
        self.setSubTitle("Configure elemental resistances and defense mechanics")

        layout = QVBoxLayout()

        # Elemental resistances
        resist_group = QGroupBox("Elemental Resistances (%)")
        resist_layout = QFormLayout()

        self.fire_resist_spin = QDoubleSpinBox()
        self.fire_resist_spin.setRange(0, 100)
        self.fire_resist_spin.setSingleStep(5)
        resist_layout.addRow("Fire Resistance:", self.fire_resist_spin)

        self.ice_resist_spin = QDoubleSpinBox()
        self.ice_resist_spin.setRange(0, 100)
        self.ice_resist_spin.setSingleStep(5)
        resist_layout.addRow("Ice Resistance:", self.ice_resist_spin)

        self.black_resist_spin = QDoubleSpinBox()
        self.black_resist_spin.setRange(0, 100)
        self.black_resist_spin.setSingleStep(5)
        resist_layout.addRow("Black Magic Resistance:", self.black_resist_spin)

        self.mind_resist_spin = QDoubleSpinBox()
        self.mind_resist_spin.setRange(0, 100)
        self.mind_resist_spin.setSingleStep(5)
        resist_layout.addRow("Mind Magic Resistance:", self.mind_resist_spin)

        resist_group.setLayout(resist_layout)
        layout.addWidget(resist_group)

        # Defense mechanics
        defense_group = QGroupBox("Defense Mechanics (%)")
        defense_layout = QFormLayout()

        self.physical_reduction_spin = QDoubleSpinBox()
        self.physical_reduction_spin.setRange(0, 75)
        self.physical_reduction_spin.setSingleStep(5)
        defense_layout.addRow("Physical Damage Reduction:", self.physical_reduction_spin)

        self.magic_reduction_spin = QDoubleSpinBox()
        self.magic_reduction_spin.setRange(0, 75)
        self.magic_reduction_spin.setSingleStep(5)
        defense_layout.addRow("Magic Damage Reduction:", self.magic_reduction_spin)

        self.critical_reduction_spin = QDoubleSpinBox()
        self.critical_reduction_spin.setRange(0, 50)
        self.critical_reduction_spin.setSingleStep(5)
        defense_layout.addRow("Critical Hit Reduction:", self.critical_reduction_spin)

        defense_group.setLayout(defense_layout)
        layout.addWidget(defense_group)

        self.setLayout(layout)

    def validatePage(self):
        """Save resistance data"""
        self.armor_data.resist_fire = self.fire_resist_spin.value()
        self.armor_data.resist_ice = self.ice_resist_spin.value()
        self.armor_data.resist_black = self.black_resist_spin.value()
        self.armor_data.resist_mind = self.mind_resist_spin.value()
        self.armor_data.physical_reduction = self.physical_reduction_spin.value()
        self.armor_data.magic_reduction = self.magic_reduction_spin.value()
        self.armor_data.critical_reduction = self.critical_reduction_spin.value()

        return True


class SpeedMobilityPage(QWizardPage):
    """Phase 5: Speed & Mobility Modifiers"""

    def __init__(self, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 5: Speed & Mobility Modifiers")
        self.setSubTitle("Configure movement and combat speed modifiers")

        layout = QVBoxLayout()

        # Speed modifiers
        speed_group = QGroupBox("Speed Modifiers (%)")
        speed_layout = QFormLayout()

        self.run_speed_spin = QDoubleSpinBox()
        self.run_speed_spin.setRange(-50, 50)
        self.run_speed_spin.setSingleStep(5)
        speed_layout.addRow("Run Speed:", self.run_speed_spin)

        self.fight_speed_spin = QDoubleSpinBox()
        self.fight_speed_spin.setRange(-50, 50)
        self.fight_speed_spin.setSingleStep(5)
        speed_layout.addRow("Fight Speed (attack speed):", self.fight_speed_spin)

        self.cast_speed_spin = QDoubleSpinBox()
        self.cast_speed_spin.setRange(-50, 50)
        self.cast_speed_spin.setSingleStep(5)
        speed_layout.addRow("Cast Speed (spell casting):", self.cast_speed_spin)

        speed_group.setLayout(speed_layout)
        layout.addWidget(speed_group)

        # Special bonuses
        special_group = QGroupBox("Special Movement Bonuses")
        special_layout = QFormLayout()

        self.stealth_spin = QDoubleSpinBox()
        self.stealth_spin.setRange(0, 100)
        self.stealth_spin.setSingleStep(10)
        special_layout.addRow("Stealth Bonus (% harder to detect):", self.stealth_spin)

        self.swimming_spin = QDoubleSpinBox()
        self.swimming_spin.setRange(-50, 100)
        self.swimming_spin.setSingleStep(10)
        special_layout.addRow("Swimming Speed (%):", self.swimming_spin)

        self.jump_spin = QDoubleSpinBox()
        self.jump_spin.setRange(-50, 100)
        self.jump_spin.setSingleStep(10)
        special_layout.addRow("Jump Height (%):", self.jump_spin)

        special_group.setLayout(special_layout)
        layout.addWidget(special_group)

        self.setLayout(layout)

    def validatePage(self):
        """Save speed data"""
        self.armor_data.run_speed_modifier = self.run_speed_spin.value()
        self.armor_data.fight_speed_modifier = self.fight_speed_spin.value()
        self.armor_data.cast_speed_modifier = self.cast_speed_spin.value()
        self.armor_data.stealth_bonus = self.stealth_spin.value()
        self.armor_data.swimming_speed = self.swimming_spin.value()
        self.armor_data.jump_height = self.jump_spin.value()

        return True


class VisualMaterialsPage(QWizardPage):
    """Phase 6: Visual Properties & Materials"""

    def __init__(self, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 6: Visual Properties & Materials")
        self.setSubTitle("Configure appearance, icons, and visual effects")

        layout = QVBoxLayout()

        # Visual components
        visual_group = QGroupBox("Visual Components")
        visual_layout = QFormLayout()

        self.icon_edit = QLineEdit()
        self.icon_edit.setPlaceholderText("e.g., ui_item_equip_armor_chest_dragon")
        visual_layout.addRow("Icon Handle:", self.icon_edit)

        self.mesh_edit = QLineEdit()
        self.mesh_edit.setPlaceholderText("3D model file path")
        visual_layout.addRow("3D Model File:", self.mesh_edit)

        self.texture_edit = QLineEdit()
        self.texture_edit.setPlaceholderText("Diffuse texture file")
        visual_layout.addRow("Texture File:", self.texture_edit)

        self.normal_edit = QLineEdit()
        self.normal_edit.setPlaceholderText("Normal map file")
        visual_layout.addRow("Normal Map:", self.normal_edit)

        visual_group.setLayout(visual_layout)
        layout.addWidget(visual_group)

        # Material properties
        material_group = QGroupBox("Material Properties")
        material_layout = QFormLayout()

        self.color_btn = QPushButton("Choose Material Color")
        self.color_btn.clicked.connect(self.choose_color)
        self.current_color = QColor("#808080")
        self.update_color_button()
        material_layout.addRow("Material Color:", self.color_btn)

        self.equip_sound_edit = QLineEdit()
        self.equip_sound_edit.setPlaceholderText("Sound played when equipping")
        material_layout.addRow("Equip Sound:", self.equip_sound_edit)

        material_group.setLayout(material_layout)
        layout.addWidget(material_group)

        # Special effects
        effects_group = QGroupBox("Special Effects")
        effects_layout = QVBoxLayout()

        self.effects_list = QListWidget()
        self.effects_list.setMaximumHeight(100)
        effects_layout.addWidget(self.effects_list)

        effects_btn_layout = QHBoxLayout()
        add_effect_btn = QPushButton("Add Effect")
        add_effect_btn.clicked.connect(self.add_effect)
        remove_effect_btn = QPushButton("Remove Effect")
        remove_effect_btn.clicked.connect(self.remove_effect)

        effects_btn_layout.addWidget(add_effect_btn)
        effects_btn_layout.addWidget(remove_effect_btn)
        effects_layout.addLayout(effects_btn_layout)

        effects_group.setLayout(effects_layout)
        layout.addWidget(effects_group)

        self.setLayout(layout)

    def choose_color(self):
        """Choose material color"""
        color = QColorDialog.getColor(self.current_color, self, "Choose Material Color")
        if color.isValid():
            self.current_color = color
            self.update_color_button()

    def update_color_button(self):
        """Update color button appearance"""
        self.color_btn.setStyleSheet(f"background-color: {self.current_color.name()}; color: white;")
        self.color_btn.setText(f"Color: {self.current_color.name()}")

    def add_effect(self):
        """Add special effect"""
        # TODO: Implement effect selection dialog
        self.effects_list.addItem("Glow Effect (placeholder)")

    def remove_effect(self):
        """Remove selected effect"""
        current_row = self.effects_list.currentRow()
        if current_row >= 0:
            self.effects_list.takeItem(current_row)

    def validatePage(self):
        """Save visual data"""
        self.armor_data.icon_handle = self.icon_edit.text().strip()
        self.armor_data.mesh_file = self.mesh_edit.text().strip()
        self.armor_data.texture_file = self.texture_edit.text().strip()
        self.armor_data.normal_map = self.normal_edit.text().strip()
        self.armor_data.material_color = self.current_color.name()
        self.armor_data.equip_sound = self.equip_sound_edit.text().strip()

        # Save effects
        self.armor_data.special_effects = []
        for i in range(self.effects_list.count()):
            self.armor_data.special_effects.append(self.effects_list.item(i).text())

        return True


class AdvancedFeaturesPage(QWizardPage):
    """Phase 7: Advanced Features & Export"""

    def __init__(self, armor_data: ArmorCreationData, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.init_ui()

    def init_ui(self):
        self.setTitle("Phase 7: Advanced Features")
        self.setSubTitle("Configure item sets, special abilities, and enchantments")

        layout = QVBoxLayout()

        # Item set
        set_group = QGroupBox("Item Set")
        set_layout = QFormLayout()

        self.set_id_spin = QSpinBox()
        self.set_id_spin.setRange(0, 9999)
        set_layout.addRow("Set ID (0 = not part of set):", self.set_id_spin)

        set_group.setLayout(set_layout)
        layout.addWidget(set_group)

        # Set bonuses (placeholder for now)
        bonuses_group = QGroupBox("Set Bonuses (2/3/4-piece bonuses)")
        bonuses_layout = QVBoxLayout()

        self.bonuses_table = QTableWidget(0, 2)
        self.bonuses_table.setHorizontalHeaderLabels(["Pieces Required", "Bonus Effect"])
        self.bonuses_table.horizontalHeader().setStretchLastSection(True)
        bonuses_layout.addWidget(self.bonuses_table)

        bonuses_btn_layout = QHBoxLayout()
        add_bonus_btn = QPushButton("Add Set Bonus")
        add_bonus_btn.clicked.connect(self.add_set_bonus)
        remove_bonus_btn = QPushButton("Remove Bonus")
        remove_bonus_btn.clicked.connect(self.remove_set_bonus)

        bonuses_btn_layout.addWidget(add_bonus_btn)
        bonuses_btn_layout.addWidget(remove_bonus_btn)
        bonuses_layout.addLayout(bonuses_btn_layout)

        bonuses_group.setLayout(bonuses_layout)
        layout.addWidget(bonuses_group)

        # Special abilities
        abilities_group = QGroupBox("Special Abilities")
        abilities_layout = QVBoxLayout()

        self.abilities_list = QListWidget()
        self.abilities_list.setMaximumHeight(100)
        abilities_layout.addWidget(self.abilities_list)

        abilities_btn_layout = QHBoxLayout()
        add_ability_btn = QPushButton("Add Ability")
        add_ability_btn.clicked.connect(self.add_ability)
        remove_ability_btn = QPushButton("Remove Ability")
        remove_ability_btn.clicked.connect(self.remove_ability)

        abilities_btn_layout.addWidget(add_ability_btn)
        abilities_btn_layout.addWidget(remove_ability_btn)
        abilities_layout.addLayout(abilities_btn_layout)

        abilities_group.setLayout(abilities_layout)
        layout.addWidget(abilities_group)

        # Enchantment slots
        enchant_group = QGroupBox("Enchantment")
        enchant_layout = QFormLayout()

        self.enchant_slots_spin = QSpinBox()
        self.enchant_slots_spin.setRange(0, 5)
        enchant_layout.addRow("Enchantment Slots:", self.enchant_slots_spin)

        enchant_group.setLayout(enchant_layout)
        layout.addWidget(enchant_group)

        self.setLayout(layout)

    def add_set_bonus(self):
        """Add set bonus"""
        # TODO: Implement set bonus dialog
        row_count = self.bonuses_table.rowCount()
        self.bonuses_table.insertRow(row_count)
        self.bonuses_table.setItem(row_count, 0, QTableWidgetItem("2"))
        self.bonuses_table.setItem(row_count, 1, QTableWidgetItem("Fire Resistance +10%"))

    def remove_set_bonus(self):
        """Remove selected set bonus"""
        current_row = self.bonuses_table.currentRow()
        if current_row >= 0:
            self.bonuses_table.removeRow(current_row)

    def add_ability(self):
        """Add special ability"""
        # TODO: Implement ability selection dialog
        self.abilities_list.addItem("Passive: Health Regeneration")

    def remove_ability(self):
        """Remove selected ability"""
        current_row = self.abilities_list.currentRow()
        if current_row >= 0:
            self.abilities_list.takeItem(current_row)

    def validatePage(self):
        """Save advanced features data"""
        self.armor_data.item_set_id = self.set_id_spin.value()
        self.armor_data.enchantment_slots = self.enchant_slots_spin.value()

        # Save set bonuses
        self.armor_data.set_bonuses = []
        for row in range(self.bonuses_table.rowCount()):
            pieces_item = self.bonuses_table.item(row, 0)
            bonus_item = self.bonuses_table.item(row, 1)
            if pieces_item and bonus_item:
                self.armor_data.set_bonuses.append({
                    "pieces": int(pieces_item.text()),
                    "bonus": bonus_item.text()
                })

        # Save abilities
        self.armor_data.special_abilities = []
        for i in range(self.abilities_list.count()):
            self.armor_data.special_abilities.append(self.abilities_list.item(i).text())

        return True


class ReviewExportPage(QWizardPage):
    """Review & Export page"""

    def __init__(self, armor_data: ArmorCreationData, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.armor_data = armor_data
        self.id_manager = id_manager
        self.init_ui()

    def init_ui(self):
        self.setTitle("Review & Export")
        self.setSubTitle("Review your armor configuration and export to game format")

        layout = QVBoxLayout()

        # Summary table
        self.summary_table = QTableWidget(0, 2)
        self.summary_table.setHorizontalHeaderLabels(["Property", "Value"])
        self.summary_table.horizontalHeader().setStretchLastSection(True)
        layout.addWidget(self.summary_table)

        # Validation results
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout()

        self.validation_results = QLabel("Validation pending...")
        validation_layout.addWidget(self.validation_results)

        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)

        # Balance rating
        balance_group = QGroupBox("Balance Analysis")
        balance_layout = QVBoxLayout()

        self.balance_label = QLabel("Balance rating: Calculating...")
        balance_layout.addWidget(self.balance_label)

        balance_group.setLayout(balance_layout)
        layout.addWidget(balance_group)

        self.setLayout(layout)

    def update_review(self):
        """Update the review display with current armor data"""
        # Clear existing rows
        self.summary_table.setRowCount(0)

        # Add summary data
        summary_data = [
            ("Armor ID", str(self.armor_data.armor_id)),
            ("Name", self.armor_data.armor_name),
            ("Slot", self.armor_data.get_slot_name()),
            ("Type", self.armor_data.armor_type.value.title()),
            ("Tier", self.armor_data.tier.value.title()),
            ("Material", self.armor_data.material_name or "None"),
            ("Base Armor", str(self.armor_data.base_armor)),
            ("Total Stat Bonuses", str(self.armor_data.get_total_stat_bonuses())),
            ("Defense Rating", f"{self.armor_data.calculate_defense_rating():.1f}/100"),
            ("Balance Rating", f"{self.armor_data.calculate_balance_rating()}/100"),
        ]

        for property_name, value in summary_data:
            row_count = self.summary_table.rowCount()
            self.summary_table.insertRow(row_count)
            self.summary_table.setItem(row_count, 0, QTableWidgetItem(property_name))
            self.summary_table.setItem(row_count, 1, QTableWidgetItem(value))

        # Update balance rating
        balance_rating = self.armor_data.calculate_balance_rating()
        if balance_rating >= 80:
            balance_text = f"⚠️ OVERPOWERED ({balance_rating}/100)"
            balance_color = "red"
        elif balance_rating >= 60:
            balance_text = f"✓ STRONG ({balance_rating}/100)"
            balance_color = "orange"
        elif balance_rating >= 40:
            balance_text = f"✓ BALANCED ({balance_rating}/100)"
            balance_color = "green"
        else:
            balance_text = f"⚠️ WEAK ({balance_rating}/100)"
            balance_color = "blue"

        self.balance_label.setText(f'<span style="color: {balance_color};">{balance_text}</span>')

        # Basic validation
        errors = []
        warnings = []

        if not self.armor_data.armor_name:
            errors.append("Armor name is required")

        if not self.armor_data.icon_handle:
            warnings.append("No icon assigned (will use placeholder)")

        if self.armor_data.base_armor == 0 and not self.armor_data.is_magic_armor():
            warnings.append("Armor provides no physical defense")

        # Display validation results
        if errors:
            validation_text = "❌ ERRORS:\n" + "\n".join(f"• {e}" for e in errors)
            if warnings:
                validation_text += "\n\n⚠️ WARNINGS:\n" + "\n".join(f"• {w}" for w in warnings)
        elif warnings:
            validation_text = "⚠️ WARNINGS:\n" + "\n".join(f"• {w}" for w in warnings)
        else:
            validation_text = "✅ All validations passed"

        self.validation_results.setText(validation_text)

    def validatePage(self):
        """Final validation before export"""
        # Check for critical errors
        if not self.armor_data.armor_name:
            QMessageBox.warning(self, "Export Failed", "Armor name is required")
            return False

        # Export would happen here in the final implementation
        QMessageBox.information(self, "Export Complete",
                              f"Armor '{self.armor_data.armor_name}' (ID: {self.armor_data.armor_id}) "
                              "has been created successfully!\n\n"
                              "Note: CFF export functionality will be implemented in the next phase.")

        return True