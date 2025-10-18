In the context of Spellforce scripting, Map Scripts are scripts that control various aspects of the game map. They can manipulate entities, control spawn points, and manage other map-related features. Two key tables available for entity management are `RtsSpawn` and `RtsSpawnNT`.

Map Scripts have access to these tables for spawning and respawning entities. These tables are particularly useful for controlling the behavior of entities in the game, such as their spawn locations, respawn rates, and conditions for spawning.
## Spawn/Respawn Tables
There are a few key differences between `RtsSpawn`and `RtsSpawnNT`. While `RtsSpawnNT` gives more control overall, it also removes some aspects achievable with `RtsSpawn`. Some of these differences are:
- `RtsSpawn` support multiple `Groups`, each with their own spawnpoint/homepoint, meaning a single `RtsSpawn` **Clan** can be present in multiple regions of the map with their own individual conditions for respawn. Meanwhile `RtsSpawnNT` only has access to one spawnpoint/homepoint as well as a single `Conditions` table for its entire **Clan**.
- `RtsSpawn` has no field for changing the spawnrate of troops; instead you have a constant ~10s spawnrate between each unit. Without `SpawnLimit = 0`, the `Group` will stop spawning units once it reaches its `SpawnLimit`. This can be circumvented by using `ResetNpcCounter` action. Which will allow the `Group` to respawn up to `SpawnLimit` number of units again even if the current number of living units exceed that limit. This however cannot bypass the **Clan** `MaxClanSize` value.

### RtsSpawnNT
```
RtsSpawnNT
{
    Clan = 0,            -- Clan Identifier.
    MaxClanSize = 0,     -- Maximum number of living clan members at one time.
    X = 0,               -- X-coordinate of spawn. Defines the homepoint that units belonging to this clan return to.
    Y = 0,               -- Y-coordinate of spawn. Defines the homepoint that units belonging to this clan return to.
    Range = 0,           -- Units spawn radius around the X/Y coordinates.
    Chief = 0,           -- Accepts one or more NpcIds for chiefs. If any of them die, the Group stops spawning. Defaults to 0.
    AvatarMinLevel = 0,  -- Min avatar level for spawn. Defaults to 0.
    AvatarMaxLevel = 0,  -- Max avatar level for spawn. Defaults to 0.
    Timer = "",          -- Name of the global timer that is set at a certain event and triggers the spawning of this clan.
    Init = {},           -- The units that should be spawned at the beginning.
    SpawnData =          -- Manage the time, spawnrate and unit types spawned by this Clan. 
    {
    -- [From X Minutes] = {Minutes/Seconds = , Units = {UnitId1, UnitId2, ...}}, 
        [0] = {Minutes = 3, Units = {777, 799}}, -- At 0 minutes after timer, spawns a random unit from Units every 3 minutes.
    },
    NpcBuildingsExist =  -- Respawn only works if this condition is true when specified. Defaults to a empty table if not specified.
    {
        X = 0,           -- X-coordinate to check for buildings.
        Y = 0,           -- Y-coordinate to check for buildings.
        Range = 0        -- Radius around the X/Y coordinate to check for buildings.
    },
    CampDestroyedActions = {}, -- Execute actions when the camp is destroyed (All nearby buildings are destroyed).
    Effect = "Materialize", -- Effect used when units belonging to this clan spawns. Defaults to "Materialize".
    Length = 2000,  -- Untested
}
```

