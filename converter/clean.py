"""
Safe cleanup functionality for File Toolkit CLI.
Supports both 'cv clear' and 'ft clear'.
"""

import os
import platform
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rich.console import Console

APP_DIR_NAME = "file-toolkit"


def get_cleanup_locations() -> Dict[str, List[Path]]:
    """
    Return mapped categories ('Temporary files', 'Cache', 'Metadata', 'Logs')
    to candidate directories owned specifically by File Toolkit.
    """
    system = platform.system()
    home = Path.home()

    locations: Dict[str, List[Path]] = {
        "Temporary files": [
            Path(tempfile.gettempdir()) / APP_DIR_NAME,
        ],
        "Cache": [],
        "Metadata": [],
        "Logs": []
    }

    if system == "Windows":
        local_app_data = Path(os.environ.get("LOCALAPPDATA", home / "AppData" / "Local"))
        locations["Cache"].append(local_app_data / APP_DIR_NAME / "cache")
        locations["Metadata"].append(local_app_data / APP_DIR_NAME / "metadata")
        locations["Logs"].append(local_app_data / APP_DIR_NAME / "logs")
    elif system == "Darwin":  # macOS
        locations["Cache"].append(home / "Library" / "Caches" / APP_DIR_NAME)
        locations["Metadata"].append(home / "Library" / "Application Support" / APP_DIR_NAME)
        locations["Logs"].append(home / "Library" / "Logs" / APP_DIR_NAME)
    else:  # Linux / Unix
        xdg_cache = Path(os.environ.get("XDG_CACHE_HOME", home / ".cache"))
        xdg_data = Path(os.environ.get("XDG_DATA_HOME", home / ".local" / "share"))
        xdg_state = Path(os.environ.get("XDG_STATE_HOME", home / ".local" / "state"))
        locations["Cache"].append(xdg_cache / APP_DIR_NAME)
        locations["Metadata"].append(xdg_data / APP_DIR_NAME)
        locations["Logs"].append(xdg_state / APP_DIR_NAME / "logs")

    # Cross-platform fallback directory (~/.file-toolkit/)
    dot_app = home / f".{APP_DIR_NAME}"
    locations["Cache"].append(dot_app / "cache")
    locations["Metadata"].append(dot_app / "metadata")
    locations["Logs"].append(dot_app / "logs")

    return locations


