# Research: Document Data Extraction Tool

**Date**: September 30, 2025
**Feature**: Document Data Extraction Tool
**Branch**: 001-use-docs-prd

## Research Questions & Decisions

### 1. GUI Framework Selection

**Decision**: tkinter (built-in)

**Rationale**:
- Built-in to Python, no additional dependency overhead for packaging
- Cross-platform development (macOS dev → Windows target)
- Sufficient for single-screen application requirements
- Mature, stable, well-documented
- PyInstaller has excellent tkinter support

**Alternatives Considered**:
- **PyQt5/PySide6**: More modern UI, but adds ~50MB to executable size, licensing complexity
- **wxPython**: Better native look, but larger dependency, more complex packaging
- **ttkbootstrap**: Modern styling layer over tkinter - considered for future enhancement if needed

**Best Practices**:
- Use `ttk` widgets where available for native platform look
- Implement MVC separation: UI components don't contain business logic
- Use thread-safe queue for worker thread → UI updates
- `.after()` method for UI updates from background threads

---

### 2. PDF Parsing Library

**Decision**: PyMuPDF (fitz) 1.23.0+

**Rationale**:
- Fast text extraction with page-level granularity
- Robust handling of various PDF formats
- Small footprint (~10MB in packaged executable)
- Excellent Unicode support (critical for Cyrillic text)
- Active maintenance and community support

**Alternatives Considered**:
- **PyPDF2**: Pure Python (smaller), but slower, less robust with complex PDFs
- **pdfplumber**: Better table extraction, but overkill for plain text, larger dependency chain
- **PDFMiner**: Older, more complex API, slower

**Best Practices**:
- Open document once, extract all pages sequentially
- Use `get_text()` with `"text"` layout mode for natural reading order
- Always close document explicitly (use context manager)
- Handle corrupted PDFs with try/except blocks
- Check for text content to detect scanned PDFs (FR-053)

---

### 3. DOCX Parsing Library

**Decision**: python-docx 1.1.0+

**Rationale**:
- De facto standard for DOCX manipulation in Python
- Simple API for text extraction
- Maintains paragraph structure
- Small footprint (~2MB)
- Good Unicode support

**Alternatives Considered**:
- **docx2txt**: Lighter, but read-only and less maintained
- **python-docx2txt**: Simple but no paragraph/page structure
- **openpyxl**: For Excel, not Word

**Best Practices**:
- Iterate through `document.paragraphs` for text extraction
- Page breaks: check for `w:lastRenderedPageBreak` in XML or use section breaks as approximation
- Preserve paragraph order
- Handle tables if they contain relevant data (iterate `document.tables`)

---

### 4. Drag-and-Drop Support

**Decision**: tkinterdnd2 0.3.0+

**Rationale**:
- Enables native drag-and-drop file selection (FR-004)
- Simple integration with tkinter
- Cross-platform support (Windows, macOS, Linux)
- Small library, minimal overhead

**Alternatives Considered**:
- **Native tkinter DND**: Very limited, platform-specific, complex
- **Manual implementation**: Too complex for simple file drop

**Best Practices**:
- Register drop target on main window or specific frame
- Validate dropped file path and extension before processing
- Provide visual feedback during drag-over
- Handle multiple files dropped (only accept first, show warning)

---

### 5. Threading Model

**Decision**: Python `threading` module with dual-thread architecture

**Rationale**:
- Built-in, no external dependencies
- Sufficient for single background worker pattern
- Thread-safe queue for communication
- tkinter requires UI updates on main thread

**Alternatives Considered**:
- **multiprocessing**: Overkill for I/O-bound task, more complex state sharing
- **asyncio**: Not well-suited for tkinter integration, adds complexity
- **concurrent.futures**: Good option, but threading is simpler for single worker

