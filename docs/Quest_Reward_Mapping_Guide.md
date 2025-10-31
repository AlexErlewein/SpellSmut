# Quest Reward Mapping Guide

## Overview

This guide explains how to manually map quest rewards from `GdsQuestRewards.lua` to quest IDs in the game database, and discusses the benefits of multi-language support.

---

## The Problem

The game's quest reward system uses **script identifiers** (like `NachGraufurtPartVillage`) in `GdsQuestRewards.lua`, while quest data in the database contains **descriptive text** (like "Fragt Darius nach Rohens Verbleib!"). Automatically matching these is difficult because:

1. **Script names are compound German words** - e.g., `DariusDerKarthograph` → "Darius the Cartographer"
2. **Quest descriptions are in German** - Making string matching unreliable
3. **No direct ID references** - The reward file doesn't include quest IDs
4. **Similar quest names** - Multiple quests might have overlapping keywords

### Current Matching Success Rate

- **Total rewards parsed**: 479 rewards across 47 platforms
- **Automatic matches**: ~9 successful (< 2%)
- **Manual mapping needed**: ~470 rewards (98%)

---

## Why Manual Mapping Helps

### ✅ Benefits

1. **100% Accuracy** - Direct ID mapping eliminates guessing
2. **Complete Coverage** - Every quest can have proper rewards
3. **Prevents Errors** - No false matches from similar quest names
4. **Future-Proof** - Mappings persist across game updates
5. **Community Collaboration** - Mapping file can be shared and improved

### 📊 Impact

Without manual mapping:
- Players see quests with **0 XP, 0 Gold, no items**
- Quest editor shows incomplete reward data
- Mod creators can't accurately balance quests

With manual mapping:
- ✅ All quest rewards display correctly
- ✅ XP values, gold, and item rewards are accurate
- ✅ Quest progression tracking works properly

---

## Multi-Language Support

### Would It Help? **YES!**

Adding multiple language versions of quest data would **significantly improve** automatic matching.

### Language Files in SpellForce

The game stores localized text in:
- `GameData.cff` - Contains all game strings in multiple languages
- Supports: English, German, French, Italian, Spanish, Polish, Russian, Czech

### How Multi-Language Would Help

#### Example Quest Matching

**Script Name**: `DariusDerKarthograph`

**Without English**:
- German Description: "Sprecht mit Darius dem Kartographen"
- Matching algorithm must parse compound German words
- Success rate: **Low**

**With English**:
- English Description: "Talk to Darius the Cartographer"
- Script name parts: `Darius`, `Der`, `Karthograph`
- English parts: `Darius`, `Cartographer`
- Success rate: **High** (exact name match)

### Implementation Strategy

```python
# Multi-language matching algorithm
def match_quest_with_languages(script_name, quest_data):
    """
    Match quest using multiple language versions
    """
    # German: "DariusDerKarthograph"
    # English: "Darius" + "Cartographer"
    # Success if name appears in ANY language version
    
    languages = ['german', 'english', 'french']
    for lang in languages:
        if matches(script_name, quest_data[lang]):
            return quest_data['quest_id']
    return None
```

### Expected Improvement

- **Current**: 2% automatic match rate
- **With English**: Estimated 40-60% automatic match rate
- **With Multiple Languages**: Estimated 60-80% automatic match rate

### Extract Language Data

To implement multi-language support:

1. **Extract strings from GameData.cff**
   ```bash
   # Use the CFF extractor tool
   python src/helper_tools/extraction/extract_cff_strings.py
   ```

2. **Parse quest text in all languages**
3. **Store in database** with language tags
4. **Update matching algorithm** to check all language versions

---

## Manual Mapping Workflow

### Step 1: Generate Mapping Template

Run the extraction script:

```bash
python src/helper_tools/extraction/extract_reward_names.py
```

This creates:
- `quest_reward_mappings_template.json` - Template for manual mappings
- `reward_names_by_platform.txt` - Readable reference list

### Step 2: Review Reward Names

Open `reward_names_by_platform.txt` to see all 479 rewards organized by platform:

