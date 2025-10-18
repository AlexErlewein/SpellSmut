# SpellForce Audio Assets - Extraction Summary

**Date:** October 18, 2025

## Overview

Successfully identified **836 audio files** from SpellForce: Platinum Edition.

## File Breakdown

- **WAV Files (Sound Effects):** ~766
- **MP3 Files (Music):** ~70

## Categories

| Category | Count | Description |
|----------|-------|-------------|
| Ambient | 9 | Environmental atmospheric sounds |
| Battle Char | 22 | Main character combat sounds |
| Battle Hit | 56 | Weapon impact sounds |
| Battle Npc | 292 | NPC creature combat sounds |
| Battle Other | 188 | Other combat sounds |
| Battle Titan | 36 | Titan unit sounds |
| Battle Weapon | 6 | Weapon swing/miss sounds |
| Idle | 12 | Idle character ambient sounds |
| Movement | 16 | Footsteps and movement sounds |
| Music Battle | 11 | Combat and battle music |
| Music Location | 24 | Location-specific themes |
| Music Menu | 1 | Main menu background music |
| Music Other | 31 | Other music tracks |
| Music Theme | 3 | Main themes and special tracks |
| Object Sounds | 19 | Building and object sounds |
| Other | 4 | Miscellaneous audio files |
| Spell Cast | 7 | Spell casting sounds |
| Spell Hit | 43 | Spell impact effects |
| Spell Melee | 3 | Melee buff/ability sounds |
| Spell Other | 6 | Other spell-related sounds |
| Spell Resolve | 7 | Spell completion sounds |
| Spell Summon | 1 | Summoning sounds |
| Ui | 2 | User interface sounds |
| Work Build | 12 | Building construction sounds |
| Work Gather | 20 | Resource gathering sounds |
| Work Other | 5 | Other work-related sounds |

## Extraction Instructions

1. Run `src/helper_tools/extract_audio_batch.bat` to launch SpellforceDataEditor
2. Go to the "Asset Viewer" tab
3. Wait for PAK files to load (5-10 minutes first time)
4. Search for specific audio files using the filter
5. Use the extraction lists in `extraction_lists/` as reference

## File Formats

- **WAV:** Uncompressed or ADPCM compressed audio (in-game sound effects)
- **MP3:** Compressed music tracks (streaming background music)

## Sound System Architecture

- **Engine:** Miles Sound System v3.x
- **3D Audio:** Distance-based falloff (FallOffMin/Max)
- **Event System:** Lua script-driven (DrwSound.lua)
- **Music System:** Priority-based track switching (SndTracks.lua)

## Next Steps

1. Extract high-priority audio (music, combat sounds)
2. Convert audio to modern formats (OGG, FLAC)
3. Create audio preview catalog
4. Document audio event mappings
