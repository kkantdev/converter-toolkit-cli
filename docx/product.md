# Product Document - File Toolkit CLI

## Product Purpose

The File Toolkit CLI (available interchangeably as `cv` or `ft`) is a fast, local file conversion and image compression tool designed for academic, professional, and general power users who need reliable document and image processing without cloud dependencies.

## Target Users

### Primary Users
- **Academic Researchers**: Converting PDFs to editable formats, compressing images for papers
- **Content Creators**: Optimizing images for web, converting between presentation formats  
- **Business Professionals**: Processing documents, creating presentations from existing content
- **Developers**: Automating file processing in build pipelines and workflows

### User Personas

**Dr. Sarah Chen - Academic Researcher**
- Needs to convert research PDFs to Word documents for collaboration
- Requires image compression to meet journal submission size limits
- Values local processing for sensitive research data
- Uses mixed Windows/Mac environments

**Mike Rodriguez - Web Developer**  
- Converts and compresses images for website optimization
- Batch processes marketing materials  
- Needs reliable CLI tool for automated workflows
- Requires consistent cross-platform behavior

**Jennifer Park - Business Analyst**
- Creates presentations from existing documents and images
- Converts spreadsheet data between formats for different stakeholders
- Values simple, efficient tools with clear error messages
- Works with files containing spaces and special characters in paths

## Supported Conversions

### Document Conversions
| From | To | Use Case |
|------|----|----|
| PDF | DOCX | Edit research papers, legal documents |
| PDF | PNG/JPG | Extract diagrams, create thumbnails |
| TXT | DOCX | Format plain text into professional documents |
| DOCX | PPTX | Convert documents into presentation format |

### Image Conversions  
| From | To | Use Case |
|------|----|----|
| PNG | JPG | Reduce file size, remove transparency |
| JPG | PNG | Add transparency support, lossless editing |
| Any Image | WebP | Modern web-optimized format |
| Any Image | PPTX | Create presentations from images |

### Data Conversions
| From | To | Use Case |
|------|----|----|  
| CSV | XLSX | Add formatting, formulas, multiple sheets |
| XLSX | CSV | Data analysis, import into other systems |

### Image Compression
- **Target-based**: Compress to specific KB size (e.g., 200KB, 100KB)
- **Quality optimization**: Automatically balance quality vs. file size
- **Combined operations**: Convert format AND compress in one command

## CLI Commands

File Toolkit CLI provides two interchangeable commands: `cv` (short for converter) and `ft` (short for file toolkit). Both commands are completely identical in functionality.

### Basic Conversion Syntax
```bash
cv <input_file> -<target_format>
# Or using the ft alias:
ft <input_file> -<target_format>
```

**Examples:**
```bash
cv report.pdf -docx        # PDF to Word
ft photo.png -jpg          # PNG to JPEG  
cv data.csv -xlsx          # CSV to Excel
cv notes.txt -docx         # Plain text to Word
```

### Compression Syntax
```bash
cv <input_file> -<target_size>kb
# Or using the ft alias:
ft <input_file> -<target_size>kb
```

**Examples:**
```bash
cv photo.jpg -200kb        # Compress to 200KB max
ft banner.png -50kb        # Compress to 50KB max
```

### Combined Conversion + Compression
```bash
cv <input_file> -<target_format> -<target_size>kb
```

**Examples:**
```bash
cv header.png -jpg -100kb  # Convert to JPEG and compress to 100KB
ft logo.bmp -webp -150kb   # Convert to WebP and compress to 150KB
```

### Self-Update Command
```bash
cv update                  # Check PyPI and self-update to latest release
ft update                  # Equivalent using ft alias
```

### Safe Cleanup Command
```bash
cv clear                   # Interactive scan & cleanup of internal temp & cache
cv clear --dry-run         # Preview cleanup without deleting any files
cv clear --yes             # Clean immediately without confirmation prompt
ft clear                   # Equivalent using ft alias
```

### Help and Version
```bash
cv --help                  # Show comprehensive help
ft --help                  # Help dynamically displays "ft" command context
cv --version               # Show version information (0.1.0)
ft --version               # Version dynamically displays "ft" command context
```

