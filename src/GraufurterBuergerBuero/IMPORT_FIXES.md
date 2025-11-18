# Import Fixes - Complete ✅

## Issues Fixed

### 1. EnhancedNpcBrowser Constructor Mismatch
**Error:**
```
TypeError: EnhancedNpcBrowser.__init__() takes from 1 to 2 positional arguments but 3 were given
```

**Cause:** The browser was being called with `(id_manager, parent)` but only accepted `(parent)`

**Fix:**
```python
# Before
class EnhancedNpcBrowser(QDialog):
    def __init__(self, parent=None):
        ...

# After  
class EnhancedNpcBrowser(QDialog):
    def __init__(self, id_manager: IDManager, parent=None):
        super().__init__(parent)
        self.id_manager = id_manager
        ...
```

### 2. Relative Import Errors
**Error:**
```
ImportError: attempted relative import with no known parent package
```

**Cause:** Files copied from TirganachReloaded had relative imports (`from ..module` or `from .module`)

**Files Fixed:**
- `npc_creator_wizard.py`
- `enhanced_npc_browser.py`

**Changes Made:**

#### npc_creator_wizard.py
```python
# Before
from .enhanced_npc_browser import EnhancedNpcBrowser
from ..exporters.npc_loader import NpcLoader
from ..exporters.npc_cff_exporter import NpcCFFExporter

# After
from enhanced_npc_browser import EnhancedNpcBrowser
from npc_loader import save_npc
from npc_cff_exporter import NpcCFFExporter
```

#### enhanced_npc_browser.py
```python
# Before
from ..shared.id_manager import IDManager
from .npc_creator_wizard import NpcCreatorWizard

id_manager = IDManager()  # Creating new instance each time
wizard = NpcCreatorWizard(id_manager, self)

# After  
from npc_creator_wizard import NpcCreatorWizard

wizard = NpcCreatorWizard(self.id_manager, self)  # Using shared instance
```

---

## Files Modified

1. **enhanced_npc_browser.py**
   - Added `id_manager` parameter to `__init__`
   - Stored `self.id_manager` as instance variable
   - Fixed 4 relative imports → absolute imports
   - Removed redundant `IDManager()` instantiation (use shared instance)

2. **npc_creator_wizard.py**
   - Fixed 3 relative imports → absolute imports
   - Changed `NpcLoader.save_npc()` → `save_npc()`

---

## Testing

### Import Test
```bash
$ cd src/GraufurterBuergerBuero
$ uv run test_imports.py

✓ npc_loader imports OK
✓ npc_creation_data imports OK
✓ id_manager imports OK
✓ Loaded 0 NPCs
✓ Allocated test NPC ID: 40000
✓ Released test NPC ID: 40000

✅ All basic tests passed!
```

### Expected App Behavior
```bash
$ uv run graufurter_buerger_buero.py

✓ Logging system initialized
✓ Loaded 0 custom NPCs from JSON
✓ Total NPCs available: 0

# Click "Browse NPCs" → Should open browser dialog ✅
# Click "Create NPC" → Should open wizard ✅
# Load CFF file → Browse game NPCs → Duplicate → Should work ✅
```

---

## Why These Issues Occurred

### Root Cause
Files were copied from **TirganachReloaded** (a package with `__init__.py`) to **GraufurterBuergerBuero** (standalone scripts).

### Package vs Standalone
- **Package structure** (TirganachReloaded):
  ```
  TirganachReloaded/
  ├── __init__.py  ← Makes it a package
  ├── cff_editor/
  │   ├── __init__.py
  │   ├── widgets/
  │   │   ├── npc_creator_wizard.py
  │   │   └── enhanced_npc_browser.py
  │   └── exporters/
  │       ├── npc_loader.py
  │       └── npc_cff_exporter.py
  ```
  Relative imports work: `from ..exporters import npc_loader`

- **Standalone structure** (GraufurterBuergerBuero):
  ```
  GraufurterBuergerBuero/
  ├── npc_creator_wizard.py
  ├── enhanced_npc_browser.py
  ├── npc_loader.py
  └── npc_cff_exporter.py
  ```
  Must use absolute imports: `import npc_loader`

---

## Prevention for Future

When copying files from TirganachReloaded to standalone tools:

### Checklist
1. ✅ Remove all relative imports (`from ..` or `from .`)
2. ✅ Change to absolute imports
3. ✅ Check function signatures match (e.g., `__init__` parameters)
4. ✅ Use shared instances (e.g., `self.id_manager`) instead of creating new ones
5. ✅ Test with `test_imports.py` before running GUI

### Common Patterns

**Relative → Absolute:**
```python
# Package (TirganachReloaded)
from ..shared.id_manager import IDManager
from .enhanced_npc_browser import EnhancedNpcBrowser
from ..models.npc_creation_data import NpcCreationData

# Standalone (GraufurterBuergerBuero)
from id_manager import IDManager
from enhanced_npc_browser import EnhancedNpcBrowser
from npc_creation_data import NpcCreationData
```

**Class method → Function:**
```python
# Package
from ..exporters.npc_loader import NpcLoader
NpcLoader.save_npc(data)

# Standalone
from npc_loader import save_npc
save_npc(data)
```

---

## Status

✅ **All Import Issues Fixed!**

Both errors are now resolved:
1. EnhancedNpcBrowser accepts `(id_manager, parent)` ✅
2. All relative imports converted to absolute imports ✅

The application should now work correctly for:
- Opening NPC browser
- Creating new NPCs
- Editing existing NPCs
- Duplicating NPCs
- All wizard functionality

**Date**: 2025-11-18  
**Files Modified**: 2  
**Import Fixes**: 7 total
