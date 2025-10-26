"""
Main Window for CFF Editor
"""

from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                                QSplitter, QMenuBar, QMenu, QFileDialog,
                                QMessageBox, QStatusBar, QLabel)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QActionGroup
from pathlib import Path

from .data_model import CFFDataModel
from tirganach.types import Language
from .widgets.category_tree import CategoryTreeWidget
from .widgets.element_table import ElementTableWidget
from .widgets.property_editor import PropertyEditorWidget
from .widgets.quest_details import QuestDetailsWidget


class MainWindow(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("SpellForce GameData.cff Editor")
        self.setMinimumSize(QSize(1200, 700))

        # Data model
        self.data_model = CFFDataModel()

        # Setup UI
        self.setup_ui()
        self.setup_menu()
        self.setup_statusbar()
        self.setup_connections()

        # Apply dark theme
        self.apply_dark_theme()

        # Auto-load default file
        self.auto_load_default_file()

    def auto_load_default_file(self):
        """Automatically load the default file on startup"""
        default_file = self.data_model.get_default_file_path()
        if default_file and Path(default_file).exists():
            self.statusBar.showMessage("Loading default file...")
            if self.data_model.load_file(default_file):
                self.statusBar.showMessage("Default file loaded successfully", 3000)
            else:
                self.statusBar.showMessage("Failed to load default file", 3000)

    def setup_ui(self):
        """Setup the main UI layout"""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter for 3-panel layout
        splitter = QSplitter(Qt.Horizontal)

        # Left panel - Category tree
        self.category_tree = CategoryTreeWidget(self.data_model)
        splitter.addWidget(self.category_tree)

        # Center panel - Element table
        self.element_table = ElementTableWidget(self.data_model)
        splitter.addWidget(self.element_table)

        # Right panel - Property editor
        self.property_editor = PropertyEditorWidget(self.data_model)
        splitter.addWidget(self.property_editor)

        # 4th panel - Quest details (initially hidden)
        self.quest_details = QuestDetailsWidget(self.data_model)
        self.quest_details.hide()  # Hidden by default
        self.quest_details.setMinimumWidth(150)  # Ensure minimum width when visible
        splitter.addWidget(self.quest_details)

        # Set initial sizes (20%, 35%, 30%, 15%)
        splitter.setSizes([250, 400, 350, 150])

        main_layout.addWidget(splitter)

    def setup_menu(self):
        """Setup menu bar"""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("&Open CFF...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("&Save", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        save_as_action = QAction("Save &As...", self)
        save_as_action.setShortcut("Ctrl+Shift+S")
        save_as_action.triggered.connect(self.save_file_as)
        file_menu.addAction(save_as_action)

        file_menu.addSeparator()

        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = menubar.addMenu("&Edit")

        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_view)
        edit_menu.addAction(refresh_action)

        # Language menu
        language_menu = menubar.addMenu("&Language")
        self._setup_language_menu(language_menu)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def _setup_language_menu(self, language_menu):
        """Setup language selection menu"""
        # Language options
        languages = [
            ("&German", Language.GERMAN),
            ("&English", Language.ENGLISH),
            ("&French", Language.FRENCH),
            ("&Spanish", Language.SPANISH),
            ("&Italian", Language.ITALIAN),
            ("&_HAEGAR", Language._HAEGAR)
        ]

        # Create action group for radio button behavior
        language_group = QActionGroup(self)
        language_group.setExclusive(True)

        for lang_name, lang_enum in languages:
            action = QAction(lang_name, self)
            action.setCheckable(True)
            action.setChecked(self.data_model.get_current_language() == lang_enum)
            action.triggered.connect(lambda checked, lang=lang_enum: self._on_language_selected(lang))
            language_menu.addAction(action)
            language_group.addAction(action)

    def _on_language_selected(self, language: Language):
        """Handle language selection"""
        self.data_model.set_current_language(language)
        self.statusBar.showMessage(f"Language changed to {language.name}", 2000)
        self.refresh_view()

    def setup_statusbar(self):
        """Setup status bar"""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # File path label
        self.file_label = QLabel("No file loaded")
        self.statusBar.addWidget(self.file_label)

        # Modified indicator
        self.modified_label = QLabel("")
        self.statusBar.addPermanentWidget(self.modified_label)

        # Stats label
        self.stats_label = QLabel("")
        self.statusBar.addPermanentWidget(self.stats_label)

    def setup_connections(self):
        """Setup signal/slot connections"""
        self.data_model.data_loaded.connect(self.on_data_loaded)
        self.data_model.data_modified.connect(self.on_data_modified)
        self.data_model.category_changed.connect(self.on_category_changed)
        self.data_model.language_changed.connect(self.on_language_changed)

    def open_file(self):
        """Open CFF file dialog"""
        # Get default directory (last opened file's directory or fallback)
        default_file = self.data_model.get_default_file_path()
        default_dir = str(Path(default_file).parent) if default_file else "H:/SpellSmut/OriginalGameFiles/data"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open GameData.cff",
            default_dir,
            "CFF Files (*.cff);;All Files (*)"
        )

        if file_path:
            self.statusBar.showMessage("Loading file...")
            if self.data_model.load_file(file_path):
                self.statusBar.showMessage("File loaded successfully", 3000)
            else:
                QMessageBox.critical(self, "Error", "Failed to load CFF file")
                self.statusBar.showMessage("Failed to load file", 3000)

    def save_file(self):
        """Save current file"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return

        if self.data_model.save_file():
            self.statusBar.showMessage("File saved successfully", 3000)
            self.update_status()
        else:
            QMessageBox.critical(self, "Error", "Failed to save file")

    def save_file_as(self):
        """Save as new file"""
        if not self.data_model.game_data:
            QMessageBox.warning(self, "Warning", "No file loaded")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save GameData.cff As",
            "H:/SpellSmut/ModdedGameFiles",
            "CFF Files (*.cff);;All Files (*)"
        )

        if file_path:
            if self.data_model.save_file(file_path):
                self.statusBar.showMessage("File saved successfully", 3000)
                self.update_status()
            else:
                QMessageBox.critical(self, "Error", "Failed to save file")

    def refresh_view(self):
        """Refresh the current view"""
        self.category_tree.refresh()
        self.element_table.refresh()
        self.property_editor.refresh()
        self.quest_details.update_quest_details()  # Refresh quest details if visible

    def on_data_loaded(self):
        """Called when data is loaded"""
        self.category_tree.populate()
        self.update_status()
        self.statusBar.showMessage("Data loaded successfully", 3000)

    def on_data_modified(self):
        """Called when data is modified"""
        self.update_status()

    def on_category_changed(self, category):
        """Called when category changes"""
        # Show/hide quest details panel based on category
        if category == "quests":
            self.quest_details.show()
            # Adjust splitter sizes to accommodate 4th panel
            self.adjust_splitter_for_quests()
        else:
            self.quest_details.hide()
            # Reset to 3-panel layout
            self.adjust_splitter_for_normal()

    def on_language_changed(self, language):
        """Called when language changes"""
        # Refresh all views to show text in new language
        self.refresh_view()

    def adjust_splitter_for_quests(self):
        """Adjust splitter sizes when showing quest details"""
        # Find the splitter containing our widgets
        for child in self.findChildren(QSplitter):
            if self.category_tree in [child.widget(i) for i in range(child.count())]:
                # Set sizes: categories, elements, properties, quest details
                child.setSizes([200, 350, 300, 200])
                break

    def adjust_splitter_for_normal(self):
        """Adjust splitter sizes for normal 3-panel layout"""
        # Find the splitter containing our widgets
        for child in self.findChildren(QSplitter):
            if self.category_tree in [child.widget(i) for i in range(child.count())]:
                # Set sizes: categories, elements, properties (hide quest details)
                child.setSizes([250, 400, 400, 0])
                break

    def update_status(self):
        """Update status bar"""
        if self.data_model.file_path:
            self.file_label.setText(f"File: {self.data_model.file_path}")
        else:
            self.file_label.setText("No file loaded")

        if self.data_model.is_modified():
            self.modified_label.setText("Modified")
            self.modified_label.setStyleSheet("color: orange;")
        else:
            self.modified_label.setText("")

        # Show category stats
        if self.data_model.current_category:
            elements = self.data_model.get_elements(self.data_model.current_category)
            self.stats_label.setText(f"{len(elements)} entries")
        else:
            self.stats_label.setText("")

    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About CFF Editor",
            "<h3>SpellForce GameData.cff Editor</h3>"
            "<p>Version 1.0.0</p>"
            "<p>A modern GUI editor for SpellForce Platinum Edition game data files.</p>"
            "<p>Built with PySide6 and the tirganach library.</p>"
        )

    def closeEvent(self, event):
        """Handle window close event"""
        if self.data_model.is_modified():
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before exiting?",
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
            )

            if reply == QMessageBox.Save:
                self.save_file()
                event.accept()
            elif reply == QMessageBox.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def apply_dark_theme(self):
        """Apply dark theme to the application"""
        dark_stylesheet = """
        QMainWindow {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QWidget {
            background-color: #2b2b2b;
            color: #ffffff;
        }
        QTreeWidget {
            background-color: #353535;
            border: 1px solid #555555;
            alternate-background-color: #3a3a3a;
        }
        QTreeWidget::item:selected {
            background-color: #0d47a1;
        }
        QTreeWidget::item:hover {
            background-color: #404040;
        }
        QTableWidget {
            background-color: #353535;
            border: 1px solid #555555;
            gridline-color: #555555;
            alternate-background-color: #3a3a3a;
        }
        QTableWidget::item:selected {
            background-color: #0d47a1;
        }
        QHeaderView::section {
            background-color: #404040;
            color: #ffffff;
            border: 1px solid #555555;
            padding: 4px;
        }
        QLineEdit, QSpinBox, QComboBox {
            background-color: #353535;
            border: 1px solid #555555;
            padding: 4px;
            color: #ffffff;
        }
        QPushButton {
            background-color: #0d47a1;
            border: none;
            padding: 6px 12px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #1565c0;
        }
        QPushButton:disabled {
            background-color: #555555;
            color: #888888;
        }
        QMenuBar {
            background-color: #353535;
            color: #ffffff;
        }
        QMenuBar::item:selected {
            background-color: #0d47a1;
        }
        QMenu {
            background-color: #353535;
            color: #ffffff;
            border: 1px solid #555555;
        }
        QMenu::item:selected {
            background-color: #0d47a1;
        }
        QStatusBar {
            background-color: #353535;
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_stylesheet)
