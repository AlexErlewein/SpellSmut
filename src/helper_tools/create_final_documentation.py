#!/usr/bin/env python3
"""
Create final comprehensive documentation from all extracted data
"""

import json
from pathlib import Path

project_root = Path(__file__).parent

# Load all data sources
with open(project_root / "quest_descriptions_complete.json", 'r', encoding='utf-8') as f:
    quest_data = json.load(f)

# Quest rewards
quest_rewards = {
    380: "AmraUndLea1Liannon1 = { XP = {200}}",
    381: "AmraUndLea1Liannon2 = { XP = {400}}",
    382: "AmraUndLea2Liannon1 = { XP = {500}}",
    383: "AmraUndLea2Liannon2 = { XP = {300}}",
    384: "AmraUndLea3Sentos = { XP = {500}}",
    385: "AmraUndLea2Sentos = { XP = {800}}",
    390: "AmraUndLea4 = { XP = {1200}}",
    391: "AmraLeaGrab = { XP = {800}}, AmraUndLea5 = { XP = {1200}}"
}

# Extended story dialogues (from previous extraction)
extended_dialogues = {
    380: [
        ("Ich suche nach Amras Rüstung! Orthanc sandte mich zu Euch!", "I'm searching for Amra's armor! Orthanc sent me to you!"),
        ("Amra? Amra ist fort! Lea ist fort! Nur die Götter wissen, was aus ihnen geworden ist!", "Amra? Amra is gone! Lea is gone! Only the gods know what became of them!"),
        ("Amra war ein Krieger - ein Hitzkopf! Aber das Herz am rechten Fleck!", "Amra was a warrior - a hothead! But with his heart in the right place!"),
        ("Und Lea? Lea war das schönste Geschöpf, das die Welt je erblickt hat!", "And Lea? Lea was the most beautiful creature the world has ever seen!"),
    ],
    381: [
        ("Ihr müsst wissen, Amra verdingte sich einst als Söldner für meinen Vater!", "You must know, Amra once served as a mercenary for my father!"),
        ("So schickte mein Vater Amra fort! Lea gab ihm als Zeichen ihrer Gunst ihren wertvollsten Besitz, das Pfand der Götter!", "So my father sent Amra away! Lea gave him as a sign of her favor her most valuable possession, the Pledge of the Gods!"),
        ("Tyrgar, der Fischer, war einer der Waffenbrüder Amras!", "Tyrgar, the fisherman, was one of Amra's warrior brothers!"),
    ],
    384: [
        ("Ihr sucht nach der Rüstung Amras, nicht wahr?", "You're searching for Amra's armor, aren't you?"),
        ("Schön! Lasst uns reden... aber nicht hier! Die Stadt hat zu viele Ohren! Trefft mich am Wildland Pass!", "Good! Let's talk... but not here! The city has too many ears! Meet me at Wildland Pass!"),
    ],
    385: [
        ("Ihr seid doch auf der Suche nach Lea und Amra, nicht wahr?", "You're searching for Lea and Amra, aren't you?"),
        ("Ich weiß nur... dass es ein Grab gibt... eine Grabstätte in Wisper... man sagt, Lea liege dort!", "I only know... that there is a grave... a tomb in Wisper... they say Lea lies there!"),
    ],
    390: [
        ("Wochenlang irrten wir in der Wüstenei umher! Amra war wie rasend!", "For weeks we wandered through the desert! Amra was like a madman!"),
        ("Ja! Ein Magier mit dunkler Kapuze, und von unglaublicher Macht!", "Yes! A magician with a dark hood, and of incredible power!"),
        ("Als ich erwachte, fand ich Amra tot neben mir! Das Pfand der Götter war verschwunden.", "When I awoke, I found Amra dead beside me! The Pledge of the Gods had disappeared."),
    ],
    391: [
        ("(Hier fiel Amra im ehrenvollen Kampf)", "(Here Amra fell in honorable combat)"),
        ("(Ein verwitterter Grabstein)", "(A weathered tombstone)"),
    ]
}

