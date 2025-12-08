#!/usr/bin/env python3
"""
Enhanced Search and Navigation System for Quest Editor

Provides comprehensive search, navigation, and filtering capabilities
for quest content, dialogue nodes, conditions, actions, and more.
"""

import re
import fnmatch
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass
from enum import Enum

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QTreeWidget, QTreeWidgetItem, QListWidget, QListWidgetItem,
    QComboBox, QLabel, QCheckBox, QGroupBox, QTabWidget,
    QTextEdit, QSplitter, QFrame, QScrollArea, QSpinBox,
    QProgressBar, QToolButton, QMenu, QDialog, QDialogButtonBox,
    QFormLayout, QTableWidget, QTableWidgetItem, QHeaderView,
    QPushButtonGroup, QButtonGroup, QRadioButton
)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, pyqtSignal
from PySide6.QtGui import QFont, QColor, QIcon, QTextCharFormat, QTextCursor, QKeySequence, QShortcut

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice, DialogueCondition, DialogueAction,
        DialogueConditionType, DialogueActionType
    )
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class SearchScope(Enum):
    """Search scope options"""
    ALL = "all"
    QUEST_INFO = "quest_info"
    DIALOGUE_NODES = "dialogue_nodes"
    CHOICE_TEXT = "choice_text"
    CONDITIONS = "conditions"
    ACTIONS = "actions"
    ANSWER_IDS = "answer_ids"
    FLAGS = "flags"
    VARIABLES = "variables"
    LUA_CODE = "lua_code"


class SearchType(Enum):
    """Search type options"""
    CONTAINS = "contains"
    EXACT = "exact"
    REGEX = "regex"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"


@dataclass
class SearchResult:
    """Represents a single search result"""
    item_type: str  # "quest", "node", "choice", "condition", "action"
    item_id: str
    parent_id: Optional[str] = None
    context: str = ""
    match_text: str = ""
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    quest_name: str = ""
    relevance_score: float = 0.0

    def __str__(self):
        return f"{self.item_type}:{self.item_id} - {self.context[:50]}..."


class SearchWorker(QThread):
    """Background worker for intensive search operations"""

    progress_updated = pyqtSignal(int, int)  # current, total
    result_found = pyqtSignal(SearchResult)
    search_completed = pyqtSignal(list)

    def __init__(self, search_data, search_params):
        super().__init__()
        self.search_data = search_data
        self.search_params = search_params
        self.results = []

    def run(self):
        """Execute search in background"""
        try:
            self.results = self._perform_search()
            self.search_completed.emit(self.results)
        except Exception as e:
            logger.error(f"Search worker error: {e}")
            self.search_completed.emit([])

    def _perform_search(self) -> List[SearchResult]:
        """Perform the actual search"""
        # Implementation depends on search parameters
        results = []
        # ... search logic here ...
        return results


