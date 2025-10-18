"""
Organize all extracted files into subcategories based on naming patterns.

This script analyzes file naming patterns across all extracted categories
and creates a detailed folder structure for better organization.
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict

# Paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
EXTRACTED_DIR = PROJECT_ROOT / "ExtractedAssets"


def organize_uncategorized_audio():
    """Further organize the uncategorized audio files by pattern."""
    print("\n" + "=" * 70)
    print("Organizing Uncategorized Audio Files...")
    print("=" * 70)

    audio_dir = EXTRACTED_DIR / "Audio" / "extracted" / "uncategorized"
    if not audio_dir.exists() or not os.listdir(audio_dir):
        print(f"No uncategorized audio files found")
        return

    # Subcategories for uncategorized audio
    categories = {
        'dialogue': {
            'pattern': lambda f: f.startswith('a_') and f.endswith('.mp3'),
            'description': 'Dialogue/voice acting (numbered MP3 files)'
        },
        'step': {
            'pattern': lambda f: f.startswith('step_') or f.startswith('wings_'),
            'description': 'Movement/footstep sounds'
        },
        'world': {
            'pattern': lambda f: f.startswith('world_'),
            'description': 'World event sounds'
        },
        'dummy': {
            'pattern': lambda f: f.startswith('dummy_'),
            'description': 'Placeholder/silence files'
        },
    }

    file_counts = defaultdict(int)
    moved_count = 0

    for file in os.listdir(audio_dir):
        source = audio_dir / file
        if not source.is_file():
            continue

        # Find matching category
        for cat_name, cat_info in categories.items():
            if cat_info['pattern'](file):
                # Create subcategory folder in main extracted dir
                dest_dir = EXTRACTED_DIR / "Audio" / "extracted" / cat_name
                dest_dir.mkdir(exist_ok=True)

                # Move file
                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    moved_count += 1
                    break
                except Exception as e:
                    print(f"  Error moving {file}: {e}")

    # Count remaining
    remaining = len([f for f in os.listdir(audio_dir) if (audio_dir / f).is_file()])

    print(f"\nMoved {moved_count} files into specific categories:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    print("-" * 70)
    print(f"  Remaining uncategorized: {remaining} files")


def organize_textures():
    """Organize texture files by naming patterns."""
    print("\n" + "=" * 70)
    print("Organizing Texture Files...")
    print("=" * 70)

    textures_dir = EXTRACTED_DIR / "Textures"
    if not textures_dir.exists():
        print(f"Textures directory not found: {textures_dir}")
        return

    # Texture categories based on naming
    categories = {
        'armor': {
            'pattern': lambda f: f.startswith('armor_'),
            'description': 'Armor and weapon textures'
        },
        'building': {
            'pattern': lambda f: f.startswith('building_'),
            'description': 'Building textures'
        },
        'character': {
            'pattern': lambda f: f.startswith('char_') or f.startswith('character_'),
            'description': 'Character/unit textures'
        },
        'creature': {
            'pattern': lambda f: f.startswith('creature_') or f.startswith('monster_'),
            'description': 'Creature/monster textures'
        },
        'effect': {
            'pattern': lambda f: f.startswith('effect_') or f.startswith('fx_'),
            'description': 'Visual effect textures'
        },
        'environment': {
            'pattern': lambda f: f.startswith('env_') or f.startswith('terrain_'),
            'description': 'Environmental textures'
        },
        'icon': {
            'pattern': lambda f: f.startswith('icon_'),
            'description': 'Game icons'
        },
        'object': {
            'pattern': lambda f: f.startswith('object_') or f.startswith('prop_'),
            'description': 'Object/prop textures'
        },
        'sky': {
            'pattern': lambda f: f.startswith('sky_') or f.startswith('cloud_'),
            'description': 'Sky and cloud textures'
        },
        'spell': {
            'pattern': lambda f: f.startswith('spell_'),
            'description': 'Spell effect textures'
        },
        'water': {
            'pattern': lambda f: f.startswith('water_'),
            'description': 'Water textures'
        },
    }

    file_counts = defaultdict(int)
    uncategorized = 0

    for file in os.listdir(textures_dir):
        source = textures_dir / file
        if not source.is_file():
            continue

        # Find matching category
        categorized = False
        for cat_name, cat_info in categories.items():
            if cat_info['pattern'](file):
                dest_dir = textures_dir / cat_name
                dest_dir.mkdir(exist_ok=True)

                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"  Error moving {file}: {e}")

        if not categorized:
            # Keep in root directory
            uncategorized += 1

    print("\nTexture Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    if uncategorized > 0:
        print(f"  {'uncategorized':20s}: {uncategorized:5d} files - Remaining in root")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(file_counts.values()) + uncategorized:5d} files")


def organize_models():
    """Organize model files by naming patterns."""
    print("\n" + "=" * 70)
    print("Organizing Model Files...")
    print("=" * 70)

    models_dir = EXTRACTED_DIR / "Models"
    if not models_dir.exists():
        print(f"Models directory not found: {models_dir}")
        return

    # Model categories
    categories = {
        'building': {
            'pattern': lambda f: f.startswith('building_'),
            'description': 'Building models'
        },
        'character': {
            'pattern': lambda f: f.startswith('char_') or f.startswith('character_'),
            'description': 'Character/unit models'
        },
        'creature': {
            'pattern': lambda f: f.startswith('creature_') or f.startswith('monster_'),
            'description': 'Creature/monster models'
        },
        'effect': {
            'pattern': lambda f: f.startswith('effect_') or f.startswith('fx_'),
            'description': 'Visual effect models'
        },
        'environment': {
            'pattern': lambda f: f.startswith('env_') or f.startswith('terrain_'),
            'description': 'Environmental models'
        },
        'object': {
            'pattern': lambda f: f.startswith('object_') or f.startswith('prop_'),
            'description': 'Object/prop models'
        },
        'spell': {
            'pattern': lambda f: f.startswith('spell_'),
            'description': 'Spell effect models'
        },
        'weapon': {
            'pattern': lambda f: f.startswith('weapon_') or f.startswith('armor_'),
            'description': 'Weapon and armor models'
        },
    }

    file_counts = defaultdict(int)
    uncategorized = 0

    for file in os.listdir(models_dir):
        source = models_dir / file
        if not source.is_file():
            continue

        # Find matching category
        categorized = False
        for cat_name, cat_info in categories.items():
            if cat_info['pattern'](file):
                dest_dir = models_dir / cat_name
                dest_dir.mkdir(exist_ok=True)

                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"  Error moving {file}: {e}")

        if not categorized:
            uncategorized += 1

    print("\nModel Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    if uncategorized > 0:
        print(f"  {'uncategorized':20s}: {uncategorized:5d} files - Remaining in root")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(file_counts.values()) + uncategorized:5d} files")


def organize_animations():
    """Organize animation files by naming patterns."""
    print("\n" + "=" * 70)
    print("Organizing Animation Files...")
    print("=" * 70)

    anims_dir = EXTRACTED_DIR / "Animations"
    if not anims_dir.exists():
        print(f"Animations directory not found: {anims_dir}")
        return

    # Animation categories
    categories = {
        'character': {
            'pattern': lambda f: f.startswith('char_') or f.startswith('character_'),
            'description': 'Character animations'
        },
        'creature': {
            'pattern': lambda f: f.startswith('creature_') or f.startswith('monster_'),
            'description': 'Creature animations'
        },
        'building': {
            'pattern': lambda f: f.startswith('building_'),
            'description': 'Building animations'
        },
        'effect': {
            'pattern': lambda f: f.startswith('effect_') or f.startswith('fx_'),
            'description': 'Effect animations'
        },
        'object': {
            'pattern': lambda f: f.startswith('object_') or f.startswith('prop_'),
            'description': 'Object animations'
        },
        'spell': {
            'pattern': lambda f: f.startswith('spell_'),
            'description': 'Spell animations'
        },
    }

    file_counts = defaultdict(int)
    uncategorized = 0

    for file in os.listdir(anims_dir):
        source = anims_dir / file
        if not source.is_file():
            continue

        categorized = False
        for cat_name, cat_info in categories.items():
            if cat_info['pattern'](file):
                dest_dir = anims_dir / cat_name
                dest_dir.mkdir(exist_ok=True)

                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"  Error moving {file}: {e}")

        if not categorized:
            uncategorized += 1

    print("\nAnimation Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    if uncategorized > 0:
        print(f"  {'uncategorized':20s}: {uncategorized:5d} files - Remaining in root")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(file_counts.values()) + uncategorized:5d} files")


def organize_scripts():
    """Organize Lua script files by naming patterns."""
    print("\n" + "=" * 70)
    print("Organizing Script Files...")
    print("=" * 70)

    scripts_dir = EXTRACTED_DIR / "Scripts"
    if not scripts_dir.exists():
        print(f"Scripts directory not found: {scripts_dir}")
        return

    # Script categories
    categories = {
        'ai': {
            'pattern': lambda f: f.startswith('ai') or 'ai' in f.lower() and f.endswith('.lua'),
            'description': 'AI behavior scripts'
        },
        'camera': {
            'pattern': lambda f: f.startswith('camera') or f.startswith('benchcam'),
            'description': 'Camera control scripts'
        },
        'quest': {
            'pattern': lambda f: 'quest' in f.lower() or 'mission' in f.lower(),
            'description': 'Quest and mission scripts'
        },
        'spell': {
            'pattern': lambda f: f.startswith('spell') or f == 'drwspells.lua',
            'description': 'Spell definition scripts'
        },
        'sound': {
            'pattern': lambda f: f.startswith('snd') or 'sound' in f.lower(),
            'description': 'Sound system scripts'
        },
        'ui': {
            'pattern': lambda f: f.startswith('ui_') or f.startswith('menu'),
            'description': 'UI scripts'
        },
        'map': {
            'pattern': lambda f: f.startswith('map_') or 'spline' in f.lower(),
            'description': 'Map and cutscene scripts'
        },
        'tutorial': {
            'pattern': lambda f: 'tutorial' in f.lower(),
            'description': 'Tutorial scripts'
        },
        'dialogue': {
            'pattern': lambda f: 'dialogue' in f.lower() or 'dialog' in f.lower(),
            'description': 'Dialogue scripts'
        },
        'cutscene': {
            'pattern': lambda f: 'cutscene' in f.lower() or 'cs_' in f.lower(),
            'description': 'Cutscene scripts'
        },
    }

    file_counts = defaultdict(int)
    uncategorized = 0

    for file in os.listdir(scripts_dir):
        source = scripts_dir / file
        if not source.is_file():
            continue

        categorized = False
        for cat_name, cat_info in categories.items():
            if cat_info['pattern'](file):
                dest_dir = scripts_dir / cat_name
                dest_dir.mkdir(exist_ok=True)

                dest = dest_dir / file
                try:
                    shutil.move(str(source), str(dest))
                    file_counts[cat_name] += 1
                    categorized = True
                    break
                except Exception as e:
                    print(f"  Error moving {file}: {e}")

        if not categorized:
            uncategorized += 1

    print("\nScript Organization Summary:")
    print("-" * 70)
    for cat in sorted(file_counts.keys()):
        count = file_counts[cat]
        desc = categories[cat]['description']
        print(f"  {cat:20s}: {count:5d} files - {desc}")
    if uncategorized > 0:
        print(f"  {'uncategorized':20s}: {uncategorized:5d} files - Remaining in root")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(file_counts.values()) + uncategorized:5d} files")


def organize_other():
    """Organize Other category files by extension."""
    print("\n" + "=" * 70)
    print("Organizing Other Files...")
    print("=" * 70)

    other_dir = EXTRACTED_DIR / "Other"
    if not other_dir.exists():
        print(f"Other directory not found: {other_dir}")
        return

    # Organize by file extension
    extension_counts = defaultdict(int)

    for file in os.listdir(other_dir):
        source = other_dir / file
        if not source.is_file():
            continue

        ext = Path(file).suffix.lower()
        if not ext:
            ext = 'no_extension'
        else:
            ext = ext[1:]  # Remove the dot

        # Create extension folder
        dest_dir = other_dir / ext
        dest_dir.mkdir(exist_ok=True)

        dest = dest_dir / file
        try:
            shutil.move(str(source), str(dest))
            extension_counts[ext] += 1
        except Exception as e:
            print(f"  Error moving {file}: {e}")

    print("\nOther Files Organization by Extension:")
    print("-" * 70)
    for ext in sorted(extension_counts.keys()):
        count = extension_counts[ext]
        print(f"  {ext:20s}: {count:5d} files")
    print("-" * 70)
    print(f"  {'TOTAL':20s}: {sum(extension_counts.values()):5d} files")


def main():
    """Main execution."""
    print("=" * 70)
    print(" " * 10 + "Comprehensive File Organization")
    print(" " * 5 + "Organizing all extracted assets into subcategories")
    print("=" * 70)

    # Organize each category
    organize_uncategorized_audio()
    organize_textures()
    organize_models()
    organize_animations()
    organize_scripts()
    organize_other()

    print("\n" + "=" * 70)
    print("Organization Complete!")
    print("=" * 70)
    print("\nAll files have been organized into detailed subcategories.")
    print(f"Location: {EXTRACTED_DIR}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
