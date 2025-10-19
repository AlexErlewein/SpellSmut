# SpellForce GameData.cff Editor - Planning Document

## Requirements Analysis

### Core Functionality

1. **File Management**
   - Open CFF file (file picker)
   - Display loading progress (176k+ entries)
   - Save modifications back to CFF
   - Export to XML (optional)

2. **Category Browser**
   - List all 43 tables (spells, items, creatures, etc.)
   - Show entry count per category
   - Quick search/filter categories

3. **Element List View**
   - Display all elements in selected category
   - Sortable columns (ID, name, type, etc.)
   - Search/filter elements
   - Pagination for large tables (176k localization entries!)

4. **Element Detail Editor**
   - Display all properties of selected element
   - Editable fields with type validation
   - Enum dropdowns (ItemType, School, Race, etc.)
   - Save/Cancel changes
   - Highlight modified fields

5. **Additional Features (Nice to Have)**
   - Add new elements
   - Clone existing elements
   - Delete elements (with warning)
   - Compare two CFF files
   - Undo/Redo functionality

---

## Option 1: GUI Application

### Framework Comparison

#### A. **Tkinter** (Built-in Python)

**Pros:**
- ✅ No installation needed (comes with Python)
- ✅ Cross-platform (Windows, Mac, Linux)
- ✅ Lightweight and fast
- ✅ Good for simple layouts
- ✅ Mature and stable

**Cons:**
- ❌ Looks dated by default
- ❌ Requires extra work for modern look
- ❌ Limited built-in widgets
- ❌ No native dark mode support

**Modern Tkinter Libraries:**
- **CustomTkinter** - Modern, dark mode, rounded corners
- **ttkbootstrap** - Bootstrap-inspired themes

**Rating:** ⭐⭐⭐ (3/5) - Functional but requires styling work

---

#### B. **PyQt6/PySide6** (Qt Framework)

**Pros:**
- ✅ Professional, native look
- ✅ Extensive widget library (tables, trees, etc.)
- ✅ Built-in dark mode
- ✅ Excellent table/list performance
- ✅ Rich documentation
- ✅ Designer tool (Qt Designer) for visual layout
- ✅ Very powerful and flexible

**Cons:**
- ❌ Larger dependency (~50MB)
- ❌ LGPL license (PySide6) or GPL/Commercial (PyQt6)
- ❌ Steeper learning curve
- ❌ Can be overkill for simple apps

**Best For:** Complex applications with lots of data

**Rating:** ⭐⭐⭐⭐⭐ (5/5) - Industry standard, excellent for data editing

---

#### C. **wxPython** (wxWidgets)

**Pros:**
- ✅ Native look on each platform
- ✅ Good widget selection
- ✅ Mature and stable
- ✅ LGPL license (more permissive)

**Cons:**
- ❌ Less modern than Qt
- ❌ Smaller community than Qt
- ❌ Documentation not as comprehensive

**Rating:** ⭐⭐⭐⭐ (4/5) - Good alternative to Qt

---

#### D. **Kivy** (Modern, Touch-focused)

**Pros:**
- ✅ Very modern and animated
- ✅ Touch-friendly
- ✅ Custom styling with KV language
- ✅ Cross-platform (even mobile)

**Cons:**
- ❌ Non-native look (custom UI)
- ❌ Not ideal for data-heavy apps
- ❌ Overkill for desktop-only
- ❌ Performance issues with large tables

**Rating:** ⭐⭐ (2/5) - Too focused on mobile/touch

---

#### E. **Dear PyGui** (Immediate Mode GUI)

**Pros:**
- ✅ Very modern look
- ✅ GPU-accelerated (fast rendering)
- ✅ Great for data visualization
- ✅ Built-in tables, plots, themes
- ✅ Easy to get started

**Cons:**
- ❌ Relatively new (less mature)
- ❌ Smaller community
- ❌ Different paradigm (immediate mode)
- ❌ Limited documentation

**Rating:** ⭐⭐⭐⭐ (4/5) - Modern and fast, but newer

---

#### F. **Flet** (Flutter-based)

**Pros:**
- ✅ Very modern Material Design UI
- ✅ Beautiful out of the box
- ✅ Easy to learn
- ✅ Cross-platform (desktop, web, mobile)
- ✅ Reactive updates

**Cons:**
- ❌ Very new (2022+)
- ❌ Limited widget library
- ❌ Requires Flutter engine
- ❌ Not ideal for complex data tables

**Rating:** ⭐⭐⭐ (3/5) - Beautiful but too new

---

### GUI Recommendation: **PyQt6/PySide6**

