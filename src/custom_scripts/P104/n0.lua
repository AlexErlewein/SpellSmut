
-- Main quest script for map P104
-- Custom campaign quest logic

function OnMapStart()
    -- Initialize quest
    Game.SetQuestState("custom_quest_104", "active")
end

function OnQuestComplete()
    -- Handle quest completion
    print("Quest completed for map P104")
end
