# Document Data Extraction Tool - Product Requirements Document

**Version:** 0.2  
**Status:** DRAFT - Awaiting Additional Information  
**Last Updated:** September 29, 2025  
**Owner:** [Your Name]

---

## 1. Product Overview

### 1.1 Purpose
A desktop application for extracting keyword-associated numerical values and personal information from PDF and DOCX files, with structured plain text output for easy human parsing.

### 1.2 Target Users
- Primary: Document creator (solo use)
- Secondary: One additional user

### 1.3 Platform
- **Development:** macOS
- **Deployment:** Windows 10/11
- **Distribution:** Single executable (.exe) via PyInstaller

---

## 2. Functional Requirements

### 2.1 File Input

#### 2.1.1 Supported File Types
- PDF documents
- Microsoft Word documents (DOCX)

#### 2.1.2 File Selection Methods
**Status:** âœ… CONFIRMED
- File browser dialog via "Browse" button
- Drag-and-drop onto application window
- Single file processing per operation

### 2.2 Keyword Management

#### 2.2.1 Keyword Input
**Status:** âœ… CONFIRMED

**Requirements:**
- Support 5-10 keywords typically
- Must support unlimited keyword count
- Case-insensitive matching
- Manual text input field
- Selectable list from keyword history

#### 2.2.2 Keyword History
**Status:** âœ… CONFIRMED

**Requirements:**
- Persist previously used keywords across sessions
- Display historical keywords in selectable list
- Allow selection of multiple historical keywords
- Allow addition of new keywords alongside historical ones

### 2.3 Data Extraction

#### 2.3.1 Keyword-Number Extraction

**Pattern Recognition:**
- Extract numbers associated with specified keywords
- Support multiple occurrences of same keyword âœ… CONFIRMED
- Extract ALL occurrences, not just first âœ… CONFIRMED

**Number Format:**
- â³ **TBD** - Decimal separator (comma vs. period)
- â³ **TBD** - Thousands separator handling
- â³ **TBD** - Integer vs. decimal support

**Proximity Rules:**
- â³ **TBD** - Distance between keyword and number
- â³ **TBD** - Same line requirement vs. flexible parsing

**Output Per Match:**
âœ… CONFIRMED
- Keyword name
- Extracted numerical value
- Page number where found
- Line number where found (if feasible)

#### 2.3.2 Personal Information Extraction

**Required Fields:**
âœ… CONFIRMED
- First name (Cyrillic and Latin character support)
- Last name (Cyrillic and Latin character support)
- First 4 digits of ID number

**Format and Location:**
- Document structure: Unstructured with minimal consistent format
- Exact extraction pattern: â³ **TBD**
- Location in document: â³ **TBD**
- Multiple document templates: â³ **TBD**

### 2.4 Output

#### 2.4.1 Output Format
**Status:** âœ… CONFIRMED

**Format:** Plain text file

**Structure:** Flat, human-readable format (Option A)

**Example:**
```
    Document: report_2024.pdf
    Processed: 2024-09-29 10:30
    Name: Ð˜Ð²Ð°Ð½ ÐŸÐµÑ‚Ñ€Ð¾Ð² (Ivan Petrov)
    ID: 1234***
    HTD: 3,5 (Page 2, Line 15)
    HTD: 4,2 (Page 5, Line 8)
    RTP: 7,8 (Page 3, Line 22)
```

#### 2.4.2 Output Contents
**Status:** âœ… CONFIRMED

**Per Extraction:**
- Keyword name
- Extracted number value
- Page number
- Line number (if available)

**Document Metadata:**
- Original filename
- Processing date and time

**Personal Information:**
- First name
- Last name
- First 4 digits of ID number

---

## 3. User Interface Requirements

### 3.1 Interface Type
**Status:** âœ… CONFIRMED

Single-screen GUI with simple workflow

### 3.2 UI Components

#### 3.2.1 File Selection Area
**Status:** âœ… CONFIRMED
- "Browse" button for file dialog
- Drag-and-drop zone
- Display of selected filename

#### 3.2.2 Keywords Section
**Status:** âœ… CONFIRMED
- Text input field for manual keyword entry
- Dropdown/list of previously used keywords
- Display of current keywords for extraction
- Ability to remove keywords from current list
- "Add" button to add keyword to current session

