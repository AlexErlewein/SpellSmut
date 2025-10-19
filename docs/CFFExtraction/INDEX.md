# SpellForce CFF Modding - Documentation Index

Quick navigation to all documentation and scripts for GameData.cff modding.

---

## 🚀 Start Here

**New to CFF modding?** Start with these in order:

1. **[README_CFF_MODDING.md](README_CFF_MODDING.md)** - Project overview and quick start
2. **[TIGANACH_RELOADED_SETUP.md](TIGANACH_RELOADED_SETUP.md)** - Library setup details
3. **[CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md)** - Complete modding guide

---

## 📖 Documentation Files

### Main Guides
| File | Description | Read When |
|------|-------------|-----------|
| **[README_CFF_MODDING.md](README_CFF_MODDING.md)** | Main project README | First time setup |
| **[CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md)** | Complete modding guide with examples | Learning how to mod |
| **[CFF_QUICK_REFERENCE.md](CFF_QUICK_REFERENCE.md)** | Quick reference card | While coding mods |
| **[CFF_EXTRACTION_SUMMARY.md](CFF_EXTRACTION_SUMMARY.md)** | Technical summary | Understanding internals |
| **[TIGANACH_RELOADED_SETUP.md](TIGANACH_RELOADED_SETUP.md)** | Library setup guide | Setting up environment |

### Library Documentation
| File | Description | Location |
|------|-------------|----------|
| **README_INSTALLATION.md** | Installation guide | `ModdingTools/TiganachReloaded/` |
| **EXPLANATION.md** | CFF file format details | `ModdingTools/TiganachReloaded/` |
| **README.md** | Original library docs | `ModdingTools/TiganachReloaded/` |

---

## 🛠️ Scripts

### Test & Example Scripts (in ModdingTools/TiganachReloaded/)
| File | Purpose | Usage |
|------|---------|-------|
| **test_cff_extract.py** | Verify library works | `cd ModdingTools\TiganachReloaded && python test_cff_extract.py` |
| **cff_modding_examples.py** | 7 working examples | `cd ModdingTools\TiganachReloaded && python cff_modding_examples.py` |
| **create_mod.py** | Mod creation template | `cd ModdingTools\TiganachReloaded && python create_mod.py` |

---

## 📁 Directory Structure

```
H:\SpellSmut\
│
├── Documentation (Start Here!)
│   ├── INDEX.md                         # ← You are here
│   ├── README_CFF_MODDING.md            # Main README
│   ├── CFF_MODDING_GUIDE.md             # Complete guide
│   ├── CFF_QUICK_REFERENCE.md           # Quick ref
│   ├── CFF_EXTRACTION_SUMMARY.md        # Technical summary
│   └── TIGANACH_RELOADED_SETUP.md       # Setup guide
│
├── Game Files
│   ├── OriginalGameFiles\
│   │   └── data\
│   │       └── GameData.cff             # Original (97 MB)
│   │
│   └── ModdedGameFiles\                 # Your mods
│       └── GameData_*.cff               # Modified files
│
└── Tools
    └── ModdingTools\
        └── TiganachReloaded\            # CFF library + scripts
            ├── tirganach\               # Library source code
            ├── test_cff_extract.py      # Test script
            ├── cff_modding_examples.py  # Examples
            ├── create_mod.py            # Mod template
            ├── README_INSTALLATION.md
            ├── EXPLANATION.md
            └── README.md
```

---

## 📚 Documentation by Topic

### Getting Started
- **Installation:** [TIGANACH_RELOADED_SETUP.md](TIGANACH_RELOADED_SETUP.md)
- **First Steps:** [README_CFF_MODDING.md](README_CFF_MODDING.md) → Quick Start section
- **Basic Examples:** Run `python cff_modding_examples.py`

