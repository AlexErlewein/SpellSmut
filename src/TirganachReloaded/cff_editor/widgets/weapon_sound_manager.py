"""
Weapon Sound Manager for SpellForce Weapon Forge

Provides a comprehensive sound selection system for weapons,
with mappings from DrwSound.lua and proper categorization.
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QGroupBox,
    QTreeWidget,
    QTreeWidgetItem,
    QLineEdit,
    QSplitter,
    QTextEdit,
    QWidget,
    QTabWidget,
    QListWidget,
    QListWidgetItem,
    QScrollArea,
    QSlider,
    QMessageBox,
    QProgressBar,
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal

# Initialize pygame mixer for sound preview
try:
    import pygame
    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("Warning: pygame not available, sound preview disabled")


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
                Path(__file__).parent.parent.parent.parent.parent
                / "OriginalGameFiles"
                / "script"
                / "DrwSound.lua",
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

            with open(drwsound_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse weapon sound mappings
            weapon_patterns = {
                "sword": {
                    "hit": r'kDrwWt1HSword\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissSword\s*=\s*"([^"]+)"',
                },
                "axe": {
                    "hit": r'kDrwWt(1H|2H)Axe\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMiss(Hammer|Sword)\s*=\s*"([^"]+)"',  # Axes often use sword miss sounds
                },
                "hammer": {
                    "hit": r'kDrwWt(1H|2H)Hammer\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissHammer\s*=\s*"([^"]+)"',
                },
                "dagger": {
                    "hit": r'kDrwWt1HDagger\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissSword\s*=\s*"([^"]+)"',  # Daggers use sword miss
                },
                "staff": {
                    "hit": r'kDrwWt(1H|2H)Staff\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissStaff\s*=\s*"([^"]+)"',
                },
                "spear": {
                    "hit": r'kDrwWt(2H)Spear\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissStaff\s*=\s*"([^"]+)"',  # Spears use staff miss
                },
                "bow": {
                    "hit": r'kDrwWt(2H)Bow\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissBow\s*=\s*"([^"]+)"',
                },
                "crossbow": {
                    "hit": r'kDrwWt(2H)Crossbow\s*=\s*"([^"]+)"',
                    "miss": r'kDrwMissBow\s*=\s*"([^"]+)"',  # Crossbows use bow miss
                },
            }

            for weapon_type, patterns in weapon_patterns.items():
                weapon_sounds = {"hit": [], "miss": [], "equip": []}

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
            "sword": {"hit": ["battle_hit_1hsword"], "miss": ["battle_miss_sword"]},
            "axe": {
                "hit": ["battle_hit_1haxe", "battle_hit_2haxe"],
                "miss": ["battle_miss_hammer"],
            },
            "hammer": {
                "hit": ["battle_hit_1hhammer", "battle_hit_2hhammer"],
                "miss": ["battle_miss_hammer"],
            },
            "dagger": {"hit": ["battle_hit_1hdagger"], "miss": ["battle_miss_sword"]},
            "staff": {
                "hit": ["battle_hit_1hstaff", "battle_hit_2hstaff"],
                "miss": ["battle_miss_staff"],
            },
            "spear": {"hit": ["battle_hit_2hspear"], "miss": ["battle_miss_staff"]},
            "bow": {"hit": ["battle_hit_2hbow"], "miss": ["battle_miss_bow"]},
            "crossbow": {"hit": ["battle_hit_2hcrossbow"], "miss": ["battle_miss_bow"]},
        }

    def get_weapon_sounds(self, weapon_type: str) -> Dict[str, List[str]]:
        """Get available sounds for a weapon type"""
        weapon_type_lower = weapon_type.lower()

        # Try to match weapon type to our categories
        for category, sounds in self.sound_mappings.items():
            if category in weapon_type_lower:
                return sounds

        # Default to sword sounds if no match
        return self.sound_mappings.get("sword", {"hit": [], "miss": []})

    def suggest_sounds(self, weapon_type: str, hands: str = "1H") -> Dict[str, str]:
        """Suggest appropriate hit and miss sounds for a weapon"""
        sounds = self.get_weapon_sounds(weapon_type)

        # Ensure hands is a string
        if not isinstance(hands, str):
            hands = str(hands)

        # Prefer sounds that match the weapon's handedness
        hit_sounds = sounds.get("hit", [])
        miss_sounds = sounds.get("miss", [])

        suggested_hit = ""
        suggested_miss = ""

        # Enhanced weapon type matching with specific fallbacks
        weapon_type_lower = weapon_type.lower()

        # Priority 1: Find sound with matching handedness
        for sound in hit_sounds:
            sound_str = sound if isinstance(sound, str) else str(sound)
            if hands.lower() in sound_str.lower():
                suggested_hit = sound_str
                break

        # Priority 2: Find exact weapon type match in sound name
        if not suggested_hit:
            weapon_type_mappings = {
                "1h": ["1h", "one", "dagger", "sword", "axe", "hammer", "mace", "staff"],
                "2h": ["2h", "two", "sword", "axe", "hammer", "mace", "staff", "spear", "halberd"],
                "dagger": ["dagger", "1hdagger"],
                "sword": ["sword", "1hsword"],
                "axe": ["axe", "1haxe"],
                "hammer": ["hammer", "1hhammer"],
                "staff": ["staff", "1hstaff"],
                "bow": ["bow", "2hbow"],
                "crossbow": ["crossbow", "2hcrossbow"],
                "spear": ["spear", "2hspear"],
                "halberd": ["halberd", "2hhalberd"],
                "mace": ["mace", "1hmace"],
                "claw": ["claw", "1hclaw"],
                "fist": ["fist", "hand"],
                "mouth": ["mouth"]
            }

            # Check specific weapon type keywords
            for weapon_key, keywords in weapon_type_mappings.items():
                if weapon_key in weapon_type_lower:
                    for sound in hit_sounds:
                        for keyword in keywords:
                            if keyword in sound.lower():
                                suggested_hit = sound
                                break
                        if suggested_hit:
                            break
                    if suggested_hit:
                        break

        # Priority 3: Use first available hit sound
        if not suggested_hit and hit_sounds:
            suggested_hit = hit_sounds[0]

        # Priority 4: Use fallback based on weapon type
        if not suggested_hit:
            fallback_hits = {
                "dagger": "battle_hit_1hdagger",
                "sword": "battle_hit_1hsword",
                "axe": "battle_hit_1haxe",
                "hammer": "battle_hit_1hhammer",
                "staff": "battle_miss_staff",  # Staff use miss sounds
                "bow": "battle_hit_2hbow",
                "crossbow": "battle_hit_2hcrossbow",
                "spear": "battle_hit_2hspear",
                "halberd": "battle_hit_2hsword",  # Halberd uses sword sounds
                "mace": "battle_hit_1hmacespiky",
                "claw": "battle_hit_1hsword",  # Claw uses sword sounds
                "fist": "battle_hit_fist",
                "default": "battle_hit_1hsword"
            }

            for weapon_type_key, fallback in fallback_hits.items():
                if weapon_type_key in weapon_type_lower:
                    suggested_hit = fallback
                    break

        # Ultimate fallback
        if not suggested_hit:
            suggested_hit = "battle_hit_1hsword"

        # Similar logic for miss sounds
        for sound in miss_sounds:
            sound_str = sound if isinstance(sound, str) else str(sound)
            if hands.lower() in sound_str.lower():
                suggested_miss = sound_str
                break

        if not suggested_miss and miss_sounds:
            suggested_miss = miss_sounds[0]

        # Fallback miss sounds by weapon type
        if not suggested_miss:
            fallback_misses = {
                "dagger": "battle_miss_sword",
                "sword": "battle_miss_sword",
                "axe": "battle_miss_sword",
                "hammer": "battle_miss_hammer",
                "staff": "battle_miss_staff",
                "bow": "battle_miss_bow",
                "crossbow": "battle_miss_bow",
                "spear": "battle_miss_staff",
                "halberd": "battle_miss_sword",
                "mace": "battle_miss_hammer",
                "claw": "battle_miss_sword",
                "fist": "battle_miss_fist",
                "default": "battle_miss_sword"
            }

            for weapon_type_key, fallback in fallback_misses.items():
                if weapon_type_key in weapon_type_lower:
                    suggested_miss = fallback
                    break

        # Ultimate fallback for miss
        if not suggested_miss:
            suggested_miss = "battle_miss_sword"

        return {"hit": suggested_hit, "miss": suggested_miss}

    def get_all_available_sounds(self) -> Dict[str, List[str]]:
        """Get all available battle sounds organized by type"""
        all_sounds = {}

        # Extract sounds from the loaded DrwSound.lua data
        if hasattr(self, 'lua_data') and self.lua_data:
            for sound_name, sound_data in self.lua_data.items():
                if sound_name.startswith("battle_hit_") or sound_name.startswith("battle_miss_"):
                    sound_type = "hit" if "hit_" in sound_name else "miss"
                    if sound_type not in all_sounds:
                        all_sounds[sound_type] = []

                    if isinstance(sound_data, dict) and "File" in sound_data:
                        files = sound_data["File"]
                        if isinstance(files, list):
                            all_sounds[sound_type].extend(files)
                        else:
                            all_sounds[sound_type].append(files)
                    else:
                        all_sounds[sound_type].append(sound_name)

        # If no Lua data loaded, return the mapped sounds
        if not all_sounds:
            # Flatten the sound mappings
            for weapon_type, sounds in self.sound_mappings.items():
                for sound_type, sound_list in sounds.items():
                    if sound_type not in all_sounds:
                        all_sounds[sound_type] = []
                    all_sounds[sound_type].extend(sound_list)

        # Remove duplicates and sort
        for sound_type in all_sounds:
            unique_sounds = set()
            for sound in all_sounds[sound_type]:
                if isinstance(sound, (tuple, list)):
                    # Flatten tuples/lists
                    for s in sound:
                        if isinstance(s, (tuple, list)):
                            unique_sounds.update(str(item) for item in s)
                        else:
                            unique_sounds.add(str(s))
                else:
                    unique_sounds.add(str(sound))
            all_sounds[sound_type] = sorted(unique_sounds)

        return all_sounds

    def get_sound_categories(self) -> List[str]:
        """Get available sound categories for filtering"""
        categories = []
        for sound_name in self.get_all_available_sounds().get("hit", []):
            if "battle_hit_" in sound_name:
                weapon_type = sound_name.replace("battle_hit_", "")
                if weapon_type not in categories:
                    categories.append(weapon_type)

        # Add common categories
        categories.extend(["sword", "axe", "hammer", "dagger", "staff", "bow", "crossbow"])
        return sorted(list(set(categories)))


class WeaponSoundSelectionDialog(QDialog):
    """Dialog for selecting weapon sounds with preview and categorization"""

    def __init__(
        self,
        weapon_type: str = "sword",
        hands: str = "1H",
        current_hit: str = "",
        current_miss: str = "",
        parent=None,
    ):
        super().__init__(parent)
        self.setWindowTitle("Select Weapon Sounds")
        self.setModal(True)
        self.resize(700, 500)

        self.weapon_type = weapon_type
        self.hands = hands
        self.sound_manager = WeaponSoundManager()

        self.selected_hit = current_hit
        self.selected_miss = current_miss

        # Audio preview properties
        self.current_preview_sound = None
        self.preview_volume = 0.7  # Default volume
        self.preview_pitch = 1.0   # Default pitch (1.0 = normal)
        self.is_preview_playing = False

        self._setup_ui()
        self._populate_sounds()

    def _setup_ui(self):
        """Setup the enhanced user interface"""
        layout = QVBoxLayout()

        # Weapon info
        info_group = QGroupBox("Weapon Information")
        info_layout = QVBoxLayout()
        info_layout.addWidget(QLabel(f"Weapon Type: {self.weapon_type.title()}"))
        info_layout.addWidget(QLabel(f"Hands: {self.hands}"))

        # Add auto-assigned sounds info
        auto_sounds = self.sound_manager.suggest_sounds(self.weapon_type, self.hands)
        auto_hit = auto_sounds.get('hit', 'None')
        auto_miss = auto_sounds.get('miss', 'None')
        info_layout.addWidget(QLabel(f"Suggested Hit: {auto_hit}"))
        info_layout.addWidget(QLabel(f"Suggested Miss: {auto_miss}"))

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Audio Preview Controls
        if PYGAME_AVAILABLE:
            preview_group = QGroupBox("Audio Preview Controls")
            preview_layout = QVBoxLayout()

            # Volume control
            volume_layout = QHBoxLayout()
            volume_layout.addWidget(QLabel("Volume:"))
            self.volume_slider = QSlider(Qt.Horizontal)
            self.volume_slider.setRange(0, 100)
            self.volume_slider.setValue(int(self.preview_volume * 100))
            self.volume_slider.setTickPosition(QSlider.TicksBelow)
            self.volume_slider.setTickInterval(10)
            self.volume_slider.valueChanged.connect(self.on_volume_changed)
            volume_layout.addWidget(self.volume_slider)
            self.volume_label = QLabel(f"{int(self.preview_volume * 100)}%")
            volume_layout.addWidget(self.volume_label)
            volume_layout.addStretch()

            preview_layout.addLayout(volume_layout)

            # Pitch control
            pitch_layout = QHBoxLayout()
            pitch_layout.addWidget(QLabel("Pitch:"))
            self.pitch_slider = QSlider(Qt.Horizontal)
            self.pitch_slider.setRange(50, 200)  # 0.5x to 2.0x pitch
            self.pitch_slider.setValue(int(self.preview_pitch * 100))
            self.pitch_slider.setTickPosition(QSlider.TicksBelow)
            self.pitch_slider.setTickInterval(25)
            self.pitch_slider.valueChanged.connect(self.on_pitch_changed)
            pitch_layout.addWidget(self.pitch_slider)
            self.pitch_label = QLabel("1.0x")
            pitch_layout.addWidget(self.pitch_label)
            pitch_layout.addStretch()

            preview_layout.addLayout(pitch_layout)

            # Preview buttons
            preview_buttons_layout = QHBoxLayout()
            self.preview_hit_btn = QPushButton("🔊 Preview Hit")
            self.preview_hit_btn.clicked.connect(self.preview_hit_sound)
            self.preview_hit_btn.setEnabled(False)
            preview_buttons_layout.addWidget(self.preview_hit_btn)

            self.preview_miss_btn = QPushButton("🔊 Preview Miss")
            self.preview_miss_btn.clicked.connect(self.preview_miss_sound)
            self.preview_miss_btn.setEnabled(False)
            preview_buttons_layout.addWidget(self.preview_miss_btn)

            self.stop_preview_btn = QPushButton("⏹ Stop Preview")
            self.stop_preview_btn.clicked.connect(self.stop_preview)
            self.stop_preview_btn.setEnabled(False)
            preview_buttons_layout.addWidget(self.stop_preview_btn)

            preview_layout.addLayout(preview_buttons_layout)

            # Preview status
            self.preview_status_label = QLabel("Ready for preview")
            self.preview_status_label.setStyleSheet("color: #666; font-style: italic;")
            preview_layout.addWidget(self.preview_status_label)

            # Audio settings
            settings_layout = QHBoxLayout()
            self.loop_preview_checkbox = QPushButton("🔁 Loop Preview")
            self.loop_preview_checkbox.setCheckable(True)
            self.loop_preview_checkbox.setChecked(False)
            settings_layout.addWidget(self.loop_preview_checkbox)

            self.auto_preview_checkbox = QPushButton("▶ Auto-preview on Selection")
            self.auto_preview_checkbox.setCheckable(True)
            self.auto_preview_checkbox.setChecked(False)
            self.auto_preview_checkbox.setToolTip("Automatically play sound when selected")
            settings_layout.addWidget(self.auto_preview_checkbox)

            settings_layout.addStretch()
            preview_layout.addLayout(settings_layout)

            preview_group.setLayout(preview_layout)
            layout.addWidget(preview_group)

        # Tab widget for different sound selection modes
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Tab 1: Quick Selection (current functionality)
        self._setup_quick_selection_tab()

        # Tab 2: Advanced Browser
        self._setup_advanced_browser_tab()

        # Tab 3: Category Browser
        self._setup_category_browser_tab()

        # Preview area
        preview_group = QGroupBox("Sound Preview")
        preview_layout = QVBoxLayout()

        # Sound details
        self.sound_details = QTextEdit()
        self.sound_details.setMaximumHeight(100)
        self.sound_details.setReadOnly(True)
        preview_layout.addWidget(self.sound_details)

        # Sound info labels
        self.current_sounds_label = QLabel("Current Selections: None")
        preview_layout.addWidget(self.current_sounds_label)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self.setLayout(layout)

    def _setup_quick_selection_tab(self):
        """Setup quick selection tab with recommended sounds"""
        quick_widget = QWidget()
        layout = QVBoxLayout()

        # Recommended sounds section
        recommended_group = QGroupBox("Recommended Sounds")
        recommended_layout = QVBoxLayout()

        self.quick_hit_combo = QComboBox()
        self.quick_hit_combo.setMinimumWidth(300)
        self.quick_hit_combo.currentTextChanged.connect(self.on_quick_hit_sound_changed)
        recommended_layout.addWidget(QLabel("Hit Sound:"))
        recommended_layout.addWidget(self.quick_hit_combo)

        self.quick_miss_combo = QComboBox()
        self.quick_miss_combo.setMinimumWidth(300)
        self.quick_miss_combo.currentTextChanged.connect(self.on_quick_miss_sound_changed)
        recommended_layout.addWidget(QLabel("Miss Sound:"))
        recommended_layout.addWidget(self.quick_miss_combo)

        recommended_group.setLayout(recommended_layout)
        layout.addWidget(recommended_group)

        quick_widget.setLayout(layout)
        self.tab_widget.addTab(quick_widget, "Quick Selection")

    def _setup_advanced_browser_tab(self):
        """Setup advanced browser tab with all sounds"""
        browser_widget = QWidget()
        layout = QVBoxLayout()

        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search sounds...")
        self.search_edit.textChanged.connect(self.filter_sounds)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)

        # All sounds lists
        sounds_layout = QHBoxLayout()

        # Hit sounds
        hit_group = QGroupBox("Hit Sounds")
        hit_layout = QVBoxLayout()
        self.hit_list = QListWidget()
        self.hit_list.setMaximumHeight(200)
        self.hit_list.itemDoubleClicked.connect(self.on_hit_list_double_clicked)
        hit_layout.addWidget(self.hit_list)
        hit_group.setLayout(hit_layout)

        # Miss sounds
        miss_group = QGroupBox("Miss Sounds")
        miss_layout = QVBoxLayout()
        self.miss_list = QListWidget()
        self.miss_list.setMaximumHeight(200)
        self.miss_list.itemDoubleClicked.connect(self.on_miss_list_double_clicked)
        miss_layout.addWidget(self.miss_list)
        miss_group.setLayout(miss_layout)

        sounds_layout.addWidget(hit_group)
        sounds_layout.addWidget(miss_group)

        layout.addLayout(sounds_layout)
        browser_widget.setLayout(layout)
        self.tab_widget.addTab(browser_widget, "Advanced Browser")

    def _setup_category_browser_tab(self):
        """Setup category browser tab"""
        browser_widget = QWidget()
        layout = QVBoxLayout()

        # Category selection
        category_layout = QHBoxLayout()
        category_layout.addWidget(QLabel("Weapon Type:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All"] + self.sound_manager.get_sound_categories())
        self.category_combo.currentTextChanged.connect(self.on_category_changed)
        category_layout.addWidget(self.category_combo)
        layout.addLayout(category_layout)

        # Category sounds display
        self.category_sounds_list = QListWidget()
        self.category_sounds_list.setMaximumHeight(250)
        layout.addWidget(self.category_sounds_list)

        browser_widget.setLayout(layout)
        self.tab_widget.addTab(browser_widget, "Category Browser")

    def _populate_sounds(self):
        """Populate sound widgets with available sounds"""
        sounds = self.sound_manager.get_weapon_sounds(self.weapon_type)

        # Populate quick selection combos
        self.quick_hit_combo.clear()
        if "hit" in sounds and sounds["hit"]:
            self.quick_hit_combo.addItems(sounds["hit"])

        self.quick_miss_combo.clear()
        if "miss" in sounds and sounds["miss"]:
            self.quick_miss_combo.addItems(sounds["miss"])

        # Set current selections
        if self.selected_hit:
            index = self.quick_hit_combo.findText(self.selected_hit)
            if index >= 0:
                self.quick_hit_combo.setCurrentIndex(index)

        if self.selected_miss:
            index = self.quick_miss_combo.findText(self.selected_miss)
            if index >= 0:
                self.quick_miss_combo.setCurrentIndex(index)

        # Populate advanced browser with all sounds
        all_sounds = self.sound_manager.get_all_available_sounds()
        for sound in all_sounds.get("hit", []):
            self.hit_list.addItem(sound)
        for sound in all_sounds.get("miss", []):
            self.miss_list.addItem(sound)

        # Populate category browser
        self.on_category_changed("All")  # Load all sounds initially

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
            preview_text += (
                "These sounds are referenced from the game's DrwSound.lua file."
            )

        self.sound_details.setPlainText(preview_text)
        self.current_sounds_label.setText(
            f"Current Selections: Hit={self.selected_hit or 'None'}, Miss={self.selected_miss or 'None'}"
        )

    def on_quick_hit_sound_changed(self, sound_name: str):
        """Handle quick hit sound selection change"""
        self.selected_hit = sound_name
        self._update_preview()

    def on_quick_miss_sound_changed(self, sound_name: str):
        """Handle quick miss sound selection change"""
        self.selected_miss = sound_name
        self._update_preview()

    def on_hit_list_double_clicked(self, item: QListWidgetItem):
        """Handle hit sound selection from advanced browser"""
        sound_name = item.text()
        self.selected_hit = sound_name
        self._update_preview()

    def on_miss_list_double_clicked(self, item: QListWidgetItem):
        """Handle miss sound selection from advanced browser"""
        sound_name = item.text()
        self.selected_miss = sound_name
        self._update_preview()

    def filter_sounds(self, search_text: str):
        """Filter sounds in advanced browser"""
        search_lower = search_text.lower()

        # Clear lists
        self.hit_list.clear()
        self.miss_list.clear()

        if not search_text:
            # Load all sounds
            all_sounds = self.sound_manager.get_all_available_sounds()
        else:
            # Filter sounds
            all_sounds = self.sound_manager.get_all_available_sounds()
            for sound_type in all_sounds:
                all_sounds[sound_type] = [
                    sound for sound in all_sounds[sound_type]
                    if search_lower in sound.lower()
                ]

        # Populate filtered lists
        for sound in all_sounds.get("hit", []):
            self.hit_list.addItem(sound)
        for sound in all_sounds.get("miss", []):
            self.miss_list.addItem(sound)

    def on_category_changed(self, category: str):
        """Handle category selection change"""
        all_sounds = self.sound_manager.get_all_available_sounds()
        self.category_sounds_list.clear()

        if category == "All":
            # Show all sounds
            for sound_type in all_sounds:
                for sound in all_sounds[sound_type]:
                    item = QListWidgetItem(f"{sound_type.upper()}: {sound}")
                    self.category_sounds_list.addItem(item)
        else:
            # Show category-specific sounds
            category_lower = category.lower()
            for sound_type in all_sounds:
                for sound in all_sounds[sound_type]:
                    if category_lower in sound.lower():
                        item = QListWidgetItem(f"{sound_type.upper()}: {sound}")
                        self.category_sounds_list.addItem(item)

    def get_selected_sounds(self) -> Tuple[str, str]:
        """Get the selected hit and miss sounds"""
        return self.selected_hit, self.selected_miss

    def on_volume_changed(self, value: int):
        """Handle volume slider change"""
        self.preview_volume = value / 100.0
        self.volume_label.setText(f"{value}%")

        # Update pygame mixer volume if sound is playing
        if PYGAME_AVAILABLE and self.current_preview_sound:
            self.current_preview_sound.set_volume(self.preview_volume)

    def on_pitch_changed(self, value: int):
        """Handle pitch slider change"""
        self.preview_pitch = value / 100.0
        self.pitch_label.setText(f"{self.preview_pitch:.1f}x")

    def preview_hit_sound(self):
        """Preview the currently selected hit sound"""
        if not PYGAME_AVAILABLE:
            QMessageBox.warning(self, "Audio Preview",
                              "Pygame not available - audio preview disabled")
            return

        current_hit = self.quick_hit_combo.currentText()
        if not current_hit or current_hit == "None":
            self.preview_status_label.setText("No hit sound selected")
            return

        self._play_sound_preview(current_hit, "hit")

    def preview_miss_sound(self):
        """Preview the currently selected miss sound"""
        if not PYGAME_AVAILABLE:
            QMessageBox.warning(self, "Audio Preview",
                              "Pygame not available - audio preview disabled")
            return

        current_miss = self.quick_miss_combo.currentText()
        if not current_miss or current_miss == "None":
            self.preview_status_label.setText("No miss sound selected")
            return

        self._play_sound_preview(current_miss, "miss")

    def _play_sound_preview(self, sound_name: str, sound_type: str):
        """Play a sound preview with error handling"""
        try:
            # Stop any currently playing sound
            self.stop_preview()

            # Find the sound file path
            sound_path = self._find_sound_file(sound_name)
            if not sound_path:
                self.preview_status_label.setText(f"Sound file not found: {sound_name}")
                return

            # Load and play the sound with pitch adjustment
            self.current_preview_sound = pygame.mixer.Sound(sound_path)
            self.current_preview_sound.set_volume(self.preview_volume)

            # Apply pitch adjustment (pygame limitation - pitch is simulated)
            if self.preview_pitch != 1.0:
                # For pitch shifting, we would need more advanced audio processing
                # For now, we'll indicate the pitch in the status
                pitch_text = f" (pitch: {self.preview_pitch:.1f}x)"
            else:
                pitch_text = ""

            self.current_preview_sound.play()

            self.is_preview_playing = True
            self.preview_status_label.setText(f"Playing {sound_type}: {sound_name}{pitch_text}")
            self.stop_preview_btn.setEnabled(True)

            # Adjust timer based on pitch (higher pitch = shorter perceived duration)
            sound_length = self.current_preview_sound.get_length() * 1000  # Convert to milliseconds
            adjusted_length = int(sound_length / self.preview_pitch)
            QTimer.singleShot(adjusted_length + 100, self.on_sound_finished)

        except Exception as e:
            self.preview_status_label.setText(f"Error playing sound: {str(e)}")
            QMessageBox.critical(self, "Audio Preview Error",
                               f"Could not play sound '{sound_name}':\n{str(e)}")

    def stop_preview(self):
        """Stop the currently playing preview"""
        if self.current_preview_sound:
            self.current_preview_sound.stop()
            self.current_preview_sound = None

        self.is_preview_playing = False
        self.preview_status_label.setText("Preview stopped")
        self.stop_preview_btn.setEnabled(False)

    def on_sound_finished(self):
        """Called when a sound preview finishes playing"""
        self.is_preview_playing = False
        self.current_preview_sound = None
        self.preview_status_label.setText("Ready for preview")
        self.stop_preview_btn.setEnabled(False)

    def _find_sound_file(self, sound_name: str) -> Optional[str]:
        """Find the actual sound file path for a given sound name"""
        # Try to find the sound file in common locations
        base_paths = [
            "../../OriginalGameFiles/sound/",
            "../../../OriginalGameFiles/sound/",
            "OriginalGameFiles/sound/",
            Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles/sound/"
        ]

        # Common sound file extensions
        extensions = [".wav", ".ogg", ".mp3", ".flac"]

        for base_path in base_paths:
            base_path = Path(base_path)
            if base_path.exists():
                # Try direct match
                for ext in extensions:
                    sound_path = base_path / f"{sound_name}{ext}"
                    if sound_path.exists():
                        return str(sound_path)

                # Try in subdirectories
                for ext in extensions:
                    for sound_dir in base_path.rglob("*"):
                        if sound_dir.is_dir():
                            sound_path = sound_dir / f"{sound_name}{ext}"
                            if sound_path.exists():
                                return str(sound_path)

        return None

    def on_quick_hit_sound_changed(self, sound_name: str):
        """Handle hit sound selection change"""
        self.selected_hit = sound_name if sound_name != "None" else ""
        enabled = bool(sound_name and sound_name != "None")
        self.preview_hit_btn.setEnabled(enabled)

        # Auto-preview if enabled
        if enabled and hasattr(self, 'auto_preview_checkbox') and self.auto_preview_checkbox.isChecked():
            self.preview_hit_sound()

    def on_quick_miss_sound_changed(self, sound_name: str):
        """Handle miss sound selection change"""
        self.selected_miss = sound_name if sound_name != "None" else ""
        enabled = bool(sound_name and sound_name != "None")
        self.preview_miss_btn.setEnabled(enabled)

        # Auto-preview if enabled
        if enabled and hasattr(self, 'auto_preview_checkbox') and self.auto_preview_checkbox.isChecked():
            self.preview_miss_sound()


# Integration function for weapon forge
def create_sound_selector_widget(
    weapon_type: str, hands: str = "1H", current_hit: str = "", current_miss: str = ""
) -> QWidget:
    """Create a sound selector widget for integration in weapon forge"""

    from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton

    widget = QWidget()
    layout = QHBoxLayout()

    # Sound display
    hit_label = QLabel(f"Hit: {current_hit or 'None'}")
    miss_label = QLabel(f"Miss: {current_miss or 'None'}")

    def open_sound_dialog():
        dialog = WeaponSoundSelectionDialog(
            weapon_type, hands, current_hit, current_miss
        )
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
def auto_assign_weapon_sounds(
    weapon_type: str, weapon_type_name: str, hands: str
) -> Dict[str, str]:
    """Automatically assign appropriate sounds based on weapon type"""
    manager = WeaponSoundManager()
    return manager.suggest_sounds(weapon_type, hands)
