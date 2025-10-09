# Quickstart Guide: Output Format and UI Enhancements

**Feature**: Output Format and UI Enhancements
**Branch**: 007-i-want-the
**Date**: 2025-10-09
**Target Users**: Developers and manual testers

## Overview

This quickstart guide provides manual validation steps for the output format and UI enhancements feature. It covers table-like formatting, abbreviated name-based filenames, semicolon suffixes, and window configuration changes.

## Prerequisites

- Development environment set up with Python 3.10+
- Repository cloned and dependencies installed
- Test documents available (PDF/DOCX with personal information and numeric data)
- Access to output folder for file verification

## Test Documents Required

### Document 1: Complete Personal Info (Cyrillic)
- **Content**: Document containing full name "Иван Йорданов Тодоров, 33" and numeric keyword values
- **Purpose**: Test table formatting with complete data
- **Expected Output**: Filename "ИЙТ-33.txt" with table-formatted content

### Document 2: Two-Part Name (Latin)
- **Content**: Document containing name "John Doe, 25" and numeric values
- **Purpose**: Test Latin character handling
- **Expected Output**: Filename "JD-25.txt"

### Document 3: Missing Age
- **Content**: Document with name but no age
- **Purpose**: Test fallback filename generation
- **Expected Output**: Timestamp-based filename "output_YYYYMMDD_HHMMSS.txt"

### Document 4: Long Keywords
- **Content**: Document with very long keyword names (50+ characters)
- **Purpose**: Test column width expansion without truncation
- **Expected Output**: Wide columns, no truncation

## Manual Validation Checklist

### Part 1: Table-Like Formatting for Personal Information

**Acceptance Criteria** (from FR-003, FR-005):
- Personal information displays in table format
- First row contains Cyrillic headers "ИМЕ" and "ГОДИНИ"
- Second row contains abbreviated name (uppercase) and age
- Columns are aligned with whitespace padding

**Test Steps**:
1. [ ] Open application and select Document 1 (Cyrillic, complete info)
2. [ ] Add keywords: "HTD", "MCV", "RBC"
3. [ ] Click Extract button
4. [ ] Open output file: "ИЙТ-33.txt"
5. [ ] Verify Personal Information section format:
   ```
   --- Personal Information ---
   ИМЕ     ГОДИНИ
   ИЙТ     33
   ```
6. [ ] Verify column headers are "ИМЕ" and "ГОДИНИ" (exact Cyrillic text)
7. [ ] Verify abbreviated name "ИЙТ" is uppercase
8. [ ] Verify age "33" appears in ГОДИНИ column
9. [ ] Verify columns are left-aligned with whitespace separation

**Expected Result**: ✅ Personal information displays in table format with Cyrillic headers

**If Failed**: Check PersonalInformation.get_abbreviated_name() and OutputGenerator.format_output()

---

### Part 2: Table-Like Formatting for Keyword Extractions

**Acceptance Criteria** (from FR-001):
- Keyword extraction output in table structure
- Keyword names appear as column headers
- Extracted values appear directly underneath
- Columns flow horizontally

**Test Steps**:
1. [ ] Using same Document 1 output file
2. [ ] Verify Keyword Extractions section format:
   ```
   --- Keyword Extractions ---
   HTD      MCV      RBC
   3,5;     85,3;    4,12;
   ```
3. [ ] Verify keyword names appear in first row as headers
4. [ ] Verify extracted values appear in second row
5. [ ] Verify columns are aligned (values directly under headers)
6. [ ] Verify whitespace padding between columns (minimum 4 spaces)

**Expected Result**: ✅ Keyword extractions display in table format

**If Failed**: Check OutputGenerator._format_table_row() and _calculate_column_widths()

---

### Part 3: Semicolon Suffix for Numeric Values

**Acceptance Criteria** (from FR-002):
- Semicolon (;) appears immediately after every numeric value
- Non-numeric values have no semicolon
- "Not found" and "Ambiguous" statuses handled correctly

