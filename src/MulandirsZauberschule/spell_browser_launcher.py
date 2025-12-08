"""
Main launcher for the Spell Browser and Spell Forge

This script provides a unified entry point to:
1. Browse original game spells from CFF files
2. Start the spell forge with selected spells
3. Create new spells from templates
"""

import sys
from pathlib import Path
import json
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt
from spell_browser import open_spell_browser
from spell_forge_wizard import SpellForgeWizard


class SpellBrowserLauncher(QMainWindow):
    """Main launcher window for spell tools"""
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Spell Browser & Forge Launcher")
        self.setMinimumSize(800, 600)
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Spell Browser & Forge")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = title_label.font()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel("Browse original game spells and create new ones")
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet("color: gray; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        # Main buttons
        buttons_layout = QHBoxLayout()
        
        # Spell Browser button
        self.browser_btn = QPushButton("🔍 Browse Original Spells")
        self.browser_btn.setMinimumHeight(50)
        self.browser_btn.clicked.connect(self.open_spell_browser)
        buttons_layout.addWidget(self.browser_btn)
        
        # Spell Forge button
        self.forge_btn = QPushButton("🔨 Open Spell Forge")
        self.forge_btn.setMinimumHeight(50)
        self.forge_btn.clicked.connect(self.open_spell_forge)
        buttons_layout.addWidget(self.forge_btn)
        
        layout.addLayout(buttons_layout)
        
        # Info section
        info_group = QGroupBox("Information")
        info_layout = QVBoxLayout()
        
        info_text = QTextEdit()
        info_text.setReadOnly(True)
        info_content = """
        <h3>Spell Browser & Forge Tools</h3>
        <p><b>Spell Browser:</b> Browse all original game spells extracted from GameData.cff with detailed level progression information.</p>
        <p><b>Spell Forge:</b> Create and edit custom spells using templates or as a starting point.</p>
        
        <h4>Features:</h4>
        <ul>
        <li>Browse all 3,461 original game spells</li>
        <li>Search and filter spells by name, school, or type</li>
        <li>View detailed level progression data</li>
        <li>Create custom spells based on original game spells</li>
        <li>Export spells for use in the game</li>
        </ul>
        """
        info_text.setHtml(info_content)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Status area
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("background-color: #f0f0f0; padding: 5px;")
        layout.addWidget(self.status_label)
        
    def open_spell_browser(self):
        """Open the spell browser dialog"""
        try:
            selected_spell, spell_id = open_spell_browser(self)
            
            if selected_spell:
                self.status_label.setText(f"Selected spell: {selected_spell.get('spell_name', 'Unknown')}")
                
                # Ask user if they want to edit the spell in the forge
                reply = QMessageBox.question(
                    self,
                    "Edit in Spell Forge?",
                    f"You selected '{selected_spell.get('spell_name', 'Unknown')}'.\n\n"
                    "Would you like to edit this spell in the Spell Forge?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.open_spell_forge_with_spell(selected_spell)
            else:
                self.status_label.setText("No spell selected")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open spell browser: {e}")
            self.status_label.setText("Error opening spell browser")
    
    def open_spell_forge(self):
        """Open the spell forge without a specific spell"""
        try:
            wizard = SpellForgeWizard()
            if wizard.exec() == wizard.Accepted:
                self.status_label.setText("Spell forge closed")
            else:
                self.status_label.setText("Spell forge cancelled")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open spell forge: {e}")
            self.status_label.setText("Error opening spell forge")
    
    def open_spell_forge_with_spell(self, spell_data):
        """Open the spell forge with a specific spell loaded"""
        try:
            wizard = SpellForgeWizard()
            wizard.load_spell(spell_data)
            if wizard.exec() == wizard.Accepted:
                self.status_label.setText(f"Edited spell: {spell_data.get('spell_name', 'Unknown')}")
            else:
                self.status_label.setText("Spell forge cancelled")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to open spell forge with spell: {e}")
            self.status_label.setText("Error opening spell forge")


def main():
    app = QApplication(sys.argv)
    
    launcher = SpellBrowserLauncher()
    launcher.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()