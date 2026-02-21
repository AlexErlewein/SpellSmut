# SpellForce P1 – Quest Script Index

This file connects the *theory* from `SpellForce_Quest_Modding_Workflow.md` with the **real Lua scripts** in:

`ModdingTools/SpellForceLUASources/script/p1`

It focuses on:

- Which scripts participate in **quest logic** (begin/solve/state checks).
- How some **quest chains** are split across multiple files.
- How to **look up any QuestId** in the P1 scripts yourself.

> Note: Many of these files use an extended encoding (German text, umlauts). Direct viewing may fail in some tools, but searching for `QuestId =` still works and is enough to map dependencies.

---

## 1. Quick Reminder – Quest Ops Used Here

From the main workflow doc, P1 scripts use these core operations:

- `QuestBegin{QuestId = X}` – start or activate a quest (or subquest).
- `QuestSolve{QuestId = X}` – mark a quest as solved/completed.
- `QuestState{QuestId = X, State = ...}` – check state (e.g. `StateUnknown`, `StateActive`).
- `PlayerHasItem{ItemId = ...}` – condition for quest progress.
- `SetPlayerFlagTrue/False`, `SetNpcFlagTrue/False`, `SetGlobalFlagTrue/False` – extra state flags around quests.

These are usually embedded inside:

- `OnOneTimeEvent { ... }` – global/map-level triggers.
- `OnBeginDialog { ... }` and `OnAnswer{ ... }` – conversation-based quest triggers.

---

## 2. High-Level Roles of Key P1 Scripts

From scanning `script/p1`:

- **`n0.lua`**  
  Global / map-level state machine for the area. Initializes several quests and reacts to world events (items owned, enemies dead, etc.).

- **`n1240.lua`**  
  Large NPC/dialogue script (Darius the Cartographer). Handles finishing early main quests and starting follow-up quest(s).

- **`n1392.lua`**  
  NPC/dialogue script for Celen (portal/troop related). Manages a chain involving quests 63, 64, 65, 15, 16 and related flags.

- **`n1393.lua`**  
  Brok / Shiel-related quest dialogue. Starts multi-quest chains (e.g. 36, 38, 41, 42, 44).

- **`n1388.lua`**  
  Side quests like **"EinSeltsamerRing"** and **"AusDerTiefe1Schreiber"**; starts/solves quests 44, 42, 46, 556, 557, 558 etc.

- **`n1398.lua`**  
  Continuation/resolution quests in the same chain (49, 50, 51, 46, 43, 558, etc.).

- **`n1394.lua`**  
  Very large script with many quest chains (e.g. 90–95, 359–361, 360, 370…). A lot of side and main-quest hub logic lives here.

- **`n1396.lua`**  
  Dialogue around Tyrgar (bag/item-related side quests). Starts/solves quests 128, 129, 130, 131 and interacts with quest 389.

- **`n1406.lua`, `n1608.lua`, `n1609.lua`, `n1610.lua`, `n1611.lua`**  
  Set handling the "Get to Eloni"/portal-style quest (17 → 262) repeated for multiple NPCs.

- **`n1670.lua`, `n3164.lua`**  
  Scripts involved in the Liannon gate / key item / quest 91–92 chain.

There are many more files with single-purpose logic (small `n####.lua` scripts), but the ones above are the big quest hubs.

---

## 3. Example Quest Chains and Their Scripts

This section groups some quests by **QuestId** and shows which scripts participate.

> These are examples, not a full list of all quests in P1.

### 3.1 Early Main Quest: 12, 14, 446, 447 (Darius the Cartographer)

**Files involved:**

- `n0.lua`
- `n1240.lua`

**Key observations (from search):**

- In `n0.lua`:
  - An `OnOneTimeEvent` checks `QuestState{QuestId = 12, State = StateUnknown}` and then:
    - `QuestBegin{QuestId = 12}`
    - `QuestBegin{QuestId = 446}`
    - `QuestBegin{QuestId = 447}`
    - `QuestSolve{QuestId = 446}`
  - This is an example of **map-level quest initialization** for the early main quest line.

