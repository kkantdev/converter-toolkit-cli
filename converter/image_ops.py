"""
Image conversion and compression operations using Pillow.
"""

import io
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image, ImageFile
from rich.console import Console

console = Console()

# Enable loading of truncated images for better compatibility
ImageFile.LOAD_TRUNCATED_IMAGES = True


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


def convert_image_format(input_path: Path, target_format: str, output_path: Optional[Path] = None) -> Path:
    """
    Convert image between supported formats.
    
    Args:
        input_path: Path to input image file
        target_format: Target format ('png', 'jpg', 'webp')
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to converted image file
        
    Raises:
        Exception: If conversion fails
    """
    # Normalize target format
    target_format = target_format.lower()
    if target_format == 'jpeg':
        target_format = 'jpg'
    
    # Generate output path if not provided
    if output_path is None:
        extension_map = {
            'png': '.png',
            'jpg': '.jpg', 
            'webp': '.webp'
        }
        
        if target_format not in extension_map:
            raise ValueError(f"Unsupported target format: {target_format}")
            
        output_path = input_path.with_suffix(extension_map[target_format])
    
    # Resolve collision-safe output path
    safe_output_path = resolve_output_path(output_path)
    
    try:
        console.print(f"[cyan]Converting {input_path.name} to {target_format.upper()}...[/cyan]")
        
        with console.status(f"Converting to {target_format.upper()}", spinner="dots"):
            # Open and process the image
            with Image.open(input_path) as img:
                # Handle different conversion scenarios
                if target_format == 'jpg':
                    # Convert to RGB for JPEG (handle transparency)
                    converted_img = _convert_to_jpeg_compatible(img)
                    converted_img.save(safe_output_path, 'JPEG', quality=95, optimize=True)
                    
                elif target_format == 'png':
                    # PNG supports all modes, but optimize for best compatibility
                    if img.mode in ('RGBA', 'LA', 'P'):
                        converted_img = img
                    else:
                        # Convert to RGBA for maximum compatibility
                        converted_img = img.convert('RGBA')
                    converted_img.save(safe_output_path, 'PNG', optimize=True)
                    
                elif target_format == 'webp':
                    # WebP supports both RGB and RGBA
                    if img.mode in ('RGBA', 'LA'):
                        converted_img = img.convert('RGBA')
                    else:
                        converted_img = img.convert('RGB')
                    converted_img.save(safe_output_path, 'WEBP', quality=95, optimize=True)
                    
                else:
                    raise ValueError(f"Unsupported target format: {target_format}")
        
        console.print(f"[green]✔ Successfully converted![/green]")
        console.print(f"[bold]Output saved to:[/bold]\n{safe_output_path}")
        
        return safe_output_path
        
    except Exception as e:
        console.print(f"[red]✖ Error during conversion:[/red] {str(e)}")
        raise


def _convert_to_jpeg_compatible(img: Image.Image) -> Image.Image:
    """
    Convert image to JPEG-compatible RGB format, handling transparency properly.
    
    Args:
        img: PIL Image object
        
    Returns:
        RGB PIL Image suitable for JPEG output
    """
    if img.mode == 'RGB':
        return img
    
    if img.mode in ('RGBA', 'LA', 'P'):
        # Create white background for transparent images
        if img.mode == 'P':
            # Convert palette mode to RGBA first to handle transparency
            img = img.convert('RGBA')
        
        # Create white background
        background = Image.new('RGB', img.size, (255, 255, 255))
        
        if img.mode in ('RGBA', 'LA'):
            # Composite image onto white background
            background.paste(img, mask=img.split()[-1])  # Use alpha channel as mask
        else:
            background.paste(img)
            
        return background
    
    # For other modes (L, CMYK, etc.), convert directly to RGB
    return img.convert('RGB')


