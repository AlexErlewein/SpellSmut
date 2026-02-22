-- In-Game Custom Campaign Integration
-- This script modifies the existing SpellForce UI to add custom campaign functionality

--------------------------------------------------------------------------------------------------------------
-- Custom Campaign System for In-Game Integration
--------------------------------------------------------------------------------------------------------------

CustomCampaignSystem = {
    IsEnabled = true,
    CurrentCampaign = nil,
    Campaigns = {},
    OriginalMenuHooked = false
}

-- Initialize the custom campaign system
function CustomCampaignSystem:Initialize()
    if not self.IsEnabled then
        return
    end
    
    print("[CustomCampaign] Initializing in-game integration...")
    
    -- Scan for campaigns
    self:ScanCampaigns()
    
    -- Hook into existing UI systems
    self:HookUISystem()
    
    -- Add console commands
    self:AddConsoleCommands()
    
    print("[CustomCampaign] System initialized with " .. #self.Campaigns .. " campaigns")
end

-- Scan for available custom campaigns
function CustomCampaignSystem:ScanCampaigns()
    self.Campaigns = {}
    
    -- Check for SampleCampaign (our test campaign)
    local sampleCampaign = {
        Name = "SampleCampaign",
        DisplayName = "Sample Campaign",
        Description = "A sample custom campaign for testing",
        StartMap = "P100_Introduction",
        Maps = {
            "P100_Introduction",
            "P101_FirstTown", 
            "P102_ForestBattle",
            "P103_MountainPass",
            "P104_FinalBoss"
        },
        Directory = "map\\CustomCampaign"
    }
    
    table.insert(self.Campaigns, sampleCampaign)
    print("[CustomCampaign] Found campaign: " .. sampleCampaign.Name)
end

-- Hook into the UI system to add our button
function CustomCampaignSystem:HookUISystem()
    print("[CustomCampaign] Hooking into UI system...")
    
    -- Method 1: Add a global keyboard shortcut
    if UiCreateGlobalShortcutShort then
        UiCreateGlobalShortcutShort("Ctrl+Shift+C", "CustomCampaignSystem_ShowMenu", 0, "Show Custom Campaign Menu")
        print("[CustomCampaign] Added keyboard shortcut: Ctrl+Shift+C")
    end
    
    -- Method 2: Hook into existing button clicks
    self:HookExistingButtons()
    
    -- Method 3: Add console commands
    self:AddConsoleCommands()
end

-- Hook into existing buttons to repurpose them
function CustomCampaignSystem:HookExistingButtons()
    -- Save original button click handler if not already saved
    if not self.OriginalMenuHooked then
        -- Try to hook into the main menu creation
        local originalUiCreateMainMenu = UiCreateMainMenu
        if originalUiCreateMainMenu then
            UiCreateMainMenu = function(Name)
                -- Call original function
                originalUiCreateMainMenu(Name)
                
                -- Add our custom campaign button
                CustomCampaignSystem:AddCampaignButtonToMenu()
            end
            self.OriginalMenuHooked = true
            print("[CustomCampaign] Hooked into main menu creation")
        end
    end
end

-- Add custom campaign button to existing menu
function CustomCampaignSystem:AddCampaignButtonToMenu()
    -- This would add a button to the main menu
    -- Implementation depends on the actual menu structure
    
    -- For now, we'll add a console command to trigger it
    print("[CustomCampaign] Campaign button would be added to main menu here")
end

-- Add console commands for testing and manual access
function CustomCampaignSystem:AddConsoleCommands()
    -- Add console commands if the console system is available
    if Application and Application.AddConsoleCommand then
        Application:AddConsoleCommand("custom_campaign", "CustomCampaignSystem_ShowMenu", "Show custom campaign menu")
        Application:AddConsoleCommand("launch_sample", "CustomCampaignSystem_LaunchSample", "Launch sample campaign")
        Application:AddConsoleCommand("list_campaigns", "CustomCampaignSystem_ListCampaigns", "List available campaigns")
    end
    
    -- Also add to global scope for direct calling
    _G.CustomCampaignSystem_ShowMenu = function() self:ShowMenu() end
    _G.CustomCampaignSystem_LaunchSample = function() self:LaunchSampleCampaign() end
    _G.CustomCampaignSystem_ListCampaigns = function() self:ListCampaigns() end
end

-- Show the custom campaign menu
function CustomCampaignSystem:ShowMenu()
    print("[CustomCampaign] Showing campaign selection menu...")
    
    if #self.Campaigns == 0 then
        self:ShowMessage("No custom campaigns found. Add campaigns to map\\CustomCampaign directory.")
        return
    end
    
    -- Create menu text
    local menuText = "=== CUSTOM CAMPAIGNS ===\n\n"
    
    for i, campaign in ipairs(self.Campaigns) do
        menuText = menuText .. i .. ". " .. campaign.DisplayName .. "\n"
        menuText = menuText .. "   " .. campaign.Description .. "\n"
        menuText = menuText .. "   Maps: " .. #campaign.Maps .. "\n\n"
    end
    
    menuText = menuText "Type number to select, or 'launch sample' for quick access"
    
    self:ShowMessage(menuText)
end

-- Launch a specific campaign
function CustomCampaignSystem:LaunchCampaign(campaignName)
    print("[CustomCampaign] Launching campaign: " .. campaignName)
    
    -- Find the campaign
    local selectedCampaign = nil
    for _, campaign in ipairs(self.Campaigns) do
        if campaign.Name == campaignName then
            selectedCampaign = campaign
            break
        end
    end
    
    if not selectedCampaign then
        self:ShowMessage("Campaign not found: " .. campaignName)
        return false
    end
    
    -- Set current campaign
    self.CurrentCampaign = selectedCampaign
    
    -- Try to launch the first map
    return self:LoadMap(selectedCampaign.StartMap)
end

-- Launch the sample campaign
function CustomCampaignSystem:LaunchSampleCampaign()
    print("[CustomCampaign] Launching SampleCampaign...")
    
    local success = self:LaunchCampaign("SampleCampaign")
    
    if success then
        self:ShowMessage("SampleCampaign launched! Starting with P100_Introduction")
    else
        self:ShowMessage("Failed to launch SampleCampaign. Check console for details.")
    end
    
    return success
end

-- Load a specific map
function CustomCampaignSystem:LoadMap(mapName)
    print("[CustomCampaign] Loading map: " .. mapName)
    
    -- Try different methods to load the map
    
    -- Method 1: Use GameControl.LoadMap
    if GameControl and GameControl.LoadMap then
        local mapPath = "map\\CustomCampaign\\" .. mapName .. ".map"
        print("[CustomCampaign] Trying GameControl.LoadMap: " .. mapPath)
        
        local success = GameControl:LoadMap(mapPath)
        if success then
            print("[CustomCampaign] Map loaded successfully!")
            return true
        else
            print("[CustomCampaign] GameControl.LoadMap failed")
        end
    end
    
    -- Method 2: Use Application.LoadMap
    if Application and Application.LoadMap then
        local mapPath = "map\\CustomCampaign\\" .. mapName .. ".map"
        print("[CustomCampaign] Trying Application.LoadMap: " .. mapPath)
        
        local success = Application:LoadMap(mapPath)
        if success then
            print("[CustomCampaign] Map loaded successfully!")
            return true
        else
            print("[CustomCampaign] Application.LoadMap failed")
        end
    end
    
    -- Method 3: Show manual instructions
    self:ShowManualLoadInstructions(mapName)
    return false
end

-- Show manual loading instructions
function CustomCampaignSystem:ShowManualLoadInstructions(mapName)
    local instructions = 
        "=== MANUAL CAMPAIGN LAUNCH ===\n\n" ..
        "To play the custom campaign:\n\n" ..
        "1. Copy campaign files to your SpellForce directory:\n" ..
        "   map\\CustomCampaign\\*.map\n\n" ..
        "2. Start SpellForce\n\n" ..
        "3. Load the map manually:\n" ..
        "   Map: " .. mapName .. "\n\n" ..
        "4. Or use console command:\n" ..
        "   load map\\CustomCampaign\\" .. mapName .. ".map\n\n" ..
        "Campaign maps available:\n"
    
    for _, campaign in ipairs(self.Campaigns) do
        if campaign.Name == "SampleCampaign" then
            for _, map in ipairs(campaign.Maps) do
                instructions = instructions .. "   - " .. map .. "\n"
            end
            break
        end
    end
    
    self:ShowMessage(instructions)
end

-- List all available campaigns
function CustomCampaignSystem:ListCampaigns()
    print("[CustomCampaign] Available campaigns:")
    
    if #self.Campaigns == 0 then
        print("  No campaigns found")
        return
    end
    
    for i, campaign in ipairs(self.Campaigns) do
        print("  " .. i .. ". " .. campaign.DisplayName)
        print("     Description: " .. campaign.Description)
        print("     Maps: " .. table.concat(campaign.Maps, ", "))
        print("     Start: " .. campaign.StartMap)
        print()
    end
end

-- Show a message to the user
function CustomCampaignSystem:ShowMessage(message)
    -- Try different methods to show the message
    
    -- Method 1: Use Screen.ShowMessageBox
    if Screen and Screen.ShowMessageBox then
        Screen:ShowMessageBox(message)
        return
    end
    
    -- Method 2: Use Application.ShowMessageBox
    if Application and Application.ShowMessageBox then
        Application:ShowMessageBox(message)
        return
    end
    
    -- Method 3: Print to console
    print("[CustomCampaign Message]")
    print(message)
    print("[End Message]")
end

-- Enable/disable the system
function CustomCampaignSystem:SetEnabled(enabled)
    self.IsEnabled = enabled
    print("[CustomCampaign] System " .. (enabled and "ENABLED" or "DISABLED"))
end

--------------------------------------------------------------------------------------------------------------
-- Auto-initialization
--------------------------------------------------------------------------------------------------------------

-- Initialize when the script loads
print("[CustomCampaign] Script loaded - initializing system...")
CustomCampaignSystem:Initialize()

-- Export to global scope
_G.CustomCampaignSystem = CustomCampaignSystem

--------------------------------------------------------------------------------------------------------------
-- Usage Instructions
--------------------------------------------------------------------------------------------------------------

print([[
[CustomCampaign] System Ready!
Usage:
- Press Ctrl+Shift+C to show campaign menu
- Console commands:
  * custom_campaign - Show campaign menu
  * launch_sample - Launch sample campaign
  * list_campaigns - List available campaigns
- Or call directly:
  * CustomCampaignSystem:LaunchSampleCampaign()
  * CustomCampaignSystem:ShowMenu()
]])
