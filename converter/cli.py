#!/usr/bin/env python3
"""
CLI entry point for File Toolkit CLI.
Handles argument parsing, validation, and conversion dispatch.
"""

import argparse
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from rich.console import Console
from rich.table import Table
from rich import box

from converter import __version__

# Ensure UTF-8 encoding on Windows console for Rich symbols
if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()


def resolve_output_path(target_path: Path) -> Path:
    """
    Resolve output path to avoid file collisions.
    
    Args:
        target_path: Desired output path
        
    Returns:
        Safe output path that doesn't overwrite existing files
    """
    if not target_path.exists():
        return target_path

    parent = target_path.parent
    stem = target_path.stem
    suffix = target_path.suffix
    counter = 1

    while True:
        candidate = parent / f"{stem}_cv{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def parse_kb_flag(flag: str) -> Optional[int]:
    """
    Parse KB compression flag like '-100kb'.
    
    Args:
        flag: Flag string to parse
        
    Returns:
        KB target as integer, or None if invalid
    """
    match = re.match(r'^-(\d+)kb$', flag.lower())
    if match:
        kb_value = int(match.group(1))
        return kb_value if kb_value > 0 else None
    return None


def parse_format_flag(flag: str) -> Optional[str]:
    """
    Parse format conversion flag like '-jpg', '-png', etc.
    
    Args:
        flag: Flag string to parse
        
    Returns:
        Target format as string, or None if invalid
    """
    if flag.startswith('-') and len(flag) > 1:
        format_name = flag[1:].lower()
        valid_formats = {
            'png', 'jpg', 'jpeg', 'webp', 'docx', 'pptx', 'csv', 'xlsx'
        }
        return format_name if format_name in valid_formats else None
    return None


