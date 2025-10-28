from PySide6.QtWidgets import (
    QCheckBox,
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
from PySide6.QtCore import Qt

from ..shared.id_manager import ContentType, IDManager
from ..models.npc_creation_data import (
    NpcCreationData,
    NpcType,
    CharacterClass,
    VoiceType,
    NpcStats,
    NpcCombatStats,
    NpcAppearance,
    NpcBehavior,
)


class NpcCreatorWizard(QWizard):
    """Multi-step wizard for NPC creation"""

    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.npc_data = None
        self.npc_id = None

        self.setWindowTitle("SpellForce NPC Creator")
        self.setMinimumSize(600, 500)

        # Add wizard pages
        self.addPage(ModeSelectionPage(self.id_manager))
        self.addPage(BasicIdentityPage())
        self.addPage(BaseStatsPage())
        self.addPage(CombatStatsPage())
        self.addPage(AppearanceVoicePage())
        self.addPage(BehaviorPage())
        self.addPage(ReviewExportPage())

    def done(self, result):
        """Handle wizard completion/cancellation"""
        if result == QDialog.Rejected and self.npc_id:
            # User canceled - release the allocated ID
            self.id_manager.release_id(ContentType.NPC, self.npc_id)
        super().done(result)

    def collect_npc_data(self) -> NpcCreationData:
        """Collect data from all wizard pages into NpcCreationData object"""
        # Get creation mode and ID from first page
        mode_page = self.page(0)  # ModeSelectionPage
        creation_mode = "new"
        if mode_page.edit_radio.isChecked():
            creation_mode = "edit"
        elif mode_page.duplicate_radio.isChecked():
            creation_mode = "duplicate"

        # Basic identity (page 1)
        identity_page = self.page(1)
        name = identity_page.name_edit.text().strip()
        title = identity_page.title_edit.text().strip()
        description = identity_page.description_edit.toPlainText().strip()
        npc_type = NpcType(identity_page.npc_type_combo.currentText().lower())
        character_class = CharacterClass(identity_page.character_class_combo.currentText().lower())
        level = identity_page.level_spin.value()
        faction = identity_page.faction_edit.text().strip()

        # Base stats (page 2)
        stats_page = self.page(2)
        base_stats = NpcStats(
            strength=stats_page.strength_spin.value(),
            stamina=stats_page.stamina_spin.value(),
            agility=stats_page.agility_spin.value(),
            dexterity=stats_page.dexterity_spin.value(),
            intelligence=stats_page.intelligence_spin.value(),
            wisdom=stats_page.wisdom_spin.value(),
            charisma=stats_page.charisma_spin.value(),
        )

        # Combat stats (page 3)
        combat_page = self.page(3)
        derived_stats = NpcCombatStats(
            melee_attack=combat_page.melee_attack_spin.value(),
            ranged_attack=combat_page.ranged_attack_spin.value(),
            magic_attack=combat_page.magic_attack_spin.value(),
            physical_defense=combat_page.physical_defense_spin.value(),
            magic_defense=combat_page.magic_defense_spin.value(),
            fire_resistance=combat_page.fire_resist_spin.value(),
            ice_resistance=combat_page.ice_resist_spin.value(),
            black_resistance=combat_page.black_resist_spin.value(),
            mind_resistance=combat_page.mind_resist_spin.value(),
        )

        # Appearance (page 4)
        appear_page = self.page(4)
        appearance = NpcAppearance(
            head_id=appear_page.head_id_spin.value(),
            race=appear_page.race_combo.currentText(),
            gender=appear_page.gender_combo.currentText(),
            voice_type=VoiceType(appear_page.voice_type_combo.currentText().lower().replace(" ", "_")),
        )

        # Behavior (page 5)
        behavior_page = self.page(5)
        behavior = NpcBehavior(
            movement_type=behavior_page.movement_combo.currentText(),
            interaction_radius=behavior_page.interaction_radius_spin.value(),
            spawn_location=(behavior_page.spawn_x_spin.value(), behavior_page.spawn_y_spin.value()),
        )

        # Create the complete NPC data object
        npc_data = NpcCreationData(
            npc_id=self.npc_id,
            creation_mode=creation_mode,
            name=name,
            title=title,
            description=description,
            npc_type=npc_type,
            character_class=character_class,
            level=level,
            faction=faction,
            base_stats=base_stats,
            derived_stats=derived_stats,
            appearance=appearance,
            behavior=behavior,
        )

        return npc_data


class ModeSelectionPage(QWizardPage):
    """Phase 1: Mode Selection & ID Assignment"""

    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.npc_id = None

        self.setTitle("NPC Creation Mode")
        self.setSubTitle("Choose how to create your NPC")

        layout = QVBoxLayout()

        # Mode selection
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()

        self.new_radio = QRadioButton("Create New NPC")
        self.new_radio.setChecked(True)
        self.new_radio.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.new_radio)

        self.edit_radio = QRadioButton("Edit Existing NPC")
        self.edit_radio.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.edit_radio)

        self.duplicate_radio = QRadioButton("Duplicate Existing NPC")
        self.duplicate_radio.toggled.connect(self._on_mode_changed)
        mode_layout.addWidget(self.duplicate_radio)

        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)

        # ID assignment section
        id_group = QGroupBox("NPC ID Assignment")
        id_layout = QVBoxLayout()

        # Auto-assign option (recommended)
        self.auto_id_radio = QRadioButton("Auto-assign next available ID")
        self.auto_id_radio.setChecked(True)
        id_layout.addWidget(self.auto_id_radio)

        # Manual ID option
        self.manual_id_radio = QRadioButton("Manually specify ID")
        id_layout.addWidget(self.manual_id_radio)

        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(40000, 49999)
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(
            lambda checked: self.manual_id_spin.setEnabled(checked)
        )
        id_layout.addWidget(self.manual_id_spin)

        # Allocate button
        allocate_btn = QPushButton("Allocate NPC ID")
        allocate_btn.clicked.connect(self.allocate_npc_id)
        id_layout.addWidget(allocate_btn)

        # Status label
        self.id_status_label = QLabel("")
        id_layout.addWidget(self.id_status_label)

        id_group.setLayout(id_layout)
        layout.addWidget(id_group)

        layout.addStretch()
        self.setLayout(layout)

    def _on_mode_changed(self):
        """Handle mode selection changes"""
        # Could add logic to show/hide NPC browser for edit/duplicate modes
        pass

    def allocate_npc_id(self):
        """Allocate an NPC ID"""
        try:
            if self.auto_id_radio.isChecked():
                # Auto-assign
                npc_id = self.id_manager.allocate_id(ContentType.NPC)
            else:
                # Manual ID
                requested_id = self.manual_id_spin.value()
                npc_id = self.id_manager.allocate_id(ContentType.NPC, requested_id)

            self.npc_id = npc_id
            self.id_status_label.setText(
                f"✓ NPC ID {npc_id} allocated successfully!"
            )
            self.id_status_label.setStyleSheet("color: green;")

            # Enable next button
            self.completeChanged.emit()

        except ValueError as e:
            self.id_status_label.setText(f"✗ Error: {str(e)}")
            self.id_status_label.setStyleSheet("color: red;")

    def isComplete(self):
        """Page is complete when ID is allocated"""
        return self.npc_id is not None

    def nextId(self):
        """Determine next page based on mode"""
        if self.new_radio.isChecked():
            return 1  # Basic Identity
        else:
            return 1  # Would go to NPC browser for edit/duplicate


