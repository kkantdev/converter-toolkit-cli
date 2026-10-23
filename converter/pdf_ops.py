"""
PDF conversion operations using pypdfium2 and pdf2docx.
"""

from pathlib import Path
from typing import List, Optional

from PIL import Image
from rich.console import Console

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


def convert_pdf_to_images(input_path: Path, target_format: str, output_dir: Optional[Path] = None) -> List[Path]:
    """
    Convert PDF pages to image files.
    
    Args:
        input_path: Path to input PDF file
        target_format: Target format ('png', 'jpg')
        output_dir: Optional output directory (same as input if None)
        
    Returns:
        List of paths to generated image files
        
    Raises:
        Exception: If conversion fails
    """
    try:
        import pypdfium2 as pdfium
    except ImportError:
        raise ImportError("pypdfium2 is required for PDF conversion. Install with: pip install .[pdf]")
    
    if output_dir is None:
        output_dir = input_path.parent
    
    target_format = target_format.lower()
    if target_format == 'jpeg':
        target_format = 'jpg'
    
    try:
        console.print(f"[cyan]Converting PDF {input_path.name} to {target_format.upper()} images...[/cyan]")
        
        with console.status(f"Processing PDF pages", spinner="dots"):
            # Open PDF
            pdf = pdfium.PdfDocument(input_path)
            page_count = len(pdf)
            
            output_paths = []
            
            for i in range(page_count):
                # Render page at 2x scale for better quality
                page = pdf.get_page(i)
                bitmap = page.render(scale=2.0)
                pil_image = bitmap.to_pil()
                
                # Generate output filename
                if page_count == 1:
                    # Single page - use simple naming
                    output_name = f"{input_path.stem}.{target_format}"
                else:
                    # Multi-page - use page numbering
                    output_name = f"{input_path.stem}_page_{i+1}.{target_format}"
                
                output_path = output_dir / output_name
                safe_output_path = resolve_output_path(output_path)
                
                # Save image
                if target_format == 'jpg':
                    # Convert to RGB for JPEG
                    if pil_image.mode in ('RGBA', 'LA', 'P'):
                        # Create white background
                        background = pil_image.mode == 'RGBA' and pil_image or pil_image.convert('RGBA')
                        white_bg = Image.new('RGB', background.size, (255, 255, 255))
                        white_bg.paste(background, mask=background.split()[-1] if background.mode == 'RGBA' else None)
                        pil_image = white_bg
                    elif pil_image.mode != 'RGB':
                        pil_image = pil_image.convert('RGB')
                    
                    pil_image.save(safe_output_path, 'JPEG', quality=95, optimize=True)
                    
                elif target_format == 'png':
                    pil_image.save(safe_output_path, 'PNG', optimize=True)
                
                output_paths.append(safe_output_path)
                
                # Clean up
                page.close()
                bitmap.close()
            
            pdf.close()
        
        console.print(f"[green]✔ Successfully converted PDF to {len(output_paths)} image(s)![/green]")
        console.print("[bold]Output files:[/bold]")
        for path in output_paths:
            console.print(f"  {path}")
        
        return output_paths
        
    except Exception as e:
        console.print(f"[red]✖ Error during PDF conversion:[/red] {str(e)}")
        raise


def convert_pdf_to_docx(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Convert PDF to Word document.
    
    Args:
        input_path: Path to input PDF file
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to Word document file
        
    Raises:
        Exception: If conversion fails
    """
    try:
        from pdf2docx import Converter
    except ImportError:
        raise ImportError("pdf2docx is required for PDF to DOCX conversion. Install with: pip install .[pdf]")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.with_suffix('.docx')
    
    # Resolve collision-safe output path
    safe_output_path = resolve_output_path(output_path)
    
    try:
        console.print(f"[cyan]Converting PDF {input_path.name} to Word document...[/cyan]")
        
        with console.status("Converting PDF to DOCX", spinner="dots"):
            # Convert PDF to DOCX
            cv = Converter(str(input_path))
            cv.convert(str(safe_output_path), start=0, end=None)
            cv.close()
        
        console.print(f"[green]✔ Successfully converted PDF to Word document![/green]")
        console.print(f"[bold]Output saved to:[/bold]\n{safe_output_path}")
        
        return safe_output_path
        
    except Exception as e:
        console.print(f"[red]✖ Error during PDF to DOCX conversion:[/red] {str(e)}")
        raise