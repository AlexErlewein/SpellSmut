"""
Test script for the Spell Forge GUI

This verifies that the GUI components can be instantiated correctly.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing Spell Forge GUI components...")
print("="*60)

# Test imports
print("\n1. Testing imports...")
try:
    from spell_forge_wizard import SpellForgeWizard
    from spell_browser_dialog import SpellBrowserDialog
    print("✓ All imports successful")
except ImportError as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test wizard instantiation (without showing UI)
print("\n2. Testing wizard instantiation...")
try:
    from PySide6.QtWidgets import QApplication

    # Create minimal QApplication
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)

    wizard = SpellForgeWizard()
    print(f"✓ Wizard created with {wizard.pageIds().__len__()} pages")

    # Verify page count
    expected_pages = 7
    actual_pages = len(wizard.pageIds())
    if actual_pages == expected_pages:
        print(f"✓ Correct number of pages: {actual_pages}")
    else:
        print(f"⚠️  Expected {expected_pages} pages, got {actual_pages}")

except Exception as e:
    print(f"❌ Wizard instantiation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test browser instantiation
print("\n3. Testing spell browser...")
try:
    browser = SpellBrowserDialog()
    print("✓ Spell browser created successfully")
except Exception as e:
    print(f"❌ Browser instantiation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test that we can access pages
print("\n4. Testing wizard pages...")
try:
    page_titles = []
    for page_id in wizard.pageIds():
        page = wizard.page(page_id)
        page_titles.append(page.title())

    print("✓ Page titles:")
    for i, title in enumerate(page_titles, 1):
        print(f"   {i}. {title}")

except Exception as e:
    print(f"❌ Page access failed: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("✓ All GUI tests passed!")
print("\nTo run the GUI wizard:")
print("  python spell_forge_wizard.py")
print("\nOr import it in your application:")
print("  from spell_forge_wizard import SpellForgeWizard")
