import os

# Count lines in MapEditorForm.cs
with open(r"H:\SpellSmut\ModdingTools\spellforce_data_editor\SpellforceDataEditor\special forms\MapEditorForm.cs", 'r') as f:
    lines = f.readlines()
    print(f"MapEditorForm.cs has {len(lines)} lines")