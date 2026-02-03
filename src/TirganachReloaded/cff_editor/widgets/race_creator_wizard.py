"""Race Creator Wizard - 7-phase guided race creation interface

This wizard provides a step-by-step interface for creating new races in SpellForce,
following the comprehensive requirements from the Race Creation Guide.
"""

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QLabel, QLineEdit, QTextEdit, QComboBox, 
    QSpinBox, QDoubleSpinBox, QGroupBox, QVBoxLayout, QHBoxLayout, 
    QGridLayout, QCheckBox, QPushButton, QButtonGroup, QRadioButton,
    QListWidget, QListWidgetItem, QMessageBox, QTabWidget, QWidget,
    QTableWidget, QTableWidgetItem
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPixmap, QIcon

from ..shared.id_manager import IDManager, ContentType
from ..models.race_creation_data import (
    RaceCreationData, RaceType, UnitType, UnitData, UnitStats, 
    UnitCombat, UnitAppearance, BuildingData
)
from AllwissendeAlmacht.allwissende_almacht import AllwissendeAlmachtDialog
from .race_validation import RaceValidator


class RaceCreatorWizard(QWizard):
    """7-phase wizard for creating custom races"""
    
    # Signal emitted when race is successfully created
    raceCreated = Signal(RaceCreationData)
    
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.race_data = None
        self.race_id = None
        
        self.setWindowTitle("SpellForce Race Creator")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setFixedSize(800, 600)
        
        # Add wizard pages
        self.mode_page = ModeSelectionPage(self.id_manager)
        self.basic_page = BasicRacePropertiesPage()
        self.stats_page = RaceStatsScalingPage()
        self.units_page = UnitsCreationPage()
        self.buildings_page = BuildingsCreationPage()
        self.assets_page = AudioVisualAssetsPage()
        self.review_page = ReviewExportPage()
        
        self.addPage(self.mode_page)
        self.addPage(self.basic_page)
        self.addPage(self.stats_page)
        self.addPage(self.units_page)
        self.addPage(self.buildings_page)
        self.addPage(self.assets_page)
        self.addPage(self.review_page)
        
        # Connect the finish button
        self.finished.connect(self.on_finished)

    def on_finished(self, result):
        """Handle wizard completion"""
        if result == QWizard.Accepted and self.race_data:
            # Race was created successfully
            self.raceCreated.emit(self.race_data)
        elif result == QWizard.Rejected and self.race_id:
            # Wizard was cancelled, release the ID
            self.id_manager.release_id(ContentType.RACE, self.race_id)

    def collect_race_data(self) -> RaceCreationData:
        """Collect data from all wizard pages into RaceCreationData object"""
        # Get the race ID from the mode selection page
        self.race_id = self.page(0).race_id  # ModeSelectionPage is page 0
        
        # Create basic race with info from basic page
        race_data = RaceCreationData(
            race_id=self.race_id,
            race_name=self.basic_page.race_name_edit.text(),
            race_type=RaceType(self.basic_page.race_type_combo.currentText().lower().replace(" ", "_")),
            description=self.basic_page.description_edit.toPlainText(),
            visual_theme=self.basic_page.visual_theme_edit.text(),
            equipment_scaling=self.stats_page.scaling_spin.value(),
            shadow_size=self.stats_page.shadow_size_spin.value(),
            animation_library=self.assets_page.anim_lib_edit.text(),
            sound_prefix=self.assets_page.sound_prefix_edit.text()
        )
        
        # Add units from units page
        units = self.units_page.get_units()
        for unit in units:
            race_data.add_unit(unit)
        
        # Add buildings from buildings page
        buildings = self.buildings_page.get_buildings()
        for building in buildings:
            race_data.add_building(building)
        
        # Add asset paths
        race_data.asset_paths = {
            "models": self.assets_page.model_path_edit.text(),
            "textures": self.assets_page.texture_path_edit.text(),
            "sounds": self.assets_page.sound_path_edit.text(),
        }
        
        # Add Lua modifications that will be required
        race_data.lua_modifications = {
            "races_properties": [f"{self.race_id}={race_data.race_name}"],
            "object_figure_init": ["Register race in racenames array", 
                                   "Add shadow size entry", 
                                   "Create animation library", 
                                   "Register all units"],
            "object_equipment_init": [f"Add {race_data.race_name} to racenames array"],
            "object_building_init": ["Register building light effect"],
            "DrwSound": ["Add race-specific combat sounds"]
        }
        
        # Store for export
        self.race_data = race_data
        return race_data


