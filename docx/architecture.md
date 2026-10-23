# Architecture Document - File Toolkit CLI

## Overview

The File Toolkit CLI is designed as a modular, progressive Python application that provides local file conversion and image compression functionality through a unified command-line interface.

## Project Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interface Layer                    │
├─────────────────────────────────────────────────────────────┤
│  CLI Entry Point (cli.py)                                  │
│  - Dual commands: cv and ft                                 │
│  - Argument parsing and validation                          │
│  - Rich UI formatting (help, progress, errors)             │
│  - Path resolution and collision prevention                 │
│  - Operation dispatch (conversions, update, clear)          │
└─────────────────────────────────────────────────────────────┘
          │                         │                  │
          ▼                         ▼                  ▼
┌──────────────────┐      ┌──────────────────┐ ┌───────────────┐
│ Conversion Layer │      │ Self-Update      │ │ Safe Cleanup  │
├──────────────────┤      ├──────────────────┤ ├───────────────┤
│ • image_ops.py   │      │ update.py        │ │ clean.py      │
│ • pdf_ops.py     │      │ - PyPI check     │ │ - Temp & cache│
│ • doc_ops.py     │      │ - pip upgrade    │ │ - Confirmation│
│                  │      │ - Verification   │ │ - Dry-run     │
└──────────────────┘      └──────────────────┘ └───────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Library Layer                             │
├─────────────────────────────────────────────────────────────┤
│  Pillow    │ pypdfium2   │ python-pptx │ pandas            │ │
│  (images)  │ (PDF render)│ (PowerPoint)│ (spreadsheets)    │ │
│            │ pdf2docx    │ python-docx │ openpyxl         │ │
│            │ (PDF→DOCX)  │ (Word docs) │                   │ │
└─────────────────────────────────────────────────────────────┘
```

### Module Responsibilities

#### `converter/cli.py` - Command Line Interface
**Primary Responsibilities:**
- Argument parsing and validation (supports `cv` and `ft` entry points)
- Input file validation (existence, format, compatibility)
- Flag parsing (`-format`, `-sizeKB`, `update` command)
- Rich-based user interface (help, version, progress, errors)
- Path resolution and collision-safe output naming
- Conversion operation dispatch to appropriate modules
- Error handling and user-friendly error messages

**Key Functions:**
- `main()` - Entry point and argument processing
- `get_command_name()` - Detects `cv` or `ft` execution alias
- `parse_format_flag()` / `parse_kb_flag()` - Flag parsing
- `validate_input_file()` / `validate_conversion_compatibility()` - Validation
- `resolve_output_path()` - Collision-safe file naming
- `show_help()` / `show_version()` - Rich UI output

#### `converter/update.py` - Self-Update Management
**Primary Responsibilities:**
- Query PyPI JSON API for latest package releases
- Dynamic installed version detection
- Robust semantic version comparison
- Invoking `pip install --upgrade` via current Python interpreter
- Post-install version verification

**Key Functions:**
- `get_current_version()` - Reads metadata version or fallback
- `get_latest_version()` - Queries PyPI JSON API with timeout & error handling
- `compare_versions()` - Semantic version ordering
- `perform_update()` - Runs pip upgrade in subprocess
- `verify_update()` - Validates installed version in fresh process
- `run_update()` - End-to-end update workflow with Rich UI

#### `converter/clean.py` - Safe Cleanup Management
**Primary Responsibilities:**
- Identify cross-platform storage locations owned by File Toolkit
- Scan and calculate exact byte sizes of internal temporary data, cache, metadata, and logs
- Strict safety verification ensuring zero deletion of user files, working directory, or system folders
- Interactive user confirmation with optional `--yes` and `--dry-run` modes

**Key Functions:**
- `get_cleanup_locations()` - Cross-platform paths for temporary files, cache, metadata, and logs
- `is_safe_to_delete()` - Strict safety guard against deleting user or external files
- `scan_cleanup_data()` - Calculates category sizes and finds eligible paths
- `perform_cleanup()` - Safely removes internal files and reports freed space
- `run_clear()` - Clear workflow orchestration with Rich UI

#### `converter/image_ops.py` - Image Processing
**Primary Responsibilities:**
- Image format conversion (PNG ↔ JPG ↔ WebP)
- KB compression using quality reduction + dimension scaling
- Image to PowerPoint conversion
- Transparency handling for format conversions

**Key Functions:**
- `convert_image_format()` - Format conversion with transparency handling
- `compress_image_to_kb()` - KB compression algorithm
- `convert_image_to_pptx()` - Image to PowerPoint slide

**Dependencies:** Pillow (PIL), python-pptx

#### `converter/pdf_ops.py` - PDF Processing  
**Primary Responsibilities:**
- PDF to image conversion (PNG, JPG) with multi-page support
- PDF to Word document conversion
- 2x scale rendering for high-quality output
- Resource cleanup and memory management

**Key Functions:**
- `convert_pdf_to_images()` - Multi-page PDF to images
- `convert_pdf_to_docx()` - PDF to Word with layout preservation

**Dependencies:** pypdfium2, pdf2docx

#### `converter/doc_ops.py` - Document & Spreadsheet Processing
**Primary Responsibilities:**
- Text to Word document conversion
- Word to PowerPoint conversion  
- CSV ↔ Excel conversion
- Spreadsheet error handling (malformed files, encoding issues)

**Key Functions:**
- `convert_txt_to_docx()` - Text file to Word document
- `convert_docx_to_pptx()` - Word paragraphs to PowerPoint slides
- `convert_csv_to_xlsx()` / `convert_xlsx_to_csv()` - Spreadsheet conversion

**Dependencies:** python-docx, python-pptx, pandas, openpyxl

## CLI Flow

### Argument Processing Flow
```
User Input → Parse Arguments → Validate Flags → Validate File
     │              │               │              │
     ▼              ▼               ▼              ▼