#### 3.2.3 Processing Controls
**Status:** âœ… CONFIRMED
- "Extract" button (primary action)
- Progress bar showing extraction progress

#### 3.2.4 Settings
**Status:** âœ… CONFIRMED
- Settings panel/button for configuration options

#### 3.2.5 Results Display
**Status:** âœ… CONFIRMED
- Display area or auto-save with location notification

### 3.3 User Workflow
**Status:** âœ… CONFIRMED

1. User selects file via browse or drag-and-drop
2. User enters keywords manually or selects from history
3. User clicks "Extract"
4. Progress bar indicates processing status
5. Results are saved/displayed
6. User can save output file to desired location

---

## 4. Error Handling

### 4.1 Error Handling Strategy
**Status:** âœ… CONFIRMED

#### 4.1.1 Keyword Not Found
- Mark as "Not found" in output
- Continue processing other keywords
- Do not halt execution

#### 4.1.2 Number Format Ambiguous
- Make best guess at interpretation
- Flag with warning indicator
- Include in output with ambiguity flag

#### 4.1.3 Personal Information Missing
- Continue processing without it
- Mark as "Not found" in output
- Do not halt execution

#### 4.1.4 Multiple Errors
- Process all keywords and data
- Collect all errors
- Report all errors at end of processing
- Do not stop on first error

---

## 5. Technical Requirements

### 5.1 Core Technologies
- **Language:** Python 3.10+
- **GUI Framework:** tkinter (built-in)
- **PDF Parsing:** PyMuPDF (fitz) or pdfplumber
- **DOCX Parsing:** python-docx
- **Text Processing:** Regular expressions (re module)

### 5.2 Character Set Support
- Full Unicode support
- Cyrillic character set (primary)
- Latin character set (secondary)
- Mixed Cyrillic/Latin text handling

### 5.3 Data Persistence
- Keyword history storage (JSON or SQLite)
- User settings/preferences storage
- Session state management

### 5.4 Performance
- Processing time: < 10 seconds per document (acceptable)
- Responsive UI during processing
- Progress indication for long operations

### 5.5 Distribution
- Single executable file (.exe)
- PyInstaller with --onefile flag
- No Python installation required on target machine
- Windows 10/11 compatibility

---

## 6. Out of Scope

### 6.1 Features NOT Included
â³ **TBD - May be added in future versions:**
- Password-protected PDF support
- Scanned PDF support (OCR)
- Image text extraction
- Multi-language support beyond Cyrillic/Latin
- Structured table data parsing
- Handwritten text recognition
- Batch processing of multiple files
- Export to multiple formats (CSV, JSON, Excel)
- Preview of extracted data before saving
- Keyword templates/presets

---

## 7. Open Questions

### 7.1 Critical Questions (Blocking Development)

#### Q4: Number Format Support
**Status:** â³ TBD  
**Question:** What number formats should be supported?

**Examples:**
- `3,5` (comma as decimal)
- `3.5` (period as decimal)
- `3` (integers only)
- `3 500` (space as thousands separator)
- `3,500.50` (US format with comma thousands separator)

**Impact:** Affects core parsing logic

---

#### Q6: Keyword-Number Proximity
**Status:** â³ TBD  
**Question:** How should the tool find numbers associated with keywords?

**Options:**
- Same line only (e.g., `HTD: 3,5`)
- Within same sentence
- Within X characters/words
- Next token after keyword regardless of whitespace

**Examples:**
- `HTD: 3,5`
- `HTD measurement is 3,5`
- `HTD\n3,5`

**Impact:** Defines extraction algorithm complexity

---

#### Q7: Personal Information Format
**Status:** â³ TBD  
**Question:** Exact format and pattern for name and ID extraction

**Needed Information:**
- Typical location in document (header, top, specific section?)
- Are fields labeled? (e.g., "Name:", "Ð˜Ð¼Ðµ:", "ID:", "Ð•Ð“Ð:")
- Name format patterns (First Last, Last First, etc.)
- ID pattern (just 4 digits, or "ID: 1234***"?)
- Spacing and punctuation patterns

**Impact:** Determines personal info extraction algorithm

---

#### Q8: Personal Information Location
**Status:** â³ TBD  
**Question:** More details on document structure for personal info

