# SpellForce Campaign Selection & Modding Analysis

## Overview
This document analyzes how SpellForce handles campaign selection and provides a roadmap for adding custom campaigns to the game. Based on analysis of both the C# data editor and Lua sources.

## Current Campaign Structure

### Campaign Organization
From the Lua sources, we can see SpellForce uses a map-based campaign structure:

```
map/
├── Campaign/          # Original Campaign 1 (The Order of Dawn)
├── Campaign2/         # Campaign 2 (The Breath of Winter)  
├── Campaign3/         # Campaign 3 (Shadow of the Phoenix)
├── Lan/              # LAN/MP maps
└── test/             # Test maps
```

### Campaign 3 Maps (Example from SndTracks.lua)
```
Campaign3/
├── P200_Collosseum.map
├── P201_Blackwater_Coast.map  
├── P202_City_Of_Souls.map
├── P203_Onyx_Shores.map
├── P204_Empyria.map
├── P205_Dryad_Cove.map
├── P206_Red_Waste.map
├── P207_Raven_Pass.map
├── P208_Blazing_Stones.map
├── P209_Kathai.map
├── P210_The_Clockwork_Crypts.map
├── P211_Darkwind_Keep.map
├── P212_The_Gorge.map
└── P213_The_Bone_Temple.map
```

## Campaign Selection System Analysis

### Current Implementation
The campaign selection appears to be handled at the engine level (C++), not in Lua scripts. The data editor doesn't contain campaign selection UI code, suggesting it's part of the original game's frontend.

### Map Loading Pattern
From `TestSpawn.lua`, we can see the world name parsing:
```lua
local worldname = GdMain:GetWorldPtr():GetWorldName()
worldname = gsub(worldname, ".map", "")
worldname = gsub(worldname, "map\\Campaign\\", "")
worldname = gsub(worldname, "map\\Lan\\", "")  
worldname = gsub(worldname, "map\\test\\", "")
```

This suggests the game identifies campaigns by the map path prefix.

## Modding Approach: Custom Campaign Addition

### Option 1: Map Directory Method (Recommended)

#### Step 1: Create Campaign Directory
```
map/
└── CustomCampaign/    # Your custom campaign
    ├── P100_YourFirstMap.map
    ├── P101_YourSecondMap.map
    └── ...
```

#### Step 2: Add Sound Definitions
Create entries in `SndTracks.lua`:
```lua
-- Custom Campaign Maps
SndDefineMapPlain{Map = "map\\CustomCampaign\\P100_YourFirstMap.map", PlainId = 33}
SndDefineMapPlain{Map = "map\\CustomCampaign\\P101_YourSecondMap.map", PlainId = 33}
```

#### Step 3: Map Script Integration
Each map needs corresponding Lua scripts in:
```
script/
└── P100/            # Custom campaign map scripts
    ├── Ai.lua
    ├── n0.lua       # Main quest logic
    ├── n1.lua       # Additional quests
    └── ...
```

### Option 2: Campaign Injection via Data Editor

#### Step 1: Campaign Definition Category
We could add a new category to the data editor:
```csharp
// New category for campaign definitions
public class Category3000 : CategoryBaseSingle<Category3000Item>
{
    public override string GetName() => "Campaign Definitions";
    public override short GetCategoryID() => 3000;
    public override short GetCategoryType() => 1;
}

public struct Category3000Item : ICategoryItem
{
    public ushort CampaignID;
    public fixed byte CampaignName[64];
    public fixed byte StartMap[256];
    public byte CampaignType; // 1=SP, 2=MP, 3=Custom
    public byte IsActive;
}
```

#### Step 2: Frontend Integration Points
The campaign selection UI would need to be modified to read from this new category and display custom campaigns alongside the original ones.

## Implementation Strategy

### Phase 1: Map-Based Campaign (Easiest)
1. **Create Custom Campaign Directory Structure**
2. **Add Map Files** with proper naming convention (P100, P101, etc.)
3. **Create Lua Scripts** for each map
4. **Add Sound Definitions** to SndTracks.lua
5. **Test Map Loading** via console commands

