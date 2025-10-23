# UV Quick Reference Card

**UV** is the project-standard Python package manager (10-100x faster than pip).

---

## Installation

### Windows
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### macOS/Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Verify
```bash
uv --version
```

---

## Common Commands

### Package Management
```bash
# Install package
uv pip install Pillow

# Install multiple packages
uv pip install Pillow requests numpy

# Upgrade package
uv pip install --upgrade Pillow

# Install from requirements.txt
uv pip install -r requirements.txt

# Uninstall package
uv pip uninstall Pillow

# List installed packages
uv pip list
```

### Script Execution
```bash
# Run Python script
uv run script.py

# Run with arguments
uv run script.py --arg value

# Run Python module
uv run -m tirganach.gui_editor

# Execute Python code
uv run python -c "print('Hello')"
```

### Virtual Environments
```bash
# Create venv
uv venv

# Create venv with specific Python version
uv venv --python 3.11

# Activate venv (Windows)
.venv\Scripts\activate

# Activate venv (macOS/Linux)
source .venv/bin/activate
```

---

## SpellSmut Project Commands

### Icon Extraction
```bash
cd SpellSmut/src/helper_tools
uv run extract_ui_with_names.py
uv run convert_ui_textures.py
uv run rotate_ui_pngs.py
uv run organize_ui_assets.py
```

### GUI Editor
```bash
cd TirganachReloaded
uv run -m tirganach.gui_editor
```

### Install Dependencies
```bash
uv pip install Pillow
```

---

## pip vs UV Comparison

| Task | pip | UV |
|------|-----|-----|
| Install package | `pip install package` | `uv pip install package` |
| Run script | `python script.py` | `uv run script.py` |
| Run module | `python -m module` | `uv run -m module` |
| Create venv | `python -m venv .venv` | `uv venv` |
| Upgrade package | `pip install --upgrade pkg` | `uv pip install --upgrade pkg` |

---

## Why UV?

✅ **10-100x faster** than pip  
✅ **Better dependency resolution**  
✅ **Works with existing tools** (pip, requirements.txt)  
✅ **Cross-platform** (Windows, macOS, Linux)  
✅ **Written in Rust** (blazingly fast)

---

## Project Standard

**ALL Python operations in SpellSmut use UV:**

❌ Don't: `pip install Pillow`  
✅ Do: `uv pip install Pillow`

❌ Don't: `python script.py`  
✅ Do: `uv run script.py`

❌ Don't: `python -m module`  
✅ Do: `uv run -m module`

---

## Troubleshooting

### UV not found
```bash
# Windows - Reinstall
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux - Add to PATH
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### Package not found
```bash
# Install the package first
uv pip install package-name

# Then run
uv run script.py
```

### Python version mismatch
```bash
# Create venv with specific version
uv venv --python 3.11

# Activate and use
.venv\Scripts\activate  # Windows
uv run script.py
```

---

## Resources

- **GitHub**: https://github.com/astral-sh/uv
- **Docs**: https://docs.astral.sh/uv/
- **Install**: https://astral.sh/uv/install

---

**Remember: UV is the SpellSmut project standard! 🚀**