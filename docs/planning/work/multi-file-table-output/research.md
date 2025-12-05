# Research: Multi-File Batch Processing with Table Output

---
**Date:** 2025-12-04
**Requirements:** `docs/planning/work/multi-file-table-output/requirements.md`
**Exploration Cache:** Loaded from `.exploration-cache.json`
**Status:** complete
---

## Platform Detection

**Stack:** Python 3.10+ / Tkinter
**Version:** Python 3.10+ (pyproject.toml target)
**Build:** pip / PyInstaller for executable packaging

## Dependencies

| Dependency | Version | Purpose | Status |
|------------|---------|---------|--------|
| tkinter | built-in | GUI framework | existing |
| tkinterdnd2 | 0.3.0+ | Drag-and-drop support | existing |
| PyMuPDF | 1.23.0+ | PDF parsing | existing |
| python-docx | 1.1.0+ | DOCX parsing | existing |
| datetime | built-in | Timestamp generation | existing |

No new dependencies required.

## Codebase Patterns

### Architecture
- **Pattern:** MVC with Service Layer
  - Controllers: `src/controllers/app_controller.py`
  - Models: `src/models/`
  - Views/UI: `src/ui/`
  - Services: `src/services/`, `src/extractors/`

### Conventions
- **State:** StateManager with ApplicationState - `src/controllers/state_manager.py`
- **Errors:** Result objects with status fields (OutputResult, ParseResult) - `src/services/output_generator.py:14-27`
- **Async:** ThreadCoordinator for background processing - `src/controllers/thread_coordinator.py`
- **Naming:** Files: snake_case, Classes: PascalCase, Functions: snake_case

### Code Examples

**Current Single File Selection (FileSelector):**
```python
# src/ui/file_selector.py:110-124
def _browse_file(self):
    """Open file dialog for file selection."""
    file_path = filedialog.askopenfilename(
        title="Select Document",
        filetypes=[
            ("Supported Documents", "*.pdf *.docx *.doc"),
            ("PDF Files", "*.pdf"),
            ("Word Documents (DOCX)", "*.docx"),
            ("Word Documents (DOC)", "*.doc"),
            ("All Files", "*.*")
        ]
    )
    if file_path:
        self._select_file(file_path)
```

**Current Output Table Formatting (OutputGenerator):**
```python
# src/services/output_generator.py:40-82
def _calculate_column_widths(self, headers: list[str], rows: list[list[str]]) -> list[int]:
    """Calculate optimal column widths for table formatting."""
    if not headers:
        return []
    widths = [len(header) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            if i < len(widths):
                widths[i] = max(widths[i], len(str(cell)))
    return widths

def _format_table_row(self, cells: list[str], widths: list[int]) -> str:
    """Format a single table row with column alignment."""
    formatted_cells = []
    for i, cell in enumerate(cells):
        if i < len(widths):
            formatted_cells.append(str(cell).ljust(widths[i] + 4))
        else:
            formatted_cells.append(str(cell))
    return ''.join(formatted_cells).rstrip()
```

**Extraction Flow (AppController._perform_extraction):**
```python
# src/controllers/app_controller.py:429-487
def _perform_extraction(self, document: Document, keywords: list[Keyword]):
    """Perform extraction in worker thread."""
    reporter = ProgressReporter(self.thread_coordinator)
    # Parse document
    parser = ParserFactory.create(document.file_path)
    parse_result = parser.parse(document.file_path)
    # Extract data
    extraction_engine = ExtractionEngine()
    keyword_texts = [kw.text for kw in keywords]
    results = extraction_engine.extract(parse_result.pages, keyword_texts, document)
    # Generate output file
    output_result = self.output_generator.generate(results, self.config)
    results.output_path = output_result.output_path
    return results
```

**PersonalInformation.get_abbreviated_name():**
```python
# src/models/personal_information.py:90-111
def get_abbreviated_name(self) -> str | None:
    """Generate abbreviated name from first letters."""
    if not self.full_name:
        return None
    parts = self.full_name.strip().split()
    return ''.join(part[0].upper() for part in parts if part)
```

## Integration Points

| Component | Location | Change | Impact |
|-----------|----------|--------|--------|
| FileSelector | `src/ui/file_selector.py` | modify | Multi-select UI, stores list of files |
| AppController | `src/controllers/app_controller.py` | modify | Batch processing loop, multi-file handling |
| OutputGenerator | `src/services/output_generator.py` | modify | New batch table output format |
| ApplicationState | `src/models/application_state.py` | modify | Store list of documents instead of single |
| BatchExtractionResults | `src/models/` | create | New model for batch results |

**Flow:**
```
FileSelector (multi-select)
    → AppController.on_files_selected()
    → loop: parse + extract each document
    → aggregate BatchExtractionResults
    → OutputGenerator.generate_batch()
    → single output file with table format
```

## Clarifications & Decisions

### Multi-Select UI Approach
**Question:** How to implement multi-file selection?
**Finding:** tkinter's `filedialog.askopenfilenames()` (plural) returns tuple of file paths
**Decision:** Change `askopenfilename` to `askopenfilenames` and update callback/state
**Rationale:** Minimal change, native tkinter support

### Batch vs Single File Processing
**Question:** Should batch mode replace single-file mode or coexist?
**Decision:** Same UI handles both - selecting one file = batch of 1
**Rationale:** Simpler UX, consistent behavior, no mode switching needed

### Output Format - Semicolon Delimiter with Padding
**Question:** How to format the aligned table with semicolons?
**Finding:** Existing `_calculate_column_widths` and `_format_table_row` methods provide alignment
**Decision:** Modify row formatting to use `"; "` as separator instead of spaces
**Rationale:** User requested semicolons + alignment; format: `value ; value ; value ;`

### First Occurrence Only
**Question:** How to get only first occurrence of each keyword?
**Finding:** Current code groups matches by keyword in `format_output()` at line 216-222
**Decision:** For batch output, take only `keyword_groups[keyword][0]` (first match per keyword per document)
**Rationale:** Explicit requirement; simpler output

### Filename Format
**Question:** What filename format for batch output?
**Decision:** `batch_YYYY-MM-DD_HHMMSS.txt` using datetime.now()
**Rationale:** User confirmed auto-generated; timestamp ensures uniqueness

## Risks & Unknowns

**Risks:**
1. **Large batch sizes may be slow** - Mitigation: Progress reporting per file, consider chunking if needed
2. **Memory usage with many files** - Mitigation: Process sequentially, don't hold all parsed content in memory
3. **Mixed encodings in files** - Mitigation: Existing parsers handle encoding; UTF-8 output

**Unknowns:**
- None remaining - all clarifications resolved

## Summary

**Key Findings:**
1. Multi-file selection is a simple change: `askopenfilename` → `askopenfilenames`
2. Existing table formatting logic (`_calculate_column_widths`, `_format_table_row`) can be adapted for semicolon-delimited output with padding
3. Batch processing requires looping the existing extraction flow, with aggregation of results
4. New output format is fundamentally different (rows = documents, columns = Initials + Age + keywords)

**Confidence:** High
- Clear path forward with existing patterns
- All requirements clarified
- Minimal new dependencies

**Next Steps:**
1. Create BatchExtractionResults model
2. Update FileSelector for multi-select
3. Modify AppController for batch loop
4. Create new batch output formatter in OutputGenerator

---
**Ready for Planning:** Yes
