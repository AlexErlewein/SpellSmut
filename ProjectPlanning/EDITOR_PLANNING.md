# SpellForce GameData.cff Editor - Planning Document

## Requirements Analysis

### Core Functionality

1. **File Management**
   - Open CFF file (file picker)
   - Display loading progress (176k+ entries)
   - Save modifications back to CFF
   - Export to XML (optional)

2. **Category Browser**
   - List all 43 tables (spells, items, creatures, etc.)
   - Show entry count per category
   - Quick search/filter categories

3. **Element List View**
   - Display all elements in selected category
   - Sortable columns (ID, name, type, etc.)
   - Search/filter elements
   - Pagination for large tables (176k localization entries!)

4. **Element Detail Editor**
   - Display all properties of selected element
   - Editable fields with type validation
   - Enum dropdowns with known values (ItemType, EquipmentType, School, Race, WeaponType, etc.)
   - Save/Cancel changes
   - Highlight modified fields

5. **Additional Features (Nice to Have)**
   - Add new elements
   - Clone existing elements
   - Delete elements (with warning)
   - Compare two CFF files
   - Undo/Redo functionality

---

## Known Enum Values for Key Categories

### Weapon Types (for weapons table)
- 0: No Weapon / Unarmed
- 1: Mouth (Bite)
- 2: Fist
- 3: Dagger
- 4: 1H Sword
- 5: 2H Sword
- 6: 1H Axe
- 7: 2H Axe
- 8: 1H Mace
- 9: 2H Mace
- 10: Staff
- 11: 1H Hammer
- 12: 2H Hammer
- 13: Spiky 1H Mace
- 14: Blunt 1H Mace
- 15: 1H Spear
- 16: 2H Spear
- 17: Halberd
- 18: Bow
- 19: Crossbow
- 20: Claws
- 21: Unknown

### Weapon Materials (for weapons table)
- 1: Iron
- 2: Steel
- 3: Silver
- 4: Obsidian
- 5: Elven Steel
- 6: Dwarven Steel
- 7: Mithril

### Armor Types (for armor table)
- (To be determined from actual armor enum data)

### Armor Materials (for armor table)
- (To be determined from actual armor enum data)

### Item Types (for items table)
- 1: EQUIPMENT
- 2: RUNE_INVENTORY
- 3: RUNE_ADDED
- 4: SCROLL
- 5: SPELL
- 6: UNIT_PLAN_INVENTORY
- 7: BUILDING_PLAN_INVENTORY
- 8: UNIT_PLAN_ADDED
- 9: BUILDING_PLAN_ADDED
- 10: QUEST_ITEM
- 11: BLANK_SCROLL

### Equipment Types (for items table item_subtype when ItemType is EQUIPMENT)
- 0: NOTHING
- 1: HELMET
- 2: UPPER (Upper Body Armor)
- 3: LOWER (Lower Body Armor)
- 6: RING
- 7: ONEHANDED_WEAPON
- 8: TWOHANDED_WEAPON
- 9: SHIELD
- 10: FULL_BODY
- 11: FIGURE_NPC
- 12: BOW
- 13: FIGURE_HERO

### Rune/Plan Types (for items table item_subtype when ItemType is RUNE_INVENTORY, RUNE_ADDED, etc.)
- 0: HEROES
- 1: HUMANS
- 2: ELVES
- 3: DWARVES
- 4: ORCS
- 5: TROLLS
- 6: DARKELVES

### Equipment Slots (for equipment placement)
- 0: HELMET
- 1: RIGHT_HAND
- 2: CHEST
- 3: LEFT_HAND
- 4: RIGHT_RING
- 5: LEGS
- 6: LEFT_RING
- 12: UNKNOWN

