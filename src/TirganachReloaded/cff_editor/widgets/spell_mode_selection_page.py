from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QRadioButton, QPushButton, QSpinBox, QFormLayout
)
from PySide6.QtCore import Signal

from .spell_browser_dialog import SpellBrowserDialog


class SpellModeSelectionPage(QWizardPage):
    """Step 0: Choose spell creation mode"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Spell Creation Mode")
        self.setSubTitle("Choose how to create your spell and assign a unique ID.")
        
        self.selected_spell = None
        self.spell_loader = None
        
        layout = QVBoxLayout()
        
        # Creation Mode
        mode_group = QGroupBox("Creation Mode")
        mode_layout = QVBoxLayout()
        self.new_spell_radio = QRadioButton("Create New Spell (blank slate)")
        self.edit_spell_radio = QRadioButton(
            "Edit Existing Spell (load from templates and game)"
        )
        self.duplicate_spell_radio = QRadioButton(
            "Duplicate & Modify (copy existing, new ID)"
        )
        self.new_spell_radio.setChecked(True)
        mode_layout.addWidget(self.new_spell_radio)
        mode_layout.addWidget(self.edit_spell_radio)
        mode_layout.addWidget(self.duplicate_spell_radio)
        
        # Browse button for edit/duplicate modes
        browse_layout = QHBoxLayout()
        self.browse_button = QPushButton("Browse Spells...")
        self.browse_button.clicked.connect(self.browse_spells)
        self.browse_button.setEnabled(False)
        browse_layout.addWidget(self.browse_button)
        browse_layout.addStretch()
        mode_layout.addLayout(browse_layout)
        
        # Selected spell display
        self.selected_spell_label = QLabel("No spell selected")
        self.selected_spell_label.setStyleSheet("color: gray; font-style: italic;")
        mode_layout.addWidget(self.selected_spell_label)
        
        # Enable browse button when edit/duplicate modes are selected
        self.edit_spell_radio.toggled.connect(self.on_mode_changed)
        self.duplicate_spell_radio.toggled.connect(self.on_mode_changed)
        
        mode_group.setLayout(mode_layout)
        layout.addWidget(mode_group)
        
        # ID Assignment
        id_group = QGroupBox("ID Assignment")
        id_layout = QVBoxLayout()
        self.auto_id_radio = QRadioButton("Auto-assign next available ID (recommended)")
        self.manual_id_radio = QRadioButton("Manual ID entry (with validation)")
        self.auto_id_radio.setChecked(True)
        id_layout.addWidget(self.auto_id_radio)
        id_layout.addWidget(self.manual_id_radio)
        
        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(300, 999)
        self.manual_id_spin.setValue(300)
        self.manual_id_spin.setEnabled(False)
        
        manual_form = QFormLayout()
        manual_form.addRow("Spell Line ID:", self.manual_id_spin)
        id_layout.addLayout(manual_form)
        
        # Enable manual ID spin when manual radio is selected
        self.manual_id_radio.toggled.connect(self.manual_id_spin.setEnabled)
        
        id_group.setLayout(id_layout)
        layout.addWidget(id_group)
        
        self.setLayout(layout)
    
    def on_mode_changed(self):
        """Handle creation mode changes"""
        is_edit_or_duplicate = self.edit_spell_radio.isChecked() or self.duplicate_spell_radio.isChecked()
        self.browse_button.setEnabled(is_edit_or_duplicate)
        
        if not is_edit_or_duplicate:
            self.selected_spell = None
            self.selected_spell_label.setText("No spell selected")
            self.selected_spell_label.setStyleSheet("color: gray; font-style: italic;")
    
    def browse_spells(self):
        """Open spell browser dialog"""
        dialog = SpellBrowserDialog(self)
        if dialog.exec() == SpellBrowserDialog.Accepted:
            self.selected_spell = dialog.get_selected_spell()
            if self.selected_spell:
                self.selected_spell_label.setText(
                    f"Selected: {self.selected_spell['name']} ({self.selected_spell['school']} {self.selected_spell['type']})"
                )
                self.selected_spell_label.setStyleSheet("color: black; font-style: normal;")
            else:
                self.selected_spell_label.setText("No spell selected")
                self.selected_spell_label.setStyleSheet("color: gray; font-style: italic;")
    
    def get_creation_mode(self) -> str:
        """Get the selected creation mode"""
        if self.new_spell_radio.isChecked():
            return "new"
        elif self.edit_spell_radio.isChecked():
            return "edit"
        elif self.duplicate_spell_radio.isChecked():
            return "duplicate"
        return "new"
    
    def get_spell_id_mode(self) -> str:
        """Get the ID assignment mode"""
        return "auto" if self.auto_id_radio.isChecked() else "manual"
    
    def get_manual_spell_id(self) -> int:
        """Get the manually entered spell ID"""
        return self.manual_id_spin.value()
    
    def get_selected_spell_data(self):
        """Get the selected spell data"""
        return self.selected_spell
    
    def isComplete(self) -> bool:
        """Validate the page"""
        creation_mode = self.get_creation_mode()
        
        # For new spells, always complete
        if creation_mode == "new":
            return True
        
        # For edit/duplicate modes, require spell selection
        if creation_mode in ["edit", "duplicate"]:
            return self.selected_spell is not None
        
        return False
    
    def initializePage(self):
        """Initialize page when shown"""
        # Reset selection when page is shown
        if self.get_creation_mode() == "new":
            self.selected_spell = None
            self.selected_spell_label.setText("No spell selected")
            self.selected_spell_label.setStyleSheet("color: gray; font-style: italic;")
        
        # Emit completeChanged to update wizard buttons
        self.completeChanged.emit()