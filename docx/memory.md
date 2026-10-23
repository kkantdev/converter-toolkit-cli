# File Toolkit CLI - Project Memory

## 📋 Project Overview

**Project Name**: File Toolkit CLI  
**CLI Commands**: `cv`, `ft` (interchangeable aliases)  
**Version**: 0.1.0  
**Purpose**: Local file conversion and image compression tool  
**Status**: ✅ **COMPLETE** - All features implemented and working

## 🏗️ Architecture Summary

### Core Components
- **CLI Entry Point**: `converter/cli.py` - Rich-based UI, argument parsing, validation (supports `cv` and `ft`)
- **Self-Update**: `converter/update.py` - PyPI version check, semantic version comparison, pip upgrade & verification
- **Safe Cleanup**: `converter/clean.py` - Scans and removes internal temp files, cache, metadata, and logs
- **Image Operations**: `converter/image_ops.py` - Format conversion, KB compression, image→PPTX
- **PDF Operations**: `converter/pdf_ops.py` - PDF→PNG/JPG, PDF→DOCX  
- **Document Operations**: `converter/doc_ops.py` - TXT→DOCX, DOCX→PPTX, CSV↔XLSX

### Key Features
- ✅ **Collision-safe naming**: Never overwrites files (uses `_cv1`, `_cv2`, etc.)
- ✅ **Rich terminal UI**: Progress spinners, colored output, professional help
- ✅ **Modular dependencies**: Optional feature groups, graceful error handling
- ✅ **Cross-platform**: Windows/macOS/Linux with proper path handling

## 🛠️ All Available Commands

### Basic Commands
```bash
cv --help                    # Show comprehensive help with examples (or ft --help)
cv --version                 # Show version information (or ft --version)
cv update                    # Check for and install latest version from PyPI (or ft update)
cv clear                     # Scan and safely remove internal temp files and cache (or ft clear)
cv clear --dry-run           # Preview cleanup without deleting files
cv clear --yes               # Clean immediately without confirmation prompt
```

### Image Format Conversion
```bash
cv image.png -jpg           # PNG to JPEG
cv image.jpg -png           # JPEG to PNG  
cv image.png -webp          # PNG to WebP
cv image.webp -jpg          # WebP to JPEG
cv image.bmp -png           # BMP to PNG
cv image.tiff -jpg          # TIFF to JPEG
```

### Image Compression (KB Targeting)
```bash
cv image.jpg -100kb         # Compress JPEG to 100KB max
cv photo.png -50kb          # Compress PNG to 50KB max
cv banner.webp -200kb       # Compress WebP to 200KB max
```

### Combined Conversion + Compression
```bash
cv image.png -jpg -100kb    # Convert PNG to JPEG and compress to 100KB
cv photo.bmp -webp -50kb    # Convert BMP to WebP and compress to 50KB
cv header.tiff -png -150kb  # Convert TIFF to PNG and compress to 150KB
```

### Image to PowerPoint
```bash
cv photo.png -pptx          # Create PowerPoint with image as slide
cv image.jpg -pptx          # JPEG to PowerPoint presentation
cv graphic.webp -pptx       # WebP to PowerPoint presentation
```

### PDF Operations  
```bash
cv document.pdf -png        # PDF pages to PNG images
cv document.pdf -jpg        # PDF pages to JPEG images
cv document.pdf -docx       # PDF to editable Word document
```

### Document Operations
```bash
cv notes.txt -docx          # Text file to Word document
cv document.docx -pptx      # Word document to PowerPoint presentation
```

### Spreadsheet Operations
```bash
cv data.csv -xlsx           # CSV to Excel file
cv spreadsheet.xlsx -csv    # Excel to CSV file
```

## 📦 Installation Commands

### From PyPI
```bash
pip install file-toolkit-cli        # Core features (image conversion & compression)
pip install file-toolkit-cli[all]   # All features (PDF, Office, Spreadsheets)
```

### Local / Source Installation
```bash
pip install .               # Core features only (images)
pip install .[pdf]          # PDF operations (pypdfium2, pdf2docx)
pip install .[office]       # Office docs (python-pptx, python-docx)
pip install .[data]         # Spreadsheets (pandas, openpyxl)
pip install .[all]          # All features
pip install .[dev]          # Development tools (pytest, twine, build)
```

### Development Installation
```bash
pip install -e .[all,dev]   # Editable install with all features + testing
```

## 🔧 Development Commands

### Testing
```bash
pytest                      # Run all 50 tests
pytest tests/test_cli.py    # Run CLI entry point & validation tests (15 passed)
pytest tests/test_update.py # Run update command tests (17 passed)
pytest tests/test_clean.py  # Run clean command tests (18 passed)
pytest -v                   # Verbose test output
pytest --cov=converter      # Run with coverage report
```

