# SpellForce: How to Add a New Race

## Overview

Adding a new race to SpellForce requires:
1. Modifying GameData.cff database (unit stats, buildings)
2. Editing Lua scripts (registering units, animations, sounds)
3. Creating 3D assets (meshes, animations, textures)
4. Creating audio assets (combat sounds, work sounds)

**Estimated Time:** 125-255 hours
**Complexity:** Advanced

## Current Races

SpellForce has 6 races with IDs 1-6:
- ID 1: Humans
- ID 2: Dwarves  
- ID 3: Elves
- ID 4: Trolls
- ID 5: Orcs
- ID 6: Dark Elves

**Your new race will be ID 7.**

## Key Files to Modify

1. `H:\SpellSmut\ModdingTools\SFGameDataEditor\Editor\src\main\resources\races.properties`
   - Add: `7=YourRaceName`

2. `H:\SpellSmut\OriginalGameFiles\data\GameData.cff`
   - Add race entry, unit stats, buildings
   - Edit with SFGameDataEditor tool

3. `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\object\object_figure_init.lua`
   - Add race to racenames array
   - Add shadow size entry
   - Create animation library
   - Register all units

4. `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\object\object_equipment_init.lua`
   - Add race to racenames array

5. `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\object\object_building_init.lua`
   - Register building light effect

6. `H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\script\DrwSound.lua`
   - Add race-specific combat sounds

## Step-by-Step Process

### Phase 1: Planning

Design your race:
- Visual theme and size
- Combat style
- Economy characteristics
- Unit roster (min 9 units: worker, fighters, ranged, mage, siege, titan, swarm)
- Building set (min 8 buildings: HQ, resource buildings, barracks, etc.)

### Phase 2: GameData.cff Editing

1. Open SFGameDataEditor: `cd H:\SpellSmut\ModdingTools\SFGameDataEditor\Editor\bin && java -jar Editor-alpha-9.jar`

2. Add race entry (ID 7):
   - Equipment Scaling: 100-180 (percentage)
   - Shadow Size: 0.8-2.0

3. For each unit, add:
   - Creature ID (use 5000+ to avoid conflicts)
   - Stats (strength, dexterity, intelligence, etc.)
   - Resistances
   - Speeds
   - Mesh names
   - Race ID: 7

4. For each building, add:
   - Building ID (use 6000+)
   - HP, costs, build time
   - Mesh names
   - Race ID: 7

5. Link units to buildings (Creature Buildings section)

6. Export as GameData.cff.mod

### Phase 3: Lua Script Modifications

See key files section above for specific edits.

**Example animation library structure:**
{% raw %}
```lua
local YourRaceAnims = {
    base_name = "figure_yourrace",
    kGdJobDefault = {"idle"; mode = kDrwPlayLooped},
    kGdJobGroupWalk = {{"walk"; mode = kDrwPlayLooped}, {"run"; mode = kDrwPlayLooped}},
    walkcycle = {4.5, 8.0, 6.0},
    kGdJobPunch = {{"punch_01"; sound = "battle_race_yourrace_attack"}},
    kGdJobStrike = {{"strike_01"; sound = "battle_race_yourrace_attack"}},
    kGdJobCriticalHit = {{"hit_01"; sound = "battle_race_yourrace_scream"}},
    kGdJobDie = {{"die"; sound = "battle_race_yourrace_die"}},
    kGdJobWoodCutterCutTree = {{"cuttree"; sound = "work_cutwood"}},
    kGdJobStoneMinerCrushStone = {{"crushstone"; sound = "work_crushstone"}},
    -- Add all job types
}
Movies.figure_yourrace = CreateMovieLib(YourRaceAnims)
```
{% endraw %}

### Phase 4: Asset Creation

**3D Assets:**
- Unit meshes (.msh): 800-4000 tris depending on unit type
- Skeletons (.bor): bone hierarchy matching SpellForce format
- Animations (.boa): idle, walk, run, combat, death, work animations
- Building meshes (.msh): 500-3000 tris
- Textures (.tga): 512x512 or 1024x1024

**Audio Assets (.wav):**
- battle_yourraceworker_hit_01.wav to _03.wav
- battle_yourraceworker_att_01.wav to _03.wav
- battle_yourraceworker_die.wav
- battle_yourracefighter_hit_01.wav to _03.wav
- battle_yourracefighter_att_01.wav to _03.wav
- battle_yourracefighter_die.wav
- battle_titan_yourrace_att_01.wav to _03.wav
- battle_titan_yourrace_hit_01.wav to _02.wav
- battle_titan_yourrace_die.wav

Format: 16-bit PCM WAV, 22050 or 44100 Hz, mono

### Phase 5: Create Mod Package

Create directory structure:
```
H:\SpellSmut\MyMods\YourRace\
├── script\
│   └── assets.lua
├── mesh\
│   └── (all .msh files)
├── animation\
│   └── (all .bor and .boa files)
├── texture\
│   └── (all texture files)
├── sound\
│   └── speech\
│       └── battle\
│           └── (all sound files)
└── data\
    └── GameData.cff.mod
```

Create assets.lua:
```lua
local Bones = {"figure_yourrace"}
local Anims = {"figure_yourrace_idle.boa", "figure_yourrace_walk.boa", ...}
local Meshes = {"figure_yourrace_worker_male.msh", ...}
local BattleSounds = {"battle_yourraceworker_hit_01", ...}

return {
    Bones = Bones,
    Anims = Anims,
    Meshes = Meshes,
    BattleSounds = BattleSounds,
}
```

### Phase 6: Installation and Testing

1. Copy mod to: `H:\SpellSmut\OriginalGameFiles\mods\YourRace\`
2. Backup original GameData.cff
3. Copy GameData.cff.mod to `H:\SpellSmut\OriginalGameFiles\data\GameData.cff`
4. Launch game
5. Test in Skirmish mode

## Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Pink/purple units | Missing textures | Check texture file paths |
| Invisible units | Mesh not loading | Verify mesh paths in assets.lua |
| No animations | Animation files missing | Check .boa files and naming |
| No sounds | Sounds not registered | Check DrwSound.lua entries |
| Crash on race selection | GameData.cff corruption | Re-edit GameData.cff |
| Units can't be produced | Missing building links | Check Creature Buildings in GameData.cff |

## Tools Required

- SFGameDataEditor (H:\SpellSmut\ModdingTools\SFGameDataEditor\)
- 3D software (Blender recommended)
- Audio editor (Audacity recommended)
- Text editor (VS Code, Notepad++)

## Checklist

- [ ] races.properties modified
- [ ] GameData.cff entries created (race, units, buildings)
- [ ] object_figure_init.lua modified
- [ ] object_equipment_init.lua modified
- [ ] object_building_init.lua modified
- [ ] DrwSound.lua modified
- [ ] All meshes created
- [ ] All animations created
- [ ] All sounds created
- [ ] assets.lua created
- [ ] Mod directory structure set up
- [ ] Game tested

## Resources

- Original scripts: H:\SpellSmut\OriginalGameFiles\modding\Original Scripts\
- Study existing races as templates
- SpellForce modding community forums

---

**Created for SpellSmut project**  
**Version 1.0 - 2025-01-15**
