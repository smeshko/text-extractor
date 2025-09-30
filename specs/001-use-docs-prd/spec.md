# Feature Specification: Document Data Extraction Tool

**Feature Branch**: `001-use-docs-prd`
**Created**: September 30, 2025
**Status**: Draft
**Input**: User description: "use @docs/prd.md for context"

## Execution Flow (main)
```
1. Parse user description from Input
   → COMPLETED: PRD document analyzed
2. Extract key concepts from description
   → Identified: document processing, keyword extraction, personal info extraction, GUI workflow
3. For each unclear aspect:
   → Marked with [NEEDS CLARIFICATION] throughout spec
4. Fill User Scenarios & Testing section
   → COMPLETED: Primary workflow and edge cases defined
5. Generate Functional Requirements
   → COMPLETED: 28 functional requirements derived from PRD
6. Identify Key Entities
   → COMPLETED: 6 key entities identified
7. Run Review Checklist
   → WARN: Spec has uncertainties - see [NEEDS CLARIFICATION] markers
8. Return: SUCCESS (spec ready for planning after clarifications)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## Clarifications

### Session 2025-09-30
- Q: Number Format Specification - Which number format convention should the system support? → A: US/UK format (period as decimal separator)
- Q: Keyword-Number Proximity Rules - How should the system determine which number is associated with a keyword? → A: Next numeric value (first number after keyword, regardless of distance)
- Q: Personal Information Field Labeling - How are personal information fields typically presented in documents? → A: Labeled fields with consistent labels
- Q: Password-Protected and OCR Document Scope - Should the system support password-protected PDFs and scanned PDFs requiring OCR? → A: Neither (out of scope; reject with error messages)
- Q: Observability & Error Reporting - What level of operational visibility should the system provide? → A: Standard (write processing log file with timestamps, warnings, and errors)

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
A document processor needs to quickly extract specific numerical values (associated with keywords like "HTD", "RTP") and personal identification information (names in Cyrillic/Latin scripts, ID numbers) from PDF and Word documents. The user wants to input keywords once, process a document, and receive a simple text file containing all found values with their page locations, allowing easy human review without manually searching through documents.

### Acceptance Scenarios

1. **Given** a user has a PDF document with keyword "HTD" appearing 3 times with values 3.5, 4.2, and 7.8 on different pages, **When** user selects the file, enters "HTD" as keyword, and clicks Extract, **Then** output file shows all three HTD values with their respective page numbers

2. **Given** a user has previously searched for keywords "HTD", "RTP", and "BGN", **When** user opens the application, **Then** the keyword history list displays these three keywords for quick selection

3. **Given** a user drags a DOCX file onto the application window, **When** the file is dropped, **Then** the filename appears in the selected file display area ready for processing

4. **Given** a document contains a person's name "Иван Петров" (Cyrillic) and ID number starting with "1234", **When** extraction runs, **Then** output includes both name and ID first 4 digits

5. **Given** a document does not contain the keyword "XYZ" that the user searched for, **When** extraction completes, **Then** output file marks "XYZ" as "Not found" and continues processing other keywords

6. **Given** a user has selected 8 keywords and a large document, **When** extraction is running, **Then** a progress bar shows current processing status until completion

### Edge Cases
- What happens when a keyword appears in a document but no number follows it anywhere in the document? System marks that keyword occurrence as "Not found"
- What happens when a number format is ambiguous (e.g., "3,500")? System interprets using US/UK convention (3,500 = three thousand five hundred)
- What happens when personal information fields are partially present (only first name, missing ID)? System marks missing fields as "Not found" and continues
- What happens when a document has mixed Cyrillic and Latin text for the same person's name? System should extract both representations
- What happens when the same keyword appears multiple times on the same page? System extracts all occurrences with the same page number
- What happens when user selects a password-protected PDF? System detects protection and displays error message: "Password-protected PDFs are not supported"
- What happens when user selects a scanned PDF requiring OCR? System detects absence of extractable text and displays error message: "Scanned PDFs requiring OCR are not supported"
- What happens when keywords are entered with different casing (e.g., "HTD" vs "htd")? System performs case-insensitive matching

---

## Requirements *(mandatory)*

### Functional Requirements

#### File Input & Selection
- **FR-001**: System MUST accept PDF documents as input
- **FR-002**: System MUST accept Microsoft Word DOCX documents as input
- **FR-003**: Users MUST be able to select a file via a "Browse" button that opens a file selection dialog
- **FR-004**: Users MUST be able to drag and drop a single file onto the application window for selection
- **FR-005**: System MUST display the selected filename to confirm file selection
- **FR-006**: System MUST process only one file at a time per extraction operation

#### Keyword Management
- **FR-007**: Users MUST be able to manually enter keywords via a text input field
- **FR-008**: System MUST support a minimum of 10 keywords simultaneously and have no upper limit on keyword count
- **FR-009**: System MUST perform case-insensitive keyword matching (e.g., "HTD" matches "htd", "Htd")
- **FR-010**: System MUST persist keyword history across application sessions
- **FR-011**: Users MUST be able to select previously used keywords from a displayed history list
- **FR-012**: Users MUST be able to combine historical keywords with newly entered keywords in the same extraction operation
- **FR-013**: Users MUST be able to remove keywords from the current extraction list before processing

#### Data Extraction - Keywords and Numbers
- **FR-014**: System MUST extract ALL occurrences of each specified keyword within a document, not just the first occurrence
- **FR-015**: System MUST extract the first numerical value that appears after each found keyword in the document text flow, regardless of distance
- **FR-016**: System MUST support US/UK number format convention with period as decimal separator (e.g., "3.5", "1,234.56") and comma as thousands separator; integers and decimals both supported
- **FR-017**: For each keyword-number match, system MUST record the page number where found
- **FR-018**: For each keyword-number match, system SHOULD record the line number where found (if technically feasible)
- **FR-019**: When a keyword is found but no associated number can be extracted, system MUST mark that keyword as "Not found" in the output

#### Data Extraction - Personal Information
- **FR-020**: System MUST extract first names from labeled fields (e.g., "First Name:", "Име:", "Name:") containing Cyrillic characters
- **FR-021**: System MUST extract first names from labeled fields containing Latin characters
- **FR-022**: System MUST extract last names from labeled fields (e.g., "Last Name:", "Фамилия:", "Surname:") containing Cyrillic characters
- **FR-023**: System MUST extract last names from labeled fields containing Latin characters
- **FR-024**: System MUST handle mixed Cyrillic and Latin text in the same name field
- **FR-025**: System MUST extract the first 4 digits of identification numbers from labeled fields (e.g., "ID:", "ЕГН:", "ID Number:") using pattern matching on common label variations in Cyrillic and Latin
- **FR-026**: When personal information fields are missing, system MUST mark them as "Not found" and continue processing

#### Output Generation
- **FR-027**: System MUST generate output as a plain text file in flat, human-readable format
- **FR-028**: Output MUST include original document filename
- **FR-029**: Output MUST include processing date and timestamp
- **FR-030**: Output MUST include extracted first name
- **FR-031**: Output MUST include extracted last name
- **FR-032**: Output MUST include first 4 digits of extracted ID number
- **FR-033**: For each keyword match, output MUST show keyword name, extracted value, and page number
- **FR-034**: For each keyword match, output SHOULD show line number if available
- **FR-035**: Users MUST be able to save the output file to a location of their choice
- **FR-054**: System MUST generate a processing log file for each extraction operation containing timestamps, warnings, errors, and processing events
- **FR-055**: Log file MUST be saved automatically in a configurable log directory alongside the output file

#### User Interface
- **FR-036**: System MUST provide a single-screen graphical user interface
- **FR-037**: System MUST display a file selection area with "Browse" button and drag-and-drop capability
- **FR-038**: System MUST display a keyword input section with text field for manual entry
- **FR-039**: System MUST display a list or dropdown of previously used keywords for selection
- **FR-040**: System MUST display current keywords selected for the extraction operation
- **FR-041**: System MUST provide an "Extract" button as the primary action trigger
- **FR-042**: System MUST show a progress bar indicating extraction progress during processing
- **FR-043**: System MUST provide a settings panel or button for configuration options
- **FR-044**: System MUST display extraction results or provide notification of output file save location

#### Error Handling & Resilience
- **FR-045**: When a keyword is not found in the document, system MUST mark it as "Not found" and continue processing remaining keywords
- **FR-046**: When number format is ambiguous, system MUST make a best guess, flag with a warning indicator, and continue processing
- **FR-047**: When personal information is missing, system MUST mark as "Not found" and continue processing
- **FR-048**: System MUST collect all errors encountered during processing and report them together at the end, not stopping on first error
- **FR-049**: System MUST complete processing and generate output even when some extractions fail
- **FR-052**: System MUST reject password-protected PDF files with clear error message: "Password-protected PDFs are not supported"
- **FR-053**: System MUST detect scanned PDFs lacking extractable text and reject with error message: "Scanned PDFs requiring OCR are not supported"

#### Performance
- **FR-050**: System SHOULD complete document processing in under 10 seconds per document for typical documents
- **FR-051**: System MUST maintain a responsive user interface during document processing (not freeze)

---

### Key Entities

- **Document**: A PDF or DOCX file submitted for processing. Must be text-based (not password-protected, not requiring OCR). Contains text content with embedded keywords, numerical values, and personal information. Has pages, and potentially line structures.

- **Keyword**: A user-defined search term (e.g., "HTD", "RTP", "BGN") used to locate numerical values in documents. Case-insensitive, can appear multiple times in a document, and is stored in history for reuse.

- **Extraction Match**: A single instance of a found keyword with its associated numerical value, including location metadata (page number, optionally line number). Multiple matches can exist for the same keyword.

- **Personal Information**: Structured identity data extracted from documents, consisting of first name, last name, and ID number prefix (first 4 digits). May contain Cyrillic, Latin, or mixed character sets.

- **Output Report**: A plain text file containing all extraction results for a single document, including document metadata, personal information, and all keyword-number matches with locations.

- **Processing Log**: A timestamped log file generated for each extraction operation, recording processing events, warnings, errors, and diagnostic information for troubleshooting purposes.

- **Keyword History**: Persistent collection of previously used keywords across sessions, allowing users to quickly reselect common search terms without re-entering them.

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain - All critical clarifications resolved
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed (with warnings)

---

## Critical Open Questions from PRD

~~All critical questions from the PRD have been resolved through the clarification process.~~

### Resolved Questions:
1. ~~**Q4 - Number Format Support**~~ **RESOLVED**: US/UK format (period as decimal separator)
2. ~~**Q6 - Keyword-Number Proximity**~~ **RESOLVED**: First number after keyword in document text flow
3. ~~**Q7 - Personal Information Format**~~ **RESOLVED**: Labeled fields with consistent labels
4. ~~**Edge Case Support (password-protected, OCR)**~~ **RESOLVED**: Out of scope; reject with error messages
5. ~~**Observability**~~ **RESOLVED**: Standard logging with timestamps, warnings, and errors

### Deferred to Planning Phase:
- **Q17 - Example Documents**: Real or anonymized examples will be used during implementation validation and testing
  - **Status**: Not blocking for planning; required for implementation validation

---

**NEXT STEP**: All critical ambiguities resolved. The specification is ready to proceed to the `/plan` phase for implementation planning.
