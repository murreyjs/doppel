"""
Interactive duplicate file removal functionality
"""

from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
from .scanner import FileInfo, DuplicateScanner
from .utils import confirm_action, parse_indices


class InteractiveRemover:
    """Handles interactive removal of duplicate files."""

    def __init__(self, scanner: DuplicateScanner):
        """
        Initialize remover.

        Args:
            scanner: DuplicateScanner instance used for content comparison
        """
        self.scanner = scanner
        self.total_removed = 0
        self.total_space_freed = 0

    def process_duplicates_auto(self, duplicates: Dict[str, List[FileInfo]]) -> None:
        """
        Process all duplicate sets automatically (keep newest, delete others).

        Args:
            duplicates: Dictionary of duplicate files from scanner
        """
        if not duplicates:
            print("No duplicates found - nothing to remove!")
            return

        total_sets = len(duplicates)
        print(f"\nProcessing {total_sets} sets of duplicates automatically...")
        print("=" * 60)

        current_set = 0
        for filename, file_list in duplicates.items():
            current_set += 1

            if len(file_list) <= 1:
                continue

            print(f"\nProcessing: {filename} ({current_set}/{total_sets})")
            print(f"Found {len(file_list)} copies - keeping newest, removing {len(file_list) - 1}")

            # Auto-remove oldest files (keep first in sorted list)
            self._auto_remove_oldest(file_list)

        self._print_summary()

    def process_duplicates(self, duplicates: Dict[str, List[FileInfo]]) -> None:
        """
        Process all duplicate sets interactively.

        Args:
            duplicates: Dictionary of duplicate files from scanner
        """
        if not duplicates:
            print("No duplicates found - nothing to remove!")
            return

        total_sets = len(duplicates)
        print(f"\nReady to process {total_sets} sets of duplicates.")

        if not confirm_action("Proceed with interactive removal?", default=False):
            print("Cancelled.")
            return

        current_set = 0
        for filename, file_list in duplicates.items():
            current_set += 1
            print(f"\n{'='*60}")
            print(f"Processing duplicates for: {filename} ({current_set}/{total_sets})")
            print(f"{'='*60}")

            if len(file_list) <= 1:
                print("Only one file found, skipping...")
                continue

            self._process_duplicate_set(filename, file_list)

        self._print_summary()

    def _process_duplicate_set(self, filename: str, file_list: List[FileInfo]) -> None:
        """
        Process a single set of duplicate files.

        Args:
            filename: The duplicate filename
            file_list: List of FileInfo objects for this filename
        """
        # Display files with details
        print(f"\nFound {len(file_list)} copies:")
        for i, file_info in enumerate(file_list, 1):
            print(f"  {i}. {file_info.path}")
            print(f"     Size: {file_info.size_str}")

        # Show content analysis if enabled
        content_groups = None
        if self.scanner.compare_content:
            content_groups = self.scanner.group_by_content(file_list)
            self._display_content_analysis(content_groups)

        # Interactive processing loop
        while True:
            choice = self._get_user_choice(len(file_list))

            if choice == 'quit':
                print(f"Exiting. Removed {self.total_removed} files total.")
                return
            elif choice == 'keep':
                print("Keeping all files.")
                break
            elif choice == 'auto':
                self._auto_remove_oldest(file_list)
                break
            elif isinstance(choice, list):
                if self._confirm_and_delete(choice, file_list):
                    break
            # If we get here, there was an error and we should ask again

    def _display_content_analysis(self, content_groups: Dict[str, List[FileInfo]]) -> None:
        """Display content analysis for duplicate files."""
        if len(content_groups) > 1:
            print(f"\n⚠️  Files have different content! ({len(content_groups)} unique versions)")
            for i, (hash_val, group) in enumerate(content_groups.items(), 1):
                indices = []
                for file_info in group:
                    # Find the index of this file in the display
                    for j, displayed_file in enumerate(file_list, 1):
                        if displayed_file.path == file_info.path:
                            indices.append(str(j))
                            break
                print(f"     Group {i} (hash {hash_val[:8]}...): files {', '.join(indices)}")
        else:
            print(f"\n✓ All files have identical content")

    def _get_user_choice(self, num_files: int):
        """
        Get user's choice for handling duplicates.

        Args:
            num_files: Number of files in this duplicate set

        Returns:
            'quit', 'keep', 'auto', or list of indices to delete
        """
        print(f"\nOptions:")
        print(f"  Enter numbers (e.g., '2,3') to delete those files")
        print(f"  'k' to keep all (skip)")
        print(f"  'a' to auto-keep newest (delete others)")
        print(f"  'q' to quit")

        while True:
            choice = input("Choice: ").strip().lower()

            if choice == 'q':
                return 'quit'
            elif choice == 'k':
                return 'keep'
            elif choice == 'a':
                return 'auto'
            else:
                try:
                    indices = parse_indices(choice, num_files)
                    if indices:
                        return indices
                    else:
                        print("No valid indices provided. Please try again.")
                except ValueError as e:
                    print(f"Error: {e}. Please try again.")

    def _auto_remove_oldest(self, file_list: List[FileInfo]) -> None:
        """
        Automatically remove all but the newest file.

        Args:
            file_list: List of FileInfo objects (should be sorted by modification time)
        """
        if len(file_list) <= 1:
            return

        # Keep the first (newest), delete the rest
        to_keep = file_list[0]
        to_delete = file_list[1:]

        print(f"Keeping newest: {to_keep.path}")

        for file_info in to_delete:
            if self._delete_file(file_info):
                print(f"Deleted: {file_info.path}")

    def _confirm_and_delete(self, indices: List[int], file_list: List[FileInfo]) -> bool:
        """
        Confirm and delete selected files.

        Args:
            indices: List of 1-based indices to delete
            file_list: List of all FileInfo objects

        Returns:
            True if deletion completed (or cancelled), False to retry
        """
        # Convert to 0-based indices
        files_to_delete = [file_list[i-1] for i in indices]

        print(f"\nWill delete {len(files_to_delete)} file(s):")
        total_size = 0
        for file_info in files_to_delete:
            print(f"  {file_info.path} ({file_info.size_str})")
            total_size += file_info.size

        if total_size > 0:
            from .utils import format_size
            print(f"Total space to free: {format_size(total_size)}")

        if not confirm_action("Confirm deletion?", default=False):
            print("Deletion cancelled.")
            return False  # Don't break, let user try again

        # Perform deletions
        deleted_count = 0
        for file_info in files_to_delete:
            if self._delete_file(file_info):
                print(f"Deleted: {file_info.path}")
                deleted_count += 1

        if deleted_count > 0:
            print(f"Successfully deleted {deleted_count} file(s).")

        return True  # Break from the choice loop

    def _delete_file(self, file_info: FileInfo) -> bool:
        """
        Delete a single file.

        Args:
            file_info: FileInfo object for file to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            file_info.path.unlink()
            self.total_removed += 1
            self.total_space_freed += file_info.size
            return True
        except OSError as e:
            print(f"Error deleting {file_info.path}: {e}")
            return False

    def _print_summary(self) -> None:
        """Print final summary of removal operation."""
        print(f"\n{'='*60}")
        print("REMOVAL COMPLETE")
        print(f"{'='*60}")
        print(f"Files removed: {self.total_removed}")

        if self.total_space_freed > 0:
            from .utils import format_size
            print(f"Space freed: {format_size(self.total_space_freed)}")

        if self.total_removed == 0:
            print("No files were removed.")
        else:
            print(f"Successfully cleaned up {self.total_removed} duplicate files!")