### Schools/Skills (for character abilities)
- (0, 0): LEVEL_ONLY
- (0, 1): UNKNOWN
- (1, 0): LIGHT_COMBAT
- (1, 1): PIERCING_WEAPONS
- (1, 2): LIGHT_BLADE_WEAPONS
- (1, 3): LIGHT_BLUNT_WEAPONS
- (1, 4): LIGHT_ARMOR
- (2, 0): HEAVY_COMBAT
- (2, 1): HEAVY_BLADE_WEAPONS
- (2, 2): HEAVY_BLUNT_WEAPONS
- (2, 3): HEAVY_ARMOR
- (2, 4): SHIELDS
- (3, 0): RANGED_COMBAT
- (3, 1): BOWS
- (3, 2): CROSSBOWS
- (4, 0): WHITE_MAGIC
- (4, 1): LIFE
- (4, 2): NATURE
- (4, 3): BOONS
- (5, 0): ELEMENTAL_MAGIC
- (5, 1): FIRE
- (5, 2): ICE
- (5, 3): EARTH
- (6, 0): MIND_MAGIC
- (6, 1): ENCHANTMENT
- (6, 2): OFFENSIVE
- (6, 3): DEFENSIVE
- (7, 0): BLACK_MAGIC
- (7, 1): DEATH
- (7, 2): NECROMANCY
- (7, 3): CURSE

### Races
- 1: HUMANS
- 2: DWARVES
- 3: ELVES
- 4: TROLLS
- 5: ORCS
- 6: DARKELVES

### Resources
- 0: UNKNOWN
- 1: WOOD
- 2: STONE
- 3: LOGS
- 4: MOONSILVER
- 5: FOOD
- 6: BERRIES
- 7: IRON
- 8: TREES
- 9: GRAIN
- 10: UNKNOWN1
- 11: FISH
- 15: MUSHROOMS
- 16: MEAT
- 18: ARIA
- 19: LENYA
- 47: UNKNOWN2
- 73: UNKNOWN3

### Gender
- 0: MALE
- 1: FEMALE
- 2: MALE_ESSENTIAL
- 3: FEMALE_ESSENTIAL

### Slot Configuration
- 1: ALL
- 2: HANDS_AND_RINGS
- 3: NONE

---

## Spell Naming Convention

### UI Handle Format
Spell UI handles follow the format: `ui_spell_[ELEMENT]_[CATEGORY]_[NAME]`
- **ELEMENT**: Two-letter abbreviation for the magic school
- **CATEGORY**: Spell category within the school
- **NAME**: Actual spell name

### Elements (Magic Schools)
- **BM**: Black Magic (Necromancy, Death, Curses)
- **EM**: Elemental Magic (Fire, Ice, Earth)
- **MM**: Mind Magic (Enchantment, Offensive, Defensive)
- **WM**: White Magic (Life, Nature, Blessings)
- **melee**: Melee combat enhancements

### Spell Categories and Names

#### Black Magic (BM)
**Curse:**
- 4. AuraSlowWalking
- 5. Poison
- 34. AuraInflexibility
- 36. DarkBanishing
- 37. AuraSlowWalking
- 38. AuraInflexibility
- 41. Remediless
- 94. AuraSlowFighting
- 95. AuraInflexibility
- 96. DispelWhiteAura
- 97. AuraSlowWalking
- 98. AuraInability
- 100. AuraInability
- 101. AuraSlowFighting
- 199. Mutation
- 200. AreaOfDarkness
- 201. Mutation_chain
- 233. Mutation

**Death:**
- 3. Death
- 18. Pain
- 23. Pestilence
- 28. AreaPain
- 35. AuraWeakness
- 39. AuraWeakness
- 81. Extinct
- 88. AuraWeakness
- 89. AuraSuffocation
- 90. SuicideDeath
- 99. AuraSuffocation
- 162. Pain
- 171. Extinct
- 193. Pain_chain
- 194. Cannibalize
- 195. Torture
- 240. Pain

**Necro:**
- 19. LifeTap
- 20. SummonGoblin
- 29. SummonSkeleton
- 30. RaiseDead
- 32. DeathGrasp
- 91. AuraLifeTap
- 92. SummonSpectre
- 93. FeignDeath
- 146. LifeTap
- 196. LifeTap_chain
- 197. DominateUndead
- 198. SummonBlade
- 231. LifeTap

#### Elemental Magic (EM)
**Earth:**
- 16. Decay
- 17. Decay
- 25. Petrify
- 76. StoneRain
- 82. DetectMetal
- 139. RockBullet
- 140. Conservation
- 141. EarthElemental
- 142. WaveOfRocks
- 208. RockBullet_chain
- 209. SummonEarthGolem
- 210. FeetOfClay
- 236. RockBullet