**Best Practices**:
- Main thread: UI only, never blocks
- Worker thread: All document processing and I/O
- Use `queue.Queue()` for thread-safe communication
- UI updates via `.after(100, check_queue)` pattern
- Set worker thread as daemon for clean shutdown

---

### 6. Regex for Keyword Matching

**Decision**: Python `re` module (built-in)

**Rationale**:
- Built-in, no dependencies
- Sufficient for case-insensitive keyword matching (FR-009)
- Pattern flexibility for number extraction
- Good Unicode support with flags

**Best Practices**:
- Compile patterns once for reuse: `re.compile(keyword, re.IGNORECASE | re.UNICODE)`
- Escape user input keywords: `re.escape(keyword)` to prevent regex injection
- Use `re.finditer()` to find all matches (FR-014: extract ALL occurrences)
- Word boundaries `\b` to avoid partial matches (unless specified otherwise)

---

### 7. Number Format Parsing

**Decision**: Custom regex patterns for US/UK format (period as decimal)

**Rationale**:
- Clarification Q4 resolved: US/UK format only (3.5, 1,234.56)
- Simple regex patterns sufficient
- No need for locale-aware parsing

**Pattern Strategy**:
```python
# Integer or decimal with optional thousands separator
pattern = r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b'
# Matches: 3, 3.5, 1,234, 1,234.56
```

**Best Practices**:
- Extract first number after keyword (FR-015: "next numeric value")
- No distance limit (simplified approach per clarification)
- Flag ambiguous formats as warnings (e.g., "3,500" could be thousands or unusual decimal)
- Store as string initially, convert to float only if needed

---

### 8. Personal Information Extraction

**Decision**: Labeled field pattern matching with Cyrillic/Latin support

**Rationale**:
- Clarification Q7: Fields have consistent labels
- Pattern-based approach simpler than NLP
- Cyrillic + Latin character class support needed

**Pattern Strategy**:
```python
# First name patterns (Cyrillic or Latin labels)
first_name_labels = r'(?:First Name|Име|Name|Имя):\s*([А-Яа-яA-Za-z\s-]+)'

# Last name patterns
last_name_labels = r'(?:Last Name|Фамилия|Surname|Фамилія):\s*([А-Яа-яA-Za-z\s-]+)'

# ID number (first 4 digits)
id_pattern = r'(?:ID|ЕГН|ID Number|Номер):\s*(\d{4})\d*'
```

**Best Practices**:
- Search first page primarily (likely location per clarification Q8)
- Fall back to full document if not found on first page
- Use Unicode character classes: `[А-Яа-я]` for Cyrillic, `[A-Za-z]` for Latin
- Trim whitespace from extracted values
- Handle mixed scripts: allow both in same match
- Mark as "Not found" if pattern doesn't match (FR-026)

---

### 9. Configuration Persistence

**Decision**: JSON file (config.json) in application directory

**Rationale**:
- Simple, human-readable format
- Built-in `json` module, no dependencies
- Easy to edit manually if needed
- Cross-platform compatible

**Schema**:
```json
{
  "output_folder": "C:/Users/...",
  "number_format": "us_uk",
  "proximity_rule": "next_number",
  "keyword_history": ["HTD", "RTP", "BGN"],
  "window_width": 800,
  "window_height": 600,
  "log_directory": "C:/Users/.../logs"
}
```

**Best Practices**:
- Load on app start with error handling (use defaults if corrupted)
- Save on app close and when settings change
- Validate structure before loading
- Provide sensible defaults for missing keys
- Use `os.path.expanduser("~")` for default paths

---

### 10. Executable Packaging

**Decision**: PyInstaller 5.13+ with `--onefile` flag

**Rationale**:
- Industry standard for Python → .exe
- Excellent tkinter support
- UPX compression reduces size
- Can bundle hidden imports

**Configuration** (build.spec):
```python
a = Analysis(['src/main.py'],
             pathex=[],
             binaries=[],
             datas=[],
             hiddenimports=['tkinterdnd2', 'fitz', 'docx'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=None,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='DocumentExtractor',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,  # No console window
          icon='icon.ico')
```

