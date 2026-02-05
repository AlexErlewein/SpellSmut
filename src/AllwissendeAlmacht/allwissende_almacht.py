"""
Allwissende Almacht - Browse and select game icons for armor, weapons, and spells
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
from PySide6.QtGui import QPixmap, QIcon, QImageReader


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
        self._tree_items: Dict[str, QTreeWidgetItem] = {}
        self._itm_section_mapping: Dict[str, Dict[str, Any]] = {}
        
        self.setWindowTitle("Allwissende Almacht")
        self.setModal(True)
        self.resize(1000, 700)

        self._load_mappings()
        
        self.init_ui()
        # Delay population to ensure Qt app is fully initialized
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self.filter_icons)

    def _normalize_mapping_key(self, key: str) -> str:
        return str(key).replace("\\", "/")

    def _get_itm_mapping_path(self) -> Path:
        if hasattr(self.data_model, "project_root"):
            return Path(self.data_model.project_root) / "src" / "AllwissendeAlmacht" / "itm_icon_sections.json"
        return Path(__file__).with_name("itm_icon_sections.json")

    def _load_mappings(self):
        self._itm_section_mapping = {}
        mapping_path = self._get_itm_mapping_path()
        if not mapping_path.exists():
            return

        try:
            with open(mapping_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
            items = raw.get("items", raw) if isinstance(raw, dict) else {}
            if not isinstance(items, dict):
                return
            self._itm_section_mapping = {
                self._normalize_mapping_key(k): (v if isinstance(v, dict) else {})
                for k, v in items.items()
            }
        except Exception:
            self._itm_section_mapping = {}

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
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_icons)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Main content area with navigation tree + tabs
        main_splitter = QSplitter(Qt.Horizontal)

        self.section_tree = QTreeWidget()
        self.section_tree.setHeaderHidden(True)
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
            "Icon", "Name", "Handle", "Category"
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
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents) # Category column
        
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
        details_form.addRow("Handle:", self.handle_label)
        
        self.path_label = QLabel()
        self.path_label.setWordWrap(True)
        details_form.addRow("Path:", self.path_label)
        
        self.category_label = QLabel()
        details_form.addRow("Category:", self.category_label)
        
        self.atlas_label = QLabel()
        details_form.addRow("Atlas:", self.atlas_label)
        
        self.index_label = QLabel()
        details_form.addRow("Index:", self.index_label)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setPlaceholderText("Icon description...")
        details_form.addRow("Description:", self.description_edit)
        
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
        stats_layout.addWidget(self.stats_label)
        stats_layout.addWidget(self.filter_label)
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
        self.section_tree.clear()
        self._tree_items.clear()

        def _add_item(parent: Optional[QTreeWidgetItem], key: str, label: str, source: Optional[str], section: Optional[str]):
            item = QTreeWidgetItem([label])
            item.setData(0, Qt.ItemDataRole.UserRole, {"source": source, "section": section})
            if parent is None:
                self.section_tree.addTopLevelItem(item)
            else:
                parent.addChild(item)
            self._tree_items[key] = item
            return item

        _add_item(None, "all", "All", None, None)
        _add_item(None, "spells", "Spells", "spell", None)

        itm_root = _add_item(None, "itm", "Items (ITM)", "itm", None)
        _add_item(itm_root, "itm_weapons", "Weapons", "itm", "weapon")
        _add_item(itm_root, "itm_armor", "Armor", "itm", "armor")
        _add_item(itm_root, "itm_other", "Other", "itm", "other")

        _add_item(None, "legacy", "Legacy Index", "legacy", None)

        self.section_tree.expandAll()

    def set_initial_section_selection(self):
        if self.category == "spell":
            item = self._tree_items.get("spells")
        else:
            item = self._tree_items.get("itm")

        if item is None:
            item = self._tree_items.get("all")

        if item is not None:
            self.section_tree.setCurrentItem(item)

    def on_section_changed(self, current: Optional[QTreeWidgetItem], previous: Optional[QTreeWidgetItem]):
        if current is None:
            self._source_filter = None
            self._section_filter = None
        else:
            data = current.data(0, Qt.ItemDataRole.UserRole) or {}
            self._source_filter = data.get("source")
            self._section_filter = data.get("section")

        self.filter_icons()

    def classify_itm_icon(self, icon_file: Path) -> str:
        try:
            reader = QImageReader(str(icon_file))
            size = reader.size()
            w = int(size.width())
            h = int(size.height())
            if w <= 0 or h <= 0:
                return "other"

            if max(w, h) < 70:
                return "other"

            ratio = h / w if w else 0.0
            if ratio >= 3.0 or ratio <= 0.45:
                return "weapon"

            return "armor"
        except Exception:
            return "other"

    def populate_icons(self, icon_list: Optional[List[Dict[str, Any]]] = None):
        """Populate the icon table"""
        if icon_list is None:
            icon_list = self.get_all_icons()
        
        self.icon_table.setRowCount(0)  # Clear existing rows
        
        for icon_data in icon_list:
            row_count = self.icon_table.rowCount()
            self.icon_table.insertRow(row_count)
            
            # Icon cell (column 0)
            icon_pixmap = self.load_icon_pixmap(icon_data)
            if icon_pixmap:
                icon_item = QTableWidgetItem()
                icon_item.setData(Qt.ItemDataRole.DecorationRole, icon_pixmap)
                self.icon_table.setItem(row_count, 0, icon_item)
            else:
                icon_item = QTableWidgetItem("No Icon")
                self.icon_table.setItem(row_count, 0, icon_item)
            
            # Name cell (column 1)
            name_item = QTableWidgetItem(icon_data.get('name', 'Unknown'))
            name_item.setData(Qt.ItemDataRole.UserRole, icon_data)  # Store full data
            self.icon_table.setItem(row_count, 1, name_item)
            
            # Handle cell (column 2)
            handle_item = QTableWidgetItem(icon_data.get('handle', ''))
            self.icon_table.setItem(row_count, 2, handle_item)
            
            # Category cell (column 3)
            category_item = QTableWidgetItem(icon_data.get('category', 'unknown'))
            self.icon_table.setItem(row_count, 3, category_item)
        
        # Update statistics
        self.update_stats(len(icon_list))

    def get_all_icons(self) -> List[Dict[str, Any]]:
        """Get all available icons from the data model"""
        if self._all_icons_cache is not None:
            return self._all_icons_cache

        icons: List[Dict[str, Any]] = []

        # Extracted ITM sprites (new item_*.png)
        itm_icons_root = self.data_model.icons_root / "itm"
        if itm_icons_root.exists():
            for atlas_dir in itm_icons_root.iterdir():
                if not (atlas_dir.is_dir() and atlas_dir.name.startswith("atlas_")):
                    continue

                for icon_file in atlas_dir.iterdir():
                    if not (icon_file.is_file() and icon_file.suffix.lower() == ".png"):
                        continue
                    if not icon_file.name.startswith("item_"):
                        continue

                    try:
                        idx = int(icon_file.stem.split("_")[1])
                    except Exception:
                        idx = 0

                    rel_path = icon_file.relative_to(self.data_model.icons_root)
                    rel_path_str = self._normalize_mapping_key(str(rel_path))
                    mapping = self._itm_section_mapping.get(rel_path_str, {})
                    mapped_section = mapping.get("section")
                    section = mapped_section if mapped_section in {"weapon", "armor", "other"} else self.classify_itm_icon(icon_file)
                    mapped_name = mapping.get("name")
                    display_name = mapped_name if isinstance(mapped_name, str) and mapped_name.strip() else f"{atlas_dir.name} {icon_file.stem}"
                    icons.append(
                        {
                            "name": display_name,
                            "handle": rel_path_str,
                            "category": section,
                            "section": section,
                            "source": "itm",
                            "path": rel_path_str,
                            "atlas": atlas_dir.name,
                            "index": idx,
                        }
                    )

        # Spell icons
        spell_icons_root = self.data_model.icons_root / "spell"
        if spell_icons_root.exists():
            for atlas_dir in spell_icons_root.iterdir():
                if atlas_dir.is_dir() and atlas_dir.name.startswith("atlas_"):
                    for icon_file in atlas_dir.iterdir():
                        if icon_file.suffix.lower() == ".png" and icon_file.name.startswith("icon_"):
                            icon_data = {
                                "name": icon_file.stem.replace("_", " ").title(),
                                "handle": icon_file.stem,
                                "category": "spell",
                                "section": None,
                                "source": "spell",
                                "path": str(icon_file.relative_to(self.data_model.icons_root)),
                                "atlas": atlas_dir.name,
                                "index": int(icon_file.stem.split("_")[1]),
                            }
                            icons.append(icon_data)

        # Legacy icon_index entries (if present) - filtered to existing files
        if hasattr(self.data_model, "icon_index") and self.data_model.icon_index:
            icon_entries = self.data_model.icon_index.get("icons", {})
            for icon_key, icon_info in icon_entries.items():
                if icon_info.get("is_empty", False):
                    continue

                rel = icon_info.get("path", "")
                if not rel:
                    continue

                full_path = self.data_model.icons_root / rel
                if not full_path.exists():
                    continue

                # Avoid duplicating spell icons since we scan them explicitly above
                if str(rel).startswith("spell/"):
                    continue

                icons.append(
                    {
                        "name": icon_info.get("name", icon_key),
                        "handle": icon_info.get("handle", ""),
                        "category": icon_info.get("category", "legacy"),
                        "section": None,
                        "source": "legacy",
                        "path": rel,
                        "atlas": icon_info.get("atlas", ""),
                        "index": icon_info.get("index", 0),
                    }
                )

        self._all_icons_cache = icons
        return icons

    def load_icon_pixmap(self, icon_data: Dict[str, Any], size=(32, 32)) -> Optional[QPixmap]:
        """Load icon pixmap from icon data"""
        try:
            icon_path = self.data_model.icons_root / icon_data.get('path', '')
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
        """Filter icons based on search text and category"""
        search_text = self.search_edit.text().lower()
        
        filtered = []
        all_icons = self.get_all_icons()
        
        for icon_data in all_icons:
            if self._source_filter and icon_data.get("source") != self._source_filter:
                continue

            if self._section_filter and icon_data.get("section") != self._section_filter:
                continue

            # Text search
            if search_text:
                search_fields = [
                    icon_data.get('name', '').lower(),
                    icon_data.get('handle', '').lower(),
                    icon_data.get('path', '').lower()
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
        """Refresh the icon list"""
        self._load_mappings()
        self._all_icons_cache = None
        self.data_model.clear_icon_cache()
        self.filter_icons()

    def on_selection_changed(self):
        """Handle table selection changes"""
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
        """Update the icon preview and details"""
        # Update preview
        pixmap = self.load_icon_pixmap(icon_data, size=(256, 256))
        if pixmap:
            self.preview_label.setPixmap(pixmap)
        else:
            self.preview_label.setText("No Preview Available")
        
        # Update details
        self.handle_label.setText(icon_data.get('handle', ''))
        self.path_label.setText(icon_data.get('path', ''))
        self.category_label.setText(icon_data.get('category', 'unknown'))
        self.atlas_label.setText(icon_data.get('atlas', ''))
        self.index_label.setText(str(icon_data.get('index', 0)))
        
        # Update description
        self.description_edit.setPlainText(icon_data.get('description', ''))

    def update_stats(self, count: int):
        """Update statistics display"""
        self.stats_label.setText(f"Total icons: {count}")
        self.filter_label.setText(f"Showing: {count} / {count}")

    def get_selected_icon(self) -> Optional[str]:
        """Get the selected icon handle"""
        selected_rows = self.icon_table.selectedIndexes()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        handle_item = self.icon_table.item(row, 2)  # Handle column
        if handle_item:
            return handle_item.text()
        
        return None

    def accept(self):
        """Handle dialog acceptance"""
        self.selected_icon = self.get_selected_icon()
        if self.selected_icon:
            self.iconSelected.emit(self.selected_icon)
            super().accept()
        else:
            QMessageBox.warning(self, "No Selection",
                              "Please select an icon to use.")