**Fire:**
- 1. FireBurst
- 11. Illuminate
- 12. FireShield
- 13. FireBall
- 60. FireShield
- 73. RainOfFire
- 133. FireElemental
- 134. WaveOfFire
- 135. MeltResistance
- 147. FireBall
- 159. FireBurst
- 170. FireBurst
- 173. FireResistance
- 202. FireBurst_chain
- 203. SummonFireGolem
- 204. FireBall_chain
- 234. FireBurst
- 239. FireBall

**Ice:**
- 9. Freeze
- 10. Fog
- 14. IceBurst
- 15. IceShield
- 22. IceShield
- 74. Blizzard
- 136. IceElemental
- 137. WaveOfIce
- 138. ChillResistance
- 145. IceBurst
- 168. IceBurst
- 169. IceBurst
- 205. IceBurst_chain
- 206. SummonIceGolem
- 207. AreaFreeze
- 235. IceBurst

#### Mind Magic (MM)
**Defensive:**
- 65. Brilliance
- 66. SacrificeMana
- 67. Manatap
- 68. Manadrain
- 83. DetectMagic
- 129. AuraBrilliance
- 130. Enlightenment
- 131. AuraManatap
- 132. Meditation
- 172. Manatap
- 217. Manatap_chain
- 218. Manashield
- 219. Manashift
- 232. Manatap

**Enchantment:**
- 63. SelfIllusion
- 86. Invisible
- 119. Distract
- 120. Dominate
- 121. ObjectIllusion
- 122. Charm
- 123. Befriend
- 124. Disentchant
- 125. Charisma
- 211. GreaterIllusion
- 212. Charm_chain
- 213. Voodoo
- 237. Charm

**Offensive:**
- 21. Hypnotize
- 69. Shock
- 70. Disrupt
- 72. Confuse
- 79. Amok
- 126. Shockwave
- 127. AuraHypnotization
- 128. Demoralization
- 161. Hypnotize
- 167. Hypnotize
- 214. Shock_chain
- 215. AreaHypnotize
- 216. AreaConfuse
- 238. Shock

#### White Magic (WM)
**Blessing:**
- 6. Invulnerability
- 48. AuraFastWalking
- 49. AuraFastWalking
- 50. Flexibility
- 51. AuraFlexibility
- 58. Hallow
- 110. AuraFastFighting
- 111. AuraFlexibility
- 112. DispelBlackAura
- 113. AuraFastWalking
- 114. AuraLight
- 115. AuraDexterity
- 116. AuraDexterity
- 118. AuraFastFighting
- 164. ProtectFromBlack
- 190. Hallow_chain
- 191. Reinforcement
- 192. AuraOfEternity
- 229. AuraOfEternity
- 230. Hallow

**Life:**
- 2. Healing
- 43. AreaHealing
- 44. SentinelHealing
- 45. GreaterHealing
- 52. AuraStrength
- 53. AuraStrength
- 102. AuraStrength
- 103. AuraHealing
- 104. AuraEndurance
- 105. SuicideHeal
- 117. AuraEndurance
- 144. Healing
- 166. Healing
- 184. Assistance
- 185. HolyTouch
- 186. Revenge

**Nature:**
- 7. CurePoison
- 24. CureDisease
- 46. CharmAnimal
- 47. ThornShield
- 56. AuraRegeneration
- 61. ThornShield
- 106. TransformWolf
- 107. AuraRegeneration
- 108. DominateAnimal
- 109. TransformBear
- 187. AreaRoots
- 188. SummonTreewrath
- 189. Roots

#### Melee Combat Enhancements (melee)
**berserk:**
- 148. Unknown
- 152. Unknown

**blessing:**
- 149. Unknown
- 153. Unknown

**shelter:**
- 150. Unknown
- 154. Unknown

**durability:**
- 151. Unknown
- 155. Unknown

**trueshot:**
- 156. Unknown

**steelskin:**
- 157. Unknown

**salvo:**
- 158. Unknown

**shiftlife:**
- 220. Unknown

**riposte:**
- 221. Unknown

**criticalhits:**
- 222. Unknown

### Template for Future Category Reference
This format can be reused for weapons and armor, with appropriate naming conventions and category breakdowns:

