"""
Tests for doppel.scanner module
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from doppel.scanner import DuplicateScanner, FileInfo


class TestDuplicateScanner:
    """Test cases for DuplicateScanner class."""

    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory with test files."""
        temp_dir = Path(tempfile.mkdtemp())

        # Create test structure
        # temp_dir/
        #   ├── file1.txt (content: "hello")
        #   ├── file2.txt (content: "world")
        #   ├── subdir1/
        #   │   ├── file1.txt (content: "hello")  # duplicate name, same content
        #   │   └── file3.txt (content: "test")
        #   └── subdir2/
        #       ├── file1.txt (content: "different")  # duplicate name, different content
        #       └── file2.txt (content: "world")     # duplicate name, same content

        # Create files
        (temp_dir / "file1.txt").write_text("hello")
        (temp_dir / "file2.txt").write_text("world")

        (temp_dir / "subdir1").mkdir()
        (temp_dir / "subdir1" / "file1.txt").write_text("hello")
        (temp_dir / "subdir1" / "file3.txt").write_text("test")

        (temp_dir / "subdir2").mkdir()
        (temp_dir / "subdir2" / "file1.txt").write_text("different")
        (temp_dir / "subdir2" / "file2.txt").write_text("world")

        yield temp_dir

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_scanner_initialization(self, temp_dir):
        """Test scanner initialization."""
        scanner = DuplicateScanner(temp_dir)
        assert scanner.root_path == temp_dir.resolve()
        assert scanner.compare_content is False

        scanner_with_content = DuplicateScanner(temp_dir, compare_content=True)
        assert scanner_with_content.compare_content is True

    def test_scan_finds_duplicates(self, temp_dir):
        """Test that scan finds duplicate filenames."""
        scanner = DuplicateScanner(temp_dir)
        duplicates = scanner.scan()

        # Should find file1.txt and file2.txt as duplicates
        assert len(duplicates) == 2
        assert "file1.txt" in duplicates
        assert "file2.txt" in duplicates

        # file1.txt should have 3 copies
        assert len(duplicates["file1.txt"]) == 3

        # file2.txt should have 2 copies
        assert len(duplicates["file2.txt"]) == 2

    def test_scan_with_content_comparison(self, temp_dir):
        """Test scanning with content comparison enabled."""
        scanner = DuplicateScanner(temp_dir, compare_content=True)
        duplicates = scanner.scan()

        # Should still find duplicates by name
        assert "file1.txt" in duplicates
        assert "file2.txt" in duplicates

        # Check that hashes are computed
        for file_list in duplicates.values():
            for file_info in file_list:
                assert file_info.hash is not None
                assert len(file_info.hash) == 32  # MD5 hash length

    def test_group_by_content(self, temp_dir):
        """Test grouping files by content hash."""
        scanner = DuplicateScanner(temp_dir, compare_content=True)
        duplicates = scanner.scan()

        file1_duplicates = duplicates["file1.txt"]
        content_groups = scanner.group_by_content(file1_duplicates)

        # Should have 2 groups (2 different content versions)
        assert len(content_groups) == 2

        # One group should have 2 files (same "hello" content)
        # One group should have 1 file ("different" content)
        group_sizes = [len(group) for group in content_groups.values()]
        assert sorted(group_sizes) == [1, 2]

    def test_nonexistent_directory(self):
        """Test scanner with nonexistent directory."""
        scanner = DuplicateScanner(Path("/nonexistent/path"))

        with pytest.raises(FileNotFoundError):
            scanner.scan()

    def test_file_instead_of_directory(self, temp_dir):
        """Test scanner with file path instead of directory."""
        file_path = temp_dir / "file1.txt"
        scanner = DuplicateScanner(file_path)

        with pytest.raises(NotADirectoryError):
            scanner.scan()

    def test_empty_directory(self):
        """Test scanner with empty directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            scanner = DuplicateScanner(Path(temp_dir))
            duplicates = scanner.scan()

            assert len(duplicates) == 0

    def test_no_duplicates(self):
        """Test scanner with directory containing no duplicates."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files with unique names
            (temp_path / "unique1.txt").write_text("content1")
            (temp_path / "unique2.txt").write_text("content2")
            (temp_path / "unique3.txt").write_text("content3")

            scanner = DuplicateScanner(temp_path)
            duplicates = scanner.scan()

            assert len(duplicates) == 0

    def test_case_insensitive_detection(self):
        """Test that duplicate detection is case-insensitive."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create files with same name but different cases
            (temp_path / "File.txt").write_text("content1")
            (temp_path / "file.txt").write_text("content2")
            (temp_path / "FILE.TXT").write_text("content3")

            scanner = DuplicateScanner(temp_path)
            duplicates = scanner.scan()

            # Should detect all as duplicates of "file.txt"
            assert len(duplicates) == 1
            assert "file.txt" in duplicates
            assert len(duplicates["file.txt"]) == 3


class TestFileInfo:
    """Test cases for FileInfo class."""

    def test_file_info_creation(self):
        """Test FileInfo object creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            test_file = temp_path / "test.txt"
            test_file.write_text("test content")

            stat = test_file.stat()
            file_info = FileInfo(
                path=test_file,
                size=stat.st_size,
                modified=stat.st_mtime
            )

            assert file_info.path == test_file
            assert file_info.size == len("test content")
            assert file_info.modified == stat.st_mtime
            assert file_info.hash is None

    def test_file_info_size_str(self):
        """Test size_str property."""
        file_info = FileInfo(
            path=Path("test.txt"),
            size=1024,
            modified=0
        )

        assert file_info.size_str == "1.0 KB"