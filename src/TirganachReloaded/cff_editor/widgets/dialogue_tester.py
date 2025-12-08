"""
Dialogue Testing and Simulation System

This module provides comprehensive testing and simulation capabilities for the dialogue system,
including conversation simulation, flow testing, quest logic validation, and performance analysis.
"""

import json
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Callable
from collections import defaultdict, deque
import random

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QTreeWidget, QTreeWidgetItem, QTextEdit, QLineEdit,
    QLabel, QPushButton, QComboBox, QSpinBox, QCheckBox,
    QGroupBox, QTabWidget, QTableWidget, QTableWidgetItem,
    QProgressBar, QFrame, QScrollArea, QSlider,
    QToolBar, QMenu, QMenuBar, QStatusBar, QMessageBox,
    QProgressBar, QDial, QLCDNumber
)
from PySide6.QtCore import Qt, QTimer, QThread, Signal, QObject, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont, QIcon, QTextCursor


class TestMode(Enum):
    """Testing modes for dialogue simulation."""
    STEP_BY_STEP = "step_by_step"        # Manual progression through dialogue
    AUTO_PLAY = "auto_play"             # Automatic progression with delays
    STRESS_TEST = "stress_test"         # Rapid cycling for performance testing
    COVERAGE_ANALYSIS = "coverage"      # Analyze dialogue coverage
    QUEST_VALIDATION = "validation"     # Validate quest logic and requirements


class TestState(Enum):
    """States during testing."""
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class DialogueNode:
    """Represents a node in the dialogue tree."""
    node_id: str
    text: str
    speaker: str = "Player"
    conditions: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    choices: List[Tuple[str, str]] = field(default_factory=list)  # (choice_text, target_node_id)
    is_entry_point: bool = False
    visited: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSession:
    """Represents a testing session."""
    session_id: str
    name: str
    mode: TestMode
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    current_node: Optional[str] = None
    visited_nodes: List[str] = field(default_factory=list)
    decisions: List[Tuple[str, str]] = field(default_factory=list)  # (node_id, choice_text)
    errors: List[str] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class QuestRequirement:
    """Represents a quest requirement for validation."""
    requirement_id: str
    description: str
    condition_type: str  # "item", "level", "faction", "quest_state", etc.
    value: Any
    comparison: str = ">="  # ">", "<", ">=", "<=", "==", "contains", etc.
    is_met: bool = False
    validation_message: str = ""


