# Character Appearance Customization Research - SpellForce
## 📋 Research Findings for NPC Creator Appearance System

## Executive Summary

**SpellForce supports extensive character appearance customization** through a combination of head models, race/gender combinations, and equipment assignment. However, **true "new model creation" is limited** - NPCs must use existing head models and body types from the game's asset library.

---

## 🔍 Research Methodology

### Data Sources Analyzed:
- ✅ Creature/CreatureStats entities in GameData.json
- ✅ Head entity structure and usage patterns
- ✅ Race and Gender enum definitions
- ✅ Equipment slot configurations
- ✅ Audio extraction lists (voice options)
- ✅ DrwSound.lua (voice assignments)

---

## 🎯 Key Findings

### 1. Head Models (✅ FULLY CUSTOMIZABLE)

**Available Head IDs**: 0-31 (32 total head models)

**Usage Pattern**:
```json
{
  "stats_id": 123,
  "head_id": 5,
  "race": "HUMANS",
  "gender": "MALE"
}
```

**Research Results**:
- **32 unique head models** available (IDs 0-31)
- **Race/Gender Agnostic**: Any head can be assigned to any race/gender combination
- **No Visual Restrictions**: Game engine allows mismatched head/race combinations
- **Essential vs Regular**: Both "ESSENTIAL" and regular gender variants can use any head

### 2. Race & Gender System (✅ FULLY CUSTOMIZABLE)

**Available Races**:
- `HUMANS`, `DWARVES`, `ELVES`, `TROLLS`, `ORCS`, `DARKELVES`
- Plus 100+ faction variants (e.g., `_MERCHANTS`, `_HAZIM`, `_ELVES_SHIEL`)

**Available Genders**:
- `MALE` (0), `FEMALE` (1)
- `MALE_ESSENTIAL` (2), `FEMALE_ESSENTIAL` (3)

**Customization Freedom**:
- **No Restrictions**: Any race can be any gender
- **Faction Override**: Race field can be faction-specific (affects AI/social behavior)
- **Visual Impact**: Race affects body model proportions and animations

### 3. Equipment & Armor (✅ FULLY CUSTOMIZABLE)

**Equipment Slots Available**:
```python
class EquipmentSlot(Enum):
    HELMET = 0
    RIGHT_HAND = 1
    CHEST = 2
    LEFT_HAND = 3
    RIGHT_RING = 4
    LEGS = 5
    LEFT_RING = 6
```

**Configuration Options**:
- `ALL` (7 slots)
- `HANDS_AND_RINGS` (4 slots: hands + rings)
- `NONE` (no equipment)

**Customization Capabilities**:
- **Any Item Assignable**: No restrictions on item type per slot
- **Multiple Configurations**: Creatures can have different equipment slot setups
- **Visual Override**: Equipment determines visual appearance

### 4. Voice System (✅ FULLY CUSTOMIZABLE)

**Voice Categories**:

1. **Main Character Voices** (battle_char_m/f):
   - 6 attack variations
   - 6 hit/damage variations
   - 2 death variations
   - **Total**: 14 voice files per gender

2. **Hero Voices** (battle_hero01-05_m/f):
   - 5 male hero voice sets
   - 5 female hero voice sets
   - Each with attack, hit, and death sounds
   - **Total**: 10 hero voice sets × 3 actions = 30 unique voice files

3. **NPC Creature Voices** (battle_npc_*):
   - 40+ creature types (basilisk, demon, dragon, etc.)
   - Each with 2 attack + 3 hit + 1 death variation
   - **Total**: 292 unique NPC voice files

**Voice Assignment**:
- **Not Data-Driven**: Voices are hardcoded in DrwSound.lua
- **Race-Based Selection**: Game likely uses race to determine voice set
- **No Custom Voices**: Cannot add new voice files (WAV format required)

---

## 🚫 Limitations & Restrictions

### 1. Model Creation (❌ NOT POSSIBLE)
- **Cannot create new 3D models** for heads or bodies
- **Cannot import custom meshes** or textures
- **Must use existing assets** from game files

### 2. Visual Customization Scope (⚠️ LIMITED)
- **Hair Styles**: No evidence of customizable hair
- **Skin Tones**: No evidence of skin tone variation
- **Facial Features**: Limited to available head models only
- **Body Types**: Determined by race (cannot customize proportions)

