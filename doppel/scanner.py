"""
File scanning and duplicate detection functionality
"""

import os
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional
from dataclasses import dataclass
from .utils import get_file_hash, format_size


@dataclass
class FileInfo:
    """Information about a file for duplicate comparison."""
    path: Path
    size: int
    modified: float
    hash: Optional[str] = None

    @property
    def size_str(self) -> str:
        """Human-readable file size."""
        return format_size(self.size)


class DuplicateScanner:
    """Scans directories for duplicate files."""

    def __init__(self, root_path: Path, compare_content: bool = False):
        """
        Initialize scanner.

        Args:
            root_path: Root directory to scan
            compare_content: Whether to compare file content via hashing
        """
        self.root_path = root_path.resolve()
        self.compare_content = compare_content
        self._scanned_files = 0

    def scan(self) -> Dict[str, List[FileInfo]]:
        """
        Scan for duplicate filenames.

        Returns:
            Dictionary mapping filenames to lists of FileInfo objects

        Raises:
            PermissionError: If access is denied to scan directory
            FileNotFoundError: If root path doesn't exist
        """
        if not self.root_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {self.root_path}")

        if not self.root_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {self.root_path}")

        print(f"Scanning directory: {self.root_path}")

        filename_map = defaultdict(list)
        self._scanned_files = 0

        try:
            for filepath in self.root_path.rglob("*"):
                if filepath.is_file():
                    try:
                        file_info = self._create_file_info(filepath)
                        filename = filepath.name.lower()  # Case-insensitive
                        filename_map[filename].append(file_info)
                        self._scanned_files += 1

                        # Progress indicator for large scans
                        if self._scanned_files % 1000 == 0:
                            print(f"Scanned {self._scanned_files} files...")

                    except (OSError, IOError) as e:
                        print(f"Warning: Could not read {filepath}: {e}")
                        continue

        except PermissionError as e:
            raise PermissionError(f"Permission denied scanning directory: {e}")

        print(f"Scan complete. Found {self._scanned_files} files.")

        # Filter to only duplicates and sort by modification time
        duplicates = {}
        for filename, file_list in filename_map.items():
            if len(file_list) > 1:
                # Sort by modification time (newest first)
                file_list.sort(key=lambda f: f.modified, reverse=True)
                duplicates[filename] = file_list

        return duplicates

    def _create_file_info(self, filepath: Path) -> FileInfo:
        """
        Create FileInfo object for a file.

        Args:
            filepath: Path to the file

        Returns:
            FileInfo object with file metadata

        Raises:
            OSError: If file cannot be accessed
        """
        try:
            stat = filepath.stat()
            file_info = FileInfo(
                path=filepath,
                size=stat.st_size,
                modified=stat.st_mtime
            )

            if self.compare_content:
                file_info.hash = get_file_hash(filepath)

            return file_info

        except (OSError, IOError) as e:
            raise OSError(f"Cannot access file {filepath}: {e}")

    def group_by_content(self, file_list: List[FileInfo]) -> Dict[str, List[FileInfo]]:
        """
        Group files by content hash.

        Args:
            file_list: List of FileInfo objects to group

        Returns:
            Dictionary mapping hash values to lists of files
        """
        if not self.compare_content:
            # If not comparing content, compute hashes now
            for file_info in file_list:
                if file_info.hash is None:
                    file_info.hash = get_file_hash(file_info.path)

        hash_groups = defaultdict(list)
        for file_info in file_list:
            if file_info.hash:  # Skip files that couldn't be hashed
                hash_groups[file_info.hash].append(file_info)

        return dict(hash_groups)

    def display_duplicates(self, duplicates: Dict[str, List[FileInfo]]) -> None:
        """
        Display duplicate files in a formatted way.

        Args:
            duplicates: Dictionary of duplicate files from scan()
        """
        if not duplicates:
            print("No duplicate filenames found!")
            return

        total_sets = len(duplicates)
        total_files = sum(len(files) for files in duplicates.values())

        print(f"\nFound {total_sets} sets of duplicate filenames ({total_files} total files):")
        print("=" * 60)

        for filename, file_list in duplicates.items():
            self._display_duplicate_set(filename, file_list)

    def _display_duplicate_set(self, filename: str, file_list: List[FileInfo]) -> None:
        """Display a single set of duplicate files."""
        print(f"\nFilename: {filename}")
        print(f"Found {len(file_list)} copies:")

        for i, file_info in enumerate(file_list, 1):
            print(f"  {i}. {file_info.path}")
            print(f"     Size: {file_info.size_str}, Modified: {file_info.modified:.0f}")

            if file_info.hash:
                print(f"     Hash: {file_info.hash[:8]}...")

        # Show content comparison if enabled
        if self.compare_content:
            hash_groups = self.group_by_content(file_list)

            if len(hash_groups) > 1:
                print(f"     → Content differs between files ({len(hash_groups)} unique versions)")
            elif len(hash_groups) == 1:
                print(f"     → All files have identical content")