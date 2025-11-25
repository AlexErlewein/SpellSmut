#!/usr/bin/env python3
"""
Validation Widget for Quest Editor

Provides user interface for validation results and issue management.
"""

from typing import Dict, List, Optional, Any
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QComboBox, QCheckBox, QGroupBox, QTextEdit,
    QSplitter, QTabWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QProgressBar, QFrame, QScrollArea, QFormLayout, QToolButton,
    QDialog, QDialogButtonBox, QSpinBox, QRadioButton, QButtonGroup,
    QCollapsibleButton, QMenu, QMessageBox, QToolBar, QSlider
)
from PySide6.QtCore import Qt, Signal, QThread, pyqtSignal, QTimer
from PySide6.QtGui import QFont, QColor, QIcon, QTextCharFormat, QTextCursor, QBrush

try:
    from TirganachReloaded.cff_editor.widgets.enhanced_validation_system import (
        ValidationEngine, ValidationIssue, ValidationSeverity, ValidationCategory,
        QuestStructureRule, DialogueFlowRule, AnswerIdRule, TextContentRule
    )
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ValidationWorker(QThread):
    """Background worker for validation operations"""

    progress_updated = pyqtSignal(int, int)  # current, total
    status_updated = pyqtSignal(str)  # status message
    validation_completed = pyqtSignal(list)  # validation issues
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, validation_engine: ValidationEngine, data: dict, enabled_rules: List[str]):
        super().__init__()
        self.validation_engine = validation_engine
        self.data = data
        self.enabled_rules = enabled_rules

    def run(self):
        """Execute validation in background"""
        try:
            self.status_updated.emit("Analyzing data structure...")
            self.progress_updated.emit(1, 4)

            # Validate data
            issues = self.validation_engine.validate_data(self.data, self.enabled_rules)

            self.progress_updated.emit(4, 4)
            self.status_updated.emit("Validation complete")
            self.validation_completed.emit(issues)

        except Exception as e:
            logger.error(f"Validation worker error: {e}")
            self.error_occurred.emit(str(e))


