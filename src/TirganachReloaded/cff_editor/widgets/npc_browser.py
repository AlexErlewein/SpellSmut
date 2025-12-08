#!/usr/bin/env python3
"""
NPC Browser and Integration System

Provides a comprehensive browser for NPCs, items, locations, and other game resources
that can be integrated into quest dialogues and activities.
"""

import json
import os
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView, QSplitter, QTabWidget,
    QTextEdit, QScrollArea, QFrame, QToolButton, QMenu, QDialog,
    QDialogButtonBox, QFormLayout, QSpinBox, QSlider, QProgressBar,
    QMessageBox, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem
)
from PySide6.QtCore import (
    Qt, Signal, pyqtSignal, QThread, QTimer, QSortFilterProxyModel,
    QAbstractListModel, QModelIndex, QItemSelectionModel, QRectF
)
from PySide6.QtGui import (
    QFont, QIcon, QPixmap, QPainter, QColor, QPalette, QMouseEvent,
    QHelpEvent, QKeyEvent, QBrush, QLinearGradient, QRadialGradient,
    QTextDocument, QTextCursor
)

try:
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class NPCType(Enum):
    """Types of NPCs in the game"""
    VILLAGER = "villager"
    GUARD = "guard"
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    TRAINER = "trainer"
    ENEMY = "enemy"
    BOSS = "boss"
    COMPANION = "companion"
    NEUTRAL = "neutral"
    CHILD = "child"
    ELDER = "elder"


class NPCFaction(Enum):
    """NPC factions affecting dialogue options"""
    PLAYER_FRIENDLY = "player_friendly"
    PLAYER_HOSTILE = "player_hostile"
    NEUTRAL = "neutral"
    MERCHANT_GUILD = "merchant_guild"
    GUARD_GUILD = "guard_guild"
    ROGUE_GUILD = "rogue_guild"
    MAGE_GUILD = "mage_guild"
    WILDLIFE = "wildlife"


@dataclass
class NPCData:
    """Data model for an NPC"""
    id: str
    name: str
    npc_type: NPCType
    faction: NPCFaction
    level: int = 1
    description: str = ""
    location: str = ""
    portrait_path: str = ""
    voice_type: str = "default"
    personality: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    dialogue_topics: List[str] = field(default_factory=list)
    known_items: List[str] = field(default_factory=list)
    special_abilities: List[str] = field(default_factory=list)
    available_hours: str = "全天"  # Chinese for "all day"
    dialogue_style: str = "friendly"
    gender: str = "unknown"

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "npc_type": self.npc_type.value,
            "faction": self.faction.value,
            "level": self.level,
            "description": self.description,
            "location": self.location,
            "portrait_path": self.portrait_path,
            "voice_type": self.voice_type,
            "personality": self.personality,
            "tags": self.tags,
            "dialogue_topics": self.dialogue_topics,
            "known_items": self.known_items,
            "special_abilities": self.special_abilities,
            "available_hours": self.available_hours,
            "dialogue_style": self.dialogue_style,
            "gender": self.gender
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'NPCData':
        """Create from dictionary"""
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            npc_type=NPCType(data.get("npc_type", "neutral")),
            faction=NPCFaction(data.get("faction", "neutral")),
            level=data.get("level", 1),
            description=data.get("description", ""),
            location=data.get("location", ""),
            portrait_path=data.get("portrait_path", ""),
            voice_type=data.get("voice_type", "default"),
            personality=data.get("personality", []),
            tags=data.get("tags", []),
            dialogue_topics=data.get("dialogue_topics", []),
            known_items=data.get("known_items", []),
            special_abilities=data.get("special_abilities", []),
            available_hours=data.get("available_hours", "全天"),
            dialogue_style=data.get("dialogue_style", "friendly"),
            gender=data.get("gender", "unknown")
        )


