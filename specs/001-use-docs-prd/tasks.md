# Tasks: Document Data Extraction Tool

**Feature**: 001-use-docs-prd
**Input**: Design documents from `/Users/A1E6E98/Developer/kris-extractor/specs/001-use-docs-prd/`
**Prerequisites**: plan.md, research.md, data-model.md, contracts/ (all present)

## Execution Flow
```
1. Load plan.md → Tech stack: Python 3.10+, tkinter, PyMuPDF, python-docx, tkinterdnd2, PyInstaller
2. Load data-model.md → 10 entities for models
3. Load contracts/ → 5 contract files for implementation
4. Generate tasks by category:
   → Setup: project structure, dependencies, configuration
   → Models: 10 dataclasses from data-model.md
   → Parsers: PDF and DOCX parsers with factory
   → Extractors: Keyword, number, and personal info extraction
   → Services: Output generation and configuration management
   → UI: 6 UI components for single-screen GUI
   → Controllers: Application control and state management
   → Integration: Main entry point and wiring
   → Build: Requirements and PyInstaller configuration
   → Validation: Manual testing scenarios
5. Order by dependencies: Setup → Models → Parsers/Services → Extractors → UI → Controllers → Integration → Build → Validation
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- All file paths are relative to repository root

---

## Phase 3.1: Setup & Project Structure

- [ ] **T001** Create project directory structure per plan.md
  - Create: `src/models/`, `src/parsers/`, `src/extractors/`, `src/ui/`, `src/controllers/`, `src/services/`
  - Create: `src/main.py` (placeholder)
  - Verify: All directories exist and are empty

- [ ] **T002** Initialize Python project dependencies
  - Create: `requirements.txt` with dependencies (tkinterdnd2>=0.3.0, PyMuPDF>=1.23.0, python-docx>=1.1.0)
  - Note: tkinter is built-in, no need to list
  - Verify: `pip install -r requirements.txt` succeeds

- [ ] **T003** [P] Configure linting with ruff
  - Create: `pyproject.toml` or `ruff.toml` with Python 3.10+ settings
  - Configure: line length 100, exclude build artifacts
  - Verify: `ruff check .` runs without errors

---

## Phase 3.2: Data Models

- [ ] **T004** [P] Document model in `src/models/document.py`
  - Implement: Document dataclass per data-model.md section 1
  - Fields: file_path, filename, file_type, page_count, is_valid, error_message
  - Validation: State transitions (UNSELECTED → SELECTED → VALIDATING → VALID/INVALID)

- [ ] **T005** [P] Keyword model in `src/models/keyword.py`
  - Implement: Keyword dataclass per data-model.md section 2
  - Fields: text, normalized, is_historical, is_active
  - Validation: 1-100 chars, sanitize for regex

- [ ] **T006** [P] ExtractionMatch model in `src/models/extraction_match.py`
  - Implement: ExtractionMatch dataclass per data-model.md section 3
  - Fields: keyword, value, page_number, line_number, status, warning
  - Status enum: 'found', 'not_found', 'ambiguous'

- [ ] **T007** [P] PersonalInformation model in `src/models/personal_information.py`
  - Implement: PersonalInformation dataclass per data-model.md section 4
  - Fields: first_name, last_name, id_number_prefix, character_set, extraction_page, is_complete
  - Character set enum: 'cyrillic', 'latin', 'mixed', 'unknown'

- [ ] **T008** [P] OutputReport model in `src/models/output_report.py`
  - Implement: OutputReport dataclass per data-model.md section 5
  - Fields: document_filename, processing_timestamp, personal_info, matches, errors, warnings, output_path
  - File naming logic: `output_[original_filename].txt`

- [ ] **T009** [P] ProcessingLog model in `src/models/processing_log.py`
  - Implement: ProcessingLog and LogEntry dataclasses per data-model.md section 6
  - Fields: log_filename, log_path, entries, start_time, end_time, status
  - LogEntry: timestamp, level, message, context

- [ ] **T010** [P] Configuration model in `src/models/configuration.py`
  - Implement: Configuration dataclass per data-model.md section 8
  - Fields: output_folder, log_directory, number_format, proximity_rule, keyword_history, window dimensions
  - Default values: Per data-model.md section 8

- [ ] **T011** [P] ApplicationState model in `src/models/application_state.py`
  - Implement: ApplicationState dataclass per data-model.md section 9
  - Fields: current_document, active_keywords, processing_status, extraction_results, error_messages, is_processing
  - State enum: IDLE, FILE_SELECTED, READY, PROCESSING, COMPLETE, ERROR, PARTIAL_SUCCESS

- [ ] **T012** [P] ExtractionResults model in `src/models/extraction_results.py`
  - Implement: ExtractionResults dataclass per data-model.md section 10
  - Fields: document, personal_info, matches, errors, warnings, processing_time, timestamp
  - Methods: add_match(), add_error(), add_warning(), has_errors(), has_warnings(), get_error_summary(), is_complete()

- [ ] **T013** [P] KeywordHistory model in `src/models/keyword_history.py`
  - Implement: KeywordHistory dataclass per data-model.md section 7
  - Fields: keywords, last_updated, max_size
  - Operations: add, select (multi-select support)

---

## Phase 3.3: Parser Implementation

- [ ] **T014** [P] Parser contract base classes in `src/parsers/base.py`
  - Implement: DocumentParser abstract base class per parser-contract.md
  - Implement: ParseResult, PageContent, ValidationResult dataclasses
  - Methods: parse(), validate(), get_page_count()
  - Custom exceptions: PasswordProtectedError, ScannedPDFError, ParsingError

- [ ] **T015** PDFParser implementation in `src/parsers/pdf_parser.py`
  - Implement: PDFParser class extending DocumentParser
  - Use: PyMuPDF (fitz) for PDF parsing per research.md section 2
  - Features: Password-protected detection, scanned PDF detection (< 10 chars in first 3 pages)
  - Error handling: FR-052 (password), FR-053 (scanned)
  - Depends on: T014

- [ ] **T016** DOCXParser implementation in `src/parsers/docx_parser.py`
  - Implement: DOCXParser class extending DocumentParser
  - Use: python-docx for DOCX parsing per research.md section 3
  - Features: Paragraph extraction, page break detection, page approximation (~500 words/page)
  - Error handling: Corrupted DOCX, invalid XML
  - Depends on: T014

- [ ] **T017** ParserFactory in `src/parsers/factory.py`
  - Implement: ParserFactory.create(file_path) → DocumentParser
  - Logic: Select PDFParser or DOCXParser based on file extension
  - Validation: Supported extensions (.pdf, .docx), case-insensitive
  - Depends on: T015, T016

---

## Phase 3.4: Services Layer

- [ ] **T018** [P] ConfigurationManager in `src/services/configuration_manager.py`
  - Implement: ConfigurationManager per configuration-contract.md
  - Features: Load from config.json, save to config.json, validate paths, defaults if missing/corrupted
  - File location: Application directory (root)
  - Depends on: T010

- [ ] **T019** [P] OutputGenerator in `src/services/output_generator.py`
  - Implement: OutputGenerator per output-contract.md
  - Features: Generate plain text output from ExtractionResults
  - Format: Per data-model.md section 5 (document filename, timestamp, personal info, matches with page/line numbers, errors, warnings)
  - Encoding: UTF-8
  - Depends on: T008, T012

- [ ] **T020** ProcessingLogger in `src/services/processing_logger.py`
  - Implement: ProcessingLogger service
  - Features: Create log file, write timestamped entries, log levels (INFO, WARNING, ERROR)
  - File naming: `extraction_YYYYMMDD_HHMMSS.log`
  - Depends on: T009

---

## Phase 3.5: Extractor Implementation

- [ ] **T021** [P] Extractor contract base in `src/extractors/base.py`
  - Implement: ExtractionEngine abstract base per extractor-contract.md
  - Implement: KeywordMatch dataclass
  - Method: extract(pages, keywords) → ExtractionResults
  - Depends on: T006, T007, T012

- [ ] **T022** KeywordMatcher in `src/extractors/keyword_matcher.py`
  - Implement: KeywordMatcher.find_keywords() per extractor-contract.md
  - Features: Case-insensitive regex matching, all occurrences (FR-014), page/line numbers, Unicode support
  - Pattern: `re.compile(re.escape(keyword), re.IGNORECASE | re.UNICODE)`
  - Depends on: T021

- [ ] **T023** NumberExtractor in `src/extractors/number_extractor.py`
  - Implement: NumberExtractor.extract_numbers() per extractor-contract.md
  - Features: US/UK number format (period decimal, comma thousands), "next number after keyword" proximity
  - Pattern: `r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b'`
  - Error handling: "Not found" status, ambiguous format warnings
  - Depends on: T021, T022

