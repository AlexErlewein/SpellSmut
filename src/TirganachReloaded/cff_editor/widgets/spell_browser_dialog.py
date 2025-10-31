import json
from pathlib import Path
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
    QMessageBox,
    QTabWidget
)
from PySide6.QtCore import Qt

class SpellBrowserDialog(QDialog):
    """Browse and select existing spells"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Spell to Copy")
        self.setModal(True)
        self.resize(900, 700)
        
        self.selected_spell = None
        
        # Load spells with error handling
        try:
            self.spells = self.load_all_spells()
            if not self.spells:
                raise ValueError("No spells loaded - spell files may be empty or corrupted")
        except Exception as e:
            QMessageBox.critical(
                self,
                "Loading Error",
                f"Failed to load spells:\n{str(e)}\n\nPlease check the spell files."
            )
            self.spells = []
        
        layout = QVBoxLayout()
        
        # Add status label
        self.status_label = QLabel(f"Loaded {len(self.spells)} spells")
        layout.addWidget(self.status_label)
        
        # Create tabs for different spell sources
        self.tab_widget = QTabWidget()
        
        # Template spells tab
        self.template_table = self.create_spell_table()
        self.tab_widget.addTab(self.template_table, "Template Spells")
        
        # Game spells tab  
        self.game_table = self.create_spell_table()
        self.tab_widget.addTab(self.game_table, "Original Game Spells")
        
        layout.addWidget(self.tab_widget)
        
        # Search/Filter
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_spells)
        search_layout.addWidget(self.search_edit)
        
        self.school_filter = QComboBox()
        self.school_filter.addItem("All Schools")
        self.school_filter.addItems([
            "White Magic", "Fire Magic", "Ice Magic", "Black Magic", 
            "Mental Magic", "Elemental Magic"
        ])
        self.school_filter.currentTextChanged.connect(self.filter_spells)
        search_layout.addWidget(self.school_filter)
        
        self.type_filter = QComboBox()
        self.type_filter.addItem("All Types")
        self.type_filter.addItems([
            "Attack", "Heal", "Buff", "Debuff", "Summon", "Aura", "Area"
        ])
        self.type_filter.currentTextChanged.connect(self.filter_spells)
        search_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_layout)
        
        # Populate tables
        if self.spells:
            self.populate_tables()
        else:
            self.template_table.setRowCount(1)
            self.template_table.setItem(0, 0, QTableWidgetItem("No spells available"))
            self.template_table.setSpan(0, 0, 1, 8)
        
        # Buttons
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Copy Spell")
        self.ok_btn.clicked.connect(self.accept)
        self.ok_btn.setEnabled(bool(self.spells))
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Connect table selection
        self.template_table.itemSelectionChanged.connect(self.on_selection_changed)
        self.game_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def create_spell_table(self):
        """Create a standardized spell table"""
        table = QTableWidget(0, 8)
        table.setHorizontalHeaderLabels([
            "ID", "Name", "School", "Type", "Level", "Damage/Heal", "Mana Cost", "Range"
        ])
        table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        table.doubleClicked.connect(self.accept)
        
        # Set column widths
        header = table.horizontalHeader()
        header.setStretchLastSection(True)
        header.resizeSection(0, 50)  # ID
        header.resizeSection(1, 150)  # Name
        header.resizeSection(2, 100)  # School
        header.resizeSection(3, 80)   # Type
        header.resizeSection(4, 60)   # Level
        header.resizeSection(5, 100)  # Damage/Heal
        header.resizeSection(6, 80)   # Mana Cost
        header.resizeSection(7, 80)   # Range
        
        return table
    
    def load_all_spells(self) -> List[Dict]:
        """Load spells from both templates and game files"""
        all_spells = []
        
        # Load template spells
        template_spells = self.load_template_spells()
        all_spells.extend(template_spells)
        
        # Load game spells
        game_spells = self.load_game_spells()
        all_spells.extend(game_spells)
        
        return all_spells
    
    def load_template_spells(self) -> List[Dict]:
        """Load spells from template JSON files"""
        spells = []
        templates_dir = Path(__file__).parent.parent / "templates"
        
        template_files = [
            "fireball_spell.json",
            "healing_spell.json", 
            "ice_blast_spell.json"
        ]
        
        for filename in template_files:
            filepath = templates_dir / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        spell_data = json.load(f)
                    
                    # Extract basic info from level 1 (or first available level)
                    levels = spell_data.get('levels', {})
                    if levels:
                        first_level_key = sorted(levels.keys())[0]
                        first_level = levels[first_level_key]
                        
                        spell_info = {
                            'source': 'template',
                            'file_path': str(filepath),
                            'id': spell_data.get('id', 0),
                            'name': spell_data.get('name', 'Unknown'),
                            'school': spell_data.get('school', 'Unknown'),
                            'type': spell_data.get('type', 'Unknown'),
                            'level': first_level_key,
                            'damage': first_level.get('damage', first_level.get('healing', 0)),
                            'mana_cost': first_level.get('mana_cost', 0),
                            'range': first_level.get('range', 0),
                            'full_data': spell_data
                        }
                        spells.append(spell_info)
                        
                except Exception as e:
                    print(f"Error loading template {filename}: {e}")
        
        return spells
    
    def load_game_spells(self) -> List[Dict]:
        """Load spells from original game script"""
        spells = []
        script_path = Path(__file__).parent.parent.parent.parent.parent / "OriginalGameFiles" / "modding" / "Original Scripts" / "script" / "sql_spellline.lua"
        
        if script_path.exists():
            try:
                with open(script_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse spell entries from the Lua script
                # Look for lines like: {300, 'FireBall', 0x00000008},
                import re
                pattern = r'\{(\d+),\s*\'([^\']+)\',\s*([^}]+)\}'
                matches = re.findall(pattern, content)
                
                school_map = {
                    0: "White Magic",
                    1: "Fire Magic", 
                    2: "Ice Magic",
                    3: "Black Magic",
                    4: "Mental Magic",
                    5: "Elemental Magic"
                }
                
                for match in matches:
                    spell_id, name, flags = match
                    try:
                        flag_int = int(flags.strip(), 0) if flags.strip().startswith('0x') else int(flags.strip())
                        school_id = (flag_int >> 3) & 0x7  # Extract school from flags
                        
                        spell_info = {
                            'source': 'game',
                            'file_path': str(script_path),
                            'id': int(spell_id),
                            'name': name,
                            'school': school_map.get(school_id, "Unknown"),
                            'type': self.guess_spell_type(name),
                            'level': "1",
                            'damage': 0,
                            'mana_cost': 0,
                            'range': 0,
                            'full_data': {'id': int(spell_id), 'name': name, 'flags': flag_int}
                        }
                        spells.append(spell_info)
                    except:
                        continue
                        
            except Exception as e:
                print(f"Error loading game spells: {e}")
        
        return spells
    
    def guess_spell_type(self, name: str) -> str:
        """Guess spell type based on name"""
        name_lower = name.lower()
        if any(word in name_lower for word in ['heal', 'cure', 'regenerate']):
            return "Heal"
        elif any(word in name_lower for word in ['summon']):
            return "Summon"
        elif any(word in name_lower for word in ['aura', 'field']):
            return "Aura"
        elif any(word in name_lower for word in ['rain', 'blizzard', 'storm']):
            return "Area"
        elif any(word in name_lower for word in ['slow', 'weak', 'pain', 'curse']):
            return "Debuff"
        elif any(word in name_lower for word in ['speed', 'strength', 'guard', 'bless']):
            return "Buff"
        else:
            return "Attack"
    
    def populate_tables(self):
        """Populate both template and game tables"""
        template_spells = [s for s in self.spells if s['source'] == 'template']
        game_spells = [s for s in self.spells if s['source'] == 'game']
        
        self.populate_table(self.template_table, template_spells)
        self.populate_table(self.game_table, game_spells)
    
    def populate_table(self, table: QTableWidget, spells: List[Dict]):
        """Populate a table with spell data"""
        table.setRowCount(len(spells))
        
        for row, spell in enumerate(spells):
            table.setItem(row, 0, QTableWidgetItem(str(spell['id'])))
            table.setItem(row, 1, QTableWidgetItem(spell['name']))
            table.setItem(row, 2, QTableWidgetItem(spell['school']))
            table.setItem(row, 3, QTableWidgetItem(spell['type']))
            table.setItem(row, 4, QTableWidgetItem(spell['level']))
            table.setItem(row, 5, QTableWidgetItem(str(spell['damage'])))
            table.setItem(row, 6, QTableWidgetItem(str(spell['mana_cost'])))
            table.setItem(row, 7, QTableWidgetItem(str(spell['range'])))
            
            # Store full spell data as item data
            table.item(row, 0).setData(Qt.UserRole, spell)
    
    def filter_spells(self):
        """Filter spells based on search and filters"""
        search_text = self.search_edit.text().lower()
        school_filter = self.school_filter.currentText()
        type_filter = self.type_filter.currentText()
        
        current_table = self.tab_widget.currentWidget()
        
        for row in range(current_table.rowCount()):
            item = current_table.item(row, 0)
            if not item:
                continue
                
            spell = item.data(Qt.UserRole)
            if not spell:
                continue
            
            # Check filters
            name_match = search_text in spell['name'].lower()
            school_match = school_filter == "All Schools" or spell['school'] == school_filter
            type_match = type_filter == "All Types" or spell['type'] == type_filter
            
            show_row = name_match and school_match and type_match
            current_table.setRowHidden(row, not show_row)
    
    def on_selection_changed(self):
        """Handle selection change in tables"""
        current_table = self.tab_widget.currentWidget()
        selected_items = current_table.selectedItems()
        self.ok_btn.setEnabled(bool(selected_items))
    
    def get_selected_spell(self) -> Optional[Dict]:
        """Get the selected spell data"""
        current_table = self.tab_widget.currentWidget()
        selected_items = current_table.selectedItems()
        
        if selected_items:
            item = current_table.item(selected_items[0].row(), 0)
            return item.data(Qt.UserRole)
        
        return None