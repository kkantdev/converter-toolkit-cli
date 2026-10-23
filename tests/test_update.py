"""
Tests for package self-update functionality in converter.update.
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
import urllib.error

from rich.console import Console

from converter.update import (
    PACKAGE_NAME,
    compare_versions,
    get_current_version,
    get_latest_version,
    perform_update,
    run_update,
    verify_update,
)


class TestVersionDetection(unittest.TestCase):
    """Test dynamic package version detection."""

    def test_get_current_version_success(self):
        ver = get_current_version(PACKAGE_NAME)
        self.assertIsInstance(ver, str)
        self.assertTrue(len(ver) > 0)

    @patch("converter.__version__", "1.2.3")
    def test_get_current_version_fallback(self):
        with patch("importlib.metadata.version", side_effect=Exception("Not found")):
            ver = get_current_version("non-existent-pkg")
            self.assertEqual(ver, "1.2.3")


class TestVersionComparison(unittest.TestCase):
    """Test semantic version comparisons."""

    def test_compare_versions_less(self):
        self.assertEqual(compare_versions("0.1.0", "0.2.0"), -1)
        self.assertEqual(compare_versions("0.1.0", "0.1.1"), -1)
        self.assertEqual(compare_versions("0.9.9", "1.0.0"), -1)

    def test_compare_versions_equal(self):
        self.assertEqual(compare_versions("0.2.0", "0.2.0"), 0)
        self.assertEqual(compare_versions("1.0.0", "1.0.0"), 0)

    def test_compare_versions_greater(self):
        self.assertEqual(compare_versions("1.0.0", "0.9.9"), 1)
        self.assertEqual(compare_versions("0.2.0", "0.1.0"), 1)
        self.assertEqual(compare_versions("0.1.2", "0.1.1"), 1)


class TestPyPICheck(unittest.TestCase):
    """Test checking latest version from PyPI."""

    @patch("urllib.request.urlopen")
    def test_get_latest_version_success(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = b'{"info": {"version": "0.3.0"}}'
        mock_urlopen.return_value.__enter__.return_value = mock_resp

        ver, err = get_latest_version("test-package")
        self.assertEqual(ver, "0.3.0")
        self.assertIsNone(err)

    @patch("urllib.request.urlopen")
    def test_get_latest_version_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.URLError("Network unreachable")

        ver, err = get_latest_version("test-package")
        self.assertIsNone(ver)
        self.assertIn("Unable to check for updates", err)
        self.assertIn("internet connection", err)

    @patch("urllib.request.urlopen")
    def test_get_latest_version_404_not_found(self, mock_urlopen):
        mock_urlopen.side_effect = urllib.error.HTTPError(
            url="https://pypi.org/pypi/unknown/json",
            code=404,
            msg="Not Found",
            hdrs={},
            fp=None
        )

        ver, err = get_latest_version("unknown")
        self.assertIsNone(ver)
        self.assertIn("not found on PyPI", err)


class TestUpdateExecution(unittest.TestCase):
    """Test invoking pip install --upgrade."""

    @patch("subprocess.run")
    def test_perform_update_success(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "Successfully installed file-toolkit-cli-0.2.0"
        mock_run.return_value = mock_proc

        success, msg = perform_update("file-toolkit-cli")
        self.assertTrue(success)
        mock_run.assert_called_once_with(
            [sys.executable, "-m", "pip", "install", "--upgrade", "file-toolkit-cli"],
            stdout=-1,
            stderr=-1,
            text=True,
            check=False
        )

    @patch("subprocess.run")
    def test_perform_update_failure(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stderr = "Permission denied"
        mock_run.return_value = mock_proc

        success, msg = perform_update("file-toolkit-cli")
        self.assertFalse(success)
        self.assertIn("Permission denied", msg)


class TestUpdateVerification(unittest.TestCase):
    """Test verification after update."""

    @patch("subprocess.run")
    def test_verify_update_success(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "0.2.0\n"
        mock_run.return_value = mock_proc

        verified, new_ver = verify_update("file-toolkit-cli", expected_version="0.2.0")
        self.assertTrue(verified)
        self.assertEqual(new_ver, "0.2.0")

    @patch("subprocess.run")
    def test_verify_update_mismatch(self, mock_run):
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "0.1.0\n"
        mock_run.return_value = mock_proc

        verified, new_ver = verify_update("file-toolkit-cli", expected_version="0.2.0")
        self.assertFalse(verified)
        self.assertEqual(new_ver, "0.1.0")


class TestRunUpdateWorkflow(unittest.TestCase):
    """Test full run_update orchestration."""

    def setUp(self):
        self.console = Console(record=True)

    @patch("converter.update.get_current_version", return_value="0.1.0")
    @patch("converter.update.get_latest_version", return_value=("0.1.0", None))
    def test_run_update_already_up_to_date(self, mock_latest, mock_curr):
        code = run_update(console=self.console, command_name="cv")
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("File Toolkit is already up to date", output)

    @patch("converter.update.get_current_version", return_value="0.1.0")
    @patch("converter.update.get_latest_version", return_value=(None, "Unable to check for updates."))
    def test_run_update_network_failure(self, mock_latest, mock_curr):
        code = run_update(console=self.console, command_name="cv")
        self.assertEqual(code, 1)
        output = self.console.export_text()
        self.assertIn("Unable to check for updates", output)

    @patch("converter.update.get_current_version", return_value="0.1.0")
    @patch("converter.update.get_latest_version", return_value=("0.2.0", None))
    @patch("converter.update.perform_update", return_value=(True, "Installed"))
    @patch("converter.update.verify_update", return_value=(True, "0.2.0"))
    def test_run_update_successful_upgrade(self, mock_verif, mock_perf, mock_latest, mock_curr):
        code = run_update(console=self.console, command_name="ft")
        self.assertEqual(code, 0)
        output = self.console.export_text()
        self.assertIn("File Toolkit successfully updated", output)
        self.assertIn("0.1.0 → 0.2.0", output)

    @patch("converter.update.get_current_version", return_value="0.1.0")
    @patch("converter.update.get_latest_version", return_value=("0.2.0", None))
    @patch("converter.update.perform_update", return_value=(False, "Permission error"))
    def test_run_update_install_failed(self, mock_perf, mock_latest, mock_curr):
        code = run_update(console=self.console, command_name="cv")
        self.assertEqual(code, 1)
        output = self.console.export_text()
        self.assertIn("Update failed", output)
        self.assertIn("pip install --upgrade", output)
        self.assertIn("file-toolkit-cli", output)

    @patch("converter.update.get_current_version", return_value="0.1.0")
    @patch("converter.update.get_latest_version", return_value=("0.2.0", None))
    @patch("converter.update.perform_update", return_value=(True, "Installed"))
    @patch("converter.update.verify_update", return_value=(False, "0.1.0"))
    def test_run_update_verification_failed(self, mock_verif, mock_perf, mock_latest, mock_curr):
        code = run_update(console=self.console, command_name="cv")
        self.assertEqual(code, 1)
        output = self.console.export_text()
        self.assertIn("verification failed", output)


if __name__ == "__main__":
    unittest.main()