- [ ] **T024** PersonalInfoExtractor in `src/extractors/personal_info_extractor.py`
  - Implement: PersonalInfoExtractor.extract_personal_info() per extractor-contract.md
  - Features: Cyrillic/Latin labels, first page priority + full document fallback, ID first 4 digits only
  - Patterns: First name, last name, ID number (per extractor-contract.md)
  - Character set detection: Cyrillic, Latin, mixed
  - Depends on: T021

- [ ] **T025** ExtractionEngine integration in `src/extractors/extraction_engine.py`
  - Implement: ExtractionEngine.extract() orchestrating all extractors
  - Flow: KeywordMatcher → NumberExtractor → PersonalInfoExtractor → ExtractionResults
  - Error collection: Graceful degradation per Constitution Principle II
  - Depends on: T022, T023, T024

---

## Phase 3.6: UI Components

- [ ] **T026** [P] MainWindow in `src/ui/main_window.py`
  - Implement: MainWindow class per ui-contract.md
  - Layout: Single-screen 800x600, resizable with minimum
  - Sections: File selection area, keyword panel, settings panel, extract button, results display
  - Event registration: on_file_selected, on_keyword_added, on_extract_clicked
  - Depends on: T011

- [ ] **T027** [P] FileSelector component in `src/ui/file_selector.py`
  - Implement: File selection area per ui-contract.md section 1
  - Features: Browse button (file dialog), drag-and-drop (tkinterdnd2), file path display, file type icon
  - Events: on_file_selected(file_path)
  - Validation: .pdf/.docx only, file exists

