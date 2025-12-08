#!/usr/bin/env python3
"""
Enhanced Quest Creation Wizard

An integrated quest creation system that combines:
- Quest identity and hierarchy setup
- Visual dialogue editing
- Reward configuration with CFF integration
- Lua script generation
- Direct GameData.cff saving

This is the main entry point for the enhanced quest creation system.
"""

import sys
from pathlib import Path
from typing import Optional, Dict, List, Any, Tuple

from PySide6.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QPushButton,
    QLabel, QGroupBox, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QRadioButton, QButtonGroup, QProgressBar, QTabWidget,
    QSplitter, QTreeWidget, QTreeWidgetItem, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, Signal, QThread, Slot, QObject
from PySide6.QtGui import QIntValidator, QFont

# Add to path and imports
try:
    project_root = Path(__file__).parent.parent.parent.parent.parent
    sys.path.insert(0, str(project_root / "src"))
    
    from TirganachReloaded.cff_editor.data_model import CFFDataModel
    from TirganachReloaded.cff_editor.logging_config import get_logger
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData, QuestReward, Dialogue, MapLocation
    from TirganachReloaded.cff_editor.widgets.quest_creation_wizard import (
        QuestIdentityPage, QuestHierarchyPage, QuestLocationPage, 
        QuestObjectivesPage, QuestRewardsPage
    )
    
    # Import our new components (with error handling)
    dialogue_editor_available = False
    reward_builder_available = False
    quest_validator_available = False
    
    try:
        from .dialogue_editor import DialogueTreeEditor
        dialogue_editor_available = True
    except ImportError as e:
        print(f"Warning: Dialogue editor not available: {e}")
        DialogueTreeEditor = None
    
    try:
        from .reward_builder import RewardBuilderWidget
        reward_builder_available = True
    except ImportError as e:
        print(f"Warning: Reward builder not available: {e}")
        RewardBuilderWidget = None
    
    try:
        from .quest_validator import QuestValidator
        quest_validator_available = True
    except ImportError as e:
        print(f"Warning: Quest validator not available: {e}")
        QuestValidator = None
    
except ImportError as e:
    print(f"Import error: {e}")
    # Create stub classes for testing
    EnhancedQuestData = None
    QuestReward = None
    Dialogue = None
    MapLocation = None
    DialogueTreeEditor = None
    RewardBuilderWidget = None
    QuestValidator = None


# Platform mappings
PLATFORM_NAMES = {
    "P1": "Liannon", "P2": "Eloni", "P3": "Leafshade", "P4": "Wildland Pass",
    "P5": "Shiel", "P7": "Ice Gate", "P8": "Gol Halad", "P9": "Gate of Swords",
    "P10": "Murmuring Valley", "P11": "Fire Peak", "P12": "Iron Fields",
    "P13": "The Abyss", "P14": "Fastholme", "P15": "The Refuge",
    "P16": "Dream Shrine", "P17": "Undergound", "P18": "Gate of Justice",
    "P19": "Needle", "P20": "Whisper", "P21": "Windwall Fog", "P22": "Steel Shore",
    "P23": "The Shattered", "P24": "Magnet Stones", "P25": "Golden Fields",
    "P26": "Mor Duine", "P27": "City of Souls", "P32": "Soul Forge",
    "P33": "Tower of Souls", "P35": "City Ship"
}