class DialogueTestEngine(QObject):
    """Core engine for dialogue testing and simulation."""

    node_visited = Signal(str)  # node_id
    choice_made = Signal(str, str)  # node_id, choice_text
    error_occurred = Signal(str)  # error_message
    session_completed = Signal(str)  # session_id
    test_progress = Signal(int, int)  # current, total

    def __init__(self):
        super().__init__()
        self.nodes: Dict[str, DialogueNode] = {}
        self.current_session: Optional[TestSession] = None
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self._on_test_tick)
        self.test_speed = 1.0  # seconds between steps in auto mode
        self.test_running = False

    def load_dialogue_data(self, dialogue_json: Dict[str, Any]) -> bool:
        """Load dialogue data from JSON structure."""
        try:
            self.nodes.clear()

            # Parse dialogue nodes
            for node_data in dialogue_json.get("nodes", []):
                node = DialogueNode(
                    node_id=node_data["id"],
                    text=node_data["text"],
                    speaker=node_data.get("speaker", "Player"),
                    conditions=node_data.get("conditions", []),
                    actions=node_data.get("actions", []),
                    choices=node_data.get("choices", []),
                    is_entry_point=node_data.get("is_entry_point", False),
                    metadata=node_data.get("metadata", {})
                )
                self.nodes[node.node_id] = node

            # Validate dialogue structure
            return self._validate_dialogue_structure()

        except Exception as e:
            self.error_occurred.emit(f"Failed to load dialogue data: {str(e)}")
            return False

    def _validate_dialogue_structure(self) -> bool:
        """Validate the loaded dialogue structure."""
        if not self.nodes:
            self.error_occurred.emit("No dialogue nodes found")
            return False

        # Check for entry points
        entry_points = [node_id for node_id, node in self.nodes.items() if node.is_entry_point]
        if not entry_points:
            self.error_occurred.emit("No entry points found in dialogue")
            return False

        # Validate node references
        for node_id, node in self.nodes.items():
            for choice_text, target_id in node.choices:
                if target_id not in self.nodes:
                    self.error_occurred.emit(f"Invalid target reference: {target_id} in node {node_id}")
                    return False

        return True

    def start_test_session(self, name: str, mode: TestMode, parameters: Dict[str, Any] = None) -> str:
        """Start a new test session."""
        session_id = str(uuid.uuid4())

        self.current_session = TestSession(
            session_id=session_id,
            name=name,
            mode=mode,
            parameters=parameters or {}
        )

        # Find entry point
        entry_point = next((node_id for node_id, node in self.nodes.items()
                           if node.is_entry_point), None)
        if entry_point:
            self.current_session.current_node = entry_point
            self._visit_node(entry_point)

        # Start testing based on mode
        if mode == TestMode.AUTO_PLAY:
            self.test_running = True
            self.test_timer.start(int(self.test_speed * 1000))
        elif mode == TestMode.STRESS_TEST:
            self.test_running = True
            self.test_speed = 0.1
            self.test_timer.start(100)

        return session_id

    def pause_test_session(self):
        """Pause the current test session."""
        self.test_running = False
        self.test_timer.stop()

    def resume_test_session(self):
        """Resume the current test session."""
        if self.current_session and not self.test_running:
            self.test_running = True
            self.test_timer.start(int(self.test_speed * 1000))

    def stop_test_session(self):
        """Stop the current test session."""
        self.test_running = False
        self.test_timer.stop()

        if self.current_session:
            self.current_session.end_time = time.time()
            self.current_session.statistics = self._calculate_session_statistics()
            self.session_completed.emit(self.current_session.session_id)

    def make_choice(self, choice_text: str) -> bool:
        """Make a choice in the current dialogue node."""
        if not self.current_session or not self.current_session.current_node:
            return False

        current_node = self.nodes.get(self.current_session.current_node)
        if not current_node:
            return False

        # Find the choice
        choice_target = None
        for choice in current_node.choices:
            if choice[0] == choice_text:
                choice_target = choice[1]
                break

        if not choice_target:
            self.error_occurred.emit(f"Invalid choice: {choice_text}")
            return False

        # Record decision
        self.current_session.decisions.append((current_node.node_id, choice_text))
        self.choice_made.emit(current_node.node_id, choice_text)

        # Move to target node
        self._visit_node(choice_target)

        return True

    def _visit_node(self, node_id: str):
        """Visit a dialogue node."""
        if not self.current_session or node_id not in self.nodes:
            return

        self.current_session.current_node = node_id
        self.current_session.visited_nodes.append(node_id)

        node = self.nodes[node_id]
        node.visited = True

        self.node_visited.emit(node_id)

        # Check for session completion
        if not node.choices:  # End of dialogue
            self.stop_test_session()

    def _on_test_tick(self):
        """Handle automatic test progression."""
        if not self.current_session or not self.current_session.current_node:
            return

        current_node = self.nodes.get(self.current_session.current_node)
        if not current_node:
            return

        # Make a random choice for stress testing
        if current_node.choices:
            choice_text = random.choice([choice[0] for choice in current_node.choices])
            self.make_choice(choice_text)

    def _calculate_session_statistics(self) -> Dict[str, Any]:
        """Calculate statistics for the current session."""
        if not self.current_session:
            return {}

        stats = {
            "total_nodes": len(self.nodes),
            "visited_nodes": len(set(self.current_session.visited_nodes)),
            "coverage_percentage": len(set(self.current_session.visited_nodes)) / len(self.nodes) * 100,
            "total_decisions": len(self.current_session.decisions),
            "session_duration": (self.current_session.end_time or time.time()) - self.current_session.start_time,
            "average_time_per_decision": 0,
            "error_count": len(self.current_session.errors),
            "unique_paths": len(set(self.current_session.decisions))
        }

        if self.current_session.decisions:
            stats["average_time_per_decision"] = stats["session_duration"] / len(self.current_session.decisions)

        return stats

    def get_coverage_report(self) -> Dict[str, Any]:
        """Generate a coverage report for all dialogue nodes."""
        report = {
            "total_nodes": len(self.nodes),
            "visited_nodes": sum(1 for node in self.nodes.values() if node.visited),
            "unvisited_nodes": [],
            "coverage_percentage": 0,
            "dead_ends": [],
            "isolated_nodes": [],
            "entry_points": []
        }

        # Categorize nodes
        for node_id, node in self.nodes.items():
            if node.is_entry_point:
                report["entry_points"].append(node_id)
            elif not node.choices:
                report["dead_ends"].append(node_id)
            elif not node.visited:
                report["unvisited_nodes"].append(node_id)

            # Check for isolated nodes (no incoming references)
            has_incoming = False
            for other_node in self.nodes.values():
                if node_id in [choice[1] for choice in other_node.choices]:
                    has_incoming = True
                    break
            if not has_incoming and not node.is_entry_point:
                report["isolated_nodes"].append(node_id)

        report["coverage_percentage"] = (report["visited_nodes"] / report["total_nodes"] * 100) if report["total_nodes"] > 0 else 0

        return report


