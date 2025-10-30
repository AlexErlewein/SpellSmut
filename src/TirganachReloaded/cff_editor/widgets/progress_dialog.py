"""
Progress Dialog for Background Operations
Provides non-blocking progress UI for cache/DB operations
"""

import time
from typing import Callable, Any, Optional

from PySide6.QtCore import QThread, Signal, QTimer
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QFrame,
    QSizePolicy,
)


class WorkerThread(QThread):
    """Background worker thread for operations"""

    # Signals
    progress_updated = Signal(int, str)  # progress_percent, status_message
    operation_completed = Signal(object)  # result
    operation_failed = Signal(str)  # error_message
    step_started = Signal(str)  # step_description

    def __init__(self, operation_func: Callable, *args, **kwargs):
        super().__init__()
        self.operation_func = operation_func
        self.args = args
        self.kwargs = kwargs

    def run(self):
        """Execute the operation in background thread"""
        try:
            # Create a progress callback function
            def progress_callback(progress_percent: int, status_message: str = ""):
                self.progress_updated.emit(progress_percent, status_message)

            def step_callback(step_description: str):
                self.step_started.emit(step_description)

            # Add callbacks to kwargs if not already present
            self.kwargs.setdefault('progress_callback', progress_callback)
            self.kwargs.setdefault('step_callback', step_callback)

            # Execute the operation
            result = self.operation_func(*self.args, **self.kwargs)
            self.operation_completed.emit(result)

        except Exception as e:
            self.operation_failed.emit(str(e))


class ProgressDialog(QDialog):
    """Modal progress dialog for background operations"""

    def __init__(self, title: str, description: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setMinimumSize(500, 300)

        # Store operation details
        self.operation_title = title
        self.operation_description = description
        self.worker_thread: Optional[WorkerThread] = None
        self.start_time = time.time()

        self.setup_ui()
        self.setup_connections()

    def setup_ui(self):
        """Setup the dialog UI"""
        layout = QVBoxLayout(self)

        # Title and description
        title_label = QLabel(f"<h3>{self.operation_title}</h3>")
        layout.addWidget(title_label)

        description_label = QLabel(self.operation_description)
        description_label.setWordWrap(True)
        layout.addWidget(description_label)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        # Current operation status
        self.status_label = QLabel("Initializing...")
        layout.addWidget(self.status_label)

        # Step information
        self.step_label = QLabel("")
        self.step_label.setStyleSheet("font-weight: bold; color: #0d47a1;")
        layout.addWidget(self.step_label)

        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(separator)

        # Details text area (collapsible)
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setPlainText("Operation started...")
        self.details_text.setReadOnly(True)
        layout.addWidget(self.details_text)

        # ETA and elapsed time
        time_layout = QHBoxLayout()

        self.elapsed_label = QLabel("Elapsed: 0:00")
        time_layout.addWidget(self.elapsed_label)

        self.eta_label = QLabel("ETA: calculating...")
        time_layout.addWidget(self.eta_label)

        time_layout.addStretch()
        layout.addLayout(time_layout)

        # Buttons
        button_layout = QHBoxLayout()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.cancel_operation)
        button_layout.addWidget(self.cancel_button)

        button_layout.addStretch()

        self.close_button = QPushButton("Close")
        self.close_button.setEnabled(False)
        self.close_button.clicked.connect(self.accept)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

        # Timer for updating elapsed time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.timer.start(1000)  # Update every second

    def setup_connections(self):
        """Setup signal connections"""
        pass  # Will be connected when operation starts

    def start_operation(self, operation_func: Callable, *args, **kwargs):
        """Start the background operation"""
        self.worker_thread = WorkerThread(operation_func, *args, **kwargs)

        # Connect signals
        self.worker_thread.progress_updated.connect(self.on_progress_updated)
        self.worker_thread.step_started.connect(self.on_step_started)
        self.worker_thread.operation_completed.connect(self.on_operation_completed)
        self.worker_thread.operation_failed.connect(self.on_operation_failed)

        # Start the operation
        self.worker_thread.start()

        # Show the dialog
        self.exec()

    def cancel_operation(self):
        """Cancel the current operation"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.terminate()
            self.worker_thread.wait()
            self.status_label.setText("Operation cancelled")
            self.cancel_button.setEnabled(False)
            self.close_button.setEnabled(True)

    def on_progress_updated(self, progress_percent: int, status_message: str):
        """Handle progress updates"""
        self.progress_bar.setValue(progress_percent)
        if status_message:
            self.status_label.setText(status_message)

        # Update ETA calculation
        elapsed = time.time() - self.start_time
        if progress_percent > 0 and elapsed > 1:
            total_estimated = elapsed / (progress_percent / 100.0)
            remaining = total_estimated - elapsed
            if remaining > 0:
                minutes, seconds = divmod(int(remaining), 60)
                self.eta_label.setText(f"ETA: {minutes}:{seconds:02d}")
            else:
                self.eta_label.setText("ETA: finishing...")
        else:
            self.eta_label.setText("ETA: calculating...")

    def on_step_started(self, step_description: str):
        """Handle step changes"""
        self.step_label.setText(f"Step: {step_description}")
        self.details_text.append(f"• {step_description}")

    def on_operation_completed(self, result):
        """Handle operation completion"""
        self.progress_bar.setValue(100)
        self.status_label.setText("Operation completed successfully")
        self.step_label.setText("")
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)

        elapsed = time.time() - self.start_time
        minutes, seconds = divmod(int(elapsed), 60)
        self.elapsed_label.setText(f"Elapsed: {minutes}:{seconds:02d}")

        self.details_text.append("✓ Operation completed successfully")

    def on_operation_failed(self, error_message: str):
        """Handle operation failure"""
        self.status_label.setText("Operation failed")
        self.step_label.setText("")
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)

        self.details_text.append(f"✗ Operation failed: {error_message}")

    def update_elapsed_time(self):
        """Update the elapsed time display"""
        if hasattr(self, 'start_time'):
            elapsed = time.time() - self.start_time
            minutes, seconds = divmod(int(elapsed), 60)
            self.elapsed_label.setText(f"Elapsed: {minutes}:{seconds:02d}")

    def closeEvent(self, event):
        """Handle dialog close event"""
        if self.worker_thread and self.worker_thread.isRunning():
            self.cancel_operation()
        event.accept()