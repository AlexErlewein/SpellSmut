"""
SpellForce Spell Creation System - Level Editor Dialog
"""

from typing import List, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QSpinBox, QDoubleSpinBox, QLabel, QPushButton,
    QMessageBox, QScrollArea, QGroupBox
)
from PySide6.QtCore import Qt

from ..models import SpellLevel


class LevelEditWidget(QWidget):
    """Widget for editing a single spell level"""

    def __init__(self, level: SpellLevel, parent=None):
        super().__init__(parent)
        self.level = level
        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for this level"""
        layout = QFormLayout()

        # Level number (read-only)
        level_label = QLabel(f"Level {self.level.level}")
        level_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addRow("Level:", level_label)

        # Damage range
        self.damage_min_spin = QSpinBox()
        self.damage_min_spin.setRange(0, 10000)
        self.damage_min_spin.setValue(self.level.damage_min)

        self.damage_max_spin = QSpinBox()
        self.damage_max_spin.setRange(0, 10000)
        self.damage_max_spin.setValue(self.level.damage_max)

        damage_layout = QHBoxLayout()
        damage_layout.addWidget(QLabel("Min:"))
        damage_layout.addWidget(self.damage_min_spin)
        damage_layout.addWidget(QLabel("Max:"))
        damage_layout.addWidget(self.damage_max_spin)
        layout.addRow("Damage:", damage_layout)

        # Mana cost
        self.mana_spin = QSpinBox()
        self.mana_spin.setRange(0, 1000)
        self.mana_spin.setValue(self.level.mana_cost)
        layout.addRow("Mana Cost:", self.mana_spin)

        # Cooldown
        self.cooldown_spin = QDoubleSpinBox()
        self.cooldown_spin.setRange(0, 300)
        self.cooldown_spin.setValue(self.level.cooldown)
        self.cooldown_spin.setSingleStep(0.1)
        self.cooldown_spin.setSuffix(" sec")
        layout.addRow("Cooldown:", self.cooldown_spin)

        # Cast time
        self.cast_time_spin = QDoubleSpinBox()
        self.cast_time_spin.setRange(0, 30)
        self.cast_time_spin.setValue(self.level.cast_time)
        self.cast_time_spin.setSingleStep(0.1)
        self.cast_time_spin.setSuffix(" sec")
        layout.addRow("Cast Time:", self.cast_time_spin)

        # Range
        self.range_spin = QDoubleSpinBox()
        self.range_spin.setRange(0, 200)
        self.range_spin.setValue(self.level.range)
        self.range_spin.setSingleStep(0.5)
        self.range_spin.setSuffix(" units")
        layout.addRow("Range:", self.range_spin)

        # AOE Radius
        self.aoe_spin = QDoubleSpinBox()
        self.aoe_spin.setRange(0, 50)
        self.aoe_spin.setValue(self.level.aoe_radius)
        self.aoe_spin.setSingleStep(0.5)
        self.aoe_spin.setSuffix(" units")
        layout.addRow("AOE Radius:", self.aoe_spin)

        # Duration (for buffs/debuffs/summons)
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 300)
        self.duration_spin.setValue(self.level.duration)
        self.duration_spin.setSingleStep(0.5)
        self.duration_spin.setSuffix(" sec")
        layout.addRow("Duration:", self.duration_spin)

        # Balance indicators
        balance_group = QGroupBox("Balance Indicators")
        balance_layout = QVBoxLayout()

        self.dpm_label = QLabel("DPM: --")
        self.dps_label = QLabel("DPS: --")
        self.efficiency_label = QLabel("Efficiency: --")

        balance_layout.addWidget(self.dpm_label)
        balance_layout.addWidget(self.dps_label)
        balance_layout.addWidget(self.efficiency_label)

        balance_group.setLayout(balance_layout)
        layout.addRow(balance_group)

        # Connect signals to update balance
        self.damage_min_spin.valueChanged.connect(self.update_balance)
        self.damage_max_spin.valueChanged.connect(self.update_balance)
        self.mana_spin.valueChanged.connect(self.update_balance)
        self.cooldown_spin.valueChanged.connect(self.update_balance)
        self.cast_time_spin.valueChanged.connect(self.update_balance)

        # Initial balance update
        self.update_balance()

        self.setLayout(layout)

    def update_balance(self):
        """Update balance indicators"""
        damage_min = self.damage_min_spin.value()
        damage_max = self.damage_max_spin.value()
        mana_cost = self.mana_spin.value()
        cooldown = self.cooldown_spin.value()
        cast_time = self.cast_time_spin.value()

        # Calculate metrics
        avg_damage = (damage_min + damage_max) / 2.0 if damage_max > 0 else 0

        dpm = avg_damage / mana_cost if mana_cost > 0 else 0
        effective_time = cast_time + cooldown
        dps = avg_damage / effective_time if effective_time > 0 else 0

        # Determine efficiency rating
        if dpm >= 5:
            efficiency = "Excellent"
        elif dpm >= 3:
            efficiency = "Good"
        elif dpm >= 1.5:
            efficiency = "Fair"
        elif dpm >= 0.5:
            efficiency = "Poor"
        else:
            efficiency = "Very Poor"

        # Update labels
        self.dpm_label.setText(f"DPM: {dpm:.2f}")
        self.dps_label.setText(f"DPS: {dps:.2f}")
        self.efficiency_label.setText(f"Efficiency: {efficiency}")

        # Color code efficiency
        if efficiency == "Excellent":
            color = "#4CAF50"  # Green
        elif efficiency == "Good":
            color = "#8BC34A"  # Light green
        elif efficiency == "Fair":
            color = "#FF9800"  # Orange
        elif efficiency == "Poor":
            color = "#FF5722"  # Red
        else:
            color = "#F44336"  # Dark red

        self.efficiency_label.setStyleSheet(f"color: {color}; font-weight: bold;")

    def get_level_data(self) -> SpellLevel:
        """Get the current level data from the UI"""
        return SpellLevel(
            level=self.level.level,
            damage_min=self.damage_min_spin.value(),
            damage_max=self.damage_max_spin.value(),
            mana_cost=self.mana_spin.value(),
            cooldown=self.cooldown_spin.value(),
            cast_time=self.cast_time_spin.value(),
            range=self.range_spin.value(),
            aoe_radius=self.aoe_spin.value(),
            duration=self.duration_spin.value(),
        )


class LevelEditorDialog(QDialog):
    """Dialog for editing individual spell levels"""

    def __init__(self, levels: List[SpellLevel], parent=None):
        super().__init__(parent)
        self.levels = levels.copy()  # Work on a copy
        self.level_widgets = []  # Store references to level widgets

        self.setWindowTitle("Edit Individual Levels")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        self.setup_ui()

    def setup_ui(self):
        """Set up the dialog UI"""
        layout = QVBoxLayout()

        # Instructions
        instructions = QLabel(
            "Edit each spell level individually. Changes here will override automatic scaling.\n"
            "Use the balance indicators to ensure your spell is reasonably balanced."
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        layout.addWidget(instructions)

        # Tab widget for levels
        self.tabs = QTabWidget()

        # Create a tab for each level
        for level in self.levels:
            level_widget = LevelEditWidget(level)
            self.level_widgets.append(level_widget)

            scroll_area = QScrollArea()
            scroll_area.setWidget(level_widget)
            scroll_area.setWidgetResizable(True)

            self.tabs.addTab(scroll_area, f"Level {level.level}")

        layout.addWidget(self.tabs)

        # Action buttons
        button_layout = QHBoxLayout()

        # Copy/paste buttons
        copy_btn = QPushButton("Copy Level →")
        copy_btn.setToolTip("Copy the current level's stats to the next level")
        copy_btn.clicked.connect(self.copy_level_to_next)

        paste_all_btn = QPushButton("Paste to All")
        paste_all_btn.setToolTip("Apply current level's stats to all levels")
        paste_all_btn.clicked.connect(self.paste_to_all_levels)

        interpolate_btn = QPushButton("Interpolate")
        interpolate_btn.setToolTip("Smoothly interpolate stats between first and last level")
        interpolate_btn.clicked.connect(self.interpolate_levels)

        button_layout.addWidget(copy_btn)
        button_layout.addWidget(paste_all_btn)
        button_layout.addWidget(interpolate_btn)
        button_layout.addStretch()

        # OK/Cancel buttons
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(self.accept)
        ok_btn.setDefault(True)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def copy_level_to_next(self):
        """Copy current level's stats to the next level"""
        current_index = self.tabs.currentIndex()
        if current_index >= len(self.level_widgets) - 1:
            QMessageBox.information(self, "Copy Level",
                                   "Cannot copy to next level - this is the last level!")
            return

        current_widget = self.level_widgets[current_index]
        next_widget = self.level_widgets[current_index + 1]

        # Copy all values
        next_widget.damage_min_spin.setValue(current_widget.damage_min_spin.value())
        next_widget.damage_max_spin.setValue(current_widget.damage_max_spin.value())
        next_widget.mana_spin.setValue(current_widget.mana_spin.value())
        next_widget.cooldown_spin.setValue(current_widget.cooldown_spin.value())
        next_widget.cast_time_spin.setValue(current_widget.cast_time_spin.value())
        next_widget.range_spin.setValue(current_widget.range_spin.value())
        next_widget.aoe_spin.setValue(current_widget.aoe_spin.value())
        next_widget.duration_spin.setValue(current_widget.duration_spin.value())

        # Update balance indicators
        next_widget.update_balance()

        # Switch to next tab
        self.tabs.setCurrentIndex(current_index + 1)

        QMessageBox.information(self, "Copy Level",
                               f"Copied Level {current_index + 1} stats to Level {current_index + 2}")

    def paste_to_all_levels(self):
        """Apply current level's stats to all levels"""
        current_index = self.tabs.currentIndex()
        current_widget = self.level_widgets[current_index]

        # Confirm action
        reply = QMessageBox.question(
            self, "Paste to All Levels",
            f"Apply Level {current_index + 1}'s stats to ALL levels?\n"
            "This will overwrite all other levels!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Get current level's data
        current_data = current_widget.get_level_data()

        # Apply to all other levels
        for i, widget in enumerate(self.level_widgets):
            if i != current_index:
                widget.damage_min_spin.setValue(current_data.damage_min)
                widget.damage_max_spin.setValue(current_data.damage_max)
                widget.mana_spin.setValue(current_data.mana_cost)
                widget.cooldown_spin.setValue(current_data.cooldown)
                widget.cast_time_spin.setValue(current_data.cast_time)
                widget.range_spin.setValue(current_data.range)
                widget.aoe_spin.setValue(current_data.aoe_radius)
                widget.duration_spin.setValue(current_data.duration)
                widget.update_balance()

        QMessageBox.information(self, "Paste Complete",
                               f"Applied Level {current_index + 1} stats to all levels")

    def interpolate_levels(self):
        """Interpolate stats between first and last level"""
        if len(self.level_widgets) < 3:
            QMessageBox.information(self, "Interpolate",
                                   "Need at least 3 levels to interpolate!")
            return

        # Confirm action
        reply = QMessageBox.question(
            self, "Interpolate Levels",
            "Interpolate stats smoothly between Level 1 and the last level?\n"
            "This will overwrite middle levels!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        first_widget = self.level_widgets[0]
        last_widget = self.level_widgets[-1]

        first_data = first_widget.get_level_data()
        last_data = last_widget.get_level_data()

        num_levels = len(self.level_widgets)

        # Interpolate each stat
        for i in range(1, num_levels - 1):  # Skip first and last
            factor = i / (num_levels - 1)  # 0.0 to 1.0

            widget = self.level_widgets[i]

            # Linear interpolation for each stat
            widget.damage_min_spin.setValue(
                int(first_data.damage_min + factor * (last_data.damage_min - first_data.damage_min))
            )
            widget.damage_max_spin.setValue(
                int(first_data.damage_max + factor * (last_data.damage_max - first_data.damage_max))
            )
            widget.mana_spin.setValue(
                int(first_data.mana_cost + factor * (last_data.mana_cost - first_data.mana_cost))
            )
            widget.cooldown_spin.setValue(
                first_data.cooldown + factor * (last_data.cooldown - first_data.cooldown)
            )
            widget.cast_time_spin.setValue(
                first_data.cast_time + factor * (last_data.cast_time - first_data.cast_time)
            )
            widget.range_spin.setValue(
                first_data.range + factor * (last_data.range - first_data.range)
            )
            widget.aoe_spin.setValue(
                first_data.aoe_radius + factor * (last_data.aoe_radius - first_data.aoe_radius)
            )
            widget.duration_spin.setValue(
                first_data.duration + factor * (last_data.duration - first_data.duration)
            )

            widget.update_balance()

        QMessageBox.information(self, "Interpolate Complete",
                               "Interpolated stats between Level 1 and the last level")

    def get_levels(self) -> List[SpellLevel]:
        """Get the updated levels from all widgets"""
        return [widget.get_level_data() for widget in self.level_widgets]


# Test function
def test_level_editor():
    """Test the level editor dialog"""
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    # Create sample levels
    levels = []
    for i in range(1, 16):
        levels.append(SpellLevel(
            level=i,
            damage_min=10 + i * 5,
            damage_max=15 + i * 6,
            mana_cost=5 + i,
            cooldown=3.0,
            cast_time=1.0,
            range=20.0,
            aoe_radius=0.0,
            duration=0.0
        ))

    dialog = LevelEditorDialog(levels)
    if dialog.exec() == QDialog.DialogCode.Accepted:
        updated_levels = dialog.get_levels()
        print("Updated levels:")
        for level in updated_levels:
            print(f"Level {level.level}: {level.damage_min}-{level.damage_max} dmg, {level.mana_cost} mana")


if __name__ == "__main__":
    test_level_editor()