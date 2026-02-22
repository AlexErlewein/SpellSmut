
-- Main quest script for map P103
-- Custom campaign quest logic

function OnMapStart()
    -- Initialize quest
    Game.SetQuestState("custom_quest_103", "active")
end

function OnQuestComplete()
    -- Handle quest completion
    print("Quest completed for map P103")
end
