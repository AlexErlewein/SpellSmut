"""
Data Model for CFF Editor
Manages loaded GameData and provides interface for GUI
"""

import sys
import os
import json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from tirganach import GameData
from tirganach.types import *
from typing import List, Dict, Any, Optional
from PySide6.QtCore import QObject, Signal, Qt, QSettings
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
    language_changed = Signal(Language)

    def __init__(self):
        super().__init__()
        self.game_data: Optional[GameData] = None
        self.file_path: Optional[str] = None
        self.modified = False
        self.current_category: Optional[str] = None
        self.current_element_index: Optional[int] = None

        # Icon-related attributes
        self.icon_cache = {}  # Cache for loaded QPixmap objects
        self.project_root = Path(__file__).parent.parent.parent
        self.ui_assets_dir = self.project_root / "ExtractedAssets" / "UI" / "extracted"
        self.icons_root = self.project_root / "ExtractedAssets" / "UI" / "icons_extracted"
        self.data_dir = self.project_root / "TirganachReloaded" / "data"

        # Load icon mappings and analysis data
        self.icon_mapping = {}
        self.icon_index = {}
        self.verified_mappings = {}
        self._load_icon_data()

        # Settings for remembering last opened file and language
        self.settings = QSettings("SpellSmut", "TirganachReloaded")
        self.current_language = self._load_language_setting()

    def _load_language_setting(self) -> Language:
        """Load current language from settings, default to ENGLISH"""
        language_value = self.settings.value("current_language", 1)  # Default to ENGLISH (1)
        try:
            return Language(language_value)
        except ValueError:
            return Language.ENGLISH

    def set_current_language(self, language: Language):
        """Set the current language and save to settings"""
        if self.current_language != language:
            self.current_language = language
            self.settings.setValue("current_language", language.value)
            self.language_changed.emit(language)

    def get_current_language(self) -> Language:
        """Get the current language"""
        return self.current_language

        # Weapon name mapping
        self.weapon_name_mapping: Dict[int, str] = {}
        # Armor name mapping
        self.armor_name_mapping: Dict[int, str] = {}

    def load_file(self, file_path: str) -> bool:
        """Load a CFF file"""
        try:
            self.game_data = GameData(file_path)
            self.file_path = file_path
            self.modified = False

            # Load weapon name mapping
            self._load_weapon_names()
            # Load armor name mapping
            self._load_armor_names()

            # Save as last opened file
            self.settings.setValue("last_opened_file", file_path)
            self.data_loaded.emit()
            return True
        except Exception as e:
            print(f"Error loading file: {e}")
            return False

    def _load_weapon_names(self):
        """Load weapon name mapping from enhanced_weapons.json"""
        try:
            # Look for the file in the TirganachReloaded directory
            weapons_json_path = Path(__file__).parent.parent / "enhanced_weapons.json"
            if weapons_json_path.exists():
                with open(weapons_json_path, 'r', encoding='utf-8') as f:
                    weapons_data = json.load(f)

                # Create mapping from item_id to name
                self.weapon_name_mapping = {}
                for weapon in weapons_data:
                    item_id = weapon.get('item_id')
                    name = weapon.get('name')
                    if item_id is not None and name:
                        self.weapon_name_mapping[item_id] = name

                print(f"Loaded {len(self.weapon_name_mapping)} weapon names")
            else:
                print("enhanced_weapons.json not found, weapon names will not be available")
                self.weapon_name_mapping = {}
        except Exception as e:
            print(f"Error loading weapon names: {e}")
            self.weapon_name_mapping = {}

    def get_weapon_name(self, item_id: int) -> Optional[str]:
        """Get weapon name by item_id"""
        return self.weapon_name_mapping.get(item_id)

    def _load_armor_names(self):
        """Load armor name mapping from enhanced_armor.json"""
        try:
            # Look for the file in the TirganachReloaded directory
            armor_json_path = Path(__file__).parent.parent / "enhanced_armor.json"
            if armor_json_path.exists():
                with open(armor_json_path, 'r', encoding='utf-8') as f:
                    armor_data = json.load(f)

                # Create mapping from item_id to name
                self.armor_name_mapping = {}
                for armor in armor_data:
                    item_id = armor.get('item_id')
                    name = armor.get('name')
                    if item_id is not None and name:
                        self.armor_name_mapping[item_id] = name

                print(f"Loaded {len(self.armor_name_mapping)} armor names")
            else:
                print("enhanced_armor.json not found, armor names will not be available")
                self.armor_name_mapping = {}
        except Exception as e:
            print(f"Error loading armor names: {e}")
            self.armor_name_mapping = {}

    def get_armor_name(self, item_id: int) -> Optional[str]:
        """Get armor name by item_id"""
        return self.armor_name_mapping.get(item_id)

    def _load_icon_data(self):
        """Load icon mapping and analysis data."""
        try:
            # Load icon mapping
            mapping_path = self.data_dir / "ui_icon_mapping.json"
            if mapping_path.exists():
                with open(mapping_path, 'r') as f:
                    self.icon_mapping = json.load(f)
                print(f"Loaded icon mapping: {len(self.icon_mapping.get('item_to_icons', {}))} items")
            else:
                print(f"Icon mapping not found: {mapping_path}")
                self.icon_mapping = {}

            # Load icon index (check for split files first)
            manifest_path = self.icons_root / "icon_index_manifest.json"
            if manifest_path.exists():
                # Load from split files
                self.icon_index = self._load_split_icon_index()
                print(f"Loaded split icon index: {len(self.icon_index.get('icons', {}))} icons")
            else:
                # Load single file
                index_path = self.icons_root / "icon_index.json"
                if index_path.exists():
                    with open(index_path, 'r') as f:
                        self.icon_index = json.load(f)
                    print(f"Loaded icon index: {len(self.icon_index.get('icons', {}))} icons")
            else:
                print(f"Icon index not found: {index_path}")
                self.icon_index = {}

            # Load verified mappings
            verified_path = self.data_dir / "verified_icon_mappings.json"
            if verified_path.exists():
                with open(verified_path, 'r') as f:
                    self.verified_mappings = json.load(f)
                print(f"Loaded verified mappings: {len(self.verified_mappings)} items")
            else:
                print("No verified mappings found (run interactive_icon_mapper.py to create)")
                self.verified_mappings = {}

        except Exception as e:
            print(f"Error loading icon data: {e}")
            self.icon_mapping = {}
            self.icon_index = {}
            self.verified_mappings = {}

    def _load_split_icon_index(self) -> dict:
        """
        Load icon index from split files.

        Returns:
            Combined icon index data with stats and icons
        """
        manifest_path = self.icons_root / "icon_index_manifest.json"

        with open(manifest_path, 'r') as f:
            manifest = json.load(f)

        # Combine all icons from split files
        all_icons = {}

        for file_info in manifest["files"]:
            file_path = self.icons_root / file_info["file"]
            with open(file_path, 'r') as f:
                part_data = json.load(f)
                all_icons.update(part_data["icons"])

        return {
            "stats": manifest["stats"],
            "icons": all_icons
        }

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
                # Special handling for localised fields
                if field_name in ['name', 'description']:
                    localised_value = self.get_localised_text(element, field_name)
                    if localised_value is not None:
                        value = localised_value
                    else:
                        value = getattr(element, field_name)
                else:
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

    def get_last_opened_file(self) -> Optional[str]:
        """Get the last opened file path from settings"""
        return self.settings.value("last_opened_file")

    def get_default_file_path(self) -> str:
        """Get the default file path (last opened or fallback)"""
        last_file = self.get_last_opened_file()
        if last_file and Path(last_file).exists():
            return last_file
        # Fallback to original GameData.cff
        default_path = self.project_root / "OriginalGameFiles" / "data" / "GameData.cff"
        return str(default_path)

    # Icon-related methods

    def get_icon_path(self, category: str, element: Any) -> Optional[str]:
        """
        Get icon path for an element.

        Priority order:
        1. Verified mappings (manually confirmed icons)
        2. Automatic mapping (based on handles)
        3. First non-empty icon from any atlas
        4. Fallback placeholder

        Args:
            category: Category name (e.g., "items", "weapons", "armor")
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

        # PRIORITY 1: Check verified mappings first
        item_id_str = str(element_id)
        if item_id_str in self.verified_mappings:
            # Get primary icon (index 1)
            if '1' in self.verified_mappings[item_id_str]:
                icon_rel_path = self.verified_mappings[item_id_str]['1']
                icon_path = self.icons_root / icon_rel_path
                if icon_path.exists():
                    return str(icon_path)

        # PRIORITY 2: Try automatic mapping based on handle
        handle = None

        # Look up in item_ui table for items/weapons/armor
        if category in ["items", "weapons", "armor"]:
            ui_entry = self._find_item_ui_entry(element_id)
            if ui_entry:
                handle = ui_entry.get("item_ui_handle")

        # Look up in spell_names table for spells
        elif category == "spells":
            spell = self._find_spell_entry(element_id)
            if spell:
                handle = spell.get("spell_ui_handle")

        if handle:
            resolved_path = self._resolve_icon_path(handle, category)
            if resolved_path:
                return resolved_path

        # PRIORITY 3: Try finding first non-empty icon from icon_mapping
        if item_id_str in self.icon_mapping.get('item_to_icons', {}):
            icons = self.icon_mapping['item_to_icons'][item_id_str]
            for icon_data in icons:
                if icon_data.get('index') == 1:  # Primary icon
                    # Try different atlases until we find a non-empty one
                    handle = icon_data.get('handle', '')
                    icon_category = 'itm' if handle and handle.startswith('ui_item_') else \
                                   'spell' if handle and handle.startswith('ui_spell_') else 'item'

                    # Try up to 10 atlases
                    for atlas_num in range(10):
                        icon_path = self.icons_root / icon_category / f"atlas_{atlas_num}" / f"icon_{icon_data['index']:03d}.png"
                        if icon_path.exists():
                            # Check if not empty
                            icon_key = f"{icon_category}_{atlas_num}_{icon_data['index']:03d}"
                            if icon_key in self.icon_index.get('icons', {}):
                                icon_info = self.icon_index['icons'][icon_key]
                                if not icon_info.get('is_empty', False):
                                    return str(icon_path)

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

    def get_localised_text(self, entity: Any, field_name: str) -> Optional[str]:
        """
        Get localised text for an entity field based on current language setting.

        Args:
            entity: The entity object
            field_name: The field name (e.g., 'name', 'description')

        Returns:
            Localised text string or None if not found
        """
        if not self.game_data or not entity:
            return None

        try:
            # Get the text_id from the entity
            text_id_field = None
            if field_name == 'name':
                # Try different possible text_id field names
                for possible_field in ['name_id', 'text_id', 'spell_name_id']:
                    if hasattr(entity, possible_field):
                        text_id = getattr(entity, possible_field)
                        if text_id and text_id != 0:
                            text_id_field = possible_field
                            break
            elif field_name == 'description':
                # For descriptions, try description_id
                if hasattr(entity, 'description_id'):
                    text_id = getattr(entity, 'description_id')
                    if text_id and text_id != 0:
                        text_id_field = 'description_id'

            if text_id_field is None:
                return None

            text_id = getattr(entity, text_id_field)

            # Query localisation table for current language
            localisation_table = self.get_table('localisation')
            if localisation_table:
                for entry in localisation_table:
                    if (getattr(entry, 'text_id', None) == text_id and
                        getattr(entry, 'language', None) == self.current_language):
                        return getattr(entry, 'text', '')

            # Fallback to English if current language not found
            if self.current_language != Language.ENGLISH and localisation_table:
                for entry in localisation_table:
                    if (getattr(entry, 'text_id', None) == text_id and
                        getattr(entry, 'language', None) == Language.ENGLISH):
                        return getattr(entry, 'text', '')

        except Exception as e:
            print(f"Error getting localised text: {e}")

        return None

    def clear_icon_cache(self):
        """Clear the icon cache to free memory."""
        self.icon_cache.clear()
