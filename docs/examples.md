# Doppel Examples

This document provides real-world examples of using doppel to clean up various types of duplicate files.

## Table of Contents

- [Basic Examples](#basic-examples)
- [Photo Management](#photo-management)
- [Document Cleanup](#document-cleanup)
- [Downloads Organization](#downloads-organization)
- [Development Projects](#development-projects)
- [System Administration](#system-administration)

## Basic Examples

### Example 1: Simple Duplicate Check

**Scenario**: Check current directory for duplicate filenames

```bash
$ doppel

Scanning directory: /home/user/workspace
Scan complete. Found 127 files.

Found 2 sets of duplicate filenames (6 total files):
============================================================

Filename: readme.txt
Found 3 copies:
  1. /home/user/workspace/readme.txt
     Size: 1.2 KB, Modified: 1640995200
  2. /home/user/workspace/backup/readme.txt
     Size: 1.2 KB, Modified: 1640995100
  3. /home/user/workspace/old/readme.txt
     Size: 0.8 KB, Modified: 1640994000

Ready to process 2 sets of duplicates.
Proceed with interactive removal? (y/N): y

Processing duplicates for: readme.txt (1/2)
============================================================

Options:
  Enter numbers (e.g., '2,3') to delete those files
  'k' to keep all (skip)
  'a' to auto-keep newest (delete others)
  'q' to quit
Choice: a

Keeping newest: /home/user/workspace/readme.txt
Deleted: /home/user/workspace/backup/readme.txt
Deleted: /home/user/workspace/old/readme.txt

============================================================
REMOVAL COMPLETE
============================================================
Files removed: 2
Space freed: 2.0 KB
Successfully cleaned up 2 duplicate files!
```

### Example 2: Content-Based Detection

**Scenario**: Find files with identical content regardless of name

```bash
$ doppel --content ~/Downloads

Scanning directory: /home/user/Downloads
Scan complete. Found 89 files.

Found 1 sets of duplicate filenames (3 total files):
============================================================

Filename: document.pdf
Found 3 copies:
  1. /home/user/Downloads/document.pdf
     Size: 2.1 MB, Modified: 1640995200
     Hash: 1a2b3c4d...
  2. /home/user/Downloads/report_final.pdf
     Size: 2.1 MB, Modified: 1640995100
     Hash: 1a2b3c4d...
  3. /home/user/Downloads/presentation.pdf
     Size: 1.8 MB, Modified: 1640994000
     Hash: 5e6f7g8h...

⚠️  Files have different content! (2 unique versions)
     Group 1 (hash 1a2b3c4d...): files 1, 2
     Group 2 (hash 5e6f7g8h...): files 3
```

## Photo Management

### Example 3: Photo Library Cleanup

**Scenario**: Clean up a photo library with many duplicates from different devices

```bash
$ doppel --content --verbose ~/Pictures

doppel 1.0.0 - Duplicate file eliminator
==================================================
Scanning mode: Content comparison
Scanning directory: /home/user/Pictures
Scanned 1000 files...
Scanned 2000 files...
Scan complete. Found 2,847 files.

Found 15 sets of duplicate filenames (45 total files):
============================================================

Filename: img_1234.jpg
Found 4 copies:
  1. /home/user/Pictures/2023/vacation/img_1234.jpg
     Size: 3.2 MB, Modified: 1640995200
  2. /home/user/Pictures/phone_backup/img_1234.jpg
     Size: 3.2 MB, Modified: 1640995150
  3. /home/user/Pictures/camera_import/img_1234.jpg
     Size: 3.2 MB, Modified: 1640995100
  4. /home/user/Pictures/duplicates/img_1234.jpg
     Size: 3.2 MB, Modified: 1640995050

✓ All files have identical content

Ready to process 15 sets of duplicates.
Proceed with interactive removal? (y/N): y

Processing duplicates for: img_1234.jpg (1/15)
============================================================

Options:
  Enter numbers (e.g., '2,3') to delete those files
  'k' to keep all (skip)
  'a' to auto-keep newest (delete others)
  'q' to quit
Choice: 2,3,4

Will delete 3 file(s):
  /home/user/Pictures/phone_backup/img_1234.jpg (3.2 MB)
  /home/user/Pictures/camera_import/img_1234.jpg (3.2 MB)
  /home/user/Pictures/duplicates/img_1234.jpg (3.2 MB)
Total space to free: 9.6 MB
Confirm deletion? (y/N): y

Deleted: /home/user/Pictures/phone_backup/img_1234.jpg
Deleted: /home/user/Pictures/camera_import/img_1234.jpg
Deleted: /home/user/Pictures/duplicates/img_1234.jpg
Successfully deleted 3 file(s).

[... continues for remaining duplicates ...]

============================================================
REMOVAL COMPLETE
============================================================
Files removed: 28
Space freed: 245.7 MB
Successfully cleaned up 28 duplicate files!
```

### Example 4: Dry Run for Photo Assessment

**Scenario**: Assess how many duplicates exist before cleanup

```bash
$ doppel --dry-run --content ~/Pictures/2023

Scanning directory: /home/user/Pictures/2023
Scan complete. Found 1,234 files.

Found 8 sets of duplicate filenames (24 total files):
============================================================

Filename: sunset.jpg
Found 3 copies:
  1. /home/user/Pictures/2023/hawaii/sunset.jpg
     Size: 4.1 MB, Modified: 1640995200
     Hash: abc123...
  2. /home/user/Pictures/2023/backup/sunset.jpg
     Size: 4.1 MB, Modified: 1640995100
     Hash: abc123...
  3. /home/user/Pictures/2023/originals/sunset.jpg
     Size: 4.1 MB, Modified: 1640995000
     Hash: abc123...

✓ All files have identical content

[... more duplicate sets ...]

Dry run complete. Found 8 sets of duplicates.
Potential files to remove: 16
```

## Document Cleanup

### Example 5: Document Version Control

**Scenario**: Clean up a Documents folder with many versions of the same files

```bash
$ doppel ~/Documents/Projects

Found 3 sets of duplicate filenames (9 total files):
============================================================

Filename: proposal.docx
Found 3 copies:
  1. /home/user/Documents/Projects/proposal.docx
     Size: 156.7 KB, Modified: 1640995200
  2. /home/user/Documents/Projects/backup/proposal.docx
     Size: 156.7 KB, Modified: 1640995100
  3. /home/user/Documents/Projects/old_versions/proposal.docx
     Size: 142.3 KB, Modified: 1640994000

Ready to process 3 sets of duplicates.
Proceed with interactive removal? (y/N): y

Processing duplicates for: proposal.docx (1/3)
============================================================

Options:
  Enter numbers (e.g., '2,3') to delete those files
  'k' to keep all (skip)
  'a' to auto-keep newest (delete others)
  'q' to quit
Choice: 3

Will delete 1 file(s):
  /home/user/Documents/Projects/old_versions/proposal.docx (142.3 KB)
Total space to free: 142.3 KB
Confirm deletion? (y/N): y

Deleted: /home/user/Documents/Projects/old_versions/proposal.docx
Successfully deleted 1 file(s).

Processing duplicates for: budget.xlsx (2/3)
============================================================

Found 2 copies:
  1. /home/user/Documents/Projects/budget.xlsx
     Size: 23.4 KB, Modified: 1640995300
  2. /home/user/Documents/Projects/archive/budget.xlsx
     Size: 23.4 KB, Modified: 1640995300

Choice: a

Keeping newest: /home/user/Documents/Projects/budget.xlsx
Deleted: /home/user/Documents/Projects/archive/budget.xlsx
```

## Downloads Organization

### Example 6: Downloads Folder Cleanup

**Scenario**: Regular cleanup of Downloads folder

```bash
$ doppel --content ~/Downloads

Found 7 sets of duplicate filenames (18 total files):
============================================================

Filename: installer.dmg
Found 4 copies:
  1. /home/user/Downloads/installer.dmg
     Size: 89.2 MB, Modified: 1640995400
  2. /home/user/Downloads/installer (1).dmg
     Size: 89.2 MB, Modified: 1640995300
  3. /home/user/Downloads/installer (2).dmg
     Size: 89.2 MB, Modified: 1640995200
  4. /home/user/Downloads/old/installer.dmg
     Size: 89.2 MB, Modified: 1640995100

✓ All files have identical content

Choice: 2,3,4

Will delete 3 file(s):
  /home/user/Downloads/installer (1).dmg (89.2 MB)
  /home/user/Downloads/installer (2).dmg (89.2 MB)
  /home/user/Downloads/old/installer.dmg (89.2 MB)
Total space to free: 267.6 MB
Confirm deletion? (y/N): y

[Files deleted successfully]

============================================================
REMOVAL COMPLETE
============================================================
Files removed: 12
Space freed: 1.2 GB
Successfully cleaned up 12 duplicate files!
```

## Development Projects

### Example 7: Code Project Cleanup

**Scenario**: Clean up duplicate configuration files in development projects

```bash
$ doppel ~/workspace --dry-run

Found 4 sets of duplicate filenames (12 total files):
============================================================

Filename: .gitignore
Found 4 copies:
  1. /home/user/workspace/project1/.gitignore
     Size: 1.2 KB, Modified: 1640995200
  2. /home/user/workspace/project2/.gitignore
     Size: 1.2 KB, Modified: 1640995100
  3. /home/user/workspace/backup/.gitignore
     Size: 1.2 KB, Modified: 1640995000
  4. /home/user/workspace/templates/.gitignore
     Size: 0.8 KB, Modified: 1640994000

Filename: package.json
Found 3 copies:
  1. /home/user/workspace/node_app/package.json
     Size: 2.3 KB, Modified: 1640995300
  2. /home/user/workspace/old_node_app/package.json
     Size: 1.9 KB, Modified: 1640994500
  3. /home/user/workspace/backup/package.json
     Size: 2.3 KB, Modified: 1640995300

Dry run complete. Found 4 sets of duplicates.
Potential files to remove: 8
```

### Example 8: Node.js Project Dependencies

**Scenario**: Clean up duplicate node_modules after project copying

```bash
$ doppel --content ~/projects/node

# Note: This would find duplicate package files, but you'd typically
# want to clean up entire node_modules directories manually
# Doppel helps identify which projects have identical dependencies

Found 156 sets of duplicate filenames (1,247 total files):
============================================================

[Many npm package files would be listed...]

# In this case, you might want to:
# 1. Use dry-run to assess the situation
# 2. Manually remove old project copies
# 3. Run npm install to regenerate node_modules as needed
```

## System Administration

### Example 9: Log File Cleanup

**Scenario**: Clean up duplicate log files

```bash
$ doppel /var/log/backup --dry-run

Found 12 sets of duplicate filenames (48 total files):
============================================================

Filename: system.log
Found 8 copies:
  1. /var/log/backup/2023-01/system.log
     Size: 12.3 MB, Modified: 1640995200
  2. /var/log/backup/2023-02/system.log
     Size: 12.3 MB, Modified: 1640995100
  [... more log files ...]

# Use content comparison to identify truly identical logs
$ doppel --content /var/log/backup
```

### Example 10: Configuration Backup Cleanup

**Scenario**: Clean up duplicate configuration backups

```bash
$ doppel --content /etc/backup

Found 6 sets of duplicate filenames (18 total files):
============================================================

Filename: nginx.conf
Found 3 copies:
  1. /etc/backup/2023-12-01/nginx.conf
     Size: 4.2 KB, Modified: 1640995200
  2. /etc/backup/2023-11-01/nginx.conf
     Size: 4.2 KB, Modified: 1640995100
  3. /etc/backup/2023-10-01/nginx.conf
     Size: 3.8 KB, Modified: 1640994000

⚠️  Files have different content! (2 unique versions)
     Group 1 (hash 1a2b3c4d...): files 1, 2
     Group 2 (hash 5e6f7g8h...): files 3

# Keep both unique versions, remove one duplicate
Choice: 2

Will delete 1 file(s):
  /etc/backup/2023-11-01/nginx.conf (4.2 KB)
Confirm deletion? (y/N): y
```

## Tips from Examples

1. **Use dry-run first** - Always assess the situation before making changes
2. **Content comparison for important files** - Use `--content` for photos, documents, and critical files
3. **Auto-mode for obvious cases** - Use 'a' when you clearly want to keep the newest
4. **Manual selection for mixed content** - Review carefully when files have different content
5. **Verbose mode for large operations** - Use `--verbose` to track progress on big scans
6. **Regular maintenance** - Set up periodic duplicate checks for active directories