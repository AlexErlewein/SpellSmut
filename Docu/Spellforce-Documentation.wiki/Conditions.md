## Functions
**OR(condition1, condition2):** This is an OR function that checks if either of the two conditions is true. It returns True if either condition1 or condition2 is true, and False otherwise. 

**ODER(condition1, condition2):** This function is similar to OR. It also checks if either of the two conditions is true and returns True if either condition1 or condition2 is true, and False otherwise.

## Tables
**IsGlobalFlagTrue{Name=“FlagName”}:** This conditional checks if a global flag (identified by “FlagName”) is set to true.

**IsGlobalFlagFalse{Name=“FlagName”}:** This conditional checks if a global flag (identified by “FlagName”) is set to false.

**Negated(condition):** This function takes a condition as an argument and returns the opposite of that condition's truth value. If the condition is true, Negated(condition) will return false, and vice versa.

**IsMonumentInUse(Name=“MonumentName”):** This conditional checks if a monument (identified by “MonumentName”) is currently in use.

**TimeOfDay{Hour=, Minute=, TimeFrame=, UpdateInterval=}**: This conditional checks whether the current time corresponds to the specified time, with a tolerance of + TimeFrame minutes. For example, at 12:30, it must be at least 12:30, and the maximum can be 12:30 + TimeFrame minutes for the condition to be true.
* **Hour =**: Specifies the hour of the day (in 24-hour format) for the condition.
* **Minute =**: Specifies the minute of the hour for the condition. This parameter is optional and defaults to 0 if not specified.
* **TimeFrame =**: Specifies the tolerance in minutes for the condition. This parameter is optional and defaults to 15 minutes if not specified.
* **UpdateInterval =**: Specifies how often the condition should be checked, in GdSteps (10 GdSteps = 1 second). This parameter is optional and defaults to 60 GdSteps if not specified.

**PlayerHasGood{Good=, Amount=, Sides=, Player=, UpdateInterval=}:** This checks whether the player has a certain amount of a certain resource.
* **Good =**: Specifies the type of Good. Goods can be GoodBoard(Wood), GoodStone, GoodMithril, GoodFood, GoodIron, GoodManaElixir(Aria), GoodManaHerb(Lenya).
* **Amount =**: Specifies the minimum amount of the specified resource. This parameter is optional and defaults to 1 if not specified.
* **Sides =**: Specifies which side to check for the resources. Sides can be SideLight (Human, Elves and Dwarves), SideDark (Dark Elves, Trolls and Orcs) or SideAll for both. This parameter is optional and defaults to SideGood if not specified.
* **Player =**: Specifies the Player to be checked (For Multiplayer). This parameter is optional and defaults to 1 if not specified.
* **UpdateInterval =**: Specifies how often the condition should be checked, in GdSteps (10 GdSteps = 1 second). This parameter is optional and defaults to 60 GdSteps if not specified.
<details>
  <summary><b>PlayerHasGood</b> Syntax:</summary>
  <pre><code>
PlayerHasGood
{
    Good = ,
    Amount = 1,
    Side = SideAll,
    Player = 1,
    UpdateInterval = 60,
}
  </code></pre>
</details>

**IsClanSize{Clan=, Size=, UpdateInterval=}**: Checks if the ClanSize of `Clan` equals the `Size` field. It's recommended to use IsNpcCounter for better interaction with ClanSize for complex scripts if you want to make use of Conditional Operators.

**IsNpcCounter**: Disclaimer: When using this to track `RtsSpawn` `Group` size, NEVER allow the condition to trigger on the same value as the `Group` `SpawnLimit` otherwise you'll have an Always-True Event which will block any Events below this one from triggering.
