"""
Tests for doppel.cli module
"""

import pytest
import tempfile
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from doppel.cli import create_parser, validate_directory, main


class TestCreateParser:
    """Test cases for create_parser function."""

    def test_parser_creation(self):
        """Test that parser is created correctly."""
        parser = create_parser()
        assert parser.prog == "doppel"

        # Test default arguments
        args = parser.parse_args([])
        assert args.directory == "."
        assert args.content is False
        assert args.dry_run is False
        assert args.verbose is False

    def test_parser_with_directory(self):
        """Test parser with directory argument."""
        parser = create_parser()
        args = parser.parse_args(["/path/to/dir"])
        assert args.directory == "/path/to/dir"

    def test_parser_with_flags(self):
        """Test parser with various flags."""
        parser = create_parser()
        args = parser.parse_args(["--content", "--dry-run", "--verbose", "/test/dir"])

        assert args.content is True
        assert args.dry_run is True
        assert args.verbose is True
        assert args.directory == "/test/dir"

    def test_parser_help(self):
        """Test that parser shows help without errors."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_parser_version(self):
        """Test that parser shows version without errors."""
        parser = create_parser()

        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])


class TestValidateDirectory:
    """Test cases for validate_directory function."""

    def test_valid_directory(self):
        """Test validation of valid directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            result = validate_directory(temp_dir)
            assert result == Path(temp_dir).resolve()

    def test_nonexistent_directory(self):
        """Test validation of nonexistent directory."""
        with pytest.raises(SystemExit):
            validate_directory("/nonexistent/directory")

    def test_file_instead_of_directory(self):
        """Test validation when path is a file, not directory."""
        with tempfile.NamedTemporaryFile() as temp_file:
            with pytest.raises(SystemExit):
                validate_directory(temp_file.name)

    def test_current_directory(self):
        """Test validation of current directory."""
        result = validate_directory(".")
        assert result == Path(".").resolve()


class TestMain:
    """Test cases for main function."""

    @patch('doppel.cli.DuplicateScanner')
    @patch('doppel.cli.InteractiveRemover')
    @patch('sys.argv', ['doppel', '--dry-run'])
    def test_main_dry_run(self, mock_remover_class, mock_scanner_class):
        """Test main function with dry-run flag."""
        # Mock scanner
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = {"test.txt": []}
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', '--dry-run', temp_dir]):
                main()

        # Should create scanner and call scan
        mock_scanner_class.assert_called_once()
        mock_scanner.scan.assert_called_once()
        mock_scanner.display_duplicates.assert_called_once()

        # Should not create remover in dry-run mode
        mock_remover_class.assert_not_called()

    @patch('doppel.cli.DuplicateScanner')
    @patch('doppel.cli.InteractiveRemover')
    @patch('builtins.input', return_value='n')  # User says no to removal
    @patch('sys.argv', ['doppel'])
    def test_main_with_duplicates_no_removal(self, mock_remover_class, mock_scanner_class, mock_input):
        """Test main function with duplicates but user declines removal."""
        # Mock scanner with duplicates
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = {"test.txt": ["file1", "file2"]}
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', temp_dir]):
                main()

        # Should create scanner and call scan
        mock_scanner_class.assert_called_once()
        mock_scanner.scan.assert_called_once()

        # Should not create remover since user declined
        mock_remover_class.assert_not_called()

    @patch('doppel.cli.DuplicateScanner')
    @patch('doppel.cli.InteractiveRemover')
    @patch('builtins.input', return_value='y')  # User says yes to removal
    @patch('sys.argv', ['doppel'])
    def test_main_with_duplicates_with_removal(self, mock_remover_class, mock_scanner_class, mock_input):
        """Test main function with duplicates and user accepts removal."""
        # Mock scanner with duplicates
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = {"test.txt": ["file1", "file2"]}
        mock_scanner_class.return_value = mock_scanner

        # Mock remover
        mock_remover = MagicMock()
        mock_remover_class.return_value = mock_remover

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', temp_dir]):
                main()

        # Should create both scanner and remover
        mock_scanner_class.assert_called_once()
        mock_remover_class.assert_called_once_with(mock_scanner)

        # Should call process_duplicates
        mock_remover.process_duplicates.assert_called_once()

    @patch('doppel.cli.DuplicateScanner')
    @patch('sys.argv', ['doppel'])
    def test_main_no_duplicates(self, mock_scanner_class):
        """Test main function when no duplicates are found."""
        # Mock scanner with no duplicates
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = {}
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', temp_dir]):
                main()

        # Should create scanner and call scan
        mock_scanner_class.assert_called_once()
        mock_scanner.scan.assert_called_once()

    @patch('sys.argv', ['doppel', '/nonexistent'])
    def test_main_invalid_directory(self):
        """Test main function with invalid directory."""
        with pytest.raises(SystemExit):
            main()

    @patch('doppel.cli.DuplicateScanner')
    @patch('sys.argv', ['doppel'])
    def test_main_keyboard_interrupt(self, mock_scanner_class):
        """Test main function handles keyboard interrupt."""
        # Mock scanner to raise KeyboardInterrupt
        mock_scanner = MagicMock()
        mock_scanner.scan.side_effect = KeyboardInterrupt()
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', temp_dir]):
                with pytest.raises(SystemExit):
                    main()

    @patch('doppel.cli.DuplicateScanner')
    @patch('sys.argv', ['doppel'])
    def test_main_permission_error(self, mock_scanner_class):
        """Test main function handles permission error."""
        # Mock scanner to raise PermissionError
        mock_scanner = MagicMock()
        mock_scanner.scan.side_effect = PermissionError("Access denied")
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', temp_dir]):
                with pytest.raises(SystemExit):
                    main()

    @patch('doppel.cli.DuplicateScanner')
    @patch('sys.argv', ['doppel', '--content'])
    def test_main_with_content_flag(self, mock_scanner_class):
        """Test main function with content comparison flag."""
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = {}
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', '--content', temp_dir]):
                main()

        # Should create scanner with content comparison enabled
        mock_scanner_class.assert_called_once()
        args, kwargs = mock_scanner_class.call_args
        assert len(args) == 2
        assert args[1] is True  # compare_content=True

    @patch('doppel.cli.DuplicateScanner')
    @patch('sys.argv', ['doppel', '--verbose'])
    def test_main_with_verbose_flag(self, mock_scanner_class):
        """Test main function with verbose flag."""
        mock_scanner = MagicMock()
        mock_scanner.scan.return_value = {}
        mock_scanner_class.return_value = mock_scanner

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch('sys.argv', ['doppel', '--verbose', temp_dir]):
                with patch('builtins.print') as mock_print:
                    main()

        # Should print banner in verbose mode
        mock_print.assert_any_call("doppel 1.0.0 - Duplicate file eliminator")