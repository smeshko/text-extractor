# Data Model: DOC File Format Support

**Feature**: Add .doc file parsing  
**Date**: 2025-09-30  
**Based On**: Feature spec + research findings

## Entities

### DOCParser (New Class)

**Type**: Document parser implementation  
**Extends**: `DocumentParser` (abstract base class from `src/parsers/base.py`)  
**Module**: `src/parsers/doc_parser.py`

**Purpose**: Parse legacy Microsoft Word (.doc) binary format files and extract text content while maintaining page structure approximation.

**Attributes**:
- `WORDS_PER_PAGE: int = 500` - Word count threshold for page approximation (class constant)

**Methods**:

#### parse(file_path: str) -> ParseResult
**Purpose**: Extract text content from .doc file  
**Parameters**:
- `file_path: str` - Absolute path to .doc file

**Returns**: `ParseResult`
- `success: bool` - Always True if no exception raised
- `pages: list[PageContent]` - List of page objects with text
- `page_count: int` - Number of approximate pages
- `error_message: str | None` - None on success
- `warnings: list[str]` - e.g., "Document has no extractable text"

**Raises**:
- `FileNotFoundError` - If file doesn't exist
- `PermissionError` - If file not readable
- `PasswordProtectedError` - If .doc is password-protected (detected via olefile)
- `ParsingError` - If antiword subprocess fails or corruption detected

**Validation Rules**:
- File must exist and be readable
- File must be valid OLE format (checked via olefile)
- File must not be password-protected (encryption flag check)
- If text extraction yields <10 chars in first 3 pages, add warning (not error)

**Processing Flow**:
1. Call `_check_file_exists(file_path)` (inherited method)
2. Run `validate(file_path)` to check password/corruption
3. Execute antiword subprocess to extract text
4. Split text into paragraphs
5. Apply word-count heuristic to create page boundaries
6. Create PageContent objects for each approximate page
7. Return ParseResult with pages

#### validate(file_path: str) -> ValidationResult
**Purpose**: Check if .doc file can be parsed without full extraction  
**Parameters**:
- `file_path: str` - Absolute path to .doc file

**Returns**: `ValidationResult`
- `is_valid: bool` - True if file can be parsed
- `error_type: str | None` - One of: 'password_protected', 'corrupted', 'invalid_format', 'file_not_found'
- `error_message: str | None` - User-friendly error description

**Validation Checks**:
1. File exists (`os.path.exists`)
2. File is readable (`os.access(file_path, os.R_OK)`)
3. File is valid OLE format (`olefile.isOleFile(file_path)`)
4. File is not password-protected (check encryption flag in WordDocument stream)

**Error Type Mapping**:
- File not found → `error_type='file_not_found'`, `error_message='File not found: {path}'`
- Not readable → `error_type='permission_denied'`, `error_message='File is not readable: {path}'`
- Not valid OLE → `error_type='invalid_format'`, `error_message='Unable to parse document. The file may be corrupted or invalid.'`
- Password-protected → `error_type='password_protected'`, `error_message='Password-protected .doc files are not supported'`
- Other errors → `error_type='corrupted'`, `error_message='Unable to parse document. The file may be corrupted or invalid.'`

#### get_page_count(file_path: str) -> int
**Purpose**: Get approximate number of pages in .doc file  
**Parameters**:
- `file_path: str` - Absolute path to .doc file

**Returns**: `int` - Approximate page count (>= 1)

**Raises**:
- `ParsingError` - If page count cannot be determined

**Algorithm**:
1. Extract text via antiword subprocess
2. Count total words in document
3. Divide by WORDS_PER_PAGE (500)
4. Round up to nearest integer
5. Return max(1, calculated_pages) to ensure at least 1 page

#### _extract_text_via_antiword(file_path: str) -> str (Private)
**Purpose**: Internal helper to run antiword subprocess  
**Parameters**:
- `file_path: str` - Path to .doc file

**Returns**: `str` - Extracted plain text (UTF-8)

**Raises**:
- `ParsingError` - If antiword not found or execution fails

**Implementation**:
```python
antiword_exe = self._get_antiword_path()
result = subprocess.run(
    [antiword_exe, file_path],
    capture_output=True,
    text=True,
    encoding='utf-8',
    timeout=30  # Prevent hanging on large files
)
if result.returncode != 0:
    raise ParsingError(f"Failed to extract text from .doc: {result.stderr}")
return result.stdout
```

#### _get_antiword_path() -> str (Private)
**Purpose**: Locate antiword executable (bundled or system)  
**Returns**: `str` - Path to antiword.exe

**Logic**:
```python
if getattr(sys, 'frozen', False):
    # PyInstaller bundle
    return os.path.join(sys._MEIPASS, 'antiword.exe')
else:
    # Development
    return 'antiword'  # Assumes in PATH
```

