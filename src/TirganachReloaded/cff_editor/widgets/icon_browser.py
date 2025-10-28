"""
Icon Browser Widget - Browse and select game icons for armor, weapons, and spells
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
import json

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QComboBox,
    QTabWidget, QGroupBox, QFormLayout, QTextEdit, QSplitter, QWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap, QIcon


class IconBrowserDialog(QDialog):
    """Browse and select game icons"""

    iconSelected = Signal(str)  # Emit the selected icon handle/path

    def __init__(self, data_model, category: str = "item", parent=None):
        super().__init__(parent)
        self.data_model = data_model
        self.category = category  # "item", "spell", etc.
        self.selected_icon = None
        
        self.setWindowTitle("Icon Browser")
        self.setModal(True)
        self.resize(1000, 700)
        
        self.init_ui()
        self.populate_icons()

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
        
        search_layout.addWidget(QLabel("Category:"))
        self.category_combo = QComboBox()
        self.category_combo.addItems([
            "All Categories",
            "Item Icons",
            "Spell Icons",
            "UI Icons",
            "Character Icons",
            "Building Icons"
        ])
        self.category_combo.currentTextChanged.connect(self.filter_icons)
        search_layout.addWidget(self.category_combo)
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_icons)
        search_layout.addWidget(refresh_btn)
        
        layout.addLayout(search_layout)
        
        # Main content area with tabs
        self.tabs = QTabWidget()
        
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
        
        layout.addWidget(self.tabs)
        
        # Statistics
        stats_layout = QHBoxLayout()
        self.stats_label = QLabel("Total icons: 0")
        stats_layout.addWidget(self.stats_label)
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
        icons = []
        
        # Get item icons
        if hasattr(self.data_model, 'icon_index') and self.data_model.icon_index:
            icon_entries = self.data_model.icon_index.get('icons', {})
            for icon_key, icon_info in icon_entries.items():
                if not icon_info.get('is_empty', False):
                    icon_data = {
                        'name': icon_info.get('name', icon_key),
                        'handle': icon_info.get('handle', ''),
                        'category': icon_info.get('category', 'item'),
                        'path': icon_info.get('path', ''),
                        'atlas': icon_info.get('atlas', ''),
                        'index': icon_info.get('index', 0)
                    }
                    icons.append(icon_data)
        
        # Get spell icons
        spell_icons_root = self.data_model.icons_root / "spell"
        if spell_icons_root.exists():
            for atlas_dir in spell_icons_root.iterdir():
                if atlas_dir.is_dir() and atlas_dir.name.startswith("atlas_"):
                    for icon_file in atlas_dir.iterdir():
                        if icon_file.suffix.lower() == ".png" and icon_file.name.startswith("icon_"):
                            icon_data = {
                                'name': icon_file.stem.replace("_", " ").title(),
                                'handle': icon_file.stem,
                                'category': 'spell',
                                'path': str(icon_file.relative_to(self.data_model.icons_root)),
                                'atlas': atlas_dir.name,
                                'index': int(icon_file.stem.split('_')[1])
                            }
                            icons.append(icon_data)
        
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
        category_filter = self.category_combo.currentText()
        
        filtered = []
        all_icons = self.get_all_icons()
        
        for icon_data in all_icons:
            # Text search
            if search_text:
                search_fields = [
                    icon_data.get('name', '').lower(),
                    icon_data.get('handle', '').lower(),
                    icon_data.get('path', '').lower()
                ]
                if not any(search_text in field for field in search_fields):
                    continue
            
            # Category filter
            if category_filter != "All Categories":
                category_map = {
                    "Item Icons": "item",
                    "Spell Icons": "spell",
                    "UI Icons": "ui",
                    "Character Icons": "character",
                    "Building Icons": "building"
                }
                expected_category = category_map.get(category_filter, "")
                if icon_data.get('category', '') != expected_category:
                    continue
            
            filtered.append(icon_data)
        
        self.populate_icons(filtered)

    def refresh_icons(self):
        """Refresh the icon list"""
        self.data_model.clear_icon_cache()
        self.populate_icons()

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
        self.stats_label.setText(f"Showing {count} icons")

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