def validate_input_file(file_path: Path) -> Tuple[bool, str]:
    """
    Validate input file exists and has supported extension.
    
    Args:
        file_path: Path to input file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not file_path.exists():
        return False, f"Input file '{file_path}' does not exist."
    
    if not file_path.is_file():
        return False, f"Input path '{file_path}' is not a file."
    
    supported_extensions = {
        '.pdf', '.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif',
        '.docx', '.txt', '.csv', '.xlsx'
    }
    
    if file_path.suffix.lower() not in supported_extensions:
        return False, f"Unsupported file extension '{file_path.suffix}'."
    
    return True, ""


def validate_conversion_compatibility(input_ext: str, target_format: str) -> Tuple[bool, str]:
    """
    Validate that the requested conversion is supported.
    
    Args:
        input_ext: Input file extension (with dot)
        target_format: Target format string
        
    Returns:
        Tuple of (is_compatible, error_message)
    """
    input_ext = input_ext.lower()
    target_format = target_format.lower()
    
    # Define conversion compatibility matrix
    conversions = {
        '.pdf': ['png', 'jpg', 'jpeg', 'docx'],
        '.png': ['jpg', 'jpeg', 'webp', 'pptx'],
        '.jpg': ['png', 'webp', 'pptx'],
        '.jpeg': ['png', 'webp', 'pptx'],
        '.webp': ['png', 'jpg', 'jpeg', 'pptx'],
        '.bmp': ['png', 'jpg', 'jpeg', 'webp', 'pptx'],
        '.tiff': ['png', 'jpg', 'jpeg', 'webp', 'pptx'],
        '.tif': ['png', 'jpg', 'jpeg', 'webp', 'pptx'],
        '.docx': ['pptx'],
        '.txt': ['docx'],
        '.csv': ['xlsx'],
        '.xlsx': ['csv']
    }
    
    # Handle jpeg as jpg
    if target_format == 'jpeg':
        target_format = 'jpg'
    
    if input_ext in conversions and target_format in conversions[input_ext]:
        return True, ""
    
    return False, f"Conversion from {input_ext} to {target_format} is not supported."


def get_command_name():
    """Get the command name used to run the CLI (supports both ft and cv)."""
    if sys.argv and sys.argv[0]:
        prog = Path(sys.argv[0]).stem.lower()
        if "ft" in prog:
            return "ft"
    return "cv"


def show_help():
    """Display help information using Rich formatting."""
    cmd = get_command_name()
    alt_cmd = "cv" if cmd == "ft" else "ft"
    console.print()
    console.print("[bold green]File Toolkit CLI v{version}[/bold green]".format(version=__version__))
    console.print(f"[dim]Commands: [bold cyan]{cmd}[/bold cyan] (alias: [bold cyan]{alt_cmd}[/bold cyan])[/dim]")
    console.print()
    console.print("[bold]DESCRIPTION[/bold]")
    console.print("    Fast, modular CLI tool for file conversion and KB size compression.")
    console.print()
    
    console.print("[bold]USAGE[/bold]")
    console.print(f"    [cyan]{cmd} <file_path> -<format>[/cyan]                    Convert file format")
    console.print(f"    [cyan]{cmd} <file_path> -<target_size>kb[/cyan]             Compress to target KB")  
    console.print(f"    [cyan]{cmd} <file_path> -<format> -<target_size>kb[/cyan]   Convert + compress")
    console.print(f"    [cyan]{cmd} update[/cyan]                                Check for and install updates")
    console.print(f"    [cyan]{cmd} clear \\[-y|--yes] \\[--dry-run][/cyan]      Clean temporary files and cache")
    console.print()
    
    console.print("[bold]COMMANDS[/bold]")
    console.print("    [cyan]update[/cyan]         Check for and install the latest published version from PyPI")
    console.print("    [cyan]clear[/cyan]          Safely remove File Toolkit temporary files, cache, metadata, and logs")
    console.print()

    console.print("[bold]SUPPORTED CONVERSIONS[/bold]")
    
    # Create conversion table
    table = Table(box=box.ROUNDED)
    table.add_column("Input Format", style="cyan")
    table.add_column("Supported Outputs", style="green")
    
    table.add_row("PDF", "png, jpg, docx")
    table.add_row("Images (png, jpg, webp, etc.)", "png, jpg, webp, pptx")
    table.add_row("Word Documents (docx)", "pptx")
    table.add_row("Text Files (txt)", "docx")
    table.add_row("Spreadsheets", "csv <-> xlsx")
    
    console.print(table)
    console.print()
    
    console.print("[bold]EXAMPLES[/bold]")
    console.print(f"    [green]{cmd} report.pdf -docx[/green]              Convert PDF to Word")
    console.print(f"    [green]{cmd} photo.png -jpg[/green]               Convert PNG to JPEG")
    console.print(f"    [green]{cmd} photo.jpg -200kb[/green]             Compress JPEG to 200KB")
    console.print(f"    [green]{cmd} header.png -jpg -100kb[/green]       Convert PNG to JPEG and compress to 100KB")
    console.print(f"    [green]{cmd} document.docx -pptx[/green]          Convert Word to PowerPoint")
    console.print(f"    [green]{cmd} data.csv -xlsx[/green]               Convert CSV to Excel")
    console.print(f"    [green]{cmd} update[/green]                       Update File Toolkit to latest version")
    console.print(f"    [green]{cmd} clear[/green]                        Scan and clean File Toolkit internal data")
    console.print(f"    [green]{cmd} clear --dry-run[/green]              Preview files to be cleaned without deleting")
    console.print()
    
    console.print("[bold]OPTIONS[/bold]")
    console.print("    [cyan]-h, --help[/cyan]     Show this help message")
    console.print("    [cyan]-v, --version[/cyan]  Show version information")
    console.print()


def show_version():
    """Display version information."""
    cmd = get_command_name()
    console.print(f"{cmd} (File Toolkit CLI) version {__version__} [aliases: cv, ft]")


def main():
    """Main CLI entry point."""
    cmd = get_command_name()
    
    # Handle help and version flags first
    if len(sys.argv) == 1 or (len(sys.argv) == 2 and sys.argv[1] in ['-h', '--help']):
        show_help()
        return
    
    if len(sys.argv) == 2 and sys.argv[1] in ['-v', '--version']:
        show_version()
        return

    # Handle update command
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "update":
        if len(sys.argv) > 2:
            console.print("[red]✖ Error:[/red] 'update' command takes no additional arguments.")
            console.print(f"Use [cyan]{cmd} update[/cyan] or [cyan]{cmd} --help[/cyan].")
            sys.exit(1)
        from converter.update import run_update
        exit_code = run_update(console=console, command_name=cmd)
        if exit_code != 0:
            sys.exit(exit_code)
        return

    # Handle clear command
    if len(sys.argv) >= 2 and sys.argv[1].lower() == "clear":
        clear_args = sys.argv[2:]
        yes = False
        dry_run = False
        
        # Check for help flag
        if any(arg in ['-h', '--help'] for arg in clear_args):
            console.print()
            console.print("[bold]File Toolkit Cleanup[/bold]")
            console.print("Safely remove File Toolkit temporary files, cache, metadata, and logs.")
            console.print()
            console.print("[bold]USAGE[/bold]")
            console.print(f"    [cyan]{cmd} clear \\[options][/cyan]")
            console.print()
            console.print("[bold]OPTIONS[/bold]")
            console.print("    [cyan]-y, --yes[/cyan]      Skip confirmation prompt and delete immediately")
            console.print("    [cyan]--dry-run[/cyan]      Show what would be deleted without removing files")
            console.print("    [cyan]-h, --help[/cyan]     Show this help message")
            console.print()
            return
            
        for arg in clear_args:
            if arg in ['-y', '--yes']:
                yes = True
            elif arg == '--dry-run':
                dry_run = True
            else:
                console.print(f"[red]✖ Error:[/red] Unknown option '{arg}' for clear command.")
                console.print(f"Use [cyan]{cmd} clear --help[/cyan] for usage information.")
                sys.exit(1)
                
        from converter.clean import run_clear
        exit_code = run_clear(console=console, yes=yes, dry_run=dry_run, command_name=cmd)
        if exit_code != 0:
            sys.exit(exit_code)
        return
    
    # Parse arguments
    if len(sys.argv) < 3:
        console.print("[red]✖ Error:[/red] Missing required arguments.")
        console.print(f"Use [cyan]{cmd} --help[/cyan] for usage information.")
        sys.exit(1)
    
    # Get input file and flags
    input_path_str = sys.argv[1]
    flags = sys.argv[2:]
    
    # Resolve input path
    input_path = Path(input_path_str).resolve()
    
    # Validate input file
    is_valid, error_msg = validate_input_file(input_path)
    if not is_valid:
        console.print(f"[red]✖ Error:[/red] {error_msg}")
        sys.exit(1)
    
    # Parse flags
    target_format = None
    target_kb = None
    
    for flag in flags:
        # Try parsing as format flag
        format_flag = parse_format_flag(flag)
        if format_flag:
            target_format = format_flag
            continue
            
        # Try parsing as KB flag
        kb_flag = parse_kb_flag(flag)
        if kb_flag:
            target_kb = kb_flag
            continue
            
        # Unknown flag
        console.print(f"[red]✖ Error:[/red] Unknown flag '{flag}'.")
        console.print(f"Use [cyan]{cmd} --help[/cyan] for usage information.")
        sys.exit(1)
    
    # Must have at least one operation
    if not target_format and not target_kb:
        console.print("[red]✖ Error:[/red] No conversion or compression operation specified.")
        console.print(f"Use [cyan]{cmd} --help[/cyan] for usage information.")
        sys.exit(1)
    
    # Validate conversion compatibility if format conversion requested
    if target_format:
        is_compatible, error_msg = validate_conversion_compatibility(input_path.suffix, target_format)
        if not is_compatible:
            console.print(f"[red]✖ Error:[/red] {error_msg}")
            sys.exit(1)
    
    # Import conversion modules with graceful error handling
    image_ops_available = True
    pdf_ops_available = True
    doc_ops_available = True
    
    try:
        from converter.image_ops import convert_image_format, compress_image_to_kb, convert_and_compress_image, convert_image_to_pptx
    except ImportError:
        image_ops_available = False
    
    try:
        from converter.pdf_ops import convert_pdf_to_images, convert_pdf_to_docx
    except ImportError:
        pdf_ops_available = False
        
    try:
        from converter.doc_ops import convert_txt_to_docx, convert_docx_to_pptx, convert_csv_to_xlsx, convert_xlsx_to_csv
    except ImportError:
        doc_ops_available = False
    
    # Dispatch to appropriate conversion handler
    try:
        input_ext = input_path.suffix.lower()
        
        # Image operations
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp', '.bmp', '.tiff', '.tif'}
        if input_ext in image_extensions:
            if not image_ops_available:
                console.print(f"[red]✖ Error:[/red] Image operations require Pillow. Install with: pip install -e .")
                sys.exit(1)
            
            if target_format and target_kb:
                # Combined conversion + compression
                if target_format in ['png', 'jpg', 'jpeg', 'webp']:
                    result_path = convert_and_compress_image(input_path, target_format, target_kb)
                    return
                elif target_format == 'pptx':
                    console.print("[red]✖ Error:[/red] Cannot combine PowerPoint conversion with compression.")
                    sys.exit(1)
                    
            elif target_format:
                # Image format conversion only
                if target_format in ['png', 'jpg', 'jpeg', 'webp']:
                    result_path = convert_image_format(input_path, target_format)
                    return
                elif target_format == 'pptx':
                    result_path = convert_image_to_pptx(input_path)
                    return
                    
            elif target_kb:
                # Image compression only
                result_path = compress_image_to_kb(input_path, target_kb)
                return
        
        # PDF operations
        elif input_ext == '.pdf':
            if not pdf_ops_available:
                console.print(f"[red]✖ Error:[/red] PDF operations require pypdfium2 and pdf2docx. Install with: pip install -e .[pdf]")
                sys.exit(1)
                
            if target_format in ['png', 'jpg', 'jpeg']:
                result_paths = convert_pdf_to_images(input_path, target_format)
                return
            elif target_format == 'docx':
                result_path = convert_pdf_to_docx(input_path)
                return
        
        # Document operations
        elif input_ext == '.txt':
            if not doc_ops_available:
                console.print(f"[red]✖ Error:[/red] Document operations require python-docx. Install with: pip install -e .[office]")
                sys.exit(1)
                
            if target_format == 'docx':
                result_path = convert_txt_to_docx(input_path)
                return
                
        elif input_ext == '.docx':
            if not doc_ops_available:
                console.print(f"[red]✖ Error:[/red] Document operations require python-pptx. Install with: pip install -e .[office]")
                sys.exit(1)
                
            if target_format == 'pptx':
                result_path = convert_docx_to_pptx(input_path)
                return
        
        # Spreadsheet operations
        elif input_ext == '.csv':
            if not doc_ops_available:
                console.print(f"[red]✖ Error:[/red] Spreadsheet operations require pandas and openpyxl. Install with: pip install -e .[data]")
                sys.exit(1)
                
            if target_format == 'xlsx':
                result_path = convert_csv_to_xlsx(input_path)
                return
                
        elif input_ext == '.xlsx':
            if not doc_ops_available:
                console.print(f"[red]✖ Error:[/red] Spreadsheet operations require pandas and openpyxl. Install with: pip install -e .[data]")
                sys.exit(1)
                
            if target_format == 'csv':
                result_path = convert_xlsx_to_csv(input_path)
                return
        
        # If we reach here, the conversion is not supported
        console.print(f"[red]✖ Error:[/red] Conversion from {input_ext} to {target_format} is not supported.")
        console.print(f"Use [cyan]{cmd} --help[/cyan] to see supported conversions.")
        sys.exit(1)
        
    except Exception as e:
        console.print(f"[red]✖ Error during conversion:[/red] {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()