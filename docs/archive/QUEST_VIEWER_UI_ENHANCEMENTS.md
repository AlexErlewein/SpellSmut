# Quest Viewer - UI/UX Enhancements ✨

## ✅ Implemented Enhancements

### 1. **Quest ID After Name**
- Format: `Quest Name [ID]`
- Example: `Staub der Sterne [1]`
- Makes quest names more prominent

### 2. **Main Quests in Bold**
- All top-level quests (main quests) are displayed in **bold**
- Sub-quests remain in regular font
- Easy visual distinction between main and sub-quests

### 3. **Collapsible Tree View**
- Parent quests show collapse/expand arrows (▶/▼)
- Click arrow to expand/collapse children
- Tree structure clearly visible

### 4. **Expand All / Collapse All Buttons**
- Located below the quest tree
- "Expand All" - Opens all quest hierarchies
- "Collapse All" - Collapses all to show only main quests

## 🎨 Visual Layout

```
┌─────────────────────────────────────────┐
│ Quest Viewer                            │
├─────────────────────────────────────────┤
│ ┌─ Quests ─────────────────────────┐   │
│ │ Quest Name                        │   │
│ │ ─────────────────────────────────│   │
│ │ ▶ Staub der Sterne [1]          │   │  ← Bold (main quest)
│ │ ▼ Darius der Kartograph [12]    │   │  ← Bold (main quest)
│ │   ├─ Der Weg nach Eloni [14]    │   │  ← Regular (sub-quest)
│ │   └─ Sprecht mit Celen [15]     │   │  ← Regular (sub-quest)
│ │ ▶ Die Geiseln [24]              │   │  ← Bold (main quest)
│ │                                   │   │
│ │ [Expand All] [Collapse All]      │   │
│ └──────────────────────────────────┘   │
└─────────────────────────────────────────┘
```

## 🔧 Technical Implementation

### Tree Widget Setup
```python
self.quest_tree.setHeaderLabels(["Quest Name"])
self.quest_tree.setColumnWidth(0, 400)  # Wider for better readability
```

### Item Creation with Formatting
```python
# Format: "Name [ID]"
display_text = f"{name} [{quest_id}]"
item = QTreeWidgetItem(self.quest_tree, [display_text])
```

### Main Quest Bold Styling
```python
# After building hierarchy, make top-level items bold
for i in range(self.quest_tree.topLevelItemCount()):
    item = self.quest_tree.topLevelItem(i)
    font = item.font(0)
    font.setBold(True)
    item.setFont(0, font)
```

## 🚀 How to Use

```bash
# Launch the enhanced quest viewer
uv run python simple_quest_viewer.py
```

### Navigation
1. **Browse Quests**: Scroll through the tree view
2. **Expand/Collapse**: Click arrows next to parent quests
3. **Quick Actions**: Use Expand All / Collapse All buttons
4. **Select Quest**: Click any quest to see details
5. **Main Quest Focus**: Bold quests are main storyline quests

## 📋 User Experience Improvements

### Before
- Quest ID in first column (takes space)
- No visual distinction between main and sub-quests
- Manual expand/collapse only

### After
✅ Quest name prominent, ID in brackets
✅ **Bold main quests** stand out
✅ Clear hierarchy with collapse arrows
✅ Quick Expand All / Collapse All buttons
✅ More readable, professional appearance

## 🎯 Benefits

1. **Better Readability**: Quest names are the focus
2. **Clear Hierarchy**: Bold main quests, indented sub-quests
3. **Efficient Navigation**: Quick expand/collapse controls
4. **Professional Look**: Clean, organized interface
5. **Consistent with Editor**: Matches main TirganachReloaded editor style

## 📝 Summary

All requested UI/UX enhancements have been implemented:

✅ Main quests in **bold letters**
✅ Quest ID after the name: `Name [ID]`
✅ Collapsible tree view with arrows
✅ Expand All / Collapse All buttons

The quest viewer now has a professional, user-friendly interface! 🎉