cv file.png -jpg -100kb → format=jpg, kb=100 → Valid flags → File exists & supported
     │
     ▼
Validate Compatibility → Dispatch Operation → Execute Conversion → Output Result
     │                        │                     │              │
     ▼                        ▼                     ▼              ▼
PNG→JPG supported → image_ops.convert_image_format() → Pillow processing → Success message
```

### Conversion Dispatch Matrix
| Input Extension | Target Format | Handler Module | Function |
|-----------------|---------------|----------------|----------|
| .pdf | png, jpg | pdf_ops | convert_pdf_to_images() |
| .pdf | docx | pdf_ops | convert_pdf_to_docx() |
| .png, .jpg, .webp, etc. | png, jpg, webp | image_ops | convert_image_format() |
| .png, .jpg, .webp, etc. | pptx | image_ops | convert_image_to_pptx() |
| .txt | docx | doc_ops | convert_txt_to_docx() |
| .docx | pptx | doc_ops | convert_docx_to_pptx() |
| .csv | xlsx | doc_ops | convert_csv_to_xlsx() |
| .xlsx | csv | doc_ops | convert_xlsx_to_csv() |

## KB Compression Algorithm

### Quality Reduction Strategy
```
Start: JPEG Quality 95
Step 1: Try qualities [95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 30, 25, 20, 15, 10]
       └─ If file_size ≤ target_kb: SUCCESS

Step 2: Reduce dimensions by 20% (scale = 0.8)
       └─ Repeat quality reduction at new dimensions
       
Step 3: Continue dimension scaling [0.8, 0.64, 0.512, 0.41, ...]
       └─ At each scale, try full quality range
       
Stop when: file_size ≤ target_kb OR practical limits reached
```

### Processing Order for Combined Operations
```
Input File → Format Conversion → KB Compression → Final Output
    │              │                    │              │
    ▼              ▼                    ▼              ▼
