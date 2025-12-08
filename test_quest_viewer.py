#!/usr/bin/env python3
"""
Test script for Quest Viewer Integration

This script tests the quest viewing functionality by loading sample data
and verifying that the quest viewer can properly display quest information.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent / "src"
sys.path.insert(0, str(project_root))

try:
    from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
    from PySide6.QtCore import QTimer

    from TirganachReloaded.cff_editor.data_model import CFFDataModel
    from TirganachReloaded.cff_editor.widgets.quest_viewer_integration import QuestViewerWidget
    from TirganachReloaded.cff_editor.logging_config import get_logger

    logger = get_logger(__name__)

    class TestQuestViewerWindow(QMainWindow):
        """Test window for quest viewer functionality"""

        def __init__(self):
            super().__init__()
            self.setWindowTitle("Quest Viewer Test")
            self.setMinimumSize(1200, 800)

            # Create data model
            self.data_model = CFFDataModel()

            # Setup UI
            self.setup_ui()

            # Load some test data
            self.load_test_data()

        def setup_ui(self):
            """Setup the test UI"""
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            layout = QVBoxLayout(central_widget)

            # Title
            title = QLabel("Quest Viewer Test Application")
            title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
            layout.addWidget(title)

            # Instructions
            instructions = QLabel(
                "Instructions:\n"
                "1. Use the Test Data button to load sample quest data\n"
                "2. The Quest Viewer will display loaded quests\n"
                "3. You can switch between view and edit modes\n"
                "4. Export functionality allows you to save quest data\n"
                "\nThis test demonstrates the integration between the quest hierarchy "
                "tree and the enhanced quest editor."
            )
            instructions.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
            layout.addWidget(instructions)

            # Test buttons
            button_layout = QVBoxLayout()

            self.load_data_btn = QPushButton("Load Test Quest Data")
            self.load_data_btn.clicked.connect(self.load_test_data)
            button_layout.addWidget(self.load_data_btn)

            self.clear_data_btn = QPushButton("Clear Quest Data")
            self.clear_data_btn.clicked.connect(self.clear_test_data)
            button_layout.addWidget(self.clear_data_btn)

            self.test_integration_btn = QPushButton("Test Quest Integration")
            self.test_integration_btn.clicked.connect(self.test_quest_integration)
            button_layout.addWidget(self.test_integration_btn)

            layout.addLayout(button_layout)

            # Quest viewer
            try:
                self.quest_viewer = QuestViewerWidget(self.data_model)
                layout.addWidget(self.quest_viewer)
                self.quest_viewer_title = QLabel("Quest Viewer (Ready)")
                self.quest_viewer_title.setStyleSheet("font-weight: bold; color: green;")
                layout.addWidget(self.quest_viewer_title)
            except Exception as e:
                error_label = QLabel(f"Failed to create Quest Viewer: {str(e)}")
                error_label.setStyleSheet("color: red; font-weight: bold; padding: 10px;")
                layout.addWidget(error_label)
                self.quest_viewer = None

        def load_test_data(self):
            """Load test quest data"""
            try:
                logger.info("Loading test quest data...")

                # Create sample quest data similar to what would be in CFF
                sample_quests = self._create_sample_quests()

                # Add to data model
                if hasattr(self.data_model, '_data'):
                    # Add quests to data model
                    if 'quests' not in self.data_model._data:
                        self.data_model._data['quests'] = []

                    self.data_model._data['quests'].extend(sample_quests)

                    # Simulate data loaded signal
                    if hasattr(self.data_model, 'data_loaded'):
                        self.data_model.data_loaded.emit()

                # Test loading a quest into the viewer
                if self.quest_viewer and sample_quests:
                    first_quest = sample_quests[0]
                    quest_id = getattr(first_quest, 'quest_id', 1)

                    success = self.quest_viewer.load_quest(quest_id)
                    if success:
                        logger.info(f"Successfully loaded quest {quest_id} into viewer")
                        self.quest_viewer_title.setText(f"Quest Viewer (Loaded: {getattr(first_quest, 'name', 'Unknown')})")
                    else:
                        logger.error(f"Failed to load quest {quest_id} into viewer")

                self.load_data_btn.setText("Reload Test Data")
                self.load_data_btn.setStyleSheet("background-color: #4CAF50; color: white;")

            except Exception as e:
                logger.error(f"Error loading test data: {e}")
                if self.quest_viewer:
                    self.quest_viewer_title.setText(f"Quest Viewer (Error: {str(e)})")

        def clear_test_data(self):
            """Clear test quest data"""
            try:
                logger.info("Clearing test quest data...")

                if hasattr(self.data_model, '_data') and 'quests' in self.data_model._data:
                    self.data_model._data['quests'].clear()

                if self.quest_viewer:
                    # Clear the viewer
                    self.quest_viewer_title.setText("Quest Viewer (Cleared)")

                self.clear_data_btn.setStyleSheet("background-color: #f44336; color: white;")
                self.load_data_btn.setText("Load Test Quest Data")

                logger.info("Test data cleared")

            except Exception as e:
                logger.error(f"Error clearing test data: {e}")

        def test_quest_integration(self):
            """Test quest integration functionality"""
            try:
                logger.info("Testing quest integration...")

                if not self.quest_viewer:
                    QMessageBox.warning(self, "Test Error", "Quest Viewer not available")
                    return

                # Test data processor
                from TirganachReloaded.cff_editor.widgets.quest_viewer_integration import QuestDataProcessor

                processor = QuestDataProcessor(self.data_model)

                # Create a sample quest element
                sample_quest = self._create_sample_quest_element()

                # Process the quest
                processed_data = processor.process_quest_data(sample_quest)

                if processed_data:
                    logger.info("Quest data processing test: SUCCESS")
                    logger.info(f"Processed quest: {processed_data.get('name', 'Unknown')}")

                    # Display processing results
                    self._show_processing_results(processed_data)
                else:
                    logger.error("Quest data processing test: FAILED")
                    QMessageBox.warning(self, "Test Failed", "Quest data processing failed")

            except Exception as e:
                logger.error(f"Error testing quest integration: {e}")
                QMessageBox.critical(self, "Test Error", f"Integration test failed: {str(e)}")

        def _create_sample_quests(self):
            """Create sample quest data for testing"""
            class MockQuest:
                def __init__(self, **kwargs):
                    for key, value in kwargs.items():
                        setattr(self, key, value)

            return [
                MockQuest(
                    quest_id=1,
                    name="The First Quest",
                    description="This is the first quest in our test data.",
                    parent_quest_id=0,
                    order_index=1,
                    priority=5,
                    status="Unknown",
                    difficulty="Easy",
                    min_level=1,
                    quest_type="Main Quest",
                    experience_reward=100,
                    gold_reward=50,
                    quest_giver_name="Town Elder",
                    quest_giver_location="Town Square"
                ),
                MockQuest(
                    quest_id=2,
                    name="The Lost Ring",
                    description="Find the lost ring of the ancient king.",
                    parent_quest_id=1,
                    order_index=2,
                    priority=3,
                    status="Unknown",
                    difficulty="Medium",
                    min_level=5,
                    quest_type="Side Quest",
                    experience_reward=250,
                    gold_reward=100,
                    quest_giver_name="Merchant",
                    quest_giver_location="Market"
                ),
                MockQuest(
                    quest_id=3,
                    name="Dragon Slayer",
                    description="Defeat the ancient dragon terrorizing the village.",
                    parent_quest_id=0,
                    order_index=3,
                    priority=1,
                    status="Unknown",
                    difficulty="Very Hard",
                    min_level=15,
                    quest_type="Main Quest",
                    experience_reward=1000,
                    gold_reward=500,
                    quest_giver_name="Village Chief",
                    quest_giver_location="Village Hall"
                )
            ]

        def _create_sample_quest_element(self):
            """Create a sample quest element for testing"""
            return self._create_sample_quests()[0]  # Return first quest

        def _show_processing_results(self, processed_data):
            """Show the results of quest data processing"""
            from PySide6.QtWidgets import QDialog, QTextEdit, QVBoxLayout, QDialogButtonBox

            dialog = QDialog(self)
            dialog.setWindowTitle("Quest Processing Results")
            dialog.setMinimumSize(800, 600)

            layout = QVBoxLayout(dialog)

            text_edit = QTextEdit()
            text_edit.setPlainText(f"""
