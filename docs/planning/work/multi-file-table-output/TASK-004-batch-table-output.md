## TASK-004: Batch Table Output Formatter

---
**Status:** COMPLETE
**Branch:** feature/multi-file-table-output
**Type:** IMPLEMENTATION
**Phase:** 2
**Depends On:** TASK-001, TASK-003
---

### Overview

Create the batch output formatter in OutputGenerator that produces an aligned, semicolon-delimited table with header row. Each document becomes one row with columns: Initials, Age, and each keyword value.

**Files:**
- `src/services/output_generator.py` (modify)

### Implementation Steps

**Commit 1: Implement batch table output generation**
- [x] Create `generate_batch(batch_results: BatchExtractionResults, config: Configuration) -> OutputResult`
- [x] Create `format_batch_output(batch_results: BatchExtractionResults) -> str`
- [x] Build header row: `Initials; Age; Keyword1; Keyword2; ...`
- [x] Build data rows: one per document with first-occurrence values only
- [x] Implement column width calculation across all rows (reuse `_calculate_column_widths`)
- [x] Format with semicolon delimiter and space padding: `value ; value ; value ;`
- [x] Create `generate_batch_filename() -> str` returning `batch_YYYY-MM-DD_HHMMSS.txt`
- [x] Handle missing values: empty string but maintain column width

### Code Example

```python
# Existing column width calculation (reuse this)
# src/services/output_generator.py:40-62

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

# New batch output format:
def format_batch_output(self, batch_results: BatchExtractionResults) -> str:
    """Format batch results as aligned semicolon-delimited table."""
    # Build header: Initials, Age, then keywords
    headers = ["Initials", "Age"] + batch_results.keywords

    # Build data rows
    rows = []
    for result in batch_results.results:
        row = []
        # Initials
        initials = result.personal_info.get_abbreviated_name() or ""
        row.append(initials)
        # Age
        age = str(result.personal_info.age) if result.personal_info.age else ""
        row.append(age)
        # Keyword values (first occurrence only)
        for keyword in batch_results.keywords:
            value = self._get_first_value_for_keyword(result, keyword)
            row.append(value)
        rows.append(row)

    # Calculate widths and format
    widths = self._calculate_column_widths(headers, rows)
    lines = []
    lines.append(self._format_batch_row(headers, widths))
    for row in rows:
        lines.append(self._format_batch_row(row, widths))

    return '\n'.join(lines)

def _format_batch_row(self, cells: list[str], widths: list[int]) -> str:
    """Format row with semicolon delimiters and padding."""
    formatted = []
    for i, cell in enumerate(cells):
        width = widths[i] if i < len(widths) else len(cell)
        formatted.append(f"{cell.ljust(width)}; ")
    return ''.join(formatted).rstrip()

def _get_first_value_for_keyword(self, result: ExtractionResults, keyword: str) -> str:
    """Get first occurrence value for a keyword."""
    for match in result.matches:
        if match.keyword.lower() == keyword.lower() and match.status == 'found':
            return match.value or ""
    return ""
```

### Success Criteria

- [ ] Build succeeds with no errors
- [ ] Output contains header row with correct column names
- [ ] Each document produces exactly one data row
- [ ] Columns are visually aligned with consistent widths
- [ ] Each value followed by `; ` (semicolon + space)
- [ ] Missing values show as empty but maintain column width
- [ ] Filename format: `batch_YYYY-MM-DD_HHMMSS.txt`

### Verification

```bash
cd src && python -c "from services.output_generator import OutputGenerator; print('OK')"
# Manual: Process 3 files, open output, verify table format
```

### Notes

- First occurrence only: iterate matches, return first found value
- Preserve keyword order as specified by user (from batch_results.keywords)
- Empty values: just empty string, semicolon still present
