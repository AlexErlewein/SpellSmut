# SpellForce Platinum Edition - Complete Sound System Guide

## Table of Contents

1. [Sound System Architecture Overview](#sound-system-architecture-overview)
2. [Sound File Organization](#sound-file-organization)
3. [Sound Types and Categories](#sound-types-and-categories)
4. [How to Add Custom Sounds](#how-to-add-custom-sounds)
5. [Voice Acting and Speech System](#voice-acting-and-speech-system)
6. [Music System](#music-system)
7. [Technical Specifications](#technical-specifications)
8. [Modding Workflow](#modding-workflow)

---

## Sound System Architecture Overview

SpellForce uses a **hybrid sound architecture** with three main components:

### 1. **Core Engine (C++)** - Miles Sound System
- RAD Game Tools' Miles Sound System handles audio playback
- Manages 3D positional audio with distance attenuation
- Handles streaming for music tracks
- Provides low-level audio mixing

### 2. **Lua Scripting Layer**
- Defines all sound events and their properties
- Maps sounds to game actions (combat, spells, UI, etc.)
- Controls music transitions and priorities
- Manages speech tags and dialogue

### 3. **PAK Archive Storage**
- Sound files are stored in compressed `.pak` archives
- Can also load from loose files in the game directory
- Mod system allows overriding sounds without modifying base files

---

## Sound File Organization

### Directory Structure

All sounds are stored within the following directories (either loose files or inside PAK archives):

```
<game_root>/
├── sound/                          # Root sound directory
│   ├── *.wav                       # Sound effects (environmental, spells, UI, etc.)
│   ├── *.mp3                       # Music tracks (streaming)
│   │
│   └── speech/                     # All voice acting
│       ├── male/                   # Male protagonist voice
│       │   └── *.wav               # Dialogue files
│       │
│       ├── female/                 # Female protagonist voice
│       │   └── *.wav               # Dialogue files
│       │
│       ├── messages/               # System messages/tutorials
│       │   └── *.wav               # Info/tutorial voice files
│       │
│       └── battle/                 # Combat voice acting
│           └── *.wav               # Battle cries, screams, death sounds
```

### PAK Files Containing Sound Data

Based on file sizes, these PAK files likely contain sound assets:

- **sf1.pak** (675 MB) - Largest file, likely contains most sound effects and music
- **sf10.pak** (382 MB) - Expansion 2 sounds
- **sf22.pak** (245 MB) - Possibly expansion 1 sounds
- **sf33.pak** (553 MB) - Large file, likely contains speech/dialogue

---

## Sound Types and Categories

### 1. Environmental Sounds (Atmospheric)

Defined in: `script/DrwSound.lua` (lines 8-40)

**Properties:**
- `File`: Sound file name(s) without extension
- `Volume`: 0.0-1.0+ (can exceed 1.0 for louder sounds)
- `FallOffMin`: Distance (in game units) where attenuation begins
- `FallOffMax`: Distance where sound becomes inaudible
- `Length`: Duration override for looping sounds
- `Atmo`: Flag (1 = atmospheric/environmental sound)

**Examples:**
```lua
water = { 
    File = {"atmo_water_loop_01", "atmo_water_loop_02", "atmo_water_loop_03"},
    Volume = 0.6, 
    FallOffMin = 2,
    FallOffMax = 25, 
    Length = 3.0,
    Atmo = 1,
}

lava = { 
    File = "atmo_lava_loop_01", 
    Volume = 0.8, 
    FallOffMin = 2, 
    FallOffMax = 30, 
    Length = 3.0, 
    Atmo = 1 
}
```

**Categories:**
- Water atmospherics (rivers, lakes, ocean)
- Swamp ambience
- Lava bubbling
- Wind sounds
- Fire/torch crackling

### 2. Object Sounds

Defined in: `script/DrwSound.lua` (lines 42-57)

**Interactive Objects:**
- Torches (torch_loop_01)
- Campfires (campfire_loop_01)
- Obelisks (obelisk_loop_01)
- Bindstones/respawn points (bindstone)
- Building destruction (building_destroy)
- Portal activation/loop (portal_activate, portal_loop_01)

### 3. Spell System Sounds

Defined in: `script/DrwSound.lua` (lines 62-201)

**Spell Sound Stages:**
1. **Cast** - Spell initiation (casting animation)
2. **Resolve** - Spell completion (effect triggers)
3. **Hit** - Impact on target
4. **DOT** - Damage/effect over time loop
5. **Resist** - Target resists the spell

**Magic Schools:**
- **White Magic** (healing, buffs, holy)
  - Examples: `spell_white_cast_01`, `spell_white_resolve_01`, `spell_white_hit_01`
- **Black Magic** (necromancy, curses)
  - Examples: `spell_black_cast_01`, `spell_black_summon_01`
- **Fire Magic**
  - Examples: `spell_fire_cast_01`, `spell_fire_hit_01`, `spell_fire_dot_01`
- **Ice Magic**
  - Examples: `spell_ice_cast_01`, `spell_ice_hit_01`
- **Earth Magic**
  - Examples: `spell_earth_cast_01`, `spell_earth_resolve_01`
- **Air/Wind Magic**
  - Examples: `spell_air_cast_01`, `spell_air_hit_01`
- **Mental Magic** (mind control, confusion)
  - Examples: `spell_mental_cast_01`, `spell_mental_resolve_01`
- **Elemental Magic** (multi-element)

**Special Spell Sounds:**
- Summon spells (creatures, workers, heroes)
- Aura effects (persistent buffs/debuffs)
- Resurrection
- Polymorph
- Petrify/freeze

### 4. Combat Voice Acting

Defined in: `script/DrwSound.lua` (lines 208-522)

**Character Types with Voice Sets:**

#### Main Characters:
- `battle_char_m_*` - Male protagonist (6 variations per action)
- `battle_char_f_*` - Female protagonist (6 variations per action)

#### Heroes:
- `battle_hero_m_*` - 5 different male hero voice sets
- `battle_hero_f_*` - 5 different female hero voice sets

#### Playable Races (6 races × 3 voice types × up to 6 variations):
1. **Humans** - `battle_human_*`
2. **Orcs** - `battle_orc_*`
3. **Elves** - `battle_elf_*`
4. **Dark Elves** - `battle_darkelf_*`
5. **Dwarves** - `battle_dwarf_*`
6. **Trolls** - `battle_troll_*`

#### Titans (Super Units):
- `battle_titan_human_*`
- `battle_titan_orc_*`
- `battle_titan_elf_*`
- `battle_titan_darkelf_*`
- `battle_titan_dwarf_*`
- `battle_titan_troll_*`

#### NPCs and Creatures (40+ types):
Examples include:
- `battle_gargoyle_*`
- `battle_minotaur_*`
- `battle_medusa_*`
- `battle_skeleton_*`
- `battle_demon_*`
- `battle_dragon_*`
- `battle_golem_*`
- `battle_spider_*`
- etc.

**Voice Action Types:**
- **screams** - Hit reaction sounds (being hit)
- **attacks** - Battle cries (attacking)
- **dies** - Death sounds

**Example:**
```lua
battle_char_m_scream = {
    File = {
        "battle_char_m_hit_01",
        "battle_char_m_hit_02",
        "battle_char_m_hit_03",
        "battle_char_m_hit_04",
        "battle_char_m_hit_05",
        "battle_char_m_hit_06"
    },
    Volume = 1, 
    FallOffMin = 10, 
    FallOffMax = 90
}
```

### 5. Weapon Sounds

Defined in: `script/DrwSound.lua` (lines 523-750)

**Weapon Categories:**

#### Melee Weapons (Hit Sounds):
- **Unarmed**: Mouth (bite), Fist
- **Bladed**: Daggers, Swords (1H/2H), Axes (1H/2H)
- **Blunt**: Maces (1H/2H, spiky/blunt), Hammers (1H/2H)
- **Polearms**: Staves (1H/2H), Spears, Halberds
- **Special**: Claws

#### Ranged Weapons:
- Bows
- Crossbows

**Sound Mixing Strategy:**
The game mixes similar weapon types to increase variety:

```lua
battle_hit_1hsword = {
    File = {
        "battle_hit_1hsword_01", 
        "battle_hit_1hsword_02", 
        "battle_hit_1hsword_03", 
        "battle_hit_1haxe_01",      -- Cross-weapon variation
        "battle_hit_1haxe_02",
        "battle_hit_1hdagger_03",
        "battle_hit_2hsword_01",
        "battle_hit_2hsword_02"
    },
    Volume = 1, 
    FallOffMin = 10,
    FallOffMax = 90
}
```

**Miss Sounds:**
Separate sounds for weapons swinging through air without hitting.

### 6. Work/Economy Sounds

Defined in: `script/DrwSound.lua` (lines 758-859)

**Resource Gathering:**
- Building construction
- Stone cutting (quarry)
- Wood chopping (lumber mill)
- Mining (ore, iron, coal, bronze)
- Smithing/crafting
- Food production
- Fishing
- Animal husbandry

---

## How to Add Custom Sounds

### Method 1: Loose Files (Easiest for Testing)

1. **Create the directory structure:**
   ```
   <game_root>/sound/
   ```

2. **Add your WAV files:**
   - For sound effects: Place `.wav` files directly in `sound/`
   - For battle speech: Place in `sound/speech/battle/`
   - For dialogue: Place in `sound/speech/male/` or `sound/speech/female/`

3. **Register in DrwSound.lua:**
   
   Edit `<game_root>/script/DrwSound.lua` and add your sound definition:
   
   ```lua
   -- Add to the Data table (around line 6)
   local Data = {
       -- ... existing sounds ...
       
       -- Your custom sound
       my_custom_sound = {
           File = "my_custom_sound_01",  -- Without .wav extension
           Volume = 1.0,
           FallOffMin = 10,
           FallOffMax = 50
       },
   }
   ```

### Method 2: PAK Archive (For Distribution)

1. **Create mod directory structure:**
   ```
   MyMod/
   ├── sound/
   │   ├── my_sound_01.wav
   │   ├── my_sound_02.wav
   │   └── speech/
   │       └── battle/
   │           ├── battle_myrace_scream_01.wav
   │           └── battle_myrace_attack_01.wav
   └── script/
       └── assets.lua
   ```

2. **Create assets.lua:**
   ```lua
   -- MyMod/script/assets.lua
   return {
       Bones = {},
       Anims = {},
       Meshes = {},
       BattleSounds = {
           "battle_myrace_scream_01",
           "battle_myrace_attack_01"
       }
   }
   ```

3. **Pack into PAK archive:**
   Use the FilePacker tool:
   ```batch
   tool_filepacker.exe MyMod
   ```
   This creates `MyMod.pak` and updates `assets.lua`

4. **Install the mod:**
   - Place `MyMod.pak` in the game's mod directory
   - The game will automatically merge your sounds with the base game

### Adding New Race Combat Sounds

To add sounds for a new race (e.g., "Goblin"):

1. **Record/prepare audio files:**
   - `battle_goblin_scream_01.wav` through `battle_goblin_scream_06.wav`
   - `battle_goblin_attack_01.wav` through `battle_goblin_attack_06.wav`
   - `battle_goblin_dies_01.wav` through `battle_goblin_dies_03.wav`

2. **Place files in:**
   ```
   sound/speech/battle/
   ```

3. **Register in DrwSound.lua:**
   ```lua
   -- Add to Data table (around line 300-400)
   battle_goblin_scream = {
       File = {
           "battle_goblin_scream_01",
           "battle_goblin_scream_02",
           "battle_goblin_scream_03",
           "battle_goblin_scream_04",
           "battle_goblin_scream_05",
           "battle_goblin_scream_06"
       },
       Volume = 1,
       FallOffMin = 10,
       FallOffMax = 90
   },
   
   battle_goblin_attack = {
       File = {
           "battle_goblin_attack_01",
           "battle_goblin_attack_02",
           "battle_goblin_attack_03",
           "battle_goblin_attack_04",
           "battle_goblin_attack_05",
           "battle_goblin_attack_06"
       },
       Volume = 1,
       FallOffMin = 10,
       FallOffMax = 90
   },
   
   battle_goblin_dies = {
       File = {
           "battle_goblin_dies_01",
           "battle_goblin_dies_02",
           "battle_goblin_dies_03"
       },
       Volume = 1,
       FallOffMin = 10,
       FallOffMax = 90
   }
   ```

4. **Map to weapon types (if needed):**
   ```lua
   -- Add to BattleData table (around line 863)
   local BattleData = { 
       hits = {
           -- ... existing mappings ...
           kDrwWtGoblinClaw = "battle_hit_claw",  -- Reuse existing or create new
       },
       misses = {
           kDrwWtGoblinClaw = "battle_miss_claw",
       }
   }
   ```

### Adding New Spell Sounds

For a new spell (e.g., "Lightning Storm"):

1. **Prepare audio files:**
   - `spell_lightning_cast_01.wav` - Casting sound
   - `spell_lightning_resolve_01.wav` - Spell completion
   - `spell_lightning_hit_01.wav` - Impact sound
   - `spell_lightning_dot_01.wav` - Ongoing damage loop (optional)

2. **Register in DrwSound.lua:**
   ```lua
   -- Add to Data table
   spell_lightning_cast = {
       File = "spell_lightning_cast_01",
       Volume = 1.0,
       FallOffMin = 15,
       FallOffMax = 100
   },
   
   spell_lightning_resolve = {
       File = "spell_lightning_resolve_01",
       Volume = 1.2,
       FallOffMin = 20,
       FallOffMax = 150
   },
   
   spell_lightning_hit = {
       File = "spell_lightning_hit_01",
       Volume = 0.9,
       FallOffMin = 10,
       FallOffMax = 80
   },
   
   spell_lightning_dot = {
       File = "spell_lightning_dot_01",
       Volume = 0.7,
       FallOffMin = 8,
       FallOffMax = 60,
       Length = 2.0  -- Loop duration
   }
   ```

---

## Voice Acting and Speech System

### Speech Tag System

SpellForce uses a **tag-based system** for dialogue and voice acting. Each line of dialogue has:
- A **Tag** - Unique identifier linking text to audio file
- A **String** - Display text (can be localized)
- An **NpcId** - Character speaking
- A **Color** - Text color (optional)

### Tag Naming Convention

Pattern: `<type><number><character><map>_<sequence>`

Examples:
- `cs01GrimP101_001` - Cutscene 01, Grim character, Platform 101, line 001
- `cs14RagnarP108_003` - Cutscene 14, Ragnar character, Platform 108, line 003
- `ocRodeP008_001` - Outcry, Rode character, Platform 008, line 001

### Dialogue Functions

#### 1. CutSceneSay (Cinematic Dialogue)

Used in cutscenes with camera control:

```lua
CutSceneSay {
    Tag = "cs01GrimP101_001",           -- Unique audio file identifier
    NpcId = 5536,                        -- Character ID (Grim)
    String = "Endlich!",                 -- Display text
    Color = ColorWhite                   -- Optional text color
}
```

**Audio File Location:**
- Male characters: `sound/speech/male/<tag>.wav`
- Female characters: `sound/speech/female/<tag>.wav`

**Example:** Tag `cs01GrimP101_001` → `sound/speech/male/cs01GrimP101_001.wav`

#### 2. Outcry (Combat/World Dialogue)

Used for in-game dialogue without cinematic control:

```lua
Outcry {
    Tag = "ocRagnarP008_002",
    NpcId = 6048,
    String = "Der Preis wird hoch sein, mein K□nig!",
    Color = ColorWhite,
    Delay = TRUE  -- 3-second delay before next outcry (prevents overlap)
}
```

#### 3. SetInfoText (Tutorial/System Messages)

Used for narrator/tutorial text:

```lua
SetInfoText {
    Tag = "tutorial_movement_001",
    String = "Click to move your character",
    Color = ColorYellow,
    ClearAfterSpeech = TRUE  -- Clear text after audio finishes
}
```

**Audio File Location:** `sound/speech/messages/<tag>.wav`

### WaitForEndOfSpeech

In cutscenes, use this marker to pause until speech finishes:

```lua
TimedActions = {
    [10] = {
        CutSceneSay {Tag = "line1", NpcId = 123, String = "First line"},
        WaitForEndOfSpeech,  -- Wait until audio completes
    },
    [20] = {
        CutSceneSay {Tag = "line2", NpcId = 456, String = "Second line"},
    }
}
```

### Adding Custom Dialogue for Quests

**Example: Adding dialogue to a quest NPC**

1. **Record voice files:**
   - `quest_merchant_greeting_001.wav`
   - `quest_merchant_accept_001.wav`
   - `quest_merchant_complete_001.wav`

2. **Place files:**
   - Male NPC: `sound/speech/male/`
   - Female NPC: `sound/speech/female/`

3. **Use in quest script:**
   ```lua
   -- In your quest script (script/p<mapid>/n<npcid>.lua)
   
   -- Initial greeting
   Outcry {
       Tag = "quest_merchant_greeting_001",
       NpcId = 9876,
       String = "Greetings, traveler! I have a task for you.",
       Color = ColorWhite
   }
   
   -- Quest acceptance
   Outcry {
       Tag = "quest_merchant_accept_001",
       NpcId = 9876,
       String = "Excellent! Return when you've found the artifact.",
       Color = ColorGreen
   }
   
   -- Quest completion
   Outcry {
       Tag = "quest_merchant_complete_001",
       NpcId = 9876,
       String = "You've done it! Here is your reward.",
       Color = ColorYellow
   }
   ```

---

## Music System

### Music Track Types

Defined in: `script/SndTracks.lua`

**Track Priority System** (highest to lowest):

1. **Movie** (Priority 150) - Cinematic videos
2. **Death** (Priority 120) - Player death
3. **DominationOpener** (Priority 118) - Map domination intro
4. **DominationLoop** (Priority 117) - Map domination loop
5. **Combat/Battle** (Priority 115) - Combat music
6. **PlatformOpener** (Priority 114) - Entering new map/platform
7. **LocationOpener** (Priority 113) - Entering special location (town, dungeon)
8. **MainMenu** (Priority 112) - Main menu
9. **LocationLoop** (Priority 90) - Location ambient music
10. **Night** (Priority 25) - Nighttime music
11. **PlatformPlain** (Priority 20) - General exploration

### Music Interruption Rules

Each track type can interrupt lower-priority tracks. Example:

- Combat music (115) interrupts LocationLoop (90)
- LocationOpener (113) interrupts Combat (115) - **special rule for dramatic entrances**
- Death music (120) interrupts everything except Movie

### Music Track Registration

**Format:** Tracks are registered in `script/SndTracks.lua`:

```lua
-- Main menu music (varies by expansion)
if SndAddon2Installed then
    SndAddTrack{Id = 200, File = "army_of_darkness.mp3", Type = "MainMenu", Volume = 1}
elseif SndAddonInstalled then
    SndAddTrack{Id = 111, File = "elvensong_menu.mp3", Type = "MainMenu", Volume = 1}
else
    SndAddTrack{Id = 5, File = "spellforce.mp3", Type = "MainMenu", Volume = 0.8}
end

-- Battle music
SndAddTrack{Id = 17, File = "battle_music1.mp3", Type = "Battle", Volume = 0.9}
SndAddTrack{Id = 18, File = "combat_music2.mp3", Type = "Combat", Volume = 0.9}

-- Location music
SndAddTrack{Id = 2, File = "elves_and_angels.mp3", Type = "LocationOpener", Volume = 1}
SndAddTrack{Id = 36, File = "elves_and_angels.mp3", Type = "LocationLoop", Volume = 1}
```

### Map-Specific Music Assignment

Defined in: `script/SndTrackTransitions.lua`

```lua
-- Assign music to specific maps
SndDefineMapPlain{
    Map = "P101",              -- Map ID
    OpenerId = 3,              -- Entry music track ID
    PlainId = 55               -- Exploration music track ID
}

-- Region-specific music within a map
SndDefineLocationTrack{
    Map = "P101",
    OpenerId = 2,              -- Music when entering region
    LoopId = 36,               -- Music while in region
    X = 150,                   -- Region center X
    Y = 200,                   -- Region center Y
    Radius = 50                -- Region radius
}
```

### Adding Custom Music Tracks

1. **Prepare MP3 file:**
   - Encoding: MP3, CBR or VBR
   - Recommended: 192-320 kbps for quality
   - **Must be seamlessly loopable** (start/end match perfectly)

2. **Place file:**
   ```
   sound/my_epic_battle.mp3
   ```

3. **Register in SndTracks.lua:**
   ```lua
   -- Add after existing tracks
   SndAddTrack{
       Id = 250,                           -- Unique ID (use 250+)
       File = "my_epic_battle.mp3",
       Type = "Battle",                    -- Or Combat, LocationOpener, etc.
       Volume = 0.95
   }
   ```

4. **Assign to map (optional):**
   ```lua
   -- In SndTrackTransitions.lua or your map script
   SndDefineMapPlain{
       Map = "P999",          -- Your custom map
       OpenerId = 250,
       PlainId = nil          -- Use default
   }
   ```

---

## Technical Specifications

### Audio File Requirements

#### WAV Files (Sound Effects & Speech)

**Format Specifications:**
- **Container:** WAV (RIFF WAVE)
- **Bit Depth:** 16-bit PCM (recommended)
- **Sample Rate:** 22050 Hz or 44100 Hz
- **Channels:** Mono (for 3D positional sounds) or Stereo (for UI/music)
- **Endianness:** Little-endian

**File Naming:**
- Use only alphanumeric characters, underscores, and hyphens
- No spaces in filenames
- Case-sensitive on some systems (use lowercase recommended)
- No file extension in Lua definitions (auto-appended)

**Size Considerations:**
- Keep individual sound files under 500 KB when possible
- Use compression (MP3) for longer audio like music
- Battle voice lines: typically 0.5-3 seconds (50-200 KB)
- Spell sounds: 0.3-2 seconds (30-150 KB)

#### MP3 Files (Music)

**Format Specifications:**
- **Container:** MP3
- **Bitrate:** 192-320 kbps CBR (Constant Bit Rate) recommended
- **Sample Rate:** 44100 Hz
- **Channels:** Stereo
- **Encoding:** LAME encoder recommended for best compatibility

**Looping:**
- Must be seamlessly loopable (no clicks/pops at loop point)
- Use tools like Audacity or Adobe Audition to ensure perfect loops
- Test in-game to verify smooth transitions

### 3D Positional Audio Parameters

**FallOffMin:**
- Distance (in game units) where sound is at full volume
- Typical values: 2-20 (small objects), 10-30 (characters), 15-50 (large objects)

**FallOffMax:**
- Distance where sound becomes inaudible (0% volume)
- Typical values: 25-100 (ambient), 80-150 (combat), 100-200 (spells)

**Volume:**
- Base volume multiplier (0.0 = silent, 1.0 = full, >1.0 = boosted)
- Typical values: 0.6-1.2
- Affected by master volume and distance attenuation

**Example Configurations:**

```lua
-- Close-range intimate sound (torch)
torch_loop = {
    Volume = 0.5,
    FallOffMin = 2,   -- Full volume within 2 units
    FallOffMax = 15   -- Inaudible beyond 15 units
}

-- Medium-range combat sound
battle_scream = {
    Volume = 1.0,
    FallOffMin = 10,  -- Full volume within 10 units
    FallOffMax = 80   -- Inaudible beyond 80 units
}

-- Long-range spell effect
spell_meteor = {
    Volume = 1.5,     -- Boosted for impact
    FallOffMin = 25,  -- Full volume in large radius
    FallOffMax = 200  -- Audible across battlefield
}
```

### Performance Considerations

**Sound Instance Limits:**
- Miles Sound System has a maximum simultaneous sound limit
- Typically 32-64 concurrent 3D sounds
- Prioritization system drops lowest-priority sounds when limit reached
- Music streams don't count against this limit

**Memory Usage:**
- WAV files loaded into memory when needed
- MP3 files streamed from disk
- Keep total WAV memory usage reasonable (avoid thousands of huge files)

---

## Modding Workflow

### Complete Workflow: Adding a New Race with Full Audio

**Scenario:** Adding "Centaur" race to the game

#### Step 1: Audio Production

1. **Record/source audio files:**
   ```
   Battle voices (6 variations each):
   - battle_centaur_scream_01 to 06.wav  (hit reactions)
   - battle_centaur_attack_01 to 06.wav  (battle cries)
   - battle_centaur_dies_01 to 03.wav    (death sounds)
   
   Weapon sounds (optional, can reuse existing):
   - battle_hit_centaur_spear_01 to 03.wav
   - battle_miss_centaur_spear_01 to 02.wav
   ```

2. **Audio specifications:**
   - Format: WAV, 16-bit PCM
   - Sample rate: 44100 Hz
   - Channels: Mono (for 3D positional)
   - Length: 0.5-3 seconds per file
   - Normalize to -3dB peak to prevent clipping

#### Step 2: File Organization

Create mod directory structure:

```
CentaurMod/
├── sound/
│   └── speech/
│       └── battle/
│           ├── battle_centaur_scream_01.wav
│           ├── battle_centaur_scream_02.wav
│           ├── battle_centaur_scream_03.wav
│           ├── battle_centaur_scream_04.wav
│           ├── battle_centaur_scream_05.wav
│           ├── battle_centaur_scream_06.wav
│           ├── battle_centaur_attack_01.wav
│           ├── battle_centaur_attack_02.wav
│           ├── battle_centaur_attack_03.wav
│           ├── battle_centaur_attack_04.wav
│           ├── battle_centaur_attack_05.wav
│           ├── battle_centaur_attack_06.wav
│           ├── battle_centaur_dies_01.wav
│           ├── battle_centaur_dies_02.wav
│           └── battle_centaur_dies_03.wav
│
└── script/
    ├── assets.lua
    └── CentaurSounds.lua (optional extension to DrwSound.lua)
```

#### Step 3: Create Mod Manifest

**CentaurMod/script/assets.lua:**
```lua
return {
    Bones = {},
    Anims = {},
    Meshes = {},
    BattleSounds = {
        "battle_centaur_scream_01",
        "battle_centaur_scream_02",
        "battle_centaur_scream_03",
        "battle_centaur_scream_04",
        "battle_centaur_scream_05",
        "battle_centaur_scream_06",
        "battle_centaur_attack_01",
        "battle_centaur_attack_02",
        "battle_centaur_attack_03",
        "battle_centaur_attack_04",
        "battle_centaur_attack_05",
        "battle_centaur_attack_06",
        "battle_centaur_dies_01",
        "battle_centaur_dies_02",
        "battle_centaur_dies_03"
    }
}
```

#### Step 4: Register Sounds

**Option A: Modify base DrwSound.lua** (not recommended for distribution)

Edit `<game_root>/script/DrwSound.lua`:

```lua
-- Add to Data table (around line 400)
battle_centaur_scream = {
    File = {
        "battle_centaur_scream_01",
        "battle_centaur_scream_02",
        "battle_centaur_scream_03",
        "battle_centaur_scream_04",
        "battle_centaur_scream_05",
        "battle_centaur_scream_06"
    },
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 90
},

battle_centaur_attack = {
    File = {
        "battle_centaur_attack_01",
        "battle_centaur_attack_02",
        "battle_centaur_attack_03",
        "battle_centaur_attack_04",
        "battle_centaur_attack_05",
        "battle_centaur_attack_06"
    },
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 90
},

battle_centaur_dies = {
    File = {
        "battle_centaur_dies_01",
        "battle_centaur_dies_02",
        "battle_centaur_dies_03"
    },
    Volume = 1.0,
    FallOffMin = 10,
    FallOffMax = 90
}
```

**Option B: Create mod script** (recommended for distribution)

**CentaurMod/script/CentaurSounds.lua:**
```lua
-- This file extends DrwSound.lua with Centaur sounds
-- Execute this after DrwSound.lua loads

-- Add Centaur sounds to the global Data table
if Data then
    Data.battle_centaur_scream = {
        File = {
            "battle_centaur_scream_01",
            "battle_centaur_scream_02",
            "battle_centaur_scream_03",
            "battle_centaur_scream_04",
            "battle_centaur_scream_05",
            "battle_centaur_scream_06"
        },
        Volume = 1.0,
        FallOffMin = 10,
        FallOffMax = 90
    }
    
    Data.battle_centaur_attack = {
        File = {
            "battle_centaur_attack_01",
            "battle_centaur_attack_02",
            "battle_centaur_attack_03",
            "battle_centaur_attack_04",
            "battle_centaur_attack_05",
            "battle_centaur_attack_06"
        },
        Volume = 1.0,
        FallOffMin = 10,
        FallOffMax = 90
    }
    
    Data.battle_centaur_dies = {
        File = {
            "battle_centaur_dies_01",
            "battle_centaur_dies_02",
            "battle_centaur_dies_03"
        },
        Volume = 1.0,
        FallOffMin = 10,
        FallOffMax = 90
    }
    
    print("Centaur sounds registered successfully!")
else
    print("ERROR: Data table not found! DrwSound.lua may not be loaded yet.")
end
```

#### Step 5: Package Mod

Use the FilePacker tool:

```batch
cd /d H:\SpellSmut\
tool_filepacker.exe CentaurMod
```

This creates:
- `CentaurMod.pak` - Compressed archive with all files
- Updates `CentaurMod/script/assets.lua` with file listings

#### Step 6: Install and Test

1. Copy `CentaurMod.pak` to the game's mod directory
2. The game automatically detects and loads mods on startup
3. Test in-game with Centaur units

#### Step 7: Distribution

Create a release package:

```
CentaurMod_v1.0/
├── CentaurMod.pak
├── README.txt          (installation instructions)
└── CREDITS.txt         (voice actor credits, licenses)
```

### Troubleshooting Common Issues

**Problem:** Sounds don't play in-game

**Solutions:**
1. Check file format (must be WAV 16-bit PCM or MP3)
2. Verify filenames match exactly (case-sensitive)
3. Ensure files are in correct directory structure
4. Check DrwSound.lua for syntax errors (missing commas, brackets)
5. Look at game logs for error messages

**Problem:** Audio cuts off or crackles

**Solutions:**
1. Check sample rate (44100 Hz recommended)
2. Verify bit depth (16-bit PCM)
3. Remove DC offset in audio editor
4. Add tiny fade-in/fade-out to prevent clicks
5. Normalize audio levels (-3dB peak maximum)

**Problem:** Mod sounds don't override base game

**Solutions:**
1. Ensure mod PAK is loaded after base game PAKs
2. Use exact same sound IDs as base game
3. Check that assets.lua is properly formatted
4. Verify mod directory structure matches base game

**Problem:** Music doesn't loop smoothly

**Solutions:**
1. Ensure MP3 has no encoder delay/padding
2. Use seamless loop editor (Audacity, Adobe Audition)
3. Export with zero padding at start/end
4. Test loop point before exporting final MP3

---

## Advanced Topics

### Dynamic Music System

The game uses a sophisticated **transition engine** (`script/SndTransitionEngine.lua`) that:

1. **Monitors game state** (combat, location, time of day)
2. **Evaluates track priorities** based on current conditions
3. **Cross-fades between tracks** smoothly (no abrupt cuts)
4. **Respects interrupt rules** (combat can interrupt ambient, etc.)

### Environmental Sound Mapping

In `script/SndEnvSounds.lua`, terrain textures are mapped to footstep sounds:

```lua
EnvSoundCol:AttachTexture("landscape_island_002_grassD", "grass")
EnvSoundCol:AttachTexture("landscape_island_007_stoneD", "stone")
EnvSoundCol:AttachTexture("landscape_island_019_snowD", "snow")
```

This creates contextual footstep sounds based on terrain type.

### Sound Randomization

The game prevents audio fatigue by:
- Using arrays of sound variations (6+ per action)
- Randomly selecting from the array each time
- Mixing similar sounds (swords with axes) for more variety

### Localization Support

For multi-language mods:

1. Create separate directories per language:
   ```
   sound/speech/male/en/  (English)
   sound/speech/male/de/  (German)
   sound/speech/male/pl/  (Polish)
   ```

2. Game detects language and loads appropriate files
3. Fallback to default if language files missing

---

## Conclusion

SpellForce Platinum Edition has a **comprehensive and moddable sound system** that supports:

✅ Custom sound effects (environmental, combat, spells)  
✅ New voice acting (races, heroes, NPCs, dialogue)  
✅ Custom music tracks (location-specific, dynamic combat)  
✅ Full 3D positional audio  
✅ Mod-friendly architecture (non-destructive additions)  

**Key Takeaways:**

1. **All sounds are stored** in `sound/` directory (loose or PAK archived)
2. **Sound definitions** are in `script/DrwSound.lua` (effects) and `script/SndTracks.lua` (music)
3. **Speech uses Tag system** - each dialogue line has unique audio file
4. **Battle voices** need 6 variations per action to prevent repetition
5. **Music system** is priority-based with smooth transitions
6. **Modding is straightforward** - create files, register in Lua, package as PAK

**Recommended Tools:**

- **Audio Recording/Editing:** Audacity (free), Adobe Audition, Reaper
- **MP3 Encoding:** LAME encoder
- **PAK Packing:** tool_filepacker.exe (included with game)
- **Script Editing:** Any text editor (VS Code, Notepad++, Sublime Text)

For questions or community support, visit:
- SpellForce Discord: discord.gg/spellforce (#spellforce1_mods channel)
- Steam Community: https://steamcommunity.com/app/39540/discussions/

---

**Document Version:** 1.0  
**Last Updated:** 2025  
**Game Version:** SpellForce Platinum Edition (Steam AppID 39540)
