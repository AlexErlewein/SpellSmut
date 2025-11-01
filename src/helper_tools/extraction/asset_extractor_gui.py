#!/usr/bin/env python3
"""
SpellForce Asset Extractor GUI
Graphical interface for the asset extraction and comparison tool

Author: SpellSmut Modding Project
Date: October 31, 2025
"""

import sys
import os
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QTextEdit, QProgressBar, QLabel, QFileDialog,
    QMessageBox, QGroupBox, QCheckBox, QTabWidget, QListWidget,
    QListWidgetItem, QSplitter, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal, QObject
from PySide6.QtGui import QFont, QIcon


# Add project root to path so we can import our modules
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Import our asset extractor module
try:
    from src.helper_tools.extraction.asset_extractor import AssetExtractor
    ASSET_EXTRACTOR_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import asset extractor: {e}")
    ASSET_EXTRACTOR_AVAILABLE = False


class ExtractionWorker(QObject):
    """Worker thread for asset extraction operations"""
    finished = Signal(bool, str)  # success, message
    progress = Signal(str)  # progress message
    progress_update = Signal(int, int)  # current, total
    
    def __init__(self, extractor: AssetExtractor, operation: str, force: bool = False):
        super().__init__()
        self.extractor = extractor
        self.operation = operation
        self.force = force
        
    def run(self):
        """Run the extraction operation"""
        try:
            success = False
            message = ""
            
            if self.operation == "extract":
                self.progress.emit("Starting asset extraction...")
                success = self.extractor.extract_assets(force=self.force)
                message = "Asset extraction completed successfully" if success else "Asset extraction failed"
                
            elif self.operation == "create_reference":
                self.progress.emit("Creating reference snapshot...")
                success = self.extractor.create_reference_snapshot(force=self.force)
                message = "Reference snapshot created successfully" if success else "Failed to create reference snapshot"
                
            elif self.operation == "compare":
                self.progress.emit("Comparing with reference...")
                success = self.extractor.compare_with_reference()
                message = "Comparison completed successfully" if success else "Comparison failed"
                
            self.finished.emit(success, message)
            
        except Exception as e:
            import traceback
            error_details = f"Error during {self.operation}: {str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.finished.emit(False, error_details)