class ValidationIssueWidget(QWidget):
    """Widget for displaying a single validation issue"""

    fix_requested = pyqtSignal(str, dict)  # issue_id, context

    def __init__(self, issue: ValidationIssue, parent=None):
        super().__init__(parent)
        self.issue = issue
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Issue header
        header_layout = QHBoxLayout()

        # Severity indicator
        severity_color = ValidationSeverity.get_color(self.issue.severity.value)
        severity_icon = ValidationSeverity.get_icon(self.issue.severity.value)

        severity_label = QLabel(severity_icon)
        severity_label.setStyleSheet(f"background-color: {severity_color.name()}; padding: 2px 6px; border-radius: 3px;")
        header_layout.addWidget(severity_label)

        # Issue title
        title_label = QLabel(self.issue.title)
        title_font = title_label.font()
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)

        # Auto-fix indicator
        if self.issue.auto_fixable:
            fix_indicator = QLabel("🔧 Auto-fixable")
            fix_indicator.setStyleSheet("color: #2e7d32; font-weight: bold;")
            header_layout.addWidget(fix_indicator)

        header_layout.addStretch()

        layout.addLayout(header_layout)

        # Issue description
        if self.issue.description:
            desc_label = QLabel(self.issue.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; margin: 5px 0;")
            layout.addWidget(desc_label)

        # Issue details
        if self.issue.location or self.issue.item_type:
            details_layout = QFormLayout()
            details_layout.setContentsMargins(10, 0, 0, 0)

            if self.issue.item_type:
                type_label = QLabel(self.issue.item_type.title())
                type_label.setStyleSheet("color: #1976d2;")
                details_layout.addRow("Type:", type_label)

            if self.issue.location:
                location_label = QLabel(self.issue.location)
                location_label.setWordWrap(True)
                location_label.setStyleSheet("color: #666; font-style: italic;")
                details_layout.addRow("Location:", location_label)

            layout.addLayout(details_layout)

        # Suggestion
        if self.issue.suggestion:
            suggestion_group = QGroupBox("💡 Suggestion")
            suggestion_layout = QVBoxLayout(suggestion_group)

            suggestion_label = QLabel(self.issue.suggestion)
            suggestion_label.setWordWrap(True)
            suggestion_label.setStyleSheet("color: #2e7d32;")
            suggestion_layout.addWidget(suggestion_label)

            layout.addWidget(suggestion_group)

        # Fix button
        if self.issue.auto_fixable:
            fix_layout = QHBoxLayout()
            fix_layout.addStretch()

            self.fix_btn = QPushButton("🔧 Auto Fix")
            self.fix_btn.clicked.connect(self._on_fix_requested)
            fix_layout.addWidget(self.fix_btn)

            layout.addLayout(fix_layout)

    def _on_fix_requested(self):
        """Handle fix request"""
        context = {
            'issue': self.issue,
            'auto_fix': True
        }
        self.fix_requested.emit(self.issue.id, context)


class ValidationResultsWidget(QWidget):
    """Widget for displaying validation results"""

    issue_selected = pyqtSignal(ValidationIssue)
    fix_requested = pyqtSignal(str, dict)  # issue_id, context
    fix_all_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.issues = []
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Toolbar
        toolbar = QToolBar()
        toolbar.setIconSize(Qt.QSize(16, 16))

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.fix_all_btn = QPushButton("🔧 Fix All")
        self.export_btn = QPushButton("📤 Export Report")

        toolbar.addWidget(self.refresh_btn)
        toolbar.addWidget(self.fix_all_btn)
        toolbar.addWidget(self.export_btn)
        toolbar.addStretch()

        layout.addWidget(toolbar)

        # Summary section
        self.summary_frame = QFrame()
        self.summary_frame.setFrameStyle(QFrame.Box)
        self.summary_frame.setStyleSheet("background-color: #f5f5f5; padding: 10px; border-radius: 5px;")
        summary_layout = QHBoxLayout(self.summary_frame)

        self.total_issues_label = QLabel("Total Issues: 0")
        self.critical_issues_label = QLabel("🔴 Critical: 0")
        self.error_issues_label = QLabel("❌ Error: 0")
        self.warning_issues_label = QLabel("⚠️ Warning: 0")
        self.info_issues_label = QLabel("ℹ️ Info: 0")

        summary_layout.addWidget(self.total_issues_label)
        summary_layout.addWidget(self.critical_issues_label)
        summary_layout.addWidget(self.error_issues_label)
        summary_layout.addWidget(self.warning_issues_label)
        summary_layout.addWidget(self.info_issues_label)
        summary_layout.addStretch()

        layout.addWidget(self.summary_frame)

        # Filter controls
        filter_frame = QFrame()
        filter_layout = QHBoxLayout(filter_frame)

        filter_layout.addWidget(QLabel("Filter:"))

        self.severity_filter = QComboBox()
        self.severity_filter.addItems(["All Severities", "Critical", "Error", "Warning", "Info"])
        filter_layout.addWidget(self.severity_filter)

        self.category_filter = QComboBox()
        self.category_filter.addItems(["All Categories", "Quest Structure", "Dialogue Flow", "Answer IDs", "Text Content", "Conditions", "Actions", "Variables"])
        filter_layout.addWidget(self.category_filter)

        self.auto_fixable_only_cb = QCheckBox("Auto-fixable only")
        filter_layout.addWidget(self.auto_fixable_only_cb)

        filter_layout.addStretch()
        layout.addWidget(filter_frame)

        # Issues display
        self.splitter = QSplitter(Qt.Vertical)

        # Issues tree
        self.issues_tree = QTreeWidget()
        self.issues_tree.setHeaderLabels(["Issue", "Type", "Severity", "Location"])
        self.issues_tree.setAlternatingRowColors(True)
        self.issues_tree.setRootIsDecorated(True)

        # Set column widths
        header = self.issues_tree.header()
        header.setStretchLastSection(True)
        header.resizeSection(0, 300)  # Issue
        header.resizeSection(1, 80)   # Type
        header.resizeSection(2, 80)   # Severity

        # Issue details
        self.issue_details = QScrollArea()
        self.issue_details.setWidgetResizable(True)
        self.issue_details_widget = QWidget()
        self.issue_details_layout = QVBoxLayout(self.issue_details_widget)
        self.issue_details.setWidget(self.issue_details_widget)

        self.splitter.addWidget(self.issues_tree)
        self.splitter.addWidget(self.issue_details)
        self.splitter.setSizes([400, 200])

        layout.addWidget(self.splitter)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

        # Connections
        self.refresh_btn.clicked.connect(self.refresh_results)
        self.fix_all_btn.clicked.connect(self.fix_all_requested.emit)
        self.export_btn.clicked.connect(self.export_report)
        self.severity_filter.currentTextChanged.connect(self.apply_filters)
        self.category_filter.currentTextChanged.connect(self.apply_filters)
        self.auto_fixable_only_cb.toggled.connect(self.apply_filters)
        self.issues_tree.itemSelectionChanged.connect(self._on_issue_selection_changed)

    def set_issues(self, issues: List[ValidationIssue]):
        """Set validation issues"""
        self.issues = issues
        self._update_display()
        self._update_summary()

    def _update_display(self):
        """Update the issues display"""
        self.issues_tree.clear()

        if not self.issues:
            # Show "No issues" message
            no_issues_item = QTreeWidgetItem(self.issues_tree)
            no_issues_item.setText(0, "✅ No validation issues found")
            no_issues_item.setData(0, Qt.UserRole, None)
            self.issues_tree.addTopLevelItem(no_issues_item)
            return

        # Group issues by category
        category_groups = {}
        for issue in self.issues:
            category = issue.category.value
            if category not in category_groups:
                category_groups[category] = []
            category_groups[category].append(issue)

        # Add grouped issues to tree
        for category, category_issues in category_groups.items():
            # Create category group item
            category_item = QTreeWidgetItem(self.issues_tree)
            category_item.setText(0, f"📁 {category.replace('_', ' ').title()}")
            category_item.setText(1, f"{len(category_issues)} issues")

            # Style category item
            font = category_item.font(0)
            font.setBold(True)
            category_item.setFont(0, font)

            # Add issues to category
            for issue in category_issues:
                issue_item = QTreeWidgetItem(category_item)
                issue_item.setText(0, issue.title)
                issue_item.setText(1, issue.item_type)
                issue_item.setText(2, issue.severity.value.title())
                issue_item.setText(3, issue.location)

                # Store issue object
                issue_item.setData(0, Qt.UserRole, issue)

                # Color code by severity
                severity_color = ValidationSeverity.get_color(issue.severity.value)
                issue_item.setBackground(2, severity_color)

        # Expand all categories by default
        self.issues_tree.expandAll()

        # Resize columns
        for col in range(self.issues_tree.columnCount()):
            self.issues_tree.resizeColumnToContents(col)

    def _update_summary(self):
        """Update the summary display"""
        total = len(self.issues)
        critical = sum(1 for issue in self.issues if issue.severity.value == ValidationSeverity.CRITICAL.value)
        error = sum(1 for issue in self.issues if issue.severity.value == ValidationSeverity.ERROR.value)
        warning = sum(1 for issue in self.issues if issue.severity.value == ValidationSeverity.WARNING.value)
        info = sum(1 for issue in self.issues if issue.severity.value == ValidationSeverity.INFO.value)

        self.total_issues_label.setText(f"Total Issues: {total}")
        self.critical_issues_label.setText(f"🔴 Critical: {critical}")
        self.error_issues_label.setText(f"❌ Error: {error}")
        self.warning_issues_label.setText(f"⚠️ Warning: {warning}")
        self.info_issues_label.setText(f"ℹ️ Info: {info}")

        # Enable/disable fix all button
        auto_fixable_count = sum(1 for issue in self.issues if issue.auto_fixable)
        self.fix_all_btn.setEnabled(auto_fixable_count > 0)
        if auto_fixable_count > 0:
            self.fix_all_btn.setText(f"🔧 Fix All ({auto_fixable_count})")

    def apply_filters(self):
        """Apply current filters to issues display"""
        severity_filter = self.severity_filter.currentText()
        category_filter = self.category_filter.currentText()
        auto_fixable_only = self.auto_fixable_only_cb.isChecked()

        # Filter issues
        filtered_issues = []
        for issue in self.issues:
            # Severity filter
            if severity_filter != "All Severities":
                if issue.severity.value.lower() != severity_filter.lower():
                    continue

            # Category filter
            if category_filter != "All Categories":
                if issue.category.value.replace("_", " ").lower() != category_filter.lower():
                    continue

            # Auto-fixable filter
            if auto_fixable_only and not issue.auto_fixable:
                continue

            filtered_issues.append(issue)

        # Update display with filtered issues
        self.issues_tree.clear()
        if not filtered_issues:
            no_results_item = QTreeWidgetItem(self.issues_tree)
            no_results_item.setText(0, "No issues match the current filters")
            self.issues_tree.addTopLevelItem(no_results_item)
        else:
            # Temporarily store original issues and update with filtered
            original_issues = self.issues
            self.issues = filtered_issues
            self._update_display()
            self.issues = original_issues

    def _on_issue_selection_changed(self):
        """Handle issue selection"""
        items = self.issues_tree.selectedItems()
        if items:
            item = items[0]
            issue = item.data(0, Qt.UserRole)
            if issue:
                self.issue_selected.emit(issue)
                self._show_issue_details(issue)
            else:
                self._clear_issue_details()

    def _show_issue_details(self, issue: ValidationIssue):
        """Show details for selected issue"""
        # Clear previous details
        self._clear_issue_details()

        # Create issue widget
        issue_widget = ValidationIssueWidget(issue)
        issue_widget.fix_requested.connect(self.fix_requested.emit)

        self.issue_details_layout.addWidget(issue_widget)

    def _clear_issue_details(self):
        """Clear issue details"""
        # Clear all widgets from details layout
        while self.issue_details_layout.count():
            child = self.issue_details_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def refresh_results(self):
        """Refresh validation results"""
        # This would trigger re-validation
        self.status_label.setText("Refreshing validation...")

    def export_report(self):
        """Export validation report"""
        # This would export the validation results to a file
        self.status_label.setText("Exporting validation report...")

    def show_progress(self, current: int, total: int):
        """Show progress bar"""
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)

    def hide_progress(self):
        """Hide progress bar"""
        self.progress_bar.setVisible(False)

    def set_status(self, status: str):
        """Set status message"""
        self.status_label.setText(status)


