# Research: DOC File Format Support

**Feature**: Add .doc file parsing to Document Data Extractor  
**Date**: 2025-09-30  
**Status**: Complete

## Research Questions

### 1. Library Selection for .doc Parsing

**Question**: Which Python library should be used to parse legacy .doc files?

**Options Evaluated**:

| Library | Pros | Cons | Verdict |
|---------|------|------|---------|
| **python-docx** | Already used for DOCX; well-maintained | Does NOT support .doc format (only .docx) | ❌ Not suitable |
| **antiword** | Lightweight; .doc specific | Requires external binary; difficult PyInstaller bundling | ❌ Too complex |
| **textract** | Supports many formats | Heavy dependencies (requires antiword/other tools) | ❌ Too heavy |
| **pywin32** | Native Windows COM | Windows-only; requires Office installation | ❌ Violates no-dependency requirement |
| **oletools** | Pure Python; reads OLE structure | Low-level; requires manual text extraction logic | ⚠️ Possible but complex |
| **docx2python** | Claims .doc support | Actually only supports .docx despite name | ❌ Misleading |
| **olefile + custom parsing** | Pure Python; full control | Significant development effort; .doc format complex | ⚠️ High risk |

**Decision**: **Use antiword via subprocess with bundled binary**

**Rationale**:
- antiword is the most reliable .doc text extractor
- Can bundle antiword.exe with PyInstaller (add to build.spec datas)
- Pure text output works for our extraction needs
- Subprocess approach isolates failures (graceful degradation)
- No Python dependencies needed - just binary execution

**Alternatives Considered**: 
- oletools: Too low-level, would require implementing .doc binary format parsing
- textract: Too many dependencies, bundle size concerns
- Custom parsing: Too risky given .doc format complexity

**Implementation Approach**:
```python
import subprocess
import platform

def extract_doc_text(file_path: str) -> str:
    """Extract text from .doc using bundled antiword binary"""
    if platform.system() == 'Windows':
        antiword_exe = os.path.join(sys._MEIPASS, 'antiword.exe')
    else:
        antiword_exe = 'antiword'  # Dev environment
    
    result = subprocess.run(
        [antiword_exe, file_path],
        capture_output=True,
        text=True,
        encoding='utf-8'
    )
    return result.stdout
```

### 2. Password Detection in .doc Files

**Question**: How can we detect password-protected .doc files without full parsing?

**Research Findings**:
- .doc files are OLE (Object Linking and Embedding) containers
- Password protection is indicated by encryption flags in the OLE structure
- Can use `olefile` library (pure Python) to read OLE headers without full parsing

**Decision**: **Use olefile to check encryption status before parsing**

**Implementation**:
```python
import olefile

def is_doc_encrypted(file_path: str) -> bool:
    """Check if .doc file is password-protected"""
    try:
        ole = olefile.OleFileIO(file_path)
        # Check for encryption in WordDocument stream
        if ole.exists('WordDocument'):
            stream = ole.openstream('WordDocument')
            header = stream.read(68)  # FIB header
            # Byte 11 contains encryption flag
            flags = header[11] if len(header) > 11 else 0
            is_encrypted = bool(flags & 0x01)
            ole.close()
            return is_encrypted
        ole.close()
        return False
    except:
        return False  # If can't read OLE, let antiword fail gracefully
```

**Rationale**: Lightweight check before expensive antiword subprocess call

### 3. Page Break Detection in .doc Format

**Question**: Can we detect actual page breaks in .doc files?

**Research Findings**:
- antiword outputs plain text only (no formatting/pagination info)
- .doc page breaks are formatting instructions, not preserved in text output
- Word's pagination depends on printer settings, margins, fonts (not in .doc data)

**Decision**: **Use same word-count heuristic as DOCX (500 words/page)**

**Rationale**:
- Consistent with existing DOCX behavior (FR-007 requirement)
- Approximation acceptable for keyword location purposes
- User expectations already set by DOCX format

**Implementation**: Reuse DOCXParser._split_into_pages() method logic

### 4. PyInstaller Bundling Requirements

**Question**: What configuration changes needed for PyInstaller to bundle antiword?

**Decision**: **Add antiword.exe to build.spec datas and binaries**

**build.spec modifications**:
```python
# In build.spec
datas = [
    ('path/to/antiword.exe', '.'),  # Bundle antiword executable
    ('path/to/antiword/*', 'antiword/'),  # Bundle resource files if needed
]

# Ensure subprocess can find bundled binary
import sys
import os
if getattr(sys, 'frozen', False):
    # Running in PyInstaller bundle
    antiword_path = os.path.join(sys._MEIPASS, 'antiword.exe')
else:
    # Running in development
    antiword_path = 'antiword'  # Assumes antiword in PATH
```