class AssetExtractorGUI(QMainWindow):
    """Main GUI window for asset extraction tool"""
    
    def __init__(self):
        super().__init__()
        self.extractor = AssetExtractor(project_root) if ASSET_EXTRACTOR_AVAILABLE else None
        self.worker_thread: Optional[QThread] = None
        self.worker: Optional[ExtractionWorker] = None
        
        self.init_ui()
        
        # Check if QuickBMS is available
        if self.extractor and not self.extractor.ensure_quickbms():
            QMessageBox.warning(
                self, 
                "QuickBMS Not Found", 
                "QuickBMS executable not found. Please run bulk_extract_paks.py first to install it."
            )
            
        # Check if PAK files directory exists
        if self.extractor:
            pak_dir = self.extractor.original_files_dir / "pak"
            if not pak_dir.exists():
                QMessageBox.warning(
                    self,
                    "PAK Directory Not Found",
                    f"PAK directory not found: {pak_dir}\n\n"
                    "Please create this directory and copy the PAK files from your SpellForce installation.\n"
                    "The PAK files are typically located in the 'pak' subdirectory of your SpellForce installation."
                )
    
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("SpellForce Asset Extractor")
        self.setGeometry(100, 100, 1000, 700)
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget for different sections
        tab_widget = QTabWidget()
        main_layout.addWidget(tab_widget)
        
        # Create tabs
        self.create_extraction_tab(tab_widget)
        self.create_reference_tab(tab_widget)
        self.create_comparison_tab(tab_widget)
        
        # Create status bar
        self.status_bar = QLabel("Ready")
        main_layout.addWidget(self.status_bar)
        
        # Create progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
    def create_extraction_tab(self, parent):
        """Create the asset extraction tab"""
        extraction_tab = QWidget()
        layout = QVBoxLayout(extraction_tab)
        
        # Extraction controls group
        extraction_group = QGroupBox("Asset Extraction")
        extraction_layout = QVBoxLayout(extraction_group)
        
        # Description
        desc_label = QLabel(
            "Extract all game assets from PAK files using QuickBMS. "
            "This will organize assets in the ExtractedAssets directory."
        )
        desc_label.setWordWrap(True)
        extraction_layout.addWidget(desc_label)
        
        # Force extraction checkbox
        self.force_extract_checkbox = QCheckBox("Force re-extraction (overwrite existing files)")
        extraction_layout.addWidget(self.force_extract_checkbox)
        
        # Extract button
        self.extract_button = QPushButton("Extract Assets")
        self.extract_button.clicked.connect(self.start_extraction)
        extraction_layout.addWidget(self.extract_button)
        
        layout.addWidget(extraction_group)
        
        # Log area
        log_group = QGroupBox("Extraction Log")
        log_layout = QVBoxLayout(log_group)
        
        self.extraction_log = QTextEdit()
        self.extraction_log.setReadOnly(True)
        font = QFont("Courier New")
        font.setPointSize(10)
        self.extraction_log.setFont(font)
        log_layout.addWidget(self.extraction_log)
        
        layout.addWidget(log_group)
        
        parent.addTab(extraction_tab, "Asset Extraction")
        
    def create_reference_tab(self, parent):
        """Create the reference management tab"""
        reference_tab = QWidget()
        layout = QVBoxLayout(reference_tab)
        
        # Reference controls group
        reference_group = QGroupBox("Reference Management")
        reference_layout = QVBoxLayout(reference_group)
        
        # Description
        desc_label = QLabel(
            "Create and manage reference snapshots of original game files. "
            "A reference snapshot is used as a baseline for comparison."
        )
        desc_label.setWordWrap(True)
        reference_layout.addWidget(desc_label)
        
        # Force reference creation checkbox
        self.force_reference_checkbox = QCheckBox("Force recreation of reference snapshot")
        reference_layout.addWidget(self.force_reference_checkbox)
        
        # Create reference button
        self.create_reference_button = QPushButton("Create Reference Snapshot")
        self.create_reference_button.clicked.connect(self.create_reference)
        reference_layout.addWidget(self.create_reference_button)
        
        layout.addWidget(reference_group)
        
        # Reference info group
        info_group = QGroupBox("Reference Information")
        info_layout = QVBoxLayout(info_group)
        
        self.reference_info = QTextEdit()
        self.reference_info.setReadOnly(True)
        self.update_reference_info()
        info_layout.addWidget(self.reference_info)
        
        layout.addWidget(info_group)
        
        parent.addTab(reference_tab, "Reference Management")
        
    def create_comparison_tab(self, parent):
        """Create the diff comparison tab"""
        comparison_tab = QWidget()
        layout = QVBoxLayout(comparison_tab)
        
        # Comparison controls group
        comparison_group = QGroupBox("Diff Comparison")
        comparison_layout = QVBoxLayout(comparison_group)
        
        # Description
        desc_label = QLabel(
            "Compare current extracted assets with the reference snapshot. "
            "This will show added, removed, and modified files."
        )
        desc_label.setWordWrap(True)
        comparison_layout.addWidget(desc_label)
        
        # Compare button
        self.compare_button = QPushButton("Compare with Reference")
        self.compare_button.clicked.connect(self.compare_with_reference)
        comparison_layout.addWidget(self.compare_button)
        
        layout.addWidget(comparison_group)
        
        # Results area
        results_group = QGroupBox("Comparison Results")
        results_layout = QVBoxLayout(results_group)
        
        # Splitter for results
        splitter = QSplitter(Qt.Horizontal)
        
        # Summary panel
        summary_frame = QFrame()
        summary_layout = QVBoxLayout(summary_frame)
        summary_label = QLabel("Summary:")
        summary_layout.addWidget(summary_label)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        splitter.addWidget(summary_frame)
        
        # Details panel
        details_frame = QFrame()
        details_layout = QVBoxLayout(details_frame)
        details_label = QLabel("Details:")
        details_layout.addWidget(details_label)
        self.details_list = QListWidget()
        details_layout.addWidget(self.details_list)
        splitter.addWidget(details_frame)
        
        # Set splitter sizes
        splitter.setSizes([300, 700])
        
        results_layout.addWidget(splitter)
        layout.addWidget(results_group)
        
        parent.addTab(comparison_tab, "Diff Comparison")
        
    def start_extraction(self):
        """Start the asset extraction process"""
        if not self.extractor:
            QMessageBox.critical(self, "Error", "Asset extractor not available")
            return
            
        self.disable_controls()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.setText("Extracting assets...")
        self.extraction_log.clear()
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = ExtractionWorker(
            self.extractor, 
            "extract", 
            self.force_extract_checkbox.isChecked()
        )
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.extraction_finished)
        self.worker.progress.connect(self.update_extraction_log)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()
        
    def create_reference(self):
        """Create a reference snapshot"""
        if not self.extractor:
            QMessageBox.critical(self, "Error", "Asset extractor not available")
            return
            
        self.disable_controls()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.setText("Creating reference snapshot...")
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = ExtractionWorker(
            self.extractor, 
            "create_reference", 
            self.force_reference_checkbox.isChecked()
        )
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.reference_finished)
        self.worker.progress.connect(self.update_status)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()
        
    def compare_with_reference(self):
        """Compare current assets with reference"""
        if not self.extractor:
            QMessageBox.critical(self, "Error", "Asset extractor not available")
            return
            
        self.disable_controls()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_bar.setText("Comparing with reference...")
        self.summary_text.clear()
        self.details_list.clear()
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = ExtractionWorker(self.extractor, "compare")
        
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.comparison_finished)
        self.worker.progress.connect(self.update_status)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        
        self.worker_thread.start()
        
    def update_extraction_log(self, message: str):
        """Update the extraction log with a new message"""
        self.extraction_log.append(message)
        self.extraction_log.verticalScrollBar().setValue(
            self.extraction_log.verticalScrollBar().maximum()
        )
        
    def update_status(self, message: str):
        """Update the status bar"""
        self.status_bar.setText(message)
        
    def extraction_finished(self, success: bool, message: str):
        """Handle completion of asset extraction"""
        self.enable_controls()
        self.progress_bar.setVisible(False)
        self.status_bar.setText(message)
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            # For detailed error messages, show in a scrollable text dialog
            if "\n" in message or len(message) > 200:
                error_dialog = QMessageBox(self)
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("Error Details")
                error_dialog.setText("Asset extraction failed. See details below:")
                error_dialog.setDetailedText(message)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec()
            else:
                QMessageBox.critical(self, "Error", message)
            
    def reference_finished(self, success: bool, message: str):
        """Handle completion of reference creation"""
        self.enable_controls()
        self.progress_bar.setVisible(False)
        self.status_bar.setText(message)
        self.update_reference_info()
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            # For detailed error messages, show in a scrollable text dialog
            if "\n" in message or len(message) > 200:
                error_dialog = QMessageBox(self)
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("Error Details")
                error_dialog.setText("Reference creation failed. See details below:")
                error_dialog.setDetailedText(message)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec_()
            else:
                QMessageBox.critical(self, "Error", message)
            
    def comparison_finished(self, success: bool, message: str):
        """Handle completion of comparison"""
        self.enable_controls()
        self.progress_bar.setVisible(False)
        self.status_bar.setText(message)
        
        # Clean up worker thread
        if self.worker_thread:
            self.worker_thread.quit()
            self.worker_thread.wait()
            
        if success:
            # Load the diff report if it exists
            self.load_diff_report()
            QMessageBox.information(self, "Success", message)
        else:
            # For detailed error messages, show in a scrollable text dialog
            if "\n" in message or len(message) > 200:
                error_dialog = QMessageBox(self)
                error_dialog.setIcon(QMessageBox.Critical)
                error_dialog.setWindowTitle("Error Details")
                error_dialog.setText("Comparison failed. See details below:")
                error_dialog.setDetailedText(message)
                error_dialog.setStandardButtons(QMessageBox.Ok)
                error_dialog.exec()
            else:
                QMessageBox.critical(self, "Error", message)
            
    def update_reference_info(self):
        """Update the reference information display"""
        reference_file = self.extractor.reference_dir / "reference_snapshot.json" if self.extractor else None
        
        if reference_file and reference_file.exists():
            try:
                import json
                with open(reference_file, 'r') as f:
                    snapshot = json.load(f)
                    
                info_text = f"""Reference Snapshot Information:
                
Timestamp: {snapshot.get('timestamp', 'Unknown')}
Game Version: {snapshot.get('game_version', 'Unknown')}
Total Assets: {len(snapshot.get('assets', {}))}
                
Location: {reference_file}"""
                
            except Exception as e:
                info_text = f"Error reading reference file: {str(e)}"
        else:
            info_text = "No reference snapshot found. Create one using the 'Create Reference Snapshot' button."
            
        self.reference_info.setPlainText(info_text)
        
    def load_diff_report(self):
        """Load and display the diff report"""
        report_file = self.extractor.extracted_assets_dir / "diff_report.md" if self.extractor else None
        
        if report_file and report_file.exists():
            try:
                with open(report_file, 'r') as f:
                    content = f.read()
                    
                # Parse the markdown report
                lines = content.split('\n')
                summary_lines = []
                detail_lines = []
                current_section = None
                
                for line in lines:
                    if line.startswith('## Summary'):
                        current_section = 'summary'
                    elif line.startswith('## Added Files') or line.startswith('## Removed Files') or line.startswith('## Modified Files'):
                        current_section = 'details'
                    elif line.startswith('##') and current_section:
                        current_section = None
                    elif line.strip() and current_section:
                        if current_section == 'summary':
                            summary_lines.append(line)
                        elif current_section == 'details':
                            detail_lines.append(line)
                            
                # Update summary
                self.summary_text.setPlainText('\n'.join(summary_lines))
                
                # Update details list
                self.details_list.clear()
                for line in detail_lines:
                    if line.startswith('- '):
                        item = QListWidgetItem(line[2:])  # Remove the "- " prefix
                        self.details_list.addItem(item)
                        
            except Exception as e:
                self.summary_text.setPlainText(f"Error loading diff report: {str(e)}")
        else:
            self.summary_text.setPlainText("No diff report found.")
            
    def disable_controls(self):
        """Disable all controls during operations"""
        self.extract_button.setEnabled(False)
        self.create_reference_button.setEnabled(False)
        self.compare_button.setEnabled(False)
        self.force_extract_checkbox.setEnabled(False)
        self.force_reference_checkbox.setEnabled(False)
        
    def enable_controls(self):
        """Enable all controls after operations complete"""
        self.extract_button.setEnabled(True)
        self.create_reference_button.setEnabled(True)
        self.compare_button.setEnabled(True)
        self.force_extract_checkbox.setEnabled(True)
        self.force_reference_checkbox.setEnabled(True)


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Set application information
    app.setApplicationName("SpellForce Asset Extractor")
    app.setApplicationVersion("1.0")
    
    # Create and show the main window
    window = AssetExtractorGUI()
    window.show()
    
    # Run the application
    sys.exit(app.exec())


if __name__ == "__main__":
    main()