**Test Steps**:
1. [ ] Verify all numeric values in output file have semicolon suffix:
   - "3,5;" ✅
   - "85,3;" ✅
   - "4,12;" ✅
2. [ ] Create Document with missing keyword value
3. [ ] Extract and verify "Not found" has no semicolon
4. [ ] Create Document with ambiguous value (multiple matches)
5. [ ] Extract and verify ambiguous numeric value has semicolon + "[Ambiguous]" marker

**Expected Result**: ✅ All numeric values have semicolon suffix

**If Failed**: Check OutputGenerator.format_output() semicolon appending logic

---

### Part 4: Abbreviated Name-Based Filename

**Acceptance Criteria** (from FR-008):
- Filename format: "{ABBREV}-{AGE}.txt"
- Abbreviated name consists of uppercase first letters
- Cyrillic characters preserved

**Test Steps**:

#### Test 4A: Three-Part Cyrillic Name
1. [ ] Extract Document 1 (Иван Йорданов Тодоров, 33)
2. [ ] Verify output filename is exactly "ИЙТ-33.txt"
3. [ ] Verify abbreviated name "ИЙТ" uses first letters: И (Иван) + Й (Йорданов) + Т (Тодоров)
4. [ ] Verify age "33" matches document content

#### Test 4B: Two-Part Latin Name
1. [ ] Extract Document 2 (John Doe, 25)
2. [ ] Verify output filename is exactly "JD-25.txt"
3. [ ] Verify abbreviated name "JD" uses first letters: J (John) + D (Doe)

#### Test 4C: Single-Part Name
1. [ ] Create document with name "Иван, 40"
2. [ ] Extract and verify filename is "И-40.txt"

#### Test 4D: Missing Age (Fallback)
1. [ ] Extract Document 3 (name without age)
2. [ ] Verify filename uses timestamp format: "output_YYYYMMDD_HHMMSS.txt"
3. [ ] Verify timestamp is current (within last minute)

#### Test 4E: Missing Name (Fallback)
1. [ ] Create document without personal information
2. [ ] Extract and verify filename uses timestamp format

**Expected Result**: ✅ Filenames follow abbreviated name-based format with proper fallback

**If Failed**: Check PersonalInformation.get_abbreviated_name() and OutputGenerator.generate_filename()

---

### Part 5: Filename Collision Handling (Removed)

**Acceptance Criteria** (from FR-009):
- No collision handling - files overwrite if same name
- No timestamp suffix on collision

**Test Steps**:
1. [ ] Extract Document 1 (ИЙТ-33.txt created)
2. [ ] Note output file modification timestamp
3. [ ] Extract Document 1 again immediately
4. [ ] Verify output file is still named "ИЙТ-33.txt" (no timestamp suffix)
5. [ ] Verify file modification timestamp updated (file was overwritten)
6. [ ] Verify content matches second extraction (not first)

**Expected Result**: ✅ Files overwrite on collision without timestamp suffix

**If Failed**: Check OutputGenerator.generate() - ensure collision handling code removed

---

### Part 6: Window Initial Size and Resizability

**Acceptance Criteria** (from FR-011, FR-012):
- Initial window size is 1080x900 (10% smaller than 1200x1000)
- Window is resizable (draggable edges/corners)
- UI components remain accessible

**Test Steps**:

#### Test 6A: Initial Size
1. [ ] Close application completely
2. [ ] Delete config.json (or rename) to reset configuration
3. [ ] Launch application
4. [ ] Measure window dimensions using OS tools or visual inspection
5. [ ] Verify window width is approximately 1080 pixels
6. [ ] Verify window height is approximately 900 pixels
7. [ ] Verify all UI components are visible and accessible

#### Test 6B: Horizontal Resize
1. [ ] Hover over left edge of window until resize cursor appears
2. [ ] Drag left edge to expand window width to ~1400 pixels
3. [ ] Verify window resizes smoothly
4. [ ] Hover over right edge and drag to shrink width to ~800 pixels
5. [ ] Verify window resizes below 1080 (no minimum enforced)

