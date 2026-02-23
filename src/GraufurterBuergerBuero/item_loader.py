"""
Item Loader for GraufurterBuergerBuero
=====================================

Loads items from CFF for merchant inventory selection.
Uses caching for speed - first load may be slow, subsequent loads are instant.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

ITEM_TYPE_MAP = {
    0: "Unknown",
    1: "Equipment",
    2: "Inventory Rune",
    3: "Installed Rune",
    4: "Spell Scroll",
    5: "Equipped Scroll",
    6: "Unit Plan",
    7: "Building Plan",
    8: "Equipped Unit Plan",
    9: "Equipped Building Plan",
    10: "Miscellaneous",
}

CACHE_FILE = Path(__file__).parent / "item_cache.json"
DEFAULT_CFF = project_root / "OriginalGameFiles" / "data" / "GameData.cff"
RUST_TOOL_PATH = project_root / "rust_src" / "target" / "release" / "cff-tool.exe"


class ItemLoader:
    def __init__(self, gamedata_path: Optional[str] = None):
        self.gamedata_path = gamedata_path or str(DEFAULT_CFF)
        self.items_cache = None

    def load_all_items(self, force_rebuild: bool = False) -> Dict[int, Dict[str, Any]]:
        # Try to load from cache first
        if not force_rebuild and CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.items_cache = {int(k): v for k, v in data.items()}
                    return self.items_cache
            except Exception as e:
                print(f"Failed to load cache: {e}")

        # Try Rust first, fall back to Python
        items = self._load_from_rust()
        if not items:
            print("Rust tool failed, falling back to Python...")
            items = self._load_from_python()

        # Save to cache for next time
        if items:
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(items, f)
            except Exception as e:
                print(f"Failed to save cache: {e}")

        self.items_cache = items
        return items

    def _load_from_rust(self) -> Dict[int, Dict[str, Any]]:
        """Load items using the Rust CLI tool (much faster)"""
        items = {}

        # Check if Rust tool exists
        if not RUST_TOOL_PATH.exists():
            # Try to build it
            print("Building Rust CFF tool...")
            try:
                result = subprocess.run(
                    ["cargo", "build", "--release"],
                    cwd=str(project_root / "rust_src"),
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if result.returncode != 0:
                    print(f"Failed to build Rust tool: {result.stderr}")
                    return {}
            except Exception as e:
                print(f"Failed to build Rust tool: {e}")
                return {}

        if not RUST_TOOL_PATH.exists():
            return {}

        try:
            print("Loading items from Rust CFF tool...")
            result = subprocess.run(
                [str(RUST_TOOL_PATH), self.gamedata_path, "items"],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                print(f"Rust tool error: {result.stderr}")
                return {}

            # Parse JSON output - find the first { and parse from there
            stdout = result.stdout
            # Find where JSON starts (after any debug output)
            json_start = stdout.find("{")
            data = {}
            if json_start >= 0:
                json_str = stdout[json_start:]
                data = json.loads(json_str)
            item_list = data.get("items", [])

            for item in item_list:
                item_id = item.get("item_id", 0)
                if item_id == 0:
                    continue

                items[item_id] = {
                    "item_id": item_id,
                    "name_id": item.get("name_id", 0),
                    "name": item.get("name", f"Item {item_id}"),
                    "item_type": item.get("item_type", 0),
                    "item_subtype": item.get("item_subtype", 0),
                    "selling_price": item.get("selling_price", 0),
                    "buying_price": item.get("buying_price", 0),
                    "item_set_id": item.get("item_set_id", 0),
                    "type_display": ITEM_TYPE_MAP.get(
                        item.get("item_type", 0), "Unknown"
                    ),
                }

            print(f"Loaded {len(items)} items from Rust")

        except subprocess.TimeoutExpired:
            print("Rust tool timed out")
            return {}
        except Exception as e:
            print(f"Error running Rust tool: {e}")
            return {}

        return items

    def _load_from_python(self) -> Dict[int, Dict[str, Any]]:
        items = {}
        try:
            from TirganachReloaded.tirganach import GameData

            gamedata = GameData(self.gamedata_path)
            all_items = list(gamedata.items)

            print(f"Loading {len(all_items)} items from CFF...")

            for item in all_items:
                try:
                    item_id_raw = getattr(item, "item_id", None)
                    if item_id_raw is None:
                        continue
                    # Handle both int and enum types
                    try:
                        item_id = int(item_id_raw)
                    except (TypeError, ValueError):
                        item_id = (
                            item_id_raw.value if hasattr(item_id_raw, "value") else 0
                        )
                    if item_id == 0:
                        continue

                    item_type_raw = getattr(item, "item_type", None)
                    try:
                        item_type = int(item_type_raw)
                    except (TypeError, ValueError):
                        item_type = (
                            item_type_raw.value
                            if hasattr(item_type_raw, "value")
                            else 0
                        )

                    name_id_raw = getattr(item, "name_id", None)
                    try:
                        name_id = int(name_id_raw)
                    except (TypeError, ValueError):
                        name_id = (
                            name_id_raw.value if hasattr(name_id_raw, "value") else 0
                        )

                    subtype_raw = getattr(item, "item_subtype", None)
                    try:
                        item_subtype = int(subtype_raw)
                    except (TypeError, ValueError):
                        item_subtype = (
                            subtype_raw.value if hasattr(subtype_raw, "value") else 0
                        )

                    items[item_id] = {
                        "item_id": item_id,
                        "name_id": name_id,
                        "name": getattr(item, "name", f"Item {item_id}"),
                        "item_type": item_type,
                        "item_subtype": item_subtype,
                        "selling_price": int(getattr(item, "selling_price", 0)),
                        "buying_price": int(getattr(item, "buying_price", 0)),
                        "item_set_id": int(getattr(item, "item_set_id", 0)),
                        "type_display": ITEM_TYPE_MAP.get(item_type, "Unknown"),
                    }
                except Exception as inner_e:
                    continue

            print(f"Loaded {len(items)} items")

        except Exception as e:
            print(f"Error loading items from Python: {e}")

        return items

    def get_items_by_type(self, item_type: int) -> Dict[int, Dict[str, Any]]:
        if self.items_cache is None:
            self.load_all_items()

        return {
            item_id: item_data
            for item_id, item_data in self.items_cache.items()
            if item_data.get("item_type") == item_type
        }

    def search_items(self, query: str) -> List[Tuple[int, str]]:
        if self.items_cache is None:
            self.load_all_items()

        query_lower = query.lower()
        results = []

        for item_id, item_data in self.items_cache.items():
            name = item_data.get("name", "").lower()
            if query_lower in name or str(item_id).startswith(query):
                results.append((item_id, item_data.get("name", f"Item {item_id}")))

        results.sort(key=lambda x: x[1])
        return results

    def get_item_by_id(self, item_id: int) -> Optional[Dict[str, Any]]:
        if self.items_cache is None:
            self.load_all_items()

        return self.items_cache.get(item_id)

    def get_all_item_names(self) -> List[Tuple[int, str]]:
        if self.items_cache is None:
            self.load_all_items()

        items_list = [
            (item_id, data.get("name", f"Item {item_id}"))
            for item_id, data in self.items_cache.items()
        ]
        items_list.sort(key=lambda x: x[1])
        return items_list


_global_item_loader = None


def get_item_loader() -> ItemLoader:
    global _global_item_loader
    if _global_item_loader is None:
        _global_item_loader = ItemLoader()
    return _global_item_loader


def load_all_items() -> Dict[int, Dict[str, Any]]:
    loader = get_item_loader()
    return loader.load_all_items()
