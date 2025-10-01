# Tasks: Add DOC File Format Support

**Input**: Design documents from `/Users/A1E6E98/Developer/kris-extractor/specs/002-i-want-to/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/doc-parser-contract.md, quickstart.md

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → ✅ Feature: Add legacy .doc file parsing to Document Data Extractor
   → ✅ Tech stack: Python 3.10+, olefile>=0.46, antiword.exe (bundled)
   → ✅ Structure: Single desktop app, src/ directory
2. Load optional design documents:
   → ✅ data-model.md: DOCParser entity, ParserFactory modifications
   → ✅ contracts/doc-parser-contract.md: DOCParser interface contract
   → ✅ research.md: antiword subprocess approach, olefile for password detection
   → ✅ quickstart.md: Manual validation scenarios
3. Generate tasks by category:
   → Setup: Dependencies, antiword binary
   → Core: DOCParser implementation
   → Integration: Factory, file filter
   → Polish: Build configuration, manual validation
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Dependencies: Setup → Core → Integration → Polish
5. Number tasks sequentially (T001, T002...)
6. ✅ COMPLETE - Tasks ready for execution
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: `src/`, `requirements.txt`, `build.spec` at repository root
- Paths shown below assume single desktop application structure

---

## Phase 3.1: Setup & Dependencies

- [X] **T001** Add olefile dependency to requirements.txt
  - File: `/Users/A1E6E98/Developer/kris-extractor/requirements.txt`
  - Add line: `olefile>=0.46`
  - Purpose: OLE file reading for password detection

- [X] **T002** Obtain and bundle antiword binary
  - Create directory: `/Users/A1E6E98/Developer/kris-extractor/bin/` (if not exists)
  - Download antiword.exe for Windows (~200KB)
  - Place in: `/Users/A1E6E98/Developer/kris-extractor/bin/antiword.exe`
  - Purpose: Text extraction from .doc files

- [X] **T003** Install olefile dependency for development
  - Run: `pip install olefile>=0.46`
  - Verify: `python -c "import olefile; print(olefile.__version__)"`
  - Purpose: Enable local development and testing

---

## Phase 3.2: Core Implementation

- [X] **T004** Create DOCParser class skeleton in src/parsers/doc_parser.py
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Implement class structure with:
    - Import statements (DocumentParser, ParseResult, ValidationResult, PageContent, etc.)
    - Class declaration: `class DOCParser(DocumentParser)`
    - Class constant: `WORDS_PER_PAGE = 500`
    - Method signatures: `parse()`, `validate()`, `get_page_count()`
  - Leave methods with `pass` or basic structure

- [X] **T005** Implement private helper: _get_antiword_path() in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Logic:
    - Check if `sys.frozen` (PyInstaller bundle)
    - If frozen: return `os.path.join(sys._MEIPASS, 'antiword.exe')`
    - Else: return `'antiword'` (development, assumes in PATH)
  - Purpose: Locate antiword binary in bundle or dev environment

- [X] **T006** Implement private helper: _is_password_protected() in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Use olefile to check encryption flag:
    - Open OLE file
    - Read WordDocument stream header (68 bytes)
    - Check byte 11 for encryption flag (flags & 0x01)
    - Return boolean
  - Per contract: Return False on any error (fail open)

- [X] **T007** Implement private helper: _extract_text_via_antiword() in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Execute subprocess:
    - Get antiword path via `_get_antiword_path()`
    - Run: `subprocess.run([antiword_exe, file_path], capture_output=True, text=True, encoding='utf-8', timeout=30)`
    - Check return code, raise ParsingError if failed
    - Return stdout as UTF-8 string
  - Purpose: Extract plain text from .doc file

- [X] **T008** Implement private helper: _split_into_pages() in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Algorithm (same as DOCXParser):
    - Accept list of paragraphs
    - Accumulate paragraphs until word count exceeds WORDS_PER_PAGE (500)
    - Create PageContent object when threshold crossed
    - Set page_number (1-indexed)
    - Return list of PageContent objects
  - Note: Can reuse logic from DOCXParser if available

- [X] **T009** Implement validate() method in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Validation sequence:
    1. Check file exists → Return ValidationResult(is_valid=False, error_type='file_not_found', ...) if not
    2. Check readable → Return ValidationResult(is_valid=False, error_type='permission_denied', ...) if not
    3. Check valid OLE format (olefile.isOleFile) → Return ValidationResult(is_valid=False, error_type='invalid_format', ...) if not
    4. Check password protection (_is_password_protected) → Return ValidationResult(is_valid=False, error_type='password_protected', ...) if protected
    5. All checks pass → Return ValidationResult(is_valid=True, error_type=None, error_message=None)
  - Per contract: Never raise exceptions

- [X] **T010** Implement get_page_count() method in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Steps:
    - Call _extract_text_via_antiword() to get full text
    - Count total words: `len(text.split())`
    - Calculate pages: `max(1, (total_words + WORDS_PER_PAGE - 1) // WORDS_PER_PAGE)`
    - Return integer >= 1
  - Raises: ParsingError, FileNotFoundError, PasswordProtectedError (via helpers)

- [X] **T011** Implement parse() method in DOCParser
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/doc_parser.py`
  - Processing flow:
    1. Call `_check_file_exists(file_path)` (inherited method)
    2. Call `validate(file_path)` to check password/corruption
    3. If validation fails, raise appropriate error (PasswordProtectedError or ParsingError)
    4. Call `_extract_text_via_antiword(file_path)` to get text
    5. Split text into paragraphs (by newlines/blank lines)
    6. Call `_split_into_pages(paragraphs)` to create PageContent list
    7. Create ParseResult with success=True, pages, page_count
    8. If text < 10 chars, add warning: "Document has no extractable text"
    9. Return ParseResult
  - Error handling: Raise exceptions per contract (PasswordProtectedError, ParsingError)

---

## Phase 3.3: Integration

- [X] **T012** [P] Update ParserFactory PARSER_MAP in src/parsers/factory.py
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/factory.py`
  - Add import: `from .doc_parser import DOCParser`
  - Modify PARSER_MAP dictionary:
    ```python
    PARSER_MAP = {
        '.pdf': PDFParser,
        '.docx': DOCXParser,
        '.doc': DOCParser,  # NEW
    }
    ```
  - No other changes needed (create(), is_supported() use PARSER_MAP automatically)

- [X] **T013** [P] Update file filter in ParserFactory.get_file_filter()
  - File: `/Users/A1E6E98/Developer/kris-extractor/src/parsers/factory.py`
  - Modify method to include *.doc:
    - If hardcoded: Change to `"Supported Documents (*.pdf *.docx *.doc)"`
    - If dynamic: Ensure it generates from PARSER_MAP keys (should auto-include .doc)
  - Purpose: Show .doc files in file picker
  - ALSO FIXED: UI file selector in src/ui/file_selector.py to accept .doc files

- [X] **T014** [P] Update build.spec to bundle antiword.exe
  - File: `/Users/A1E6E98/Developer/kris-extractor/build.spec`
  - Modifications:
    1. Add to `datas` list: `('bin/antiword.exe', '.')`
    2. Add to `hiddenimports` list (if exists): `'olefile'`
  - Ensure antiword.exe is bundled at root of _MEIPASS in PyInstaller bundle
  - Note: Verify paths match where antiword.exe was placed in T002

---

## Phase 3.4: Build & Distribution

- [ ] **T015** Test PyInstaller build with DOC support
  - Run: `pyinstaller build.spec` from repo root
  - Verify build succeeds without errors
  - Check bundle includes:
    - antiword.exe: `7z l dist/kris-extractor.exe | grep antiword` or similar
    - olefile: Check no import errors
  - Expected: Clean build, executable created

- [ ] **T016** Verify bundle size within limits
  - Check: `ls -lh dist/kris-extractor.exe`
  - Constraint: Executable should be < 100MB (per constitution)
  - Note: antiword.exe adds ~200KB, should be well under limit
  - Expected: Bundle size acceptable

---

## Phase 3.5: Manual Validation (Per Constitution)

- [ ] **T017** Manual validation - Basic functionality (per quickstart.md section 1)
  - Test environment: Windows 10/11 (or development environment)
  - Test cases:
    - Select .doc via Browse button → file accepted
    - Drag-and-drop .doc → file accepted
    - File filter shows "*.doc" option
    - Extract keywords from .doc → results generated with correct format
  - Files needed: `valid_english.doc` with known keywords
  - Expected: All basic functionality works

- [ ] **T018** Manual validation - Character encoding (per quickstart.md section 2)
  - Test cases:
    - .doc with Cyrillic text → characters preserved
    - .doc with Latin text → characters preserved
    - .doc with mixed Cyrillic/Latin → both preserved
  - Files needed: `valid_cyrillic.doc`, `valid_mixed.doc`
  - Keywords: "Влажность" (Cyrillic), "Temperature" (Latin)
  - Expected: Perfect character preservation (UTF-8)

- [ ] **T019** Manual validation - Edge cases (per quickstart.md section 3)
  - Test cases:
    - Password-protected .doc → error message: "Password-protected .doc files are not supported"
    - Corrupted .doc → error message: "Unable to parse document. The file may be corrupted or invalid."
    - Empty .doc (no text) → warning displayed, no crash
    - Renamed file (not real .doc) → validation error
  - Files needed: `password_protected.doc`, `corrupted.doc`, `empty.doc`, `fake.doc`
  - Expected: All errors handled gracefully, no crashes

- [ ] **T020** Manual validation - Performance (per quickstart.md section 4)
  - Test cases:
    - Small .doc (<10 pages) → <5 seconds
    - Medium .doc (20-30 pages) → <15 seconds
    - Large .doc (40-50 pages) → <30 seconds
  - Files needed: Various sizes of .doc files
  - Measure: Time from "Extract" click to completion
  - Expected: All performance targets met

- [ ] **T021** Manual validation - Integration (per quickstart.md section 5)
  - Test cases:
    - Switch between PDF → DOC → DOCX → all work
    - Output format same for .doc as PDF/DOCX (metadata, structure, encoding)
    - Page numbers approximate (word-count based, similar to DOCX)
  - Files needed: Same content in .pdf, .docx, .doc formats
  - Expected: Seamless integration, consistent output

---

## Dependencies

**Setup Phase**:
- T001, T002, T003 can run in parallel (different concerns)

**Core Implementation**:
- T004 blocks T005-T011 (need skeleton first)
- T005, T006, T007, T008 can run in parallel [P] (different helpers)
- T009 depends on T006 (_is_password_protected)
- T010 depends on T007 (_extract_text_via_antiword)
- T011 depends on T006, T007, T008, T009 (uses all helpers)

**Integration Phase**:
- T012, T013, T014 can run in parallel [P] (different files)
- All integration tasks depend on T011 (DOCParser complete)

**Build & Validation**:
- T015, T016 depend on T012-T014 (factory integration)
- T017-T021 depend on T015, T016 (working build)

**Critical Path**:
T001-T003 → T004 → T011 → T012-T014 → T015-T016 → T017-T021

---

## Parallel Execution Examples

### Parallel Group 1: Setup (all independent)
```bash
# Can run simultaneously:
Task: "Add olefile dependency to requirements.txt"
Task: "Obtain and bundle antiword binary"
Task: "Install olefile dependency for development"
```

### Parallel Group 2: Helper Methods (different methods, same file - use caution)
```bash
# These modify different parts of same file, coordinate carefully:
Task: "Implement private helper: _get_antiword_path() in DOCParser"
Task: "Implement private helper: _is_password_protected() in DOCParser"
Task: "Implement private helper: _extract_text_via_antiword() in DOCParser"
Task: "Implement private helper: _split_into_pages() in DOCParser"
# Note: Same file, but different methods - can be parallel if agents coordinate
```

### Parallel Group 3: Integration (different files)
```bash
# Can run simultaneously:
Task: "Update ParserFactory PARSER_MAP in src/parsers/factory.py"
Task: "Update file filter in ParserFactory.get_file_filter()"  # Same file as above - SEQUENTIAL
Task: "Update build.spec to bundle antiword.exe"
```

### Parallel Group 4: Manual Validation (can be done simultaneously)
```bash
# Different test scenarios:
Task: "Manual validation - Basic functionality"
Task: "Manual validation - Character encoding"
Task: "Manual validation - Edge cases"
Task: "Manual validation - Performance"
Task: "Manual validation - Integration"
```

---

## Notes

- **[P] tasks** = different files OR different independent methods, no dependencies
- **Same file conflicts**: T012 and T013 both modify factory.py - must be sequential
- **Commit after each task**: Maintain clean history
- **Avoid**: Vague tasks, same file conflicts
- **Manual validation after implementation**: No automated tests per constitution
- **antiword.exe**: Must be obtained separately (GPL-2.0 license, ~200KB)
- **Character encoding**: Critical for Cyrillic support - use UTF-8 throughout
- **Performance target**: <30 seconds for 50-page documents

---

## Validation Checklist
*Applied during task generation*

- [x] All entities have implementation tasks (DOCParser)
- [x] All contract methods have implementation tasks (parse, validate, get_page_count)
- [x] Parallel tasks truly independent (different files)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task (T012/T013 sequential)
- [x] Manual validation tasks included (T017-T021)
- [x] Dependencies clearly mapped
- [x] Build configuration tasks included (T015-T016)

---

**Status**: ✅ Complete - Ready for execution via Task agents