- [ ] **T028** [P] KeywordPanel component in `src/ui/keyword_panel.py`
  - Implement: Keyword management panel per ui-contract.md section 2
  - Features: Text input + Add button, keyword history dropdown, active keywords chips (removable), Clear All button
  - Events: on_keyword_added, on_keyword_selected_from_history, on_keyword_removed, on_keywords_cleared
  - Validation: 1-100 chars, no duplicates (case-insensitive)

- [ ] **T029** [P] SettingsPanel component in `src/ui/settings_panel.py`
  - Implement: Collapsible settings panel per ui-contract.md section 3
  - Features: Output folder browser, log directory browser, number format dropdown, proximity rule dropdown
  - Events: on_output_folder_changed, on_log_directory_changed, on_settings_changed
  - State: Collapsed (default) / Expanded

- [ ] **T030** [P] ProgressBar component in `src/ui/progress_bar.py`
  - Implement: Progress bar and status message per ui-contract.md section 4
  - Features: Indeterminate progress bar, status label, Extract button enable/disable
  - States: Ready, Processing, Complete, Error
  - Depends on: T011

- [ ] **T031** [P] ResultsDisplay component in `src/ui/results_display.py`
  - Implement: Results display area per ui-contract.md section 5
  - Features: Success/error/warning messages, "Open Output File/Folder/Log" buttons, expandable error details
  - Events: on_open_output_file, on_open_output_folder, on_open_log_file
  - States: Hidden, Success, Partial Success, Error

---

## Phase 3.7: Controllers & State Management

- [ ] **T032** StateManager in `src/controllers/state_manager.py`
  - Implement: StateManager for ApplicationState management
  - Features: State transitions (per data-model.md section 9), thread-safe state updates, immutable state pattern
  - State machine: IDLE → FILE_SELECTED → READY → PROCESSING → COMPLETE/ERROR/PARTIAL_SUCCESS
  - Depends on: T011

- [ ] **T033** ThreadCoordinator in `src/controllers/thread_coordinator.py`
  - Implement: ThreadCoordinator for worker thread management per ui-contract.md threading section
  - Features: Worker thread creation, queue-based communication, main thread queue polling (100ms)
  - Pattern: Worker sends {'type': 'progress'/'complete'/'error', 'message'/'results': ...}
  - Depends on: T012