def compress_image_to_kb(input_path: Path, target_kb: int, output_path: Optional[Path] = None) -> Path:
    """
    Compress image to target KB size using quality reduction and dimension scaling.
    
    Args:
        input_path: Path to input image file
        target_kb: Target size in KB
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to compressed image file
        
    Raises:
        Exception: If compression fails
    """
    if target_kb <= 0:
        raise ValueError("Target KB size must be greater than 0")
    
    target_bytes = target_kb * 1024
    
    # Generate output path if not provided
    if output_path is None:
        # Preserve original format for compression-only operations
        output_path = input_path.with_stem(f"{input_path.stem}_compressed")
    
    # Resolve collision-safe output path
    safe_output_path = resolve_output_path(output_path)
    
    try:
        console.print(f"[cyan]Compressing {input_path.name} to {target_kb}KB...[/cyan]")
        
        with console.status(f"Compressing to {target_kb}KB", spinner="dots"):
            # Open and process the image
            with Image.open(input_path) as img:
                # Get original dimensions and format
                original_width, original_height = img.size
                original_format = _determine_compression_format(input_path)
                
                # Try compression with different quality levels and dimensions
                result_path = _compress_with_algorithm(
                    img, safe_output_path, target_bytes, original_format
                )
        
        # Verify final file size
        final_size_kb = result_path.stat().st_size / 1024
        
        console.print(f"[green]✔ Successfully compressed![/green]")
        console.print(f"[bold]Final size:[/bold] {final_size_kb:.1f}KB (target: {target_kb}KB)")
        console.print(f"[bold]Output saved to:[/bold]\n{result_path}")
        
        return result_path
        
    except Exception as e:
        console.print(f"[red]✖ Error during compression:[/red] {str(e)}")
        raise


def _determine_compression_format(input_path: Path) -> str:
    """
    Determine the best compression format for the input file.
    
    Args:
        input_path: Path to input file
        
    Returns:
        Format string ('JPEG', 'PNG', 'WEBP')
    """
    input_ext = input_path.suffix.lower()
    
    # For PNG files that might need aggressive compression, consider JPEG
    if input_ext == '.png':
        try:
            with Image.open(input_path) as img:
                # If image has no transparency, JPEG will be more efficient
                if img.mode in ('RGB', 'L'):
                    return 'JPEG'
                # If image has transparency, keep as PNG
                return 'PNG'
        except:
            return 'PNG'
    
    # For JPEG files, keep as JPEG
    elif input_ext in ['.jpg', '.jpeg']:
        return 'JPEG'
    
    # For WebP files, keep as WebP
    elif input_ext == '.webp':
        return 'WEBP'
    
    # For other formats, convert to JPEG for best compression
    else:
        return 'JPEG'