class BasicIdentityPage(QWizardPage):
    """Phase 2: Basic Identity & Classification"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Basic Identity & Classification")
        self.setSubTitle("Define your NPC's basic properties")

        layout = QVBoxLayout()

        # Name and title
        identity_group = QGroupBox("Identity")
        identity_layout = QFormLayout()

        self.name_edit = QLineEdit()
        self.name_edit.setMaxLength(32)
        identity_layout.addRow("NPC Name:", self.name_edit)

        self.title_edit = QLineEdit()
        self.title_edit.setMaxLength(32)
        identity_layout.addRow("Title/Class Display:", self.title_edit)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        identity_layout.addRow("Description:", self.description_edit)

        identity_group.setLayout(identity_layout)
        layout.addWidget(identity_group)

        # Classification
        class_group = QGroupBox("Classification")
        class_layout = QFormLayout()

        self.npc_type_combo = QComboBox()
        self.npc_type_combo.addItems([t.value for t in NpcType])
        class_layout.addRow("NPC Type:", self.npc_type_combo)

        self.character_class_combo = QComboBox()
        self.character_class_combo.addItems([c.value for c in CharacterClass])
        class_layout.addRow("Character Class:", self.character_class_combo)

        self.level_spin = QSpinBox()
        self.level_spin.setRange(1, 100)
        self.level_spin.setValue(1)
        class_layout.addRow("Level:", self.level_spin)

        self.faction_edit = QLineEdit("HUMANS")
        class_layout.addRow("Faction:", self.faction_edit)

        class_group.setLayout(class_layout)
        layout.addWidget(class_group)

        layout.addStretch()
        self.setLayout(layout)

    def isComplete(self):
        """Page is complete when name is provided"""
        return bool(self.name_edit.text().strip())


class BaseStatsPage(QWizardPage):
    """Phase 3: Base Statistics"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Base Statistics")
        self.setSubTitle("Set your NPC's fundamental attributes")

        layout = QVBoxLayout()

        # Primary Stats
        primary_group = QGroupBox("Primary Attributes")
        primary_layout = QFormLayout()

        self.strength_spin = QSpinBox()
        self.strength_spin.setRange(1, 100)
        self.strength_spin.setValue(10)
        primary_layout.addRow("Strength:", self.strength_spin)

        self.stamina_spin = QSpinBox()
        self.stamina_spin.setRange(1, 100)
        self.stamina_spin.setValue(10)
        primary_layout.addRow("Stamina:", self.stamina_spin)

        self.agility_spin = QSpinBox()
        self.agility_spin.setRange(1, 100)
        self.agility_spin.setValue(10)
        primary_layout.addRow("Agility:", self.agility_spin)

        self.dexterity_spin = QSpinBox()
        self.dexterity_spin.setRange(1, 100)
        self.dexterity_spin.setValue(10)
        primary_layout.addRow("Dexterity:", self.dexterity_spin)

        self.intelligence_spin = QSpinBox()
        self.intelligence_spin.setRange(1, 100)
        self.intelligence_spin.setValue(10)
        primary_layout.addRow("Intelligence:", self.intelligence_spin)

        self.wisdom_spin = QSpinBox()
        self.wisdom_spin.setRange(1, 100)
        self.wisdom_spin.setValue(10)
        primary_layout.addRow("Wisdom:", self.wisdom_spin)

        self.charisma_spin = QSpinBox()
        self.charisma_spin.setRange(1, 100)
        self.charisma_spin.setValue(10)
        primary_layout.addRow("Charisma:", self.charisma_spin)

        primary_group.setLayout(primary_layout)
        layout.addWidget(primary_group)

        # Derived Stats Preview
        derived_group = QGroupBox("Derived Stats Preview")
        derived_layout = QFormLayout()

        self.health_label = QLabel("100")
        derived_layout.addRow("Health (HP):", self.health_label)

        self.mana_label = QLabel("50")
        derived_layout.addRow("Mana (MP):", self.mana_label)

        self.armor_label = QLabel("5")
        derived_layout.addRow("Base Armor:", self.armor_label)

        derived_group.setLayout(derived_layout)
        layout.addWidget(derived_group)

        # Connect stat changes to preview updates
        for spin in [self.strength_spin, self.stamina_spin, self.agility_spin,
                     self.dexterity_spin, self.intelligence_spin, self.wisdom_spin,
                     self.charisma_spin]:
            spin.valueChanged.connect(self.update_derived_preview)

        layout.addStretch()
        self.setLayout(layout)

    def update_derived_preview(self):
        """Update derived stats preview based on primary stats"""
        # Simple calculation for preview (actual calculation will be more complex)
        strength = self.strength_spin.value()
        stamina = self.stamina_spin.value()

        health = 50 + (stamina * 5)
        mana = 20 + (strength * 2)
        armor = 2 + (strength // 10)

        self.health_label.setText(str(health))
        self.mana_label.setText(str(mana))
        self.armor_label.setText(str(armor))


class CombatStatsPage(QWizardPage):
    """Phase 4: Combat & Skills"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Combat Statistics")
        self.setSubTitle("Configure your NPC's combat capabilities")

        layout = QVBoxLayout()

        # Combat Stats
        combat_group = QGroupBox("Combat Ratings")
        combat_layout = QFormLayout()

        self.melee_attack_spin = QSpinBox()
        self.melee_attack_spin.setRange(0, 100)
        self.melee_attack_spin.setValue(10)
        combat_layout.addRow("Melee Attack:", self.melee_attack_spin)

        self.ranged_attack_spin = QSpinBox()
        self.ranged_attack_spin.setRange(0, 100)
        self.ranged_attack_spin.setValue(0)
        combat_layout.addRow("Ranged Attack:", self.ranged_attack_spin)

        self.magic_attack_spin = QSpinBox()
        self.magic_attack_spin.setRange(0, 100)
        self.magic_attack_spin.setValue(0)
        combat_layout.addRow("Magic Attack:", self.magic_attack_spin)

        self.physical_defense_spin = QSpinBox()
        self.physical_defense_spin.setRange(0, 100)
        self.physical_defense_spin.setValue(5)
        combat_layout.addRow("Physical Defense:", self.physical_defense_spin)

        self.magic_defense_spin = QSpinBox()
        self.magic_defense_spin.setRange(0, 100)
        self.magic_defense_spin.setValue(5)
        combat_layout.addRow("Magic Defense:", self.magic_defense_spin)

        combat_group.setLayout(combat_layout)
        layout.addWidget(combat_group)

        # Resistances
        resist_group = QGroupBox("Elemental Resistances")
        resist_layout = QFormLayout()

        self.fire_resist_spin = QSpinBox()
        self.fire_resist_spin.setRange(-50, 100)
        self.fire_resist_spin.setValue(0)
        resist_layout.addRow("Fire Resistance:", self.fire_resist_spin)

        self.ice_resist_spin = QSpinBox()
        self.ice_resist_spin.setRange(-50, 100)
        self.ice_resist_spin.setValue(0)
        resist_layout.addRow("Ice Resistance:", self.ice_resist_spin)

        self.black_resist_spin = QSpinBox()
        self.black_resist_spin.setRange(-50, 100)
        self.black_resist_spin.setValue(0)
        resist_layout.addRow("Black Magic Resistance:", self.black_resist_spin)

        self.mind_resist_spin = QSpinBox()
        self.mind_resist_spin.setRange(-50, 100)
        self.mind_resist_spin.setValue(0)
        resist_layout.addRow("Mind Resistance:", self.mind_resist_spin)

        resist_group.setLayout(resist_layout)
        layout.addWidget(resist_group)

        layout.addStretch()
        self.setLayout(layout)


class AppearanceVoicePage(QWizardPage):
    """Phase 5: Appearance & Voice"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Appearance & Voice")
        self.setSubTitle("Customize your NPC's visual appearance and audio")

        layout = QVBoxLayout()

        # Visual Properties
        visual_group = QGroupBox("Visual Appearance")
        visual_layout = QFormLayout()

        self.head_id_spin = QSpinBox()
        self.head_id_spin.setRange(0, 31)
        self.head_id_spin.setValue(0)
        self.head_id_spin.setToolTip("Head model ID (0-31 available)")
        visual_layout.addRow("Head Model ID:", self.head_id_spin)

        self.race_combo = QComboBox()
        self.race_combo.addItems([
            "HUMANS", "DWARVES", "ELVES", "TROLLS", "ORCS", "DARKELVES",
            "_MERCHANTS", "_HAZIM", "_ELVES_SHIEL", "_WULFGAR"
        ])
        visual_layout.addRow("Race:", self.race_combo)

        self.gender_combo = QComboBox()
        self.gender_combo.addItems(["MALE", "FEMALE", "MALE_ESSENTIAL", "FEMALE_ESSENTIAL"])
        visual_layout.addRow("Gender:", self.gender_combo)

        visual_group.setLayout(visual_layout)
        layout.addWidget(visual_group)

        # Audio Properties
        audio_group = QGroupBox("Voice & Audio")
        audio_layout = QFormLayout()

        self.voice_type_combo = QComboBox()
        self.voice_type_combo.addItems([v.value for v in VoiceType])
        self.voice_type_combo.setToolTip("Note: Cannot add custom voices")
        audio_layout.addRow("Voice Type:", self.voice_type_combo)

        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)

        # Research Note
        note_label = QLabel(
            "<b>Research Note:</b> Head models are limited to existing game assets (IDs 0-31). "
            "Custom voices cannot be added - only predefined voice sets are available."
        )
        note_label.setWordWrap(True)
        note_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(note_label)

        layout.addStretch()
        self.setLayout(layout)


