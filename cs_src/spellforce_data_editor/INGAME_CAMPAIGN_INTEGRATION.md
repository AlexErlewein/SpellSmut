# In-Game Custom Campaign Integration

## Overview
Instead of creating an external GUI, we've integrated custom campaign functionality directly into SpellForce's in-game UI system. This approach modifies the existing Lua scripts to add custom campaign capabilities.

## Implementation Details

### 1. 🎮 Modified UiInit.lua
- **File**: `script/UiInit.lua`
- **Changes**: Repurposed Button3 as a "CUSTOM" campaign button
- **Functionality**: Clicking triggers custom campaign menu
- **Integration**: Uses existing button system with custom click handler

### 2. 🔧 CustomCampaignSystem.lua
- **File**: `script/CustomCampaignSystem.lua`
- **Features**:
  - Campaign scanning and detection
  - Keyboard shortcuts (Ctrl+Shift+C)
  - Console commands for testing
  - Map loading integration
  - Manual launch instructions

### 3. 📋 CustomCampaign.lua
- **File**: `script/CustomCampaign.lua`
- **Purpose**: Additional integration utilities
- **Features**: Menu system, campaign management

## How It Works

### In-Game Button Integration
```
Original Button3 → Custom Campaign Button
├── Caption: "CUSTOM" (instead of "B3")
├── OnClick: CustomCampaign_ShowMenu()
└── Functionality: Shows campaign selection menu
```

### Campaign Detection
The system automatically scans for campaigns in:
- `map\CustomCampaign\` directory
- Looks for P100-P199 map files
- Detects SampleCampaign with 5 maps

### Launch Methods
1. **Automatic**: Uses `GameControl.LoadMap()` if available
2. **Fallback**: Shows manual instructions
3. **Console**: Commands for direct access

## Usage in Game

### Method 1: Button Click
1. Find the repurposed "CUSTOM" button in the UI
2. Click it to show campaign menu
3. Select campaign to launch

### Method 2: Keyboard Shortcut
- Press `Ctrl+Shift+C` to open campaign menu

### Method 3: Console Commands
```
custom_campaign      - Show campaign menu
launch_sample        - Launch sample campaign
list_campaigns       - List available campaigns
```

### Method 4: Direct Function Calls
```
CustomCampaignSystem:LaunchSampleCampaign()
CustomCampaignSystem:ShowMenu()
```

## Sample Campaign Integration

The system detects our SampleCampaign:
```
SampleCampaign
├── P100_Introduction.map
├── P101_FirstTown.map
├── P102_ForestBattle.map
├── P103_MountainPass.map
└── P104_FinalBoss.map
```

## File Structure

```
ModdingTools/SpellForceLUASources/script/
├── UiInit.lua (modified)
├── CustomCampaignSystem.lua (new)
└── CustomCampaign.lua (new)

data/maps/SampleCampaign/
├── P100_Introduction.map
├── P101_FirstTown.map
├── P102_ForestBattle.map
├── P103_MountainPass.map
├── P104_FinalBoss.map
└── campaign_info.txt

src/custom_scripts/
├── P100/Ai.lua, n0.lua
├── P101/Ai.lua, n0.lua
└── ...
```

## Integration Points

### 1. UI System Hook
```lua
function B_OnClick()
    if UiGetClickedButtonName() == "<ctrl>Button3" then
        CustomCampaign_ShowMenu()
    end
end
```

### 2. Menu Creation Hook
```lua
UiCreateMainMenu = function(Name)
    -- Original menu creation
    originalUiCreateMainMenu(Name)
    -- Add our custom button
    CustomCampaignSystem:AddCampaignButtonToMenu()
end
```

### 3. Map Loading Integration
```lua
if GameControl and GameControl.LoadMap then
    local success = GameControl:LoadMap(mapPath)
    if success then
        print("Custom campaign launched!")
    end
end
```

## Testing and Debugging

### Console Output
The system provides detailed console logging:
```
[CustomCampaign] Initializing in-game integration...
[CustomCampaign] Found campaign: SampleCampaign
[CustomCampaign] Added keyboard shortcut: Ctrl+Shift+C
[CustomCampaign] System initialized with 1 campaigns
```

### Manual Fallback
If automatic map loading fails:
- Shows manual instructions
- Provides console commands
- Lists all available maps

## Advantages of In-Game Integration

✅ **Seamless Experience**: Uses existing game UI
✅ **No External Tools**: Everything runs inside the game
✅ **Native Feel**: Follows game's visual style
✅ **Keyboard Support**: Native keyboard shortcuts
✅ **Console Integration**: Uses game's console system
✅ **Minimal Dependencies**: Works with existing game systems

## Next Steps

### 1. Real Map Integration
- Replace placeholder .map files with real maps
- Test actual map loading functionality
- Verify campaign progression

### 2. Enhanced UI
- Create custom button graphics
- Add campaign selection dialog
- Implement campaign progress tracking

### 3. Save Integration
- Integrate with game's save system
- Track campaign progress
- Handle save/load for custom campaigns

### 4. Multi-Campaign Support
- Support multiple custom campaigns
- Campaign management interface
- Campaign packaging system

## Usage Example

1. **Start the game** with modified Lua scripts
2. **Press Ctrl+Shift+C** or click "CUSTOM" button
3. **Select SampleCampaign** from menu
4. **Game attempts** to load P100_Introduction.map
5. **If successful**, campaign starts
6. **If not**, shows manual instructions

This approach provides a **native in-game experience** for custom campaigns without requiring external launchers or GUI tools!
