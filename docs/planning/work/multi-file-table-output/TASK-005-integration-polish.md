## TASK-005: Integration and Edge Cases

---
**Status:** OPEN
**Branch:** feature/multi-file-table-output
**Type:** INTEGRATION
**Phase:** 2
**Depends On:** TASK-002, TASK-003, TASK-004
---

### Overview

Wire all components together, update UI for batch results display, and handle edge cases like missing personal info, mixed file types, and single-file mode.

**Files:**
- `src/ui/main_window.py` (modify)
- `src/ui/results_display.py` (modify)
- `src/controllers/app_controller.py` (modify - final wiring)

### Implementation Steps

**Commit 1: Integrate components and handle edge cases**
- [ ] Update MainWindow to wire FileSelector callback to `on_files_selected`
- [ ] Update ResultsDisplay to show batch success message: "Processed N files successfully"
- [ ] Update `_on_state_changed()` to handle `BatchExtractionResults`
- [ ] Handle edge case: document with no personal info (empty Initials/Age columns)
- [ ] Handle edge case: document with no keyword matches (empty value columns)
- [ ] Handle edge case: mixed file types (PDF + DOCX + DOC in same batch)
- [ ] Handle edge case: single file selection (batch of 1 with header + 1 row)
- [ ] Ensure "Open Output File" button works with batch output path

### Code Example

```python
# Current results display callback
# src/ui/results_display.py - update for batch

def show_results(self, results):
    """Show extraction results."""
    if isinstance(results, BatchExtractionResults):
        # Batch results
        doc_count = results.document_count
        if doc_count == 1:
            self.message_label.configure(text="Extraction complete")
        else:
            self.message_label.configure(text=f"Processed {doc_count} files successfully")
        self._show_success_state()
    else:
        # Single result (backward compatibility)
        self.message_label.configure(text="Extraction complete")
        self._show_success_state()
```

```python
# Handle missing personal info in output
# src/services/output_generator.py

def _build_data_row(self, result: ExtractionResults, keywords: list[str]) -> list[str]:
    """Build data row handling missing values."""
    row = []
    # Initials - empty string if not available
    initials = result.personal_info.get_abbreviated_name() if result.personal_info else ""
    row.append(initials or "")

    # Age - empty string if not available
    age = str(result.personal_info.age) if result.personal_info and result.personal_info.age else ""
    row.append(age)

    # Keywords
    for keyword in keywords:
        value = self._get_first_value_for_keyword(result, keyword)
        row.append(value)

    return row
```

### Success Criteria

- [ ] Build succeeds with no errors
- [ ] End-to-end flow works: select files → extract → view output
- [ ] ResultsDisplay shows appropriate message for batch
- [ ] Single file produces table with header + 1 data row
- [ ] Mixed file types (PDF + DOCX) process correctly
- [ ] Documents with missing personal info have empty columns (not errors)
- [ ] "Open Output File" opens the batch output file
- [ ] "Open Output Folder" still works

### Verification

```bash
cd src && python -m pytest tests/ -v  # If tests exist
cd src && python main.py  # Manual verification
```

**Manual Test Cases:**
1. Select 3 PDF files → verify all processed, output has 4 lines (header + 3 rows)
2. Select 1 file → verify output has 2 lines (header + 1 row)
3. Select PDF + DOCX → verify both processed
4. Select file with no names → verify empty Initials/Age, not error

### Notes

- This task brings everything together - ensure all paths tested
- Backward compatibility important: single file should still work
- Error display: show warnings for failed documents but overall success if any succeeded