def _compress_with_algorithm(img: Image.Image, output_path: Path, target_bytes: int, format_type: str) -> Path:
    """
    Compress image using quality reduction and dimension scaling algorithm.
    
    Args:
        img: PIL Image object
        output_path: Output file path
        target_bytes: Target file size in bytes
        format_type: Output format ('JPEG', 'PNG', 'WEBP')
        
    Returns:
        Path to compressed image file
    """
    original_size = img.size
    current_img = img.copy()
    
    # Quality levels to try (from high to low)
    quality_levels = list(range(95, 9, -5))  # [95, 90, 85, ..., 15, 10]
    
    # Dimension scaling factors
    scale_factors = [1.0, 0.8, 0.64, 0.512, 0.41, 0.328, 0.262, 0.21]
    
    for scale_factor in scale_factors:
        # Scale image dimensions if needed
        if scale_factor < 1.0:
            new_width = max(1, int(original_size[0] * scale_factor))
            new_height = max(1, int(original_size[1] * scale_factor))
            current_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Try different quality levels at this scale
        for quality in quality_levels:
            buffer = io.BytesIO()
            
            try:
                # Save image to memory buffer with current settings
                if format_type == 'JPEG':
                    # Convert to RGB for JPEG if needed
                    save_img = _convert_to_jpeg_compatible(current_img)
                    save_img.save(buffer, 'JPEG', quality=quality, optimize=True)
                    
                elif format_type == 'PNG':
                    # PNG doesn't use quality parameter, but we can optimize
                    save_img = current_img
                    if save_img.mode not in ('RGBA', 'LA', 'P'):
                        save_img = save_img.convert('RGBA')
                    save_img.save(buffer, 'PNG', optimize=True)
                    
                elif format_type == 'WEBP':
                    # WebP supports quality parameter
                    save_img = current_img
                    if save_img.mode in ('RGBA', 'LA'):
                        save_img = save_img.convert('RGBA')
                    else:
                        save_img = save_img.convert('RGB')
                    save_img.save(buffer, 'WEBP', quality=quality, optimize=True)
                
                # Check if we've achieved the target size
                current_size = buffer.tell()
                
                if current_size <= target_bytes:
                    # Success! Save the compressed image
                    buffer.seek(0)
                    
                    # Determine output extension
                    if format_type == 'JPEG':
                        final_path = output_path.with_suffix('.jpg')
                    elif format_type == 'PNG':
                        final_path = output_path.with_suffix('.png')
                    elif format_type == 'WEBP':
                        final_path = output_path.with_suffix('.webp')
                    
                    # Resolve collision-safe path again in case extension changed
                    final_path = resolve_output_path(final_path)
                    
                    with open(final_path, 'wb') as f:
                        f.write(buffer.getvalue())
                    
                    return final_path
                    
            except Exception:
                # Skip this quality/scale combination if it fails
                continue
            
            # For PNG, quality doesn't apply, so break after first attempt
            if format_type == 'PNG':
                break
    
    # If we couldn't reach the target, save the most compressed version
    console.print("[yellow]⚠ Warning:[/yellow] Could not reach exact target size. Saving most compressed version.")
    
    # Use the most aggressive settings
    buffer = io.BytesIO()
    
    # Use smallest scale
    final_scale = scale_factors[-1]
    new_width = max(1, int(original_size[0] * final_scale))
    new_height = max(1, int(original_size[1] * final_scale))
    final_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    if format_type == 'JPEG':
        save_img = _convert_to_jpeg_compatible(final_img)
        save_img.save(buffer, 'JPEG', quality=10, optimize=True)
        final_path = output_path.with_suffix('.jpg')
    elif format_type == 'PNG':
        save_img = final_img
        if save_img.mode not in ('RGBA', 'LA', 'P'):
            save_img = save_img.convert('RGBA')
        save_img.save(buffer, 'PNG', optimize=True)
        final_path = output_path.with_suffix('.png')
    elif format_type == 'WEBP':
        save_img = final_img
        if save_img.mode in ('RGBA', 'LA'):
            save_img = save_img.convert('RGBA')
        else:
            save_img = save_img.convert('RGB')
        save_img.save(buffer, 'WEBP', quality=10, optimize=True)
        final_path = output_path.with_suffix('.webp')
    
    # Save the final result
    final_path = resolve_output_path(final_path)
    buffer.seek(0)
    with open(final_path, 'wb') as f:
        f.write(buffer.getvalue())
    
    return final_path