```
================================================================================
PLATFORM P63 - Greyfell - 36 rewards
================================================================================

  NachGraufurtPartVillage
    → XP: 20, Items: [532]
    💬 done

  Zauberwerk1Augenglas
    → XP: 10
    💬 done

  BlutAdhiraTrank
    → XP: 4000
    💬 done
```

### Step 3: Find Quest IDs

Use one of these methods to find the correct quest ID:

#### Method A: CFF Editor Quest Browser
1. Open the CFF editor
2. Load quest data for the platform (e.g., P63)
3. Search for keywords from the reward name
4. Note the quest ID

#### Method B: Database Query
```python
import sqlite3
from pathlib import Path

db_path = Path.home() / ".spellforce_editor" / "lua_cache" / "lua_quest_cache.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Search for quests containing "Adhira"
cursor.execute("""
    SELECT quest_id, quest_name, description 
    FROM lua_quests 
    WHERE platform = 'P63' 
    AND (description LIKE '%Adhira%' OR description LIKE '%Blut%')
""")

for row in cursor.fetchall():
    print(f"Quest {row[0]}: {row[2][:100]}")
```

#### Method C: In-Game Testing
1. Play the game to the specific quest
2. Note the quest details
3. Cross-reference with the reward name

#### Method D: Community Knowledge
- Check SpellForce wikis
- Consult gameplay guides
- Ask the modding community

### Step 4: Fill in Mappings

Edit `quest_reward_mappings_template.json`:

```json
{
  "P63": {
    "_platform_name": "Greyfell",
    "_count": 36,
    "rewards": {
      "NachGraufurtPartVillage": {
        "quest_id": 265,  // ← Fill this in!
        "xp": 20,
        "items": [532],
        "comment": "done"
      },
      "BlutAdhiraTrank": {
        "quest_id": 396,  // ← Fill this in!
        "xp": 4000,
        "comment": "done"
      }
    }
  }
}
```

### Step 5: Validate Mappings

Run the validation script:

```bash
python src/helper_tools/extraction/validate_reward_mappings.py
```

This checks:
- ✓ All quest IDs exist in the database
- ✓ Platform matches are correct
- ✓ No duplicate mappings
- ⚠️ Warnings for unusual reward values

### Step 6: Apply Mappings

Save your file as `quest_reward_mappings.json` (without `_template`).

The parser will automatically use these mappings when loading quest data:

```python
# The parser checks for manual mappings first
manual_mapping = load_manual_mapping(quest_name, platform)
if manual_mapping:
    quest_id = manual_mapping['quest_id']
    # Use manual mapping
else:
    # Fall back to automatic matching
    quest_id = auto_match_quest(quest_name, platform)
```

---

## Hybrid Approach (Recommended)

Combine automatic and manual mapping for best results:

### Phase 1: Automatic (Already Implemented)
- Parser attempts automatic matching using German text
- ~2% success rate
- Fast, no manual work

### Phase 2: Multi-Language Enhancement
- Extract English/other language quest text from GameData.cff
- Improve automatic matching to ~60% success rate
- Reduces manual work significantly

### Phase 3: Manual Mapping
- Fill in remaining ~40% that couldn't be auto-matched
- Ensure 100% coverage
- Create shareable mapping file

---

## Mapping Statistics

### Current Status (After Regex Fix)

| Metric | Value |
|--------|-------|
| Total Rewards | 479 |
| Platforms | 47 |
| Automatic Matches | 9 (2%) |
| Needs Manual Mapping | 470 (98%) |
| Database Quest Entries | 998 |

### Platform Breakdown

| Platform | Name | Rewards |
|----------|------|---------|
| P63 | Greyfell | 36 |
| P1 | Greydusk Vale | 21 |
| P204 | Unknown | 25 |
| P208 | Unknown | 22 |
| P209 | Unknown | 21 |
| P202 | Unknown | 17 |

---

## Example Mappings

### Example 1: Simple Compound Word

**Script Name**: `DariusDerKarthograph`

**Quest Search**:
- Keywords: "Darius", "Karthograph", "Kartograph", "Cartographer"
- Platform: P1
- Found: Quest 127 - "Sprecht mit Darius dem Kartographen"

