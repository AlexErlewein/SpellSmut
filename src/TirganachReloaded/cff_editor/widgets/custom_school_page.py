from PySide6.QtWidgets import (
    QWizardPage, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QLineEdit, QTextEdit, QPushButton, QColorDialog, QFormLayout,
    QCheckBox, QSpinBox, QComboBox, QRadioButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont


class CustomSchoolPage(QWizardPage):
    """Step for creating custom magic schools"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Custom Magic School")
        self.setSubTitle("Create your own magic school with unique properties.")

        layout = QVBoxLayout()

        # School Selection
        school_group = QGroupBox("Magic School Selection")
        school_layout = QVBoxLayout()
        
        self.existing_radio = QRadioButton("Use Existing Magic School")
        self.custom_radio = QRadioButton("Create Custom Magic School")
        self.existing_radio.setChecked(True)
        
        school_layout.addWidget(self.existing_radio)
        school_layout.addWidget(self.custom_radio)
        
        # Existing school dropdown
        school_form = QFormLayout()
        self.existing_school_combo = QComboBox()
        self.existing_school_combo.addItems([
            "White Magic (Holy/Life)",
            "Fire Magic (Fire Elemental)", 
            "Ice Magic (Ice Elemental)",
            "Black Magic (Necromancy/Dark)",
            "Mental Magic (Mind/Illusion)",
            "Earth Magic (Earth Elemental)"
        ])
        school_form.addRow("Select School:", self.existing_school_combo)
        school_layout.addLayout(school_form)
        
        # Custom school creation
        custom_form = QFormLayout()
        self.custom_name_edit = QLineEdit()
        self.custom_name_edit.setPlaceholderText("e.g., Blood Magic")
        custom_form.addRow("School Name:", self.custom_name_edit)
        
        self.custom_color_button = QPushButton("Choose School Color")
        self.custom_color_button.clicked.connect(self.choose_school_color)
        self.custom_color_label = QLabel("#FF6B35")
        self.custom_color_label.setStyleSheet("background-color: #FF6B35; padding: 5px; border: 1px solid black;")
        self.custom_color = QColor(255, 107, 53)  # Default orange-red
        
        color_layout = QHBoxLayout()
        color_layout.addWidget(self.custom_color_button)
        color_layout.addWidget(self.custom_color_label)
        color_layout.addStretch()
        custom_form.addRow("School Color:", color_layout)
        
        self.custom_description_edit = QTextEdit()
        self.custom_description_edit.setPlaceholderText(
            "Describe your custom magic school...\n\n"
            "Examples:\n"
            "• Blood Magic - Manipulates life force and blood\n"
            "• Time Magic - Controls time flow and temporal effects\n"
            "• Shadow Magic - Uses darkness and void energy"
        )
        self.custom_description_edit.setMaximumHeight(100)
        custom_form.addRow("Description:", self.custom_description_edit)
        
        school_layout.addLayout(custom_form)
        school_group.setLayout(school_layout)
        layout.addWidget(school_group)

        # Enable/disable custom fields based on selection
        self.existing_radio.toggled.connect(self.on_school_mode_changed)
        self.custom_radio.toggled.connect(self.on_school_mode_changed)
        
        # Initially disable custom fields
        self.on_school_mode_changed()

        layout.addStretch()
        self.setLayout(layout)

    def on_school_mode_changed(self):
        """Enable/disable custom fields based on selection"""
        use_custom = self.custom_radio.isChecked()
        
        self.existing_school_combo.setEnabled(not use_custom)
        self.custom_name_edit.setEnabled(use_custom)
        self.custom_color_button.setEnabled(use_custom)
        self.custom_description_edit.setEnabled(use_custom)

    def choose_school_color(self):
        """Open color picker for school color"""
        color = QColorDialog.getColor(self.custom_color, self, "Choose Magic School Color")
        if color.isValid():
            self.custom_color = color
            self.custom_color_label.setText(color.name())
            self.custom_color_label.setStyleSheet(
                f"background-color: {color.name()}; padding: 5px; border: 1px solid black;"
            )

    def get_magic_school(self):
        """Get the selected magic school"""
        if self.existing_radio.isChecked():
            school_map = {
                0: "White Magic (Holy/Life)",
                1: "Fire Magic (Fire Elemental)", 
                2: "Ice Magic (Ice Elemental)",
                3: "Black Magic (Necromancy/Dark)",
                4: "Mental Magic (Mind/Illusion)",
                5: "Earth Magic (Earth Elemental)"
            }
            return school_map.get(self.existing_school_combo.currentIndex(), "Fire Magic")
        else:
            return self.custom_name_edit.text() or "Custom Magic"

    def get_custom_school_data(self):
        """Get custom school data if custom mode is selected"""
        if self.custom_radio.isChecked():
            return {
                'name': self.custom_name_edit.text(),
                'color': self.custom_color.name(),
                'description': self.custom_description_edit.toPlainText()
            }
        return None

    def isComplete(self) -> bool:
        """Validate page"""
        if self.existing_radio.isChecked():
            return True  # Existing schools are always valid
        
        # For custom schools, require at least a name
        return bool(self.custom_name_edit.text().strip())

    def initializePage(self):
        """Initialize page when shown"""
        # Emit completeChanged to update wizard buttons
        self.completeChanged.emit()