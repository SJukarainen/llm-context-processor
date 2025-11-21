"""File operation utilities."""

import os
from pathlib import Path
from typing import Optional


def get_file_extension(file_path: str) -> str:
    """Get file extension in lowercase."""
    return Path(file_path).suffix.lower()


def should_skip_file(file_name: str) -> bool:
    """Determine if a file should be skipped during ingestion."""
    if file_name.startswith(".") or file_name.startswith("~$"):
        return True

    if file_name.lower() in [".ds_store", "thumbs.db", "desktop.ini"]:
        return True

    return False


def create_parallel_output_path(
    source_path: str, input_root: str, output_root: str, preserve_extension: bool = False, output_ext: str = ".md"
) -> str:
    """Create output path maintaining parallel directory structure."""
    try:
        rel_path = os.path.relpath(source_path, input_root)
    except ValueError:
        rel_path = os.path.basename(source_path)

    if '..' in Path(rel_path).parts:
        raise ValueError(f"Path traversal detected in relative path: {rel_path}")

    if preserve_extension:
        output_path = os.path.join(output_root, rel_path)
    else:
        base_name = os.path.splitext(rel_path)[0]
        output_path = os.path.join(output_root, f"{base_name}{output_ext}")

    resolved_output = Path(output_path).resolve()
    resolved_root = Path(output_root).resolve()
    if not str(resolved_output).startswith(str(resolved_root)):
        raise ValueError(f"Output path escapes output root: {output_path}")

    return output_path


def ensure_directory_exists(file_path: str) -> None:
    """Ensure parent directory exists for a file path."""
    directory = os.path.dirname(file_path)
    if directory:
        os.makedirs(directory, exist_ok=True)


def get_safe_filename(filename: str) -> str:
    """Create a safe filename by removing problematic characters."""
    safe_name = "".join(c for c in filename if c.isalnum() or c in "._- ")
    safe_name = safe_name.strip()
    if not safe_name:
        safe_name = "file"
    return safe_name


def get_file_size_mb(file_path: str) -> float:
    """Get file size in megabytes."""
    try:
        size_bytes = os.path.getsize(file_path)
        return size_bytes / (1024 * 1024)
    except (FileNotFoundError, OSError):
        return float('inf')
