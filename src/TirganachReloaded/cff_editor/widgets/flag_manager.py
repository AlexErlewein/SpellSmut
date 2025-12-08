"""
Flag Manager Widget
===================
Manages flags used in quests (Item, NPC, Global).

Author: Quest Editor Team
Date: November 16, 2025
"""

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QTextEdit, QDialog,
    QDialogButtonBox, QHeaderView, QMessageBox, QGroupBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor
from typing import Dict, List, Optional
import json


class FlagDefinition:
    """Represents a single flag definition"""
    
    def __init__(self, name: str, flag_type: str, description: str = "", 
                 used_by: List[str] = None, auto_generated: bool = False):
        self.name = name
        self.flag_type = flag_type  # "item", "npc", "global"
        self.description = description
        self.used_by = used_by or []  # List of quest IDs/condition IDs
        self.auto_generated = auto_generated
    
    def to_dict(self):
        return {
            "name": self.name,
            "flag_type": self.flag_type,
            "description": self.description,
            "used_by": self.used_by,
            "auto_generated": self.auto_generated
        }
    
    @staticmethod
    def from_dict(data: dict):
        return FlagDefinition(
            name=data.get("name", ""),
            flag_type=data.get("flag_type", "global"),
            description=data.get("description", ""),
            used_by=data.get("used_by", []),
            auto_generated=data.get("auto_generated", False)
        )


