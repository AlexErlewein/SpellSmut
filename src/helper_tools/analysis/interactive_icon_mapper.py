#!/usr/bin/env python3
"""
Interactive Icon Mapper Tool

Provides a GUI for visually mapping icon handles to actual icon files.
Allows manual verification and correction of automatic mappings.

Features:
- Browse items and their assigned icons
- View all possible icon matches
- Manually select correct icon
- Export verified mappings
- Search by item ID or handle name
"""

import json
import sys
from pathlib import Path

try:
    from PyQt6.QtCore import QSize, Qt
    from PyQt6.QtGui import QIcon, QImage, QPixmap
    from PyQt6.QtWidgets import (
        QApplication,
        QCheckBox,
        QComboBox,
        QFileDialog,
        QGridLayout,
        QGroupBox,
        QHBoxLayout,
        QLabel,
        QLineEdit,
        QListWidget,
        QListWidgetItem,
        QMainWindow,
        QMessageBox,
        QPushButton,
        QScrollArea,
        QSpinBox,
        QSplitter,
        QTextEdit,
        QVBoxLayout,
        QWidget,
    )
except ImportError:
    print("PyQt6 not found. Please install: uv pip install PyQt6")
    sys.exit(1)


class IconMapperWindow(QMainWindow):
    """Main window for icon mapping tool."""

    def __init__(self):
        super().__init__()

        self.project_root = Path(__file__).parent.parent.parent.parent
        self.icons_root = (
            self.project_root / "ExtractedAssets" / "UI" / "icons_extracted"
        )
        self.mapping_path = (
            self.project_root
            / "src"
            / "TirganachReloaded"
            / "data"
            / "ui_icon_mapping.json"
        )
        self.gamedata_path = (
            self.project_root
            / "src"
            / "TirganachReloaded"
            / "exports"
            / "GameData.json"
        )

        # Load data
        self.load_data()

        # Current state
        self.current_item_id = None
        self.verified_mappings = {}  # item_id -> {index -> icon_path}
        self.load_verified_mappings()

        # Setup UI
        self.init_ui()

        # Load first item
        if self.item_list:
            self.item_list_widget.setCurrentRow(0)

    def load_data(self):
        """Load all required data files."""

        # Load icon index (check for split files first)
        manifest_path = self.icons_root / "icon_index_manifest.json"
        if manifest_path.exists():
            # Load from split files
            self.icon_index = self._load_split_icon_index()
        else:
            # Load single file
            with open(self.icons_root / "icon_index.json", "r") as f:
                self.icon_index = json.load(f)

        # Load icon analysis (check for split files first)
        analysis_manifest_path = self.icons_root / "icon_analysis_manifest.json"
        if analysis_manifest_path.exists():
            # Load from split files
            self.icon_analysis = self._load_split_icon_analysis()
        else:
            # Load single file
            analysis_path = self.icons_root / "icon_analysis.json"
            if analysis_path.exists():
                with open(analysis_path, "r") as f:
                    self.icon_analysis = json.load(f)
            else:
                # No analysis file found, create empty structure
                self.icon_analysis = {"analyses": []}

        # Load mapping
        with open(self.mapping_path, "r") as f:
            self.mapping = json.load(f)

        # Load GameData for item names
        with open(self.gamedata_path, "r") as f:
            gamedata = json.load(f)

            # Build localization lookup (English names)
            self.localization = {}
            for entry in gamedata.get("localisation", []):
                # Only use English entries (language value 1)
                if entry.get("language", {}).get("value") == [1]:
                    text_id = entry.get("text_id")
                    text = entry.get("text")
                    if text_id is not None and text:
                        self.localization[str(text_id)] = text

            # Build item name lookup
            self.item_names = {}
            for item in gamedata.get("items", []):
                item_id = item.get("item_id")
                name_id = item.get("name_id")
                if item_id and name_id:
                    # Look up the actual name from localization
                    name = self.localization.get(str(name_id), f"Item {item_id}")
                    self.item_names[item_id] = name

        # Build item list
        self.item_list = []
        for item_id_str, icons in sorted(
            self.mapping["item_to_icons"].items(), key=lambda x: int(x[0])
        ):
            item_id = int(item_id_str)
            item_name = self.item_names.get(item_id, f"Item {item_id}")
            self.item_list.append({"id": item_id, "name": item_name, "icons": icons})

    def _load_split_icon_index(self) -> dict:
        """
        Load icon index from split files.

        Returns:
            Combined icon index data with stats and icons
        """
        manifest_path = self.icons_root / "icon_index_manifest.json"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Combine all icons from split files
        all_icons = {}

        for file_info in manifest["files"]:
            file_path = self.icons_root / file_info["file"]
            with open(file_path, "r") as f:
                part_data = json.load(f)
                all_icons.update(part_data["icons"])

        return {"stats": manifest["stats"], "icons": all_icons}

    def _load_split_icon_analysis(self) -> dict:
        """
        Load icon analysis from split files.

        Returns:
            Combined analysis data
        """
        manifest_path = self.icons_root / "icon_analysis_manifest.json"

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Combine all analyses from split files
        all_analyses = []

        for file_info in manifest["files"]:
            file_path = self.icons_root / file_info["file"]
            with open(file_path, "r") as f:
                part_data = json.load(f)
                all_analyses.extend(part_data["analyses"])

        return {"summary": manifest["summary"], "analyses": all_analyses}

    def load_verified_mappings(self):
        """Load previously verified mappings."""
        verified_path = (
            self.project_root
            / "src"
            / "TirganachReloaded"
            / "data"
            / "verified_icon_mappings.json"
        )

        if verified_path.exists():
            with open(verified_path, "r") as f:
                self.verified_mappings = json.load(f)

    def save_verified_mappings(self):
        """Save verified mappings."""
        verified_path = (
            self.project_root
            / "src"
            / "TirganachReloaded"
            / "data"
            / "verified_icon_mappings.json"
        )

        verified_path.parent.mkdir(parents=True, exist_ok=True)
        with open(verified_path, "w") as f:
            json.dump(self.verified_mappings, f, indent=2)

        QMessageBox.information(
            self, "Saved", f"Verified mappings saved to:\n{verified_path}"
        )

    def init_ui(self):
        """Initialize the user interface."""

        self.setWindowTitle("SpellForce Icon Mapper")
        self.setGeometry(100, 100, 1400, 900)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)

        # Main layout
        main_layout = QHBoxLayout(central)

        # Left panel: Item list
        left_panel = self.create_left_panel()

        # Right panel: Icon details
        right_panel = self.create_right_panel()

        # Add to splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 3)

        main_layout.addWidget(splitter)

        # Status bar
        self.statusBar().showMessage("Ready")

    def create_left_panel(self) -> QWidget:
        """Create left panel with item list."""

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Search
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Item ID or name...")
        self.search_input.textChanged.connect(self.filter_items)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        # Filter options
        filter_group = QGroupBox("Filters")
        filter_layout = QVBoxLayout(filter_group)

        self.show_verified = QCheckBox("Show verified only")
        self.show_verified.stateChanged.connect(self.filter_items)
        filter_layout.addWidget(self.show_verified)

        self.show_unverified = QCheckBox("Show unverified only")
        self.show_unverified.stateChanged.connect(self.filter_items)
        filter_layout.addWidget(self.show_unverified)

        layout.addWidget(filter_group)

        # Item list
        layout.addWidget(QLabel(f"Items ({len(self.item_list)}):"))
        self.item_list_widget = QListWidget()
        self.item_list_widget.currentItemChanged.connect(self.on_item_selected)
        layout.addWidget(self.item_list_widget)

        # Populate list
        self.filter_items()

        # Stats
        stats_label = QLabel()
        verified_count = len(self.verified_mappings)
        total_count = len(self.item_list)
        stats_label.setText(
            f"Verified: {verified_count} / {total_count} "
            f"({verified_count / total_count * 100:.1f}%)"
        )
        layout.addWidget(stats_label)
        self.stats_label = stats_label

        return panel

    def create_right_panel(self) -> QWidget:
        """Create right panel with icon details."""

        panel = QWidget()
        layout = QVBoxLayout(panel)

        # Item info
        info_group = QGroupBox("Item Information")
        info_layout = QVBoxLayout(info_group)

        self.item_info_label = QLabel("Select an item")
        self.item_info_label.setWordWrap(True)
        info_layout.addWidget(self.item_info_label)

        layout.addWidget(info_group)

        # Icon selection
        icons_group = QGroupBox("Icon Assignment")
        icons_layout = QVBoxLayout(icons_group)

        # For each icon index (1, 2, 3...)
        self.icon_selectors = {}

        for i in range(1, 4):  # Max 3 indices
            selector = self.create_icon_selector(i)
            icons_layout.addWidget(selector)
            self.icon_selectors[i] = selector

        layout.addWidget(icons_group)

        # Actions
        actions_layout = QHBoxLayout()

        save_btn = QPushButton("Save Verification")
        save_btn.clicked.connect(self.save_current_item)
        actions_layout.addWidget(save_btn)

        save_all_btn = QPushButton("Save All to File")
        save_all_btn.clicked.connect(self.save_verified_mappings)
        actions_layout.addWidget(save_all_btn)

        export_btn = QPushButton("Export Mappings")
        export_btn.clicked.connect(self.export_mappings)
        actions_layout.addWidget(export_btn)

        layout.addLayout(actions_layout)

        layout.addStretch()

        return panel

    def create_icon_selector(self, index: int) -> QGroupBox:
        """Create icon selector for a specific index."""

        group = QGroupBox(f"Icon Index {index}")
        layout = QVBoxLayout(group)

        # Handle label
        handle_label = QLabel("Handle:")
        layout.addWidget(handle_label)

        handle_value = QLabel("")
        handle_value.setWordWrap(True)
        layout.addWidget(handle_value)

        # Possible icons area
        icons_label = QLabel("Possible Icons:")
        layout.addWidget(icons_label)

        # Scroll area for icons
        icons_scroll = QScrollArea()
        icons_scroll.setWidgetResizable(True)
        icons_scroll.setMinimumHeight(100)
        icons_scroll.setMaximumHeight(200)

        icons_widget = QWidget()
        self.icons_layout = QGridLayout(icons_widget)
        icons_scroll.setWidget(icons_widget)
        layout.addWidget(icons_scroll)

        # Store widgets for later access
        group.handle_label = handle_value
        group.icons_layout = self.icons_layout
        group.icons_widget = icons_widget
        group.icons_scroll = icons_scroll
        group.possible_icons = []  # Store possible icon data
        group.selected_icon = None  # Store selected icon path
        group.setVisible(False)

        return group

    def filter_items(self):
        """Filter item list based on search and filters."""

        search_text = self.search_input.text().lower()
        show_verified = self.show_verified.isChecked()
        show_unverified = self.show_unverified.isChecked()

        self.item_list_widget.clear()

        for item in self.item_list:
            # Search filter
            if search_text:
                if (
                    search_text not in str(item["id"]).lower()
                    and search_text not in str(item["name"]).lower()
                ):
                    continue

            # Verification filter
            item_id_str = str(item["id"])
            is_verified = item_id_str in self.verified_mappings

            if show_verified and not is_verified:
                continue
            if show_unverified and is_verified:
                continue

            # Add to list
            icon_text = "✓ " if is_verified else "  "
            list_item = QListWidgetItem(f"{icon_text}[{item['id']}] {item['name']}")
            list_item.setData(Qt.ItemDataRole.UserRole, item)
            self.item_list_widget.addItem(list_item)

    def on_item_selected(self, current: QListWidgetItem, previous: QListWidgetItem):
        """Handle item selection."""

        if not current:
            return

        item = current.data(Qt.ItemDataRole.UserRole)
        self.current_item_id = item["id"]

        # Update info label
        info_text = f"<b>Item ID:</b> {item['id']}<br>"
        info_text += f"<b>Name:</b> {item['name']}<br>"
        info_text += f"<b>Icon Count:</b> {len(item['icons'])}"
        self.item_info_label.setText(info_text)

        # Update icon selectors
        for i, icon_data in enumerate(item["icons"], 1):
            if i in self.icon_selectors:
                selector = self.icon_selectors[i]
                selector.setVisible(True)

                # Update handle
                selector.handle_label.setText(icon_data["handle"])

                # Clear previous icons
                for j in reversed(range(selector.icons_layout.count())):
                    widget = selector.icons_layout.itemAt(j).widget()
                    if widget:
                        widget.setParent(None)

                # Get possible icons from detailed mapping
                detailed_key = f"{item['id']}_{i}"
                possible_icons = []

                if detailed_key in self.mapping.get("detailed_mapping", {}):
                    possible_icons = self.mapping["detailed_mapping"][detailed_key].get(
                        "possible_icons", []
                    )

                # Store possible icons for this selector
                selector.possible_icons = possible_icons

                # Display all possible icons
                for idx, icon_info in enumerate(possible_icons):
                    # Create button for each icon
                    icon_button = QPushButton()
                    icon_button.setFixedSize(64, 64)
                    icon_button.setIconSize(QSize(64, 64))
                    icon_button.setCheckable(True)

                    # Load icon
                    icon_path = self.icons_root / icon_info["path"]
                    if icon_path.exists():
                        pixmap = QPixmap(str(icon_path))
                        if not pixmap.isNull():
                            icon_button.setIcon(QIcon(pixmap))

                    # Store icon info with button
                    icon_button.setProperty("icon_path", icon_info["path"])
                    icon_button.setProperty("atlas", icon_info["atlas"])
                    icon_button.clicked.connect(
                        lambda checked,
                        btn=icon_button,
                        sel=selector: self.on_icon_selected(btn, sel)
                    )

                    # Add to layout (4 icons per row)
                    row = idx // 4
                    col = idx % 4
                    selector.icons_layout.addWidget(icon_button, row, col)

                # Check if this item/icon combination was already verified
                item_id_str = str(item["id"])
                if (
                    item_id_str in self.verified_mappings
                    and str(i) in self.verified_mappings[item_id_str]
                ):
                    verified_path = self.verified_mappings[item_id_str][str(i)]
                    # Find and select the verified icon
                    for j in range(selector.icons_layout.count()):
                        widget = selector.icons_layout.itemAt(j).widget()
                        if (
                            widget
                            and hasattr(widget, "property")
                            and widget.property("icon_path") == verified_path
                        ):
                            widget.setChecked(True)
                            selector.selected_icon = verified_path
                            break

        # Hide unused selectors
        for i in range(len(item["icons"]) + 1, 4):
            if i in self.icon_selectors:
                self.icon_selectors[i].setVisible(False)

        self.statusBar().showMessage(f"Viewing item {item['id']}: {item['name']}")

    def update_icon_preview(self, index: int):
        """Update icon preview for given index."""

        if index not in self.icon_selectors:
            return

        selector = self.icon_selectors[index]
        atlas_num = selector.atlas_combo.currentData()

        if atlas_num is None:
            return

        # Get current item
        current = self.item_list_widget.currentItem()
        if not current:
            return

        item = current.data(Qt.ItemDataRole.UserRole)

        # Get icon data for this index
        icon_data = None
        for ic in item["icons"]:
            if ic["index"] == index:
                icon_data = ic
                break

        if not icon_data:
            return

        # Determine category
        category = (
            "item"
            if icon_data["handle"].startswith("ui_item_")
            else "spell"
            if icon_data["handle"].startswith("ui_spell_")
            else "other"
        )

        # Build icon path
        icon_path = (
            self.icons_root / category / f"atlas_{atlas_num}" / f"icon_{index:03d}.png"
        )

        # Load and display
        if icon_path.exists():
            pixmap = QPixmap(str(icon_path))
            if not pixmap.isNull():
                # Scale to 64x64
                scaled = pixmap.scaled(
                    64,
                    64,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.FastTransformation,
                )
                selector.icon_preview.setPixmap(scaled)

                # Check if empty
                key = f"{category}_{atlas_num}_{index:03d}"
                is_empty = False

                if key in self.icon_index.get("icons", {}):
                    icon_info = self.icon_index["icons"][key]
                    is_empty = icon_info.get("is_empty", False)

                if is_empty:
                    selector.icon_preview.setStyleSheet(
                        "border: 2px solid red; background: white;"
                    )
                else:
                    selector.icon_preview.setStyleSheet(
                        "border: 1px solid #ccc; background: white;"
                    )
            else:
                selector.icon_preview.setText("Invalid")
        else:
            selector.icon_preview.setText("Not found")

    def on_icon_selected(self, button, selector):
        """Handle icon selection."""
        # Uncheck all other buttons in this selector
        for i in range(selector.icons_layout.count()):
            widget = selector.icons_layout.itemAt(i).widget()
            if widget and isinstance(widget, QPushButton) and widget != button:
                widget.setChecked(False)

        # Store selected icon path
        if button.isChecked():
            selector.selected_icon = button.property("icon_path")
        else:
            selector.selected_icon = None

    def save_current_item(self):
        """Save verification for current item."""

        if self.current_item_id is None:
            return

        item_id_str = str(self.current_item_id)

        # Get current selections
        selections = {}

        current = self.item_list_widget.currentItem()
        if not current:
            return

        item = current.data(Qt.ItemDataRole.UserRole)

        for i, icon_data in enumerate(item["icons"], 1):
            if i in self.icon_selectors and self.icon_selectors[i].isVisible():
                selector = self.icon_selectors[i]

                # Save selected icon if any
                if selector.selected_icon:
                    selections[str(i)] = selector.selected_icon

        # Save to verified mappings
        self.verified_mappings[item_id_str] = selections

        # Update UI
        self.filter_items()
        self.update_stats()

        self.statusBar().showMessage(
            f"Saved verification for item {self.current_item_id}"
        )

    def update_stats(self):
        """Update statistics label."""

        verified_count = len(self.verified_mappings)
        total_count = len(self.item_list)
        self.stats_label.setText(
            f"Verified: {verified_count} / {total_count} "
            f"({verified_count / total_count * 100:.1f}%)"
        )

    def export_mappings(self):
        """Export verified mappings to file."""

        filename, _ = QFileDialog.getSaveFileName(
            self,
            "Export Mappings",
            str(
                self.project_root
                / "src"
                / "TirganachReloaded"
                / "data"
                / "verified_icon_mappings.json"
            ),
            "JSON Files (*.json)",
        )

        if filename:
            with open(filename, "w") as f:
                json.dump(self.verified_mappings, f, indent=2)

            QMessageBox.information(
                self, "Exported", f"Mappings exported to:\n{filename}"
            )


def main():
    """Run the interactive mapper."""

    app = QApplication(sys.argv)
    window = IconMapperWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