#### Weapon Naming Convention
- Format: `ui_weapon_[TYPE]_[MATERIAL]_[NAME]`
- **TYPE**: Weapon type (Dagger, Sword, Axe, etc.)
- **MATERIAL**: Weapon material (Iron, Steel, etc.)
- **NAME**: Specific weapon name

#### Armor Naming Convention  
- Format: `ui_armor_[TYPE]_[MATERIAL]_[NAME]`
- **TYPE**: Armor type (Helmet, Chest, etc.)
- **MATERIAL**: Armor material (Leather, Chain, Plate, etc.)  
- **NAME**: Specific armor name

---

## Option 1: GUI Application

### Framework Comparison

#### A. **Tkinter** (Built-in Python)

**Pros:**
- ✅ No installation needed (comes with Python)
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Lightweight and fast
- ✅ Good for simple layouts
- ✅ Mature and stable

**Cons:**
- ❌ Looks dated by default
- ❌ Requires extra work for modern look
- ❌ Limited built-in widgets
- ❌ No native dark mode support

**Modern Tkinter Libraries:**
- **CustomTkinter** - Modern, dark mode, rounded corners
- **ttkbootstrap** - Bootstrap-inspired themes

**Rating:** ⭐⭐⭐ (3/5) - Functional but requires styling work

---

#### B. **PyQt6/PySide6** (Qt Framework)

**Pros:**
- ✅ Professional, native look
- ✅ Extensive widget library (tables, trees, etc.)
- ✅ Built-in dark mode
- ✅ Excellent table/list performance
- ✅ Rich documentation
- ✅ Designer tool (Qt Designer) for visual layout
- ✅ Very powerful and flexible

**Cons:**
- ❌ Larger dependency (~50MB)
- ❌ LGPL license (PySide6) or GPL/Commercial (PyQt6)
- ❌ Steeper learning curve
- ❌ Can be overkill for simple apps

**Best For:** Complex applications with lots of data

**Rating:** ⭐⭐⭐⭐⭐ (5/5) - Industry standard, excellent for data editing

---

#### C. **wxPython** (wxWidgets)

**Pros:**
- ✅ Native look on each platform
- ✅ Good widget selection
- ✅ Mature and stable
- ✅ LGPL license (more permissive)

**Cons:**
- ❌ Less modern than Qt
- ❌ Smaller community than Qt
- ❌ Documentation not as comprehensive

**Rating:** ⭐⭐⭐⭐ (4/5) - Good alternative to Qt

---

#### D. **Kivy** (Modern, Touch-focused)

**Pros:**
- ✅ Very modern and animated
- ✅ Touch-friendly
- ✅ Custom styling with KV language
- ✅ Cross-platform (even mobile)

**Cons:**
- ❌ Non-native look (custom UI)
- ❌ Not ideal for data-heavy apps
- ❌ Overkill for desktop-only
- ❌ Performance issues with large tables

**Rating:** ⭐⭐ (2/5) - Too focused on mobile/touch

---

#### E. **Dear PyGui** (Immediate Mode GUI)

**Pros:**
- ✅ Very modern look
- ✅ GPU-accelerated (fast rendering)
- ✅ Great for data visualization
- ✅ Built-in tables, plots, themes
- ✅ Easy to get started

**Cons:**
- ❌ Relatively new (less mature)
- ❌ Smaller community
- ❌ Different paradigm (immediate mode)
- ❌ Limited documentation

**Rating:** ⭐⭐⭐⭐ (4/5) - Modern and fast, but newer

---

#### F. **Flet** (Flutter-based)

**Pros:**
- ✅ Very modern Material Design UI
- ✅ Beautiful out of the box
- ✅ Easy to learn
- ✅ Cross-platform (desktop, web, mobile)
- ✅ Reactive updates

**Cons:**
- ❌ Very new (2022+)
- ❌ Limited widget library
- ❌ Requires Flutter engine
- ❌ Not ideal for complex data tables

**Rating:** ⭐⭐⭐ (3/5) - Beautiful but too new

---

### GUI Recommendation: **PyQt6/PySide6**