**Needed Information:**
- Always on first page?
- In specific area (top 25%, header, footer)?
- Any consistent markers/keywords nearby?
- Relationship to other content

**Impact:** Affects extraction reliability and performance

---

#### Q17: Example Documents
**Status:** â³ TBD  
**Request:** Real or anonymized example documents

**Why Needed:**
- Shows actual document structure
- Reveals edge cases and variations
- Clarifies ambiguous requirements
- Enables accurate pattern development
- Allows extraction testing

**Acceptable Formats:**
- Anonymized real documents
- Detailed textual descriptions
- Screenshots of structure
- Sample snippets

**Impact:** Critical for accurate implementation

---

### 7.2 Important Questions (Recommended Before Development)

#### Q9: Document Template Variations
**Status:** â³ TBD  
**Question:** Will different document types require different extraction rules?

**Impact:** Affects architecture (single parser vs. template system)

---

#### Q16: Edge Case Support
**Status:** â³ TBD  
**Question:** Which special cases should be handled?

**Options:**
- Password-protected PDFs
- Scanned PDFs (OCR required)
- Images within documents
- Tables and structured data
- Multiple columns
- Headers and footers

**Impact:** Determines scope and development complexity

---

## 8. Acceptance Criteria

### 8.1 Must Have (Version 1.0)

#### Core Functionality
- [ ] Successfully extracts keywords + numbers from PDF files
- [ ] Successfully extracts keywords + numbers from DOCX files
- [ ] Extracts ALL occurrences of each keyword âœ…
- [ ] Case-insensitive keyword matching âœ…
- [ ] Supports 5-10 keywords minimum, unlimited maximum âœ…

#### Personal Information
- [ ] Extracts first name (Cyrillic + Latin) âœ…
- [ ] Extracts last name (Cyrillic + Latin) âœ…
- [ ] Extracts first 4 digits of ID number âœ…
- [ ] Handles mixed Cyrillic/Latin text âœ…

#### Output
- [ ] Generates plain text output file âœ…
- [ ] Includes page numbers for each match âœ…
- [ ] Includes document metadata (filename, timestamp) âœ…
- [ ] Uses flat, human-readable format âœ…

#### User Interface
- [ ] File selection via browse button âœ…
- [ ] File selection via drag-and-drop âœ…
- [ ] Manual keyword input field âœ…
- [ ] Keyword history selection list âœ…
- [ ] Progress bar during processing âœ…
- [ ] Settings panel âœ…
- [ ] Single-screen interface âœ…

#### Error Handling
- [ ] Continues processing on errors âœ…
- [ ] Reports all errors at end âœ…
- [ ] Flags ambiguous number formats âœ…
- [ ] Marks missing data as "Not found" âœ…

#### Distribution
- [ ] Builds as single .exe file
- [ ] Runs on Windows 10/11 without Python installed
- [ ] File size under 100 MB

### 8.2 Should Have (Version 1.1)
- [ ] Line number extraction for each match
- [ ] Detailed error messages with context
- [ ] Validation warnings before processing
- [ ] Configurable settings persistence
- [ ] Export location preference

### 8.3 Nice to Have (Future Versions)
- [ ] Batch processing of multiple files
- [ ] Export to multiple formats (CSV, JSON)
- [ ] Preview of extracted data before saving
- [ ] Keyword templates/presets
- [ ] Search history with timestamps
- [ ] Undo/redo functionality
- [ ] Dark mode

---

---

## 9. Dependencies

### 9.1 External Dependencies
- Python 3.10+ (development)
- PyMuPDF or pdfplumber library
- python-docx library
- PyInstaller (for distribution)
- Windows 10/11 VM (for testing/building)

### 9.2 Information Dependencies
- Example documents (Q17) - **CRITICAL**
- Number format specification (Q4) - **CRITICAL**
- Personal info patterns (Q7, Q8) - **CRITICAL**
- Keyword proximity rules (Q6) - **HIGH PRIORITY**

---

## Appendix A: Change Log

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 0.1 | 2025-09-29 | Assistant | Initial draft with questions |
| 0.2 | 2025-09-29 | Assistant | Updated with confirmed requirements, formatted as proper PRD |

---

**END OF DOCUMENT**