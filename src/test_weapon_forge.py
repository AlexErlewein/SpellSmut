#!/usr/bin/env python3
"""
Test script for running the Weapon Forge wizard directly
This script sets up the necessary environment to test the Weapon Forge
"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from PySide6.QtWidgets import QApplication, QMessageBox, QWidget, QDialog
from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.cff_editor.shared.id_manager import IDManager
from TirganachReloaded.cff_editor.widgets.weapon_forge_wizard import WeaponForgeWizard


def main():
    """Run the Weapon Forge wizard test"""
    print("🔧 Weapon Forge Test Runner")
    print("=" * 40)

    # Create QApplication
    app = QApplication(sys.argv)

    try:
        # Initialize components
        print("📁 Initializing components...")

        # Create data model (try to load game data)
        data_model = CFFDataModel()

        # Create ID manager
        id_manager = IDManager()

        print("✅ Components initialized successfully")

        # Create a minimal mock parent with data_model
        class MockParent(QWidget):
            def __init__(self, data_model):
                super().__init__()
                self.data_model = data_model

        mock_parent = MockParent(data_model)

        # Create and show the Weapon Forge wizard
        print("🗡️ Launching Weapon Forge wizard...")
        wizard = WeaponForgeWizard(id_manager, parent=mock_parent)

        # Show the wizard
        result = wizard.exec()

        if result == QDialog.Accepted:
            print("✅ Weapon creation completed successfully!")
            if hasattr(wizard, 'weapon_data') and wizard.weapon_data:
                print(f"   Weapon: {wizard.weapon_data.weapon_name}")
                print(f"   ID: {wizard.weapon_data.weapon_id}")
                print(f"   DPS: {wizard.weapon_data.calculate_dps():.1f}")
                print(f"   Icon: {wizard.weapon_data.icon_handle}")
        else:
            print("❌ Weapon creation was cancelled")

    except Exception as e:
        print(f"❌ Error running Weapon Forge: {e}")
        QMessageBox.critical(None, "Error", f"Failed to run Weapon Forge:\n{str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())