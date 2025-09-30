# Quickstart Guide & Manual Validation

**Feature**: Document Data Extraction Tool
**Branch**: 001-use-docs-prd
**Date**: September 30, 2025

## Purpose

This document provides manual validation steps to verify the application meets all functional requirements. Use this for testing after implementation.

---

## Setup

### Prerequisites
1. Windows 10 or 11 (64-bit) for runtime testing
2. OR macOS for development testing
3. Sample documents:
   - PDF with Cyrillic text, keywords (HTD, RTP), and personal info
   - DOCX with Latin text, keywords, and personal info
   - Password-protected PDF (for error testing)
   - Scanned PDF without extractable text (for error testing)

### Installation
1. Copy `DocumentExtractor.exe` to any folder (Windows)
2. OR run from Python environment (macOS development)
3. Double-click to launch (Windows)
4. OR `python src/main.py` (macOS)

### First Run
- Config file (`config.json`) created automatically
- Default output folder: `~/Documents/DocumentExtractor/Output`
- Default log folder: `~/Documents/DocumentExtractor/Logs`

---

## Validation Scenarios

### 1. Basic Extraction Workflow

**Objective**: Verify core extraction functionality with single keyword

**Steps**:
1. Launch application
2. Click "Browse" button
3. Select a valid PDF file containing keyword "HTD" with value "3.5" on page 2
4. Enter "HTD" in keyword input field
5. Click "Add" or press Enter
6. Verify keyword appears in active keywords list
7. Click "Extract Data"
8. Wait for processing to complete
9. Verify success message displayed
10. Click "Open Output File"

**Expected Results**:
- [x] Output file opens in text editor
- [x] File named `output_[original_filename].txt`
- [x] Contains document filename
- [x] Contains processing timestamp
- [x] Contains "HTD: 3.5 (Page 2, Line X)" or "(Page 2)"
- [x] File is plain text, human-readable
- [x] Cyrillic characters display correctly (if applicable)

**Acceptance Criteria**: FR-001, FR-003, FR-007, FR-014, FR-015, FR-016, FR-027, FR-028, FR-033

---

### 2. Multiple Keywords and Occurrences

**Objective**: Verify extraction of multiple keywords with multiple occurrences

**Steps**:
1. Launch application
2. Select PDF with:
   - "HTD" appearing 3 times with values 3.5, 4.2, 7.8 on pages 2, 5, 12
   - "RTP" appearing 1 time with value 125.5 on page 3
   - "BGN" not present in document
3. Add keywords: "HTD", "RTP", "BGN"
4. Click "Extract Data"
5. Open output file

**Expected Results**:
- [x] HTD shows 3 separate entries with correct values and pages
- [x] RTP shows 1 entry with correct value and page
- [x] BGN shows "Not found" status
- [x] All other keywords extracted correctly
- [x] Processing completed without stopping on "BGN not found"

**Acceptance Criteria**: FR-008, FR-014, FR-019, FR-045

---

### 3. Keyword History Persistence

**Objective**: Verify keyword history saves and loads across sessions

**Steps**:
1. Launch application (fresh install)
2. Add keywords "HTD", "RTP", "BGN"
3. Complete extraction
4. Close application
5. Relaunch application
6. Check keyword history dropdown/list

**Expected Results**:
- [x] History shows "HTD", "RTP", "BGN"
- [x] Keywords can be selected from history
- [x] Selected keywords appear in active keywords list
- [x] Can combine historical + new keywords

**Acceptance Criteria**: FR-010, FR-011, FR-012

---

### 4. Drag and Drop File Selection

**Objective**: Verify drag-and-drop functionality

**Steps**:
1. Launch application
2. Open file explorer with valid PDF
3. Drag file to application window
4. Drop file on designated drop zone

**Expected Results**:
- [x] Filename appears in file selection area
- [x] File type detected correctly (PDF/DOCX)
- [x] Keyword section enabled
- [x] Multiple files dropped: Only first accepted (or show warning)