class DialogueVisualizer(QWidget):
    """Visual representation of the dialogue flow."""

    def __init__(self):
        super().__init__()
        self.nodes: Dict[str, DialogueNode] = {}
        self.current_node: Optional[str] = None
        self.visited_nodes: List[str] = []
        self.node_positions: Dict[str, Tuple[float, float]] = {}
        self.zoom_level = 1.0
        self.setup_ui()

    def setup_ui(self):
        """Setup the visualizer UI."""
        layout = QVBoxLayout()

        # Toolbar for zoom and controls
        toolbar = QToolBar()
        self.zoom_in_btn = QPushButton("+")
        self.zoom_out_btn = QPushButton("-")
        self.reset_view_btn = QPushButton("Reset View")

        toolbar.addWidget(QLabel("Zoom:"))
        toolbar.addWidget(self.zoom_in_btn)
        toolbar.addWidget(self.zoom_out_btn)
        toolbar.addWidget(self.reset_view_btn)

        # Canvas for visualization
        self.canvas = DialogueCanvas()

        # Connect signals
        self.zoom_in_btn.clicked.connect(self.zoom_in)
        self.zoom_out_btn.clicked.connect(self.zoom_out)
        self.reset_view_btn.clicked.connect(self.reset_view)

        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def load_dialogue(self, nodes: Dict[str, DialogueNode]):
        """Load dialogue nodes for visualization."""
        self.nodes = nodes
        self._calculate_node_positions()
        self.canvas.update_visualization(nodes, self.node_positions)

    def set_current_node(self, node_id: str):
        """Set the current node for highlighting."""
        self.current_node = node_id
        self.canvas.set_current_node(node_id)

    def mark_node_visited(self, node_id: str):
        """Mark a node as visited."""
        if node_id not in self.visited_nodes:
            self.visited_nodes.append(node_id)
            self.canvas.update_visited_nodes(self.visited_nodes)

    def _calculate_node_positions(self):
        """Calculate positions for nodes in the visualization."""
        if not self.nodes:
            return

        # Simple hierarchical layout
        levels = defaultdict(list)
        visited = set()
        queue = deque()

        # Find entry points
        entry_points = [node_id for node_id, node in self.nodes.items() if node.is_entry_point]
        if not entry_points:
            return

        for entry_point in entry_points:
            queue.append((entry_point, 0))

        # BFS to determine levels
        while queue:
            node_id, level = queue.popleft()
            if node_id in visited:
                continue

            visited.add(node_id)
            levels[level].append(node_id)

            node = self.nodes.get(node_id)
            if node:
                for _, target_id in node.choices:
                    if target_id not in visited:
                        queue.append((target_id, level + 1))

        # Calculate positions
        max_width = max(len(nodes) for nodes in levels.values()) if levels else 1
        for level, node_list in levels.items():
            for i, node_id in enumerate(node_list):
                x = (i + 1) * 800 / (len(node_list) + 1)
                y = (level + 1) * 150
                self.node_positions[node_id] = (x, y)

    def zoom_in(self):
        """Zoom in the visualization."""
        self.zoom_level = min(self.zoom_level * 1.2, 3.0)
        self.canvas.set_zoom(self.zoom_level)

    def zoom_out(self):
        """Zoom out the visualization."""
        self.zoom_level = max(self.zoom_level / 1.2, 0.3)
        self.canvas.set_zoom(self.zoom_level)

    def reset_view(self):
        """Reset the visualization view."""
        self.zoom_level = 1.0
        self.canvas.set_zoom(self.zoom_level)