**Best Practices**:
- Build on Windows or Windows VM for compatibility
- Test executable on clean Windows system without Python
- Specify hidden imports explicitly
- Use UPX compression to reduce size
- Set `console=False` for GUI-only app
- Include version metadata and icon

---

### 11. Error Handling Architecture

**Decision**: Error collection pattern with graceful degradation

**Rationale**:
- Constitution Principle II: Graceful Degradation
- FR-045 to FR-049: Non-blocking error handling
- Better UX than stopping on first error

**Implementation Pattern**:
```python
class ExtractionResults:
    def __init__(self):
        self.matches = []
        self.personal_info = {}
        self.errors = []
        self.warnings = []

    def add_error(self, error_type, message, context):
        self.errors.append({
            'type': error_type,
            'message': message,
            'context': context
        })

    def add_warning(self, message):
        self.warnings.append(message)
```

**Best Practices**:
- Try/except blocks around each extraction operation
- Continue processing on errors
- Collect all errors/warnings in results object
- Display summary at end
- Include errors in output file for transparency
- Mark missing data as "Not found" instead of failing

---

### 12. Logging Strategy

**Decision**: Processing log file per extraction (per FR-054, FR-055)

**Rationale**:
- Clarification resolved: Standard logging with timestamps, warnings, errors
- Helps debugging without cluttering UI
- Provides audit trail for extractions

**Implementation**:
```python
import logging

# Configure per-extraction logger
log_filename = f"extraction_{timestamp}.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Log key events
logging.info(f"Starting extraction: {filename}")
logging.warning(f"Keyword '{keyword}' not found")
logging.error(f"Failed to parse PDF: {error}")
```

**Best Practices**:
- One log file per extraction operation
- Save logs to configurable directory (from config.json)
- Include: timestamps, filename, keywords, extraction results, errors, warnings
- Rotate/archive old logs (optional enhancement)
- Don't log sensitive personal information in detail

---

## Technology Stack Summary

| Component | Technology | Version | Size Impact |
|-----------|-----------|---------|-------------|
| Language | Python | 3.10+ | Base |
| GUI | tkinter | Built-in | ~2MB |
| DND Support | tkinterdnd2 | 0.3.0+ | <1MB |
| PDF Parser | PyMuPDF (fitz) | 1.23.0+ | ~10MB |
| DOCX Parser | python-docx | 1.1.0+ | ~2MB |
| Packaging | PyInstaller | 5.13+ | Base overhead ~5MB |
| **Total Estimated** | | | **~20-30MB** (well under 100MB limit) |

---

## Open Questions Resolution Status

All critical technical questions from the PRD have been resolved:

- ✅ **Q4 - Number Format**: US/UK format (period decimal) - resolved via clarification
- ✅ **Q6 - Proximity Rule**: First number after keyword in text flow - resolved via clarification
- ✅ **Q7 - Personal Info Format**: Labeled fields with consistent labels - resolved via clarification
- ✅ **Q8 - Personal Info Location**: Focus on first page, fall back to full document - resolved via clarification
- ✅ **Password-protected/OCR PDFs**: Out of scope, reject with error - resolved via clarification
- ✅ **Logging**: Standard logging with timestamps, warnings, errors - resolved via clarification

**No remaining NEEDS CLARIFICATION items** - Ready to proceed to Phase 1 Design.

---

## References

- [PyMuPDF Documentation](https://pymupdf.readthedocs.io/)
- [python-docx Documentation](https://python-docx.readthedocs.io/)
- [tkinter Best Practices](https://tkdocs.com/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [Python Threading Guide](https://docs.python.org/3/library/threading.html)
- [Python Regex Documentation](https://docs.python.org/3/library/re.html)

---

**Research Complete**: All technology decisions finalized, best practices documented, ready for Phase 1 design.