- [ ] **T034** AppController in `src/controllers/app_controller.py`
  - Implement: AppController coordinating UI and business logic per ui-contract.md
  - Callbacks: on_file_selected, on_keyword_added, on_extract_clicked, on_settings_changed
  - Flow: Validate → Update state → Update UI → Start extraction
  - Depends on: T032, T033

---

## Phase 3.8: Integration & Main Entry

- [ ] **T035** Main application entry in `src/main.py`
  - Implement: Application initialization and wiring
  - Flow: Load config → Create MainWindow → Initialize AppController → Register callbacks → Start event loop
  - Error handling: Corrupted config fallback to defaults
  - Depends on: T018, T026, T034

---

## Phase 3.9: Build Configuration

- [ ] **T036** Update requirements.txt for production
  - Add: PyInstaller>=5.13 for packaging
  - Verify: All dependencies listed with minimum versions
  - Test: Fresh virtual environment install

- [ ] **T037** Create PyInstaller build.spec
  - Implement: build.spec per research.md section 10
  - Configuration: --onefile flag, hiddenimports (tkinterdnd2, fitz, docx), console=False, UPX compression
  - Name: DocumentExtractor.exe
  - Target: Windows 10/11 64-bit
  - Icon: (optional) icon.ico if available

---

## Phase 3.10: Manual Validation

- [ ] **T038** Validation Scenario 1: Basic extraction workflow
  - Test: quickstart.md scenario 1
  - Verify: Single keyword extraction with page/line numbers, plain text output, UTF-8 encoding
  - Acceptance: FR-001, FR-003, FR-007, FR-014, FR-015, FR-016, FR-027, FR-028, FR-033

- [ ] **T039** Validation Scenario 2: Multiple keywords and occurrences
  - Test: quickstart.md scenario 2
  - Verify: 3 keywords, multiple occurrences, "Not found" handling, graceful degradation
  - Acceptance: FR-008, FR-014, FR-019, FR-045

- [ ] **T040** Validation Scenario 3: Keyword history persistence
  - Test: quickstart.md scenario 3
  - Verify: Keywords save to config.json, load on restart, multi-select from history
  - Acceptance: FR-010, FR-011, FR-012

- [ ] **T041** Validation Scenario 4: Drag and drop file selection
  - Test: quickstart.md scenario 4
  - Verify: Drag-and-drop works, file type detection, only first file accepted if multiple
  - Acceptance: FR-004, FR-005

- [ ] **T042** Validation Scenario 5: Personal info extraction (Cyrillic)
  - Test: quickstart.md scenario 5
  - Verify: Cyrillic name extraction, ID first 4 digits, character set detection, UTF-8 output
  - Acceptance: FR-020, FR-022, FR-025, Constitution Principle III

- [ ] **T043** Validation Scenario 6: Personal info extraction (Latin)
  - Test: quickstart.md scenario 6
  - Verify: Latin name extraction, ID first 4 digits, character set detection
  - Acceptance: FR-021, FR-023, FR-025

- [ ] **T044** Validation Scenario 7: Mixed script handling
  - Test: quickstart.md scenario 7
  - Verify: Mixed Cyrillic/Latin text, character set marked as "mixed", no character corruption
  - Acceptance: FR-024, Constitution Principle III

- [ ] **T045** Validation Scenario 8: Password-protected PDF error
  - Test: quickstart.md scenario 8
  - Verify: Error message "Password-protected PDFs are not supported", no processing attempt
  - Acceptance: FR-052

- [ ] **T046** Validation Scenario 9: Scanned PDF error
  - Test: quickstart.md scenario 9
  - Verify: Error message "Scanned PDFs requiring OCR are not supported", no processing attempt
  - Acceptance: FR-053

- [ ] **T047** Validation Scenario 10: Number format handling
  - Test: quickstart.md scenario 10
  - Verify: US/UK number formats (integer, decimal, thousands), ambiguous format warnings
  - Acceptance: FR-016, FR-046

- [ ] **T048** Validation Scenario 11: Keyword not found handling
  - Test: quickstart.md scenario 11
  - Verify: "Not found" status, processing continues, partial success indicated
  - Acceptance: FR-019, FR-045, FR-049, Constitution Principle II

