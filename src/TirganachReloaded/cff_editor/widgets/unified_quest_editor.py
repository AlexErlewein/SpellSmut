#!/usr/bin/env python3
"""
Unified Quest Editor

A comprehensive quest editor combining the best features from:
- Darius Almanach (quest browsing, data structure)
- Enhanced Quest Creation Wizard (guided quest creation)
- Visual Dialogue Editor (dialogue flow management)
- Quest Validator (comprehensive validation)

Features:
- Tabbed interface for easy navigation
- Real-time validation
- Quest browser with search and filtering
- Visual dialogue editor integration
- Direct CFF and Lua export
- Quest preview functionality
"""

import sys
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTabWidget,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTextEdit,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QLabel,
    QGroupBox,
    QFormLayout,
    QListWidget,
    QListWidgetItem,
    QMessageBox,
    QProgressBar,
    QStatusBar,
    QMenuBar,
    QToolBar,
    QDialog,
    QDialogButtonBox,
    QCheckBox,
    QRadioButton,
    QButtonGroup,
    QFrame,
    QScrollArea,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QAbstractItemView,
    QTreeWidgetItemIterator,
    QInputDialog,
)
from PySide6.QtCore import (
    Qt,
    Signal,
    Slot,
    QThread,
    QTimer,
    QSettings,
    QSize,
    QPoint,
    QSortFilterProxyModel,
    QItemSelectionModel,
)
from PySide6.QtGui import (
    QFont,
    QPixmap,
    QIcon,
    QAction,
    QKeySequence,
    QPalette,
    QColor,
    QTextCursor,
    QIntValidator,
)

# Add to path with better error handling
try:
    script_path = Path(__file__).resolve()
    # script_path is in: quest-wizard/src/TirganachReloaded/cff_editor/widgets/
    # We need to add quest-wizard/src to Python path
    src_dir = (
        script_path.parent.parent.parent
    )  # widgets -> cff_editor -> TirganachReloaded -> src

    if src_dir.exists() and (src_dir / "TirganachReloaded").exists():
        sys.path.insert(0, str(src_dir))
    else:
        # Try alternative path calculation
        cwd = Path.cwd()
        if cwd.name == "widgets":
            calculated_src = cwd.parent.parent.parent
            if calculated_src.exists():
                sys.path.insert(0, str(calculated_src))
except Exception as e:
    print(f"Warning: Could not set up Python path: {e}")
    # Try fallback
    try:
        import os

        # Add parent directories to path as fallback
        current_dir = Path(__file__).parent
        for _ in range(4):  # Go up 4 levels
            current_dir = current_dir.parent
            if (current_dir / "TirganachReloaded").exists():
                sys.path.insert(0, str(current_dir))
                break
    except Exception:
        pass

# Try imports with graceful fallback
try:
    from TirganachReloaded.cff_editor.data_model import CFFDataModel
    from TirganachReloaded.cff_editor.logging_config import (
        configure_logging,
        get_logger,
    )
    from TirganachReloaded.cff_editor.models.quest_models import (
        EnhancedQuestData,
        QuestReward,
        Dialogue,
        MapLocation,
    )

    CFF_AVAILABLE = True
except ImportError as e:
    print(f"Warning: CFF components not available: {e}")
    CFF_AVAILABLE = False
    # Create stub classes
    CFFDataModel = None
    EnhancedQuestData = None
    QuestReward = None
    Dialogue = None
    MapLocation = None

# Import optional components
DIALOGUE_EDITOR_AVAILABLE = False
QUEST_VALIDATOR_AVAILABLE = False
VISUAL_DIALOGUE_EDITOR_AVAILABLE = False

try:
    from .dialogue_editor import DialogueTreeEditor

    DIALOGUE_EDITOR_AVAILABLE = True
except ImportError:
    DialogueTreeEditor = None

try:
    from .quest_validator import QuestValidator

    QUEST_VALIDATOR_AVAILABLE = True
except ImportError:
    QuestValidator = None

# Visual dialogue widget will be imported dynamically after directory change
VISUAL_DIALOGUE_EDITOR_AVAILABLE = True  # Assume available, will verify at runtime

# Platform names from Darius Almanach
PLATFORM_NAMES = {
    "P1": "Liannon",
    "P2": "Eloni",
    "P3": "Leafshade",
    "P4": "Wildland Pass",
    "P5": "Shiel",
    "P6": "Wildland Pass / Greyfell area",
    "P7": "Ice Gate",
    "P8": "Underhall",
    "P10": "Iron Fields",
    "P11": "The Shiel",
    "P12": "峡谷",
    "P15": "Desert / Burning Sands",
    "P16": "Whisper",
    "P17": "Tirganach",
    "P19": "Dun Mora",
    "P23": "The Gorge",
    "P25": "Godmark / Mountains",
    "P27": "Urgath",
    "P30": "Breathing Forest",
    "P32": "Soul Forge",
    "P63": "Greyfell",
    "P101": "Tutorial",
    "P105": "Tirganach",
    "P107": "Encounter Map",
    "P108": "Encounter Map",
    "P109": "Warzone",
    "P110": "Ghost Watch",
    "P111": "Shadow Realm",
    "P113": "Underground",
    "P115": "Dragon Storm",
}


class QuestBrowser(QWidget):
    """Quest browser with search, filtering, and hierarchy display"""

    quest_selected = Signal(int)  # quest_id
    quest_created = Signal(dict)  # quest_data
    quest_updated = Signal(int, dict)  # quest_id, quest_data

    def __init__(self, item_loader=None, parent=None):
        super().__init__(parent)
        self.item_loader = item_loader
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the quest browser UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Search and filter bar
        search_frame = QFrame()
        search_layout = QHBoxLayout(search_frame)
        search_layout.setContentsMargins(5, 5, 5, 5)

        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name, ID, or description...")
        search_layout.addWidget(self.search_edit)

        self.filter_combo = QComboBox()
        self.filter_combo.addItems(
            [
                "All Quests",
                "Main Quests",
                "Side Quests",
                "Custom Quests (9000+)",
                "With Dialogues",
                "Without Dialogues",
            ]
        )
        search_layout.addWidget(self.filter_combo)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.setMaximumWidth(80)
        search_layout.addWidget(self.refresh_btn)

        self.new_quest_btn = QPushButton("New Quest")
        self.new_quest_btn.setMaximumWidth(100)
        self.new_quest_btn.setStyleSheet(
            "QPushButton { background-color: #27ae60; color: white; font-weight: bold; }"
        )
        search_layout.addWidget(self.new_quest_btn)

        layout.addWidget(search_frame)

        # Quest tree
        self.quest_tree = QTreeWidget()
        self.quest_tree.setHeaderLabels(["Quest Name", "ID", "Location", "Type"])
        self.quest_tree.setAlternatingRowColors(True)
        self.quest_tree.setSortingEnabled(True)
        self.quest_tree.setRootIsDecorated(True)
        layout.addWidget(self.quest_tree)

        # Status label
        self.status_label = QLabel("No quests loaded")
        self.status_label.setStyleSheet(
            "color: #666; font-style: italic; padding: 5px;"
        )
        layout.addWidget(self.status_label)

    def _setup_connections(self):
        """Setup signal connections"""
        self.search_edit.textChanged.connect(self._on_search_changed)
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        self.refresh_btn.clicked.connect(self.refresh_quests)
        self.new_quest_btn.clicked.connect(self._create_new_quest)
        self.quest_tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.quest_tree.itemDoubleClicked.connect(self._on_item_double_clicked)

    def load_quests(self, quest_data: Dict[int, Dict]):
        """Load quest data into browser"""
        self.quest_data = quest_data.copy()
        self.filtered_quests = quest_data.copy()
        self._populate_tree()
        self._update_status()

    def _populate_tree(self):
        """Populate the quest tree"""
        self.quest_tree.clear()

        if not self.filtered_quests:
            return

        # Create items
        items_by_id = {}
        root_items = []

        for quest_id, quest_info in sorted(self.filtered_quests.items()):
            name = quest_info.get("name", f"Quest {quest_id}")
            location = self._get_quest_location(quest_info)
            quest_type = self._get_quest_type(quest_id, quest_info)

            item = QTreeWidgetItem([name, str(quest_id), location, quest_type])
            item.setData(0, Qt.UserRole, quest_id)

            # Styling based on quest type
            if quest_type == "Main Quest":
                item.setFont(0, QFont("Arial", 9, QFont.Bold))
                item.setForeground(0, QColor(41, 128, 185))  # Blue
            elif quest_type.startswith("Custom"):
                item.setForeground(0, QColor(39, 174, 96))  # Green

            items_by_id[quest_id] = item

            # Check if it's a root quest (no parent in current data)
            parent_id = quest_info.get("parent_id", 0)
            if parent_id == 0 or parent_id not in self.filtered_quests:
                root_items.append(item)

        # Build hierarchy
        for quest_id, quest_info in self.filtered_quests.items():
            parent_id = quest_info.get("parent_id", 0)
            if parent_id in items_by_id and quest_id in items_by_id:
                parent_item = items_by_id[parent_id]
                child_item = items_by_id[quest_id]
                parent_item.addChild(child_item)

        # Add root items to tree
        for item in root_items:
            self.quest_tree.addTopLevelItem(item)

        # Expand first level
        self.quest_tree.expandToDepth(0)

        # Resize columns
        for i in range(self.quest_tree.columnCount()):
            self.quest_tree.resizeColumnToContents(i)

    def _on_search_changed(self, text):
        """Handle search text change"""
        self._apply_filters()

    def _on_filter_changed(self):
        """Handle filter change"""
        self._apply_filters()

    def _apply_filters(self):
        """Apply search and filter"""
        search_text = self.search_edit.text().lower().strip()
        filter_type = self.filter_combo.currentText()

        self.filtered_quests = {}

        for quest_id, quest_info in self.quest_data.items():
            # Search filter
            if search_text:
                name = quest_info.get("name", "").lower()
                description = quest_info.get("description", "").lower()
                quest_id_str = str(quest_id)

                if not (
                    search_text in name
                    or search_text in description
                    or search_text in quest_id_str
                ):
                    continue

            # Type filter
            if filter_type != "All Quests":
                quest_type = self._get_quest_type(quest_id, quest_info)

                if filter_type == "Main Quests" and quest_type != "Main Quest":
                    continue
                elif filter_type == "Side Quests" and quest_type not in [
                    "Side Quest",
                    "Sub-Quest",
                ]:
                    continue
                elif filter_type == "Custom Quests (9000+)" and quest_id < 9000:
                    continue
                elif filter_type == "With Dialogues" and not quest_info.get(
                    "dialogues"
                ):
                    continue
                elif filter_type == "Without Dialogues" and quest_info.get("dialogues"):
                    continue

            self.filtered_quests[quest_id] = quest_info

        self._populate_tree()
        self._update_status()

    def _on_selection_changed(self):
        """Handle tree selection change"""
        current_items = self.quest_tree.selectedItems()
        if current_items:
            quest_id = current_items[0].data(0, Qt.UserRole)
            parent = self.parent()
            if quest_id and parent and hasattr(parent, "current_quest_id"):
                if quest_id != parent.current_quest_id:
                    parent.current_quest_id = quest_id
                    self.quest_selected.emit(quest_id)

    def _on_item_double_clicked(self, item, column):
        """Handle double click - edit quest"""
        quest_id = item.data(0, Qt.UserRole)
        if quest_id:
            self.quest_selected.emit(quest_id)

    def _get_quest_location(self, quest_info: Dict) -> str:
        """Get quest location display name"""
        # Try various location fields
        location = None

        if "map_locations" in quest_info and quest_info["map_locations"]:
            location = (
                quest_info["map_locations"][0].get("name")
                if quest_info["map_locations"][0]
                else None
            )
        elif "platform" in quest_info:
            platform = quest_info["platform"]
            location = PLATFORM_NAMES.get(platform, platform)
        elif "platform_name" in quest_info:
            location = quest_info["platform_name"]

        return location or "Unknown"

    def _get_quest_type(self, quest_id: int, quest_info: Dict) -> str:
        """Get quest type classification"""
        if quest_id >= 9000:
            return "Custom Quest"
        elif quest_info.get("parent_id", 0) == 0:
            return "Main Quest"
        else:
            return "Side Quest"

    def _update_status(self):
        """Update status label"""
        total = len(self.quest_data)
        filtered = len(self.filtered_quests)

        if filtered == total:
            self.status_label.setText(f"{total} quests total")
        else:
            self.status_label.setText(f"{filtered} of {total} quests (filtered)")

    def _create_new_quest(self):
        """Create a new quest immediately with placeholder data"""
        # Generate new quest ID from parent UnifiedQuestEditor
        parent = self.parent()
        if parent and hasattr(parent, "next_custom_quest_id"):
            quest_id = parent.next_custom_quest_id
            parent.next_custom_quest_id += 1
        else:
            # Fallback if parent doesn't have the attribute
            quest_id = 10000

        # Create quest data with placeholder name
        quest_data = {
            "id": quest_id,
            "name": f"New Quest {quest_id}",
            "description": "Click to edit this quest...",
            "type": "Side Quest",
            "location": "Liannon",
            "suggested_level": 1,
            "is_custom": True,
            "created_at": "2025-11-08",  # Current date
            "objectives": [],
            "rewards": [],
            "dialogues": [],
            "script": "",
            "prerequisites": [],
        }

        # Add to quest data
        self.quest_data[quest_id] = quest_data
        self.filtered_quests[quest_id] = quest_data

        # Refresh display
        self._populate_tree()
        self._update_status()

        # Select the new quest immediately
        self._select_quest_by_id(quest_id)

        # Emit signal
        self.quest_created.emit(quest_data)

    def _select_quest_by_id(self, quest_id: int):
        """Select a quest by its ID"""
        for i in range(self.quest_tree.topLevelItemCount()):
            item = self.quest_tree.topLevelItem(i)
            if item.data(0, Qt.UserRole) == quest_id:
                self.quest_tree.setCurrentItem(item)
                self._on_selection_changed()
                return

    def update_quest(self, quest_id: int, quest_data: dict):
        """Update quest data and refresh display"""
        if quest_id in self.quest_data:
            self.quest_data[quest_id] = quest_data
            self.filtered_quests[quest_id] = quest_data
            self._populate_tree()
            # Re-select the quest to maintain selection
            self._select_quest_by_id(quest_id)
            # Emit update signal
            self.quest_updated.emit(quest_id, quest_data)

    def refresh_quests(self):
        """Refresh quest display"""
        self._populate_tree()

    def select_quest(self, quest_id: int):
        """Select a specific quest in the tree"""
        # Find and select the quest
        iterator = QTreeWidgetItemIterator(self.quest_tree)
        while iterator.value():
            item = iterator.value()
            if item.data(0, Qt.UserRole) == quest_id:
                item.setSelected(True)
                self.quest_tree.scrollToItem(item)
                break
            iterator += 1


