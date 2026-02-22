SpellSmutCampaign = {}

function SpellSmutCampaign_Launch()
    local mapBase = "map\\CustomCampaign\\P100_Introduction"
    local mapPath = mapBase .. ".map"
    local ok = false

    print("[SpellSmutCampaign] Launch requested for " .. mapPath)

    if Application and Application.LoadMap then
        print("[SpellSmutCampaign] Trying Application:LoadMap")
        ok = Application:LoadMap(mapPath)
    end
    if (not ok) and GameControl and GameControl.LoadMap then
        print("[SpellSmutCampaign] Trying GameControl:LoadMap")
        ok = GameControl:LoadMap(mapPath)
    end
    if not ok then
        print("[SpellSmutCampaign] Could not auto-load " .. mapPath)
    else
        print("[SpellSmutCampaign] Map load reported success")
    end
end

function SpellSmutCampaign_OnClick()
    print("[SpellSmutCampaign] Button click handler called")
    SpellSmutCampaign_Launch()
end

function SpellSmutCampaign_OnShortcut()
    print("[SpellSmutCampaign] Keyboard shortcut handler called")
    SpellSmutCampaign_Launch()
end

function SpellSmutCampaign_InitUI()
    print("[SpellSmutCampaign] InitUI called")

    if not UiCreateForm then
        print("[SpellSmutCampaign] UiCreateForm not available yet")
        return
    end
    if Screen and Screen:ControlByName("<cont>SpellSmutCampaign") ~= nil then
        print("[SpellSmutCampaign] UI already exists, skipping")
        return
    end
    local form = {
        800, 10, 180, 30;
        Name = "<cont>SpellSmutCampaign";
        AddTo = "Screen";
        HandleIfTransparent = true;
        Controls = {
            { 0, 0, 160, 24; Type = "GfxButton", Name = "<ctrl>btSpellSmutCampaign", Caption = "SpellSmut Campaign", MeshGfx = "ui_btn_dummy_color.msh", OnClick = "SpellSmutCampaign_OnClick" }
        }
    }
    UiCreateForm(form)
    print("[SpellSmutCampaign] UI form created")
end

function SpellSmutCampaign_RegisterShortcuts()
    if UiCreateGlobalShortcutShort then
        print("[SpellSmutCampaign] Registering Ctrl+Shift+C shortcut")
        UiCreateGlobalShortcutShort("Ctrl+Shift+C", "SpellSmutCampaign_OnShortcut", 0, "SpellSmut Campaign")
    else
        print("[SpellSmutCampaign] UiCreateGlobalShortcutShort not available")
    end
end
