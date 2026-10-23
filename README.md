# File Toolkit CLI

Fast, modular command-line tool for local file conversion, KB-targeted image compression, and package self-updating.

---

## Overview

**File Toolkit CLI** provides fast, local file conversions across PDFs, images, Office documents, and spreadsheets, plus KB-targeted image compression. All conversions and compressions run 100% locally on your machine without external cloud dependencies or privacy risks.

The CLI offers two interchangeable commands:
- **`cv`**: The classic, fast command
- **`ft`**: The modern File Toolkit command

You can use either command interchangeably:
```bash
cv document.pdf -docx
# or
ft document.pdf -docx
```

---

## Installation

### Standard Installation (PyPI)

Install File Toolkit into your current Python environment:

```bash
python -m pip install file-toolkit-cli
```

### Full Installation (Recommended)

To enable all format conversions (PDF, Office documents, and spreadsheets), install with all feature extras:

```bash
python -m pip install "file-toolkit-cli[all]"
```

### Modular Feature-Specific Installation

Install only the feature sets you need:

```bash
# Core + PDF features (PDF→PNG/JPG, PDF→DOCX)
python -m pip install "file-toolkit-cli[pdf]"

# Core + Microsoft Office features (TXT→DOCX, DOCX→PPTX, Image→PPTX)
python -m pip install "file-toolkit-cli[office]"

# Core + Spreadsheet features (CSV ↔ XLSX)
python -m pip install "file-toolkit-cli[data]"
```

### Development / Local Installation

To install in editable mode for local development:

```bash
python -m pip install -e ".[all]"
```

### Quick Verification

Verify that both commands are installed and working:

```bash
cv --help
ft --help
```

---

## Basic Command Syntax

```bash
cv <file_path> -<target_format>                   # Format conversion
cv <file_path> -<target_size>kb                   # Target KB compression
cv <file_path> -<target_format> -<target_size>kb  # Convert + compress
cv update                                        # Self-update to latest version
cv clear                                         # Safely clean temporary data & cache
```
*(All commands also work identically with `ft`)*

---

## Complete Command Reference

### 1. General & Information Commands

```bash
# Display help and usage information
cv --help
ft --help

# Display version information and command aliases
cv --version
ft --version
```

### 2. Self-Update Command

Check PyPI for the newest published release and upgrade automatically in place:

```bash
cv update
# or
ft update
```

> [!NOTE]
> All document/image conversion operations are strictly local and offline. The `update` command is the only operation requiring internet access to query PyPI and upgrade the package.

### 3. Safe Cleanup Command

Safely scan and clean File Toolkit's own internal temporary files, cache, metadata, and logs:

```bash
# Scan and ask for confirmation before deleting
cv clear
# or
ft clear

# Preview what would be removed without deleting anything
cv clear --dry-run
ft clear --dry-run

# Skip the confirmation prompt and delete immediately
cv clear --yes
ft clear --yes
```

> [!IMPORTANT]
> **Safety Guarantee**: The `clear` command only inspects and removes File Toolkit's own internal storage (temporary processing files, cache, metadata, and logs). It **NEVER** deletes:
> - Original input files
> - Converted or compressed output files (PNG, JPG, PDF, DOCX, PPTX, CSV, XLSX)
> - Files in your current working directory, Desktop, Downloads, or Documents
> - Any arbitrary user files

### 4. Image Format Conversion

Convert between popular image formats with automatic transparency handling:

```bash
# Convert PNG to JPEG (flattens transparency with clean white background)
cv photo.png -jpg

# Convert JPEG to PNG
cv photo.jpg -png

# Convert PNG to WebP
cv photo.png -webp

# Convert WebP to JPEG
cv graphic.webp -jpg

# Convert BMP to PNG
cv diagram.bmp -png

# Convert TIFF to JPEG
cv scan.tiff -jpg
```

### 5. Image Compression (KB Targeting)