class NPCTreeWidgetItem(QTreeWidgetItem):
    """Custom tree widget item for NPCs"""

    def __init__(self, npc: NPCData = None, parent=None):
        super().__init__(parent)
        self.npc = npc
        if npc:
            self.setup_data()

    def setup_data(self):
        """Setup item data"""
        if not self.npc:
            return

        # Set text with NPC type icon
        type_icons = {
            NPCType.VILLAGER: "👤",
            NPCType.GUARD: "⚔️",
            NPCType.MERCHANT: "🛒",
            NPCType.QUEST_GIVER: "📜",
            NPCType.TRAINER: "🎯",
            NPCType.ENEMY: "🗡️",
            NPCType.BOSS: "👹",
            NPCType.COMPANION: "🐕",
            NPCType.NEUTRAL: "🤷",
            NPCType.CHILD: "👶",
            NPCType.ELDER: "👴"
        }

        type_icon = type_icons.get(self.npc.npc_type, "🤷")
        faction_colors = {
            NPCFaction.PLAYER_FRIENDLY: "#4CAF50",
            NPCFaction.PLAYER_HOSTILE: "#F44336",
            NPCFaction.NEUTRAL: "#FF9800",
            NPCFaction.MERCHANT_GUILD: "#FFD700",
            NPCFaction.GUARD_GUILD: "#2196F3"
        }

        faction_color = faction_colors.get(self.npc.faction, "#888")

        self.setText(0, f"{type_icon} {self.npc.name}")
        self.setText(1, f"Level {self.npc.level}")
        self.setText(2, self.npc.npc_type.value.title())
        self.setText(3, self.npc.location)
        self.setText(4, ", ".join(self.npc.tags[:3]) if self.npc.tags else "")

        # Set color based on faction
        self.setForeground(2, QColor(faction_color))

        # Store NPC data
        self.setData(0, Qt.UserRole, self.npc)