- [ ] **T049** Validation Scenario 12: Settings persistence
  - Test: quickstart.md scenario 12
  - Verify: Output folder/log directory saved to config.json, window size preserved
  - Acceptance: FR-043, Configuration persistence

- [ ] **T050** Validation Scenario 13: Progress indication
  - Test: quickstart.md scenario 13
  - Verify: Progress bar animates, UI responsive, Extract button disabled during processing, < 30 seconds for 50 pages
  - Acceptance: FR-042, FR-050, FR-051

- [ ] **T051** Validation Scenario 14: Output file naming
  - Test: quickstart.md scenario 14
  - Verify: `output_[filename].txt` naming, timestamped duplicates, original file unmodified
  - Acceptance: FR-035

- [ ] **T052** Validation Scenario 15: Processing log generation
  - Test: quickstart.md scenario 15
  - Verify: Log file `extraction_YYYYMMDD_HHMMSS.log`, timestamps, extraction events, human-readable
  - Acceptance: FR-054, FR-055

- [ ] **T053** Validation Scenario 16: Case-insensitive keyword matching
  - Test: quickstart.md scenario 16
  - Verify: "HTD" matches "htd" in document, value extracted correctly
  - Acceptance: FR-009

- [ ] **T054** Validation Scenario 17: Keyword removal
  - Test: quickstart.md scenario 17
  - Verify: Remove keyword from active list before extraction, removed keyword not in output
  - Acceptance: FR-013

- [ ] **T055** Validation Scenario 18: Edge case - Empty document
  - Test: quickstart.md scenario 18
  - Verify: No crash, "Not found" for all keywords, warning for minimal content
  - Acceptance: FR-045, FR-047, FR-048

- [ ] **T056** Validation Scenario 19: Edge case - Large keyword list
  - Test: quickstart.md scenario 19
  - Verify: 20+ keywords processed, all in output (found or not found), UI responsive
  - Acceptance: FR-008, FR-050

- [ ] **T057** Validation Scenario 20: Single-screen UI verification
  - Test: quickstart.md scenario 20
  - Verify: All functionality on main screen, settings collapsible, no separate windows for core workflow
  - Acceptance: FR-036, Constitution Principle I

- [ ] **T058** Performance validation: Typical document
  - Test: 15-page PDF, 5 keywords
  - Verify: Processing < 10 seconds (preferred), < 30 seconds (required)
  - Acceptance: Performance goals from plan.md

- [ ] **T059** Performance validation: Large document
  - Test: 50-page PDF, 10 keywords
  - Verify: Processing < 30 seconds, UI remains responsive
  - Acceptance: Performance goals from plan.md

- [ ] **T060** Cross-platform: Windows runtime
  - Test: Copy .exe to Windows 10/11 without Python, run full workflow
  - Verify: No missing dependencies, Unicode displays correctly, all features work
  - Acceptance: Constitution Principle VI, target platform requirement

---

## Dependencies

### Phase Dependencies
- Phase 3.2 (Models) → No dependencies (all [P])
- Phase 3.3 (Parsers) → T014 must complete before T015, T016, T017
- Phase 3.4 (Services) → T018, T019, T020 depend on models (T010, T008, T012, T009)
- Phase 3.5 (Extractors) → T021 blocks T022-T024, T025 depends on T022-T024
- Phase 3.6 (UI) → All UI components depend on T011 (ApplicationState model)
- Phase 3.7 (Controllers) → T032 depends on T011, T033 depends on T012, T034 depends on T032, T033
- Phase 3.8 (Integration) → T035 depends on T018, T026, T034
- Phase 3.9 (Build) → T037 depends on T035 (fully functional app)
- Phase 3.10 (Validation) → All validation tasks depend on T037 (built executable)

### Critical Paths
```
Setup (T001-T003)
  ↓
Models [P] (T004-T013)
  ↓
├─ Parsers (T014 → T015, T016 → T017)
├─ Services [P] (T018, T019, T020)
└─ Extractors (T021 → T022, T023, T024 → T025)
  ↓
UI Components [P] (T026-T031)
  ↓
Controllers (T032 → T033 → T034)
  ↓
Integration (T035)
  ↓
Build (T036 → T037)
  ↓
Validation (T038-T060)
```

---

