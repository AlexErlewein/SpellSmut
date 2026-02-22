# SpellForce 1 – Example Quest Walkthrough

This document walks through a concrete **example side quest** using the workflow from `SpellForce_Quest_Modding_Workflow.md`.

The names/IDs here are **fictional placeholders** – replace them with your actual map, NPC, and ID values.

---

## 1. Example Quest Concept – "The Lost Relic"

- **Map**: `GreyfellOutskirts` (example campaign map name).
- **Quest giver**: NPC `Arik the Scout` near the city gate.
- **Goal**: Retrieve an old relic from a nearby cave and return it to Arik.
- **Stages**:
  - S1: Talk to Arik and accept the quest.
  - S2: Enter the cave region and pick up the relic.
  - S3: Return to Arik to complete the quest and get a reward.
- **Reward**: A unique amulet and some XP.

---

## 2. GameData.cff – Text & Data Setup

Open **GameData Editor** and add / note the following. The IDs below are **examples** only.

### 2.1 Journal & Text Entries

Create text entries like:

| Purpose                         | Example ID | Example Text                                      |
|---------------------------------|-----------:|---------------------------------------------------|
| Quest title                     |    910000 | The Lost Relic                                   |
| Quest description (stage 1)     |    910001 | Arik asked me to retrieve an old relic...        |
| Quest description (stage 2)     |    910002 | I have found the relic. I should return to Arik. |
| Quest description (completed)   |    910003 | I returned the relic to Arik and got a reward.   |
| Dialogue: Arik intro            |    910010 | "Greetings, traveler. I have a favor to ask..." |
| Dialogue: Arik accept           |    910011 | "Thank you. The relic is in a cave nearby..."   |
| Dialogue: Arik turn-in          |    910012 | "You found it! Here, take this amulet."        |

Write down the **actual** IDs GameData Editor assigns – you will use them in Lua.

### 2.2 Optional: New Item

If you want a **special amulet** as reward:

- In the **items table**, duplicate a similar amulet and adjust:
  - Name text ID (e.g. 910020 – "Relic Amulet").
  - Stats / requirements as you like.
- Note the **item ID** (e.g. `ITEM_ID_RELIC_AMULET = 520000`).

---

## 3. Lua Script – Quest Logic

Assume the map already loads a script file like `q_greyfell_outskirts.lua`. If not, follow the pattern from existing campaign scripts for that map.

Below is **pseudo-Lua 4 style** showing the overall structure – adapt it to match existing SpellForce scripts.

```lua
-- q_greyfell_outskirts.lua (example)

-- Constants (use your real IDs)
QUEST_ID_LOST_RELIC = 20001
TEXT_Q_TITLE        = 910000
TEXT_Q_STAGE1       = 910001
TEXT_Q_STAGE2       = 910002
TEXT_Q_COMPLETE     = 910003

TEXT_ARIK_INTRO     = 910010
TEXT_ARIK_ACCEPT    = 910011
TEXT_ARIK_TURNIN    = 910012

ITEM_ID_RELIC       = 530000    -- item placed in cave chest
ITEM_ID_REWARD      = 520000    -- Relic Amulet, from GameData

-- Called when player first talks to Arik
function Quest_LostRelic_OnTalk_Arik()
    local state = GetQuestState(QUEST_ID_LOST_RELIC)

    if state == QS_NOT_STARTED then
        SayNpc(TEXT_ARIK_INTRO)
        if AskYesNo(TEXT_ARIK_ACCEPT) == true then
            StartQuest_LostRelic()
        end

    elseif state == QS_IN_PROGRESS and PlayerHasItem(ITEM_ID_RELIC) == false then
        -- Remind player to get the relic
        SayNpc(TEXT_ARIK_ACCEPT)

    elseif state == QS_IN_PROGRESS and PlayerHasItem(ITEM_ID_RELIC) == true then
        CompleteQuest_LostRelic()

    elseif state == QS_COMPLETED then
        SayNpc(TEXT_ARIK_TURNIN)
    end
end

function StartQuest_LostRelic()
    SetQuestState(QUEST_ID_LOST_RELIC, QS_IN_PROGRESS)
    SetQuestLog(QUEST_ID_LOST_RELIC, TEXT_Q_TITLE, TEXT_Q_STAGE1)
end

function CompleteQuest_LostRelic()
    RemoveItemFromPlayer(ITEM_ID_RELIC, 1)
    GiveItemToPlayer(ITEM_ID_REWARD, 1)
    GiveXPToPlayer(500)  -- example value

    SetQuestState(QUEST_ID_LOST_RELIC, QS_COMPLETED)
    SetQuestLog(QUEST_ID_LOST_RELIC, TEXT_Q_TITLE, TEXT_Q_COMPLETE)

    SayNpc(TEXT_ARIK_TURNIN)
end

-- Optional: region trigger handler for entering the cave
function Quest_LostRelic_OnEnterCave()
    local state = GetQuestState(QUEST_ID_LOST_RELIC)
    if state == QS_IN_PROGRESS then
        -- Update journal when player reaches the cave
        SetQuestLog(QUEST_ID_LOST_RELIC, TEXT_Q_TITLE, TEXT_Q_STAGE2)
    end
end
```

