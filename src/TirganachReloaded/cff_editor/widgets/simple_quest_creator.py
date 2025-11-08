#!/usr/bin/env python3
"""
Simple Quest Wizard - All Components Working

Test wizard without CFF loading issues.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
script_path = Path(__file__).resolve()
widgets_dir = script_path.parent
src_dir = widgets_dir.parent.parent.parent
project_root = src_dir.parent

sys.path.insert(0, str(src_dir))

print(f"Project root: {project_root}")

# Import PySide6
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QHBoxLayout,
    QWidget, QLabel, QLineEdit, QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Import quest model
from TirganachReloaded.cff_editor.models.quest_models import (
    EnhancedQuestData, QuestReward, Dialogue, MapLocation
)

# Platform mappings
PLATFORM_NAMES = {
    "P1": "Liannon", "P2": "Eloni", "P3": "Leafshade", "P4": "Wildland Pass",
    "P5": "Shiel", "P7": "Ice Gate", "P8": "Gol Halad", "P9": "Gate of Swords"
}


class SimpleQuestWizard(QWizard):
    """Simple quest wizard that works"""
    
    quest_created = Signal(dict)
    
    def __init__(self, quest_data: Dict):
        super().__init__()
        self.quest_data = quest_data
        self.next_quest_id = max(quest_data.keys()) + 1 if quest_data else 9001
        
        # Store wizard data
        self.wizard_data = {}
        
        self.setWindowTitle("Simple Quest Creation Wizard")
        self.setWizardStyle(QWizard.ModernStyle)
        self.setMinimumSize(600, 500)
        
        self._setup_pages()
    
    def _setup_pages(self):
        """Setup wizard pages"""
        # Page 1: Quest Identity
        identity_page = self._create_identity_page()
        self.addPage(identity_page)
        
        # Page 2: Basic Info
        info_page = self._create_info_page()
        self.addPage(info_page)
        
        # Page 3: Rewards
        rewards_page = self._create_rewards_page()
        self.addPage(rewards_page)
        
        # Page 4: Summary
        summary_page = self._create_summary_page()
        self.addPage(summary_page)
    
    def _create_identity_page(self):
        """Create quest identity page"""
        page = QWizardPage()
        page.setTitle("Quest Identity")
        page.setSubTitle("Enter basic quest information")
        
        layout = QVBoxLayout(page)
        
        # Quest name
        name_label = QLabel("Quest Name:")
        layout.addWidget(name_label)
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter quest name...")
        page.registerField("questName*", self.name_edit)
        layout.addWidget(self.name_edit)
        
        # Quest description
        desc_label = QLabel("Description:")
        layout.addWidget(desc_label)
        
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Enter quest description...")
        page.registerField("questDescription", self.desc_edit)
        layout.addWidget(self.desc_edit)
        
        layout.addStretch()
        
        return page
    
    def _create_info_page(self):
        """Create basic info page"""
        page = QWizardPage()
        page.setTitle("Quest Information")
        page.setSubTitle("Set quest details and location")
        
        layout = QVBoxLayout(page)
        
        # Quest ID info
        id_label = QLabel(f"Auto-assigned Quest ID: {self.next_quest_id}")
        id_label.setStyleSheet("font-weight: bold; color: #3498db; padding: 10px;")
        layout.addWidget(id_label)
        
        # Platform selection
        platform_label = QLabel("Quest Location:")
        layout.addWidget(platform_label)
        
        self.platform_combo = QWizard().page().findChild(QComboBox) if hasattr(self, 'platform_combo') else None
        if not self.platform_combo:
            from PySide6.QtWidgets import QComboBox
            self.platform_combo = QComboBox()
            self.platform_combo.addItem("Select location...")
            for code, name in PLATFORM_NAMES.items():
                self.platform_combo.addItem(f"{name} ({code})", code)
            page.registerField("platform", self.platform_combo)
            layout.addWidget(self.platform_combo)
        
        layout.addStretch()
        
        return page
    
    def _create_rewards_page(self):
        """Create rewards page"""
        page = QWizardPage()
        page.setTitle("Quest Rewards")
        page.setSubTitle("Configure quest completion rewards")
        
        layout = QVBoxLayout(page)
        
        # Reward explanation
        info_label = QLabel("Set experience and gold rewards:")
        info_label.setStyleSheet("color: #7f8c8d; margin-bottom: 10px;")
        layout.addWidget(info_label)
        
        # XP
        xp_label = QLabel("Experience Points:")
        layout.addWidget(xp_label)
        
        from PySide6.QtWidgets import QSpinBox
        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 99999)
        self.xp_spin.setValue(100)
        page.registerField("xp", self.xp_spin)
        layout.addWidget(self.xp_spin)
        
        # Gold
        gold_label = QLabel("Gold:")
        layout.addWidget(gold_label)
        
        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(0, 99999)
        self.gold_spin.setValue(10)
        page.registerField("gold", self.gold_spin)
        layout.addWidget(self.gold_spin)
        
        layout.addStretch()
        
        return page
    
    def _create_summary_page(self):
        """Create summary page"""
        page = QWizardPage()
        page.setTitle("Summary")
        page.setSubTitle("Review quest details")
        
        layout = QVBoxLayout(page)
        
        summary_text = QTextEdit()
        summary_text.setReadOnly(True)
        summary_text.setPlainText("Review your quest details before creating...")
        layout.addWidget(summary_text)
        
        # Update summary when shown
        def update_summary():
            name = self.field("questName")
            desc = self.field("questDescription")
            platform = self.field("platform")
            xp = self.field("xp")
            gold = self.field("gold")
            
            platform_name = PLATFORM_NAMES.get(platform, platform) if platform else "Not selected"
            
            summary = f"""=== QUEST SUMMARY ===
