"""
Unit tests for File Toolkit safe cleanup functionality in converter.clean.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from rich.console import Console

from converter.clean import (
    APP_DIR_NAME,
    format_size,
    get_cleanup_locations,
    is_safe_to_delete,
    perform_cleanup,
    run_clear,
    scan_category,
    scan_cleanup_data,
)


class TestFormatSize(unittest.TestCase):
    """Test human-readable byte size formatting."""

    def test_format_size_bytes(self):
        self.assertEqual(format_size(500), "500 B")

    def test_format_size_kb(self):
        self.assertEqual(format_size(2048), "2.0 KB")

    def test_format_size_mb(self):
        self.assertEqual(format_size(10 * 1024 * 1024), "10.0 MB")

    def test_format_size_gb(self):
        self.assertEqual(format_size(2 * 1024 * 1024 * 1024), "2.0 GB")


class TestSafeToDeleteGuards(unittest.TestCase):
    """Test strict safety guards against deleting user files or root dirs."""

    def setUp(self):
        self.tmp_dir = Path(tempfile.mkdtemp(prefix="test_ft_safe_"))
        self.app_dir = self.tmp_dir / APP_DIR_NAME
        self.app_dir.mkdir(parents=True, exist_ok=True)
        self.allowed_roots = [self.app_dir]

    def tearDown(self):
        import shutil
        if self.tmp_dir.exists():
            shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_allowed_app_directory(self):
        target = self.app_dir / "cache" / "temp.dat"
        self.assertTrue(is_safe_to_delete(target, self.allowed_roots))

    def test_reject_user_home(self):
        self.assertFalse(is_safe_to_delete(Path.home(), self.allowed_roots))

    def test_reject_user_desktop(self):
        self.assertFalse(is_safe_to_delete(Path.home() / "Desktop", self.allowed_roots))

    def test_reject_current_working_directory(self):
        self.assertFalse(is_safe_to_delete(Path.cwd(), self.allowed_roots))

    def test_reject_system_temp_root(self):
        self.assertFalse(is_safe_to_delete(Path(tempfile.gettempdir()), self.allowed_roots))

    def test_reject_user_files(self):
        user_file = self.tmp_dir / "my_document.docx"
        user_file.write_text("important user document")
        self.assertFalse(is_safe_to_delete(user_file, self.allowed_roots))


class TestScanAndClean(unittest.TestCase):
    """Test scanning and deleting internal File Toolkit data."""

    def setUp(self):
        self.base_tmp = Path(tempfile.mkdtemp(prefix="test_ft_storage_"))
        self.app_root = self.base_tmp / APP_DIR_NAME
        self.app_root.mkdir(parents=True, exist_ok=True)

        self.custom_locations = {
            "Temporary files": [self.app_root / "temp"],
            "Cache": [self.app_root / "cache"],
            "Metadata": [self.app_root / "metadata"],
            "Logs": [self.app_root / "logs"],
        }
        self.console = Console(record=True)

    def tearDown(self):
        import shutil
        if self.base_tmp.exists():
            shutil.rmtree(self.base_tmp, ignore_errors=True)

    def test_scan_empty_returns_nothing(self):
        cat_sizes, total, cat_paths, roots = scan_cleanup_data(self.custom_locations)
        self.assertEqual(total, 0)
        self.assertEqual(len(cat_paths), 0)

    def test_run_clear_already_clean(self):
        code = run_clear(
            console=self.console,
            command_name="cv",
            custom_locations=self.custom_locations
        )
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("File Toolkit is already clean", output)
        self.assertIn("No temporary files, cache, metadata, or logs were found", output)

    def test_scan_with_populated_categories(self):
        # Populate test data in isolated test folder
        temp_dir = self.app_root / "temp"
        temp_dir.mkdir(parents=True)
        (temp_dir / "file1.tmp").write_bytes(b"A" * 1024)

        cache_dir = self.app_root / "cache"
        cache_dir.mkdir(parents=True)
        (cache_dir / "cache1.dat").write_bytes(b"B" * 2048)

        cat_sizes, total, cat_paths, roots = scan_cleanup_data(self.custom_locations)
        self.assertEqual(total, 3072)
        self.assertIn("Temporary files", cat_sizes)
        self.assertEqual(cat_sizes["Temporary files"], 1024)
        self.assertIn("Cache", cat_sizes)
        self.assertEqual(cat_sizes["Cache"], 2048)

    def test_run_clear_dry_run(self):
        temp_dir = self.app_root / "temp"
        temp_dir.mkdir(parents=True)
        test_file = temp_dir / "file1.tmp"
        test_file.write_bytes(b"A" * 512)

        code = run_clear(
            console=self.console,
            dry_run=True,
            command_name="cv",
            custom_locations=self.custom_locations
        )
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("Cleanup Preview", output)
        self.assertIn("Dry run complete", output)
        self.assertIn("No files were deleted", output)
        self.assertTrue(test_file.exists())  # Must NOT delete

    @patch("builtins.input", return_value="n")
    def test_run_clear_user_declines(self, mock_input):
        temp_dir = self.app_root / "temp"
        temp_dir.mkdir(parents=True)
        test_file = temp_dir / "file1.tmp"
        test_file.write_bytes(b"A" * 512)

        code = run_clear(
            console=self.console,
            yes=False,
            command_name="cv",
            custom_locations=self.custom_locations
        )
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("Cleanup cancelled", output)
        self.assertTrue(test_file.exists())

    @patch("builtins.input", return_value="y")
    def test_run_clear_user_confirms(self, mock_input):
        temp_dir = self.app_root / "temp"
        temp_dir.mkdir(parents=True)
        test_file = temp_dir / "file1.tmp"
        test_file.write_bytes(b"A" * 1024)

        code = run_clear(
            console=self.console,
            yes=False,
            command_name="cv",
            custom_locations=self.custom_locations
        )
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("Cleanup complete", output)
        self.assertIn("1.0 KB freed", output)
        self.assertFalse(test_file.exists())

    def test_run_clear_yes_flag(self):
        cache_dir = self.app_root / "cache"
        cache_dir.mkdir(parents=True)
        test_file = cache_dir / "data.bin"
        test_file.write_bytes(b"B" * 2048)

        code = run_clear(
            console=self.console,
            yes=True,
            command_name="ft",
            custom_locations=self.custom_locations
        )
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("Cleanup complete", output)
        self.assertIn("2.0 KB freed", output)
        self.assertFalse(test_file.exists())


class TestPlatformLocations(unittest.TestCase):
    """Test get_cleanup_locations returns expected structure on current platform."""

    def test_locations_keys(self):
        locs = get_cleanup_locations()
        self.assertIn("Temporary files", locs)
        self.assertIn("Cache", locs)
        self.assertIn("Metadata", locs)
        self.assertIn("Logs", locs)
        self.assertTrue(len(locs["Temporary files"]) > 0)


if __name__ == "__main__":
    unittest.main()
