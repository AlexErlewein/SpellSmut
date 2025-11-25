"""
External Resource Integration System

This module provides integration with external resources including:
- SpellForce Wiki integration
- Item and equipment databases
- NPC and character databases
- Quest template libraries
- External file import/export
- API connections to game resources
- Reference material integration
"""

import json
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field
from enum import Enum
import time
import threading
from urllib.parse import urljoin, quote
import re

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTabWidget, QGroupBox, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QSpinBox, QCheckBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QToolBar, QMenu, QMenuBar, QStatusBar, QMessageBox,
    QFrame, QScrollArea, QSlider, QLCDNumber,
    QGridLayout, QFormLayout, QButtonGroup, QRadioButton,
    QDialog, QDialogButtonBox, QFileDialog, QInputDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QThread, pyqtSignal
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon, QTextCursor, QPalette


class ResourceType(Enum):
    """Types of external resources."""
    WIKI = "wiki"
    ITEM_DATABASE = "item_database"
    NPC_DATABASE = "npc_database"
    QUEST_TEMPLATES = "quest_templates"
    MAP_DATA = "map_data"
    LOCALE_DATA = "locale_data"
    SCRIPT_LIBRARY = "script_library"
    REFERENCE_IMAGES = "reference_images"
    EXTERNAL_API = "external_api"


