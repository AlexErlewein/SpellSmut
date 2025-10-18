## Table of Contents
- [OnEvent](#onevent)
- [OnOneTimeEvent](#ononetimeevent)
- [OnToggleEvent](#ontoggleevent)
- [BeginScript](#beginscript)
- [KillScript](#killscript)
- [OnWakeUpEvent](#onwakeupevent)
- [OnFollowMe](#onfollowme)
- [OnFollowForever](#onfollowforever)
- [OnFollowToggle](#onfollowtoggle)
- [OnAttackPattern](#onattackpattern)


### OnEvent
```
OnEvent
{
    RemoveTransition = FALSE,
    NotInDialog = FALSE,
    Conditions = {},
    Actions = {},
}
```
Checks at regular intervals whether the specified Conditions are true. If yes - or if no Conditions are specified - then the Actions are executed.
- The `RemoveTransition` field when `TRUE` causes `OnEvent` to behave like `OnOneTimeEvent`, which means it will be triggered only once and not repeat.
- The `NotInDialog` field determines whether the NPC is not in a dialog. If this is set to `FALSE`, this event will trigger even if the NPC is in a dialog. This field likely requires the event to be present in a NPC Script to be of use. (untested)
- The `Conditions` field is a table of conditions that, when met, will trigger the event.
- The `Actions` field is a table of actions that is executed when the event is triggered.

- **WARNING**: `OnEvent` is very powerful, but you also have to be careful here as this can be at the expense of performance. 
In addition, events that have no `Conditions` are problematic as this will prevent the NPC from being able to be controlled by the AI. 
That is, possibly the NPC will constantly run to its Goto Point, turn around one field later to attack the player, and after one field run back to the Goto Point etc. 
`Conditions` that are very complex to query are queried by default only every minute. 
This can be regulated with the `UpdateInterval` field of the Conditions.
- **IMPORTANT**: `OnEvent` triggers state changes in an NPC. If you use an `OnEvent` without Conditions, it will always be true and thus none of the other events standing under this event will ever be executed!!!
- **Disclaimer**: This event seems to exhibit an issue where, if the condition is met even once, it will continuously trigger the Actions without stopping. This could effectively block any Events listed after this one from being triggered. Further testing is required for a conclusive answer.

If you are having problems with `OnEvent` and need an event that can trigger several times it's recommended to use `OnToggleEvent` instead.

### OnOneTimeEvent
```
OnOneTimeEvent
{
    NotInDialog = FALSE, 
    UpdateInterval = 60,
    Conditions = {},
    Actions = {}
}
```
Similar to `OnEvent`, but it is executed globally only once. This represents an absolutely unique event in the game and for all players. 
This event should be used for everything that should be triggered only once, such as changing the value of a variable. 
- The `NotInDialog` field determines whether the player is not in a dialog. If this is set to `FALSE`, this event will trigger even if the NPC is in a dialog. This field likely requires the event to be present in a NPC Script to be of use. (untested)
- The `UpdateInterval` field determines the interval at which the conditions are checked. By default, it is set to 60 GDs, where 10 GDs equals 1 second.
- The `Conditions` field is a table of conditions that, when met, will trigger the event.
- The `Actions` field is a table of actions that is executed when the event is triggered.

### OnToggleEvent
```
OnToggleEvent
{
    NotInDialog = FALSE,
    ResetOnPlatformLoad = FALSE,
    ResetOnDeath = FALSE,
    UpdateInterval = 60,
    OnConditions = {},
    OnActions = {},
    OffConditions = {},
    OffActions = {},
}
```
`OnToggleEvent` functions as follows: Initially, the toggle is in the "Off" position. It switches to "On" upon meeting the `OnConditions`, triggering the `OnActions` to execute once. In the absence of specified `OffConditions`, it assesses whether all `OnConditions` are not met before executing the `OffActions` once. Conversely, if `OffConditions` are defined, they are evaluated directly to execute the `OffActions` once. The toggle can be switched between "On" and "Off" states indefinitely, with actions executed only once during each state transition.

- The `NotInDialog` field determines whether the NPC is not in a dialog. If this is set to `FALSE`, this event will trigger even if the NPC is in a dialog. This field likely requires the event to be present in a NPC Script to be of use. (untested)
- The `ResetOnPlatformLoad` field determines whether the event should be reset when the platform is loaded. If this is set to `TRUE`, the event will be reset.
- The `ResetOnDeath` field determines whether the event should be reset when the NPC dies. If this is set to `TRUE`, the event will be reset.
- The `UpdateInterval` field determines the interval at which the conditions are checked. By default, it is set to 60 GDs where 10 GDs equals 1 second.
- The `OnConditions` field is a table of conditions that, when met, will trigger the event and execute the `OnActions`.
- The `OnActions` field is a table of actions that the event performs when `OnConditions` is triggered.
- The `OffConditions` field is a table of conditions that, when met, will execute the `OffActions`.
- The `OffActions` field is a table of actions that the event perform when the `OffConditions` is triggered.

**Note**: `OnToggleEvent` can be used in place of `OnEvent` for Events that are aimed to trigger several times. This is achieved by setting identical conditions/actions for both the off and on states.

### BeginScript
```
BeginScript
{
    Conditions = {},
    Actions = {},
}
```
Waits with the execution of the script until the Conditions have been met. If an NPC uses this, they should NEVER be able to die until then! Mainly intended for platform scripts.
- The `Conditions` field is a table of conditions that, when met, will trigger the event.
- The `Actions` field is a table of actions that is executed when the event is triggered.

### KillScript
```
KillScript
{
    Conditions = {},
    Actions = {},
}
```
Terminates the execution of a script. Should not be used for NPCs that can die! Mainly intended for platform scripts!
- The `Conditions` field is a table of conditions that, when met, will trigger the event.
- The `Actions` field is a table of actions that is executed when the event is triggered.


### OnWakeUpEvent
```
OnWakeUpEvent
{
    SleepOnlyOnce = TRUE,
    SleepConditions = {},
    SleepActions = {},
    WakeUpConditions = {},
    WakeUpActions = {},
}
```
This event puts an NPC into a sleep state when the `SleepConditions` are met and wakes it up when the `WakeUpConditions` are met.
- The `SleepOnlyOnce` field determines whether the NPC will only go to sleep once. If this is set to `TRUE`, the NPC will not go to sleep again after the `WakeUpConditions` are met.
- The `SleepConditions` field is a table of conditions that, when met, will cause the NPC to go to sleep.
- The `SleepActions` field is a table of actions that the NPC should perform while it is sleeping.
- The `WakeUpConditions` field is a table of conditions that, when met, will cause the NPC to wake up.
- The `WakeUpActions` field is a table of actions that the NPC should perform once it wakes up.

"Sleep" implies that the NPC will not trigger global events, thus not impacting performance while in this state. It will not check for events or engage in dialogues, only monitoring for `WakeUpConditions`.

**IMPORTANT**: If `SleepOnlyOnce` is set to TRUE and the NPC dies and respawns, it will not return to sleep mode post-respawn. Conversely, if `SleepOnlyOnce` is FALSE, ensure that `SleepConditions` are invalidated once `WakeUpConditions` become true to avoid an infinite loop.

### OnFollowMe
Used only in NPC Scripts.
```
OnFollowMe
{
    X = ,
    Y = ,
    Direction = random,
    LeadRange = 20,
    Conditions = {},
    Actions = {},
    HomeActions = {},
}
```
This function implements a "Marcus-Style" follow. The entity requests the player to follow. The entity runs ahead. If the entity is outside the `LeadRange`, it stops and calls "Over here". If the player then does not come trotting along, the entity goes into follow mode and "searches" for the player.
- The `X` and `Y` fields determine the coordinates of the location.
- The `Direction` field determines the direction in which the entity should move. By default, it is set to a random direction.
- The `LeadRange` field determines the range within which the entity will lead the player. By default, it is set to 20.
- The `Conditions` field is a table of conditions that, when met, will trigger the event.
- The `Actions` field is a table of actions that is executed when the event is triggered.
- The `HomeActions` field is a table of actions that the entity should perform when it returns to its home location.


### OnFollowForever
```
{
    Target = ,
    NpcId = NpcId,
    Conditions = {},
    Actions = {},
}
```
This event allows an NPC to follow a target indefinitely under certain conditions.
- The `Target` field specifies the NpcId of the target that the NPC should follow.
- The `NpcId` field is the ID of the NPC that will be following the target. This is typically the NPC itself.
- The `Conditions` field is a table of conditions that, when met, will cause the NPC to start following the target.
- The `Actions` field is a table of actions that the NPC should perform while it is following the target.

**Notes:**
- The event automatically checks if the target is alive, the NPC has no aggro and is idle.
- The persistence of the follow mode remains as long as the `Conditions` are true. If the `Conditions` are no longer true, then the NPC will not resume his follow after platform change.
- The event saves data for respawn reactivation of follow. If the NPC dies and respawns, it will continue to follow the target if the `Conditions` are still met.

### OnFollowToggle
Used only in NPC Scripts.
```
{
    Target = ,
    NpcId = NpcId,
    FollowOnlyOnce = FALSE,
    FollowConditions = {},
    FollowActions = {},
    StopFollowConditions = {},
    StopFollowActions = {},
}
```
This event allows an NPC to follow a target under certain conditions and stop following under other conditions.
- The `Target` field specifies the NpcId of the target that the NPC should follow.
- The `NpcId` field is the ID of the NPC that will be following the target. This is typically the NPC itself.
- The `FollowOnlyOnce` field determines whether the NPC will only follow the target once. If this is set to `TRUE`, the NPC will not follow the target again after the `StopFollowConditions` are met.
- The `FollowConditions` field is a table of conditions that determine when the NPC should start following the target.
- The `FollowActions` field is a table of actions that the NPC should perform while it is following the target.
- The `StopFollowConditions` field is a table of conditions that determine when the NPC should stop following the target.
- The `StopFollowActions` field is a table of actions that the NPC should perform after it stops following the target.

**Notes:**
- The event automatically checks if the target is alive, the NPC has no aggro and is idle.
- The persistence of the follow mode remains as long as the `FollowConditions` are true. If no StopFollow was executed, but the `FollowConditions` are no longer true, then the NPC will not resume his follow after platform change! (Exception: NP platforms)

### OnAttackPattern
```
OnAttackPattern
{
    PatternAlpha = 
    {
        Retries = ,
        GuardTime = ,
        [1] = {X= , Y= , Direction= , WalkMode= },
        [2] = {X= , Y= , Direction= , WalkMode= },
    },
    PatternDelta = 
    {
        Retries = ,
        GuardTime = ,
        [1] = {X= , Y= , Direction= , WalkMode= },
        [2] = {X= , Y= , Direction= , WalkMode= },
    },
    PatternOmega = 
    {
        Retries = ,
        GuardTime = ,
        [1] = {X= , Y= , Direction= , WalkMode= },
        [2] = {X= , Y= , Direction= , WalkMode= },
    },
    CommonGoal = {X= , Y= , GuardTime= },
    Name = ,
    RestartAfterCommonGoal = FALSE,
}
```
This function defines an attack pattern for AI. The `PatternAlpha`, `PatternDelta`, and `PatternOmega` are different attack patterns that can be chosen. Each pattern has a `Retries` field which defines how often to take this attack path consecutively, a `GuardTime` parameter which defines the seconds to wait at each point, and a set of points with their X and Y coordinates, direction, and walk mode. The `CommonGoal` is the common target point for all patterns.
- The `PatternAlpha`, `PatternDelta`, and `PatternOmega` fields are a table of different attack patterns that can be chosen. Each pattern is a table of waypoints, each waypoint is a table with X, Y, Direction, and WalkMode fields.
    - The `Retries` field defines how often to take this attack path consecutively.
    - The `GuardTime` field defines the seconds to wait at each waypoint.
    - The `[<number>]` field is a table that defines waypoints to be followed containing the following fields:
        - The `X` and `Y` fields defines the X/Y coordinates of the waypoint.
        - The `Direction` field determines the direction the entity should face when at the waypoint. If `Direction` is not specified, the entity will face a random direction at the waypoint. Available directions are `East`, `SouthEast`, `South`, `SouthWest`, `West`, `NorthWest`, `North` and `NorthEast`.
        - The `WalkMode` field defines if units should follow this waypoint by walking or running which is determined by `Walk` or `Run`.
- The `CommonGoal` field is a table representing the common target point for all patterns. It has X, Y, and GuardTime fields that works in the same way as the explanation above.
- The `Name` field is a string that represents the name of the attack pattern.
- The `RestartAfterCommonGoal` field is a boolean that determines whether the attack pattern should restart after reaching the common goal. If this is set to `FALSE`, the attack pattern will not restart. By default, it is set to `FALSE`.