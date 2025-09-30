# Data Model: Document Data Extraction Tool

**Date**: September 30, 2025
**Feature**: Document Data Extraction Tool
**Branch**: 001-use-docs-prd

## Entity Definitions

### 1. Document

**Description**: Represents a PDF or DOCX file submitted for processing.

**Attributes**:
- `file_path` (str): Absolute path to the document file
- `filename` (str): Original filename without path
- `file_type` (str): Document type ("pdf" or "docx")
- `page_count` (int): Total number of pages in document
- `is_valid` (bool): Whether document is accessible and parsable
- `error_message` (str | None): Error description if document is invalid

**Validation Rules**:
- File must exist at specified path
- Extension must be `.pdf` or `.docx` (case-insensitive)
- File must be readable (permissions check)
- PDF must not be password-protected (FR-052)
- PDF must contain extractable text, not be scanned-only (FR-053)
- File size should be reasonable (< 50MB recommended)

**State Transitions**:
- UNSELECTED → SELECTED (user chooses file)
- SELECTED → VALIDATING (checking file properties)
- VALIDATING → VALID (all checks pass)
- VALIDATING → INVALID (any check fails)

**Related Entities**: ExtractionMatch, PersonalInformation, OutputReport

---

### 2. Keyword

**Description**: A user-defined search term for locating numerical values in documents.

**Attributes**:
- `text` (str): The keyword text (original case preserved)
- `normalized` (str): Lowercase version for case-insensitive matching
- `is_historical` (bool): Whether from keyword history or newly entered
- `is_active` (bool): Whether currently selected for extraction

**Validation Rules**:
- Length: 1-100 characters (FR-specific, from technical specs)
- Characters: Alphanumeric + limited punctuation (prevent regex injection)
- No empty or whitespace-only strings
- Sanitized for regex use (escape special characters)

**Persistence**:
- Keywords added to history after first use
- History stored in config.json (FR-010)
- No duplicates in history (case-insensitive comparison)
- Order: most recent last

**Related Entities**: ExtractionMatch, KeywordHistory

---

### 3. ExtractionMatch

**Description**: A single instance of a found keyword with its associated numerical value and location metadata.

**Attributes**:
- `keyword` (str): The matched keyword text
- `value` (str | float): Extracted numerical value (stored as string initially)
- `page_number` (int): Page where match was found (1-indexed)
- `line_number` (int | None): Line number within page (if available)
- `status` (str): Match status ("found", "not_found", "ambiguous")
- `warning` (str | None): Warning message if value is ambiguous

**Validation Rules**:
- Keyword must be non-empty
- Page number must be >= 1 and <= document page count
- Line number (if present) must be >= 1
- Status must be one of: "found", "not_found", "ambiguous"
- If status is "not_found", value should be None or "Not found"

**Value Format**:
- US/UK number format: period as decimal, comma as thousands separator
- Examples: "3.5", "1,234.56", "42"
- Stored as string to preserve original format from document

**Multiple Occurrences**:
- Same keyword can have multiple ExtractionMatch instances (FR-014)
- Each occurrence tracked separately with its own location

**Related Entities**: Keyword, Document, OutputReport

---

### 4. PersonalInformation

**Description**: Structured identity data extracted from document, including name and ID number.

**Attributes**:
- `first_name` (str | None): Extracted first name
- `last_name` (str | None): Extracted last name
- `id_number_prefix` (str | None): First 4 digits of ID number
- `character_set` (str): Character set detected ("cyrillic", "latin", "mixed")
- `extraction_page` (int | None): Page where information was found
- `is_complete` (bool): Whether all fields were successfully extracted

**Validation Rules**:
- Names: May contain Cyrillic or Latin characters, spaces, hyphens
- ID prefix: Exactly 4 digits if found
- Character set: One of "cyrillic", "latin", "mixed", "unknown"
- If any field is None, mark as "Not found" (FR-026)

**Field Extraction**:
- First name: From labeled fields (FR-020, FR-021)
  - Cyrillic labels: "Име:", "Имя:", "Name:"
  - Latin labels: "First Name:", "Name:"
- Last name: From labeled fields (FR-022, FR-023)
  - Cyrillic labels: "Фамилия:", "Фамилія:", "Surname:"
  - Latin labels: "Last Name:", "Surname:"
- ID number: From labeled fields (FR-025)
  - Labels: "ID:", "ЕГН:", "ID Number:", "Номер:"
  - Extract only first 4 digits

**Search Strategy**:
- Primary: First page of document (most likely location)
- Fallback: Full document scan if not found on first page
- Stop on first successful match for each field

**Related Entities**: Document, OutputReport

---

### 5. OutputReport

**Description**: Plain text file containing all extraction results for a single document.

