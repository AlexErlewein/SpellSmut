"""
Property Editor Widget
Displays and allows editing of element properties
"""

import enum

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QScrollArea,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class PropertyEditorWidget(QWidget):
    """Widget for editing element properties"""

    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.current_element = None
        self.current_category = None
        self.current_index = None
        self.field_widgets = {}

        # Setup UI
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        self.header_label = QLabel("Select an element to edit")
        self.header_label.setStyleSheet(
            "font-weight: bold; font-size: 14px; padding: 10px;"
        )
        layout.addWidget(self.header_label)

        # Scroll area for properties
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Icon display (will be hidden for categories without icons like quests)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(128, 128)
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.icon_label.setStyleSheet("border: 2px solid #555; background: #222;")
        layout.addWidget(self.icon_label)

        # Quest information section (only shown for quests)
        self.quest_info_group = QGroupBox("Quest Information")
        quest_info_layout = QVBoxLayout(self.quest_info_group)

        # Quest ID
        quest_id_layout = QHBoxLayout()
        quest_id_layout.addWidget(QLabel("Quest ID:"))
        self.quest_id_label = QLabel("-")
        self.quest_id_label.setStyleSheet("font-weight: bold;")
        quest_id_layout.addWidget(self.quest_id_label)
        quest_id_layout.addStretch()
        quest_info_layout.addLayout(quest_id_layout)

        # Name ID
        name_id_layout = QHBoxLayout()
        name_id_layout.addWidget(QLabel("Name ID:"))
        self.name_id_label = QLabel("-")
        name_id_layout.addWidget(self.name_id_label)
        name_id_layout.addStretch()
        quest_info_layout.addLayout(name_id_layout)

        # Description ID
        desc_id_layout = QHBoxLayout()
        desc_id_layout.addWidget(QLabel("Description ID:"))
        self.desc_id_label = QLabel("-")
        desc_id_layout.addWidget(self.desc_id_label)
        desc_id_layout.addStretch()
        quest_info_layout.addLayout(desc_id_layout)

        # Quest Name (localized)
        quest_info_layout.addWidget(QLabel("Quest Name:"))
        self.quest_name_display = QTextEdit()
        self.quest_name_display.setMaximumHeight(50)
        self.quest_name_display.setReadOnly(True)
        quest_info_layout.addWidget(self.quest_name_display)

        # Quest Description (localized)
        quest_info_layout.addWidget(QLabel("Quest Description:"))
        self.quest_desc_display = QTextEdit()
        self.quest_desc_display.setMaximumHeight(100)
        self.quest_desc_display.setReadOnly(True)
        quest_info_layout.addWidget(self.quest_desc_display)

        self.quest_info_group.hide()  # Hidden by default
        layout.addWidget(self.quest_info_group)

        # Properties container
        self.props_widget = QWidget()
        self.props_layout = QFormLayout(self.props_widget)
        scroll.setWidget(self.props_widget)

        layout.addWidget(scroll)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.save_button.setEnabled(False)
        button_layout.addWidget(self.save_button)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_changes)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)

        # Connect to data model signals
        self.data_model.element_selected.connect(self.on_element_selected)

    def on_element_selected(self, category, index):
        """Handle element selection"""
        self.current_category = category
        self.current_index = index
        self.current_element = self.data_model.get_element_by_index(category, index)
        self.display_element()

    def display_element(self):
        """Display element properties"""
        # Clear existing widgets
        while self.props_layout.count():
            item = self.props_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.field_widgets.clear()

        if not self.current_element:
            self.header_label.setText("Select an element to edit")
            self.save_button.setEnabled(False)
            self.cancel_button.setEnabled(False)
            self.icon_label.hide()
            self.quest_info_group.hide()
            return

        # Hide icon for quest category (quests don't have icons)
        is_quest = self.current_category and "quest" in self.current_category.lower()

        if is_quest:
            self.icon_label.hide()
            self.quest_info_group.show()

            # Populate quest information
            quest_id = getattr(self.current_element, "quest_id", "Unknown")
            name_id = getattr(self.current_element, "name_id", "None")
            description_id = getattr(self.current_element, "description_id", "None")

            self.quest_id_label.setText(str(quest_id))
            self.name_id_label.setText(str(name_id) if name_id else "None")
            self.desc_id_label.setText(
                str(description_id) if description_id else "None"
            )

            # Get localized name and description
            quest_name = self.data_model.get_localised_text(
                self.current_element, "name"
            )
            if not quest_name:
                quest_name = getattr(self.current_element, "name", "No name available")

            quest_desc = self.data_model.get_advanced_description(self.current_element)
            if not quest_desc:
                quest_desc = "No description available"

            self.quest_name_display.setPlainText(str(quest_name))
            self.quest_desc_display.setPlainText(str(quest_desc))
        else:
            self.icon_label.show()
            self.quest_info_group.hide()

            # Load and display icon
            icon_pixmap = self.data_model.get_icon_pixmap(
                self.current_category, self.current_element, size=(128, 128)
            )
            if icon_pixmap:
                self.icon_label.setPixmap(icon_pixmap)
            else:
                self.icon_label.setText("No Icon")

        # Update header
        element_name = "Unknown"
        # Try localised name first
        localised_name = self.data_model.get_localised_text(
            self.current_element, "name"
        )
        if localised_name:
            element_name = localised_name
        elif hasattr(self.current_element, "name"):
            element_name = str(self.current_element.name)
        elif hasattr(self.current_element, "spell_id"):
            element_name = f"Spell ID: {self.current_element.spell_id}"
        elif hasattr(self.current_element, "item_id"):
            element_name = f"Item ID: {self.current_element.item_id}"

        self.header_label.setText(f"Editing: {element_name}")

        # Get fields
        fields = self.data_model.get_element_fields(self.current_element)

        # Create widgets for each field
        for field_name, value, field_info in fields:
            label = QLabel(field_name)
            label.setToolTip(field_name)

            # Create appropriate widget based on type
            widget = self.create_field_widget(value, field_info)
            widget.setProperty("field_name", field_name)
            widget.setProperty("original_value", value)

            # Connect change signal to enable save button
            self.connect_widget_signal(widget)

            self.field_widgets[field_name] = widget
            self.props_layout.addRow(label, widget)

        self.save_button.setEnabled(True)
        self.cancel_button.setEnabled(True)

    def create_field_widget(self, value, field_info):
        """Create appropriate widget for field type"""
        # Check if it's an enum
        if hasattr(value, "__class__") and isinstance(value.__class__, type(enum.Enum)):
            widget = QComboBox()
            # Add enum values
            for member in value.__class__:
                widget.addItem(f"{value.__class__.__name__}.{member.name}", member)

            # Set current value
            current_idx = widget.findText(f"{value.__class__.__name__}.{value.name}")
            if current_idx >= 0:
                widget.setCurrentIndex(current_idx)

            return widget

        # Integer field
        elif isinstance(value, int):
            widget = QSpinBox()
            widget.setRange(-2147483648, 2147483647)
            widget.setValue(value)
            return widget

        # Boolean field
        elif isinstance(value, bool):
            widget = QComboBox()
            widget.addItem("False", False)
            widget.addItem("True", True)
            widget.setCurrentIndex(1 if value else 0)
            return widget

        # String or other - use line edit
        else:
            widget = QLineEdit()
            widget.setText(str(value))
            return widget

    def connect_widget_signal(self, widget):
        """Connect widget's change signal"""
        if isinstance(widget, QLineEdit):
            widget.textChanged.connect(lambda: None)  # Just to enable save
        elif isinstance(widget, QSpinBox):
            widget.valueChanged.connect(lambda: None)
        elif isinstance(widget, QComboBox):
            widget.currentIndexChanged.connect(lambda: None)

    def save_changes(self):
        """Save changes to current element"""
        if not self.current_element or not self.current_category:
            return

        changes_made = False

        for field_name, widget in self.field_widgets.items():
            original_value = widget.property("original_value")
            new_value = self.get_widget_value(widget)

            # Check if value changed
            if str(new_value) != str(original_value):
                # Update the field
                if self.data_model.update_element_field(
                    self.current_category, self.current_index, field_name, new_value
                ):
                    changes_made = True
                    widget.setProperty("original_value", new_value)
                else:
                    QMessageBox.warning(
                        self, "Error", f"Failed to update field: {field_name}"
                    )

        if changes_made:
            QMessageBox.information(self, "Success", "Changes saved successfully")

    def cancel_changes(self):
        """Cancel changes and reload element"""
        self.display_element()

    def get_widget_value(self, widget):
        """Get value from widget"""
        if isinstance(widget, QLineEdit):
            return widget.text()
        elif isinstance(widget, QSpinBox):
            return widget.value()
        elif isinstance(widget, QComboBox):
            return widget.currentData()
        return None

    def refresh(self):
        """Refresh the property editor"""
        if self.current_element:
            self.display_element()