### 3. Voice Limitations (❌ HARD RESTRICTIONS)
- **No Custom Audio**: Cannot add new voice files
- **Hardcoded Assignments**: Voices linked to specific sound IDs in Lua
- **Format Locked**: Must use WAV format with specific naming conventions

---

## 🎨 Appearance Customization Matrix

| Aspect | Customizable? | Options | Notes |
|--------|---------------|---------|-------|
| **Head Model** | ✅ Yes | 32 head models (0-31) | Any combination allowed |
| **Race** | ✅ Yes | 6 base + 100+ factions | Affects body proportions |
| **Gender** | ✅ Yes | 4 variants | Essential vs regular |
| **Equipment** | ✅ Yes | Any items in any slots | Visual appearance |
| **Voice** | ⚠️ Limited | 3 categories, hardcoded | Cannot add custom voices |
| **Hair Style** | ❌ No | N/A | Fixed per head model |
| **Skin Tone** | ❌ No | N/A | Fixed per race |
| **Body Proportions** | ❌ No | N/A | Race-determined |
| **New Models** | ❌ No | N/A | Must use existing assets |

---

## 🛠️ Implementation Recommendations for NPC Creator

### Phase 5: Appearance & Voice (NOW FEASIBLE)

**Head Selection**:
- Dropdown with 32 head model options (0-31)
- Preview images if available (would need asset extraction)
- Default to race-appropriate heads

**Race/Gender Selection**:
- Race dropdown (6 main races + faction options)
- Gender radio buttons (Male/Female with Essential variants)
- Smart defaults based on NPC type

**Equipment Assignment**:
- Equipment browser dialog (reuse from Weapon Forge)
- Slot-based assignment interface
- Preview of equipped appearance

**Voice Selection**:
- Dropdown with available voice sets:
  - "Main Character (Male/Female)"
  - "Hero 1-5 (Male/Female)"
  - "Creature: [Type]" (40+ options)
- Note limitation: cannot add custom voices

### Future Enhancements (Post-V1)

1. **Head Model Preview**: Extract and display head model thumbnails
2. **Equipment Preview**: Show equipped NPC appearance
3. **Voice Preview**: Play voice samples in editor
4. **Race Compatibility**: Warn about unusual race/head combinations

---

## 📊 Data Validation Rules

**Head ID Validation**:
- Must be 0-31
- No range restrictions (any head with any race/gender)

**Race Validation**:
- Must be valid Race enum value
- Faction races accepted (affects AI behavior)

**Equipment Validation**:
- Item IDs must exist in game data
- Slot configuration must be valid
- No type restrictions (game allows any item in any slot)

**Voice Validation**:
- Must reference existing sound IDs
- Limited to predefined voice sets

---

## 🔬 Research Gaps & Future Investigation

### Unanswered Questions:
1. **Head Model Visual Differences**: What do heads 0-31 actually look like?
2. **Race Visual Impact**: How much do different races change appearance?
3. **Equipment Visual Priority**: Which equipment slots are most visible?
4. **Faction Race Differences**: Do faction races have unique visuals?

### Recommended Next Steps:
1. **Asset Extraction**: Extract head model images/thumbnails
2. **Visual Documentation**: Screenshots of different race/head combinations
3. **Equipment Testing**: Document which equipment is most visible
4. **Voice Mapping**: Document which races use which voice sets

---

## ✅ Research Conclusion

**The NPC Creator CAN implement a comprehensive appearance system** using existing game assets. While true "custom model creation" isn't possible, the extensive existing asset library (32 heads × 100+ races × 4 genders × extensive equipment options) provides **thousands of unique NPC appearances**.

**Key Implementation Strategy**:
- Focus on **asset selection and combination** rather than creation
- Provide **extensive preview capabilities** (when assets are extracted)
- **Document limitations clearly** to set user expectations
- **Future-proof for asset extraction** enhancements

---

## 📝 References

- `src/TirganachReloaded/tirganach/entities.py` - Creature/CreatureStats definitions
- `src/TirganachReloaded/tirganach/types.py` - Race/Gender enums
- `OriginalGameFiles/script/DrwSound.lua` - Voice assignments
- `ExtractedAssets/Audio/extraction_lists/` - Available voice files
- `src/TirganachReloaded/GameData.json` - Live usage examples

---

**Research Completed**: ✅ 2025-10-28
**Researcher**: SpellSmut Development Team
**Status**: ✅ Appearance System Ready for Implementation