class BehaviorPage(QWizardPage):
    """Phase 6: Behavior & Interaction"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Behavior & Interaction")
        self.setSubTitle("Configure your NPC's AI behavior and interaction settings")

        layout = QVBoxLayout()

        # Behavior Patterns
        behavior_group = QGroupBox("AI Behavior")
        behavior_layout = QFormLayout()

        self.movement_combo = QComboBox()
        self.movement_combo.addItems(["stationary", "patrol", "wander"])
        behavior_layout.addRow("Movement Type:", self.movement_combo)

        self.interaction_radius_spin = QSpinBox()
        self.interaction_radius_spin.setRange(1, 50)
        self.interaction_radius_spin.setValue(5)
        behavior_layout.addRow("Interaction Radius:", self.interaction_radius_spin)

        behavior_group.setLayout(behavior_layout)
        layout.addWidget(behavior_group)

        # Spawn Settings
        spawn_group = QGroupBox("Spawn Settings")
        spawn_layout = QFormLayout()

        self.spawn_x_spin = QSpinBox()
        self.spawn_x_spin.setRange(-10000, 10000)
        self.spawn_x_spin.setValue(0)
        spawn_layout.addRow("Spawn X Coordinate:", self.spawn_x_spin)

        self.spawn_y_spin = QSpinBox()
        self.spawn_y_spin.setRange(-10000, 10000)
        self.spawn_y_spin.setValue(0)
        spawn_layout.addRow("Spawn Y Coordinate:", self.spawn_y_spin)

        spawn_group.setLayout(spawn_layout)
        layout.addWidget(spawn_group)

        layout.addStretch()
        self.setLayout(layout)


class ReviewExportPage(QWizardPage):
    """Phase 7: Review & Export"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setTitle("Review & Export")
        self.setSubTitle("Review your NPC configuration and export to game files")

        layout = QVBoxLayout()

        # Review text area
        self.review_text = QTextEdit()
        self.review_text.setReadOnly(True)
        layout.addWidget(self.review_text)

        # Export options
        export_group = QGroupBox("Export Options")
        export_layout = QVBoxLayout()

        self.export_cff_check = QCheckBox("Export to CFF format")
        self.export_cff_check.setChecked(True)
        export_layout.addWidget(self.export_cff_check)

        self.export_lua_check = QCheckBox("Export Lua behavior scripts")
        self.export_lua_check.setChecked(True)
        export_layout.addWidget(self.export_lua_check)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Export button
        self.export_btn = QPushButton("Export NPC")
        self.export_btn.clicked.connect(self.export_npc)
        layout.addWidget(self.export_btn)

        # Status
        self.status_label = QLabel("")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def initializePage(self):
        """Generate review text when page is shown"""
        wizard = self.wizard()

        # Collect data from all pages
        review_text = "NPC Configuration Review:\n\n"

        # Basic info (page 1: BasicIdentityPage)
        identity_page = wizard.page(1)
        review_text += f"Name: {identity_page.name_edit.text()}\n"
        review_text += f"Title: {identity_page.title_edit.text()}\n"
        review_text += f"Type: {identity_page.npc_type_combo.currentText()}\n"
        review_text += f"Class: {identity_page.character_class_combo.currentText()}\n"
        review_text += f"Level: {identity_page.level_spin.value()}\n"
        review_text += f"Faction: {identity_page.faction_edit.text()}\n\n"

        # Stats (page 2: BaseStatsPage)
        stats_page = wizard.page(2)
        review_text += "Base Stats:\n"
        review_text += f"  STR: {stats_page.strength_spin.value()}\n"
        review_text += f"  STA: {stats_page.stamina_spin.value()}\n"
        review_text += f"  AGI: {stats_page.agility_spin.value()}\n"
        review_text += f"  DEX: {stats_page.dexterity_spin.value()}\n"
        review_text += f"  INT: {stats_page.intelligence_spin.value()}\n"
        review_text += f"  WIS: {stats_page.wisdom_spin.value()}\n"
        review_text += f"  CHA: {stats_page.charisma_spin.value()}\n\n"

        # Combat Stats (page 3: CombatStatsPage)
        combat_page = wizard.page(3)
        review_text += "Combat Stats:\n"
        review_text += f"  Melee Attack: {combat_page.melee_attack_spin.value()}\n"
        review_text += f"  Ranged Attack: {combat_page.ranged_attack_spin.value()}\n"
        review_text += f"  Magic Attack: {combat_page.magic_attack_spin.value()}\n"
        review_text += f"  Physical Defense: {combat_page.physical_defense_spin.value()}\n"
        review_text += f"  Magic Defense: {combat_page.magic_defense_spin.value()}\n"
        review_text += f"  Fire Resistance: {combat_page.fire_resist_spin.value()}\n"
        review_text += f"  Ice Resistance: {combat_page.ice_resist_spin.value()}\n"
        review_text += f"  Black Magic Resistance: {combat_page.black_resist_spin.value()}\n"
        review_text += f"  Mind Resistance: {combat_page.mind_resist_spin.value()}\n\n"

        # Appearance (page 4: AppearanceVoicePage)
        appear_page = wizard.page(4)
        review_text += "Appearance:\n"
        review_text += f"  Head ID: {appear_page.head_id_spin.value()}\n"
        review_text += f"  Race: {appear_page.race_combo.currentText()}\n"
        review_text += f"  Gender: {appear_page.gender_combo.currentText()}\n"
        review_text += f"  Voice: {appear_page.voice_type_combo.currentText()}\n\n"

        # Behavior (page 5: BehaviorPage)
        behavior_page = wizard.page(5)
        review_text += "Behavior:\n"
        review_text += f"  Movement Type: {behavior_page.movement_combo.currentText()}\n"
        review_text += f"  Interaction Radius: {behavior_page.interaction_radius_spin.value()}\n"
        review_text += f"  Spawn Location: ({behavior_page.spawn_x_spin.value()}, {behavior_page.spawn_y_spin.value()})\n"

        self.review_text.setPlainText(review_text)

    def export_npc(self):
        """Export the NPC configuration"""
        try:
            # Collect all data from wizard pages
            self.npc_data = self.collect_npc_data()

            # Basic validation
            if not self.npc_data.name:
                raise ValueError("NPC name is required")

            # TODO: Implement actual export to CFF and Lua files
            # For now, just show success message
            self.status_label.setText("✓ NPC data collected successfully! Export functionality coming soon.")
            self.status_label.setStyleSheet("color: green;")

            # Store the data in the wizard for parent access
            self.wizard().npc_data = self.npc_data

        except Exception as e:
            self.status_label.setText(f"✗ Export failed: {str(e)}")
            self.status_label.setStyleSheet("color: red;")