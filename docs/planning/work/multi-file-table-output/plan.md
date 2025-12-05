# Implementation Plan: Multi-File Batch Processing with Table Output

---
**Date:** 2025-12-04
**Requirements:** `docs/planning/work/multi-file-table-output/requirements.md`
**Research:** `docs/planning/work/multi-file-table-output/research.md`
**Branch:** `feature/multi-file-table-output`
**Status:** draft
---

## Summary

**What:** Enable batch processing of multiple patient documents with consolidated output formatted as an aligned, semicolon-delimited table.

**Why:** Medical professionals need to process multiple patient records efficiently and receive results in a spreadsheet-ready format.

**Who:** Medical data analysts processing patient documents (PDF, DOCX, DOC).

## Technical Context

**Stack:** Python 3.10+ / Tkinter
**Version:** Python 3.10+
**Build:** pip / PyInstaller

**Key Dependencies:**
- tkinter: GUI framework with native multi-file dialog support
- Existing parsers (PyMuPDF, python-docx): Document parsing
- datetime: Timestamp generation for filenames

**Architecture:** MVC with Service Layer
- Controllers handle orchestration
- Models contain data structures
- Services perform business logic
- UI components remain decoupled

**Files:**
| File | Action | Purpose |
|------|--------|---------|
| `src/ui/file_selector.py` | modify | Multi-file selection UI |
| `src/controllers/app_controller.py` | modify | Batch processing orchestration |
| `src/services/output_generator.py` | modify | Table output formatting |
| `src/models/application_state.py` | modify | Store multiple documents |
| `src/models/batch_extraction_results.py` | create | Aggregate results container |

## Technical Decisions

1. **Multi-select approach:** Use `askopenfilenames()` (native tkinter) - simplest solution with no new dependencies
2. **Batch vs single mode:** Unified handling - single file = batch of 1, no mode switching
3. **Table format:** Semicolon delimiter with space padding (`value ; value ;`) for both CSV compatibility and visual alignment
4. **First occurrence only:** Take first match per keyword per document to simplify output

## Phase Breakdown

### Phase 0: Models & Data Structures
**Goal:** Create the data structures needed for batch processing

**Deliverables:**
- [ ] Create `BatchExtractionResults` model to hold list of `ExtractionResults`
- [ ] Update `ApplicationState` to store list of `Document` instead of single document
- [ ] Add helper methods for batch result aggregation

**Dependencies:** None
**Effort:** 1-2 hours

**Success Criteria:**
- Models can store and access multiple documents
- BatchExtractionResults can aggregate data from multiple ExtractionResults

**Approach:** Create a simple dataclass for BatchExtractionResults containing a list of ExtractionResults plus metadata. Update ApplicationState.current_document to current_documents (list). Maintain backward compatibility with helper properties.

---

### Phase 1: Multi-File Selection UI
**Goal:** Enable users to select multiple files in the file selector

**Deliverables:**
- [ ] Update FileSelector to use `askopenfilenames()` instead of `askopenfilename()`
- [ ] Update file display to show count of selected files
- [ ] Update drag-and-drop to accept multiple files
- [ ] Update callback signature to handle list of file paths

**Dependencies:** Phase 0 (ApplicationState changes)
**Effort:** 2-3 hours

**Success Criteria:**
- User can select multiple files via Browse dialog
- User can drag-and-drop multiple files
- UI displays "N files selected" or individual filename for single file
- Callback receives list of file paths

**Approach:** Change `_browse_file` to use `askopenfilenames()`. Update `_handle_drop` to process all dropped files instead of just first. Modify `_file_selected_callback` signature to accept `list[str]`. Update display logic to show file count.

---

### Phase 2: Batch Processing Controller Logic
**Goal:** Enable AppController to process multiple documents in sequence

**Deliverables:**
- [ ] Update `on_file_selected` to `on_files_selected` accepting list
- [ ] Create batch extraction method that loops through documents
- [ ] Update progress reporting to show current file / total files
- [ ] Aggregate individual ExtractionResults into BatchExtractionResults

**Dependencies:** Phase 0, Phase 1
**Effort:** 2-3 hours

**Success Criteria:**
- All selected documents are processed sequentially
- Progress shows "Processing file 2 of 5..."
- Results are aggregated correctly
- Errors on one file don't stop processing of others

**Approach:** Create `on_files_selected()` handler. Modify `_perform_extraction` to accept list of documents and return BatchExtractionResults. Use existing ThreadCoordinator for background processing. Report progress per document.

---

### Phase 3: Batch Table Output Format
**Goal:** Generate the aligned semicolon-delimited table output

