#!/usr/bin/env python3
"""
MappingResolver - Resolves game data IDs to human-readable names

This utility class loads the ID-to-name mappings extracted from Lua sources
and provides convenient methods for displaying IDs with their names in the editor.

Display format: "Name [ID]" (e.g., "One-handed Sword [4]")
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class MappingResolver:
    """Resolves game data IDs to human-readable names

    Usage:
        resolver = MappingResolver()
        name = resolver.get_display_name(4, "weapon_types")
        # Returns: "One-handed Sword [4]"
    """

    # Field name patterns that should use ID resolution
    ID_FIELD_PATTERNS = [
        "_id",
        "_type",
        "weapon",
        "spell",
        "effect",
        "race",
        "job",
        "task",
        "slot",
        "direction",
        "target",
        "state",
    ]

    # Category mappings for common field names
    FIELD_TO_CATEGORY = {
        "weapon_type": "weapon_types",
        "weapontype": "weapon_types",
        "spell_line": "spell_lines",
        "spellline": "spell_lines",
        "effect_type": "effect_types",
        "effecttype": "effect_types",
        "race": "races",
        "race_id": "races",
        "job_type": "job_types",
        "jobtype": "job_types",
        "task": "figure_tasks",
        "task_type": "figure_tasks",
        "equipment_slot": "equipment_slots",
        "slot": "equipment_slots",
        "direction": "directions",
        "target_type": "target_types",
        "quest_state": "quest_states",
        "state": "quest_states",
        "monument_type": "monument_types",
        "movement_mode": "movement_modes",
    }

    def __init__(self, mappings_file: Optional[str] = None):
        """Initialize the resolver with mapping data

        Args:
            mappings_file: Path to JSON mapping file. If None, uses default location.
        """
        if mappings_file is None:
            # Default location relative to this file
            base_dir = Path(__file__).parent.parent.parent
            mappings_file = base_dir / "data" / "id_name_mappings.json"

        self.mappings_file = Path(mappings_file)
        self.mappings: Dict[str, Dict[str, Any]] = {}
        self.load_mappings()

    def load_mappings(self):
        """Load mappings from JSON file"""
        if not self.mappings_file.exists():
            print(f"⚠️  Warning: Mappings file not found: {self.mappings_file}")
            print("   Run extract_lua_mappings.py to generate it.")
            return

        with open(self.mappings_file, "r", encoding="utf-8") as f:
            self.mappings = json.load(f)

        print(f"✅ Loaded {len(self.mappings)} mapping categories")

    def get_display_name(self, id_value: Any, category: str) -> str:
        """Get display name in format: "Name [ID]"

        Args:
            id_value: The ID value (can be int or string)
            category: Category name (e.g., "weapon_types", "spell_lines")

        Returns:
            Formatted string like "One-handed Sword [4]" or "[Unknown: 999]"
        """
        if category not in self.mappings:
            return f"[{id_value}]"

        # Convert to string for lookup
        id_str = str(id_value)

        if id_str in self.mappings[category]:
            mapping = self.mappings[category][id_str]
            return mapping.get(
                "display", f"{mapping.get('name', 'Unknown')} [{id_value}]"
            )
        else:
            # Try numeric lookup if string didn't work
            try:
                id_int = int(id_value)
                if str(id_int) in self.mappings[category]:
                    mapping = self.mappings[category][str(id_int)]
                    return mapping.get(
                        "display", f"{mapping.get('name', 'Unknown')} [{id_int}]"
                    )
            except (ValueError, TypeError):
                pass

        return f"[Unknown: {id_value}]"

    def get_name_only(self, id_value: Any, category: str) -> str:
        """Get just the name without ID

        Args:
            id_value: The ID value
            category: Category name

        Returns:
            Just the name (e.g., "One-handed Sword") or "Unknown"
        """
        if category not in self.mappings:
            return f"Unknown ({id_value})"

        id_str = str(id_value)
        if id_str in self.mappings[category]:
            return self.mappings[category][id_str].get("name", "Unknown")

        return f"Unknown ({id_value})"

    def get_constant(self, id_value: Any, category: str) -> Optional[str]:
        """Get the constant name (e.g., "kDrwWt1HSword")

        Args:
            id_value: The ID value
            category: Category name

        Returns:
            Constant name or None if not found
        """
        if category not in self.mappings:
            return None

        id_str = str(id_value)
        if id_str in self.mappings[category]:
            return self.mappings[category][id_str].get("constant")

        return None

    def get_full_info(self, id_value: Any, category: str) -> Optional[Dict[str, Any]]:
        """Get complete mapping information

        Args:
            id_value: The ID value
            category: Category name

        Returns:
            Dictionary with all mapping data or None
        """
        if category not in self.mappings:
            return None

        id_str = str(id_value)
        return self.mappings[category].get(id_str)

    def get_all_in_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get all mappings in a category

        Args:
            category: Category name

        Returns:
            Dictionary of all mappings in the category
        """
        return self.mappings.get(category, {})

    def get_dropdown_options(self, category: str) -> List[Tuple[int, str]]:
        """Get list of (id, display_name) tuples for dropdown menus

        Args:
            category: Category name

        Returns:
            List of tuples suitable for populating dropdown menus,
            sorted by ID
        """
        options = []
        category_data = self.mappings.get(category, {})

        for id_str, data in category_data.items():
            try:
                id_int = int(id_str) if id_str.isdigit() else id_str
                display = data.get(
                    "display", f"{data.get('name', 'Unknown')} [{id_str}]"
                )
                options.append((id_int, display))
            except (ValueError, AttributeError):
                continue

        # Sort by ID (numeric first, then by value)
        options.sort(key=lambda x: (isinstance(x[0], str), x[0]))

        return options

    def search_by_name(
        self, search_term: str, category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search for entries by name

        Args:
            search_term: Text to search for (case-insensitive)
            category: Specific category to search, or None for all

        Returns:
            List of matching entries with category info added
        """
        results = []
        search_lower = search_term.lower()

        categories_to_search = [category] if category else self.mappings.keys()

        for cat in categories_to_search:
            if cat not in self.mappings:
                continue

            for id_str, data in self.mappings[cat].items():
                name = data.get("name", "").lower()
                constant = data.get("constant", "").lower()

                if search_lower in name or search_lower in constant:
                    result = data.copy()
                    result["category"] = cat
                    result["id"] = id_str
                    results.append(result)

        return results

    def is_id_field(self, field_name: str) -> bool:
        """Check if a field name should use ID resolution

        Args:
            field_name: Field name to check

        Returns:
            True if this field should display with name resolution
        """
        field_lower = field_name.lower()

        # Check exact matches first
        if field_lower in self.FIELD_TO_CATEGORY:
            return True

        # Check patterns
        for pattern in self.ID_FIELD_PATTERNS:
            if pattern in field_lower:
                return True

        return False

    def guess_category(self, field_name: str) -> Optional[str]:
        """Attempt to guess the category from field name

        Args:
            field_name: Field name

        Returns:
            Category name or None if can't determine
        """
        field_lower = field_name.lower()

        # Check exact mappings
        if field_lower in self.FIELD_TO_CATEGORY:
            return self.FIELD_TO_CATEGORY[field_lower]

        # Try partial matches
        if "weapon" in field_lower:
            return "weapon_types"
        elif "spell" in field_lower:
            return "spell_lines"
        elif "effect" in field_lower:
            return "effect_types"
        elif "race" in field_lower:
            return "races"
        elif "job" in field_lower:
            return "job_types"
        elif "task" in field_lower:
            return "figure_tasks"
        elif "slot" in field_lower or "equipment" in field_lower:
            return "equipment_slots"
        elif "direction" in field_lower:
            return "directions"
        elif "target" in field_lower:
            return "target_types"
        elif "quest" in field_lower or "state" in field_lower:
            return "quest_states"
        elif "monument" in field_lower:
            return "monument_types"

        return None

    def get_available_categories(self) -> List[str]:
        """Get list of all available categories

        Returns:
            List of category names
        """
        return list(self.mappings.keys())

    def get_stats(self) -> Dict[str, int]:
        """Get statistics about loaded mappings

        Returns:
            Dictionary with counts per category
        """
        return {category: len(data) for category, data in self.mappings.items()}


# Convenience singleton instance
_resolver_instance = None


def get_resolver() -> MappingResolver:
    """Get global singleton instance of MappingResolver

    Returns:
        Shared MappingResolver instance
    """
    global _resolver_instance
    if _resolver_instance is None:
        _resolver_instance = MappingResolver()
    return _resolver_instance


if __name__ == "__main__":
    # Test the resolver
    print("=" * 70)
    print("MappingResolver Test")
    print("=" * 70)

    resolver = MappingResolver()

    print("\n📊 Statistics:")
    for category, count in resolver.get_stats().items():
        print(f"  • {category}: {count} entries")

    print("\n🔍 Sample Lookups:")
    print(f"  Weapon ID 4: {resolver.get_display_name(4, 'weapon_types')}")
    print(f"  Race ID 1: {resolver.get_display_name(1, 'races')}")
    print(f"  Effect ID 1: {resolver.get_display_name(1, 'effect_types')}")
    print(f"  Direction ID 0: {resolver.get_display_name(0, 'directions')}")

    print("\n🔎 Search Test:")
    results = resolver.search_by_name("sword", "weapon_types")
    for result in results:
        print(f"  • Found: {result['name']} (ID: {result['id']})")

    print("\n✨ Test complete!")
