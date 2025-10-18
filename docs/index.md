# SpellForce Platinum Edition - Modding Documentation

Welcome to the comprehensive modding documentation for **SpellForce: The Order of Dawn - Platinum Edition**! This wiki provides in-depth guides for creating custom content, from races and spells to complete campaigns.

---

## 📚 Table of Contents

- [📚 Table of Contents](#-table-of-contents)
- [🎮 Game Systems](#-game-systems)
  - [Quest System Guide](#quest-system-guide)
  - [Spell System Guide](#spell-system-guide)
  - [Sound System Guide](#sound-system-guide)
- [🛠️ Content Creation](#️-content-creation)
  - [Race Creation Guide](#race-creation-guide)
  - [Campaign System Guide](#campaign-system-guide)
  - [Quest & Campaign Creation Guide](#quest--campaign-creation-guide)
  - [Multiplayer & FreeGame Guide](#multiplayer--freegame-guide)
- [🚀 Quick Start Guides](#-quick-start-guides)
  - [For Beginners](#for-beginners)
  - [For Intermediate Modders](#for-intermediate-modders)
  - [For Advanced Modders](#for-advanced-modders)
- [📖 Documentation Format](#-documentation-format)
- [🛠️ Required Tools](#️-required-tools)
  - [Essential](#essential)
  - [Recommended](#recommended)
- [📁 Project Structure](#-project-structure)
- [🎓 Learning Path](#-learning-path)
  - [Phase 1: Foundations (Week 1-2)](#phase-1-foundations-week-1-2)
  - [Phase 2: Systems (Week 3-4)](#phase-2-systems-week-3-4)
  - [Phase 3: Content (Week 5-6)](#phase-3-content-week-5-6)
  - [Phase 4: Integration (Week 7-8)](#phase-4-integration-week-7-8)
  - [Phase 5: Polish (Week 9+)](#phase-5-polish-week-9)
- [🤝 Community Resources](#-community-resources)
  - [Official](#official)
  - [Fan Resources](#fan-resources)
- [💾 Modding Workflow](#-modding-workflow)
  - [1. Planning](#1-planning)
  - [2. Development](#2-development)
  - [3. Integration](#3-integration)
  - [4. Packaging](#4-packaging)
  - [5. Distribution](#5-distribution)
- [🔍 Finding Information](#-finding-information)
  - [By Topic](#by-topic)
  - [By Skill Level](#by-skill-level)
- [⚙️ Technical Reference](#️-technical-reference)
  - [Lua Scripting](#lua-scripting)
  - [File Formats](#file-formats)
  - [Key Systems](#key-systems)
- [📝 Contributing to Documentation](#-contributing-to-documentation)
- [🎮 Happy Modding!](#-happy-modding)

---

## 🎮 Game Systems

#### [Quest System Guide](SpellForce_Quest_System_Guide.md)
Learn how to create quests, dialogue systems, and interactive storytelling elements.

**Topics Covered:**
- Quest creation fundamentals
- Dialogue and NPC interactions
- Branching quest paths
- Quest triggers and conditions
- Reward systems

---

#### [Spell System Guide](SpellForce_Spell_System_Guide.md)
Complete guide to SpellForce's magic system and creating custom spells.

**Topics Covered:**
- Spell types and schools (White, Black, Fire, Ice, Earth, Air, Mental, Elemental)
- Spell parameters and effects
- Casting mechanics
- Visual effects and animations
- Balancing spells

---

#### [Sound System Guide](SOUND_SYSTEM_GUIDE.md)
Everything you need to know about audio in SpellForce - from sound effects to music to voice acting.

**Topics Covered:**
- Sound architecture and file organization
- Environmental sounds and ambience
- Combat voice acting
- Spell sound effects
- Music system and dynamic tracks
- Speech/dialogue system (Tag-based)
- 3D positional audio
- Adding custom sounds and voice recordings

---

### 🛠️ Content Creation

#### [Race Creation Guide](Race_Creation_Guide.md)
Step-by-step guide to creating entirely new playable races.

**Topics Covered:**
- Race data structures
- Unit definitions
- Building trees
- Technology progression
- Balancing new races

---

#### [Campaign System Guide](SpellForce_Campaign_System_Guide.md)
Master the campaign creation system for story-driven experiences.

**Topics Covered:**
- Campaign structure and flow
- Map progression
- Story integration
- Cutscene scripting
- Platform/map connections
- Save system integration

---

#### [Quest & Campaign Creation Guide](SpellForce_Quest_Campaign_Creation_Guide.md)
Comprehensive guide combining quests and campaigns into cohesive experiences.

**Topics Covered:**
- Integrating quests into campaigns
- Story arc development
- Character progression across maps
- World-building techniques
- Narrative design patterns

---

#### [Multiplayer & FreeGame Guide](SpellForce_Multiplayer_FreeGame_Guide.md)
Create multiplayer maps and FreeGame (skirmish) content.

**Topics Covered:**
- Multiplayer map design
- FreeGame mode setup
- AI configuration
- Balance considerations
- Map scripting for multiplayer
- Network/sync considerations

---

## 🚀 Quick Start Guides

### For Beginners
1. Start with the **[Quest System Guide](SpellForce_Quest_System_Guide.md)** to learn basic scripting
2. Move to **[Sound System Guide](SOUND_SYSTEM_GUIDE.md)** to add audio to your content
3. Try creating a simple custom spell using the **[Spell System Guide](SpellForce_Spell_System_Guide.md)**

### For Intermediate Modders
1. Create custom content with **[Race Creation Guide](Race_Creation_Guide.md)**
2. Build story-driven experiences with **[Campaign System Guide](SpellForce_Campaign_System_Guide.md)**
3. Design multiplayer experiences with **[Multiplayer & FreeGame Guide](SpellForce_Multiplayer_FreeGame_Guide.md)**

### For Advanced Modders
1. Combine everything in **[Quest & Campaign Creation Guide](SpellForce_Quest_Campaign_Creation_Guide.md)**
2. Create total conversions using all guides together

---

## 📖 Documentation Format

Each guide includes:
- **📋 Table of Contents** - Navigate to specific topics
- **🔧 Technical Specifications** - File formats, data structures, parameters
- **💡 Examples** - Code snippets and real implementations
- **🎯 Best Practices** - Tips from experienced modders
- **⚠️ Common Pitfalls** - Avoid frequent mistakes
- **🔗 Cross-References** - Links to related guides

---

## 🛠️ Required Tools

### Essential
- **SpellForce Platinum Edition** (Steam AppID: 39540)
- **Text Editor** (VS Code, Notepad++, Sublime Text)
- **Lua 4.0** knowledge (scripting language)

### Recommended
- **FilePacker Tool** (`tool_filepacker.exe`) - Create PAK archives
- **SFGameDataEditor** - Edit game data (units, spells, items)
- **3D Modeling Software** (Blender, 3ds Max) - For custom models
- **Audio Editor** (Audacity, Adobe Audition) - For custom sounds
- **FBX Converter** - Convert 3D assets to SpellForce format

---

## 📁 Project Structure

Understanding the game's file organization:

```
SpellForce/
├── pak/                    # PAK archives (compressed game assets)
├── script/                 # Lua scripts (game logic, systems)
│   ├── DrwSound.lua       # Sound definitions
│   ├── SndTracks.lua      # Music tracks
│   └── p###/              # Map-specific scripts
├── sound/                  # Audio files
│   ├── *.wav              # Sound effects
│   ├── *.mp3              # Music tracks
│   └── speech/            # Voice acting
│       ├── male/
│       ├── female/
│       └── battle/
├── texture/               # Textures and fonts
├── mesh/                  # 3D models
├── animation/             # Skeletal animations
└── videos/                # Bink video cutscenes
```

---

## 🎓 Learning Path

### Phase 1: Foundations (Week 1-2)
- Read **Quest System Guide** cover to cover
- Create a simple quest with dialogue
- Add sound effects using **Sound System Guide**

### Phase 2: Systems (Week 3-4)
- Study **Spell System Guide**
- Create 3-5 custom spells
- Experiment with different spell types

### Phase 3: Content (Week 5-6)
- Follow **Race Creation Guide** to create a basic race
- Design a small campaign using **Campaign System Guide**

### Phase 4: Integration (Week 7-8)
- Use **Quest & Campaign Creation Guide** to build a complete experience
- Add custom audio, spells, and races together

### Phase 5: Polish (Week 9+)
- Test thoroughly
- Balance gameplay
- Optimize performance
- Package for distribution

---

## 🤝 Community Resources

### Official
- **Steam Community**: [SpellForce Platinum Discussion](https://steamcommunity.com/app/39540/discussions/)
- **Discord**: discord.gg/spellforce (#spellforce1_mods channel)

### Fan Resources
- **Modding Forums**: Community-driven support
- **Asset Libraries**: Shared models, sounds, textures
- **Script Templates**: Pre-built quest and campaign templates

---

## 💾 Modding Workflow

### 1. Planning
- Design your mod concept
- Outline features and content
- Plan asset requirements

### 2. Development
- Create loose files in game directory for testing
- Use Lua scripts for game logic
- Test frequently in-game

### 3. Integration
- Organize files into mod structure
- Create `assets.lua` manifest
- Test mod loading system

### 4. Packaging
- Use FilePacker to create `.pak` archive
- Write installation instructions
- Create README with credits

### 5. Distribution
- Share on Steam Workshop (if available)
- Upload to modding sites
- Engage with community feedback

---

## 🔍 Finding Information

### By Topic
- **Audio/Sound**: → [Sound System Guide](SOUND_SYSTEM_GUIDE.md)
- **Magic/Spells**: → [Spell System Guide](SpellForce_Spell_System_Guide.md)
- **Quests/NPCs**: → [Quest System Guide](SpellForce_Quest_System_Guide.md)
- **Story/Campaigns**: → [Campaign System Guide](SpellForce_Campaign_System_Guide.md) or [Quest & Campaign Creation](SpellForce_Quest_Campaign_Creation_Guide.md)
- **Multiplayer**: → [Multiplayer & FreeGame Guide](SpellForce_Multiplayer_FreeGame_Guide.md)
- **New Races**: → [Race Creation Guide](Race_Creation_Guide.md)

### By Skill Level
- **Beginner**: Quest System → Sound System → Spell System
- **Intermediate**: Race Creation → Campaign System → Multiplayer
- **Advanced**: Quest & Campaign Creation (combines all systems)

---

## ⚙️ Technical Reference

### Lua Scripting
- **Version**: Lua 4.0
- **Syntax**: Legacy (pre-Lua 5.0)
- **Key Differences**: `getn()` instead of `#`, different table functions

### File Formats
- **Scripts**: `.lua` (Lua 4.0 syntax)
- **Sound Effects**: `.wav` (16-bit PCM, 44100 Hz)
- **Music**: `.mp3` (192-320 kbps)
- **Models**: `.msb` (SpellForce mesh format)
- **Animations**: `.bob` (SpellForce animation)
- **Skeletons**: `.bor` (bone rig)
- **Textures**: `.dds` (DirectDraw Surface)
- **Archives**: `.pak` (custom compression)

### Key Systems
- **DrwSound.lua**: Sound event definitions (~1000 lines)
- **SndTracks.lua**: Music track registration
- **GdsActions.lua**: Game action functions
- **GdsConditions.lua**: Game condition checks
- **Object Files**: Unit/spell/item definitions

---

## 📝 Contributing to Documentation

Found an error or want to add content?
1. Fork the repository
2. Make your changes
3. Submit a pull request

Documentation improvements are always welcome!

---

## 🎮 Happy Modding!

Whether you're creating a single custom spell or a full campaign, these guides will help you bring your vision to life in SpellForce. Start with any guide that interests you, and don't hesitate to jump between documents as you learn.

**Remember**: The best way to learn is by doing. Start small, test often, and gradually build up to more complex mods!

---

**Last Updated**: October 2025
**Game Version**: SpellForce Platinum Edition (Steam)
**Documentation Version**: 1.0