def convert_and_compress_image(input_path: Path, target_format: str, target_kb: int, output_path: Optional[Path] = None) -> Path:
    """
    Convert image format AND compress to target KB size in one operation.
    
    Args:
        input_path: Path to input image file
        target_format: Target format ('png', 'jpg', 'webp')
        target_kb: Target size in KB
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to converted and compressed image file
        
    Raises:
        Exception: If conversion or compression fails
    """
    if target_kb <= 0:
        raise ValueError("Target KB size must be greater than 0")
    
    target_bytes = target_kb * 1024
    
    # Normalize target format
    target_format = target_format.lower()
    if target_format == 'jpeg':
        target_format = 'jpg'
    
    # Generate output path if not provided
    if output_path is None:
        extension_map = {
            'png': '.png',
            'jpg': '.jpg', 
            'webp': '.webp'
        }
        
        if target_format not in extension_map:
            raise ValueError(f"Unsupported target format: {target_format}")
            
        output_path = input_path.with_suffix(extension_map[target_format])
    
    # Resolve collision-safe output path
    safe_output_path = resolve_output_path(output_path)
    
    try:
        console.print(f"[cyan]Converting {input_path.name} to {target_format.upper()} and compressing to {target_kb}KB...[/cyan]")
        
        with console.status(f"Converting to {target_format.upper()} and compressing", spinner="dots"):
            # Open and process the image
            with Image.open(input_path) as img:
                # Determine the target format for compression algorithm
                format_map = {
                    'png': 'PNG',
                    'jpg': 'JPEG',
                    'webp': 'WEBP'
                }
                
                format_type = format_map[target_format]
                
                # Use the compression algorithm with the target format
                result_path = _compress_with_algorithm(
                    img, safe_output_path, target_bytes, format_type
                )
        
        # Verify final file size
        final_size_kb = result_path.stat().st_size / 1024
        
        console.print(f"[green]✔ Successfully converted and compressed![/green]")
        console.print(f"[bold]Final size:[/bold] {final_size_kb:.1f}KB (target: {target_kb}KB)")
        console.print(f"[bold]Output saved to:[/bold]\n{result_path}")
        
        return result_path
        
    except Exception as e:
        console.print(f"[red]✖ Error during conversion and compression:[/red] {str(e)}")
        raise
    """
    Convert image to PowerPoint presentation.
    
    Args:
        input_path: Path to input image file
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to PowerPoint file
        
    Raises:
        Exception: If conversion fails
    """
    raise NotImplementedError("Image to PowerPoint conversion will be implemented in task 4")


def convert_image_to_pptx(input_path: Path, output_path: Optional[Path] = None) -> Path:
    """
    Convert image to PowerPoint presentation.
    
    Args:
        input_path: Path to input image file
        output_path: Optional output path (auto-generated if None)
        
    Returns:
        Path to PowerPoint file
        
    Raises:
        Exception: If conversion fails
    """
    try:
        from pptx import Presentation
        from pptx.util import Inches
    except ImportError:
        raise ImportError("python-pptx is required for PowerPoint conversion. Install with: pip install .[office]")
    
    # Generate output path if not provided
    if output_path is None:
        output_path = input_path.with_suffix('.pptx')
    
    # Resolve collision-safe output path
    safe_output_path = resolve_output_path(output_path)
    
    try:
        console.print(f"[cyan]Converting {input_path.name} to PowerPoint presentation...[/cyan]")
        
        with console.status("Creating PowerPoint presentation", spinner="dots"):
            # Create a new presentation with 16:9 widescreen layout
            prs = Presentation()
            
            # Remove default slide and add blank slide
            if prs.slides:
                # Clear default slides
                prs.slides._sldIdLst.clear()
            
            # Add a blank slide
            blank_slide_layout = prs.slide_layouts[6]  # Blank layout
            slide = prs.slides.add_slide(blank_slide_layout)
            
            # Open and get image dimensions
            with Image.open(input_path) as img:
                img_width, img_height = img.size
                img_ratio = img_width / img_height
            
            # Calculate slide dimensions (16:9 aspect ratio)
            slide_width = prs.slide_width
            slide_height = prs.slide_height
            slide_ratio = slide_width / slide_height
            
            # Calculate image placement to maintain aspect ratio and center it
            if img_ratio > slide_ratio:
                # Image is wider than slide ratio - fit by width
                pic_width = slide_width * 0.9  # Use 90% of slide width for margins
                pic_height = pic_width / img_ratio
            else:
                # Image is taller than slide ratio - fit by height  
                pic_height = slide_height * 0.9  # Use 90% of slide height for margins
                pic_width = pic_height * img_ratio
            
            # Center the image on the slide
            left = (slide_width - pic_width) / 2
            top = (slide_height - pic_height) / 2
            
            # Add image to slide
            slide.shapes.add_picture(
                str(input_path), 
                int(left), 
                int(top), 
                int(pic_width), 
                int(pic_height)
            )
            
            # Save presentation
            prs.save(safe_output_path)
        
        console.print(f"[green]✔ Successfully created PowerPoint presentation![/green]")
        console.print(f"[bold]Output saved to:[/bold]\n{safe_output_path}")
        
        return safe_output_path
        
    except Exception as e:
        console.print(f"[red]✖ Error during PowerPoint creation:[/red] {str(e)}")
        raise