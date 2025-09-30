# Implementation Plan: Add DOC File Format Support

**Branch**: `002-i-want-to` | **Date**: 2025-09-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/A1E6E98/Developer/kris-extractor/specs/002-i-want-to/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → ✅ Feature spec loaded successfully
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → ✅ No NEEDS CLARIFICATION markers in spec (all resolved via clarification session)
   → ✅ Project Type: Single desktop application
   → ✅ Structure Decision: Existing src/ directory structure
3. Fill the Constitution Check section based on the content of the constitution document.
   → ✅ Constitution v1.0.0 requirements mapped
4. Evaluate Constitution Check section below
   → ✅ No violations - feature extends existing parser system
   → ✅ Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → ✅ Research completed - library selection (antiword), bundling strategy
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
   → ✅ data-model.md created (DOCParser entity definition)
   → ✅ contracts/doc-parser-contract.md created (interface contract)
   → ✅ quickstart.md created (validation checklist)
   → ✅ CLAUDE.md updated (agent context)
7. Re-evaluate Constitution Check section
   → ✅ No new violations introduced
   → ✅ Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
   → ✅ Task generation strategy documented (15-18 tasks estimated)
9. ✅ COMPLETE - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 8. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

Add support for legacy Microsoft Word (.doc) binary format files to the Document Data Extractor, enabling users to process older Word documents alongside existing PDF and DOCX formats. The implementation will create a new DOCParser class that integrates with the existing parser factory architecture, using the `python-docx-legacy` or `antiword` library for .doc file parsing. Page numbering will use the same word-count heuristic as DOCX (~500 words/page), and all error handling will follow existing patterns (password-protected files rejected, corrupted files display generic error message). Performance target: under 30 seconds for typical documents.

## Technical Context

**Language/Version**: Python 3.10+  
**Primary Dependencies**: 
- Existing: PyMuPDF 1.23.0+ (PDF), python-docx 1.1.0+ (DOCX), tkinterdnd2 0.3.0+ (GUI)
- New: python-docx-legacy OR antiword OR textract (to be researched in Phase 0)
**Storage**: JSON configuration file (config.json), keyword history persistence  
**Testing**: Manual validation (per constitution - no automated tests)  
**Target Platform**: Windows 10/11 (developed on macOS)  
**Project Type**: Single desktop application  
**Performance Goals**: <30 seconds for typical documents, consistent with PDF/DOCX  
**Constraints**: Single executable via PyInstaller --onefile, no external dependencies  
**Scale/Scope**: 2-3 users, 5-10 keywords per document, documents up to 50 pages

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### User-First Simplicity
- [x] Single-screen GUI workflow maintained (no UI changes needed)
- [x] No technical knowledge required for operation (transparent to user)
- [x] Complex operations hidden behind simple controls (automatic parser selection)

### Graceful Degradation
- [x] Error handling continues processing on failures (follows existing error patterns)
- [x] All errors collected and reported at end (validation errors, parsing errors)
- [x] Partial results prioritized over complete failure (mark as "not found" vs crash)

### Unicode-First
- [x] Full Cyrillic and Latin character support verified (inherits from base parser)
- [x] Mixed script handling implemented (same as PDF/DOCX)
- [x] Character encoding preserved throughout pipeline (UTF-8)

### Keyword History Persistence
- [x] Keyword storage mechanism defined (no changes - uses existing config.json)
- [x] History persists across sessions (existing functionality)
- [x] Multi-select from history supported (existing functionality)

### Human-Readable Output
- [x] Plain text format with clear labels (uses existing output generator)
- [x] Metadata included (filename, timestamp) (existing functionality)
- [x] Page/line numbers for each extraction (page numbers via word-count heuristic)

### Distribution Requirements
- [x] PyInstaller --onefile configuration (existing build.spec)
- [x] Windows 10/11 compatibility verified (library must be Windows-compatible)
- [x] No external Python/dependencies required (bundle library in executable)

*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*

## Project Structure

