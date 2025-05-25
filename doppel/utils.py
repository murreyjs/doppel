"""
Utility functions for doppel package
"""

import hashlib
from pathlib import Path
from typing import Optional


def get_file_hash(filepath: Path) -> str:
    """
    Calculate MD5 hash of a file for content comparison.

    Args:
        filepath: Path to the file

    Returns:
        MD5 hash as hexadecimal string, empty string if error
    """
    hash_md5 = hashlib.md5()
    try:
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except (OSError, IOError):
        return ""


def format_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted size string (e.g., "1.2 MB")
    """
    if size_bytes == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def safe_path_str(path: Path, max_length: Optional[int] = None) -> str:
    """
    Convert Path to string, optionally truncating for display.

    Args:
        path: Path object
        max_length: Maximum length for display (None for no limit)

    Returns:
        String representation of path
    """
    path_str = str(path)
    if max_length and len(path_str) > max_length:
        # Truncate middle of path for readability
        start_len = max_length // 2 - 2
        end_len = max_length - start_len - 3
        return f"{path_str[:start_len]}...{path_str[-end_len:]}"
    return path_str


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Get yes/no confirmation from user.

    Args:
        prompt: Question to ask user
        default: Default value if user just presses enter

    Returns:
        True for yes, False for no
    """
    default_hint = " (Y/n)" if default else " (y/N)"
    response = input(f"{prompt}{default_hint}: ").strip().lower()

    if not response:
        return default

    return response in ('y', 'yes', 'true', '1')


def parse_indices(input_str: str, max_index: int) -> list[int]:
    """
    Parse comma-separated indices from user input.

    Args:
        input_str: User input string (e.g., "1,3,5" or "2")
        max_index: Maximum valid index

    Returns:
        List of valid indices

    Raises:
        ValueError: If input format is invalid
    """
    if not input_str.strip():
        return []

    indices = []
    parts = input_str.split(',')

    for part in parts:
        part = part.strip()
        if not part:
            continue

        try:
            index = int(part)
            if 1 <= index <= max_index:
                indices.append(index)
            else:
                raise ValueError(f"Index {index} out of range (1-{max_index})")
        except ValueError as e:
            if "invalid literal" in str(e):
                raise ValueError(f"'{part}' is not a valid number")
            raise

    return sorted(list(set(indices)))  # Remove duplicates and sort