### Learning to Mod
- **Complete Guide:** [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md)
- **Query Patterns:** [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Query Data section
- **Modify Data:** [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Practical Examples section

### Reference
- **Quick Commands:** [CFF_QUICK_REFERENCE.md](CFF_QUICK_REFERENCE.md)
- **Enums & Types:** [CFF_QUICK_REFERENCE.md](CFF_QUICK_REFERENCE.md) → Common Enums section
- **Available Tables:** [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Available Tables section

### Advanced
- **File Format:** `ModdingTools/TiganachReloaded/EXPLANATION.md`
- **Source Code:** `ModdingTools/TiganachReloaded/tirganach/`
- **Technical Details:** [CFF_EXTRACTION_SUMMARY.md](CFF_EXTRACTION_SUMMARY.md)

---

## 🎯 Common Tasks

### I want to...

**Test if everything works**
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python test_cff_extract.py
```
→ See: `ModdingTools/TiganachReloaded/test_cff_extract.py`

**Learn query patterns**
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python cff_modding_examples.py
```
→ See: `ModdingTools/TiganachReloaded/cff_modding_examples.py`

**Create my first mod**
```bash
cd H:\SpellSmut\ModdingTools\TiganachReloaded
python create_mod.py
```
→ See: `ModdingTools/TiganachReloaded/create_mod.py`

**Find specific items/spells**
→ See: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Query Data section

**Modify item stats**
→ See: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Example 1

**Create overpowered heroes**
→ See: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Example 3

**Change spell costs**
→ See: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Example 4

**Look up enum values**
→ See: [CFF_QUICK_REFERENCE.md](CFF_QUICK_REFERENCE.md) → Common Enums

**Understand the file format**
→ See: `ModdingTools/TiganachReloaded/EXPLANATION.md`

**Troubleshoot errors**
→ See: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Troubleshooting section

---

## 📊 Quick Stats

**GameData.cff contains:**
- 3,455 Spells
- 7,101 Items
- 2,617 Creatures
- 207 Buildings
- 635 Armor pieces
- 721 Weapons
- 176,318 Text strings

**Total size:** 97 MB (66,859,922 bytes)

---

## 🔗 Quick Links

### Documentation
- [Main README](README_CFF_MODDING.md)
- [Modding Guide](CFF_MODDING_GUIDE.md)
- [Quick Reference](CFF_QUICK_REFERENCE.md)
- [Setup Guide](TIGANACH_RELOADED_SETUP.md)

### Scripts
- [Test Script](ModdingTools/TiganachReloaded/test_cff_extract.py)
- [Examples](ModdingTools/TiganachReloaded/cff_modding_examples.py)
- [Mod Creator](ModdingTools/TiganachReloaded/create_mod.py)

### Library
- [Installation](ModdingTools/TiganachReloaded/README_INSTALLATION.md)
- [File Format](ModdingTools/TiganachReloaded/EXPLANATION.md)
- [Source Code](ModdingTools/TiganachReloaded/tirganach/)

---

## 🆘 Help

### Something not working?

1. **Check installation:**
   ```bash
   pip show tirganach
   ```

2. **Run test script:**
   ```bash
   python test_cff_extract.py
   ```

3. **Read troubleshooting:**
   - [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md) → Troubleshooting
   - [README_CFF_MODDING.md](README_CFF_MODDING.md) → Troubleshooting

4. **Check file locations:**
   - Library: `ModdingTools/TiganachReloaded/`
   - Original CFF: `OriginalGameFiles/data/GameData.cff`
   - Modded CFF: `ModdedGameFiles/`

---

## 🎮 Ready to Start?

### Three-Step Quickstart

1. **Verify Installation**
   ```bash
   cd H:\SpellSmut\ModdingTools\TiganachReloaded
   python test_cff_extract.py
   ```

2. **Read the Guide**
   Open: [CFF_MODDING_GUIDE.md](CFF_MODDING_GUIDE.md)

3. **Create Your First Mod**
   ```bash
   cd H:\SpellSmut\ModdingTools\TiganachReloaded
   python create_mod.py
   ```

---

## 📝 Notes

- All paths assume Windows
- Python 3.11+ required
- Always backup GameData.cff before testing
- Start with small mods, test frequently

---

**Happy Modding!** 🎮

*Last Updated: 2025-10-19*