**Why Qt?**
1. **Table Performance** - Handles 176k entries smoothly
2. **Built-in Widgets** - QTableView, QTreeView perfect for our needs
3. **Professional Look** - Native styling + dark mode
4. **Mature** - Battle-tested, stable, excellent docs
5. **Model/View Architecture** - Perfect for large datasets

**UI Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  SpellForce CFF Editor                    [─][□][×]    │
├─────────────────────────────────────────────────────────┤
│  File  Edit  View  Tools  Help                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📁 H:\SpellSmut\OriginalGameFiles\data\GameData.cff  │
│                                                         │
├──────────────┬──────────────────────┬───────────────────┤
│              │                      │                   │
│  Categories  │   Element List       │  Properties       │
│              │                      │                   │
│ ▼ Items      │ ID    Name      Type │  ┌─────────────┐ │
│   □ Spells   │ 531   Soulguard Ring │  │ item_id: 531│ │
│   □ Armor    │ 532   Ruby Ring  Ring │  │ name: Soul..│ │
│   □ Weapons  │ 537   Antique... Ring │  │             │ │
│   □ Creatures│ ...                   │  │ item_type:  │ │
│   [43 more]  │                      │  │ [EQUIPMENT▼]│ │
│              │ [Search: ____]       │  │             │ │
│              │                      │  │ health: 0   │ │
│              │ Showing 1-50 of 120  │  │ mana: 0     │ │
│              │ [<] [1][2][3] [>]    │  │ ...         │ │
│              │                      │  │             │ │
│              │                      │  │ [Save][Cncl]│ │
│              │                      │  └─────────────┘ │
└──────────────┴──────────────────────┴───────────────────┘
```

---

## Option 2: Terminal UI (TUI) Application

### Framework Comparison

#### A. **Rich** (Modern Python TUI)

**Pros:**
- ✅ Beautiful, modern styling
- ✅ Colors, tables, progress bars
- ✅ Great for output/display
- ✅ Easy to use

**Cons:**
- ❌ Limited interactivity
- ❌ Not designed for complex forms
- ❌ No built-in navigation widgets

**Rating:** ⭐⭐⭐ (3/5) - Great for display, not for editing

---

#### B. **Textual** (Modern TUI Framework)

**Pros:**
- ✅ Built on Rich (beautiful styling)
- ✅ Reactive, component-based
- ✅ Mouse support
- ✅ CSS-like styling
- ✅ Great performance
- ✅ Modern paradigm (like React)
- ✅ Active development

**Cons:**
- ❌ Relatively new (2021+)
- ❌ Smaller community
- ❌ Limited complex widgets (improving)

**Rating:** ⭐⭐⭐⭐⭐ (5/5) - Best modern TUI framework

---

#### C. **urwid** (Traditional TUI)

**Pros:**
- ✅ Mature and stable
- ✅ Good widget library
- ✅ Used in production apps

**Cons:**
- ❌ Older, less modern look
- ❌ More complex API
- ❌ Limited styling

**Rating:** ⭐⭐⭐ (3/5) - Functional but dated

---

#### D. **py_cui** (Simple TUI)

**Pros:**
- ✅ Simple and lightweight
- ✅ Easy to learn

**Cons:**
- ❌ Very basic
- ❌ Limited widgets
- ❌ Not actively developed

**Rating:** ⭐⭐ (2/5) - Too simple for our needs

---

### TUI Recommendation: **Textual**

**Why Textual?**
1. **Modern Look** - Beautiful, styled terminal UI
2. **Mouse Support** - Click on items, scroll, etc.
3. **Good Performance** - Handles large datasets
4. **Active Development** - Rapidly improving
5. **Component-based** - Easy to organize

**UI Layout:**

```
╭─────────────────────────────────────────────────────────────────╮
│ SpellForce CFF Editor                                      v1.0 │
├─────────────────────────────────────────────────────────────────┤
│ File: GameData.cff                         [Open] [Save] [Quit] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ╭─Categories───╮ ╭─Elements─────────────╮ ╭─Properties──────╮ │
│ │              │ │                      │ │                 │ │
│ │ ▶ Spells     │ │  ID    Name     Type │ │ item_id: 531   │ │
│ │ ▼ Items      │ │ ─────────────────── │ │ name: Soulguard│ │
│ │   ▶ Armor    │ │  531   Soulguard  R │ │                │ │
│ │   ▶ Weapons  │ │  532   Ruby Ring  R │ │ item_type:     │ │
│ │ ▶ Creatures  │ │  537   Antique... R │ │  EQUIPMENT     │ │
│ │ ▶ Buildings  │ │  ...                │ │                │ │
│ │ ...          │ │                     │ │ health: 0      │ │
│ │              │ │ Search: ________    │ │ mana: 0        │ │
│ │ [43 total]   │ │                     │ │ stamina: 0     │ │
│ │              │ │ Page 1/3            │ │ ...            │ │
│ │              │ │                     │ │                │ │
│ ╰──────────────╯ ╰─────────────────────╯ │ [Save] [Cancel]│ │
│                                           ╰─────────────────╯ │
│                                                                 │
│ Status: Ready                                    Memory: 97 MB │
╰─────────────────────────────────────────────────────────────────╯
```

---

## Comparison: GUI vs TUI

### Feature Comparison

| Feature | PyQt6 (GUI) | Textual (TUI) |
|---------|-------------|---------------|
| **Visual Appeal** | ⭐⭐⭐⭐⭐ Professional | ⭐⭐⭐⭐ Modern terminal |
| **Ease of Use** | ⭐⭐⭐⭐⭐ Mouse, native | ⭐⭐⭐⭐ Keyboard/mouse |
| **Performance** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very good |
| **Large Tables** | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐⭐⭐ Good |
| **Installation** | ⭐⭐⭐ pip install PyQt6 | ⭐⭐⭐⭐⭐ pip install textual |
| **Learning Curve** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ Easier |
| **File Dialogs** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Custom |
| **Dropdowns** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Custom |
| **Tables/Lists** | ⭐⭐⭐⭐⭐ QTableView | ⭐⭐⭐⭐ DataTable |
| **Portability** | ⭐⭐⭐⭐ Desktop only | ⭐⭐⭐⭐⭐ SSH friendly |
| **Deployment** | ⭐⭐⭐ ~50MB app | ⭐⭐⭐⭐⭐ Small script |
| **Maturity** | ⭐⭐⭐⭐⭐ 25+ years | ⭐⭐⭐ 3 years |

---

## Recommendation

### **Primary: PyQt6 GUI Application**

**Reasons:**
1. ✅ **Better UX** - Native file dialogs, dropdown menus, tooltips
2. ✅ **Table Performance** - QTableView handles 176k entries smoothly
3. ✅ **Professional** - Users expect GUI for data editing
4. ✅ **Validation** - Easier to implement complex form validation
5. ✅ **Rich Editing** - Better support for complex field types

**Best For:**
- Primary editor tool
- Users who want full features
- Complex data manipulation

---

### **Secondary: Textual TUI Application**

**Reasons:**
1. ✅ **Lightweight** - No GUI dependencies
2. ✅ **SSH-Friendly** - Work remotely via terminal
3. ✅ **Quick Launch** - Fast startup
4. ✅ **Scriptable** - Can be automated

**Best For:**
- Quick edits
- Remote server work
- Advanced users who prefer terminal
- Complement to GUI version

---

## Development Plan

### Phase 1: Core Functionality (GUI - PySide6) ✅ COMPLETE
- See [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md) for details

### Phase 2: Advanced Features ⏳ PENDING
- See [GUI_EDITOR_PLAN.md](./GUI_EDITOR_PLAN.md) for details

### Phase 3: TUI Version (Textual) ⏳ PENDING
- See [TUI_EDITOR_PLAN.md](./TUI_EDITOR_PLAN.md) for details

## Data Extraction and Analysis ✅ COMPLETE
- See [DATA_EXTRACTION_PLAN.md](./DATA_EXTRACTION_PLAN.md) for details

---

## Technical Architecture

### Data Layer
```python
class CFFDataModel:
    """Manages loaded CFF data"""
    def __init__(self, cff_path):
        self.game_data = GameData(cff_path)
        self.modified = False
        self.undo_stack = []

    def get_categories(self) -> List[str]:
        """Returns list of all tables"""

    def get_elements(self, category: str) -> List[Entity]:
        """Returns all elements in category"""

    def get_element_details(self, category: str, element_id: int) -> Dict:
        """Returns element properties"""

    def update_element(self, category: str, element_id: int, changes: Dict):
        """Applies changes to element"""

    def save(self, path: str):
        """Saves modified CFF"""