### Documentation (this feature)
```
specs/002-i-want-to/
├── spec.md              # Feature specification (completed with clarifications)
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   └── doc-parser-contract.md
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── parsers/
│   ├── __init__.py
│   ├── base.py              # Existing - DocumentParser abstract class
│   ├── pdf_parser.py        # Existing - PyMuPDF implementation
│   ├── docx_parser.py       # Existing - python-docx implementation
│   ├── doc_parser.py        # NEW - .doc parser implementation
│   └── factory.py           # MODIFY - add .doc to PARSER_MAP
├── models/
│   └── (no changes needed)
├── controllers/
│   └── (no changes needed)
├── extractors/
│   └── (no changes needed)
├── services/
│   └── (no changes needed)
├── ui/
│   ├── file_selector.py     # MODIFY - update file filter string
│   └── (other UI files unchanged)
└── main.py                  # No changes needed

requirements.txt             # MODIFY - add .doc parsing library
build.spec                   # MODIFY - include hidden imports if needed
```

**Structure Decision**: Single desktop application using existing src/ directory structure. The .doc support extends the parsers subsystem by adding a new DOCParser class and updating the factory. No architectural changes needed - feature integrates cleanly with existing parser pattern.

## Phase 0: Outline & Research

### Research Tasks

1. **Library Selection for .doc Parsing**
   - Research: Compare python-docx-legacy, antiword, textract, oletools for .doc support
   - Criteria: Windows compatibility, PyInstaller bundling, Unicode support, maintenance status
   - Output: Recommended library with justification

2. **Password Detection in .doc Files**
   - Research: How to detect password-protected .doc files without attempting full parse
   - Goal: Consistent error handling with PDF/DOCX password protection
   - Output: Detection method/pattern

3. **Page Break Detection in .doc Format**
   - Research: Can .doc files provide explicit page break information?
   - Fallback: Confirm word-count heuristic is appropriate
   - Output: Page numbering strategy

4. **PyInstaller Bundling Requirements**
   - Research: Hidden imports, data files, DLL dependencies for chosen library
   - Goal: Ensure --onefile builds work on Windows
   - Output: build.spec modifications needed

5. **Error Patterns in .doc Parsing**
   - Research: Common failure modes (corruption, wrong format, empty files)
   - Goal: Map to existing error types (ParsingError, ValidationResult patterns)
   - Output: Error handling strategy

**Output**: research.md with library selection, bundling strategy, and error handling approach

## Phase 1: Design & Contracts

### 1. Data Model (`data-model.md`)

Extract entities from feature spec:

**DOCParser** (new class)
- Extends: DocumentParser abstract base class
- Methods: parse(), validate(), get_page_count()
- Dependencies: chosen .doc library
- Page strategy: word-count heuristic (WORDS_PER_PAGE = 500)
- Error types: ParsingError, ValidationResult

**ParserFactory** (modified class)
- PARSER_MAP: add `.doc: DOCParser` entry
- get_file_filter(): update to include "*.doc"
- No other changes needed

**Validation Rules**:
- Password-protected → ValidationResult(is_valid=False, error_type='password_protected')
- Corrupted file → ValidationResult(is_valid=False, error_type='corrupted')
- Empty/no text → ParseResult with warnings
- Invalid format → ValidationResult(is_valid=False, error_type='invalid_format')

### 2. API Contracts (`contracts/doc-parser-contract.md`)

**DOCParser Interface Contract**:

```python
class DOCParser(DocumentParser):
    """Parse .doc files using [selected library]"""
    
    WORDS_PER_PAGE = 500  # Same as DOCXParser
    
    def parse(file_path: str) -> ParseResult:
        """
        Input: Absolute path to .doc file
        Output: ParseResult with pages[] and page_count
        Errors: PasswordProtectedError, ParsingError
        Performance: <30 seconds for typical docs
        """
    
    def validate(file_path: str) -> ValidationResult:
        """
        Input: Absolute path to .doc file
        Output: ValidationResult(is_valid, error_type, error_message)
        Error types: password_protected, corrupted, invalid_format
        """
    
    def get_page_count(file_path: str) -> int:
        """
        Input: Absolute path to .doc file
        Output: Approximate page count (word-count based)
        """
```