Compress images to meet strict file size limits (e.g., email attachments, web upload forms, job portals):

```bash
# Compress JPEG to a maximum of 200KB
cv photo.jpg -200kb

# Compress PNG to a maximum of 100KB
cv passport.png -100kb

# Compress WebP to a maximum of 50KB
cv banner.webp -50kb
```

### 6. Combined Conversion + Compression

Convert formats and compress in a single execution:

```bash
# Convert PNG to JPEG and compress to 100KB max
cv header.png -jpg -100kb

# Convert BMP to WebP and compress to 50KB max
ft photo.bmp -webp -50kb

# Convert TIFF to PNG and compress to 150KB max
ft capture.tiff -png -150kb
```

### 7. Image to PowerPoint (PPTX)

Embed images directly into a presentation slide:

```bash
# Create PowerPoint presentation with image scaled to slide
cv photo.png -pptx
ft slide_image.jpg -pptx
```

### 8. PDF Operations

Convert PDF documents to images or editable Microsoft Word files:

```bash
# Convert single- or multi-page PDF into PNG images (2x high-res rendering)
cv document.pdf -png

# Convert PDF into JPEG images
cv document.pdf -jpg

# Convert PDF into an editable Word document with preserved layout
cv report.pdf -docx
```

### 9. Document Operations

Convert text and document formats:

```bash
# Convert plain text file into formatted Microsoft Word document
cv notes.txt -docx

# Convert Word document into Microsoft PowerPoint presentation
cv presentation.docx -pptx
```

### 10. Spreadsheet Operations

Convert between spreadsheet and table formats:

```bash
# Convert CSV spreadsheet to Excel XLSX workbook
cv data.csv -xlsx

# Convert Excel XLSX workbook to CSV spreadsheet
cv financial_report.xlsx -csv
```

---

## Supported Formats Matrix

| Input Format | Supported Outputs | Description |
|---|---|---|
| **PDF** (`.pdf`) | `png`, `jpg`, `docx` | Extract pages as high-res images or editable Word |
| **PNG** (`.png`) | `jpg`, `webp`, `pptx` | Convert format, compress, or generate slide |
| **JPG / JPEG** (`.jpg`, `.jpeg`) | `png`, `webp`, `pptx` | Convert format, compress, or generate slide |
| **WebP** (`.webp`) | `png`, `jpg`, `pptx` | Modern web image optimization |
| **BMP** (`.bmp`) | `png`, `jpg`, `webp`, `pptx` | Bitmap format conversion |
| **TIFF** (`.tiff`, `.tif`) | `png`, `jpg`, `webp`, `pptx` | Tagged Image File conversion |
| **Word** (`.docx`) | `pptx` | Document to presentation conversion |
| **Text** (`.txt`) | `docx` | Plain text to Word document conversion |
| **CSV** (`.csv`) | `xlsx` | Delimited table to Excel spreadsheet |
| **Excel** (`.xlsx`) | `csv` | Excel sheet to CSV table |

---

## Core Features & Guarantees

- **100% Local & Private**: All file conversions happen entirely on your computer. Your files never touch external servers or cloud APIs.
- **Collision-Safe Naming**: Never overwrites existing files. Automatically suffixes output names with `_cv1`, `_cv2`, etc.
  ```text
  photo.jpg (exists) -> photo_cv1.jpg -> photo_cv2.jpg
  ```
- **Path Flexibility**: Handles relative paths, absolute paths, and filenames containing spaces or special characters.
- **Multi-Page PDFs**: Multi-page PDFs automatically produce numbered images:
  ```text
  report.pdf -> report_page_1.png, report_page_2.png, ...
  ```
- **Smart Compression**: Multi-tier optimization adjusts compression quality before gracefully scaling dimensions to meet strict KB caps.
- **Rich Terminal UI**: Formatted status banners, progress feedback, and clean error messages without Python tracebacks.

---

## License

This project is open source and licensed under the [Apache License 2.0](LICENSE).