**Deliverables:**
- [ ] Create `generate_batch()` method in OutputGenerator
- [ ] Implement aligned column formatting with semicolons
- [ ] Generate header row: `Initials; Age; Keyword1; Keyword2; ...`
- [ ] Generate data rows: one per document with first-occurrence values
- [ ] Implement auto-generated filename: `batch_YYYY-MM-DD_HHMMSS.txt`

**Dependencies:** Phase 0, Phase 2
**Effort:** 3-4 hours

**Success Criteria:**
- Output file contains header row with column names
- Each document produces exactly one data row
- Columns are visually aligned with consistent widths
- Semicolons follow each value including last
- Missing values show as empty but maintain column width
- Filename follows `batch_YYYY-MM-DD_HHMMSS.txt` format

**Approach:** Create new `generate_batch()` method. First pass: collect all values to calculate column widths. Second pass: format rows with padding. Use format `{value.ljust(width)}; ` for each cell.

---

### Phase 4: Integration & Polish
**Goal:** Wire everything together and handle edge cases

**Deliverables:**
- [ ] Update MainWindow to handle batch results display
- [ ] Update ResultsDisplay for batch success message
- [ ] Handle edge cases: empty files, missing personal info, mixed file types
- [ ] Add error handling for partial batch failures
- [ ] Ensure single-file mode still works (batch of 1)

**Dependencies:** Phase 1, 2, 3
**Effort:** 2-3 hours

**Success Criteria:**
- End-to-end flow works: select files → extract → view output
- Single file selection produces table with header + 1 row
- Mixed file types (PDF + DOCX) process correctly
- Partial failures are reported but don't stop processing
- Output can be opened and viewed

**Approach:** Update UI callbacks. Add batch-specific success message ("Processed 5 files successfully"). Ensure ResultsDisplay shows correct output path. Test all edge cases from requirements.

---

## Implementation Strategy

**State Management:**
- ApplicationState stores `current_documents: list[Document]` (list replaces single document)
- StateManager methods updated for list operations
- Backward compatibility via `current_document` property returning first item

**Data Flow:**
```
FileSelector.on_files_selected(file_paths: list[str])
    → AppController.on_files_selected()
    → StateManager.set_documents(documents)
    → ThreadCoordinator (background)
        → loop: ParserFactory + ExtractionEngine per document
        → aggregate to BatchExtractionResults
    → OutputGenerator.generate_batch()
    → ResultsDisplay.show_results()
```

**Error Handling:**
- Document validation errors: Skip document, add to warnings
- Parse failures: Skip document, continue with others
- Extraction failures: Include partial results for that document
- Output write failure: Report error, no partial output

**Performance:**
- Sequential processing (memory-safe)
- Progress updates per document
- No additional threading complexity

## Dependencies & Risks

**Internal:**
- Phase 1 depends on Phase 0 (state model changes)
- Phase 2 depends on Phase 0 and Phase 1
- Phase 3 depends on Phase 0 and Phase 2
- Phase 4 depends on all previous phases

**External:** None - all dependencies are existing

**Risks:**
| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Large batch performance | Low | Medium | Progress reporting per file |
| Memory with many files | Low | Medium | Process sequentially, don't hold all in memory |
| Breaking single-file mode | Medium | High | Explicit tests for single-file as batch-of-1 |

**Assumptions:**
- Users typically process < 50 files at once
- Existing parsers handle all file types correctly
- UTF-8 encoding is sufficient for all output

## Acceptance Mapping

| Criterion | Phase | Verification |
|-----------|-------|--------------|
| Select multiple files | Phase 1 | Browse dialog returns multiple paths |
| All documents processed | Phase 2 | Count of processed = count of selected |
| Header row present | Phase 3 | First line contains "Initials; Age; ..." |
| Semicolon delimiters | Phase 3 | Each value followed by "; " |
| Columns aligned | Phase 3 | Visual inspection in text editor |
| First occurrence only | Phase 3 | Compare with multi-occurrence document |
| Auto-generated filename | Phase 3 | Check filename matches pattern |
| Single file produces table | Phase 4 | Select 1 file, get header + 1 row |
| Mixed file types | Phase 4 | Select PDF + DOCX, both processed |
| Missing values handled | Phase 4 | Document with no matches shows empty columns |

## Next Steps

1. Review this plan
2. Generate detailed tasks: `/tasks`
3. Begin Phase 0 implementation

**Unknowns:**
- None - all questions resolved in research phase

---
**Status:** draft
**Target Start:** Upon approval