## Compression Behavior

### Quality Reduction Strategy
1. **JPEG Quality Scaling**: Start at quality 95, reduce by 5 until target size reached
2. **Dimension Scaling**: If quality reaches minimum, reduce dimensions by 20% increments
3. **Format Optimization**: Choose most efficient format for target size when converting

### Size Targeting
- **Goal**: Output file ≤ target KB whenever technically possible  
- **Priority**: Maintain visual quality while meeting size constraints
- **Fallback**: Clear messaging when target cannot be achieved

### Format-Specific Handling
- **PNG Compression**: May convert to JPEG if significant size reduction needed
- **JPEG Optimization**: Progressive JPEG for web compatibility
- **WebP Support**: Modern compression for best size/quality ratio

## UX Philosophy

### Simplicity First
- **Intuitive syntax**: `cv file.ext -target` pattern for all operations
- **Minimal flags**: No complex configuration options in basic usage
- **Clear output**: Success confirmations with output file paths

### Safety and Reliability  
- **Never overwrite**: Collision-safe naming (file_cv1.ext, file_cv2.ext)
- **Input preservation**: Original files never modified or deleted  
- **Graceful errors**: User-friendly error messages, no technical stack traces
- **Path handling**: Support for spaces, special characters, relative/absolute paths

### Professional Output
- **Rich formatting**: Colored output, progress indicators, formatted tables
- **Clear feedback**: Success ✔, error ✖, warning ⚠ indicators
- **Helpful guidance**: Suggest correct syntax on errors, show supported formats

### Local Processing Commitment
- **No cloud dependencies**: All conversions and processing happen on user's machine
- **Privacy protection**: User files never leave local environment
- **Offline operation**: All conversion commands work completely offline
- **Self-update network access**: The `update` command (`cv update` / `ft update`) is the only command requiring network access to query PyPI and upgrade the package
- **Performance**: Fast local processing, no network latency

## Version 0.1.0 Scope

### ✅ FULLY IMPLEMENTED FEATURES

**All core functionality is complete and working:**

1. **Image Operations** ✅
   - PNG ↔ JPG ↔ WebP conversion with transparency handling
   - KB compression with quality/dimension scaling algorithm  
   - Image to PowerPoint conversion with proper slide formatting

2. **PDF Operations** ✅
   - PDF to PNG/JPG with multi-page support and 2x scaling
   - PDF to DOCX with layout preservation

3. **Document Operations** ✅
   - Text to DOCX conversion with proper encoding handling
   - DOCX to PPTX conversion with intelligent slide creation

4. **Spreadsheet Operations** ✅
   - CSV ↔ XLSX conversion with encoding detection
   - Error handling for malformed spreadsheets

5. **CLI Foundation** ✅
   - Dual command aliases (`cv` and `ft`)
   - Complete argument parsing and validation
   - Rich UI with progress indicators and colored output
   - Collision-safe file naming
   - Comprehensive error handling

6. **Self-Update System** ✅
   - `cv update` and `ft update` commands
   - Dynamic PyPI version detection and semantic comparison
   - In-place upgrade via running interpreter
   - Post-install verification and graceful offline handling
   - Cross-platform path support

7. **Safe Cleanup System** ✅
   - `cv clear` and `ft clear` commands
   - Scans File Toolkit internal storage (temporary files, cache, metadata, logs)
   - Strict safety protection preventing any deletion of user files or working directory
   - Interactive confirmation prompt with `--yes` and `--dry-run` options
   - Real byte calculations and accurate freed-space reporting

### 🚀 Ready for Production Use

The file toolkit is fully functional and ready for production use. All documented conversions work as specified, with proper error handling and user-friendly output.

### 📋 Future Enhancements (Post v0.1.0)
- **Batch processing**: Multiple files in single command
- **Advanced compression**: WebP, AVIF format support
- **Configuration files**: User preferences, default settings
- **Watch mode**: Automatic conversion of files in directories  
- **Progress bars**: Visual progress for large file operations
- **Plugin system**: User-defined conversion handlers

## Technical Limitations

### Python Requirements
- **Minimum version**: Python 3.8+
- **Platform support**: Windows, macOS, Linux
- **Dependencies**: Optional dependency groups for different features

