# Enhanced Objectives - Quick Reference

## Launch Quest Editor

```bash
uv run quest_creator.py
```

Then go to: **Objectives** tab

---

## Enhanced Objective Types

### 💬 Talk to NPC
**Use:** Quest givers, dialogue triggers, information gathering

**Fields:**
- **Target ID:** NPC ID number
- **Target Name:** Auto-filled from NPC browser
- **Browse:** Click "🔍 Browse NPCs..." to select

**Example:** `💬 Talk to Shan Muir`

**How to Use:**
1. Click "Add Objective"
2. Select "💬 Talk to NPC"
3. Click "🔍 Browse NPCs..."
4. Search and select NPC
5. Add description (optional)
6. Click OK

---

### ⚔️ Kill Target
**Use:** Combat objectives, boss fights, clearing areas

**Fields:**
- **Target ID:** Enemy/creature ID
- **Target Name:** Enemy name (manual for now)
- **Quantity:** Number to kill (1-999)
- **Browse:** Click "🔍 Browse Enemies..." (placeholder)

**Example:** `⚔️ Kill 3x Troll Chieftain`

**How to Use:**
1. Click "Add Objective"
2. Select "⚔️ Kill Target"
3. Enter enemy ID manually (or wait for enemy browser)
4. Set quantity
5. Add description
6. Click OK

---

### 📦 Gather Items
**Use:** Collection quests, crafting materials, gathering resources

**Fields:**
- **Target ID:** Item ID number
- **Target Name:** Item name (manual for now)
- **Quantity:** Number to gather (1-999)
- **Browse:** Click "🔍 Browse Items..." (placeholder)

**Example:** `📦 Gather 5x Magic Herbs`

**How to Use:**
1. Click "Add Objective"
2. Select "📦 Gather Items"
3. Enter item ID manually (or wait for item browser)
4. Set quantity
5. Add description
6. Click OK

---

### 🗺 Explore Location
**Use:** Discovery quests, area exploration, finding locations

**Fields:**
- **Location:** Location name to explore
- **Target:** Hidden (not used)

**Example:** `🗺 Explore Ancient Ruins`

**How to Use:**
1. Click "Add Objective"
2. Select "🗺 Explore Location"
3. Enter location name
4. Add description
5. Click OK

---

### 👥 Escort NPC
**Use:** Protection quests, delivery missions, guiding NPCs

**Fields:**
- **Target ID:** NPC ID to escort
- **Target Name:** NPC name (from browser)
- **Location:** Destination location
- **Browse:** Click "🔍 Browse NPCs..." for NPC selection

**Example:** `👥 Escort Merchant Caravan to Liannon`

**How to Use:**
1. Click "Add Objective"
2. Select "👥 Escort NPC"
3. Click "🔍 Browse NPCs..." to select NPC
4. Enter destination location
5. Add description
6. Click OK

---

### 📝 Custom Objective
**Use:** Special objectives, unique conditions, custom text

**Fields:**
- **Objective Text:** Free-form text entry
- **Description:** Detailed explanation

**Example:** `📝 Find the lost artifact`

**How to Use:**
1. Click "Add Objective"
2. Select "📝 Custom Objective"
3. Enter objective text
4. Add description
5. Click OK

---

## Objective Management

### Adding Objectives
1. Click **Add Objective** button
2. Choose objective type from dropdown
3. Fill in type-specific fields
4. Click **OK** to add to quest

### Editing Objectives
1. **Double-click** objective in list to edit
2. Modify fields as needed
3. Click **OK** to save changes

### Removing Objectives
1. Select objective in list
2. Click **Remove Selected** button
3. Confirm deletion

### Reordering Objectives
1. Select objective
2. Use **Up/Down arrow keys** (if available) or
3. Remove and re-add in desired order

---

## Browser Integration

### NPC Browser (Working)
- **Full Search:** By name, ID, location
- **German Names:** Primary language with English fallback
- **Multi-select:** Choose multiple NPCs if needed
- **Auto-fill:** Sets NPC ID and name automatically

### Enemy Browser (Placeholder)
- **Status:** Shows info dialog for now
- **Future:** Will show enemy stats, levels, locations
- **Manual Entry:** Enter enemy ID directly

### Item Browser (Placeholder)
- **Status:** Shows info dialog for now
- **Future:** Will show item icons, stats, categories
- **Manual Entry:** Enter item ID directly

---

## Display Format

