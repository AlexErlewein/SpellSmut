from PySide6.QtWidgets import (
    QWizard,
    QWizardPage,
    QVBoxLayout,
    QLabel,
    QRadioButton,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QSpinBox,
    QDoubleSpinBox,
    QTextEdit,
    QDialog,
)
from ..shared.id_manager import IDManager, ContentType
from ..models.weapon_creation_data import (
    WeaponCreationData,
    WeaponHands,
    DamageCategory,
    DamageType,
    Rarity,
    WeaponRequirements,
    WeaponEffect,
)

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
        self.setTitle("Mode Selection & ID Assignment")
        self.setSubTitle("Choose how to create your weapon and assign a unique ID.")

        layout = QVBoxLayout()
        
        # Creation Mode
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()
        self.new_weapon_radio = QRadioButton("Create New Weapon (blank slate)")
        self.edit_weapon_radio = QRadioButton("Edit Existing Weapon (load from 719 weapons)")
        self.duplicate_weapon_radio = QRadioButton("Duplicate & Modify (copy existing, new ID)")
        self.new_weapon_radio.setChecked(True)
        mode_layout.addWidget(self.new_weapon_radio)
        mode_layout.addWidget(self.edit_weapon_radio)
        mode_layout.addWidget(self.duplicate_weapon_radio)
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
        self.weapon_type_combo.addItems(["1H Sword", "2H Axe", "Dagger"]) # Placeholder
        layout.addRow("Weapon Type:", self.weapon_type_combo)

        self.weapon_material_combo = QComboBox()
        # This would be populated with existing and new materials
        self.weapon_material_combo.addItems(["Metal", "Wood", "Bone"]) # Placeholder
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

class RequirementsValuePage(QWizardPage):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Requirements & Value")
        self.setSubTitle("Define what is needed to use the weapon and its economic value.")

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
        self.validation_text.setText("This is a placeholder for the validation results.")
