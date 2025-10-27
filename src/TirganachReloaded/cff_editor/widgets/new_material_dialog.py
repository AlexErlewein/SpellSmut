from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QLineEdit,
    QSpinBox,
    QDoubleSpinBox,
    QPushButton,
    QGroupBox,
    QHBoxLayout,
    QColorDialog,
)

class NewMaterialDialog(QDialog):
    """Create a new weapon material"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Create New Material")
        
        layout = QFormLayout()
        
        # Material ID (auto-assigned from 10+)
        self.material_id_label = QLabel("Auto-assigned: 10")
        layout.addRow("Material ID:", self.material_id_label)
        
        # Material name
        self.material_name_edit = QLineEdit()
        self.material_name_edit.setPlaceholderText("e.g., Mithril, Adamantium, Dragonbone")
        layout.addRow("Material Name:", self.material_name_edit)
        
        # Material properties
        self.hardness_spin = QSpinBox()
        self.hardness_spin.setRange(1, 100)
        self.hardness_spin.setValue(50)
        layout.addRow("Hardness (1-100):", self.hardness_spin)
        
        self.weight_spin = QDoubleSpinBox()
        self.weight_spin.setRange(0.1, 10.0)
        self.weight_spin.setValue(1.0)
        self.weight_spin.setSuffix(" kg")
        layout.addRow("Weight:", self.weight_spin)
        
        self.durability_spin = QSpinBox()
        self.durability_spin.setRange(10, 1000)
        self.durability_spin.setValue(100)
        layout.addRow("Durability:", self.durability_spin)
        
        # Visual properties
        self.color_btn = QPushButton("Choose Color")
        self.color_btn.clicked.connect(self.choose_color)
        layout.addRow("Material Color:", self.color_btn)
        
        self.texture_edit = QLineEdit()
        self.texture_edit.setPlaceholderText("Optional texture file")
        layout.addRow("Texture File:", self.texture_edit)
        
        # Stat modifiers
        mod_group = QGroupBox("Stat Modifiers")
        mod_layout = QFormLayout()
        
        self.damage_mod_spin = QSpinBox()
        self.damage_mod_spin.setRange(-50, 50)
        self.damage_mod_spin.setSuffix("%")
        mod_layout.addRow("Damage Modifier:", self.damage_mod_spin)
        
        self.speed_mod_spin = QSpinBox()
        self.speed_mod_spin.setRange(-50, 50)
        self.speed_mod_spin.setSuffix("%")
        mod_layout.addRow("Speed Modifier:", self.speed_mod_spin)
        
        self.value_mod_spin = QSpinBox()
        self.value_mod_spin.setRange(-50, 200)
        self.value_mod_spin.setSuffix("%")
        mod_layout.addRow("Value Modifier:", self.value_mod_spin)
        
        mod_group.setLayout(mod_layout)
        layout.addRow(mod_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        create_btn = QPushButton("Create Material")
        create_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(create_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addRow(btn_layout)
        self.setLayout(layout)
    
    def choose_color(self):
        """Choose material color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.color_btn.setStyleSheet(f"background-color: {color.name()};")