class ConnectionStatus(Enum):
    """Connection status for external resources."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    SYNCING = "syncing"


@dataclass
class ResourceEndpoint:
    """Configuration for an external resource endpoint."""
    name: str
    url: str
    resource_type: ResourceType
    api_key: Optional[str] = None
    auth_required: bool = False
    last_sync: Optional[float] = None
    cache_duration: int = 3600  # seconds
    is_enabled: bool = True


@dataclass
class ResourceItem:
    """Represents an item from an external resource."""
    item_id: str
    name: str
    description: str
    resource_type: ResourceType
    data: Dict[str, Any] = field(default_factory=dict)
    source_url: Optional[str] = None
    last_updated: Optional[float] = None
    is_cached: bool = False


class ResourceDownloader(QObject):
    """Background downloader for external resources."""

    download_progress = Signal(str, int, int)  # resource_name, current, total
    download_completed = Signal(str, List[ResourceItem])  # resource_name, items
    download_error = Signal(str, str)  # resource_name, error_message

    def __init__(self):
        super().__init__()
        self.active_downloads = {}
        self.cache_dir = Path(__file__).parent.parent.parent / "data" / "external_cache"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def download_resource(self, endpoint: ResourceEndpoint) -> bool:
        """Download data from an external resource."""
        try:
            self.download_progress.emit(endpoint.name, 0, 100)

            if endpoint.resource_type == ResourceType.WIKI:
                items = self._download_wiki_data(endpoint)
            elif endpoint.resource_type == ResourceType.ITEM_DATABASE:
                items = self._download_item_data(endpoint)
            elif endpoint.resource_type == ResourceType.NPC_DATABASE:
                items = self._download_npc_data(endpoint)
            elif endpoint.resource_type == ResourceType.QUEST_TEMPLATES:
                items = self._download_quest_templates(endpoint)
            elif endpoint.resource_type == ResourceType.MAP_DATA:
                items = self._download_map_data(endpoint)
            else:
                raise ValueError(f"Unsupported resource type: {endpoint.resource_type}")

            # Cache the results
            self._cache_results(endpoint.name, items)

            self.download_progress.emit(endpoint.name, 100, 100)
            self.download_completed.emit(endpoint.name, items)
            return True

        except Exception as e:
            self.download_error.emit(endpoint.name, str(e))
            return False

    def _download_wiki_data(self, endpoint: ResourceEndpoint) -> List[ResourceItem]:
        """Download data from a wiki API."""
        # This would implement actual wiki API calls
        # For now, return sample data
        return [
            ResourceItem(
                item_id="spellforce_quest_basics",
                name="Quest Creation Basics",
                description="Basic guide for creating quests in SpellForce",
                resource_type=ResourceType.WIKI,
                source_url=urljoin(endpoint.url, "Quest_Creation_Basics"),
                data={"category": "Tutorial", "difficulty": "Beginner"}
            ),
            ResourceItem(
                item_id="dialogue_writing",
                name="Dialogue Writing Guide",
                description="Best practices for writing engaging dialogue",
                resource_type=ResourceType.WIKI,
                source_url=urljoin(endpoint.url, "Dialogue_Writing"),
                data={"category": "Writing", "difficulty": "Intermediate"}
            )
        ]

    def _download_item_data(self, endpoint: ResourceEndpoint) -> List[ResourceItem]:
        """Download item database information."""
        return [
            ResourceItem(
                item_id="sword_of_flames",
                name="Sword of Flames",
                description="A legendary sword imbued with fire magic",
                resource_type=ResourceType.ITEM_DATABASE,
                data={
                    "type": "weapon",
                    "damage": 150,
                    "level_required": 25,
                    "rarity": "legendary",
                    "properties": ["fire_damage", "intelligence_boost"]
                }
            ),
            ResourceItem(
                item_id="health_potion",
                name="Health Potion",
                description="Restores 500 health points",
                resource_type=ResourceType.ITEM_DATABASE,
                data={
                    "type": "consumable",
                    "healing": 500,
                    "stack_size": 20,
                    "rarity": "common"
                }
            )
        ]

    def _download_npc_data(self, endpoint: ResourceEndpoint) -> List[ResourceItem]:
        """Download NPC database information."""
        return [
            ResourceItem(
                item_id="guard_captain",
                name="Guard Captain",
                description="Leader of the town guard",
                resource_type=ResourceType.NPC_DATABASE,
                data={
                    "level": 20,
                    "faction": "player_friendly",
                    "dialogue_topics": ["quest", "town_info", "enemies"],
                    "location": "liannon_town_center"
                }
            ),
            ResourceItem(
                item_id="merchant_mage",
                name="Merchant Mage",
                description="Sells magical items and artifacts",
                resource_type=ResourceType.NPC_DATABASE,
                data={
                    "level": 30,
                    "faction": "neutral",
                    "dialogue_topics": ["items_for_sale", "magic", "rumors"],
                    "location": "market_square"
                }
            )
        ]

    def _download_quest_templates(self, endpoint: ResourceEndpoint) -> List[ResourceItem]:
        """Download quest templates."""
        return [
            ResourceItem(
                item_id="fetch_quest_template",
                name="Fetch Quest Template",
                description="Template for creating fetch quests",
                resource_type=ResourceType.QUEST_TEMPLATES,
                data={
                    "template_type": "fetch",
                    "objectives": ["Collect specified items"],
                    "rewards": ["Experience", "Items"],
                    "difficulty_range": [1, 10]
                }
            ),
            ResourceItem(
                item_id="escort_quest_template",
                name="Escort Quest Template",
                description="Template for creating escort quests",
                resource_type=ResourceType.QUEST_TEMPLATES,
                data={
                    "template_type": "escort",
                    "objectives": ["Protect NPC while traveling"],
                    "rewards": ["Experience", "Reputation"],
                    "difficulty_range": [5, 15]
                }
            )
        ]

    def _download_map_data(self, endpoint: ResourceEndpoint) -> List[ResourceItem]:
        """Download map and location data."""
        return [
            ResourceItem(
                item_id="liannon",
                name="Liannon",
                description="Main starting area and town",
                resource_type=ResourceType.MAP_DATA,
                data={
                    "map_code": "P1",
                    "size": "large",
                    "terrain": "grassland",
                    "landmarks": ["town_center", "market", "guild_hall"],
                    "connections": ["dark_forest", "river_crossing"]
                }
            ),
            ResourceItem(
                item_id="dark_forest",
                name="Dark Forest",
                description="Dense forest with dangerous creatures",
                resource_type=ResourceType.MAP_DATA,
                data={
                    "map_code": "P2",
                    "size": "medium",
                    "terrain": "forest",
                    "landmarks": ["ancient_ruins", "hidden_cave"],
                    "connections": ["liannon", "mountain_pass"]
                }
            )
        ]

    def _cache_results(self, resource_name: str, items: List[ResourceItem]):
        """Cache downloaded results."""
        cache_file = self.cache_dir / f"{resource_name.lower().replace(' ', '_')}.json"

        cache_data = {
            "timestamp": time.time(),
            "items": [
                {
                    "item_id": item.item_id,
                    "name": item.name,
                    "description": item.description,
                    "resource_type": item.resource_type.value,
                    "data": item.data,
                    "source_url": item.source_url
                }
                for item in items
            ]
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def load_from_cache(self, resource_name: str) -> Optional[List[ResourceItem]]:
        """Load items from cache if available and not expired."""
        cache_file = self.cache_dir / f"{resource_name.lower().replace(' ', '_')}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)

            # Check if cache is still valid (24 hours)
            if time.time() - cache_data["timestamp"] > 86400:
                return None

            items = []
            for item_data in cache_data["items"]:
                item = ResourceItem(
                    item_id=item_data["item_id"],
                    name=item_data["name"],
                    description=item_data["description"],
                    resource_type=ResourceType(item_data["resource_type"]),
                    data=item_data["data"],
                    source_url=item_data.get("source_url"),
                    last_updated=cache_data["timestamp"],
                    is_cached=True
                )
                items.append(item)

            return items

        except Exception:
            return None


class ExternalResourcesWidget(QWidget):
    """Main widget for external resource integration."""

    def __init__(self):
        super().__init__()
        self.downloader = ResourceDownloader()
        self.endpoints: Dict[str, ResourceEndpoint] = {}
        self.resource_items: Dict[str, List[ResourceItem]] = {}
        self.setup_ui()
        self.setup_connections()
        self.load_default_endpoints()

    def setup_ui(self):
        """Setup the main UI layout."""
        layout = QVBoxLayout()

        # Create toolbar
        toolbar = self._create_toolbar()
        layout.addWidget(toolbar)

        # Create main content area with tabs
        self.main_tabs = QTabWidget()

        # Resource Browser tab
        self.browser_tab = self._create_browser_tab()
        self.main_tabs.addTab(self.browser_tab, "Resource Browser")

        # Search tab
        self.search_tab = self._create_search_tab()
        self.main_tabs.addTab(self.search_tab, "Search")

        # Import/Export tab
        self.import_export_tab = self._create_import_export_tab()
        self.main_tabs.addTab(self.import_export_tab, "Import/Export")

        # Settings tab
        self.settings_tab = self._create_settings_tab()
        self.main_tabs.addTab(self.settings_tab, "Settings")

        layout.addWidget(self.main_tabs)

        # Status bar
        self.status_bar = QStatusBar()
        self.status_label = QLabel("Ready")
        self.status_bar.addWidget(self.status_label)
        layout.addWidget(self.status_bar)

        self.setLayout(layout)

    def _create_toolbar(self) -> QToolBar:
        """Create the main toolbar."""
        toolbar = QToolBar("External Resources")
        toolbar.setIconSize(Qt.QSize(16, 16))

        # Sync actions
        toolbar.addAction("Sync All", self.sync_all_resources)
        toolbar.addAction("Sync Selected", self.sync_selected_resource)
        toolbar.addSeparator()

        # Import actions
        toolbar.addAction("Import File", self.import_file)
        toolbar.addAction("Export Selection", self.export_selection)
        toolbar.addSeparator()

        # Refresh actions
        toolbar.addAction("Refresh View", self.refresh_current_view)
        toolbar.addAction("Clear Cache", self.clear_cache)

        return toolbar

    def _create_browser_tab(self) -> QWidget:
        """Create the resource browser tab."""
        tab = QWidget()
        layout = QHBoxLayout()

        # Left panel - Resource categories
        left_panel = QVBoxLayout()

        # Resource tree
        resources_group = QGroupBox("Available Resources")
        resources_layout = QVBoxLayout()

        self.resource_tree = QTreeWidget()
        self.resource_tree.setHeaderLabels(["Resource", "Status", "Items"])
        self.resource_tree.setColumnWidth(0, 200)
        self.resource_tree.setColumnWidth(1, 100)
        self.resource_tree.setColumnWidth(2, 60)

        resources_layout.addWidget(self.resource_tree)

        # Resource actions
        actions_layout = QHBoxLayout()

        self.sync_resource_btn = QPushButton("Sync")
        self.sync_resource_btn.clicked.connect(self.sync_selected_resource)

        self.view_details_btn = QPushButton("Details")
        self.view_details_btn.clicked.connect(self.view_resource_details)

        self.add_to_project_btn = QPushButton("Add to Project")
        self.add_to_project_btn.clicked.connect(self.add_to_project)

        actions_layout.addWidget(self.sync_resource_btn)
        actions_layout.addWidget(self.view_details_btn)
        actions_layout.addWidget(self.add_to_project_btn)

        resources_layout.addLayout(actions_layout)
        resources_group.setLayout(resources_layout)
        left_panel.addWidget(resources_group)

        left_panel.addStretch()

        # Right panel - Item browser
        right_panel = QVBoxLayout()

        # Item details
        item_details_group = QGroupBox("Item Details")
        item_details_layout = QVBoxLayout()

        self.item_title_label = QLabel("Select an item to view details")
        self.item_title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        item_details_layout.addWidget(self.item_title_label)

        self.item_description = QTextEdit()
        self.item_description.setReadOnly(True)
        self.item_description.setMaximumHeight(100)
        item_details_layout.addWidget(self.item_description)

        # Item metadata
        metadata_layout = QFormLayout()
        self.item_type_label = QLabel("-")
        self.item_source_label = QLabel("-")
        self.item_updated_label = QLabel("-")

        metadata_layout.addRow("Type:", self.item_type_label)
        metadata_layout.addRow("Source:", self.item_source_label)
        metadata_layout.addRow("Last Updated:", self.item_updated_label)

        item_details_layout.addLayout(metadata_layout)
        item_details_group.setLayout(item_details_layout)
        right_panel.addWidget(item_details_group)

        # Item preview/editor
        preview_group = QGroupBox("Item Preview")
        preview_layout = QVBoxLayout()

        self.item_preview = QTextEdit()
        self.item_preview.setReadOnly(True)
        preview_layout.addWidget(self.item_preview)

        preview_group.setLayout(preview_layout)
        right_panel.addWidget(preview_group)

        right_panel.addStretch()

        # Add panels to layout
        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        right_widget = QWidget()
        right_widget.setLayout(right_panel)

        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 500])

        layout.addWidget(splitter)
        tab.setLayout(layout)

        return tab

    def _create_search_tab(self) -> QWidget:
        """Create the search tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Search controls
        search_group = QGroupBox("Search Resources")
        search_layout = QGridLayout()

        search_layout.addWidget(QLabel("Search Term:"), 0, 0)
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter search terms...")
        search_layout.addWidget(self.search_edit, 0, 1, 1, 2)

        search_layout.addWidget(QLabel("Resource Type:"), 1, 0)
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["All Types", "Wiki", "Items", "NPCs", "Quest Templates", "Maps"])
        search_layout.addWidget(self.search_type_combo, 1, 1)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self.perform_search)
        search_layout.addWidget(self.search_btn, 1, 2)

        search_layout.addWidget(QLabel("Filters:"), 2, 0)
        filters_layout = QHBoxLayout()

        self.only_cached_check = QCheckBox("Only Cached")
        self.recent_first_check = QCheckBox("Recent First")
        self.include_descriptions_check = QCheckBox("Include Descriptions")

        filters_layout.addWidget(self.only_cached_check)
        filters_layout.addWidget(self.recent_first_check)
        filters_layout.addWidget(self.include_descriptions_check)

        search_layout.addLayout(filters_layout, 2, 1, 1, 2)

        search_group.setLayout(search_layout)
        layout.addWidget(search_group)

        # Search results
        results_group = QGroupBox("Search Results")
        results_layout = QVBoxLayout()

        self.search_results_table = QTableWidget()
        self.search_results_table.setColumnCount(6)
        self.search_results_table.setHorizontalHeaderLabels([
            "Name", "Type", "Description", "Source", "Updated", "Actions"
        ])
        self.search_results_table.setAlternatingRowColors(True)
        self.search_results_table.setSelectionBehavior(QTableWidget.SelectRows)

        # Set column widths
        self.search_results_table.setColumnWidth(0, 200)
        self.search_results_table.setColumnWidth(1, 100)
        self.search_results_table.setColumnWidth(2, 300)
        self.search_results_table.setColumnWidth(3, 150)
        self.search_results_table.setColumnWidth(4, 120)
        self.search_results_table.setColumnWidth(5, 100)

        results_layout.addWidget(self.search_results_table)
        results_group.setLayout(results_layout)
        layout.addWidget(results_group)

        tab.setLayout(layout)
        return tab

    def _create_import_export_tab(self) -> QWidget:
        """Create the import/export tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Import section
        import_group = QGroupBox("Import Resources")
        import_layout = QGridLayout()

        # File import
        import_layout.addWidget(QLabel("Import from File:"), 0, 0)
        file_import_layout = QHBoxLayout()

        self.import_file_path = QLineEdit()
        self.import_file_path.setPlaceholderText("Select file to import...")
        file_import_layout.addWidget(self.import_file_path)

        self.browse_file_btn = QPushButton("Browse")
        self.browse_file_btn.clicked.connect(self.browse_import_file)
        file_import_layout.addWidget(self.browse_file_btn)

        self.import_file_btn = QPushButton("Import")
        self.import_file_btn.clicked.connect(self.import_from_file)
        file_import_layout.addWidget(self.import_file_btn)

        import_layout.addLayout(file_import_layout, 0, 1, 1, 2)

        # URL import
        import_layout.addWidget(QLabel("Import from URL:"), 1, 0)
        url_import_layout = QHBoxLayout()

        self.import_url = QLineEdit()
        self.import_url.setPlaceholderText("Enter URL...")
        url_import_layout.addWidget(self.import_url)

        self.import_url_btn = QPushButton("Import")
        self.import_url_btn.clicked.connect(self.import_from_url)
        url_import_layout.addWidget(self.import_url_btn)

        import_layout.addLayout(url_import_layout, 1, 1, 1, 2)

        # API import
        import_layout.addWidget(QLabel("API Import:"), 2, 0)
        api_import_layout = QHBoxLayout()

        self.api_endpoint = QLineEdit()
        self.api_endpoint.setPlaceholderText("API endpoint URL...")
        api_import_layout.addWidget(self.api_endpoint)

        self.api_key = QLineEdit()
        self.api_key.setPlaceholderText("API key (optional)...")
        self.api_key.setEchoMode(QLineEdit.Password)
        api_import_layout.addWidget(self.api_key)

        self.import_api_btn = QPushButton("Import from API")
        self.import_api_btn.clicked.connect(self.import_from_api)
        api_import_layout.addWidget(self.import_api_btn)

        import_layout.addLayout(api_import_layout, 2, 1, 1, 3)

        import_group.setLayout(import_layout)
        layout.addWidget(import_group)

        # Export section
        export_group = QGroupBox("Export Resources")
        export_layout = QGridLayout()

        # Export format
        export_layout.addWidget(QLabel("Export Format:"), 0, 0)
        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["JSON", "XML", "CSV", "YAML"])
        export_layout.addWidget(self.export_format_combo, 0, 1)

        # Export selection
        export_layout.addWidget(QLabel("Export Selection:"), 1, 0)
        selection_layout = QHBoxLayout()

        self.export_all_radio = QRadioButton("All Resources")
        self.export_selected_radio = QRadioButton("Selected Resources")
        self.export_filtered_radio = QRadioButton("Filtered Resources")

        self.export_all_radio.setChecked(True)

        button_group = QButtonGroup()
        button_group.addButton(self.export_all_radio)
        button_group.addButton(self.export_selected_radio)
        button_group.addButton(self.export_filtered_radio)

        selection_layout.addWidget(self.export_all_radio)
        selection_layout.addWidget(self.export_selected_radio)
        selection_layout.addWidget(self.export_filtered_radio)

        export_layout.addLayout(selection_layout, 1, 1, 1, 3)

        # Export actions
        export_actions_layout = QHBoxLayout()

        self.export_preview_btn = QPushButton("Preview Export")
        self.export_preview_btn.clicked.connect(self.preview_export)
        export_actions_layout.addWidget(self.export_preview_btn)

        self.export_file_btn = QPushButton("Export to File")
        self.export_file_btn.clicked.connect(self.export_to_file)
        export_actions_layout.addWidget(self.export_file_btn)

        self.export_clipboard_btn = QPushButton("Copy to Clipboard")
        self.export_clipboard_btn.clicked.connect(self.export_to_clipboard)
        export_actions_layout.addWidget(self.export_clipboard_btn)

        export_layout.addLayout(export_actions_layout, 2, 0, 1, 4)

        export_group.setLayout(export_layout)
        layout.addWidget(export_group)

        # Recent imports/exports
        history_group = QGroupBox("Recent Activity")
        history_layout = QVBoxLayout()

        self.activity_table = QTableWidget()
        self.activity_table.setColumnCount(4)
        self.activity_table.setHorizontalHeaderLabels(["Time", "Type", "Resource", "Status"])
        self.activity_table.setAlternatingRowColors(True)
        self.activity_table.setMaximumHeight(150)

        history_layout.addWidget(self.activity_table)
        history_group.setLayout(history_layout)
        layout.addWidget(history_group)

        tab.setLayout(layout)
        return tab

    def _create_settings_tab(self) -> QWidget:
        """Create the settings tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Connection settings
        connection_group = QGroupBox("Connection Settings")
        connection_layout = QFormLayout()

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(5, 300)
        self.timeout_spin.setValue(30)
        self.timeout_spin.setSuffix(" seconds")
        connection_layout.addRow("Request Timeout:", self.timeout_spin)

        self.retry_attempts_spin = QSpinBox()
        self.retry_attempts_spin.setRange(0, 10)
        self.retry_attempts_spin.setValue(3)
        connection_layout.addRow("Retry Attempts:", self.retry_attempts_spin)

        self.parallel_downloads_spin = QSpinBox()
        self.parallel_downloads_spin.setRange(1, 10)
        self.parallel_downloads_spin.setValue(3)
        connection_layout.addRow("Parallel Downloads:", self.parallel_downloads_spin)

        connection_group.setLayout(connection_layout)
        layout.addWidget(connection_group)

        # Cache settings
        cache_group = QGroupBox("Cache Settings")
        cache_layout = QFormLayout()

        self.cache_duration_spin = QSpinBox()
        self.cache_duration_spin.setRange(0, 168)  # 0 to 168 hours (1 week)
        self.cache_duration_spin.setValue(24)
        self.cache_duration_spin.setSuffix(" hours")
        cache_layout.addRow("Cache Duration:", self.cache_duration_spin)

        self.max_cache_size_spin = QSpinBox()
        self.max_cache_size_spin.setRange(10, 1000)
        self.max_cache_size_spin.setValue(100)
        self.max_cache_size_spin.setSuffix(" MB")
        cache_layout.addRow("Max Cache Size:", self.max_cache_size_spin)

        self.auto_clear_cache_check = QCheckBox("Auto-clear expired cache")
        self.auto_clear_cache_check.setChecked(True)
        cache_layout.addRow("Cache Maintenance:", self.auto_clear_cache_check)

        cache_group.setLayout(cache_layout)
        layout.addWidget(cache_group)

        # API endpoints management
        endpoints_group = QGroupBox("API Endpoints")
        endpoints_layout = QVBoxLayout()

        self.endpoints_table = QTableWidget()
        self.endpoints_table.setColumnCount(5)
        self.endpoints_table.setHorizontalHeaderLabels(["Name", "Type", "URL", "Status", "Actions"])
        self.endpoints_table.setAlternatingRowColors(True)

        endpoints_layout.addWidget(self.endpoints_table)

        # Endpoint actions
        endpoint_actions_layout = QHBoxLayout()

        self.add_endpoint_btn = QPushButton("Add Endpoint")
        self.add_endpoint_btn.clicked.connect(self.add_endpoint)
        endpoint_actions_layout.addWidget(self.add_endpoint_btn)

        self.edit_endpoint_btn = QPushButton("Edit")
        self.edit_endpoint_btn.clicked.connect(self.edit_endpoint)
        endpoint_actions_layout.addWidget(self.edit_endpoint_btn)

        self.remove_endpoint_btn = QPushButton("Remove")
        self.remove_endpoint_btn.clicked.connect(self.remove_endpoint)
        endpoint_actions_layout.addWidget(self.remove_endpoint_btn)

        endpoint_actions_layout.addStretch()

        endpoints_layout.addLayout(endpoint_actions_layout)
        endpoints_group.setLayout(endpoints_layout)
        layout.addWidget(endpoints_group)

        # Save settings button
        save_layout = QHBoxLayout()
        save_layout.addStretch()

        self.save_settings_btn = QPushButton("Save Settings")
        self.save_settings_btn.clicked.connect(self.save_settings)
        save_layout.addWidget(self.save_settings_btn)

        layout.addLayout(save_layout)
        tab.setLayout(layout)

        return tab

    def setup_connections(self):
        """Setup signal connections."""
        # Downloader connections
        self.downloader.download_progress.connect(self.on_download_progress)
        self.downloader.download_completed.connect(self.on_download_completed)
        self.downloader.download_error.connect(self.on_download_error)

        # Tree widget selection
        self.resource_tree.itemSelectionChanged.connect(self.on_resource_selection_changed)
        self.resource_tree.itemDoubleClicked.connect(self.on_resource_double_clicked)

        # Search
        self.search_edit.returnPressed.connect(self.perform_search)

        # Search results selection
        self.search_results_table.itemSelectionChanged.connect(self.on_search_result_selection_changed)

    def load_default_endpoints(self):
        """Load default resource endpoints."""
        default_endpoints = [
            ResourceEndpoint(
                name="SpellForce Wiki",
                url="https://spellforce.fandom.com/api.php",
                resource_type=ResourceType.WIKI,
                is_enabled=True
            ),
            ResourceEndpoint(
                name="Item Database",
                url="https://api.spellforce-items.com/v1",
                resource_type=ResourceType.ITEM_DATABASE,
                is_enabled=True
            ),
            ResourceEndpoint(
                name="NPC Database",
                url="https://api.spellforce-npcs.com/v1",
                resource_type=ResourceType.NPC_DATABASE,
                is_enabled=True
            ),
            ResourceEndpoint(
                name="Quest Templates",
                url="https://api.spellforce-templates.com/v1",
                resource_type=ResourceType.QUEST_TEMPLATES,
                is_enabled=True
            )
        ]

        for endpoint in default_endpoints:
            self.endpoints[endpoint.name] = endpoint

        self.update_resource_tree()
        self.update_endpoints_table()

    def update_resource_tree(self):
        """Update the resource tree widget."""
        self.resource_tree.clear()

        for name, endpoint in self.endpoints.items():
            # Create category item
            category_item = QTreeWidgetItem(self.resource_tree)
            category_item.setText(0, name)
            category_item.setText(1, "Ready" if endpoint.is_enabled else "Disabled")
            category_item.setData(0, Qt.UserRole, endpoint)

            # Load cached items or show loading status
            cached_items = self.downloader.load_from_cache(name)
            if cached_items:
                category_item.setText(2, f"{len(cached_items)}")

                # Add items to tree
                for item in cached_items:
                    item_widget = QTreeWidgetItem(category_item)
                    item_widget.setText(0, item.name)
                    item_widget.setText(1, "Cached" if item.is_cached else "Live")
                    item_widget.setText(2, "")
                    item_widget.setData(0, Qt.UserRole, item)
            else:
                category_item.setText(2, "0")

        self.resource_tree.expandAll()

    def update_endpoints_table(self):
        """Update the endpoints table in settings."""
        self.endpoints_table.setRowCount(len(self.endpoints))

        for row, (name, endpoint) in enumerate(self.endpoints.items()):
            self.endpoints_table.setItem(row, 0, QTableWidgetItem(name))
            self.endpoints_table.setItem(row, 1, QTableWidgetItem(endpoint.resource_type.value))
            self.endpoints_table.setItem(row, 2, QTableWidgetItem(endpoint.url))
            self.endpoints_table.setItem(row, 3, QTableWidgetItem("Enabled" if endpoint.is_enabled else "Disabled"))

            # Add edit button
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, ep=endpoint: self.edit_endpoint_dialog(ep))
            self.endpoints_table.setCellWidget(row, 4, edit_btn)

    def sync_all_resources(self):
        """Synchronize all enabled resources."""
        for name, endpoint in self.endpoints.items():
            if endpoint.is_enabled:
                self.sync_resource(name)

    def sync_selected_resource(self):
        """Synchronize the selected resource."""
        current_item = self.resource_tree.currentItem()
        if current_item:
            endpoint = current_item.data(0, Qt.UserRole)
            if isinstance(endpoint, ResourceEndpoint):
                self.sync_resource(endpoint.name)

    def sync_resource(self, resource_name: str):
        """Synchronize a specific resource."""
        if resource_name not in self.endpoints:
            self.status_label.setText(f"Unknown resource: {resource_name}")
            return

        endpoint = self.endpoints[resource_name]

        # Update status
        self.status_label.setText(f"Syncing {resource_name}...")

        # Start download in background thread
        thread = threading.Thread(target=self.downloader.download_resource, args=(endpoint,))
        thread.daemon = True
        thread.start()

    def view_resource_details(self):
        """View details of selected resource."""
        current_item = self.resource_tree.currentItem()
        if current_item:
            item = current_item.data(0, Qt.UserRole)
            if isinstance(item, ResourceItem):
                self.show_item_details(item)

    def show_item_details(self, item: ResourceItem):
        """Show details for a resource item."""
        self.item_title_label.setText(item.name)
        self.item_description.setPlainText(item.description)
        self.item_type_label.setText(item.resource_type.value)
        self.item_source_label.setText(item.source_url or "Unknown")
        self.item_updated_label.setText(
            time.strftime("%Y-%m-%d %H:%M", time.localtime(item.last_updated))
            if item.last_updated else "Unknown"
        )

        # Show item data as formatted JSON
        item_json = json.dumps(item.data, indent=2, ensure_ascii=False)
        self.item_preview.setPlainText(item_json)

    def add_to_project(self):
        """Add selected resource item to the current project."""
        current_item = self.resource_tree.currentItem()
        if current_item:
            item = current_item.data(0, Qt.UserRole)
            if isinstance(item, ResourceItem):
                # This would integrate with the quest editor to add the item
                QMessageBox.information(
                    self,
                    "Added to Project",
                    f"Added '{item.name}' to the current project."
                )

    def perform_search(self):
        """Perform a search across all resources."""
        search_term = self.search_edit.text().strip()
        if not search_term:
            return

        resource_type = self.search_type_combo.currentText()
        self.status_label.setText(f"Searching for '{search_term}'...")

        # Collect all items from resources
        all_items = []
        for resource_name, items in self.resource_items.items():
            all_items.extend(items)

        # Also load cached items
        for endpoint_name in self.endpoints.keys():
            cached_items = self.downloader.load_from_cache(endpoint_name)
            if cached_items:
                all_items.extend(cached_items)

        # Filter items based on search criteria
        filtered_items = self.filter_items(all_items, search_term, resource_type)

        # Update search results table
        self.update_search_results(filtered_items)

        self.status_label.setText(f"Found {len(filtered_items)} results")

    def filter_items(self, items: List[ResourceItem], search_term: str, resource_type: str) -> List[ResourceItem]:
        """Filter items based on search criteria."""
        filtered = []

        for item in items:
            # Filter by resource type
            if resource_type != "All Types":
                type_mapping = {
                    "Wiki": ResourceType.WIKI,
                    "Items": ResourceType.ITEM_DATABASE,
                    "NPCs": ResourceType.NPC_DATABASE,
                    "Quest Templates": ResourceType.QUEST_TEMPLATES,
                    "Maps": ResourceType.MAP_DATA
                }
                if resource_type in type_mapping and item.resource_type != type_mapping[resource_type]:
                    continue

            # Filter by search term
            search_lower = search_term.lower()
            if (search_lower in item.name.lower() or
                (self.include_descriptions_check.isChecked() and search_lower in item.description.lower())):
                filtered.append(item)

        # Sort by recently updated if requested
        if self.recent_first_check.isChecked():
            filtered.sort(key=lambda x: x.last_updated or 0, reverse=True)

        return filtered

    def update_search_results(self, items: List[ResourceItem]):
        """Update the search results table."""
        self.search_results_table.setRowCount(len(items))

        for row, item in enumerate(items):
            self.search_results_table.setItem(row, 0, QTableWidgetItem(item.name))
            self.search_results_table.setItem(row, 1, QTableWidgetItem(item.resource_type.value))
            self.search_results_table.setItem(row, 2, QTableWidgetItem(item.description[:100] + "..." if len(item.description) > 100 else item.description))
            self.search_results_table.setItem(row, 3, QTableWidgetItem(item.source_url or "Unknown"))
            self.search_results_table.setItem(row, 4, QTableWidgetItem(
                time.strftime("%Y-%m-%d", time.localtime(item.last_updated)) if item.last_updated else "Unknown"
            ))

            # Add action button
            action_btn = QPushButton("Add")
            action_btn.clicked.connect(lambda checked, i=item: self.add_to_project())
            self.search_results_table.setCellWidget(row, 5, action_btn)

    def on_search_result_selection_changed(self):
        """Handle search result selection change."""
        current_row = self.search_results_table.currentRow()
        if current_row >= 0:
            # Find the corresponding item and show details
            # This would need mapping from table rows to items
            pass

    def browse_import_file(self):
        """Browse for import file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Import File",
            "",
            "JSON Files (*.json);;XML Files (*.xml);;CSV Files (*.csv);;All Files (*)"
        )

        if file_path:
            self.import_file_path.setText(file_path)

    def import_from_file(self):
        """Import resources from a file."""
        file_path = self.import_file_path.text()
        if not file_path or not Path(file_path).exists():
            QMessageBox.warning(self, "Import Error", "Please select a valid file.")
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.endswith('.json'):
                    data = json.load(f)
                elif file_path.endswith('.xml'):
                    tree = ET.parse(f)
                    data = self.xml_to_dict(tree.getroot())
                else:
                    # Assume CSV or other format
                    data = self.parse_import_file(file_path)

            # Process imported data
            self.process_imported_data(data)

            # Add to activity log
            self.add_activity_log("Import", file_path, "Success")

            QMessageBox.information(self, "Import Complete", f"Successfully imported data from {file_path}")

        except Exception as e:
            self.add_activity_log("Import", file_path, f"Error: {str(e)}")
            QMessageBox.critical(self, "Import Error", f"Failed to import file: {str(e)}")

    def import_from_url(self):
        """Import resources from a URL."""
        url = self.import_url.text().strip()
        if not url:
            QMessageBox.warning(self, "Import Error", "Please enter a valid URL.")
            return

        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Process response based on content type
            content_type = response.headers.get('content-type', '').lower()
            if 'json' in content_type:
                data = response.json()
            elif 'xml' in content_type:
                root = ET.fromstring(response.text)
                data = self.xml_to_dict(root)
            else:
                # Assume text/CSV
                data = {"content": response.text}

            self.process_imported_data(data)
            self.add_activity_log("Import", url, "Success")

            QMessageBox.information(self, "Import Complete", f"Successfully imported data from {url}")

        except Exception as e:
            self.add_activity_log("Import", url, f"Error: {str(e)}")
            QMessageBox.critical(self, "Import Error", f"Failed to import from URL: {str(e)}")

    def import_from_api(self):
        """Import resources from an API endpoint."""
        url = self.api_endpoint.text().strip()
        if not url:
            QMessageBox.warning(self, "Import Error", "Please enter a valid API endpoint.")
            return

        try:
            headers = {}
            api_key = self.api_key.text().strip()
            if api_key:
                headers['Authorization'] = f'Bearer {api_key}'

            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()

            data = response.json()
            self.process_imported_data(data)
            self.add_activity_log("API Import", url, "Success")

            QMessageBox.information(self, "Import Complete", f"Successfully imported from API: {url}")

        except Exception as e:
            self.add_activity_log("API Import", url, f"Error: {str(e)}")
            QMessageBox.critical(self, "Import Error", f"Failed to import from API: {str(e)}")

    def process_imported_data(self, data: Dict[str, Any]):
        """Process imported data and convert to resource items."""
        # This would implement specific logic for different data formats
        # For now, just store the data
        pass

    def xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}

        # Add element attributes
        if element.attrib:
            result['@attributes'] = element.attrib

        # Add element text
        if element.text and element.text.strip():
            if len(element) == 0:
                return element.text.strip()
            result['#text'] = element.text.strip()

        # Process child elements
        for child in element:
            child_data = self.xml_to_dict(child)

            if child.tag in result:
                if not isinstance(result[child.tag], list):
                    result[child.tag] = [result[child.tag]]
                result[child.tag].append(child_data)
            else:
                result[child.tag] = child_data

        return result

    def parse_import_file(self, file_path: str) -> Dict[str, Any]:
        """Parse various import file formats."""
        # This would implement parsing for different formats
        return {"data": "Imported from file"}

    def export_to_file(self):
        """Export selected resources to a file."""
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self,
            "Export Resources",
            "",
            "JSON Files (*.json);;XML Files (*.xml);;CSV Files (*.csv);;All Files (*)"
        )

        if not file_path:
            return

        try:
            # Determine export format
            if selected_filter.endswith('.json'):
                format_type = 'json'
            elif selected_filter.endswith('.xml'):
                format_type = 'xml'
            elif selected_filter.endswith('.csv'):
                format_type = 'csv'
            else:
                # Determine from file extension
                if file_path.endswith('.json'):
                    format_type = 'json'
                elif file_path.endswith('.xml'):
                    format_type = 'xml'
                elif file_path.endswith('.csv'):
                    format_type = 'csv'
                else:
                    format_type = 'json'
                    file_path += '.json'

            # Get data to export
            export_data = self.get_export_data()

            # Write to file
            with open(file_path, 'w', encoding='utf-8') as f:
                if format_type == 'json':
                    json.dump(export_data, f, indent=2, ensure_ascii=False)
                elif format_type == 'xml':
                    f.write(self.dict_to_xml(export_data))
                elif format_type == 'csv':
                    f.write(self.dict_to_csv(export_data))

            self.add_activity_log("Export", file_path, "Success")
            QMessageBox.information(self, "Export Complete", f"Successfully exported to {file_path}")

        except Exception as e:
            self.add_activity_log("Export", file_path, f"Error: {str(e)}")
            QMessageBox.critical(self, "Export Error", f"Failed to export: {str(e)}")

    def get_export_data(self) -> Dict[str, Any]:
        """Get data for export based on current selection."""
        if self.export_all_radio.isChecked():
            # Export all resources
            return {
                "resources": [
                    {
                        "name": name,
                        "items": [self.item_to_dict(item) for item in items]
                    }
                    for name, items in self.resource_items.items()
                ]
            }
        elif self.export_selected_radio.isChecked():
            # Export selected items
            selected_items = self.get_selected_items()
            return {
                "resources": [
                    self.item_to_dict(item) for item in selected_items
                ]
            }
        else:
            # Export filtered items
            filtered_items = self.get_filtered_items()
            return {
                "resources": [
                    self.item_to_dict(item) for item in filtered_items
                ]
            }

    def item_to_dict(self, item: ResourceItem) -> Dict[str, Any]:
        """Convert ResourceItem to dictionary."""
        return {
            "item_id": item.item_id,
            "name": item.name,
            "description": item.description,
            "resource_type": item.resource_type.value,
            "data": item.data,
            "source_url": item.source_url,
            "last_updated": item.last_updated
        }

    def dict_to_xml(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to XML string."""
        # This would implement proper XML conversion
        return "<xml>Export data would be here</xml>"

    def dict_to_csv(self, data: Dict[str, Any]) -> str:
        """Convert dictionary to CSV string."""
        # This would implement proper CSV conversion
        return "CSV export data would be here"

    def export_to_clipboard(self):
        """Export selected resources to clipboard."""
        try:
            export_data = self.get_export_data()
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

            # Copy to clipboard
            from PySide6.QtWidgets import QApplication
            QApplication.clipboard().setText(json_str)

            QMessageBox.information(self, "Export Complete", "Data copied to clipboard")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to copy to clipboard: {str(e)}")

    def preview_export(self):
        """Preview export data."""
        try:
            export_data = self.get_export_data()
            json_str = json.dumps(export_data, indent=2, ensure_ascii=False)

            # Show preview dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Export Preview")
            dialog.resize(800, 600)

            layout = QVBoxLayout()

            text_edit = QTextEdit()
            text_edit.setPlainText(json_str)
            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)

            buttons = QDialogButtonBox(QDialogButtonBox.Close)
            buttons.rejected.connect(dialog.close)
            layout.addWidget(buttons)

            dialog.setLayout(layout)
            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to preview export: {str(e)}")

    def get_selected_items(self) -> List[ResourceItem]:
        """Get currently selected items."""
        # This would implement selection logic
        return []

    def get_filtered_items(self) -> List[ResourceItem]:
        """Get currently filtered items."""
        # This would implement filtering logic
        return []

    def add_activity_log(self, activity_type: str, resource: str, status: str):
        """Add an entry to the activity log."""
        timestamp = time.strftime("%H:%M:%S")

        row = self.activity_table.rowCount()
        self.activity_table.insertRow(row)

        self.activity_table.setItem(row, 0, QTableWidgetItem(timestamp))
        self.activity_table.setItem(row, 1, QTableWidgetItem(activity_type))
        self.activity_table.setItem(row, 2, QTableWidgetItem(resource))
        self.activity_table.setItem(row, 3, QTableWidgetItem(status))

        # Color code status
        status_item = self.activity_table.item(row, 3)
        if "Error" in status:
            status_item.setBackground(QColor(255, 200, 200))  # Light red
        elif "Success" in status:
            status_item.setBackground(QColor(200, 255, 200))  # Light green

        # Auto-scroll to latest entry
        self.activity_table.scrollToBottom()

        # Limit to recent entries
        if self.activity_table.rowCount() > 50:
            self.activity_table.removeRow(0)

    def clear_cache(self):
        """Clear the resource cache."""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "This will remove all cached resource data. Continue?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # Clear cache directory
            import shutil
            if self.downloader.cache_dir.exists():
                shutil.rmtree(self.downloader.cache_dir)
                self.downloader.cache_dir.mkdir(parents=True, exist_ok=True)

            # Clear in-memory cache
            self.resource_items.clear()

            # Update displays
            self.update_resource_tree()

            self.status_label.setText("Cache cleared")

    def refresh_current_view(self):
        """Refresh the currently active view."""
        current_tab = self.main_tabs.currentIndex()

        if current_tab == 0:  # Resource browser
            self.update_resource_tree()
        elif current_tab == 1:  # Search
            if self.search_edit.text().strip():
                self.perform_search()

        self.status_label.setText("View refreshed")

    def add_endpoint(self):
        """Add a new API endpoint."""
        dialog = EndpointDialog(self)
        if dialog.exec() == QDialog.Accepted:
            endpoint = dialog.get_endpoint()
            self.endpoints[endpoint.name] = endpoint
            self.update_endpoints_table()
            self.update_resource_tree()

    def edit_endpoint(self):
        """Edit the selected endpoint."""
        current_row = self.endpoints_table.currentRow()
        if current_row >= 0:
            endpoint_name = self.endpoints_table.item(current_row, 0).text()
            if endpoint_name in self.endpoints:
                endpoint = self.endpoints[endpoint_name]
                dialog = EndpointDialog(self, endpoint)
                if dialog.exec() == QDialog.Accepted:
                    updated_endpoint = dialog.get_endpoint()
                    self.endpoints[endpoint_name] = updated_endpoint
                    self.update_endpoints_table()
                    self.update_resource_tree()

    def edit_endpoint_dialog(self, endpoint: ResourceEndpoint):
        """Edit endpoint dialog from table button."""
        dialog = EndpointDialog(self, endpoint)
        if dialog.exec() == QDialog.Accepted:
            updated_endpoint = dialog.get_endpoint()
            self.endpoints[endpoint.name] = updated_endpoint
            self.update_endpoints_table()
            self.update_resource_tree()

    def remove_endpoint(self):
        """Remove the selected endpoint."""
        current_row = self.endpoints_table.currentRow()
        if current_row >= 0:
            endpoint_name = self.endpoints_table.item(current_row, 0).text()

            reply = QMessageBox.question(
                self,
                "Remove Endpoint",
                f"Remove endpoint '{endpoint_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                del self.endpoints[endpoint_name]
                self.update_endpoints_table()
                self.update_resource_tree()

    def save_settings(self):
        """Save the current settings."""
        settings = {
            "timeout": self.timeout_spin.value(),
            "retry_attempts": self.retry_attempts_spin.value(),
            "parallel_downloads": self.parallel_downloads_spin.value(),
            "cache_duration": self.cache_duration_spin.value(),
            "max_cache_size": self.max_cache_size_spin.value(),
            "auto_clear_cache": self.auto_clear_cache_check.isChecked(),
            "endpoints": [
                {
                    "name": endpoint.name,
                    "url": endpoint.url,
                    "resource_type": endpoint.resource_type.value,
                    "is_enabled": endpoint.is_enabled
                }
                for endpoint in self.endpoints.values()
            ]
        }

        # Save to file
        settings_file = Path(__file__).parent.parent.parent / "data" / "external_resources_settings.json"
        settings_file.parent.mkdir(parents=True, exist_ok=True)

        with open(settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)

        QMessageBox.information(self, "Settings Saved", "External resources settings have been saved.")

    def load_settings(self):
        """Load settings from file."""
        settings_file = Path(__file__).parent.parent.parent / "data" / "external_resources_settings.json"

        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                # Apply settings
                self.timeout_spin.setValue(settings.get("timeout", 30))
                self.retry_attempts_spin.setValue(settings.get("retry_attempts", 3))
                self.parallel_downloads_spin.setValue(settings.get("parallel_downloads", 3))
                self.cache_duration_spin.setValue(settings.get("cache_duration", 24))
                self.max_cache_size_spin.setValue(settings.get("max_cache_size", 100))
                self.auto_clear_cache_check.setChecked(settings.get("auto_clear_cache", True))

                # Load endpoints
                for endpoint_data in settings.get("endpoints", []):
                    endpoint = ResourceEndpoint(
                        name=endpoint_data["name"],
                        url=endpoint_data["url"],
                        resource_type=ResourceType(endpoint_data["resource_type"]),
                        is_enabled=endpoint_data.get("is_enabled", True)
                    )
                    self.endpoints[endpoint.name] = endpoint

                self.update_endpoints_table()
                self.update_resource_tree()

            except Exception as e:
                QMessageBox.warning(self, "Settings Error", f"Failed to load settings: {str(e)}")

    # Signal handlers
    def on_download_progress(self, resource_name: str, current: int, total: int):
        """Handle download progress updates."""
        self.status_label.setText(f"Downloading {resource_name}: {current}/{total}")

    def on_download_completed(self, resource_name: str, items: List[ResourceItem]):
        """Handle download completion."""
        self.resource_items[resource_name] = items
        self.update_resource_tree()
        self.status_label.setText(f"Completed syncing {resource_name}: {len(items)} items")

    def on_download_error(self, resource_name: str, error_message: str):
        """Handle download errors."""
        self.status_label.setText(f"Error syncing {resource_name}: {error_message}")
        self.add_activity_log("Sync", resource_name, f"Error: {error_message}")

    def on_resource_selection_changed(self):
        """Handle resource tree selection changes."""
        current_item = self.resource_tree.currentItem()
        if current_item:
            item = current_item.data(0, Qt.UserRole)
            if isinstance(item, ResourceItem):
                self.show_item_details(item)
                self.add_to_project_btn.setEnabled(True)
                self.view_details_btn.setEnabled(True)
            else:
                # Endpoint selected
                self.add_to_project_btn.setEnabled(False)
                self.view_details_btn.setEnabled(False)

    def on_resource_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click on resource items."""
        item_data = item.data(0, Qt.UserRole)
        if isinstance(item_data, ResourceItem):
            self.show_item_details(item_data)


class EndpointDialog(QDialog):
    """Dialog for adding/editing API endpoints."""

    def __init__(self, parent=None, endpoint: Optional[ResourceEndpoint] = None):
        super().__init__(parent)
        self.endpoint = endpoint
        self.setup_ui()

    def setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Add Endpoint" if self.endpoint is None else "Edit Endpoint")
        self.setModal(True)
        self.resize(500, 300)

        layout = QVBoxLayout()

        # Form layout
        form_layout = QFormLayout()

        self.name_edit = QLineEdit()
        form_layout.addRow("Name:", self.name_edit)

        self.url_edit = QLineEdit()
        form_layout.addRow("URL:", self.url_edit)

        self.type_combo = QComboBox()
        self.type_combo.addItems([t.value for t in ResourceType])
        form_layout.addRow("Type:", self.type_combo)

        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        form_layout.addRow("API Key (optional):", self.api_key_edit)

        self.enabled_check = QCheckBox()
        self.enabled_check.setChecked(True)
        form_layout.addRow("Enabled:", self.enabled_check)

        layout.addLayout(form_layout)

        # Buttons
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

        # Load existing endpoint data if editing
        if self.endpoint:
            self.name_edit.setText(self.endpoint.name)
            self.url_edit.setText(self.endpoint.url)
            self.type_combo.setCurrentText(self.endpoint.resource_type.value)
            self.api_key_edit.setText(self.endpoint.api_key or "")
            self.enabled_check.setChecked(self.endpoint.is_enabled)

    def get_endpoint(self) -> ResourceEndpoint:
        """Get the endpoint data from the dialog."""
        return ResourceEndpoint(
            name=self.name_edit.text(),
            url=self.url_edit.text(),
            resource_type=ResourceType(self.type_combo.currentText()),
            api_key=self.api_key_edit.text() or None,
            is_enabled=self.enabled_check.isChecked()
        )