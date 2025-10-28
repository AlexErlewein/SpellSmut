import json
from typing import List, Dict, Optional
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
)

class WeaponBrowserDialog(QDialog):
    """Browse and select existing weapons"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Weapon to Edit")
        self.setModal(True)
        self.resize(800, 600)
        
        self.selected_weapon = None
        self.weapons = self.load_weapons()
        
        layout = QVBoxLayout()
        
        # Search/Filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_weapons)
        search_layout.addWidget(self.search_edit)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems([
            "Daggers", "Swords", "Axes", "Maces", "Hammers",
            "Staves", "Spears", "Halberds", "Bows", "Crossbows"
        ])
        self.type_filter.currentTextChanged.connect(self.filter_weapons)
        search_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_layout)
        
        # Weapon table
        self.weapon_table = QTableWidget(0, 7)
        self.weapon_table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Material", "Damage", "Speed", "Rarity"
        ])
        self.weapon_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.weapon_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.weapon_table.doubleClicked.connect(self.accept)
        self.populate_table()
        layout.addWidget(self.weapon_table)
        
        # Buttons
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("Load Weapon")
        ok_btn.clicked.connect(self.accept)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def load_weapons(self) -> List[Dict]:
        """Load weapons from enhanced_weapons.json"""
        with open("src/TirganachReloaded/enhanced_weapons.json", 'r') as f:
            return json.load(f)
    
    def populate_table(self, weapons=None):
        """Populate weapon table"""
        if weapons is None:
            weapons = self.weapons
        
        self.weapon_table.setRowCount(len(weapons))
        
        for row, weapon in enumerate(weapons):
            self.weapon_table.setItem(row, 0, QTableWidgetItem(str(weapon['item_id'])))
            self.weapon_table.setItem(row, 1, QTableWidgetItem(weapon['name']))
            self.weapon_table.setItem(row, 2, QTableWidgetItem(weapon.get('weapon_type_name', 'Unknown')))
            self.weapon_table.setItem(row, 3, QTableWidgetItem(weapon.get('weapon_material_name', 'Unknown')))
            
            damage_str = f"{weapon.get('min_damage', 0)}-{weapon.get('max_damage', 0)}"
            self.weapon_table.setItem(row, 4, QTableWidgetItem(damage_str))
            self.weapon_table.setItem(row, 5, QTableWidgetItem(str(weapon.get('weapon_speed', 0))))
            self.weapon_table.setItem(row, 6, QTableWidgetItem(weapon.get('rarity', 'Common')))
        
        self.weapon_table.resizeColumnsToContents()
    
    def filter_weapons(self):
        """Filter weapons by search text and type"""
        search_text = self.search_edit.text().lower()
        type_filter = self.type_filter.currentText()
        
        filtered = []
        for weapon in self.weapons:
            # Text search
            if search_text and search_text not in weapon['name'].lower():
                continue
            
            # Type filter
            if type_filter != "All Types":
                weapon_type = weapon.get('weapon_type_name', '')
                if type_filter.lower() not in weapon_type.lower():
                    continue
            
            filtered.append(weapon)
        
        self.populate_table(filtered)
    
    def get_selected_weapon(self) -> Optional[Dict]:
        """Get selected weapon data"""
        selected_rows = self.weapon_table.selectedIndexes()
        if not selected_rows:
            return None
        
        row = selected_rows[0].row()
        id_item = self.weapon_table.item(row, 0)
        if id_item is None:
            return None
        weapon_id = int(id_item.text())
        
        for weapon in self.weapons:
            if weapon['item_id'] == weapon_id:
                return weapon
        
        return None
