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
from PySide6.QtCore import QObject, Signal, Qt
from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import Qt
from pathlib import Path


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

        # Icon-related attributes
        self.icon_cache = {}  # Cache for loaded QPixmap objects
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.ui_assets_dir = self.project_root / "ExtractedAssets" / "UI" / "extracted"

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

    # Icon-related methods

    def get_icon_path(self, category: str, element: Any) -> Optional[str]:
        """
        Get icon path for an element.

        Args:
            category: Category name (e.g., "items", "weapons", "spells")
            element: The element object

        Returns:
            Path to PNG file or None
        """
        if not self.game_data:
            return None

        # Get element ID based on category
        element_id = self._get_element_id(category, element)
        if element_id is None:
            return None

        # Look up in item_ui table for items/weapons/armor
        if category in ["items", "weapons", "armor"]:
            ui_entry = self._find_item_ui_entry(element_id)
            if ui_entry:
                handle = ui_entry.get("item_ui_handle")
                if handle:
                    return self._resolve_icon_path(handle, "items")

        # Look up in spell_names table for spells
        elif category == "spells":
            spell = self._find_spell_entry(element_id)
            if spell and spell.get("spell_ui_handle"):
                handle = spell["spell_ui_handle"]
                return self._resolve_icon_path(handle, "spells")

        return None

    def get_icon_pixmap(self, category: str, element: Any, size=(64, 64)) -> Optional[QPixmap]:
        """
        Get QPixmap for display in GUI.
        Uses cache for performance.

        Args:
            category: Category name
            element: Element object
            size: Desired size as (width, height) tuple

        Returns:
            QPixmap object or None
        """
        cache_key = f"{category}_{id(element)}_{size}"
        if cache_key in self.icon_cache:
            return self.icon_cache[cache_key]

        icon_path = self.get_icon_path(category, element)
        if icon_path and Path(icon_path).exists():
            pixmap = QPixmap(icon_path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(size[0], size[1])
                self.icon_cache[cache_key] = pixmap
                return pixmap

        # Return fallback icon
        return self._get_fallback_icon(category, size)

    def get_icon_icon(self, category: str, element: Any, size=(64, 64)) -> QIcon:
        """
        Get QIcon for display in GUI elements like buttons.

        Args:
            category: Category name
            element: Element object
            size: Desired size as (width, height) tuple

        Returns:
            QIcon object
        """
        pixmap = self.get_icon_pixmap(category, element, size)
        if pixmap:
            return QIcon(pixmap)
        return QIcon()

    def _get_element_id(self, category: str, element: Any) -> Optional[int]:
        """Extract ID from element based on category."""
        try:
            # Common ID field names
            id_fields = ["id", "item_id", "spell_id", "weapon_id", "armor_id"]

            for field_name in id_fields:
                if hasattr(element, field_name):
                    return getattr(element, field_name)

            # Try index-based ID for some categories
            if hasattr(element, '_index'):
                return element._index

        except Exception:
            pass

        return None

    def _find_item_ui_entry(self, item_id: int) -> Optional[Dict]:
        """Find item_ui entry by item_id."""
        try:
            item_ui_table = self.get_table("item_ui")
            if item_ui_table:
                for entry in item_ui_table:
                    if getattr(entry, "item_id", None) == item_id and getattr(entry, "item_ui_index", None) == 1:
                        return {
                            "item_id": getattr(entry, "item_id", 0),
                            "item_ui_index": getattr(entry, "item_ui_index", 0),
                            "item_ui_handle": getattr(entry, "item_ui_handle", ""),
                            "scaled_down": getattr(entry, "scaled_down", 0)
                        }
        except Exception:
            pass
        return None

    def _find_spell_entry(self, spell_id: int) -> Optional[Dict]:
        """Find spell entry by spell_id."""
        try:
            spells_table = self.get_table("spells")
            if spells_table:
                for spell in spells_table:
                    if getattr(spell, "spell_id", None) == spell_id:
                        return {
                            "spell_id": getattr(spell, "spell_id", 0),
                            "spell_name_id": getattr(spell, "spell_name_id", 0),
                            "spell_ui_handle": getattr(spell, "spell_ui_handle", "")
                        }
        except Exception:
            pass
        return None

    def _resolve_icon_path(self, handle: str, category: str) -> Optional[str]:
        """
        Convert UI handle to file path.
        Since we have numbered PNG files instead of named ones,
        create a mapping based on handle hash.
        """
        if not handle:
            return None

        # First try direct lookup (in case we have properly named files)
        icon_path = self.ui_assets_dir / category / f"{handle}.png"
        if icon_path.exists():
            return str(icon_path)

        # Fall back to mapping numbered files
        # Use a hash of the handle to map to available numbered files
        import hashlib
        hash_obj = hashlib.md5(handle.encode('utf-8'))
        hash_int = int(hash_obj.hexdigest(), 16)

        # Get list of available PNG files for this category
        png_dir = self.ui_assets_dir / category / "png"
        if png_dir.exists():
            png_files = sorted(png_dir.glob("*.png"))
            if png_files:
                # Map hash to available files
                file_index = hash_int % len(png_files)
                mapped_file = png_files[file_index]
                return str(mapped_file)

        return None

        # Direct lookup: handle + .png
        icon_path = self.ui_assets_dir / category / f"{handle}.png"

        if icon_path.exists():
            return str(icon_path)

        return None

    def _get_fallback_icon(self, category: str, size) -> Optional[QPixmap]:
        """
        Get fallback icon for missing assets.

        Args:
            category: Category name
            size: Desired size tuple

        Returns:
            QPixmap of fallback icon or None
        """
        fallback_dir = self.ui_assets_dir.parent / "fallback_icons"
        fallback_files = {
            "items": "ui_item_unknown.png",
            "weapons": "ui_weapon_unknown.png",
            "armor": "ui_armor_unknown.png",
            "spells": "ui_spell_unknown.png"
        }

        fallback_file = fallback_files.get(category, "ui_unknown.png")
        fallback_path = fallback_dir / fallback_file

        if fallback_path.exists():
            pixmap = QPixmap(str(fallback_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(size[0], size[1])
                return pixmap

        return None

    def clear_icon_cache(self):
        """Clear the icon cache to free memory."""
        self.icon_cache.clear()