**Mapping**:
```json
"DariusDerKarthograph": {
  "quest_id": 127,
  "xp": 25,
  "comment": "Darius the Cartographer quest"
}
```

### Example 2: Character Name

**Script Name**: `BlutAdhiraTrank`

**Quest Search**:
- Keywords: "Blut" (blood), "Adhira", "Trank" (potion)
- Platform: P63
- Found: Quest 396 - Quest about Adhira's blood potion

**Mapping**:
```json
"BlutAdhiraTrank": {
  "quest_id": 396,
  "xp": 4000,
  "comment": "Adhira's blood potion quest"
}
```

### Example 3: Sequential Quests

**Script Names**: `Zauberwerk1Augenglas`, `Zauberwerk2Feder`, `Zauberwerk3Kreide`, `Zauberwerk4Robe`

**Pattern**: Quest series about magical items (Zauberwerk = magical work)

**Mappings**:
```json
"Zauberwerk1Augenglas": {
  "quest_id": 112,
  "xp": 10,
  "comment": "Magical Work part 1 - Eyeglass"
},
"Zauberwerk2Feder": {
  "quest_id": 113,
  "xp": 25,
  "comment": "Magical Work part 2 - Feather"
}
```

---

## Tools and Resources

### Extraction Tools

- `extract_reward_names.py` - Generate mapping templates
- `validate_reward_mappings.py` - Check mapping correctness
- `extract_cff_strings.py` - Extract multi-language text (future)

### Reference Files

- `reward_names_by_platform.txt` - Human-readable reward list
- `quest_reward_mappings_template.json` - JSON template for mappings
- `quest_reward_mappings.json` - Active mapping file (your edits)

### Database Queries

Useful SQL queries for finding quest IDs:

```sql
-- Find all quests for a platform
SELECT quest_id, description FROM lua_quests WHERE platform = 'P63';

-- Search by keyword
SELECT quest_id, description FROM lua_quests 
WHERE description LIKE '%keyword%' AND platform = 'P63';

-- Find unmapped quests
SELECT lq.quest_id, lq.description 
FROM lua_quests lq
LEFT JOIN quest_rewards qr ON lq.quest_id = qr.quest_id
WHERE qr.xp = 0 AND qr.gold = 0 AND qr.items = '[]';
```

---

## Community Collaboration

### Sharing Mappings

Once you've created mappings, you can share them:

1. **GitHub** - Commit `quest_reward_mappings.json` to the repository
2. **SpellForce Forums** - Share with other modders
3. **Discord Communities** - Collaborate on difficult mappings

### Partial Mappings

Don't worry about completing all 479 rewards at once:

- Map the most important quests first (high XP, unique items)
- Focus on one platform at a time
- Leave `"quest_id": null` for unknowns
- Update incrementally as you discover more

### Mapping Quality

Priority levels:

1. **Critical** - Main story quests, high XP rewards
2. **Important** - Side quests with unique item rewards
3. **Nice to have** - Minor quests, low XP rewards
4. **Optional** - Tutorial quests, repeatable quests

---

## Conclusion

### Short Answer

**Yes, manual mapping would definitely help!** With 479 rewards and only 2% automatic match rate, manual mapping is currently the most practical solution.

**Yes, multi-language support would help significantly!** Adding English/other languages could improve automatic matching from 2% to 60%+, drastically reducing manual work.

### Recommended Approach

1. ✅ **Implement multi-language extraction** (extract English text from GameData.cff)
2. ✅ **Enhance automatic matching** (use English strings to improve matching)
3. ✅ **Manual mapping for remaining quests** (40% of quests, not 98%)
4. ✅ **Community sharing** (distribute mapping file with mod)

### Next Steps

1. Run `extract_reward_names.py` to generate templates
2. Review `reward_names_by_platform.txt`
3. Start mapping high-priority quests (main story, high XP)
4. Consider implementing multi-language support for long-term benefits

---

## Questions?

If you need help with:
- Extracting multi-language data
- Writing validation scripts
- Finding specific quest IDs
- Automating parts of the mapping process

Feel free to ask! The SpellForce modding community is also a great resource.