"""
Python wrapper for spellsmut-tools Rust CLI.

Usage:
    from rust_src.tools import rust_tools

    files = rust_tools.list_files("./src", extension="py")
    content = rust_tools.read_file("./src/main.py")
"""

import subprocess
import json
from pathlib import Path
from typing import Optional


class RustTools:
    def __init__(self):
        # Get the path to the compiled Rust binary relative to this file
        self._bin_path = Path(__file__).parent / "target" / "release" / "spellsmut-tools"

    @property
    def bin_path(self) -> Path:
        if not self._bin_path.exists():
            raise FileNotFoundError(
                f"Rust binary not found at {self._bin_path}. "
                "Run 'cargo build --release' in the rust-src directory."
            )
        return self._bin_path

    def _run(self, *args: str) -> subprocess.CompletedProcess:
        """Run the Rust tool with given arguments."""
        result = subprocess.run(
            [str(self.bin_path), *args],
            capture_output=True,
            text=True
        )
        return result

    def list_files(
        self,
        path: str | Path,
        extension: Optional[str] = None,
        as_json: bool = True
    ) -> list[str]:
        """
        List files in a directory.

        Args:
            path: Directory to scan
            extension: Optional file extension filter (e.g., "lua", "pak")
            as_json: Return parsed list (True) or raw output (False)

        Returns:
            List of file paths
        """
        args = ["list", "--path", str(path), "--json"]
        if extension:
            args.extend(["--extension", extension])

        result = self._run(*args)

        if result.returncode != 0:
            raise RuntimeError(f"list_files failed: {result.stderr}")

        if as_json:
            return json.loads(result.stdout)
        return result.stdout

    def read_file(self, path: str | Path) -> str:
        """
        Read a file and return its contents.

        Args:
            path: File to read

        Returns:
            File contents as string
        """
        result = self._run("read", "--path", str(path))

        if result.returncode != 0:
            raise RuntimeError(f"read_file failed: {result.stderr}")

        return result.stdout

    def echo(self, message: str) -> str:
        """
        Echo a message (for testing connectivity).

        Args:
            message: Message to echo

        Returns:
            Echoed message
        """
        result = self._run("echo", message)

        if result.returncode != 0:
            raise RuntimeError(f"echo failed: {result.stderr}")

        return result.stdout.strip()


# Singleton instance for easy importing
rust_tools = RustTools()


# Convenience functions for direct import
def list_files(path: str | Path, extension: Optional[str] = None) -> list[str]:
    """List files in a directory. See RustTools.list_files for details."""
    return rust_tools.list_files(path, extension)


def read_file(path: str | Path) -> str:
    """Read a file. See RustTools.read_file for details."""
    return rust_tools.read_file(path)