class QuestSaverWorker(QObject):
    """Worker for saving quests to CFF in background thread"""
    
    progress_updated = Signal(int)  # Progress percentage
    finished = Signal(bool, str)  # Success, message
    
    def __init__(self, data_model, quest_data):
        super().__init__()
        self.data_model = data_model
        self.quest_data = quest_data
        try:
            self.logger = get_logger("quest_saver")
        except:
            import logging
            self.logger = logging.getLogger("quest_saver")
    
    def save_quest(self):
        """Save quest to CFF file"""
        try:
            self.progress_updated.emit(10)
            
            # Validate quest data
            if quest_validator_available and QuestValidator:
                validator = QuestValidator()
                is_valid, errors = validator.validate_quest(self.quest_data)
                if not is_valid:
                    self.finished.emit(False, f"Validation failed: {'; '.join(errors)}")
                    return
            
            self.progress_updated.emit(30)
            
            # Add quest to CFF data model
            quest_element = self._create_quest_element()
            self.data_model.add_element("quests", quest_element)
            
            self.progress_updated.emit(60)
            
            # Save CFF file
            try:
                cff_path = project_root / "OriginalGameFiles/data/GameData.cff"
                if not self.data_model.save_file(str(cff_path)):
                    self.finished.emit(False, "Failed to save GameData.cff")
                    return
            except Exception as e:
                self.finished.emit(False, f"CFF save error: {str(e)}")
                return
            
            self.progress_updated.emit(90)
            
            # Generate Lua script
            lua_script = self._generate_lua_script()
            try:
                lua_path = project_root / f"ModdedGameFiles/lua/quest_{self.quest_data.quest_id}.lua"
                lua_path.parent.mkdir(parents=True, exist_ok=True)
                
                with open(lua_path, 'w', encoding='utf-8') as f:
                    f.write(lua_script)
                
                success_message = f"Quest saved successfully!\nLua script: {lua_path}"
            except Exception as e:
                success_message = f"Quest saved to CFF (Lua script error: {str(e)})"
            
            self.progress_updated.emit(100)
            self.finished.emit(True, success_message)
            
        except Exception as e:
            try:
                self.logger.exception("Failed to save quest")
            except:
                import traceback
                traceback.print_exc()
            self.finished.emit(False, f"Failed to save quest: {str(e)}")
    
    def _create_quest_element(self):
        """Create quest element for CFF data model"""
        # Create quest element with proper structure
        quest_element = type('QuestElement', (), {})()
        
        # Basic properties
        quest_element.quest_id = self.quest_data.quest_id
        quest_element.name = self.quest_data.name
        quest_element.description = self.quest_data.description
        quest_element.parent_quest_id = self.quest_data.parent_id
        quest_element.order_index = self.quest_data.order_index
        
        # Localization IDs (generate new ones)
        quest_element.name_id = self._generate_string_id()
        quest_element.description_id = self._generate_string_id()
        
        return quest_element
    
    def _generate_string_id(self):
        """Generate unique string ID for localization"""
        existing_ids = set()
        try:
            elements = self.data_model.get_elements("quests") or []
            for element in elements:
                if hasattr(element, 'name_id'):
                    existing_ids.add(element.name_id)
                if hasattr(element, 'description_id'):
                    existing_ids.add(element.description_id)
        except:
            pass
        
        # Find first available ID starting from 50000 (custom range)
        for i in range(50000, 60000):
            if i not in existing_ids:
                return i
        
        return 50000
    
    def _generate_lua_script(self):
        """Generate Lua quest script"""
        if not self.quest_data:
            return "-- No quest data available"
        
        script = f'''-- Generated Quest Script: {self.quest_data.name}
-- Quest ID: {self.quest_data.quest_id}
-- Platform: {self.quest_data.map_locations[0].code if self.quest_data.map_locations else "Unknown"}

function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)
BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

-- Quest: {self.quest_data.name}
-- ID: {self.quest_data.quest_id}

-- Initialize quest when conditions are met
OnOneTimeEvent
{{
    EventName = "Init_{self.quest_data.name.replace(' ', '')}",
    Conditions = 
    {{
        -- Add prerequisites here
    }},
    Actions = 
    {{
        -- Begin the quest
        QuestBegin{{QuestId = {self.quest_data.quest_id}}},
        -- Add quest to journal
        Outcry{{
            NpcId = 0,  -- Player
            String = "{self.quest_data.name}: {self.quest_data.description[:100]}...",
            Color = ColorYellow
        }},
    }}
}}

-- Quest completion conditions
OnOneTimeEvent
{{
    EventName = "Complete_{self.quest_data.name.replace(' ', '')}",
    Conditions = 
    {{
        QuestState{{QuestId = {self.quest_data.quest_id}, State = StateActive}},
        -- Add completion conditions here
    }},
    Actions = 
    {{
        -- Complete the quest
        QuestSolve{{QuestId = {self.quest_data.quest_id}}},
        -- Grant rewards
        SetRewardFlagTrue{{Name = "Quest{self.quest_data.quest_id}Reward"}},
        -- Success message
        Outcry{{
            NpcId = 0,
            String = "Quest completed: {self.quest_data.name}!",
            Color = ColorGreen
        }},
    }}
}}

EndDefinition()
end
'''
        return script


