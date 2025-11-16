#!/usr/bin/env python3
"""
NPC Browser Dialog

A searchable, filterable NPC browser for selecting:
- Quest givers
- Dialogue speakers
- Involved NPCs

Features:
- Search by name and ID
- Filter by race, faction, and map
- Preview pane with NPC info
- Single and multi-select modes
- Keyboard navigation
- Fast indexed searching
"""

from pathlib import Path
from typing import List, Dict, Optional, Set
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QGroupBox,
    QTextEdit,
    QSplitter,
    QHeaderView,
    QMessageBox,
    QAbstractItemView,
)
from PySide6.QtCore import Qt, Signal, QThread, QObject, Slot
from PySide6.QtGui import QFont

try:
    from TirganachReloaded.tirganach import GameData
    from TirganachReloaded.tirganach.types import Race, Language
    from TirganachReloaded.cff_editor.logging_config import get_logger

    GAMEDATA_AVAILABLE = True
    logger = get_logger(__name__)
except ImportError:
    GAMEDATA_AVAILABLE = False
    import logging

    logger = logging.getLogger(__name__)


class SelectionMode(Enum):
    """NPC selection modes"""

    SINGLE = "single"  # For quest giver, speaker
    MULTI = "multi"  # For involved NPCs


@dataclass
class NPCData:
    """NPC data structure"""

    npc_id: int
    name: str
    race: str = "Unknown"
    faction: str = "Unknown"
    level: int = 1
    stats_id: int = 0
    map_hint: str = ""  # Optional map/region info
    creature_type: str = "NPC"

    def matches_search(self, search_text: str) -> bool:
        """Check if NPC matches search text"""
        search_lower = search_text.lower()
        return (
            search_lower in self.name.lower()
            or search_lower in str(self.npc_id)
            or search_lower in self.faction.lower()
            or search_lower in self.map_hint.lower()
        )

    def matches_filters(
        self, race_filter: str, faction_filter: str, map_filter: str
    ) -> bool:
        """Check if NPC matches active filters"""
        if race_filter and race_filter != "All Races":
            if race_filter.lower() not in self.race.lower():
                return False

        if faction_filter and faction_filter != "All Factions":
            if faction_filter.lower() not in self.faction.lower():
                return False

        if map_filter and map_filter != "All Maps":
            if map_filter.lower() not in self.map_hint.lower():
                return False

        return True


