"""
Tests for CLI entry point handling cv and ft aliases and update command.
"""

import sys
import unittest
from unittest.mock import patch

from converter.cli import get_command_name, main


class TestCLIEntryPoints(unittest.TestCase):
    """Test get_command_name for cv and ft."""

    def test_get_command_name_cv(self):
        with patch.object(sys, "argv", ["cv", "--help"]):
            self.assertEqual(get_command_name(), "cv")

    def test_get_command_name_ft(self):
        with patch.object(sys, "argv", ["ft", "--help"]):
            self.assertEqual(get_command_name(), "ft")

    def test_get_command_name_executable_path(self):
        with patch.object(sys, "argv", ["C:\\path\\to\\ft.exe", "--help"]):
            self.assertEqual(get_command_name(), "ft")

        with patch.object(sys, "argv", ["C:\\path\\to\\cv.exe", "--help"]):
            self.assertEqual(get_command_name(), "cv")


class TestCLICommands(unittest.TestCase):
    """Test CLI dispatch for help, version, and update."""

    @patch("converter.cli.show_help")
    def test_cv_help(self, mock_help):
        with patch.object(sys, "argv", ["cv", "--help"]):
            main()
            mock_help.assert_called_once()

    @patch("converter.cli.show_help")
    def test_ft_help(self, mock_help):
        with patch.object(sys, "argv", ["ft", "-h"]):
            main()
            mock_help.assert_called_once()

    @patch("converter.cli.show_version")
    def test_cv_version(self, mock_version):
        with patch.object(sys, "argv", ["cv", "--version"]):
            main()
            mock_version.assert_called_once()

    @patch("converter.cli.show_version")
    def test_ft_version(self, mock_version):
        with patch.object(sys, "argv", ["ft", "-v"]):
            main()
            mock_version.assert_called_once()

    @patch("converter.update.run_update", return_value=0)
    def test_cv_update_invokes_run_update(self, mock_run_update):
        with patch.object(sys, "argv", ["cv", "update"]):
            main()
            mock_run_update.assert_called_once()
            _, kwargs = mock_run_update.call_args
            self.assertEqual(kwargs.get("command_name"), "cv")

    @patch("converter.update.run_update", return_value=0)
    def test_ft_update_invokes_run_update(self, mock_run_update):
        with patch.object(sys, "argv", ["ft", "update"]):
            main()
            mock_run_update.assert_called_once()
            _, kwargs = mock_run_update.call_args
            self.assertEqual(kwargs.get("command_name"), "ft")

    def test_update_with_extra_args_fails(self):
        with patch.object(sys, "argv", ["cv", "update", "extra"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

    @patch("converter.clean.run_clear", return_value=0)
    def test_cv_clear_invokes_run_clear(self, mock_run_clear):
        with patch.object(sys, "argv", ["cv", "clear"]):
            main()
            mock_run_clear.assert_called_once()
            _, kwargs = mock_run_clear.call_args
            self.assertEqual(kwargs.get("command_name"), "cv")
            self.assertFalse(kwargs.get("yes"))
            self.assertFalse(kwargs.get("dry_run"))

    @patch("converter.clean.run_clear", return_value=0)
    def test_ft_clear_invokes_run_clear(self, mock_run_clear):
        with patch.object(sys, "argv", ["ft", "clear"]):
            main()
            mock_run_clear.assert_called_once()
            _, kwargs = mock_run_clear.call_args
            self.assertEqual(kwargs.get("command_name"), "ft")

    @patch("converter.clean.run_clear", return_value=0)
    def test_cv_clear_yes_and_dry_run_flags(self, mock_run_clear):
        with patch.object(sys, "argv", ["cv", "clear", "--yes", "--dry-run"]):
            main()
            mock_run_clear.assert_called_once()
            _, kwargs = mock_run_clear.call_args
            self.assertTrue(kwargs.get("yes"))
            self.assertTrue(kwargs.get("dry_run"))

    def test_clear_unknown_flag_fails(self):
        with patch.object(sys, "argv", ["cv", "clear", "--invalid-flag"]):
            with self.assertRaises(SystemExit) as cm:
                main()
            self.assertEqual(cm.exception.code, 1)

    def test_cv_clear_help_flag(self):
        with patch.object(sys, "argv", ["cv", "clear", "--help"]):
            # Should show clear help and return without error
            main()


if __name__ == "__main__":
    unittest.main()