**Why Qt?**
1. **Table Performance** - Handles 176k entries smoothly
2. **Built-in Widgets** - QTableView, QTreeView perfect for our needs
3. **Professional Look** - Native styling + dark mode
4. **Mature** - Battle-tested, stable, excellent docs
5. **Model/View Architecture** - Perfect for large datasets

**UI Layout:**

```
┌─────────────────────────────────────────────────────────┐
│  SpellForce CFF Editor                    [─][□][×]    │
├─────────────────────────────────────────────────────────┤
│  File  Edit  View  Tools  Help                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  📁 H:\SpellSmut\OriginalGameFiles\data\GameData.cff  │
│                                                         │
├──────────────┬──────────────────────┬───────────────────┤
│              │                      │                   │
│  Categories  │   Element List       │  Properties       │
│              │                      │                   │
│ ▼ Items      │ ID    Name      Type │  ┌─────────────┐ │
│   □ Spells   │ 531   Soulguard Ring │  │ item_id: 531│ │
│   □ Armor    │ 532   Ruby Ring  Ring │  │ name: Soul..│ │
│   □ Weapons  │ 537   Antique... Ring │  │             │ │
│   □ Creatures│ ...                   │  │ item_type:  │ │
│   [43 more]  │                      │  │ [EQUIPMENT▼]│ │
│              │ [Search: ____]       │  │             │ │
│              │                      │  │ health: 0   │ │
│              │ Showing 1-50 of 120  │  │ mana: 0     │ │
│              │ [<] [1][2][3] [>]    │  │ ...         │ │
│              │                      │  │             │ │
│              │                      │  │ [Save][Cncl]│ │
│              │                      │  └─────────────┘ │
└──────────────┴──────────────────────┴───────────────────┘
```

---

## Option 2: Terminal UI (TUI) Application

### Framework Comparison

#### A. **Rich** (Modern Python TUI)

**Pros:**
- ✅ Beautiful, modern styling
- ✅ Colors, tables, progress bars
- ✅ Great for output/display
- ✅ Easy to use

**Cons:**
- ❌ Limited interactivity
- ❌ Not designed for complex forms
- ❌ No built-in navigation widgets

**Rating:** ⭐⭐⭐ (3/5) - Great for display, not for editing

---

#### B. **Textual** (Modern TUI Framework)

**Pros:**
- ✅ Built on Rich (beautiful styling)
- ✅ Reactive, component-based
- ✅ Mouse support
- ✅ CSS-like styling
- ✅ Great performance
- ✅ Modern paradigm (like React)
- ✅ Active development

**Cons:**
- ❌ Relatively new (2021+)
- ❌ Smaller community
- ❌ Limited complex widgets (improving)

**Rating:** ⭐⭐⭐⭐⭐ (5/5) - Best modern TUI framework

---

#### C. **urwid** (Traditional TUI)

**Pros:**
- ✅ Mature and stable
- ✅ Good widget library
- ✅ Used in production apps

**Cons:**
- ❌ Older, less modern look
- ❌ More complex API
- ❌ Limited styling

**Rating:** ⭐⭐⭐ (3/5) - Functional but dated

---

#### D. **py_cui** (Simple TUI)

**Pros:**
- ✅ Simple and lightweight
- ✅ Easy to learn

**Cons:**
- ❌ Very basic
- ❌ Limited widgets
- ❌ Not actively developed

**Rating:** ⭐⭐ (2/5) - Too simple for our needs

---

### TUI Recommendation: **Textual**

**Why Textual?**
1. **Modern Look** - Beautiful, styled terminal UI
2. **Mouse Support** - Click on items, scroll, etc.
3. **Good Performance** - Handles large datasets
4. **Active Development** - Rapidly improving
5. **Component-based** - Easy to organize

**UI Layout:**

```
╭─────────────────────────────────────────────────────────────────╮
│ SpellForce CFF Editor                                      v1.0 │
├─────────────────────────────────────────────────────────────────┤
│ File: GameData.cff                         [Open] [Save] [Quit] │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ ╭─Categories───╮ ╭─Elements─────────────╮ ╭─Properties──────╮ │
│ │              │ │                      │ │                 │ │
│ │ ▶ Spells     │ │  ID    Name     Type │ │ item_id: 531   │ │
│ │ ▼ Items      │ │ ─────────────────── │ │ name: Soulguard│ │
│ │   ▶ Armor    │ │  531   Soulguard  R │ │                │ │
│ │   ▶ Weapons  │ │  532   Ruby Ring  R │ │ item_type:     │ │
│ │ ▶ Creatures  │ │  537   Antique... R │ │  EQUIPMENT     │ │
│ │ ▶ Buildings  │ │  ...                │ │                │ │
│ │ ...          │ │                     │ │ health: 0      │ │
│ │              │ │ Search: ________    │ │ mana: 0        │ │
│ │ [43 total]   │ │                     │ │ stamina: 0     │ │
│ │              │ │ Page 1/3            │ │ ...            │ │
│ │              │ │                     │ │                │ │
│ ╰──────────────╯ ╰─────────────────────╯ │ [Save] [Cancel]│ │
│                                           ╰─────────────────╯ │
│                                                                 │
│ Status: Ready                                    Memory: 97 MB │
╰─────────────────────────────────────────────────────────────────╯
```

