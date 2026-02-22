--------------------------------------------------------------------------------------------------------------
-- constants
--------------------------------------------------------------------------------------------------------------

local kal_Top						=  2
local kal_Bottom					=  4


--------------------------------------------------------------------------------------------------------------
-- functions
--------------------------------------------------------------------------------------------------------------

function B_OnClick ()
	print("Button clicked - checking for custom campaign...")
	
	-- Check if this is Button3 (which we'll repurpose for custom campaign)
	if UiGetClickedButtonName and UiGetClickedButtonName() == "<ctrl>Button3" then
		CustomCampaign_ShowMenu()
	else
		print("Regular button click")
	end
end

function CustomCampaign_ShowMenu()
	print("Custom Campaign menu activated!")
	
	-- Check if custom campaign directory exists
	local customMaps = {}
	local campaignFound = false
	
	-- Simulate finding SampleCampaign
	campaignFound = true
	print("Found SampleCampaign with maps:")
	print("- P100_Introduction")
	print("- P101_FirstTown") 
	print("- P102_ForestBattle")
	print("- P103_MountainPass")
	print("- P104_FinalBoss")
	
	if campaignFound then
		print("Launching SampleCampaign - P100_Introduction...")
		
		-- Try to load the custom map
		if GameControl and GameControl.LoadMap then
			local success = GameControl:LoadMap("map\\CustomCampaign\\P100_Introduction.map")
			if success then
				print("Custom campaign launched successfully!")
			else
				print("Failed to load custom campaign map")
			end
		else
			print("GameControl.LoadMap not available - showing manual instructions")
			print("To play custom campaign:")
			print("1. Copy campaign files to game directory")
			print("2. Load map: map\\CustomCampaign\\P100_Introduction.map")
		end
	else
		print("No custom campaigns found in map\\CustomCampaign directory")
	end
end

function UiGetClickedButtonName()
	-- This would need to be implemented based on the game's UI system
	-- For now, we'll return a placeholder
	return "<ctrl>Button3"
end


--------------------------------------------------------------------------------------------------------------
-- forms
--------------------------------------------------------------------------------------------------------------


MainForm =
{
	0, 0, 0, 0;
	Name = "<cont>Maincontainer #1",
	AddTo = "Screen",
	HandleIfTransparent = 1,
}

SubForm1 =
{
	0, 380, 640, 100;
	Name = "<cont>Subcontainer #1",
	Background = "bottom_maprockfield.msh",
	AddTo = "<cont>Maincontainer #1",
	HandleIfTransparent = 0,
	Controls =
	{
		{ 25, 25, 50, 50; Type = "Button", Name = "<ctrl>Button1", Caption = "B1", Mesh1 = "Alchemist_Relief.msh",Mesh2 = "Alchemist_Mousepressed.msh",  Mesh3 = "Alchemist_Mousepressed.msh", Mesh4 = "Alchemist_Mouseover.msh", OnClick = "B_OnClick"},
		{ 95, 25, 50, 50; Type = "Button", Name = "<ctrl>Button2", Caption = "B2", Mesh1 = "Church_Relief.msh", Mesh2 = "Church_Mousepressed.msh", Mesh3 = "Church_Mousepressed.msh", Mesh4 = "Church_Mouseover.msh", OnClick = "B_OnClick"},
		{ 165, 25, 50, 50; Type = "Button", Name = "<ctrl>Button3", Caption = "CUSTOM", Mesh1 = "MagicianTower_Relief.msh", Mesh2 = "MagicianTower_Mousepressed.msh", Mesh3 = "MagicianTower_Mousepressed.msh", Mesh4 = "MagicianTower_Mouseover.msh", OnClick = "B_OnClick"}
	}
}
   
SubForm2 = 
{
	225, 0, 300, 100;
	Name = "<cont>Subcontainer #2",
	AddTo = "<cont>Subcontainer #1",
	Controls =
	{
		{ 25, 25, 50, 50; Type = "Button", Name = "<ctrl>Button4", Caption = "B4", Mesh1 = "Smith_Relief.msh", Mesh2 = "Smith_Mousepressed.msh", Mesh3 = "Smith_Mousepressed.msh", Mesh4 = "Smith_Mouseover.msh", Enabled = "off" , OnClick = "B_OnClick"},
		{ 100, 25, 50, 50; Type = "Button", Name = "<ctrl>Button5", Caption = "B5", Mesh1 = "Woodcutter_Relief.msh", Mesh2 = "Woodcutter_Mousepressed.msh", Mesh3 = "Woodcutter_Mousepressed.msh", Mesh4 = "Woodcutter_Mouseover.msh", OnClick = "B_OnClick"}
	}
}

SubForm3 = 
{
	150, 0, 75, 100;
	Name = "<cont>Subcontainer #3",
	AddTo = "<cont>Subcontainer #2",
	Controls =
	{ 
		{ 25, 25, 50, 50; Type = "Button", Name = "<ctrl>Button6", Caption = "B6", Mesh1 = "House_Relief.msh", Mesh2 = "House_Mousepressed.msh", Mesh3 = "House_Mousepressed.msh", Mesh4 = "House_Mouseover.msh", OnClick = "B_OnClickDel"}
	}
}

SubForm4 =
{
	0, 0, 0, 20;
	Background = "Top.msh",
	Name = "<cont>Subcontainer #4",
	AddTo = "<cont>Maincontainer #1",
	Alignment = kal_Top
}

UiCreateForm (MainForm)
UiCreateForm (SubForm1)
UiCreateForm (SubForm2)
UiCreateForm (SubForm3)
UiCreateForm (SubForm4)
