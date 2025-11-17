#!/usr/bin/env python3
"""
Test script for Condition Builder and Flag Manager integration.

This script tests both widgets standalone and integrated together.
"""

import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QTabWidget,
    QVBoxLayout,
    QWidget,
)
from TirganachReloaded.cff_editor.widgets.flag_manager import (
    FlagManagerWidget,
    FlagDefinition,
)
from TirganachReloaded.cff_editor.widgets.condition_builder import (
    ConditionBuilderWidget,
    Condition,
    LogicalCondition,
)


class TestWindow(QMainWindow):
    """Test window for conditions and flags"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Condition Builder & Flag Manager Test")
        self.resize(1200, 800)

        # Central widget with tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        tabs = QTabWidget()
        layout.addWidget(tabs)

        # Tab 1: Flag Manager
        self.flag_manager = FlagManagerWidget()
        tabs.addTab(self.flag_manager, "Flag Manager")

        # Tab 2: Condition Builder (with flag manager integration)
        self.condition_builder = ConditionBuilderWidget(flag_manager=self.flag_manager)
        tabs.addTab(self.condition_builder, "Condition Builder")

        # Add test data
        self.add_test_data()

        # Connect signals
        self.flag_manager.flags_changed.connect(self.on_flags_changed)
        self.condition_builder.conditions_changed.connect(self.on_conditions_changed)

    def add_test_data(self):
        """Add some test flags and conditions"""
        print("Adding test data...")

        # Add test flags
        self.flag_manager.add_flag(
            FlagDefinition(
                name="PlayerHasItemSanduhr",
                flag_type="item",
                description="Player possesses the Sanduhr (hourglass) item",
                used_by=["Quest_646"],
                auto_generated=False,
            )
        )

        self.flag_manager.add_flag(
            FlagDefinition(
                name="AmraUndLea1Complete",
                flag_type="global",
                description="First part of Amra and Lea quest completed",
                used_by=["Quest_652", "Dialogue_Amra_2"],
            )
        )

        self.flag_manager.add_flag(
            FlagDefinition(
                name="n_P213_Talked",
                flag_type="npc",
                description="Player has talked to NPC P213 (Shan Muir)",
            )
        )

        self.flag_manager.add_flag(
            FlagDefinition(
                name="TrollCampDestroyed",
                flag_type="global",
                description="Troll camp has been destroyed",
                auto_generated=True,
            )
        )

        # Add test conditions
        cond1 = Condition("QuestState", {"quest_id": 646, "state": "StateActive"})
        cond2 = Condition(
            "ItemFlag", {"flag_name": "PlayerHasItemSanduhr", "flag_state": "true"}
        )
        cond3 = Condition(
            "GlobalFlag",
            {"flag_name": "TrollCampDestroyed", "flag_state": "false"},
            negated=True,
        )

        or_group = LogicalCondition("ODER")
        or_group.children.append(Condition("TimeDay", {}))
        or_group.children.append(Condition("TimeNight", {}))

        self.condition_builder.root_condition.children = [cond1, cond2, cond3, or_group]
        self.condition_builder.refresh_tree()

        print(f"Added {len(self.flag_manager.flags)} test flags")
        print(
            f"Added {len(self.condition_builder.root_condition.children)} test conditions"
        )

    def on_flags_changed(self):
        """Handle flag changes"""
        print(f"Flags changed! Now have {len(self.flag_manager.flags)} flags")

        # Export to see structure
        flags_dict = self.flag_manager.to_dict()
        print(f"Flags data structure: {len(flags_dict)} flags defined")

    def on_conditions_changed(self):
        """Handle condition changes"""
        print("Conditions changed!")

        # Generate and print LUA
        lua_code = self.condition_builder.to_lua()
        print(f"Generated LUA:\n{lua_code}\n")


def test_data_export_import():
    """Test data export and import"""
    print("\n=== Testing Data Export/Import ===\n")

    # Create flag manager (app must exist first)
    flag_mgr = FlagManagerWidget()

    # Add flags
    flag_mgr.add_flag(FlagDefinition("TestFlag1", "global", "Test flag 1"))
    flag_mgr.add_flag(FlagDefinition("TestFlag2", "item", "Test flag 2", ["Quest_1"]))

    # Export
    exported = flag_mgr.to_dict()
    print(f"Exported {len(exported)} flags")
    print(f"Export data: {exported}")

    # Create new manager and import
    flag_mgr2 = FlagManagerWidget()
    flag_mgr2.load_from_dict(exported)

    print(f"Imported {len(flag_mgr2.flags)} flags")
    assert len(flag_mgr2.flags) == len(exported), "Import/export mismatch!"

    print("✓ Export/Import test passed!")

    # Test condition export/import
    cond_builder = ConditionBuilderWidget()

    # Add conditions
    cond1 = Condition("QuestState", {"quest_id": 123, "state": "StateActive"})
    cond2 = Condition("ItemFlag", {"flag_name": "TestItem", "flag_state": "true"})

    cond_builder.root_condition.children = [cond1, cond2]

    # Export
    cond_exported = cond_builder.to_dict()
    print(f"\nExported conditions: {cond_exported}")

    # Import
    cond_builder2 = ConditionBuilderWidget()
    cond_builder2.load_from_dict(cond_exported)

    print(f"Imported {len(cond_builder2.root_condition.children)} conditions")
    assert len(cond_builder2.root_condition.children) == 2, (
        "Condition import/export mismatch!"
    )

    print("✓ Condition export/import test passed!")


def test_lua_generation():
    """Test LUA code generation"""
    print("\n=== Testing LUA Generation ===\n")

    cond_builder = ConditionBuilderWidget()

    # Simple condition
    simple = Condition("QuestState", {"quest_id": 100, "state": "StateActive"})
    cond_builder.root_condition.children = [simple]
    lua = cond_builder.to_lua()
    print(f"Simple condition LUA:\n{lua}\n")

    # Complex nested condition
    cond_builder.root_condition.children.clear()

    cond1 = Condition("QuestState", {"quest_id": 100, "state": "StateActive"})
    cond2 = Condition("ItemFlag", {"flag_name": "PlayerHasItem", "flag_state": "true"})

    or_group = LogicalCondition("ODER")
    or_group.children.append(Condition("TimeDay", {}))
    or_group.children.append(
        Condition("GlobalFlag", {"flag_name": "IsDaytime", "flag_state": "true"})
    )

    cond_builder.root_condition.children = [cond1, cond2, or_group]

    lua = cond_builder.to_lua()
    print(f"Complex nested condition LUA:\n{lua}\n")

    print("✓ LUA generation test passed!")


if __name__ == "__main__":
    print("=" * 60)
    print("Condition Builder & Flag Manager Test Suite")
    print("=" * 60)

    # Create QApplication first (required for all Qt widgets)
    app = QApplication(sys.argv)

    # Run unit tests
    test_data_export_import()
    test_lua_generation()

    # Run interactive test
    print("\n" + "=" * 60)
    print("Starting interactive test...")
    print("=" * 60)

    window = TestWindow()
    window.show()

    print("\n=== Test Window Opened ===")
    print("You can now:")
    print("1. Add/edit/delete flags in the Flag Manager tab")
    print("2. Build complex conditions in the Condition Builder tab")
    print("3. Use the 'Browse' button in conditions to select existing flags")
    print("4. Preview LUA code generation")
    print("\nClose the window to exit.\n")

    sys.exit(app.exec())