#### Test 6C: Vertical Resize
1. [ ] Hover over top edge of window until resize cursor appears
2. [ ] Drag top edge to expand window height to ~1200 pixels
3. [ ] Verify window resizes smoothly
4. [ ] Hover over bottom edge and drag to shrink height to ~600 pixels
5. [ ] Verify window resizes below 900 (no minimum enforced)

#### Test 6D: Corner Resize
1. [ ] Hover over bottom-right corner until diagonal resize cursor appears
2. [ ] Drag corner to resize both dimensions simultaneously
3. [ ] Verify window resizes in both directions

#### Test 6E: Very Small Window (Edge Case)
1. [ ] Resize window to very small dimensions (e.g., 500x400)
2. [ ] Verify application does not crash
3. [ ] Verify UI components may overlap but remain functional
4. [ ] Verify scrolling or other degradation is graceful

#### Test 6F: Size Persistence
1. [ ] Resize window to custom size (e.g., 1300x1100)
2. [ ] Close application normally
3. [ ] Verify config.json contains updated dimensions:
   ```json
   {
     "window_width": 1300,
     "window_height": 1100,
     ...
   }
   ```
4. [ ] Relaunch application
5. [ ] Verify window opens at 1300x1100 (saved size)

**Expected Result**: ✅ Window is 1080x900 initially, fully resizable, and persists size

**If Failed**: Check MainWindow.__init__() geometry and minsize configuration

---

### Part 7: Long Keyword Names (Edge Case)

**Acceptance Criteria** (from FR-007):
- Long keyword names extend column width
- No truncation of keyword names or values
- Fixed-width columns without separators

**Test Steps**:
1. [ ] Extract Document 4 with long keyword name (e.g., "VeryLongKeywordNameThatExceedsFiftyCharacters")
2. [ ] Open output file
3. [ ] Verify keyword name is fully displayed (no truncation)
4. [ ] Verify column width expands to accommodate full keyword
5. [ ] Verify value column aligns under expanded header
6. [ ] Verify output format:
   ```
   --- Keyword Extractions ---
   VeryLongKeywordNameThatExceedsFiftyCharacters    ShortKeyword
   1234;                                            56;
   ```

**Expected Result**: ✅ Long keywords expand columns without truncation

**If Failed**: Check OutputGenerator._calculate_column_widths() logic

---

### Part 8: Character Encoding (Cyrillic Preservation)

**Acceptance Criteria** (from FR-004, FR-010):
- Cyrillic characters preserved in abbreviated names
- Cyrillic characters preserved in filenames
- UTF-8 encoding maintained

**Test Steps**:
1. [ ] Extract Document 1 (Cyrillic name)
2. [ ] Verify filename "ИЙТ-33.txt" displays correctly in file system
3. [ ] Open file in text editor
4. [ ] Verify "ИМЕ" and "ГОДИНИ" headers display correctly (not corrupted)
5. [ ] Verify "ИЙТ" abbreviated name displays correctly
6. [ ] Verify file encoding is UTF-8 (check editor encoding setting)
7. [ ] Copy filename to clipboard and verify Cyrillic characters paste correctly

**Expected Result**: ✅ Cyrillic characters preserved throughout pipeline

**If Failed**: Check file writing encoding in OutputGenerator.generate() and PersonalInformation methods

---

### Part 9: Integration Test (Complete Workflow)

**Acceptance Criteria**: All features work together end-to-end

**Test Steps**:
1. [ ] Launch application (first launch, 1080x900)
2. [ ] Resize window to 1200x950
3. [ ] Select Document 1 (Cyrillic, complete personal info)
4. [ ] Add keywords: "HTD", "MCV", "RBC", "Hemoglobin"
5. [ ] Click Extract
6. [ ] Verify output file created: "ИЙТ-33.txt"
7. [ ] Open file and verify complete format:
   ```
   Document: document1.pdf
   Processed: 2025-10-09 14:30:22

   --- Personal Information ---
   ИМЕ     ГОДИНИ
   ИЙТ     33

   --- Keyword Extractions ---
   HTD      MCV      RBC      Hemoglobin
   3,5;     85,3;    4,12;    140;

   --- Processing Summary ---
   Total keywords: 4 (HTD, Hemoglobin, MCV, RBC)
   Successful extractions: 4
   Not found: 0
   Processing time: 1.23 seconds

   --- Warnings ---
   None

   --- Errors ---
   None
   ```