Quest Processing Test Results:
{'='*50}

Quest ID: {processed_data.get('quest_id', 'Unknown')}
Name: {processed_data.get('name', 'Unknown')}
Type: {processed_data.get('quest_type', 'Unknown')}
Difficulty: {processed_data.get('difficulty', 'Unknown')}
Priority: {processed_data.get('priority', 5)}
Status: {processed_data.get('status', 'Unknown')}

Description:
{processed_data.get('description', 'No description')}

Quest Giver:
{processed_data.get('quest_giver', {}).get('name', 'Unknown')} at {processed_data.get('quest_giver', {}).get('location', 'Unknown')}

Requirements:
{chr(10).join([f'• {req.get("description", "Unknown")}' for req in processed_data.get('requirements', [])])}

Objectives:
{chr(10).join([f'• {obj.get("description", "Unknown")}' for obj in processed_data.get('objectives', [])])}

Rewards:
• Experience: {processed_data.get('rewards', {}).get('experience', 0)}
• Gold: {processed_data.get('rewards', {}).get('gold', 0)}

Map Locations:
{chr(10).join([f'• {loc.get("name", "Unknown")} ({loc.get("code", "Unknown")})' for loc in processed_data.get('map_locations', [])])}

Dialogue Nodes: {len(processed_data.get('dialogue_data', {}).get('nodes', {}))}
Variables: {len(processed_data.get('variables', []))}

Processing: SUCCESS ✅
""")

            text_edit.setReadOnly(True)
            layout.addWidget(text_edit)

            buttons = QDialogButtonBox(QDialogButtonBox.Ok)
            buttons.accepted.connect(dialog.accept)
            layout.addWidget(buttons)

            dialog.exec()

    def test_quest_viewer_functionality():
        """Test the quest viewer functionality"""
        app = QApplication(sys.argv)

        try:
            # Create test window
            window = TestQuestViewerWindow()
            window.show()

            # Auto-load test data after a short delay
            QTimer.singleShot(1000, window.load_test_data)

            # Run the application
            return app.exec()

        except Exception as e:
            print(f"Error running test: {e}")
            return 1

    if __name__ == "__main__":
        print("Starting Quest Viewer Test...")
        print("=" * 50)

        exit_code = test_quest_viewer_functionality()
        print("=" * 50)
        print(f"Test completed with exit code: {exit_code}")
        sys.exit(exit_code)

except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are available:")
    print("- PySide6")
    print("- TirganachReloaded.cff_editor modules")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)