# Contract: DOCParser Implementation

**Component**: DOCParser  
**Module**: `src/parsers/doc_parser.py`  
**Type**: Document parser implementation  
**Date**: 2025-09-30

## Interface Contract

### Class Declaration

```python
from src.parsers.base import (
    DocumentParser,
    ParseResult,
    PageContent,
    ValidationResult,
    ParsingError,
    PasswordProtectedError
)
import subprocess
import sys
import os
import olefile


class DOCParser(DocumentParser):
    """Parse legacy Microsoft Word (.doc) binary format documents.
    
    Features:
    - Extract text via bundled antiword binary
    - Detect password-protected files via OLE structure inspection
    - Approximate page numbers using word-count heuristic (~500 words/page)
    - UTF-8 encoding support for Cyrillic and Latin text
    """
    
    WORDS_PER_PAGE = 500  # Approximate words per page (same as DOCXParser)
```

---

## Public Methods

### 1. parse(file_path: str) -> ParseResult

**Contract**:
```python
def parse(self, file_path: str) -> ParseResult:
    """Parse .doc file and extract text content.
    
    Args:
        file_path: Absolute path to .doc file
    
    Returns:
        ParseResult with extracted pages and metadata
            - success: True if parsing succeeded
            - pages: List of PageContent objects (approximate page boundaries)
            - page_count: Number of approximate pages
            - error_message: None on success
            - warnings: List of non-fatal issues (e.g., "no extractable text")
    
    Raises:
        FileNotFoundError: If file doesn't exist
        PermissionError: If file is not readable
        PasswordProtectedError: If .doc is password-protected
        ParsingError: If antiword fails or file is corrupted
    
    Performance:
        - Typical docs (<30 pages): <5 seconds
        - Large docs (40-50 pages): <30 seconds
        - Timeout: 30 seconds for antiword subprocess
    """
```

**Preconditions**:
- `file_path` must be an absolute path string
- File must exist on filesystem
- File must be readable by current user
- File must not be password-protected

**Postconditions**:
- If successful: Returns ParseResult with `success=True`, non-empty `pages` list
- If error: Raises appropriate exception (never returns ParseResult with `success=False`)
- Pages are 1-indexed (first page is page_number=1)
- Each PageContent has `text`, `lines`, and `page_number` populated
- Character encoding preserved (UTF-8)

**Side Effects**:
- Spawns subprocess (antiword.exe)
- Reads file from disk
- No persistent state changes

**Error Handling**:
- Password-protected → Raise PasswordProtectedError("Password-protected .doc files are not supported")
- Corrupted file → Raise ParsingError("Unable to parse document. The file may be corrupted or invalid.")
- Empty text (<10 chars) → Return ParseResult with warnings, don't raise exception
- antiword not found → Raise ParsingError("DOC parser not available")
- antiword timeout → Raise ParsingError("Document processing timed out")

---

### 2. validate(file_path: str) -> ValidationResult

**Contract**:
```python
def validate(self, file_path: str) -> ValidationResult:
    """Validate .doc file without full parsing.
    
    Args:
        file_path: Absolute path to .doc file
    
    Returns:
        ValidationResult with validity status
            - is_valid: True if file can be parsed
            - error_type: None if valid, else one of:
                'file_not_found', 'permission_denied', 'password_protected',
                'invalid_format', 'corrupted'
            - error_message: None if valid, else user-friendly description
    
    Performance:
        - Lightweight check: <100ms
        - Does not run antiword (only checks OLE structure)
    """
```

**Preconditions**:
- `file_path` must be a string (can be non-existent file)

**Postconditions**:
- Always returns ValidationResult (never raises exception)
- If `is_valid=True`: file can be passed to `parse()`
- If `is_valid=False`: `error_type` and `error_message` are populated
- Does not modify file or filesystem

**Validation Checks** (in order):
1. File exists → If not: `(False, 'file_not_found', 'File not found: {path}')`
2. File readable → If not: `(False, 'permission_denied', 'File is not readable: {path}')`
3. Valid OLE format → If not: `(False, 'invalid_format', 'Unable to parse document. The file may be corrupted or invalid.')`
4. Not encrypted → If encrypted: `(False, 'password_protected', 'Password-protected .doc files are not supported')`
5. All checks pass → `(True, None, None)`