**Factory Contract Update**:
```python
# In factory.py PARSER_MAP
PARSER_MAP = {
    '.pdf': PDFParser,
    '.docx': DOCXParser,
    '.doc': DOCParser,  # NEW
}

# In factory.py get_file_filter()
return "Supported Documents (*.pdf *.docx *.doc)"  # UPDATED
```

### 3. Validation Checklist (`quickstart.md`)

Manual validation steps for acceptance:

1. **Basic Functionality**
   - [ ] Select .doc file via Browse button → file accepted
   - [ ] Drag-and-drop .doc file → file accepted
   - [ ] File filter shows "*.doc" option
   - [ ] Extract keywords from .doc → results generated

2. **Character Encoding**
   - [ ] .doc with Cyrillic text → characters preserved
   - [ ] .doc with Latin text → characters preserved
   - [ ] .doc with mixed Cyrillic/Latin → both preserved

3. **Edge Cases**
   - [ ] Password-protected .doc → error message displayed
   - [ ] Corrupted .doc → generic error message displayed
   - [ ] Empty .doc (no text) → warning displayed, no crash
   - [ ] Renamed file (not real .doc) → validation error

4. **Performance**
   - [ ] Small .doc (<10 pages) → <5 seconds
   - [ ] Medium .doc (20-30 pages) → <15 seconds
   - [ ] Large .doc (40-50 pages) → <30 seconds

5. **Integration**
   - [ ] Switch between PDF → DOC → DOCX → all work
   - [ ] Output format same for .doc as PDF/DOCX
   - [ ] Page numbers approximate (word-count based)

### 4. Update Agent Context (`CLAUDE.md`)

Will execute: `.specify/scripts/bash/update-agent-context.sh claude`
- Add: .doc parser implementation context
- Add: Selected library and rationale
- Update: Recent changes section
- Preserve: Existing manual additions
- Keep: Under 150 lines

**Output**: data-model.md, contracts/doc-parser-contract.md, quickstart.md, CLAUDE.md

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **From Research (Phase 0)**:
   - Task: Install and test selected .doc parsing library
   - Task: Verify PyInstaller bundling with library

2. **From Contracts (Phase 1)**:
   - Task: Implement DOCParser.parse() method
   - Task: Implement DOCParser.validate() method
   - Task: Implement DOCParser.get_page_count() method
   - Task: Add password detection logic
   - Task: Add corruption detection logic

3. **From Data Model (Phase 1)**:
   - Task: Create doc_parser.py file with DOCParser class [P]
   - Task: Update factory.py PARSER_MAP [P]
   - Task: Update factory.py get_file_filter() [P]
   - Task: Update requirements.txt with library [P]

4. **From Quickstart (Phase 1)**:
   - Task: Manual validation - basic functionality
   - Task: Manual validation - character encoding
   - Task: Manual validation - edge cases
   - Task: Manual validation - performance
   - Task: Manual validation - integration

5. **Build & Distribution**:
   - Task: Update build.spec with hidden imports
   - Task: Test Windows build
   - Task: Verify executable size (<100MB)

**Ordering Strategy**:
1. Library setup (install, test bundling)
2. DOCParser implementation (all methods can be parallel [P])
3. Factory integration (updates can be parallel [P])
4. Manual validation tasks (sequential, depends on implementation)
5. Build verification (final step)

**Estimated Output**: 15-18 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (manual testing per quickstart.md, Windows build verification)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

No constitutional violations. This feature:
- Extends existing parser pattern (no new architecture)
- Maintains single-screen GUI (no UI changes)
- Follows graceful degradation (error handling consistent)
- Preserves Unicode support (inherits from base)
- No testing infrastructure (per constitution)
- Single executable (library bundled via PyInstaller)

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, contracts/, quickstart.md, CLAUDE.md created
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS (no new violations introduced)
- [x] All NEEDS CLARIFICATION resolved (clarification session completed)
- [x] Complexity deviations documented (none - no violations)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*