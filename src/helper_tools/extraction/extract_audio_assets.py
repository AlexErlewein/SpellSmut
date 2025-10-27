"""
SpellForce Audio Asset Scanner
Scans PAK data and Lua scripts to identify all audio files for extraction.

This script:
1. Parses DrwSound.lua to extract all WAV file references
2. Parses SndTracks.lua to extract all MP3 file references
3. Scans pakdata.dat for audio file entries
4. Categorizes sounds by type
5. Generates comprehensive extraction lists

Author: SpellSmut Modding Project
Date: October 18, 2025
"""

import os
import re
from pathlib import Path
from collections import defaultdict

# Paths
GAME_DIR = Path(r"H:\SpellSmut\OriginalGameFiles")
SCRIPT_DIR = GAME_DIR / "script"
MODDING_SCRIPTS_DIR = GAME_DIR / "modding" / "Original Scripts" / "script"
PAKDATA_FILE = GAME_DIR / "pakdata.dat"
OUTPUT_DIR = Path(r"H:\SpellSmut\ExtractedAssets\Audio")

# Sound categories based on file naming patterns
SOUND_CATEGORIES = {
    # Music tracks (MP3)
    'music_menu': r'.*menu.*\.mp3$',
    'music_battle': r'.*(battle|combat).*\.mp3$',
    'music_location': r'.*(plain|world|location).*\.mp3$',
    'music_theme': r'(spellforce|elven|army_of_darkness|death_music).*\.mp3$',
    'music_other': r'.*\.mp3$',

    # Environmental sounds
    'ambient': r'atmo_.*\.wav$',
    'object_sounds': r'object_.*\.wav$',

    # Spell sounds
    'spell_cast': r'spell_cast_.*\.wav$',
    'spell_resolve': r'spell_resolve_.*\.wav$',
    'spell_hit': r'spell_hit_.*\.wav$',
    'spell_melee': r'spell_melee_.*\.wav$',
    'spell_summon': r'spell_summon.*\.wav$',
    'spell_other': r'spell_.*\.wav$',

    # Combat sounds
    'battle_char': r'battle_char_.*\.wav$',
    'battle_hero': r'battle_hero_.*\.wav$',
    'battle_npc': r'battle_npc_.*\.wav$',
    'battle_race': r'battle_race_.*\.wav$',
    'battle_titan': r'battle_titan_.*\.wav$',
    'battle_hit': r'battle_hit_.*\.wav$',
    'battle_weapon': r'battle_weapon_.*\.wav$',
    'battle_other': r'battle_.*\.wav$',

    # Work sounds
    'work_build': r'work_build_.*\.wav$',
    'work_gather': r'work_(cut|get)_.*\.wav$',
    'work_other': r'work_.*\.wav$',

    # Movement sounds
    'movement': r'(step_|wings_).*\.wav$',

    # UI sounds
    'ui': r'ui_.*\.wav$',

    # Idle/ambient character sounds
    'idle': r'idle_.*\.wav$',

    # Other
    'other': r'.*\.(wav|mp3)$',
}


