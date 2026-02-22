# Script Editing Guide

The Script Editor and Lua Decompiler allow you to view, decompile, and modify game scripts.

## Table of Contents

1. [Overview](#overview)
2. [Lua in SpellForce](#lua-in-spellforce)
3. [Decompiling Scripts](#decompiling-scripts)
4. [Understanding Decompiled Code](#understanding-decompiled-code)
5. [Modifying Scripts](#modifying-scripts)
6. [Limitations](#limitations)

## Overview

SpellForce uses **Lua 4.01** for game scripting. The editor provides:

- Lua 4.01 bytecode decompiler
- Script browser
- Basic syntax highlighting
- Export/import functionality

### Opening Script Editor

1. Click **"Script Editor"** on main window
2. Navigate to `scripts/` folder
3. Select `.lua` or `.lub` file
4. View decompiled source

## Lua in SpellForce

### Lua Version

**Lua 4.01** (not 5.x!)

Key differences from modern Lua:
- No `break` statement
- Different scoping rules
- Different argument passing
- No `continue` statement
- `repeat...until` instead of `while...do`

### Script Types

| Type | Extension | Description |
|------|-----------|-------------|
| Source | .lua | Human-readable source |
| Bytecode | .lub | Compiled bytecode |
| Precompiled | .lua | Actually bytecode |

**Note**: Most game files are bytecode (`.lua` extension but compiled).

### Script Locations

- `scripts/` - Main game scripts
- `scripts/ai/` - AI behavior
- `scripts/quests/` - Quest scripts
- `scripts/dialogs/` - Dialogue trees
- `scripts/spells/` - Spell scripts

## Decompiling Scripts

### Automatic Decompilation

When you open a compiled script:
1. Select file in browser
2. Editor detects bytecode
3. Automatically decompiles
4. Shows source code

### Manual Decompilation

To decompile without opening:
1. Right-click script file
2. Select **"Decompile"**
3. Choose save location
4. Decompiled source saved

### Batch Decompilation

Decompile entire folder:
1. Right-click folder
2. Select **"Decompile All"**
3. Choose destination
4. All `.lua` files decompiled

## Understanding Decompiled Code

### Variable Names

Decompiled code has regenerated variable names:
- Local variables: `_loc0`, `_loc1`, etc.
- Arguments: `_arg0`, `_arg1`, etc.
- Upvalues: `_upvalue_0`, etc.

### Code Structure

The decompiler produces working but not pretty code:

```lua
-- Decompiled code example
function func(_arg0, _arg1)
    local _loc0 = _arg0 + 10
    if _loc0 > 100 then
        return _loc0
    else
        return _arg1 * 2
    end
end
```

### Common Patterns

**Function Definition**:
```lua
function name(arg1, arg2)
    -- body
end
```

**Tables (Arrays)**:
```lua
local arr = {1, 2, 3, 4}
```

**Tables (Dictionaries)**:
```lua
local dict = {key1 = "value1", key2 = "value2"}
```

**If Statements**:
```lua
if condition then
    -- then
elseif condition2 then
    -- elseif
else
    -- else
end
```

**Loops**:
```lua
-- Numeric for loop
for i = 1, 10, 1 do
    -- body
end

-- Generic for loop (foreach)
for k, v in table do
    -- body
end

-- While loop (decompiled as repeat until with condition)
repeat
    -- body
until not condition
```

**Function Calls**:
```lua
-- Regular call
result = function(arg1, arg2)

-- Method call (object:method)
obj:method(arg1, arg2)
```

## Modifying Scripts

### Editing Decompiled Code

1. Open script
2. Edit source code
3. Click **"Apply"**
4. **Warning**: Cannot recompile to Lua 4.01 bytecode

### Limitations

**The editor CANNOT**:
- Compile Lua 4.01 bytecode
- Inject scripts into PAK files
- Modify compiled `.lua` files

**What you CAN do**:
- View and understand game logic
- Extract algorithms
- Document behavior
- Create reference implementations

### Workarounds

**For Modding**:
1. Understand the original script
2. Create a new script with your changes
3. Load your script from a custom location

**For Analysis**:
1. Decompile scripts
2. Study the logic
3. Document your findings
4. Share knowledge with community

## Script Analysis

### Finding Functions

Use the function list:
1. Click **"Functions"** panel
2. Shows all functions in current script
3. Click to jump to function

### Searching

**Find in File**:
```
Ctrl+F: Open search
Enter term to find
F3: Find next
Shift+F3: Find previous
```

**Find in All Scripts**:
```
Ctrl+Shift+F: Search all scripts
Results show in search panel
Click result to open file
```

### Cross-Reference

Find all calls to a function:
1. Right-click function name
2. Select **"Find References"**
3. Shows all call sites

## Common Script Types

### AI Scripts

AI behavior scripts control:
- Unit decision-making
- Attack priorities
- Retreat conditions
- Spell usage

**Example pattern**:
```lua
function onAttack(unit, target)
    if target.health < 100 then
        castSpell("Fireball", target)
    else
        attack(target)
    end
end
```

### Quest Scripts

Quest scripts manage:
- Quest state
- Objective tracking
- Rewards
- Fail conditions

**Example pattern**:
```lua
function onQuestStart(player)
    setQuestState("QUEST_001", "IN_PROGRESS")
    addQuestObjective(player, "Kill 5 enemies")
end

function onEnemyKilled(player, enemy)
    if getQuestState("QUEST_001") == "IN_PROGRESS" then
        progress = getQuestProgress(player, "QUEST_001")
        if progress >= 5 then
            completeQuest(player, "QUEST_001")
        end
    end
end
```

### Spell Scripts

Spell scripts define:
- Damage calculations
- Area of effect
- Duration
- Visual effects

**Example pattern**:
```lua
function onSpellCast(caster, target, params)
    damage = params.power * (caster.level / 10)
    applyDamage(target, damage, params.damageType)
    createVisualEffect(target, "fire_explosion")
end
```

## Best Practices

### 1. Document Decompiled Code

Add comments to clarify logic:
```lua
-- param0: base damage
-- param1: damage multiplier
function calculateDamage(base, mult)
    return base * mult
end
```

### 2. Rename Variables

When studying, create annotated versions:
```lua
-- Original: local _loc0 = _arg0 + 10
-- Annotated: local total_health = base_health + 10
```

### 3. Create Function Summaries

Document what each function does:
```lua
-- Checks if unit should retreat based on health percentage
function shouldRetreat(unit)
    return unit.hp < unit.max_hp * 0.2
end
```

### 4. Identify Key Functions

Look for important functions:
- `onInit` - Initialization
- `onUpdate` - Per-frame update
- `onAttack` - Attack handler
- `onDeath` - Death handler

## Advanced Usage

### Extracting Game Logic

Use decompiler to understand:
- Damage formulas
- AI behavior
- Quest requirements
- Spell mechanics

**Example**: Extract damage formula from spell script
```lua
-- Decompiled
function calc(_arg0, _arg1, _arg2)
    local _loc0 = _arg0 * _arg1
    return _loc0 + _arg2
end

-- Documented
-- arg0: base damage
-- arg1: spell power multiplier
-- arg2: flat bonus
function calculateDamage(base, multiplier, bonus)
    return base * multiplier + bonus
end
```

### Creating Compatibility Layers

When creating new scripts:
1. Study original script patterns
2. Match function signatures
3. Use similar structure
4. Test thoroughly

## Troubleshooting

### Decompilation Errors

**"Unknown opcode"**:
- Script uses custom bytecode
- May be obfuscated
- Cannot decompile

**"Malformed chunk"**:
- Corrupted script file
- Invalid bytecode
- Cannot recover

### Variable Naming Confusion

**Solution**: Keep a reference:
```lua
-- _loc0: current health
-- _loc1: max health
-- _arg0: damage amount
```

### Control Flow Confusion

**Complex conditions**:
- Break down into smaller parts
- Use parentheses to clarify
- Add comments

**Nested loops**:
- Indent properly
- Comment loop purpose
- Track loop variables

## Tools and Resources

### External Tools

- **Lua 4.0 Reference**: https://www.lua.org/manual/4.0/
- **Hex Editor**: For inspecting bytecode
- **Diff Tool**: Compare script versions

### Community Resources

- **Script Database**: Community-decompiled scripts
- **Function Reference**: Documented game functions
- **Modding Tutorials**: Script modification guides

## Limitations

### Technical Limitations

- No Lua 4.01 compiler available
- Cannot modify compiled scripts directly
- Decompilation is not perfect
- Comments are lost

### Legal/Ethical

- Respect game copyright
- Use for modding/analysis only
- Do not redistribute game assets
- Credit original authors

## Next Steps

- [Game Data Editor](gamedata-editor.md) - Edit game database
- [Map Editor](map-editor.md) - Create maps
- [Asset Management](assets.md) - Extract assets

---

**Related**: [Getting Started Guide](README.md), [Architecture: Lua System](../architecture/lua-system.md)