class DialogueCanvas(QWidget):
    """Canvas for drawing dialogue nodes and connections."""

    def __init__(self):
        super().__init__()
        self.nodes = {}
        self.node_positions = {}
        self.current_node = None
        self.visited_nodes = []
        self.zoom_level = 1.0
        self.setMinimumSize(800, 600)

    def update_visualization(self, nodes: Dict[str, DialogueNode], positions: Dict[str, Tuple[float, float]]):
        """Update the visualization with new data."""
        self.nodes = nodes
        self.node_positions = positions
        self.update()

    def set_current_node(self, node_id: str):
        """Set the currently active node."""
        self.current_node = node_id
        self.update()

    def update_visited_nodes(self, visited: List[str]):
        """Update the list of visited nodes."""
        self.visited_nodes = visited
        self.update()

    def set_zoom(self, level: float):
        """Set the zoom level."""
        self.zoom_level = level
        self.update()

    def paintEvent(self, event):
        """Paint the dialogue visualization."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Apply zoom transformation
        painter.scale(self.zoom_level, self.zoom_level)

        # Draw connections
        painter.setPen(QColor(150, 150, 150))
        for node_id, node in self.nodes.items():
            if node_id in self.node_positions:
                pos = self.node_positions[node_id]
                for _, target_id in node.choices:
                    if target_id in self.node_positions:
                        target_pos = self.node_positions[target_id]
                        painter.drawLine(pos[0], pos[1], target_pos[0], target_pos[1])

        # Draw nodes
        for node_id, node in self.nodes.items():
            if node_id in self.node_positions:
                self._draw_node(painter, node_id, node)

    def _draw_node(self, painter: QPainter, node_id: str, node: DialogueNode):
        """Draw a single dialogue node."""
        pos = self.node_positions[node_id]
        node_size = 120

        # Determine node color based on state
        if node_id == self.current_node:
            color = QColor(255, 200, 0)  # Gold for current
        elif node_id in self.visited_nodes:
            color = QColor(0, 200, 0)  # Green for visited
        elif node.is_entry_point:
            color = QColor(0, 150, 255)  # Blue for entry point
        else:
            color = QColor(200, 200, 200)  # Gray for unvisited

        # Draw node rectangle
        painter.fillRect(pos[0] - node_size//2, pos[1] - node_size//2, node_size, node_size, color)
        painter.setPen(QColor(0, 0, 0))
        painter.drawRect(pos[0] - node_size//2, pos[1] - node_size//2, node_size, node_size)

        # Draw node text
        painter.drawText(pos[0] - node_size//2, pos[1] - node_size//2, node_size, node_size,
                        Qt.AlignCenter, node_id)


class DialogueTesterWidget(QWidget):
    """Main widget for dialogue testing and simulation."""

    def __init__(self):
        super().__init__()
        self.test_engine = DialogueTestEngine()
        self.current_dialogue_data = {}
        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the main UI layout."""
        layout = QVBoxLayout()

        # Header with test controls
        header = self._create_header()
        layout.addWidget(header)

        # Main content area with tabs
        self.main_tabs = QTabWidget()

        # Test Runner tab
        self.test_runner_tab = self._create_test_runner_tab()
        self.main_tabs.addTab(self.test_runner_tab, "Test Runner")

        # Visual Flow tab
        self.visual_flow_tab = self._create_visual_flow_tab()
        self.main_tabs.addTab(self.visual_flow_tab, "Visual Flow")

        # Coverage Analysis tab
        self.coverage_tab = self._create_coverage_tab()
        self.main_tabs.addTab(self.coverage_tab, "Coverage Analysis")

        # Session History tab
        self.history_tab = self._create_history_tab()
        self.main_tabs.addTab(self.history_tab, "Session History")

        layout.addWidget(self.main_tabs)
        self.setLayout(layout)

    def _create_header(self) -> QWidget:
        """Create the header with test controls."""
        header = QGroupBox("Dialogue Testing Controls")
        layout = QHBoxLayout()

        # Test mode selection
        layout.addWidget(QLabel("Test Mode:"))
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([mode.value for mode in TestMode])
        layout.addWidget(self.mode_combo)

        # Test name
        layout.addWidget(QLabel("Test Name:"))
        self.test_name_edit = QLineEdit("Test Session")
        self.test_name_edit.setMinimumWidth(150)
        layout.addWidget(self.test_name_edit)

        # Test speed (for auto-play)
        layout.addWidget(QLabel("Speed:"))
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(1, 50)  # 0.1s to 5s
        self.speed_slider.setValue(10)  # 1s default
        self.speed_slider.setMaximumWidth(100)
        layout.addWidget(self.speed_slider)

        # Control buttons
        self.load_btn = QPushButton("Load Dialogue")
        self.start_btn = QPushButton("Start Test")
        self.pause_btn = QPushButton("Pause")
        self.stop_btn = QPushButton("Stop")
        self.reset_btn = QPushButton("Reset All")

        layout.addWidget(self.load_btn)
        layout.addWidget(self.start_btn)
        layout.addWidget(self.pause_btn)
        layout.addWidget(self.stop_btn)
        layout.addWidget(self.reset_btn)

        layout.addStretch()

        # Status indicator
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")
        layout.addWidget(self.status_label)

        header.setLayout(layout)
        return header

    def _create_test_runner_tab(self) -> QWidget:
        """Create the test runner tab."""
        tab = QWidget()
        layout = QHBoxLayout()

        # Left panel - Current dialogue
        left_panel = QVBoxLayout()

        # Current node display
        current_node_group = QGroupBox("Current Dialogue Node")
        current_node_layout = QVBoxLayout()

        self.speaker_label = QLabel("Speaker: -")
        self.speaker_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        current_node_layout.addWidget(self.speaker_label)

        self.dialogue_text = QTextEdit()
        self.dialogue_text.setReadOnly(True)
        self.dialogue_text.setMaximumHeight(120)
        current_node_layout.addWidget(self.dialogue_text)

        current_node_group.setLayout(current_node_layout)
        left_panel.addWidget(current_node_group)

        # Choices
        choices_group = QGroupBox("Available Choices")
        choices_layout = QVBoxLayout()

        self.choices_list = QTextEdit()
        self.choices_list.setReadOnly(True)
        self.choices_list.setMaximumHeight(150)
        choices_layout.addWidget(self.choices_list)

        self.choice_input = QLineEdit()
        self.choice_input.setPlaceholderText("Enter your choice here...")
        choices_layout.addWidget(self.choice_input)

        self.make_choice_btn = QPushButton("Make Choice")
        choices_layout.addWidget(self.make_choice_btn)

        choices_group.setLayout(choices_layout)
        left_panel.addWidget(choices_group)

        # Session statistics
        stats_group = QGroupBox("Session Statistics")
        stats_layout = QVBoxLayout()

        self.nodes_visited_label = QLabel("Nodes Visited: 0")
        self.coverage_label = QLabel("Coverage: 0%")
        self.decisions_label = QLabel("Decisions: 0")
        self.errors_label = QLabel("Errors: 0")

        stats_layout.addWidget(self.nodes_visited_label)
        stats_layout.addWidget(self.coverage_label)
        stats_layout.addWidget(self.decisions_label)
        stats_layout.addWidget(self.errors_label)

        stats_group.setLayout(stats_layout)
        left_panel.addWidget(stats_group)

        left_panel.addStretch()

        # Right panel - Test output
        right_panel = QVBoxLayout()

        output_group = QGroupBox("Test Output Log")
        output_layout = QVBoxLayout()

        self.output_log = QTextEdit()
        self.output_log.setReadOnly(True)
        self.output_log.setStyleSheet("font-family: monospace; font-size: 12px;")
        output_layout.addWidget(self.output_log)

        self.clear_log_btn = QPushButton("Clear Log")
        output_layout.addWidget(self.clear_log_btn)

        output_group.setLayout(output_layout)
        right_panel.addWidget(output_group)

        # Add panels to main layout
        splitter = QSplitter(Qt.Horizontal)

        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        splitter.addWidget(left_widget)

        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        splitter.addWidget(right_widget)

        splitter.setSizes([400, 600])
        layout.addWidget(splitter)

        tab.setLayout(layout)
        return tab

    def _create_visual_flow_tab(self) -> QWidget:
        """Create the visual flow tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Visualization canvas
        self.visualizer = DialogueVisualizer()
        layout.addWidget(self.visualizer)

        tab.setLayout(layout)
        return tab

    def _create_coverage_tab(self) -> QWidget:
        """Create the coverage analysis tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Coverage statistics
        stats_group = QGroupBox("Coverage Statistics")
        stats_layout = QHBoxLayout()

        # Progress bars for different metrics
        node_coverage_layout = QVBoxLayout()
        node_coverage_layout.addWidget(QLabel("Node Coverage:"))
        self.node_coverage_bar = QProgressBar()
        node_coverage_layout.addWidget(self.node_coverage_bar)
        self.node_coverage_label = QLabel("0%")
        node_coverage_layout.addWidget(self.node_coverage_label)
        stats_layout.addLayout(node_coverage_layout)

        path_coverage_layout = QVBoxLayout()
        path_coverage_layout.addWidget(QLabel("Path Coverage:"))
        self.path_coverage_bar = QProgressBar()
        path_coverage_layout.addWidget(self.path_coverage_bar)
        self.path_coverage_label = QLabel("0%")
        path_coverage_layout.addWidget(self.path_coverage_label)
        stats_layout.addLayout(path_coverage_layout)

        condition_coverage_layout = QVBoxLayout()
        condition_coverage_layout.addWidget(QLabel("Branch Coverage:"))
        self.condition_coverage_bar = QProgressBar()
        condition_coverage_layout.addWidget(self.condition_coverage_bar)
        self.condition_coverage_label = QLabel("0%")
        condition_coverage_layout.addWidget(self.condition_coverage_label)
        stats_layout.addLayout(condition_coverage_layout)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Coverage details table
        details_group = QGroupBox("Coverage Details")
        details_layout = QVBoxLayout()

        self.coverage_table = QTableWidget()
        self.coverage_table.setColumnCount(5)
        self.coverage_table.setHorizontalHeaderLabels(["Node ID", "Status", "Visit Count", "Conditions", "Actions"])
        self.coverage_table.setAlternatingRowColors(True)
        details_layout.addWidget(self.coverage_table)

        # Generate report button
        self.generate_report_btn = QPushButton("Generate Coverage Report")
        details_layout.addWidget(self.generate_report_btn)

        details_group.setLayout(details_layout)
        layout.addWidget(details_group)

        tab.setLayout(layout)
        return tab

    def _create_history_tab(self) -> QWidget:
        """Create the session history tab."""
        tab = QWidget()
        layout = QVBoxLayout()

        # Session list
        sessions_group = QGroupBox("Test Sessions")
        sessions_layout = QVBoxLayout()

        self.sessions_table = QTableWidget()
        self.sessions_table.setColumnCount(6)
        self.sessions_table.setHorizontalHeaderLabels(["Session ID", "Name", "Mode", "Duration", "Coverage", "Status"])
        self.sessions_table.setAlternatingRowColors(True)
        self.sessions_table.setSelectionBehavior(QTableWidget.SelectRows)
        sessions_layout.addWidget(self.sessions_table)

        # Session details
        details_layout = QHBoxLayout()

        # Left side - Decisions made
        decisions_group = QGroupBox("Session Decisions")
        decisions_layout = QVBoxLayout()
        self.decisions_list = QTextEdit()
        self.decisions_list.setReadOnly(True)
        decisions_layout.addWidget(self.decisions_list)
        decisions_group.setLayout(decisions_layout)

        # Right side - Errors and statistics
        right_details = QVBoxLayout()

        errors_group = QGroupBox("Errors Encountered")
        errors_layout = QVBoxLayout()
        self.errors_list = QTextEdit()
        self.errors_list.setReadOnly(True)
        errors_layout.addWidget(self.errors_list)
        errors_group.setLayout(errors_layout)

        statistics_group = QGroupBox("Session Statistics")
        statistics_layout = QVBoxLayout()
        self.session_stats_label = QLabel("No session selected")
        statistics_layout.addWidget(self.session_stats_label)
        statistics_group.setLayout(statistics_layout)

        right_details.addWidget(errors_group)
        right_details.addWidget(statistics_group)

        details_layout.addWidget(decisions_group)
        details_layout.addLayout(right_details)

        sessions_layout.addLayout(details_layout)
        sessions_group.setLayout(sessions_layout)
        layout.addWidget(sessions_group)

        tab.setLayout(layout)
        return tab

    def setup_connections(self):
        """Setup signal connections."""
        # Header controls
        self.load_btn.clicked.connect(self.load_dialogue_file)
        self.start_btn.clicked.connect(self.start_test)
        self.pause_btn.clicked.connect(self.pause_test)
        self.stop_btn.clicked.connect(self.stop_test)
        self.reset_btn.clicked.connect(self.reset_all)

        self.speed_slider.valueChanged.connect(self.update_test_speed)

        # Test runner controls
        self.choice_input.returnPressed.connect(self.make_choice)
        self.make_choice_btn.clicked.connect(self.make_choice)
        self.clear_log_btn.clicked.connect(self.clear_output_log)

        # Coverage controls
        self.generate_report_btn.clicked.connect(self.generate_coverage_report)

        # Test engine signals
        self.test_engine.node_visited.connect(self.on_node_visited)
        self.test_engine.choice_made.connect(self.on_choice_made)
        self.test_engine.error_occurred.connect(self.on_error_occurred)
        self.test_engine.session_completed.connect(self.on_session_completed)
        self.test_engine.test_progress.connect(self.on_test_progress)

        # Session selection
        self.sessions_table.itemSelectionChanged.connect(self.on_session_selected)

    def load_dialogue_file(self):
        """Load a dialogue file for testing."""
        # This would typically open a file dialog
        # For now, create sample dialogue data
        sample_dialogue = {
            "nodes": [
                {
                    "id": "start",
                    "text": "Welcome to the quest system! How can I help you today?",
                    "speaker": "Guard",
                    "is_entry_point": True,
                    "choices": [
                        ("I need information about the quest.", "quest_info"),
                        ("Tell me about the area.", "area_info"),
                        ("Never mind, I'll leave.", "end_dialogue")
                    ]
                },
                {
                    "id": "quest_info",
                    "text": "The quest involves retrieving an ancient artifact from the nearby ruins. Be careful, as they are heavily guarded.",
                    "speaker": "Guard",
                    "choices": [
                        ("What kind of guards?", "guard_info"),
                        ("What does the artifact look like?", "artifact_info"),
                        ("I accept the quest.", "quest_accepted"),
                        ("This sounds too dangerous.", "decline_quest")
                    ]
                },
                {
                    "id": "area_info",
                    "text": "This area is known for its ancient ruins and mysterious creatures. Many adventurers have come seeking fortune, but few have returned.",
                    "speaker": "Guard",
                    "choices": [
                        ("What creatures are there?", "creature_info"),
                        ("What happened to the other adventurers?", "adventurer_info"),
                        ("I need to go now.", "end_dialogue")
                    ]
                },
                {
                    "id": "end_dialogue",
                    "text": "Good luck on your journey!",
                    "speaker": "Guard",
                    "choices": []
                },
                {
                    "id": "guard_info",
                    "text": "The ruins are guarded by ancient constructs and magical wards. You'll need both strength and magic to survive.",
                    "speaker": "Guard",
                    "choices": [
                        ("What kind of constructs?", "construct_info"),
                        ("Tell me about the wards.", "ward_info"),
                        ("I'll be prepared.", "quest_accepted")
                    ]
                },
                {
                    "id": "artifact_info",
                    "text": "The artifact is an ancient crystal said to contain immense power. It pulses with an otherworldly energy.",
                    "speaker": "Guard",
                    "choices": [
                        ("What kind of power?", "power_info"),
                        ("Where exactly is it located?", "location_info"),
                        ("I must have it.", "quest_accepted")
                    ]
                },
                {
                    "id": "quest_accepted",
                    "text": "Excellent! The artifact is located in the deepest chamber of the ruins. May fortune favor you!",
                    "speaker": "Guard",
                    "choices": [
                        ("Thank you for the information.", "end_dialogue")
                    ]
                },
                {
                    "id": "decline_quest",
                    "text": "I understand. Not everyone is cut out for such dangerous tasks. Perhaps you'll reconsider later.",
                    "speaker": "Guard",
                    "choices": [
                        ("Goodbye.", "end_dialogue")
                    ]
                }
            ]
        }

        self.current_dialogue_data = sample_dialogue
        if self.test_engine.load_dialogue_data(sample_dialogue):
            self.log_output("Dialogue data loaded successfully")
            self.visualizer.load_dialogue(self.test_engine.nodes)
            self.update_coverage_display()
        else:
            self.log_output("Failed to load dialogue data")

    def start_test(self):
        """Start a new test session."""
        mode = TestMode(self.mode_combo.currentText())
        test_name = self.test_name_edit.text()

        session_id = self.test_engine.start_test_session(test_name, mode)

        self.status_label.setText(f"Testing ({mode.value})")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")

        self.log_output(f"Started test session: {session_id} ({mode.value})")
        self.update_session_display()

    def pause_test(self):
        """Pause the current test."""
        self.test_engine.pause_test_session()
        self.status_label.setText("Paused")
        self.status_label.setStyleSheet("color: orange; font-weight: bold;")
        self.log_output("Test session paused")

    def stop_test(self):
        """Stop the current test."""
        self.test_engine.stop_test_session()
        self.status_label.setText("Stopped")
        self.status_label.setStyleSheet("color: red; font-weight: bold;")
        self.log_output("Test session stopped")

    def reset_all(self):
        """Reset all testing data."""
        reply = QMessageBox.question(self, "Reset All",
                                   "This will clear all test data and reset the dialogue nodes. Continue?",
                                   QMessageBox.Yes | QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.test_engine.nodes.clear()
            self.current_dialogue_data.clear()
            self.visualizer.nodes.clear()
            self.visualizer.visited_nodes.clear()
            self.current_dialogue_data.clear()

            self.clear_output_log()
            self.update_session_display()
            self.update_coverage_display()

            self.status_label.setText("Ready")
            self.status_label.setStyleSheet("color: green; font-weight: bold;")
            self.log_output("All test data reset")

    def make_choice(self):
        """Make a choice in the current dialogue."""
        choice_text = self.choice_input.text().strip()
        if choice_text:
            if self.test_engine.make_choice(choice_text):
                self.choice_input.clear()
                self.log_output(f"Choice made: {choice_text}")
            else:
                self.log_output(f"Invalid choice: {choice_text}")

    def update_test_speed(self, value):
        """Update the test speed for auto-play mode."""
        self.test_engine.test_speed = value / 10.0  # Convert slider value to seconds

    def clear_output_log(self):
        """Clear the output log."""
        self.output_log.clear()

    def generate_coverage_report(self):
        """Generate and display a coverage report."""
        report = self.test_engine.get_coverage_report()

        report_text = f"""
        Coverage Report
        ===============

        Total Nodes: {report['total_nodes']}
        Visited Nodes: {report['visited_nodes']}
        Coverage Percentage: {report['coverage_percentage']:.1f}%

        Entry Points: {len(report['entry_points'])}
        Dead Ends: {len(report['dead_ends'])}
        Isolated Nodes: {len(report['isolated_nodes'])}

        Unvisited Nodes: {len(report['unvisited_nodes'])}
        """

        self.log_output(report_text)

        # Show detailed report in a message box
        msg = QMessageBox()
        msg.setWindowTitle("Coverage Report")
        msg.setText(f"Overall Coverage: {report['coverage_percentage']:.1f}%")
        msg.setDetailedText(report_text)
        msg.exec()

    def log_output(self, message: str):
        """Add a message to the output log."""
        timestamp = time.strftime("%H:%M:%S")
        self.output_log.append(f"[{timestamp}] {message}")

        # Auto-scroll to bottom
        cursor = self.output_log.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.output_log.setTextCursor(cursor)

    def update_session_display(self):
        """Update the current session display."""
        if self.test_engine.current_session:
            session = self.test_engine.current_session

            # Update statistics labels
            self.nodes_visited_label.setText(f"Nodes Visited: {len(set(session.visited_nodes))}")
            coverage = (len(set(session.visited_nodes)) / len(self.test_engine.nodes) * 100) if self.test_engine.nodes else 0
            self.coverage_label.setText(f"Coverage: {coverage:.1f}%")
            self.decisions_label.setText(f"Decisions: {len(session.decisions)}")
            self.errors_label.setText(f"Errors: {len(session.errors)}")

    def update_coverage_display(self):
        """Update the coverage display."""
        if not self.test_engine.nodes:
            return

        total_nodes = len(self.test_engine.nodes)
        visited_nodes = sum(1 for node in self.test_engine.nodes.values() if node.visited)

        coverage_percentage = (visited_nodes / total_nodes * 100) if total_nodes > 0 else 0

        self.node_coverage_bar.setValue(int(coverage_percentage))
        self.node_coverage_label.setText(f"{coverage_percentage:.1f}%")

        # Update coverage table
        self.coverage_table.setRowCount(len(self.test_engine.nodes))

        for row, (node_id, node) in enumerate(self.test_engine.nodes.items()):
            status = "Visited" if node.visited else "Unvisited"
            visit_count = self.test_engine.current_session.visited_nodes.count(node_id) if self.test_engine.current_session else 0

            self.coverage_table.setItem(row, 0, QTableWidgetItem(node_id))
            self.coverage_table.setItem(row, 1, QTableWidgetItem(status))
            self.coverage_table.setItem(row, 2, QTableWidgetItem(str(visit_count)))
            self.coverage_table.setItem(row, 3, QTableWidgetItem(", ".join(node.conditions)))
            self.coverage_table.setItem(row, 4, QTableWidgetItem(", ".join(node.actions)))

    # Signal handlers
    def on_node_visited(self, node_id: str):
        """Handle node visitation."""
        node = self.test_engine.nodes.get(node_id)
        if node:
            self.speaker_label.setText(f"Speaker: {node.speaker}")
            self.dialogue_text.setPlainText(node.text)

            # Update choices
            if node.choices:
                choices_text = "\n".join([f"{i+1}. {choice_text}" for i, (choice_text, _) in enumerate(node.choices)])
                self.choices_list.setPlainText(choices_text)
            else:
                self.choices_list.setPlainText("No choices available - dialogue ended")

            # Update visualizer
            self.visualizer.set_current_node(node_id)
            self.visualizer.mark_node_visited(node_id)

            self.log_output(f"Visited node: {node_id} ({node.speaker})")

        self.update_session_display()
        self.update_coverage_display()

    def on_choice_made(self, node_id: str, choice_text: str):
        """Handle choice selection."""
        self.log_output(f"Choice made in {node_id}: {choice_text}")

    def on_error_occurred(self, error_message: str):
        """Handle test errors."""
        self.log_output(f"ERROR: {error_message}")
        if self.test_engine.current_session:
            self.test_engine.current_session.errors.append(error_message)
            self.update_session_display()

    def on_session_completed(self, session_id: str):
        """Handle session completion."""
        self.status_label.setText("Completed")
        self.status_label.setStyleSheet("color: green; font-weight: bold;")

        session = self.test_engine.current_session
        if session:
            duration = session.end_time - session.start_time
            self.log_output(f"Session {session_id} completed in {duration:.2f} seconds")

            # Add to sessions table
            row = self.sessions_table.rowCount()
            self.sessions_table.insertRow(row)

            self.sessions_table.setItem(row, 0, QTableWidgetItem(session_id))
            self.sessions_table.setItem(row, 1, QTableWidgetItem(session.name))
            self.sessions_table.setItem(row, 2, QTableWidgetItem(session.mode.value))
            self.sessions_table.setItem(row, 3, QTableWidgetItem(f"{duration:.2f}s"))

            coverage = session.statistics.get("coverage_percentage", 0)
            self.sessions_table.setItem(row, 4, QTableWidgetItem(f"{coverage:.1f}%"))
            self.sessions_table.setItem(row, 5, QTableWidgetItem("Completed"))

    def on_test_progress(self, current: int, total: int):
        """Handle test progress updates."""
        pass  # Could add a progress bar if needed

    def on_session_selected(self):
        """Handle session selection in the history table."""
        current_row = self.sessions_table.currentRow()
        if current_row >= 0:
            session_id = self.sessions_table.item(current_row, 0).text()
            # Load session details here
            self.log_output(f"Selected session: {session_id}")