#!/usr/bin/env python3
"""
AnswerId Management Panel

A dedicated panel for managing AnswerIds in the dialogue editor.
Provides:
- Overview of all AnswerIds and their assignments
- Conflict detection and resolution
- Manual assignment of AnswerIds
- Import/export functionality
- Integration with AnswerIdManager
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QSpinBox, QComboBox, QMessageBox, QFrame,
    QSplitter, QTextEdit, QGroupBox, QCheckBox, QHeaderView,
    QDialog, QDialogButtonBox, QFormLayout, QProgressBar
)
from PySide6.QtCore import Qt, Signal, QTimer
from PySide6.QtGui import QFont, QColor, QBrush, QPalette

try:
    from TirganachReloaded.cff_editor.logging_config import get_logger
    from TirganachReloaded.cff_editor.widgets.answer_id_manager import (
        AnswerIdManager, AnswerIdAssignment, AnswerIdConflict
    )
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

    # Mock classes if AnswerIdManager not available
    @dataclass
    class AnswerIdAssignment:
        answer_id: int
        step_id: str
        choice_index: int
        choice_text: str
        auto_assigned: bool = True

    @dataclass
    class AnswerIdConflict:
        answer_id: int
        step_ids: List[str]
        severity: str = "error"

    class AnswerIdManager:
        def __init__(self, start_id=1000, quest_name=""):
            self.assignments = {}
            self.next_available_id = start_id

        def assign_answer_id(self, step_id: str, choice_index: int = 0, choice_text: str = "") -> int:
            return self.next_available_id

        def validate_uniqueness(self) -> List[AnswerIdConflict]:
            return []


class AnswerIdManagementPanel(QWidget):
    """
    AnswerId Management Panel

    Provides a comprehensive interface for managing AnswerIds in dialogue trees.
    Integrates with the AnswerIdManager to provide tracking, validation, and editing.
    """

    # Signals
    answer_id_changed = Signal(str, int, int)  # step_id, choice_index, new_answer_id
    conflict_resolved = Signal(str, int)  # step_id, answer_id
    refresh_requested = Signal()  # Request refresh of main editor

    def __init__(self, answer_id_manager: Optional[AnswerIdManager] = None, parent=None):
        super().__init__(parent)
        self.answer_id_manager = answer_id_manager or AnswerIdManager()
        self.current_dialogue_data = {}
        self.conflicts = []

        self.setup_ui()
        self.setup_connections()
        self.setup_refresh_timer()

    def setup_ui(self):
        """Setup the UI layout"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)

        title_label = QLabel("AnswerId Management")
        title_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header_layout.addWidget(title_label)

        header_layout.addStretch()

        # Action buttons
        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.setToolTip("Refresh AnswerId assignments from dialogue")
        header_layout.addWidget(self.refresh_btn)

        self.auto_assign_btn = QPushButton("⚡ Auto-Assign Missing")
        self.auto_assign_btn.setToolTip("Automatically assign AnswerIds to unassigned choices")
        header_layout.addWidget(self.auto_assign_btn)

        self.resolve_conflicts_btn = QPushButton("⚠️ Resolve Conflicts")
        self.resolve_conflicts_btn.setToolTip("Detect and resolve AnswerId conflicts")
        header_layout.addWidget(self.resolve_conflicts_btn)

        layout.addWidget(header_frame)

        # Main content area - splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        layout.addWidget(splitter)

        # Top: AnswerId Overview Table
        table_frame = self.create_overview_table()
        splitter.addWidget(table_frame)

        # Middle: Conflicts Panel
        conflicts_frame = self.create_conflicts_panel()
        splitter.addWidget(conflicts_frame)

        # Bottom: Assignment/Editing Panel
        editing_frame = self.create_editing_panel()
        splitter.addWidget(editing_frame)

        # Set splitter sizes
        splitter.setSizes([300, 150, 200])

        # Status bar
        self.status_label = QLabel("Ready - No dialogue loaded")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def create_overview_table(self) -> QFrame:
        """Create the AnswerId overview table"""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Table header
        header_label = QLabel("AnswerId Overview")
        header_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header_label)

        # Table widget
        self.overview_table = QTableWidget()
        self.overview_table.setColumnCount(6)
        self.overview_table.setHorizontalHeaderLabels([
            "AnswerId", "Node ID", "Choice", "Choice Text", "Type", "Status"
        ])

        # Configure table
        header = self.overview_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)  # AnswerId
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # Node ID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Choice
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)           # Choice Text
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Type
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)  # Status

        self.overview_table.setAlternatingRowColors(True)
        self.overview_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.overview_table.setSortingEnabled(True)

        layout.addWidget(self.overview_table)

        # Table controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)

        controls_layout.addWidget(QLabel("Filter:"))
        self.filter_edit = QLineEdit()
        self.filter_edit.setPlaceholderText("Search by node ID or choice text...")
        controls_layout.addWidget(self.filter_edit)

        controls_layout.addStretch()

        self.export_btn = QPushButton("📤 Export")
        self.export_btn.setToolTip("Export AnswerId assignments")
        controls_layout.addWidget(self.export_btn)

        self.import_btn = QPushButton("📥 Import")
        self.import_btn.setToolTip("Import AnswerId assignments")
        controls_layout.addWidget(self.import_btn)

        layout.addWidget(controls_frame)

        return frame

    def create_conflicts_panel(self) -> QFrame:
        """Create the conflicts detection panel"""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Header with conflict count
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)

        header_label = QLabel("Conflicts & Issues")
        header_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        header_layout.addWidget(header_label)

        self.conflict_count_label = QLabel("0 conflicts")
        self.conflict_count_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        header_layout.addWidget(self.conflict_count_label)

        header_layout.addStretch()

        # Validation controls
        self.validate_btn = QPushButton("🔍 Validate")
        self.validate_btn.setToolTip("Run validation check")
        header_layout.addWidget(self.validate_btn)

        layout.addWidget(header_frame)

        # Conflicts list
        self.conflicts_text = QTextEdit()
        self.conflicts_text.setMaximumHeight(120)
        self.conflicts_text.setFont(QFont("Courier New", 9))
        self.conflicts_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 1px solid #34495e;
            }
        """)
        self.conflicts_text.setPlaceholderText("No conflicts detected. Click 'Validate' to check for issues.")
        layout.addWidget(self.conflicts_text)

        return frame

    def create_editing_panel(self) -> QFrame:
        """Create the AnswerId assignment/editing panel"""
        frame = QFrame()
        layout = QVBoxLayout(frame)

        # Header
        header_label = QLabel("AnswerId Assignment")
        header_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(header_label)

        # Form layout
        form_layout = QFormLayout()

        # Node selection
        self.node_combo = QComboBox()
        self.node_combo.setMinimumWidth(200)
        form_layout.addRow("Target Node:", self.node_combo)

        # Choice selection
        self.choice_combo = QComboBox()
        self.choice_combo.setMinimumWidth(200)
        form_layout.addRow("Choice:", self.choice_combo)

        # AnswerId input
        answer_id_layout = QHBoxLayout()

        self.answer_id_spin = QSpinBox()
        self.answer_id_spin.setMinimum(1)
        self.answer_id_spin.setMaximum(99999)
        self.answer_id_spin.setValue(1000)
        answer_id_layout.addWidget(self.answer_id_spin)

        self.auto_assign_checkbox = QCheckBox("Auto-assign")
        self.auto_assign_checkbox.setChecked(True)
        answer_id_layout.addWidget(self.auto_assign_checkbox)

        answer_id_layout.addStretch()
        form_layout.addRow("AnswerId:", answer_id_layout)

        # Choice text display
        self.choice_text_edit = QTextEdit()
        self.choice_text_edit.setMaximumHeight(60)
        self.choice_text_edit.setPlaceholderText("Choice text will appear here...")
        form_layout.addRow("Choice Text:", self.choice_text_edit)

        layout.addLayout(form_layout)

        # Action buttons
        buttons_layout = QHBoxLayout()

        self.assign_btn = QPushButton("✅ Assign AnswerId")
        self.assign_btn.setToolTip("Assign the specified AnswerId to this choice")
        buttons_layout.addWidget(self.assign_btn)

        self.remove_btn = QPushButton("🗑️ Remove Assignment")
        self.remove_btn.setToolTip("Remove AnswerId assignment from this choice")
        buttons_layout.addWidget(self.remove_btn)

        buttons_layout.addStretch()

        self.goto_node_btn = QPushButton("🔍 Go to Node")
        self.goto_node_btn.setToolTip("Jump to selected node in dialogue editor")
        buttons_layout.addWidget(self.goto_node_btn)

        layout.addLayout(buttons_layout)

        return frame

    def setup_connections(self):
        """Setup signal connections"""
        # Table connections
        self.overview_table.itemSelectionChanged.connect(self.on_table_selection_changed)
        self.overview_table.itemDoubleClicked.connect(self.on_table_item_double_clicked)

        # Filter
        self.filter_edit.textChanged.connect(self.on_filter_changed)

        # Buttons
        self.refresh_btn.clicked.connect(self.refresh_from_dialogue)
        self.auto_assign_btn.clicked.connect(self.auto_assign_missing)
        self.resolve_conflicts_btn.clicked.connect(self.resolve_conflicts)
        self.validate_btn.clicked.connect(self.validate_answer_ids)
        self.export_btn.clicked.connect(self.export_assignments)
        self.import_btn.clicked.connect(self.import_assignments)

        # Editing panel
        self.node_combo.currentTextChanged.connect(self.on_node_changed)
        self.choice_combo.currentIndexChanged.connect(self.on_choice_changed)
        self.auto_assign_checkbox.toggled.connect(self.on_auto_assign_toggled)
        self.assign_btn.clicked.connect(self.assign_answer_id)
        self.remove_btn.clicked.connect(self.remove_answer_id)
        self.goto_node_btn.clicked.connect(self.goto_selected_node)

    def setup_refresh_timer(self):
        """Setup auto-refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.auto_refresh)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds

    def set_dialogue_data(self, dialogue_data: Dict[str, Any]):
        """Set dialogue data and refresh AnswerId tracking"""
        self.current_dialogue_data = dialogue_data
        self.refresh_from_dialogue()

    def refresh_from_dialogue(self):
        """Refresh AnswerId assignments from current dialogue data"""
        if not self.current_dialogue_data or "nodes" not in self.current_dialogue_data:
            self.status_label.setText("No dialogue data available")
            return

        nodes = self.current_dialogue_data["nodes"]

        # Clear current selections
        self.node_combo.clear()
        self.choice_combo.clear()

        # Populate node combo
        node_ids = []
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("node_type", "").upper()
            speaker = node.get("speaker", "")

            # Format: "node_001 (NPC - Rolf)"
            display_text = f"{node_id}"
            if speaker:
                display_text += f" ({node_type} - {speaker})"
            elif node_type:
                display_text += f" ({node_type})"

            self.node_combo.addItem(display_text, node_id)
            node_ids.append(node_id)

        # Update overview table
        self.update_overview_table(nodes)

        # Update conflicts
        self.validate_answer_ids()

        self.status_label.setText(f"Loaded {len(nodes)} nodes with AnswerId tracking")

    def update_overview_table(self, nodes: List[Dict[str, Any]]):
        """Update the overview table with current AnswerId assignments"""
        self.overview_table.setRowCount(0)

        row = 0
        for node in nodes:
            node_id = node.get("id", "")
            node_type = node.get("node_type", "")
            speaker = node.get("speaker", "")
            choices = node.get("choices", [])
            answer_id = node.get("answer_id")

            # Add row for node itself if it has an AnswerId (for OnAnswer patterns)
            if answer_id is not None:
                self.overview_table.insertRow(row)

                self.overview_table.setItem(row, 0, self.create_table_item(str(answer_id), QColor(52, 152, 219)))
                self.overview_table.setItem(row, 1, self.create_table_item(node_id, QColor(41, 128, 185)))
                self.overview_table.setItem(row, 2, self.create_table_item("NODE", QColor(39, 174, 96)))
                self.overview_table.setItem(row, 3, self.create_table_item(f"Node response ({node_type})", QColor(50, 50, 50)))
                self.overview_table.setItem(row, 4, self.create_table_item("Node AnswerId", QColor(150, 150, 150)))
                self.overview_table.setItem(row, 5, self.create_table_item("✓ Valid", QColor(39, 174, 96)))

                row += 1

            # Add rows for each choice
            for i, choice in enumerate(choices):
                choice_text = choice.get("text", f"Choice {i+1}")
                choice_answer_id = choice.get("answer_id")
                next_node = choice.get("next_node", "")

                self.overview_table.insertRow(row)

                # AnswerId
                if choice_answer_id is not None:
                    answer_id_item = self.create_table_item(str(choice_answer_id), QColor(52, 152, 219))
                else:
                    answer_id_item = self.create_table_item("Unassigned", QColor(231, 76, 60))
                self.overview_table.setItem(row, 0, answer_id_item)

                # Node ID
                self.overview_table.setItem(row, 1, self.create_table_item(node_id, QColor(41, 128, 185)))

                # Choice
                choice_letter = chr(65 + i)  # A, B, C, ...
                self.overview_table.setItem(row, 2, self.create_table_item(f"[{choice_letter}]", QColor(142, 68, 173)))

                # Choice text
                self.overview_table.setItem(row, 3, self.create_table_item(choice_text, QColor(50, 50, 50)))

                # Type
                self.overview_table.setItem(row, 4, self.create_table_item("Player Choice", QColor(150, 150, 150)))

                # Status
                if choice_answer_id is not None:
                    if next_node:
                        status_text = "✓ Connected"
                        status_color = QColor(39, 174, 96)
                    else:
                        status_text = "⚠️ No response"
                        status_color = QColor(243, 156, 18)
                else:
                    status_text = "✗ Unassigned"
                    status_color = QColor(231, 76, 60)

                self.overview_table.setItem(row, 5, self.create_table_item(status_text, status_color))

                # Store node data for reference
                self.overview_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, {
                    "node_id": node_id,
                    "choice_index": i,
                    "choice_data": choice
                })

                row += 1

        # Resize table to content
        self.overview_table.resizeColumnsToContents()

    def create_table_item(self, text: str, color: QColor) -> QTableWidgetItem:
        """Create a table item with text color"""
        item = QTableWidgetItem(text)
        item.setForeground(QBrush(color))
        return item

    def on_table_selection_changed(self):
        """Handle table selection change"""
        current_row = self.overview_table.currentRow()
        if current_row < 0:
            return

        answer_id_item = self.overview_table.item(current_row, 0)
        if answer_id_item:
            data = answer_id_item.data(Qt.ItemDataRole.UserRole)
            if data:
                # Update editing panel
                node_id = data["node_id"]
                choice_index = data["choice_index"]
                choice_data = data["choice_data"]

                # Select node in combo
                for i in range(self.node_combo.count()):
                    if self.node_combo.itemData(i) == node_id:
                        self.node_combo.setCurrentIndex(i)
                        break

                # Update choice combo will be triggered by node change

    def on_table_item_double_clicked(self, item):
        """Handle double-click on table item"""
        if item:
            data = item.data(Qt.ItemDataRole.UserRole)
            if data:
                self.goto_node(data["node_id"])

    def on_filter_changed(self, text: str):
        """Handle filter text change"""
        filter_text = text.lower()

        for row in range(self.overview_table.rowCount()):
            node_id_item = self.overview_table.item(row, 1)
            choice_text_item = self.overview_table.item(row, 3)

            if node_id_item and choice_text_item:
                node_id = node_id_item.text().lower()
                choice_text = choice_text_item.text().lower()

                show = filter_text in node_id or filter_text in choice_text
                self.overview_table.setRowHidden(row, not show)

    def on_node_changed(self, node_text: str):
        """Handle node selection change"""
        self.choice_combo.clear()

        # Get current node data
        current_data = self.current_dialogue_data.get("nodes", [])
        selected_node_id = self.node_combo.currentData()

        for node in current_data:
            if node.get("id") == selected_node_id:
                choices = node.get("choices", [])
                for i, choice in enumerate(choices):
                    choice_text = choice.get("text", f"Choice {i+1}")
                    choice_letter = chr(65 + i)
                    self.choice_combo.addItem(f"[{choice_letter}] {choice_text}", i)
                break

    def on_choice_changed(self, index: int):
        """Handle choice selection change"""
        if index < 0:
            return

        selected_node_id = self.node_combo.currentData()
        choice_index = self.choice_combo.currentData()

        # Find the choice data
        for node in self.current_dialogue_data.get("nodes", []):
            if node.get("id") == selected_node_id:
                choices = node.get("choices", [])
                if choice_index < len(choices):
                    choice = choices[choice_index]
                    choice_text = choice.get("text", "")
                    answer_id = choice.get("answer_id")

                    self.choice_text_edit.setPlainText(choice_text)

                    if answer_id is not None:
                        self.answer_id_spin.setValue(answer_id)
                        self.auto_assign_checkbox.setChecked(False)
                    else:
                        self.auto_assign_checkbox.setChecked(True)

                    break

    def on_auto_assign_toggled(self, checked: bool):
        """Handle auto-assign checkbox toggle"""
        self.answer_id_spin.setEnabled(not checked)

    def assign_answer_id(self):
        """Assign AnswerId to selected choice"""
        selected_node_id = self.node_combo.currentData()
        if not selected_node_id:
            QMessageBox.warning(self, "No Selection", "Please select a node first.")
            return

        choice_index = self.choice_combo.currentData()
        if choice_index is None:
            QMessageBox.warning(self, "No Choice", "Please select a choice first.")
            return

        if self.auto_assign_checkbox.isChecked():
            # Auto-assign using AnswerIdManager
            answer_id = self.answer_id_manager.assign_answer_id(selected_node_id, choice_index)
        else:
            # Manual assignment
            answer_id = self.answer_id_spin.value()
            success = self.answer_id_manager.assign_manual_id(selected_node_id, choice_index, answer_id)
            if not success:
                QMessageBox.error(self, "Assignment Failed", f"Could not assign AnswerId {answer_id}. It may be in use.")
                return

        # Update dialogue data
        for node in self.current_dialogue_data.get("nodes", []):
            if node.get("id") == selected_node_id:
                choices = node.get("choices", [])
                if choice_index < len(choices):
                    choices[choice_index]["answer_id"] = answer_id
                    break

        # Refresh display
        self.refresh_from_dialogue()

        # Emit signal
        self.answer_id_changed.emit(selected_node_id, choice_index, answer_id)

        self.status_label.setText(f"Assigned AnswerId {answer_id} to {selected_node_id} choice {choice_index}")

    def remove_answer_id(self):
        """Remove AnswerId assignment from selected choice"""
        selected_node_id = self.node_combo.currentData()
        if not selected_node_id:
            QMessageBox.warning(self, "No Selection", "Please select a node first.")
            return

        choice_index = self.choice_combo.currentData()
        if choice_index is None:
            QMessageBox.warning(self, "No Choice", "Please select a choice first.")
            return

        # Remove from AnswerIdManager
        self.answer_id_manager.remove_assignment(selected_node_id, choice_index)

        # Update dialogue data
        for node in self.current_dialogue_data.get("nodes", []):
            if node.get("id") == selected_node_id:
                choices = node.get("choices", [])
                if choice_index < len(choices):
                    choices[choice_index].pop("answer_id", None)
                    break

        # Refresh display
        self.refresh_from_dialogue()

        self.status_label.setText(f"Removed AnswerId from {selected_node_id} choice {choice_index}")

    def auto_assign_missing(self):
        """Auto-assign AnswerIds to all unassigned choices"""
        assigned_count = 0

        for node in self.current_dialogue_data.get("nodes", []):
            node_id = node.get("id", "")
            choices = node.get("choices", [])

            for i, choice in enumerate(choices):
                if choice.get("answer_id") is None:
                    answer_id = self.answer_id_manager.assign_answer_id(node_id, i, choice.get("text", ""))
                    choice["answer_id"] = answer_id
                    assigned_count += 1

        if assigned_count > 0:
            self.refresh_from_dialogue()
            QMessageBox.information(self, "Auto-Assign Complete",
                                  f"Assigned {assigned_count} AnswerIds automatically.")
        else:
            QMessageBox.information(self, "Auto-Assign", "All choices already have AnswerIds.")

    def validate_answer_ids(self):
        """Validate AnswerIds for conflicts and issues"""
        self.conflicts = self.answer_id_manager.validate_uniqueness()

        if not self.conflicts:
            self.conflicts_text.setPlainText("✅ No AnswerId conflicts detected.")
            self.conflict_count_label.setText("0 conflicts")
            self.conflict_count_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        else:
            # Format conflicts
            lines = ["⚠️ AnswerId conflicts detected:"]
            for conflict in self.conflicts:
                lines.append(f"  • AnswerId {conflict.answer_id}: {len(conflict.step_ids)} nodes")
                for step_id in conflict.step_ids:
                    lines.append(f"    - {step_id}")

            self.conflicts_text.setPlainText("\n".join(lines))
            self.conflict_count_label.setText(f"{len(self.conflicts)} conflicts")
            self.conflict_count_label.setStyleSheet("color: #e74c3c; font-weight: bold;")

    def resolve_conflicts(self):
        """Resolve AnswerId conflicts using the AnswerIdManager"""
        if not self.conflicts:
            QMessageBox.information(self, "No Conflicts", "No conflicts to resolve.")
            return

        # Ask user for resolution strategy
        strategy_dialog = QDialog(self)
        strategy_dialog.setWindowTitle("Choose Conflict Resolution Strategy")
        strategy_dialog.setMinimumWidth(400)

        layout = QVBoxLayout(strategy_dialog)

        # Instructions
        instructions = QLabel("Choose how to resolve AnswerId conflicts:")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)

        # Strategy options
        from PySide6.QtWidgets import QRadioButton, QButtonGroup

        strategy_group = QButtonGroup()
        keep_first_radio = QRadioButton("Keep first assignment, reassign others")
        keep_last_radio = QRadioButton("Keep last assignment, reassign others")
        reassign_all_radio = QRadioButton("Reassign all conflicting assignments")

        strategy_group.addButton(keep_first_radio, 0)
        strategy_group.addButton(keep_last_radio, 1)
        strategy_group.addButton(reassign_all_radio, 2)

        keep_first_radio.setChecked(True)  # Default option

        layout.addWidget(keep_first_radio)
        layout.addWidget(keep_last_radio)
        layout.addWidget(reassign_all_radio)

        # Conflict summary
        conflict_summary = QLabel(f"Found {len(self.conflicts)} conflicts affecting {sum(len(c.step_ids) for c in self.conflicts)} assignments")
        conflict_summary.setStyleSheet("font-weight: bold; color: #e74c3c;")
        layout.addWidget(conflict_summary)

        # Buttons
        from PySide6.QtWidgets import QDialogButtonBox
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(strategy_dialog.accept)
        buttons.rejected.connect(strategy_dialog.reject)
        layout.addWidget(buttons)

        if strategy_dialog.exec() == QDialog.DialogCode.Accepted:
            # Get selected strategy
            strategy_map = ["keep_first", "keep_last", "reassign_all"]
            selected_strategy = strategy_map[strategy_group.checkedId()]

            # Resolve conflicts using AnswerIdManager
            try:
                resolved_count = self.answer_id_manager.resolve_conflicts(selected_strategy)

                if resolved_count > 0:
                    # Update dialogue data with resolved AnswerIds
                    self._update_dialogue_from_manager()

                    # Refresh the display
                    self.refresh_from_dialogue()

                    QMessageBox.information(self, "Conflicts Resolved",
                                          f"Successfully resolved {resolved_count} AnswerId conflicts.")
                else:
                    QMessageBox.information(self, "No Resolutions",
                                          "No conflicts needed resolution.")

            except Exception as e:
                QMessageBox.critical(self, "Resolution Error",
                                    f"Error resolving conflicts: {str(e)}")

    def _update_dialogue_from_manager(self):
        """Update dialogue data from AnswerIdManager assignments"""
        if not self.current_dialogue_data:
            return

        for node in self.current_dialogue_data.get("nodes", []):
            node_id = node.get("id", "")

            # Update node-level AnswerId
            node_answer_id = node.get("answer_id")
            if node_answer_id is not None:
                # Check if this assignment still exists in manager
                current_id = self.answer_id_manager.get_answer_id(node_id, 0)  # Use 0 for node-level
                if current_id != node_answer_id:
                    node["answer_id"] = current_id

            # Update choice-level AnswerIds
            choices = node.get("choices", [])
            for i, choice in enumerate(choices):
                current_id = self.answer_id_manager.get_answer_id(node_id, i)
                if current_id is not None:
                    choice["answer_id"] = current_id
                else:
                    choice.pop("answer_id", None)  # Remove if no longer assigned

    def export_assignments(self):
        """Export AnswerId assignments to file"""
        # Implementation for export functionality
        QMessageBox.information(self, "Export", "Export functionality to be implemented.")

    def import_assignments(self):
        """Import AnswerId assignments from file"""
        # Implementation for import functionality
        QMessageBox.information(self, "Import", "Import functionality to be implemented.")

    def goto_selected_node(self):
        """Go to selected node in dialogue editor"""
        selected_node_id = self.node_combo.currentData()
        if selected_node_id:
            self.goto_node(selected_node_id)

    def goto_node(self, node_id: str):
        """Emit signal to go to specific node"""
        # This would connect to the main editor to jump to the node
        self.refresh_requested.emit()
        self.status_label.setText(f"Navigate to node: {node_id}")

    def auto_refresh(self):
        """Auto-refresh from current data"""
        if self.current_dialogue_data:
            # Only refresh if there are actual changes
            self.validate_answer_ids()


# Test function
def test_answer_id_panel():
    """Test the AnswerId management panel"""
    from PySide6.QtWidgets import QApplication

    app = QApplication([])

    # Create test data
    test_data = {
        "nodes": [
            {
                "id": "node_001",
                "node_type": "npc",
                "speaker": "Guard",
                "text": "Halt! Who goes there?",
                "choices": [
                    {"text": "I'm a traveler.", "answer_id": 1, "next_node": "node_002"},
                    {"text": "None of your business.", "answer_id": 2, "next_node": "node_003"},
                    {"text": "[Show pass]", "answer_id": None}
                ]
            },
            {
                "id": "node_002",
                "answer_id": 1,
                "node_type": "npc",
                "speaker": "Guard",
                "text": "State your business."
            },
            {
                "id": "node_003",
                "answer_id": 2,
                "node_type": "npc",
                "speaker": "Guard",
                "text": "Such insolence! Leave at once!"
            }
        ]
    }

    # Create panel
    panel = AnswerIdManagementPanel()
    panel.set_dialogue_data(test_data)
    panel.show()

    return app.exec()


if __name__ == "__main__":
    test_answer_id_panel()