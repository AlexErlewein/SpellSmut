#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""A wizard for creating and editing buildings."""

from pathlib import Path
from PySide6.QtWidgets import (
    QWizard,
    QWizardPage,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QComboBox,
    QPushButton,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QWidget,
)

from ..models.building_data import BuildingData, BuildingResourceCost, BuildingButton


class BuildingWizard(QWizard):
    """The main wizard for creating and editing buildings."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Building Wizard")

        self.building_data = BuildingData()

        self.addPage(BasicsPage(self.building_data))
        self.addPage(VisualsPage(self.building_data))
        self.addPage(ConstructionPage(self.building_data))
        self.addPage(FunctionsPage(self.building_data))
        self.addPage(PlanItemPage(self.building_data))
        self.addPage(ReviewPage(self.building_data))


class BasicsPage(QWizardPage):
    """Page for defining the basic properties of a building."""

    def __init__(self, building_data: BuildingData, parent=None):
        super().__init__(parent)
        self.building_data = building_data
        self.setTitle("Step 1: Basic Properties")
        self.setSubTitle("Define the core attributes of the building.")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- Form Fields ---
        self.name_label = QLabel("Building Name:")
        self.name_input = QLineEdit()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)

        self.health_label = QLabel("Health:")
        self.health_input = QSpinBox()
        self.health_input.setRange(1, 100000)
        self.health_input.setValue(100)
        layout.addWidget(self.health_label)
        layout.addWidget(self.health_input)

        self.race_label = QLabel("Race:")
        self.race_combo = QComboBox()
        self.race_combo.addItems(["HUMANS", "ELVES", "DWARVES", "ORCS", "TROLLS", "DARKELVES"])
        layout.addWidget(self.race_label)
        layout.addWidget(self.race_combo)

        self.registerField("buildingName*", self.name_input)
        self.registerField("buildingHealth", self.health_input)
        self.registerField("buildingRace", self.race_combo)

    def validatePage(self):
        self.building_data.name = self.field("buildingName")
        self.building_data.health = self.field("buildingHealth")
        self.building_data.race_name = self.race_combo.currentText()
        return True


class VisualsPage(QWizardPage):
    """Page for selecting the building's visual assets."""

    def __init__(self, building_data: BuildingData, parent=None):
        super().__init__(parent)
        self.building_data = building_data
        self.setTitle("Step 2: Visuals & Assets")
        self.setSubTitle("Select the 3D model for the building based on naming convention.")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- UI Elements ---
        self.search_button = QPushButton("Find Matching Assets")
        layout.addWidget(self.search_button)

        self.asset_list = QListWidget()
        layout.addWidget(self.asset_list)

        self.selected_asset_label = QLabel("Selected Asset Model (*.msb):" )
        self.selected_asset_input = QLineEdit()
        self.selected_asset_input.setReadOnly(True)
        layout.addWidget(self.selected_asset_label)
        layout.addWidget(self.selected_asset_input)

        # --- Connections ---
        self.search_button.clicked.connect(self.find_assets)
        self.asset_list.currentItemChanged.connect(self.on_asset_selected)

    def initializePage(self):
        """Called when the page is about to be shown."""
        self.find_assets()

    def find_assets(self):
        """Find assets based on the naming convention."""
        self.asset_list.clear()
        name = self.building_data.name.lower().replace(" ", "")
        race = self.building_data.race_name.lower()

        if not name or not race:
            self.asset_list.addItem("Enter a name and race on the previous page.")
            return

        pattern = f"ExtractedAssets/Models/**/building_{race}_{name}*.msb"
        try:
            results = default_api.glob(pattern=pattern)
            if results and results['glob_response']['output']:
                # The output is a string, need to parse it.
                # Assuming the output format is as observed before.
                lines = results['glob_response']['output'].split('\n')
                # First line is a header, so skip it.
                asset_paths = [line.strip() for line in lines[1:] if line.strip()]
                if asset_paths:
                    self.asset_list.addItems(asset_paths)
                else:
                    self.asset_list.addItem(f"No assets found for pattern: {pattern}")
            else:
                self.asset_list.addItem(f"No assets found for pattern: {pattern}")
        except Exception as e:
            self.asset_list.addItem(f"Error searching for assets: {e}")

    def on_asset_selected(self, current, previous):
        """Handle the selection of an asset from the list."""
        if current is not None:
            asset_path = current.text()
            asset_name = Path(asset_path).stem
            self.selected_asset_input.setText(asset_name)
            self.building_data.asset_name = asset_name



class ConstructionPage(QWizardPage):
    """Page for defining the building's construction costs."""

    def __init__(self, building_data: BuildingData, parent=None):
        super().__init__(parent)
        self.building_data = building_data
        self.setTitle("Step 3: Construction Costs")
        self.setSubTitle("Define the resources required to build this structure.")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- UI Elements ---
        self.costs_table = QTableWidget()
        self.costs_table.setColumnCount(2)
        self.costs_table.setHorizontalHeaderLabels(["Resource", "Amount"])
        layout.addWidget(self.costs_table)

        # --- Input Row ---
        input_layout = QHBoxLayout()
        self.resource_combo = QComboBox()
        self.resource_combo.addItems(["Wood", "Stone", "Iron", "Lenya", "Aria", "Moonsilver", "Food"])
        input_layout.addWidget(self.resource_combo)

        self.amount_spinbox = QSpinBox()
        self.amount_spinbox.setRange(1, 10000)
        input_layout.addWidget(self.amount_spinbox)

        self.add_button = QPushButton("Add Cost")
        input_layout.addWidget(self.add_button)
        layout.addLayout(input_layout)

        self.remove_button = QPushButton("Remove Selected Cost")
        layout.addWidget(self.remove_button)

        # --- Connections ---
        self.add_button.clicked.connect(self.add_cost)
        self.remove_button.clicked.connect(self.remove_cost)

    def add_cost(self):
        resource = self.resource_combo.currentText()
        amount = self.amount_spinbox.value()

        row_count = self.costs_table.rowCount()
        self.costs_table.insertRow(row_count)
        self.costs_table.setItem(row_count, 0, QTableWidgetItem(resource))
        self.costs_table.setItem(row_count, 1, QTableWidgetItem(str(amount)))

    def remove_cost(self):
        current_row = self.costs_table.currentRow()
        if current_row >= 0:
            self.costs_table.removeRow(current_row)

    def validatePage(self):
        self.building_data.construction_costs.clear()
        for row in range(self.costs_table.rowCount()):
            resource_item = self.costs_table.item(row, 0)
            amount_item = self.costs_table.item(row, 1)
            if resource_item and amount_item:
                cost = BuildingResourceCost(
                    resource_name=resource_item.text(),
                    amount=int(amount_item.text())
                )
                self.building_data.construction_costs.append(cost)
        return True


