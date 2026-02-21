import re

# Read the MapEditorForm.cs file
with open(r"H:\SpellSmut\ModdingTools\spellforce_data_editor\SpellforceDataEditor\special forms\MapEditorForm.cs", 'r') as f:
    content = f.read()

# Find existing radio button event handlers
radio_event_pattern = r'private void \w+_CheckedChanged\(object sender, EventArgs e\)'
radio_events = re.findall(radio_event_pattern, content)

print("Found radio button event handlers:")
for event in radio_events[:10]:  # Show first 10
    print(f"  {event}")

# Also look for any existing click handlers
click_pattern = r'private void \w+_Click\(object sender, EventArgs e\)'
click_events = re.findall(click_pattern, content)

print(f"\nFound click event handlers: {len(click_events)}")
for event in click_events[:10]:  # Show first 10
    print(f"  {event}")

# Find the end of the class to know where to add new methods
class_end = content.rfind('    }')
if class_end != -1:
    # Find the actual class end (there might be nested classes)
    lines = content[:class_end].split('\n')
    method_end = class_end
    for i in range(len(lines)-1, -1, -1):
        if 'private void' in lines[i] or 'public void' in lines[i]:
            # Find the end of this method
            method_start = content.find(lines[i], method_end - 1000, method_end)
            if method_start != -1:
                method_lines = content[method_start:class_end].split('\n')
                brace_count = 0
                for j, line in enumerate(method_lines):
                    if '{' in line:
                        brace_count += line.count('{')
                    if '}' in line:
                        brace_count -= line.count('}')
                    if brace_count <= 0 and j > 0:
                        method_end = method_start + content[method_start:class_end].find('\n'.join(method_lines[:j+1]))
                        break
            break
    
    print(f"\nFound end of last method around line {content[:method_end].count(chr(10))}")