**Error Type Mapping**:
| Condition | error_type | error_message |
|-----------|------------|---------------|
| File missing | `'file_not_found'` | `'File not found: {path}'` |
| No read permission | `'permission_denied'` | `'File is not readable: {path}'` |
| Not OLE format | `'invalid_format'` | `'Unable to parse document. The file may be corrupted or invalid.'` |
| Password-protected | `'password_protected'` | `'Password-protected .doc files are not supported'` |
| OLE read error | `'corrupted'` | `'Unable to parse document. The file may be corrupted or invalid.'` |

**Side Effects**:
- Opens file for reading (via olefile)
- Closes file before returning
- No subprocess spawned
- No persistent state changes

---

### 3. get_page_count(file_path: str) -> int

**Contract**:
```python
def get_page_count(self, file_path: str) -> int:
    """Get approximate number of pages in .doc file.
    
    Note: .doc doesn't have explicit page numbers, so this is an approximation
    based on word count (~500 words per page).
    
    Args:
        file_path: Absolute path to .doc file
    
    Returns:
        Approximate number of pages (>= 1)
    
    Raises:
        ParsingError: If page count cannot be determined
    
    Performance:
        - Requires full text extraction via antiword
        - Same performance as parse() method
    """
```

**Preconditions**:
- `file_path` must point to valid, readable .doc file
- File must not be password-protected

**Postconditions**:
- Returns integer >= 1
- Empty documents return 1 (minimum)
- Page count matches what `parse()` would return

**Algorithm**:
```python
total_words = len(text.split())
if total_words == 0:
    return 1
pages = max(1, (total_words + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE)
return pages
```

**Error Handling**:
- If antiword fails → Raise ParsingError
- If file not found → Raise FileNotFoundError (via _check_file_exists)
- If password-protected → Raise PasswordProtectedError

**Side Effects**:
- Spawns antiword subprocess
- Reads entire file
- No caching (each call re-extracts text)

---

## Private Methods (Internal Contract)

### _extract_text_via_antiword(file_path: str) -> str

**Purpose**: Execute antiword subprocess and return extracted text

**Contract**:
- Input: Absolute path to .doc file
- Output: Plain text string (UTF-8 encoded)
- Raises: ParsingError if antiword fails or times out
- Timeout: 30 seconds
- Subprocess: `[antiword_exe, file_path]` with UTF-8 encoding

**Implementation**:
```python
antiword_exe = self._get_antiword_path()
result = subprocess.run(
    [antiword_exe, file_path],
    capture_output=True,
    text=True,
    encoding='utf-8',
    timeout=30
)
if result.returncode != 0:
    raise ParsingError(f"Failed to extract text from .doc: {result.stderr}")
return result.stdout
```

---

### _get_antiword_path() -> str

**Purpose**: Locate antiword executable (PyInstaller bundle vs development)

**Contract**:
- Input: None
- Output: Path to antiword executable
- Logic:
  - If `sys.frozen` (PyInstaller): Return `os.path.join(sys._MEIPASS, 'antiword.exe')`
  - Else (development): Return `'antiword'` (assumes in PATH)

---

### _is_password_protected(file_path: str) -> bool

**Purpose**: Check encryption flag in .doc OLE structure

**Contract**:
- Input: Path to .doc file
- Output: True if password-protected, False otherwise
- Method: Read byte 11 of WordDocument stream header (encryption flag)
- Returns False on any error (fail open)

**Implementation**:
```python
try:
    ole = olefile.OleFileIO(file_path)
    if ole.exists('WordDocument'):
        stream = ole.openstream('WordDocument')
        header = stream.read(68)  # FIB header
        flags = header[11] if len(header) > 11 else 0
        is_encrypted = bool(flags & 0x01)
        ole.close()
        return is_encrypted
    ole.close()
    return False
except:
    return False  # Assume not encrypted if can't read
```

---