### Package Building
```bash
python -m build             # Build wheel and source distribution
twine check dist/*          # Verify distribution package metadata
pip install dist/*.whl      # Install built package locally
```

### Project Structure
```bash
file-toolkit-cli/
├── converter/                  # Main package
│   ├── __init__.py            # Version: 0.1.0
│   ├── cli.py                 # CLI entry point (cv / ft commands)
│   ├── update.py              # Package self-update & PyPI check
│   ├── clean.py               # Safe cleanup of internal temp & cache
│   ├── image_ops.py           # Image conversion & compression  
│   ├── pdf_ops.py             # PDF operations
│   └── doc_ops.py             # Document & spreadsheet operations
├── tests/                     # Automated test suite (50 tests passing)
│   ├── test_cli.py            # CLI parsing, aliases, and validation tests
│   ├── test_update.py         # Self-update logic and subprocess tests
│   └── test_clean.py          # Safe cleanup and protection guard tests
├── docx/                      # Project documentation
│   ├── architecture.md        # Technical architecture details
│   ├── memory.md              # Project memory and reference
│   ├── product.md             # Product requirements & roadmap
│   └── test.md                # Testing status and test logs
├── pyproject.toml             # Build system & package metadata (PEP 517/621)
├── README.md                  # Comprehensive user guide
├── PACKAGE_PUBLISHING.md      # PyPI publishing & release verification guide
└── LICENSE                    # Apache 2.0 license
```

## 🎯 Supported Conversions Matrix

| From | To | Command Example |
|------|----|----|
| **Images** | | |
| PNG | JPG, WebP, PPTX | `cv image.png -jpg` |
| JPG | PNG, WebP, PPTX | `cv image.jpg -webp` |
| WebP | PNG, JPG, PPTX | `cv image.webp -png` |
| BMP/TIFF | PNG, JPG, WebP, PPTX | `cv image.bmp -jpg` |
| **PDF** | | |
| PDF | PNG, JPG, DOCX | `cv doc.pdf -png` |
| **Documents** | | |
| TXT | DOCX | `cv notes.txt -docx` |
| DOCX | PPTX | `cv doc.docx -pptx` |
| **Spreadsheets** | | |
| CSV | XLSX | `cv data.csv -xlsx` |
| XLSX | CSV | `cv data.xlsx -csv` |

## 🚨 Important Implementation Notes

### Collision Prevention
- **Never overwrites existing files**
- Uses pattern: `file.jpg` → `file_cv1.jpg` → `file_cv2.jpg`
- Applies to all operations including multi-page PDFs

### Error Handling  
- **No raw Python tracebacks** shown to users
- **Helpful error messages** with installation guidance
- **Graceful dependency handling** with clear instructions

### Compression Algorithm
- **Quality reduction**: 95 → 90 → 85 → ... → 10 (by steps of 5)
- **Dimension scaling**: 100% → 80% → 64% → 51.2% → ... (20% reduction per step)
- **Format optimization**: Chooses best format for compression (PNG→JPEG when beneficial)

### Multi-page PDF Handling
- **Single page**: `report.pdf` → `report.png`
- **Multiple pages**: `report.pdf` → `report_page_1.png`, `report_page_2.png`, etc.
- **Collision-safe**: `report_page_1.png` exists → `report_page_1_cv1.png`

## 🔧 Common Modifications

### Adding New Format Support
1. **Update compatibility matrix** in `cli.py` (`validate_conversion_compatibility`)
2. **Add conversion logic** in appropriate module (`image_ops.py`, etc.)
3. **Update help text** and documentation
4. **Add tests** for new format

### Adding New Dependencies
1. **Add to pyproject.toml** in appropriate optional group
2. **Import with try/catch** and provide helpful error message
3. **Test graceful degradation** when dependency missing

### Modifying Compression Algorithm
- **Edit `_compress_with_algorithm`** in `image_ops.py`
- **Adjust quality levels or scaling factors** as needed
- **Test with various image types and sizes**

## 📝 Future Agent Instructions

**If another agent needs to modify this project:**

1. **Read this memory.md** for complete understanding
2. **Check test.md** for current testing status  
3. **Use commands above** for development setup
4. **Follow architecture patterns** established in existing modules
5. **Maintain Rich UI consistency** for user-facing output
6. **Preserve collision-safe naming** behavior
7. **Keep modular dependency structure** with helpful error messages

**Key files to understand:**
- `converter/cli.py` - Main entry point and validation logic
- `converter/image_ops.py` - Core image processing (most complex)  
- `pyproject.toml` - Package configuration and dependencies

**Testing approach:**
- **Check test.md** for remaining test items
- **Create sample files** for testing each conversion type
- **Test with and without** optional dependencies installed
- **Verify collision handling** with existing output files