image.png → image.jpg (quality=95) → compress to target → final.jpg
```

## Collision Prevention System

### Safe Output Naming Algorithm
```python
def resolve_output_path(target_path: Path) -> Path:
    if not target_path.exists():
        return target_path
    
    # Generate collision-safe names: file_cv1.ext, file_cv2.ext, etc.
    counter = 1
    while True:
        candidate = parent / f"{stem}_cv{counter}{suffix}"
        if not candidate.exists():
            return candidate
        counter += 1
```

### Multi-page PDF Naming
```
Single page:  report.pdf → report.png
Multi-page:   report.pdf → report_page_1.png, report_page_2.png, report_page_3.png

With collision: report_page_1.png exists → report_page_1_cv1.png
```

## Error Handling Strategy

### Validation Layers
1. **Argument Validation**: Flag format, KB values, file paths
2. **File Validation**: Existence, type, extension support  
3. **Compatibility Validation**: Input/output format combinations
4. **Runtime Validation**: File corruption, permission errors, resource limits

### Error Message Design
- **User-friendly**: No raw Python tracebacks exposed
- **Actionable**: Clear explanation of what went wrong
- **Rich formatting**: Red ✖ for errors, yellow ⚠ for warnings
- **Contextual**: Include file paths and attempted operations

### Resource Management
- Context managers for file operations
- Proper cleanup of temporary files
- Memory-efficient processing for large files
- Graceful degradation on resource constraints

## Dependency Management

### Core Dependencies (Always Installed)
- `rich>=13.0.0` - Terminal UI, progress indicators, formatting
- `Pillow>=9.0.0` - Image processing foundation
- `packaging>=20.0` - Semantic version comparison for package self-update

### Optional Dependencies (Feature Groups)
- `pdf` group: pypdfium2, pdf2docx
- `office` group: python-pptx, python-docx  
- `data` group: pandas, openpyxl
- `all` group: All optional dependencies
- `dev` group: pytest, twine, build

### Progressive Dependency Loading
```python
try:
    import pypdfium2
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False
```

## Cross-Platform Considerations

### Path Handling
- Use `pathlib.Path` for all path operations
- Support Windows UNC paths, spaces in filenames
- Proper path resolution with `Path.resolve()`

### Command Execution  
- PowerShell on Windows, bash on Unix-like systems
- Windows console UTF-8 stream reconfiguring (`sys.stdout.reconfigure(encoding="utf-8")`)
- No shell-specific syntax in core functionality

### File Encoding
- UTF-8 by default with fallback handling
- Proper encoding detection for text files

## Testing Strategy

### Unit Testing Structure
```
tests/
├── test_cli.py              # CLI argument parsing, flags, aliases, validation (15 tests)
├── test_update.py           # Self-update PyPI API querying, version parsing, subprocess (17 tests)
└── test_clean.py            # Safe cleanup, path safety guards, dry-run, confirmation (18 tests)
```

### Testing Approach
- **pytest** with temporary directories (`tmp_path`) for file operations
- **Mocking** `urllib.request` and `subprocess` for external operations (PyPI, pip)
- **Safety assertions** verifying no user files or system directories can ever be removed
- **CLI integration tests** invoking `main()` with simulated arguments

## Performance Considerations

### Memory Management
- Stream processing for large files where possible
- Chunked operations for PDF page processing
- In-memory buffers for compression iterations

### Processing Optimization
- Parallel page processing for multi-page PDFs
- Early termination for compression when target reached
- Efficient format detection without full file loading

## Future Extension Points

### Plugin Architecture
- Modular converter registration system
- Custom format handlers
- User-defined conversion profiles

### Configuration System  
- User preference files (quality defaults, output paths)
- Format-specific settings
- Batch processing configurations

### Advanced Features
- Batch conversion support
- Watch folder functionality  
- Progress resumption for large operations
- Advanced compression algorithms (WebP, AVIF)

This architecture supports the progressive implementation approach while maintaining clean separation of concerns and extensibility for future enhancements.