### Enhanced Icons
- 💬 Talk objectives
- ⚔️ Kill objectives  
- 📦 Gather objectives
- 🗺 Explore objectives
- 👥 Escort objectives
- 📝 Custom objectives

### Automatic Display Text
- **Talk:** `💬 Talk to {NPC Name}`
- **Kill:** `⚔️ Kill {quantity}x {Enemy Name}`
- **Gather:** `📦 Gather {quantity}x {Item Name}`
- **Explore:** `🗺 Explore {Location}`
- **Escort:** `👥 Escort {NPC Name} to {Location}`
- **Custom:** `📝 {Custom Text}`

---

## Data Structure

### Saved Objective Data
```json
{
    "type": "talk",
    "text": "Custom text (for other type)",
    "target_id": 213,
    "target_name": "Shan Muir",
    "quantity": 1,
    "location": "Liannon",
    "description": "Detailed description of objective"
}
```

### Backward Compatibility
- **Old Format:** `[type] text` still loads correctly
- **Enhanced Display:** Attempts to show formatted version
- **Migration:** No data migration needed

---

## Tips and Best Practices

### Objective Naming
- **Be Specific:** "Talk to Guard Captain" vs "Talk to guard"
- **Include Quantities:** "Gather 5 herbs" vs "Gather herbs"
- **Clear Locations:** "Explore Ancient Ruins" vs "Explore ruins"

### Browser Usage
- **Use Search:** Filter by name or ID quickly
- **Check German Names:** Often more complete than English
- **Verify Selection:** Double-check NPC/item is correct

### Description Writing
- **Add Context:** Why is this objective important?
- **Include Hints:** Where to find target, what to expect
- **Keep Concise:** One or two sentences maximum

### Quest Design
- **Logical Flow:** Objectives should progress naturally
- **Clear Prerequisites:** Player should know what to do next
- **Reasonable Quantities:** Don't require 100 of rare items

---

## Troubleshooting

### Browser Not Available
- **NPC Browser:** Should work with existing system
- **Enemy/Item Browsers:** Show placeholder dialogs
- **Solution:** Enter IDs manually for now

### Objective Not Saving
- **Check Required Fields:** Target ID for talk/kill/gather
- **Check Location:** Required for explore/escort
- **Check Text:** Required for custom objectives

### Display Issues
- **Old Objectives:** May show as `[type] text` format
- **Solution:** Edit objective to update display
- **Enhanced Display:** Only works with new editor

---

## Examples

### Example Quest: "The Missing Merchant"

**Objectives:**
1. `💬 Talk to Guard Captain` (Get information)
2. `🗺 Explore Bandit Hideout` (Find location)
3. `⚔️ Kill 3x Bandit Leader` (Remove threat)
4. `👥 Escort Merchant to Liannon` (Complete quest)

**Data Structure:**
```json
[
    {
        "type": "talk",
        "target_id": 156,
        "target_name": "Guard Captain",
        "description": "Get information about missing merchant"
    },
    {
        "type": "explore",
        "location": "Bandit Hideout",
        "description": "Search the bandit hideout for clues"
    },
    {
        "type": "kill",
        "target_id": 892,
        "target_name": "Bandit Leader",
        "quantity": 3,
        "description": "Defeat the bandit leader and his guards"
    },
    {
        "type": "escort",
        "target_id": 445,
        "target_name": "Merchant",
        "location": "Liannon",
        "description": "Safely escort the merchant back to town"
    }
]
```

---

## Testing

### Test Enhanced Objectives
```bash
uv run python test_objectives.py
```

This opens a test window where you can:
- Try all 6 objective types
- Test NPC browser integration
- Verify display formatting
- Test data persistence

---

## Future Enhancements

### Planned (Not Yet Implemented)

1. **Enemy Browser Implementation**
   - Enemy stats and levels
   - Location-based filtering
   - Group by enemy type

2. **Item Browser Integration**
   - Use existing item browser widget
   - Show item icons and stats
   - Filter by category/type

3. **Objective Templates**
   - Pre-built common patterns
   - Quick-add for frequent types
   - Customizable templates

4. **Objective Dependencies**
   - Link objectives (prerequisites)
   - Visual dependency graph
   - Auto-suggest next objectives

---

## Summary

The Enhanced Objectives system provides:

✅ **Type-specific editors** for all 6 objective types  
✅ **Browser integration** with existing NPC system  
✅ **Enhanced display** with icons and formatting  
✅ **Backward compatibility** with existing objectives  
✅ **Comprehensive testing** and validation  

**Result:** Much more detailed and user-friendly objective creation compared to basic text input.
