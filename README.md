# SpellSmut - SpellForce Modding Project

A comprehensive modding project and documentation repository for **SpellForce: The Order of Dawn - Platinum Edition**.

## 📋 Issue Tracking with Beads

**This project uses [beads](https://github.com/ben-vargas/ai-beads) for task tracking.**

All development work is tracked in beads - a distributed, git-backed issue tracker designed for AI-agent collaboration.

**Quick Commands:**
```bash
bd ready              # View ready work (no blockers)
bd show SpellSmut-ID  # Show issue details
bd update ID --status in_progress  # Claim work
bd close ID           # Complete work
```

📖 **See [CONTRIBUTING.md](CONTRIBUTING.md) for the complete workflow.**
🤖 **AI Agents:** See [.ai/WORKFLOW.md](.ai/WORKFLOW.md) for universal workflow (works for Claude, GPT-4, Gemini, Qwen, Cursor, Windsurf, Zed, etc.).

## 📚 Documentation

**[View Complete Modding Documentation →](https://alexerlewein.github.io/SpellSmut/)**

Our documentation includes detailed guides for:

- **Quest System** - Create quests, dialogue, and interactive storytelling
- **Spell System** - Design custom spells and magic systems
- **Sound System** - Add audio, music, and voice acting
- **Race Creation** - Build entirely new playable races
- **Campaign System** - Craft story-driven campaign experiences
- **Multiplayer & FreeGame** - Design skirmish and multiplayer maps

## 🎨 Creator Tools

Comprehensive visual tools for creating mod content:

- **Quest Creator** - 6-phase wizard for custom quests with test maps
- **Spell Creator** - 7-phase "Spell Wizard" with 1-15 level progression system
- **Weapon Creator** - 7-phase "Weapon Forge" with edit-existing feature (719 weapons to modify)
- **Armor Creator** - 7-phase "Armor Forge" for custom armor pieces with stat bonuses
- **NPC Creator** - 7-phase "NPC Workshop" system for custom characters
- **Map Viewer** - 3D terrain viewer with texture rendering and lighting
- **Universal Savefile System** - ModSave Framework with custom file extensions
- **Utility Tools Suite** - Asset management, testing, and automation utilities

All tools feature integrated ID management to prevent conflicts and support collaborative modding.

## 🎮 About SpellForce

SpellForce Platinum Edition is a fantasy RTS/RPG hybrid released in 2005. This project aims to document its modding capabilities and provide tools for creating custom content.

## 🛠️ Project Structure

```
SpellSmut/
├── docs/                          # Complete modding documentation
│   ├── index.md                  # Documentation home page
│   ├── Quest_System_Guide.md     # Quest creation guide
│   ├── Spell_System_Guide.md     # Spell system guide
│   ├── Sound_System_Guide.md     # Audio & sound guide
│   └── ...                       # More specialized guides
├── OriginalGameFiles/            # Reference game files
├── tools/                        # Modding utilities
├── src/                          # Python scripts and modding utilities
│   ├── helper_tools/             # Asset extraction and organization scripts
│   └── TirganachReloaded/        # CFF editing library and tools
├── ProjectPlanning/              # Project plans and roadmaps
│   └── Components/               # Detailed system plans
│       ├── QUEST_CREATION_PLAN.md   # Quest Creator system plan
│       ├── SPELL_CREATION_PLAN.md   # Spell Creator system plan
│       ├── WEAPON_CREATION_PLAN.md  # Weapon Creator system plan
│       ├── ARMOR_CREATION_PLAN.md   # Armor Creator system plan
│       ├── NPC_CREATION_PLAN.md     # NPC Creator system plan
│       ├── MAP_VIEWER_STATUS.md     # Map Viewer development status
│       ├── SAVEFILE_SYSTEM.md       # Universal Savefile system plan
│       ├── UTILITY_TOOLS.md         # Utility tools suite plan
│       └── ID_MANAGEMENT_SYSTEM.md  # ID Management system plan
└── mods/                         # Custom mod content

```

## 🚀 Quick Start

1. **Read the documentation**: Visit the [documentation site](https://alexerlewein.github.io/SpellSmut/)
2. **Start with basics**: Begin with the Quest System Guide
3. **Experiment**: Try creating simple quests and spells
4. **Build up**: Gradually work towards more complex mods

## 📋 Project Plan

See **[ProjectPlanning/Components/MODDING_PLAN.md](ProjectPlanning/Components/MODDING_PLAN.md)** for:
- Completed tasks and achievements
- Current work in progress
- Future roadmap and milestones
- UI asset extraction status (✅ Complete - 683 assets cataloged!)
- Creator tool development plans (Quest, Spell, Weapon, Armor, NPC systems)
- ID Management System implementation
- Universal Savefile System specification

## 🤝 Contributing

Contributions to documentation and tools are welcome! Feel free to:

- Submit issues for documentation errors
- Propose new guides or sections
- Share modding discoveries
- Contribute tools and utilities

## 📝 License

This project is a community effort for educational and modding purposes. SpellForce and related trademarks are property of THQ Nordic and Grimlore Games.

## 🔗 Resources

- **Steam Page**: [SpellForce Platinum Edition](https://store.steampowered.com/app/39540/)
- **Steam Community**: [Discussions](https://steamcommunity.com/app/39540/discussions/)
- **Documentation**: [Modding Guides](https://alexerlewein.github.io/SpellSmut/)

---

**Last Updated**: October 2025  
**Game Version**: SpellForce Platinum Edition (Steam AppID: 39540)
