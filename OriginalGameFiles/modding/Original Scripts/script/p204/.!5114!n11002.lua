-->INFO: Puppenspieler
function CreateStateMachine(_Type,_PlatformId,_NpcId,_X,_Y)

BeginDefinition(_Type,_PlatformId,_NpcId,_X,_Y)

--!EDS ONIDLEGOHOME BEGIN
OnIdleGoHome{WalkMode = Walk, X = _X, Y = _Y, Direction = 3}
--!EDS ONIDLEGOHOME END

OnToggleEvent
{
	OnConditions =
	{
		IsGlobalFlagFalse{Name = "g_P204_YrmirSidequestOn"},
	},
	OnActions =
	{
		SetGlobalFlagTrue{Name = "PleaseRemoveDialog_11002"},
	},
	OffConditions =
	{
		IsGlobalFlagTrue{Name = "g_P204_YrmirSidequestOn"},
	},
	OffActions =
	{
		SetGlobalFlagTrue{Name = "PleaseEnableSideQuestDialog_11002"},
	}
}


--------------------------------------------------------------------------
-- DO NOT EDIT THIS LINE OR THE ABOVE LINE, MOREOVER AND MOST IMPORTANTLY:
-- DO NOT EDIT ANYTHING BELOW THIS LINE! ANY CHANGES WILL BE LOST!
--------------------------------------------------------------------------
-- Script file created by AllClear -> Lua exporter 1.1
-- Source: C:\project\main\mission\dialoge\P204\n11002_Puppenspieler.txt


	

	-- 3 globale flags steuern das an/abschalten eines NPC Dialogs