### RtsSpawn
```
GroupToSpawn_1 =
{
    X = 0,                 -- X-coordinate of the spawn location.
    Y = 0,                 -- Y-coordinate of the spawn location.
    Range = 0,             -- Units Spawn Radius.
    WaitTime = 0,          -- Time in seconds the group waits before spawning (GlobalTimeElapsed condition).
    AvatarMinLevel = 0,    -- Minimum level of the Avatar for this Group to spawn.
    AvatarMaxLevel = 0,    -- Maximum level of the Avatar for this Group to spawn.
    SpawnLimit = 0,        -- Maximum number of units that can be spawned by this Group. -1 = Spawn Units{} tabl only once, 0 = No-limit.
    Chief = NpcId or {NpcId1, NpcId2, ...}, -- NpcId of the Group Chief (the Group Boss Unit). If any of them die, the Group stops spawning.
    Conditions = {},       -- Conditions for spawn to work. If this fails, only this Group will stop spawning.
    ShuffleUnits = FALSE,  -- If TRUE Discards the order set in Units{} table and spawns randomly.
    Units = {},  -- Units to spawn in the order specified until it reaches the end, then it starts again from the beginning, except if SpawnLimit is equal to -1, in that case once it reaches the end the Group stop spawning units.
}

RtsSpawn
{
    Clan = 3,           -- Clan Identifier
    MaxClanSize = 20,   -- Maximum number of living members of this clan throughout all the Groups.
    MaxClanLevel = 0,   -- Untested. Defaults to 0.
    Groups = {GroupToSpawn_1},
    Conditions = {},    -- Condition for enabling this RtsSpawn.
    Effect = 0,         -- Effect to use when spawning a unit. Use "Materialize" if you want the same effect as RtsSpawnNT. Defaults to 0.
    Length = 0,         -- Length of the Effect in milliseconds.
}
```
`RtsSpawn` table is used to spawn groups of entities, typically led by one or more Chiefs. Each group can normally only spawn up to `SpawnLimit` units. If one or more `Chief` is assigned, then the condition `FigureAlive` will automatically be added to the Group, and shall any of the Chiefs die then the spawn will stop prematurely. The spawnrate of units spawned by RtsSpawn seems to be around 10 seconds per unit, which is not something you can change.

The `RtsSpawn` table has the following fields:
* The `Clan` field defines the Clan identifier.
* The `MaxClanSize` field defines the maximum number of living units throughout all the `Groups`.
* The `MaxClanLevel` field. Untested.
* The `Groups` field is a Table containing different `Group` tables.
* The `Conditions` field is a table of `Conditions` for enabling this **Clan** and subsequently the spawn of all `Groups` within.
* The `Effect` field defines the effect used when spawning units belonging to this Clan.
* The `Length` field defines the length of the `Effect` in milliseconds.

Each `Group` table in the `Groups` table has the following fields:
* The `X` and `Y` fields define the X/Y-coordinate of the group spawn location.
* The `Range` field defines the spawn radius of units. Defaults to 0 if not specified.
* The `WaitTime` field defines the time in seconds the group waits before spawning (GlobalTimeElapsed condition).
* The `AvatarMinLevel` field defines the minimum level of the Avatar for this Group to spawn. Defaults to 0 if not specified.
* The `AvatarMaxLevel` field defines the maximum level of the Avatar for this Group to spawn. Defaults to 0 if not specified.
* The `SpawnLimit` field defines the maximum number of units that can be spawned by this Group. -1 = Spawn Units{} table only once, 0 = No-limit. Defaults to 0 if not specified.
* The `Chief` field is a value/table of NpcId(s) of Group Chief (the Group Boss Unit). The value can be either a NpcId or a table of NpcIds. If a Chief dies, the Group stops spawning. Defaults to 0 if not specified.
* The `BeginConditions` field is table. Untested. Defaults to a empty table if not specified.
* The `Conditions` field is a table of `Conditions` for this group to spawn. If this fails, only this Group will stop spawning. Defaults to a empty table if not specified.
* The `ShuffleUnits` field when set to `TRUE` discards the order set in `Units = {}` table and set spawn order to random (Check `Units` below for explanation on spawn order). Defaults to `FALSE` if not specified.
* The `Units` field is a table of `UnitId`(s) that is spawned in the order specified until it reaches the end, then it starts again from the beginning. For example: `Units = {555, 556, 666}` will mean 555 will be spawned first, then 556 and finally 666, except if `SpawnLimit` is equal to -1. In that case, the `Group` ceases to spawn units once the end is reached.
