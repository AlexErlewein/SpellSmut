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

	if not UiCreateForm or not Screen then
		print("[SpellSmutCampaign] UiCreateForm or Screen not available yet")
		return
	end

	local existing = Screen:ControlByName("<cont>SpellSmutCampaign")
	if existing ~= nil then
		print("[SpellSmutCampaign] UI already exists, skipping")
		return
	end

	local form = {
		10, 10, 180, 30;
		Name = "<cont>SpellSmutCampaign",
		AddTo = "Screen",
		HandleIfTransparent = 1,
		Controls = {
			{ 0, 0, 160, 24; Type = "GfxButton", Name = "<ctrl>btSpellSmutCampaign", Caption = "SpellSmut Campaign", MeshGfx = "ui_btn_dummy_color.msh", OnClick = "SpellSmutCampaign_OnClick" }
		}
	}

	UiCreateForm(form)
	print("[SpellSmutCampaign] UI form created")
end

function SpellSmutCampaign_RegisterShortcuts()
	if UiCreateGlobalShortcut and INP_Keyboard and kMnu_kmCONTROL and kMnu_kmSHIFT then
		print("[SpellSmutCampaign] Registering Ctrl+Shift+C shortcut")
		UiCreateGlobalShortcut{
			kMnu_kmCONTROL + kMnu_kmSHIFT,
			INP_Keyboard.KC_C,
			"SpellSmutCampaign_OnShortcut",
			0,
			"SpellSmut Campaign"
		}
	else
		print("[SpellSmutCampaign] Shortcut constants not available")
	end
end