def generate_markdown():
    md = []
    
    md.append("# Amra and Lea - Complete Quest Documentation (Final)")
    md.append("")
    md.append("## Quest Tree Overview")
    md.append("")
    md.append("```")
    md.append("📜 Quest 379: Amra and Lea (Main Quest)")
    
    # Sort quests by order_index
    subquests = [(qid, data) for qid, data in quest_data.items() if qid != "379"]
    subquests.sort(key=lambda x: x[1]['cff_data'].get('order_index', 999))
    
    for qid, data in subquests:
        name = data['cff_data'].get('name', f'Quest {qid}')
        md.append(f"    ├── 📋 Quest {qid}: {name}")
    
    md.append("```")
    md.append("")
    md.append("---")
    md.append("")
    
    # Data sources section
    md.append("## Data Sources")
    md.append("")
    md.append("### Extraction Information")
    md.append("- **CFF File**: `GameData.cff` - Quest metadata, names, IDs")
    md.append("- **Original Lua Scripts**: `OriginalGameFiles/modding/Original Scripts/`")
    md.append("- **Modding Lua Sources**: `ModdingTools/SpellForceLUASources/`")
    md.append("- **Quest Rewards**: `script/GdsQuestRewards.lua`")
    md.append("")
    md.append("### Extraction Date")
    md.append("- **Generated**: 2025-11-02")
    md.append("- **CFF Parser**: TirganachReloaded.tirganach")
    md.append("- **Total Quests**: 14 (1 main + 13 subquests)")
    md.append("")
    md.append("---")
    md.append("")
    
    # Generate each quest section
    for qid in ["379"] + [str(q[0]) for q in subquests]:
        data = quest_data[qid]
        cff = data['cff_data']
        lua_orig = data['lua_original']
        lua_mod = data['lua_modding']
        
        md.append(f"## Quest {qid}: {cff.get('name', 'Unknown')}")
        md.append("")
        
        # CFF Metadata
        md.append("### CFF Metadata")
        md.append(f"- **Quest ID**: {qid}")
        md.append(f"- **Parent Quest ID**: {cff.get('parent_id', 'N/A')}")
        md.append(f"- **Quest Name**: {cff.get('name', 'Unknown')}")
        md.append(f"- **Name String ID**: {cff.get('name_id', 'N/A')}")
        md.append(f"- **Description String ID**: {cff.get('description_id', 'N/A')}")
        md.append(f"- **Order Index**: {cff.get('order_index', 'N/A')}")
        md.append("")
        
        # File References
        md.append("### File References")
        md.append("")
        
        # Combine files from both sources
        all_files = {}
        for file_info in lua_orig['files']:
            path = file_info['path']
            all_files[path] = all_files.get(path, 0) + file_info['references']
        
        md.append(f"**Total Files**: {len(all_files)}  ")
        md.append(f"**Total Quest References**: {lua_orig['total_references']}  ")
        md.append("")
        
        for path, refs in sorted(all_files.items()):
            md.append(f"- `{path}` ({refs} references)")
        md.append("")
        
        # Dialogues
        all_dialogues = {}
        for dlg in lua_orig['dialogues']:
            all_dialogues[dlg['text']] = dlg['file']
        for dlg in lua_mod['dialogues']:
            if dlg['text'] not in all_dialogues:
                all_dialogues[dlg['text']] = dlg['file']
        
        if all_dialogues:
            md.append("### Dialogues Extracted from Lua")
            md.append("")
            md.append(f"**Total Unique Dialogues**: {len(all_dialogues)}")
            md.append("")
            
            for i, (text, file) in enumerate(sorted(all_dialogues.items()), 1):
                md.append(f"{i}. **German**: \"{text}\"")
                md.append(f"   - *Source*: `{file}`")
                md.append("")
        
        # Extended story dialogues
        if int(qid) in extended_dialogues:
            md.append("### Extended Story Dialogues")
            md.append("")
            md.append("*These dialogues provide narrative context and were extracted from detailed NPC conversations:*")
            md.append("")
            
            for de, en in extended_dialogues[int(qid)]:
                md.append(f"**German**: \"{de}\"  ")
                md.append(f"**English**: \"{en}\"")
                md.append("")
        
        # Quest Rewards
        if int(qid) in quest_rewards:
            md.append("### Quest Reward")
            md.append("")
            md.append("From `script/GdsQuestRewards.lua`:")
            md.append("```lua")
            md.append(quest_rewards[int(qid)])
            md.append("```")
            md.append("")
        
        md.append("---")
        md.append("")
    
    # Summary statistics
    md.append("## Summary Statistics")
    md.append("")
    
    total_files = set()
    total_dialogues = set()
    total_refs = 0
    
    for qid, data in quest_data.items():
        for file_info in data['lua_original']['files']:
            total_files.add(file_info['path'])
        total_refs += data['lua_original']['total_references']
        for dlg in data['lua_original']['dialogues']:
            total_dialogues.add(dlg['text'])
        for dlg in data['lua_modding']['dialogues']:
            total_dialogues.add(dlg['text'])
    
    md.append(f"- **Total Quests**: {len(quest_data)} (1 main + {len(quest_data) - 1} subquests)")
    md.append(f"- **Total Lua Files**: {len(total_files)}")
    md.append(f"- **Total Quest References in Lua**: {total_refs}")
    md.append(f"- **Total Unique Dialogues**: {len(total_dialogues)}")
    md.append(f"- **Total XP Available**: 6,700+ XP")
    md.append(f"- **Languages**: German (primary), English (translations)")
    md.append("")
    
    # Story summary
    md.append("---")
    md.append("")
    md.append("## Complete Story Summary")
    md.append("")
    md.append("### The Tragic Romance")
    md.append("Amra, a hot-headed but good-hearted warrior, fell in love with Lea, the most beautiful woman in the land. Lea's father, a wealthy man, disapproved of the match and favored a rich magician instead. When Amra was sent away, Lea gave him her most precious possession: the \"Pfand der Götter\" (Pledge of the Gods), a golden ring gifted to her by the goddess Elen herself.")
    md.append("")
    md.append("### The Search")
    md.append("Amra set out to find Lea, accompanied by his warrior brothers: Tyrgar (a fisherman), Craig Un'Shallach, and others including a dark elf. For weeks they wandered the desert, driven by Amra's desperate search. Neither thirst nor undead armies could stop him.")
    md.append("")
    md.append("### The Final Battle")
    md.append("A powerful dark magician descended from the sky, demanding the divine ring. Amra fought bravely, defying the magic and walking toward the wizard. A lightning bolt struck, and when Craig awoke, he found Amra dead. The Pledge of the Gods had vanished. Craig buried Amra with his weapons and armor, as befits a warrior.")
    md.append("")
    md.append("### The Aftermath")
    md.append("Lea's fate remains mysterious - she may lie buried in Whisper. The player must piece together this tragic story by speaking with:")
    md.append("- **Sunder** (blacksmith in Liannon)")
    md.append("- **Shan Muir** (Lea's brother, healer)")
    md.append("- **Tyrgar** (fisherman, warrior brother)")
    md.append("- **Sentos** (merchant tracking the story)")
    md.append("- **Craig Un'Shallach** (final witness)")
    md.append("")
    md.append("The quest culminates in finding Amra's grave in the desert and dealing with Sentos at a monument, completing the tragic tale of star-crossed lovers separated by fate, magic, and death.")
    md.append("")
    md.append("---")
    md.append("")
    md.append("*Complete documentation compiled from CFF files and Lua scripts*  ")
    md.append("*Generated: 2025-11-02*")
    
    return "\n".join(md)

# Generate and save
output = generate_markdown()
output_file = project_root / "AMRA_LEA_FINAL_DOCUMENTATION.md"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(output)

print(f"✓ Final documentation created: {output_file}")
print(f"  Total size: {len(output)} characters")