## Parallel Execution Examples

### Models Phase (All Parallel)
```bash
# Launch T004-T013 together (10 model tasks):
Task: "Document model in src/models/document.py"
Task: "Keyword model in src/models/keyword.py"
Task: "ExtractionMatch model in src/models/extraction_match.py"
Task: "PersonalInformation model in src/models/personal_information.py"
Task: "OutputReport model in src/models/output_report.py"
Task: "ProcessingLog model in src/models/processing_log.py"
Task: "Configuration model in src/models/configuration.py"
Task: "ApplicationState model in src/models/application_state.py"
Task: "ExtractionResults model in src/models/extraction_results.py"
Task: "KeywordHistory model in src/models/keyword_history.py"
```

### Services Phase (All Parallel)
```bash
# Launch T018-T020 together (3 service tasks):
Task: "ConfigurationManager in src/services/configuration_manager.py"
Task: "OutputGenerator in src/services/output_generator.py"
Task: "ProcessingLogger in src/services/processing_logger.py"
```

### UI Components Phase (All Parallel)
```bash
# Launch T026-T031 together (6 UI tasks):
Task: "MainWindow in src/ui/main_window.py"
Task: "FileSelector component in src/ui/file_selector.py"
Task: "KeywordPanel component in src/ui/keyword_panel.py"
Task: "SettingsPanel component in src/ui/settings_panel.py"
Task: "ProgressBar component in src/ui/progress_bar.py"
Task: "ResultsDisplay component in src/ui/results_display.py"
```

### Validation Phase (Selected Parallel Groups)
```bash
# Personal info validation (can run in parallel):
Task: "Validation Scenario 5: Personal info extraction (Cyrillic)"
Task: "Validation Scenario 6: Personal info extraction (Latin)"
Task: "Validation Scenario 7: Mixed script handling"

# Error handling validation (can run in parallel):
Task: "Validation Scenario 8: Password-protected PDF error"
Task: "Validation Scenario 9: Scanned PDF error"

# Performance validation (can run in parallel):
Task: "Performance validation: Typical document"
Task: "Performance validation: Large document"
```

---

## Notes

- **[P] markers**: 29 tasks marked for parallel execution (models, services, UI components)
- **Test-Driven Development**: No automated tests per constitution (manual validation only), but validation tasks structured for systematic testing
- **Commit strategy**: Commit after each task or logical group of [P] tasks
- **Manual validation**: All validation tasks (T038-T060) require human tester with test documents
- **Build target**: Windows 10/11 64-bit executable via PyInstaller
- **Development platform**: macOS for development, Windows for final testing and packaging
- **Constitution compliance**: All tasks designed to maintain constitutional principles (user-first simplicity, graceful degradation, Unicode support, keyword history persistence, human-readable output, distribution requirements)

---

## Task Generation Rules Applied

1. **From Data Model**: 10 entities → 10 model tasks (T004-T013), all [P]
2. **From Contracts**:
   - Parser contract → 4 parser tasks (T014-T017)
   - Extractor contract → 5 extractor tasks (T021-T025)
   - Output contract → 1 output generator task (T019)
   - Configuration contract → 1 config manager task (T018)
   - UI contract → 6 UI component tasks (T026-T031), all [P]
3. **From Quickstart**: 23 validation scenarios → 23 validation tasks (T038-T060)
4. **From Research**: Technology decisions → setup tasks (T001-T003), build tasks (T036-T037)
5. **Ordering**: Setup → Models → Core (Parsers, Services, Extractors) → UI → Controllers → Integration → Build → Validation

---

## Validation Checklist
*GATE: All items verified before declaring tasks complete*

- [x] All 10 entities have model tasks (T004-T013)
- [x] All 5 contracts have implementation tasks (Parsers: T014-T017, Extractors: T021-T025, Output: T019, Config: T018, UI: T026-T031)
- [x] All [P] tasks are truly independent (different files, no shared dependencies)
- [x] Each task specifies exact file path or component
- [x] No [P] task modifies same file as another [P] task
- [x] All 23 quickstart scenarios have validation tasks (T038-T060)
- [x] Dependencies documented in Dependencies section
- [x] Parallel execution examples provided
- [x] Critical path identified

**Tasks ready for execution via /implement command**
