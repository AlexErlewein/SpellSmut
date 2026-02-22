
-- Main quest script for map P102
-- Custom campaign quest logic

function OnMapStart()
    -- Initialize quest
    Game.SetQuestState("custom_quest_102", "active")
end

function OnQuestComplete()
    -- Handle quest completion
    print("Quest completed for map P102")
end