class QuickSearchWidget(QWidget):
    """Quick search widget with keyboard shortcuts"""

    search_requested = Signal(dict)
    result_selected = Signal(SearchResult)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_shortcuts()

    def setup_ui(self):
        """Setup the UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Quick search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Quick search... (Ctrl+K)")
        self.search_input.setMinimumWidth(300)

        # Search type dropdown
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems([
            "Contains", "Exact", "Regex", "Starts With", "Ends With"
        ])
        self.search_type_combo.setMaximumWidth(100)

        # Scope dropdown
        self.scope_combo = QComboBox()
        self.scope_combo.addItems([
            "All Content", "Quest Info", "Dialogue", "Conditions", "Actions", "AnswerIds"
        ])
        self.scope_combo.setMaximumWidth(120)

        # Search button
        self.search_btn = QPushButton("Search")
        self.search_btn.setIcon(self.style().standardIcon(self.style().SP_FileDialogDetailedView))

        # Clear button
        self.clear_btn = QToolButton()
        self.clear_btn.setText("✕")
        self.clear_btn.setToolTip("Clear search")

        # Layout
        layout.addWidget(QLabel("🔍"))
        layout.addWidget(self.search_input)
        layout.addWidget(self.search_type_combo)
        layout.addWidget(self.scope_combo)
        layout.addWidget(self.search_btn)
        layout.addWidget(self.clear_btn)

        # Connections
        self.search_input.returnPressed.connect(self._on_search)
        self.search_btn.clicked.connect(self._on_search)
        self.clear_btn.clicked.connect(self._clear_search)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Ctrl+K for quick search
        shortcut = QShortcut(QKeySequence("Ctrl+K"), self)
        shortcut.activated.connect(self._focus_search)

        # Ctrl+F for find
        shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut.activated.connect(self._focus_search)

    def _focus_search(self):
        """Focus the search input"""
        self.search_input.setFocus()
        self.search_input.selectAll()

    def _on_search(self):
        """Handle search request"""
        query = self.search_input.text().strip()
        if not query:
            return

        search_params = {
            "query": query,
            "type": SearchType(self.search_type_combo.currentText().lower().replace(" ", "_")),
            "scope": SearchScope(self.scope_combo.currentText().lower().replace(" ", "_")),
            "case_sensitive": False
        }

        self.search_requested.emit(search_params)

    def _clear_search(self):
        """Clear search input and results"""
        self.search_input.clear()
        self.search_input.setFocus()


class AdvancedSearchWidget(QWidget):
    """Advanced search with multiple criteria and filters"""

    search_requested = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Search criteria group
        criteria_group = QGroupBox("Search Criteria")
        criteria_layout = QFormLayout(criteria_group)

        # Main search terms
        self.search_text = QLineEdit()
        self.search_text.setPlaceholderText("Enter search terms...")
        criteria_layout.addRow("Search Text:", self.search_text)

        # Search options
        search_options_layout = QHBoxLayout()

        self.case_sensitive_cb = QCheckBox("Case Sensitive")
        self.whole_words_cb = QCheckBox("Whole Words")
        self.regex_cb = QCheckBox("Use Regular Expressions")

        search_options_layout.addWidget(self.case_sensitive_cb)
        search_options_layout.addWidget(self.whole_words_cb)
        search_options_layout.addWidget(self.regex_cb)
        search_options_layout.addStretch()

        criteria_layout.addRow("Options:", search_options_layout)

        # Scopes
        self.scopes_group = QGroupBox("Search Scope")
        scopes_layout = QVBoxLayout(self.scopes_group)

        self.scope_checkboxes = {}
        for scope in SearchScope:
            cb = QCheckBox(scope.value.replace("_", " ").title())
            cb.setChecked(scope == SearchScope.ALL)
            self.scope_checkboxes[scope] = cb
            scopes_layout.addWidget(cb)

        criteria_layout.addRow(self.scopes_group)

        # Filters group
        filters_group = QGroupBox("Additional Filters")
        filters_layout = QFormLayout(filters_group)

        # Quest ID filter
        self.quest_id_filter = QSpinBox()
        self.quest_id_filter.setRange(1, 99999)
        self.quest_id_filter.setSpecialValueText("Any")
        self.quest_id_filter.setValue(0)
        filters_layout.addRow("Quest ID:", self.quest_id_filter)

        # Answer ID filter
        self.answer_id_filter = QSpinBox()
        self.answer_id_filter.setRange(1, 9999)
        self.answer_id_filter.setSpecialValueText("Any")
        self.answer_id_filter.setValue(0)
        filters_layout.addRow("Answer ID:", self.answer_id_filter)

        # Node type filter
        self.node_type_combo = QComboBox()
        self.node_type_combo.addItems(["Any", "Start", "NPC", "Player", "End"])
        filters_layout.addRow("Node Type:", self.node_type_combo)

        # Layout
        layout.addWidget(criteria_group)
        layout.addWidget(filters_group)

        # Search buttons
        button_layout = QHBoxLayout()

        self.search_btn = QPushButton("🔍 Search")
        self.search_btn.setMinimumHeight(35)
        self.reset_btn = QPushButton("Reset")

        button_layout.addWidget(self.reset_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.search_btn)

        layout.addLayout(button_layout)
        layout.addStretch()

        # Connections
        self.search_btn.clicked.connect(self._on_search)
        self.reset_btn.clicked.connect(self._reset_form)

        # Connect scope checkboxes
        for cb in self.scope_checkboxes.values():
            cb.toggled.connect(self._on_scope_changed)

    def _on_scope_changed(self):
        """Handle scope checkbox changes"""
        # If "all" is checked, uncheck others
        if self.scope_checkboxes[SearchScope.ALL].isChecked():
            for scope, cb in self.scope_checkboxes.items():
                if scope != SearchScope.ALL:
                    cb.blockSignals(True)
                    cb.setChecked(False)
                    cb.blockSignals(False)
        else:
            # If any other scope is checked, uncheck "all"
            self.scope_checkboxes[SearchScope.ALL].blockSignals(True)
            self.scope_checkboxes[SearchScope.ALL].setChecked(False)
            self.scope_checkboxes[SearchScope.ALL].blockSignals(False)

    def _on_search(self):
        """Handle advanced search"""
        # Collect search parameters
        search_params = self._collect_search_params()
        self.search_requested.emit(search_params)

    def _collect_search_params(self) -> dict:
        """Collect all search parameters"""
        # Get active scopes
        active_scopes = []
        for scope, cb in self.scope_checkboxes.items():
            if cb.isChecked():
                active_scopes.append(scope)

        # If no specific scopes, use ALL
        if not active_scopes:
            active_scopes = [SearchScope.ALL]

        return {
            "query": self.search_text.text().strip(),
            "type": SearchType.REGEX if self.regex_cb.isChecked() else SearchType.CONTAINS,
            "scope": active_scopes,
            "case_sensitive": self.case_sensitive_cb.isChecked(),
            "whole_words": self.whole_words_cb.isChecked(),
            "quest_id": self.quest_id_filter.value() if self.quest_id_filter.value() > 0 else None,
            "answer_id": self.answer_id_filter.value() if self.answer_id_filter.value() > 0 else None,
            "node_type": self.node_type_combo.currentText() if self.node_type_combo.currentIndex() > 0 else None
        }

    def _reset_form(self):
        """Reset the search form"""
        self.search_text.clear()
        self.case_sensitive_cb.setChecked(False)
        self.whole_words_cb.setChecked(False)
        self.regex_cb.setChecked(False)
        self.quest_id_filter.setValue(0)
        self.answer_id_filter.setValue(0)
        self.node_type_combo.setCurrentIndex(0)

        # Reset scopes
        for scope, cb in self.scope_checkboxes.items():
            cb.setChecked(scope == SearchScope.ALL)


class SearchResultsWidget(QWidget):
    """Widget for displaying search results"""

    result_selected = Signal(SearchResult)
    result_double_clicked = Signal(SearchResult)
    result_context_menu = Signal(SearchResult, QPoint)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_results = []

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Results header
        header_layout = QHBoxLayout()

        self.results_label = QLabel("No results")
        self.results_count_label = QLabel("")

        header_layout.addWidget(self.results_label)
        header_layout.addStretch()
        header_layout.addWidget(self.results_count_label)

        layout.addLayout(header_layout)

        # Results tree
        self.results_tree = QTreeWidget()
        self.results_tree.setHeaderLabels(["Type", "ID", "Context", "Match", "Quest"])
        self.results_tree.setAlternatingRowColors(True)
        self.results_tree.setRootIsDecorated(False)

        # Setup columns
        header = self.results_tree.header()
        header.setStretchLastSection(True)
        header.resizeSection(0, 80)   # Type
        header.resizeSection(1, 100)  # ID
        header.resizeSection(2, 200)  # Context
        header.resizeSection(3, 150)  # Match
        # Quest column stretches to fill remaining space

        layout.addWidget(self.results_tree)

        # Progress bar for long searches
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Connections
        self.results_tree.itemSelectionChanged.connect(self._on_selection_changed)
        self.results_tree.itemDoubleClicked.connect(self._on_item_double_clicked)
        self.results_tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.results_tree.customContextMenuRequested.connect(self._on_context_menu)

    def set_results(self, results: List[SearchResult]):
        """Set search results"""
        self.current_results = results
        self._update_display()

    def _update_display(self):
        """Update the results display"""
        self.results_tree.clear()

        if not self.current_results:
            self.results_label.setText("No results")
            self.results_count_label.setText("")
            return

        # Update header
        self.results_label.setText(f"Search Results")
        self.results_count_label.setText(f"{len(self.current_results)} items")

        # Group results by type and quest
        grouped_results = {}
        for result in self.current_results:
            key = f"{result.item_type}:{result.quest_name}"
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)

        # Add grouped results to tree
        for group_key, group_results in grouped_results.items():
            item_type, quest_name = group_key.split(":", 1)

            # Create group item
            group_item = QTreeWidgetItem(self.results_tree)
            group_item.setText(0, item_type.title())
            group_item.setText(1, f"{len(group_results)} items")
            group_item.setText(2, quest_name or "No Quest")
            group_item.setText(4, "")

            # Style group item
            font = group_item.font(0)
            font.setBold(True)
            group_item.setFont(0, font)
            group_item.setBackground(0, QColor(240, 240, 240))

            # Add individual results
            for result in sorted(group_results, key=lambda x: (x.quest_name, x.parent_id or "", x.item_id)):
                child_item = QTreeWidgetItem(group_item)
                child_item.setText(0, result.item_type)
                child_item.setText(1, result.item_id)
                child_item.setText(2, result.context[:50] + "..." if len(result.context) > 50 else result.context)
                child_item.setText(3, result.match_text[:30] + "..." if len(result.match_text) > 30 else result.match_text)
                child_item.setText(4, result.quest_name)

                # Store result object
                child_item.setData(0, Qt.UserRole, result)

                # Color code by relevance
                if result.relevance_score > 0.8:
                    child_item.setBackground(1, QColor(144, 238, 144, 50))  # Light green
                elif result.relevance_score > 0.5:
                    child_item.setBackground(1, QColor(255, 255, 224, 50))  # Light yellow

            # Expand group by default if few items
            if len(group_results) <= 5:
                group_item.setExpanded(True)

        # Adjust column widths
        for col in range(self.results_tree.columnCount()):
            self.results_tree.resizeColumnToContents(col)

    def _on_selection_changed(self):
        """Handle result selection"""
        items = self.results_tree.selectedItems()
        if items:
            item = items[0]
            result = item.data(0, Qt.UserRole)
            if result:
                self.result_selected.emit(result)

    def _on_item_double_clicked(self, item, column):
        """Handle double click"""
        result = item.data(0, Qt.UserRole)
        if result:
            self.result_double_clicked.emit(result)

    def _on_context_menu(self, pos):
        """Handle context menu"""
        item = self.results_tree.itemAt(pos)
        if item:
            result = item.data(0, Qt.UserRole)
            if result:
                self.result_context_menu.emit(result, self.results_tree.mapToGlobal(pos))


class NavigationWidget(QWidget):
    """Navigation widget with bookmarks and history"""

    navigation_requested = Signal(str, dict)  # destination, context

    def __init__(self, parent=None):
        super().__init__(parent)
        self.bookmarks = []
        self.history = []
        self.current_history_index = -1
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Quick navigation
        quick_group = QGroupBox("Quick Navigation")
        quick_layout = QVBoxLayout(quick_group)

        # Navigation buttons
        nav_buttons = QHBoxLayout()

        self.back_btn = QPushButton("← Back")
        self.forward_btn = QPushButton("Forward →")
        self.up_btn = QPushButton("↑ Up")

        nav_buttons.addWidget(self.back_btn)
        nav_buttons.addWidget(self.forward_btn)
        nav_buttons.addWidget(self.up_btn)
        nav_buttons.addStretch()

        quick_layout.addLayout(nav_buttons)

        # Bookmarks
        bookmarks_layout = QHBoxLayout()
        bookmarks_layout.addWidget(QLabel("Bookmarks:"))

        self.bookmarks_combo = QComboBox()
        self.bookmarks_combo.setMinimumWidth(200)

        self.add_bookmark_btn = QPushButton("📌")
        self.add_bookmark_btn.setToolTip("Add current location")
        self.remove_bookmark_btn = QPushButton("🗑️")
        self.remove_bookmark_btn.setToolTip("Remove bookmark")

        bookmarks_layout.addWidget(self.bookmarks_combo)
        bookmarks_layout.addWidget(self.add_bookmark_btn)
        bookmarks_layout.addWidget(self.remove_bookmark_btn)

        quick_layout.addLayout(bookmarks_layout)
        layout.addWidget(quick_group)

        # Recent items
        recent_group = QGroupBox("Recent Items")
        recent_layout = QVBoxLayout(recent_group)

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)

        recent_layout.addWidget(self.recent_list)
        layout.addWidget(recent_group)

        # Connections
        self.back_btn.clicked.connect(self._go_back)
        self.forward_btn.clicked.connect(self._go_forward)
        self.up_btn.clicked.connect(self._go_up)
        self.add_bookmark_btn.clicked.connect(self._add_bookmark)
        self.remove_bookmark_btn.clicked.connect(self._remove_bookmark)
        self.bookmarks_combo.currentIndexChanged.connect(self._go_to_bookmark)
        self.recent_list.itemDoubleClicked.connect(self._go_to_recent)

    def add_to_history(self, location: str, context: dict = None):
        """Add location to navigation history"""
        if context is None:
            context = {}

        # Remove any forward history
        if self.current_history_index < len(self.history) - 1:
            self.history = self.history[:self.current_history_index + 1]

        # Add new location
        self.history.append((location, context))
        self.current_history_index = len(self.history) - 1

        # Limit history size
        if len(self.history) > 50:
            self.history = self.history[-50:]
            self.current_history_index = len(self.history) - 1

        self._update_navigation_buttons()

        # Add to recent items
        self._add_to_recent(location, context)

    def _add_to_recent(self, location: str, context: dict):
        """Add to recent items list"""
        # Remove if already exists
        for i in range(self.recent_list.count()):
            item = self.recent_list.item(i)
            if item and item.data(Qt.UserRole) == (location, context):
                self.recent_list.takeItem(i)
                break

        # Add to top
        item = QListWidgetItem(f"📍 {location}")
        item.setData(Qt.UserRole, (location, context))
        self.recent_list.insertItem(0, item)

        # Limit recent items
        while self.recent_list.count() > 20:
            self.recent_list.takeItem(self.recent_list.count() - 1)

    def _update_navigation_buttons(self):
        """Update navigation button states"""
        self.back_btn.setEnabled(self.current_history_index > 0)
        self.forward_btn.setEnabled(self.current_history_index < len(self.history) - 1)

    def _go_back(self):
        """Go back in history"""
        if self.current_history_index > 0:
            self.current_history_index -= 1
            location, context = self.history[self.current_history_index]
            self.navigation_requested.emit(location, context)
            self._update_navigation_buttons()

    def _go_forward(self):
        """Go forward in history"""
        if self.current_history_index < len(self.history) - 1:
            self.current_history_index += 1
            location, context = self.history[self.current_history_index]
            self.navigation_requested.emit(location, context)
            self._update_navigation_buttons()

    def _go_up(self):
        """Go up one level"""
        # Implementation depends on current context
        if self.current_history_index >= 0:
            current_location, current_context = self.history[self.current_history_index]
            # Logic to go up one level in the hierarchy
            # This would need to be customized based on the navigation structure

    def _add_bookmark(self):
        """Add current location to bookmarks"""
        if self.current_history_index >= 0:
            location, context = self.history[self.current_history_index]
            bookmark_data = (location, context)

            if bookmark_data not in self.bookmarks:
                self.bookmarks.append(bookmark_data)
                self.bookmarks_combo.addItem(f"📍 {location}")

    def _remove_bookmark(self):
        """Remove selected bookmark"""
        index = self.bookmarks_combo.currentIndex()
        if 0 <= index < len(self.bookmarks):
            del self.bookmarks[index]
            self.bookmarks_combo.removeItem(index)

    def _go_to_bookmark(self):
        """Navigate to selected bookmark"""
        index = self.bookmarks_combo.currentIndex()
        if 0 <= index < len(self.bookmarks):
            location, context = self.bookmarks[index]
            self.navigation_requested.emit(location, context)

    def _go_to_recent(self, item):
        """Go to recent item"""
        location, context = item.data(Qt.UserRole)
        self.navigation_requested.emit(location, context)


class EnhancedSearchNavigationWidget(QWidget):
    """Main enhanced search and navigation widget"""

    search_requested = Signal(dict)
    result_selected = Signal(SearchResult)
    navigate_to = Signal(str, dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Tab widget for different search modes
        self.tab_widget = QTabWidget()

        # Quick search tab
        self.quick_search = QuickSearchWidget()
        self.tab_widget.addTab(self.quick_search, "🔍 Quick Search")

        # Advanced search tab
        self.advanced_search = AdvancedSearchWidget()
        self.tab_widget.addTab(self.advanced_search, "🔎 Advanced")

        layout.addWidget(self.tab_widget)

        # Results and navigation splitter
        splitter = QSplitter(Qt.Vertical)

        # Search results
        self.results_widget = SearchResultsWidget()
        splitter.addWidget(self.results_widget)

        # Navigation
        self.navigation_widget = NavigationWidget()
        splitter.addWidget(self.navigation_widget)

        # Set splitter sizes
        splitter.setSizes([400, 200])
        splitter.setChildrenCollapsible(False)

        layout.addWidget(splitter)

        # Connections
        self.quick_search.search_requested.connect(self._on_search_requested)
        self.advanced_search.search_requested.connect(self._on_search_requested)
        self.results_widget.result_selected.connect(self._on_result_selected)
        self.results_widget.result_double_clicked.connect(self._on_result_double_clicked)
        self.navigation_widget.navigation_requested.connect(self.navigate_to)

    def _on_search_requested(self, search_params: dict):
        """Handle search request"""
        self.search_requested.emit(search_params)

    def _on_result_selected(self, result: SearchResult):
        """Handle result selection"""
        self.result_selected.emit(result)

    def _on_result_double_clicked(self, result: SearchResult):
        """Handle result double click - navigate to item"""
        location = f"{result.item_type}:{result.item_id}"
        context = {
            "quest_name": result.quest_name,
            "parent_id": result.parent_id,
            "line_number": result.line_number
        }
        self.navigate_to.emit(location, context)

    def set_search_results(self, results: List[SearchResult]):
        """Set search results"""
        self.results_widget.set_results(results)

    def add_navigation_history(self, location: str, context: dict = None):
        """Add location to navigation history"""
        self.navigation_widget.add_to_history(location, context)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test the search widget
    widget = EnhancedSearchNavigationWidget()
    widget.resize(800, 600)
    widget.setWindowTitle("Enhanced Search and Navigation")
    widget.show()

    sys.exit(app.exec())