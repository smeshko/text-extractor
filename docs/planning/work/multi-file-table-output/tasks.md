# Execution Tasks: Multi-File Batch Processing with Table Output

**Branch:** `feature/multi-file-table-output` → `staging` → `main`
**Complexity:** Medium
**Duration:** 10-15 hours
**Created:** 2025-12-04

---

## Overview

Enable batch processing of multiple patient documents with consolidated output formatted as an aligned, semicolon-delimited table suitable for spreadsheet import.

**Deliverables:**
- Multi-file selection UI (browse + drag-and-drop)
- Batch processing of all selected documents
- Aligned table output with semicolon delimiters
- Auto-generated batch output filename

---

## Quick Reference

- **Phases:** 2 | **Tasks:** 5 | **Commits:** 5
- **Parallel:** T001 (independent) | **Critical Path:** T001 → T002 → T003 → T004 → T005

---

## Phase 1: Core Implementation

**Goal:** Create data models and enable multi-file selection with batch processing
**PR:** `feat: Add multi-file batch processing support`
**Deliverable:** Users can select multiple files and process them in a batch

---

### Task T001: Batch Extraction Results Model ✅
**Source:** `TASK-001-batch-results-model.md`
**Type:** IMPLEMENTATION
**Files:** `src/models/batch_extraction_results.py` (create), `src/models/application_state.py`

**Implementation Steps:**
- [x] Create `BatchExtractionResults` dataclass
- [x] Add fields: results list, keywords, timestamp, output_path
- [x] Add helper methods: `add_result()`, `document_count`
- [x] Update `ApplicationState` to store list of documents

**Checkpoint:** ✓ Build | ✓ Import succeeds

---

### Task T002: Multi-File Selection UI ✅
**Source:** `TASK-002-multi-file-selection-ui.md`
**Type:** IMPLEMENTATION
**Files:** `src/ui/file_selector.py`
**Depends On:** T001

**Implementation Steps:**
- [x] Change `askopenfilename()` to `askopenfilenames()`
- [x] Update internal state to store list of files
- [x] Update display: "N files selected" for multiple
- [x] Update drag-and-drop to accept all files
- [x] Update callback to pass list of paths

**Checkpoint:** ✓ Build | ✓ Multi-select works

---

### Task T003: Batch Processing Controller Logic ✅
**Source:** `TASK-003-batch-processing-controller.md`
**Type:** IMPLEMENTATION
**Files:** `src/controllers/app_controller.py`, `src/controllers/state_manager.py`
**Depends On:** T001, T002

**Implementation Steps:**
- [x] Create `on_files_selected()` handler
- [x] Create `_perform_batch_extraction()` method
- [x] Loop through documents, aggregate results
- [x] Update progress: "Processing file N of M"
- [x] Handle per-document errors without stopping batch

**Checkpoint:** ✓ Build | ✓ Multiple files processed

---

**Phase 1 Completion:**
- [x] All tasks complete (T001, T002, T003)
- [x] Build succeeds
- [x] Multiple files can be selected and processed
- [x] Ready for Phase 2

---

## Phase 2: Output & Integration

**Goal:** Implement table output format and integrate all components
**PR:** `feat: Add aligned table output for batch processing`
**Deliverable:** Complete end-to-end batch processing with formatted output

---

### Task T004: Batch Table Output Formatter ✅
**Source:** `TASK-004-batch-table-output.md`
**Type:** IMPLEMENTATION
**Files:** `src/services/output_generator.py`
**Depends On:** T001, T003

**Implementation Steps:**
- [x] Create `generate_batch()` method
- [x] Create `format_batch_output()` for table format
- [x] Build header row: Initials; Age; Keywords...
- [x] Build data rows with first-occurrence values
- [x] Format with semicolon delimiter + padding
- [x] Create `generate_batch_filename()` for timestamped name

**Checkpoint:** ✓ Build | ✓ Output file formatted correctly

---

### Task T005: Integration and Edge Cases ✅
**Source:** `TASK-005-integration-polish.md`
**Type:** INTEGRATION
**Files:** `src/ui/main_window.py`, `src/ui/results_display.py`, `src/controllers/app_controller.py`
**Depends On:** T002, T003, T004

**Implementation Steps:**
- [x] Wire FileSelector callback to controller
- [x] Update ResultsDisplay for batch messages
- [x] Handle missing personal info (empty columns)
- [x] Handle mixed file types
- [x] Handle single file (batch of 1)
- [x] Verify "Open Output File" works

**Checkpoint:** ✓ Build | ✓ End-to-end flow works

---

**Phase 2 Completion:**
- [x] All tasks complete (T004, T005)
- [x] Build succeeds
- [x] End-to-end flow works
- [x] Output format matches requirements
- [ ] Create PR: `feature/multi-file-table-output` → `staging`

---

## Execution

**Commit Format:**
```
feat(scope): description

- Change 1
- Change 2

Task: T00X | Phase: N
```

**Build:** `cd src && python -c "import main; print('OK')"`
**Test:** `cd src && python -m pytest tests/ -v` (if tests exist)

---

## Task Reference

| ID | Phase | Type | Files | Depends On | Status |
|----|-------|------|-------|------------|--------|
| T001 | 1 | IMPL | batch_extraction_results.py, application_state.py | - | ✅ DONE |
| T002 | 1 | IMPL | file_selector.py | T001 | ✅ DONE |
| T003 | 1 | IMPL | app_controller.py, state_manager.py | T001, T002 | ✅ DONE |
| T004 | 2 | IMPL | output_generator.py | T001, T003 | ✅ DONE |
| T005 | 2 | INTEG | main_window.py, results_display.py, app_controller.py | T002-T004 | ✅ DONE |

---

## Timeline Estimate

| Phase | Tasks | Effort | Cumulative |
|-------|-------|--------|------------|
| Phase 1 | T001-T003 | 5-7 hrs | 5-7 hrs |
| Phase 2 | T004-T005 | 5-7 hrs | 10-14 hrs |

---

## Notes

- **Single file mode:** Treated as batch of 1 - same output format
- **Error handling:** Per-document errors don't stop batch; add warnings
- **Memory:** Process documents sequentially to avoid holding all in memory
- **Output format:** `Initials; Age; Keyword1; Keyword2;` with aligned columns
