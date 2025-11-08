#!/usr/bin/env python3
"""
Enhanced Quest Creation System Launcher (Final Fixed Paths)

This script launches complete enhanced quest creation system with:
- Quest creation wizard
- Visual dialogue editor
- Reward builder with item browser
- Quest validation
- Direct CFF integration

Usage:
    python launch_enhanced_quest_creator.py [--debug]
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, Any

# Fix path calculation - go from widgets to project root properly
script_path = Path(__file__).resolve()
widgets_dir = script_path.parent
# widgets -> cff_editor -> TirganachReloaded -> src -> quest-wizard
src_dir = widgets_dir.parent.parent.parent
project_root = src_dir.parent

sys.path.insert(0, str(src_dir))

# Absolute path to CFF file (relative to actual project root)
CFF_ABSOLUTE_PATH = Path("/Users/alex/Desktop/code/Others/SpellSmut-worktrees/quest-wizard/OriginalGameFiles/data/GameData.cff")
CFF_RELATIVE_PATH = "OriginalGameFiles/data/GameData.cff"

print(f"DEBUG: Script path: {script_path}")
print(f"DEBUG: Widgets dir: {widgets_dir}")
print(f"DEBUG: Src dir: {src_dir}")
print(f"DEBUG: Project root: {project_root}")

try:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QVBoxLayout, QHBoxLayout,
        QWidget, QPushButton, QLabel, QMessageBox, QStatusBar, QDialog
    )
    from PySide6.QtCore import Qt, Signal, QTimer
    from PySide6.QtGui import QFont, QPixmap
except ImportError as e:
    print(f"Error: PySide6 not found: {e}")
    print("Please install PySide6: pip install PySide6")
    sys.exit(1)

from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.logging_config import configure_logging, get_logger

# Import wizard with error handling
try:
    from TirganachReloaded.cff_editor.widgets.enhanced_quest_creation_wizard import EnhancedQuestCreationWizard
    WIZARD_AVAILABLE = True
    print("✓ Enhanced quest creation wizard available")
except ImportError as e:
    print(f"⚠ Enhanced wizard not available: {e}")
    WIZARD_AVAILABLE = False
    EnhancedQuestCreationWizard = None


class QuestCreationLauncher(QMainWindow):
    """Main launcher window for enhanced quest creation system"""
    
    def __init__(self):
        super().__init__()
        self.logger = None
        self.data_model = None
        self.quest_data = {}
        
        print(f"DEBUG: Initializing launcher...")
        
        self._setup_ui()
        self._load_data()
    
    def _setup_ui(self):
        """Setup main launcher UI"""
        self.setWindowTitle("Enhanced Quest Creation System")
        self.setMinimumSize(800, 600)
        
        print("DEBUG: Setting up UI...")
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(50, 50, 50, 50)
        
        # Title
        title_label = QLabel("Enhanced Quest Creation System")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(
            "Create complete quests with visual dialogue editor, reward builder,\n"
            "and direct GameData.cff integration."
        )
        desc_label.setFont(QFont("Arial", 12))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: #7f8c8d; margin-bottom: 30px;")
        layout.addWidget(desc_label)
        
        # Path info for debugging
        path_info = QLabel(
            f"Project Root: {project_root}\n"
            f"CFF Path (Absolute): {CFF_ABSOLUTE_PATH}\n"
            f"CFF Path (Relative): {CFF_RELATIVE_PATH}\n"
            f"CFF Exists: {'✓' if CFF_ABSOLUTE_PATH.exists() else '✗'}\n"
            f"Wizard Available: {'✓' if WIZARD_AVAILABLE else '✗'}"
        )
        path_info.setFont(QFont("Courier", 9))
        path_info.setAlignment(Qt.AlignLeft)
        path_info.setStyleSheet("color: #34495e; background-color: #ecf0f1; padding: 10px; margin-bottom: 20px;")
        layout.addWidget(path_info)
        
        # Launch button
        self.launch_btn = QPushButton("Launch Quest Creation Wizard")
        self.launch_btn.setFont(QFont("Arial", 14, QFont.Bold))
        self.launch_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #3498db;"
            "   color: white;"
            "   border: none;"
            "   padding: 15px 30px;"
            "   border-radius: 8px;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #2980b9;"
            "}"
            "QPushButton:disabled {"
            "   background-color: #bdc3c7;"
            "}"
        )
        self.launch_btn.clicked.connect(self.launch_quest_wizard)
        self.launch_btn.setEnabled(False)  # Enable after data loads
        layout.addWidget(self.launch_btn)
        
        # Status label
        self.status_label = QLabel("Initializing...")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #e67e22; margin-top: 20px; font-style: italic;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Status bar
        self.statusBar().showMessage("Initializing...")
        
        print("DEBUG: UI setup completed")
    
    def _load_data(self):
        """Load required data in background"""
        try:
            print("DEBUG: Starting data loading...")
            
            # Configure logging
            configure_logging()
            self.logger = get_logger("quest_launcher")
            
            self.status_label.setText("Loading CFF data...")
            self.statusBar().showMessage("Loading CFF data...")
            QApplication.processEvents()
            
            # Initialize data model
            self.data_model = CFFDataModel()
            
            # Load CFF file using absolute path
            cff_file = CFF_ABSOLUTE_PATH
            print(f"DEBUG: Using CFF file: {cff_file}")
            
            if not cff_file.exists():
                self._show_error(
                    f"CFF file not found at:\n{cff_file}\n\n"
                    "Please ensure the CFF file exists at the specified path."
                )
                return
            
            print("DEBUG: Loading CFF file...")
            if not self.data_model.load_file(str(cff_file)):
                self._show_error("Failed to load GameData.cff file")
                return
            
            print("DEBUG: CFF file loaded successfully")
            
            # Load quest data
            self.status_label.setText("Loading quest data...")
            self.statusBar().showMessage("Loading quest data...")
            QApplication.processEvents()
            
            self._load_quest_data()
            
            # Success
            self.status_label.setText("Ready to create quests!")
            self.status_label.setStyleSheet("color: #27ae60; margin-top: 20px; font-style: italic;")
            
            if WIZARD_AVAILABLE:
                self.launch_btn.setEnabled(True)
            else:
                self.launch_btn.setText("Enhanced Wizard Not Available")
                self.launch_btn.setEnabled(False)
            
            self.statusBar().showMessage("Ready")
            
            print("DEBUG: Data loading completed successfully")
            
        except Exception as e:
            print(f"DEBUG: Error during data loading: {e}")
            try:
                self.logger.exception("Failed to load quest creation system")
            except:
                import traceback
                traceback.print_exc()
            self._show_error(f"Failed to load system:\n{str(e)}")
    
    def _load_quest_data(self):
        """Load existing quest data from CFF"""
        try:
            print("DEBUG: Loading quest data...")
            quests = self.data_model.get_elements("quests") or []
            self.quest_data = {}
            
            for quest in quests:
                quest_id = getattr(quest, 'quest_id', None)
                if quest_id is not None:
                    name = self.data_model.get_localised_text(quest, 'name')
                    if not name:
                        name = getattr(quest, 'name', f'Quest {quest_id}')
                    
                    self.quest_data[quest_id] = {
                        'name': name,
                        'description': getattr(quest, 'description', ''),
                        'quest_object': quest
                    }
            
            print(f"DEBUG: Loaded {len(self.quest_data)} existing quests")
            
            if self.logger:
                self.logger.info(f"Loaded {len(self.quest_data)} existing quests")
            
        except Exception as e:
            print(f"DEBUG: Error loading quest data: {e}")
            try:
                self.logger.exception("Failed to load quest data")
            except:
                import traceback
                traceback.print_exc()
            self.quest_data = {}
    
    def launch_quest_wizard(self):
        """Launch the enhanced quest creation wizard"""
        try:
            print("DEBUG: Launching quest wizard...")
            
            if not WIZARD_AVAILABLE or not EnhancedQuestCreationWizard:
                QMessageBox.warning(
                    self, "Wizard Not Available", 
                    "Enhanced quest creation wizard is not available.\n"
                    "Some components may be missing."
                )
                return
            
            # Create wizard
            wizard = EnhancedQuestCreationWizard(self.data_model, self.quest_data, self)
            
            # Connect signals
            wizard.quest_created.connect(self.on_quest_created)
            
            # Show wizard
            print("DEBUG: Showing wizard dialog...")
            result = wizard.exec()
            
            if result == QDialog.Accepted:
                self.statusBar().showMessage("Quest created successfully!")
            else:
                self.statusBar().showMessage("Ready")
                
        except Exception as e:
            print(f"DEBUG: Error launching wizard: {e}")
            try:
                self.logger.exception("Failed to launch quest wizard")
            except:
                import traceback
                traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to launch quest wizard:\n{str(e)}")
    
    def on_quest_created(self, quest_data: Dict):
        """Handle quest creation success"""
        quest_id = quest_data.get('quest_id', 'Unknown')
        quest_name = quest_data.get('name', 'Unknown')
        
        QMessageBox.information(
            self,
            "Quest Created!",
            f"Quest '{quest_name}' (ID: {quest_id}) has been created and saved successfully!\n\n"
            "The quest is now available in the game data."
        )
        
        # Refresh quest data to include new quest
        self._load_quest_data()
        
        self.statusBar().showMessage(f"Quest '{quest_name}' created successfully")
    
    def _show_error(self, message: str):
        """Show error message and disable launcher"""
        self.status_label.setText(f"Error: {message}")
        self.status_label.setStyleSheet("color: #e74c3c; margin-top: 20px; font-weight: bold;")
        self.launch_btn.setText("Cannot Launch - See Error Above")
        self.launch_btn.setEnabled(False)
        self.statusBar().showMessage("Error - Cannot launch")
        
        QMessageBox.critical(self, "Initialization Error", message)
    
    def closeEvent(self, event):
        """Handle application close"""
        if self.logger:
            self.logger.info("Enhanced quest creation system closed")
        
        # Clean up
        if self.data_model:
            # Any cleanup needed for data model
            pass
        
        super().closeEvent(event)


def main():
    """Main entry point"""
    print("DEBUG: Starting main function...")
    
    parser = argparse.ArgumentParser(description="Enhanced Quest Creation System Launcher")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    # Create application
    print("DEBUG: Creating Qt application...")
    app = QApplication(sys.argv)
    app.setApplicationName("Enhanced Quest Creation System")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("SpellSmut")
    
    # Configure debug logging if requested
    if args.debug:
        import logging
        logging.basicConfig(level=logging.DEBUG)
        print("Debug logging enabled")
    
    # Create and show launcher
    print("DEBUG: Creating launcher window...")
    launcher = QuestCreationLauncher()
    
    print("DEBUG: Showing launcher window...")
    launcher.show()
    
    # Force UI to show
    launcher.raise_()
    QApplication.processEvents()
    
    print("DEBUG: Starting Qt event loop...")
    # Run application
    return app.exec()


if __name__ == "__main__":
    try:
        print("DEBUG: Script started")
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)