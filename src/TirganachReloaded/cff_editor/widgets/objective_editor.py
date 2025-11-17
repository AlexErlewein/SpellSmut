"""
Objective Editor Dialog
======================
Enhanced objective editor with proper value selection for each objective type.

Author: Quest Editor Team
Date: November 17, 2025
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QDialogButtonBox,
    QGroupBox,
    QCheckBox,
    QTextEdit,
    QMessageBox,
    QScrollArea,
    QWidget,
    QApplication,
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
from typing import Dict, Any, Optional, Tuple
import json


class ObjectiveData:
    """Represents a quest objective with full details"""

    def __init__(
        self,
        obj_type: str,
        text: str = "",
        target_id: int = 0,
        target_name: str = "",
        quantity: int = 1,
        location: str = "",
        description: str = "",
    ):
        self.obj_type = obj_type  # talk, kill, gather, explore, escort, other
        self.text = text
        self.target_id = target_id  # NPC ID, Item ID, etc.
        self.target_name = target_name  # NPC name, Item name, etc.
        self.quantity = quantity
        self.location = location
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.obj_type,
            "text": self.text,
            "target_id": self.target_id,
            "target_name": self.target_name,
            "quantity": self.quantity,
            "location": self.location,
            "description": self.description,
        }

    @staticmethod
    def from_dict(data: Dict[str, Any]):
        return ObjectiveData(
            obj_type=data.get("type", "other"),
            text=data.get("text", ""),
            target_id=data.get("target_id", 0),
            target_name=data.get("target_name", ""),
            quantity=data.get("quantity", 1),
            location=data.get("location", ""),
            description=data.get("description", ""),
        )

    def get_display_text(self) -> str:
        """Get formatted display text for list widget"""
        if self.obj_type == "talk":
            return f"💬 Talk to {self.target_name or f'NPC {self.target_id}'}"
        elif self.obj_type == "kill":
            return f"⚔️ Kill {self.quantity}x {self.target_name or f'Enemy {self.target_id}'}"
        elif self.obj_type == "gather":
            return f"📦 Gather {self.quantity}x {self.target_name or f'Item {self.target_id}'}"
        elif self.obj_type == "explore":
            return f"🗺 Explore {self.location or 'location'}"
        elif self.obj_type == "escort":
            return f"👥 Escort {self.target_name or 'NPC'} to {self.location or 'destination'}"
        else:
            return f"📝 {self.text}"

    def get_description(self) -> str:
        """Get full description for display"""
        if self.description:
            return self.description

        # Generate auto-description
        if self.obj_type == "talk":
            return f"Talk to {self.target_name or f'NPC {self.target_id}'}"
        elif self.obj_type == "kill":
            return (
                f"Kill {self.quantity}x {self.target_name or f'Enemy {self.target_id}'}"
            )
        elif self.obj_type == "gather":
            return f"Gather {self.quantity}x {self.target_name or f'Item {self.target_id}'}"
        elif self.obj_type == "explore":
            return f"Explore {self.location or 'the specified location'}"
        elif self.obj_type == "escort":
            return f"Escort {self.target_name or 'NPC'} to {self.location or 'destination'}"
        else:
            return self.text


class ObjectiveEditorDialog(QDialog):
    """Enhanced objective editor with type-specific fields"""

    def __init__(
        self, parent=None, objective: Optional[ObjectiveData] = None, data_model=None
    ):
        super().__init__(parent)
        self.objective = objective
        self.data_model = data_model
        self.setup_ui()

        if objective:
            self.load_objective(objective)

    def setup_ui(self):
        self.setWindowTitle("Objective Editor")
        self.setModal(True)
        self.resize(600, 700)

        layout = QVBoxLayout(self)

        # Create scroll area for long forms
        scroll = QScrollArea()
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)

        # Basic objective info
        basic_group = QGroupBox("Objective Details")
        basic_layout = QFormLayout(basic_group)

        # Objective type
        self.type_combo = QComboBox()
        self.type_combo.addItem("💬 Talk to NPC", "talk")
        self.type_combo.addItem("⚔️ Kill Target", "kill")
        self.type_combo.addItem("📦 Gather Items", "gather")
        self.type_combo.addItem("🗺 Explore Location", "explore")
        self.type_combo.addItem("👥 Escort NPC", "escort")
        self.type_combo.addItem("📝 Custom Objective", "other")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        basic_layout.addRow("Objective Type:", self.type_combo)

        # Custom text (for "other" type)
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("Enter custom objective text...")
        basic_layout.addRow("Objective Text:", self.text_edit)

        # Description
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(80)
        self.description_edit.setPlaceholderText("Detailed description (optional)...")
        basic_layout.addRow("Description:", self.description_edit)

        scroll_layout.addWidget(basic_group)

        # Target-specific group
        self.target_group = QGroupBox("Target Details")
        self.target_layout = QFormLayout(self.target_group)

        # Target ID
        self.target_id_spin = QSpinBox()
        self.target_id_spin.setRange(0, 99999)
        self.target_id_spin.valueChanged.connect(self.on_target_id_changed)
        self.target_layout.addRow("Target ID:", self.target_id_spin)

        # Target name (auto-filled from browser)
        self.target_name_edit = QLineEdit()
        self.target_name_edit.setPlaceholderText(
            "Target name (auto-filled from browser)"
        )
        self.target_name_edit.setReadOnly(True)
        self.target_layout.addRow("Target Name:", self.target_name_edit)

        # Browse button
        browse_layout = QHBoxLayout()
        self.browse_btn = QPushButton("🔍 Browse...")
        self.browse_btn.clicked.connect(self.browse_target)
        browse_layout.addWidget(self.browse_btn)
        browse_layout.addStretch()
        self.target_layout.addRow("", browse_layout)

        scroll_layout.addWidget(self.target_group)

        # Quantity and location group
        self.details_group = QGroupBox("Additional Details")
        self.details_layout = QFormLayout(self.details_group)

        # Quantity
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setRange(1, 999)
        self.quantity_spin.setValue(1)
        self.details_layout.addRow("Quantity:", self.quantity_spin)

        # Location
        self.location_edit = QLineEdit()
        self.location_edit.setPlaceholderText("Location name (for explore/escort)...")
        self.details_layout.addRow("Location:", self.location_edit)

        scroll_layout.addWidget(self.details_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        # Initialize UI state
        self.on_type_changed()

    def on_type_changed(self):
        """Update UI based on objective type"""
        current_data = self.type_combo.currentData()

        if current_data == "other":
            # Custom objective - show text field, hide target
            self.text_edit.setEnabled(True)
            self.text_edit.setVisible(True)
            self.target_group.setVisible(False)
            self.details_group.setVisible(False)
        elif current_data == "talk":
            # Talk objective - show NPC browser
            self.text_edit.setEnabled(False)
            self.text_edit.setVisible(False)
            self.target_group.setVisible(True)
            self.target_group.setTitle("NPC Target")
            self.details_group.setVisible(False)
            self.browse_btn.setText("🔍 Browse NPCs...")
        elif current_data == "kill":
            # Kill objective - show enemy browser
            self.text_edit.setEnabled(False)
            self.text_edit.setVisible(False)
            self.target_group.setVisible(True)
            self.target_group.setTitle("Enemy Target")
            self.details_group.setVisible(True)
            self.quantity_spin.setEnabled(True)
            self.browse_btn.setText("🔍 Browse Enemies...")
        elif current_data == "gather":
            # Gather objective - show item browser
            self.text_edit.setEnabled(False)
            self.text_edit.setVisible(False)
            self.target_group.setVisible(True)
            self.target_group.setTitle("Item Target")
            self.details_group.setVisible(True)
            self.quantity_spin.setEnabled(True)
            self.browse_btn.setText("🔍 Browse Items...")
        elif current_data == "explore":
            # Explore objective - show location
            self.text_edit.setEnabled(False)
            self.text_edit.setVisible(False)
            self.target_group.setVisible(False)
            self.details_group.setVisible(True)
            self.quantity_spin.setEnabled(False)
            self.location_edit.setEnabled(True)
            self.location_edit.setPlaceholderText("Enter location to explore...")
        elif current_data == "escort":
            # Escort objective - show NPC and location
            self.text_edit.setEnabled(False)
            self.text_edit.setVisible(False)
            self.target_group.setVisible(True)
            self.target_group.setTitle("NPC to Escort")
            self.details_group.setVisible(True)
            self.quantity_spin.setEnabled(False)
            self.location_edit.setEnabled(True)
            self.location_edit.setPlaceholderText("Enter destination...")
            self.browse_btn.setText("🔍 Browse NPCs...")

    def on_target_id_changed(self):
        """Handle target ID change"""
        # Clear name when ID changes (user should browse again)
        self.target_name_edit.clear()

    def browse_target(self):
        """Browse for target based on objective type"""
        current_type = self.type_combo.currentData()

        if current_type in ["talk", "escort"]:
            # Browse NPCs
            try:
                from .npc_browser_dialog import choose_quest_giver

                npc = choose_quest_giver(parent=self)
                if npc:
                    self.target_id_spin.setValue(npc.npc_id)
                    self.target_name_edit.setText(npc.name)
            except ImportError:
                QMessageBox.warning(
                    self,
                    "NPC Browser Not Available",
                    "NPC browser is not available. Please enter NPC ID manually.",
                )

        elif current_type == "kill":
            # Browse enemies/creatures
            try:
                from .item_browser_widget import ItemBrowserWidget

                dialog = QDialog(self)
                dialog.setWindowTitle("Select Enemy Target")
                dialog.resize(800, 600)

                layout = QVBoxLayout(dialog)

                # Create item browser (reuse for enemies)
                browser = ItemBrowserWidget(data_model=self.data_model)
                browser.set_filter_categories(["creatures", "enemies"])
                layout.addWidget(browser)

                # Buttons
                button_box = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)
                layout.addWidget(button_box)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected = browser.get_selected_item()
                    if selected:
                        self.target_id_spin.setValue(selected.get("id", 0))
                        self.target_name_edit.setText(selected.get("name", ""))
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Enemy Browser Not Available",
                    "Enemy browser is not available. Please enter enemy ID manually.",
                )

        elif current_type == "gather":
            # Browse items
            try:
                from .item_browser_widget import ItemBrowserWidget

                dialog = QDialog(self)
                dialog.setWindowTitle("Select Item to Gather")
                dialog.resize(800, 600)

                layout = QVBoxLayout(dialog)

                browser = ItemBrowserWidget()
                layout.addWidget(browser)

                button_box = QDialogButtonBox(
                    QDialogButtonBox.StandardButton.Ok
                    | QDialogButtonBox.StandardButton.Cancel
                )
                button_box.accepted.connect(dialog.accept)
                button_box.rejected.connect(dialog.reject)
                layout.addWidget(button_box)

                if dialog.exec() == QDialog.DialogCode.Accepted:
                    selected = browser.get_selected_item()
                    if selected:
                        self.target_id_spin.setValue(selected.get("id", 0))
                        self.target_name_edit.setText(selected.get("name", ""))
            except ImportError:
                QMessageBox.warning(
                    self,
                    "Item Browser Not Available",
                    "Item browser is not available. Please enter item ID manually.",
                )

    def load_objective(self, objective: ObjectiveData):
        """Load objective data into form"""
        # Find type in combo
        for i in range(self.type_combo.count()):
            if self.type_combo.itemData(i) == objective.obj_type:
                self.type_combo.setCurrentIndex(i)
                break

        self.text_edit.setText(objective.text)
        self.description_edit.setPlainText(objective.description)
        self.target_id_spin.setValue(objective.target_id)
        self.target_name_edit.setText(objective.target_name)
        self.quantity_spin.setValue(objective.quantity)
        self.location_edit.setText(objective.location)

    def get_objective(self) -> Optional[ObjectiveData]:
        """Get the edited objective"""
        obj_type = self.type_combo.currentData()

        # Validate based on type
        if obj_type == "other":
            text = self.text_edit.text().strip()
            if not text:
                QMessageBox.warning(
                    self, "Invalid Input", "Objective text cannot be empty!"
                )
                return None
        else:
            text = self.text_edit.text().strip()

        target_id = self.target_id_spin.value()
        target_name = self.target_name_edit.text().strip()
        quantity = self.quantity_spin.value()
        location = self.location_edit.text().strip()
        description = self.description_edit.toPlainText().strip()

        # Type-specific validation
        if obj_type in ["talk", "kill", "gather"] and target_id == 0:
            QMessageBox.warning(self, "Invalid Input", "Please select a valid target!")
            return None

        if obj_type in ["explore", "escort"] and not location:
            QMessageBox.warning(self, "Invalid Input", "Please enter a location!")
            return None

        return ObjectiveData(
            obj_type=obj_type,
            text=text,
            target_id=target_id,
            target_name=target_name,
            quantity=quantity,
            location=location,
            description=description,
        )


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)

    # Test dialog
    dialog = ObjectiveEditorDialog()
    if dialog.exec() == QDialog.DialogCode.Accepted:
        obj = dialog.get_objective()
        if obj:
            print(f"Created objective: {obj.get_display_text()}")
            print(f"Data: {obj.to_dict()}")

    sys.exit(app.exec())
