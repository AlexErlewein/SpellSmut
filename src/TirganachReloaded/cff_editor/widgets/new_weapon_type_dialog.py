from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QGroupBox,
    QPushButton,
    QHBoxLayout,
)
from ..shared.id_manager import IDManager

class NewWeaponTypeDialog(QDialog):
    """Create a new weapon type"""
    
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Weapon Type")
        self.setModal(True)
        self.id_manager = id_manager
        
        layout = QFormLayout()
        
        # Type ID (auto-assigned from 20+)
        self.type_id_label = QLabel("Auto-assigned: 20")
        layout.addRow("Type ID:", self.type_id_label)
        
        # Type name
        self.type_name_edit = QLineEdit()
        self.type_name_edit.setPlaceholderText("e.g., Katana, Scimitar, Wand")
        layout.addRow("Type Name:", self.type_name_edit)
        
        # Category
        self.category_combo = QComboBox()
        self.category_combo.addItems(["Melee", "Ranged", "Magic"])
        layout.addRow("Category:", self.category_combo)
        
        # Hands
        self.hands_combo = QComboBox()
        self.hands_combo.addItems(["1H", "2H", "Unarmed"])
        layout.addRow("Hands:", self.hands_combo)
        
        # Damage type
        self.damage_type_combo = QComboBox()
        self.damage_type_combo.addItems(["Slash", "Pierce", "Blunt", "Mixed"])
        layout.addRow("Damage Type:", self.damage_type_combo)
        
        # Base weapon (for sounds/animations)
        self.base_weapon_combo = QComboBox()
        self.base_weapon_combo.addItems([
            "Dagger", "Sword", "Axe", "Mace", "Hammer",
            "Staff", "Spear", "Halberd", "Bow", "Crossbow", "Claw"
        ])
        layout.addRow("Base Weapon (for animations):", self.base_weapon_combo)
        
        # Sounds
        sound_group = QGroupBox("Sound Effects")
        sound_layout = QFormLayout()
        
        self.hit_sound_combo = QComboBox()
        self.populate_hit_sounds()
        sound_layout.addRow("Hit Sound:", self.hit_sound_combo)
        
        self.miss_sound_combo = QComboBox()
        self.populate_miss_sounds()
        sound_layout.addRow("Miss Sound:", self.miss_sound_combo)
        
        sound_group.setLayout(sound_layout)
        layout.addRow(sound_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Type")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def populate_hit_sounds(self):
        """Populate hit sound dropdown"""
        hit_sounds = [
            "battle_hit_1hdagger",
            "battle_hit_1hsword",
            "battle_hit_1haxe",
            "battle_hit_1hmacespiky",
            "battle_hit_1hmaceblunt",
            "battle_hit_1hhammer",
            "battle_hit_1hstaff",
            "battle_hit_2hsword",
            "battle_hit_2haxe",
            "battle_hit_2hmace",
            "battle_hit_2hhammer",
            "battle_hit_2hstaff",
            "battle_hit_2hspear",
            "battle_hit_2hhalberd",
            "battle_hit_2hbow",
            "battle_hit_2hcrossbow",
            "battle_hit_claw",
            "battle_hit_fist",
            "battle_hit_mouth"
        ]
        self.hit_sound_combo.addItems(hit_sounds)
    
    def populate_miss_sounds(self):
        """Populate miss sound dropdown"""
        miss_sounds = [
            "battle_miss_sword",
            "battle_miss_hammer",
            "battle_miss_staff",
            "battle_miss_bow",
            "battle_miss_fist"
        ]
        self.miss_sound_combo.addItems(miss_sounds)
    
    def get_weapon_type_data(self) -> dict:
        """Get new weapon type data"""
        return {
            "type_id": 20,  # Start from 20 (after official 0-19)
            "type_name": self.type_name_edit.text(),
            "category": self.category_combo.currentText().lower(),
            "hands": self.hands_combo.currentText(),
            "damage_type": self.damage_type_combo.currentText().lower(),
            "base_weapon": self.base_weapon_combo.currentText().lower(),
            "hit_sound": self.hit_sound_combo.currentText(),
            "miss_sound": self.miss_sound_combo.currentText()
        }