### _split_into_pages(paragraphs: list[str]) -> list[PageContent]

**Purpose**: Convert paragraph list into approximate pages

**Contract**:
- Input: List of paragraph text strings
- Output: List of PageContent objects with page boundaries
- Algorithm: Accumulate paragraphs until WORDS_PER_PAGE threshold, then start new page
- Page numbers: 1-indexed
- Returns empty list if no paragraphs

**Behavior**:
- Same logic as DOCXParser._split_into_pages()
- Words counted via `len(paragraph.split())`
- Page boundary on threshold exceeded
- Last page contains remaining paragraphs

---

## Integration Points

### ParserFactory Integration

**Required Change**: Add .doc to PARSER_MAP

```python
# In src/parsers/factory.py
from .doc_parser import DOCParser

PARSER_MAP = {
    '.pdf': PDFParser,
    '.docx': DOCXParser,
    '.doc': DOCParser,  # NEW
}
```

**File Filter Update**:
```python
def get_file_filter(cls) -> str:
    patterns = [f"*{ext}" for ext in cls.PARSER_MAP.keys()]
    return f"Supported Documents ({' '.join(patterns)})"
    # Result: "Supported Documents (*.pdf *.docx *.doc)"
```

---

## External Dependencies

### Required Libraries

**Python Packages** (requirements.txt):
```
olefile>=0.46  # OLE file structure reading
```

**External Binaries**:
- antiword.exe (Windows)
- Source: http://www.winfield.demon.nl/ or bundled in repo
- Size: ~200KB
- License: GPL-2.0
- Location in bundle: `sys._MEIPASS/antiword.exe`

**PyInstaller Configuration** (build.spec):
```python
datas = [
    ('path/to/antiword.exe', '.'),  # Bundle antiword
]

hiddenimports = [
    'olefile',  # Ensure olefile is included
]
```

---

## Performance Guarantees

| Operation | Typical (<30 pages) | Large (40-50 pages) | Maximum |
|-----------|---------------------|---------------------|---------|
| validate() | <100ms | <200ms | <500ms |
| parse() | <5s | <15s | <30s |
| get_page_count() | <5s | <15s | <30s |

**Notes**:
- Subprocess overhead: ~100-500ms
- antiword processing: ~1-2s per 50 pages
- Text processing: <1s for typical documents
- Timeout prevents infinite hangs

---

## Error Contract

### Exception Hierarchy

```
Exception
└─ ParsingError (custom, from base.py)
   └─ PasswordProtectedError (custom, from base.py)
```

### When to Raise Each Exception

| Exception | Condition | User Message |
|-----------|-----------|--------------|
| FileNotFoundError | File doesn't exist | (Built-in Python message) |
| PermissionError | File not readable | (Built-in Python message) |
| PasswordProtectedError | Encryption flag set | "Password-protected .doc files are not supported" |
| ParsingError | antiword fails | "Unable to parse document. The file may be corrupted or invalid." |
| ParsingError | antiword timeout | "Document processing timed out" |
| ParsingError | antiword not found | "DOC parser not available" |

### Validation vs Parse Error Handling

- **validate()**: Never raises exceptions, always returns ValidationResult
- **parse()**: Raises exceptions for errors, never returns ParseResult with success=False

---

## Testing Contract

**Manual Validation Required** (per constitution - no automated tests):

1. Valid .doc with text → parse() succeeds, pages extracted
2. Password-protected .doc → validate() returns is_valid=False, parse() raises PasswordProtectedError
3. Corrupted .doc → validate() returns is_valid=False or parse() raises ParsingError
4. Empty .doc → parse() succeeds with warnings
5. Cyrillic text → Characters preserved in output
6. Large .doc (50 pages) → Completes in <30 seconds
7. File not found → FileNotFoundError raised
8. Wrong format (.txt renamed to .doc) → validate() catches, returns invalid_format

**Test Files Needed**:
- valid_cyrillic.doc
- password_protected.doc
- corrupted.doc
- empty.doc
- large_50pages.doc

---

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-09-30 | Initial contract definition |

---

**Status**: ✅ Complete - Ready for implementation