def parse_drwsound_lua():
    """
    Parse DrwSound.lua to extract all sound file references.
    Returns a list of sound files (WAV format).
    """
    print("=" * 60)
    print("Parsing DrwSound.lua for sound effects...")
    print("=" * 60)

    drwsound_path = SCRIPT_DIR / "DrwSound.lua"
    if not drwsound_path.exists():
        print(f"WARNING: {drwsound_path} not found!")
        return []

    sound_files = set()

    with open(drwsound_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Pattern 1: File = "filename" (single file)
    single_file_pattern = r'File\s*=\s*"([^"]+)"'
    matches = re.findall(single_file_pattern, content)
    for match in matches:
        # Add .wav extension if not present
        if not match.endswith('.wav'):
            match = match + '.wav'
        sound_files.add(match)

    # Pattern 2: File = {"file1", "file2", ...} (array of files)
    array_pattern = r'File\s*=\s*\{([^}]+)\}'
    array_matches = re.findall(array_pattern, content)
    for array_match in array_matches:
        # Extract individual filenames from array
        file_pattern = r'"([^"]+)"'
        files = re.findall(file_pattern, array_match)
        for file in files:
            if not file.endswith('.wav'):
                file = file + '.wav'
            sound_files.add(file)

    print(f"Found {len(sound_files)} unique sound effect files in DrwSound.lua")
    return sorted(list(sound_files))


def parse_sndtracks_lua():
    """
    Parse SndTracks.lua to extract all music track references.
    Returns a list of music files (MP3 format).
    """
    print("\n" + "=" * 60)
    print("Parsing SndTracks.lua for music tracks...")
    print("=" * 60)

    # Try multiple possible locations
    sndtracks_paths = [
        SCRIPT_DIR / "SndTracks.lua",
        MODDING_SCRIPTS_DIR / "SndTracks.lua",
    ]

    sndtracks_path = None
    for path in sndtracks_paths:
        if path.exists():
            sndtracks_path = path
            print(f"Found SndTracks.lua at: {path}")
            break

    if not sndtracks_path:
        print("WARNING: SndTracks.lua not found in any expected location!")
        return []

    music_files = set()

    with open(sndtracks_path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    # Pattern: filename.mp3 references
    mp3_pattern = r'([a-zA-Z0-9_]+\.mp3)'
    matches = re.findall(mp3_pattern, content)
    music_files.update(matches)

    # Also look for quoted strings
    quoted_pattern = r'"([^"]+\.mp3)"'
    quoted_matches = re.findall(quoted_pattern, content)
    music_files.update(quoted_matches)

    print(f"Found {len(music_files)} unique music files in SndTracks.lua")
    return sorted(list(music_files))


def scan_pakdata():
    """
    Scan pakdata.dat binary file for audio file references.
    Returns a list of audio files found in PAK archives.
    """
    print("\n" + "=" * 60)
    print("Scanning pakdata.dat for audio files...")
    print("=" * 60)

    if not PAKDATA_FILE.exists():
        print(f"WARNING: {PAKDATA_FILE} not found!")
        return []

    audio_files = set()

    # Read binary file
    with open(PAKDATA_FILE, 'rb') as f:
        data = f.read()

    # Convert to string for regex matching (ignore encoding errors)
    try:
        text = data.decode('latin-1', errors='ignore')
    except:
        print("ERROR: Could not read pakdata.dat")
        return []

    # Search for audio file patterns
    # WAV files
    wav_pattern = r'([a-zA-Z0-9_\-]+\.wav)'
    wav_matches = re.findall(wav_pattern, text, re.IGNORECASE)
    audio_files.update(wav_matches)

    # MP3 files
    mp3_pattern = r'([a-zA-Z0-9_\-]+\.mp3)'
    mp3_matches = re.findall(mp3_pattern, text, re.IGNORECASE)
    audio_files.update(mp3_matches)

    # Clean up filenames (remove special characters)
    cleaned_files = set()
    for file in audio_files:
        # Remove leading non-alphanumeric characters
        file = re.sub(r'^[^a-zA-Z0-9]+', '', file)
        if file:
            cleaned_files.add(file.lower())

    print(f"Found {len(cleaned_files)} unique audio files in pakdata.dat")
    return sorted(list(cleaned_files))


def categorize_audio_files(audio_files):
    """
    Categorize audio files by type based on naming patterns.
    Returns a dictionary of category -> file list.
    """
    print("\n" + "=" * 60)
    print("Categorizing audio files...")
    print("=" * 60)

    categorized = defaultdict(list)

    for file in audio_files:
        categorized_flag = False

        # Try to match each category pattern (in order)
        for category, pattern in SOUND_CATEGORIES.items():
            if re.match(pattern, file, re.IGNORECASE):
                categorized[category].append(file)
                categorized_flag = True
                break  # Only assign to first matching category

        # If no category matched, put in 'other'
        if not categorized_flag:
            categorized['other'].append(file)

    # Print category counts
    print("\nCategory Breakdown:")
    print("-" * 60)
    total = 0
    for category in sorted(categorized.keys()):
        count = len(categorized[category])
        total += count
        print(f"  {category:20s}: {count:4d} files")
    print("-" * 60)
    print(f"  {'TOTAL':20s}: {total:4d} files")

    return dict(categorized)


def save_extraction_lists(categorized_audio):
    """
    Save extraction lists to text files by category.
    """
    print("\n" + "=" * 60)
    print("Saving extraction lists...")
    print("=" * 60)

    # Create output directories
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    lists_dir = OUTPUT_DIR / "extraction_lists"
    lists_dir.mkdir(exist_ok=True)

    # Save master list
    master_list_path = OUTPUT_DIR / "audio_assets_list.txt"
    with open(master_list_path, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("SpellForce Platinum Edition - Audio Assets Master List\n")
        f.write("=" * 70 + "\n\n")

        total = sum(len(files) for files in categorized_audio.values())
        f.write(f"Total Audio Files: {total}\n\n")

        for category in sorted(categorized_audio.keys()):
            files = categorized_audio[category]
            f.write(f"\n{category.upper()}\n")
            f.write("-" * 70 + "\n")
            for file in sorted(files):
                f.write(f"{file}\n")

    print(f"Saved master list: {master_list_path}")

    # Save category-specific lists
    for category, files in categorized_audio.items():
        if not files:
            continue

        category_file = lists_dir / f"{category}.txt"
        with open(category_file, 'w', encoding='utf-8') as f:
            f.write(f"# SpellForce Audio Assets - {category.upper()}\n")
            f.write(f"# Total files: {len(files)}\n")
            f.write("#\n")
            f.write("# Use this list with SpellforceDataEditor to extract these assets\n")
            f.write("#\n\n")

            for file in sorted(files):
                f.write(f"{file}\n")

        print(f"  Saved: {category}.txt ({len(files)} files)")

    print(f"\nExtraction lists saved to: {lists_dir}")


def generate_summary_report(categorized_audio):
    """
    Generate a summary report with statistics and recommendations.
    """
    summary_path = OUTPUT_DIR / "EXTRACTION_SUMMARY.md"

    total_files = sum(len(files) for files in categorized_audio.values())
    wav_count = sum(len(files) for cat, files in categorized_audio.items()
                    if any(f.endswith('.wav') for f in files))
    mp3_count = sum(len(files) for cat, files in categorized_audio.items()
                    if any(f.endswith('.mp3') for f in files))

    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("# SpellForce Audio Assets - Extraction Summary\n\n")
        f.write(f"**Date:** October 18, 2025\n\n")
        f.write("## Overview\n\n")
        f.write(f"Successfully identified **{total_files} audio files** from SpellForce: Platinum Edition.\n\n")

        f.write("## File Breakdown\n\n")
        f.write(f"- **WAV Files (Sound Effects):** ~{wav_count}\n")
        f.write(f"- **MP3 Files (Music):** ~{mp3_count}\n\n")

        f.write("## Categories\n\n")
        f.write("| Category | Count | Description |\n")
        f.write("|----------|-------|-------------|\n")

        for category in sorted(categorized_audio.keys()):
            count = len(categorized_audio[category])
            desc = category.replace('_', ' ').title()
            f.write(f"| {desc} | {count} | {get_category_description(category)} |\n")

        f.write("\n## Extraction Instructions\n\n")
        f.write("1. Run `src/helper_tools/extract_audio_batch.bat` to launch SpellforceDataEditor\n")
        f.write("2. Go to the \"Asset Viewer\" tab\n")
        f.write("3. Wait for PAK files to load (5-10 minutes first time)\n")
        f.write("4. Search for specific audio files using the filter\n")
        f.write("5. Use the extraction lists in `extraction_lists/` as reference\n\n")

        f.write("## File Formats\n\n")
        f.write("- **WAV:** Uncompressed or ADPCM compressed audio (in-game sound effects)\n")
        f.write("- **MP3:** Compressed music tracks (streaming background music)\n\n")

        f.write("## Sound System Architecture\n\n")
        f.write("- **Engine:** Miles Sound System v3.x\n")
        f.write("- **3D Audio:** Distance-based falloff (FallOffMin/Max)\n")
        f.write("- **Event System:** Lua script-driven (DrwSound.lua)\n")
        f.write("- **Music System:** Priority-based track switching (SndTracks.lua)\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. Extract high-priority audio (music, combat sounds)\n")
        f.write("2. Convert audio to modern formats (OGG, FLAC)\n")
        f.write("3. Create audio preview catalog\n")
        f.write("4. Document audio event mappings\n")

    print(f"\nSummary report saved: {summary_path}")


def get_category_description(category):
    """Get a human-readable description for each category."""
    descriptions = {
        'music_menu': 'Main menu background music',
        'music_battle': 'Combat and battle music',
        'music_location': 'Location-specific themes',
        'music_theme': 'Main themes and special tracks',
        'music_other': 'Other music tracks',
        'ambient': 'Environmental atmospheric sounds',
        'object_sounds': 'Building and object sounds',
        'spell_cast': 'Spell casting sounds',
        'spell_resolve': 'Spell completion sounds',
        'spell_hit': 'Spell impact effects',
        'spell_melee': 'Melee buff/ability sounds',
        'spell_summon': 'Summoning sounds',
        'spell_other': 'Other spell-related sounds',
        'battle_char': 'Main character combat sounds',
        'battle_hero': 'Hero unit combat sounds',
        'battle_npc': 'NPC creature combat sounds',
        'battle_race': 'Race-specific combat sounds',
        'battle_titan': 'Titan unit sounds',
        'battle_hit': 'Weapon impact sounds',
        'battle_weapon': 'Weapon swing/miss sounds',
        'battle_other': 'Other combat sounds',
        'work_build': 'Building construction sounds',
        'work_gather': 'Resource gathering sounds',
        'work_other': 'Other work-related sounds',
        'movement': 'Footsteps and movement sounds',
        'ui': 'User interface sounds',
        'idle': 'Idle character ambient sounds',
        'other': 'Miscellaneous audio files',
    }
    return descriptions.get(category, category.replace('_', ' ').title())


def main():
    """Main execution function."""
    print("\n" + "=" * 70)
    print(" " * 15 + "SpellForce Audio Asset Scanner")
    print("=" * 70 + "\n")

    # Step 1: Parse Lua scripts
    sound_effects = parse_drwsound_lua()
    music_tracks = parse_sndtracks_lua()

    # Step 2: Scan PAK data
    pak_audio = scan_pakdata()

    # Step 3: Combine all sources
    all_audio = set(sound_effects + music_tracks + pak_audio)
    print(f"\n{'=' * 60}")
    print(f"TOTAL UNIQUE AUDIO FILES: {len(all_audio)}")
    print(f"{'=' * 60}\n")

    # Step 4: Categorize
    categorized = categorize_audio_files(list(all_audio))

    # Step 5: Save extraction lists
    save_extraction_lists(categorized)

    # Step 6: Generate summary report
    generate_summary_report(categorized)

    print("\n" + "=" * 70)
    print("AUDIO ASSET SCANNING COMPLETE!")
    print("=" * 70)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Master list: {OUTPUT_DIR / 'audio_assets_list.txt'}")
    print(f"Extraction lists: {OUTPUT_DIR / 'extraction_lists'}")
    print(f"Summary report: {OUTPUT_DIR / 'EXTRACTION_SUMMARY.md'}")
    print("\nNext step: Run extract_audio_batch.bat to begin extraction!")


if __name__ == "__main__":
    main()
