"""
Example: Using GameData.json
=============================

This script demonstrates how to load and query the exported GameData.json file.
Much faster than loading the .cff file directly!

Usage:
    python example_use_json.py
"""

import json
from pathlib import Path


def load_gamedata():
    """Load the GameData.json file"""
    json_path = Path(__file__).parent / "GameData.json"

    if not json_path.exists():
        print("❌ GameData.json not found!")
        print("   Run: python export_to_json.py")
        return None

    print(f"Loading {json_path}...")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("✅ Loaded successfully!")
    return data


def print_summary(data):
    """Print summary statistics"""
    print("\n" + "=" * 80)
    print("GameData Summary")
    print("=" * 80)

    summary = data["_summary"]
    for key, value in summary.items():
        label = key.replace("total_", "").replace("_", " ").title()
        print(f"  {label:.<30} {value:>10,}")


def find_spells_by_school(data, school_name="FIRE", min_level=1, max_level=5):
    """Find all spells from a specific school and level range"""
    print(f"\n🔥 Fire Spells (Level {min_level}-{max_level}):")
    print("=" * 80)

    spells = data["spells"]
    matching = []

    for spell in spells:
        req1 = spell.get("req1_class", {})
        if isinstance(req1, dict) and req1.get("name") == school_name:
            level = spell.get("req1_level", 0)
            if min_level <= level <= max_level:
                matching.append(spell)

    print(f"Found {len(matching)} spells")

    # Show first 5
    for spell in matching[:5]:
        spell_id = spell["spell_id"]
        mana = spell["mana"]
        cast_time = spell["cast_time"]
        cooldown = spell["cooldown"]
        print(
            f"  Spell #{spell_id:>4} | Mana: {mana:>3} | Cast: {cast_time:>4}ms | CD: {cooldown:>4}ms"
        )


def find_powerful_items(data, min_stats=100):
    """Find items with high stat bonuses"""
    print(f"\n⚔️  Powerful Armor (stats > {min_stats}):")
    print("=" * 80)

    armor = data["armor"]
    powerful = []

    for item in armor:
        # Check various stats
        strength = item.get("strength", 0) or 0
        dexterity = item.get("dexterity", 0) or 0
        intelligence = item.get("intelligence", 0) or 0
        agility = item.get("agility", 0) or 0

        total_stats = strength + dexterity + intelligence + agility

        if total_stats >= min_stats:
            powerful.append(
                {
                    "item_id": item.get("item_id"),
                    "stats": total_stats,
                    "str": strength,
                    "dex": dexterity,
                    "int": intelligence,
                    "agi": agility,
                }
            )

    # Sort by total stats
    powerful.sort(key=lambda x: x["stats"], reverse=True)

    print(f"Found {len(powerful)} powerful items")

    # Show top 10
    for item in powerful[:10]:
        print(
            f"  Item #{item['item_id']:>4} | Total: {item['stats']:>3} | "
            f"STR:{item['str']:>2} DEX:{item['dex']:>2} INT:{item['int']:>2} AGI:{item['agi']:>2}"
        )


def analyze_creatures(data):
    """Analyze creature data"""
    print("\n🐉 Creature Analysis:")
    print("=" * 80)

    creatures = data["creatures"]
    stats = data["creature_stats"]

    print(f"Total creatures: {len(creatures)}")
    print(f"Total stat entries: {len(stats)}")

    # Find creatures with highest HP
    stats_with_hp = [
        (s.get("creature_id"), s.get("health", 0) or 0)
        for s in stats
        if s.get("creature_id") is not None
    ]
    stats_with_hp.sort(key=lambda x: x[1], reverse=True)

    print("\nTop 5 creatures by HP:")
    for creature_id, hp in stats_with_hp[:5]:
        if creature_id is not None:
            print(f"  Creature #{creature_id:>4} | HP: {hp:>6,}")


def search_localization(data, search_term="ring"):
    """Search localization strings"""
    print(f"\n🔍 Searching localization for '{search_term}':")
    print("=" * 80)

    loc = data["localisation"]
    matches = []

    search_lower = search_term.lower()
    for entry in loc:
        text = entry.get("text", "")
        if text and search_lower in text.lower():
            matches.append(entry)
            if len(matches) >= 10:  # Limit to first 10
                break

    print(f"Found {len(matches)} matches (showing first 10):")
    for entry in matches[:10]:
        text_id = entry.get("text_id")
        text = entry.get("text", "")[:60]  # Truncate long text
        print(f"  [{text_id:>6}] {text}")


def main():
    """Main example function"""
    print("=" * 80)
    print("GameData.json Example Usage")
    print("=" * 80)

    # Load data
    data = load_gamedata()
    if not data:
        return

    # Run examples
    print_summary(data)
    find_spells_by_school(data, school_name="FIRE", min_level=1, max_level=5)
    find_powerful_items(data, min_stats=100)
    analyze_creatures(data)
    search_localization(data, search_term="ring")

    print("\n" + "=" * 80)
    print("💡 Tips:")
    print("=" * 80)
    print("  - JSON is much faster to load than .cff (seconds vs. minutes)")
    print("  - Use list comprehensions for fast filtering")
    print(
        "  - Enum values are stored as {'_type': 'enum', 'class': '...', 'name': '...'}"
    )
    print("  - Metadata includes export date and source file")
    print()
    print("Try modifying this script to:")
    print("  - Find all legendary weapons")
    print("  - List all buildings and their requirements")
    print("  - Export specific item sets to CSV")
    print("  - Create a spell damage calculator")
    print()


if __name__ == "__main__":
    main()
