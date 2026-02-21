import re

def find_tab_and_update_methods():
    """Find the correct tab control name and how UI updates work"""
    
    with open(r"H:\SpellSmut\ModdingTools\spellforce_data_editor\SpellforceDataEditor\special forms\MapEditorForm.cs", 'r') as f:
        content = f.read()
    
    # Look for any tab control initialization
    tab_control_init = re.findall(r'this\.(\w+)\s*=\s*new System\.Windows\.Forms\.TabControl\(\);', content)
    print("Tab controls found:")
    for tab in tab_control_init:
        print(f"  {tab}")
    
    # Look for tabPage initialization
    tab_page_init = re.findall(r'this\.(\w+)\s*=\s*new System\.Windows\.Forms\.TabPage\(\);', content)
    print("\nTab pages found:")
    for page in tab_page_init:
        if 'Tab' in page and 'Page' in page:
            print(f"  {page}")
    
    # Look for existing radio button CheckedChanged handlers to see pattern
    checked_handlers = re.findall(r'private void (\w+)_CheckedChanged\(object sender, EventArgs e\)', content)
    print(f"\nRadio button CheckedChanged handlers found: {len(checked_handlers)}")
    for handler in checked_handlers[:10]:
        print(f"  {handler}")
    
    # Look for any methods that switch tabs
    tab_methods = re.findall(r'private void (\w+)\(.*?\).*?SelectedTab.*?=.*?(\w+)', content, re.DOTALL)
    print(f"\nTab switching methods: {len(tab_methods)}")
    for method in tab_methods:
        print(f"  {method[0]} -> {method[1]}")
    
    return content

if __name__ == '__main__':
    find_tab_and_update_methods()