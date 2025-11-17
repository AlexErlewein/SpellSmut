#!/usr/bin/env python3
"""
Reward Builder with Item Browser (PySide6 Compatible)

Visual reward configuration with:
- CFF item database integration
- Item search and filtering
- Balance checking and validation
- Visual reward preview
- Gold/silver/copper calculator

This component integrates with enhanced quest creation wizard and uses only PySide6.
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QSpinBox, QComboBox, QPushButton,
    QLabel, QGroupBox, QListWidget, QListWidgetItem, QMessageBox,
    QCheckBox, QRadioButton, QButtonGroup, QTabWidget, QTableWidget,
    QTableWidgetItem, QHeaderView, QProgressBar, QSplitter
)
from PySide6.QtCore import Qt, Signal, QThread, Slot, QObject
from PySide6.QtGui import QIntValidator, QFont, QPixmap

from TirganachReloaded.cff_editor.models.quest_models import QuestReward


# Simple logger fallback
def get_logger(name):
    import logging
    return logging.getLogger(name)


@dataclass
class RewardBalance:
    """Balance information for rewards"""
    xp_value: int = 0
    gold_value: int = 0
    item_value: int = 0
    total_value: int = 0
    recommended_level: int = 1
    is_balanced: bool = True
    warnings: List[str] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


class ItemBrowserWorker(QObject):
    """Worker for loading items from CFF database"""
    
    items_loaded = Signal(list)
    finished = Signal()
    
    def __init__(self, data_model):
        super().__init__()
        self.data_model = data_model
        self.logger = get_logger("item_browser")
    
    def load_items(self):
        """Load items from CFF database"""
        try:
            items = []
            
            # Load weapons
            weapons = self.data_model.get_elements("weapons") or []
            for weapon in weapons:
                items.append({
                    'id': getattr(weapon, 'item_id', 0),
                    'name': self.data_model.get_localised_text(weapon, 'name') or getattr(weapon, 'name', 'Unknown Weapon'),
                    'type': 'Weapon',
                    'value': getattr(weapon, 'value', 0),
                    'level': getattr(weapon, 'level_requirement', 1),
                    'damage': getattr(weapon, 'damage_min', 0),
                    'icon': self._get_item_icon(weapon)
                })
            
            # Load armor
            armor = self.data_model.get_elements("armor") or []
            for armor_item in armor:
                items.append({
                    'id': getattr(armor_item, 'item_id', 0),
                    'name': self.data_model.get_localised_text(armor_item, 'name') or getattr(armor_item, 'name', 'Unknown Armor'),
                    'type': 'Armor',
                    'value': getattr(armor_item, 'value', 0),
                    'level': getattr(armor_item, 'level_requirement', 1),
                    'defense': getattr(armor_item, 'armor_class', 0),
                    'icon': self._get_item_icon(armor_item)
                })
            
            # Load general items
            general_items = self.data_model.get_elements("items") or []
            for item in general_items:
                items.append({
                    'id': getattr(item, 'item_id', 0),
                    'name': self.data_model.get_localised_text(item, 'name') or getattr(item, 'name', 'Unknown Item'),
                    'type': 'Item',
                    'value': getattr(item, 'value', 0),
                    'level': getattr(item, 'level_requirement', 1),
                    'icon': self._get_item_icon(item)
                })
            
            self.items_loaded.emit(items)
            
        except Exception as e:
            self.logger.error(f"Failed to load items: {e}")
        finally:
            self.finished.emit()
    
    def _get_item_icon(self, item):
        """Get item icon from CFF data"""
        try:
            # This would load actual icons from CFF
            # For now, return None
            return None
        except:
            return None


class RewardBuilderWidget(QWidget):
    """Main reward builder widget"""
    
    # Signals using PySide6 Signal
    rewards_changed = Signal(dict)
    
    def __init__(self, data_model, parent=None):
        super().__init__(parent)
        self.data_model = data_model
        self.logger = get_logger("reward_builder")
        
        # Data storage
        self.items = []  # All items from CFF
        self.selected_items = []  # Currently selected reward items
        self.current_rewards = {
            'xp': 0,
            'gold': 0,
            'silver': 0,
            'copper': 0,
            'items_given': [],  # Items player receives
            'items_taken': []   # Items removed from player (quest items)
        }
        
        # Balance data
        self.balance_data = RewardBalance()
        
        self._setup_ui()
        self._setup_connections()
        self._load_items()
    
    def _setup_ui(self):
        """Setup UI"""
        layout = QVBoxLayout(self)
        
        # Header with quick settings
        header_group = self._create_header_group()
        layout.addWidget(header_group)
        
        # Main content with splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Item browser
        item_browser = self._create_item_browser()
        splitter.addWidget(item_browser)
        
        # Right side - Reward configuration
        reward_config = self._create_reward_config()
        splitter.addWidget(reward_config)
        
        splitter.setSizes([400, 400])
        layout.addWidget(splitter)
        
        # Bottom - Balance checking
        balance_group = self._create_balance_group()
        layout.addWidget(balance_group)
    
    def _create_header_group(self) -> QGroupBox:
        """Create header group with quick settings"""
        group = QGroupBox("Quick Settings")
        layout = QHBoxLayout(group)
        
        # Quest level estimate
        layout.addWidget(QLabel("Quest Level:"))
        self.quest_level_spin = QSpinBox()
        self.quest_level_spin.setRange(1, 50)
        self.quest_level_spin.setValue(1)
        self.quest_level_spin.valueChanged.connect(self._update_balance)
        layout.addWidget(self.quest_level_spin)
        
        layout.addStretch()
        
        # Quick reward templates
        layout.addWidget(QLabel("Template:"))
        self.template_combo = QComboBox()
        self.template_combo.addItems(["Custom", "Starter Quest", "Medium Quest", "Main Quest", "Epic Quest"])
        self.template_combo.currentTextChanged.connect(self._apply_template)
        layout.addWidget(self.template_combo)
        
        return group
    
    def _create_item_browser(self) -> QWidget:
        """Create item browser widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Search and filter
        search_layout = QHBoxLayout()
        
        self.item_search = QLineEdit()
        self.item_search.setPlaceholderText("Search items...")
        self.item_search.textChanged.connect(self._filter_items)
        search_layout.addWidget(self.item_search)
        
        self.item_type_filter = QComboBox()
        self.item_type_filter.addItems(["All Types", "Weapon", "Armor", "Item"])
        self.item_type_filter.currentTextChanged.connect(self._filter_items)
        search_layout.addWidget(self.item_type_filter)
        
        layout.addLayout(search_layout)
        
        # Item table
        self.item_table = QTableWidget()
        self.item_table.setColumnCount(6)
        self.item_table.setHorizontalHeaderLabels(["Name", "Type", "Level", "Value", "Damage/Defense", "Actions"])
        
        # Configure columns
        header = self.item_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.item_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.item_table.setSortingEnabled(True)
        layout.addWidget(self.item_table)
        
        # Add/remove buttons
        button_layout = QHBoxLayout()
        
        add_item_btn = QPushButton("Add Item to Rewards")
        add_item_btn.clicked.connect(self._add_selected_item)
        button_layout.addWidget(add_item_btn)
        
        remove_item_btn = QPushButton("Remove Selected Reward")
        remove_item_btn.clicked.connect(self._remove_selected_reward)
        button_layout.addWidget(remove_item_btn)
        
        layout.addLayout(button_layout)
        
        return widget
    
    def _create_reward_config(self) -> QWidget:
        """Create reward configuration widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Basic rewards
        basic_group = QGroupBox("Basic Rewards")
        basic_layout = QFormLayout(basic_group)
        
        # XP
        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 999999)
        self.xp_spin.valueChanged.connect(self._on_rewards_changed)
        basic_layout.addRow("Experience Points:", self.xp_spin)
        
        # Money
        money_layout = QHBoxLayout()
        
        money_layout.addWidget(QLabel("Gold:"))
        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(0, 999999)
        self.gold_spin.valueChanged.connect(self._on_rewards_changed)
        money_layout.addWidget(self.gold_spin)
        
        money_layout.addWidget(QLabel("Silver:"))
        self.silver_spin = QSpinBox()
        self.silver_spin.setRange(0, 99)
        self.silver_spin.valueChanged.connect(self._on_rewards_changed)
        money_layout.addWidget(self.silver_spin)
        
        money_layout.addWidget(QLabel("Copper:"))
        self.copper_spin = QSpinBox()
        self.copper_spin.setRange(0, 99)
        self.copper_spin.valueChanged.connect(self._on_rewards_changed)
        money_layout.addWidget(self.copper_spin)
        
        money_layout.addStretch()
        basic_layout.addRow("Money:", money_layout)
        
        layout.addWidget(basic_group)
        
        # Items tabs (given vs taken)
        items_tabs = QTabWidget()
        
        # Items GIVEN tab
        items_given_widget = QWidget()
        items_given_layout = QVBoxLayout(items_given_widget)
        
        items_given_layout.addWidget(QLabel("Items the player receives as rewards:"))
        self.items_given_list = QListWidget()
        self.items_given_list.setMaximumHeight(120)
        items_given_layout.addWidget(self.items_given_list)
        
        items_given_btn_layout = QHBoxLayout()
        add_given_btn = QPushButton("Add Selected Item")
        add_given_btn.clicked.connect(lambda: self._add_selected_item('given'))
        items_given_btn_layout.addWidget(add_given_btn)
        
        remove_given_btn = QPushButton("Remove")
        remove_given_btn.clicked.connect(lambda: self._remove_item('given'))
        items_given_btn_layout.addWidget(remove_given_btn)
        items_given_layout.addLayout(items_given_btn_layout)
        
        items_tabs.addTab(items_given_widget, "Items Given")
        
        # Items TAKEN tab
        items_taken_widget = QWidget()
        items_taken_layout = QVBoxLayout(items_taken_widget)
        
        items_taken_layout.addWidget(QLabel("Quest items removed from player upon completion:"))
        self.items_taken_list = QListWidget()
        self.items_taken_list.setMaximumHeight(120)
        items_taken_layout.addWidget(self.items_taken_list)
        
        items_taken_btn_layout = QHBoxLayout()
        add_taken_btn = QPushButton("Add Selected Item")
        add_taken_btn.clicked.connect(lambda: self._add_selected_item('taken'))
        items_taken_btn_layout.addWidget(add_taken_btn)
        
        remove_taken_btn = QPushButton("Remove")
        remove_taken_btn.clicked.connect(lambda: self._remove_item('taken'))
        items_taken_layout.addLayout(items_taken_btn_layout)
        
        items_tabs.addTab(items_taken_widget, "Items Taken")
        
        layout.addWidget(items_tabs)
        
        # Reward preview
        preview_group = QGroupBox("Reward Preview")
        preview_layout = QVBoxLayout(preview_group)
        
        self.reward_preview = QTextEdit()
        self.reward_preview.setReadOnly(True)
        self.reward_preview.setMaximumHeight(100)
        preview_layout.addWidget(self.reward_preview)
        
        layout.addWidget(preview_group)
        
        return widget
    
    def _create_balance_group(self) -> QGroupBox:
        """Create balance checking group"""
        group = QGroupBox("Balance Checking")
        layout = QVBoxLayout(group)
        
        # Balance indicator
        indicator_layout = QHBoxLayout()
        
        self.balance_label = QLabel("Balance Status:")
        indicator_layout.addWidget(self.balance_label)
        
        self.balance_status = QLabel("Not Calculated")
        self.balance_status.setStyleSheet("font-weight: bold; color: orange;")
        indicator_layout.addWidget(self.balance_status)
        
        indicator_layout.addStretch()
        
        self.refresh_balance_btn = QPushButton("Refresh Balance")
        self.refresh_balance_btn.clicked.connect(self._update_balance)
        indicator_layout.addWidget(self.refresh_balance_btn)
        
        layout.addLayout(indicator_layout)
        
        # Balance details
        self.balance_details = QTextEdit()
        self.balance_details.setReadOnly(True)
        self.balance_details.setMaximumHeight(80)
        layout.addWidget(self.balance_details)
        
        # Warnings
        self.warnings_label = QLabel("Warnings:")
        layout.addWidget(self.warnings_label)
        
        self.warnings_list = QListWidget()
        self.warnings_list.setMaximumHeight(100)
        layout.addWidget(self.warnings_list)
        
        return group
    
    def _setup_connections(self):
        """Setup signal connections"""
        # Item table selection
        self.item_table.itemSelectionChanged.connect(self._on_item_selection_changed)
        
        # Reward items list selection
        self.reward_items_list.itemSelectionChanged.connect(self._on_reward_item_selection_changed)
    
    @Slot()
    def _load_items(self):
        """Load items from CFF database"""
        # Show loading indicator
        self.item_table.setRowCount(1)
        self.item_table.setItem(0, 0, QTableWidgetItem("Loading items..."))
        
        # Create worker thread
        self.worker_thread = QThread()
        self.worker = ItemBrowserWorker(self.data_model)
        self.worker.moveToThread(self.worker_thread)
        
        # Connect signals
        self.worker.items_loaded.connect(self._on_items_loaded)
        self.worker.finished.connect(self._on_items_load_finished)
        self.worker_thread.started.connect(self.worker.load_items)
        
        # Start worker
        self.worker_thread.start()
    
    @Slot(list)
    def _on_items_loaded(self, items: List[Dict]):
        """Handle items loaded from worker"""
        self.items = items
        self._populate_item_table()
    
    @Slot()
    def _on_items_load_finished(self):
        """Handle item loading finished"""
        # Clean up worker thread
        try:
            self.worker_thread.quit()
            self.worker_thread.wait()
        except:
            pass
    
    def _populate_item_table(self):
        """Populate item table with loaded items"""
        self.item_table.setRowCount(len(self.items))
        
        for row, item in enumerate(self.items):
            # Name
            name_item = QTableWidgetItem(item['name'])
            name_item.setData(Qt.UserRole, item)  # Store full item data
            self.item_table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(item['type'])
            self.item_table.setItem(row, 1, type_item)
            
            # Level
            level_item = QTableWidgetItem(str(item['level']))
            self.item_table.setItem(row, 2, level_item)
            
            # Value
            value_item = QTableWidgetItem(str(item['value']))
            self.item_table.setItem(row, 3, value_item)
            
            # Damage/Defense
            if item['type'] == 'Weapon':
                damage_text = f"{item.get('damage', 0)} dmg"
            elif item['type'] == 'Armor':
                damage_text = f"{item.get('defense', 0)} def"
            else:
                damage_text = "-"
            
            damage_item = QTableWidgetItem(damage_text)
            self.item_table.setItem(row, 4, damage_item)
            
            # Actions
            action_btn = QPushButton("Add")
            action_btn.clicked.connect(lambda checked, r=row: self._add_item_at_row(r))
            self.item_table.setCellWidget(row, 5, action_btn)
        
        self.item_table.resizeColumnsToContents()
    
    @Slot()
    def _filter_items(self):
        """Filter items based on search and type"""
        search_text = self.item_search.text().lower()
        type_filter = self.item_type_filter.currentText()
        
        for row in range(self.item_table.rowCount()):
            item = self.item_table.item(row, 0).data(Qt.UserRole)
            if not item:
                continue
            
            # Check search
            name_match = search_text in item['name'].lower()
            
            # Check type
            type_match = (type_filter == "All Types" or item['type'] == type_filter)
            
            # Show/hide row
            self.item_table.setRowHidden(row, not (name_match and type_match))
    
    @Slot()
    def _on_item_selection_changed(self):
        """Handle item selection change"""
        selected_items = self.item_table.selectedItems()
        if selected_items:
            # Get full item data from first column
            row = selected_items[0].row()
            item = self.item_table.item(row, 0).data(Qt.UserRole)
            
            # Update UI with item details
            self.logger.debug(f"Selected item: {item['name']}")
    
    @Slot()
    def _on_reward_item_selection_changed(self):
        """Handle reward item selection change"""
        # Could show item details here
        pass
    
    @Slot()
    def _add_selected_item(self, item_type='given'):
        """Add currently selected item to rewards (given or taken)"""
        selected_items = self.item_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an item to add.")
            return
        
        # Get full item data
        row = selected_items[0].row()
        item = self.item_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        
        self._add_item_to_rewards(item, item_type)
    
    @Slot(int)
    def _add_item_at_row(self, row: int):
        """Add item at specific row to rewards (defaults to given)"""
        item = self.item_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        self._add_item_to_rewards(item, 'given')
    
    def _add_item_to_rewards(self, item: Dict, item_type='given'):
        """Add item to reward list (given or taken)"""
        # Select target list
        target_list = self.items_given_list if item_type == 'given' else self.items_taken_list
        target_rewards = self.current_rewards['items_given'] if item_type == 'given' else self.current_rewards['items_taken']
        
        # Check if already added
        for existing in target_rewards:
            if existing['id'] == item['id']:
                type_str = "given to" if item_type == 'given' else "taken from"
                QMessageBox.information(self, "Already Added", f"{item['name']} is already in items {type_str} player.")
                return
        
        # Add to rewards
        target_rewards.append(item)
        
        # Update list widget
        list_item = QListWidgetItem(f"[{item['id']}] {item['name']} ({item['type']})")
        list_item.setData(Qt.ItemDataRole.UserRole, item)
        target_list.addItem(list_item)
        
        # Emit change and update balance
        self._on_rewards_changed()
    
    @Slot()
    def _remove_item(self, item_type='given'):
        """Remove selected item from rewards (given or taken)"""
        target_list = self.items_given_list if item_type == 'given' else self.items_taken_list
        target_rewards = self.current_rewards['items_given'] if item_type == 'given' else self.current_rewards['items_taken']
        
        selected_items = target_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select an item to remove.")
            return
        
        # Remove from rewards
        list_item = selected_items[0]
        item = list_item.data(Qt.ItemDataRole.UserRole)
        
        if item in target_rewards:
            target_rewards.remove(item)
        
        # Remove from list widget
        row = target_list.row(list_item)
        target_list.takeItem(row)
        
        # Emit change and update balance
        self._on_rewards_changed()
    
    @Slot()
    def _on_rewards_changed(self):
        """Handle any reward change"""
        # Update current rewards from UI
        self.current_rewards['xp'] = self.xp_spin.value()
        self.current_rewards['gold'] = self.gold_spin.value()
        self.current_rewards['silver'] = self.silver_spin.value()
        self.current_rewards['copper'] = self.copper_spin.value()
        
        # Update preview
        self._update_reward_preview()
        
        # Update balance
        self._update_balance()
        
        # Emit change signal
        self.rewards_changed.emit(self.current_rewards.copy())
    
    def _update_reward_preview(self):
        """Update reward preview"""
        preview_lines = []
        
        # XP
        if self.current_rewards['xp'] > 0:
            preview_lines.append(f"Experience: {self.current_rewards['xp']} XP")
        
        # Money
        money_parts = []
        if self.current_rewards['gold'] > 0:
            money_parts.append(f"{self.current_rewards['gold']} Gold")
        if self.current_rewards['silver'] > 0:
            money_parts.append(f"{self.current_rewards['silver']} Silver")
        if self.current_rewards['copper'] > 0:
            money_parts.append(f"{self.current_rewards['copper']} Copper")
        
        if money_parts:
            preview_lines.append(f"Money: {', '.join(money_parts)}")
        
        # Items Given
        if self.current_rewards['items_given']:
            item_names = [f"{item['name']} ({item['id']})" for item in self.current_rewards['items_given']]
            preview_lines.append(f"Items Given: {', '.join(item_names)}")
        
        # Items Taken
        if self.current_rewards['items_taken']:
            item_names = [f"{item['name']} ({item['id']})" for item in self.current_rewards['items_taken']]
            preview_lines.append(f"Items Taken: {', '.join(item_names)}")
        
        # Update preview
        preview_text = '\n'.join(preview_lines) if preview_lines else "No rewards set"
        self.reward_preview.setPlainText(preview_text)
    
    @Slot()
    def _update_balance(self):
        """Update balance checking"""
        # Calculate balance
        quest_level = self.quest_level_spin.value()
        
        # Simple balance calculation
        self.balance_data = self._calculate_balance(self.current_rewards, quest_level)
        
        # Update UI
        if self.balance_data.is_balanced:
            self.balance_status.setText("Balanced")
            self.balance_status.setStyleSheet("font-weight: bold; color: green;")
        else:
            self.balance_status.setText("Unbalanced")
            self.balance_status.setStyleSheet("font-weight: bold; color: red;")
        
        # Update details
        details = f"Total Value: {self.balance_data.total_value}\n"
        details += f"Recommended Level: {self.balance_data.recommended_level}"
        self.balance_details.setPlainText(details)
        
        # Update warnings
        self.warnings_list.clear()
        for warning in self.balance_data.warnings:
            self.warnings_list.addItem(warning)
    
    def _calculate_balance(self, rewards: Dict, quest_level: int) -> RewardBalance:
        """Calculate reward balance"""
        balance = RewardBalance()
        
        # Calculate XP value (1 XP = 1 value point)
        balance.xp_value = rewards.get('xp', 0)
        
        # Calculate money value (1 Gold = 100 value points)
        gold = rewards.get('gold', 0)
        silver = rewards.get('silver', 0)
        copper = rewards.get('copper', 0)
        balance.gold_value = gold * 100 + silver * 10 + copper * 1
        
        # Calculate item value
        balance.item_value = sum(item.get('value', 0) for item in rewards.get('items', []))
        
        # Total value
        balance.total_value = balance.xp_value + balance.gold_value + balance.item_value
        
        # Recommended level based on value
        balance.recommended_level = max(1, balance.total_value // 500)
        
        # Check balance
        level_diff = abs(balance.recommended_level - quest_level)
        balance.is_balanced = level_diff <= 2
        
        # Generate warnings
        if balance.total_value == 0:
            balance.warnings.append("No rewards set")
        elif balance.total_value < 50:
            balance.warnings.append("Very low rewards for any quest")
        elif balance.total_value > 10000:
            balance.warnings.append("Extremely high rewards - possibly overpowered")
        
        if level_diff > 5:
            balance.warnings.append(f"Rewards更适合等级 {balance.recommended_level} 的任务")
        elif level_diff > 2:
            balance.warnings.append(f"Rewards may be too {'high' if balance.recommended_level < quest_level else 'low'} for quest level")
        
        if not rewards.get('items'):
            balance.warnings.append("No item rewards - consider adding at least one item")
        
        return balance
    
    @Slot()
    def _apply_template(self, template_name: str):
        """Apply reward template"""
        templates = {
            "Starter Quest": {
                'xp': 50, 'gold': 5, 'silver': 25, 'copper': 50,
                'target_items': 1, 'target_value': 20
            },
            "Medium Quest": {
                'xp': 200, 'gold': 20, 'silver': 50, 'copper': 0,
                'target_items': 2, 'target_value': 100
            },
            "Main Quest": {
                'xp': 1000, 'gold': 100, 'silver': 0, 'copper': 0,
                'target_items': 3, 'target_value': 500
            },
            "Epic Quest": {
                'xp': 5000, 'gold': 500, 'silver': 50, 'copper': 0,
                'target_items': 5, 'target_value': 2000
            }
        }
        
        if template_name == "Custom":
            return
        
        template = templates.get(template_name)
        if not template:
            return
        
        # Apply template values
        self.xp_spin.setValue(template['xp'])
        self.gold_spin.setValue(template['gold'])
        self.silver_spin.setValue(template['silver'])
        self.copper_spin.setValue(template['copper'])
        
        # Auto-select some items that fit template
        self._auto_select_items(template['target_items'], template['target_value'])
    
    def _auto_select_items(self, target_count: int, target_value: int):
        """Auto-select items that fit target criteria"""
        if not self.items:
            return
        
        # Filter items by value range
        suitable_items = [item for item in self.items 
                        if item['value'] <= target_value * 1.5 and item['value'] >= target_value * 0.5]
        
        # Sort by value (prefer closer to target)
        suitable_items.sort(key=lambda x: abs(x['value'] - target_value))
        
        # Select top items
        items_to_add = min(target_count, len(suitable_items))
        for i in range(items_to_add):
            self._add_item_to_rewards(suitable_items[i])
    
    def get_rewards(self) -> Dict:
        """Get current reward configuration"""
        return self.current_rewards.copy()
    
    def set_rewards(self, rewards: Dict):
        """Set reward configuration"""
        self.current_rewards = rewards.copy()
        
        # Update UI
        self.xp_spin.setValue(rewards.get('xp', 0))
        self.gold_spin.setValue(rewards.get('gold', 0))
        self.silver_spin.setValue(rewards.get('silver', 0))
        self.copper_spin.setValue(rewards.get('copper', 0))
        
        # Update items
        self.selected_items.clear()
        self.reward_items_list.clear()
        
        for item in rewards.get('items', []):
            self.selected_items.append(item)
            list_item = QListWidgetItem(f"{item['name']} ({item['type']})")
            list_item.setData(Qt.UserRole, item)
            self.reward_items_list.addItem(list_item)
        
        # Update preview and balance
        self._on_rewards_changed()


# Simple test function
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    from TirganachReloaded.cff_editor.data_model import CFFDataModel
    from pathlib import Path
    
    app = QApplication(sys.argv)
    
    # Create simple data model for testing
    class MockDataModel:
        def get_elements(self, element_type):
            if element_type == "weapons":
                return [
                    type('Weapon', (), {'item_id': 1001, 'name': 'Sword of Testing', 'value': 100, 'damage_min': 10})
                ]
            elif element_type == "armor":
                return [
                    type('Armor', (), {'item_id': 2001, 'name': 'Armor of Testing', 'value': 80, 'armor_class': 15})
                ]
            elif element_type == "items":
                return [
                    type('Item', (), {'item_id': 3001, 'name': 'Potion of Testing', 'value': 25})
                ]
            return []
        
        def get_localised_text(self, item, field):
            return getattr(item, field, None)
    
    # Test reward builder
    data_model = MockDataModel()
    builder = RewardBuilderWidget(data_model)
    builder.setWindowTitle("Reward Builder Test")
    builder.resize(900, 700)
    builder.show()
    
    sys.exit(app.exec())