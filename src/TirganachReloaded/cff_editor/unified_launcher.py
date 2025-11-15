"""
Unified Creator Tools Launcher
Allows users to choose between different forge systems: Weapon Forge, Armor Forge, etc.
"""
import sys
from pathlib import Path

# Add the parent directory to the path so we can import from shared modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Try to import using relative paths first (when running as module)
try:
    from .shared.id_manager import IDManager, ContentType
    from .widgets.weapon_forge_wizard import WeaponForgeWizard
    from .widgets.armor_forge_wizard import ArmorForgeWizard
except ImportError:
    # Fallback to absolute imports (when running as script)
    try:
        from cff_editor.shared.id_manager import IDManager, ContentType
        from cff_editor.widgets.weapon_forge_wizard import WeaponForgeWizard
        from cff_editor.widgets.armor_forge_wizard import ArmorForgeWizard
    except ImportError:
        # Direct imports as last resort
        import sys
        from pathlib import Path
        sys.path.insert(0, str(Path(__file__).parent.parent.parent))
        from cff_editor.shared.id_manager import IDManager, ContentType
        from cff_editor.widgets.weapon_forge_wizard import WeaponForgeWizard
        from cff_editor.widgets.armor_forge_wizard import ArmorForgeWizard

try:
    from PySide6.QtWidgets import (
        QApplication, 
        QMainWindow, 
        QWidget, 
        QVBoxLayout, 
        QHBoxLayout, 
        QPushButton, 
        QLabel, 
        QFrame
    )
    from PySide6.QtCore import Qt
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


def run_unified_launcher():
    """Run the unified launcher for all creator tools"""
    if not GUI_AVAILABLE:
        print("PySide6 not available. Running in CLI mode...")
        run_cli_launcher()
        return

    app = QApplication(sys.argv)
    
    window = CreatorToolsWindow()
    window.show()
    
    sys.exit(app.exec())


def run_cli_launcher():
    """CLI version of the launcher"""
    print("\n" + "="*60)
    print("              ORTHANC'S SCHMIEDE - UNIFIED LAUNCHER")
    print("            Weapon Forge, Armor Forge & More")
    print("="*60)
    
    id_manager = IDManager()
    
    while True:
        print("\nSelect a creation tool:")
        print("1. Weapon Forge Wizard (GUI)")
        print("2. Armor Forge Wizard (GUI)")
        print("3. Exit")
        
        try:
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == '1':
                # For CLI, we can't launch the GUI directly, so we'll show info
                print("\nTo run the Weapon Forge Wizard in GUI mode:")
                print("python -m cff_editor.widgets.weapon_forge_wizard")
                print()
                
            elif choice == '2':
                # For CLI, we can't launch the GUI directly, so we'll show info
                print("\nTo run the Armor Forge Wizard in GUI mode:")
                print("python -m cff_editor.widgets.armor_forge_wizard")
                print()
                
            elif choice == '3':
                print("\nThank you for using Orthanc's Schmiede!")
                break
                
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
                
        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user.")
            break


class CreatorToolsWindow(QMainWindow):
    """Main window for the unified creator tools launcher"""
    
    def __init__(self):
        super().__init__()
        self.id_manager = IDManager()
        self.setWindowTitle("Orthanc's Schmiede - Creator Tools")
        self.setGeometry(100, 100, 600, 500)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        # Title
        title_label = QLabel("Orthanc's Schmiede - Creator Tools")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-size: 18pt; font-weight: bold; margin: 20px;")
        self.layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel("Create custom weapons, armor, and other game content")
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("font-size: 12pt; color: gray; margin-bottom: 30px;")
        self.layout.addWidget(subtitle_label)
        
        # Add some space
        self.layout.addSpacing(20)
        
        # Create tools buttons
        self.create_weapon_button = QPushButton("⚔️  Weapon Forge Wizard")
        self.create_weapon_button.clicked.connect(self.open_weapon_forge)
        self.create_weapon_button.setStyleSheet(
            "QPushButton {"
            "   font-size: 14pt; padding: 15px;"
            "   background-color: #3498db; color: white; border: none; border-radius: 8px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #2980b9;"
            "}"
        )
        self.create_weapon_button.setMinimumHeight(60)
        self.layout.addWidget(self.create_weapon_button)
        
        # Add some space
        self.layout.addSpacing(15)
        
        self.create_armor_button = QPushButton("🛡️  Armor Forge Wizard")
        self.create_armor_button.clicked.connect(self.open_armor_forge)
        self.create_armor_button.setStyleSheet(
            "QPushButton {"
            "   font-size: 14pt; padding: 15px;"
            "   background-color: #9b59b6; color: white; border: none; border-radius: 8px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #8e44ad;"
            "}"
        )
        self.create_armor_button.setMinimumHeight(60)
        self.layout.addWidget(self.create_armor_button)
        
        # Add some space
        self.layout.addSpacing(15)
        
        # Future tools placeholder (for spells, NPCs, etc.)
        placeholder_btn = QPushButton("🔮 Coming Soon: Spell Forge")
        placeholder_btn.setEnabled(False)
        placeholder_btn.setStyleSheet(
            "QPushButton {"
            "   font-size: 14pt; padding: 15px;"
            "   background-color: #bdc3c7; color: #7f8c8d; border: none; border-radius: 8px;"
            "}"
        )
        placeholder_btn.setMinimumHeight(60)
        self.layout.addWidget(placeholder_btn)
        
        # Add stretch to push everything up
        self.layout.addStretch()
        
        # Status bar
        self.status_bar = self.statusBar()
        self.update_status()
    
    def update_status(self):
        """Update the status bar with ID availability"""
        weapon_count = self.id_manager.get_available_count(ContentType.WEAPON)
        armor_count = self.id_manager.get_available_count(ContentType.ARMOR)
        
        status_text = f"Available IDs - Weapons: {weapon_count}, Armor: {armor_count}"
        self.status_bar.showMessage(status_text)
    
    def open_weapon_forge(self):
        """Open the weapon forge wizard"""
        wizard = WeaponForgeWizard(self.id_manager, self)
        wizard.finished.connect(self.update_status)  # Update status when wizard closes
        wizard.show()
    
    def open_armor_forge(self):
        """Open the armor forge wizard"""
        wizard = ArmorForgeWizard(self.id_manager, self)
        wizard.finished.connect(self.update_status)  # Update status when wizard closes
        wizard.show()


if __name__ == "__main__":
    run_unified_launcher()