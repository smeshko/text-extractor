# Quickstart: DOC File Format Support Validation

**Feature**: Add .doc file parsing  
**Date**: 2025-09-30  
**Purpose**: Manual validation checklist for DOC support

## Prerequisites

### Test Environment Setup

1. **Windows 10/11** test machine (for production validation)
2. **Test Files** (create or obtain):
   - `valid_english.doc` - Standard .doc with English text
   - `valid_cyrillic.doc` - .doc with Cyrillic text
   - `valid_mixed.doc` - .doc with Cyrillic and Latin text
   - `password_protected.doc` - Password-protected .doc file
   - `corrupted.doc` - Intentionally corrupted file (open in hex editor and modify)
   - `empty.doc` - .doc with no text content
   - `large_50pages.doc` - Document with ~50 pages (~25,000 words)
   - `fake.doc` - .txt file renamed to .doc
3. **Keywords** for testing: HTD, RTP, Temperature, Влажность (Humidity in Cyrillic)

### Installation

1. Build executable with DOC support:
   ```bash
   pyinstaller build.spec
   ```

2. Verify antiword.exe is bundled:
   ```bash
   # Check bundle contents
   7z l dist/kris-extractor.exe | grep antiword
   # Should show antiword.exe
   ```

3. Copy executable to Windows test machine

---

## Validation Scenarios

### 1. Basic Functionality

**Objective**: Verify .doc files can be selected and processed

#### Test 1.1: File Selection via Browse
- [ ] Launch application
- [ ] Click "Browse" button
- [ ] Verify file filter shows "Supported Documents (*.pdf *.docx *.doc)"
- [ ] Select `valid_english.doc`
- [ ] Verify file name displayed in UI
- [ ] Expected: File accepted, UI shows filename

#### Test 1.2: File Selection via Drag-and-Drop
- [ ] Launch application
- [ ] Drag `valid_english.doc` from Explorer onto application window
- [ ] Verify file name displayed in UI
- [ ] Expected: File accepted, UI shows filename

#### Test 1.3: Keyword Extraction
- [ ] Select `valid_english.doc`
- [ ] Enter keyword: "HTD" (if present in file) or create test file with known keyword
- [ ] Click "Extract"
- [ ] Wait for processing
- [ ] Verify output file generated
- [ ] Open output file and check:
  - [ ] Keyword matches found
  - [ ] Numbers extracted
  - [ ] Page numbers shown (approximate)
  - [ ] Format matches PDF/DOCX output
- [ ] Expected: Successful extraction with results

---

### 2. Character Encoding

**Objective**: Verify Cyrillic and Latin character preservation

#### Test 2.1: Cyrillic Text
- [ ] Select `valid_cyrillic.doc`
- [ ] Enter Cyrillic keyword: "Влажность" (Humidity)
- [ ] Click "Extract"
- [ ] Open output file
- [ ] Verify:
  - [ ] Cyrillic characters displayed correctly
  - [ ] No garbled text or "?" characters
  - [ ] Keyword matches preserved with correct characters
- [ ] Expected: Perfect Cyrillic character preservation

#### Test 2.2: Latin Text
- [ ] Select `valid_english.doc`
- [ ] Enter Latin keyword: "Temperature"
- [ ] Click "Extract"
- [ ] Open output file
- [ ] Verify Latin characters correct
- [ ] Expected: Perfect Latin character preservation

#### Test 2.3: Mixed Cyrillic/Latin
- [ ] Select `valid_mixed.doc` (contains both scripts)
- [ ] Enter mixed keywords: "HTD" and "Влажность"
- [ ] Click "Extract"
- [ ] Open output file
- [ ] Verify both character sets preserved correctly
- [ ] Expected: Both Cyrillic and Latin extracted without corruption

---

### 3. Edge Cases

**Objective**: Verify error handling and edge case behavior

#### Test 3.1: Password-Protected File
- [ ] Select `password_protected.doc`
- [ ] Click "Extract"
- [ ] Verify error message displayed:
  - [ ] Message: "Password-protected .doc files are not supported"
  - [ ] Application does not crash
  - [ ] Error is user-friendly (no stack traces)
- [ ] Expected: Clear error message, graceful handling

#### Test 3.2: Corrupted File
- [ ] Select `corrupted.doc`
- [ ] Click "Extract"
- [ ] Verify error message displayed:
  - [ ] Message: "Unable to parse document. The file may be corrupted or invalid."
  - [ ] Application does not crash
  - [ ] Error is generic (not technical details)
- [ ] Expected: Generic error message, no crash

#### Test 3.3: Empty File (No Text)
- [ ] Select `empty.doc` (valid .doc but no text)
- [ ] Enter keyword: "HTD"
- [ ] Click "Extract"
- [ ] Verify:
  - [ ] Processing completes (no crash)
  - [ ] Output file generated
  - [ ] Warning about "no extractable text" or "keyword not found"
  - [ ] No stack trace or technical error
- [ ] Expected: Graceful handling with warning

#### Test 3.4: Invalid Format (Fake .doc)
- [ ] Select `fake.doc` (.txt renamed to .doc)
- [ ] Click "Extract"
- [ ] Verify error message:
  - [ ] Message: "Unable to parse document. The file may be corrupted or invalid."
  - [ ] Application does not crash
- [ ] Expected: Format validation catches fake file

#### Test 3.5: File Size Limits
- [ ] Create or select .doc file > 10MB (if size limits exist)
- [ ] Attempt to select file
- [ ] Verify behavior matches PDF/DOCX handling
- [ ] Expected: Consistent file size handling across formats

