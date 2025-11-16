#!/usr/bin/env python3
"""
Quick test launcher for the NPC Browser

This script demonstrates the NPC Browser functionality.
You can test both single and multi-selection modes.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QLabel,
    QTextEdit,
)

from TirganachReloaded.cff_editor.widgets.npc_browser_dialog import (
    NPCBrowserDialog,
    SelectionMode,
    choose_quest_giver,
    choose_involved_npcs,
)


class NPCBrowserTestWindow(QMainWindow):
    """Simple test window for NPC Browser"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NPC Browser Test")
        self.resize(600, 400)

        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Title
        title = QLabel("<h2>NPC Browser Test</h2>")
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Click the buttons below to test the NPC Browser in different modes.\n"
            "The browser will load NPCs from GameData.cff."
        )
        layout.addWidget(instructions)

        # Test buttons
        btn1 = QPushButton("Test: Choose Quest Giver (Single Selection)")
        btn1.clicked.connect(self.test_single_selection)
        layout.addWidget(btn1)

        btn2 = QPushButton("Test: Choose Involved NPCs (Multi Selection)")
        btn2.clicked.connect(self.test_multi_selection)
        layout.addWidget(btn2)

        btn3 = QPushButton("Test: Quick Helper - Quest Giver")
        btn3.clicked.connect(self.test_quick_quest_giver)
        layout.addWidget(btn3)

        btn4 = QPushButton("Test: Quick Helper - Involved NPCs")
        btn4.clicked.connect(self.test_quick_involved_npcs)
        layout.addWidget(btn4)

        # Results display
        layout.addWidget(QLabel("<b>Results:</b>"))
        self.results = QTextEdit()
        self.results.setReadOnly(True)
        self.results.setMaximumHeight(150)
        layout.addWidget(self.results)

        layout.addStretch()

    def test_single_selection(self):
        """Test single selection mode"""
        self.results.append("\n--- Testing Single Selection Mode ---")

        dialog = NPCBrowserDialog(mode=SelectionMode.SINGLE, parent=self)
        if dialog.exec():
            npc = dialog.get_selected_npc()
            if npc:
                self.results.append(f"✓ Selected NPC:")
                self.results.append(f"  - ID: {npc.npc_id}")
                self.results.append(f"  - Name: {npc.name}")
                self.results.append(f"  - Race: {npc.race}")
                self.results.append(f"  - Level: {npc.level}")
                self.results.append(f"  - Faction: {npc.faction}")
            else:
                self.results.append("✗ No NPC selected")
        else:
            self.results.append("✗ Dialog cancelled")

    def test_multi_selection(self):
        """Test multi-selection mode"""
        self.results.append("\n--- Testing Multi-Selection Mode ---")

        dialog = NPCBrowserDialog(mode=SelectionMode.MULTI, parent=self)
        if dialog.exec():
            npcs = dialog.get_selected_npcs()
            if npcs:
                self.results.append(f"✓ Selected {len(npcs)} NPCs:")
                for npc in npcs:
                    self.results.append(
                        f"  - {npc.name} (ID: {npc.npc_id}, Race: {npc.race})"
                    )
            else:
                self.results.append("✗ No NPCs selected")
        else:
            self.results.append("✗ Dialog cancelled")

    def test_quick_quest_giver(self):
        """Test quick helper for quest giver"""
        self.results.append("\n--- Testing Quick Helper: Quest Giver ---")

        npc = choose_quest_giver(parent=self)
        if npc:
            self.results.append(f"✓ Quest Giver: {npc.name} (ID: {npc.npc_id})")
        else:
            self.results.append("✗ No quest giver selected")

    def test_quick_involved_npcs(self):
        """Test quick helper for involved NPCs"""
        self.results.append("\n--- Testing Quick Helper: Involved NPCs ---")

        npcs = choose_involved_npcs(parent=self)
        if npcs:
            self.results.append(f"✓ Selected {len(npcs)} involved NPCs:")
            for npc in npcs:
                self.results.append(f"  - {npc.name}")
        else:
            self.results.append("✗ No involved NPCs selected")


def main():
    """Main entry point"""
    app = QApplication(sys.argv)

    window = NPCBrowserTestWindow()
    window.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    print("=" * 60)
    print("NPC Browser Test Launcher")
    print("=" * 60)
    print("\nStarting test window...")
    print("\nThis test requires:")
    print("  - GameData.cff in: OriginalGameFiles/data/GameData.cff")
    print("  - PySide6 installed")
    print("  - TirganachReloaded module accessible")
    print("\n" + "=" * 60 + "\n")

    main()
