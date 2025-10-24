# Source Code Analysis: UI Icon Loading

## Files Analyzed

From `ModdingTools/Inspiration/spellforce_data_editor/`:

1. **SFEngine/SFCFF/CTG/Category2012.cs** - Item UI data structure
2. **SpellforceDataEditor/SFCFF/category forms/Control13.cs** - Item UI editor
3. **SFEngine/SFResources/SFResourceContainer.cs** - Resource loading system

## Key Finding: UIHandle = Filename

### Category2012.cs - Data Structure

```csharp
[StructLayout(LayoutKind.Sequential, Pack = 1)]
public unsafe struct Category2012Item : ICategorySubItem
{
    public ushort ItemID;           // Links to item table
    public byte UIIndex;            // 1=main icon, 2=overlay
    public fixed byte UIHandle[64]; // ⭐ THE ICON FILENAME
    public ushort IsScaledDown;     // Scale flag
    
    public string GetHandleString()
    {
        Encoding encoding = Encoding.GetEncoding(1252);
        fixed (byte* s = UIHandle)
        {
            return (encoding.GetString(s, 64));
        }
    }
}

public class Category2012 : CategoryBaseMultiple<Category2012Item>
{
    public override string GetName() => "Item UI data";
    public override short GetCategoryID() => 2012;
}
```

**Key Points:**
- `UIHandle` is a 64-byte fixed char array
- Contains the asset name WITHOUT extension
- Example: `"ui_item_equip_weapon_dagger_flame"`

### SFResourceContainer.cs - Texture Loading

```csharp
public class SFResourceContainer<T>
{
    string prefix_path;      // "texture"
    string[] extensions;     // ".dds|.tga"
    string[] pak_files;      // ["sf35.pak", "sf32.pak", ...]
    
    public bool Load(string rname, FileSource source, out T res, out int err_code)
    {
        // Construct full path
        string full_res_name = prefix_path + "\\" + rname + extension;
        
        // Example:
        // prefix_path = "texture"
        // rname = "ui_item_equip_weapon_dagger_flame"
        // extension = ".dds"
        // full_res_name = "texture\\ui_item_equip_weapon_dagger_flame.dds"
        
        // Search PAK files in priority order
        data = SFUnPak.SFUnPak.LoadFileFind(full_res_name, paks_to_search);
        
        return true;
    }
}

// Texture resource manager initialization
public static SFResourceContainer<SFTexture> Textures = 
    new SFResourceContainer<SFTexture>(
        "texture",                    // Base directory in PAK
        ".dds|.tga",                  // File extensions to try
        new string[] {                // PAK search order (newest first)
            "sf35.pak",
            "sf32.pak", 
            "sf25.pak",
            "sf22.pak",
            "sf1.pak",
            "sf0.pak"
        }
    );
```

**Key Points:**
- UIHandle is used directly as the resource name
- Path is constructed as: `texture\{UIHandle}.{ext}`
- PAK files searched in priority order (mods override base game)

### Control13.cs - Editor UI

```csharp
public partial class Control13 : SFControl
{
    Category2012 c2012;
    
    public Control13()
    {
        c2012 = SFCategoryManager.gamedata.c2012;
        
        column_dict.Add("Item ID", "ItemID");
        column_dict.Add("Item UI index", "UIIndex");
        column_dict.Add("Item UI handle", "UIHandle");  // ⭐ Displayed as text
        column_dict.Add("Scaled down?", "IsScaledDown");
    }
    
    private void ListUI_SelectedIndexChanged(object sender, EventArgs e)
    {
        int cur_selected = ListUI.SelectedIndex;
        if (cur_selected < 0) return;
        
        // Display UIHandle as text (no icon preview!)
        textBox4.Text = c2012[current_element, cur_selected].GetHandleString();
        checkBox1.Checked = (c2012[current_element, cur_selected].IsScaledDown == 1);
    }
    
    public override string get_element_string(int index)
    {
        UInt16 item_id = c2012[index, 0].ItemID;
        return $"{item_id} {SFCategoryManager.GetItemName(item_id)}";
    }
}
```

**Key Points:**
- Editor displays UIHandle as text only
- No icon preview in the editor
- We can do better in our GUI!

## Complete Loading Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Game needs to display item icon                          │
│    Item ID: 27                                               │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Look up in Category2012 (item_ui table)                  │
│    c2012[item_id=27].UIHandle = "ui_item_equip_weapon_...   │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. SFResourceContainer.Load("ui_item_equip_weapon_...", ...) │
│    Constructs: "texture\\ui_item_equip_weapon_...dds"       │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Search PAK files in order:                               │
│    sf35.pak → sf32.pak → sf25.pak → sf22.pak → sf1.pak      │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Extract DDS data from PAK                                │
│    Decompress, load into GPU texture                        │
└─────────────────────────────────────────────────────────────┘
```

## Implications for Our GUI Editor

### What We Need to Do

1. **Re-extract UI assets** preserving original filenames:
   ```
   texture/ui_item_equip_weapon_dagger_flame.dds
   texture/ui_spell_EM_Fire_FireBurst.dds
   ```

2. **Convert to PNG** keeping the same names:
   ```
   ExtractedAssets/UI/extracted/items/ui_item_equip_weapon_dagger_flame.png
   ExtractedAssets/UI/extracted/spells/ui_spell_EM_Fire_FireBurst.png
   ```

3. **Direct lookup** in Python:
   ```python
   def get_icon_path(item_id):
       ui_entry = find_item_ui(item_id)
       handle = ui_entry["item_ui_handle"]
       # Direct file lookup - no mapping needed!
       return f"ExtractedAssets/UI/extracted/items/{handle}.png"
   ```

### What We DON'T Need

- ❌ Mapping file (UIHandle → filename)
- ❌ Index-based lookup
- ❌ Complex resolution logic

### Why This is Better

- ✅ Matches game engine behavior exactly
- ✅ Simple, direct file lookup
- ✅ Easy to add new icons (just drop PNG with correct name)
- ✅ Modders can override icons by filename
- ✅ No synchronization issues

## Example Data

### From GameData.json

```json
{
  "item_id": 27,
  "item_ui_index": 1,
  "item_ui_handle": "ui_item_equip_weapon_dagger_flame",
  "scaled_down": 0
}
```

### File We Need

```
ExtractedAssets/UI/extracted/items/ui_item_equip_weapon_dagger_flame.png
```

### Python Code

```python
icon_path = Path("ExtractedAssets/UI/extracted/items") / f"{ui_handle}.png"
if icon_path.exists():
    pixmap = QPixmap(str(icon_path))
    label.setPixmap(pixmap.scaled(64, 64))
```

## Conclusion

The SpellForce engine uses a **simple, direct filename-based system**:
- UIHandle = filename (without extension)
- No hash tables, no indices, no complex mapping
- Just: `texture\{UIHandle}.dds`

We should replicate this exact behavior in our editor for maximum compatibility and simplicity.
