-- ConUserInit_SpellSmut.lua
-- User init hook to wire SpellSmut campaign UI into the game start menu

-- Load SpellSmut campaign helpers
doscript("SpellSmutCampaign")

function ConStartMenuUserInit()
    print("[SpellSmutCampaign] ConStartMenuUserInit running")
    -- Initialize SpellSmut campaign UI on the start menu
    if SpellSmutCampaign_InitUI ~= nil then
        SpellSmutCampaign_InitUI()
    end
    if SpellSmutCampaign_RegisterShortcuts ~= nil then
        SpellSmutCampaign_RegisterShortcuts()
    end
end

-- Optional: also make it available in in-game UI after loading a map
function ConGameMenuUserInit()
    print("[SpellSmutCampaign] ConGameMenuUserInit running")
    if SpellSmutCampaign_InitUI ~= nil then
        SpellSmutCampaign_InitUI()
    end
end
