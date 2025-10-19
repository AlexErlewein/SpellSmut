"""
Data Model for CFF Editor
Manages loaded GameData and provides interface for GUI
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tirganach import GameData
from tirganach.types import *
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal


class CFFDataModel(QObject):
    """Manages loaded CFF data and provides signals for UI updates"""

    # Signals
    data_loaded = Signal()
    data_modified = Signal()
    category_changed = Signal(str)
    element_selected = Signal(str, int)

    def __init__(self):
        super().__init__()
        self.game_data: Optional[GameData] = None
        self.file_path: Optional[str] = None
        self.modified = False
        self.current_category: Optional[str] = None
        self.current_element_index: Optional[int] = None

    def load_file(self, file_path: str) -> bool:
        """Load a CFF file"""
        try:
            self.game_data = GameData(file_path)
            self.file_path = file_path
            self.modified = False
            self.data_loaded.emit()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def get_categories(self) -> List[tuple]:
        """Returns list of (category_name, count) tuples"""
        if not self.game_data:
            return []

        categories = []
        for table_name, table_type in self.game_data.table_info().items():
            table = getattr(self.game_data, table_name)
            count = len(table)
            # Make name more readable
            display_name = table_name.replace('_', ' ').title()
            categories.append((table_name, display_name, count))

        return categories

    def get_table(self, category: str):
        """Get table by category name"""
        if not self.game_data:
            return None
        return getattr(self.game_data, category, None)

    def get_elements(self, category: str) -> List[Any]:
        """Returns all elements in a category"""
        if not self.game_data:
            return []

        table = self.get_table(category)
        if table is None:
            return []

        return list(table)

    def get_element_by_index(self, category: str, index: int) -> Optional[Any]:
        """Get element by index in category"""
        elements = self.get_elements(category)
        if 0 <= index < len(elements):
            return elements[index]
        return None

    def get_element_fields(self, element: Any) -> List[tuple]:
        """Returns list of (field_name, value, field_info) tuples for an element"""
        if element is None:
            return []

        fields = []
        for field_name in sorted(element._fields.keys()):
            try:
                value = getattr(element, field_name)
                field_info = element._fields[field_name]
                fields.append((field_name, value, field_info))
            except Exception as e:
                fields.append((field_name, f"[Error: {e}]", None))

        return fields

    def update_element_field(self, category: str, index: int, field_name: str, new_value: Any) -> bool:
        """Update a field value in an element"""
        try:
            element = self.get_element_by_index(category, index)
            if element is None:
                return False

            setattr(element, field_name, new_value)
            self.modified = True
            self.data_modified.emit()
            return True
        except Exception as e:
            print(f"Error updating field: {e}")
            return False

    def save_file(self, file_path: Optional[str] = None) -> bool:
        """Save CFF file"""
        if not self.game_data:
            return False

        save_path = file_path or self.file_path
        if not save_path:
            return False

        try:
            self.game_data.save(save_path)
            self.file_path = save_path
            self.modified = False
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False

    def is_modified(self) -> bool:
        """Check if data has been modified"""
        return self.modified

    def get_file_path(self) -> Optional[str]:
        """Get current file path"""
        return self.file_path
