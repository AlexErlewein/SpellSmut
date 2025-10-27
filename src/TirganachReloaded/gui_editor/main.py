#!/usr/bin/env python3
"""
SpellForce CFF Editor - Main Entry Point
========================================

GUI application for editing SpellForce GameData.cff files.
Built with PySide6 for professional, native look.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QSplitter, QTreeWidget, QTreeWidgetItem, QTableWidget, QTableWidgetItem, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QFileDialog, QMessageBox, QProgressBar, QStatusBar, QLineEdit
    from PySide6.QtCore import Qt, QThread, Signal
    from PySide6.QtGui import QAction, QIcon, QColor, QPalette
except ImportError:
    print("Error: PySide6 not installed. Run: pip install PySide6")
    sys.exit(1)

from tirganach import GameData


class CFFLoaderThread(QThread):
    """Background thread for loading CFF files"""
    progress_updated = Signal(int, str)
    loading_finished = Signal(object)
    loading_error = Signal(str)

    def __init__(self, cff_path):
        super().__init__()
        self.cff_path = cff_path

    def run(self):
        try:
            self.progress_updated.emit(10, "Initializing...")
            gd = GameData(self.cff_path)
            self.progress_updated.emit(100, "Complete!")
            self.loading_finished.emit(gd)
        except Exception as e:
            self.loading_error.emit(str(e))


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.game_data = None
        self.modified = False
        self.current_category = None
        self.all_elements = []
        self.filtered_elements = []
        self.current_page = 0
        self.page_size = 50

        self.setWindowTitle("SpellForce CFF Editor")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QHBoxLayout(central_widget)

        # Left panel: Category tree
        self.category_tree = QTreeWidget()
        self.category_tree.setHeaderLabel("Categories")
        self.category_tree.itemClicked.connect(self.on_category_selected)
        layout.addWidget(self.category_tree, 1)

        # Center panel: Element table with search
        center_widget = QWidget()
        center_layout = QVBoxLayout(center_widget)

        # Search box
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search elements...")
        self.search_box.textChanged.connect(self.filter_elements)
        center_layout.addWidget(self.search_box)

        # Element table
        self.element_table = QTableWidget()
        self.element_table.setColumnCount(3)
        self.element_table.setHorizontalHeaderLabels(["ID", "Name", "Type"])
        self.element_table.itemClicked.connect(self.on_element_selected)
        center_layout.addWidget(self.element_table)

        # Pagination controls
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)

        self.prev_button = QPushButton("Previous")
        self.prev_button.clicked.connect(self.previous_page)
        self.prev_button.setEnabled(False)
        pagination_layout.addWidget(self.prev_button)

        self.page_label = QLabel("Page 1 of 1")
        pagination_layout.addWidget(self.page_label)

        self.next_button = QPushButton("Next")
        self.next_button.clicked.connect(self.next_page)
        self.next_button.setEnabled(False)
        pagination_layout.addWidget(self.next_button)

        center_layout.addWidget(pagination_widget)

        layout.addWidget(center_widget, 2)

        # Right panel: Properties
        self.properties_widget = QWidget()
        properties_layout = QVBoxLayout(self.properties_widget)
        properties_layout.addWidget(QLabel("Properties"))
        properties_layout.addStretch()
        layout.addWidget(self.properties_widget, 1)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_bar.addWidget(self.progress_bar)

        # Menu bar
        self.create_menu_bar()

        # Load initial data if file exists
        self.load_initial_file()

    def create_menu_bar(self):
        """Create the menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        # View menu
        view_menu = menubar.addMenu("View")

        # Tools menu
        tools_menu = menubar.addMenu("Tools")

        load_weapons_action = QAction("Load Weapon Data", self)
        load_weapons_action.triggered.connect(self.load_weapon_data)
        tools_menu.addAction(load_weapons_action)

    def load_initial_file(self):
        """Load the default CFF file if it exists"""
        default_path = Path(__file__).parent.parent / "OriginalGameFiles" / "data" / "GameData.cff"
        if default_path.exists():
            self.load_cff_file(str(default_path))

    def open_file(self):
        """Open a CFF file dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open CFF File", "", "CFF Files (*.cff)"
        )
        if file_path:
            self.load_cff_file(file_path)

    def load_cff_file(self, file_path):
        """Load a CFF file in background thread"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)

        self.loader_thread = CFFLoaderThread(file_path)
        self.loader_thread.progress_updated.connect(self.update_progress)
        self.loader_thread.loading_finished.connect(self.on_loading_finished)
        self.loader_thread.loading_error.connect(self.on_loading_error)
        self.loader_thread.start()

    def update_progress(self, value, message):
        """Update progress bar"""
        self.progress_bar.setValue(value)
        self.status_bar.showMessage(message)

    def on_loading_finished(self, game_data):
        """Handle successful loading"""
        self.game_data = game_data
        self.progress_bar.setVisible(False)
        self.status_bar.showMessage(f"Loaded {len(game_data.items)} items")
        self.populate_category_tree()
        self.load_weapon_data()  # Auto-load weapon data
        self.modified = False

    def on_loading_error(self, error):
        """Handle loading error"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Loading Error", f"Failed to load CFF file:\n{error}")

    def populate_category_tree(self):
        """Populate the category tree with loaded data"""
        self.category_tree.clear()

        if not self.game_data:
            return

        categories = [
            ("Items", len(self.game_data.items)),
            ("Spells", len(self.game_data.spells)),
            ("Creatures", len(self.game_data.creatures)),
            ("Buildings", len(self.game_data.buildings)),
            ("Armor", len(self.game_data.armor)),
            ("Weapons", len(self.game_data.weapons)),
            ("Localization", len(self.game_data.localisation)),
        ]

        for name, count in categories:
            item = QTreeWidgetItem([f"{name} ({count})"])
            item.setData(0, Qt.UserRole, name.lower())
            self.category_tree.addTopLevelItem(item)

    def on_category_selected(self, item, column):
        """Handle category selection"""
        category = item.data(0, Qt.UserRole)
        self.populate_element_table(category)

    def populate_element_table(self, category):
        """Populate the element table for selected category with pagination"""
        if not self.game_data:
            return

        self.current_category = category
        self.current_page = 0

        # Get data for category
        if category == "items":
            self.all_elements = self.game_data.items
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Name", "Type"])
        elif category == "spells":
            self.all_elements = self.game_data.spells
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Name", "School"])
        elif category == "creatures":
            self.all_elements = self.game_data.creatures
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Name", "Race"])
        elif category == "buildings":
            self.all_elements = self.game_data.buildings
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Name", "Race"])
        elif category == "armor":
            self.all_elements = self.game_data.armor
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Name", "Type"])
        elif category == "weapons":
            self.all_elements = self.game_data.weapons
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Name", "Type"])
        elif category == "localization":
            self.all_elements = self.game_data.localisation[:1000]  # Limit for performance
            self.element_table.setColumnCount(3)
            self.element_table.setHorizontalHeaderLabels(["ID", "Language", "Text"])
        else:
            return

        # Apply initial filter
        self.filter_elements()
        self.update_pagination()

    def save_file(self):
        """Save the CFF file"""
        if not self.game_data:
            return

        # TODO: Implement save functionality
        QMessageBox.information(self, "Save", "Save functionality not yet implemented")

    def filter_elements(self):
        """Filter elements based on search text"""
        search_text = self.search_box.text().lower()
        if not search_text:
            self.filtered_elements = self.all_elements
        else:
            self.filtered_elements = []
            for item in self.all_elements:
                # Simple search in string representation
                if search_text in str(item).lower():
                    self.filtered_elements.append(item)

        self.current_page = 0
        self.update_pagination()

    def update_pagination(self):
        """Update the table with current page data"""
        total_elements = len(self.filtered_elements)
        total_pages = (total_elements + self.page_size - 1) // self.page_size

        # Update page label
        if total_pages == 0:
            self.page_label.setText("No results")
        else:
            self.page_label.setText(f"Page {self.current_page + 1} of {total_pages}")

        # Update navigation buttons
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < total_pages - 1)

        # Calculate slice for current page
        start_idx = self.current_page * self.page_size
        end_idx = min(start_idx + self.page_size, total_elements)

        # Populate table
        self.element_table.setRowCount(end_idx - start_idx)
        for row, item in enumerate(self.filtered_elements[start_idx:end_idx]):
            if self.current_category == "items":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.item_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem("Item Name"))  # TODO: Resolve
                self.element_table.setItem(row, 2, QTableWidgetItem(str(item.item_type)))
            elif self.current_category == "spells":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.spell_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem("Spell Name"))  # TODO: Resolve
                self.element_table.setItem(row, 2, QTableWidgetItem("School"))  # TODO: Resolve
            elif self.current_category == "creatures":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.creature_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem("Creature Name"))  # TODO: Resolve
                self.element_table.setItem(row, 2, QTableWidgetItem("Race"))  # TODO: Resolve
            elif self.current_category == "buildings":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.building_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem("Building Name"))  # TODO: Resolve
                self.element_table.setItem(row, 2, QTableWidgetItem("Race"))  # TODO: Resolve
            elif self.current_category == "armor":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.item_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem("Armor Name"))  # TODO: Resolve
                self.element_table.setItem(row, 2, QTableWidgetItem("Type"))  # TODO: Resolve
            elif self.current_category == "weapons":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.item_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem("Weapon Name"))  # TODO: Resolve
                self.element_table.setItem(row, 2, QTableWidgetItem(str(item.weapon_type)))
            elif self.current_category == "localization":
                self.element_table.setItem(row, 0, QTableWidgetItem(str(item.text_id)))
                self.element_table.setItem(row, 1, QTableWidgetItem(str(item.language)))
                self.element_table.setItem(row, 2, QTableWidgetItem(item.text[:50]))

    def previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self.update_pagination()

    def next_page(self):
        """Go to next page"""
        total_pages = (len(self.filtered_elements) + self.page_size - 1) // self.page_size
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self.update_pagination()

    def on_element_selected(self, item):
        """Handle element selection for details view"""
        row = item.row()
        start_idx = self.current_page * self.page_size
        element = self.filtered_elements[start_idx + row]
        self.show_element_details(element)

    def show_element_details(self, element):
        """Show element details in properties panel"""
        # Clear previous details
        # TODO: Implement detailed property view
        self.status_bar.showMessage(f"Selected element: {element}")

    def load_weapon_data(self):
        """Load and display weapon data from JSON or dynamically"""
        import json
        from pathlib import Path

        # Try to load from JSON first
        weapons_file = Path(__file__).parent.parent / "enhanced_weapons.json"
        if weapons_file.exists():
            try:
                with open(weapons_file, 'r', encoding='utf-8') as f:
                    weapons = json.load(f)

                # Switch to weapons category and populate
                self.populate_element_table("weapons")
                self.element_table.setRowCount(len(weapons))
                for row, weapon in enumerate(weapons):
                    self.element_table.setItem(row, 0, QTableWidgetItem(str(weapon['item_id'])))
                    self.element_table.setItem(row, 1, QTableWidgetItem(weapon['name']))
                    self.element_table.setItem(row, 2, QTableWidgetItem(weapon['weapon_type_name']))

                self.status_bar.showMessage(f"Loaded {len(weapons)} weapons from JSON")
                return
            except Exception as e:
                QMessageBox.warning(self, "JSON Load Error", f"Failed to load JSON: {str(e)}\nFalling back to dynamic loading.")

        # Fallback: Load dynamically from CFF
        if self.game_data:
            self.populate_element_table("weapons")
            self.status_bar.showMessage(f"Loaded {len(self.game_data.weapons)} weapons from CFF")
        else:
            QMessageBox.warning(self, "No Data", "No game data loaded")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    # Set dark theme (optional)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()