class FunctionsPage(QWizardPage):
    """Page for defining building functions like unit training and research."""

    def __init__(self, building_data: BuildingData, parent=None):
        super().__init__(parent)
        self.building_data = building_data
        self.setTitle("Step 4: Functions & Buttons")
        self.setSubTitle("Define what this building can do, such as train units or research upgrades.")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        # --- Tab Widget ---
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- Unit Training Tab ---
        self.unit_tab = QWidget()
        self.unit_layout = QVBoxLayout(self.unit_tab)
        self.tabs.addTab(self.unit_tab, "Unit Training")

        self.unit_list = QListWidget()
        self.unit_layout.addWidget(self.unit_list)

        unit_button_layout = QHBoxLayout()
        self.add_unit_button = QPushButton("Add Unit...")
        self.remove_unit_button = QPushButton("Remove Selected")
        unit_button_layout.addWidget(self.add_unit_button)
        unit_button_layout.addWidget(self.remove_unit_button)
        self.unit_layout.addLayout(unit_button_layout)

        # --- Research Tab ---
        self.research_tab = QWidget()
        self.research_layout = QVBoxLayout(self.research_tab)
        self.tabs.addTab(self.research_tab, "Research/Upgrades")
        self.research_layout.addWidget(QLabel("Research and upgrade configuration will go here."))

        # --- Connections ---
        self.add_unit_button.clicked.connect(self.add_unit)

    def add_unit(self):
        # In a real implementation, this would open a dialog to select a unit.
        # For now, we'll add a placeholder.
        # This functionality depends on reading creature_stats, which is a future step.
        self.unit_list.addItem("Placeholder Unit (e.g., Human Worker)")

    def validatePage(self):
        self.building_data.functions.clear()
        for i in range(self.unit_list.count()):
            # This is a placeholder, we will need to store real unit IDs later
            button = BuildingButton(
                button_id=i, # Placeholder
                name=self.unit_list.item(i).text(),
                action_type='train_unit',
                action_target_id=0 # Placeholder for unit_stats_id
            )
            self.building_data.functions.append(button)
        return True


class PlanItemPage(QWizardPage):
    """Page for configuring the building plan item."""

    def __init__(self, building_data: BuildingData, parent=None):
        super().__init__(parent)
        self.building_data = building_data
        self.setTitle("Step 5: Building Plan")
        self.setSubTitle("This item will be used in-game to construct the building.")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.plan_name_label = QLabel("Building Plan Item Name:")
        self.plan_name_input = QLineEdit()
        layout.addWidget(self.plan_name_label)
        layout.addWidget(self.plan_name_input)

        self.registerField("planName*", self.plan_name_input)

    def initializePage(self):
        """Suggest a default name for the plan."""
        building_name = self.building_data.name
        if building_name:
            self.plan_name_input.setText(f"Plan: {building_name}")

    def validatePage(self):
        self.building_data.plan_item_name = self.field("planName")
        return True


class ReviewPage(QWizardPage):
    """Page for reviewing the building's properties before creation."""

    def __init__(self, building_data: BuildingData, parent=None):
        super().__init__(parent)
        self.building_data = building_data
        self.setTitle("Step 6: Review & Export")
        self.setSubTitle("Review the building details below before finishing.")

        layout = QVBoxLayout(self)
        self.setLayout(layout)

        self.summary_label = QLabel("Building Summary:")
        self.summary_label.setStyleSheet("font-weight: bold;")
        layout.addWidget(self.summary_label)

        self.summary_text = QLabel()
        self.summary_text.setWordWrap(True)
        layout.addWidget(self.summary_text)

    def initializePage(self):
        """Populate the summary text with data from the wizard."""
        summary_lines = [
            f"<b>Name:</b> {self.building_data.name}",
            f"<b>Health:</b> {self.building_data.health}",
            f"<b>Race:</b> {self.building_data.race_name}",
            f"<b>Asset Name:</b> {self.building_data.asset_name}",
            f"<b>Plan Item Name:</b> {self.building_data.plan_item_name}",
            "<b>Construction Costs:</b>"
        ]

        if self.building_data.construction_costs:
            for cost in self.building_data.construction_costs:
                summary_lines.append(f"- {cost.amount} {cost.resource_name}")
        else:
            summary_lines.append("- None")

        summary_lines.append("<b>Functions:</b>")
        if self.building_data.functions:
            for func in self.building_data.functions:
                summary_lines.append(f"- {func.name} (Action: {func.action_type})")
        else:
            summary_lines.append("- None")

        self.summary_text.setText("<br>".join(summary_lines))

