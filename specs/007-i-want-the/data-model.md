# Data Model: Output Format and UI Enhancements

**Feature**: Output Format and UI Enhancements
**Branch**: 007-i-want-the
**Date**: 2025-10-09

## Overview

This document defines the data model changes and extensions required for implementing table-like output formatting, abbreviated name generation, and dynamic filename creation.

## Model Changes

### 1. PersonalInformation Model Extension

**Location**: `src/models/personal_information.py`

**Current State**:
```python
@dataclass
class PersonalInformation:
    first_name: str | None
    last_name: str | None
    id_number_prefix: str | None
    character_set: str
    extraction_page: int | None
    is_complete: bool
```

**Required Changes**:

#### New Fields
```python
@dataclass
class PersonalInformation:
    first_name: str | None
    last_name: str | None
    middle_name: str | None  # NEW - for 3+ name parts
    id_number_prefix: str | None
    age: int | None  # NEW - extracted from document after name
    character_set: str
    extraction_page: int | None
    is_complete: bool
```

#### New Computed Properties/Methods
```python
@property
def full_name(self) -> str | None:
    """Combine all name parts into full name.

    Returns:
        Full name string or None if no name parts available

    Example:
        first_name="Иван", last_name="Петров" → "Иван Петров"
        first_name="Иван", middle_name="Йорданов", last_name="Тодоров"
            → "Иван Йорданов Тодоров"
    """

def get_abbreviated_name(self) -> str | None:
    """Generate abbreviated name from first letters.

    Returns:
        Uppercase abbreviated name or None if no full_name

    Example:
        "Иван Петров" → "ИП"
        "Иван Йорданов Тодоров" → "ИЙТ"
        "John" → "J"

    Rules:
        - Take first letter of each name part
        - Convert to uppercase
        - Preserve Cyrillic characters
        - Filter empty parts
    """
```

**Validation Rules**:
- `age`: Must be None or integer in range 0-150
- `age`: Must be extracted from text content appearing after name, separated by comma
- `middle_name`: Optional, supports multiple middle names (stored as single string)
- `full_name` property: Returns space-joined non-None name parts
- `is_complete`: Updated logic to include age check (optional for backward compatibility)

**State Transitions**: None (data class, no state machine)

### 2. OutputGenerator Service Changes

**Location**: `src/services/output_generator.py`

**Current Methods to Modify**:

#### `format_output(results: ExtractionResults) -> str`

**Changes**:
- Replace Personal Information section with table format:
  ```
  --- Personal Information ---
  ИМЕ     ГОДИНИ
  ИЙТ     33
  ```
- Replace Keyword Extractions section with table format:
  ```
  --- Keyword Extractions ---
  Keyword1    Keyword2    Keyword3
  1234;       5678;       9012;
  ```
- Add semicolons to all numeric values in keyword section

**Table Formatting Algorithm**:
```
1. Collect all column headers (keywords or "ИМЕ"/"ГОДИНИ")
2. Collect all column values
3. Calculate max width per column: max(len(header), len(value))
4. Pad each cell with str.ljust(width) for left alignment
5. Join cells with fixed spacing (e.g., 4 spaces)
6. Generate header row
7. Generate value row(s)
```

#### `generate_filename(results: ExtractionResults) -> str`

**Current Signature**:
```python
def generate_filename(self, document_filename: str) -> str:
    # Returns: "output_{document_name}.txt"
```

**New Signature**:
```python
def generate_filename(self, personal_info: PersonalInformation) -> str:
    """Generate filename from personal information.

    Args:
        personal_info: PersonalInformation with full_name and age

    Returns:
        Filename in format "{ABBREV}-{AGE}.txt" (e.g., "ИЙТ-33.txt")
        Falls back to timestamp format if personal info incomplete

    Examples:
        full_name="Иван Йорданов Тодоров", age=33 → "ИЙТ-33.txt"
        full_name="John Doe", age=25 → "JD-25.txt"
        full_name=None → "output_20251009_143022.txt"
    """
```

**Fallback Behavior**:
- If `personal_info.full_name` is None → use timestamp format
- If `personal_info.age` is None → use timestamp format
- If `get_abbreviated_name()` returns None → use timestamp format
- Timestamp format: `"output_{YYYYMMDD_HHMMSS}.txt"`

**File Collision Handling**: REMOVED per FR-009
- No timestamp suffix on collision
- File will be overwritten or error based on system behavior

