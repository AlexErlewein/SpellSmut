"""
Quest Viewer Integration Module

This module provides integration between the quest hierarchy tree and the unified quest editor,
allowing users to view existing quests with all their details in the editor.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Union

from PySide6.QtCore import Qt, Signal, QObject
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QLabel, QPushButton, QComboBox,
    QTextEdit, QLineEdit, QSpinBox, QCheckBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
    QToolBar, QMenu, QMenuBar, QStatusBar, QMessageBox,
    QFrame, QScrollArea, QSlider, QDial,
    QGridLayout, QFormLayout, QButtonGroup, QRadioButton,
    QDialog, QDialogButtonBox, QFileDialog, QTabWidget
)
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon, QTextCursor

try:
    from ..logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

try:
    from .unified_enhanced_quest_editor import UnifiedEnhancedQuestEditor
    from ..models.quest_models import EnhancedQuestData, Dialogue, QuestReward, MapLocation
    from ..models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice,
        DialogueCondition, DialogueAction, DialogueConditionType, DialogueActionType
    )
except ImportError as e:
    logger.warning(f"Could not import quest editor components: {e}")
    UnifiedEnhancedQuestEditor = None
    EnhancedQuestData = None


class QuestDataProcessor:
    """Processes raw quest data from the CFF model into enhanced quest editor format"""

    def __init__(self, data_model):
        self.data_model = data_model

    def process_quest_data(self, quest_element) -> Optional[Dict[str, Any]]:
        """Process quest data from CFF element into enhanced quest format"""
        try:
            if not quest_element:
                return None

            # Extract basic quest information
            quest_id = getattr(quest_element, 'quest_id', None)
            if quest_id is None:
                return None

            # Get localized name and description
            name = self.data_model.get_localised_text(quest_element, 'name')
            if not name:
                name = getattr(quest_element, 'name', f'Quest {quest_id}')

            description = self.data_model.get_localised_text(quest_element, 'description')
            if not description:
                description = getattr(quest_element, 'description', 'No description available')

            # Build quest data structure
            quest_data = {
                'quest_id': quest_id,
                'name': name,
                'description': description,
                'parent_id': getattr(quest_element, 'parent_quest_id', 0),
                'order_index': getattr(quest_element, 'order_index', 0),
                'quest_type': self._determine_quest_type(quest_element),
                'difficulty': self._determine_difficulty(quest_element),
                'priority': getattr(quest_element, 'priority', 5),
                'status': getattr(quest_element, 'status', 'Unknown'),

                # Process quest giver information
                'quest_giver': self._extract_quest_giver(quest_element),

                # Process requirements
                'requirements': self._extract_requirements(quest_element),

                # Process objectives
                'objectives': self._extract_objectives(quest_element),

                # Process rewards
                'rewards': self._extract_rewards(quest_element),

                # Process map locations
                'map_locations': self._extract_map_locations(quest_element),

                # Process dialogues
                'dialogues': self._extract_dialogues(quest_element),

                # Process dialogue tree for enhanced editor
                'dialogue_data': self._extract_dialogue_tree(quest_element),

                # Process variables and flags
                'variables': self._extract_variables(quest_element),

                # Raw element for additional processing
                '_raw_element': quest_element
            }

            return quest_data

        except Exception as e:
            logger.error(f"Error processing quest data: {e}")
            return None

    def _determine_quest_type(self, quest_element) -> str:
        """Determine quest type from quest element"""
        # Check various attributes to determine type
        quest_type = getattr(quest_element, 'quest_type', 'Side Quest')

        # If quest has no parent, it's likely a main quest
        parent_id = getattr(quest_element, 'parent_quest_id', 0)
        if parent_id == 0 or parent_id is None:
            quest_type = 'Main Quest'

        # Check for repeatable flag
        if getattr(quest_element, 'repeatable', False):
            quest_type = 'Repeatable Quest'

        # Check for hidden flag
        if getattr(quest_element, 'hidden', False):
            quest_type = 'Hidden Quest'

        return quest_type

    def _determine_difficulty(self, quest_element) -> str:
        """Determine quest difficulty from quest element"""
        # Try to get difficulty from attributes or infer from other data
        difficulty = getattr(quest_element, 'difficulty', 'Medium')

        if difficulty not in ['Very Easy', 'Easy', 'Medium', 'Hard', 'Very Hard']:
            # Infer difficulty from quest ID or other attributes
            quest_id = getattr(quest_element, 'quest_id', 0)

            if quest_id < 100:
                difficulty = 'Easy'
            elif quest_id < 500:
                difficulty = 'Medium'
            elif quest_id < 1000:
                difficulty = 'Hard'
            else:
                difficulty = 'Very Hard'

        return difficulty

    def _extract_quest_giver(self, quest_element) -> Dict[str, Any]:
        """Extract quest giver information"""
        giver = {}

        # Try to get giver from various attributes
        giver_name = getattr(quest_element, 'quest_giver_name', None)
        giver_npc = getattr(quest_element, 'quest_giver_npc', None)
        giver_location = getattr(quest_element, 'quest_giver_location', None)

        if giver_name:
            giver['name'] = giver_name
        if giver_npc:
            giver['npc_id'] = giver_npc
        if giver_location:
            giver['location'] = giver_location

        # If no giver found, provide default
        if not giver:
            giver = {
                'name': 'Unknown',
                'npc_id': None,
                'location': 'Unknown'
            }

        return giver

    def _extract_requirements(self, quest_element) -> List[Dict[str, Any]]:
        """Extract quest requirements"""
        requirements = []

        # Extract level requirements
        min_level = getattr(quest_element, 'min_level', None)
        if min_level:
            requirements.append({
                'type': 'level',
                'value': min_level,
                'operator': '>=',
                'description': f'Minimum level {min_level}'
            })

        # Extract item requirements
        required_items = getattr(quest_element, 'required_items', [])
        if required_items:
            for item in required_items:
                requirements.append({
                    'type': 'item',
                    'item_id': getattr(item, 'item_id', 0),
                    'count': getattr(item, 'count', 1),
                    'description': f'Require {getattr(item, "count", 1)}x {getattr(item, "name", "Item")}'
                })

        # Extract quest prerequisites
        prerequisites = getattr(quest_element, 'prerequisites', [])
        for prereq in prerequisites:
            prereq_id = getattr(prereq, 'quest_id', 0)
            if prereq_id:
                requirements.append({
                    'type': 'quest',
                    'quest_id': prereq_id,
                    'state': getattr(prereq, 'state', 'solved'),
                    'description': f'Must complete quest {prereq_id}'
                })

        return requirements

    def _extract_objectives(self, quest_element) -> List[Dict[str, Any]]:
        """Extract quest objectives"""
        objectives = []

        # Get objectives from quest element
        quest_objectives = getattr(quest_element, 'objectives', [])

        for obj in quest_objectives:
            objective = {
                'id': getattr(obj, 'id', f'obj_{len(objectives)}'),
                'description': self.data_model.get_localised_text(obj, 'description') or getattr(obj, 'description', 'Objective'),
                'type': getattr(obj, 'type', 'custom'),
                'target': getattr(obj, 'target', None),
                'count': getattr(obj, 'count', 1),
                'completed': getattr(obj, 'completed', False)
            }
            objectives.append(objective)

        # If no objectives found, create a default one
        if not objectives:
            objectives.append({
                'id': 'obj_default',
                'description': 'Complete the quest',
                'type': 'custom',
                'target': None,
                'count': 1,
                'completed': False
            })

        return objectives

    def _extract_rewards(self, quest_element) -> Dict[str, Any]:
        """Extract quest rewards"""
        rewards = {
            'experience': getattr(quest_element, 'experience_reward', 0),
            'gold': getattr(quest_element, 'gold_reward', 0),
            'silver': getattr(quest_element, 'silver_reward', 0),
            'copper': getattr(quest_element, 'copper_reward', 0),
            'items': [],
            'faction_reputation': {},
            'skill_points': getattr(quest_element, 'skill_points', 0)
        }

        # Extract item rewards
        item_rewards = getattr(quest_element, 'item_rewards', [])
        for item in item_rewards:
            rewards['items'].append({
                'item_id': getattr(item, 'item_id', 0),
                'count': getattr(item, 'count', 1),
                'name': getattr(item, 'name', 'Unknown Item')
            })

        # Extract faction rewards
        faction_rewards = getattr(quest_element, 'faction_rewards', [])
        for faction in faction_rewards:
            faction_name = getattr(faction, 'faction_name', 'Unknown')
            reputation = getattr(faction, 'reputation', 0)
            if reputation != 0:
                rewards['faction_reputation'][faction_name] = reputation

        return rewards

    def _extract_map_locations(self, quest_element) -> List[Dict[str, Any]]:
        """Extract map locations"""
        locations = []

        # Get map locations from quest element
        map_locations = getattr(quest_element, 'map_locations', [])

        for loc in map_locations:
            location = {
                'code': getattr(loc, 'platform_code', ''),
                'name': getattr(loc, 'name', 'Unknown Location'),
                'x': getattr(loc, 'x', 0),
                'y': getattr(loc, 'y', 0),
                'type': getattr(loc, 'type', 'general')
            }
            locations.append(location)

        return locations

    def _extract_dialogues(self, quest_element) -> List[Dict[str, Any]]:
        """Extract basic dialogue information"""
        dialogues = []

        # Get dialogues from quest element
        quest_dialogues = getattr(quest_element, 'dialogues', [])

        for dialogue in quest_dialogues:
            dialogue_info = {
                'text': self.data_model.get_localised_text(dialogue, 'text') or getattr(dialogue, 'text', ''),
                'speaker': getattr(dialogue, 'speaker', 'Unknown'),
                'translation': getattr(dialogue, 'translation', ''),
                'source_file': getattr(dialogue, 'source_file', ''),
                'dialogue_type': getattr(dialogue, 'dialogue_type', 'Dialog'),
                'answer_id': getattr(dialogue, 'answer_id', None)
            }
            dialogues.append(dialogue_info)

        return dialogues

    def _extract_dialogue_tree(self, quest_element) -> Dict[str, Any]:
        """Extract dialogue tree structure for enhanced editor"""
        # This is a simplified version - in a full implementation,
        # you would parse the actual LUA files or dialogue data

        dialogue_tree = {
            'nodes': {},
            'start_node_id': ''
        }

        # Get dialogues from quest element
        quest_dialogues = getattr(quest_element, 'dialogues', [])

        if quest_dialogues:
            # Create a simple linear dialogue tree
            start_node_id = f'quest_{quest_element.quest_id}_start'

            # Create start node
            dialogue_tree['nodes'][start_node_id] = {
                'node_id': start_node_id,
                'node_type': 'npc',
                'speaker': quest_dialogues[0].get('speaker', 'Quest Giver'),
                'text': quest_dialogues[0].get('text', 'Welcome to the quest!'),
                'conditions': [],
                'actions': [
                    {
                        'action_type': 'quest_begin',
                        'params': {'quest_id': quest_element.quest_id},
                        'description': f'Begin quest {quest_element.quest_id}'
                    }
                ],
                'choices': [
                    {
                        'choice_id': 1,
                        'text': 'I accept this quest!',
                        'next_node_id': f'quest_{quest_element.quest_id}_accept',
                        'conditions': [],
                        'actions': []
                    },
                    {
                        'choice_id': 2,
                        'text': 'I need more information.',
                        'next_node_id': f'quest_{quest_element.quest_id}_info',
                        'conditions': [],
                        'actions': []
                    }
                ]
            }

            # Create accept node
            accept_node_id = f'quest_{quest_element.quest_id}_accept'
            dialogue_tree['nodes'][accept_node_id] = {
                'node_id': accept_node_id,
                'node_type': 'response',
                'speaker': quest_dialogues[0].get('speaker', 'Quest Giver'),
                'text': 'Excellent! Here are the details of what you need to do.',
                'answer_id': 1,
                'conditions': [],
                'actions': [],
                'choices': []
            }

            # Create info node
            info_node_id = f'quest_{quest_element.quest_id}_info'
            dialogue_tree['nodes'][info_node_id] = {
                'node_id': info_node_id,
                'node_type': 'response',
                'speaker': quest_dialogues[0].get('speaker', 'Quest Giver'),
                'text': 'This is an important quest that will help the people of this land.',
                'answer_id': 2,
                'conditions': [],
                'actions': [],
                'choices': [
                    {
                        'choice_id': 10,
                        'text': 'I understand. I will help.',
                        'next_node_id': accept_node_id,
                        'conditions': [],
                        'actions': []
                    }
                ]
            }

            dialogue_tree['start_node_id'] = start_node_id

        return dialogue_tree

    def _extract_variables(self, quest_element) -> List[Dict[str, Any]]:
        """Extract quest variables and flags"""
        variables = []

        # Extract quest flags
        quest_flags = getattr(quest_element, 'flags', [])
        for flag in quest_flags:
            flag_name = getattr(flag, 'name', '')
            if flag_name:
                variables.append({
                    'name': flag_name,
                    'type': 'flag',
                    'initial_value': getattr(flag, 'initial_value', False),
                    'scope': 'quest',
                    'description': getattr(flag, 'description', f'Quest flag: {flag_name}')
                })

        # Add standard quest flags
        quest_id = getattr(quest_element, 'quest_id', 0)
        variables.extend([
            {
                'name': f'Quest{quest_id}Started',
                'type': 'flag',
                'initial_value': False,
                'scope': 'global',
                'description': f'Quest {quest_id} has been started'
            },
            {
                'name': f'Quest{quest_id}Completed',
                'type': 'flag',
                'initial_value': False,
                'scope': 'global',
                'description': f'Quest {quest_id} has been completed'
            }
        ])

        return variables


class QuestViewerIntegration(QObject):
    """Integration manager for viewing existing quests in the enhanced quest editor"""

    # Signals
    quest_loaded = Signal(dict)  # Quest data loaded and ready for viewing
    quest_view_error = Signal(str)  # Error occurred during quest loading

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.quest_processor = QuestDataProcessor(data_model)
        self.quest_editor = None
        self.current_quest_id = None

    def set_quest_editor(self, quest_editor):
        """Set the quest editor instance"""
        self.quest_editor = quest_editor

    def load_quest_for_viewing(self, quest_id: int) -> bool:
        """Load a quest for viewing in the editor"""
        try:
            # Get quest element from data model
            quests = self.data_model.get_elements("quests")
            quest_element = None

            for quest in quests:
                if getattr(quest, 'quest_id', None) == quest_id:
                    quest_element = quest
                    break

            if not quest_element:
                self.quest_view_error.emit(f"Quest with ID {quest_id} not found")
                return False

            # Process quest data
            quest_data = self.quest_processor.process_quest_data(quest_element)
            if not quest_data:
                self.quest_view_error.emit(f"Failed to process quest data for quest {quest_id}")
                return False

            # Load into quest editor
            if self.quest_editor:
                self._load_quest_into_editor(quest_data)
                self.current_quest_id = quest_id
                self.quest_loaded.emit(quest_data)
                return True
            else:
                self.quest_view_error.emit("Quest editor not available")
                return False

        except Exception as e:
            error_msg = f"Error loading quest {quest_id}: {str(e)}"
            logger.error(error_msg)
            self.quest_view_error.emit(error_msg)
            return False

    def _load_quest_into_editor(self, quest_data: Dict[str, Any]):
        """Load processed quest data into the enhanced quest editor"""
        try:
            if not self.quest_editor or not hasattr(self.quest_editor, 'set_quest_data'):
                # Fallback: try to update individual UI components
                self._load_quest_into_ui_fallback(quest_data)
                return

            # Use the enhanced quest editor's set_quest_data method
            self.quest_editor.set_quest_data(quest_data)

            # Update editor status
            if hasattr(self.quest_editor, 'status_label'):
                self.quest_editor.status_label.setText(
                    f"Viewing quest: {quest_data['name']} (ID: {quest_data['quest_id']})"
                )

            # Mark as read-only mode if available
            self._set_read_only_mode(True)

        except Exception as e:
            logger.error(f"Error loading quest into editor: {e}")
            self._load_quest_into_ui_fallback(quest_data)

    def _load_quest_into_ui_fallback(self, quest_data: Dict[str, Any]):
        """Fallback method to load quest data into UI components directly"""
        try:
            # Update basic quest information
            if hasattr(self.quest_editor, 'quest_id_spin'):
                self.quest_editor.quest_id_spin.setValue(quest_data['quest_id'])
                self.quest_editor.quest_id_spin.setReadOnly(True)

            if hasattr(self.quest_editor, 'quest_name_edit'):
                self.quest_editor.quest_name_edit.setText(quest_data['name'])
                self.quest_editor.quest_name_edit.setReadOnly(True)

            if hasattr(self.quest_editor, 'quest_description_edit'):
                self.quest_editor.quest_description_edit.setPlainText(quest_data['description'])
                self.quest_editor.quest_description_edit.setReadOnly(True)

            # Update quest type and difficulty
            if hasattr(self.quest_editor, 'quest_type_combo'):
                index = self.quest_editor.quest_type_combo.findText(quest_data['quest_type'])
                if index >= 0:
                    self.quest_editor.quest_type_combo.setCurrentIndex(index)
                self.quest_editor.quest_type_combo.setEnabled(False)

            if hasattr(self.quest_editor, 'quest_difficulty_combo'):
                index = self.quest_editor.quest_difficulty_combo.findText(quest_data['difficulty'])
                if index >= 0:
                    self.quest_editor.quest_difficulty_combo.setCurrentIndex(index)
                self.quest_editor.quest_difficulty_combo.setEnabled(False)

            # Load dialogue data if available
            if 'dialogue_data' in quest_data and hasattr(self.quest_editor, 'enhanced_dialogue_editor'):
                self.quest_editor.enhanced_dialogue_editor.set_dialogue_data(quest_data['dialogue_data'])
                # Set read-only mode for dialogue editor
                if hasattr(self.quest_editor.enhanced_dialogue_editor, 'set_read_only'):
                    self.quest_editor.enhanced_dialogue_editor.set_read_only(True)

            # Update status
            if hasattr(self.quest_editor, 'status_label'):
                self.quest_editor.status_label.setText(
                    f"Viewing quest: {quest_data['name']} (Read-Only Mode)"
                )

        except Exception as e:
            logger.error(f"Error in fallback quest loading: {e}")

    def _set_read_only_mode(self, read_only: bool):
        """Set read-only mode for the quest editor"""
        try:
            # Disable editing controls
            if hasattr(self.quest_editor, 'save_quest_btn'):
                self.quest_editor.save_quest_btn.setEnabled(not read_only)

            if hasattr(self.quest_editor, 'validate_btn'):
                self.quest_editor.validate_btn.setEnabled(not read_only)

            if hasattr(self.quest_editor, 'test_btn'):
                self.quest_editor.test_btn.setEnabled(not read_only)

            # Enable view-only controls
            if hasattr(self.quest_editor, 'preview_btn'):
                self.quest_editor.preview_btn.setEnabled(True)

            if hasattr(self.quest_editor, 'export_lua_btn'):
                self.quest_editor.export_lua_btn.setEnabled(True)

        except Exception as e:
            logger.error(f"Error setting read-only mode: {e}")

    def enable_editing_mode(self):
        """Enable editing mode for the current quest"""
        try:
            if self.quest_editor:
                # Re-enable editing controls
                if hasattr(self.quest_editor, 'save_quest_btn'):
                    self.quest_editor.save_quest_btn.setEnabled(True)

                if hasattr(self.quest_editor, 'validate_btn'):
                    self.quest_editor.validate_btn.setEnabled(True)

                if hasattr(self.quest_editor, 'test_btn'):
                    self.quest_editor.test_btn.setEnabled(True)

                # Make UI components editable
                if hasattr(self.quest_editor, 'quest_name_edit'):
                    self.quest_editor.quest_name_edit.setReadOnly(False)

                if hasattr(self.quest_editor, 'quest_description_edit'):
                    self.quest_editor.quest_description_edit.setReadOnly(False)

                # Update status
                if hasattr(self.quest_editor, 'status_label'):
                    self.quest_editor.status_label.setText(
                        f"Editing quest: {self.quest_editor.quest_name_edit.text()}"
                    )

        except Exception as e:
            logger.error(f"Error enabling editing mode: {e}")

    def get_current_quest_id(self) -> Optional[int]:
        """Get the currently loaded quest ID"""
        return self.current_quest_id

    def refresh_current_quest(self) -> bool:
        """Refresh the currently loaded quest from the data model"""
        if self.current_quest_id:
            return self.load_quest_for_viewing(self.current_quest_id)
        return False

    def export_current_quest(self, format_type: str = 'json') -> Optional[str]:
        """Export the current quest data"""
        try:
            if not self.quest_editor or not self.current_quest_id:
                return None

            # Get current quest data
            if hasattr(self.quest_editor, 'get_quest_data'):
                quest_data = self.quest_editor.get_quest_data()
            else:
                # Fallback to data model
                quests = self.data_model.get_elements("quests")
                quest_data = None
                for quest in quests:
                    if getattr(quest, 'quest_id', None) == self.current_quest_id:
                        quest_data = self.quest_processor.process_quest_data(quest)
                        break

            if not quest_data:
                return None

            # Export in requested format
            if format_type.lower() == 'json':
                return json.dumps(quest_data, indent=2, ensure_ascii=False)
            elif format_type.lower() == 'summary':
                return self._generate_quest_summary(quest_data)
            else:
                return json.dumps(quest_data, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Error exporting quest: {e}")
            return None

    def _generate_quest_summary(self, quest_data: Dict[str, Any]) -> str:
        """Generate a text summary of the quest"""
        try:
            summary_lines = [
                f"Quest Summary: {quest_data['name']}",
                "=" * 50,
                f"ID: {quest_data['quest_id']}",
                f"Type: {quest_data['quest_type']}",
                f"Difficulty: {quest_data['difficulty']}",
                f"Priority: {quest_data.get('priority', 5)}",
                f"Status: {quest_data.get('status', 'Unknown')}",
                "",
                "Description:",
                quest_data['description'],
                ""
            ]

            # Add objectives
            if 'objectives' in quest_data and quest_data['objectives']:
                summary_lines.extend([
                    "Objectives:",
                    "-" * 20
                ])
                for i, obj in enumerate(quest_data['objectives'], 1):
                    status = "✓" if obj.get('completed', False) else "○"
                    summary_lines.append(f"{status} {obj['description']}")
                summary_lines.append("")

            # Add requirements
            if 'requirements' in quest_data and quest_data['requirements']:
                summary_lines.extend([
                    "Requirements:",
                    "-" * 20
                ])
                for req in quest_data['requirements']:
                    summary_lines.append(f"• {req.get('description', 'Unknown requirement')}")
                summary_lines.append("")

            # Add rewards
            if 'rewards' in quest_data:
                rewards = quest_data['rewards']
                reward_lines = ["Rewards:", "-" * 20]

                if rewards.get('experience', 0) > 0:
                    reward_lines.append(f"• {rewards['experience']} Experience")

                total_money = rewards.get('gold', 0) * 100 + rewards.get('silver', 0) * 10 + rewards.get('copper', 0)
                if total_money > 0:
                    reward_lines.append(f"• {total_money} Gold")

                if rewards.get('items'):
                    for item in rewards['items']:
                        count = item.get('count', 1)
                        name = item.get('name', f'Item {item.get("item_id", 0)}')
                        reward_lines.append(f"• {count}x {name}")

                if len(reward_lines) > 2:
                    summary_lines.extend(reward_lines)
                    summary_lines.append("")

            # Add quest giver
            if 'quest_giver' in quest_data and quest_data['quest_giver']:
                giver = quest_data['quest_giver']
                summary_lines.extend([
                    "Quest Giver:",
                    "-" * 20,
                    f"• {giver.get('name', 'Unknown')}"
                ])
                if giver.get('location'):
                    summary_lines.append(f"• Location: {giver['location']}")
                summary_lines.append("")

            return "\n".join(summary_lines)

        except Exception as e:
            logger.error(f"Error generating quest summary: {e}")
            return f"Error generating summary: {str(e)}"


class QuestViewerWidget(QWidget):
    """Complete quest viewer widget with integrated enhanced quest editor"""

    def __init__(self, data_model, parent=None):
        super().__init__(parent)
        self.data_model = data_model
        self.viewer_integration = QuestViewerIntegration(data_model)
        self.quest_editor = None

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header with controls
        header_widget = self._create_header()
        layout.addWidget(header_widget)

        # Main quest editor
        self.quest_editor = self._create_quest_editor()
        layout.addWidget(self.quest_editor)

        # Set up integration
        self.viewer_integration.set_quest_editor(self.quest_editor)

    def _create_header(self) -> QWidget:
        """Create header controls"""
        header = QWidget()
        header_layout = QHBoxLayout(header)

        # Title
        self.title_label = QLabel("Quest Viewer")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(self.title_label)

        header_layout.addStretch()

        # Mode toggle
        self.mode_toggle = QPushButton("Enable Editing")
        self.mode_toggle.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        header_layout.addWidget(self.mode_toggle)

        # Export button
        self.export_btn = QPushButton("Export Quest")
        header_layout.addWidget(self.export_btn)

        # Refresh button
        self.refresh_btn = QPushButton("Refresh")
        header_layout.addWidget(self.refresh_btn)

        return header

    def _create_quest_editor(self) -> QWidget:
        """Create the enhanced quest editor"""
        if UnifiedEnhancedQuestEditor:
            return UnifiedEnhancedQuestEditor(self)
        else:
            # Fallback widget
            fallback = QWidget()
            layout = QVBoxLayout(fallback)

            error_label = QLabel("Enhanced Quest Editor not available")
            error_label.setStyleSheet("color: red; font-weight: bold;")
            layout.addWidget(error_label)

            info_label = QLabel("Please ensure all required components are installed.")
            layout.addWidget(info_label)

            return fallback

    def setup_connections(self):
        """Setup signal connections"""
        # Header controls
        self.mode_toggle.clicked.connect(self._toggle_editing_mode)
        self.export_btn.clicked.connect(self._export_quest)
        self.refresh_btn.clicked.connect(self._refresh_quest)

        # Integration signals
        self.viewer_integration.quest_loaded.connect(self._on_quest_loaded)
        self.viewer_integration.quest_view_error.connect(self._on_quest_error)

    def load_quest(self, quest_id: int) -> bool:
        """Load a quest for viewing"""
        return self.viewer_integration.load_quest_for_viewing(quest_id)

    def _toggle_editing_mode(self):
        """Toggle between viewing and editing modes"""
        if self.mode_toggle.text() == "Enable Editing":
            self.viewer_integration.enable_editing_mode()
            self.mode_toggle.setText("Read-Only Mode")
            self.mode_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            self.title_label.setText("Quest Editor")
        else:
            self.viewer_integration._set_read_only_mode(True)
            self.mode_toggle.setText("Enable Editing")
            self.mode_toggle.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 5px 15px;
                    border-radius: 3px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            self.title_label.setText("Quest Viewer")

    def _export_quest(self):
        """Export the current quest"""
        try:
            export_data = self.viewer_integration.export_current_quest('summary')
            if export_data:
                # Show export dialog
                dialog = QDialog(self)
                dialog.setWindowTitle("Quest Export")
                dialog.setMinimumSize(800, 600)

                layout = QVBoxLayout(dialog)

                text_edit = QTextEdit()
                text_edit.setPlainText(export_data)
                text_edit.setReadOnly(True)
                layout.addWidget(text_edit)

                buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Save)
                buttons.accepted.connect(dialog.accept)
                # buttons.accepted.connect(lambda: self._save_export_to_file(export_data))  # TODO: Implement
                layout.addWidget(buttons)

                dialog.exec()
            else:
                QMessageBox.warning(self, "Export Error", "No quest data available for export.")

        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export quest: {str(e)}")

    def _refresh_quest(self):
        """Refresh the current quest"""
        if self.viewer_integration.refresh_current_quest():
            QMessageBox.information(self, "Refresh", "Quest data refreshed successfully.")
        else:
            QMessageBox.warning(self, "Refresh", "No quest is currently loaded for refresh.")

    def _on_quest_loaded(self, quest_data: Dict[str, Any]):
        """Handle quest loaded signal"""
        self.title_label.setText(f"Quest Viewer - {quest_data['name']}")

    def _on_quest_error(self, error_message: str):
        """Handle quest error signal"""
        QMessageBox.critical(self, "Quest Loading Error", error_message)
        self.title_label.setText("Quest Viewer - Error")