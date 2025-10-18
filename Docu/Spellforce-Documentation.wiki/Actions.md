### Spawn
```
Spawn
{
    X = ,
    Y = ,
    NpcId = 0,
    Target = 0, -- Does not seem to work.
    Range = 0,
    UnitId = ,
    Clan = 0,
    NotPersistant = FALSE,
    Effect = 0,
    Length = 0,
    XRand = 0,
    YRand = 0,
}
```
Spawns a figure with the specified NpcId (Attention: duplicate NpcIds will cause the game to crash) at coordinate `X`, `Y`.
- The `X` and `Y` fields defines the spawn coordinates.
- The `NpcId` field defines the `NpcId` of this unit. If you don't need to address this spawned unit with scripts later, keep the `NpcId` as 0 or leave out the field, as this allows the spawning of any number of NPCs with ID 0.
- The `Target` field defines the `NpcId` of the target to spawn around. It does not seem to work.
- The `Range` field defines the spawn radius around the `X`, `Y` coordinates (rectangular).
- The `UnitId` field defines the Id of the unit you want to spawn. `UnitId` can be used as a table {...} to randomly spawn one of the units specified in the table. However, the `NpcId` must then be 0.
- The `Clan` field defines the `Clan` the spawned unit will belong to. The unit will be subject to all `Clan` behaviors upon spawning such as scouting, attacking or going back to the `Clan` Homepoint.
- The `NotPersistant` field defines whether the figure remains after leaving the platform (FALSE, default) or is then deleted again (TRUE).
- The `Effect` field defines what effect to use when spawning a unit.
- The `Length` field defines the duration of the effect on the spawned target, measured in milliseconds.
- The `XRand` and `YRand` fields defines the random radius by which the `X` and `Y`coordinate may change. If `XRand` has the value 20, for example, the `X`position is randomly changed by -10 to +9. The value of `X/YRand` must be positive and 2 or higher to take effect.

### Outcry
```
Outcry
{
    NpcId = ,
    String = "",
    Tag = "" ,
    Delay = TRUE ,
    Color = ColorWhite,
}
```
The specified Npc triggers an outcry that is displayed as text in the middle of the screen and, if available, plays a sound file associated with the specified `Tag`.
- The `NpcId` field represents the `NpcId` of the Npc making the Outcry, his name will be shown ingame, for example: <Npc Name>: <String>.
- The `String` field is the default text to display if the `Tag` text data does not contain any text.
- The `Tag` field determines both text and sound to display. Text is determined inside **(2016, Text Data)** category of the Spellforce Editor, inside each entry there's a field called **Text Handle** that determines the `Tag` name. Sound is determined by a file of the same name as the **Text Handle**, but ends with a .bar. For example: With a **Text Handle** of "TextHandleExample" you'd need a sound file by the name of "TextHandleExample.bar", if the sound name and Text Handle name matches then the sound will be played on any Action where this `Tag` is used.
- The `Delay` field can be used to disable the 3-second delay after an outcry. This allows, for example, conversation outcries to be played consecutively.
- The `Color` field determines the color of the text that is displayed.