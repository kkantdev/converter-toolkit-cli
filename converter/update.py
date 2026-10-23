"""
Package self-update functionality for File Toolkit CLI.
Supports both 'cv update' and 'ft update'.
"""

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request
from typing import Optional, Tuple

from rich.console import Console

try:
    from packaging.version import parse as parse_version
except ImportError:
    # Fallback semver parser if packaging is not installed
    def parse_version(v: str):
        parts = []
        for part in re.split(r'[-.+_]', str(v)):
            if part.isdigit():
                parts.append(int(part))
            else:
                parts.append(part)
        return parts

PACKAGE_NAME = "file-toolkit-cli"
PYPI_URL_TEMPLATE = "https://pypi.org/pypi/{package}/json"


def get_current_version(package_name: str = PACKAGE_NAME) -> str:
    """
    Detect the currently installed version of File Toolkit CLI.
    First checks importlib.metadata, falling back to converter.__version__.
    """
    try:
        if sys.version_info >= (3, 8):
            from importlib.metadata import version, PackageNotFoundError
            try:
                return version(package_name)
            except PackageNotFoundError:
                pass
    except Exception:
        pass

    try:
        from converter import __version__
        return __version__
    except Exception:
        return "0.1.0"


def get_latest_version(
    package_name: str = PACKAGE_NAME,
    timeout: float = 10.0
) -> Tuple[Optional[str], Optional[str]]:
    """
    Query PyPI JSON API for the latest published package version.
    
    Returns:
        (latest_version, None) on success, or
        (None, error_message) on failure.
    """
    url = PYPI_URL_TEMPLATE.format(package=package_name)
    current_ver = get_current_version(package_name)
    
    req = urllib.request.Request(
        url,
        headers={"User-Agent": f"FileToolkitCLI/{current_ver}"}
    )
    
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
            info = data.get("info", {})
            latest_version = info.get("version")
            if not latest_version:
                return None, "Unable to determine latest version from PyPI response."
            return latest_version, None
            
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None, f"Package '{package_name}' was not found on PyPI."
        return None, f"PyPI returned HTTP error {e.code}: {e.reason}."
        
    except (urllib.error.URLError, TimeoutError, OSError):
        return None, "Unable to check for updates.\n\nPlease check your internet connection and try again."
        
    except Exception:
        return None, "Unable to check for updates from PyPI. Please try again later."


def compare_versions(current_v: str, latest_v: str) -> int:
    """
    Compare two version strings.
    
    Returns:
        -1 if current_v < latest_v (newer version available)
         0 if current_v == latest_v (already up to date)
         1 if current_v > latest_v (current is newer / dev build)
    """
    parsed_curr = parse_version(current_v)
    parsed_latest = parse_version(latest_v)
    
    if parsed_curr < parsed_latest:
        return -1
    elif parsed_curr > parsed_latest:
        return 1
    return 0


def perform_update(package_name: str = PACKAGE_NAME) -> Tuple[bool, str]:
    """
    Execute pip install --upgrade using the current Python interpreter.
    
    Returns:
        (success, output_or_error_message)
    """
    cmd = [sys.executable, "-m", "pip", "install", "--upgrade", package_name]
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if proc.returncode == 0:
            return True, proc.stdout
        else:
            err_msg = proc.stderr.strip() or proc.stdout.strip() or "Installation returned non-zero code."
            return False, err_msg
    except Exception as e:
        return False, str(e)


def verify_update(
    package_name: str = PACKAGE_NAME,
    expected_version: Optional[str] = None
) -> Tuple[bool, str]:
    """
    Verify the updated package version by querying a fresh Python subprocess
    to bypass in-memory metadata caches.
    
    Returns:
        (is_verified, actual_version)
    """
    code = (
        f"import sys\n"
        f"try:\n"
        f"    from importlib.metadata import version\n"
        f"    print(version('{package_name}'))\n"
        f"except Exception:\n"
        f"    try:\n"
        f"        import converter\n"
        f"        print(converter.__version__)\n"
        f"    except Exception:\n"
        f"        sys.exit(1)\n"
    )
    
    try:
        proc = subprocess.run(
            [sys.executable, "-c", code],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False
        )
        if proc.returncode == 0:
            actual_version = proc.stdout.strip()
            if expected_version:
                # Verified if actual_version matches or exceeds expected_version
                is_ok = compare_versions(actual_version, expected_version) >= 0
                return is_ok, actual_version
            return True, actual_version
    except Exception:
        pass
        
    return False, ""


def run_update(console: Optional[Console] = None, command_name: str = "cv") -> int:
    """
    Main update workflow executed by 'cv update' or 'ft update'.
    
    Returns:
        Exit code: 0 for success/already up-to-date, 1 for failure.
    """
    if console is None:
        console = Console()
        
    console.print()
    console.print("[bold]File Toolkit Update[/bold]")
    console.print()
    
    current_ver = get_current_version(PACKAGE_NAME)
    latest_ver, err = get_latest_version(PACKAGE_NAME)
    
    if err:
        console.print(f"[red]✖ {err}[/red]")
        console.print()
        return 1
        
    console.print(f"Current version: [cyan]{current_ver}[/cyan]")
    console.print(f"Latest version:  [cyan]{latest_ver}[/cyan]")
    console.print()
    
    cmp = compare_versions(current_ver, latest_ver)
    
    if cmp >= 0:
        console.print("[green]✔ File Toolkit is already up to date.[/green]")
        console.print()
        return 0
        
    console.print("[bold]A new version is available.[/bold]")
    console.print("Updating File Toolkit...")
    console.print()
    
    success, err_msg = perform_update(PACKAGE_NAME)
    if not success:
        console.print("[red]✖ Update failed.[/red]")
        console.print()
        console.print("The package could not be updated in the current Python environment.")
        console.print()
        console.print("You can try:")
        console.print(f"    [cyan]{sys.executable} -m pip install --upgrade {PACKAGE_NAME}[/cyan]")
        console.print()
        return 1
        
    verified, new_ver = verify_update(PACKAGE_NAME, latest_ver)
    if verified:
        console.print("[green]✔ File Toolkit successfully updated[/green]")
        console.print(f"[green]✔ Version: {current_ver} → {new_ver}[/green]")
        console.print()
        return 0
    else:
        console.print("[yellow]⚠ Update completed but version verification failed.[/yellow]")
        if new_ver:
            console.print(f"Expected version: {latest_ver}, detected: {new_ver}")
        console.print(f"You can check with: [cyan]{command_name} --version[/cyan]")
        console.print()
        return 1
