# Conditions & Flags - Quick Reference

## Launch Quest Editor

```bash
uv run quest_creator.py
```

Then go to: **🔧 Conditions & Flags** tab

---

## Flag Manager (Top Panel)

### Add New Flag

1. Click **➕ Add Flag**
2. Enter flag name (follow naming hints)
3. Select type:
   - **Global** - World state (e.g., `QuestComplete`, `BossDead`)
   - **Item** - Item possession (e.g., `PlayerHasItemSword`)
   - **NPC** - NPC interactions (e.g., `n_Guard_Talked`)
4. Add description
5. Click **OK**

### Naming Conventions

- **Item Flags**: Start with `PlayerHasItem` (e.g., `PlayerHasItemSanduhr`)
- **NPC Flags**: Start with `n_` or NPC name (e.g., `n_P213_Talked`, `ShanMuirGreeted`)
- **Global Flags**: Descriptive name (e.g., `TrollCampDestroyed`, `AmraUndLea1Complete`)

### Search & Filter

- **Search box**: Type to search by name/description
- **Type filter**: Filter by Global/Item/NPC
- **Double-click**: Edit flag

---

## Condition Builder (Bottom Panel)

### Add Simple Condition

1. Click **➕ Add Condition**
2. Select type:
   - **QuestState**: Check quest status (Active/Solved/Failed)
   - **ItemFlag**: Check if item flag is true/false
   - **NpcFlag**: Check if NPC flag is true/false
   - **GlobalFlag**: Check if global flag is true/false
   - **TimeDay**: Check if daytime
   - **TimeNight**: Check if nighttime
3. Fill in parameters
4. Check **Negate** to invert (NOT)
5. Click **OK**

### Add Logical Group (AND/OR)

1. Click **➕ Add Group (AND/OR)**
2. Select operator:
   - **UND (AND)**: All children must be true
   - **ODER (OR)**: Any child must be true
3. Check **Negate** to invert entire group
4. Click **OK**
5. Add conditions to the group

### Using Flags in Conditions

1. Select `ItemFlag`, `NpcFlag`, or `GlobalFlag`
2. Click **🔍 Browse** button
3. Select flag from list
4. Choose if flag should be **true** or **false**

### Preview LUA Code

Click **👁️ Preview LUA** to see generated SpellForce code

---

## Common Patterns

### Quest Available After Previous Quest

```
UND(
    QuestState{QuestId = 646, State = StateSolved}
)
```

### Player Has Item

```
IsItemFlagTrue{Name = "PlayerHasItemSanduhr"}
```

### Quest Active + Item Owned

```
UND(
    QuestState{QuestId = 100, State = StateActive},
    IsItemFlagTrue{Name = "PlayerHasItemKey"}
)
```

### Daytime OR Special Event

```
ODER(
    TimeDay(),
    IsGlobalFlagTrue{Name = "SpecialEvent"}
)
```

### NOT (Quest Complete)

```
Negated(QuestState{QuestId = 100, State = StateSolved})
```

---

## Keyboard Shortcuts

- **Double-click condition**: Edit
- **Delete key**: Remove selected (when available)

---

## Tips

1. **Build Complex Conditions Incrementally**: Start simple, add groups as needed
2. **Use Descriptive Flag Names**: Makes debugging easier
3. **Check Flag Usage**: See which quests use each flag in Flag Manager
4. **Preview Often**: Click Preview LUA to verify logic
5. **Test Conditions**: Use simple conditions first, then combine

---

## Example: Timed Quest Chain

```
Flags:
- Quest646Complete (global)
- PlayerHasItemSanduhr (item)
- TimeRequirement (global)

Condition:
UND(
    IsGlobalFlagTrue{Name = "Quest646Complete"},
    IsItemFlagTrue{Name = "PlayerHasItemSanduhr"},
    TimeDay()
)
```

This condition means: "Previous quest done + player has item + it's daytime"

---

## Troubleshooting

**Condition not showing in tree?**
→ Make sure you clicked OK in the dialog

**Flag not in browse list?**
→ Add the flag in Flag Manager first

**Can't edit condition?**
→ Double-click the condition row

**LUA looks wrong?**
→ SpellForce uses binary operators - nesting is normal!

---

## Data Location

Flags and conditions are saved to:
```
quest_data[quest_id]["flags"]      # Flag definitions
quest_data[quest_id]["conditions"]  # Condition tree
```

Auto-saved to: `~/.spellmut/quests/quest_{id}.json`