class ValidationWidget(QWidget):
    """Main validation widget"""

    validation_completed = pyqtSignal(list)  # validation issues
    fix_applied = pyqtSignal(str, bool)  # issue_id, success

    def __init__(self, parent=None):
        super().__init__(parent)
        self.validation_engine = ValidationEngine()
        self.current_data = {}
        self.current_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Validation controls
        controls_frame = QFrame()
        controls_layout = QHBoxLayout(controls_frame)

        controls_layout.addWidget(QLabel("Validation Rules:"))

        self.run_validation_btn = QPushButton("🔍 Run Validation")
        self.run_validation_btn.clicked.connect(self.run_validation)

        self.validate_on_change_cb = QCheckBox("Auto-validate on change")
        self.validate_on_change_cb.setChecked(True)

        controls_layout.addWidget(self.run_validation_btn)
        controls_layout.addWidget(self.validate_on_change_cb)
        controls_layout.addStretch()

        layout.addWidget(controls_frame)

        # Results widget
        self.results_widget = ValidationResultsWidget()
        self.results_widget.issue_selected.connect(self._on_issue_selected)
        self.results_widget.fix_requested.connect(self._on_fix_requested)
        self.results_widget.fix_all_requested.connect(self._on_fix_all_requested)

        layout.addWidget(self.results_widget)

    def set_data(self, data: dict):
        """Set data for validation"""
        self.current_data = data

        if self.validate_on_change_cb.isChecked():
            self.run_validation()

    def run_validation(self):
        """Run validation on current data"""
        if not self.current_data:
            self.results_widget.set_status("No data to validate")
            return

        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.quit()
            self.current_worker.wait()

        # Start background validation
        self.results_widget.show_progress(0, 4)
        self.results_widget.set_status("Starting validation...")
        self.run_validation_btn.setEnabled(False)

        # Get enabled rules (for now, enable all)
        enabled_rules = [rule.id for rule in self.validation_engine.rules if rule.enabled]

        self.current_worker = ValidationWorker(self.validation_engine, self.current_data, enabled_rules)
        self.current_worker.progress_updated.connect(self.results_widget.show_progress)
        self.current_worker.status_updated.connect(self.results_widget.set_status)
        self.current_worker.validation_completed.connect(self._on_validation_completed)
        self.current_worker.error_occurred.connect(self._on_validation_error)
        self.current_worker.start()

    def _on_validation_completed(self, issues: List[ValidationIssue]):
        """Handle validation completion"""
        self.results_widget.hide_progress()
        self.results_widget.set_status("Validation complete")
        self.run_validation_btn.setEnabled(True)

        self.results_widget.set_issues(issues)
        self.validation_completed.emit(issues)

    def _on_validation_error(self, error_message: str):
        """Handle validation error"""
        self.results_widget.hide_progress()
        self.results_widget.set_status(f"Validation error: {error_message}")
        self.run_validation_btn.setEnabled(True)

        QMessageBox.critical(self, "Validation Error", f"Validation encountered an error:\n{error_message}")

    def _on_issue_selected(self, issue: ValidationIssue):
        """Handle issue selection"""
        # Could emit signal for editor to navigate to the issue location
        pass

    def _on_fix_requested(self, issue_id: str, context: dict):
        """Handle individual fix request"""
        # Find the issue
        issue = None
        for i in self.results_widget.issues:
            if i.id == issue_id:
                issue = i
                break

        if not issue:
            return

        # Apply fix
        success, updated_data, message = self.validation_engine.fix_issue(issue, self.current_data)

        if success:
            self.current_data = updated_data
            self.results_widget.set_status(f"Fix applied: {message}")

            # Run validation again to check if issue is resolved
            QTimer.singleShot(1000, self.run_validation)
        else:
            self.results_widget.set_status(f"Fix failed: {message}")

        self.fix_applied.emit(issue_id, success)

    def _on_fix_all_requested(self):
        """Handle fix all request"""
        auto_fixable_issues = [issue for issue in self.results_widget.issues if issue.auto_fixable]

        if not auto_fixable_issues:
            return

        # Apply fixes for all auto-fixable issues
        fixed_count = 0
        for issue in auto_fixable_issues:
            success, updated_data, message = self.validation_engine.fix_issue(issue, self.current_data)
            if success:
                self.current_data = updated_data
                fixed_count += 1

        self.results_widget.set_status(f"Applied {fixed_count} automatic fixes")

        # Run validation again
        QTimer.singleShot(1000, self.run_validation)


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test the validation widget
    widget = ValidationWidget()
    widget.resize(800, 600)
    widget.setWindowTitle("Quest Validation")
    widget.show()

    # Add some test data
    test_data = {
        'quest_info': {
            'quest_id': 0,
            'quest_name': '',
            'quest_description': 'Test quest'
        },
        'dialogue_trees': {}
    }
    widget.set_data(test_data)

    sys.exit(app.exec())