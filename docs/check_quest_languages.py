#!/usr/bin/env python3
"""
Diagnostic script to check what language quest descriptions are in the database.
This helps us understand if we should use German text for matching rewards.
"""

import sqlite3
from pathlib import Path


def check_quest_languages():
    """Check the language of quest descriptions in the cache"""

    # Find the database
    cache_path = Path("./src/TirganachReloaded/data/cache/lua_cache/lua_quest_cache.db")

    if not cache_path.exists():
        print(f"❌ Database not found at: {cache_path}")
        print("\nPlease load Lua scripts first:")
        print("  1. Start the application")
        print("  2. Load a CFF file")
        print("  3. Go to Tools → Load Lua Quest Scripts...")
        return

    print("=" * 70)
    print("Quest Language Check")
    print("=" * 70)

    conn = sqlite3.connect(cache_path)
    cursor = conn.cursor()

    # Get total quest count
    cursor.execute("SELECT COUNT(*) FROM lua_quests")
    total_quests = cursor.fetchone()[0]
    print(f"\n📊 Total quests in database: {total_quests}")

    # Sample quests from different platforms
    print("\n" + "=" * 70)
    print("Sample Quest Descriptions (checking language):")
    print("=" * 70)

    cursor.execute("""
        SELECT quest_id, quest_name, description, platform
        FROM lua_quests
        WHERE description IS NOT NULL AND description != ''
        LIMIT 20
    """)

    german_indicators = ["der", "die", "das", "und", "ist", "nach", "vor", "zu", "bei"]
    english_indicators = ["the", "and", "is", "to", "at", "of", "for", "with"]

    german_count = 0
    english_count = 0

    for row in cursor.fetchall():
        quest_id, name, description, platform = row

        # Show first 100 chars of description
        desc_preview = description[:100] if description else "No description"

        # Check language indicators
        desc_lower = description.lower() if description else ""
        has_german = any(word in desc_lower for word in german_indicators)
        has_english = any(word in desc_lower for word in english_indicators)

        if has_german and not has_english:
            language = "🇩🇪 German"
            german_count += 1
        elif has_english and not has_german:
            language = "🇬🇧 English"
            english_count += 1
        elif has_german and has_english:
            language = "🌐 Mixed"
        else:
            language = "❓ Unknown"

        print(f"\nQuest {quest_id} ({platform}) - {language}")
        print(f"  Name: {name}")
        print(f"  Description: {desc_preview}...")

    print("\n" + "=" * 70)
    print("Language Statistics:")
    print("=" * 70)
    print(f"German descriptions: {german_count}")
    print(f"English descriptions: {english_count}")
    print(f"Mixed/Unknown: {20 - german_count - english_count}")

    # Check reward matching
    print("\n" + "=" * 70)
    print("Reward Matching Check:")
    print("=" * 70)

    cursor.execute("SELECT COUNT(*) FROM quest_rewards")
    total_rewards = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM quest_rewards WHERE xp > 0")
    rewards_with_xp = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM quest_rewards WHERE gold > 0")
    rewards_with_gold = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM quest_rewards WHERE items != '[]'")
    rewards_with_items = cursor.fetchone()[0]

    print(f"Total reward entries: {total_rewards}")
    print(
        f"Rewards with XP > 0: {rewards_with_xp} ({rewards_with_xp / total_rewards * 100:.1f}%)"
    )
    print(
        f"Rewards with Gold > 0: {rewards_with_gold} ({rewards_with_gold / total_rewards * 100:.1f}%)"
    )
    print(
        f"Rewards with Items: {rewards_with_items} ({rewards_with_items / total_rewards * 100:.1f}%)"
    )

    # Sample some actual rewards
    print("\n" + "=" * 70)
    print("Sample Quests with Rewards:")
    print("=" * 70)

    cursor.execute("""
        SELECT q.quest_id, q.quest_name, q.description, q.platform, r.xp, r.gold, r.items
        FROM lua_quests q
        JOIN quest_rewards r ON q.quest_id = r.quest_id
        WHERE r.xp > 0
        LIMIT 10
    """)

    for row in cursor.fetchall():
        quest_id, name, desc, platform, xp, gold, items = row
        print(f"\nQuest {quest_id} ({platform})")
        print(f"  XP: {xp}, Gold: {gold}, Items: {items}")
        print(f"  Desc: {desc[:80] if desc else 'No description'}...")

    # Check objectives
    print("\n" + "=" * 70)
    print("Objectives Check:")
    print("=" * 70)

    cursor.execute("SELECT COUNT(*) FROM quest_objectives")
    total_objectives = cursor.fetchone()[0]
    print(f"Total objectives: {total_objectives}")

    if total_objectives > 0:
        cursor.execute("""
            SELECT quest_id, description, objective_type, target, count
            FROM quest_objectives
            LIMIT 10
        """)

        print("\nSample objectives:")
        for row in cursor.fetchall():
            quest_id, desc, obj_type, target, count = row
            print(
                f"  Quest {quest_id}: {desc} (Type: {obj_type}, Target: {target}, Count: {count})"
            )

    conn.close()

    print("\n" + "=" * 70)
    print("Recommendations:")
    print("=" * 70)

    if german_count > english_count:
        print("✅ Most descriptions are in GERMAN")
        print("   → Reward matching should work well with German quest names")
        print("   → The improved matching algorithm will help significantly")
    elif english_count > german_count:
        print("⚠️  Most descriptions are in ENGLISH")
        print("   → Reward matching may be challenging (rewards use German names)")
        print("   → Consider loading German CFF if available")
    else:
        print("❓ Mixed or unclear language distribution")
        print("   → Check sample descriptions above")

    if rewards_with_xp < total_rewards * 0.2:
        print(
            f"\n⚠️  Only {rewards_with_xp / total_rewards * 100:.1f}% of quests have matched rewards"
        )
        print("   → Try deleting cache and reloading with improved matching:")
        print("   → rm -rf src/TirganachReloaded/data/cache/lua_cache/")
        print("   → Then reload Lua scripts in the app")
    else:
        print(
            f"\n✅ {rewards_with_xp / total_rewards * 100:.1f}% of quests have rewards - good!"
        )

    if total_objectives == 0:
        print("\n⚠️  No objectives found")
        print("   → The objective parser may not be working")
        print("   → Check console output when loading Lua scripts")
    else:
        print(f"\n✅ Found {total_objectives} objectives - parser working!")


if __name__ == "__main__":
    try:
        check_quest_languages()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()