def format_size(size_bytes: int) -> str:
    """Format bytes into human-readable string (B, KB, MB, GB)."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_safe_to_delete(path: Path, allowed_roots: List[Path]) -> bool:
    """
    Strict safety check ensuring a path is directly inside one of File Toolkit's
    designated internal directories, and NEVER a user directory or root.
    """
    try:
        resolved = path.resolve()
    except Exception:
        return False

    # Forbidden paths: user home, current working dir, standard user content folders
    forbidden_roots = [
        Path.home().resolve(),
        Path.cwd().resolve(),
        (Path.home() / "Desktop").resolve(),
        (Path.home() / "Downloads").resolve(),
        (Path.home() / "Documents").resolve(),
        (Path.home() / "Pictures").resolve(),
        (Path.home() / "Videos").resolve(),
        (Path.home() / "Music").resolve(),
        Path(tempfile.gettempdir()).resolve(),
    ]

    if resolved in forbidden_roots or resolved.parent == resolved:
        return False

    # Verify that the path clearly contains the application directory name
    parts_lower = [p.lower() for p in resolved.parts]
    if APP_DIR_NAME.lower() not in parts_lower and f".{APP_DIR_NAME}".lower() not in parts_lower:
        # If allowed_roots are custom test roots, check if it's within one of them
        if not any(resolved == r.resolve() or resolved.is_relative_to(r.resolve()) for r in allowed_roots):
            return False

    # Must be equal to or a subpath of one of the allowed roots
    for root in allowed_roots:
        try:
            resolved_root = root.resolve()
            if resolved == resolved_root or resolved.is_relative_to(resolved_root):
                return True
        except (ValueError, AttributeError):
            continue

    return False


def scan_category(dir_path: Path) -> Tuple[int, int, List[Path]]:
    """
    Scan a directory for existing files and total byte size.
    Returns:
        (total_bytes, file_count, list_of_existing_items)
    """
    total_bytes = 0
    file_count = 0
    items: List[Path] = []

    if not dir_path.exists():
        return 0, 0, []

    try:
        if dir_path.is_file():
            return dir_path.stat().st_size, 1, [dir_path]

        for entry in dir_path.rglob("*"):
            if entry.is_file():
                try:
                    size = entry.stat().st_size
                    total_bytes += size
                    file_count += 1
                except (OSError, PermissionError):
                    pass
            items.append(entry)
    except (OSError, PermissionError):
        pass

    return total_bytes, file_count, items


def scan_cleanup_data(
    locations: Optional[Dict[str, List[Path]]] = None
) -> Tuple[Dict[str, int], int, Dict[str, List[Path]], List[Path]]:
    """
    Scan File Toolkit internal storage locations.
    
    Returns:
        (category_sizes, total_size, category_paths, all_allowed_roots)
    """
    if locations is None:
        locations = get_cleanup_locations()

    category_sizes: Dict[str, int] = {}
    category_paths: Dict[str, List[Path]] = {}
    all_allowed_roots: List[Path] = []
    total_size = 0

    for category, paths in locations.items():
        cat_bytes = 0
        existing_targets: List[Path] = []
        for path in paths:
            all_allowed_roots.append(path)
            if path.exists():
                b, count, _ = scan_category(path)
                if count > 0 or any(path.iterdir() if path.is_dir() else [path]):
                    cat_bytes += b
                    existing_targets.append(path)
        if existing_targets:
            category_sizes[category] = cat_bytes
            category_paths[category] = existing_targets
            total_size += cat_bytes

    return category_sizes, total_size, category_paths, all_allowed_roots


def perform_cleanup(
    category_paths: Dict[str, List[Path]],
    allowed_roots: List[Path]
) -> Tuple[int, List[str], List[str]]:
    """
    Safely delete File Toolkit internal data.
    
    Returns:
        (freed_bytes, cleaned_categories, error_messages)
    """
    freed_bytes = 0
    cleaned_categories: List[str] = []
    errors: List[str] = []

    for category, paths in category_paths.items():
        category_freed = 0
        cat_success = True

        for target in paths:
            if not is_safe_to_delete(target, allowed_roots):
                errors.append(f"Skipped unsafe path: {target}")
                cat_success = False
                continue

            if not target.exists():
                continue

            # Calculate size before deletion
            t_bytes, _, _ = scan_category(target)

            try:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                category_freed += t_bytes
            except Exception as e:
                errors.append(f"Could not remove {target}: {str(e)}")
                cat_success = False

        freed_bytes += category_freed
        if cat_success and category_freed >= 0:
            cleaned_categories.append(category)

    return freed_bytes, cleaned_categories, errors


def run_clear(
    console: Optional[Console] = None,
    yes: bool = False,
    dry_run: bool = False,
    command_name: str = "cv",
    custom_locations: Optional[Dict[str, List[Path]]] = None
) -> int:
    """
    Main clear workflow executed by 'cv clear' or 'ft clear'.
    
    Returns:
        Exit code: 0 for success/clean, 1 on error.
    """
    if console is None:
        console = Console()

    console.print()
    if dry_run:
        console.print("[bold]File Toolkit Cleanup Preview[/bold]")
    else:
        console.print("[bold]File Toolkit Cleanup[/bold]")
    console.print()

    console.print("[dim]Scanning File Toolkit data...[/dim]")
    console.print()

    category_sizes, total_size, category_paths, allowed_roots = scan_cleanup_data(custom_locations)

    if not category_paths or total_size == 0 and not any(category_sizes.values()):
        console.print("[green]✔ File Toolkit is already clean.[/green]")
        console.print("No temporary files, cache, metadata, or logs were found.")
        console.print()
        return 0

    # Display found categories with formatted sizes
    max_label_len = max(len(cat) for cat in category_sizes.keys())
    for cat, size in category_sizes.items():
        size_str = format_size(size)
        console.print(f"{cat.ljust(max_label_len + 4)} [cyan]{size_str.rjust(10)}[/cyan]")

    console.print("─" * (max_label_len + 16))
    total_str = format_size(total_size)
    console.print(f"{'Total'.ljust(max_label_len + 4)} [bold cyan]{total_str.rjust(10)}[/bold cyan]")
    console.print()

    console.print("[dim]These files were created by File Toolkit.[/dim]")
    console.print()

    if dry_run:
        console.print("[yellow]Dry run complete.[/yellow]")
        console.print("No files were deleted.")
        console.print()
        return 0

    # Ask for confirmation unless --yes is supplied
    if not yes:
        try:
            response = input("Delete these files? [y/N]: ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            console.print()
            console.print("Cleanup cancelled.")
            console.print("No files were deleted.")
            console.print()
            return 0

        if response not in ("y", "yes"):
            console.print("Cleanup cancelled.")
            console.print("No files were deleted.")
            console.print()
            return 0

    console.print("[dim]Cleaning File Toolkit data...[/dim]")
    console.print()

    freed_bytes, cleaned_categories, errors = perform_cleanup(category_paths, allowed_roots)

    for cat in cleaned_categories:
        console.print(f"[green]✔[/green] {cat} removed")

    if errors:
        console.print()
        console.print("[yellow]⚠ Some File Toolkit data could not be accessed:[/yellow]")
        for err in errors:
            console.print(f"  [red]•[/red] {err}")

    console.print()
    console.print("[green]✔ Cleanup complete[/green]")
    console.print(f"[bold green]{format_size(freed_bytes)} freed[/bold green]")
    console.print()

    return 0 if not errors else 1