```

### GUI Layer (PyQt6)
```python
class MainWindow(QMainWindow):
    """Main application window"""
    - MenuBar (File, Edit, View, Tools, Help)
    - CategoryTreeWidget (left panel)
    - ElementTableWidget (center panel)
    - PropertyEditorWidget (right panel)
    - StatusBar (file info, memory usage)

class CategoryTreeWidget(QTreeWidget):
    """Displays 43 categories with counts"""

class ElementTableWidget(QTableView):
    """Displays elements in selected category"""
    - Sortable columns
    - Search box
    - Pagination

class PropertyEditorWidget(QWidget):
    """Displays/edits element properties"""
    - Auto-generates form fields
    - Type-specific widgets (spinbox, combobox, lineedit)
    - Save/Cancel buttons
```

### TUI Layer (Textual)
```python
class CFFEditorApp(App):
    """Main TUI application"""
    - CategoryList (left panel)
    - ElementDataTable (center panel)
    - PropertyEditor (right panel)

class CategoryList(ListView):
    """Category selection"""

class ElementDataTable(DataTable):
    """Element list with search"""

class PropertyEditor(Container):
    """Property editing form"""
```

---

## Dependency Analysis

### PyQt6 GUI
```bash
pip install PyQt6
# Size: ~50 MB
# License: GPL v3 (or commercial)
```

### PySide6 GUI (Alternative - LGPL)
```bash
pip install PySide6
# Size: ~50 MB
# License: LGPL (more permissive)
```

### Textual TUI
```bash
pip install textual
# Size: ~5 MB
# License: MIT
```

**Recommendation:** Use **PySide6** for GUI (better license than PyQt6)

---

## File Structure

```
H:\SpellSmut\src\TirganachReloaded\
├── gui_editor/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models.py            # Data models
│   ├── widgets/
│   │   ├── category_tree.py
│   │   ├── element_table.py
│   │   └── property_editor.py
│   ├── dialogs/
│   │   ├── about.py
│   │   └── preferences.py
│   └── resources/
│       ├── icons/
│       └── styles.qss       # Qt stylesheet
│
├── tui_editor/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── widgets/
│   │   ├── category_list.py
│   │   ├── element_table.py
│   │   └── property_form.py
│   └── styles.css           # Textual CSS
│
└── shared/
    ├── data_model.py        # Shared data layer
    └── validators.py        # Field validation