- In `n1240.lua` (Darius dialog):
  - Repeated patterns like:
    - `QuestBegin{QuestId = 14, SubQuestActivate = TRUE}`
    - `QuestSolve{QuestId = 447}, QuestSolve{QuestId = 12}`
    - and setting reward flags like `DariusDerKarthograph` plus player flags (`FlagDariusKnown`).

**Interpretation:**

- `n0.lua` starts the initial main quest chain when you arrive / meet certain conditions.
- `n1240.lua` handles dialogue resolution, rewards, and transitioning from quests 12/447 into quest 14.

For modding: follow this pattern if you want **map-based auto-activation + NPC-based resolution**.

---

### 3.2 Westcamp / Dagger / Portal Troops: 63, 64, 65, 16, 351, 340

**Files involved:**

- `n0.lua`
- `n1392.lua`

**Key observations:**

- In `n0.lua`:
  - "Checker ob Spieler Dolch hat UND Queste" (player has dagger and quest):
    - Conditions: `PlayerHasItem{ItemId = 2336}`, `QuestState{QuestId = 65, State = StateActive}`.
    - Actions: `SetPlayerFlagTrue{Name = "Q65HasDaggerAndQuest"}`.
  - "Siegbedingung Westcamp" (Westcamp victory condition):
    - Conditions include `QuestState{QuestId = 65, State = StateActive}` and enemy units dead.
    - Actions: `QuestSolve{QuestId = 63}`, `QuestBegin{QuestId = 64}`.
  - Another checker:
    - `PlayerHasItem{ItemId = 2001}`, `QuestState{QuestId = 351, State = StateActive}`.
    - Actions: `QuestSolve{QuestId = 351}`, `QuestBegin{QuestId = 340}`.

- In `n1392.lua` (Celen dialog):
  - Starting the chain:
    - `QuestBegin{QuestId = 65}, QuestBegin{QuestId = 63}`.
  - Resolving and moving on:
    - After taking item 2336 and clearing conditions:
      - `QuestSolve{QuestId = 64}, QuestSolve{QuestId = 63}, QuestSolve{QuestId = 65}`.
      - `QuestBegin{QuestId = 16}`.
      - Set global flags like `PortalTroopsSpawning`, `PortalTroopsWalking`, etc.
  - Another block:
    - `QuestSolve{QuestId = 15}` followed by `QuestBegin{QuestId = 16}` (earlier stage of the same portal troop arc).

**Interpretation:**

- `n1392.lua` handles **dialogue-driven start and completion** of the Westcamp/portal troop quests.
- `n0.lua` monitors **world conditions** (items, enemy deaths) and updates quest states accordingly.
- Global/player flags tie both behaviour layers together.

---

### 3.3 Brok / Shiel / Udwin-Related Side Quests: 36, 38, 41, 42, 44, 46, 49, 50, 51, 556, 557, 558

**Files involved:**

- `n1393.lua`
- `n1388.lua`
- `n1398.lua`

**Key observations:**

- In `n1393.lua` (Brok dialog):
  - `QuestBegin{QuestId = 36}, QuestBegin{QuestId = 38}` with dialog tag `brok005`.
  - Later: `QuestBegin{QuestId = 41}, QuestBegin{QuestId = 42}, QuestBegin{QuestId = 44}` with dialog `brok011`.

- In `n1388.lua`:
  - Rewards and quest solves around **"EinSeltsamerRing"** etc.:
    - `SetRewardFlagTrue{Name = "EinSeltsamerRing"}` and `QuestBegin{QuestId = 556}`.
    - `QuestSolve{QuestId = 44}, QuestSolve{QuestId = 42}`.
  - For **"AusDerTiefe1Schreiber"**:
    - `SetRewardFlagTrue{Name = "AusDerTiefe1Schreiber"}`, `QuestBegin{QuestId = 557}`.
  - Another action:
    - `QuestBegin{QuestId = 46}` when checking some item / conditions.
    - `SetPlayerFlagTrue{Name = "SpawnFlagForUdwin"}`, `QuestBegin{QuestId = 558}`.

