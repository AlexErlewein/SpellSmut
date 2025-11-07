#!/usr/bin/env python3
"""
Test script to verify spell icon display in the GUI.
This script creates a minimal test to check if spell icons are actually showing up.
"""

import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from TirganachReloaded.cff_editor.data_model import CFFDataModel
from TirganachReloaded.tirganach import GameData


def test_spell_icon_display():
    """Test that spell icons can be displayed in a Qt widget."""
    print("Testing Spell Icon Display")
    print("=" * 40)

    # Initialize Qt application first
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Initialize data model
    data_model = CFFDataModel()

    # Load GameData
    gamedata_path = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
    if not gamedata_path.exists():
        print(f"❌ GameData not found: {gamedata_path}")
        return False

    print(f"✓ Loading GameData from: {gamedata_path}")

    try:
        game_data = GameData(str(gamedata_path))
        data_model.game_data = game_data
        print("✓ GameData loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load GameData: {e}")
        return False

    # Test icon path resolution for spell ID 22
    spells_table = data_model.get_table("spells")
    if not spells_table:
        print("❌ No spells table found")
        return False

    # Find spell ID 22
    test_spell = None
    for spell in spells_table:
        if getattr(spell, "spell_id", None) == 22:
            test_spell = spell
            break

    if not test_spell:
        print("❌ Spell ID 22 not found")
        return False

    print(f"✓ Found spell ID 22: {test_spell}")

    # Get icon path
    icon_path = data_model.get_icon_path("spell", test_spell)
    if not icon_path:
        print("❌ No icon path found for spell ID 22")
        return False

    print(f"✓ Icon path resolved: {icon_path}")

    # Check if file exists
    if not Path(icon_path).exists():
        print(f"❌ Icon file does not exist: {icon_path}")
        return False

    print(f"✓ Icon file exists: {icon_path}")

    # Try to load the pixmap
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        print(f"❌ Failed to load pixmap from: {icon_path}")
        return False

    print(f"✓ Pixmap loaded successfully: {pixmap.size()}")

    # Create a simple GUI to display the icon
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create window
    window = QWidget()
    window.setWindowTitle("Spell Icon Test - Spell ID 22")
    window.setGeometry(100, 100, 200, 200)

    # Create layout
    layout = QVBoxLayout()

    # Create label with icon
    icon_label = QLabel()
    icon_label.setPixmap(pixmap)
    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(icon_label)

    # Create text label
    text_label = QLabel("Spell ID 22: ui_spell_MM_Enchantment_Charm")
    text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
    layout.addWidget(text_label)

    window.setLayout(layout)
    window.show()

    print("✓ GUI window created and shown")
    print("  (Close the window to continue)")

    # Run event loop briefly to show window
    app.processEvents()

    return True


if __name__ == "__main__":
    success = test_spell_icon_display()
    if success:
        print("\n🎉 Spell icon display test PASSED!")
        print("The spell icon should be visible in the GUI window.")
    else:
        print("\n❌ Spell icon display test FAILED!")
        print("Check the error messages above.")

    # Keep the application running if successful
    if success:
        import sys
        app = QApplication.instance()
        if app:
            sys.exit(app.exec())