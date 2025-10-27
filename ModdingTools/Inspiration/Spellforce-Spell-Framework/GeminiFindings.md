# Spellforce-Spell-Framework Analysis

An analysis of the Spellforce-Spell-Framework project reveals that it is a powerful, low-level C++ toolkit designed to create custom spell logic for *Spellforce 1 Platinum Edition*. It operates by injecting a DLL (`.asi` file) into the game, which then loads custom mod files and uses function hooking to override the game's default spell behaviors.

Here is a detailed breakdown of how the framework handles game data and the creation of new spells, with a special focus on the inclusion of icons and images.

### How the Framework Handles Game Data

The framework's core design is to separate the **logic** of a spell from its static **data**.

1.  **Spell Logic (C++ Code):** The framework allows developers to write C++ functions that define what a spell *does*. This is handled through a system of "handlers" that are registered for specific Spell IDs. The example file `src/dev/TestMod.cpp` demonstrates this process clearly:
    *   **`registerSpell(spell_id)`**: A mod claims a specific Spell ID.
    *   **`linkTypeHandler(...)`**: A function is linked to handle the initial cast of the spell.
    *   **`linkEffectHandler(...)`**: A function is linked to handle the spell's ongoing effect (e.g., damage over time, buffs).
    *   **`linkEndHandler(...)`**: A function is linked to handle the spell's expiration or cleanup.

2.  **Spell Data (`GameData.cff`):** The framework does **not** manage the fundamental data of a spell, such as its name, description, mana cost, level requirements, or visual appearance. A crucial comment in the `TestMod.cpp` example file clarifies this:

    ```cpp
    // This custom spell type and custom spell effect need to be setup manually in the GameData.cff file currently
    ```

    This means that a mod author must use a separate tool to edit the game's primary data file, `GameData.cff`. Within this file, they would define a new spell entry, assign it the same Spell ID that they use in their C++ code, and configure all its static properties.

### Handling of Icons and Images

The framework **does not include any functionality for adding new icons or images to the game**. The API headers (`sfsf.h`, `sf_figure_functions.h`, etc.) contain no functions for loading textures, manipulating UI elements, or assigning graphical assets to spells.

The process for assigning an icon to a new spell created with this framework is as follows:

1.  **Reuse Existing Icons:** The modder must choose an icon that already exists within the original game's asset files.
2.  **Reference in `GameData.cff`:** Using a `GameData.cff` editor, the modder would find the ID or reference for the desired existing icon.
3.  **Assign Icon to Spell:** In the new spell's data entry within `GameData.cff`, the modder would set the icon property to point to that existing icon.

When the spell is cast in-game, the C++ logic from the framework's mod is executed, but the game engine reads the `GameData.cff` file to determine which icon to display on the UI.

### Summary

| Feature | Handled by Spellforce-Spell-Framework? | How it Works |
| :--- | :--- | :--- |
| **Spell Logic & Behavior** | **Yes** | Developers write C++ functions for spell casting, effects, and expiration, then link them to a Spell ID using the framework's registration API. |
| **Spell Name & Description** | **No** | Must be defined manually in `GameData.cff` using a separate editor. |
| **Spell Mana Cost & Requirements** | **No** | Must be defined manually in `GameData.cff`. |
| **Spell Icons & Images** | **No** | The framework has no API for graphics. Modders must **reuse existing in-game icons** and assign them to the new spell within the `GameData.cff` file. |

In conclusion, the Spellforce-Spell-Framework is a code-centric tool for injecting complex, dynamic behaviors into the game. It is not an asset management tool. Creating a complete custom spell requires a two-part process: using this framework for the *logic* and using other modding tools to edit the game's data files for the *static properties and visual representation*, which involves reusing existing game icons.
