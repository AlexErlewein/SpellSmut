#!/usr/bin/env python3
"""
Test script for item browser system.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QLabel,
    QDialog,
)
from TirganachReloaded.cff_editor.widgets.item_browser_widget import ItemBrowserDialog
from TirganachReloaded.cff_editor.data_model import CFFDataModel


class TestItemBrowserWindow(QMainWindow):
    """Test window for item browser"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Item Browser Test")
        self.resize(900, 700)

        # Initialize data model
        self.data_model = CFFDataModel()
        cff_path = Path(__file__).parent / "OriginalGameFiles" / "data" / "GameData.cff"
        if cff_path.exists():
            self.data_model.load_file(str(cff_path))
            print(f"Loaded CFF data from {cff_path}")
        else:
            print(f"CFF file not found at {cff_path}, using sample data")

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Info label
        info_label = QLabel(
            "Test the comprehensive item browser with different categories:"
        )
        info_label.setStyleSheet("font-size: 12px; padding: 10px; color: #666;")
        layout.addWidget(info_label)

        # Buttons for different categories
        button_layout = QHBoxLayout()

        # General Items
        general_btn = QPushButton("Browse General Items")
        general_btn.clicked.connect(
            lambda: self.browse_items("General Items", ["General Items", "Consumables"])
        )
        button_layout.addWidget(general_btn)

        # Weapons
        weapons_btn = QPushButton("Browse Weapons")
        weapons_btn.clicked.connect(lambda: self.browse_items("Weapons", ["Weapons"]))
        button_layout.addWidget(weapons_btn)

        # Armor
        armor_btn = QPushButton("Browse Armor")
        armor_btn.clicked.connect(lambda: self.browse_items("Armor", ["Armor"]))
        button_layout.addWidget(armor_btn)

        # Creatures
        creatures_btn = QPushButton("Browse Creatures")
        creatures_btn.clicked.connect(
            lambda: self.browse_items("Creatures", ["Creatures/Enemies"])
        )
        button_layout.addWidget(creatures_btn)

        # Quest Items
        quest_btn = QPushButton("Browse Quest Items")
        quest_btn.clicked.connect(
            lambda: self.browse_items("Quest Items", ["Quest Items"])
        )
        button_layout.addWidget(quest_btn)

        # Materials
        materials_btn = QPushButton("Browse Materials")
        materials_btn.clicked.connect(
            lambda: self.browse_items("Materials", ["Materials"])
        )
        button_layout.addWidget(materials_btn)

        layout.addLayout(button_layout)

        # Status label
        self.status_label = QLabel("Ready to test item browser")
        self.status_label.setStyleSheet(
            "padding: 10px; font-style: italic; color: #666;"
        )
        layout.addWidget(self.status_label)

        layout.addStretch()

    def browse_items(self, title: str, categories: list):
        """Open item browser with specific categories"""
        print(f"DEBUG: Creating ItemBrowserDialog with data_model: {self.data_model}")
        dialog = ItemBrowserDialog(
            parent=self,
            title=f"Select {title}",
            categories=categories,
            data_model=self.data_model,
        )
        print(
            f"DEBUG: Dialog created, browser has {len(dialog.browser.items_data)} items"
        )

        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.get_selected_item()
            if selected:
                self.status_label.setText(
                    f"Selected: {selected.get('icon', '')} {selected.get('name', '')} "
                    f"(ID: {selected.get('id', 0)}, Type: {selected.get('type', '')})"
                )
                print(f"Selected item: {selected}")
            else:
                self.status_label.setText("No item selected")
        else:
            self.status_label.setText("Item browser cancelled")


if __name__ == "__main__":
    print("=" * 60)
    print("Item Browser Test")
    print("=" * 60)

    app = QApplication(sys.argv)

    window = TestItemBrowserWindow()
    window.show()

    print("\n=== Test Window Opened ===")
    print("You can now:")
    print("1. Browse different item categories")
    print("2. Search and filter items")
    print("3. View item details and stats")
    print("4. Test item selection")
    print("\nClose the window to exit.\n")

    sys.exit(app.exec())