**Attributes**:
- `document_filename` (str): Original document filename
- `processing_timestamp` (str): Date and time of extraction (ISO 8601 format)
- `personal_info` (PersonalInformation): Extracted personal information
- `matches` (list[ExtractionMatch]): All keyword-number matches
- `errors` (list[str]): Collection of error messages
- `warnings` (list[str]): Collection of warning messages
- `output_path` (str): Full path to generated output file

**File Naming**:
- Convention: `output_[original_filename].txt`
- Example: `output_report_2024.txt`
- Location: User-configurable output folder (from config.json)

**Content Structure**:
```
Document: [filename]
Processed: [timestamp]
Name: [first] [last]
ID: [4 digits]***
[Keyword]: [value] (Page X, Line Y)
[Keyword]: [value] (Page X, Line Y)
...
Errors:
- [error message 1]
- [error message 2]
Warnings:
- [warning message 1]
```

**Format Requirements** (Constitution Principle V):
- Plain text, UTF-8 encoding
- Human-readable, flat structure
- Clear labels for all fields
- Page and line numbers for each match
- Document metadata at top
- Errors and warnings at bottom

**Related Entities**: Document, ExtractionMatch, PersonalInformation, ProcessingLog

---

### 6. ProcessingLog

**Description**: Timestamped log file recording extraction events, warnings, and errors.

**Attributes**:
- `log_filename` (str): Unique log filename with timestamp
- `log_path` (str): Full path to log file
- `entries` (list[LogEntry]): Collection of log entries
- `start_time` (datetime): Extraction start timestamp
- `end_time` (datetime | None): Extraction end timestamp
- `status` (str): Overall status ("success", "partial_success", "failure")

**LogEntry Structure**:
- `timestamp` (datetime): When event occurred
- `level` (str): Log level ("INFO", "WARNING", "ERROR")
- `message` (str): Log message
- `context` (dict | None): Additional context data

**File Naming**:
- Convention: `extraction_YYYYMMDD_HHMMSS.log`
- Example: `extraction_20250930_143022.log`
- Location: Configurable log directory (from config.json)

**Logged Events**:
- Extraction start (document filename, keywords)
- Document parsing success/failure
- Each keyword search result
- Personal information extraction results
- Number format ambiguities (warnings)
- Missing data (not found keywords)
- Errors and exceptions
- Extraction completion

**Retention**:
- No automatic deletion (user manages logs)
- Optional enhancement: Archive logs older than 30 days

**Related Entities**: OutputReport, Document

---

### 7. KeywordHistory

**Description**: Persistent collection of previously used keywords across sessions.

**Attributes**:
- `keywords` (list[str]): Ordered list of unique keywords
- `last_updated` (datetime): Last modification timestamp
- `max_size` (int): Maximum number of keywords to retain (unlimited by default, practical limit ~1000)

**Persistence**:
- Stored in config.json as array of strings
- Loaded on application start
- Saved on application close and when new keyword added
- Order maintained: most recent last

**Operations**:
- Add: Append new keyword if not already present (case-insensitive check)
- Remove: Optional feature (not in MVP scope)
- Select: Multi-select for extraction operation
- Clear: Optional feature (not in MVP scope)

**Related Entities**: Keyword, Configuration

---

### 8. Configuration

**Description**: Application settings persisted across sessions.

**Attributes**:
- `output_folder` (str): Default output file location
- `log_directory` (str): Log file storage location
- `number_format` (str): Number format preference ("us_uk")
- `proximity_rule` (str): Keyword-number association rule ("next_number")
- `keyword_history` (list[str]): Historical keywords
- `window_width` (int): Main window width (pixels)
- `window_height` (int): Main window height (pixels)

**Storage**:
- File: `config.json` in application directory
- Format: JSON
- Encoding: UTF-8

**Default Values**:
```json
{
  "output_folder": "~/Documents/ExtractionOutput",
  "log_directory": "~/Documents/ExtractionOutput/logs",
  "number_format": "us_uk",
  "proximity_rule": "next_number",
  "keyword_history": [],
  "window_width": 800,
  "window_height": 600
}
```

**Validation**:
- Output folder and log directory must be writable
- Number format must be "us_uk" (only supported format)
- Proximity rule must be "next_number" (only supported rule)
- Window dimensions must be >= 600x400 (minimum usable size)

**Lifecycle**:
- Load on app start (create with defaults if missing)
- Save on app close
- Save immediately when user changes settings
- Use defaults if file is corrupted

**Related Entities**: KeywordHistory

---

### 9. ApplicationState

**Description**: Runtime application state (not persisted).

**Attributes**:
- `current_document` (Document | None): Currently selected document
- `active_keywords` (list[Keyword]): Keywords selected for extraction
- `processing_status` (str): Current processing state
- `extraction_results` (ExtractionResults | None): Results of last extraction
- `error_messages` (list[str]): Current session errors
- `is_processing` (bool): Whether extraction is currently running

