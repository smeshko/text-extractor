# Feature Specification: Output Format and UI Enhancements

**Feature Branch**: `007-i-want-the`
**Created**: 2025-10-09
**Status**: Ready for Planning
**Input**: User description: "i want the following changes: 1. the values should be in a table-like format, name above, value underneath, all flowwing horizontally; 2. add a ; after each number; 3. personal information should follow the same table-like format and the values should be ИМЕ and the first letters of the 3 names and ГОДИНИ and the age that should be after the name, separated by a comma; 4. the file name should use the abbreviated name and the age, e.g. IYT-33.txt; 5. make sure the window is resizable and reduce the initial size by 10%"

## Execution Flow (main)
```
1. Parse user description from Input
   → Extract 5 distinct enhancement requirements
2. Extract key concepts from description
   → Identify: output formatting, personal info transformation, filename generation, window configuration
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → Define scenarios for output generation and UI interaction
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
Users extract data from documents and need the output file to be formatted in a more structured, readable table-like format. The personal information section should display abbreviated names with age, and the output filename should reflect this abbreviated naming convention. Additionally, users need a resizable application window with a more compact initial size to better fit different screen configurations.

### Acceptance Scenarios

1. **Given** a document has been processed with keyword extractions, **When** the output file is generated, **Then** the extracted values must be displayed in a table-like format with keyword names as headers and their corresponding values displayed underneath in aligned columns flowing horizontally.

2. **Given** numerical values are extracted from the document, **When** these values are written to the output file, **Then** each number must be followed by a semicolon (;) separator.

3. **Given** personal information contains names and age extracted from the document (where age appears after the name, separated by a comma), **When** the personal information section is formatted, **Then** it must display in a table-like format with "ИМЕ" (NAME in Cyrillic) and "ГОДИНИ" (YEARS in Cyrillic) as column headers in the first row, and the abbreviated name (first letters of all available names in uppercase) and age as values in the second row, aligned underneath their respective headers.

**Example Output Format:**
```
--- Personal Information ---
ИМЕ    ГОДИНИ
ABC    33

--- Keyword Extractions ---
Keyword1    Keyword2    Keyword3
1234;       5678;       9012;
```

4. **Given** a document has been successfully processed with extracted personal information, **When** the output filename is generated, **Then** the filename must use the abbreviated name format (first letters of three names) followed by a hyphen and the age with .txt extension (e.g., "IYT-33.txt").

5. **Given** the application window is launched, **When** it first appears, **Then** the window must be resizable (draggable edges/corners) and the initial dimensions must be 10% smaller than the current default size while maintaining all UI components accessible.

### Edge Cases

- What happens when age is not found in the document after the name - should system use placeholder value or leave empty?
- How should the system handle names with only one part (e.g., single name) when generating abbreviated form?
- What if multiple extractions occur for the same person/document, resulting in filename collisions with the identical "[ABC]-[age].txt" format?
- How should the system behave if the reduced window size (10% smaller) makes UI elements overlap or become unusable on very small screens?
- Keywords and values with very long text will not be truncated and may extend beyond typical column widths in the fixed-width table format.

---

## Requirements

### Functional Requirements

#### Output Format Requirements

- **FR-001**: System MUST format keyword extraction output in a table-like structure where keyword names appear as column headers and their corresponding extracted values appear directly underneath in aligned columns, flowing horizontally across the page.

- **FR-002**: System MUST append a semicolon (;) character immediately after every numerical value extracted from documents in the output file.

- **FR-003**: System MUST format the personal information section in a table-like structure with Cyrillic labels "ИМЕ" and "ГОДИНИ" as column headers in the first row, and their corresponding values aligned in columns underneath in the second row, flowing horizontally (similar to keyword extraction format).

- **FR-004**: System MUST generate an abbreviated name representation by taking the first letter of each available name (regardless of how many names exist), displayed in uppercase, preserving Cyrillic characters if names are in Cyrillic.

- **FR-005**: System MUST display personal information in table format where the first row contains column headers "ИМЕ" and "ГОДИНИ", and the second row contains the abbreviated name (uppercase first letters of all available names) and age (numeric value) aligned underneath their respective headers.

- **FR-006**: System MUST extract age from the document text content, where age appears after the person's name separated by a comma.

- **FR-007**: System MUST use fixed-width columns for the table-like format without column separators, allowing long keyword names or values to extend beyond typical column widths without truncation.

#### Filename Generation Requirements

- **FR-008**: System MUST generate output filenames using the format "[abbreviated name]-[age].txt" where abbreviated name consists of uppercase letters representing first letters of all available names (in Cyrillic if source names are in Cyrillic), followed by a hyphen, followed by the numeric age value.

- **FR-009**: System MUST NOT implement collision handling for the new filename format - if a file with the same name exists, it will be overwritten or result in an error based on system default behavior.

- **FR-010**: System MUST ensure generated filenames with the new format are valid for the target file system and do not contain illegal characters.

#### Window Configuration Requirements

- **FR-011**: System MUST make the application window resizable, allowing users to drag window edges and corners to adjust width and height.

- **FR-012**: System MUST reduce the initial window dimensions by 10% compared to the hardcoded minsize values (1200x1000), resulting in an initial size of 1080x900.

- **FR-013**: System MUST maintain minimum window size constraints to ensure UI components remain accessible and usable even when window is reduced.

- **FR-014**: System MUST persist user-adjusted window dimensions across application sessions (note: this may already be implemented in current system).

### Key Entities

- **Output File**: Plain text file containing formatted extraction results with table-like structure, semicolon-separated numbers, and Cyrillic-labeled personal information section.

- **Personal Information Display**: Formatted text representation in table-like structure with two rows: first row contains Cyrillic column headers ("ИМЕ", "ГОДИНИ"), second row contains abbreviated name (first letters of all available names in uppercase, preserving Cyrillic) and age values aligned underneath their respective headers.

- **Abbreviated Name**: Variable-length string derived from first letters of all available names in uppercase, preserving Cyrillic characters if present in source names.

- **Output Filename**: Text file name following pattern "[ABC]-[33].txt" derived from abbreviated personal information.

- **Application Window**: Resizable GUI window with 10% reduced initial dimensions while maintaining usability.

---

## Review & Acceptance Checklist

### Content Quality
- [ ] No implementation details (languages, frameworks, APIs)
- [ ] Focused on user value and business needs
- [ ] Written for non-technical stakeholders
- [ ] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted (5 distinct changes identified)
- [x] Ambiguities marked and resolved
- [x] User scenarios defined
- [x] Requirements generated (14 functional requirements)
- [x] Entities identified
- [x] Review checklist passed

---

## Clarifications Resolved

1. **Age Determination**: Age is extracted from document text content, appearing after the person's name separated by a comma.

2. **Variable Name Count**: System takes first letters of all available names regardless of count (not limited to exactly three names).

3. **Character Set Handling**: Cyrillic characters are preserved in abbreviated names and filenames.

4. **Filename Collision Strategy**: No collision handling - files may be overwritten if names conflict.

5. **Window Size Baseline**: 10% reduction calculated from hardcoded minsize values (1200x1000), resulting in 1080x900 initial size.

6. **Table Format Alignment**: Fixed-width columns without separators; long text extends without truncation.

---
