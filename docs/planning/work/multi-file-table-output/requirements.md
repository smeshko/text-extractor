---
type: feature
status: draft
priority: P2
created: 2025-12-04
slug: multi-file-table-output
feature_branch: feature/multi-file-table-output
exploration_cache: .exploration-cache.json
---

# Multi-File Batch Processing with Table Output

## Overview

**Context**: Currently the application processes a single document at a time and generates an individual output file per document. Users who need to process multiple patient files must repeat the workflow for each file and manually consolidate results.

**Objective**: Enable batch processing of multiple documents simultaneously with consolidated output formatted as a semicolon-delimited table suitable for spreadsheet import.

**Impact**: Medical professionals processing multiple patient records can extract data from all files in one operation and receive a ready-to-use table format for further analysis.

## User Stories

**US-1**: As a medical data analyst, I want to select and process multiple patient documents at once so that I can save time on repetitive extraction tasks.
- **Given** multiple patient documents exist, **When** I select them for processing, **Then** all documents are parsed and extracted in a single operation.

**US-2**: As a medical data analyst, I want the extraction results formatted as a table with semicolon delimiters so that I can easily import the data into spreadsheet software.
- **Given** multiple documents have been processed, **When** extraction completes, **Then** a single output file contains all results in tabular format with semicolons separating values.

## Requirements

1. **REQ-001**: The system shall allow selection of multiple documents for batch processing
   - Rationale: Users need to process many files without repeating the workflow

2. **REQ-002**: The system shall process all selected documents using the same keyword list
   - Rationale: Consistent extraction criteria across all documents ensures comparable results

3. **REQ-003**: The system shall generate a single consolidated output file for batch operations
   - Rationale: One file is easier to work with than many individual files

4. **REQ-004**: The output shall be formatted as a semicolon-delimited table with the following column order:
   - Column 1: Patient initials (abbreviated name)
   - Column 2: Patient age
   - Columns 3+: One column per keyword/property in the order they were specified
   - Rationale: Semicolon delimiters work well for CSV import; column order matches logical data grouping

5. **REQ-005**: Each row shall represent one processed document
   - Rationale: One patient per row maintains data integrity

6. **REQ-006**: For each keyword/property, only the first occurrence value shall be used
   - Rationale: Subsequent occurrences may be duplicates or less relevant; first occurrence provides consistent behavior

7. **REQ-007**: Every value (initials, age, each property value) shall be followed by a semicolon
   - Rationale: Consistent delimiter placement enables reliable parsing

8. **REQ-008**: The output shall include a header row with column names
   - Rationale: Headers make the table self-documenting and improve spreadsheet usability

9. **REQ-009**: Values shall be padded with spaces to create consistent column widths for visual alignment
   - Each column width is determined by the longest value in that column (including header)
   - Values are left-padded or right-padded to match the column width
   - Rationale: Aligned columns allow users to visually identify which value belongs to which column at a glance

10. **REQ-010**: The output filename shall be auto-generated using the format `batch_YYYY-MM-DD_HHMMSS.txt`
    - Example: `batch_2025-12-04_143052.txt`
    - Rationale: Unique timestamped names prevent overwrites and require no user input

## Example Output

Given keywords: `HGL`, `WBC`, `RBC`

**Aligned table output (3 patients processed):**
```
Initials; Age; HGL ; WBC; RBC;
ABC     ; 45 ; 14.2; 7.5; 4.8;
DEF     ; 32 ; 12.8; 6.2; 4.5;
GHI     ; 67 ; 11.5; 8.1; 5.2;
```

**With a missing value (HGL not found for second patient):**
```
Initials; Age; HGL ; WBC; RBC;
ABC     ; 45 ; 14.2; 7.5; 4.8;
DEF     ; 32 ;     ; 6.2; 4.5;
GHI     ; 67 ; 11.5; 8.1; 5.2;
```

**Notes:**
- Each value is followed by a semicolon (including the last value in each row)
- Values are padded with spaces so columns align vertically
- Missing values leave the space empty but maintain column width
- Initials are uppercase abbreviations (e.g., "John Adam Smith" → "JAS")
- Output filename: `batch_2025-12-04_143052.txt` (auto-generated)

## Acceptance Criteria

### Functional
- [ ] **Given** I am on the main screen, **When** I use the file selector, **Then** I can select multiple files (not just one)
- [ ] **Given** I have selected 3 documents and 3 keywords, **When** I click Extract, **Then** all 3 documents are processed
- [ ] **Given** batch processing completes, **When** I view the output file, **Then** it contains a header row plus one data row per document
- [ ] **Given** the output file, **When** I examine any row, **Then** values are separated by semicolons including after the last value
- [ ] **Given** a keyword appears multiple times in a document, **When** extraction runs, **Then** only the first occurrence's value is used
- [ ] **Given** the output file, **When** I view it in a text editor, **Then** all columns are visually aligned with consistent spacing
- [ ] **Given** batch processing completes, **When** I check the output folder, **Then** the file is named with format `batch_YYYY-MM-DD_HHMMSS.txt`

### Edge Cases
- [ ] Handles documents where some keywords are not found (empty values in those columns)
- [ ] Handles documents where patient name/age cannot be extracted (empty initials/age columns)
- [ ] Handles mixed file types in batch (PDF, DOCX, DOC)
- [ ] Handles case where user selects only one file (produces table with header + 1 data row)

## Affected Areas

**Components**:
- FileSelector - Must support multi-file selection
- AppController - Must orchestrate batch processing loop
- OutputGenerator - Must produce table format instead of individual reports
- ExtractionResults - May need batch aggregation model

**Files**:
- `src/ui/file_selector.py` - Multi-selection UI
- `src/controllers/app_controller.py` - Batch processing logic
- `src/services/output_generator.py` - Table output formatting
- `src/models/extraction_results.py` - Batch results container

## Assumptions
- Existing keyword extraction logic (first-occurrence behavior for values) is already correct
- Header column names use the exact keyword text as entered by the user
- Output file uses UTF-8 encoding (matching current behavior)
- The order of rows in output matches the order files were selected/processed

## Open Questions

None - all questions resolved.

---
**Next Steps**: Proceed to planning with `/plan`.
