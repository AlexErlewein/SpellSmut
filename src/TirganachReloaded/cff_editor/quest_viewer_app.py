#!/usr/bin/env python3
"""
Standalone Quest Viewer Application
===================================

A lightweight application for viewing SpellForce quest data.
Uses cached Lua files and triggers cache creation if needed.

Usage:
    python quest_viewer_app.py [--debug] [--rebuild-cache]
"""

import argparse
import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication, QMessageBox

# Add the src directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger
from TirganachReloaded.cff_editor.lua_parser.lua_data_manager import LuaDataManager
from TirganachReloaded.cff_editor.widgets.quest_details_viewer import QuestDetailsViewer
from TirganachReloaded.cff_editor.widgets.quest_hierarchy_tree import (
    QuestHierarchyTreeWidget,
)


class QuestViewerApp:
    """Main quest viewer application"""

    def __init__(self, project_root: Path, rebuild_cache: bool = False):
        self.project_root = project_root
        self.rebuild_cache = rebuild_cache
        self.logger = None

        # Initialize services
        self.data_model = None
        self.lua_manager = None

        # UI components
        self.main_window = None

    def initialize_services(self):
        """Initialize quest data services and cache management"""
        try:
            self.logger.info("Initializing quest data services...")

            # Initialize Lua data manager first (this handles cache creation)
            cache_dir = (
                self.project_root / "src" / "TirganachReloaded" / "data" / "cache"
            )
            self.lua_manager = LuaDataManager(cache_dir=cache_dir)

            # Check if we need to build cache
            if self.rebuild_cache or not self.lua_manager.cache_loaded:
                self.logger.info("Building quest cache...")
                self._build_quest_cache()

            # Initialize data model (this handles CFF data and quest service integration)
            self.data_model = CFFDataModel()

            # Try to load default quest data
            self._load_quest_data()

            self.logger.info("Quest data services initialized successfully")

        except Exception as e:
            self.logger.exception(f"Failed to initialize quest services: {e}")
            raise

    def _load_quest_data(self):
        """Load quest data from available sources"""
        try:
            # Load the default CFF file
            default_cff_path = self.data_model.get_default_file_path()
            if Path(default_cff_path).exists():
                self.logger.info(f"Loading CFF file: {default_cff_path}")
                self.data_model.load_file(default_cff_path)
                self.logger.info("CFF file loaded successfully")
            else:
                self.logger.error(f"CFF file not found: {default_cff_path}")
                raise FileNotFoundError(f"CFF file not found: {default_cff_path}")

        except Exception as e:
            self.logger.exception(f"Failed to load quest data: {e}")
            raise

    def _build_quest_cache(self):
        """Build quest cache from Lua files"""
        try:
            # Look for Lua files in common locations
            lua_paths = [
                self.project_root / "ModdingTools" / "SpellForceLUASources",
                self.project_root / "OriginalGameFiles" / "lua",
                # Add more paths as needed
            ]

            lua_source_path = None
            for path in lua_paths:
                if path.exists() and path.is_dir():
                    lua_source_path = path
                    break

            if lua_source_path:
                self.logger.info(f"Building cache from Lua files in: {lua_source_path}")
                self.lua_manager.build_cache_from_directory(lua_source_path)
                self.logger.info("Quest cache built successfully")
            else:
                self.logger.warning(
                    "No Lua source directory found. Cache will be empty."
                )

        except Exception as e:
            self.logger.exception(f"Failed to build quest cache: {e}")
            # Continue without cache - will use available data

    def create_ui(self):
        """Create the main UI"""
        from PySide6.QtCore import QSize, Qt
        from PySide6.QtWidgets import (
            QMainWindow,
            QSplitter,
            QVBoxLayout,
            QWidget,
        )

        class MainWindow(QMainWindow):
            def __init__(self, data_model: CFFDataModel):
                super().__init__()
                self.data_model = data_model
                self.setWindowTitle("TirganachReloaded: Quest Viewer")
                self.setMinimumSize(QSize(1200, 800))

                # Create central widget with splitter
                central_widget = QWidget()
                self.setCentralWidget(central_widget)

                layout = QVBoxLayout(central_widget)

                # Create horizontal splitter
                splitter = QSplitter(Qt.Horizontal)
                layout.addWidget(splitter)

                # Quest hierarchy tree (left)
                self.quest_tree = QuestHierarchyTreeWidget(self.data_model)
                self.quest_tree.setMaximumWidth(400)
                splitter.addWidget(self.quest_tree)

                # Quest details viewer (right)
                self.quest_details = QuestDetailsViewer(self.data_model)
                splitter.addWidget(self.quest_details)

                # Set splitter proportions
                splitter.setStretchFactor(0, 1)
                splitter.setStretchFactor(1, 3)

                # Load initial data
                self.load_data()

            def load_data(self):
                """Load quest data"""
                try:
                    # Show progress
                    from PySide6.QtWidgets import QProgressDialog

                    progress = QProgressDialog(
                        "Loading quest data...", None, 0, 0, self
                    )
                    progress.setWindowModality(Qt.WindowModal)
                    progress.show()

                    QApplication.processEvents()

                    # Load quest hierarchy
                    self.quest_tree.load_quests()

                    progress.close()

                    # Select first quest if available
                    quests = self.data_model.get_elements("quests")
                    if quests:
                        # Set current element index and emit signal
                        self.data_model.current_element_index = 0
                        self.data_model.element_selected.emit("quests", 0)

                except Exception as e:
                    QMessageBox.critical(
                        self, "Error", f"Failed to load quest data: {e}"
                    )

        self.main_window = MainWindow(self.data_model)

    def run(self):
        """Run the application"""
        # Configure logging
        configure_logging(project_root=self.project_root)
        self.logger = get_logger("quest_viewer")

        try:
            self.logger.info("Starting Quest Viewer Application")

            # Initialize services
            self.initialize_services()

            # Create Qt application
            app = QApplication(sys.argv)
            app.setApplicationName("TirganachReloaded Quest Viewer")
            app.setOrganizationName("SpellSmut Modding Tools")

            # Apply dark theme stylesheet
            app.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                }
                QMainWindow {
                    background-color: #2b2b2b;
                }
                QTreeWidget, QListWidget, QTextEdit {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    border: 1px solid #3c3c3c;
                    alternate-background-color: #252525;
                }
                QTreeWidget::item:selected, QListWidget::item:selected {
                    background-color: #094771;
                }
                QTreeWidget::item:hover, QListWidget::item:hover {
                    background-color: #2d2d30;
                }
                QGroupBox {
                    border: 1px solid #3c3c3c;
                    border-radius: 4px;
                    margin-top: 8px;
                    padding-top: 8px;
                    font-weight: bold;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px;
                }
                QLabel {
                    background-color: transparent;
                }
                QPushButton {
                    background-color: #3c3c3c;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                    padding: 5px 10px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #4a4a4a;
                }
                QPushButton:pressed {
                    background-color: #2a2a2a;
                }
                QScrollArea {
                    background-color: #2b2b2b;
                    border: none;
                }
                QHeaderView::section {
                    background-color: #3c3c3c;
                    color: #e0e0e0;
                    padding: 5px;
                    border: 1px solid #555555;
                }
                QSplitter::handle {
                    background-color: #3c3c3c;
                }
            """)

            # Create UI
            self.create_ui()

            # Show main window
            self.main_window.show()

            self.logger.info("Quest Viewer started successfully")

            # Run event loop
            return app.exec()

        except Exception as e:
            if self.logger:
                self.logger.exception(f"Application failed to start: {e}")
            else:
                print(f"Failed to start application: {e}")
            return 1


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="TirganachReloaded Quest Viewer")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument(
        "--rebuild-cache",
        action="store_true",
        help="Rebuild quest cache from Lua files",
    )

    args = parser.parse_args()

    # Get project root
    project_root = Path(__file__).parent.parent

    # Create and run application
    app = QuestViewerApp(project_root, rebuild_cache=args.rebuild_cache)
    return app.run()


if __name__ == "__main__":
    sys.exit(main())
