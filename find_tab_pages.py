import re

def find_tab_pages():
    """Find existing tab pages in the Designer file"""
    
    with open(r"H:\SpellSmut\ModdingTools\spellforce_data_editor\SpellforceDataEditor\special forms\MapEditorForm.Designer.cs", 'r') as f:
        content = f.read()
    
    # Find tab page declarations
    tab_pages = re.findall(r'this\.(\w+)\s*=\s*new System\.Windows\.Forms\.TabPage\(\);', content)
    
    print("Tab page declarations:")
    for page in tab_pages:
        print(f"  {page}")
    
    # Find their names
    name_assignments = re.findall(r'this\.' + r'(\w+)\.Name\s*=\s*"([^"]+)"', content)
    print("\nTab page names:")
    for page, name in name_assignments:
        if 'Tab' in page:
            print(f"  {page} = {name}")
    
    return tab_pages

if __name__ == '__main__':
    find_tab_pages()