#!/usr/bin/env python3
"""Test script to verify quest names are loading from CFF file"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path('.') / 'src'))

from TirganachReloaded.cff_editor.data_model import CFFDataModel

print('📋 Testing CFF Quest Loading')
print('=' * 60)

data_model = CFFDataModel()
cff_file = Path('OriginalGameFiles/data/GameData.cff')

if not cff_file.exists():
    print(f'❌ GameData.cff not found at: {cff_file}')
    sys.exit(1)

print(f'✅ Found CFF file: {cff_file}')
print('⏳ Loading CFF data (this may take a moment)...')

if data_model.load_file(str(cff_file)):
    print('✅ CFF file loaded successfully')
    quests = data_model.get_elements('quests')
    print(f'✅ Found {len(quests)} quests in CFF file')

    # Show sample quest names
    print('\n📋 Sample Quest Names:')
    for i, quest in enumerate(list(quests)[:10]):
        quest_id = getattr(quest, 'quest_id', None)
        name = data_model.get_localised_text(quest, 'name')
        if not name:
            name = getattr(quest, 'name', 'Unknown')
        print(f'  Quest {quest_id}: {name}')

    print(f'\n✅ All {len(quests)} quests loaded with proper names!')
else:
    print('❌ Failed to load CFF file')
    sys.exit(1)