#!/usr/bin/env python3
"""
Test AnswerId Management Integration

Test the integration of AnswerId management panel with the text mode dialogue overview.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PySide6.QtCore import Qt

def test_answer_id_integration():
    """Test the integrated AnswerId management system"""

    # Add the current directory to path for imports
    sys.path.insert(0, 'src')

    app = QApplication(sys.argv)

    # Create main window
    window = QMainWindow()
    window.setWindowTitle("AnswerId Management Integration Test")
    window.resize(1400, 900)

    # Create central widget
    central_widget = QWidget()
    window.setCentralWidget(central_widget)
    layout = QVBoxLayout(central_widget)

    # Import and create the text mode dialogue overview
    try:
        from TirganachReloaded.cff_editor.widgets.text_mode_dialogue_overview import TextModeDialogueOverview
        overview = TextModeDialogueOverview()
        layout.addWidget(overview)

        # Create test dialogue data based on the game example
        test_data = {
            "nodes": [
                {
                    "id": "start_node",
                    "node_type": "start",
                    "speaker": "",
                    "text": "Dialogue begins here",
                    "choices": [],
                    "conditions": [],
                    "actions": [],
                    "next_nodes": ["npc_001"],
                    "answer_id": None,
                    "tag": "start_001"
                },
                {
                    "id": "npc_001",
                    "node_type": "npc",
                    "speaker": "Sternenpriester",
                    "text": "Macht schon, bringt es hinter Euch, Lichtgläubiger!",
                    "choices": [
                        {
                            "text": "Tot nützt Ihr mir nichts. Aber vielleicht habt Ihr etwas anzubieten, das mir Euer Leben wert ist?",
                            "answer_id": 1,
                            "next_node": "npc_resp_1"
                        },
                        {
                            "text": "Ihr werdet heute sterben.",
                            "answer_id": None,  # Unassigned for testing
                            "next_node": "npc_resp_2"
                        }
                    ],
                    "conditions": [],
                    "actions": [],
                    "next_nodes": [],
                    "answer_id": None,
                    "tag": "sternenpriester110_001"
                },
                {
                    "id": "npc_resp_1",
                    "node_type": "npc",
                    "speaker": "Sternenpriester",
                    "text": "Was wäre, wenn ich Euch sage, dass es geheime Gänge in die anderen Stadtteile gibt?",
                    "choices": [
                        {
                            "text": "Sprecht weiter.",
                            "answer_id": 2,
                            "next_node": "npc_resp_2"
                        }
                    ],
                    "conditions": [],
                    "actions": [],
                    "next_nodes": [],
                    "answer_id": 1,  # This node responds to AnswerId=1
                    "tag": "sternenpriester110_003"
                },
                {
                    "id": "npc_resp_2",
                    "node_type": "npc",
                    "speaker": "Sternenpriester",
                    "text": "Die Gänge wurden von Ulkar Kahn angelegt, bevor die Sonnenpriester ihn ermordet haben. Sie führen in die Sonnen- und Mondstadt. Aber sie sind magisch verschlossen.",
                    "choices": [
                        {
                            "text": "Was nützen sie mir dann?",
                            "answer_id": 3,
                            "next_node": "npc_resp_3"
                        }
                    ],
                    "conditions": [],
                    "actions": [],
                    "next_nodes": [],
                    "answer_id": 2,  # This node responds to AnswerId=2
                    "tag": "sternenpriester110_005"
                },
                {
                    "id": "npc_resp_3",
                    "node_type": "npc",
                    "speaker": "Sternenpriester",
                    "text": "Wartet! Nur die Hand Kahns kann die Tore öffnen! Kahn ist tot, aber seine Hand befindet sich in unserem Besitz!",
                    "choices": [
                        {
                            "text": "Gut, gebt sie mir und Ihr sollt verschont bleiben.",
                            "answer_id": 5,
                            "next_node": "npc_final"
                        },
                        {
                            "text": "Ich nehme sie gewaltsam.",
                            "answer_id": None,  # Unassigned
                            "next_node": "npc_combat"
                        }
                    ],
                    "conditions": [],
                    "actions": [],
                    "next_nodes": [],
                    "answer_id": 3,  # This node responds to AnswerId=3
                    "tag": "sternenpriester110_007"
                },
                {
                    "id": "npc_final",
                    "node_type": "npc",
                    "speaker": "Sternenpriester",
                    "text": "Man weiß nie, wann man sie brauchen könnte. Aber nun ist es wohl soweit.",
                    "choices": [
                        {
                            "text": "[Hand übergeben]",
                            "answer_id": 99,  # End dialogue
                            "next_node": "end_node"
                        }
                    ],
                    "conditions": [],
                    "actions": [
                        {"type": "GiveItem", "item_id": 2648, "description": "Khan's Hand"},
                        {"type": "RemoveDialog", "target": "self"}
                    ],
                    "next_nodes": [],
                    "answer_id": 5,  # This node responds to AnswerId=5
                    "tag": "sternenpriester110_009"
                },
                {
                    "id": "end_node",
                    "node_type": "end",
                    "speaker": "",
                    "text": "Dialogue ends - Player receives Khan's Hand",
                    "choices": [],
                    "conditions": [],
                    "actions": [],
                    "next_nodes": [],
                    "answer_id": 99,
                    "tag": "end_001"
                },
                {
                    "id": "npc_combat",
                    "node_type": "npc",
                    "speaker": "Sternenpriester",
                    "text": "Niemals! Ihr werdet sie mir entreißen müssen!",
                    "choices": [
                        {
                            "text": "[Kampf beginnen]",
                            "answer_id": None,  # Unassigned
                            "next_node": "end_node"
                        }
                    ],
                    "conditions": [],
                    "actions": [
                        {"type": "StartCombat", "target": "sternenpriester"}
                    ],
                    "next_nodes": [],
                    "answer_id": None,
                    "tag": "sternenpriester110_combat"
                }
            ],
            "connections": [
                {"from": "start_node", "to": "npc_001"},
                {"from": "npc_001", "to": "npc_resp_1"},
                {"from": "npc_001", "to": "npc_resp_2"},
                {"from": "npc_resp_1", "to": "npc_resp_2"},
                {"from": "npc_resp_2", "to": "npc_resp_3"},
                {"from": "npc_resp_3", "to": "npc_final"},
                {"from": "npc_resp_3", "to": "npc_combat"},
                {"from": "npc_final", "to": "end_node"},
                {"from": "npc_combat", "to": "end_node"}
            ]
        }

        # Load the test data
        overview.set_dialogue_data(test_data)

        # Add control buttons for testing
        control_frame = QWidget()
        control_layout = QVBoxLayout(control_frame)

        test_btn = QPushButton("🧪 Test Auto-Assign")
        test_btn.clicked.connect(lambda: overview.answer_id_panel.auto_assign_missing() if hasattr(overview, 'answer_id_panel') else None)
        control_layout.addWidget(test_btn)

        validate_btn = QPushButton("🔍 Test Validation")
        validate_btn.clicked.connect(lambda: overview.answer_id_panel.validate_answer_ids() if hasattr(overview, 'answer_id_panel') else None)
        control_layout.addWidget(validate_btn)

        layout.addWidget(control_frame)

        print("✅ AnswerId Management Integration Test Loaded Successfully!")
        print("📋 Features available:")
        print("   • Text-based dialogue tree view with AnswerId highlighting")
        print("   • AnswerId management panel with assignment tracking")
        print("   • Conflict detection and resolution")
        print("   • Auto-assignment of missing AnswerIds")
        print("   • Integration with existing dialogue system")

    except ImportError as e:
        # Fallback if modules not available
        error_label = QPushButton(f"❌ Import Error: {e}")
        layout.addWidget(error_label)
        print(f"❌ Import Error: {e}")

    window.show()
    return app.exec()

if __name__ == "__main__":
    sys.exit(test_answer_id_integration())