**Acceptance Criteria**: FR-004, FR-005

---

### 5. Personal Information Extraction (Cyrillic)

**Objective**: Verify personal info extraction from Cyrillic document

**Steps**:
1. Select PDF with Cyrillic personal info:
   - "Име: Иван"
   - "Фамилия: Петров"
   - "ЕГН: 1234567890"
2. Add any keyword for extraction
3. Complete extraction
4. Open output file

**Expected Results**:
- [x] First Name: Иван
- [x] Last Name: Петров
- [x] ID: 1234*** (only first 4 digits shown)
- [x] Character set indicated as Cyrillic or mixed
- [x] Cyrillic characters display correctly in output

**Acceptance Criteria**: FR-020, FR-022, FR-025, Constitution Principle III

---

### 6. Personal Information Extraction (Latin)

**Objective**: Verify personal info extraction from Latin document

**Steps**:
1. Select DOCX with Latin personal info:
   - "First Name: John"
   - "Last Name: Smith"
   - "ID Number: 5678901234"
2. Add any keyword for extraction
3. Complete extraction
4. Open output file

**Expected Results**:
- [x] First Name: John
- [x] Last Name: Smith
- [x] ID: 5678***
- [x] Character set indicated as Latin

**Acceptance Criteria**: FR-021, FR-023, FR-025

---

### 7. Mixed Script Handling

**Objective**: Verify handling of documents with both Cyrillic and Latin text

**Steps**:
1. Select document with:
   - Name in both scripts: "Иван Петров (Ivan Petrov)"
   - Keyword in Latin, value nearby
2. Complete extraction

**Expected Results**:
- [x] Both name representations extracted or one preferred
- [x] Character set marked as "mixed"
- [x] All text preserved correctly in output
- [x] No character corruption

**Acceptance Criteria**: FR-024, Constitution Principle III

---

### 8. Password-Protected PDF Error

**Objective**: Verify password-protected PDFs rejected with proper error

**Steps**:
1. Select password-protected PDF
2. Attempt extraction

**Expected Results**:
- [x] Error message: "Password-protected PDFs are not supported"
- [x] Processing does not attempt to continue
- [x] User can select different file

**Acceptance Criteria**: FR-052

---

### 9. Scanned PDF Error

**Objective**: Verify scanned PDFs (requiring OCR) rejected with proper error

**Steps**:
1. Select scanned PDF with no extractable text
2. Attempt extraction

**Expected Results**:
- [x] Error message: "Scanned PDFs requiring OCR are not supported"
- [x] Processing does not attempt to continue
- [x] User can select different file

**Acceptance Criteria**: FR-053

---

### 10. Number Format Handling

**Objective**: Verify US/UK number format parsing

**Steps**:
1. Select document with various number formats:
   - Integer: 42
   - Decimal: 3.5
   - Thousands: 1,234
   - Thousands + decimal: 1,234.56
   - Potentially ambiguous: 3,500 (should be 3500)
2. Add keywords near these numbers
3. Complete extraction

**Expected Results**:
- [x] All numbers extracted correctly
- [x] Period interpreted as decimal separator
- [x] Comma interpreted as thousands separator
- [x] "3,500" interpreted as 3500 (with warning if ambiguous)
- [x] Warnings shown in output for ambiguous cases

**Acceptance Criteria**: FR-016, FR-046

---

### 11. Keyword Not Found Handling

**Objective**: Verify graceful handling when keyword not in document

**Steps**:
1. Select document
2. Add keyword "NOTPRESENT" that doesn't exist in document
3. Add keyword "HTD" that does exist
4. Complete extraction

**Expected Results**:
- [x] Extraction completes successfully
- [x] "NOTPRESENT: Not found" in output
- [x] "HTD" extracted normally
- [x] Processing continued after not finding "NOTPRESENT"
- [x] No error state, partial success indicated

**Acceptance Criteria**: FR-019, FR-045, FR-049, Constitution Principle II

---

### 12. Settings Persistence

**Objective**: Verify settings saved and loaded correctly

