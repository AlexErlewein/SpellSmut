#!/usr/bin/env python3
"""
Ultra Simple Quest Creator

Fixed all imports - minimal working version.
"""

import sys
from pathlib import Path
from typing import Dict

# Add src directory to Python path
script_path = Path(__file__).resolve()
widgets_dir = script_path.parent
src_dir = widgets_dir.parent.parent.parent
project_root = src_dir.parent

sys.path.insert(0, str(src_dir))

print(f"Project root: {project_root}")

# Import PySide6
from PySide6.QtWidgets import (
    QApplication, QWizard, QWizardPage, QVBoxLayout, QWidget,
    QLabel, QLineEdit, QPushButton, QMessageBox, QSpinBox, QComboBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont

# Platform mappings
PLATFORM_NAMES = {
    "P1": "Liannon", "P2": "Eloni", "P3": "Leafshade", 
    "P4": "Wildland Pass", "P5": "Shiel", "P7": "Ice Gate", 
    "P8": "Gol Halad", "P9": "Gate of Swords"
}


class UltraSimpleQuestWizard(QWizard):
    """Ultra simple quest wizard"""
    
    quest_created = Signal(dict)
    
    def __init__(self, quest_data: Dict):
        super().__init__()
        self.quest_data = quest_data
        self.next_quest_id = 9001  # Simple ID
        
        self.setWindowTitle("Quest Creation Wizard")
        self.setMinimumSize(500, 400)
        
        # Create pages
        self._create_pages()
    
    def _create_pages(self):
        """Create simple wizard pages"""
        
        # Page 1: Basic info
        page1 = QWizardPage()
        page1.setTitle("Quest Details")
        page1.setSubTitle("Enter quest information")
        
        layout1 = QVBoxLayout(page1)
        
        # Quest name
        layout1.addWidget(QLabel("Quest Name:"))
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Enter quest name...")
        layout1.addWidget(self.name_edit)
        
        # Quest description  
        layout1.addWidget(QLabel("Description:"))
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("Enter quest description...")
        layout1.addWidget(self.desc_edit)
        
        # Quest ID
        layout1.addWidget(QLabel(f"Quest ID: {self.next_quest_id} (auto-assigned)"))
        
        layout1.addStretch()
        self.addPage(page1)
        
        # Page 2: Rewards
        page2 = QWizardPage()
        page2.setTitle("Quest Rewards")
        page2.setSubTitle("Set quest completion rewards")
        
        layout2 = QVBoxLayout(page2)
        
        # XP
        layout2.addWidget(QLabel("Experience Points:"))
        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 99999)
        self.xp_spin.setValue(100)
        layout2.addWidget(self.xp_spin)
        
        # Gold
        layout2.addWidget(QLabel("Gold:"))
        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(0, 99999)
        self.gold_spin.setValue(10)
        layout2.addWidget(self.gold_spin)
        
        layout2.addStretch()
        self.addPage(page2)
        
        # Page 3: Summary
        page3 = QWizardPage()
        page3.setTitle("Summary")
        page3.setSubTitle("Review and create quest")
        
        layout3 = QVBoxLayout(page3)
        
        self.summary_label = QLabel("Review your quest details below")
        self.summary_label.setWordWrap(True)
        self.summary_label.setStyleSheet("padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        layout3.addWidget(self.summary_label)
        
        # Update summary when page changes
        self.currentIdChanged.connect(lambda page_id: self._update_summary() if page_id == 2 else None)
        
        layout3.addStretch()
        self.addPage(page3)
    
    def _update_summary(self):
        """Update summary with current wizard data"""
        name = self.name_edit.text() or "Untitled Quest"
        desc = self.desc_edit.text() or "No description"
        xp = self.xp_spin.value()
        gold = self.gold_spin.value()
        
        summary = f"""📝 QUEST SUMMARY:
        
Name: {name}
Description: {desc}
Quest ID: {self.next_quest_id}
Experience: {xp} XP
Gold: {gold} coins

✅ Ready to create this quest!
Click 'Finish' to create it."""
        
        self.summary_label.setText(summary)
    
    def accept(self):
        """Create quest when wizard finishes"""
        try:
            # Collect data
            quest_data = {
                'quest_id': self.next_quest_id,
                'name': self.name_edit.text() or "Untitled Quest",
                'description': self.desc_edit.text() or "",
                'xp': self.xp_spin.value(),
                'gold': self.gold_spin.value()
            }
            
            print(f"Creating quest: {quest_data}")
            
            # Emit success
            self.quest_created.emit(quest_data)
            
            super().accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create quest:\n{str(e)}")


class UltraSimpleWindow(QWidget):
    """Ultra simple test window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ultra Simple Quest Creator")
        self.setMinimumSize(400, 300)
        
        # Mock quest data
        self.quest_data = {
            1: {'name': 'Sample Quest 1'},
            12: {'name': 'Sample Quest 2'}
        }
        
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Ultra Simple Quest Creator")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Status
        status = QLabel("✅ PySide6 Working\n✅ Quest Creator Ready\n✅ Click Button Below")
        status.setAlignment(Qt.AlignCenter)
        status.setStyleSheet("color: #27ae60; font-size: 14px; margin-bottom: 20px;")
        layout.addWidget(status)
        
        # Launch button
        self.launch_btn = QPushButton("🚀 Launch Quest Wizard")
        self.launch_btn.setFont(QFont("Arial", 12, QFont.Bold))
        self.launch_btn.setStyleSheet(
            "QPushButton {"
            "   background-color: #27ae60;"
            "   color: white;"
            "   padding: 15px 25px;"
            "   border-radius: 8px;"
            "   font-size: 14px;"
            "}"
            "QPushButton:hover {"
            "   background-color: #229954;"
            "}"
        )
        self.launch_btn.clicked.connect(self.launch_wizard)
        layout.addWidget(self.launch_btn)
        
        layout.addStretch()
    
    def launch_wizard(self):
        """Launch the quest wizard"""
        wizard = UltraSimpleQuestWizard(self.quest_data)
        wizard.quest_created.connect(self.on_quest_created)
        
        result = wizard.exec()
        
        if result == QWizard.Accepted:
            QMessageBox.information(self, "Success!", "Quest creator test completed! 🎉")
    
    def on_quest_created(self, quest_data):
        """Handle quest creation"""
        name = quest_data.get('name', 'Unknown')
        quest_id = quest_data.get('quest_id', 'Unknown')
        
        QMessageBox.information(
            self,
            "Quest Created! 🎉",
            f"Quest '{name}' (ID: {quest_id}) created!\n\n"
            f"XP: {quest_data.get('xp', 0)}\n"
            f"Gold: {quest_data.get('gold', 0)}\n\n"
            "Ultra simple quest creator working perfectly! ✅"
        )


def main():
    """Main function"""
    print("Ultra Simple Quest Creator Starting...")
    
    app = QApplication(sys.argv)
    app.setApplicationName("Ultra Simple Quest Creator")
    
    # Create and show window
    window = UltraSimpleWindow()
    window.show()
    
    # macOS activation
    window.raise_()
    window.activateWindow()
    
    print("Ultra simple quest creator window should be visible!")
    
    return app.exec()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)