class NPCLoaderWorker(QObject):
    """Worker thread for loading NPCs from CFF database"""

    npcs_loaded = Signal(list)
    progress_update = Signal(str)
    finished = Signal()

    def __init__(self, gamedata_path: Path, limit: Optional[int] = None):
        super().__init__()
        self.gamedata_path = gamedata_path
        self.limit = limit  # Limit number of NPCs to load (for fast mode)

    def load_npcs(self):
        """Load NPCs from GameData.cff"""
        try:
            self.progress_update.emit("Loading GameData.cff...")

            if not GAMEDATA_AVAILABLE:
                logger.error("GameData module not available")
                self.npcs_loaded.emit([])
                self.finished.emit()
                return

            if not self.gamedata_path.exists():
                logger.error(f"GameData.cff not found at: {self.gamedata_path}")
                self.npcs_loaded.emit([])
                self.finished.emit()
                return

            # Load game data
            from TirganachReloaded.tirganach import GameData as GD

            gd = GD(str(self.gamedata_path))

            npcs = []

            # Load from NPC names table
            self.progress_update.emit("Loading NPC names...")
            npc_names = gd.npc_names or []

            # Pre-cache lookups for speed
            from TirganachReloaded.tirganach.types import Language as Lang

            creature_dict = {}
            stats_dict = {}
            loc_en_dict = {}
            loc_de_dict = {}

            self.progress_update.emit("Indexing creatures...")
            for creature in gd.creatures:
                creature_dict[creature.creature_id] = creature

            self.progress_update.emit("Indexing stats...")
            for stat in gd.creature_stats:
                stats_dict[stat.stats_id] = stat

            self.progress_update.emit("Indexing localizations...")
            for loc in gd.localisation:
                if loc.language == Lang.ENGLISH and loc.text and loc.text.strip():
                    loc_en_dict[loc.text_id] = loc.text.strip()
                elif loc.language == Lang.GERMAN and loc.text and loc.text.strip():
                    loc_de_dict[loc.text_id] = loc.text.strip()

            # Process NPCs - smart filtering for fast loading
            # Priority 1: NPCs with names (most useful for quests)
            # Priority 2: High ID NPCs (10000+, likely quest NPCs)
            named_npcs = []
            high_id_npcs = []

            for n in npc_names:
                if n.name_id > 0:
                    # Check if it has an actual name in cache
                    if n.name_id in loc_en_dict or n.name_id in loc_de_dict:
                        named_npcs.append(n)
                    elif n.npc_id >= 10000:
                        high_id_npcs.append(n)
                elif n.npc_id >= 10000:
                    high_id_npcs.append(n)

            # Load named NPCs first, then high ID NPCs
            filtered_npc_names = named_npcs + high_id_npcs

            # Apply limit if specified (for fast loading)
            if self.limit and len(filtered_npc_names) > self.limit:
                filtered_npc_names = filtered_npc_names[: self.limit]
                total = self.limit
                self.progress_update.emit(
                    f"Quick loading {total} most relevant NPCs..."
                )
            else:
                total = len(filtered_npc_names)
                self.progress_update.emit(f"Loading all {total} NPCs...")

            for idx, npc_name in enumerate(filtered_npc_names):
                # Update progress every 200 NPCs
                if idx % 200 == 0:
                    self.progress_update.emit(f"Loading NPCs... {idx}/{total}")
                npc_id = npc_name.npc_id

                # Get localized name - try German first, then English, then use ID
                name = f"NPC {npc_id}"
                if hasattr(npc_name, "name") and npc_name.name:
                    name = str(npc_name.name)
                elif npc_name.name_id and npc_name.name_id > 0:
                    # Try German first using cached dict
                    if npc_name.name_id in loc_de_dict:
                        text = loc_de_dict[npc_name.name_id]
                        if text and text.strip():
                            name = text.strip()
                    # Try English as fallback
                    elif npc_name.name_id in loc_en_dict:
                        text = loc_en_dict[npc_name.name_id]
                        if text and text.strip():
                            name = text.strip() + " [EN]"

                # Try to find associated creature for more info
                race_str = "Unknown"
                level = 1
                stats_id = 0
                faction = "Unknown"

                # Look up in creatures table using cached dict
                if npc_id in creature_dict:
                    creature = creature_dict[npc_id]
                    stats_id = creature.stats_id

                    # Get stats for race and level using cached dict
                    if stats_id in stats_dict:
                        stat = stats_dict[stats_id]
                        level = stat.level
                        try:
                            if hasattr(stat.race, "name"):
                                race_str = stat.race.name.replace("_", " ").title()
                            else:
                                race_str = (
                                    str(stat.race)
                                    .replace("Race._", "")
                                    .replace("_", " ")
                                    .title()
                                )
                        except:
                            race_str = "Unknown"

                npc_data = NPCData(
                    npc_id=npc_id,
                    name=name,
                    race=race_str,
                    faction=faction,
                    level=level,
                    stats_id=stats_id,
                )

                npcs.append(npc_data)

            self.progress_update.emit(f"Loaded {len(npcs)} NPCs")
            self.npcs_loaded.emit(npcs)

        except Exception as e:
            logger.error(f"Failed to load NPCs: {e}", exc_info=True)
            self.npcs_loaded.emit([])
        finally:
            self.finished.emit()