### Format Limitations  
- **PDF complexity**: Complex layouts may not convert perfectly to DOCX
- **Image transparency**: JPEG format doesn't support transparency
- **Spreadsheet features**: Advanced Excel features may not transfer to CSV
- **File size**: Very large files may require significant processing time

### Compression Trade-offs
- **Quality loss**: Aggressive compression reduces image quality
- **Format constraints**: Some formats have compression limitations
- **Processing time**: Multiple compression iterations for precise KB targeting

## Quality Assurance

### Testing Strategy
- **Unit tests**: Individual function testing with sample files
- **Integration tests**: End-to-end CLI workflow testing  
- **Cross-platform testing**: Windows, macOS, Linux validation
- **Format compatibility**: Testing with various file types and edge cases

### Error Handling Standards
- **Validation layers**: Input, compatibility, runtime error checking
- **User-friendly messages**: Clear explanations without technical jargon
- **Graceful degradation**: Partial success reporting when possible
- **Resource cleanup**: Proper handling of temporary files and memory

### Performance Benchmarks
- **Small files** (<1MB): Sub-second processing
- **Medium files** (1-10MB): Under 10 seconds
- **Large files** (10MB+): Progress indication, reasonable performance
- **Memory usage**: Efficient processing without excessive RAM consumption

## Success Metrics

### User Experience Metrics
- **Command success rate**: >95% of valid operations complete successfully
- **Error clarity**: Users can resolve issues based on error messages alone
- **Performance**: Processing times meet user expectations for file sizes
- **Cross-platform consistency**: Identical behavior across operating systems

### Adoption Indicators
- **Installation success**: Clean pip installation across Python 3.8+
- **Documentation clarity**: Users can complete tasks using README alone
- **Feature completeness**: All documented conversions work as specified
- **Community feedback**: Positive responses on functionality and reliability

## Competitive Analysis

### vs. Online Converters
**Advantages:**
- Privacy: Files never leave local machine
- No file size limits imposed by servers  
- Works offline, faster processing
- No account creation or usage tracking

**Considerations:**
- Requires local Python environment
- User responsible for dependency management

### vs. GUI Applications
**Advantages:**
- Scriptable and automatable
- Faster for power users
- Lower resource usage
- Consistent cross-platform interface

**Considerations:**  
- Command-line interface learning curve
- Less visual feedback than GUI

### vs. Specialized Tools
**Advantages:**
- Unified interface for multiple conversion types
- Consistent syntax and behavior patterns
- Single tool installation for diverse needs
- Modular feature installation (optional dependencies)

**Considerations:**
- May not match specialized tools for specific edge cases
- Broader scope vs. deep specialization trade-off

## Roadmap

### Current Release: v0.1.0 (Completed & Production Ready) ✅
- **Core Image Processing**: PNG ↔ JPG ↔ WebP conversion with transparency flattening
- **Target KB Compression**: Dual-stage quality reduction and dimension scaling
- **Office Document Support**: Image to PPTX, TXT to DOCX, DOCX to PPTX
- **PDF Operations**: High-fidelity PDF to images (2x scaling) and PDF to DOCX
- **Spreadsheets**: Robust CSV ↔ XLSX conversion
- **Dual CLI Aliases**: Complete interchangeable support for `cv` and `ft` commands
- **Package Self-Update**: Seamless `update` command querying PyPI with in-place upgrade
- **Safe Cleanup System**: Safe `clear` command with zero-data-loss protection guards
- **Automated Test Suite**: 50 passing unit tests and clean package build verification

### v0.2.0 (Near-Term Planned)
- Batch processing mode (`cv *.png -jpg`)
- Next-gen format support (AVIF, SVG export)
- User configuration file (`~/.filetoolkit/config.toml`) for default quality & compression thresholds
- Parallel conversion execution for multi-file operations

### v0.3.0+ (Future Enhancements)
- Directory watch mode for automated background conversions
- Plugin architecture for custom user-defined conversion handlers
- Optional lightweight cross-platform GUI wrapper

This product vision balances powerful functionality with ease of use, targeting professional users who value privacy, performance, and reliability in their file processing workflows.