# Doppel Usage Guide

This guide covers detailed usage of the `doppel` duplicate file finder and eliminator.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Command Line Options](#command-line-options)
- [Interactive Mode](#interactive-mode)
- [Content vs Name Comparison](#content-vs-name-comparison)
- [Safety Features](#safety-features)
- [Common Workflows](#common-workflows)
- [Troubleshooting](#troubleshooting)

## Basic Usage

### Simple Duplicate Finding

```bash
# Search current directory
doppel

# Search specific directory
doppel /path/to/directory

# Search with verbose output
doppel --verbose ~/Downloads
```

### Preview Mode (Dry Run)

Use `--dry-run` to see what duplicates exist without any risk of deletion:

```bash
# Preview duplicates in Documents folder
doppel --dry-run ~/Documents

# Preview with content comparison
doppel --dry-run --content ~/Photos
```

## Command Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `--content` | | Compare file content using MD5 hashes |
| `--dry-run` | | Show duplicates without interactive removal |
| `--verbose` | `-v` | Show detailed progress information |
| `--version` | | Show version information |
| `--help` | `-h` | Show help message |

### Examples

```bash
# Find duplicates by name only (fast)
doppel ~/Downloads

# Find duplicates by content (slower but more accurate)
doppel --content ~/Downloads

# Verbose mode with content comparison
doppel --verbose --content ~/Documents

# Preview only
doppel --dry-run --content .
```

## Interactive Mode

When duplicates are found (and not using `--dry-run`), doppel enters interactive mode for each set of duplicates.

### Available Actions

For each duplicate set, you can choose:

1. **Manual Selection** - Enter numbers to delete specific files
2. **Auto Mode** - Keep newest, delete older files
3. **Keep All** - Skip this duplicate set
4. **Quit** - Exit the program

### Manual Selection Examples

```
Options:
  Enter numbers (e.g., '2,3') to delete those files
  'k' to keep all (skip)
  'a' to auto-keep newest (delete others)
  'q' to quit
Choice: 2,3
```

This would delete files #2 and #3 from the displayed list.

### Auto Mode

```
Choice: a
```

This automatically keeps the newest file (by modification date) and deletes all others.

## Content vs Name Comparison

### Name Comparison (Default)

- **Fast** - Only compares filenames
- **Good for** - Finding obvious duplicates like "photo.jpg" in multiple folders
- **Limitations** - Won't detect renamed files with identical content

```bash
doppel ~/Downloads
```

### Content Comparison (`--content`)

- **Thorough** - Compares actual file content using MD5 hashes
- **Good for** - Finding true duplicates regardless of filename
- **Slower** - Must read and hash every file
- **Detects** - Files with same content but different names

```bash
doppel --content ~/Downloads
```

#### Content Comparison Output

When using `--content`, doppel shows additional information:

```
Filename: document.pdf
Found 3 copies:
  1. /home/user/document.pdf
     Size: 2.1 MB, Modified: 1640995200
  2. /home/user/backup/document.pdf
     Size: 2.1 MB, Modified: 1640995100
  3. /home/user/old/document_old.pdf
     Size: 1.8 MB, Modified: 1640994000

⚠️  Files have different content! (2 unique versions)
     Group 1 (hash 1a2b3c4d...): files 1, 2
     Group 2 (hash 5e6f7g8h...): files 3
```

This tells you that files 1 and 2 have identical content, while file 3 has different content.

## Safety Features

### Confirmation Prompts

Doppel always asks for confirmation before deleting files:

```
Will delete 2 file(s):
  /home/user/Downloads/duplicate1.txt (1.2 KB)
  /home/user/Downloads/backup/duplicate1.txt (1.2 KB)
Total space to free: 2.4 KB
Confirm deletion? (y/N): 
```

### Dry Run Mode

Use `--dry-run` to preview results without any risk:

```bash
doppel --dry-run ~/Downloads
```

This shows you what duplicates exist and how many files could potentially be removed.

### Error Handling

- **Permission errors** - Gracefully handles files you can't read or delete
- **Missing files** - Continues if files are moved/deleted during operation
- **Invalid paths** - Validates directory exists before starting

## Common Workflows

### Cleaning Download Folder

```bash
# Preview what's duplicated
doppel --dry-run ~/Downloads

# Clean up name duplicates interactively
doppel ~/Downloads

# More thorough content-based cleanup
doppel --content ~/Downloads
```

### Photo Library Cleanup

```bash
# Find duplicate photos by content (recommended for photos)
doppel --content ~/Pictures

# With verbose output to see progress
doppel --verbose --content ~/Pictures
```

### Document Folder Maintenance

```bash
# Quick name-based duplicate check
doppel ~/Documents

# Thorough content check for important documents
doppel --content ~/Documents
```

### Large Archive Cleanup

```bash
# First, get an overview
doppel --dry-run /large/archive

# Clean up interactively with content comparison
doppel --verbose --content /large/archive
```

## Troubleshooting

### Permission Denied Errors

If you see permission errors:

```bash
# Run with verbose mode to see details
doppel --verbose /restricted/path

# Or change to accessible directory
cd ~/Downloads && doppel
```

### Large File Collections

For very large file collections:

```bash
# Use verbose mode to see progress
doppel --verbose --content /huge/directory

# Consider breaking into smaller chunks
doppel /huge/directory/subfolder1
doppel /huge/directory/subfolder2
```

### Slow Performance

- **Name comparison** is much faster than content comparison
- **Large files** take longer to hash - consider name comparison first
- **Network drives** are slower - copy locally if possible

### Memory Usage

Doppel is designed to be memory-efficient:
- Only keeps file metadata in memory
- Processes one duplicate set at a time
- No issues with large file collections

### Interrupted Operations

If doppel is interrupted (Ctrl+C):
- No files are left in an inconsistent state
- Any deletions already confirmed are completed
- You can safely restart the operation

## Advanced Tips

### Combining with Find

```bash
# First use find to identify large duplicate candidates
find . -type f -size +10M -name "*.mp4" | sort

# Then run doppel on specific directories
doppel --content ./videos
```

### Scripting Integration

While doppel is designed for interactive use, you can integrate it into scripts:

```bash
#!/bin/bash
# Automated cleanup script

# First, show what would be cleaned
echo "=== Dry run preview ==="
doppel --dry-run ~/Downloads

# Ask user if they want to proceed
read -p "Proceed with interactive cleanup? (y/N): " answer
if [[ $answer =~ ^[Yy]$ ]]; then
    doppel ~/Downloads
fi
```

### Regular Maintenance

Set up regular duplicate checking:

```bash
# Weekly cleanup cron job (preview only)
0 9 * * 1 /usr/local/bin/doppel --dry-run ~/Downloads > ~/duplicate-report.txt

# Monthly interactive cleanup reminder
0 9 1 * * echo "Time for monthly duplicate cleanup!" | mail -s "Cleanup Reminder" user@domain.com
```

## Exit Codes

Doppel returns different exit codes for different scenarios:

- `0` - Success (normal completion)
- `1` - General error or user interruption
- `2` - Permission error
- `3` - Other error (file system, etc.)

This allows for proper error handling in scripts:

```bash
#!/bin/bash
doppel --dry-run /path/to/check
case $? in
    0) echo "Scan completed successfully" ;;
    1) echo "Scan was interrupted or failed" ;;
    2) echo "Permission denied" ;;
    *) echo "Unexpected error occurred" ;;
esac
```