---

## Comparison: GUI vs TUI

### Feature Comparison

| Feature | PyQt6 (GUI) | Textual (TUI) |
|---------|-------------|---------------|
| **Visual Appeal** | ⭐⭐⭐⭐⭐ Professional | ⭐⭐⭐⭐ Modern terminal |
| **Ease of Use** | ⭐⭐⭐⭐⭐ Mouse, native | ⭐⭐⭐⭐ Keyboard/mouse |
| **Performance** | ⭐⭐⭐⭐⭐ Excellent | ⭐⭐⭐⭐ Very good |
| **Large Tables** | ⭐⭐⭐⭐⭐ Perfect | ⭐⭐⭐⭐ Good |
| **Installation** | ⭐⭐⭐ pip install PyQt6 | ⭐⭐⭐⭐⭐ pip install textual |
| **Learning Curve** | ⭐⭐⭐ Moderate | ⭐⭐⭐⭐ Easier |
| **File Dialogs** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Custom |
| **Dropdowns** | ⭐⭐⭐⭐⭐ Native | ⭐⭐⭐ Custom |
| **Tables/Lists** | ⭐⭐⭐⭐⭐ QTableView | ⭐⭐⭐⭐ DataTable |
| **Portability** | ⭐⭐⭐⭐ Desktop only | ⭐⭐⭐⭐⭐ SSH friendly |
| **Deployment** | ⭐⭐⭐ ~50MB app | ⭐⭐⭐⭐⭐ Small script |
| **Maturity** | ⭐⭐⭐⭐⭐ 25+ years | ⭐⭐⭐ 3 years |

---

## Recommendation

### **Primary: PyQt6 GUI Application**

**Reasons:**
1. ✅ **Better UX** - Native file dialogs, dropdown menus, tooltips
2. ✅ **Table Performance** - QTableView handles 176k entries smoothly
3. ✅ **Professional** - Users expect GUI for data editing
4. ✅ **Validation** - Easier to implement complex form validation
5. ✅ **Rich Editing** - Better support for complex field types

**Best For:**
- Primary editor tool
- Users who want full features
- Complex data manipulation

---

### **Secondary: Textual TUI Application**

**Reasons:**
1. ✅ **Lightweight** - No GUI dependencies
2. ✅ **SSH-Friendly** - Work remotely via terminal
3. ✅ **Quick Launch** - Fast startup
4. ✅ **Scriptable** - Can be automated

**Best For:**
- Quick edits
- Remote server work
- Advanced users who prefer terminal
- Complement to GUI version

---

## Development Plan

### Phase 1: Core Functionality (GUI - PyQt6)

**Week 1: Foundation**
- [ ] File loading with progress bar
- [ ] Category tree view (43 tables)
- [ ] Basic table display

**Week 2: Navigation**
- [ ] Element list with search/filter
- [ ] Pagination for large tables
- [ ] Click to view details

**Week 3: Editing**
- [ ] Property display/edit panel
- [ ] Type validation (int, string, enum)
- [ ] Save modifications

**Week 4: Polish**
- [ ] Dark mode theme
- [ ] Error handling
- [ ] Save confirmations
- [ ] Recent files menu

### Phase 2: Advanced Features

**Week 5-6:**
- [ ] Add new elements
- [ ] Clone elements
- [ ] Delete elements
- [ ] Undo/redo

**Week 7:**
- [ ] Compare two CFF files
- [ ] Export to XML
- [ ] Import from XML (maybe)

### Phase 3: TUI Version (Textual)

**Week 8-9:**
- [ ] Port core functionality to Textual
- [ ] Simplified interface for terminal
- [ ] Basic editing capabilities

---

## Technical Architecture

