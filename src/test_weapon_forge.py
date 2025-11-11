#!/usr/bin/env python3
"""
Test script for running Weapon Forge wizard directly
This script sets up necessary environment to test Weapon Forge with all latest features
"""

import sys
import os
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QDialog
from PySide6.QtCore import QDir
from PySide6.QtGui import QFont
from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.shared.id_manager import IDManager
from TirganachReloaded.cff_editor.widgets.weapon_forge_wizard import WeaponForgeWizard
from TirganachReloaded.cff_editor.shared.gamedata_resolver import find_gamedata_path


def test_components_only():
    """Test component initialization without GUI"""
    try:
        print("📁 Testing component initialization...")

        # Test ID manager
        from TirganachReloaded.cff_editor.shared.id_manager import ContentType

        id_manager = IDManager()
        weapon_count = id_manager.get_available_count(ContentType.WEAPON)
        print(f"   ✅ ID Manager: {weapon_count} weapon IDs available")

        # Test data model
        data_model = CFFDataModel()
        print(f"   ✅ Data Model: {len(data_model.icon_mapping)} icons loaded")

        # Test weapon forge wizard creation (without showing)
        # Note: We need QApplication for QWidget, so create minimal one
        from PySide6.QtWidgets import QApplication, QWidget

        # Create minimal QApplication if none exists
        app = QApplication.instance()
        if app is None:
            app = QApplication([])

        class MockParent(QWidget):
            def __init__(self):
                super().__init__()
                self.data_model = data_model

        mock_parent = MockParent()
        wizard = WeaponForgeWizard(id_manager, parent=mock_parent)
        print(f"   ✅ Weapon Forge: Wizard created successfully")

        print("✅ All components initialized successfully!")
        return True

    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def setup_dark_theme(app):
    """Apply professional dark theme matching the weapon forge styling"""
    app.setStyle("Fusion")

    dark_stylesheet = """
    /* Main application background */
    QMainWindow {
        background-color: #1e1e1e;
        color: #e0e0e0;
    }

    /* Widgets */
    QWidget {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }

    /* Group boxes */
    QGroupBox {
        font-weight: bold;
        border: 2px solid #3c3c3c;
        border-radius: 5px;
        margin-top: 1ex;
        background-color: #2b2b2b;
        color: #e0e0e0;
    }

    QGroupBox::title {
        subcontrol-origin: margin;
        left: 10px;
        padding: 0 10px 0 10px;
        color: #e0e0e0;
        font-weight: bold;
    }

    /* Buttons */
    QPushButton {
        background-color: #3c3c3c;
        color: #e0e0e0;
        border: 1px solid #555;
        padding: 5px 10px;
        border-radius: 3px;
        font-weight: normal;
    }

    QPushButton:hover {
        background-color: #4a4a4a;
    }

    QPushButton:pressed {
        background-color: #2d2d30;
    }

    /* Labels */
    QLabel {
        color: #e0e0e0;
    }

    /* Line edits */
    QLineEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3c3c3c;
        padding: 3px;
        selection-background-color: #094771;
    }

    /* Combo boxes */
    QComboBox {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3c3c3c;
        padding: 3px;
        selection-background-color: #094771;
    }

    QComboBox::drop-down {
        border: none;
    }

    QComboBox::down-arrow {
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 4px solid #e0e0e0;
        margin-right: 5px;
    }

    QComboBox QAbstractItemView {
        background-color: #1e1e1e;
        color: #e0e0e0;
        selection-background-color: #094771;
        border: 1px solid #3c3c3c;
    }

    /* Spin boxes */
    QSpinBox, QDoubleSpinBox {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3c3c3c;
        padding: 3px;
        selection-background-color: #094771;
    }

    /* Text edits */
    QTextEdit {
        background-color: #1e1e1e;
        color: #e0e0e0;
        border: 1px solid #3c3c3c;
        selection-background-color: #094771;
    }

    /* Wizards */
    QWizard {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }

    QWizard QWidget {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }

    QWizardPage {
        background-color: #2b2b2b;
        color: #e0e0e0;
    }
    """

    app.setStyleSheet(dark_stylesheet)


def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")

    # Check pygame for audio features
    try:
        import pygame

        print("   ✅ Pygame available for audio preview")
    except ImportError:
        print("   ⚠️  Pygame not found - audio preview will be disabled")
        print("      Install with: pip install pygame==2.6.1")

    # Check tirganach library for CFF export
    try:
        from TirganachReloaded.tirganach import GameData

        print("   ✅ Tirganach library available for CFF export")
    except ImportError:
        print("   ⚠️  Tirganach library not found - CFF export will be disabled")

    # Check GameData.cff file using shared resolver
    gd_path = find_gamedata_path()
    if gd_path:
        print(f"   ✅ GameData.cff found: {gd_path}")
    else:
        print("   ⚠️  GameData.cff not found - some features may be limited")
        print("      Expected locations:")
        expected = [
            project_root.parent / "OriginalGameFiles" / "data" / "GameData.cff",
            project_root.parent / "OriginalGameFiles" / "GameData.cff",
            project_root / "OriginalGameFiles" / "data" / "GameData.cff",
            project_root / "OriginalGameFiles" / "GameData.cff",
            Path.home() / "SpellForce Platinum Edition" / "data" / "GameData.cff",
        ]
        for p in expected:
            print(f"        - {p}")

    print()