class FlagEditorDialog(QDialog):
    """Dialog for adding/editing a flag"""
    
    def __init__(self, parent=None, flag: FlagDefinition = None):
        super().__init__(parent)
        self.flag = flag
        self.setup_ui()
        
        if flag:
            self.load_flag(flag)
    
    def setup_ui(self):
        self.setWindowTitle("Flag Editor")
        self.setModal(True)
        self.resize(500, 350)
        
        layout = QVBoxLayout(self)
        
        # Flag Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Flag Name:"))
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., PlayerHasItemSanduhr or AmraUndLea1Complete")
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Flag Type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Flag Type:"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["global", "item", "npc"])
        self.type_combo.currentTextChanged.connect(self.on_type_changed)
        type_layout.addWidget(self.type_combo)
        layout.addLayout(type_layout)
        
        # Naming Convention Hint
        self.naming_hint = QLabel()
        self.naming_hint.setStyleSheet("color: #666; font-style: italic;")
        self.naming_hint.setWordWrap(True)
        layout.addWidget(self.naming_hint)
        self.on_type_changed(self.type_combo.currentText())
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Describe what this flag tracks...")
        self.description_input.setMaximumHeight(80)
        layout.addWidget(self.description_input)
        
        # Auto-generated checkbox (disabled for editing)
        self.auto_gen_label = QLabel("🤖 Auto-generated flag")
        self.auto_gen_label.setStyleSheet("color: #0066cc; font-weight: bold;")
        self.auto_gen_label.setVisible(False)
        layout.addWidget(self.auto_gen_label)
        
        # Used by info (read-only)
        self.used_by_label = QLabel()
        self.used_by_label.setStyleSheet("color: #666;")
        self.used_by_label.setWordWrap(True)
        layout.addWidget(self.used_by_label)
        
        layout.addStretch()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def on_type_changed(self, flag_type: str):
        """Update naming convention hint based on flag type"""
        hints = {
            "item": "💡 Item flags usually start with 'PlayerHasItem' (e.g., PlayerHasItemSanduhr)",
            "npc": "💡 NPC flags track dialogue/interactions (e.g., n_P213_Talked, ShanMuirGreeted)",
            "global": "💡 Global flags track world state (e.g., TrollCampDestroyed, QuestXComplete)"
        }
        self.naming_hint.setText(hints.get(flag_type, ""))
    
    def load_flag(self, flag: FlagDefinition):
        """Load flag data into editor"""
        self.name_input.setText(flag.name)
        self.type_combo.setCurrentText(flag.flag_type)
        self.description_input.setPlainText(flag.description)
        
        if flag.auto_generated:
            self.auto_gen_label.setVisible(True)
        
        if flag.used_by:
            self.used_by_label.setText(f"Used by: {', '.join(flag.used_by)}")
        else:
            self.used_by_label.setText("Not used yet")
    
    def get_flag(self) -> Optional[FlagDefinition]:
        """Get the edited flag"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Invalid Input", "Flag name cannot be empty!")
            return None
        
        flag_type = self.type_combo.currentText()
        description = self.description_input.toPlainText().strip()
        
        if self.flag:
            # Editing existing flag - preserve metadata
            self.flag.name = name
            self.flag.flag_type = flag_type
            self.flag.description = description
            return self.flag
        else:
            # Creating new flag
            return FlagDefinition(
                name=name,
                flag_type=flag_type,
                description=description,
                auto_generated=False
            )


class FlagManagerWidget(QWidget):
    """
    Widget for managing quest flags.
    
    Features:
    - Add/edit/delete flags
    - Track flag usage across quests
    - Auto-generate flags from quest data
    - Export/import flag definitions
    """
    
    flag_selected = Signal(str, str)  # flag_name, flag_type
    flags_changed = Signal()  # Emitted when flags are modified
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.flags: Dict[str, FlagDefinition] = {}  # name -> FlagDefinition
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = QLabel("Flag Manager")
        header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 5px;")
        layout.addWidget(header)
        
        # Description
        desc = QLabel("Manage flags used in quest conditions and dialogues. "
                     "Flags track quest progress, item possession, and world state.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(desc)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Filter:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search flags...")
        self.search_input.textChanged.connect(self.filter_flags)
        filter_layout.addWidget(self.search_input, 1)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["All Types", "Global", "Item", "NPC"])
        self.type_filter.currentTextChanged.connect(self.filter_flags)
        filter_layout.addWidget(self.type_filter)
        
        layout.addLayout(filter_layout)
        
        # Flags table
        self.flags_table = QTableWidget()
        self.flags_table.setColumnCount(5)
        self.flags_table.setHorizontalHeaderLabels([
            "Flag Name", "Type", "Description", "Used By", "Auto"
        ])
        self.flags_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.flags_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.flags_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.flags_table.setSelectionMode(QTableWidget.SingleSelection)
        self.flags_table.itemDoubleClicked.connect(self.edit_selected_flag)
        layout.addWidget(self.flags_table)
        
        # Stats
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(self.stats_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        add_btn = QPushButton("➕ Add Flag")
        add_btn.clicked.connect(self.add_flag)
        button_layout.addWidget(add_btn)
        
        edit_btn = QPushButton("✏️ Edit Flag")
        edit_btn.clicked.connect(self.edit_selected_flag)
        button_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️ Delete Flag")
        delete_btn.clicked.connect(self.delete_selected_flag)
        button_layout.addWidget(delete_btn)
        
        button_layout.addStretch()
        
        export_btn = QPushButton("📤 Export")
        export_btn.clicked.connect(self.export_flags)
        button_layout.addWidget(export_btn)
        
        import_btn = QPushButton("📥 Import")
        import_btn.clicked.connect(self.import_flags)
        button_layout.addWidget(import_btn)
        
        layout.addLayout(button_layout)
        
        self.update_stats()
    
    def add_flag(self, flag: FlagDefinition = None):
        """Add a new flag or open dialog to create one"""
        if flag:
            # Direct addition (e.g., auto-generated)
            self.flags[flag.name] = flag
            self.refresh_table()
            self.flags_changed.emit()
            return
        
        # Open dialog
        dialog = FlagEditorDialog(self)
        if dialog.exec() == QDialog.Accepted:
            new_flag = dialog.get_flag()
            if new_flag:
                if new_flag.name in self.flags:
                    reply = QMessageBox.question(
                        self, "Flag Exists",
                        f"Flag '{new_flag.name}' already exists. Replace it?",
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if reply != QMessageBox.Yes:
                        return
                
                self.flags[new_flag.name] = new_flag
                self.refresh_table()
                self.flags_changed.emit()
    
    def edit_selected_flag(self):
        """Edit the selected flag"""
        row = self.flags_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a flag to edit.")
            return
        
        flag_name = self.flags_table.item(row, 0).text()
        flag = self.flags.get(flag_name)
        if not flag:
            return
        
        dialog = FlagEditorDialog(self, flag)
        if dialog.exec() == QDialog.Accepted:
            edited_flag = dialog.get_flag()
            if edited_flag:
                # Handle name change
                if edited_flag.name != flag_name:
                    del self.flags[flag_name]
                
                self.flags[edited_flag.name] = edited_flag
                self.refresh_table()
                self.flags_changed.emit()
    
    def delete_selected_flag(self):
        """Delete the selected flag"""
        row = self.flags_table.currentRow()
        if row < 0:
            QMessageBox.information(self, "No Selection", "Please select a flag to delete.")
            return
        
        flag_name = self.flags_table.item(row, 0).text()
        flag = self.flags.get(flag_name)
        
        if flag and flag.used_by:
            reply = QMessageBox.warning(
                self, "Flag In Use",
                f"Flag '{flag_name}' is used by: {', '.join(flag.used_by)}\n\n"
                "Deleting it may break conditions. Continue?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply != QMessageBox.Yes:
                return
        
        del self.flags[flag_name]
        self.refresh_table()
        self.flags_changed.emit()
    
    def filter_flags(self):
        """Filter flags based on search and type"""
        search_text = self.search_input.text().lower()
        type_filter = self.type_filter.currentText().lower()
        
        for row in range(self.flags_table.rowCount()):
            flag_name = self.flags_table.item(row, 0).text().lower()
            flag_type = self.flags_table.item(row, 1).text().lower()
            flag_desc = self.flags_table.item(row, 2).text().lower()
            
            # Check search match
            search_match = (search_text in flag_name or 
                          search_text in flag_desc)
            
            # Check type match
            type_match = (type_filter == "all types" or 
                         type_filter == flag_type)
            
            self.flags_table.setRowHidden(row, not (search_match and type_match))
    
    def refresh_table(self):
        """Refresh the flags table"""
        self.flags_table.setRowCount(0)
        
        # Sort flags by type, then name
        sorted_flags = sorted(
            self.flags.values(),
            key=lambda f: (f.flag_type, f.name)
        )
        
        for flag in sorted_flags:
            row = self.flags_table.rowCount()
            self.flags_table.insertRow(row)
            
            # Name
            name_item = QTableWidgetItem(flag.name)
            self.flags_table.setItem(row, 0, name_item)
            
            # Type
            type_item = QTableWidgetItem(flag.flag_type.capitalize())
            type_colors = {
                "global": QColor(52, 152, 219),  # Blue
                "item": QColor(46, 204, 113),    # Green
                "npc": QColor(155, 89, 182)      # Purple
            }
            type_item.setForeground(type_colors.get(flag.flag_type, Qt.black))
            self.flags_table.setItem(row, 1, type_item)
            
            # Description
            desc_item = QTableWidgetItem(flag.description[:100])
            self.flags_table.setItem(row, 2, desc_item)
            
            # Used By
            used_count = len(flag.used_by)
            used_item = QTableWidgetItem(
                f"{used_count} location{'s' if used_count != 1 else ''}"
            )
            self.flags_table.setItem(row, 3, used_item)
            
            # Auto-generated
            auto_item = QTableWidgetItem("🤖" if flag.auto_generated else "")
            auto_item.setTextAlignment(Qt.AlignCenter)
            self.flags_table.setItem(row, 4, auto_item)
        
        self.filter_flags()
        self.update_stats()
    
    def update_stats(self):
        """Update statistics label"""
        total = len(self.flags)
        global_count = sum(1 for f in self.flags.values() if f.flag_type == "global")
        item_count = sum(1 for f in self.flags.values() if f.flag_type == "item")
        npc_count = sum(1 for f in self.flags.values() if f.flag_type == "npc")
        used_count = sum(1 for f in self.flags.values() if f.used_by)
        
        self.stats_label.setText(
            f"📊 Total: {total} flags | "
            f"🌍 Global: {global_count} | "
            f"📦 Item: {item_count} | "
            f"👤 NPC: {npc_count} | "
            f"✓ Used: {used_count}"
        )
    
    def export_flags(self):
        """Export flags to JSON"""
        data = {name: flag.to_dict() for name, flag in self.flags.items()}
        json_str = json.dumps(data, indent=2)
        
        # For now, just show in a dialog (TODO: save to file)
        dialog = QDialog(self)
        dialog.setWindowTitle("Export Flags")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Copy this JSON to save flags:"))
        
        text_edit = QTextEdit()
        text_edit.setPlainText(json_str)
        text_edit.selectAll()
        layout.addWidget(text_edit)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def import_flags(self):
        """Import flags from JSON"""
        # For now, just show input dialog (TODO: load from file)
        dialog = QDialog(self)
        dialog.setWindowTitle("Import Flags")
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        layout.addWidget(QLabel("Paste JSON data:"))
        
        text_edit = QTextEdit()
        layout.addWidget(text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec() == QDialog.Accepted:
            try:
                json_str = text_edit.toPlainText()
                data = json.loads(json_str)
                
                imported = 0
                for name, flag_data in data.items():
                    flag = FlagDefinition.from_dict(flag_data)
                    self.flags[name] = flag
                    imported += 1
                
                self.refresh_table()
                self.flags_changed.emit()
                
                QMessageBox.information(
                    self, "Import Complete",
                    f"Successfully imported {imported} flags."
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Import Error",
                    f"Failed to import flags:\n{str(e)}"
                )
    
    def register_flag_usage(self, flag_name: str, used_by: str):
        """Register that a flag is used by a quest/condition"""
        if flag_name in self.flags:
            if used_by not in self.flags[flag_name].used_by:
                self.flags[flag_name].used_by.append(used_by)
                self.refresh_table()
    
    def unregister_flag_usage(self, flag_name: str, used_by: str):
        """Unregister flag usage"""
        if flag_name in self.flags:
            if used_by in self.flags[flag_name].used_by:
                self.flags[flag_name].used_by.remove(used_by)
                self.refresh_table()
    
    def get_flags_by_type(self, flag_type: str) -> List[FlagDefinition]:
        """Get all flags of a specific type"""
        return [f for f in self.flags.values() if f.flag_type == flag_type]
    
    def get_all_flag_names(self) -> List[str]:
        """Get list of all flag names"""
        return sorted(self.flags.keys())
    
    def load_from_dict(self, data: dict):
        """Load flags from dictionary"""
        self.flags.clear()
        for name, flag_data in data.items():
            self.flags[name] = FlagDefinition.from_dict(flag_data)
        self.refresh_table()
    
    def to_dict(self) -> dict:
        """Export flags to dictionary"""
        return {name: flag.to_dict() for name, flag in self.flags.items()}


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    # Test widget
    widget = FlagManagerWidget()
    
    # Add some test flags
    widget.add_flag(FlagDefinition(
        "PlayerHasItemSanduhr",
        "item",
        "Player possesses the Sanduhr (hourglass) item",
        ["Quest_646", "Dialogue_Amra_1"],
        auto_generated=True
    ))
    
    widget.add_flag(FlagDefinition(
        "AmraUndLea1Complete",
        "global",
        "First part of Amra and Lea quest completed",
        ["Quest_652"]
    ))
    
    widget.add_flag(FlagDefinition(
        "n_P213_Talked",
        "npc",
        "Player has talked to NPC P213 (Shan Muir)"
    ))
    
    widget.show()
    sys.exit(app.exec())
