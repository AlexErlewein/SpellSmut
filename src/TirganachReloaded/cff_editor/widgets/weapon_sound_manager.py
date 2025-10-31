"""
Weapon Sound Manager for SpellForce Weapon Forge

Provides a comprehensive sound selection system for weapons,
with mappings from DrwSound.lua and proper categorization.
"""
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, 
    QPushButton, QDialogButtonBox, QGroupBox, QTreeWidget, 
    QTreeWidgetItem, QLineEdit, QSplitter, QTextEdit
)
from PySide6.QtCore import Qt


class WeaponSoundManager:
    """Manages weapon sounds with comprehensive database from DrwSound.lua"""
    
    def __init__(self):
        self.sound_mappings = {}
        self.weapon_categories = {}
        self._load_sound_mappings()
    
    def _load_sound_mappings(self):
        """Load sound mappings from DrwSound.lua"""
        try:
            # Try to find DrwSound.lua in various locations
            possible_paths = [
                Path("../../OriginalGameFiles/script/DrwSound.lua"),
                Path("../../../OriginalGameFiles/script/DrwSound.lua"),
                Path("OriginalGameFiles/script/DrwSound.lua"),
                Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "script" / "DrwSound.lua"
            ]
            
            drwsound_path = None
            for path in possible_paths:
                if path.exists():
                    drwsound_path = path
                    break
            
            if not drwsound_path:
                print("Warning: DrwSound.lua not found, using fallback sounds")
                self._load_fallback_sounds()
                return
            
            print(f"Loading sound mappings from: {drwsound_path}")
            
            with open(drwsound_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Parse weapon sound mappings
            weapon_patterns = {
                'sword': {
                    'hit': r'kDrwWt1HSword\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissSword\s*=\s*"([^"]+)"'
                },
                'axe': {
                    'hit': r'kDrwWt(1H|2H)Axe\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMiss(Hammer|Sword)\s*=\s*"([^"]+)"'  # Axes often use sword miss sounds
                },
                'hammer': {
                    'hit': r'kDrwWt(1H|2H)Hammer\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissHammer\s*=\s*"([^"]+)"'
                },
                'dagger': {
                    'hit': r'kDrwWt1HDagger\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissSword\s*=\s*"([^"]+)"'  # Daggers use sword miss
                },
                'staff': {
                    'hit': r'kDrwWt(1H|2H)Staff\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissStaff\s*=\s*"([^"]+)"'
                },
                'spear': {
                    'hit': r'kDrwWt(2H)Spear\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissStaff\s*=\s*"([^"]+)"'  # Spears use staff miss
                },
                'bow': {
                    'hit': r'kDrwWt(2H)Bow\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissBow\s*=\s*"([^"]+)"'
                },
                'crossbow': {
                    'hit': r'kDrwWt(2H)Crossbow\s*=\s*"([^"]+)"',
                    'miss': r'kDrwMissBow\s*=\s*"([^"]+)"'  # Crossbows use bow miss
                }
            }
            
            for weapon_type, patterns in weapon_patterns.items():
                weapon_sounds = {'hit': [], 'miss': [], 'equip': []}
                
                for sound_type, pattern in patterns.items():
                    matches = re.findall(pattern, content)
                    # Extract unique sounds, remove duplicates, keep first few
                    unique_sounds = []
                    seen = set()
                    for match in matches:
                        if match and match not in seen:
                            unique_sounds.append(match)
                            seen.add(match)
                        if len(unique_sounds) >= 5:  # Limit to first 5
                            break
                    
                    weapon_sounds[sound_type] = unique_sounds
                
                self.sound_mappings[weapon_type] = weapon_sounds
            
            print(f"Loaded sounds for weapon types: {list(self.sound_mappings.keys())}")
            
        except Exception as e:
            print(f"Error loading sound mappings: {e}")
            self._load_fallback_sounds()
    
    def _load_fallback_sounds(self):
        """Load basic fallback sounds when DrwSound.lua is not available"""
        self.sound_mappings = {
            'sword': {
                'hit': ['battle_hit_1hsword'],
                'miss': ['battle_miss_sword']
            },
            'axe': {
                'hit': ['battle_hit_1haxe', 'battle_hit_2haxe'],
                'miss': ['battle_miss_hammer']
            },
            'hammer': {
                'hit': ['battle_hit_1hhammer', 'battle_hit_2hhammer'],
                'miss': ['battle_miss_hammer']
            },
            'dagger': {
                'hit': ['battle_hit_1hdagger'],
                'miss': ['battle_miss_sword']
            },
            'staff': {
                'hit': ['battle_hit_1hstaff', 'battle_hit_2hstaff'],
                'miss': ['battle_miss_staff']
            },
            'spear': {
                'hit': ['battle_hit_2hspear'],
                'miss': ['battle_miss_staff']
            },
            'bow': {
                'hit': ['battle_hit_2hbow'],
                'miss': ['battle_miss_bow']
            },
            'crossbow': {
                'hit': ['battle_hit_2hcrossbow'],
                'miss': ['battle_miss_bow']
            }
        }
    
    def get_weapon_sounds(self, weapon_type: str) -> Dict[str, List[str]]:
        """Get available sounds for a weapon type"""
        weapon_type_lower = weapon_type.lower()
        
        # Try to match weapon type to our categories
        for category, sounds in self.sound_mappings.items():
            if category in weapon_type_lower:
                return sounds
        
        # Default to sword sounds if no match
        return self.sound_mappings.get('sword', {'hit': [], 'miss': []})
    
    def suggest_sounds(self, weapon_type: str, hands: str = "1H") -> Dict[str, str]:
        """Suggest appropriate hit and miss sounds for a weapon"""
        sounds = self.get_weapon_sounds(weapon_type)
        
        # Prefer sounds that match the weapon's handedness
        hit_sounds = sounds.get('hit', [])
        miss_sounds = sounds.get('miss', [])
        
        suggested_hit = ""
        suggested_miss = ""
        
        # Find sound with matching handedness
        for sound in hit_sounds:
            if hands.lower() in sound.lower():
                suggested_hit = sound
                break
        
        # If no exact match, use first available
        if not suggested_hit and hit_sounds:
            suggested_hit = hit_sounds[0]
        elif not suggested_hit:
            suggested_hit = "battle_hit_1hsword"  # Ultimate fallback
        
        # Same for miss sounds
        for sound in miss_sounds:
            if hands.lower() in sound.lower():
                suggested_miss = sound
                break
        
        if not suggested_miss and miss_sounds:
            suggested_miss = miss_sounds[0]
        elif not suggested_miss:
            suggested_miss = "battle_miss_sword"  # Ultimate fallback
        
        return {
            'hit': suggested_hit,
            'miss': suggested_miss
        }


class WeaponSoundSelectionDialog(QDialog):
    """Dialog for selecting weapon sounds with preview and categorization"""
    
    def __init__(self, weapon_type: str = "sword", hands: str = "1H", 
                 current_hit: str = "", current_miss: str = "", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Weapon Sounds")
        self.setModal(True)
        self.resize(700, 500)
        
        self.weapon_type = weapon_type
        self.hands = hands
        self.sound_manager = WeaponSoundManager()
        
        self.selected_hit = current_hit
        self.selected_miss = current_miss
        
        self._setup_ui()
        self._populate_sounds()
    
    def _setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        
        # Weapon info
        info_group = QGroupBox("Weapon Information")
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Weapon Type: {self.weapon_type.title()}"))
        info_layout.addWidget(QLabel(f"Hands: {self.hands}"))
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Main content area
        splitter = QSplitter(Qt.Horizontal)
        
        # Hit sounds
        hit_group = QGroupBox("Hit Sound")
        hit_layout = QVBoxLayout()
        
        self.hit_combo = QComboBox()
        self.hit_combo.setMinimumWidth(300)
        self.hit_combo.currentTextChanged.connect(self.on_hit_sound_changed)
        hit_layout.addWidget(self.hit_combo)
        
        # Miss sounds
        miss_group = QGroupBox("Miss Sound")  
        miss_layout = QVBoxLayout()
        
        self.miss_combo = QComboBox()
        self.miss_combo.setMinimumWidth(300)
        self.miss_combo.currentTextChanged.connect(self.on_miss_sound_changed)
        miss_layout.addWidget(self.miss_combo)
        
        hit_group.setLayout(hit_layout)
        miss_group.setLayout(miss_layout)
        
        # Add to splitter
        splitter.addWidget(hit_group)
        splitter.addWidget(miss_group)
        
        layout.addWidget(splitter)
        
        # Preview area
        preview_group = QGroupBox("Sound Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setMaximumHeight(100)
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def _populate_sounds(self):
        """Populate sound combos with available sounds"""
        sounds = self.sound_manager.get_weapon_sounds(self.weapon_type)
        
        # Populate hit sounds
        self.hit_combo.clear()
        if 'hit' in sounds and sounds['hit']:
            self.hit_combo.addItems(sounds['hit'])
        
        # Populate miss sounds
        self.miss_combo.clear()
        if 'miss' in sounds and sounds['miss']:
            self.miss_combo.addItems(sounds['miss'])
        
        # Set current selections
        if self.selected_hit:
            index = self.hit_combo.findText(self.selected_hit)
            if index >= 0:
                self.hit_combo.setCurrentIndex(index)
        
        if self.selected_miss:
            index = self.miss_combo.findText(self.selected_miss)
            if index >= 0:
                self.miss_combo.setCurrentIndex(index)
        
        # Update preview
        self._update_preview()
    
    def on_hit_sound_changed(self, sound_name: str):
        """Handle hit sound selection change"""
        self.selected_hit = sound_name
        self._update_preview()
    
    def on_miss_sound_changed(self, sound_name: str):
        """Handle miss sound selection change"""
        self.selected_miss = sound_name
        self._update_preview()
    
    def _update_preview(self):
        """Update preview text with sound information"""
        preview_text = f"Selected Sounds:\n\n"
        preview_text += f"Hit Sound: {self.selected_hit or 'None'}\n"
        preview_text += f"Miss Sound: {self.selected_miss or 'None'}\n\n"
        
        if self.selected_hit or self.selected_miss:
            preview_text += "Sound will be applied when weapon is used in combat.\n"
            preview_text += "These sounds are referenced from the game's DrwSound.lua file."
        
        self.preview_text.setPlainText(preview_text)
    
    def get_selected_sounds(self) -> Tuple[str, str]:
        """Get the selected hit and miss sounds"""
        return self.selected_hit, self.selected_miss


# Integration function for weapon forge
def create_sound_selector_widget(weapon_type: str, hands: str = "1H", 
                           current_hit: str = "", current_miss: str = "") -> QWidget:
    """Create a sound selector widget for integration in weapon forge"""
    
    from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget
    
    widget = QWidget()
    layout = QHBoxLayout()
    
    # Sound display
    hit_label = QLabel(f"Hit: {current_hit or 'None'}")
    miss_label = QLabel(f"Miss: {current_miss or 'None'}")
    
    def open_sound_dialog():
        dialog = WeaponSoundSelectionDialog(weapon_type, hands, current_hit, current_miss)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            hit_sound, miss_sound = dialog.get_selected_sounds()
            hit_label.setText(f"Hit: {hit_sound}")
            miss_label.setText(f"Miss: {miss_sound}")
            # Store the sounds somewhere accessible to the main wizard
            widget.hit_sound = hit_sound
            widget.miss_sound = miss_sound
    
    # Browse button
    browse_btn = QPushButton("Browse Sounds...")
    browse_btn.clicked.connect(open_sound_dialog)
    
    layout.addWidget(QLabel(f"{weapon_type.title()} ({hands}):"))
    layout.addWidget(hit_label)
    layout.addWidget(miss_label)
    layout.addWidget(browse_btn)
    layout.addStretch()
    
    widget.setLayout(layout)
    widget.hit_sound = current_hit
    widget.miss_sound = current_miss
    
    return widget


# Utility function for automatic sound assignment
def auto_assign_weapon_sounds(weapon_type: str, weapon_type_name: str, hands: str) -> Dict[str, str]:
    """Automatically assign appropriate sounds based on weapon type"""
    manager = WeaponSoundManager()
    return manager.suggest_sounds(weapon_type, hands)