class QuestBasicInfoWidget(QWidget):
    """Basic quest information editor"""

    data_changed = Signal()

    def __init__(self, item_loader=None, parent=None):
        super().__init__(parent)
        self.item_loader = item_loader
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QFormLayout(self)
        layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)

        # Quest ID
        self.quest_id_spin = QSpinBox()
        self.quest_id_spin.setRange(1, 99999)
        self.quest_id_spin.setValue(9000)
        layout.addRow("Quest ID*:", self.quest_id_spin)

        # Quest name
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter quest name...")
        layout.addRow("Quest Name*:", self.name_edit)

        # Quest description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Enter quest description...")
        layout.addRow("Description:", self.description_edit)

        # Parent quest
        self.parent_combo = QComboBox()
        self.parent_combo.addItem("None (Main Quest)", 0)
        layout.addRow("Parent Quest:", self.parent_combo)

        # Order index
        self.order_spin = QSpinBox()
        self.order_spin.setRange(0, 99)
        self.order_spin.setValue(0)
        layout.addRow("Order Index:", self.order_spin)

        # Quest type
        self.type_group = QButtonGroup(self)
        type_layout = QHBoxLayout()

        self.main_radio = QRadioButton("Main")
        self.main_radio.setChecked(True)
        self.side_radio = QRadioButton("Side")
        self.sub_radio = QRadioButton("Sub")

        self.type_group.addButton(self.main_radio, 0)
        self.type_group.addButton(self.side_radio, 1)
        self.type_group.addButton(self.sub_radio, 2)

        type_layout.addWidget(self.main_radio)
        type_layout.addWidget(self.side_radio)
        type_layout.addWidget(self.sub_radio)
        type_layout.addStretch()

        layout.addRow("Quest Type:", type_layout)

    def _setup_connections(self):
        """Setup signal connections"""
        self.quest_id_spin.valueChanged.connect(self.data_changed)
        self.name_edit.textChanged.connect(self.data_changed)
        self.description_edit.textChanged.connect(self.data_changed)
        self.parent_combo.currentIndexChanged.connect(self.data_changed)
        self.order_spin.valueChanged.connect(self.data_changed)
        self.type_group.buttonClicked.connect(self.data_changed)

    def load_quest(self, quest_data: Dict):
        """Load quest data into form"""
        self.current_quest = quest_data

        self.quest_id_spin.setValue(quest_data.get("quest_id", 9000))
        self.name_edit.setText(quest_data.get("name", ""))
        self.description_edit.setPlainText(quest_data.get("description", ""))
        self.order_spin.setValue(quest_data.get("order_index", 0))

        # Set parent
        parent_id = quest_data.get("parent_id", 0)
        for i in range(self.parent_combo.count()):
            if self.parent_combo.itemData(i) == parent_id:
                self.parent_combo.setCurrentIndex(i)
                break

        # Set quest type based on parent
        if parent_id == 0:
            self.main_radio.setChecked(True)
        else:
            self.side_radio.setChecked(True)

    def get_quest_data(self) -> Dict:
        """Get quest data from form"""
        parent_id = self.parent_combo.currentData()

        # Determine quest type
        if parent_id == 0:
            quest_type = "Main Quest"
        elif self.type_group.checkedId() == 2:
            quest_type = "Sub-Quest"
        else:
            quest_type = "Side Quest"

        return {
            "quest_id": self.quest_id_spin.value(),
            "name": self.name_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "parent_id": parent_id,
            "order_index": self.order_spin.value(),
            "quest_type": quest_type,
        }

    def set_parent_quests(self, quest_data: Dict[int, Dict]):
        """Set available parent quests"""
        current_id = self.quest_id_spin.value()

        # Clear existing items except "None"
        while self.parent_combo.count() > 1:
            self.parent_combo.removeItem(1)

        # Add available quests (excluding current quest)
        for quest_id, quest_info in sorted(quest_data.items()):
            if quest_id != current_id:
                name = quest_info.get("name", f"Quest {quest_id}")
                self.parent_combo.addItem(f"{name} [{quest_id}]", quest_id)

    def clear_form(self):
        """Clear the form"""
        self.current_quest = None
        self.quest_id_spin.setValue(9000)
        self.name_edit.clear()
        self.description_edit.clear()
        self.parent_combo.setCurrentIndex(0)
        self.order_spin.setValue(0)
        self.main_radio.setChecked(True)


