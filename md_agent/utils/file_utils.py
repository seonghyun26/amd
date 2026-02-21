"""File reading and path utilities."""

from __future__ import annotations

import glob
from pathlib import Path
from typing import Optional


def read_file(
    file_path: str,
    max_lines: int = 500,
    tail: bool = False,
) -> str:
    """Read a text file and return its contents.

    Args:
        file_path: Path to the file.
        max_lines: Maximum number of lines to return.
        tail: If True, return the last ``max_lines`` instead of the first.
    """
    path = Path(file_path)
    if not path.exists():
        return f"[Error] File not found: {file_path}"
    try:
        lines = path.read_text(errors="replace").splitlines()
    except Exception as exc:
        return f"[Error] Could not read {file_path}: {exc}"

    if tail:
        lines = lines[-max_lines:]
    else:
        lines = lines[:max_lines]
    return "\n".join(lines)


def list_files(
    directory: str,
    pattern: str = "*",
    recursive: bool = False,
) -> list[str]:
    """List files in a directory matching a glob pattern."""
    base = Path(directory)
    if not base.exists():
        return []
    glob_pattern = f"**/{pattern}" if recursive else pattern
    matched = sorted(str(p) for p in base.glob(glob_pattern) if p.is_file())
    return matched


def ensure_dir(path: str) -> str:
    """Create directory (and parents) if it does not exist. Returns path."""
    Path(path).mkdir(parents=True, exist_ok=True)
    return path