**Steps**:
1. Open Settings panel
2. Change output folder to custom path
3. Change log directory to custom path
4. Close application
5. Relaunch application
6. Open Settings panel

**Expected Results**:
- [x] Output folder shows custom path
- [x] Log directory shows custom path
- [x] Window size preserved if changed

**Acceptance Criteria**: FR-043, Configuration persistence

---

### 13. Progress Indication

**Objective**: Verify progress bar and UI responsiveness during processing

**Steps**:
1. Select large document (50 pages)
2. Add 10 keywords
3. Click Extract
4. Observe during processing

**Expected Results**:
- [x] Progress bar appears and animates
- [x] Status message updates ("Processing...", etc.)
- [x] UI remains responsive (can move window, click settings)
- [x] Extract button disabled during processing
- [x] Processing completes in < 30 seconds

**Acceptance Criteria**: FR-042, FR-050, FR-051

---

### 14. Output File Naming and Location

**Objective**: Verify output file naming convention and location

**Steps**:
1. Select file named "report_2024.pdf"
2. Complete extraction
3. Check output folder
4. Complete second extraction on same file

**Expected Results**:
- [x] First output: `output_report_2024.txt`
- [x] Second output: `output_report_2024_YYYYMMDD_HHMMSS.txt` (timestamped)
- [x] Both files in configured output folder
- [x] Original file not modified

**Acceptance Criteria**: FR-035, Output file specification

---

### 15. Processing Log Generation

**Objective**: Verify processing log created for each extraction

**Steps**:
1. Complete extraction
2. Click "Open Log File" (or navigate to log directory)
3. Open log file in text editor

**Expected Results**:
- [x] Log file exists in log directory
- [x] Named `extraction_YYYYMMDD_HHMMSS.log`
- [x] Contains timestamps for all events
- [x] Contains document filename, keywords
- [x] Contains extraction results
- [x] Contains warnings and errors
- [x] Human-readable format

**Acceptance Criteria**: FR-054, FR-055

---

### 16. Case-Insensitive Keyword Matching

**Objective**: Verify keywords match regardless of case

**Steps**:
1. Select document with text "htd: 3.5"
2. Add keyword "HTD" (uppercase)
3. Complete extraction