- In `n1398.lua`:
  - `QuestBegin{QuestId = 49}` and `QuestSolve{QuestId = 558}`.
  - Later: `QuestSolve{QuestId = 50}, QuestBegin{QuestId = 51}, QuestSolve{QuestId = 46}, QuestSolve{QuestId = 43}`.

**Interpretation:**

- `n1393.lua` introduces several Shiel-related quests via Brok.
- `n1388.lua` handles mid-chain progression and specialized side quests.
- `n1398.lua` finishes or branches later parts of this relative cluster.

This is a **good reference cluster** if you want to see how one NPC hub can start several side quests and how later scripts conclude them.

---

### 3.4 Liannon / Key / Gate Chain: 90–95, 91, 92, 359–361, 370, 360

**Files involved:**

- `n1394.lua`
- `n3164.lua`
- `n1670.lua`

**Key observations:**

- In `n1394.lua`:
  - One block:
    - `QuestSolve{QuestId = 90}, QuestBegin{QuestId = 91}`.
  - Another: `QuestSolve{QuestId = 93}, QuestBegin{QuestId = 95}`.
  - A later cluster:
    - `QuestBegin{QuestId = 370}, QuestSolve{QuestId = 359}`.
    - `QuestSolve{QuestId = 370}, QuestBegin{QuestId = 360}`.
    - `QuestSolve{QuestId = 370}, QuestBegin{QuestId = 361}`.

- In `n3164.lua`:
  - After removing dialog, taking item 3184 and setting `LiannonGateOpen`:
    - `QuestSolve{QuestId = 91}, QuestBegin{QuestId = 92}`.

- In `n1670.lua`:
  - A matching pattern: `QuestBegin{QuestId = 92}, QuestSolve{QuestId = 91}` plus reward item transfers (same item 3184).

**Interpretation:**

- `n1394.lua` manages mid-chain progression and links to later quests.
- `n3164.lua` and `n1670.lua` handle the **actual gate opening / item handover** and transition between quests 91 and 92.

For modding, this is an example of **map event + NPC + item** all working together around a gate/portal.

---

### 3.5 Get to Eloni / Portal Quest: 17, 262

**Files involved:**

- `n1406.lua`
- `n1608.lua`, `n1609.lua`, `n1610.lua`, `n1611.lua`

**Key observations:**

- In each of these files there is a nearly identical action block:
  - `QuestSolve{QuestId = 17}`
  - `QuestBegin{QuestId = 262}`
  - Set player and NPC flags like `QuestGetToEloniSolved`, `IchSollDasPortalAufmachen`, `IchGeheZumPortal`.

**Interpretation:**

- Multiple NPCs can complete the same quest step.
- All of them **solve quest 17** and **start quest 262** with nearly identical side effects.

This shows how the engine allows **redundant NPCs or dialog paths** leading to the same quest transition.

---

### 3.6 Tyrgar / Bag / Scout Side Quests: 128, 129, 130, 131, 389

**Files involved:**

- `n1396.lua`

**Key observations:**

- Repeated `OnBeginDialog` and `OnAnswer` blocks checking:
  - `QuestState{QuestId = 128, State = StateUnknown}` and `QuestState{QuestId = 389, State = StateActive}`.
  - Item 2461 ownership plus quest 130 active.
- Actions include:
  - `QuestBegin{QuestId = 128}`, `QuestBegin{QuestId = 129}` (starting initial quests).
  - Later: `QuestSolve{QuestId = 130}, QuestBegin{QuestId = 131}` and `SetPlayerFlagFalse{Name = "Q118HasBagandQuest"}`.

**Interpretation:**

- `n1396.lua` is largely self-contained for this side-quest chain, with internal branching based on items and flags.

---

## 4. Per-File Quest Usage Snapshot (P1)

This is a **non-exhaustive** snapshot of quest-related activity per script in `script/p1`.

- **`n0.lua`**
  - Starts quests: 12, 446, 447, 351, 340, 63, 64, 65 (and possibly more).
  - Checks quest states: 12, 65, 351, 63, 64, etc.
  - Uses item IDs (e.g. 2336 dagger, 2001 feather quill) in combination with quest checks.
  - Role: **global/map-level quest initializer and condition checker**.