### Phase 2: Data Editor Integration
1. **Add Campaign Category** to the data editor
2. **Create Campaign Management UI** in the data editor
3. **Implement Campaign Export/Import** functionality
4. **Add Campaign Validation** tools

### Phase 3: Frontend Integration (Advanced)
1. **Decompile/Analyze Original Game Frontend**
2. **Add Custom Campaign Button** to main menu
3. **Implement Campaign Selection Logic**
4. **Add Campaign Progression Tracking**

## Technical Requirements

### Map Development
- **Map Editor**: Use the existing MapEditorForm in the data editor
- **Script Integration**: Each map needs corresponding Lua scripts in script/ directory
- **Sound Integration**: Add map sound definitions to SndTracks.lua
- **Testing**: Use TestSpawn.lua system for testing

### Script Development
- **Quest System**: Follow existing quest naming conventions (n0.lua, n1.lua, etc.)
- **AI Scripts**: Each map needs Ai.lua for enemy behavior
- **Cutscenes**: Use existing cutscene naming patterns
- **Save Integration**: Ensure proper save/load functionality

### Data Integration
- **Entity References**: Use existing entity IDs from GameData.cff
- **Item Integration**: Leverage existing item system
- **Character Integration**: Use existing character/hero system
- **Building Integration**: Utilize existing building types

## File Structure for Custom Campaign

```
ProjectRoot/
├── map/
│   └── MyCustomCampaign/
│       ├── P100_Intro.map
│       ├── P101_FirstTown.map
│       └── P102_BossBattle.map
├── script/
│   ├── P100/
│   │   ├── Ai.lua
│   │   ├── n0.lua
│   │   └── custom_quest_1.lua
│   ├── P101/
│   │   ├── Ai.lua
│   │   ├── n0.lua
│   │   └── town_dialogue.lua
│   └── P102/
│       ├── Ai.lua
│       ├── n0.lua
│       └── boss_logic.lua
└── data/
    └── custom_campaign_data.cff (optional)
```

## Development Tools Integration

### Data Editor Enhancements
1. **Campaign Manager Form**: New form for managing custom campaigns
2. **Map Validation**: Tools to check map-script consistency
3. **Campaign Export**: Package custom campaigns for distribution
4. **Debug Tools**: Enhanced debugging for custom campaigns

### Lua Development Tools
1. **Script Templates**: Templates for new map scripts
2. **Quest Editor**: Visual quest creation tools
3. **Dialogue Editor**: Tools for creating character dialogues
4. **Testing Framework**: Automated testing for campaign scripts

## Next Steps

### Immediate Actions (Map-Based Approach)
1. **Create Custom Campaign Directory**: `map/CustomCampaign/`
2. **Create Test Map**: Simple map with basic objectives
3. **Add Basic Scripts**: Minimal Ai.lua and n0.lua
4. **Test Loading**: Verify map loads correctly
5. **Add Sound Definitions**: Update SndTracks.lua

### Medium Term (Data Editor Integration)
1. **Design Campaign Category Structure**: Define data format
2. **Implement Campaign Manager UI**: Create management interface
3. **Add Campaign Validation**: Ensure data integrity
4. **Create Export/Import System**: Package campaigns for sharing

### Long Term (Frontend Integration)
1. **Reverse Engineer Frontend**: Understand campaign selection UI
2. **Implement Custom Campaign Button**: Add to main menu
3. **Add Campaign Progression**: Track player progress
4. **Integrate with Save System**: Proper save/load support

## Conclusion

The most feasible approach for adding custom campaigns is the **map-based method**, which leverages existing game systems without requiring frontend modifications. This approach:

- ✅ **Requires minimal engine changes**
- ✅ **Leverages existing map/script systems**  
- ✅ **Can be implemented immediately**
- ✅ **Supports full campaign functionality**
- ❌ **Requires manual map selection** (no frontend button initially)

The data editor can be enhanced to provide tools for creating and managing these custom campaigns, making the process much more user-friendly for modders.
