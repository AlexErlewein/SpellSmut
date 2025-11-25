#!/usr/bin/env python3
"""
Import/Export Manager for Quest Editor

Provides comprehensive import/export capabilities for quest data,
dialogue trees, and related content in multiple formats.
"""

import json
import xml.etree.ElementTree as ET
import csv
import yaml
import pickle
import zipfile
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import asdict
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QCheckBox, QGroupBox,
    QFileDialog, QMessageBox, QProgressBar, QTextEdit, QSplitter,
    QTableWidget, QTableWidgetItem, QHeaderView, QFormLayout,
    QDialog, QDialogButtonBox, QSpinBox, QRadioButton, QButtonGroup
)
from PySide6.QtCore import Qt, Signal, QThread, pyqtSignal
from PySide6.QtGui import QFont, QColor, QIcon

try:
    from TirganachReloaded.cff_editor.models.enhanced_dialogue_models import (
        DialogueTree, DialogueNode, DialogueChoice, DialogueCondition, DialogueAction
    )
    from TirganachReloaded.cff_editor.models.quest_models import EnhancedQuestData
    from TirganachReloaded.cff_editor.logging_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)


class ExportFormat:
    """Supported export formats"""
    JSON = "json"
    XML = "xml"
    YAML = "yaml"
    CSV = "csv"
    LUA = "lua"
    PICKLE = "pickle"
    ZIP = "zip"

    @classmethod
    def get_formats(cls):
        """Get all supported formats"""
        return [
            (cls.JSON, "JSON", "JavaScript Object Notation"),
            (cls.XML, "XML", "eXtensible Markup Language"),
            (cls.YAML, "YAML", "YAML Ain't Markup Language"),
            (cls.CSV, "CSV", "Comma Separated Values"),
            (cls.LUA, "LUA", "Lua Script Format"),
            (cls.PICKLE, "Pickle", "Python Pickle Format"),
            (cls.ZIP, "ZIP", "Compressed Archive Package")
        ]

    @classmethod
    def get_file_extension(cls, format_type: str) -> str:
        """Get file extension for format"""
        extensions = {
            cls.JSON: ".json",
            cls.XML: ".xml",
            cls.YAML: ".yaml",
            cls.CSV: ".csv",
            cls.LUA: ".lua",
            cls.PICKLE: ".pkl",
            cls.ZIP: ".zip"
        }
        return extensions.get(format_type, ".txt")

    @classmethod
    def get_mime_type(cls, format_type: str) -> str:
        """Get MIME type for format"""
        mime_types = {
            cls.JSON: "application/json",
            cls.XML: "application/xml",
            cls.YAML: "application/x-yaml",
            cls.CSV: "text/csv",
            cls.LUA: "text/x-lua",
            cls.PICKLE: "application/octet-stream",
            cls.ZIP: "application/zip"
        }
        return mime_types.get(format_type, "text/plain")


class ImportWorker(QThread):
    """Background worker for import operations"""

    progress_updated = pyqtSignal(int, int)  # current, total
    status_updated = pyqtSignal(str)  # status message
    import_completed = pyqtSignal(bool, dict)  # success, imported_data
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, file_path: str, import_options: dict):
        super().__init__()
        self.file_path = file_path
        self.import_options = import_options

    def run(self):
        """Execute import in background"""
        try:
            self.status_updated.emit("Reading file...")
            imported_data = self._import_file()
            self.import_completed.emit(True, imported_data)
        except Exception as e:
            logger.error(f"Import error: {e}")
            self.error_occurred.emit(str(e))

    def _import_file(self) -> dict:
        """Import file based on format"""
        # Implementation depends on file format
        # This would handle different import formats
        return {}