- **`n1240.lua`**
  - Starts quest 14 with `SubQuestActivate = TRUE`.
  - Solves quests 12 and 447 repeatedly depending on dialog branches.
  - Sets reward flags for Darius the Cartographer and various player flags.
  - Role: **main quest resolution + reward handling** for early campaign.

- **`n1388.lua`**
  - Starts/solves quests 44, 42, 46, 556, 557, 558 and uses flags `EinSeltsamerRing`, `AusDerTiefe1Schreiber`, `SpawnFlagForScribe`, `SpawnFlagForScout`, etc.
  - Role: **hub for several Shiel-related side quests**.

- **`n1392.lua`**
  - Begins quests 65, 63, 16 and solves 64, 63, 65, 15.
  - Coordinates portal troop spawning via global flags.
  - Role: **dialogue hub for Westcamp/portal troop chain**.

- **`n1393.lua`**
  - Begins quests 36, 38, 41, 42, 44 and likely more in deeper sections.
  - Role: **Brok’s quest hub**, starts multiple related quests.

- **`n1394.lua`**
  - Manages many quest IDs: 90–95, 359–361, 360, 370, etc.
  - Role: **large multi-quest hub**; many side and main quests branch here.

- **`n1396.lua`**
  - Manages quests 128, 129, 130, 131 in conjunction with quest 389.
  - Role: **self-contained side quest chain with item requirements**.

- **`n1398.lua`**
  - Manages later stages of Shiel/Udwin-related quests (49, 50, 51, 46, 43, 558).
  - Role: **late-stage resolver** for one of the Shiel side quest arcs.

- **`n1406.lua`, `n1608.lua`, `n1609.lua`, `n1610.lua`, `n1611.lua`**
  - All: `QuestSolve{QuestId = 17}`, `QuestBegin{QuestId = 262}` plus portal-related flags.
  - Role: multiple NPCs sharing the **same quest transition**.

- **`n1670.lua`, `n3164.lua`**
  - Both handle `QuestSolve{QuestId = 91}`, `QuestBegin{QuestId = 92}` around item 3184 and gate flags.
  - Role: **Liannon gate / key item handover**.

There are many smaller `n####.lua` scripts with only 1–2 quests tied to them; you can map them using the search approach below.

---

## 5. How to Look Up Any QuestId in P1 Scripts

If you want to know *"which scripts affect Quest X?"*, you can repeat the process used for the examples above:

1. **Search for the quest ID in scripts**
   - In your IDE, search inside `ModdingTools/SpellForceLUASources/script/p1` for:  
     `QuestId = <your-id>`
   - Note the list of files and lines where it appears.

2. **Classify each occurrence by context**
   - Inside `OnOneTimeEvent` → map/global trigger.
   - Inside `OnBeginDialog` / `OnAnswer` → dialogue-based start/branch.
   - In `Actions` → `QuestBegin`, `QuestSolve`, item transfers, flag changes.
   - In `Conditions` → `QuestState` checks, `PlayerHasItem`, flags.

3. **Build a mini-chain for that quest**
   - Where is the quest **started**? (first `QuestBegin` or `QuestState ... StateUnknown` → `QuestBegin`).
   - Where is it **checked**? (conditions gating other events / NPC states).
   - Where is it **solved**? (`QuestSolve` + rewards / flags).
   - Are there any **follow-up quests** started after it solves?

4. **Extend this index**
   - Add a new section to this `.md` file for your quest, using the same structure as Section 3.
   - Over time, you’ll build a complete map of P1 quest dependencies tailored to the quests you care about.

---

## 6. How This Relates to Your Own Mods

Linking back to `SpellForce_Quest_Modding_Workflow.md`:

- These scripts are **reference implementations** of the patterns described there.
- When adding a new quest:
  - Pick an existing quest chain that behaves similarly (e.g. Westcamp, Shiel side quests, portal quests).
  - Study which files it touches and how `QuestBegin` / `QuestSolve` / `QuestState` are used.
  - Mirror that structure in your own Lua scripts and map setups.

As you identify more quest chains in `p1`, you can extend this index so it becomes your personal "atlas" of how SpellForce’s original quests are wired.