**State Values** (processing_status):
- `IDLE`: No document selected or ready for new extraction
- `FILE_SELECTED`: Document selected, waiting for keywords
- `READY`: Document and keywords ready, can start extraction
- `PROCESSING`: Extraction in progress
- `COMPLETE`: Extraction finished successfully
- `ERROR`: Extraction failed
- `PARTIAL_SUCCESS`: Some extractions succeeded, some failed

**State Transitions**:
- IDLE → FILE_SELECTED (user selects file)
- FILE_SELECTED → READY (user adds keywords)
- READY → PROCESSING (user clicks Extract)
- PROCESSING → COMPLETE (extraction succeeds)
- PROCESSING → ERROR (extraction fails completely)
- PROCESSING → PARTIAL_SUCCESS (some extractions fail)
- Any state → IDLE (user resets or selects new file)

**Thread Safety**:
- State updates only from main thread
- Worker thread communicates via queue
- Immutable state transitions (create new state object)

**Related Entities**: Document, Keyword, ExtractionResults

---

### 10. ExtractionResults

**Description**: Container for all results from a single extraction operation.

**Attributes**:
- `document` (Document): Processed document reference
- `personal_info` (PersonalInformation): Extracted personal data
- `matches` (list[ExtractionMatch]): All keyword matches
- `errors` (list[dict]): Structured error collection
- `warnings` (list[str]): Warning messages
- `processing_time` (float): Seconds taken for extraction
- `timestamp` (datetime): When extraction was performed

**Error Structure**:
```python
{
  'type': 'keyword_not_found' | 'parsing_error' | 'file_error' | 'extraction_error',
  'message': 'Human-readable error description',
  'context': {
    'keyword': 'HTD',  # if applicable
    'page': 5,         # if applicable
    'detail': '...'    # additional info
  }
}
```

**Methods**:
- `add_match(match: ExtractionMatch)`: Add successful extraction
- `add_error(type: str, message: str, context: dict)`: Add error
- `add_warning(message: str)`: Add warning
- `has_errors() -> bool`: Check if any errors occurred
- `has_warnings() -> bool`: Check if any warnings occurred
- `get_error_summary() -> str`: Human-readable error summary
- `is_complete() -> bool`: Check if all extractions attempted

**Related Entities**: ExtractionMatch, PersonalInformation, OutputReport, ProcessingLog

---

## Entity Relationships

```
Document (1) -----> (N) ExtractionMatch
Document (1) -----> (1) PersonalInformation
Document (1) -----> (1) OutputReport
Document (1) -----> (1) ProcessingLog

Keyword (1) ------> (N) ExtractionMatch
Keyword (N) <-----> (1) KeywordHistory

ExtractionMatch (N) --> (1) OutputReport
PersonalInformation (1) --> (1) OutputReport

Configuration (1) ----> (1) KeywordHistory

ApplicationState (1) --> (0..1) Document
ApplicationState (1) --> (N) Keyword
ApplicationState (1) --> (0..1) ExtractionResults

ExtractionResults (1) --> (1) Document
ExtractionResults (1) --> (1) PersonalInformation
ExtractionResults (1) --> (N) ExtractionMatch
```

---

## Data Flow

### Extraction Pipeline

```
1. User selects Document
   → Document entity created, validated
   → ApplicationState updated (IDLE → FILE_SELECTED)

2. User adds Keywords
   → Keyword entities created
   → Keywords added to ApplicationState.active_keywords
   → ApplicationState updated (FILE_SELECTED → READY)

3. User clicks Extract
   → ApplicationState updated (READY → PROCESSING)
   → ExtractionResults entity created
   → ProcessingLog entity created

4. Worker thread processes Document
   → Parse document pages
   → For each Keyword:
      a. Search for matches
      b. Extract numbers
      c. Create ExtractionMatch entities
      d. Add to ExtractionResults
   → Extract PersonalInformation
   → Collect errors and warnings

5. Generate outputs
   → Create OutputReport from ExtractionResults
   → Write report to file
   → Finalize ProcessingLog
   → ApplicationState updated (PROCESSING → COMPLETE/ERROR/PARTIAL_SUCCESS)

6. Update persistence
   → Add new keywords to KeywordHistory
   → Save Configuration
```

---

## Validation Summary

| Entity | Critical Validations |
|--------|---------------------|
| Document | File exists, readable, supported format, not password-protected, has text |
| Keyword | Non-empty, 1-100 chars, sanitized for regex |
| ExtractionMatch | Valid page/line numbers, status enum, value format |
| PersonalInformation | Character set validation, field format (4-digit ID prefix) |
| OutputReport | Valid UTF-8, proper structure, all required fields |
| ProcessingLog | Valid timestamps, log level enum |
| Configuration | Writable paths, valid enum values, minimum window size |
| ApplicationState | Valid state transitions, thread-safe updates |

---

**Data Model Complete**: All entities defined with attributes, validation rules, and relationships. Ready for contract generation.
