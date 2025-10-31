"""
Data Model for CFF Editor
Manages loaded GameData and provides interface for GUI
"""

import hashlib
import json
import os
import pickle
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from pathlib import Path
from typing import Any, Dict, List, Optional

from PySide6.QtCore import QObject, QSettings, Signal
from PySide6.QtGui import QIcon, QPixmap
from tirganach import GameData
from tirganach.types import *

# Import Lua data manager for quest scripts
try:
    from .lua_parser.lua_data_manager import LuaDataManager

    LUA_MANAGER_AVAILABLE = True
except ImportError:
    LUA_MANAGER_AVAILABLE = False
    LuaDataManager = None

# Cache version for invalidation when cache format changes
CACHE_VERSION = "1.0.0"

# Try to import data providers
try:
    import cff_editor.data_providers as dp

    DATA_PROVIDERS_AVAILABLE = True
except ImportError:
    DATA_PROVIDERS_AVAILABLE = False
    dp = None

# Data providers will be imported when needed


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
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.ui_assets_dir = self.project_root / "ExtractedAssets" / "UI" / "extracted"
        self.icons_root = (
            self.project_root / "ExtractedAssets" / "UI" / "icons_extracted"
        )
        self.data_dir = self.project_root / "src" / "TirganachReloaded" / "data"

        # Load icon mappings and analysis data
        self.icon_mapping = {}
        self.icon_index = {}
        self.verified_mappings = {}
        self._load_icon_data()

        # Settings for remembering last opened file and language
        self.settings = QSettings("SpellSmut", "TirganachReloaded")
        self.current_language = self._load_language_setting()

        # Cache directory
        self.cache_dir = (
            self.project_root / "src" / "TirganachReloaded" / "data" / "cache"
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Database directory
        self.db_dir = self.cache_dir / "db"
        self.db_dir.mkdir(parents=True, exist_ok=True)

        # Data providers (for future use)
        self.data_provider: Optional[Any] = None
        self.use_db_provider = False  # Flag to enable DB provider

        # Localisation index for fast lookups
        self.localisation_index = None
        self.localisation_index_language = None

        # Advanced descriptions index for fast lookups
        self.advanced_descriptions_index = None

        # Lua data manager for quest scripts
        self.lua_data_manager = None
        self.lua_quest_directory = None
        if LUA_MANAGER_AVAILABLE:
            lua_cache_dir = self.cache_dir / "lua_cache"
            self.lua_data_manager = LuaDataManager(cache_dir=lua_cache_dir)

    def _load_language_setting(self) -> Language:
        """Load current language from settings, default to ENGLISH"""
        language_value = self.settings.value(
            "current_language", 1
        )  # Default to ENGLISH (1)
        try:
            return Language(language_value)
        except ValueError:
            return Language.ENGLISH

    def _generate_fingerprint(self, file_path: str) -> str:
        """Generate a fingerprint for cache validation"""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file stats
        stat = path.stat()
        file_size = stat.st_size
        mtime = stat.st_mtime

        # Calculate partial SHA-256 of first 32MB
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            # Read first 32MB or entire file if smaller
            chunk_size = 32 * 1024 * 1024  # 32MB
            data = f.read(chunk_size)
            sha256.update(data)

        # Combine all components
        fingerprint_data = {
            "path": str(path.absolute()),
            "size": file_size,
            "mtime": mtime,
            "sha256_partial": sha256.hexdigest(),
            "cache_version": CACHE_VERSION,
        }

        # Create final fingerprint hash
        fingerprint_str = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()

    def _get_cache_paths(self, fingerprint: str) -> tuple[Path, Path]:
        """Get cache file paths for a given fingerprint"""
        cache_file = self.cache_dir / f"GameData_{fingerprint}.pkl"
        meta_file = self.cache_dir / f"GameData_{fingerprint}.meta.json"
        return cache_file, meta_file

    def _load_from_cache(
        self, fingerprint: str
    ) -> tuple[Optional[GameData], Optional[str]]:
        """Load GameData from cache if valid

        Returns:
            tuple: (game_data, reason_for_failure)
            - game_data: GameData object if cache is valid, None otherwise
            - reason_for_failure: string describing why cache was invalid, None if valid
        """
        try:
            cache_file, meta_file = self._get_cache_paths(fingerprint)

            if not cache_file.exists() or not meta_file.exists():
                return None, "Cache files not found"

            # Load and validate metadata
            with open(meta_file, "r") as f:
                meta = json.load(f)

            cached_version = meta.get("cache_version")
            if cached_version != CACHE_VERSION:
                return (
                    None,
                    f"Cache version mismatch: {cached_version} → {CACHE_VERSION}",
                )

            # Load pickled data
            with open(cache_file, "rb") as f:
                game_data = pickle.load(f)

            return game_data, None

        except Exception as e:
            return None, f"Cache load error: {str(e)}"

    def _save_to_cache(self, game_data: GameData, fingerprint: str, source_path: str):
        """Save GameData to cache"""
        cache_file, meta_file = None, None
        try:
            cache_file, meta_file = self._get_cache_paths(fingerprint)

            # Save metadata
            meta = {
                "cache_version": CACHE_VERSION,
                "source_path": source_path,
                "created_at": time.time(),
                "fingerprint": fingerprint,
            }

            with open(meta_file, "w") as f:
                json.dump(meta, f, indent=2)

            # Save pickled data
            with open(cache_file, "wb") as f:
                pickle.dump(game_data, f)

        except PermissionError as e:
            cache_dir = cache_file.parent if cache_file else self.cache_dir
            print(f"Permission denied saving cache to {cache_dir}: {e}")
            print("Cache will not be available for future loads")
        except OSError as e:
            print(f"OS error saving cache: {e}")
            print("Cache will not be available for future loads")
        except Exception as e:
            print(f"Unexpected error saving cache: {e}")
            print("Cache will not be available for future loads")

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

    def load_file(self, file_path: str, force_parse: bool = False) -> bool:
        """Load a CFF file, using cache when possible"""
        try:
            path = Path(file_path)
            if not path.exists():
                print(f"File not found: {file_path}")
                return False

            # Generate fingerprint for cache validation
            fingerprint = self._generate_fingerprint(file_path)

            # Try DB provider if enabled
            if self.use_db_provider and DATA_PROVIDERS_AVAILABLE and dp:
                db_path = str(self.db_dir / "cff_data.db")
                db_manager = dp.DatabaseManager(db_path)

                if not force_parse:
                    is_valid, db_failure_reason = db_manager.is_valid_for_fingerprint(
                        fingerprint
                    )
                    if is_valid:
                        # Database is valid, use DB provider
                        self.data_provider = dp.DBProvider(db_path)
                        if self.data_provider.is_loaded():
                            self.game_data = None  # Not needed for DB provider
                            self.file_path = file_path
                            self.modified = False

                            # Load mappings
                            self._load_weapon_names()
                            self._load_armor_names()

                            # Save as last opened file
                            self.settings.setValue("last_opened_file", file_path)

                            # Build indices for faster lookups
                            self._build_localisation_index()
                            self._build_advanced_descriptions_index()

                            self.data_loaded.emit()
                            return True
                    elif db_failure_reason:
                        print(f"Database rebuild triggered: {db_failure_reason}")

                # Need to rebuild database - first load CFF data
                self.game_data = GameData(file_path)
                db_manager.create_schema()
                db_manager.populate_from_cff(self.game_data, fingerprint)
                self.data_provider = dp.DBProvider(db_path)

                self.file_path = file_path
                self.modified = False

                # Load mappings
                self._load_weapon_names()
                self._load_armor_names()

                # Save as last opened file
                self.settings.setValue("last_opened_file", file_path)

                # Build indices for faster lookups
                self._build_localisation_index()
                self._build_advanced_descriptions_index()

                self.data_loaded.emit()
                return True

            # Try to load from cache unless force_parse is True
            if not force_parse:
                cached_data, cache_failure_reason = self._load_from_cache(fingerprint)
                if cached_data is not None:
                    self.game_data = cached_data
                    self.file_path = file_path
                    self.modified = False

                    # Load mappings
                    self._load_weapon_names()
                    self._load_armor_names()

                    # Save as last opened file
                    self.settings.setValue("last_opened_file", file_path)

                    # Build indices for faster lookups
                    self._build_localisation_index()
                    self._build_advanced_descriptions_index()

                    self.data_loaded.emit()
                    return True
                elif cache_failure_reason:
                    print(f"Cache rebuild triggered: {cache_failure_reason}")

            # Parse from file (cache miss or force_parse)
            self.game_data = GameData(file_path)
            self.file_path = file_path
            self.modified = False

            # Save to cache for future use
            self._save_to_cache(self.game_data, fingerprint, file_path)

            # Load mappings
            self._load_weapon_names()
            self._load_armor_names()

            # Build indices for faster lookups
            self._build_localisation_index()
            self._build_advanced_descriptions_index()

            # Save as last opened file
            self.settings.setValue("last_opened_file", file_path)
            self.data_loaded.emit()
            return True

        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return False
        except PermissionError:
            print(f"Permission denied accessing file: {file_path}")
            return False
        except Exception as e:
            error_msg = f"Failed to load CFF file '{file_path}': {str(e)}"
            print(error_msg)
            # Could emit an error signal here for UI feedback
            return False

            if self.use_db_provider and DATA_PROVIDERS_AVAILABLE and dp:
                # Try to use database provider
                db_path = str(self.db_dir / "cff_data.db")
                db_manager = dp.DatabaseManager(db_path)

                if not force_parse:
                    is_valid, db_failure_reason = db_manager.is_valid_for_fingerprint(
                        fingerprint
                    )
                    if is_valid:
                        # Database is valid, use DB provider
                        self.data_provider = dp.DBProvider(db_path)
                        if self.data_provider.is_loaded():
                            self.game_data = None  # Not needed for DB provider
                        self.file_path = file_path
                        self.modified = False

                        # Load mappings
                        self._load_weapon_names()
                        self._load_armor_names()

                        # Save as last opened file
                        self.settings.setValue("last_opened_file", file_path)
                        self.data_loaded.emit()
                        return True
                    elif db_failure_reason:
                        print(f"Database rebuild triggered: {db_failure_reason}")

                # Need to rebuild database
                self.game_data = GameData(file_path)
                db_manager.create_schema()
                db_manager.populate_from_cff(self.game_data, fingerprint)
                self.data_provider = dp.DBProvider(db_path)

            else:
                # Use CFF provider (with pickle cache)
                # Try to load from cache unless force_parse is True
                if not force_parse:
                    cached_data, cache_failure_reason = self._load_from_cache(
                        fingerprint
                    )
                    if cached_data is not None:
                        self.game_data = cached_data
                        if DATA_PROVIDERS_AVAILABLE and dp:
                            self.data_provider = dp.CFFProvider(cached_data)
                        self.file_path = file_path
                        self.modified = False

                        # Load mappings
                        self._load_weapon_names()
                        self._load_armor_names()

                        # Save as last opened file
                        self.settings.setValue("last_opened_file", file_path)
                        self.data_loaded.emit()
                        return True
                    elif cache_failure_reason:
                        print(f"Cache rebuild triggered: {cache_failure_reason}")

                # Parse from file (cache miss or force_parse)
                self.game_data = GameData(file_path)
                if DATA_PROVIDERS_AVAILABLE and dp:
                    self.data_provider = dp.CFFProvider(self.game_data)

                # Save to cache for future use
                self._save_to_cache(self.game_data, fingerprint, file_path)

            self.file_path = file_path
            self.modified = False

            # Load mappings
            self._load_weapon_names()
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
                with open(weapons_json_path, "r", encoding="utf-8") as f:
                    weapons_data = json.load(f)

                # Create mapping from item_id to name
                self.weapon_name_mapping = {}
                for weapon in weapons_data:
                    item_id = weapon.get("item_id")
                    name = weapon.get("name")
                    if item_id is not None and name:
                        self.weapon_name_mapping[item_id] = name

                print(f"Loaded {len(self.weapon_name_mapping)} weapon names")
            else:
                print(
                    "enhanced_weapons.json not found, weapon names will not be available"
                )
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
                with open(armor_json_path, "r", encoding="utf-8") as f:
                    armor_data = json.load(f)

                # Create mapping from item_id to name
                self.armor_name_mapping = {}

                # Handle both old format (list) and new format (dict with 'armors' key)
                if isinstance(armor_data, dict) and "armors" in armor_data:
                    armors_list = armor_data["armors"]
                elif isinstance(armor_data, list):
                    armors_list = armor_data
                else:
                    print("Unexpected armor data format")
                    armors_list = []

                for armor in armors_list:
                    # Try both 'item_id' and 'id' fields
                    item_id = armor.get("item_id") or armor.get("id")
                    name = armor.get("name")
                    if item_id is not None and name:
                        self.armor_name_mapping[item_id] = name

                print(f"Loaded {len(self.armor_name_mapping)} armor names")
            else:
                print(
                    "enhanced_armor.json not found, armor names will not be available"
                )
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
                with open(mapping_path, "r") as f:
                    self.icon_mapping = json.load(f)
                print(
                    f"Loaded icon mapping: {len(self.icon_mapping.get('item_to_icons', {}))} items"
                )
            else:
                print(f"Icon mapping not found: {mapping_path}")
                self.icon_mapping = {}

            # Load icon index (check for split files first)
            manifest_path = self.icons_root / "icon_index_manifest.json"
            if manifest_path.exists():
                # Load from split files
                self.icon_index = self._load_split_icon_index()
                print(
                    f"Loaded split icon index: {len(self.icon_index.get('icons', {}))} icons"
                )
            else:
                # Load single file
                index_path = self.icons_root / "icon_index.json"
                if index_path.exists():
                    with open(index_path, "r") as f:
                        self.icon_index = json.load(f)
                    print(
                        f"Loaded icon index: {len(self.icon_index.get('icons', {}))} icons"
                    )
                else:
                    print(f"Icon index not found: {index_path}")
                    self.icon_index = {}

            # Load verified mappings
            verified_path = self.data_dir / "verified_icon_mappings.json"
            if verified_path.exists():
                with open(verified_path, "r") as f:
                    self.verified_mappings = json.load(f)
                print(f"Loaded verified mappings: {len(self.verified_mappings)} items")
            else:
                print(
                    "No verified mappings found (run interactive_icon_mapper.py to create)"
                )
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

        with open(manifest_path, "r") as f:
            manifest = json.load(f)

        # Combine all icons from split files
        all_icons = {}

        for file_info in manifest["files"]:
            file_path = self.icons_root / file_info["file"]
            with open(file_path, "r") as f:
                part_data = json.load(f)
                all_icons.update(part_data["icons"])

        return {"stats": manifest["stats"], "icons": all_icons}

    def get_categories(self) -> List[tuple]:
        """Returns list of (category_name, count) tuples"""
        if not self.game_data:
            return []

        categories = []
        for table_name, table_type in self.game_data.table_info().items():
            table = getattr(self.game_data, table_name)
            count = len(table)
            # Make name more readable
            display_name = table_name.replace("_", " ").title()
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
                # Special handling for text fields that might be Relations
                if field_name == "name":
                    value = self.safe_get_text_field(element, "name")
                    if value is None:
                        value = "[No name]"
                elif field_name == "description":
                    value = self.safe_get_text_field(element, "description")
                    if value is None:
                        value = "[No description]"
                else:
                    # For other fields, get the value normally
                    # Skip if it's a known Relation field that would be slow
                    field_info = element._fields[field_name]
                    field_type_str = str(field_info) if field_info else ""

                    # Skip complex Relation fields (lists, nested objects)
                    if "Relation" in field_type_str and (
                        "list" in field_type_str.lower()
                        or "multiple" in field_type_str.lower()
                    ):
                        value = "[Complex Relation - not displayed]"
                    else:
                        value = getattr(element, field_name)

                field_info = element._fields[field_name]
                fields.append((field_name, value, field_info))
            except Exception as e:
                fields.append((field_name, f"[Error: {e}]", None))

        return fields

    def update_element_field(
        self, category: str, index: int, field_name: str, new_value: Any
    ) -> bool:
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

        # Map table names to icon category names
        category_mapping = {
            "spells": "spell",  # spells table -> spell icons
            "items": "item",  # items table -> item icons
            # Add more mappings as needed
        }
        icon_category = category_mapping.get(category, category)

        # Get element ID based on category
        element_id = self._get_element_id(category, element)
        if element_id is None:
            return None

        # PRIORITY 1: Check verified mappings first
        item_id_str = str(element_id)
        if item_id_str in self.verified_mappings:
            # Get primary icon (index 1)
            if "1" in self.verified_mappings[item_id_str]:
                icon_rel_path = self.verified_mappings[item_id_str]["1"]
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
            resolved_path = self._resolve_icon_path(handle, icon_category)
            if resolved_path:
                return resolved_path

        # PRIORITY 3: Try finding first non-empty icon from icon_mapping
        if item_id_str in self.icon_mapping.get("item_to_icons", {}):
            icons = self.icon_mapping["item_to_icons"][item_id_str]
            for icon_data in icons:
                if icon_data.get("index") == 1:  # Primary icon
                    # Try different atlases until we find a non-empty one
                    handle = icon_data.get("handle", "")
                    # Use the already mapped icon_category, but determine the subdirectory
                    icon_subdir = (
                        "itm"
                        if handle and handle.startswith("ui_item_")
                        else "spell"
                        if handle and handle.startswith("ui_spell_")
                        else "item"
                    )

                    # Try up to 10 atlases
                    for atlas_num in range(10):
                        icon_path = (
                            self.icons_root
                            / icon_subdir
                            / f"atlas_{atlas_num}"
                            / f"icon_{icon_data['index']:03d}.png"
                        )
                        if icon_path.exists():
                            # Check if not empty
                            icon_key = (
                                f"{icon_subdir}_{atlas_num}_{icon_data['index']:03d}"
                            )
                            if icon_key in self.icon_index.get("icons", {}):
                                icon_info = self.icon_index["icons"][icon_key]
                                if not icon_info.get("is_empty", False):
                                    return str(icon_path)

        return None

    def get_icon_pixmap(
        self, category: str, element: Any, size=(64, 64)
    ) -> Optional[QPixmap]:
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
            if hasattr(element, "_index"):
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
                    if (
                        getattr(entry, "item_id", None) == item_id
                        and getattr(entry, "item_ui_index", None) == 1
                    ):
                        return {
                            "item_id": getattr(entry, "item_id", 0),
                            "item_ui_index": getattr(entry, "item_ui_index", 0),
                            "item_ui_handle": getattr(entry, "item_ui_handle", ""),
                            "scaled_down": getattr(entry, "scaled_down", 0),
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
                        # Get the UI handle from the spell data
                        ui_handle = getattr(spell, "spell_ui_handle", "")

                        # If spell_ui_handle is empty, try to look it up in the icon mapping
                        if not ui_handle and self.icon_mapping:
                            item_to_icons = self.icon_mapping.get("item_to_icons", {})
                            spell_id_str = str(spell_id)
                            if spell_id_str in item_to_icons:
                                icons = item_to_icons[spell_id_str]
                                if icons and len(icons) > 0:
                                    # Prefer spell handles over item handles
                                    for icon in icons:
                                        handle = icon.get("handle", "")
                                        if handle.startswith("ui_spell_"):
                                            ui_handle = handle
                                            break
                                    # If no spell handle found, use the first icon as fallback
                                    if not ui_handle:
                                        ui_handle = icons[0].get("handle", "")

                        return {
                            "spell_id": getattr(spell, "spell_id", 0),
                            "spell_name_id": getattr(spell, "spell_name_id", 0),
                            "spell_ui_handle": ui_handle,
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

        # For spell category, handle different types of handles
        if category == "spell":
            # If it's a spell handle, look in spell directories
            if handle.startswith("ui_spell_"):
                # Look up in our verified icon mapping
                # The mapping provides detailed paths for spell handles
                if self.icon_mapping and "detailed_mapping" in self.icon_mapping:
                    detailed = self.icon_mapping["detailed_mapping"]
                    # Look for exact handle match
                    for mapping_key, mapping_data in detailed.items():
                        if mapping_data.get("handle") == handle:
                            # Found exact match, try the mapped path
                            icon_path = self.icons_root / mapping_data["path"]
                            if icon_path.exists():
                                return str(icon_path)

                            # Try alternative paths if primary doesn't exist
                            if "alternatives" in mapping_data:
                                for alt_path in mapping_data["alternatives"]:
                                    alt_icon_path = self.icons_root / alt_path
                                    if alt_icon_path.exists():
                                        return str(alt_icon_path)

                # Fallback: Use handle-based selection from available spell icons
                spell_icons_root = self.icons_root / "spell"
                if spell_icons_root.exists():
                    # Get all available spell icon files
                    all_spell_icons = []
                    for atlas_num in range(18):
                        atlas_dir = spell_icons_root / f"atlas_{atlas_num}"
                        if atlas_dir.exists():
                            for icon_idx in range(1, 17):
                                icon_file = atlas_dir / f"icon_{icon_idx:03d}.png"
                                if icon_file.exists():
                                    all_spell_icons.append(icon_file)

                    if all_spell_icons:
                        # Use hash of handle to deterministically select an icon
                        import hashlib

                        hash_obj = hashlib.md5(handle.encode("utf-8"))
                        hash_int = int(hash_obj.hexdigest(), 16)
                        selected_index = hash_int % len(all_spell_icons)
                        return str(all_spell_icons[selected_index])

            # If it's an item handle (like ui_item_spellscroll), resolve as item icon
            elif handle.startswith("ui_item_"):
                return self._resolve_icon_path(handle, "item")

        # For other categories, use the mapping approach
        # Fall back to mapping numbered files
        # Use a hash of the handle to map to available numbered files
        import hashlib

        hash_obj = hashlib.md5(handle.encode("utf-8"))
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
            "spell": "ui_spell_unknown.png",
        }

        fallback_file = fallback_files.get(category, "ui_unknown.png")
        fallback_path = fallback_dir / fallback_file

        if fallback_path.exists():
            pixmap = QPixmap(str(fallback_path))
            if not pixmap.isNull():
                pixmap = pixmap.scaled(size[0], size[1])
                return pixmap

        return None

    def _build_localisation_index(self):
        """Build an index of localisation entries by text_id for fast O(1) lookups"""
        if not self.game_data:
            return

        try:
            localisation_table = self.get_table("localisation")
            if not localisation_table:
                return

            # Build index: {language: {text_id: text}}
            self.localisation_index = {}

            for entry in localisation_table:
                language = getattr(entry, "language", None)
                text_id = getattr(entry, "text_id", None)
                text = getattr(entry, "text", "")

                if language is not None and text_id is not None:
                    if language not in self.localisation_index:
                        self.localisation_index[language] = {}
                    self.localisation_index[language][text_id] = text

            self.localisation_index_language = self.current_language

        except Exception as e:
            print(f"Error building localisation index: {e}")
            self.localisation_index = None

    def _build_advanced_descriptions_index(self):
        """Build an index of advanced descriptions by description_id for fast O(1) lookups"""
        if not self.game_data:
            return

        try:
            descriptions_table = self.get_table("advanced_descriptions")
            if not descriptions_table:
                return

            # Build index: {description_id: text}
            self.advanced_descriptions_index = {}

            for entry in descriptions_table:
                description_id = getattr(entry, "description_id", None)
                text = getattr(entry, "text", "")

                if description_id is not None:
                    self.advanced_descriptions_index[description_id] = text

        except Exception as e:
            print(f"Error building advanced descriptions index: {e}")
            self.advanced_descriptions_index = None

    def get_localised_text(self, entity: Any, field_name: str) -> Optional[str]:
        """
        Get localised text for an entity field based on current language setting.

        Args:
            entity: The entity object
            field_name: The field name (e.g., 'name', 'description')

        Returns:
            Localised text string or None if not found
        """
        # Try data provider first (for DB provider)
        if self.data_provider and hasattr(self.data_provider, "get_localised_text"):
            try:
                # Get the text_id from the entity
                text_id = None
                if field_name == "name":
                    # Try different possible text_id field names
                    for possible_field in ["name_id", "text_id", "spell_name_id"]:
                        if hasattr(entity, possible_field):
                            text_id = getattr(entity, possible_field)
                            if text_id and text_id != 0:
                                break
                elif field_name == "description":
                    # For descriptions, try description_id
                    if hasattr(entity, "description_id"):
                        text_id = getattr(entity, "description_id")

                if text_id:
                    return self.data_provider.get_localised_text(
                        text_id, self.current_language
                    )
            except Exception:
                pass  # Fall back to CFF method

        # Fall back to original CFF method with indexed lookups
        if not self.game_data or not entity:
            return None

        try:
            # Build index if not already built or language changed
            if (
                self.localisation_index is None
                or self.localisation_index_language != self.current_language
            ):
                self._build_localisation_index()

            # Get the text_id from the entity
            text_id = None
            if field_name == "name":
                # Try different possible text_id field names
                for possible_field in ["name_id", "text_id", "spell_name_id"]:
                    if hasattr(entity, possible_field):
                        text_id = getattr(entity, possible_field)
                        if text_id and text_id != 0:
                            break
            elif field_name == "description":
                # For descriptions, try description_id
                if hasattr(entity, "description_id"):
                    text_id = getattr(entity, "description_id")

            if text_id is None or text_id == 0:
                return None

            # Fast O(1) lookup using index
            if (
                self.localisation_index
                and self.current_language in self.localisation_index
            ):
                if text_id in self.localisation_index[self.current_language]:
                    return self.localisation_index[self.current_language][text_id]

            # Fallback to English if current language not found
            if (
                self.current_language != Language.ENGLISH
                and self.localisation_index
                and Language.ENGLISH in self.localisation_index
            ):
                if text_id in self.localisation_index[Language.ENGLISH]:
                    return self.localisation_index[Language.ENGLISH][text_id]

        except (AttributeError, KeyError, TypeError) as e:
            print(f"Error getting localised text: {e}")

        return None

    def safe_get_text_field(self, entity: Any, field_name: str) -> Optional[str]:
        """
        Safely get a text field without triggering expensive Relation lookups.

        This method checks if the field is a known Relation field and uses indexed
        lookups instead of direct field access.

        Args:
            entity: The entity object
            field_name: The field name (e.g., 'name', 'description')

        Returns:
            Text string or None if not found
        """
        if not entity:
            return None

        # Handle known Relation fields with indexed lookups
        if field_name == "name":
            return self.get_localised_text(entity, "name")
        elif field_name == "description":
            # Check if it's an advanced description (quests use this)
            if hasattr(entity, "description_id"):
                return self.get_advanced_description(entity)
            # Otherwise try regular description
            return self.get_localised_text(entity, "description")

        # For other fields, check if they exist and are not Relations
        if hasattr(entity, field_name):
            value = getattr(entity, field_name, None)
            # Check if it's already a simple type (not a Relation object)
            if value is not None and isinstance(value, (str, int, float, bool)):
                return str(value)

        return None

    def get_advanced_description(self, entity: Any) -> Optional[str]:
        """
        Get advanced description text for an entity.

        Args:
            entity: The entity object with description_id field

        Returns:
            Description text string or None if not found
        """
        if not self.game_data or not entity:
            return None

        try:
            # Build index if not already built
            if self.advanced_descriptions_index is None:
                self._build_advanced_descriptions_index()

            # Get description_id from entity
            description_id = getattr(entity, "description_id", None)
            if description_id is None or description_id == 0:
                return None

            # Fast O(1) lookup using index
            if (
                self.advanced_descriptions_index
                and description_id in self.advanced_descriptions_index
            ):
                return self.advanced_descriptions_index[description_id]

        except (AttributeError, KeyError, TypeError) as e:
            print(f"Error getting advanced description: {e}")

        return None

    def enable_db_provider(self, enabled: bool = True):
        """Enable or disable database provider for faster queries"""
        self.use_db_provider = enabled
        if enabled and self.file_path:
            # Reload with DB provider
            self.load_file(self.file_path, force_parse=True)

    def get_quests_from_provider(self):
        """Get quests using data provider (for DB optimization)"""
        if self.data_provider and hasattr(self.data_provider, "get_quests"):
            try:
                return self.data_provider.get_quests()
            except Exception:
                pass  # Fall back to table method
        return None

    def get_quest_dialogs_from_provider(self, quest_id: int):
        """Get quest dialogs using data provider (for DB optimization)"""
        if self.data_provider and hasattr(self.data_provider, "get_quest_dialogs"):
            try:
                return self.data_provider.get_quest_dialogs(quest_id)
            except Exception:
                pass  # Fall back to table method
        return None

    def clear_icon_cache(self):
        """Clear the icon cache to free memory."""
        self.icon_cache.clear()

    def invalidate_localisation_index(self):
        """Invalidate the localisation index (call when language changes or data reloads)"""
        self.localisation_index = None
        self.localisation_index_language = None
        self.advanced_descriptions_index = None

    def get_element_name_safe(self, element: Any) -> str:
        """
        Safely get an element's name without triggering Relations.
        This is a convenience wrapper around safe_get_text_field with fallbacks.

        Args:
            element: The element object

        Returns:
            Element name as string, with intelligent fallbacks
        """
        if not element:
            return "Unknown"

        # Try localised name first (fast indexed lookup)
        name = self.safe_get_text_field(element, "name")
        if name:
            return name

        # Try common simple name fields (not Relations)
        simple_name_fields = [
            "item_name",
            "spell_name",
            "creature_name",
            "building_name",
            "map_handle",
            "npc_name",
        ]
        for field in simple_name_fields:
            if hasattr(element, field):
                value = getattr(element, field, None)
                if value and isinstance(value, str) and value != "":
                    return value

        # Fallback: construct name from ID fields
        id_fields = [
            "quest_id",
            "item_id",
            "spell_id",
            "creature_id",
            "building_id",
            "npc_id",
            "object_id",
            "id",
        ]
        for field in id_fields:
            if hasattr(element, field):
                value = getattr(element, field, None)
                if value is not None and value != 0:
                    entity_type = field.replace("_id", "").replace("_", " ").title()
                    return f"{entity_type} {value}"

        return "Unknown"

    def clear_db_cache(self):
        """Clear database cache files"""
        if self.db_dir.exists():
            import shutil

            try:
                shutil.rmtree(self.db_dir)
                self.db_dir.mkdir(parents=True, exist_ok=True)
                print("Database cache cleared")
            except Exception as e:
                print(f"Error clearing database cache: {e}")

    def get_cache_info(self) -> dict:
        """Get information about cache usage"""
        info = {
            "pickle_cache": {"files": 0, "size": 0},
            "db_cache": {"files": 0, "size": 0},
        }

        # Count pickle cache files
        if self.cache_dir.exists():
            for file in self.cache_dir.glob("GameData_*.pkl"):
                info["pickle_cache"]["files"] += 1
                info["pickle_cache"]["size"] += file.stat().st_size

        # Count DB cache files
        if self.db_dir.exists():
            for file in self.db_dir.glob("*.db"):
                info["db_cache"]["files"] += 1
                info["db_cache"]["size"] += file.stat().st_size

        return info

    # Lua Quest Data Methods

    def set_lua_quest_directory(self, lua_dir: Path):
        """Set the directory containing Lua quest scripts"""
        if not LUA_MANAGER_AVAILABLE:
            print("Warning: Lua data manager not available")
            return False

        self.lua_quest_directory = Path(lua_dir)
        if not self.lua_quest_directory.exists():
            print(f"Warning: Lua quest directory not found: {lua_dir}")
            return False

        return True

    def load_lua_quest_data(self, force_refresh: bool = False) -> int:
        """
        Load quest data from Lua scripts

        Args:
            force_refresh: If True, reparse all Lua files

        Returns:
            Number of quests parsed, or 0 if failed
        """
        if not LUA_MANAGER_AVAILABLE or not self.lua_data_manager:
            print("Warning: Lua data manager not available")
            return 0

        if not self.lua_quest_directory:
            print(
                "Warning: Lua quest directory not set. Use set_lua_quest_directory() first"
            )
            return 0

        try:
            count = self.lua_data_manager.parse_lua_directory(
                self.lua_quest_directory, force_refresh=force_refresh
            )
            print(f"Loaded Lua data for {count} quests")
            return count
        except Exception as e:
            print(f"Error loading Lua quest data: {e}")
            return 0

    def get_lua_quest_data(self, quest_id: int):
        """
        Get Lua quest data for a specific quest ID

        Returns:
            QuestData object or None if not found
        """
        if not LUA_MANAGER_AVAILABLE or not self.lua_data_manager:
            return None

        try:
            return self.lua_data_manager.get_quest_data(quest_id)
        except Exception as e:
            print(f"Error getting Lua quest data for quest {quest_id}: {e}")
            return None

    def has_lua_data(self) -> bool:
        """Check if Lua data is available and loaded"""
        if not LUA_MANAGER_AVAILABLE or not self.lua_data_manager:
            print("[DEBUG] Lua manager not available")
            return False

        cache_loaded = self.lua_data_manager.cache_loaded
        cache_size = len(self.lua_data_manager.quest_cache)
        has_data = cache_loaded and cache_size > 0

        print(
            f"[DEBUG] has_lua_data check: cache_loaded={cache_loaded}, cache_size={cache_size}, has_data={has_data}"
        )

        return has_data

    def get_all_lua_quest_ids(self) -> List[int]:
        """Get all quest IDs that have Lua data"""
        if not LUA_MANAGER_AVAILABLE or not self.lua_data_manager:
            return []

        try:
            return list(self.lua_data_manager.quest_cache.keys())
        except Exception:
            return []