#### _is_password_protected(file_path: str) -> bool (Private)
**Purpose**: Check encryption flag in .doc OLE structure  
**Returns**: `bool` - True if password-protected

**Implementation** (using olefile):
```python
ole = olefile.OleFileIO(file_path)
if ole.exists('WordDocument'):
    stream = ole.openstream('WordDocument')
    header = stream.read(68)
    flags = header[11] if len(header) > 11 else 0
    is_encrypted = bool(flags & 0x01)
    ole.close()
    return is_encrypted
ole.close()
return False
```

#### _split_into_pages(paragraphs: list[str]) -> list[PageContent] (Private)
**Purpose**: Convert paragraph list into page objects using word-count heuristic  
**Parameters**:
- `paragraphs: list[str]` - List of paragraph texts

**Returns**: `list[PageContent]` - Pages with approximate boundaries

**Algorithm**: Same as DOCXParser._split_into_pages() (reusable logic)
- Accumulate paragraphs until word count exceeds WORDS_PER_PAGE
- Create new page boundary when threshold crossed
- Maintain page numbers (1-indexed)
- Return list of PageContent objects

---

### ParserFactory (Modified Class)

**Module**: `src/parsers/factory.py`  
**Changes**: Add .doc support to existing factory

**Modified Attributes**:

#### PARSER_MAP (Class Variable)
**Before**:
```python
PARSER_MAP = {
    '.pdf': PDFParser,
    '.docx': DOCXParser,
}
```

**After**:
```python
PARSER_MAP = {
    '.pdf': PDFParser,
    '.docx': DOCXParser,
    '.doc': DOCParser,  # NEW
}
```

**Modified Methods**:

#### get_file_filter() -> str
**Before**: `"Supported Documents (*.pdf *.docx)"`  
**After**: `"Supported Documents (*.pdf *.docx *.doc)"`

**No other changes needed** - `create()`, `is_supported()`, `get_supported_extensions()` automatically include .doc via PARSER_MAP lookup.

---

### PageContent (Existing Entity - No Changes)

**Module**: `src/parsers/base.py`  
**Purpose**: Container for single page text content

**Attributes** (used by DOCParser):
- `page_number: int` - 1-indexed page number (approximate for .doc)
- `text: str` - Full page text
- `lines: list[str]` - Text split by line breaks

---

### ParseResult (Existing Entity - No Changes)

**Module**: `src/parsers/base.py`  
**Purpose**: Return value from parse() methods

**Attributes** (used by DOCParser):
- `success: bool` - True if parsing succeeded
- `pages: list[PageContent]` - Extracted pages
- `page_count: int` - Total approximate pages
- `error_message: str | None` - None on success
- `warnings: list[str]` - Non-fatal issues (e.g., no text)

---

### ValidationResult (Existing Entity - No Changes)

**Module**: `src/parsers/base.py`  
**Purpose**: Return value from validate() methods

**Attributes** (used by DOCParser):
- `is_valid: bool` - True if document can be parsed
- `error_type: str | None` - Category of error
- `error_message: str | None` - User-facing description

---

## Relationships

```
DocumentParser (abstract)
    ↑
    ├─ PDFParser (existing)
    ├─ DOCXParser (existing)
    └─ DOCParser (new)

ParserFactory
    └─ PARSER_MAP
        ├─ '.pdf' → PDFParser
        ├─ '.docx' → DOCXParser
        └─ '.doc' → DOCParser (new)

DOCParser.parse()
    └─ returns ParseResult
        └─ contains list[PageContent]

DOCParser.validate()
    └─ returns ValidationResult
```

## State Transitions

**DOCParser Lifecycle** (per file):

```
1. CREATED → validate() called
2. VALIDATING → check OLE format, encryption
3. ↓ valid → VALIDATED (is_valid=True)
   ↓ invalid → ERROR_STATE (is_valid=False, error details)
4. VALIDATED → parse() called
5. PARSING → antiword subprocess, text extraction
6. ↓ success → COMPLETE (ParseResult with pages)
   ↓ failure → ERROR (ParsingError raised)
```

No persistent state - each parse operation is independent.

## Data Volume

**Expected Scale**:
- Typical .doc: 5-30 pages (~2500-15000 words)
- Large .doc: 50 pages (~25000 words)
- Text extraction: ~50-100KB raw text per document
- In-memory: PageContent objects (~10-20 per document)

**Performance Impact**:
- antiword subprocess: 100-500ms overhead
- Text processing: <1 second for typical doc
- Total: <5 seconds for typical, <30 seconds for large (within target)

## Dependencies

**New External Dependencies**:
- `olefile>=0.46` (pure Python, OLE file reading)
- antiword.exe (bundled binary, ~200KB)

**Internal Dependencies**:
- `src/parsers/base.py` (DocumentParser, ParseResult, ValidationResult, PageContent)
- Python stdlib: `subprocess`, `os`, `sys`, `platform`

---

**Status**: ✅ Complete - Ready for contract generation