class QuestLocationWidget(QWidget):
    """Quest location and NPC assignment widget"""

    data_changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Setup the UI"""
        layout = QFormLayout(self)

        # Platform/location
        self.platform_combo = QComboBox()
        self.platform_combo.addItem("Select Location...", "")
        for code in sorted(
            PLATFORM_NAMES.keys(), key=lambda x: int(x[1:]) if x[1:].isdigit() else 999
        ):
            name = PLATFORM_NAMES[code]
            self.platform_combo.addItem(f"{name} ({code})", code)
        layout.addRow("Location*:", self.platform_combo)

        # Quest giver NPC selection with browser
        npc_giver_layout = QHBoxLayout()

        self.npc_id_edit = QLineEdit()
        self.npc_id_edit.setPlaceholderText("NPC ID (e.g., 100)")
        self.npc_id_edit.setValidator(QIntValidator(0, 99999))
        npc_giver_layout.addWidget(self.npc_id_edit)

        # Browse NPCs button
        browse_npc_btn = QPushButton("Browse NPCs...")
        browse_npc_btn.setToolTip("Open NPC browser to select quest giver")
        browse_npc_btn.clicked.connect(self._browse_quest_giver)
        npc_giver_layout.addWidget(browse_npc_btn)

        layout.addRow("Quest Giver NPC ID:", npc_giver_layout)

        # Quest giver name (for reference - auto-filled when browsing)
        self.npc_name_edit = QLineEdit()
        self.npc_name_edit.setPlaceholderText("NPC name (auto-filled from browser)")
        self.npc_name_edit.setReadOnly(True)  # Make read-only since it's auto-filled
        layout.addRow("Quest Giver Name:", self.npc_name_edit)

        # Additional locations (for multi-location quests)
        self.additional_locations = QListWidget()
        self.additional_locations.setMaximumHeight(100)
        layout.addRow("Additional Locations:", self.additional_locations)

        # Location buttons
        location_btn_layout = QHBoxLayout()
        add_location_btn = QPushButton("Add Location")
        add_location_btn.clicked.connect(self._add_additional_location)
        remove_location_btn = QPushButton("Remove Selected")
        remove_location_btn.clicked.connect(self._remove_additional_location)
        location_btn_layout.addWidget(add_location_btn)
        location_btn_layout.addWidget(remove_location_btn)
        location_btn_layout.addStretch()
        layout.addRow("", location_btn_layout)

    def _setup_connections(self):
        """Setup signal connections"""
        self.platform_combo.currentIndexChanged.connect(self.data_changed)
        self.npc_id_edit.textChanged.connect(self.data_changed)
        self.npc_name_edit.textChanged.connect(self.data_changed)

    def load_quest_data(self, quest_data: Dict):
        """Load quest location data"""
        # Platform
        platform = quest_data.get("platform")
        if platform:
            for i in range(self.platform_combo.count()):
                if self.platform_combo.itemData(i) == platform:
                    self.platform_combo.setCurrentIndex(i)
                    break

        # NPC info
        self.npc_id_edit.setText(str(quest_data.get("npc_id", "")))
        self.npc_name_edit.setText(quest_data.get("quest_giver_name", ""))

        # Additional locations
        self.additional_locations.clear()
        additional_locations = quest_data.get("additional_locations", [])
        for location in additional_locations:
            code = location.get("code", "")
            name = location.get("name", PLATFORM_NAMES.get(code, code))
            self.additional_locations.addItem(f"{name} ({code})")

    def get_location_data(self) -> Dict:
        """Get location data from form"""
        # Collect additional locations
        additional_locations = []
        for i in range(self.additional_locations.count()):
            item_text = self.additional_locations.item(i).text()
            # Extract platform code from format "Name (P1)"
            if "(" in item_text and ")" in item_text:
                code = item_text.split("(")[-1].rstrip(")")
                name = item_text.split("(")[0].strip()
                additional_locations.append({"code": code, "name": name})

        return {
            "platform": self.platform_combo.currentData(),
            "npc_id": int(self.npc_id_edit.text())
            if self.npc_id_edit.text().isdigit()
            else 0,
            "quest_giver_name": self.npc_name_edit.text().strip(),
            "additional_locations": additional_locations,
        }

    def _add_additional_location(self):
        """Add additional location"""
        platform = self.platform_combo.currentData()
        if platform:
            name = PLATFORM_NAMES.get(platform, platform)
            self.additional_locations.addItem(f"{name} ({platform})")

    def _remove_additional_location(self):
        """Remove selected additional location"""
        current_row = self.additional_locations.currentRow()
        if current_row >= 0:
            self.additional_locations.takeItem(current_row)

    def _browse_quest_giver(self):
        """Open NPC browser to select quest giver"""
        try:
            from TirganachReloaded.cff_editor.widgets.npc_browser_dialog import (
                choose_quest_giver,
            )

            npc = choose_quest_giver(parent=self)
            if npc:
                # Update NPC ID and name fields
                self.npc_id_edit.setText(str(npc.npc_id))
                self.npc_name_edit.setText(npc.name)

                self.logger.info(f"Selected quest giver: {npc.name} (ID: {npc.npc_id})")
                # Status message logged above (status_bar belongs to parent window)
        except ImportError as e:
            self.logger.error(f"Failed to import NPC browser: {e}")
            QMessageBox.warning(
                self,
                "NPC Browser Not Available",
                "The NPC browser could not be loaded. Please select NPC ID manually.",
            )


class QuestPreviewWidget(QWidget):
    """Quest preview widget showing how quest will appear in game"""

    def __init__(self, item_loader=None, parent=None):
        super().__init__(parent)
        self.item_loader = item_loader
        self._setup_ui()

    def _setup_ui(self):
        """Setup the preview UI"""
        layout = QVBoxLayout(self)

        # Preview title
        title_label = QLabel("Quest Preview")
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title_label)

        # Preview content
        self.preview_edit = QTextEdit()
        self.preview_edit.setReadOnly(True)
        # Apply dark theme for better readability and consistency
        self.preview_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
                border-radius: 4px;
                padding: 8px;
            }
        """)
        self.preview_edit.setHtml(
            "<p style='color: #ecf0f1;'>Select a quest to preview...</p>"
        )
        layout.addWidget(self.preview_edit)

    def update_preview(self, quest_data: Dict):
        """Update preview with quest data"""
        if not quest_data:
            self.preview_edit.setHtml("<p>No quest data to preview</p>")
            return

        # Generate HTML preview
        html = self._generate_preview_html(quest_data)
        self.preview_edit.setHtml(html)

    def _generate_preview_html(self, quest_data: Dict) -> str:
        """Generate HTML preview of quest"""
        html = (
            "<html><body style='font-family: Arial; font-size: 11pt; color: #ecf0f1;'>"
        )

        # Quest header
        quest_name = quest_data.get("name", "Unnamed Quest")
        quest_id = quest_data.get("quest_id", 0)
        html += f"<h2 style='color: #3498db; margin-bottom: 5px;'>{quest_name}</h2>"
        html += (
            f"<p style='color: #bdc3c7; margin-top: 0;'><b>Quest ID:</b> {quest_id}</p>"
        )

        # Description
        description = quest_data.get("description", "")
        if description:
            html += "<div style='background-color: #34495e; padding: 10px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #3498db;'>"
            html += f"<p style='color: #ecf0f1; margin: 0;'><b>Description:</b></p><p style='color: #ecf0f1; margin: 5px 0 0 0;'>{description}</p>"
            html += "</div>"

        # Location and NPC
        location_name = "Unknown"
        platform = quest_data.get("platform")
        if platform and platform in PLATFORM_NAMES:
            location_name = PLATFORM_NAMES[platform]

        npc_name = quest_data.get("quest_giver_name", "Unknown NPC")
        npc_id = quest_data.get("npc_id", 0)

        html += "<h3 style='color: #e74c3c; margin-top: 15px;'>Quest Details</h3>"
        html += "<ul>"
        html += f"<li><b>Location:</b> {location_name}</li>"
        html += f"<li><b>Quest Giver:</b> {npc_name} (ID: {npc_id})</li>"

        parent_id = quest_data.get("parent_id", 0)
        if parent_id > 0:
            html += f"<li><b>Parent Quest:</b> ID {parent_id}</li>"

        html += "</ul>"

        # Objectives
        objectives = quest_data.get("objectives", [])
        if objectives:
            html += "<h3 style='color: #34495e; margin-top: 15px;'>Objectives</h3>"
            html += "<ul>"
            for obj in objectives:
                if isinstance(obj, dict):
                    obj_text = obj.get("text", str(obj))
                    obj_type = obj.get("type", "other")
                    html += f"<li>[{obj_type.title()}] {obj_text}</li>"
                else:
                    html += f"<li>{obj}</li>"
            html += "</ul>"

        # Rewards
        rewards = quest_data.get("rewards", {})
        if rewards:
            html += "<h3 style='color: #27ae60; margin-top: 15px;'>Rewards</h3>"
            html += "<ul>"

            if isinstance(rewards, dict):
                xp = rewards.get("xp", 0)
                gold = rewards.get("gold", 0)
                silver = rewards.get("silver", 0)
                copper = rewards.get("copper", 0)
                items = rewards.get("items", [])

                if xp > 0:
                    html += f"<li><b>Experience:</b> {xp} XP</li>"
                if gold > 0:
                    html += f"<li><b>Gold:</b> {gold}</li>"
                if silver > 0 or copper > 0:
                    html += f"<li><b>Money:</b> {silver} Silver, {copper} Copper</li>"
                if items:
                    html += f"<li><b>Items ({len(items)}):</b></li>"
                    html += "<ul style='margin-left: 20px;'>"
                    for item in items:
                        if isinstance(item, dict):
                            item_id = item.get("id", 0)
                            count = item.get("count", 1)

                            # Try to resolve item name from item loader
                            item_name = f"Item {item_id}"  # Default fallback
                            if hasattr(self, "item_loader") and self.item_loader:
                                item_data = self.item_loader.get_item_by_id(item_id)
                                if item_data:
                                    item_name = item_data.get("name", f"Item {item_id}")

                            html += f"<li>{item_name} (ID: {item_id}) x{count}</li>"
                        else:
                            html += f"<li>{item}</li>"
                    html += "</ul>"
            else:
                html += f"<li>{rewards}</li>"

            html += "</ul>"

        # Dialogues (sample)
        dialogues = quest_data.get("dialogues", [])
        if dialogues:
            html += (
                "<h3 style='color: #8e44ad; margin-top: 15px;'>Dialogue Preview</h3>"
            )
            html += "<div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; border-left: 4px solid #8e44ad;'>"

            # Show first few dialogues as sample
            for i, dialogue in enumerate(dialogues[:3]):
                if isinstance(dialogue, dict):
                    speaker = dialogue.get("speaker", "NPC")
                    text = dialogue.get("text", "")
                else:
                    speaker = getattr(dialogue, "speaker", "NPC")
                    text = getattr(dialogue, "text", str(dialogue))

                speaker_color = "#3498db" if speaker.lower() == "player" else "#27ae60"
                html += (
                    f"<p><b style='color: {speaker_color};'>{speaker}:</b> {text}</p>"
                )

            if len(dialogues) > 3:
                html += f"<p><i>... and {len(dialogues) - 3} more dialogues</i></p>"

            html += "</div>"

        html += "</body></html>"
        return html