class ExportWorker(QThread):
    """Background worker for export operations"""

    progress_updated = pyqtSignal(int, int)  # current, total
    status_updated = pyqtSignal(str)  # status message
    export_completed = pyqtSignal(bool, str)  # success, output_path
    error_occurred = pyqtSignal(str)  # error message

    def __init__(self, data: dict, output_path: str, export_options: dict):
        super().__init__()
        self.data = data
        self.output_path = output_path
        self.export_options = export_options

    def run(self):
        """Execute export in background"""
        try:
            self.status_updated.emit("Preparing data...")
            self._export_data()
            self.export_completed.emit(True, self.output_path)
        except Exception as e:
            logger.error(f"Export error: {e}")
            self.error_occurred.emit(str(e))

    def _export_data(self):
        """Export data based on format"""
        # Implementation depends on export format
        # This would handle different export formats
        pass


class ImportExportManager(QWidget):
    """Main import/export manager widget"""

    data_imported = Signal(dict)  # Imported data
    export_requested = Signal(str, dict)  # Export format and options

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_worker = None
        self.setup_ui()

    def setup_ui(self):
        """Setup the UI"""
        layout = QVBoxLayout(self)

        # Tab widget for import/export
        self.tab_widget = QTabWidget()

        # Import tab
        self.import_tab = self._setup_import_tab()
        self.tab_widget.addTab(self.import_tab, "📥 Import")

        # Export tab
        self.export_tab = self._setup_export_tab()
        self.tab_widget.addTab(self.export_tab, "📤 Export")

        # Batch operations tab
        self.batch_tab = self._setup_batch_tab()
        self.tab_widget.addTab(self.batch_tab, "🔄 Batch Operations")

        layout.addWidget(self.tab_widget)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.status_label)

    def _setup_import_tab(self) -> QWidget:
        """Setup import tab"""
        import_tab = QWidget()
        layout = QVBoxLayout(import_tab)

        # File selection
        file_group = QGroupBox("File Selection")
        file_layout = QFormLayout(file_group)

        self.import_file_path = QLineEdit()
        self.import_file_path.setPlaceholderText("Select file to import...")
        self.import_file_path.setReadOnly(True)

        self.browse_import_btn = QPushButton("Browse...")
        self.browse_import_btn.setMaximumWidth(100)

        file_path_layout = QHBoxLayout()
        file_path_layout.addWidget(self.import_file_path)
        file_path_layout.addWidget(self.browse_import_btn)
        file_layout.addRow("File:", file_path_layout)

        # Format selection
        self.import_format_combo = QComboBox()
        formats = ["Auto-detect"] + [format_name for _, format_name, _ in ExportFormat.get_formats()]
        self.import_format_combo.addItems(formats)
        file_layout.addRow("Format:", self.import_format_combo)

        # Import options
        options_group = QGroupBox("Import Options")
        options_layout = QVBoxLayout(options_group)

        self.overwrite_existing_cb = QCheckBox("Overwrite existing data")
        self.validate_import_cb = QCheckBox("Validate data after import")
        self.create_backup_cb = QCheckBox("Create backup before import")
        self.create_backup_cb.setChecked(True)

        options_layout.addWidget(self.overwrite_existing_cb)
        options_layout.addWidget(self.validate_import_cb)
        options_layout.addWidget(self.create_backup_cb)

        # Preview section
        preview_group = QGroupBox("Preview")
        preview_layout = QVBoxLayout(preview_group)

        self.import_preview = QTextEdit()
        self.import_preview.setReadOnly(True)
        self.import_preview.setMaximumHeight(200)
        self.import_preview.setPlaceholderText("File preview will appear here...")
        preview_layout.addWidget(self.import_preview)

        # Import button
        self.import_btn = QPushButton("📥 Import Data")
        self.import_btn.setMinimumHeight(40)
        self.import_btn.setEnabled(False)

        # Layout
        layout.addWidget(file_group)
        layout.addWidget(options_group)
        layout.addWidget(preview_group)
        layout.addWidget(self.import_btn)
        layout.addStretch()

        # Connections
        self.browse_import_btn.clicked.connect(self._browse_import_file)
        self.import_file_path.textChanged.connect(self._on_import_file_changed)
        self.import_btn.clicked.connect(self._start_import)

        return import_tab

    def _setup_export_tab(self) -> QWidget:
        """Setup export tab"""
        export_tab = QWidget()
        layout = QVBoxLayout(export_tab)

        # Export selection
        selection_group = QGroupBox("What to Export")
        selection_layout = QVBoxLayout(selection_group)

        self.export_quest_cb = QCheckBox("Quest Information")
        self.export_dialogue_cb = QCheckBox("Dialogue Trees")
        self.export_conditions_cb = QCheckBox("Conditions & Actions")
        self.export_variables_cb = QCheckBox("Variables & Flags")
        self.export_all_cb = QCheckBox("Export Everything")

        # Set all as default
        for cb in [self.export_quest_cb, self.export_dialogue_cb,
                   self.export_conditions_cb, self.export_variables_cb]:
            cb.setChecked(True)

        # Connect "export everything" checkbox
        self.export_all_cb.toggled.connect(self._on_export_all_toggled)

        selection_layout.addWidget(self.export_all_cb)
        selection_layout.addWidget(self.export_quest_cb)
        selection_layout.addWidget(self.export_dialogue_cb)
        selection_layout.addWidget(self.export_conditions_cb)
        selection_layout.addWidget(self.export_variables_cb)

        # Format and destination
        format_group = QGroupBox("Export Format & Destination")
        format_layout = QFormLayout(format_group)

        self.export_format_combo = QComboBox()
        for format_id, format_name, description in ExportFormat.get_formats():
            self.export_format_combo.addItem(f"{format_name} - {description}", format_id)
        format_layout.addRow("Format:", self.export_format_combo)

        self.export_file_path = QLineEdit()
        self.export_file_path.setPlaceholderText("Select output location...")
        self.export_file_path.setReadOnly(True)

        self.browse_export_btn = QPushButton("Browse...")
        self.browse_export_btn.setMaximumWidth(100)

        export_path_layout = QHBoxLayout()
        export_path_layout.addWidget(self.export_file_path)
        export_path_layout.addWidget(self.browse_export_btn)
        format_layout.addRow("Destination:", export_path_layout)

        # Export options
        options_group = QGroupBox("Export Options")
        options_layout = QVBoxLayout(options_group)

        self.include_metadata_cb = QCheckBox("Include metadata (timestamps, version)")
        self.pretty_print_cb = QCheckBox("Pretty print (human-readable)")
        self.pretty_print_cb.setChecked(True)
        self.compress_output_cb = QCheckBox("Compress output (ZIP)")
        self.generate_lua_cb = QCheckBox("Generate LUA code for SpellForce")

        options_layout.addWidget(self.include_metadata_cb)
        options_layout.addWidget(self.pretty_print_cb)
        options_layout.addWidget(self.compress_output_cb)
        options_layout.addWidget(self.generate_lua_cb)

        # Export button
        self.export_btn = QPushButton("📤 Export Data")
        self.export_btn.setMinimumHeight(40)
        self.export_btn.setEnabled(False)

        # Layout
        layout.addWidget(selection_group)
        layout.addWidget(format_group)
        layout.addWidget(options_group)
        layout.addWidget(self.export_btn)
        layout.addStretch()

        # Connections
        self.browse_export_btn.clicked.connect(self._browse_export_file)
        self.export_file_path.textChanged.connect(self._on_export_file_changed)
        self.export_btn.clicked.connect(self._start_export)

        return export_tab

    def _setup_batch_tab(self) -> QWidget:
        """Setup batch operations tab"""
        batch_tab = QWidget()
        layout = QVBoxLayout(batch_tab)

        # Batch export
        batch_export_group = QGroupBox("Batch Export")
        batch_export_layout = QVBoxLayout(batch_export_group)

        batch_export_info = QLabel("Export multiple quests or dialogues at once")
        batch_export_info.setStyleSheet("color: #666; font-style: italic;")
        batch_export_layout.addWidget(batch_export_info)

        # Source selection
        self.batch_source_path = QLineEdit()
        self.batch_source_path.setPlaceholderText("Select source directory...")
        self.batch_source_path.setReadOnly(True)

        self.browse_batch_source_btn = QPushButton("Browse...")
        self.browse_batch_source_btn.setMaximumWidth(100)

        batch_source_layout = QHBoxLayout()
        batch_source_layout.addWidget(self.batch_source_path)
        batch_source_layout.addWidget(self.browse_batch_source_btn)
        batch_export_layout.addLayout(batch_source_layout)

        # Batch export options
        batch_options_layout = QHBoxLayout()
        self.batch_format_combo = QComboBox()
        self.batch_format_combo.addItems(["JSON", "XML", "YAML", "LUA"])
        batch_options_layout.addWidget(QLabel("Format:"))
        batch_options_layout.addWidget(self.batch_format_combo)

        self.batch_recursive_cb = QCheckBox("Include subdirectories")
        batch_options_layout.addWidget(self.batch_recursive_cb)

        batch_export_layout.addLayout(batch_options_layout)

        self.batch_export_btn = QPushButton("📦 Batch Export")
        self.batch_export_btn.setEnabled(False)

        batch_export_layout.addWidget(self.batch_export_btn)

        # Batch import
        batch_import_group = QGroupBox("Batch Import")
        batch_import_layout = QVBoxLayout(batch_import_group)

        batch_import_info = QLabel("Import multiple quest files into the current project")
        batch_import_info.setStyleSheet("color: #666; font-style: italic;")
        batch_import_layout.addWidget(batch_import_info)

        # Target directory
        self.batch_target_path = QLineEdit()
        self.batch_target_path.setPlaceholderText("Select target directory...")
        self.batch_target_path.setReadOnly(True)

        self.browse_batch_target_btn = QPushButton("Browse...")
        self.browse_batch_target_btn.setMaximumWidth(100)

        batch_target_layout = QHBoxLayout()
        batch_target_layout.addWidget(self.batch_target_path)
        batch_target_layout.addWidget(self.browse_batch_target_btn)
        batch_import_layout.addLayout(batch_target_layout)

        self.batch_import_btn = QPushButton("📥 Batch Import")
        self.batch_import_btn.setEnabled(False)

        batch_import_layout.addWidget(self.batch_import_btn)

        # Layout
        layout.addWidget(batch_export_group)
        layout.addWidget(batch_import_group)
        layout.addStretch()

        # Connections
        self.browse_batch_source_btn.clicked.connect(self._browse_batch_source)
        self.browse_batch_target_btn.clicked.connect(self._browse_batch_target)
        self.batch_source_path.textChanged.connect(self._on_batch_source_changed)
        self.batch_target_path.textChanged.connect(self._on_batch_target_changed)
        self.batch_export_btn.clicked.connect(self._start_batch_export)
        self.batch_import_btn.clicked.connect(self._start_batch_import)

        return batch_tab

    def _browse_import_file(self):
        """Browse for import file"""
        file_filter = "All Supported Files (*.json *.xml *.yaml *.csv *.lua *.pkl *.zip);;JSON Files (*.json);;XML Files (*.xml);;YAML Files (*.yaml);;CSV Files (*.csv);;LUA Files (*.lua);;Pickle Files (*.pkl);;ZIP Files (*.zip);;All Files (*.*)"

        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select File to Import", "", file_filter
        )

        if file_path:
            self.import_file_path.setText(file_path)
            self._preview_import_file(file_path)

    def _browse_export_file(self):
        """Browse for export file location"""
        format_id = self.export_format_combo.currentData()
        if not format_id:
            format_id = ExportFormat.JSON

        extension = ExportFormat.get_file_extension(format_id)
        default_name = f"quest_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}{extension}"

        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export As", default_name,
            f"{ExportFormat.get_file_extension(format_id)[1:]} Files (*{ExportFormat.get_file_extension(format_id)})"
        )

        if file_path:
            self.export_file_path.setText(file_path)

    def _browse_batch_source(self):
        """Browse for batch export source directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if directory:
            self.batch_source_path.setText(directory)

    def _browse_batch_target(self):
        """Browse for batch import target directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Target Directory")
        if directory:
            self.batch_target_path.setText(directory)

    def _on_import_file_changed(self):
        """Handle import file path change"""
        file_path = self.import_file_path.text()
        self.import_btn.setEnabled(bool(file_path))

    def _on_export_file_changed(self):
        """Handle export file path change"""
        file_path = self.export_file_path.text()
        self.export_btn.setEnabled(bool(file_path))

    def _on_batch_source_changed(self):
        """Handle batch source directory change"""
        directory = self.batch_source_path.text()
        self.batch_export_btn.setEnabled(bool(directory))

    def _on_batch_target_changed(self):
        """Handle batch target directory change"""
        directory = self.batch_target_path.text()
        self.batch_import_btn.setEnabled(bool(directory))

    def _on_export_all_toggled(self, checked: bool):
        """Handle export all checkbox toggle"""
        self.export_quest_cb.setEnabled(not checked)
        self.export_dialogue_cb.setEnabled(not checked)
        self.export_conditions_cb.setEnabled(not checked)
        self.export_variables_cb.setEnabled(not checked)

        if checked:
            self.export_quest_cb.setChecked(True)
            self.export_dialogue_cb.setChecked(True)
            self.export_conditions_cb.setChecked(True)
            self.export_variables_cb.setChecked(True)

    def _preview_import_file(self, file_path: str):
        """Preview the import file"""
        try:
            self.status_label.setText("Generating preview...")

            # Read file based on format
            file_ext = Path(file_path).suffix.lower()

            if file_ext == '.json':
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    preview_text = json.dumps(data, indent=2)[:1000] + "..." if len(json.dumps(data)) > 1000 else json.dumps(data, indent=2)

            elif file_ext == '.xml':
                tree = ET.parse(file_path)
                root = tree.getroot()
                preview_text = ET.tostring(root, encoding='unicode')[:1000] + "..." if len(ET.tostring(root, encoding='unicode')) > 1000 else ET.tostring(root, encoding='unicode')

            elif file_ext in ['.yaml', '.yml']:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = yaml.safe_load(f)
                    preview_text = yaml.dump(data, indent=2)[:1000] + "..." if len(yaml.dump(data, indent=2)) > 1000 else yaml.dump(data, indent=2)

            elif file_ext == '.csv':
                with open(file_path, 'r', encoding='utf-8') as f:
                    preview_text = f.read()[:1000] + "..." if len(f.read()) > 1000 else f.read()

            else:
                # Default to text preview
                with open(file_path, 'r', encoding='utf-8') as f:
                    preview_text = f.read()[:1000] + "..." if len(f.read()) > 1000 else f.read()

            self.import_preview.setPlainText(preview_text)
            self.status_label.setText(f"Preview loaded: {Path(file_path).name}")

        except Exception as e:
            self.import_preview.setPlainText(f"Error reading file: {e}")
            self.status_label.setText(f"Preview error: {e}")

    def _start_import(self):
        """Start import process"""
        file_path = self.import_file_path.text()
        if not file_path:
            QMessageBox.warning(self, "Import Error", "Please select a file to import")
            return

        # Prepare import options
        import_options = {
            "format": self.import_format_combo.currentText(),
            "overwrite_existing": self.overwrite_existing_cb.isChecked(),
            "validate_import": self.validate_import_cb.isChecked(),
            "create_backup": self.create_backup_cb.isChecked()
        }

        # Start background import
        self.status_label.setText("Starting import...")
        self.progress_bar.setVisible(True)
        self.import_btn.setEnabled(False)

        self.current_worker = ImportWorker(file_path, import_options)
        self.current_worker.progress_updated.connect(self.progress_bar.setValue)
        self.current_worker.status_updated.connect(self.status_label.setText)
        self.current_worker.import_completed.connect(self._on_import_completed)
        self.current_worker.error_occurred.connect(self._on_import_error)
        self.current_worker.start()

    def _start_export(self):
        """Start export process"""
        file_path = self.export_file_path.text()
        if not file_path:
            QMessageBox.warning(self, "Export Error", "Please select an export location")
            return

        # Collect export data (this would come from the quest editor)
        export_data = self._collect_export_data()

        # Prepare export options
        export_options = {
            "format": self.export_format_combo.currentData(),
            "include_metadata": self.include_metadata_cb.isChecked(),
            "pretty_print": self.pretty_print_cb.isChecked(),
            "compress_output": self.compress_output_cb.isChecked(),
            "generate_lua": self.generate_lua_cb.isChecked()
        }

        # Start background export
        self.status_label.setText("Starting export...")
        self.progress_bar.setVisible(True)
        self.export_btn.setEnabled(False)

        self.current_worker = ExportWorker(export_data, file_path, export_options)
        self.current_worker.progress_updated.connect(self.progress_bar.setValue)
        self.current_worker.status_updated.connect(self.status_label.setText)
        self.current_worker.export_completed.connect(self._on_export_completed)
        self.current_worker.error_occurred.connect(self._on_export_error)
        self.current_worker.start()

    def _start_batch_export(self):
        """Start batch export process"""
        QMessageBox.information(self, "Batch Export", "Batch export functionality will be implemented in the next phase")

    def _start_batch_import(self):
        """Start batch import process"""
        QMessageBox.information(self, "Batch Import", "Batch import functionality will be implemented in the next phase")

    def _collect_export_data(self) -> dict:
        """Collect data for export"""
        # This would collect data from the quest editor
        # For now, return empty dict
        return {
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "version": "1.0"
            }
        }

    def _on_import_completed(self, success: bool, imported_data: dict):
        """Handle import completion"""
        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)

        if success:
            self.status_label.setText("Import completed successfully")
            self.data_imported.emit(imported_data)
            QMessageBox.information(self, "Import Complete", "Data imported successfully!")
        else:
            self.status_label.setText("Import failed")
            QMessageBox.warning(self, "Import Failed", "Import could not be completed")

        self.current_worker = None

    def _on_export_completed(self, success: bool, output_path: str):
        """Handle export completion"""
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)

        if success:
            self.status_label.setText(f"Export completed: {Path(output_path).name}")
            QMessageBox.information(self, "Export Complete", f"Data exported to:\n{output_path}")
        else:
            self.status_label.setText("Export failed")
            QMessageBox.warning(self, "Export Failed", "Export could not be completed")

        self.current_worker = None

    def _on_import_error(self, error_message: str):
        """Handle import error"""
        self.progress_bar.setVisible(False)
        self.import_btn.setEnabled(True)
        self.status_label.setText("Import error")
        QMessageBox.critical(self, "Import Error", f"Import failed with error:\n{error_message}")
        self.current_worker = None

    def _on_export_error(self, error_message: str):
        """Handle export error"""
        self.progress_bar.setVisible(False)
        self.export_btn.setEnabled(True)
        self.status_label.setText("Export error")
        QMessageBox.critical(self, "Export Error", f"Export failed with error:\n{error_message}")
        self.current_worker = None

    def set_quest_data(self, quest_data: Optional[dict]):
        """Set quest data for export"""
        # Store quest data for export operations
        self.quest_data = quest_data

    def set_dialogue_trees(self, dialogue_trees: Optional[dict]):
        """Set dialogue trees for export"""
        # Store dialogue trees for export operations
        self.dialogue_trees = dialogue_trees


if __name__ == "__main__":
    import sys
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Test the import/export manager
    widget = ImportExportManager()
    widget.resize(800, 600)
    widget.setWindowTitle("Import/Export Manager")
    widget.show()

    sys.exit(app.exec())