### Data Layer
```python
class CFFDataModel:
    """Manages loaded CFF data"""
    def __init__(self, cff_path):
        self.game_data = GameData(cff_path)
        self.modified = False
        self.undo_stack = []

    def get_categories(self) -> List[str]:
        """Returns list of all tables"""

    def get_elements(self, category: str) -> List[Entity]:
        """Returns all elements in category"""

    def get_element_details(self, category: str, element_id: int) -> Dict:
        """Returns element properties"""

    def update_element(self, category: str, element_id: int, changes: Dict):
        """Applies changes to element"""

    def save(self, path: str):
        """Saves modified CFF"""
```

### GUI Layer (PyQt6)
```python
class MainWindow(QMainWindow):
    """Main application window"""
    - MenuBar (File, Edit, View, Tools, Help)
    - CategoryTreeWidget (left panel)
    - ElementTableWidget (center panel)
    - PropertyEditorWidget (right panel)
    - StatusBar (file info, memory usage)

class CategoryTreeWidget(QTreeWidget):
    """Displays 43 categories with counts"""

class ElementTableWidget(QTableView):
    """Displays elements in selected category"""
    - Sortable columns
    - Search box
    - Pagination

class PropertyEditorWidget(QWidget):
    """Displays/edits element properties"""
    - Auto-generates form fields
    - Type-specific widgets (spinbox, combobox, lineedit)
    - Save/Cancel buttons
```

### TUI Layer (Textual)
```python
class CFFEditorApp(App):
    """Main TUI application"""
    - CategoryList (left panel)
    - ElementDataTable (center panel)
    - PropertyEditor (right panel)

class CategoryList(ListView):
    """Category selection"""

class ElementDataTable(DataTable):
    """Element list with search"""

class PropertyEditor(Container):
    """Property editing form"""
```

---

## Dependency Analysis

### PyQt6 GUI
```bash
pip install PyQt6
# Size: ~50 MB
# License: GPL v3 (or commercial)
```

### PySide6 GUI (Alternative - LGPL)
```bash
pip install PySide6
# Size: ~50 MB
# License: LGPL (more permissive)
```

### Textual TUI
```bash
pip install textual
# Size: ~5 MB
# License: MIT
```

**Recommendation:** Use **PySide6** for GUI (better license than PyQt6)

---

## File Structure

```
H:\SpellSmut\src\TiganachReloaded\
├── gui_editor/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models.py            # Data models
│   ├── widgets/
│   │   ├── category_tree.py
│   │   ├── element_table.py
│   │   └── property_editor.py
│   ├── dialogs/
│   │   ├── about.py
│   │   └── preferences.py
│   └── resources/
│       ├── icons/
│       └── styles.qss       # Qt stylesheet
│
├── tui_editor/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── widgets/
│   │   ├── category_list.py
│   │   ├── element_table.py
│   │   └── property_form.py
│   └── styles.css           # Textual CSS
│
└── shared/
    ├── data_model.py        # Shared data layer
    └── validators.py        # Field validation
```

---

## Next Steps

### Immediate Actions

1. **Choose Approach**
   - ✅ Primary: PySide6 GUI
   - ✅ Secondary: Textual TUI (later)

2. **Install Dependencies**
   ```bash
   pip install PySide6
   pip install textual
   ```

3. **Create Prototype**
   - Basic window with 3 panels
   - Load CFF file
   - Display categories
   - Show elements
   - View properties

4. **Iterate**
   - Add search/filter
   - Add editing
   - Add save functionality
   - Polish UI

---

## Questions for You

1. **Which do you prefer to start with?**
   - A) GUI (PySide6) - Full-featured, professional
   - B) TUI (Textual) - Lightweight, terminal-based
   - C) Both in parallel (more work)

2. **Priority features?**
   - Must-have: View, Edit, Save
   - Nice-to-have: Add, Clone, Delete, Compare, Undo/Redo

3. **Dark mode preference?**
   - Yes (modern look)
   - No (light theme)
   - Both (switchable)

4. **Target users?**
   - Just you (optimize for your workflow)
   - Community release (more polish needed)

---

## Conclusion

**Recommended Path:**
1. ✅ Start with **PySide6 GUI** for full-featured editor
2. ✅ Focus on core functionality (view, edit, save)
3. ✅ Add **Textual TUI** version later for quick edits
4. ✅ Keep both versions sharing the same data model

**Timeline:**
- Week 1-4: Working GUI editor
- Week 5-7: Advanced features
- Week 8-9: TUI version (optional)

**Effort:**
- GUI: Medium complexity, high usability
- TUI: Lower complexity, good for quick tasks
- Both: Best of both worlds!

Let me know which direction you'd like to pursue! 🚀