### 3. Configuration Model (Unchanged)

**Location**: `src/models/configuration.py`

**Window Size Fields**:
- `window_width`: Default changes from 1200 to 1080
- `window_height`: Default changes from 1000 to 900
- No new fields required

**Note**: Changes are in MainWindow initialization, not Configuration model itself.

## Entity Relationships

```
ExtractionResults
├── personal_info: PersonalInformation (1:1)
│   ├── full_name: str | None
│   ├── age: int | None
│   └── get_abbreviated_name() -> str | None
├── matches: List[ExtractionMatch] (1:N)
└── document: Document (1:1)

OutputGenerator
├── format_output(ExtractionResults) -> str
│   ├── Uses: PersonalInformation.full_name, .age
│   └── Uses: ExtractionMatch.keyword, .value
└── generate_filename(PersonalInformation) -> str
    └── Uses: PersonalInformation.get_abbreviated_name(), .age
```

## Data Flow

### 1. Personal Information Extraction
```
Document (PDF/DOCX)
    ↓
PersonalInfoExtractor.extract()
    ↓ (parse name parts + age from text)
PersonalInformation(
    first_name="Иван",
    middle_name="Йорданов",
    last_name="Тодоров",
    age=33
)
    ↓ (computed property)
full_name → "Иван Йорданов Тодоров"
    ↓ (method call)
get_abbreviated_name() → "ИЙТ"
```

### 2. Output File Generation
```
ExtractionResults
    ↓
OutputGenerator.generate(results, config)
    ↓
generate_filename(results.personal_info)
    ├── results.personal_info.get_abbreviated_name() → "ИЙТ"
    ├── results.personal_info.age → 33
    └── Returns: "ИЙТ-33.txt"
    ↓
format_output(results)
    ├── Format personal info as table (ИМЕ/ГОДИНИ headers)
    ├── Format keyword extractions as table (keyword headers)
    └── Add semicolons to numeric values
    ↓
Write to file: "{output_folder}/ИЙТ-33.txt"
```

## Validation Rules Summary

| Field | Type | Validation | Default/Fallback |
|-------|------|------------|------------------|
| PersonalInformation.age | int \| None | 0 ≤ age ≤ 150 or None | None |
| PersonalInformation.middle_name | str \| None | Any string or None | None |
| PersonalInformation.full_name (property) | str \| None | Auto-computed from name parts | None if all parts None |
| OutputGenerator filename | str | Valid filesystem chars, UTF-8 | Timestamp format if personal info missing |
| Table column widths | int | max(len(header), max(len(values))) | Minimum 1 character |

## Backward Compatibility

**PersonalInformation Model**:
- Existing code using `first_name`, `last_name` continues to work
- `middle_name` and `age` are optional (default None)
- `is_complete` logic optionally includes age check

**OutputGenerator**:
- `generate_filename()` signature changes - BREAKING CHANGE
  - Old calls: `generate_filename(document.filename)`
  - New calls: `generate_filename(results.personal_info)`
  - Requires update in `OutputGenerator.generate()` method

**MainWindow**:
- No model changes, only configuration values
- Existing window size persistence continues to work

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No name parts available | `full_name` returns None, filename uses timestamp |
| Single-word name | `full_name` = "Иван", `get_abbreviated_name()` = "И" |
| Age missing from document | `age` = None, filename uses timestamp |
| Age extraction fails (non-numeric) | `age` = None, graceful degradation |
| Keyword value is empty string | Display empty cell in table, maintain alignment |
| Very long keyword (50+ chars) | Column expands, no truncation per FR-007 |
| Cyrillic + Latin mixed name | "John Иванов" → "JI", preserves both scripts |

## Migration Path

**Phase 1: Model Extension**
1. Add `middle_name` and `age` fields to PersonalInformation
2. Implement `full_name` property
3. Implement `get_abbreviated_name()` method
4. Update PersonalInfoExtractor to parse age from comma-separated format

**Phase 2: Output Generator Refactor**
1. Create table formatting helper methods
2. Refactor `format_output()` for table layout
3. Update `generate_filename()` signature and implementation
4. Update `generate()` method to pass PersonalInformation instead of document filename

**Phase 3: UI Configuration**
1. Update MainWindow geometry initialization to 1080x900
2. Remove or adjust minsize constraint

No database migrations required (file-based storage only).