class NPCSearchFilterProxyModel(QSortFilterProxyModel):
    """Proxy model for filtering NPCs"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filter_text = ""
        self.filter_type = "all"
        self.filter_faction = "all"
        self.filter_location = "all"
        self.min_level = 1
        self.max_level = 100

    def setFilterText(self, text: str):
        """Set text filter"""
        self.filter_text = text.lower()
        self.invalidateFilter()

    def setFilterType(self, npc_type: str):
        """Set NPC type filter"""
        self.filter_type = npc_type
        self.invalidateFilter()

    def setFilterFaction(self, faction: str):
        """Set faction filter"""
        self.filter_faction = faction
        self.invalidateFilter()

    def setFilterLocation(self, location: str):
        """Set location filter"""
        self.filter_location = location
        self.invalidateFilter()

    def setLevelRange(self, min_level: int, max_level: int):
        """Set level range filter"""
        self.min_level = min_level
        self.max_level = max_level
        self.invalidateFilter()

    def filterAcceptsRow(self, source_row: int, source_parent):
        """Filter logic"""
        if not self.sourceModel():
            return False

        # Get NPC data
        item = self.sourceModel().item(source_row, source_parent)
        if not item or not hasattr(item, 'npc') or not item.npc:
            return False

        npc = item.npc

        # Text filter
        if self.filter_text:
            if (self.filter_text not in npc.name.lower() and
                self.filter_text not in npc.description.lower() and
                not any(self.filter_text in tag.lower() for tag in npc.tags)):
                return False

        # Type filter
        if self.filter_type != "all" and npc.npc_type.value != self.filter_type:
            return False

        # Faction filter
        if self.filter_faction != "all" and npc.faction.value != self.filter_faction:
            return False

        # Location filter
        if self.filter_location != "all" and npc.location != self.filter_location:
            return False

        # Level filter
        if not (self.min_level <= npc.level <= self.max_level):
            return False

        return True


class NPCPortraitWidget(QWidget):
    """Widget for displaying NPC portrait"""

    def __init__(self, size: int = 100, parent=None):
        super().__init__(parent)
        self.size = size
        self.npc = None
        self.setFixedSize(size, size)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        self.setStyleSheet("""
            QWidget {
                background-color: #2a2a2a;
                border: 2px solid #555;
                border-radius: 5px;
            }
        """)

    def setNPC(self, npc: NPCData):
        """Set the NPC to display"""
        self.npc = npc
        self.update()

    def paintEvent(self, event):
        """Paint the portrait"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if not self.npc:
            # Draw placeholder
            painter.setPen(QColor("#666"))
            painter.drawText(self.rect(), Qt.AlignCenter, "No NPC")
            return

        # Draw background gradient based on faction
        faction_colors = {
            NPCFaction.PLAYER_FRIENDLY: QColor(76, 175, 80, 100),
            NPCFaction.PLAYER_HOSTILE: QColor(244, 67, 54, 100),
            NPCFaction.NEUTRAL: QColor(255, 152, 0, 100),
        }

        bg_color = faction_colors.get(self.npc.faction, QColor(136, 136, 136, 100))
        painter.fillRect(self.rect(), bg_color)

        # Try to load portrait image
        if self.npc.portrait_path and os.path.exists(self.npc.portrait_path):
            pixmap = QPixmap(self.npc.portrait_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(self.size() - 4, self.size() - 4,
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                painter.drawPixmap(2, 2, scaled_pixmap)
            else:
                # Draw placeholder
                self.draw_placeholder_portrait(painter)
        else:
            # Draw placeholder
            self.draw_placeholder_portrait(painter)

        # Draw level indicator
        painter.setPen(QPen(QColor(255, 255, 255, 200)))
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        level_text = f"Lv.{self.npc.level}"
        painter.drawText(self.rect().adjusted(5, 5, -5, -25), Qt.AlignBottom | Qt.AlignRight, level_text)

    def draw_placeholder_portrait(self, painter):
        """Draw placeholder portrait when no image is available"""
        # Type-based icons
        type_icons = {
            NPCType.VILLAGER: "👤",
            NPCType.GUARD: "⚔️",
            NPCType.MERCHANT: "🛒",
            NPCType.QUEST_GIVER: "📜",
            NPCType.TRAINER: "🎯",
            NPCType.ENEMY: "🗡️",
            NPCType.BOSS: "👹",
            NPCType.COMPANION: "🐕",
            NPCType.NEUTRAL: "🤷",
            NPCType.CHILD: "👶",
            NPCType.ELDER: "👴"
        }

        icon = type_icons.get(self.npc.npc_type, "🤷")

        painter.setPen(QColor("#ccc"))
        painter.setFont(QFont("Arial", 32))
        painter.drawText(self.rect(), Qt.AlignCenter, icon)


class NPCDetailWidget(QWidget):
    """Widget for displaying detailed NPC information"""

    npc_selected = pyqtSignal(NPCData)  # Emitted when an NPC is selected

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_npc = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Portrait and basic info
        header_layout = QHBoxLayout()

        # Portrait
        self.portrait_widget = NPCPortraitWidget()
        header_layout.addWidget(self.portrait_widget)

        # Basic info
        info_layout = QVBoxLayout()

        self.name_label = QLabel("Select an NPC")
        name_font = self.name_label.font()
        name_font.setPointSize(16)
        name_font.setBold(True)
        self.name_label.setFont(name_font)
        info_layout.addWidget(self.name_label)

        self.type_label = QLabel("")
        self.faction_label = QLabel("")
        self.level_label = QLabel("")

        info_layout.addWidget(self.type_label)
        info_layout.addWidget(self.faction_label)
        info_layout.addWidget(self.level_label)

        info_layout.addStretch()
        header_layout.addLayout(info_layout)

        # Add NPC to dialogue button
        self.add_to_dialogue_btn = QPushButton("➕ Add to Dialogue")
        self.add_to_dialogue_btn.clicked.connect(self.add_npc_to_dialogue)
        self.add_to_dialogue_btn.setEnabled(False)
        info_layout.addWidget(self.add_to_dialogue_btn)

        layout.addLayout(header_layout)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout(desc_group)

        self.description_text = QTextEdit()
        self.description_text.setReadOnly(True)
        self.description_text.setMaximumHeight(80)
        desc_layout.addWidget(self.description_text)

        layout.addWidget(desc_group)

        # Details
        details_group = QGroupBox("Details")
        details_form = QFormLayout(details_group)

        self.location_label = QLabel("")
        self.voice_label = QLabel("")
        self.hours_label = QLabel("")
        self.style_label = QLabel("")

        details_form.addRow("Location:", self.location_label)
        details_form.addRow("Voice:", self.voice_label)
        details_form.addRow("Available:", self.hours_label)
        details_form.addRow("Style:", self.style_label)

        layout.addWidget(details_group)

        # Personality traits
        personality_group = QGroupBox("Personality")
        personality_layout = QVBoxLayout(personality_group)

        self.personality_tags = QLabel("")
        self.personality_tags.setWordWrap(True)
        personality_layout.addWidget(self.personality_tags)

        layout.addWidget(personality_group)

        # Tags
        tags_group = QGroupBox("Tags")
        tags_layout = QVBoxLayout(tags_group)

        self.tags_list = QTextEdit()
        self.tags_list.setReadOnly(True)
        self.tags_list.setMaximumHeight(60)
        tags_layout.addWidget(self.tags_list)

        layout.addWidget(tags_group)

        # Dialogue topics
        topics_group = QGroupBox("Known Dialogue Topics")
        topics_layout = QVBoxLayout(topics_group)

        self.topics_list = QTextEdit()
        self.topics_list.setReadOnly(True)
        self.topics_list.setMaximumHeight(60)
        topics_layout.addWidget(self.topics_list)

        layout.addWidget(topics_group)

        # Items
        items_group = QGroupBox("Known Items")
        items_layout = QVBoxLayout(items_group)

        self.items_list = QTextEdit()
        self.items_list.setReadOnly(True)
        self.items_list.setMaximumHeight(60)
        items_layout.addWidget(self.items_list)

        layout.addWidget(items_group)

        layout.addStretch()

    def setNPC(self, npc: NPCData):
        """Set the NPC to display"""
        self.current_npc = npc
        self.portrait_widget.setNPC(npc)

        # Update labels
        self.name_label.setText(npc.name)
        self.type_label.setText(f"Type: {npc.npc_type.value.title()}")
        self.faction_label.setText(f"Faction: {npc.faction.value.title()}")
        self.level_label.setText(f"Level: {npc.level}")

        self.description_text.setPlainText(npc.description)
        self.location_label.setText(npc.location)
        self.voice_label.setText(npc.voice_type)
        self.hours_label.setText(npc.available_hours)
        self.style_label.setText(npc.dialogue_style.title())

        # Update lists
        self.personality_tags.setText(", ".join(npc.personality) if npc.personality else "None")
        self.tags_list.setPlainText(", ".join(npc.tags) if npc.tags else "None")
        self.topics_list.setPlainText(", ".join(npc.dialogue_topics) if npc.dialogue_topics else "None")
        self.items_list.setPlainText(", ".join(npc.known_items) if npc.known_items else "None")

        # Enable add button
        self.add_to_dialogue_btn.setEnabled(True)

    def clear(self):
        """Clear the display"""
        self.current_npc = None
        self.portrait_widget.setNPC(None)

        self.name_label.setText("Select an NPC")
        self.type_label.setText("")
        self.faction_label.setText("")
        self.level_label.setText("")

        self.description_text.clear()
        self.location_label.setText("")
        self.voice_label.setText("")
        self.hours_label.setText("")
        self.style_label.setText("")

        self.personality_tags.setText("")
        self.tags_list.clear()
        self.topics_list.clear()
        self.items_list.clear()

        self.add_to_dialogue_btn.setEnabled(False)

    def add_npc_to_dialogue(self):
        """Add NPC to current dialogue"""
        if self.current_npc:
            self.npc_selected.emit(self.current_npc)


class NPCBrowserWidget(QWidget):
    """Main NPC browser widget"""

    npc_selected = pyqtSignal(NPCData)
    npc_added_to_dialogue = pyqtSignal(NPCData)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.npcs = []
        self.setup_ui()
        self.load_sample_data()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("NPC Browser")
        title_font = title_label.font()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)

        # Search and filters
        filter_group = QGroupBox("Search & Filters")
        filter_layout = QVBoxLayout(filter_group)

        # Search bar
        search_layout = QHBoxLayout()
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search NPCs by name or tags...")
        self.search_edit.textChanged.connect(self.on_search_text_changed)
        search_layout.addWidget(QLabel("🔍"))
        search_layout.addWidget(self.search_edit)
        filter_layout.addLayout(search_layout)

        # Filter options
        filters_row1 = QHBoxLayout()

        # Type filter
        filters_row1.addWidget(QLabel("Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["all", "villager", "guard", "merchant", "quest_giver",
                                  "trainer", "enemy", "boss", "companion", "neutral", "child", "elder"])
        self.type_combo.currentTextChanged.connect(self.on_filters_changed)
        filters_row1.addWidget(self.type_combo)

        # Faction filter
        filters_row1.addWidget(QLabel("Faction:"))
        self.faction_combo = QComboBox()
        self.faction_combo.addItems(["all", "player_friendly", "player_hostile", "neutral",
                                    "merchant_guild", "guard_guild", "rogue_guild", "mage_guild"])
        self.faction_combo.currentTextChanged.connect(self.on_filters_changed)
        filters_row1.addWidget(self.faction_combo)

        filter_layout.addLayout(filters_row1)

        # Location and level filters
        filters_row2 = QHBoxLayout()

        # Location filter
        filters_row2.addWidget(QLabel("Location:"))
        self.location_combo = QComboBox()
        self.location_combo.setEditable(True)
        self.location_combo.addItems(["all"])
        self.location_combo.currentTextChanged.connect(self.on_filters_changed)
        filters_row2.addWidget(self.location_combo)

        # Level filter
        filters_row2.addWidget(QLabel("Level:"))
        self.level_slider = QSlider(Qt.Horizontal)
        self.level_slider.setRange(1, 100)
        self.level_slider.setValue(50)
        self.level_slider.setMinimumWidth(100)
        self.level_slider.valueChanged.connect(self.on_level_filter_changed)
        filters_row2.addWidget(self.level_slider)

        self.level_label = QLabel("1-100")
        filters_row2.addWidget(self.level_label)

        filter_layout.addLayout(filters_row2)

        # Quick filters
        quick_filters_layout = QHBoxLayout()

        self.friendly_btn = QCheckBox("Friendly")
        self.friendly_btn.toggled.connect(lambda checked: self.toggle_quick_filter("friendly", checked))
        quick_filters_layout.addWidget(self.friendly_btn)

        self.merchant_btn = QCheckBox("Merchants")
        self.merchant_btn.toggled.connect(lambda checked: self.toggle_quick_filter("merchant", checked))
        quick_filters_layout.addWidget(self.merchant_btn)

        self.quest_btn = QCheckBox("Quest Givers")
        self.quest_btn.toggled.connect(lambda checked: self.toggle_quick_filter("quest_giver", checked))
        quick_filters_layout.addWidget(self.quest_btn)

        quick_filters_layout.addStretch()
        filter_layout.addLayout(quick_filters_layout)

        layout.addWidget(filter_group)

        # Content area with splitter
        content_splitter = QSplitter(Qt.Horizontal)

        # NPC list
        list_widget = QWidget()
        list_layout = QVBoxLayout(list_widget)

        list_header = QHBoxLayout()
        list_header.addWidget(QLabel("NPCs"))
        self.count_label = QLabel("(0)")
        list_header.addWidget(self.count_label)
        list_header.addStretch()
        list_layout.addLayout(list_header)

        self.npc_tree = QTreeWidget()
        self.npc_tree.setHeaderLabels(["Name", "Level", "Type", "Location", "Tags"])
        self.npc_tree.setAlternatingRowColors(True)
        self.npc_tree.setSelectionMode(QAbstractItemView.SingleSelection)
        self.npc_tree.itemSelectionChanged.connect(self.on_npc_selected)
        self.npc_tree.itemDoubleClicked.connect(self.on_npc_double_clicked)

        # Set column widths
        header = self.npc_tree.header()
        header.setStretchLastSection(True)
        header.resizeSection(0, 200)  # Name
        header.resizeSection(1, 60)   # Level
        header.resizeSection(2, 100)  # Type
        header.resizeSection(3, 150)  # Location
        # Tags column stretches

        list_layout.addWidget(self.npc_tree)
        content_splitter.addWidget(list_widget)

        # NPC details
        self.detail_widget = NPCDetailWidget()
        self.detail_widget.npc_selected.connect(self.npc_selected)
        self.detail_widget.npc_selected.connect(self.on_npc_added_to_dialogue)
        content_splitter.addWidget(self.detail_widget)

        content_splitter.setSizes([400, 400])
        layout.addWidget(content_splitter)

        # Status bar
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #888; font-style: italic;")
        layout.addWidget(self.status_label)

    def load_sample_data(self):
        """Load sample NPC data"""
        self.npcs = [
            NPCData(
                id="villager_001",
                name="Elder Johnson",
                npc_type=NPCType.ELDER,
                faction=NPCFaction.PLAYER_FRIENDLY,
                level=5,
                description="A wise old man who has lived in the village for decades. He knows many local legends and secrets.",
                location="Greenhaven Village",
                voice_type="elderly_male",
                personality=["wise", "friendly", "storyteller", "cautious"],
                tags=["elder", "storyteller", "village", "quests"],
                dialogue_topics=["local legends", "village history", "weather", "quests"],
                known_items=["healing_potion", "map", "gold_coins"],
                special_abilities=["gives quests", "storytelling", "wisdom"],
                available_hours="全天",
                dialogue_style="wise",
                gender="male"
            ),
            NPCData(
                id="guard_001",
                name="Captain Marcus",
                npc_type=NPCType.GUARD,
                faction=NPCFaction.PLAYER_FRIENDLY,
                level=12,
                description="The stoic captain of the village guard. Loyal to his duty but fair in his judgments.",
                location="Greenhaven Gate",
                voice_type="authoritative_male",
                personality=["stern", "honorable", "protective", "by_the_book"],
                tags=["guard", "captain", "security", "rules"],
                dialogue_topics=["security", "village_rules", "threats", "travel", "permits"],
                known_items=["sword", "shield", "keys"],
                special_abilities=["gate_control", "arrest", "investigation"],
                available_hours="全天",
                dialogue_style="formal",
                gender="male"
            ),
            NPCData(
                id="merchant_001",
                name="Silas the Trader",
                npc_type=NPCType.MERCHANT,
                faction=NPCFaction.MERCHANT_GUILD,
                level=8,
                description="A traveling merchant with a keen eye for valuable items. Always looking for good deals.",
                location="Market Square",
                voice_type="friendly_male",
                personality=["shrewd", "friendly", "talkative", "bargainer"],
                tags=["merchant", "trader", "items", "bargaining"],
                dialogue_topics=["trade", "items", "prices", "rumors", "trade_routes"],
                known_items=["various_goods", "rare_items", "trade_goods"],
                special_abilities=["trading", "appraisal", "market_knowledge"],
                available_hours="9:00-17:00",
                dialogue_style="merchant",
                gender="male"
            ),
            NPCData(
                id="quest_giver_001",
                name="Mira the Guide",
                npc_type=NPCType.QUEST_GIVER,
                faction=NPCType.PLAYER_FRIENDLY,
                level=10,
                description="A mysterious guide who appears when adventurers need direction. Seems to know more than she lets on.",
                location="Unknown",
                voice_type="enigmatic_female",
                personality=["mysterious", "helpful", "cryptic", "knowledgeable"],
                tags=["quest_giver", "guide", "mystery", "advice"],
                dialogue_topics=["quests", "advice", "directions", "prophecies", "ancients"],
                known_items=["ancient_map", "quest_items", "mysterious_artifacts"],
                special_abilities=["quest_guidance", "teleportation", "prophecy"],
                available_hours="随时出现",
                dialogue_style="cryptic",
                gender="female"
            ),
            NPCData(
                id="child_001",
                name="Little Timmy",
                npc_type=NPCType.CHILD,
                faction=NPCType.PLAYER_FRIENDLY,
                level=2,
                description="A cheerful child who loves to play and explore. Often has interesting information about the village.",
                location="Village Square",
                voice_type="child_male",
                personality=["playful", "curious", "friendly", "talkative"],
                tags=["child", "playful", "innocent", "information"],
                dialogue_topics=["games", "toys", "friends", "parents", "secrets"],
                known_items=["toy_sword", "marbles", "candy"],
                special_abilities=["child_network", "innocent_observations"],
                available_hours="10:00-18:00",
                dialogue_style="childish",
                gender="male"
            ),
            NPCData(
                id="enemy_001",
                name="Goblin Scout",
                npc_type=NPCType.ENEMY,
                faction=NPCFaction.PLAYER_HOSTILE,
                level=15,
                description="A sneaky goblin scout watching the village. Armed with a short sword and always alert.",
                location="Forest Outskirts",
                voice_type="guttural",
                personality=["aggressive", "cunning", "hostile", "territorial"],
                tags=["goblin", "enemy", "scout", "hostile"],
                dialogue_topics=["threats", "territory", "treasure", "raids"],
                known_items=["stolen_goods", "weapon", "treasure_map"],
                special_abilities=["scouting", "ambush_tactics", "quick_escape"],
                available_hours="夜间",
                dialogue_style="hostile",
                gender="male"
            )
        ]

        self.update_display()

    def update_display(self):
        """Update the display with current NPCs"""
        self.npc_tree.clear()

        for npc in self.npcs:
            item = NPCTreeWidgetItem(npc)
            self.npc_tree.addTopLevelItem(item)

        self.count_label.setText(f"({len(self.npcs)})")
        self.status_label.setText(f"Loaded {len(self.npcs)} NPCs")

    def on_search_text_changed(self, text: str):
        """Handle search text change"""
        # Simple search implementation
        items = []
        for i in range(self.npc_tree.topLevelItemCount()):
            item = self.npc_tree.topLevelItem(i)
            items.append(item)

        search_text = text.lower().strip()
        if not search_text:
            # Show all items
            for item in items:
                item.setHidden(False)
        else:
            # Filter items
            for item in items:
                npc = item.npc
                should_show = (
                    search_text in npc.name.lower() or
                    any(search_text in tag.lower() for tag in npc.tags) or
                    search_text in npc.description.lower()
                )
                item.setHidden(not should_show)

        visible_count = sum(1 for item in items if not item.isHidden())
        self.count_label.setText(f"({visible_count})")

    def on_filters_changed(self):
        """Handle filter changes"""
        # Implementation would filter the tree widget items
        pass

    def on_level_filter_changed(self, value: int):
        """Handle level filter change"""
        self.level_label.setText(f"1-{value}")
        # Implementation would filter by level
        pass

    def toggle_quick_filter(self, filter_type: str, checked: bool):
        """Toggle quick filter"""
        # Implementation would apply quick filter
        pass

    def on_npc_selected(self):
        """Handle NPC selection"""
        items = self.npc_tree.selectedItems()
        if items:
            item = items[0]
            if hasattr(item, 'npc'):
                self.detail_widget.setNPC(item.npc)

    def on_npc_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle NPC double click - add to dialogue"""
        if hasattr(item, 'npc'):
            self.npc_added_to_dialogue.emit(item.npc)
            self.status_label.setText(f"Added {item.npc.name} to dialogue")

    def on_npc_added_to_dialogue(self, npc: NPCData):
        """Handle NPC added to dialogue"""
        self.npc_added_to_dialogue.emit(npc)
        self.status_label.setText(f"Added {npc.name} to dialogue")

    def get_selected_npc(self) -> Optional[NPCData]:
        """Get currently selected NPC"""
        items = self.npc_tree.selectedItems()
        if items and hasattr(items[0], 'npc'):
            return items[0].npc
        return None

    def add_npc(self, npc: NPCData):
        """Add an NPC to the browser"""
        self.npcs.append(npc)
        item = NPCTreeWidgetItem(npc)
        self.npc_tree.addTopLevelItem(item)
        self.update_display()

    def remove_npc(self, npc_id: str):
        """Remove an NPC from the browser"""
        self.npcs = [npc for npc in self.npcs if npc.id != npc_id]
        self.update_display()

    def get_npcs_by_type(self, npc_type: NPCType) -> List[NPCData]:
        """Get NPCs by type"""
        return [npc for npc in self.npcs if npc.npc_type == npc_type]

    def get_npcs_by_faction(self, faction: NPCFaction) -> List[NPCData]:
        """Get NPCs by faction"""
        return [npc for npc in self.npcs if npc.faction == faction]

    def get_npcs_by_location(self, location: str) -> List[NPCData]:
        """Get NPCs by location"""
        return [npc for npc in self.npcs if location.lower() in npc.location.lower()]


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Create and show NPC browser
    browser = NPCBrowserWidget()
    browser.resize(800, 600)
    browser.setWindowTitle("NPC Browser")
    browser.show()

    # Test signals
    def on_npc_selected(npc: NPCData):
        print(f"Selected NPC: {npc.name} ({npc.npc_type.value})")

    def on_npc_added_to_dialogue(npc: NPCData):
        print(f"Added NPC to dialogue: {npc.name}")

    browser.npc_selected.connect(on_npc_selected)
    browser.npc_added_to_dialogue.connect(on_npc_added_to_dialogue)

    sys.exit(app.exec())