class ModeSelectionPage(QWizardPage):
    """Page 1: Select creation mode and assign race ID"""
    
    def __init__(self, id_manager: IDManager):
        super().__init__()
        self.id_manager = id_manager
        self.race_id = None
        self.setTitle("Race Creation Mode")
        self.setSubTitle("Choose how to create your race and assign a unique ID.")
        
        layout = QVBoxLayout()
        
        # Mode selection
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()
        
        self.new_radio = QRadioButton("Create New Race from Scratch")
        self.edit_radio = QRadioButton("Edit Existing Race (Advanced)")
        self.use_template_radio = QRadioButton("Use Predefined Template")
        
        self.new_radio.setChecked(True)
        mode_layout.addWidget(self.new_radio)
        mode_layout.addWidget(self.edit_radio)
        mode_layout.addWidget(self.use_template_radio)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # ID Assignment
        id_group = QGroupBox("Race ID Assignment")
        id_layout = QVBoxLayout()
        
        # Note about race ID
        id_note = QLabel("Note: Custom races should use ID 7 or higher (existing races use IDs 1-6)")
        id_note.setWordWrap(True)
        id_note.setStyleSheet("color: gray; font-size: 9pt;")
        id_layout.addWidget(id_note)
        
        # ID input
        id_input_layout = QHBoxLayout()
        id_input_layout.addWidget(QLabel("Race ID:"))
        self.id_spin = QSpinBox()
        self.id_spin.setRange(7, 999)  # Allow up to 999 for custom races
        self.id_spin.setValue(7)
        self.id_spin.setToolTip("Enter a unique ID for your race (7+ recommended)")
        
        self.allocate_btn = QPushButton("Auto-Assign Next ID")
        self.allocate_btn.clicked.connect(self.allocate_race_id)
        
        id_input_layout.addWidget(self.id_spin)
        id_input_layout.addWidget(self.allocate_btn)
        id_layout.addLayout(id_input_layout)
        
        # Show available IDs
        available_layout = QHBoxLayout()
        available_layout.addWidget(QLabel("Available IDs:"))
        self.available_count_label = QLabel()
        available_layout.addWidget(self.available_count_label)
        available_layout.addStretch()
        id_layout.addLayout(available_layout)
        
        id_group.setLayout(id_layout)
        layout.addWidget(id_group)
        
        # Template selection (only visible if template mode selected)
        self.template_group = QGroupBox("Select Race Template")
        template_layout = QVBoxLayout()
        
        self.template_combo = QComboBox()
        self.template_combo.addItems([
            "Humanoid (Human/Elf/Dwarf-like)", 
            "Orcish (Orc/Troll-like)", 
            "Dark (Dark Elf-like)", 
            "Beast (Animal-like)", 
            "Magical (Magic-based)"
        ])
        template_layout.addWidget(self.template_combo)
        
        self.template_group.setLayout(template_layout)
        self.template_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.template_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
        # Connect signals
        self.edit_radio.toggled.connect(lambda: self.template_group.setVisible(False))
        self.use_template_radio.toggled.connect(lambda: self.template_group.setVisible(True))
        self.new_radio.toggled.connect(lambda: self.template_group.setVisible(False))

    def allocate_race_id(self):
        """Allocate the next available race ID"""
        race_id = self.id_manager.allocate_id(ContentType.RACE)
        if race_id is not None:
            self.id_spin.setValue(race_id)
            self.race_id = race_id
            QMessageBox.information(self, "ID Assigned", f"Race ID {race_id} allocated successfully!")
        else:
            QMessageBox.warning(self, "No IDs Available", "No more race IDs are available in the defined range.")
    
    def initializePage(self):
        """Update available count when page is shown"""
        available_count = self.id_manager.get_available_count(ContentType.RACE)
        self.available_count_label.setText(str(available_count))
        # Get the next available ID to show as a suggestion
        next_id = self.id_manager.get_next_id(ContentType.RACE)
        if next_id:
            self.id_spin.setValue(next_id)
    
    def validatePage(self):
        """Validate the selection before proceeding"""
        self.race_id = self.id_spin.value()
        
        # Check if ID is already in use
        if self.id_manager.is_id_used(ContentType.RACE, self.race_id):
            reply = QMessageBox.question(
                self, 
                "ID In Use", 
                f"Race ID {self.race_id} is already in use. Do you want to continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return False
        
        # If creating new race, temporarily mark ID as used
        if self.new_radio.isChecked() or self.use_template_radio.isChecked():
            # Allocate this ID temporarily (will be properly allocated in collect_race_data)
            pass
        elif self.edit_radio.isChecked():
            # For editing, we'll need to load existing data (not implemented in this basic version)
            pass
            
        return True

    def nextId(self):
        """Go to the next page"""
        return 1


class BasicRacePropertiesPage(QWizardPage):
    """Page 2: Define basic race properties"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Basic Race Properties")
        self.setSubTitle("Define the fundamental characteristics of your race.")
        
        layout = QVBoxLayout()
        
        # Race name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Race Name:"))
        self.race_name_edit = QLineEdit()
        self.race_name_edit.setPlaceholderText("e.g., Dragonkin, Crystal Elves, Iron Dwarves...")
        name_layout.addWidget(self.race_name_edit)
        layout.addLayout(name_layout)
        
        # Race type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Race Type:"))
        self.race_type_combo = QComboBox()
        self.race_type_combo.addItems([t.value.replace("_", " ").title() for t in RaceType])
        type_layout.addWidget(self.race_type_combo)
        layout.addLayout(type_layout)
        
        # Visual theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Visual Theme:"))
        self.visual_theme_edit = QLineEdit()
        self.visual_theme_edit.setPlaceholderText("e.g., Large giants, small faeries, metallic skin...")
        theme_layout.addWidget(self.visual_theme_edit)
        layout.addLayout(theme_layout)
        
        # Description
        desc_group = QGroupBox("Race Description")
        desc_layout = QVBoxLayout()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Describe your race's lore, appearance, and unique characteristics...")
        desc_layout.addWidget(self.description_edit)
        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def validatePage(self):
        """Validate the inputs"""
        if not self.race_name_edit.text().strip():
            QMessageBox.warning(self, "Invalid Input", "Race name cannot be empty.")
            return False
        return True


class RaceStatsScalingPage(QWizardPage):
    """Page 3: Set race stats and scaling"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Race Stats & Scaling")
        self.setSubTitle("Configure equipment scaling, shadow size, and other race-wide stats.")
        
        layout = QGridLayout()
        
        # Equipment scaling (100-180)
        layout.addWidget(QLabel("Equipment Scaling:"), 0, 0)
        self.scaling_spin = QSpinBox()
        self.scaling_spin.setRange(100, 180)
        self.scaling_spin.setValue(100)
        self.scaling_spin.setSuffix("%")
        self.scaling_spin.setToolTip("How effectively race members use equipment (100-180%)")
        layout.addWidget(self.scaling_spin, 0, 1)
        
        # Shadow size (0.8-2.0)
        layout.addWidget(QLabel("Shadow Size:"), 1, 0)
        self.shadow_size_spin = QDoubleSpinBox()
        self.shadow_size_spin.setRange(0.8, 2.0)
        self.shadow_size_spin.setValue(1.0)
        self.shadow_size_spin.setSingleStep(0.1)
        self.shadow_size_spin.setToolTip("Size of shadows cast by race units (0.8-2.0)")
        layout.addWidget(self.shadow_size_spin, 1, 1)
        
        # Note about values
        note_label = QLabel(
            "Equipment scaling: 100-180% (how effectively the race uses equipment)\n"
            "Shadow size: 0.8-2.0 (relative size of unit shadows, affects visual appearance)"
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray; font-size: 9pt; margin-top: 10px;")
        layout.addWidget(note_label, 2, 0, 1, 2)
        
        # Additional race stats could go here
        layout.setRowStretch(3, 1)
        self.setLayout(layout)


class UnitsCreationPage(QWizardPage):
    """Page 4: Design required units for the race"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Units Creation")
        self.setSubTitle("Design the required units for your race (minimum 9 types).")
        
        layout = QVBoxLayout()
        
        # Unit types to be created
        self.required_units = {
            "Worker": UnitType.WORKER,
            "Fighter": UnitType.FIGHTER, 
            "Ranged": UnitType.RANGED,
            "Mage": UnitType.MAGE,
            "Siege": UnitType.SIEGE,
            "Titan": UnitType.TITAN,
            "Swarm": UnitType.SWARM
        }
        
        # Tabs for different unit types
        self.unit_tabs = QTabWidget()
        
        # Create a tab for each required unit type
        for unit_name, unit_type in self.required_units.items():
            tab = self.create_unit_tab(unit_name, unit_type)
            self.unit_tabs.addTab(tab, unit_name)
        
        # Add button for special units if needed
        add_special_btn = QPushButton("Add Special Unit")
        add_special_btn.clicked.connect(self.add_special_unit_tab)
        
        layout.addWidget(self.unit_tabs)
        layout.addWidget(add_special_btn)
        
        # Info about required units
        info_label = QLabel(
            "Required units:\n"
            "• Worker: Resource gatherer\n"
            "• Fighter: Basic melee combatant\n" 
            "• Ranged: Projectile attacker\n"
            "• Mage: Magic user\n"
            "• Siege: Building destroyer\n"
            "• Titan: Powerful elite unit\n"
            "• Swarm: Multiple small units"
        )
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def create_unit_tab(self, unit_name: str, unit_type: UnitType):
        """Create a tab for configuring a specific unit type"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # Basic unit info
        basic_group = QGroupBox(f"{unit_name} Unit Properties")
        basic_layout = QGridLayout()
        
        basic_layout.addWidget(QLabel("Unit Name:"), 0, 0)
        unit_name_edit = QLineEdit()
        unit_name_edit.setPlaceholderText(f"e.g., {unit_name} of this race")
        basic_layout.addWidget(unit_name_edit, 0, 1)
        
        basic_layout.addWidget(QLabel("Description:"), 1, 0)
        unit_desc_edit = QTextEdit()
        unit_desc_edit.setMaximumHeight(50)
        basic_layout.addWidget(unit_desc_edit, 1, 1)
        
        basic_group.setLayout(basic_layout)
        layout.addWidget(basic_group)
        
        # Stats group
        stats_group = QGroupBox("Base Stats")
        stats_layout = QGridLayout()
        
        stats_layout.addWidget(QLabel("Strength:"), 0, 0)
        strength_spin = QSpinBox()
        strength_spin.setRange(1, 100)
        strength_spin.setValue(10)
        stats_layout.addWidget(strength_spin, 0, 1)
        
        stats_layout.addWidget(QLabel("Dexterity:"), 1, 0)
        dexterity_spin = QSpinBox()
        dexterity_spin.setRange(1, 100)
        dexterity_spin.setValue(10)
        stats_layout.addWidget(dexterity_spin, 1, 1)
        
        stats_layout.addWidget(QLabel("Intelligence:"), 2, 0)
        intelligence_spin = QSpinBox()
        intelligence_spin.setRange(1, 100)
        intelligence_spin.setValue(10)
        stats_layout.addWidget(intelligence_spin, 2, 1)
        
        stats_layout.addWidget(QLabel("Phys. Resistance:"), 0, 2)
        phys_res_spin = QSpinBox()
        phys_res_spin.setRange(-50, 100)
        phys_res_spin.setValue(0)
        stats_layout.addWidget(phys_res_spin, 0, 3)
        
        stats_layout.addWidget(QLabel("Magic Resistance:"), 1, 2)
        mag_res_spin = QSpinBox()
        mag_res_spin.setRange(-50, 100)
        mag_res_spin.setValue(0)
        stats_layout.addWidget(mag_res_spin, 1, 3)
        
        stats_layout.addWidget(QLabel("Walk Speed:"), 2, 2)
        walk_speed_spin = QDoubleSpinBox()
        walk_speed_spin.setRange(0.1, 20.0)
        walk_speed_spin.setValue(4.0)
        walk_speed_spin.setSingleStep(0.5)
        stats_layout.addWidget(walk_speed_spin, 2, 3)
        
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # Combat group
        combat_group = QGroupBox("Combat Stats")
        combat_layout = QGridLayout()
        
        combat_layout.addWidget(QLabel("Health:"), 0, 0)
        health_spin = QSpinBox()
        health_spin.setRange(1, 10000)
        health_spin.setValue(100)
        combat_layout.addWidget(health_spin, 0, 1)
        
        combat_layout.addWidget(QLabel("Health Regen.:"), 1, 0)
        health_regen_spin = QDoubleSpinBox()
        health_regen_spin.setRange(0.0, 100.0)
        health_regen_spin.setValue(0.0)
        health_regen_spin.setSingleStep(0.1)
        combat_layout.addWidget(health_regen_spin, 1, 1)
        
        combat_layout.addWidget(QLabel("Mana:"), 0, 2)
        mana_spin = QSpinBox()
        mana_spin.setRange(0, 10000)
        mana_spin.setValue(50)
        combat_layout.addWidget(mana_spin, 0, 3)
        
        combat_layout.addWidget(QLabel("Mana Regen.:"), 1, 2)
        mana_regen_spin = QDoubleSpinBox()
        mana_regen_spin.setRange(0.0, 100.0)
        mana_regen_spin.setValue(0.0)
        mana_regen_spin.setSingleStep(0.1)
        combat_layout.addWidget(mana_regen_spin, 1, 3)
        
        combat_layout.addWidget(QLabel("Armor:"), 2, 0)
        armor_spin = QSpinBox()
        armor_spin.setRange(0, 1000)
        armor_spin.setValue(0)
        combat_layout.addWidget(armor_spin, 2, 1)
        
        combat_layout.addWidget(QLabel("Min Damage:"), 2, 2)
        min_dmg_spin = QSpinBox()
        min_dmg_spin.setRange(0, 10000)
        min_dmg_spin.setValue(10)
        combat_layout.addWidget(min_dmg_spin, 2, 3)
        
        combat_layout.addWidget(QLabel("Max Damage:"), 3, 0)
        max_dmg_spin = QSpinBox()
        max_dmg_spin.setRange(0, 10000)
        max_dmg_spin.setValue(15)
        combat_layout.addWidget(max_dmg_spin, 3, 1)
        
        combat_layout.addWidget(QLabel("Damage Type:"), 3, 2)
        damage_type_combo = QComboBox()
        damage_type_combo.addItems(["Normal", "Piercing", "Fire", "Ice", "Earth", "Air"])
        combat_layout.addWidget(damage_type_combo, 3, 3)
        
        combat_group.setLayout(combat_layout)
        layout.addWidget(combat_group)
        
        # Appearance group
        appearance_group = QGroupBox("Appearance")
        appearance_layout = QGridLayout()
        
        appearance_layout.addWidget(QLabel("Mesh Name:"), 0, 0)
        mesh_edit = QLineEdit()
        mesh_edit.setPlaceholderText("e.g., figure_yourrace_worker_male.msh")
        appearance_layout.addWidget(mesh_edit, 0, 1)
        
        appearance_layout.addWidget(QLabel("Texture Name:"), 1, 0)
        texture_edit = QLineEdit()
        texture_edit.setPlaceholderText("e.g., figure_yourrace_worker.tga")
        appearance_layout.addWidget(texture_edit, 1, 1)
        
        appearance_layout.addWidget(QLabel("Shadow Size:"), 0, 2)
        shadow_size_spin = QDoubleSpinBox()
        shadow_size_spin.setRange(0.1, 5.0)
        shadow_size_spin.setValue(1.0)
        shadow_size_spin.setSingleStep(0.1)
        appearance_layout.addWidget(shadow_size_spin, 0, 3)
        
        appearance_layout.addWidget(QLabel("Scale:"), 1, 2)
        scale_spin = QDoubleSpinBox()
        scale_spin.setRange(0.1, 5.0)
        scale_spin.setValue(1.0)
        scale_spin.setSingleStep(0.1)
        appearance_layout.addWidget(scale_spin, 1, 3)
        
        appearance_group.setLayout(appearance_layout)
        layout.addWidget(appearance_group)
        
        # Store references to all widgets for later retrieval
        tab.unit_name_edit = unit_name_edit
        tab.unit_desc_edit = unit_desc_edit
        tab.strength_spin = strength_spin
        tab.dexterity_spin = dexterity_spin
        tab.intelligence_spin = intelligence_spin
        tab.phys_res_spin = phys_res_spin
        tab.mag_res_spin = mag_res_spin
        tab.walk_speed_spin = walk_speed_spin
        tab.health_spin = health_spin
        tab.health_regen_spin = health_regen_spin
        tab.mana_spin = mana_spin
        tab.mana_regen_spin = mana_regen_spin
        tab.armor_spin = armor_spin
        tab.min_dmg_spin = min_dmg_spin
        tab.max_dmg_spin = max_dmg_spin
        tab.damage_type_combo = damage_type_combo
        tab.mesh_edit = mesh_edit
        tab.texture_edit = texture_edit
        tab.shadow_size_spin = shadow_size_spin
        tab.scale_spin = scale_spin
        tab.unit_type = unit_type
        
        # Add vertical spacer
        layout.addStretch()
        tab.setLayout(layout)
        
        return tab

    def add_special_unit_tab(self):
        """Add a special unit tab (not required but can be added)"""
        # Get a unique name for the new tab
        tab_name = f"Special_{self.unit_tabs.count() + 1}"
        
        # Create the special unit tab
        tab = self.create_unit_tab(tab_name, UnitType.SPECIAL)
        
        # Add to tabs
        self.unit_tabs.addTab(tab, tab_name)
    
    def get_units(self):
        """Retrieve all configured units from the tabs"""
        units = []
        race_id = self.wizard().race_id  # Get race ID from wizard
        
        for i in range(self.unit_tabs.count()):
            tab = self.unit_tabs.widget(i)
            tab_name = self.unit_tabs.tabText(i)
            
            # Create UnitData object from tab widgets
            unit = UnitData(
                unit_id=5000 + i,  # Start at 5000 to avoid conflicts with existing units
                unit_type=tab.unit_type,
                name=tab.unit_name_edit.text() or tab_name,
                description=tab.unit_desc_edit.toPlainText(),
                stats=UnitStats(
                    strength=tab.strength_spin.value(),
                    dexterity=tab.dexterity_spin.value(),
                    intelligence=tab.intelligence_spin.value(),
                    resistance_physical=tab.phys_res_spin.value(),
                    resistance_magic=tab.mag_res_spin.value(),
                    speed_walk=tab.walk_speed_spin.value(),
                    speed_run=tab.walk_speed_spin.value() * 1.5  # Run is typically 1.5x walk speed
                ),
                combat=UnitCombat(
                    health=tab.health_spin.value(),
                    health_regeneration=tab.health_regen_spin.value(),
                    mana=tab.mana_spin.value(),
                    mana_regeneration=tab.mana_regen_spin.value(),
                    armor=tab.armor_spin.value(),
                    damage_min=tab.min_dmg_spin.value(),
                    damage_max=tab.max_dmg_spin.value(),
                    damage_type=tab.damage_type_combo.currentText().lower()
                ),
                appearance=UnitAppearance(
                    mesh_name=tab.mesh_edit.text(),
                    texture_name=tab.texture_edit.text(),
                    shadow_size=tab.shadow_size_spin.value(),
                    scale=tab.scale_spin.value(),
                    animation_library=f"figure_{race_id}"  # Base animation library name
                ),
                sounds={
                    "combat_hit": f"battle_{tab_name.lower()}_hit",
                    "combat_attack": f"battle_{tab_name.lower()}_att",
                    "combat_die": f"battle_{tab_name.lower()}_die",
                    "work": f"work_{tab_name.lower()}"
                },
                base_name=f"figure_{race_id}",  # Base name for animations
                weapon_types=[],  # Will be filled in later based on race compatibility
                building_id=None  # Will be assigned when we link units to buildings
            )
            
            units.append(unit)
        
        return units


class BuildingsCreationPage(QWizardPage):
    """Page 5: Design required buildings for the race"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Buildings Creation")
        self.setSubTitle("Design the required buildings for your race (minimum 8 types).")
        
        layout = QVBoxLayout()
        
        # Required building types
        self.required_buildings = [
            ("Headquarters", "HQ"),
            ("Resource Depot", "resource"),
            ("Barracks", "barracks"), 
            ("Mage Tower", "mage_tower"),
            ("Siege Workshop", "siege_workshop"),
            ("Titan Forge", "titan_forge"),
            ("Swarm Nest", "swarm_nest"),
            ("Wall Segment", "defense")
        ]
        
        # Create table for buildings
        self.buildings_table = QTableWidget(len(self.required_buildings), 4)
        self.buildings_table.setHorizontalHeaderLabels(["Building Type", "Name", "HP", "Build Time (s)"])
        
        for i, (building_name, building_type) in enumerate(self.required_buildings):
            # Building type
            type_item = QTableWidgetItem(building_name)
            type_item.setFlags(type_item.flags() & ~Qt.ItemIsEditable)  # Make non-editable
            self.buildings_table.setItem(i, 0, type_item)
            
            # Building name
            name_item = QTableWidgetItem(f"{building_name} of {building_type}")
            self.buildings_table.setItem(i, 1, name_item)
            
            # HP (default values)
            hp_item = QTableWidgetItem("500")
            self.buildings_table.setItem(i, 2, hp_item)
            
            # Build time (default values)
            time_item = QTableWidgetItem("30")
            self.buildings_table.setItem(i, 3, time_item)
        
        self.buildings_table.resizeColumnsToContents()
        layout.addWidget(self.buildings_table)
        
        # Add button for custom buildings
        add_custom_btn = QPushButton("Add Custom Building")
        add_custom_btn.clicked.connect(self.add_custom_building)
        layout.addWidget(add_custom_btn)
        
        # Info about required buildings
        info_label = QLabel(
            "Required buildings:\n"
            "• Headquarters: Main building for the race\n"
            "• Resource Depot: Storage for gathered resources\n" 
            "• Barracks: Trains basic military units\n"
            "• Mage Tower: Trains magical units\n"
            "• Siege Workshop: Creates siege weapons\n"
            "• Titan Forge: Creates titan units\n"
            "• Swarm Nest: Creates swarm units\n"
            "• Wall Segment: Defensive structures"
        )
        info_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(info_label)
        
        self.setLayout(layout)
    
    def add_custom_building(self):
        """Add a custom building to the table"""
        row = self.buildings_table.rowCount()
        self.buildings_table.insertRow(row)
        
        # Building type (user can modify)
        type_item = QTableWidgetItem("Custom Building")
        self.buildings_table.setItem(row, 0, type_item)
        
        # Building name
        name_item = QTableWidgetItem("Custom Building Name")
        self.buildings_table.setItem(row, 1, name_item)
        
        # HP
        hp_item = QTableWidgetItem("500")
        self.buildings_table.setItem(row, 2, hp_item)
        
        # Build time
        time_item = QTableWidgetItem("30")
        self.buildings_table.setItem(row, 3, time_item)
    
    def get_buildings(self):
        """Retrieve all configured buildings from the table"""
        buildings = []
        
        for row in range(self.buildings_table.rowCount()):
            type_item = self.buildings_table.item(row, 0)
            name_item = self.buildings_table.item(row, 1)
            hp_item = self.buildings_table.item(row, 2)
            time_item = self.buildings_table.item(row, 3)
            
            building_type = type_item.text()
            name = name_item.text() if name_item else building_type
            hp = int(hp_item.text()) if hp_item and hp_item.text().isdigit() else 500
            build_time = int(time_item.text()) if time_item and time_item.text().isdigit() else 30
            
            building = BuildingData(
                building_id=6000 + row,  # Start at 6000 to avoid conflicts with existing buildings
                building_type=self.map_building_type(building_type),
                name=name,
                description=f"{name} building for the race",
                hp=hp,
                build_time=build_time,
                costs={"gold": 100, "wood": 50, "stone": 50},  # Default costs
                mesh_name=f"building_{building_type.lower().replace(' ', '_')}.msh",
                texture_name=f"building_{building_type.lower().replace(' ', '_')}.tga",
                light_effect=""  # Will be set based on race
            )
            
            buildings.append(building)
        
        return buildings
    
    def map_building_type(self, display_type):
        """Map display building names to internal types"""
        mapping = {
            "Headquarters": "HQ",
            "Resource Depot": "resource",
            "Barracks": "barracks",
            "Mage Tower": "mage_tower",
            "Siege Workshop": "siege_workshop", 
            "Titan Forge": "titan_forge",
            "Swarm Nest": "swarm_nest",
            "Wall Segment": "defense",
        }
        return mapping.get(display_type, display_type.lower().replace(" ", "_"))


class AudioVisualAssetsPage(QWizardPage):
    """Page 6: Link audio and visual assets"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Audio & Visual Assets")
        self.setSubTitle("Specify paths to your race's audio and visual assets.")
        
        layout = QVBoxLayout()
        
        # Animation library name
        anim_layout = QHBoxLayout()
        anim_layout.addWidget(QLabel("Animation Library Name:"))
        self.anim_lib_edit = QLineEdit()
        self.anim_lib_edit.setPlaceholderText("e.g., YourRaceAnims")
        self.anim_lib_edit.setText("RaceAnimLibrary")
        anim_layout.addWidget(self.anim_lib_edit)
        layout.addLayout(anim_layout)
        
        # Sound prefix
        sound_layout = QHBoxLayout()
        sound_layout.addWidget(QLabel("Sound Prefix:"))
        self.sound_prefix_edit = QLineEdit()
        self.sound_prefix_edit.setPlaceholderText("e.g., battle_yourrace")
        self.sound_prefix_edit.setText("battle_race")
        sound_layout.addWidget(self.sound_prefix_edit)
        layout.addLayout(sound_layout)
        
        # Asset paths
        paths_group = QGroupBox("Asset File Paths")
        paths_layout = QGridLayout()
        
        # Model path
        paths_layout.addWidget(QLabel("3D Model Path:"), 0, 0)
        self.model_path_edit = QLineEdit()
        self.model_path_edit.setPlaceholderText("Path to .msh files")
        paths_layout.addWidget(self.model_path_edit, 0, 1)
        
        # Texture path
        paths_layout.addWidget(QLabel("Texture Path:"), 1, 0)
        self.texture_path_edit = QLineEdit()
        self.texture_path_edit.setPlaceholderText("Path to .tga/.png files") 
        paths_layout.addWidget(self.texture_path_edit, 1, 1)
        
        # Sound path
        paths_layout.addWidget(QLabel("Sound Path:"), 2, 0)
        self.sound_path_edit = QLineEdit()
        self.sound_path_edit.setPlaceholderText("Path to .wav files")
        paths_layout.addWidget(self.sound_path_edit, 2, 1)
        
        paths_group.setLayout(paths_layout)
        layout.addWidget(paths_group)
        
        # Required sounds checklist
        sounds_group = QGroupBox("Required Sounds Checklist")
        sounds_layout = QVBoxLayout()
        
        self.required_sounds = [
            "Worker: hit sounds (battle_yourraceworker_hit_01.wav)",
            "Worker: attack sounds (battle_yourraceworker_att_01.wav)", 
            "Worker: die sound (battle_yourraceworker_die.wav)",
            "Fighter: hit sounds (battle_yourracefighter_hit_01.wav)",
            "Fighter: attack sounds (battle_yourracefighter_att_01.wav)",
            "Fighter: die sound (battle_yourracefighter_die.wav)",
            "Titan: attack sounds (battle_titan_yourrace_att_01.wav)",
            "Titan: hit sounds (battle_titan_yourrace_hit_01.wav)",
            "Titan: die sound (battle_titan_yourrace_die.wav)"
        ]
        
        for sound_desc in self.required_sounds:
            checkbox = QCheckBox(sound_desc)
            sounds_layout.addWidget(checkbox)
        
        sounds_group.setLayout(sounds_layout)
        layout.addWidget(sounds_group)
        
        # Note about assets
        note_label = QLabel(
            "Note: You will need to create these assets separately. "
            "The Race Creator will generate the required Lua modifications and file templates, "
            "but the actual 3D models, textures, and sound files must be created in 3D modeling "
            "software and audio editors."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(note_label)
        
        layout.addStretch()
        self.setLayout(layout)


class ReviewExportPage(QWizardPage):
    """Page 7: Review race configuration and export"""
    
    def __init__(self):
        super().__init__()
        self.setTitle("Review & Export Race")
        self.setSubTitle("Review your race configuration and export to game files.")
        
        layout = QVBoxLayout()
        
        # Race summary
        summary_group = QGroupBox("Race Summary")
        summary_layout = QVBoxLayout()
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Validation results
        validation_group = QGroupBox("Validation Results")
        validation_layout = QVBoxLayout()
        
        self.validation_text = QTextEdit()
        self.validation_text.setReadOnly(True)
        self.validation_text.setMaximumHeight(100)
        validation_layout.addWidget(self.validation_text)
        
        validation_group.setLayout(validation_layout)
        layout.addWidget(validation_group)
        
        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()
        
        self.export_lua_checkbox = QCheckBox("Generate Lua modification files")
        self.export_lua_checkbox.setChecked(True)
        export_layout.addWidget(self.export_lua_checkbox)
        
        self.export_cff_checkbox = QCheckBox("Generate CFF data (GameData.cff.mod)")
        self.export_cff_checkbox.setChecked(True)
        export_layout.addWidget(self.export_cff_checkbox)
        
        self.export_assets_checkbox = QCheckBox("Generate assets.lua template")
        self.export_assets_checkbox.setChecked(True)
        export_layout.addWidget(self.export_assets_checkbox)
        
        export_group.setLayout(export_layout)
        layout.addWidget(export_group)
        
        # Export button
        self.export_btn = QPushButton("Export Race Configuration")
        self.export_btn.clicked.connect(self.export_race)
        layout.addWidget(self.export_btn)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
    
    def initializePage(self):
        """Update the summary when page is shown"""
        wizard = self.wizard()
        if wizard:
            race_data = wizard.collect_race_data()
            summary_text = self.format_race_summary(race_data)
            self.summary_text.setPlainText(summary_text)
            
            # Validate the race data
            validator = RaceValidator(wizard.id_manager)
            errors, warnings = validator.validate(race_data)
            validation_html = self.format_validation_results(errors, warnings)
            self.validation_text.setHtml(validation_html)
    
    def format_race_summary(self, race: RaceCreationData) -> str:
        """Format race data as text summary"""
        summary = f"Race: {race.race_name} (ID: {race.race_id})\n"
        summary += f"Type: {race.race_type.value}\n"
        summary += f"Equipment Scaling: {race.equipment_scaling}%\n"
        summary += f"Shadow Size: {race.shadow_size}\n"
        summary += f"Units: {len(race.units)}\n"
        summary += f"Buildings: {len(race.buildings)}\n\n"
        
        # Units summary
        summary += "Units:\n"
        for unit in race.units:
            summary += f"  - {unit.name} ({unit.unit_type.value})\n"
        
        # Buildings summary
        summary += "\nBuildings:\n"
        for building in race.buildings:
            summary += f"  - {building.name} ({building.building_type})\n"
        
        return summary
    
    def format_validation_results(self, errors: list, warnings: list) -> str:
        """Format validation results as HTML"""
        html = "<p>"
        if not errors and not warnings:
            html += '<span style="color: green; font-weight: bold;">✓ Race is valid and ready for export!</span>'
        else:
            if errors:
                html += f'<span style="color: red; font-weight: bold;">{len(errors)} Errors:</span><br>'
                for err in errors:
                    html += f'• {err}<br>'
            if warnings:
                html += f'<span style="color: orange; font-weight: bold;">{len(warnings)} Warnings:</span><br>'
                for warn in warnings:
                    html += f'• {warn}<br>'
        html += "</p>"
        return html
    
    def export_race(self):
        """Export the race configuration"""
        try:
            # Get the race data from the wizard
            wizard = self.wizard()
            race_data = wizard.race_data or wizard.collect_race_data()
            
            # Validate data
            if not race_data.race_name:
                raise ValueError("Race name is required")
            
            # In a real implementation, this would call the race exporter
            # For now, we'll just show a success message
            self.status_label.setText(
                f"✓ Race '{race_data.race_name}' exported successfully!\n"
                f"Files created in the export directory."
            )
            
            # Emit the signal that race was created
            wizard.raceCreated.emit(race_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export race:\n{str(e)}")