8. [ ] Verify all aspects:
   - Table format for personal info ✅
   - Table format for keyword extractions ✅
   - Semicolons after all numeric values ✅
   - Abbreviated filename "ИЙТ-33.txt" ✅
   - Cyrillic characters preserved ✅
9. [ ] Close application
10. [ ] Verify config.json has window_width=1200, window_height=950
11. [ ] Relaunch and verify window opens at saved size

**Expected Result**: ✅ All features integrated successfully

---

## Edge Cases Validation

### Edge Case 1: Empty Personal Information
- **Test**: Document with no personal info
- **Expected**: Timestamp filename, "Not found" messages in output (legacy format, not table)

### Edge Case 2: Multiple Spaces in Names
- **Test**: Name "Иван  Петров" (double space)
- **Expected**: Abbreviated name "ИП" (extra space filtered)

### Edge Case 3: Very Long Value
- **Test**: Keyword value with 100+ characters
- **Expected**: Column expands, no truncation, alignment maintained

### Edge Case 4: Mixed Cyrillic/Latin Name
- **Test**: Name "John Иванов Петров, 30"
- **Expected**: Filename "JИП-30.txt", mixed script preserved

---

## Performance Validation

**Test Steps**:
1. [ ] Extract document with 50+ keywords
2. [ ] Verify extraction completes in <5 seconds
3. [ ] Verify output file generation completes in <1 second
4. [ ] Verify table formatting performance is acceptable

**Expected**: No performance degradation from new formatting logic

---

## Rollback Criteria

If any of the following occur, rollback implementation:

- [ ] **Critical**: Cyrillic characters corrupted in output files
- [ ] **Critical**: Application crashes on resize
- [ ] **Critical**: Output file generation fails for valid documents
- [ ] **High**: Window becomes unusable at default size (1080x900)
- [ ] **High**: Filename generation fails for common name patterns

---

## Success Criteria

**Feature is complete when all checkboxes above are checked (✅) with:**
- All table formatting tests pass
- All filename generation tests pass
- All window resizing tests pass
- All edge cases handled gracefully
- No critical or high severity issues

---

## Troubleshooting

### Issue: Table columns misaligned
- **Check**: _calculate_column_widths() logic
- **Verify**: str.ljust() padding calculation

### Issue: Semicolons missing from numeric values
- **Check**: format_output() value formatting logic
- **Verify**: Numeric value detection (is value a number?)

### Issue: Abbreviated name has lowercase letters
- **Check**: get_abbreviated_name() .upper() call
- **Verify**: Cyrillic uppercase conversion works

### Issue: Filename uses timestamp instead of name
- **Check**: PersonalInformation.full_name and .age values
- **Verify**: PersonalInfoExtractor successfully extracted data

### Issue: Window doesn't resize
- **Check**: MainWindow.__init__() for minsize() calls
- **Verify**: minsize() removed or set to very small values

### Issue: Window size not persisted
- **Check**: _on_closing() handler
- **Verify**: config.window_width/height updated
- **Verify**: ConfigurationManager.save() called

---

## Manual Testing Checklist Summary

Total Validation Steps: 75+ checkboxes

**By Category**:
- Personal Info Table: 9 checks
- Keyword Extractions Table: 6 checks
- Semicolon Suffixes: 5 checks
- Filename Generation: 12 checks
- Window Configuration: 17 checks
- Long Keywords: 6 checks
- Character Encoding: 7 checks
- Integration Test: 11 checks
- Edge Cases: 4+ checks

**Estimated Testing Time**: 2-3 hours for complete manual validation

**Sign-Off Required**: Developer + QA tester validation
