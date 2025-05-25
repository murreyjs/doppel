"""
Tests for doppel.utils module
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from doppel.utils import (
    get_file_hash,
    format_size,
    safe_path_str,
    confirm_action,
    parse_indices
)


class TestGetFileHash:
    """Test cases for get_file_hash function."""

    def test_hash_calculation(self):
        """Test MD5 hash calculation for a file."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            hash_result = get_file_hash(temp_path)

            # MD5 hash should be 32 characters
            assert len(hash_result) == 32
            assert hash_result.isalnum()

            # Same content should produce same hash
            hash_result2 = get_file_hash(temp_path)
            assert hash_result == hash_result2
        finally:
            temp_path.unlink()

    def test_hash_different_content(self):
        """Test that different content produces different hashes."""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f1:
            f1.write("content1")
            temp_path1 = Path(f1.name)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f2:
            f2.write("content2")
            temp_path2 = Path(f2.name)

        try:
            hash1 = get_file_hash(temp_path1)
            hash2 = get_file_hash(temp_path2)

            assert hash1 != hash2
        finally:
            temp_path1.unlink()
            temp_path2.unlink()

    def test_hash_nonexistent_file(self):
        """Test hash calculation for nonexistent file."""
        hash_result = get_file_hash(Path("/nonexistent/file.txt"))
        assert hash_result == ""

    def test_hash_empty_file(self):
        """Test hash calculation for empty file."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_path = Path(f.name)

        try:
            hash_result = get_file_hash(temp_path)

            # MD5 of empty file is d41d8cd98f00b204e9800998ecf8427e
            assert hash_result == "d41d8cd98f00b204e9800998ecf8427e"
        finally:
            temp_path.unlink()


class TestFormatSize:
    """Test cases for format_size function."""

    def test_bytes_formatting(self):
        """Test formatting of sizes in bytes."""
        assert format_size(0) == "0 B"
        assert format_size(512) == "512.0 B"
        assert format_size(1023) == "1023.0 B"

    def test_kilobytes_formatting(self):
        """Test formatting of sizes in kilobytes."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(1536) == "1.5 KB"
        assert format_size(1024 * 1023) == "1023.0 KB"

    def test_megabytes_formatting(self):
        """Test formatting of sizes in megabytes."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(1024 * 1024 * 2.5) == "2.5 MB"

    def test_gigabytes_formatting(self):
        """Test formatting of sizes in gigabytes."""
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"
        assert format_size(1024 * 1024 * 1024 * 1.5) == "1.5 GB"

    def test_terabytes_formatting(self):
        """Test formatting of sizes in terabytes."""
        assert format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"


class TestSafePathStr:
    """Test cases for safe_path_str function."""

    def test_short_path(self):
        """Test that short paths are not truncated."""
        path = Path("/short/path.txt")
        result = safe_path_str(path, max_length=50)
        assert result == str(path)

    def test_long_path_truncation(self):
        """Test that long paths are truncated properly."""
        long_path = Path("/very/long/path/to/some/deeply/nested/directory/with/file.txt")
        result = safe_path_str(long_path, max_length=30)

        assert len(result) <= 30
        assert "..." in result
        assert result.startswith("/very/long")
        assert result.endswith("file.txt")

    def test_no_max_length(self):
        """Test that paths are not truncated when max_length is None."""
        long_path = Path("/very/long/path/to/some/deeply/nested/directory/with/file.txt")
        result = safe_path_str(long_path, max_length=None)
        assert result == str(long_path)


class TestConfirmAction:
    """Test cases for confirm_action function."""

    @patch('builtins.input', return_value='y')
    def test_confirm_yes(self, mock_input):
        """Test confirmation with 'y' response."""
        result = confirm_action("Continue?")
        assert result is True

    @patch('builtins.input', return_value='n')
    def test_confirm_no(self, mock_input):
        """Test confirmation with 'n' response."""
        result = confirm_action("Continue?")
        assert result is False

    @patch('builtins.input', return_value='')
    def test_confirm_default_false(self, mock_input):
        """Test confirmation with default False."""
        result = confirm_action("Continue?", default=False)
        assert result is False

    @patch('builtins.input', return_value='')
    def test_confirm_default_true(self, mock_input):
        """Test confirmation with default True."""
        result = confirm_action("Continue?", default=True)
        assert result is True

    @patch('builtins.input', return_value='yes')
    def test_confirm_yes_variations(self, mock_input):
        """Test confirmation with various 'yes' responses."""
        result = confirm_action("Continue?")
        assert result is True


class TestParseIndices:
    """Test cases for parse_indices function."""

    def test_single_index(self):
        """Test parsing single index."""
        result = parse_indices("3", max_index=5)
        assert result == [3]

    def test_multiple_indices(self):
        """Test parsing multiple indices."""
        result = parse_indices("1,3,5", max_index=5)
        assert result == [1, 3, 5]

    def test_indices_with_spaces(self):
        """Test parsing indices with spaces."""
        result = parse_indices(" 1 , 3 , 5 ", max_index=5)
        assert result == [1, 3, 5]

    def test_duplicate_indices(self):
        """Test that duplicate indices are removed."""
        result = parse_indices("1,3,1,5", max_index=5)
        assert result == [1, 3, 5]

    def test_out_of_range_index(self):
        """Test that out of range indices raise ValueError."""
        with pytest.raises(ValueError, match="Index 6 out of range"):
            parse_indices("1,6", max_index=5)

    def test_invalid_number(self):
        """Test that invalid numbers raise ValueError."""
        with pytest.raises(ValueError, match="'abc' is not a valid number"):
            parse_indices("1,abc,3", max_index=5)

    def test_empty_input(self):
        """Test that empty input returns empty list."""
        result = parse_indices("", max_index=5)
        assert result == []

        result = parse_indices("   ", max_index=5)
        assert result == []

    def test_zero_index(self):
        """Test that zero index raises ValueError."""
        with pytest.raises(ValueError, match="Index 0 out of range"):
            parse_indices("0,1,2", max_index=5)