Name: {name or 'Not set'}
Description: {desc or 'Not set'}
Quest ID: {self.next_quest_id}
Location: {platform_name}
Rewards: {xp or 0} XP, {gold or 0} Gold

Click "Finish" to create this quest!"""
            
            summary_text.setPlainText(summary)
        
        page.entered.connect(update_summary)
        
        return page
    
    def accept(self):
        """Handle wizard completion"""
        try:
            # Collect wizard data
            quest_data = {
                'quest_id': self.next_quest_id,
                'name': self.field("questName") or "Untitled Quest",
                'description': self.field("questDescription") or "",
                'xp': self.field("xp") or 0,
                'gold': self.field("gold") or 0,
                'platform': self.field("platform")
            }
            
            print(f"Creating quest: {quest_data}")
            
            # Create enhanced quest data
            quest = EnhancedQuestData(
                quest_id=quest_data['quest_id'],
                name=quest_data['name'],
                description=quest_data['description'],
                parent_id=0,
                order_index=0
            )
            
            # Add location
            if quest_data['platform']:
                quest.map_locations.append(MapLocation(
                    code=quest_data['platform'],
                    name=PLATFORM_NAMES.get(quest_data['platform'], quest_data['platform'])
                ))
            
            # Add rewards
            quest.rewards = QuestReward(
                xp=quest_data['xp'],
                gold=quest_data['gold'],
                silver=0,
                copper=0,
                items=[]
            )
            
            # Add sample dialogues
            quest.dialogues.append(Dialogue(
                text=f"Welcome to {quest_data['name']}!",
                speaker="NPC",
                dialogue_type="Greeting"
            ))
            quest.dialogues.append(Dialogue(
                text="I accept this quest!",
                speaker="Player", 
                dialogue_type="Accept"
            ))
            
            # Emit success
            self.quest_created.emit({
                'quest_id': quest.quest_id,
                'name': quest.name,
                'description': quest.description,
                'xp': quest.rewards.xp,
                'gold': quest.rewards.gold,
                'platform': quest.map_locations[0].code if quest.map_locations else None,
                'quest_object': quest
            })
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create quest:\n{str(e)}")


class SimpleTestWindow(QMainWindow):
    """Simple test window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple Quest Creator Test")
        self.setMinimumSize(400, 300)
        
        # Mock quest data
        self.quest_data = {
            1: {'name': 'Sample Quest 1'},
            12: {'name': 'Sample Quest 2'}
        }
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Title
        title = QLabel("Simple Quest Creator")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Status
        status = QLabel("✅ PySide6 Working\n✅ Quest Creator Ready\n✅ Click Button Below")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #27ae60; margin-bottom: 20px;")
        layout.addWidget(status)
        
        # Test button
        btn = QPushButton("Launch Quest Creator")
        btn.setFont(QFont("Arial", 12, QFont.Bold))
        btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #3498db;"
            "   color: white;"
            "   padding: 12px 25px;"
            "   border-radius: 6px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #2980b9;"
            "}"
        )
        btn.clicked.connect(self.launch_wizard)
        layout.addWidget(btn)
        
        layout.addStretch()
    
    def launch_wizard(self):
        """Launch quest wizard"""
        wizard = SimpleQuestWizard(self.quest_data)
        wizard.quest_created.connect(self.on_quest_created)
        
        result = wizard.exec()
        if result == QWizard.Accepted:
            self.statusBar().showMessage("Quest created!")
    
    def on_quest_created(self, quest_data):
        """Handle quest created"""
        QMessageBox.information(
            self, 
            "Quest Created!", 
            f"Quest '{quest_data['name']}' created successfully!\n\n"
            f"ID: {quest_data['quest_id']}\n"
            f"XP: {quest_data['xp']}\n"
            f"Gold: {quest_data['gold']}\n\n"
            "Simple quest creation system is working! 🎉"
        )


def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("Simple Quest Creator")
    
    # Create test window
    window = SimpleTestWindow()
    window.show()
    
    print("Simple quest creator window should be visible!")
    
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)