class EnhancedQuestCreationWizard(QWizard):
    """Enhanced Quest Creation Wizard with full integration"""
    
    quest_created = Signal(dict)  # Emitted when quest is successfully created and saved
    
    def __init__(self, data_model, quest_data, parent=None):
        super().__init__(parent)
        
        self.data_model = data_model
        self.quest_data = quest_data  # Reference to existing quests
        try:
            self.logger = get_logger("enhanced_quest_wizard")
        except:
            import logging
            self.logger = logging.getLogger("enhanced_quest_wizard")
        
        self.next_quest_id = self._generate_quest_id()
        
        # Storage for wizard data
        self.wizard_data = {}
        
        self.setWindowTitle("Enhanced Quest Creation Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setOption(QWizard.HaveHelpButton, True)
        self.setMinimumSize(900, 700)
        
        self._setup_ui()
        self._setup_connections()
    
    def _setup_ui(self):
        """Setup wizard UI"""
        # Create custom pages
        self.identity_page = QuestIdentityPage(self)
        self.hierarchy_page = QuestHierarchyPage(self)
        self.location_page = QuestLocationPage(self)
        self.objectives_page = QuestObjectivesPage(self)
        
        # Create enhanced pages (with fallbacks)
        self.dialogue_page = self._create_dialogue_page()
        self.rewards_page = self._create_rewards_page()
        self.summary_page = self._create_summary_page()
        
        # Add pages to wizard
        self.addPage(self.identity_page)
        self.addPage(self.hierarchy_page)
        self.addPage(self.location_page)
        self.addPage(self.objectives_page)
        self.addPage(self.dialogue_page)
        self.addPage(self.rewards_page)
        self.addPage(self.summary_page)
    
    def _create_dialogue_page(self):
        """Create enhanced dialogue page"""
        page = QWizardPage()
        page.setTitle("Quest Dialogues")
        page.setSubTitle("Design dialogue flow for this quest")
        
        layout = QVBoxLayout(page)
        
        if dialogue_editor_available and DialogueTreeEditor:
            # Add dialogue tree editor
            self.dialogue_editor = DialogueTreeEditor(page)
            layout.addWidget(self.dialogue_editor)
        else:
            # Fallback: simple text editor
            layout.addWidget(QLabel("Dialogue Editor (Basic Mode - Advanced editor not available)"))
            self.dialogue_text = QTextEdit()
            self.dialogue_text.setPlaceholderText("Enter basic dialogue text here...")
            self.dialogue_text.setMaximumHeight(200)
            layout.addWidget(self.dialogue_text)
        
        return page
    
    def _create_rewards_page(self):
        """Create enhanced rewards page"""
        page = QWizardPage()
        page.setTitle("Quest Rewards")
        page.setSubTitle("Configure rewards and quest completion")
        
        layout = QVBoxLayout(page)
        
        if reward_builder_available and RewardBuilderWidget:
            # Add reward builder
            self.reward_builder = RewardBuilderWidget(self.data_model, page)
            layout.addWidget(self.reward_builder)
        else:
            # Fallback: basic reward configuration
            layout.addWidget(QLabel("Reward Configuration (Basic Mode - Item browser not available)"))
            
            reward_form = QFormLayout()
            
            self.xp_spin = QSpinBox()
            self.xp_spin.setRange(0, 999999)
            reward_form.addRow("Experience Points:", self.xp_spin)
            
            self.gold_spin = QSpinBox()
            self.gold_spin.setRange(0, 999999)
            reward_form.addRow("Gold:", self.gold_spin)
            
            self.silver_spin = QSpinBox()
            self.silver_spin.setRange(0, 99)
            reward_form.addRow("Silver:", self.silver_spin)
            
            self.copper_spin = QSpinBox()
            self.copper_spin.setRange(0, 99)
            reward_form.addRow("Copper:", self.copper_spin)
            
            layout.addLayout(reward_form)
        
        return page
    
    def _create_summary_page(self):
        """Create summary and save page"""
        page = QWizardPage()
        page.setTitle("Summary & Save")
        page.setSubTitle("Review quest details and save to game")
        
        layout = QVBoxLayout(page)
        
        # Summary display
        summary_group = QGroupBox("Quest Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMaximumHeight(200)
        summary_layout.addWidget(self.summary_text)
        
        layout.addWidget(summary_group)
        
        # Save progress
        save_group = QGroupBox("Save Quest")
        save_layout = QVBoxLayout(save_group)
        
        self.save_progress = QProgressBar()
        self.save_progress.setVisible(False)
        save_layout.addWidget(self.save_progress)
        
        self.save_status = QLabel("")
        save_layout.addWidget(self.save_status)
        
        layout.addWidget(save_group)
        
        layout.addStretch()
        
        # Register fields for validation
        page.registerField("summaryComplete*", self.summary_text)
        
        return page
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Custom button handling
        self.helpRequested.connect(self.show_help)
        
        # Update summary when page changes
        self.currentIdChanged.connect(self.update_summary)
    
    def _generate_quest_id(self):
        """Generate next available quest ID in custom range (9000-9999)"""
        custom_ids = [qid for qid in self.quest_data.keys() if 9000 <= qid <= 9999]
        if custom_ids:
            return max(custom_ids) + 1
        return 9000
    
    def show_help(self):
        """Show help for current page"""
        current_page = self.currentPage()
        
        help_texts = {
            "Quest Identity": "Enter basic quest information. Quest ID is automatically generated.",
            "Quest Hierarchy": "Set parent quest relationships for sub-quests.",
            "Location & Quest Giver": "Specify where the quest takes place and which NPC gives it.",
            "Objectives & Requirements": "Define what the player needs to do and any prerequisites.",
            "Quest Dialogues": "Create dialogue trees using the editor. Advanced features require all components.",
            "Quest Rewards": "Configure rewards. Advanced item browser requires all components.",
            "Summary & Save": "Review all quest details before saving to GameData.cff."
        }
        
        help_text = help_texts.get(current_page.title(), "No help available for this page.")
        QMessageBox.information(self, "Help", help_text)
    
    def update_summary(self, page_id):
        """Update summary when showing summary page"""
        page = self.page(page_id)
        if page.title() == "Summary & Save":
            summary = self._generate_summary()
            self.summary_text.setHtml(summary)
    
    def _generate_summary(self):
        """Generate HTML summary of quest data"""
        html = "<html><body style='font-family: Arial; font-size: 10pt;'>"
        html += f"<h3>Quest Summary</h3>"
        
        # Basic info
        html += f"<p><b>ID:</b> {self.next_quest_id}</p>"
        html += f"<p><b>Name:</b> {self.field('questName') or 'Not set'}</p>"
        
        # Location
        platform = self.field("platform")
        if platform:
            html += f"<p><b>Location:</b> {PLATFORM_NAMES.get(platform, platform)} ({platform})</p>"
        
        # Objectives count
        if hasattr(self.objectives_page, 'objectives_list'):
            obj_count = self.objectives_page.objectives_list.count()
            html += f"<p><b>Objectives:</b> {obj_count}</p>"
        
        # Rewards
        if hasattr(self, 'reward_builder') and self.reward_builder:
            rewards = self.reward_builder.get_rewards()
            if rewards:
                html += f"<p><b>XP:</b> {rewards.get('xp', 0)}</p>"
                html += f"<p><b>Gold:</b> {rewards.get('gold', 0)}</p>"
                items_count = len(rewards.get('items', []))
                html += f"<p><b>Items:</b> {items_count}</p>"
        elif hasattr(self, 'xp_spin'):
            html += f"<p><b>XP:</b> {self.xp_spin.value()}</p>"
            html += f"<p><b>Gold:</b> {self.gold_spin.value()}</p>"
        
        # Dialogues
        if hasattr(self, 'dialogue_editor') and self.dialogue_editor:
            dialogues = self.dialogue_editor.get_dialogue_count()
            html += f"<p><b>Dialogue nodes:</b> {dialogues}</p>"
        elif hasattr(self, 'dialogue_text'):
            dialogue_len = len(self.dialogue_text.toPlainText())
            html += f"<p><b>Dialogue length:</b> {dialogue_len} characters</p>"
        
        html += "</body></html>"
        return html
    
    def validateCurrentPage(self):
        """Validate current page before proceeding"""
        current_page = self.currentPage()
        
        # Custom validation for each page
        if current_page.title() == "Quest Identity":
            quest_name = self.field("questName")
            if not quest_name or not quest_name.strip():
                QMessageBox.warning(self, "Validation Error", "Quest name is required.")
                return False
        
        elif current_page.title() == "Location & Quest Giver":
            platform = self.field("platform")
            if not platform:
                QMessageBox.warning(self, "Validation Error", "Please select a location.")
                return False
        
        return super().validateCurrentPage()
    
    def create_quest(self):
        """Create and save quest from wizard data"""
        try:
            # Collect all wizard data
            quest_data = self._collect_wizard_data()
            
            # Create worker thread for saving
            self.worker_thread = QThread()
            self.worker = QuestSaverWorker(self.data_model, quest_data)
            self.worker.moveToThread(self.worker_thread)
            
            # Connect signals
            self.worker.progress_updated.connect(self.save_progress.setValue)
            self.worker.finished.connect(self.on_save_finished)
            self.worker_thread.started.connect(self.worker.save_quest)
            
            # Show progress UI
            self.save_progress.setVisible(True)
            self.save_status.setText("Saving quest...")
            
            # Start worker thread
            self.worker_thread.start()
            
        except Exception as e:
            try:
                self.logger.exception("Failed to create quest")
            except:
                import traceback
                traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Failed to create quest: {str(e)}")
    
    def _collect_wizard_data(self):
        """Collect data from all wizard pages"""
        if not EnhancedQuestData:
            # Create basic data structure if models not available
            class BasicQuestData:
                def __init__(self):
                    self.quest_id = self.next_quest_id
                    self.name = self.field("questName") or ""
                    self.description = self.field("questDescription") or ""
                    self.parent_id = self.hierarchy_page.parent_combo.currentData() or 0
                    self.order_index = self.hierarchy_page.order_spin.value()
                    self.map_locations = []
                    self.dialogues = []
                    self.rewards = None
            
            quest_data = BasicQuestData()
        else:
            # Use enhanced quest data model
            quest_data = EnhancedQuestData(
                quest_id=self.next_quest_id,
                name=self.field("questName") or "",
                description=self.field("questDescription") or "",
                parent_id=self.hierarchy_page.parent_combo.currentData() or 0,
                order_index=self.hierarchy_page.order_spin.value()
            )
        
        # Add platform location
        platform = self.field("platform")
        if platform:
            if MapLocation:
                quest_data.map_locations.append(MapLocation(
                    code=platform,
                    name=PLATFORM_NAMES.get(platform, platform)
                ))
            else:
                # Basic location storage
                if not hasattr(quest_data, 'map_locations'):
                    quest_data.map_locations = []
                quest_data.map_locations.append({'code': platform, 'name': PLATFORM_NAMES.get(platform, platform)})
        
        # Collect objectives
        if hasattr(self.objectives_page, 'objectives_list'):
            for i in range(self.objectives_page.objectives_list.count()):
                item = self.objectives_page.objectives_list.item(i)
                obj_data = item.data(Qt.UserRole)
                if obj_data:
                    if not hasattr(quest_data, 'objectives'):
                        quest_data.objectives = []
                    quest_data.objectives.append(obj_data.get('text', ''))
        
        # Add dialogues
        if hasattr(self, 'dialogue_editor') and self.dialogue_editor:
            dialogues = self.dialogue_editor.get_dialogues()
            for dlg in dialogues:
                if Dialogue:
                    quest_data.dialogues.append(Dialogue(
                        text=dlg.get('text', ''),
                        speaker=dlg.get('speaker', 'NPC'),
                        dialogue_type=dlg.get('type', 'Standard')
                    ))
                else:
                    if not hasattr(quest_data, 'dialogues'):
                        quest_data.dialogues = []
                    quest_data.dialogues.append(dlg)
        elif hasattr(self, 'dialogue_text'):
            # Basic dialogue from text editor
            dialogue_text = self.dialogue_text.toPlainText()
            if dialogue_text:
                if not hasattr(quest_data, 'dialogues'):
                    quest_data.dialogues = []
                if Dialogue:
                    quest_data.dialogues.append(Dialogue(
                        text=dialogue_text,
                        speaker="NPC",
                        dialogue_type="Standard"
                    ))
                else:
                    quest_data.dialogues.append({'text': dialogue_text, 'speaker': 'NPC'})
        
        # Add rewards
        if hasattr(self, 'reward_builder') and self.reward_builder:
            rewards_data = self.reward_builder.get_rewards()
            if rewards_data and QuestReward:
                quest_data.rewards = QuestReward(
                    xp=rewards_data.get('xp', 0),
                    gold=rewards_data.get('gold', 0),
                    silver=rewards_data.get('silver', 0),
                    copper=rewards_data.get('copper', 0),
                    items=rewards_data.get('items', [])
                )
            else:
                if rewards_data:
                    if not hasattr(quest_data, 'rewards'):
                        quest_data.rewards = {}
                    quest_data.rewards = rewards_data
        elif hasattr(self, 'xp_spin'):
            # Basic rewards from spinboxes
            if QuestReward:
                quest_data.rewards = QuestReward(
                    xp=self.xp_spin.value(),
                    gold=self.gold_spin.value(),
                    silver=self.silver_spin.value(),
                    copper=self.copper_spin.value(),
                    items=[]
                )
            else:
                if not hasattr(quest_data, 'rewards'):
                    quest_data.rewards = {}
                quest_data.rewards = {
                    'xp': self.xp_spin.value(),
                    'gold': self.gold_spin.value(),
                    'silver': self.silver_spin.value(),
                    'copper': self.copper_spin.value(),
                    'items': []
                }
        
        return quest_data
    
    def on_save_finished(self, success, message):
        """Handle quest save completion"""
        # Clean up worker thread
        try:
            self.worker_thread.quit()
            self.worker_thread.wait()
        except:
            pass
        
        if success:
            self.save_status.setText(f"<span style='color: green;'>✓ {message}</span>")
            self.quest_created.emit(self.wizard_data)
            
            # Ask if user wants to create another quest
            reply = QMessageBox.question(
                self, "Success", 
                "Quest saved successfully!\n\nWould you like to create another quest?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.restart()
            else:
                self.accept()
        else:
            self.save_status.setText(f"<span style='color: red;'>✗ {message}</span>")
            QMessageBox.critical(self, "Save Failed", message)


# Main launcher function
def launch_enhanced_quest_wizard(data_model, quest_data):
    """Launch enhanced quest creation wizard"""
    from PySide6.QtWidgets import QApplication
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    wizard = EnhancedQuestCreationWizard(data_model, quest_data)
    wizard.quest_created.connect(lambda data: print(f"Quest created: {data}"))
    
    if wizard.exec():
        return 0
    return 1


if __name__ == "__main__":
    # Test enhanced quest creation wizard
    from pathlib import Path
    
    # Initialize data model
    data_model = CFFDataModel()
    cff_file = project_root / "OriginalGameFiles/data/GameData.cff"
    
    if cff_file.exists():
        try:
            data_model.load_file(str(cff_file))
            print("✓ CFF file loaded successfully")
        except Exception as e:
            print(f"⚠ CFF file loading error: {e}")
            print("Continuing with basic functionality...")
    else:
        print(f"⚠ CFF file not found at {cff_file}")
        print("Continuing with basic functionality...")
    
    # Mock quest data for testing
    mock_quest_data = {
        1: {'name': 'Staub der Sterne', 'description': '...'},
        12: {'name': 'Darius der Kartograph', 'description': '...'},
    }
    
    try:
        sys.exit(launch_enhanced_quest_wizard(data_model, mock_quest_data))
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)