> **Important**: Replace helper functions (`GetQuestState`, `SetQuestLog`, etc.) with the **actual API** names used in the existing SpellForce Lua sources. This snippet is a structural example only.

---

## 4. Map Editor – Wiring the Quest

Open **Map Editor** (SpellForce Editor) and load your example map, e.g. `GreyfellOutskirts`.

### 4.1 Quest Giver NPC

1. Select the NPC you want to use as `Arik the Scout` (or place a new one).
2. In its **script/event properties**:
   - Set the **OnTalk** (or equivalent) callback to:  
     `Quest_LostRelic_OnTalk_Arik`
3. Ensure the map is configured to load `q_greyfell_outskirts.lua` (follow how other scripts are attached to the map).

### 4.2 Cave Region Trigger

1. Create a **region** covering the cave entrance or interior.
2. In the region’s event settings, assign the handler:  
   `Quest_LostRelic_OnEnterCave`
3. This lets the script update the quest journal when the player arrives.

### 4.3 Relic Item Placement

1. Place a **chest** (or container) inside the cave.
2. In the chest’s contents, include the **relic item** with ID `ITEM_ID_RELIC`.
3. Make sure the item entry exists in `GameData.cff` and can actually be looted.

Save the map into your mod workspace.

---

## 5. Building the Mod and Testing

### 5.1 Create the Mod Package

Using **Mod Manager / Mod Creator**:

1. Create a new mod, e.g. `LostRelicMod`.
2. Add:
   - Your **modified `GameData.cff`** with the new text (and item) entries.
   - The **Lua script** file `q_greyfell_outskirts.lua` (or whichever name you used).
   - The **modified map** `GreyfellOutskirts`.
3. Build the mod so it produces the proper PAKs / configuration.
4. Activate `LostRelicMod` in Mod Manager.

### 5.2 In‑Game Test Checklist

1. Start SpellForce with the mod enabled.
2. Load a save where you can reach `GreyfellOutskirts`.
3. Approach **Arik** and talk to him:
   - Check that his dialogue appears using your new text IDs.
   - Accept the quest and verify you see **"The Lost Relic"** in the quest log.
4. Go to the **cave region**:
   - Confirm the quest log updates to the stage‑2 description.
5. Loot the **relic item** from the chest.
6. Return to **Arik**:
   - Dialogue should change to a turn‑in.
   - The relic is removed and the reward amulet is added.
   - Quest state becomes **Completed**, and the final journal text is set.

If anything fails:

- **Missing or wrong text** → recheck `GameData.cff` IDs and Lua constants.
- **NPC does nothing** → verify map is using the correct script file & function name.
- **Relic doesn’t exist** → confirm the item is properly defined in GameData and placed on the map.

---

## 6. How to Adapt This Example

To turn this into a real quest in your project:

- Replace the placeholder map name (`GreyfellOutskirts`) with your **actual target map**.
- Use your **real NPC** and change dialogue text to fit the lore.
- Choose appropriate **reward items / XP**.
- Swap all example IDs (910000+, 520000+, etc.) with the **actual IDs** from your `GameData.cff`.

You can duplicate this pattern for more quests by:

- Copying the Lua structure.
- Adjusting text IDs and item IDs.
- Wiring new NPCs/regions in different maps.
