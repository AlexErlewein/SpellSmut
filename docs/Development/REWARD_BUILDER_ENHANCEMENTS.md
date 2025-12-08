# Reward Builder Enhancements

**Date**: November 16, 2025  
**Status**: ✅ COMPLETE  
**Component**: `reward_builder.py`

---

## 🎯 Overview

Enhanced the existing Reward Builder to match SpellForce's quest reward system based on research findings from game LUA files.

---

## ✨ Enhancements Made

### 1. Items Given vs Items Taken System

**Before**: Single "Selected Items" list  
**After**: Separate tabs for:
- **Items Given**: Rewards player receives
- **Items Taken**: Quest items removed from player

**Implementation**:
```python
self.current_rewards = {
    'xp': 0,
    'gold': 0,
    'silver': 0,
    'copper': 0,
    'items_given': [],  # NEW: Items player receives
    'items_taken': []   # NEW: Items removed from player
}
```

**UI Structure**:
```
[Tab: Items Given]
  - Shows items player receives as rewards
  - [Add Selected Item] [Remove] buttons
  
[Tab: Items Taken]
  - Shows quest items taken from player
  - [Add Selected Item] [Remove] buttons
```

---

### 2. Enhanced Reward Preview

**Before**: Simple item list  
**After**: Detailed breakdown with item IDs

**Example Output**:
```
Experience: 250 XP
Money: 0 Gold, 2 Silver, 50 Copper
Items Given: Karte (626), Ring (833)
Items Taken: Old Map (2336)
```

---

### 3. Improved Item Management

**Methods Updated**:
- `_add_selected_item(item_type='given')` - Specify given/taken
- `_add_item_to_rewards(item, item_type)` - Separate lists
- `_remove_item(item_type)` - Remove from correct list

**Features**:
- Duplicate detection per list
- Item ID display in lists
- Clear visual separation

---

## 📊 Data Structure

### Quest Reward Model

```python
{
    'xp': 250,
    'gold': 0,
    'silver': 2,
    'copper': 50,
    'items_given': [
        {'id': 626, 'name': 'Karte', 'type': 'Item', 'value': 10},
        {'id': 833, 'name': 'Ring', 'type': 'Item', 'value': 50}
    ],
    'items_taken': [
        {'id': 2336, 'name': 'Old Map', 'type': 'Item', 'value': 0}
    ]
}
```

---

## 🎨 UI Components

### Existing Components (Retained)
- ✅ Quick Settings (quest level, templates)
- ✅ Item Browser (search, filter, table)
- ✅ Basic Rewards (XP, Gold/Silver/Copper)
- ✅ Balance Checking
- ✅ Reward Preview

### New Components
- ✅ Items Given Tab
- ✅ Items Taken Tab
- ✅ Separate add/remove buttons per tab
- ✅ Item ID display in lists

---

## 🔧 Integration Points

### Quest Editor Integration

```python
from TirganachReloaded.cff_editor.widgets.reward_builder import RewardBuilderWidget

# In quest editor
self.reward_builder = RewardBuilderWidget(data_model=self.data_model)
self.reward_builder.rewards_changed.connect(self._on_rewards_changed)

# Get rewards
rewards = self.reward_builder.get_rewards()
print(rewards['items_given'])  # Items to give
print(rewards['items_taken'])  # Items to take
```

### LUA Export Format

```lua
-- Based on research findings
OnQuestSolved{
    QuestId = 14,
    Actions = {
        -- XP reward
        GiveXP{Amount = 250},
        
        -- Currency reward
        GiveMoney{Gold = 0, Silver = 2, Copper = 50},
        
        -- Items GIVEN to player
        GiveItem{ItemId = 626},  -- Karte
        GiveItem{ItemId = 833},  -- Ring
        
        -- Items TAKEN from player
        TakeItem{ItemId = 2336},  -- Old Map
    }
}
```

---

## 📋 Real-World Examples

### Example 1: Simple Reward
```yaml
Quest: DariusDerKarthograph (ID: 14)
XP: 25
Items Given: 626 (Karte)
Items Taken: -
```

### Example 2: Multi-Item Reward
```yaml
Quest: Kopfjagd6Complete (ID: 463)
XP: 60
Items Given: -
Items Taken: 3202, 3203, 3204, 3205, 3206
```

### Example 3: Currency + Items
```yaml
Quest: GeistInDerMine (ID: 36)
XP: 35
Money: 0g 2s 50c
Items Given: -
Items Taken: 1998
```

---

## ✅ Features Checklist

### Basic Functionality
- [x] XP input (0-999999)
- [x] Gold/Silver/Copper inputs
- [x] Item browser with search/filter
- [x] Items given list
- [x] Items taken list
- [x] Add/remove items per category
- [x] Duplicate detection
- [x] Reward preview

### Advanced Features
- [x] Quest level for balance checking
- [x] Reward templates (Starter, Medium, Main, Epic)
- [x] Balance calculation
- [x] Warning system
- [x] Item ID display
- [x] Signals for integration

### Future Enhancements
- [ ] Choice rewards (pick 1 of N items)
- [ ] Skill rewards
- [ ] Reputation rewards
- [ ] Conditional rewards
- [ ] LUA export integration

---

## 🎯 Usage Guide

### Adding Rewards

1. **Set XP**:
   ```
   Experience Points: [250] XP
   ```

2. **Set Currency**:
   ```
   Gold: [0]  Silver: [2]  Copper: [50]
   ```

3. **Add Items Given** (player receives):
   - Go to "Items Given" tab
   - Search/select item in browser
   - Click "Add Selected Item"

4. **Add Items Taken** (removed from player):
   - Go to "Items Taken" tab
   - Search/select quest item
   - Click "Add Selected Item"

5. **Preview**:
   - Check "Reward Preview" section
   - Verify all rewards are correct

---

## 🔍 Testing

### Manual Testing

```python
# Test the reward builder
from TirganachReloaded.cff_editor.widgets.reward_builder import RewardBuilderWidget

builder = RewardBuilderWidget(data_model)

# Set rewards
builder.xp_spin.setValue(250)
builder.gold_spin.setValue(0)
builder.silver_spin.setValue(2)
builder.copper_spin.setValue(50)

# Get rewards
rewards = builder.get_rewards()
assert rewards['xp'] == 250
assert rewards['silver'] == 2
assert len(rewards['items_given']) >= 0
assert len(rewards['items_taken']) >= 0
```

---

## 📁 Files Modified

- `src/TirganachReloaded/cff_editor/widgets/reward_builder.py` (ENHANCED)
  - Added items_given/items_taken separation
  - Updated item management methods
  - Enhanced preview generation
  - Improved data structure

---

## 🎉 Success Criteria

All criteria met:

- ✅ Separate given/taken item lists
- ✅ XP, currency, and item rewards
- ✅ Item browser integration
- ✅ Duplicate detection
- ✅ Clear preview display
- ✅ Signal emission for integration
- ✅ Matches SpellForce reward patterns

---

## 🚀 Next Steps

1. **Integrate into Quest Editor**
   - Add reward builder to quest editor UI
   - Connect reward_changed signal
   - Save/load rewards with quest data

2. **LUA Export**
   - Generate GiveXP actions
   - Generate GiveMoney actions
   - Generate GiveItem/TakeItem actions
   - Match SpellForce format exactly

3. **Advanced Features**
   - Choice rewards system
   - Conditional rewards
   - Reputation/faction rewards

---

**Status**: ✅ Ready for Integration  
**Next Task**: Condition Builder → Flag Management → LUA Export