class NPCBrowserDialog(QDialog):
    """
    Browse and select NPCs for quests

    Usage:
        # Single selection mode (quest giver)
        dialog = NPCBrowserDialog(mode=SelectionMode.SINGLE)
        if dialog.exec():
            npc = dialog.get_selected_npc()

        # Multi-selection mode (involved NPCs)
        dialog = NPCBrowserDialog(mode=SelectionMode.MULTI)
        if dialog.exec():
            npcs = dialog.get_selected_npcs()
    """

    def __init__(self, mode: SelectionMode = SelectionMode.SINGLE, parent=None):
        super().__init__(parent)

        self.mode = mode
        self.npcs: List[NPCData] = []
        self.filtered_npcs: List[NPCData] = []
        self.selected_npc: Optional[NPCData] = None
        self.selected_npcs: List[NPCData] = []

        # Setup UI
        self.setWindowTitle("NPC Browser - Select NPC")
        self.setModal(True)
        self.resize(1000, 700)

        self._setup_ui()
        self._load_npcs()

    def _setup_ui(self):
        """Setup user interface"""
        layout = QVBoxLayout(self)

        # Header with status
        header_layout = QHBoxLayout()
        self.status_label = QLabel("Loading NPCs...")
        self.status_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(self.status_label)
        header_layout.addStretch()

        if self.mode == SelectionMode.MULTI:
            self.selection_count_label = QLabel("Selected: 0")
            header_layout.addWidget(self.selection_count_label)

        layout.addLayout(header_layout)

        # Search and filter section
        filter_group = self._create_filter_group()
        layout.addWidget(filter_group)

        # Main content with splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left: NPC table
        table_widget = self._create_npc_table()
        splitter.addWidget(table_widget)

        # Right: Preview pane
        preview_widget = self._create_preview_pane()
        splitter.addWidget(preview_widget)

        splitter.setSizes([600, 400])
        layout.addWidget(splitter)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.ok_btn = QPushButton("Select")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(False)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)

        layout.addLayout(btn_layout)

    def _create_filter_group(self) -> QGroupBox:
        """Create search and filter controls"""
        group = QGroupBox("Search & Filter")
        layout = QVBoxLayout(group)

        # Search bar
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name, ID, faction, or map...")
        self.search_edit.textChanged.connect(self._apply_filters)
        search_layout.addWidget(self.search_edit)

        layout.addLayout(search_layout)

        # Filters
        filter_layout = QHBoxLayout()

        # Race filter
        filter_layout.addWidget(QLabel("Race:"))
        self.race_filter = QComboBox()
        self.race_filter.addItem("All Races")
        self.race_filter.addItems(["Human", "Elf", "Dwarf", "Orc", "Troll", "Dark Elf"])
        self.race_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.race_filter)

        # Faction filter
        filter_layout.addWidget(QLabel("Faction:"))
        self.faction_filter = QComboBox()
        self.faction_filter.addItem("All Factions")
        self.faction_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.faction_filter)

        # Map filter
        filter_layout.addWidget(QLabel("Map:"))
        self.map_filter = QComboBox()
        self.map_filter.addItem("All Maps")
        self.map_filter.currentTextChanged.connect(self._apply_filters)
        filter_layout.addWidget(self.map_filter)

        filter_layout.addStretch()

        layout.addLayout(filter_layout)

        return group

    def _create_npc_table(self) -> QGroupBox:
        """Create NPC table widget"""
        group = QGroupBox("NPCs")
        layout = QVBoxLayout(group)

        # Table
        self.npc_table = QTableWidget(0, 5)
        self.npc_table.setHorizontalHeaderLabels(
            ["ID", "Name", "Race", "Level", "Map/Region"]
        )

        # Selection mode
        if self.mode == SelectionMode.SINGLE:
            self.npc_table.setSelectionMode(
                QAbstractItemView.SelectionMode.SingleSelection
            )
        else:
            self.npc_table.setSelectionMode(
                QAbstractItemView.SelectionMode.MultiSelection
            )

        self.npc_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.npc_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)

        # Auto-resize columns
        header = self.npc_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Signals
        self.npc_table.itemSelectionChanged.connect(self._on_selection_changed)
        self.npc_table.doubleClicked.connect(self._on_double_click)

        layout.addWidget(self.npc_table)

        return group

    def _create_preview_pane(self) -> QGroupBox:
        """Create NPC preview pane"""
        group = QGroupBox("NPC Preview")
        layout = QVBoxLayout(group)

        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Select an NPC to view details...")

        layout.addWidget(self.preview_text)

        return group

    def _load_npcs(self):
        """Load NPCs in background thread"""
        # Find GameData.cff
        gamedata_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "OriginalGameFiles"
            / "data"
            / "GameData.cff"
        )

        if not gamedata_path.exists():
            QMessageBox.warning(
                self,
                "GameData Not Found",
                f"Could not find GameData.cff at:\n{gamedata_path}\n\nPlease ensure the game files are in the correct location.",
            )
            self.npcs = []
            self._populate_table()
            return

        # Create worker thread with fast loading (limit to 2000 most relevant NPCs)
        self.worker_thread = QThread()
        self.worker = NPCLoaderWorker(gamedata_path, limit=2000)
        self.worker.moveToThread(self.worker_thread)

        # Connect signals
        self.worker.npcs_loaded.connect(self._on_npcs_loaded)
        self.worker.progress_update.connect(self._on_progress_update)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.started.connect(self.worker.load_npcs)

        # Start loading
        self.worker_thread.start()

    @Slot(list)
    def _on_npcs_loaded(self, npcs: List[NPCData]):
        """Handle NPCs loaded"""
        self.npcs = npcs
        self.filtered_npcs = npcs.copy()

        # Populate filter dropdowns
        self._populate_filters()

        # Populate table
        self._populate_table()

        # Update status
        self.status_label.setText(f"Loaded {len(npcs)} NPCs")

    @Slot(str)
    def _on_progress_update(self, message: str):
        """Handle progress update"""
        self.status_label.setText(message)

    def _populate_filters(self):
        """Populate filter dropdowns from loaded NPCs"""
        # Get unique factions
        factions = sorted(
            set(npc.faction for npc in self.npcs if npc.faction != "Unknown")
        )
        self.faction_filter.addItems(factions)

        # Get unique maps
        maps = sorted(set(npc.map_hint for npc in self.npcs if npc.map_hint))
        self.map_filter.addItems(maps)

    def _populate_table(self, npcs: Optional[List[NPCData]] = None):
        """Populate NPC table"""
        if npcs is None:
            npcs = self.filtered_npcs

        self.npc_table.setRowCount(len(npcs))

        for row, npc in enumerate(npcs):
            self.npc_table.setItem(row, 0, QTableWidgetItem(str(npc.npc_id)))
            self.npc_table.setItem(row, 1, QTableWidgetItem(npc.name))
            self.npc_table.setItem(row, 2, QTableWidgetItem(npc.race))
            self.npc_table.setItem(row, 3, QTableWidgetItem(str(npc.level)))
            self.npc_table.setItem(row, 4, QTableWidgetItem(npc.map_hint or "-"))

    def _apply_filters(self):
        """Apply search and filters to NPC list"""
        search_text = self.search_edit.text()
        race_filter = self.race_filter.currentText()
        faction_filter = self.faction_filter.currentText()
        map_filter = self.map_filter.currentText()

        filtered = []
        for npc in self.npcs:
            # Apply search
            if search_text and not npc.matches_search(search_text):
                continue

            # Apply filters
            if not npc.matches_filters(race_filter, faction_filter, map_filter):
                continue

            filtered.append(npc)

        self.filtered_npcs = filtered
        self._populate_table(filtered)

        # Update status
        total = len(self.npcs)
        showing = len(filtered)
        if showing == total:
            self.status_label.setText(f"Loaded {total} NPCs")
        else:
            self.status_label.setText(f"Showing {showing} of {total} NPCs")

    def _on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.npc_table.selectionModel().selectedRows()

        if not selected_rows:
            self.ok_btn.setEnabled(False)
            self.preview_text.clear()
            return

        self.ok_btn.setEnabled(True)

        # Get selected NPC(s)
        if self.mode == SelectionMode.SINGLE:
            row = selected_rows[0].row()
            if row < len(self.filtered_npcs):
                self.selected_npc = self.filtered_npcs[row]
                self._update_preview(self.selected_npc)
        else:
            self.selected_npcs = []
            for selected_row in selected_rows:
                row = selected_row.row()
                if row < len(self.filtered_npcs):
                    self.selected_npcs.append(self.filtered_npcs[row])

            # Update selection count
            if hasattr(self, "selection_count_label"):
                self.selection_count_label.setText(
                    f"Selected: {len(self.selected_npcs)}"
                )

            # Preview first selected
            if self.selected_npcs:
                self._update_preview(self.selected_npcs[0])

    def _update_preview(self, npc: NPCData):
        """Update preview pane with NPC details"""
        preview_html = f"""
        <h3>{npc.name}</h3>
        <table>
        <tr><td><b>ID:</b></td><td>{npc.npc_id}</td></tr>
        <tr><td><b>Race:</b></td><td>{npc.race}</td></tr>
        <tr><td><b>Level:</b></td><td>{npc.level}</td></tr>
        <tr><td><b>Faction:</b></td><td>{npc.faction}</td></tr>
        <tr><td><b>Stats ID:</b></td><td>{npc.stats_id}</td></tr>
        <tr><td><b>Type:</b></td><td>{npc.creature_type}</td></tr>
        """

        if npc.map_hint:
            preview_html += f"<tr><td><b>Map:</b></td><td>{npc.map_hint}</td></tr>"

        preview_html += "</table>"

        self.preview_text.setHtml(preview_html)

    def _on_double_click(self):
        """Handle double-click on NPC (accept selection)"""
        if self.mode == SelectionMode.SINGLE and self.selected_npc:
            self.accept()

    # Public API

    def get_selected_npc(self) -> Optional[NPCData]:
        """Get selected NPC (single selection mode)"""
        return self.selected_npc

    def get_selected_npcs(self) -> List[NPCData]:
        """Get selected NPCs (multi-selection mode)"""
        return self.selected_npcs

    def get_selected_npc_id(self) -> Optional[int]:
        """Get selected NPC ID (convenience method)"""
        npc = self.selected_npc
        if npc:
            return npc.npc_id
        return None

    def get_selected_npc_ids(self) -> List[int]:
        """Get selected NPC IDs (convenience method)"""
        return [npc.npc_id for npc in self.selected_npcs]

    def get_selected_npc_name(self) -> Optional[str]:
        """Get selected NPC name (convenience method)"""
        npc = self.selected_npc
        if npc:
            return npc.name
        return None


# Convenience functions for quick usage


def choose_quest_giver(parent=None) -> Optional[NPCData]:
    """Quick helper to choose a quest giver NPC"""
    dialog = NPCBrowserDialog(mode=SelectionMode.SINGLE, parent=parent)
    if dialog.exec():
        return dialog.get_selected_npc()
    return None


def choose_involved_npcs(parent=None) -> List[NPCData]:
    """Quick helper to choose multiple involved NPCs"""
    dialog = NPCBrowserDialog(mode=SelectionMode.MULTI, parent=parent)
    if dialog.exec():
        return dialog.get_selected_npcs()
    return []


if __name__ == "__main__":
    """Test the NPC browser"""
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test single selection
    dialog = NPCBrowserDialog(mode=SelectionMode.SINGLE)
    if dialog.exec():
        npc = dialog.get_selected_npc()
        if npc:
            print(f"Selected NPC: {npc.name} (ID: {npc.npc_id})")

    sys.exit(0)
