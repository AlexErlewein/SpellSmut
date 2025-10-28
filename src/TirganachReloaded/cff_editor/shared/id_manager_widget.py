from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLabel,
    QGroupBox,
    QTableWidget,
    QTableWidgetItem,
    QFormLayout,
    QComboBox,
    QRadioButton,
    QSpinBox,
    QPushButton,
)

from .id_manager import IDManager, ContentType

class IDManagerWidget(QWidget):
    """Visual ID manager interface"""
    
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("ID Management System")
        title.setStyleSheet("font-size: 16pt; font-weight: bold;")
        layout.addWidget(title)
        
        # Stats table
        stats_group = QGroupBox("ID Usage Statistics")
        stats_layout = QVBoxLayout()
        
        self.stats_table = QTableWidget(8, 5)
        self.stats_table.setHorizontalHeaderLabels([
            "Content Type", "Range", "Used", "Available", "Usage %"
        ])
        self.update_stats_table()
        
        stats_layout.addWidget(self.stats_table)
        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)
        
        # ID allocation section
        alloc_group = QGroupBox("Allocate New ID")
        alloc_layout = QFormLayout()
        
        self.content_type_combo = QComboBox()
        self.content_type_combo.addItems([ct.value.title() for ct in ContentType])
        alloc_layout.addRow("Content Type:", self.content_type_combo)
        
        self.auto_id_radio = QRadioButton("Auto-assign next available ID")
        self.manual_id_radio = QRadioButton("Manually specify ID")
        self.auto_id_radio.setChecked(True)
        alloc_layout.addRow(self.auto_id_radio)
        alloc_layout.addRow(self.manual_id_radio)
        
        self.manual_id_spin = QSpinBox()
        self.manual_id_spin.setRange(0, 99999)
        self.manual_id_spin.setEnabled(False)
        self.manual_id_radio.toggled.connect(lambda checked: self.manual_id_spin.setEnabled(checked))
        alloc_layout.addRow("Specific ID:", self.manual_id_spin)
        
        allocate_btn = QPushButton("Allocate ID")
        allocate_btn.clicked.connect(self.allocate_id)
        alloc_layout.addRow(allocate_btn)
        
        self.allocated_id_label = QLabel("")
        self.allocated_id_label.setStyleSheet("color: green; font-weight: bold;")
        alloc_layout.addRow("Allocated:", self.allocated_id_label)
        
        alloc_group.setLayout(alloc_layout)
        layout.addWidget(alloc_group)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh Statistics")
        refresh_btn.clicked.connect(self.update_stats_table)
        layout.addWidget(refresh_btn)
        
        self.setLayout(layout)
    
    def update_stats_table(self):
        """Update statistics table"""
        stats = self.id_manager.get_stats()
        
        row = 0
        for content_type_str, stat_data in stats.items():
            self.stats_table.setItem(row, 0, QTableWidgetItem(content_type_str.title()))
            self.stats_table.setItem(row, 1, QTableWidgetItem(
                f"{stat_data['range_start']}-{stat_data['range_end']}"
            ))
            self.stats_table.setItem(row, 2, QTableWidgetItem(str(stat_data['used'])))
            self.stats_table.setItem(row, 3, QTableWidgetItem(str(stat_data['available'])))
            self.stats_table.setItem(row, 4, QTableWidgetItem(f"{stat_data['usage_percent']}%"))
            row += 1
        
        self.stats_table.resizeColumnsToContents()
    
    def allocate_id(self):
        """Allocate a new ID"""
        content_type_str = self.content_type_combo.currentText().lower()
        content_type = ContentType(content_type_str)
        
        try:
            if self.auto_id_radio.isChecked():
                # Auto-assign
                new_id = self.id_manager.allocate_id(content_type)
            else:
                # Manual ID
                requested_id = self.manual_id_spin.value()
                new_id = self.id_manager.allocate_id(content_type, requested_id)
            
            self.allocated_id_label.setText(f"✓ ID {new_id} allocated successfully!")
            self.allocated_id_label.setStyleSheet("color: green; font-weight: bold;")
            self.update_stats_table()
            
        except ValueError as e:
            self.allocated_id_label.setText(f"✗ Error: {str(e)}")
            self.allocated_id_label.setStyleSheet("color: red; font-weight: bold;")