def main():
    """Run Weapon Forge wizard test with all latest features"""
    import argparse

    parser = argparse.ArgumentParser(description="Test Weapon Forge wizard")
    parser.add_argument(
        "--no-gui", action="store_true", help="Run in non-GUI mode for testing"
    )
    args = parser.parse_args()

    print("🔧 Weapon Forge Test Runner (Enhanced)")
    print("=" * 50)

    # Check dependencies first
    check_dependencies()

    if args.no_gui:
        print("🔧 Running in non-GUI test mode")
        test_components_only()
        return 0

    # Create QApplication with dark theme
    app = QApplication(sys.argv)
    app.setApplicationName("Weapon Forge Test")
    app.setOrganizationName("TirganachReloaded Modding Tools")

    # Apply dark theme
    setup_dark_theme(app)

    try:
        # Initialize components
        print("📁 Initializing components...")

        # Create data model (try to load game data)
        print("   Loading CFF data model...")
        data_model = CFFDataModel()

        # Try to load game data if available
        try:
            gd_path = find_gamedata_path()
            if gd_path:
                print(f"   ✅ Game data available at {gd_path}")
            else:
                print("   ⚠️  GameData.cff not found, using empty data model")
        except Exception as e:
            print(f"   ⚠️  Failed to check game data: {e}")

        # Create ID manager
        print("   Initializing ID manager...")
        id_manager = IDManager()

        # Show available ID ranges
        from TirganachReloaded.cff_editor.shared.id_manager import ContentType

        weapon_count = id_manager.get_available_count(ContentType.WEAPON)
        print(f"   ✅ {weapon_count} weapon IDs available (10000-19999)")

        print("✅ Components initialized successfully")
        print()

        # Create a mock parent with data_model (simulates OrthancsSchmiede)
        class MockParent(QWidget):
            def __init__(self, data_model):
                super().__init__()
                self.data_model = data_model
                self.setWindowTitle("Weapon Forge Test Environment")
                self.setMinimumSize(400, 300)

                # Add some info text
                from PySide6.QtWidgets import QVBoxLayout, QLabel

                layout = QVBoxLayout(self)

                info_label = QLabel(
                    "🗡️ Weapon Forge Test Environment\n\n"
                    "This test window provides data_model context\n"
                    "for the Weapon Forge wizard.\n\n"
                    "Features available:\n"
                    "• Weapon creation/editing/duplication\n"
                    "• Icon browser (if data loaded)\n"
                    "• Sound preview (if pygame installed)\n"
                    "• CFF export (if tirganach available)\n"
                    "• Dark theme styling\n"
                    "• Complete validation system"
                )
                info_label.setWordWrap(True)
                info_label.setStyleSheet("color: #a0a0a0; padding: 20px;")
                layout.addWidget(info_label)

        mock_parent = MockParent(data_model)
        mock_parent.show()  # Show the test parent window

        # Create and show Weapon Forge wizard
        print("🗡️ Launching Weapon Forge wizard...")
        print("   Features available:")
        print("   • Complete weapon properties inheritance")
        print("   • Professional sound system with preview")
        print("   • Enhanced UI with dark theme")
        print("   • CFF and JSON export options")
        print("   • Comprehensive validation")
        print()

        wizard = WeaponForgeWizard(id_manager, parent=mock_parent)

        # Show wizard
        result = wizard.exec()

        if result == QDialog.DialogCode.Accepted:
            print("✅ Weapon creation completed successfully!")
            if hasattr(wizard, "weapon_data") and wizard.weapon_data:
                weapon = wizard.weapon_data
                print(f"   📋 Weapon Summary:")
                print(f"      Name: {weapon.weapon_name}")
                print(f"      ID: {weapon.weapon_id}")
                print(f"      Type: {weapon.weapon_type_name} ({weapon.hands.value})")
                print(
                    f"      Damage: {weapon.min_damage}-{weapon.max_damage} {weapon.damage_type.value}"
                )
                print(f"      DPS: {weapon.calculate_dps():.1f}")
                print(f"      Balance: {weapon.get_balance_rating()}/100")
                print(f"      Icon: {weapon.icon_handle or 'None'}")
                print(f"      Hit Sound: {weapon.hit_sound}")
                print(f"      Miss Sound: {weapon.miss_sound}")
                print(f"      Creation Mode: {weapon.creation_mode}")

                if (
                    weapon.creation_mode in ["edit", "duplicate"]
                    and weapon.source_weapon_id
                ):
                    print(f"      Source Weapon ID: {weapon.source_weapon_id}")

                print(
                    f"      Requirements: STR {weapon.requirements.strength}, "
                    f"DEX {weapon.requirements.dexterity}, "
                    f"INT {weapon.requirements.intelligence}, "
                    f"LVL {weapon.requirements.level}"
                )
        else:
            print("❌ Weapon creation was cancelled")

    except Exception as e:
        print(f"❌ Error running Weapon Forge: {e}")
        import traceback

        traceback.print_exc()

        QMessageBox.critical(
            None,
            "Weapon Forge Test Error",
            f"Failed to run Weapon Forge:\n\n{str(e)}\n\n"
            f"Check the console output for detailed error information.",
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
