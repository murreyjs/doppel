#!/usr/bin/env python3
"""
Command-line interface for doppel
"""

import sys
import argparse
from pathlib import Path
from . import __version__
from .scanner import DuplicateScanner
from .remover import InteractiveRemover
from .utils import confirm_action


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser."""
    parser = argparse.ArgumentParser(
        prog="doppel",
        description="Find and eliminate duplicate filenames in a directory tree",
        epilog="Examples:\n"
               "  doppel                    # Search current directory\n"
               "  doppel /path/to/folder    # Search specific directory\n"
               "  doppel --content ~/docs   # Compare file content too\n"
               "  doppel --dry-run .        # Preview without deletion",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "directory",
        nargs="?",
        default=".",
        help="Directory to search (default: current directory)"
    )

    parser.add_argument(
        "--content",
        action="store_true",
        help="Compare file content, not just names (slower but more accurate)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show duplicates without interactive removal"
    )

    parser.add_argument(
        "--auto",
        action="store_true",
        help="Automatically keep newest file from each duplicate set (no prompts)"
    )

    parser.add_argument(
        "--version",
        action="version",
        version=f"doppel {__version__}"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed progress information"
    )

    return parser


def validate_directory(directory_path: str) -> Path:
    """
    Validate and return directory path.

    Args:
        directory_path: Path string from command line

    Returns:
        Validated Path object

    Raises:
        SystemExit: If directory is invalid
    """
    path = Path(directory_path).resolve()

    if not path.exists():
        print(f"Error: Directory '{directory_path}' does not exist.", file=sys.stderr)
        sys.exit(1)

    if not path.is_dir():
        print(f"Error: '{directory_path}' is not a directory.", file=sys.stderr)
        sys.exit(1)

    return path


def main():
    """Main entry point for doppel CLI."""
    parser = create_parser()
    args = parser.parse_args()

    # Print banner
    if args.verbose:
        print(f"doppel {__version__} - Duplicate file eliminator")
        print("=" * 50)

    # Validate directory
    try:
        root_path = validate_directory(args.directory)
    except KeyboardInterrupt:
        print("\nInterrupted by user.")
        sys.exit(1)

    # Create scanner
    scanner = DuplicateScanner(root_path, compare_content=args.content)

    try:
        # Scan for duplicates
        if args.verbose:
            print(f"Scanning mode: {'Content comparison' if args.content else 'Name comparison'}")

        duplicates = scanner.scan()

        # Display results
        scanner.display_duplicates(duplicates)

        if args.dry_run:
            print(f"\nDry run complete. Found {len(duplicates)} sets of duplicates.")
            if duplicates:
                total_files = sum(len(files) for files in duplicates.values())
                potential_removals = total_files - len(duplicates)  # Keep one from each set
                print(f"Potential files to remove: {potential_removals}")
            return

        # Interactive removal
        if duplicates:
            remover = InteractiveRemover(scanner)

            if args.auto:
                print(f"\nAuto mode: Will keep newest file from each duplicate set.")
                if not confirm_action("Proceed with automatic removal?", default=False):
                    print("Cancelled.")
                    return

                remover.process_duplicates_auto(duplicates)
            else:
                remover.process_duplicates(duplicates)
        else:
            print("No duplicates found - nothing to remove!")

    except KeyboardInterrupt:
        print("\n\nOperation interrupted by user.")
        sys.exit(1)
    except PermissionError as e:
        print(f"Permission error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        if args.verbose:
            import traceback
            traceback.print_exc()
        else:
            print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)


if __name__ == "__main__":
    main()