#!/usr/bin/env python3
"""
Test script for enhanced objectives system.
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
    QListWidget,
    QPushButton,
    QHBoxLayout,
)
from TirganachReloaded.cff_editor.widgets.objective_editor_simple import (
    ObjectiveEditorDialog,
    ObjectiveData,
)


class TestObjectivesWindow(QMainWindow):
    """Test window for objectives"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enhanced Objectives Test")
        self.resize(600, 400)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Objectives list
        self.objectives_list = QListWidget()
        layout.addWidget(self.objectives_list)

        # Buttons
        btn_layout = QHBoxLayout()
        add_btn = QPushButton("Add Talk Objective")
        add_btn.clicked.connect(lambda: self.add_objective("talk"))
        btn_layout.addWidget(add_btn)

        add_btn2 = QPushButton("Add Kill Objective")
        add_btn2.clicked.connect(lambda: self.add_objective("kill"))
        btn_layout.addWidget(add_btn2)

        add_btn3 = QPushButton("Add Gather Objective")
        add_btn3.clicked.connect(lambda: self.add_objective("gather"))
        btn_layout.addWidget(add_btn3)

        add_btn4 = QPushButton("Add Custom Objective")
        add_btn4.clicked.connect(lambda: self.add_objective("other"))
        btn_layout.addWidget(add_btn4)

        layout.addLayout(btn_layout)

        # Add some test objectives
        self.add_test_objectives()

    def add_objective(self, obj_type: str):
        """Add objective of specific type"""
        dialog = ObjectiveEditorDialog(self)

        # Pre-select type
        for i in range(dialog.type_combo.count()):
            if dialog.type_combo.itemData(i) == obj_type:
                dialog.type_combo.setCurrentIndex(i)
                break

        dialog.on_type_changed()

        if dialog.exec() == QDialog.DialogCode.Accepted:
            objective = dialog.get_objective()
            if objective:
                display_text = objective.get_display_text()
                self.objectives_list.addItem(display_text)
                print(f"Added: {display_text}")
                print(f"Data: {objective.to_dict()}")

    def add_test_objectives(self):
        """Add some test objectives"""
        test_obj1 = ObjectiveData(
            obj_type="talk",
            target_id=213,
            target_name="Shan Muir",
            description="Talk to Shan Muir about the quest",
        )

        test_obj2 = ObjectiveData(
            obj_type="kill",
            target_id=1001,
            target_name="Troll Chieftain",
            quantity=3,
            description="Defeat the troll chieftain and his guards",
        )

        test_obj3 = ObjectiveData(
            obj_type="gather",
            target_id=5001,
            target_name="Magic Herbs",
            quantity=5,
            description="Collect 5 magic herbs for the potion",
        )

        test_obj4 = ObjectiveData(
            obj_type="explore",
            location="Ancient Ruins",
            description="Explore the ancient ruins to find clues",
        )

        test_obj5 = ObjectiveData(
            obj_type="escort",
            target_id=305,
            target_name="Merchant Caravan",
            location="Liannon",
            description="Escort the merchant caravan safely to Liannon",
        )

        test_obj6 = ObjectiveData(
            obj_type="other",
            text="Find the lost artifact",
            description="Search the area for the ancient artifact",
        )

        for obj in [test_obj1, test_obj2, test_obj3, test_obj4, test_obj5, test_obj6]:
            self.objectives_list.addItem(obj.get_display_text())


if __name__ == "__main__":
    print("=" * 60)
    print("Enhanced Objectives Test")
    print("=" * 60)

    app = QApplication(sys.argv)

    window = TestObjectivesWindow()
    window.show()

    print("\n=== Test Window Opened ===")
    print("You can now:")
    print("1. Click buttons to add different objective types")
    print("2. Browse NPCs for talk/escort objectives")
    print("3. Set quantities for kill/gather objectives")
    print("4. Set locations for explore/escort objectives")
    print("5. Create custom text objectives")
    print("\nClose the window to exit.\n")

    sys.exit(app.exec())