```

---

## Next Steps

### Immediate Actions

1. **Choose Approach**
   - ✅ Primary: PySide6 GUI
   - ✅ Secondary: Textual TUI (later)

2. **Install Dependencies**
   ```bash
   pip install PySide6
   pip install textual
   ```

3. **Create Prototype**
   - Basic window with 3 panels
   - Load CFF file
   - Display categories
   - Show elements
   - View properties

4. **Iterate**
   - Add search/filter
   - Add editing
   - Add save functionality
   - Polish UI

---

## Questions for You

1. **Which do you prefer to start with?**
   - A) GUI (PySide6) - Full-featured, professional
   - B) TUI (Textual) - Lightweight, terminal-based
   - C) Both in parallel (more work)

2. **Priority features?**
   - Must-have: View, Edit, Save
   - Nice-to-have: Add, Clone, Delete, Compare, Undo/Redo

3. **Dark mode preference?**
   - Yes (modern look)
   - No (light theme)
   - Both (switchable)

4. **Target users?**
   - Just you (optimize for your workflow)
   - Community release (more polish needed)

---

## Conclusion

**Recommended Path:**
1. ✅ Start with **PySide6 GUI** for full-featured editor
2. ✅ Focus on core functionality (view, edit, save)
3. ✅ Add **Textual TUI** version later for quick edits
4. ✅ Keep both versions sharing the same data model

**Timeline:**
- Week 1-4: Working GUI editor
- Week 5-7: Advanced features
- Week 8-9: TUI version (optional)

**Effort:**
- GUI: Medium complexity, high usability
- TUI: Lower complexity, good for quick tasks
- Both: Best of both worlds!

Let me know which direction you'd like to pursue! 🚀
