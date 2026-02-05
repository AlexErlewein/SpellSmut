# Rust Tools for SpellSmut

Fast file handling tools written in Rust, callable from Python.

## Structure

```
rust_src/
├── __init__.py      # Package exports
├── tools.py         # Python wrapper functions
├── Cargo.toml       # Rust dependencies
├── src/
│   └── main.rs      # Rust CLI implementation
└── target/release/
    └── spellsmut-tools  # Compiled binary
```

## Python Usage

```python
from rust_src import list_files, read_file

# List files with optional extension filter
files = list_files("./some/path", extension="lua")

# Read file contents
content = read_file("./some/file.txt")
```

## Building

After making changes to Rust code:

```bash
cd rust_src
cargo build --release
```

## Adding New Functions

### 1. Add Rust Command

In `src/main.rs`, add a new subcommand to the `Commands` enum:

```rust
#[derive(Subcommand)]
enum Commands {
    // ... existing commands ...

    /// Description of your new command
    YourCommand {
        #[arg(short, long)]
        input: PathBuf,

        #[arg(short, long)]
        output: Option<PathBuf>,
    },
}
```

Then handle it in `main()`:

```rust
Commands::YourCommand { input, output } => {
    // Your implementation here
    let result = your_function(&input);
    println!("{}", serde_json::to_string(&result).unwrap());
}
```

### 2. Add Python Wrapper

In `tools.py`, add a method to the `RustTools` class:

```python
def your_function(self, input_path: str | Path, output_path: Optional[str | Path] = None) -> dict:
    """
    Description of your function.

    Args:
        input_path: Input file path
        output_path: Optional output file path

    Returns:
        Result data
    """
    args = ["your-command", "--input", str(input_path)]
    if output_path:
        args.extend(["--output", str(output_path)])

    result = self._run(*args)

    if result.returncode != 0:
        raise RuntimeError(f"your_function failed: {result.stderr}")

    return json.loads(result.stdout)
```

### 3. Export the Function

In `tools.py`, add a convenience function at the bottom:

```python
def your_function(input_path: str | Path, output_path: Optional[str | Path] = None) -> dict:
    """See RustTools.your_function for details."""
    return rust_tools.your_function(input_path, output_path)
```

In `__init__.py`, add to exports:

```python
from .tools import rust_tools, list_files, read_file, your_function, RustTools

__all__ = ["rust_tools", "list_files", "read_file", "your_function", "RustTools"]
```

### 4. Rebuild

```bash
cd rust_src
cargo build --release
```

## Available Commands

| Command | Python Function | Description |
|---------|-----------------|-------------|
| `list`  | `list_files()`  | List files in directory with optional extension filter |
| `read`  | `read_file()`   | Read file contents |
| `echo`  | `rust_tools.echo()` | Test connectivity |

## Tips

- Use `--json` flag for structured data exchange
- Return JSON from Rust for complex data types
- Handle errors in Python with try/except around the wrapper functions
- For binary data, consider base64 encoding in JSON or writing to temp files