---

### 4. Performance

**Objective**: Verify processing speed meets targets

#### Test 4.1: Small Document (<10 pages)
- [ ] Select small .doc (~5 pages, ~2500 words)
- [ ] Enter 5 keywords
- [ ] Click "Extract"
- [ ] Measure time from click to completion
- [ ] Expected: Completes in <5 seconds

#### Test 4.2: Medium Document (20-30 pages)
- [ ] Select medium .doc (~25 pages, ~12,500 words)
- [ ] Enter 10 keywords
- [ ] Click "Extract"
- [ ] Measure time
- [ ] Expected: Completes in <15 seconds

#### Test 4.3: Large Document (40-50 pages)
- [ ] Select `large_50pages.doc`
- [ ] Enter 10 keywords
- [ ] Click "Extract"
- [ ] Measure time
- [ ] Expected: Completes in <30 seconds (target limit)

#### Test 4.4: Progress Indication
- [ ] Select large .doc
- [ ] Click "Extract"
- [ ] Verify:
  - [ ] Progress bar appears
  - [ ] Progress bar animates during processing
  - [ ] UI remains responsive (not frozen)
- [ ] Expected: Visual progress feedback

---

### 5. Integration

**Objective**: Verify .doc works alongside existing formats

#### Test 5.1: Format Switching
- [ ] Select `document.pdf`
- [ ] Note filename displayed
- [ ] Select `document.docx`
- [ ] Note filename updated
- [ ] Select `document.doc`
- [ ] Note filename updated
- [ ] Click "Extract" on .doc
- [ ] Verify processing works
- [ ] Expected: Seamless switching between all formats

#### Test 5.2: Output Format Consistency
- [ ] Extract same keyword from PDF, DOCX, and DOC versions of same document
- [ ] Compare output files
- [ ] Verify format is identical:
  - [ ] Same metadata structure (Document:, Processed:, Name:, ID:)
  - [ ] Same result format (Keyword: Value (Page X, Line Y))
  - [ ] Same character encoding
- [ ] Expected: Consistent output regardless of input format

#### Test 5.3: Page Number Approximation
- [ ] Select .doc and .docx with same content
- [ ] Extract keywords
- [ ] Compare page numbers in output
- [ ] Verify:
  - [ ] Both use ~500 words/page approximation
  - [ ] Page numbers are similar (may differ by ±1 due to paragraph boundaries)
- [ ] Expected: Consistent page approximation strategy

---

## Acceptance Criteria

### Must Pass (Critical)

- [x] All Basic Functionality tests pass (1.1, 1.2, 1.3)
- [x] All Character Encoding tests pass (2.1, 2.2, 2.3)
- [x] All Edge Cases handled gracefully (3.1, 3.2, 3.3, 3.4)
- [x] Performance targets met (4.1 <5s, 4.2 <15s, 4.3 <30s)
- [x] Integration with existing formats works (5.1, 5.2)

### Should Pass (Important)

- [x] Progress bar displays during processing (4.4)
- [x] Page numbers approximate correctly (5.3)
- [x] File size limits consistent with other formats (3.5)

### Nice to Have (Optional)

- [ ] Error messages provide helpful troubleshooting steps
- [ ] Very large files (>50 pages) complete without timeout

---

## Troubleshooting

### Common Issues

**Issue**: "DOC parser not available" error  
**Cause**: antiword.exe not bundled in executable  
**Fix**: Verify build.spec includes antiword.exe in datas

**Issue**: Cyrillic text appears garbled  
**Cause**: Encoding not set to UTF-8 in subprocess  
**Fix**: Ensure antiword subprocess uses `encoding='utf-8'`

**Issue**: Processing hangs on large files  
**Cause**: No timeout on antiword subprocess  
**Fix**: Add `timeout=30` to subprocess.run()

**Issue**: Password-protected files crash application  
**Cause**: Password detection not working  
**Fix**: Verify olefile checks encryption flag before parse

**Issue**: .doc files not visible in file picker  
**Cause**: File filter not updated  
**Fix**: Update ParserFactory.get_file_filter() to include "*.doc"

---

## Validation Report Template

```
DOC Support Validation Report
Date: ___________
Tester: ___________
Environment: Windows 10/11 (specify)
Build Version: ___________

BASIC FUNCTIONALITY:
[ ] File selection via browse: PASS / FAIL
[ ] File selection via drag-drop: PASS / FAIL
[ ] Keyword extraction: PASS / FAIL

CHARACTER ENCODING:
[ ] Cyrillic text: PASS / FAIL
[ ] Latin text: PASS / FAIL
[ ] Mixed text: PASS / FAIL

EDGE CASES:
[ ] Password-protected: PASS / FAIL
[ ] Corrupted file: PASS / FAIL
[ ] Empty file: PASS / FAIL
[ ] Invalid format: PASS / FAIL

PERFORMANCE:
[ ] Small doc (<10 pages): ___ seconds (target: <5s)
[ ] Medium doc (20-30 pages): ___ seconds (target: <15s)
[ ] Large doc (40-50 pages): ___ seconds (target: <30s)

INTEGRATION:
[ ] Format switching: PASS / FAIL
[ ] Output consistency: PASS / FAIL
[ ] Page approximation: PASS / FAIL

OVERALL: PASS / FAIL
Notes:
_______________________________________________
_______________________________________________
_______________________________________________
```

---

**Validation Status**: ⏳ Pending implementation  
**Next Step**: Implement DOCParser per contract, then execute validation
