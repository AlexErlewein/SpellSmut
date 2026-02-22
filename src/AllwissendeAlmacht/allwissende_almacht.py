"""
Allwissende Almacht - Browse and select game icons for armor, weapons, and spells

Uses MSB-derived mappings for accurate handle names and categorization.
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QTabWidget, QGroupBox, QFormLayout, QTextEdit, QSplitter, QWidget,
    QTreeWidget, QTreeWidgetItem
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap


class AllwissendeAlmachtDialog(QDialog):
    """Browse and select game icons (Allwissende Almacht)"""

    iconSelected = Signal(str)  # Emit the selected icon handle/path

    def __init__(self, data_model, category: str = "item", parent=None):
        super().__init__(parent)
        self.data_model = data_model
        self.category = category  # "item", "spell", etc.
        self.selected_icon = None
        self._all_icons_cache: Optional[List[Dict[str, Any]]] = None
        self._source_filter: Optional[str] = None
        self._section_filter: Optional[str] = None
        self._subsection_filter: Optional[str] = None
        self._tree_items: Dict[str, QTreeWidgetItem] = {}

        # MSB-derived mappings
        self._item_mapping: Dict[str, Dict[str, Any]] = {}
        self._spell_mapping: Dict[str, Dict[str, Any]] = {}
        self._path_to_handle: Dict[str, str] = {}

        self.setWindowTitle("Allwissende Almacht - Icon Browser")
        self.setModal(True)
        self.resize(1100, 750)

        self._load_mappings()

        self.init_ui()
        # Delay population to ensure Qt app is fully initialized
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.filter_icons)

    def _get_data_path(self) -> Path:
        """Get the path to the data directory."""
        if hasattr(self.data_model, "project_root"):
            return Path(self.data_model.project_root) / "src" / "TirganachReloaded" / "data"
        return Path(__file__).parent.parent / "TirganachReloaded" / "data"

    def _get_icons_root(self) -> Path:
        """Get the path to the icons directory (prefer mapped with proper sizes)."""
        if hasattr(self.data_model, "project_root"):
            base = Path(self.data_model.project_root) / "ExtractedAssets" / "UI"
            # Prefer mapped icons (proper multi-cell dimensions)
            mapped = base / "icons_mapped"
            if mapped.exists():
                return mapped
            # Fall back to reextracted
            reextracted = base / "icons_reextracted"
            if reextracted.exists():
                return reextracted
            return base / "icons_extracted"
        # Fallback
        return Path(__file__).parent.parent.parent / "ExtractedAssets" / "UI" / "icons_mapped"

    def _load_mappings(self):
        """Load MSB-derived icon mappings."""
        data_path = self._get_data_path()

        # Load item mapping
        item_mapping_path = data_path / "item_icon_mapping.json"
        if item_mapping_path.exists():
            try:
                with open(item_mapping_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._item_mapping = data.get("mappings", {})
                # Build reverse lookup: icon path -> handle
                for handle, info in self._item_mapping.items():
                    if isinstance(info, dict) and "icon_path" in info:
                        self._path_to_handle[info["icon_path"]] = handle
            except Exception as e:
                print(f"Error loading item mapping: {e}")

        # Load spell mapping
        spell_mapping_path = data_path / "spell_icon_mapping.json"
        if spell_mapping_path.exists():
            try:
                with open(spell_mapping_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._spell_mapping = data.get("mappings", {})
                # Build reverse lookup
                for handle, info in self._spell_mapping.items():
                    if isinstance(info, dict) and "icon_path" in info:
                        self._path_to_handle[info["icon_path"]] = handle
            except Exception as e:
                print(f"Error loading spell mapping: {e}")

    def _handle_to_display_name(self, handle: str) -> str:
        """Convert a handle to a human-readable display name."""
        # Remove common prefixes
        name = handle
        for prefix in ["ui_item_equip_", "ui_item_quest_", "ui_item_", "ui_spell_"]:
            if name.lower().startswith(prefix):
                name = name[len(prefix):]
                break

        # Replace underscores with spaces and title case
        name = name.replace("_", " ").title()
        return name

    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout()

        # Search/filter section
        search_layout = QHBoxLayout()

        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Search by name or handle...")
        self.search_edit.textChanged.connect(self.filter_icons)
        search_layout.addWidget(self.search_edit)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_icons)
        search_layout.addWidget(refresh_btn)

        layout.addLayout(search_layout)

        # Main content area with navigation tree + tabs
        main_splitter = QSplitter(Qt.Horizontal)

        self.section_tree = QTreeWidget()
        self.section_tree.setHeaderHidden(True)
        self.section_tree.setMinimumWidth(180)
        self.section_tree.currentItemChanged.connect(self.on_section_changed)
        main_splitter.addWidget(self.section_tree)

        self.tabs = QTabWidget()
        main_splitter.addWidget(self.tabs)
        main_splitter.setStretchFactor(0, 0)
        main_splitter.setStretchFactor(1, 1)

        # Icon grid view
        grid_widget = QWidget()
        grid_layout = QVBoxLayout()

        # Icon table
        self.icon_table = QTableWidget(0, 4)
        self.icon_table.setHorizontalHeaderLabels([
            "Icon", "Name", "Handle", "Type"
        ])
        self.icon_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.icon_table.setSelectionMode(QTableWidget.SingleSelection)
        self.icon_table.doubleClicked.connect(self.accept)
        self.icon_table.setSortingEnabled(True)

        # Configure headers
        header = self.icon_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Icon column
        header.setSectionResizeMode(1, QHeaderView.Stretch)          # Name column
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents) # Handle column
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Type column

        # Set row height to accommodate icons
        self.icon_table.verticalHeader().setDefaultSectionSize(40)

        grid_layout.addWidget(self.icon_table)
        grid_widget.setLayout(grid_layout)
        self.tabs.addTab(grid_widget, "Icons")

        # Icon details view
        details_widget = QWidget()
        details_layout = QVBoxLayout()

        # Splitter for preview and details
        splitter = QSplitter(Qt.Horizontal)

        # Icon preview
        preview_group = QGroupBox("Icon Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel()
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("border: 2px solid #555; background: #222;")
        self.preview_label.setFixedSize(256, 256)
        preview_layout.addWidget(self.preview_label)

        preview_group.setLayout(preview_layout)
        splitter.addWidget(preview_group)

        # Icon details
        details_group = QGroupBox("Icon Details")
        details_form = QFormLayout()

        self.handle_label = QLabel()
        self.handle_label.setWordWrap(True)
        self.handle_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_form.addRow("Handle:", self.handle_label)

        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        self.path_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        details_form.addRow("Path:", self.path_label)

        self.category_label = QLabel()
        details_form.addRow("Category:", self.category_label)

        self.subcategory_label = QLabel()
        details_form.addRow("Subcategory:", self.subcategory_label)

        self.atlas_label = QLabel()
        details_form.addRow("Atlas:", self.atlas_label)

        self.index_label = QLabel()
        details_form.addRow("Index:", self.index_label)

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Icon description...")
        details_form.addRow("Notes:", self.description_edit)

        details_group.setLayout(details_form)
        splitter.addWidget(details_group)

        # Set initial sizes
        splitter.setSizes([300, 500])

        details_layout.addWidget(splitter)
        details_widget.setLayout(details_layout)
        self.tabs.addTab(details_widget, "Details")

        self.populate_section_tree()

        layout.addWidget(main_splitter)

        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Total icons: 0")
        self.filter_label = QLabel("Showing: 0 / 0")
        self.mapping_label = QLabel("Mapped: 0")
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.filter_label)
        stats_layout.addWidget(self.mapping_label)
        stats_layout.addStretch()
        layout.addLayout(stats_layout)

        # Buttons
        btn_layout = QHBoxLayout()

        self.select_btn = QPushButton("Select Icon")
        self.select_btn.clicked.connect(self.accept)
        self.select_btn.setEnabled(False)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.select_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        # Connect table selection
        self.icon_table.itemSelectionChanged.connect(self.on_selection_changed)

        self.setLayout(layout)

        self.set_initial_section_selection()

    def populate_section_tree(self):
        """Populate the category navigation tree."""
        self.section_tree.clear()
        self._tree_items.clear()

        def _add_item(parent: Optional[QTreeWidgetItem], key: str, label: str,
                      source: Optional[str], section: Optional[str], subsection: Optional[str] = None):
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.ItemDataRole.UserRole, {
                "source": source,
                "section": section,
                "subsection": subsection
            })
            if parent is None:
                self.section_tree.addTopLevelItem(item)
            else:
                parent.addChild(item)
            self._tree_items[key] = item
            return item

        _add_item(None, "all", "All Icons", None, None)

        # Spells
        _add_item(None, "spell", "Spells", "spell", None)

        # Items - with subcategories from MSB parsing
        itm_root = _add_item(None, "item", "Items", "item", None)

        # Weapons
        weapon_root = _add_item(itm_root, "weapon", "Weapons", "item", "weapon")
        _add_item(weapon_root, "weapon_sword", "Swords", "item", "weapon", "sword")
        _add_item(weapon_root, "weapon_axe", "Axes", "item", "weapon", "axe")
        _add_item(weapon_root, "weapon_mace", "Maces/Hammers", "item", "weapon", "mace")
        _add_item(weapon_root, "weapon_staff", "Staves", "item", "weapon", "staff")
        _add_item(weapon_root, "weapon_bow", "Bows", "item", "weapon", "bow")
        _add_item(weapon_root, "weapon_dagger", "Daggers", "item", "weapon", "dagger")
        _add_item(weapon_root, "weapon_other", "Other Weapons", "item", "weapon", "other")

        # Armor
        armor_root = _add_item(itm_root, "armor", "Armor", "item", "armor")
        _add_item(armor_root, "armor_chest", "Chest", "item", "armor", "chest")
        _add_item(armor_root, "armor_helmet", "Helmets", "item", "armor", "helmet")
        _add_item(armor_root, "armor_legs", "Legs", "item", "armor", "legs")
        _add_item(armor_root, "armor_shield", "Shields", "item", "armor", "shield")

        # Accessories
        acc_root = _add_item(itm_root, "accessory", "Accessories", "item", "accessory")
        _add_item(acc_root, "accessory_ring", "Rings", "item", "accessory", "ring")
        _add_item(acc_root, "accessory_amulet", "Amulets", "item", "accessory", "amulet")

        # Other categories
        _add_item(itm_root, "rune", "Runes", "item", "rune")
        _add_item(itm_root, "consumable", "Consumables", "item", "consumable")
        _add_item(itm_root, "misc", "Miscellaneous", "item", "misc")

        self.section_tree.expandAll()

    def set_initial_section_selection(self):
        """Set the initial tree selection based on category."""
        if self.category == "spell":
            item = self._tree_items.get("spell")
        else:
            item = self._tree_items.get("item")

        if item is None:
            item = self._tree_items.get("all")

        if item is not None:
            self.section_tree.setCurrentItem(item)

    def on_section_changed(self, current: Optional[QTreeWidgetItem], previous: Optional[QTreeWidgetItem]):
        """Handle tree selection changes."""
        if current is None:
            self._source_filter = None
            self._section_filter = None
            self._subsection_filter = None
        else:
            data = current.data(0, Qt.ItemDataRole.UserRole) or {}
            self._source_filter = data.get("source")
            self._section_filter = data.get("section")
            self._subsection_filter = data.get("subsection")

        self.filter_icons()

    def get_all_icons(self) -> List[Dict[str, Any]]:
        """Get all available icons using MSB mappings."""
        if self._all_icons_cache is not None:
            return self._all_icons_cache

        icons: List[Dict[str, Any]] = []
        icons_root = self._get_icons_root()

        # Item icons from MSB mapping
        for handle, info in self._item_mapping.items():
            if not isinstance(info, dict):
                continue

            icon_path = info.get("icon_path", "")
            full_path = icons_root / icon_path

            if not full_path.exists():
                continue

            category = info.get("category") or "misc"
            subcategory = info.get("subcategory") or "other"

            # Build display type string
            if subcategory and subcategory != "other":
                display_type = f"{category}/{subcategory}"
            else:
                display_type = category

            icons.append({
                "name": self._handle_to_display_name(handle),
                "handle": handle,
                "category": category,
                "subcategory": subcategory,
                "display_type": display_type,
                "source": "item",
                "path": icon_path,
                "atlas": f"atlas_{info.get('atlas_number', 0)}",
                "index": info.get("icon_index", 0),
                "mapped": True,
            })

        # Spell icons from MSB mapping
        for handle, info in self._spell_mapping.items():
            if not isinstance(info, dict):
                continue

            icon_path = info.get("icon_path", "")
            full_path = icons_root / icon_path

            if not full_path.exists():
                continue

            icons.append({
                "name": self._handle_to_display_name(handle),
                "handle": handle,
                "category": "spell",
                "subcategory": None,
                "display_type": "spell",
                "source": "spell",
                "path": icon_path,
                "atlas": f"atlas_{info.get('atlas_number', 0)}",
                "index": info.get("icon_index", 0),
                "mapped": True,
            })

        # Also scan for unmapped icons (those without MSB entries)
        self._add_unmapped_icons(icons, icons_root)

        self._all_icons_cache = icons
        return icons

    def _add_unmapped_icons(self, icons: List[Dict[str, Any]], icons_root: Path):
        """Add icons that don't have MSB mappings."""
        mapped_paths = {icon["path"] for icon in icons}

        # Scan item icons
        itm_dir = icons_root / "itm"
        if itm_dir.exists():
            for atlas_dir in itm_dir.iterdir():
                if not (atlas_dir.is_dir() and atlas_dir.name.startswith("atlas_")):
                    continue

                for icon_file in atlas_dir.iterdir():
                    if not (icon_file.is_file() and icon_file.suffix.lower() == ".png"):
                        continue
                    if icon_file.name.startswith("_"):
                        continue  # Skip atlas preview files

                    rel_path = f"itm/{atlas_dir.name}/{icon_file.name}"
                    if rel_path in mapped_paths:
                        continue

                    try:
                        idx = int(icon_file.stem.split("_")[1])
                    except (ValueError, IndexError):
                        idx = 0

                    icons.append({
                        "name": f"{atlas_dir.name} {icon_file.stem}",
                        "handle": "",
                        "category": "unmapped",
                        "subcategory": None,
                        "display_type": "unmapped",
                        "source": "item",
                        "path": rel_path,
                        "atlas": atlas_dir.name,
                        "index": idx,
                        "mapped": False,
                    })

        # Scan spell icons
        spell_dir = icons_root / "spell"
        if spell_dir.exists():
            for atlas_dir in spell_dir.iterdir():
                if not (atlas_dir.is_dir() and atlas_dir.name.startswith("atlas_")):
                    continue

                for icon_file in atlas_dir.iterdir():
                    if not (icon_file.is_file() and icon_file.suffix.lower() == ".png"):
                        continue
                    if icon_file.name.startswith("_"):
                        continue

                    rel_path = f"spell/{atlas_dir.name}/{icon_file.name}"
                    if rel_path in mapped_paths:
                        continue

                    try:
                        idx = int(icon_file.stem.split("_")[1])
                    except (ValueError, IndexError):
                        idx = 0

                    icons.append({
                        "name": f"{atlas_dir.name} {icon_file.stem}",
                        "handle": "",
                        "category": "unmapped",
                        "subcategory": None,
                        "display_type": "unmapped (spell)",
                        "source": "spell",
                        "path": rel_path,
                        "atlas": atlas_dir.name,
                        "index": idx,
                        "mapped": False,
                    })

    def populate_icons(self, icon_list: Optional[List[Dict[str, Any]]] = None):
        """Populate the icon table."""
        if icon_list is None:
            icon_list = self.get_all_icons()

        self.icon_table.setSortingEnabled(False)
        self.icon_table.setRowCount(0)

        for icon_data in icon_list:
            row_count = self.icon_table.rowCount()
            self.icon_table.insertRow(row_count)

            # Icon cell (column 0)
            icon_pixmap = self.load_icon_pixmap(icon_data)
            icon_item = QTableWidgetItem()
            if icon_pixmap:
                icon_item.setData(Qt.ItemDataRole.DecorationRole, icon_pixmap)
            else:
                icon_item.setText("?")
            self.icon_table.setItem(row_count, 0, icon_item)

            # Name cell (column 1)
            name_item = QTableWidgetItem(icon_data.get('name', 'Unknown'))
            name_item.setData(Qt.ItemDataRole.UserRole, icon_data)
            self.icon_table.setItem(row_count, 1, name_item)

            # Handle cell (column 2)
            handle = icon_data.get('handle', '')
            handle_item = QTableWidgetItem(handle if handle else "(unmapped)")
            if not handle:
                handle_item.setForeground(Qt.gray)
            self.icon_table.setItem(row_count, 2, handle_item)

            # Type cell (column 3)
            display_type = icon_data.get('display_type', 'unknown')
            type_item = QTableWidgetItem(display_type)
            self.icon_table.setItem(row_count, 3, type_item)

        self.icon_table.setSortingEnabled(True)
        self.update_stats(icon_list)

    def load_icon_pixmap(self, icon_data: Dict[str, Any], size=(32, 32)) -> Optional[QPixmap]:
        """Load icon pixmap from icon data."""
        try:
            icons_root = self._get_icons_root()
            icon_path = icons_root / icon_data.get('path', '')
            if icon_path.exists():
                pixmap = QPixmap(str(icon_path))
                if not pixmap.isNull():
                    return pixmap.scaled(size[0], size[1],
                                       Qt.AspectRatioMode.KeepAspectRatio,
                                       Qt.TransformationMode.SmoothTransformation)
        except Exception as e:
            print(f"Error loading icon pixmap: {e}")
        return None

    def filter_icons(self):
        """Filter icons based on search text and category."""
        search_text = self.search_edit.text().lower()

        filtered = []
        all_icons = self.get_all_icons()

        for icon_data in all_icons:
            # Source filter (spell vs item)
            if self._source_filter:
                if icon_data.get("source") != self._source_filter:
                    continue

            # Section filter (weapon, armor, etc.)
            if self._section_filter:
                if icon_data.get("category") != self._section_filter:
                    continue

            # Subsection filter (sword, helmet, etc.)
            if self._subsection_filter:
                if icon_data.get("subcategory") != self._subsection_filter:
                    continue

            # Text search
            if search_text:
                search_fields = [
                    icon_data.get('name', '').lower(),
                    icon_data.get('handle', '').lower(),
                    icon_data.get('path', '').lower(),
                    icon_data.get('category', '').lower(),
                    icon_data.get('subcategory', '').lower() if icon_data.get('subcategory') else '',
                ]
                if not any(search_text in field for field in search_fields):
                    continue

            filtered.append(icon_data)

        self.populate_icons(filtered)

        # Update filter statistics
        total_icons = len(all_icons)
        filtered_count = len(filtered)
        self.filter_label.setText(f"Showing: {filtered_count} / {total_icons}")

    def refresh_icons(self):
        """Refresh the icon list."""
        self._all_icons_cache = None
        self._load_mappings()
        self.filter_icons()

    def on_selection_changed(self):
        """Handle table selection changes."""
        selected_rows = self.icon_table.selectedIndexes()
        self.select_btn.setEnabled(len(selected_rows) > 0)

        if selected_rows:
            row = selected_rows[0].row()
            name_item = self.icon_table.item(row, 1)
            if name_item:
                icon_data = name_item.data(Qt.ItemDataRole.UserRole)
                if icon_data:
                    self.update_preview(icon_data)

    def update_preview(self, icon_data: Dict[str, Any]):
        """Update the icon preview and details."""
        # Update preview
        pixmap = self.load_icon_pixmap(icon_data, size=(256, 256))
        if pixmap:
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("No Preview Available")

        # Update details
        self.handle_label.setText(icon_data.get('handle', '') or "(no handle)")
        self.path_label.setText(icon_data.get('path', ''))
        self.category_label.setText(icon_data.get('category', 'unknown'))
        self.subcategory_label.setText(icon_data.get('subcategory', '') or '-')
        self.atlas_label.setText(icon_data.get('atlas', ''))
        self.index_label.setText(str(icon_data.get('index', 0)))

    def update_stats(self, icon_list: List[Dict[str, Any]]):
        """Update statistics display."""
        total = len(icon_list)
        mapped = sum(1 for i in icon_list if i.get('mapped', False))

        self.stats_label.setText(f"Total: {total}")
        self.mapping_label.setText(f"Mapped: {mapped} ({100*mapped//max(total,1)}%)")

    def get_selected_icon(self) -> Optional[str]:
        """Get the selected icon handle or path."""
        selected_rows = self.icon_table.selectedIndexes()
        if not selected_rows:
            return None

        row = selected_rows[0].row()
        name_item = self.icon_table.item(row, 1)
        if name_item:
            icon_data = name_item.data(Qt.ItemDataRole.UserRole)
            if icon_data:
                # Return handle if available, otherwise path
                return icon_data.get('handle') or icon_data.get('path')

        return None

    def accept(self):
        """Handle dialog acceptance."""
        self.selected_icon = self.get_selected_icon()
        if self.selected_icon:
            self.iconSelected.emit(self.selected_icon)
            super().accept()
        else:
            QMessageBox.warning(self, "No Selection",
                              "Please select an icon to use.")
