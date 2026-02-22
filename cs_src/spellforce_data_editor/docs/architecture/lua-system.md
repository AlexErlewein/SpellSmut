# Lua Decompiler (SFLua)

The Lua decompiler system converts Lua 4.01 bytecode back into readable source code, enabling modding of game scripts.

## Table of Contents

1. [Overview](#overview)
2. [Lua 4.01 Bytecode](#lua-401-bytecode)
3. [Decompilation Process](#decompilation-process)
4. [AST Nodes](#ast-nodes)
5. [Code Generation](#code-generation)
6. [Usage](#usage)

## Overview

SpellForce uses **Lua 4.01** for game scripting. The decompiler:

- Parses Lua 4.01 bytecode
- Builds an Abstract Syntax Tree (AST)
- Generates readable Lua source code
- Handles nested functions and closures

### Why Lua 4.01?

Lua 4.01 is an older version (current is 5.4+). Key differences:
- Different bytecode format
- No `break` statement (uses `return`)
- Different scoping rules
- Different argument passing

### Components

| Component | Purpose |
|-----------|---------|
| `LuaDecompiler/` | Bytecode to AST conversion |
| `LuaParser/` | Source code parsing |
| `LuaTokenizer/` | Lexical analysis |
| `lua_sql/` | SQL-like data structures |

## Lua 4.01 Bytecode

### Function Header

```
Offset | Size | Type   | Description
-------|------|--------|-------------------
0x00   | 12   | bytes  | Lua header (Escaped Lua)
0x0C   | var  | string | Source name (null-terminated)
0x??   | 4    | int    | Line defined
0x??   | 4    | int    | Last line defined
0x??   | 1    | byte   | Number of upvalues
0x??   | 1    | byte   | Number of parameters
0x??   | 1    | byte   | Is vararg flag
0x??   | 1    | byte   | Max stack size
```

### Instruction Format

Each instruction is 4 bytes:

```
[OpCode: 1 byte][ArgA: 1 byte][ArgB: 1 byte][ArgC: 1 byte]
```

Or for instructions with larger arguments:

```
[OpCode: 1 byte][ArgA: 1 byte][ArgBx: 2 bytes]
```

### Common Opcodes

| OpCode | Name | Description |
|--------|------|-------------|
| 0 | MOVE | Copy register A to B |
| 1 | LOADK | Load constant to register |
| 2 | LOADBOOL | Load boolean |
| 3 | LOADNIL | Load nil |
| 4 | GETUPVAL | Get upvalue |
| 5 | GETGLOBAL | Get global variable |
| 6 | GETTABLE | Get table field |
| 7 | SETGLOBAL | Set global variable |
| 8 | SETUPVAL | Set upvalue |
| 9 | SETTABLE | Set table field |
| 10 | NEWTABLE | Create table |
| 11 | SELF | Method call setup |
| 12 | ADD | Addition |
| 13 | SUB | Subtraction |
| 14 | MUL | Multiplication |
| 15 | DIV | Division |
| 16 | POW | Power |
| 20 | JMP | Jump |
| 21 | JMPNE | Jump if not equal |
| 22 | JMPEQ | Jump if equal |
| ... | ... | ... |

## Decompilation Process

### Phase 1: Load Bytecode

```csharp
public class LuaBinaryFunction
{
    public string SourceName;
    public int LineDefined;
    public int LastLineDefined;
    public byte NumParams;
    public bool IsVarArg;
    public byte MaxStackSize;

    public List<LuaInstruction> Instructions;
    public List<double> Numbers;
    public List<string> Strings;
    public List<LuaBinaryFunction> Functions;
}
```

### Phase 2: Identify Control Flow

The decompiler scans instructions to identify:

- **Loops**: FORLOOP, LFORLOOP, FORPREP, LFORPREP
- **Conditionals**: JMPxx + JMP patterns
- **Returns**: OP_RETURN
- **Breaks**: Special JMP patterns

```csharp
public List<ChunkInterval> PreloadChunks(LuaBinaryFunction fnc)
{
    List<ChunkInterval> chunks = new List<ChunkInterval>();

    // Scan backward for loops
    for (int i = fnc.Instructions.Count - 1; i >= 0; i--)
    {
        LuaInstruction instr = fnc.Instructions[i];

        switch (instr.OpCode)
        {
            case LuaOpCode.OP_FORLOOP:
                chunks.Add(new ChunkInterval(i, i + instr.ArgS, ChunkType.FOR));
                break;
            case LuaOpCode.OP_LFORLOOP:
                chunks.Add(new ChunkInterval(i, i + instr.ArgS, ChunkType.FOREACH));
                break;
            // ... more cases
        }
    }

    // Scan forward for conditionals
    // ...

    return chunks;
}
```

### Phase 3: Build AST

Using the identified control flow structures, the decompiler builds an AST:

```csharp
public class Decompiler
{
    public Chunk Decompile(LuaBinaryFunction fnc)
    {
        Chunk root = new Chunk();
        List<ChunkInterval> chunks = PreloadChunks(fnc);

        // Process instructions
        for (int i = 0; i < fnc.Instructions.Count; i++)
        {
            LuaInstruction instr = fnc.Instructions[i];

            switch (instr.OpCode)
            {
                case LuaOpCode.OP_RETURN:
                    Return ret = new Return() { parent = root };
                    root.Items.Add(ret);
                    break;

                case LuaOpCode.OP_CALL:
                    Function call = new Function() { parent = root };
                    root.Items.Add(call);
                    break;

                // ... more cases
            }
        }

        Simplify(root);
        return root;
    }
}
```

## AST Nodes

### Node Hierarchy

```
IStatement (interface)
├── Chunk (block of statements)
│   └── Items: List<IStatement>
├── Assignment
│   ├── Left: ILValue
│   └── Right: IRValue
├── MultiAssignment
│   ├── Left: List<ILValue>
│   └── Right: List<IRValue>
├── Function (function call)
│   ├── Name: ILValue
│   └── Arguments: Table
├── Procedure (procedure call)
│   ├── Name: ILValue
│   └── Arguments: Table
├── Return
│   └── Items: List<IRValue>
├── Fork (if statement)
│   ├── IfCondition: IOperatorLogic
│   ├── IfChunk: Chunk
│   ├── ElseIfChunks: List<Chunk>
│   └── ElseChunk: Chunk
├── While (while loop)
│   ├── Condition: IOperatorLogic
│   └── LoopChunk: Chunk
├── For (numeric for loop)
│   ├── name: Identifier
│   ├── from: IRValue
│   ├── to: IRValue
│   ├── step: IRValue
│   └── LoopChunk: Chunk
├── Foreach (generic for loop)
│   ├── index: Identifier
│   ├── value: Identifier
│   ├── table: IRValue
│   └── LoopChunk: Chunk
└── Break
```

### Expression Hierarchy

```
IRValue (interface)
├── Primitive
│   ├── Num (number)
│   ├── Str (string)
│   └── Nil
├── Identifier (variable name)
├── LocalIdentifier (local variable)
├── UpIdentifier (upvalue)
├── SelfIdentifier (method call: obj:method)
├── IndexedIdentifier (table[index])
├── DottedIdentifier (obj.field)
└── Table (array literal)
    └── Items: List<TableAssignment>

IOperator (interface)
├── OperatorUnaryArithmetic (-value)
├── OperatorUnaryLogic (not value)
└── OperatorBinaryArithmetic/Logic (+, -, *, /, ^, ==, !=, <, >, etc.)
    └── Values: List<IRValue>
```

## Code Generation

### Converting AST to Source

```csharp
public override string ToString()
{
    StringBuilder sb = new StringBuilder();

    foreach (IStatement stmt in Items)
    {
        sb.Append(stmt.ToString());
        sb.AppendLine();
    }

    return sb.ToString();
}
```

### Example: Function Call

```lua
-- AST
Function
├── Name: Identifier("print")
└── Arguments: Table
    └── Items: [TableAssignment(nil, Str("Hello"))]

-- Generated source
print("Hello")
```

### Example: If Statement

```lua
-- AST
Fork
├── IfCondition: OperatorBinaryLogic(EQ)
│   └── Values: [Identifier("x"), Num(5)]
├── IfChunk: Chunk
│   └── Items: [Assignment(Identifier("y"), Num(10))]
└── ElseChunk: Chunk
    └── Items: [Assignment(Identifier("y"), Num(20))]

-- Generated source
if x == 5 then
    y = 10
else
    y = 20
end
```

### Example: For Loop

```lua
-- AST
For
├── name: Identifier("i")
├── from: Num(1)
├── to: Num(10)
├── step: Num(1)
└── LoopChunk: Chunk
    └── Items: [Function(...)]

-- Generated source
for i = 1, 10, 1 do
    -- body
end
```

## Usage

### Decompiling a Script

```csharp
// Load bytecode
byte[] bytecode = File.ReadAllBytes("script.luac");

// Parse binary function
LuaBinaryFunction func = new LuaBinaryFunction();
func.Load(bytecode);

// Decompile
Decompiler decompiler = new Decompiler();
Chunk ast = decompiler.Decompile(func);

// Generate source
string source = ast.ToString();

// Save
File.WriteAllText("script.lua", source);
```

### Handling Closures

```csharp
// For nested functions (closures)
Chunk closure = new Chunk();
decompiler.Decompile(func.NestedFunctions[0], closure);

string closureSource = closure.ToString();
```

### Error Handling

Common issues:
- **Unknown opcodes**: New or custom bytecode
- **Malformed chunks**: Corrupted bytecode
- **Stack imbalance**: Parser errors

```csharp
try
{
    Chunk ast = decompiler.Decompile(func);
}
catch (Exception e)
{
    LogUtils.Log.Error($"Decompilation failed: {e.Message}");
}
```

## Limitations

1. **Comments Lost**: Original comments are not in bytecode
2. **Variable Names**: Local variables are regenerated (_loc0, _loc1, etc.)
3. **Formatting**: Output is functional but not pretty
4. **Edge Cases**: Some obfuscated code may not decompile perfectly

## Implementation Reference

| File | Description |
|------|-------------|
| `SFEngine/SFLua/LuaDecompiler/Decompiler.cs` | Main decompiler |
| `SFEngine/SFLua/LuaDecompiler/LuaBinaryFunction.cs` | Bytecode parser |
| `SFEngine/SFLua/LuaDecompiler/Chunk.cs` | AST root |
| `SFEngine/SFLua/LuaDecompiler/Node.cs` | AST nodes |
| `SFEngine/SFLua/LuaTokenizer/Parser.cs` | Source tokenizer |

---

**Related**: [Architecture Overview](../architecture/README.md)