**Hidden Imports**: 
- olefile (for password detection)
- No other hidden imports needed (subprocess is stdlib)

**Dependencies to Add**:
- requirements.txt: `olefile>=0.46`
- External binary: antiword.exe (include in repository or download in build script)

### 5. Error Patterns in .doc Parsing

**Question**: How to map antiword/OLE errors to existing error types?

**Error Mapping**:

| Condition | Detection Method | Error Type | Error Message |
|-----------|------------------|------------|---------------|
| **Password-protected** | olefile check (encryption flag) | ValidationResult(error_type='password_protected') | "Password-protected .doc files are not supported" |
| **Corrupted file** | olefile.OleFileIO() fails OR antiword returns error | ValidationResult(error_type='corrupted') | "Unable to parse document. The file may be corrupted or invalid." |
| **Not a .doc file** | olefile.isOleFile() returns False | ValidationResult(error_type='invalid_format') | "Unable to parse document. The file may be corrupted or invalid." |
| **No extractable text** | antiword returns empty/whitespace only | ParseResult with warnings | Warning: "Document has no extractable text" |
| **antiword not found** | FileNotFoundError on subprocess | ParsingError | "DOC parser not available" (shouldn't happen in bundled .exe) |

**Decision**: **Follow existing error patterns from PDFParser and DOCXParser**

**Graceful Degradation**:
- If password-protected: Raise ValidationError (user-facing message)
- If corrupted: Display generic message, don't expose technical details
- If no text: Continue with warnings, don't fail
- If antiword fails: Wrap in ParsingError with user-friendly message

## Technical Decisions Summary

### Selected Approach

**Library**: antiword (bundled binary) + olefile (password detection)  
**Text Extraction**: Subprocess call to antiword.exe  
**Password Detection**: olefile OLE header inspection  
**Page Numbering**: Word-count heuristic (500 words/page)  
**Error Handling**: Map to existing ValidationResult and ParsingError types  
**Bundling**: PyInstaller datas include antiword.exe

### Implementation Pattern

```python
# doc_parser.py structure
class DOCParser(DocumentParser):
    WORDS_PER_PAGE = 500
    
    def validate(self, file_path: str) -> ValidationResult:
        # 1. Check file is valid OLE
        # 2. Check encryption flag
        # 3. Return ValidationResult
    
    def parse(self, file_path: str) -> ParseResult:
        # 1. Validate first (check password/corruption)
        # 2. Run antiword subprocess
        # 3. Split text into pages (word-count)
        # 4. Return ParseResult
    
    def get_page_count(self, file_path: str) -> int:
        # 1. Run antiword to get text
        # 2. Count words, divide by 500
        # 3. Return approximate page count
```

### Performance Considerations

- **Subprocess overhead**: ~100-500ms to spawn antiword process
- **Text extraction**: antiword is fast (~1-2 seconds for 50-page doc)
- **Total time**: Well under 30-second target for typical documents
- **Memory**: Low (subprocess isolated, no large libraries loaded)

### Risk Mitigation

**Risk 1**: antiword.exe not available on user's system  
**Mitigation**: Bundle with PyInstaller, include in build artifacts

**Risk 2**: antiword doesn't support all .doc variants  
**Mitigation**: Graceful error message, user can convert to .docx

**Risk 3**: Encoding issues with Cyrillic text  
**Mitigation**: Use UTF-8 encoding in subprocess, test with Cyrillic samples

**Risk 4**: Large executable size with bundled binary  
**Mitigation**: antiword.exe is ~200KB, well within 100MB limit

## Dependencies

**New Requirements**:
- `olefile>=0.46` (pure Python, password detection)

**External Binaries**:
- antiword.exe (Windows) - download from antiword.org or include in repo
- Size: ~200KB
- License: GPL-2.0 (compatible with project use)

**Build Configuration**:
- build.spec: Add antiword.exe to datas
- build.spec: No hidden imports beyond olefile

## Next Steps

1. **Phase 1**: Create data model and contracts based on decisions above
2. **Implementation**: Follow DOCParser structure outlined in research
3. **Testing**: Validate with .doc files containing Cyrillic text
4. **Build**: Test PyInstaller bundle with antiword.exe on Windows

---
**Research Status**: ✅ Complete - All unknowns resolved, ready for Phase 1 design
