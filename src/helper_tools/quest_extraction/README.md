# Quest Extraction Tools

This directory contains tools specifically for extracting and analyzing quest data from SpellForce game files.

## Tools

- **extract_cff_quest_data.py** - Extract quest data from CFF files
- **extract_complete_quest_data.py** - Extract all quest data comprehensively  
- **extract_map_and_descriptions.py** - Extract quest maps and descriptions
- **extract_quest_379_dialogues.py** - Extract dialogues for specific quest (ID: 379)
- **extract_quest_descriptions.py** - Extract quest descriptions
- **extract_quest_dialogues.py** - Extract quest dialogues

## Usage

Run from project root using UV:

```bash
uv run python src/helper_tools/quest_extraction/extract_complete_quest_data.py
```

## Output

Quest extraction tools typically output:
- JSON files with quest data (placed in `src/TirganachReloaded/data/`)
- Markdown documentation files (placed in `docs/Extraction/`)
- Analysis reports for debugging

## Related Documentation

See `docs/Extraction/` for:
- AMRA_LEA_COMPLETE_QUEST_DOCUMENTATION.md
- QUEST_EXTRACTION_COMPLETE.md
- amra_and_lea_quest_tree_complete.md
- amra_and_lea_complete_quest_data.md