**Expected Results**:
- [x] Keyword "HTD" matches "htd" in document
- [x] Value 3.5 extracted correctly
- [x] Output shows "HTD: 3.5" (preserves user's case)

**Acceptance Criteria**: FR-009

---

### 17. Keyword Removal

**Objective**: Verify keywords can be removed before extraction

**Steps**:
1. Add keywords "HTD", "RTP", "BGN"
2. Remove "RTP" using X button or delete action
3. Complete extraction

**Expected Results**:
- [x] Only "HTD" and "BGN" processed
- [x] "RTP" not in output
- [x] Active keywords list shows only "HTD" and "BGN"

**Acceptance Criteria**: FR-013

---

### 18. Edge Case: Empty Document

**Objective**: Verify handling of document with no text

**Steps**:
1. Select document with no text (blank pages)
2. Add keyword "HTD"
3. Complete extraction

**Expected Results**:
- [x] Extraction completes without crash
- [x] "HTD: Not found" in output
- [x] Personal info: All fields "Not found"
- [x] Warning or error indicating minimal content

**Acceptance Criteria**: FR-045, FR-047, FR-048

---

### 19. Edge Case: Very Large Keyword List

**Objective**: Verify handling of 20+ keywords

**Steps**:
1. Add 20 different keywords
2. Complete extraction on moderate-size document

**Expected Results**:
- [x] All keywords processed
- [x] Output contains all 20 keywords (found or not found)
- [x] Processing completes in reasonable time
- [x] UI remains responsive

**Acceptance Criteria**: FR-008 (no upper limit), FR-050

---

### 20. Single-Screen UI Verification

**Objective**: Verify all functionality accessible from single screen

**Steps**:
1. Launch application
2. Attempt to complete full workflow without opening additional windows (except file dialogs, output)

**Expected Results**:
- [x] File selection on main screen
- [x] Keyword management on main screen
- [x] Settings panel on main screen (collapsible)
- [x] Extraction control on main screen
- [x] Results display on main screen
- [x] No separate windows required for core workflow

**Acceptance Criteria**: FR-036, Constitution Principle I

---

## Performance Validation

### Typical Document Processing Time

**Test Setup**:
- Document: 15 pages PDF
- Keywords: 5 keywords
- Machine: Standard Windows 10 laptop

**Measurements**:
1. Start timer when "Extract" clicked
2. Stop timer when success message appears
3. Record processing time from output or log

**Acceptance**:
- [x] Processing completes in < 10 seconds (preferred)
- [x] Processing completes in < 30 seconds (required)

---

### Large Document Processing

**Test Setup**:
- Document: 50 pages PDF
- Keywords: 10 keywords

**Measurements**:
- Same as above

**Acceptance**:
- [x] Processing completes in < 30 seconds

---

## Error Recovery Validation

### Output Folder Not Writable

**Steps**:
1. Set output folder to read-only directory
2. Attempt extraction

**Expected**:
- [x] Error message: "Output folder is not writable: [path]"
- [x] Suggestion to select different folder
- [x] Can change settings and retry

---

### Corrupted Config File

**Steps**:
1. Edit config.json to invalid JSON
2. Relaunch application

**Expected**:
- [x] Application launches successfully
- [x] Uses default settings
- [x] Corrupted config backed up to config.json.bak
- [x] Warning logged (if log visible)

---

## Cross-Platform Compatibility

### Windows Runtime

**Steps**:
1. Copy .exe to Windows 10/11 machine without Python
2. Double-click to launch
3. Complete full extraction workflow

**Expected**:
- [x] Application launches without errors
- [x] No missing dependencies
- [x] All functionality works
- [x] Output files created correctly
- [x] Unicode text displays correctly

---

### macOS Development

**Steps**:
1. Run from Python on macOS
2. Complete full extraction workflow

**Expected**:
- [x] Application runs from source
- [x] All functionality works
- [x] Can build executable for testing (optional)

---

## Acceptance Checklist

Before release, verify all scenarios pass:

**Core Functionality**:
- [ ] Scenario 1: Basic extraction
- [ ] Scenario 2: Multiple keywords
- [ ] Scenario 3: Keyword history
- [ ] Scenario 4: Drag and drop
- [ ] Scenario 5: Personal info (Cyrillic)
- [ ] Scenario 6: Personal info (Latin)
- [ ] Scenario 7: Mixed scripts

**Error Handling**:
- [ ] Scenario 8: Password-protected PDF
- [ ] Scenario 9: Scanned PDF
- [ ] Scenario 10: Number formats
- [ ] Scenario 11: Keyword not found
- [ ] Scenario 18: Empty document

**Settings & Persistence**:
- [ ] Scenario 12: Settings persistence
- [ ] Scenario 15: Processing log

**UI & UX**:
- [ ] Scenario 13: Progress indication
- [ ] Scenario 14: Output naming
- [ ] Scenario 16: Case-insensitive matching
- [ ] Scenario 17: Keyword removal
- [ ] Scenario 20: Single-screen UI

**Performance**:
- [ ] Typical document < 10 seconds
- [ ] Large document < 30 seconds
- [ ] UI remains responsive

**Platform**:
- [ ] Windows 10/11 executable works
- [ ] macOS development environment works

**Constitution Compliance**:
- [ ] Single-screen GUI (Principle I)
- [ ] Graceful degradation (Principle II)
- [ ] Unicode support (Principle III)
- [ ] Keyword history persistence (Principle IV)
- [ ] Human-readable output (Principle V)

---

## Known Limitations

Document any known issues or limitations discovered during validation:
1. [To be filled during testing]
2. [To be filled during testing]

---

**Quickstart Complete**: All validation scenarios defined, ready for manual testing after implementation.
