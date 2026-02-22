"""
Item Loader for GraufurterBuergerBuero
=====================================

Loads items from CFF for merchant inventory selection.
Uses pre-built cache for speed.
"""

import json
import os
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
RUST_LOADER = project_root / "rust_src" / "target" / "release" / "item-loader.exe"
DEFAULT_CFF = project_root / "OriginalGameFiles" / "data" / "GameData.cff"


class ItemLoader:
    def __init__(self, gamedata_path: Optional[str] = None):
        self.gamedata_path = gamedata_path or str(DEFAULT_CFF)
        self.items_cache = None

    def load_all_items(self, force_rebuild: bool = False) -> Dict[int, Dict[str, Any]]:
        if not force_rebuild and CACHE_FILE.exists():
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.items_cache = {int(k): v for k, v in data.items()}
                    return self.items_cache
            except Exception as e:
                print(f"Failed to load cache: {e}")

        if RUST_LOADER.exists():
            try:
                result = subprocess.run(
                    [str(RUST_LOADER), self.gamedata_path],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode == 0:
                    data = json.loads(result.stdout)
                    if "items" in data:
                        items = {}
                        for item in data["items"]:
                            item_id = item["item_id"]
                            items[item_id] = item
                        self.items_cache = items

                        try:
                            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                                json.dump(items, f)
                        except Exception:
                            pass
                        return items
            except Exception as e:
                print(f"Rust loader failed: {e}")

        self.items_cache = self._load_from_python()
        return self.items_cache

    def _load_from_python(self) -> Dict[int, Dict[str, Any]]:
        items = {}
        try:
            from TirganachReloaded.tirganach import GameData

            gamedata = GameData(self.gamedata_path)
            all_items = list(gamedata.items)

            for item in all_items:
                item_id = getattr(item, "item_id", 0)
                if item_id == 0:
                    continue

                items[item_id] = {
                    "item_id": item_id,
                    "name_id": getattr(item, "name_id", 0),
                    "name": getattr(item, "name", f"Item {item_id}"),
                    "item_type": getattr(item, "item_type", 0),
                    "item_subtype": getattr(item, "item_subtype", 0),
                    "selling_price": getattr(item, "selling_price", 0),
                    "buying_price": getattr(item, "buying_price", 0),
                    "item_set_id": getattr(item, "item_set_id", 0),
                    "type_display": ITEM_TYPE_MAP.get(
                        getattr(item, "item_type", 0), "Unknown"
                    ),
                }

            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(items, f)
            except Exception:
                pass

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
