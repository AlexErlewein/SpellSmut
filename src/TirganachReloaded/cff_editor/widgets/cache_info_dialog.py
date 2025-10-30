"""
Cache Info Dialog
Shows cache statistics, versions, and management controls
"""

import os
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QGroupBox,
    QFormLayout,
    QTextEdit,
    QFrame,
    QMessageBox,
    QProgressBar,
    QSizePolicy,
)

from ..data_model import CACHE_VERSION
from ..data_providers import SCHEMA_VERSION


class CacheInfoDialog(QDialog):
    """Dialog showing cache information and management controls"""

    def __init__(self, data_model, parent=None):
        super().__init__(parent)
        self.data_model = data_model
        self.setWindowTitle("Cache Information & Management")
        self.setModal(True)
        self.setMinimumSize(600, 500)

        self.setup_ui()
        self.load_cache_info()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("<h3>Cache Information & Management</h3>")
        layout.addWidget(title_label)

        # Cache Statistics Group
        stats_group = QGroupBox("Cache Statistics")
        stats_layout = QFormLayout()

        self.pickle_files_label = QLabel("0")
        self.pickle_size_label = QLabel("0 MB")
        self.db_files_label = QLabel("0")
        self.db_size_label = QLabel("0 MB")

        stats_layout.addRow("Pickle Cache Files:", self.pickle_files_label)
        stats_layout.addRow("Pickle Cache Size:", self.pickle_size_label)
        stats_layout.addRow("Database Cache Files:", self.db_files_label)
        stats_layout.addRow("Database Cache Size:", self.db_size_label)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Version Information Group
        version_group = QGroupBox("Version Information")
        version_layout = QFormLayout()

        self.cache_version_label = QLabel(CACHE_VERSION)
        self.schema_version_label = QLabel(SCHEMA_VERSION)
        self.current_file_label = QLabel(self.data_model.file_path or "No file loaded")

        version_layout.addRow("Cache Version:", self.cache_version_label)
        version_layout.addRow("Schema Version:", self.schema_version_label)
        version_layout.addRow("Current File:", self.current_file_label)

        version_group.setLayout(version_layout)
        layout.addWidget(version_group)

        # Cache Directories Group
        dirs_group = QGroupBox("Cache Directories")
        dirs_layout = QFormLayout()

        cache_dir = self.data_model.cache_dir if hasattr(self.data_model, 'cache_dir') else Path("data/cache")
        db_dir = self.data_model.db_dir if hasattr(self.data_model, 'db_dir') else Path("data/db")

        self.cache_dir_label = QLabel(str(cache_dir))
        self.db_dir_label = QLabel(str(db_dir))

        dirs_layout.addRow("Pickle Cache:", self.cache_dir_label)
        dirs_layout.addRow("Database Cache:", self.db_dir_label)

        dirs_group.setLayout(dirs_layout)
        layout.addWidget(dirs_group)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Management Controls
        controls_group = QGroupBox("Cache Management")
        controls_layout = QVBoxLayout()

        # Action buttons
        button_layout = QHBoxLayout()

        self.clear_pickle_button = QPushButton("Clear Pickle Cache")
        self.clear_pickle_button.clicked.connect(self.clear_pickle_cache)
        button_layout.addWidget(self.clear_pickle_button)

        self.clear_db_button = QPushButton("Clear Database Cache")
        self.clear_db_button.clicked.connect(self.clear_db_cache)
        button_layout.addWidget(self.clear_db_button)

        self.clear_all_button = QPushButton("Clear All Caches")
        self.clear_all_button.clicked.connect(self.clear_all_caches)
        self.clear_all_button.setStyleSheet("QPushButton { color: red; }")
        button_layout.addWidget(self.clear_all_button)

        controls_layout.addLayout(button_layout)

        # Progress bar for operations
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)

        controls_group.setLayout(controls_layout)
        layout.addWidget(controls_group)

        # Details text area
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(150)
        self.details_text.setPlainText("Cache information loaded...")
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)

        # Dialog buttons
        button_layout = QHBoxLayout()

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.load_cache_info)
        button_layout.addWidget(self.refresh_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def load_cache_info(self):
        """Load and display cache information"""
        try:
            cache_info = self.data_model.get_cache_info()

            # Update statistics
            pickle_files = cache_info['pickle_cache']['files']
            pickle_size_mb = cache_info['pickle_cache']['size'] / (1024 * 1024)
            db_files = cache_info['db_cache']['files']
            db_size_mb = cache_info['db_cache']['size'] / (1024 * 1024)

            self.pickle_files_label.setText(str(pickle_files))
            self.pickle_size_label.setText(".1f")
            self.db_files_label.setText(str(db_files))
            self.db_size_label.setText(".1f")

            # Build details text
            details = []
            details.append("Cache Information")
            details.append("=" * 50)
            details.append(f"Pickle Cache: {pickle_files} files, {pickle_size_mb:.1f} MB")
            details.append(f"Database Cache: {db_files} files, {db_size_mb:.1f} MB")
            details.append("")
            details.append("Version Information:")
            details.append(f"  Cache Version: {CACHE_VERSION}")
            details.append(f"  Schema Version: {SCHEMA_VERSION}")
            details.append("")
            details.append("Current File:")
            details.append(f"  {self.data_model.file_path or 'No file loaded'}")

            # Add cache file details
            if pickle_files > 0:
                details.append("")
                details.append("Pickle Cache Files:")
                cache_dir = self.data_model.cache_dir
                for file in sorted(cache_dir.glob("GameData_*.pkl")):
                    size_mb = file.stat().st_size / (1024 * 1024)
                    details.append(f"  {file.name}: {size_mb:.1f} MB")

            if db_files > 0:
                details.append("")
                details.append("Database Cache Files:")
                db_dir = self.data_model.db_dir
                for file in sorted(db_dir.glob("*.db")):
                    size_mb = file.stat().st_size / (1024 * 1024)
                    details.append(f"  {file.name}: {size_mb:.1f} MB")

            self.details_text.setPlainText("\n".join(details))

        except Exception as e:
            self.details_text.setPlainText(f"Error loading cache info: {str(e)}")

    def clear_pickle_cache(self):
        """Clear the pickle cache"""
        try:
            reply = QMessageBox.question(
                self,
                "Clear Pickle Cache",
                "Are you sure you want to clear the pickle cache?\n\n"
                "This will force a full rebuild on next load.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate progress

                self.data_model.clear_pickle_cache()

                self.progress_bar.setVisible(False)
                self.load_cache_info()

                QMessageBox.information(
                    self,
                    "Success",
                    "Pickle cache cleared successfully."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear pickle cache: {str(e)}")
            self.progress_bar.setVisible(False)

    def clear_db_cache(self):
        """Clear the database cache"""
        try:
            reply = QMessageBox.question(
                self,
                "Clear Database Cache",
                "Are you sure you want to clear the database cache?\n\n"
                "This will force a full rebuild on next load.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate progress

                self.data_model.clear_db_cache()

                self.progress_bar.setVisible(False)
                self.load_cache_info()

                QMessageBox.information(
                    self,
                    "Success",
                    "Database cache cleared successfully."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear database cache: {str(e)}")
            self.progress_bar.setVisible(False)

    def clear_all_caches(self):
        """Clear all caches"""
        try:
            reply = QMessageBox.question(
                self,
                "Clear All Caches",
                "Are you sure you want to clear ALL caches?\n\n"
                "This will force a full rebuild of both pickle and database caches on next load.",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                self.progress_bar.setVisible(True)
                self.progress_bar.setRange(0, 0)  # Indeterminate progress

                self.data_model.clear_pickle_cache()
                self.data_model.clear_db_cache()

                self.progress_bar.setVisible(False)
                self.load_cache_info()

                QMessageBox.information(
                    self,
                    "Success",
                    "All caches cleared successfully."
                )

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to clear caches: {str(e)}")
            self.progress_bar.setVisible(False)