class UnifiedQuestEditor(QMainWindow):
    """Main unified quest editor window"""

    def __init__(self):
        super().__init__()

        # Initialize components
        self.logger = None
        self.data_model = None
        self.item_loader = None  # Will be initialized if needed
        self.quest_data = {}
        self.current_quest_id = None
        self.validator = None
        self.next_custom_quest_id = 10000  # Start custom quests at 10000

        # Initialize settings
        self.settings = QSettings("SpellSmut", "UnifiedQuestEditor")

        # Auto-save timer
        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self._auto_save)
        self.auto_save_timer.setSingleShot(True)  # Single shot timer
        self.auto_save_delay = 2000  # 2 seconds

        self._setup_logging()
        self._setup_ui()
        self._setup_menu_bar()
        self._setup_status_bar()
        self._setup_connections()
        self._load_data()

        # Restore geometry
        self._restore_settings()

    def _setup_logging(self):
        """Setup logging"""
        try:
            if CFF_AVAILABLE:
                configure_logging()
                self.logger = get_logger("unified_quest_editor")
            else:
                import logging

                logging.basicConfig(level=logging.INFO)
                self.logger = logging.getLogger("unified_quest_editor")
        except Exception as e:
            print(f"Warning: Could not setup logging: {e}")
            self.logger = None

    def _setup_ui(self):
        """Setup the main UI"""
        self.setWindowTitle("Unified Quest Editor - SpellForce Modding Tools")
        self.setMinimumSize(1400, 900)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left side - Quest browser
        self.quest_browser = QuestBrowser()
        splitter.addWidget(self.quest_browser)

        # Right side - Quest editor tabs
        self.quest_editor_tabs = QTabWidget()
        splitter.addWidget(self.quest_editor_tabs)

        # Setup editor tabs
        self._setup_editor_tabs()

        # Set splitter proportions
        splitter.setSizes([400, 1000])

        # Status indicator (removed from here, will be added as a status bar)

    def _setup_editor_tabs(self):
        """Setup the quest editor tabs"""

        # Tab 1: Overview (Text Mode) - NEW
        try:
            from .text_mode_dialogue_overview import TextModeDialogueOverview

            self.text_mode_overview = TextModeDialogueOverview()
            self.text_mode_overview.node_selected.connect(
                self._on_text_mode_node_selected
            )
            self.text_mode_overview.node_edited.connect(self._on_text_mode_node_edited)
            self.text_mode_overview.node_added.connect(self._on_text_mode_node_added)
            self.text_mode_overview.node_deleted.connect(
                self._on_text_mode_node_deleted
            )
            self.text_mode_overview.jump_to_visual.connect(self._on_jump_to_visual)
            self.quest_editor_tabs.addTab(self.text_mode_overview, "📋 Overview")
        except ImportError as e:
            print(f"Warning: Text mode overview not available: {e}")
            self.text_mode_overview = None

        # Tab 2: Basic Info
        self.basic_info_widget = QuestBasicInfoWidget()
        self.quest_editor_tabs.addTab(self.basic_info_widget, "Basic Info")

        # Tab 3: Location & NPC
        self.location_widget = QuestLocationWidget()
        self.quest_editor_tabs.addTab(self.location_widget, "Location & NPC")

        # Tab 3.5: Conditions & Flags - NEW
        try:
            from .flag_manager import FlagManagerWidget
            from .condition_builder import ConditionBuilderWidget

            # Create a combined widget for conditions and flags
            conditions_flags_widget = QWidget()
            conditions_flags_layout = QVBoxLayout(conditions_flags_widget)
            conditions_flags_layout.setContentsMargins(5, 5, 5, 5)

            # Create splitter for conditions and flags
            cf_splitter = QSplitter(Qt.Vertical)

            # Flag Manager (top)
            self.flag_manager = FlagManagerWidget()
            self.flag_manager.flags_changed.connect(self._on_flags_changed)
            cf_splitter.addWidget(self.flag_manager)

            # Condition Builder (bottom) - pass flag manager for integration
            self.condition_builder = ConditionBuilderWidget(
                flag_manager=self.flag_manager
            )
            self.condition_builder.conditions_changed.connect(
                self._on_conditions_changed
            )
            cf_splitter.addWidget(self.condition_builder)

            # Set initial sizes (60% flags, 40% conditions)
            cf_splitter.setSizes([600, 400])

            conditions_flags_layout.addWidget(cf_splitter)

            self.quest_editor_tabs.addTab(
                conditions_flags_widget, "🔧 Conditions & Flags"
            )
        except ImportError as e:
            print(f"Warning: Conditions & Flags widgets not available: {e}")
            self.flag_manager = None
            self.condition_builder = None

        # Tab 4: Objectives & Requirements
        self.objectives_widget = QWidget()
        self._setup_objectives_tab()
        self.quest_editor_tabs.addTab(self.objectives_widget, "Objectives")

        # Tab 5: Dialogue Editor (Visual)
        self.visual_dialogue_widget = None
        if VISUAL_DIALOGUE_EDITOR_AVAILABLE:
            try:
                from .visual_dialogue_widget import VisualDialogueWidget

                self.visual_dialogue_widget = VisualDialogueWidget()
                self.visual_dialogue_widget.dialogue_changed.connect(
                    self._on_visual_dialogue_changed
                )
                self.quest_editor_tabs.addTab(
                    self.visual_dialogue_widget, "🎨 Dialogue (Visual)"
                )
            except (ImportError, NameError, AttributeError) as e:
                print(f"Warning: Visual dialogue widget not available: {e}")
                self.visual_dialogue_widget = None
                # Fallback to simple dialogue editor
                if not hasattr(self, "dialogue_widget"):
                    self.dialogue_widget = self._create_simple_dialogue_editor()
                    self.quest_editor_tabs.addTab(
                        self.dialogue_widget, "Dialogues (Simple)"
                    )
        else:
            # Fallback dialogue editor
            if not hasattr(self, "dialogue_widget"):
                self.dialogue_widget = self._create_simple_dialogue_editor()
                self.quest_editor_tabs.addTab(
                    self.dialogue_widget, "Dialogues (Simple)"
                )

        # Tab 6: Rewards
        self.rewards_widget = QWidget()
        self._setup_rewards_tab()
        self.quest_editor_tabs.addTab(self.rewards_widget, "Rewards")

        # Tab 7: Preview
        self.preview_widget = QuestPreviewWidget(self.item_loader)
        self.quest_editor_tabs.addTab(self.preview_widget, "Preview")

        # Tab 8: Validation
        self.validation_widget = QWidget()
        self._setup_validation_tab()
        self.quest_editor_tabs.addTab(self.validation_widget, "Validation")

        # Initially disable editing until a quest is selected
        self.quest_editor_tabs.setEnabled(False)

    def _setup_objectives_tab(self):
        """Setup objectives tab"""
        layout = QVBoxLayout(self.objectives_widget)

        # Objectives section
        objectives_group = QGroupBox("Quest Objectives")
        objectives_layout = QVBoxLayout(objectives_group)

        self.objectives_list = QListWidget()
        objectives_layout.addWidget(self.objectives_list)

        objectives_btn_layout = QHBoxLayout()
        add_obj_btn = QPushButton("Add Objective")
        add_obj_btn.clicked.connect(self._add_objective)
        remove_obj_btn = QPushButton("Remove Selected")
        remove_obj_btn.clicked.connect(self._remove_objective)
        objectives_btn_layout.addWidget(add_obj_btn)
        objectives_btn_layout.addWidget(remove_obj_btn)
        objectives_btn_layout.addStretch()
        objectives_layout.addLayout(objectives_btn_layout)

        layout.addWidget(objectives_group)

        # Requirements section
        requirements_group = QGroupBox("Quest Requirements")
        requirements_layout = QVBoxLayout(requirements_group)

        self.requirements_list = QListWidget()
        requirements_layout.addWidget(self.requirements_list)

        requirements_btn_layout = QHBoxLayout()
        add_req_btn = QPushButton("Add Requirement")
        add_req_btn.clicked.connect(self._add_requirement)
        remove_req_btn = QPushButton("Remove Selected")
        remove_req_btn.clicked.connect(self._remove_requirement)
        requirements_btn_layout.addWidget(add_req_btn)
        requirements_btn_layout.addWidget(remove_req_btn)
        requirements_btn_layout.addStretch()
        requirements_layout.addLayout(requirements_btn_layout)

        layout.addWidget(requirements_group)

    def _setup_rewards_tab(self):
        """Setup rewards tab"""
        layout = QVBoxLayout(self.rewards_widget)

        # Experience and money
        currency_group = QGroupBox("Currency Rewards")
        currency_layout = QFormLayout(currency_group)

        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 999999)
        self.xp_spin.setValue(0)
        currency_layout.addRow("Experience Points:", self.xp_spin)

        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(0, 999999)
        self.gold_spin.setValue(0)
        currency_layout.addRow("Gold:", self.gold_spin)

        self.silver_spin = QSpinBox()
        self.silver_spin.setRange(0, 99)
        self.silver_spin.setValue(0)
        currency_layout.addRow("Silver:", self.silver_spin)

        self.copper_spin = QSpinBox()
        self.copper_spin.setRange(0, 99)
        self.copper_spin.setValue(0)
        currency_layout.addRow("Copper:", self.copper_spin)

        layout.addWidget(currency_group)

        # Items
        items_group = QGroupBox("Item Rewards")
        items_layout = QVBoxLayout(items_group)

        # Item type selector
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Browse:"))
        self.item_type_combo = QComboBox()
        self.item_type_combo.addItems(["General Items", "Weapons", "Armor", "Spells"])
        self.item_type_combo.currentTextChanged.connect(self._on_item_type_changed)
        type_layout.addWidget(self.item_type_combo)
        type_layout.addStretch()
        items_layout.addLayout(type_layout)

        # Items list
        self.items_list = QListWidget()
        items_layout.addWidget(self.items_list)

        # Item management buttons
        items_btn_layout = QHBoxLayout()
        add_item_btn = QPushButton("Add Item")
        add_item_btn.clicked.connect(self._add_reward_item)
        remove_item_btn = QPushButton("Remove Selected")
        remove_item_btn.clicked.connect(self._remove_reward_item)
        edit_quantity_btn = QPushButton("Edit Quantity")
        edit_quantity_btn.clicked.connect(self._edit_item_quantity)
        items_btn_layout.addWidget(add_item_btn)
        items_btn_layout.addWidget(edit_quantity_btn)
        items_btn_layout.addWidget(remove_item_btn)
        items_btn_layout.addStretch()
        items_layout.addLayout(items_btn_layout)

        layout.addWidget(items_group)

        layout.addStretch()

    def _setup_validation_tab(self):
        """Setup validation tab"""
        layout = QVBoxLayout(self.validation_widget)

        # Validation controls
        controls_layout = QHBoxLayout()

        self.validate_btn = QPushButton("Validate Current Quest")
        self.validate_btn.clicked.connect(self._validate_current_quest)
        controls_layout.addWidget(self.validate_btn)

        self.auto_validate_check = QCheckBox("Auto-validate on changes")
        self.auto_validate_check.setChecked(True)
        controls_layout.addWidget(self.auto_validate_check)

        controls_layout.addStretch()
        layout.addLayout(controls_layout)

        # Validation results
        results_group = QGroupBox("Validation Results")
        results_layout = QVBoxLayout(results_group)

        self.validation_status = QLabel("No quest selected for validation")
        self.validation_status.setStyleSheet("padding: 10px; font-weight: bold;")
        results_layout.addWidget(self.validation_status)

        self.validation_results = QTextEdit()
        self.validation_results.setReadOnly(True)
        self.validation_results.setMaximumHeight(300)
        results_layout.addWidget(self.validation_results)

        layout.addWidget(results_group)

        layout.addStretch()

    def _create_simple_dialogue_editor(self) -> QWidget:
        """Create simple dialogue editor as fallback"""
        widget = QWidget()
        layout = QVBoxLayout(widget)

        layout.addWidget(QLabel("Simple Dialogue Editor"))
        layout.addWidget(QLabel("(Visual editor not available)"))

        self.dialogues_list = QListWidget()
        layout.addWidget(self.dialogues_list)

        btn_layout = QHBoxLayout()
        add_dlg_btn = QPushButton("Add Dialogue")
        add_dlg_btn.clicked.connect(self._add_dialogue)
        remove_dlg_btn = QPushButton("Remove Selected")
        remove_dlg_btn.clicked.connect(self._remove_dialogue)
        btn_layout.addWidget(add_dlg_btn)
        btn_layout.addWidget(remove_dlg_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        return widget

    def _setup_menu_bar(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        new_action = QAction("New Quest", self)
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self._new_quest)
        file_menu.addAction(new_action)

        save_action = QAction("Save Quest", self)
        save_action.setShortcut(QKeySequence.Save)
        save_action.triggered.connect(self._save_quest)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        export_lua_action = QAction("Export Lua Script", self)
        export_lua_action.triggered.connect(self._export_lua_script)
        file_menu.addAction(export_lua_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        validate_action = QAction("Validate Quest", self)
        validate_action.setShortcut(QKeySequence("F5"))
        validate_action.triggered.connect(self._validate_current_quest)
        edit_menu.addAction(validate_action)

        # View menu
        view_menu = menubar.addMenu("View")

        refresh_action = QAction("Refresh Quest Data", self)
        refresh_action.setShortcut(QKeySequence.Refresh)
        refresh_action.triggered.connect(self._load_data)
        view_menu.addAction(refresh_action)

    def _setup_status_bar(self):
        """Setup status bar"""
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Add editing status widget to status bar
        self.edit_status_widget = QWidget()
        edit_status_layout = QHBoxLayout(self.edit_status_widget)
        edit_status_layout.setContentsMargins(10, 2, 10, 2)

        self.edit_status_icon = QLabel("📝")
        self.edit_status_icon.setStyleSheet("font-size: 14px;")

        self.edit_status_text = QLabel("No Quest Selected")
        self.edit_status_text.setStyleSheet("""
            QLabel {
                background-color: #95a5a6;
                color: white;
                padding: 4px 12px;
                border-radius: 12px;
                font-weight: 500;
                font-size: 11px;
            }
        """)

        edit_status_layout.addWidget(self.edit_status_icon)
        edit_status_layout.addWidget(self.edit_status_text)
        edit_status_layout.addStretch()

        self.status_bar.addPermanentWidget(self.edit_status_widget)

        # Initially set the editing status
        self._set_editing_enabled(False)

    def _setup_connections(self):
        """Setup signal connections"""
        # Quest browser
        self.quest_browser.quest_selected.connect(self._on_quest_selected)
        self.quest_browser.quest_created.connect(self._on_quest_created)
        self.quest_browser.quest_updated.connect(self._on_quest_updated)

        # Editor widgets
        self.basic_info_widget.data_changed.connect(self._on_data_changed)
        self.location_widget.data_changed.connect(self._on_data_changed)

        # Tab changes
        self.quest_editor_tabs.currentChanged.connect(self._on_tab_changed)

        # Auto-validation
        self.xp_spin.valueChanged.connect(self._on_data_changed)
        self.gold_spin.valueChanged.connect(self._on_data_changed)
        self.silver_spin.valueChanged.connect(self._on_data_changed)
        self.copper_spin.valueChanged.connect(self._on_data_changed)

    def _load_data(self):
        """Load quest data"""
        try:
            if self.logger:
                self.logger.info("Loading quest data...")

            self.status_bar.showMessage("Loading quest data...")
            QApplication.processEvents()

            # Initialize data model if CFF is available
            if CFF_AVAILABLE and not self.data_model:
                self.data_model = CFFDataModel()

                # Try to load CFF file
                # Calculate project root from script path
                script_path = Path(__file__).resolve()
                calculated_project_root = script_path.parent.parent.parent.parent.parent
                cff_path = (
                    calculated_project_root / "OriginalGameFiles/data/GameData.cff"
                )
                if cff_path.exists():
                    if self.data_model.load_file(str(cff_path)):
                        if self.logger:
                            self.logger.info("CFF file loaded successfully")
                    else:
                        if self.logger:
                            self.logger.warning("Failed to load CFF file")
                else:
                    if self.logger:
                        self.logger.warning(f"CFF file not found: {cff_path}")

            # Load quest data
            if self.data_model:
                quests = self.data_model.get_elements("quests") or []
                self.quest_data = {}

                for quest in quests:
                    quest_id = getattr(quest, "quest_id", None)
                    if quest_id is not None:
                        name = self.data_model.get_localised_text(quest, "name")
                        if not name:
                            name = getattr(quest, "name", f"Quest {quest_id}")

                        self.quest_data[quest_id] = {
                            "name": name,
                            "description": self.data_model.get_localised_text(
                                quest, "description"
                            )
                            or "",
                            "quest_object": quest,
                        }
            else:
                # Mock data for testing
                self.quest_data = {
                    1: {
                        "name": "Staub der Sterne",
                        "description": "Quest description...",
                    },
                    12: {
                        "name": "Darius der Kartograph",
                        "description": "Quest description...",
                    },
                }

            # Load into browser
            self.quest_browser.load_quests(self.quest_data)

            # Setup validator
            if QUEST_VALIDATOR_AVAILABLE:
                self.validator = QuestValidator()
                self.validator.set_existing_quests(self.quest_data)

            # Update basic info parent options
            self.basic_info_widget.set_parent_quests(self.quest_data)

            quest_count = len(self.quest_data)
            self.status_bar.showMessage(f"Loaded {quest_count} quests")
            self.edit_status_text.setText(f"Loaded {quest_count} quests")

            if self.logger:
                self.logger.info(f"Loaded {quest_count} quests")

        except Exception as e:
            error_msg = f"Failed to load quest data: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            else:
                print(error_msg)

            self.status_bar.showMessage(error_msg)
            self.edit_status_text.setText("Load Failed")
            self.edit_status_text.setStyleSheet("""
                QLabel {
                    background-color: #e74c3c;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 11px;
                }
            """)

    def _on_quest_selected(self, quest_id: int):
        """Handle quest selection"""
        if quest_id not in self.quest_data:
            return

        self.current_quest_id = quest_id
        quest_info = self.quest_data[quest_id]

        # Load quest data into all editor tabs
        self.basic_info_widget.load_quest(quest_info)
        self.location_widget.load_quest_data(quest_info)

        # Load objectives
        self._load_quest_objectives(quest_info)

        # Load rewards
        self._load_quest_rewards(quest_info)

        # Load dialogues
        self._load_quest_dialogues(quest_info)

        # Load flags and conditions
        if hasattr(self, "flag_manager") and self.flag_manager:
            flags_data = quest_info.get("flags", {})
            if flags_data:
                self.flag_manager.load_from_dict(flags_data)
            else:
                # Clear flags for new quest
                self.flag_manager.flags.clear()
                self.flag_manager.refresh_table()

        if hasattr(self, "condition_builder") and self.condition_builder:
            conditions_data = quest_info.get("conditions", {})
            if conditions_data:
                self.condition_builder.load_from_dict(conditions_data)
            else:
                # Clear conditions for new quest
                self.condition_builder.root_condition.children.clear()
                self.condition_builder.refresh_tree()

        # Update preview
        self.preview_widget.update_preview(quest_info)

        # Auto-validate if enabled
        if self.auto_validate_check.isChecked():
            self._validate_current_quest()

        self.status_bar.showMessage(
            f"Editing quest: {quest_info.get('name', f'Quest {quest_id}')}"
        )

        # Enable editing
        self._set_editing_enabled(True)

    def _on_quest_created(self, quest_data: dict):
        """Handle quest creation"""
        quest_id = quest_data["id"]

        # Add to quest data
        self.quest_data[quest_id] = quest_data

        # Select the new quest
        self._on_quest_selected(quest_id)

        self.status_bar.showMessage(
            f"Created new quest: {quest_data.get('name', f'Quest {quest_id}')}"
        )

    def _on_quest_updated(self, quest_id: int, quest_data: dict):
        """Handle quest updates"""
        if quest_id == self.current_quest_id:
            # Update current quest data
            self.quest_data[quest_id] = quest_data

            # Update status bar to show auto-save
            self.status_bar.showMessage(
                f"Auto-saved: {quest_data.get('name', f'Quest {quest_id}')}"
            )

            # Trigger auto-save timer
            self.auto_save_timer.start(self.auto_save_delay)

    def _auto_save(self):
        """Auto-save current quest"""
        if not self.current_quest_id:
            return

        try:
            # Save to JSON file
            import json
            from pathlib import Path

            # Create saves directory if it doesn't exist
            saves_dir = Path.home() / ".spellmut" / "quests"
            saves_dir.mkdir(parents=True, exist_ok=True)

            # Save current quest
            quest_data = self.quest_data[self.current_quest_id]
            filename = f"quest_{self.current_quest_id}.json"
            filepath = saves_dir / filename

            with open(filepath, "w") as f:
                json.dump(quest_data, f, indent=2)

            # Update status
            quest_name = quest_data.get("name", f"Quest {self.current_quest_id}")
            self.status_bar.showMessage(f"Auto-saved: {quest_name}")

            self.logger.info(f"Auto-saved quest {self.current_quest_id} to {filepath}")

        except Exception as e:
            self.logger.error(f"Failed to auto-save quest: {e}")
            self.status_bar.showMessage(f"Auto-save failed: {e}")

    def _set_editing_enabled(self, enabled: bool):
        """Enable or disable all editing widgets"""
        # Enable/disable quest editor tabs
        self.quest_editor_tabs.setEnabled(enabled)

        # Update status indicator in status bar
        if enabled:
            self.edit_status_icon.setText("✏️")
            self.edit_status_text.setText("Editing Mode")
            self.edit_status_text.setStyleSheet("""
                QLabel {
                    background-color: #27ae60;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 11px;
                }
            """)
        else:
            self.edit_status_icon.setText("📝")
            self.edit_status_text.setText("No Quest Selected")
            self.edit_status_text.setStyleSheet("""
                QLabel {
                    background-color: #95a5a6;
                    color: white;
                    padding: 4px 12px;
                    border-radius: 12px;
                    font-weight: 500;
                    font-size: 11px;
                }
            """)

    def _load_quest_objectives(self, quest_info: Dict):
        """Load quest objectives with enhanced display"""
        self.objectives_list.clear()
        self.requirements_list.clear()

        objectives = quest_info.get("objectives", [])
        for obj in objectives:
            if isinstance(obj, dict):
                # Enhanced objective data
                obj_type = obj.get("type", "other")

                # Try to create enhanced display text
                if "target_name" in obj and obj["target_name"]:
                    if obj_type == "talk":
                        display_text = f"💬 Talk to {obj['target_name']}"
                    elif obj_type == "kill":
                        quantity = obj.get("quantity", 1)
                        display_text = f"⚔️ Kill {quantity}x {obj['target_name']}"
                    elif obj_type == "gather":
                        quantity = obj.get("quantity", 1)
                        display_text = f"📦 Gather {quantity}x {obj['target_name']}"
                    elif obj_type == "explore":
                        location = obj.get("location", "")
                        display_text = (
                            f"🗺 Explore {location}"
                            if location
                            else "🗺 Explore location"
                        )
                    elif obj_type == "escort":
                        target = obj.get("target_name", "NPC")
                        location = obj.get("location", "destination")
                        display_text = f"👥 Escort {target} to {location}"
                    else:
                        obj_text = obj.get("text", str(obj))
                        display_text = f"📝 {obj_text}"
                else:
                    # Fallback to simple display
                    obj_text = obj.get("text", str(obj))
                    display_text = f"[{obj_type}] {obj_text}"

                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, obj)
            else:
                item = QListWidgetItem(str(obj))
                item.setData(Qt.UserRole, {"text": str(obj), "type": "other"})
            self.objectives_list.addItem(item)

        requirements = quest_info.get("requirements", [])
        for req in requirements:
            if isinstance(req, dict):
                req_type = req.get("type", "other")
                req_text = req.get("text", str(req))
                item = QListWidgetItem(f"[{req_type}] {req_text}")
                item.setData(Qt.UserRole, req)
            else:
                item = QListWidgetItem(str(req))
                item.setData(Qt.UserRole, {"text": str(req), "type": "other"})
            self.requirements_list.addItem(item)

    def _load_quest_rewards(self, quest_info: Dict):
        """Load quest rewards"""
        rewards = quest_info.get("rewards", {})

        if isinstance(rewards, dict):
            self.xp_spin.setValue(rewards.get("xp", 0))
            self.gold_spin.setValue(rewards.get("gold", 0))
            self.silver_spin.setValue(rewards.get("silver", 0))
            self.copper_spin.setValue(rewards.get("copper", 0))

            # Load items
            self.items_list.clear()
            items = rewards.get("items", [])
            for item in items:
                if isinstance(item, dict):
                    item_id = item.get("id", "Unknown")
                    item_name = item.get("name", f"Item {item_id}")
                    count = item.get("count", 1)
                    display_text = f"{item_name} x{count}" if count > 1 else item_name
                else:
                    display_text = f"Item {item}"

                list_item = QListWidgetItem(display_text)
                list_item.setData(Qt.UserRole, item)
                self.items_list.addItem(list_item)

    def _load_quest_dialogues(self, quest_info: Dict):
        """Load quest dialogues"""
        dialogues = quest_info.get("dialogues", [])

        # Get dialogue data (could be in visual editor format)
        dialogue_data = quest_info.get("dialogue_data", {})
        if not dialogue_data and dialogues:
            # Convert simple dialogue list to visual editor format
            dialogue_data = self._convert_dialogues_to_visual_format(dialogues)

        # Load into text mode overview first (so it's always available)
        if hasattr(self, "text_mode_overview") and self.text_mode_overview:
            if dialogue_data:
                self.text_mode_overview.set_dialogue_data(dialogue_data)

        # Load into visual dialogue widget if available
        if hasattr(self, "visual_dialogue_widget") and self.visual_dialogue_widget:
            if dialogue_data:
                self.visual_dialogue_widget.set_dialogue_data(dialogue_data)
        elif DIALOGUE_EDITOR_AVAILABLE and hasattr(self, "dialogue_editor"):
            # Load into visual dialogue editor
            dialogue_dicts = []
            for dlg in dialogues:
                if isinstance(dlg, dict):
                    dialogue_dicts.append(dlg)
                else:
                    # Convert object to dict
                    dialogue_dicts.append(
                        {
                            "text": getattr(dlg, "text", str(dlg)),
                            "speaker": getattr(dlg, "speaker", "NPC"),
                            "type": getattr(dlg, "dialogue_type", "Standard"),
                        }
                    )

            self.dialogue_editor.load_dialogues(dialogue_dicts)
        else:
            # Load into simple dialogue list
            if hasattr(self, "dialogues_list"):
                self.dialogues_list.clear()
                for dlg in dialogues:
                    if isinstance(dlg, dict):
                        speaker = dlg.get("speaker", "NPC")
                        text = dlg.get("text", "")
                        dlg_type = dlg.get("type", "Standard")
                    else:
                        speaker = getattr(dlg, "speaker", "NPC")
                        text = getattr(dlg, "text", str(dlg))
                        dlg_type = getattr(dlg, "dialogue_type", "Standard")

                    display_text = (
                        f"[{speaker}] {text[:50]}{'...' if len(text) > 50 else ''}"
                    )
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, dlg)
                    self.dialogues_list.addItem(item)

    def _on_data_changed(self):
        """Handle data changes"""
        if not self.current_quest_id:
            return

        # Get current quest data
        current_data = self._get_current_quest_data()

        # Update quest data
        self.quest_data[self.current_quest_id] = current_data

        # Update quest browser
        self.quest_browser.update_quest(self.current_quest_id, current_data)

        # Update preview
        self.preview_widget.update_preview(current_data)

        # Auto-validate if enabled
        if self.auto_validate_check.isChecked():
            self._validate_current_quest()

        # Trigger auto-save timer
        self.auto_save_timer.start(self.auto_save_delay)

    def _on_tab_changed(self, index: int):
        """Handle tab change"""
        tab_name = self.quest_editor_tabs.tabText(index)
        self.status_bar.showMessage(f"Viewing: {tab_name}")

    def _get_current_quest_data(self) -> Dict:
        """Get current quest data from all editor tabs"""
        if not self.current_quest_id:
            return {}

        # Start with basic info
        quest_data = self.basic_info_widget.get_quest_data()

        # Add location data
        quest_data.update(self.location_widget.get_location_data())

        # Add objectives
        objectives = []
        for i in range(self.objectives_list.count()):
            item = self.objectives_list.item(i)
            obj_data = item.data(Qt.UserRole)
            if obj_data:
                objectives.append(obj_data)
        quest_data["objectives"] = objectives

        # Add requirements
        requirements = []
        for i in range(self.requirements_list.count()):
            item = self.requirements_list.item(i)
            req_data = item.data(Qt.UserRole)
            if req_data:
                requirements.append(req_data)
        quest_data["requirements"] = requirements

        # Add rewards
        rewards = {
            "xp": self.xp_spin.value(),
            "gold": self.gold_spin.value(),
            "silver": self.silver_spin.value(),
            "copper": self.copper_spin.value(),
            "items": [],
        }

        for i in range(self.items_list.count()):
            item = self.items_list.item(i)
            item_data = item.data(Qt.UserRole)
            if item_data:
                rewards["items"].append(item_data)

        quest_data["rewards"] = rewards

        # Add dialogues - prioritize visual dialogue widget, then text mode, then fallback
        if hasattr(self, "visual_dialogue_widget") and self.visual_dialogue_widget:
            dialogue_data = self.visual_dialogue_widget.get_dialogue_data()
            quest_data["dialogue_data"] = dialogue_data
            quest_data["dialogues"] = self._convert_visual_format_to_dialogues(
                dialogue_data
            )
        elif hasattr(self, "text_mode_overview") and self.text_mode_overview:
            dialogue_data = self.text_mode_overview.get_dialogue_data()
            quest_data["dialogue_data"] = dialogue_data
            quest_data["dialogues"] = self._convert_visual_format_to_dialogues(
                dialogue_data
            )
        elif DIALOGUE_EDITOR_AVAILABLE and hasattr(self, "dialogue_editor"):
            dialogues = self.dialogue_editor.get_dialogues()
            quest_data["dialogues"] = dialogues
        else:
            dialogues = []
            if hasattr(self, "dialogues_list"):
                for i in range(self.dialogues_list.count()):
                    item = self.dialogues_list.item(i)
                    dlg_data = item.data(Qt.UserRole)
                    if dlg_data:
                        dialogues.append(dlg_data)
            quest_data["dialogues"] = dialogues

        return quest_data

    def _validate_current_quest(self):
        """Validate the current quest"""
        if not self.current_quest_id:
            self.validation_status.setText("No quest selected for validation")
            self.validation_status.setStyleSheet(
                "padding: 10px; font-weight: bold; background-color: #f39c12; color: white;"
            )
            self.validation_results.clear()
            return

        if not QUEST_VALIDATOR_AVAILABLE or not self.validator:
            self.validation_status.setText("Validator not available")
            self.validation_status.setStyleSheet(
                "padding: 10px; font-weight: bold; background-color: #e74c3c; color: white;"
            )
            self.validation_results.setPlainText(
                "Quest validation component is not available."
            )
            return

        try:
            # Get current quest data
            quest_data = self._get_current_quest_data()

            # Convert to EnhancedQuestData for validation
            if EnhancedQuestData:
                enhanced_quest = self._convert_to_enhanced_data(quest_data)
                if enhanced_quest:
                    result = self.validator.validate_quest_detailed(enhanced_quest)

                    # Update validation status
                    if result.is_valid:
                        self.validation_status.setText(
                            "✓ Quest is valid and ready to save"
                        )
                        self.validation_status.setStyleSheet(
                            "padding: 10px; font-weight: bold; background-color: #27ae60; color: white;"
                        )
                    else:
                        self.validation_status.setText(
                            f"✗ Quest has {len(result.errors)} errors"
                        )
                        self.validation_status.setStyleSheet(
                            "padding: 10px; font-weight: bold; background-color: #e74c3c; color: white;"
                        )

                    # Display validation results
                    results_html = (
                        "<html><body style='font-family: Arial; font-size: 10pt;'>"
                    )

                    if result.errors:
                        results_html += "<h3 style='color: #e74c3c;'>Errors</h3><ul>"
                        for error in result.errors:
                            results_html += (
                                f"<li><b>{error.category}:</b> {error.message}"
                            )
                            if error.suggestion:
                                results_html += (
                                    f"<br><i>Suggestion: {error.suggestion}</i>"
                                )
                            results_html += "</li>"
                        results_html += "</ul>"

                    if result.warnings:
                        results_html += "<h3 style='color: #f39c12;'>Warnings</h3><ul>"
                        for warning in result.warnings:
                            results_html += (
                                f"<li><b>{warning.category}:</b> {warning.message}"
                            )
                            if warning.suggestion:
                                results_html += (
                                    f"<br><i>Suggestion: {warning.suggestion}</i>"
                                )
                            results_html += "</li>"
                        results_html += "</ul>"

                    if result.info:
                        results_html += (
                            "<h3 style='color: #3498db;'>Information</h3><ul>"
                        )
                        for info in result.info:
                            results_html += (
                                f"<li><b>{info.category}:</b> {info.message}</li>"
                            )
                        results_html += "</ul>"

                    if result.is_valid and not result.errors and not result.warnings:
                        results_html += "<p style='color: #27ae60; font-weight: bold;'>✓ No issues found!</p>"

                    results_html += "</body></html>"
                    self.validation_results.setHtml(results_html)
                else:
                    self.validation_status.setText(
                        "Failed to convert quest data for validation"
                    )
                    self.validation_status.setStyleSheet(
                        "padding: 10px; font-weight: bold; background-color: #e74c3c; color: white;"
                    )
            else:
                self.validation_status.setText(
                    "Enhanced quest data model not available"
                )
                self.validation_status.setStyleSheet(
                    "padding: 10px; font-weight: bold; background-color: #f39c12; color: white;"
                )

        except Exception as e:
            error_msg = f"Validation error: {e}"
            if self.logger:
                self.logger.exception(error_msg)

            self.validation_status.setText("Validation failed")
            self.validation_status.setStyleSheet(
                "padding: 10px; font-weight: bold; background-color: #e74c3c; color: white;"
            )
            self.validation_results.setPlainText(error_msg)

    def _convert_to_enhanced_data(
        self, quest_data: Dict
    ) -> Optional[EnhancedQuestData]:
        """Convert dictionary data to EnhancedQuestData"""
        try:
            if not EnhancedQuestData:
                return None

            # Extract basic fields
            quest_id = quest_data.get("quest_id", 0)
            name = quest_data.get("name", "")
            description = quest_data.get("description", "")
            parent_id = quest_data.get("parent_id", 0)
            order_index = quest_data.get("order_index", 0)

            # Convert locations
            locations = []
            platform = quest_data.get("platform")
            if platform and MapLocation:
                locations.append(
                    MapLocation(
                        code=platform, name=PLATFORM_NAMES.get(platform, platform)
                    )
                )

            # Convert dialogues
            dialogues = []
            for dlg_data in quest_data.get("dialogues", []):
                if isinstance(dlg_data, dict) and Dialogue:
                    dialogues.append(
                        Dialogue(
                            text=dlg_data.get("text", ""),
                            speaker=dlg_data.get("speaker", "NPC"),
                            dialogue_type=dlg_data.get("type", "Standard"),
                        )
                    )

            # Convert rewards
            rewards = None
            rewards_data = quest_data.get("rewards", {})
            if rewards_data and QuestReward:
                if isinstance(rewards_data, dict):
                    rewards = QuestReward(
                        xp=rewards_data.get("xp", 0),
                        gold=rewards_data.get("gold", 0),
                        silver=rewards_data.get("silver", 0),
                        copper=rewards_data.get("copper", 0),
                        items=rewards_data.get("items", []),
                    )

            return EnhancedQuestData(
                quest_id=quest_id,
                name=name,
                description=description,
                parent_id=parent_id,
                order_index=order_index,
                map_locations=locations,
                dialogues=dialogues,
                rewards=rewards,
            )

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Error converting quest data: {e}")
            return None

    # Action methods
    def _new_quest(self):
        """Create new quest - open quest browser dialog"""
        # Trigger the quest browser's new quest dialog
        self.quest_browser._create_new_quest()

    def _save_quest(self):
        """Save current quest"""
        if not self.current_quest_id:
            QMessageBox.warning(
                self, "No Quest", "Please select or create a quest first."
            )
            return

        # Validate first
        if QUEST_VALIDATOR_AVAILABLE and self.validator:
            self._validate_current_quest()

            # Check if validation passed
            if not self.validation_status.text().startswith("✓"):
                reply = QMessageBox.question(
                    self,
                    "Validation Issues",
                    "Quest has validation issues. Save anyway?",
                    QMessageBox.Yes | QMessageBox.No,
                )
                if reply != QMessageBox.Yes:
                    return

        try:
            # Get current quest data
            quest_data = self._get_current_quest_data()

            # Here you would implement actual saving logic
            # For now, just show success message
            QMessageBox.information(
                self,
                "Quest Saved",
                f"Quest '{quest_data.get('name', 'Unnamed')}' has been saved successfully!\n\n"
                f"Quest ID: {quest_data.get('quest_id')}\n"
                f"Note: Actual CFF/Lua saving would be implemented here.",
            )

            # Update quest data in browser
            self.quest_data[self.current_quest_id] = quest_data
            self.quest_browser.refresh_quests()

            self.status_bar.showMessage(
                f"Quest saved: {quest_data.get('name', 'Unnamed')}"
            )

        except Exception as e:
            error_msg = f"Failed to save quest: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            QMessageBox.critical(self, "Save Failed", error_msg)

    def _export_lua_script(self):
        """Export quest as Lua script"""
        if not self.current_quest_id:
            QMessageBox.warning(self, "No Quest", "Please select a quest first.")
            return

        try:
            quest_data = self._get_current_quest_data()
            lua_script = self._generate_lua_script(quest_data)

            # Show Lua script in dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Generated Lua Script")
            dialog.resize(800, 600)

            layout = QVBoxLayout(dialog)

            script_edit = QTextEdit()
            script_edit.setPlainText(lua_script)
            script_edit.setFont(QFont("Courier", 10))
            layout.addWidget(script_edit)

            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save)
            button_box.accepted.connect(dialog.accept)
            # TODO: Implement save functionality
            layout.addWidget(button_box)

            dialog.exec()

        except Exception as e:
            error_msg = f"Failed to generate Lua script: {e}"
            if self.logger:
                self.logger.exception(error_msg)
            QMessageBox.critical(self, "Export Failed", error_msg)

    def _generate_lua_script(self, quest_data: Dict) -> str:
        """Generate Lua quest script"""
        quest_id = quest_data.get("quest_id", 0)
        quest_name = quest_data.get("name", "Unnamed Quest")
        platform = quest_data.get("platform", "P1")
        description = quest_data.get("description", "")

        # Escape Lua strings
        def escape_lua_string(s):
            return s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

        script = f'''-- Generated Quest Script: {escape_lua_string(quest_name)}
-- Quest ID: {quest_id}
-- Platform: {platform}

function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Quest: {escape_lua_string(quest_name)}
-- ID: {quest_id}

-- Initialize quest when conditions are met
OnOneTimeEvent
{{
    EventName = "Init_{quest_name.replace(" ", "")}",
    Conditions =
    {{
        -- Add prerequisites here
        -- Example: QuestState{{QuestId = {parent_id}, State = StateCompleted}}
    }},
    Actions =
    {{
        -- Begin the quest
        QuestBegin{{QuestId = {quest_id}}},
        -- Add quest to journal
        Outcry{{
            NpcId = 0,  -- Player
            String = "{escape_lua_string(description[:100])}...",
            Color = ColorYellow
        }},
    }}
}}

-- Quest completion conditions
OnOneTimeEvent
{{
    EventName = "Complete_{quest_name.replace(" ", "")}",
    Conditions =
    {{
        QuestState{{QuestId = {quest_id}, State = StateActive}},
        -- Add completion conditions here
        -- Example: FigureDead{{FigureId = SomeFigureId}}
    }},
    Actions =
    {{
        -- Complete the quest
        QuestSolve{{QuestId = {quest_id}}},
        -- Grant rewards
        SetRewardFlagTrue{{Name = "Quest{quest_id}Reward"}},
        -- Success message
        Outcry{{
            NpcId = 0,
            String = "Quest completed: {escape_lua_string(quest_name)}!",
            Color = ColorGreen
        }},
    }}
}}

EndDefinition()
end
'''
        return script

    # Objective management methods
    def _add_objective(self):
        """Add new objective with enhanced editor"""
        try:
            from .objective_editor_simple import ObjectiveEditorDialog, ObjectiveData

            dialog = ObjectiveEditorDialog(self, data_model=self.data_model)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                objective = dialog.get_objective()
                if objective:
                    # Create list item with enhanced display
                    display_text = objective.get_display_text()
                    item = QListWidgetItem(display_text)
                    item.setData(Qt.UserRole, objective.to_dict())
                    self.objectives_list.addItem(item)

                    self._on_data_changed()

        except ImportError as e:
            # Fallback to simple dialog if enhanced editor not available
            from PySide6.QtWidgets import QInputDialog

            types = ["talk", "kill", "gather", "explore", "escort", "other"]
            obj_type, ok = QInputDialog.getItem(
                self, "Objective Type", "Select type:", types, 0, False
            )
            if not ok:
                return

            obj_text, ok = QInputDialog.getText(
                self, "Objective Text", "Enter objective:"
            )
            if not ok or not obj_text.strip():
                return

            item = QListWidgetItem(f"[{obj_type}] {obj_text}")
            item.setData(Qt.UserRole, {"type": obj_type, "text": obj_text})
            self.objectives_list.addItem(item)

            self._on_data_changed()

    def _remove_objective(self):
        """Remove selected objective"""
        current_row = self.objectives_list.currentRow()
        if current_row >= 0:
            self.objectives_list.takeItem(current_row)
            self._on_data_changed()

    def _add_requirement(self):
        """Add new requirement"""
        from PySide6.QtWidgets import QInputDialog

        types = ["quest", "level", "item", "flag", "other"]
        req_type, ok = QInputDialog.getItem(
            self, "Requirement Type", "Select type:", types, 0, False
        )
        if not ok:
            return

        req_text, ok = QInputDialog.getText(
            self, "Requirement Text", "Enter requirement:"
        )
        if not ok or not req_text.strip():
            return

        item = QListWidgetItem(f"[{req_type}] {req_text}")
        item.setData(Qt.UserRole, {"type": req_type, "text": req_text})
        self.requirements_list.addItem(item)

        self._on_data_changed()

    def _remove_requirement(self):
        """Remove selected requirement"""
        current_row = self.requirements_list.currentRow()
        if current_row >= 0:
            self.requirements_list.takeItem(current_row)
            self._on_data_changed()

    # Reward management methods
    def _add_reward_item(self):
        """Add reward item with item browser"""
        try:
            from .item_browser_widget import ItemBrowserDialog

            dialog = ItemBrowserDialog(
                parent=self,
                title="Select Reward Item",
                categories=[
                    "General Items",
                    "Weapons",
                    "Armor",
                    "Quest Items",
                    "Materials",
                ],
            )
            if dialog.exec() == QDialog.DialogCode.Accepted:
                selected = dialog.get_selected_item()
                if selected:
                    # Ask for quantity
                    from PySide6.QtWidgets import QInputDialog

                    item_count, ok = QInputDialog.getInt(
                        self, "Item Count", "Enter count:", 1, 1, 99
                    )
                    if not ok:
                        return

                    if item_count > 1:
                        item_id = selected.get("id", 0)
                        item_name = selected.get("name", "")
                        display_text = f"{item_name} (Item {item_id}) x{item_count}"
                    else:
                        item_id = selected.get("id", 0)
                        item_name = selected.get("name", "")
                        display_text = f"{item_name} (Item {item_id})"

                    item = QListWidgetItem(display_text)
                    item.setData(
                        Qt.UserRole,
                        {
                            "id": selected.get("id", 0),
                            "name": selected.get("name", ""),
                            "count": item_count,
                            "type": selected.get("type", "item"),
                            "description": selected.get("description", ""),
                        },
                    )
                    self.items_list.addItem(item)

                    self._on_data_changed()

        except ImportError:
            # Fallback to manual entry
            from PySide6.QtWidgets import QInputDialog

            item_id, ok = QInputDialog.getInt(
                self, "Item ID", "Enter item ID:", 1, 1, 99999
            )
            if not ok:
                return

            item_name, ok = QInputDialog.getText(
                self, "Item Name", "Enter item name (optional):"
            )
            item_count, ok = QInputDialog.getInt(
                self, "Item Count", "Enter count:", 1, 1, 99
            )

            display_text = (
                f"{item_name or f'Item {item_id}'} x{item_count}"
                if item_count > 1
                else (item_name or f"Item {item_id}")
            )

            item = QListWidgetItem(display_text)
            item.setData(
                Qt.UserRole, {"id": item_id, "name": item_name, "count": item_count}
            )
            self.items_list.addItem(item)

            self._on_data_changed()

    def _remove_reward_item(self):
        """Remove selected reward item"""
        current_row = self.items_list.currentRow()
        if current_row >= 0:
            self.items_list.takeItem(current_row)
            self._on_data_changed()

    def _on_item_type_changed(self, item_type):
        """Handle item type selection change"""
        # This method is called when the user changes the item type dropdown
        # For now, we'll just show a message about which browser would be used
        if item_type == "Weapons":
            QMessageBox.information(
                self,
                "Weapon Browser",
                "Weapon browser would show detailed weapon stats (damage, speed, etc.) from game data.",
            )
        elif item_type == "Armor":
            QMessageBox.information(
                self,
                "Armor Browser",
                "Armor browser would show detailed armor stats (defense, slots, etc.) from game data.",
            )
        elif item_type == "Spells":
            QMessageBox.information(
                self,
                "Spell Browser",
                "Spell browser would show spell details (mana cost, effects, etc.) from game data.",
            )
        # General Items uses the existing ItemBrowserWidget

    def _edit_item_quantity(self):
        """Edit quantity of selected reward item"""
        current_item = self.items_list.currentItem()
        if not current_item:
            QMessageBox.warning(
                self, "No Selection", "Please select an item to edit quantity."
            )
            return

        # Get current quantity from item data
        item_data = current_item.data(Qt.UserRole)
        if not item_data or not isinstance(item_data, dict):
            QMessageBox.warning(self, "Invalid Item", "Selected item has invalid data.")
            return

        current_quantity = item_data.get("count", 1)

        # Show quantity dialog
        quantity, ok = QInputDialog.getInt(
            self,
            "Edit Quantity",
            f"Enter quantity for {item_data.get('name', 'item')}:",
            current_quantity,
            1,
            999,
            1,
        )

        if ok and quantity != current_quantity:
            # Update item data
            item_data["count"] = quantity
            current_item.setData(Qt.UserRole, item_data)

            # Update display text
            item_name = item_data.get("name", f"Item {item_data.get('id', 0)}")
            current_item.setText(f"{item_name} x{quantity}")

            self._on_data_changed()

    # Dialogue management methods
    def _add_dialogue(self):
        """Add new dialogue"""
        from PySide6.QtWidgets import QInputDialog, QDialog, QDialogButtonBox

        dialog = QDialog(self)
        dialog.setWindowTitle("Add Dialogue")
        layout = QVBoxLayout(dialog)

        # Speaker
        speaker_layout = QHBoxLayout()
        speaker_layout.addWidget(QLabel("Speaker:"))
        speaker_combo = QComboBox()
        speaker_combo.addItems(["NPC", "Player"])
        speaker_layout.addWidget(speaker_combo)
        layout.addLayout(speaker_layout)

        # Text
        layout.addWidget(QLabel("Text:"))
        text_edit = QTextEdit()
        text_edit.setMaximumHeight(100)
        layout.addWidget(text_edit)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        if dialog.exec() != QDialog.Accepted:
            return

        speaker = speaker_combo.currentText()
        text = text_edit.toPlainText().strip()
        if not text:
            return

        display_text = f"[{speaker}] {text[:50]}{'...' if len(text) > 50 else ''}"
        item = QListWidgetItem(display_text)
        item.setData(
            Qt.UserRole,
            {"speaker": speaker, "text": text, "is_player": speaker == "Player"},
        )
        self.dialogues_list.addItem(item)

        self._on_data_changed()

    def _remove_dialogue(self):
        """Remove selected dialogue"""
        current_row = self.dialogues_list.currentRow()
        if current_row >= 0:
            self.dialogues_list.takeItem(current_row)
            self._on_data_changed()

    def _restore_settings(self):
        """Restore window settings"""
        geometry = self.settings.value("geometry")
        if geometry:
            self.restoreGeometry(geometry)

        window_state = self.settings.value("windowState")
        if window_state:
            self.restoreState(window_state)

        splitter_state = self.settings.value("splitterState")
        if splitter_state and hasattr(self, "quest_browser"):
            # Find the splitter
            for child in self.findChildren(QSplitter):
                child.restoreState(splitter_state)
                break

    # Text mode overview sync methods
    def _on_text_mode_node_selected(self, node_id: str):
        """Handle node selection in text mode"""
        # Could switch to visual editor and highlight node
        self.status_bar.showMessage(f"Selected node in text mode: {node_id}")

    def _on_text_mode_node_edited(self, node_id: str, node_data: dict):
        """Handle node edit in text mode"""
        # Sync to visual editor if available
        if hasattr(self, "visual_dialogue_widget") and self.visual_dialogue_widget:
            # Update visual editor
            dialogue_data = self.text_mode_overview.get_dialogue_data()
            self.visual_dialogue_widget.set_dialogue_data(dialogue_data)

        # Trigger data change
        self._on_data_changed()
        self.status_bar.showMessage(f"Updated node in text mode: {node_id}")

    def _on_text_mode_node_added(self, node_id: str, node_data: dict):
        """Handle node addition in text mode"""
        # Sync to visual editor if available
        if hasattr(self, "visual_dialogue_widget") and self.visual_dialogue_widget:
            dialogue_data = self.text_mode_overview.get_dialogue_data()
            self.visual_dialogue_widget.set_dialogue_data(dialogue_data)

        # Trigger data change
        self._on_data_changed()
        self.status_bar.showMessage(f"Added node in text mode: {node_id}")

    def _on_text_mode_node_deleted(self, node_id: str):
        """Handle node deletion in text mode"""
        # Sync to visual editor if available
        if hasattr(self, "visual_dialogue_widget") and self.visual_dialogue_widget:
            dialogue_data = self.text_mode_overview.get_dialogue_data()
            self.visual_dialogue_widget.set_dialogue_data(dialogue_data)

        # Trigger data change
        self._on_data_changed()
        self.status_bar.showMessage(f"Deleted node in text mode: {node_id}")

    def _on_jump_to_visual(self, node_id: str):
        """Handle jump to visual editor request"""
        # Switch to visual dialogue tab
        if hasattr(self, "visual_dialogue_widget") and self.visual_dialogue_widget:
            # Find tab index
            for i in range(self.quest_editor_tabs.count()):
                if self.quest_editor_tabs.widget(i) == self.visual_dialogue_widget:
                    self.quest_editor_tabs.setCurrentIndex(i)
                    break
            self.status_bar.showMessage(f"Jumped to visual editor for node: {node_id}")
        else:
            self.status_bar.showMessage("Visual dialogue editor not available")

    def _on_visual_dialogue_changed(self, dialogue_data: dict):
        """Handle dialogue change in visual editor"""
        # Sync to text mode overview
        if hasattr(self, "text_mode_overview") and self.text_mode_overview:
            self.text_mode_overview.set_dialogue_data(dialogue_data)

        # Trigger data change
        self._on_data_changed()
        self.status_bar.showMessage("Dialogue updated in visual editor")

    def _on_flags_changed(self):
        """Handle flag changes"""
        if not self.current_quest_id:
            return

        # Save flags to quest data
        if hasattr(self, "flag_manager") and self.flag_manager:
            quest_data = self._get_current_quest_data()
            quest_data["flags"] = self.flag_manager.to_dict()
            self.quest_data[self.current_quest_id] = quest_data

        # Trigger auto-save
        self.auto_save_timer.start(self.auto_save_delay)
        self.status_bar.showMessage("Flags updated")

    def _on_conditions_changed(self):
        """Handle condition changes"""
        if not self.current_quest_id:
            return

        # Save conditions to quest data
        if hasattr(self, "condition_builder") and self.condition_builder:
            quest_data = self._get_current_quest_data()
            quest_data["conditions"] = self.condition_builder.to_dict()
            self.quest_data[self.current_quest_id] = quest_data

        # Trigger auto-save
        self.auto_save_timer.start(self.auto_save_delay)
        self.status_bar.showMessage("Conditions updated")

    def _convert_dialogues_to_visual_format(self, dialogues: List) -> Dict[str, Any]:
        """Convert simple dialogue list to visual editor format"""
        nodes = []
        connections = []

        for i, dlg in enumerate(dialogues):
            if isinstance(dlg, dict):
                node_id = dlg.get("id", f"node_{i + 1}")
                node_type = dlg.get("type", "npc").lower()
                speaker = dlg.get("speaker", "NPC")
                text = dlg.get("text", "")
            else:
                node_id = getattr(dlg, "id", f"node_{i + 1}")
                node_type = getattr(dlg, "dialogue_type", "npc").lower()
                speaker = getattr(dlg, "speaker", "NPC")
                text = getattr(dlg, "text", str(dlg))

            node = {
                "id": node_id,
                "node_type": node_type,
                "speaker": speaker,
                "text": text,
                "choices": dlg.get("choices", []) if isinstance(dlg, dict) else [],
                "conditions": dlg.get("conditions", [])
                if isinstance(dlg, dict)
                else [],
                "actions": dlg.get("actions", []) if isinstance(dlg, dict) else [],
                "next_nodes": dlg.get("next_nodes", [])
                if isinstance(dlg, dict)
                else [],
                "answer_id": dlg.get("answer_id") if isinstance(dlg, dict) else None,
                "tag": dlg.get("tag", "") if isinstance(dlg, dict) else "",
            }
            nodes.append(node)

            # Add connections
            next_nodes = node.get("next_nodes", [])
            for next_id in next_nodes:
                connections.append({"from": node_id, "to": next_id})

        return {"nodes": nodes, "connections": connections}

    def _convert_visual_format_to_dialogues(
        self, dialogue_data: Dict[str, Any]
    ) -> List[Dict]:
        """Convert visual editor format to simple dialogue list"""
        dialogues = []

        if "nodes" in dialogue_data:
            for node_data in dialogue_data["nodes"]:
                dialogue = {
                    "id": node_data.get("id", ""),
                    "speaker": node_data.get("speaker", "NPC"),
                    "text": node_data.get("text", ""),
                    "type": node_data.get("node_type", "npc"),
                    "choices": node_data.get("choices", []),
                    "conditions": node_data.get("conditions", []),
                    "actions": node_data.get("actions", []),
                }
                dialogues.append(dialogue)

        return dialogues

    def closeEvent(self, event):
        """Handle window close"""
        # Save settings
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("windowState", self.saveState())

        # Save splitter state
        for child in self.findChildren(QSplitter):
            self.settings.setValue("splitterState", child.saveState())
            break

        if self.logger:
            self.logger.info("Unified quest editor closed")

        super().closeEvent(event)


# Main entry point
def main():
    """Main entry point for unified quest editor"""
    app = QApplication(sys.argv)
    app.setApplicationName("Unified Quest Editor")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SpellSmut Modding Tools")

    # Create and show main window
    editor = UnifiedQuestEditor()
    editor.show()

    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)
