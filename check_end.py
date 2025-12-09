with open(r"H:\SpellSmut\ModdingTools\spellforce_data_editor\SpellforceDataEditor\special forms\MapEditorForm.cs", 'r') as f:
    lines = f.readlines()

print("Last 10 lines:")
for i, line in enumerate(lines[-10:], len(lines)-9):
    print(f"{i:4d}: {repr(line)}")