"""
Tests for doppel.remover module
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
from doppel.remover import InteractiveRemover
from doppel.scanner import DuplicateScanner, FileInfo


class TestInteractiveRemover:
    """Test cases for InteractiveRemover class."""

    @pytest.fixture
    def mock_scanner(self):
        """Create a mock scanner for testing."""
        scanner = MagicMock(spec=DuplicateScanner)
        scanner.compare_content = False
        return scanner

    @pytest.fixture
    def sample_file_info(self):
        """Create sample FileInfo objects for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Create test files
            file1 = temp_path / "test1.txt"
            file2 = temp_path / "test2.txt"
            file1.write_text("content")
            file2.write_text("content")

            stat1 = file1.stat()
            stat2 = file2.stat()

            file_info1 = FileInfo(
                path=file1,
                size=stat1.st_size,
                modified=stat1.st_mtime
            )

            file_info2 = FileInfo(
                path=file2,
                size=stat2.st_size,
                modified=stat2.st_mtime
            )

            yield [file_info1, file_info2]

    def test_remover_initialization(self, mock_scanner):
        """Test remover initialization."""
        remover = InteractiveRemover(mock_scanner)
        assert remover.scanner == mock_scanner
        assert remover.total_removed == 0
        assert remover.total_space_freed == 0

    @patch('builtins.input', return_value='n')
    def test_process_duplicates_cancelled(self, mock_input, mock_scanner):
        """Test that processing can be cancelled."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {"test.txt": []}

        with patch('builtins.print'):
            remover.process_duplicates(duplicates)

        # Should not have removed anything
        assert remover.total_removed == 0

    def test_process_duplicates_empty(self, mock_scanner):
        """Test processing with no duplicates."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {}

        with patch('builtins.print') as mock_print:
            remover.process_duplicates(duplicates)

        mock_print.assert_any_call("No duplicates found - nothing to remove!")

    @patch('builtins.input', side_effect=['y', 'k'])  # Accept processing, then keep files
    def test_process_duplicates_keep_all(self, mock_input, mock_scanner, sample_file_info):
        """Test keeping all files in a duplicate set."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {"test.txt": sample_file_info}

        with patch('builtins.print'):
            remover.process_duplicates(duplicates)

        # Should not have removed anything
        assert remover.total_removed == 0

        # Files should still exist
        for file_info in sample_file_info:
            assert file_info.path.exists()

    @patch('builtins.input', side_effect=['y', 'a'])  # Accept processing, then auto-remove
    def test_process_duplicates_auto_remove(self, mock_input, mock_scanner, sample_file_info):
        """Test auto-removing oldest files."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {"test.txt": sample_file_info}

        with patch('builtins.print'):
            remover.process_duplicates(duplicates)

        # Should have removed one file (keeping the newest)
        assert remover.total_removed == 1

        # At least one file should still exist
        existing_files = [f for f in sample_file_info if f.path.exists()]
        assert len(existing_files) >= 1

    @patch('builtins.input', side_effect=['y', '2', 'y'])  # Accept, select file 2, confirm
    def test_process_duplicates_manual_selection(self, mock_input, mock_scanner, sample_file_info):
        """Test manually selecting files to delete."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {"test.txt": sample_file_info}

        with patch('builtins.print'):
            remover.process_duplicates(duplicates)

        # Should have removed one file
        assert remover.total_removed == 1

        # File 1 should exist, file 2 should be deleted
        assert sample_file_info[0].path.exists()
        assert not sample_file_info[1].path.exists()

    @patch('builtins.input', side_effect=['y', '1,2', 'n', 'k'])  # Select both, cancel, then keep
    def test_process_duplicates_cancel_deletion(self, mock_input, mock_scanner, sample_file_info):
        """Test cancelling deletion after selection."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {"test.txt": sample_file_info}

        with patch('builtins.print'):
            remover.process_duplicates(duplicates)

        # Should not have removed anything due to cancellation
        assert remover.total_removed == 0

        # Both files should still exist
        for file_info in sample_file_info:
            assert file_info.path.exists()

    @patch('builtins.input', side_effect=['y', 'q'])  # Accept processing, then quit
    def test_process_duplicates_quit(self, mock_input, mock_scanner, sample_file_info):
        """Test quitting during processing."""
        remover = InteractiveRemover(mock_scanner)
        duplicates = {"test.txt": sample_file_info}

        with patch('builtins.print'):
            remover.process_duplicates(duplicates)

        # Should not have removed anything
        assert remover.total_removed == 0

    def test_delete_file_success(self, mock_scanner, sample_file_info):
        """Test successful file deletion."""
        remover = InteractiveRemover(mock_scanner)
        file_info = sample_file_info[0]

        result = remover._delete_file(file_info)

        assert result is True
        assert remover.total_removed == 1
        assert remover.total_space_freed == file_info.size
        assert not file_info.path.exists()

    def test_delete_file_failure(self, mock_scanner):
        """Test file deletion failure."""
        remover = InteractiveRemover(mock_scanner)

        # Create FileInfo for nonexistent file
        file_info = FileInfo(
            path=Path("/nonexistent/file.txt"),
            size=100,
            modified=0
        )

        with patch('builtins.print'):
            result = remover._delete_file(file_info)

        assert result is False
        assert remover.total_removed == 0
        assert remover.total_space_freed == 0

    @patch('builtins.input', return_value='1,3,5')
    def test_get_user_choice_indices(self, mock_input, mock_scanner):
        """Test getting user choice with indices."""
        remover = InteractiveRemover(mock_scanner)

        with patch('builtins.print'):
            choice = remover._get_user_choice(5)

        assert choice == [1, 3, 5]

    @patch('builtins.input', return_value='k')
    def test_get_user_choice_keep(self, mock_input, mock_scanner):
        """Test getting user choice to keep files."""
        remover = InteractiveRemover(mock_scanner)

        with patch('builtins.print'):
            choice = remover._get_user_choice(3)

        assert choice == 'keep'

    @patch('builtins.input', return_value='a')
    def test_get_user_choice_auto(self, mock_input, mock_scanner):
        """Test getting user choice for auto-removal."""
        remover = InteractiveRemover(mock_scanner)

        with patch('builtins.print'):
            choice = remover._get_user_choice(3)

        assert choice == 'auto'

    @patch('builtins.input', return_value='q')
    def test_get_user_choice_quit(self, mock_input, mock_scanner):
        """Test getting user choice to quit."""
        remover = InteractiveRemover(mock_scanner)

        with patch('builtins.print'):
            choice = remover._get_user_choice(3)

        assert choice == 'quit'

    @patch('builtins.input', side_effect=['invalid', '6', '1,2'])
    def test_get_user_choice_invalid_input(self, mock_input, mock_scanner):
        """Test handling invalid input in user choice."""
        remover = InteractiveRemover(mock_scanner)

        with patch('builtins.print'):
            choice = remover._get_user_choice(3)

        # Should eventually return valid choice after invalid attempts
        assert choice == [1, 2]

    def test_print_summary(self, mock_scanner):
        """Test printing removal summary."""
        remover = InteractiveRemover(mock_scanner)
        remover.total_removed = 5
        remover.total_space_freed = 1024 * 1024  # 1 MB

        with patch('builtins.print') as mock_print:
            remover._print_summary()

        # Should print summary information
        mock_print.assert_any_call("Files removed: 5")
        mock_print.assert_any_call("Space freed: 1.0 MB")