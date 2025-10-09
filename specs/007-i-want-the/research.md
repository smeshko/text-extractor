# Research: Output Format and UI Enhancements

**Feature**: Output Format and UI Enhancements
**Branch**: 007-i-want-the
**Date**: 2025-10-09

## Overview

This document consolidates research findings for implementing table-like output formatting, abbreviated name generation, filename updates, and window configuration changes.

## Research Areas

### 1. Table-Like Formatting in Plain Text

**Decision**: Use fixed-width column formatting with whitespace padding

**Rationale**:
- Plain text files require column alignment for human readability
- Python's built-in `str.ljust()`, `str.rjust()`, and `str.center()` provide simple column alignment
- No separators (|, tabs) per spec requirements - just whitespace
- Compatible with UTF-8/Unicode including Cyrillic characters

**Implementation Approach**:
```python
# Example table output:
ИМЕ     ГОДИНИ
АБЦ     33

Keyword1    Keyword2    Keyword3
1234;       5678;       9012;
```

**Alternatives Considered**:
- Tab-separated format: Rejected - inconsistent display across text editors
- CSV format: Rejected - adds complexity, requires quotes, not plain text format
- PrettyTable library: Rejected - adds dependency, violates constitution (single executable)

### 2. Abbreviated Name Generation

**Decision**: Extract first letter from each name part, preserve Cyrillic, uppercase output

**Rationale**:
- Python's Unicode string handling natively supports Cyrillic characters
- `str.upper()` works correctly with Cyrillic letters (е → Е, и → И)
- Variable number of names supported by iterating over split results
- Age extraction from comma-separated format already exists in personal info extractor

**Implementation Approach**:
```python
def generate_abbreviated_name(full_name: str) -> str:
    """
    Input: "Иван Йорданов Тодоров"
    Output: "ИЙТ"
    """
    parts = full_name.strip().split()
    return ''.join(part[0].upper() for part in parts if part)
```

**Alternatives Considered**:
- Fixed 3-letter abbreviation: Rejected - spec allows variable number of names
- ASCII transliteration: Rejected - spec requires Cyrillic preservation
- Lowercase output: Rejected - spec requires uppercase

### 3. Semicolon Suffix for Numbers

**Decision**: Append `;` to numeric values during output formatting

**Rationale**:
- Simple string concatenation (`value + ";"`)
- Applied only to numeric values (not "Not found" or "Ambiguous")
- No impact on storage models - purely output formatting concern

**Implementation Approach**:
```python
# In format_output method:
if match.status == 'found' and match.value:
    formatted_value = f"{match.value};"
```

**Alternatives Considered**:
- Modify extraction logic: Rejected - violates separation of concerns
- Add to data model: Rejected - semicolon is presentation detail, not data

### 4. Dynamic Filename Generation

**Decision**: Replace `generate_filename()` to use abbreviated name and age format

**Rationale**:
- Filename format: `{ABBREV_NAME}-{AGE}.txt` (e.g., "ИЙТ-33.txt")
- Windows filesystem supports Cyrillic filenames (UTF-8)
- Collision handling removed per spec FR-009 - overwrite behavior
- Age must be extracted from PersonalInformation model

**Implementation Approach**:
```python
def generate_filename(self, personal_info: PersonalInformation) -> str:
    """
    Generate filename from personal info.
    Format: ABC-33.txt
    """
    if not personal_info.full_name or not personal_info.age:
        # Fallback for missing data
        return f"output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

    abbrev = self._generate_abbreviated_name(personal_info.full_name)
    return f"{abbrev}-{personal_info.age}.txt"
```

**Alternatives Considered**:
- Keep collision handling: Rejected - spec explicitly excludes (FR-009)
- Sanitize Cyrillic characters: Rejected - spec requires preservation (FR-010)

### 5. Window Resizability and Initial Size

**Decision**: Remove `minsize()` lock, set initial geometry to 1080x900

**Rationale**:
- Current implementation sets `minsize(1200, 1000)` which prevents resizing below that threshold
- Per spec FR-012: 10% reduction = 1200×0.9 = 1080, 1000×0.9 = 900
- tkinter windows are resizable by default unless explicitly disabled
- Removing `minsize()` allows full user control while maintaining usability

**Implementation Approach**:
```python
# In main_window.py __init__:
self.root.geometry("1080x900")  # 10% smaller than 1200x1000
# Remove: self.root.minsize(1200, 1000)
```

**Alternatives Considered**:
- Add `resizable(True, True)`: Rejected - redundant, True is default
- Set new minsize to 1080x900: Rejected - spec says "resizable", implying no hard limits
- Calculate 10% from config values: Rejected - spec references hardcoded 1200x1000

## Technical Constraints

### Unicode/Cyrillic Handling
- All string operations must preserve Cyrillic characters
- Python 3.10+ handles UTF-8 natively
- Windows filesystem supports Unicode filenames
- No transliteration or encoding changes needed

### Existing Architecture Integration
- **PersonalInformation Model**: Must add `full_name` and `age` fields (currently only has first_name, last_name)
- **OutputGenerator**: Requires refactor of `format_output()` and `generate_filename()` methods
- **MainWindow**: Minimal changes to geometry and minsize configuration

### Constitutional Compliance
- **No new dependencies**: All changes use Python stdlib
- **Single executable**: No impact on PyInstaller packaging
- **Graceful degradation**: Missing personal info → fallback filename with timestamp
- **Human-readable output**: Table format improves readability per Constitution V

## Data Model Changes Required

### PersonalInformation Model Extensions

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
1. Add `full_name: str | None` property or method combining first_name + last_name
2. Add `age: int | None` field for age extraction (currently not captured)
3. Add `get_abbreviated_name() -> str` method

**Extraction Impact**:
- PersonalInfoExtractor must parse age from comma-separated format after name
- Age validation: must be numeric, typically 0-120 range

## Edge Case Handling

### Missing Personal Information
- **Missing age**: Use timestamp filename fallback
- **Missing name**: Use timestamp filename fallback
- **Single-word name**: "Иван" → "И-33.txt"
- **Empty name parts**: Filter out with `if part` check

### Table Formatting
- **Variable column widths**: Calculate max width per column dynamically
- **Long keyword names**: Extend column, no truncation (per spec FR-007)
- **Empty values**: Display as empty cell, maintain alignment

### Filename Edge Cases
- **Cyrillic in filename**: Windows supports natively, no sanitization
- **File collision**: Per FR-009, no handling - overwrite or error
- **Invalid age values**: Fallback to timestamp format

## Performance Considerations

- Column width calculation: O(n) per column, negligible for typical extractions (5-20 keywords)
- String concatenation: Use list + join for efficiency
- Abbreviated name generation: O(m) where m = number of name parts, typically 2-4
- No performance degradation expected

## Testing Strategy (Manual Validation)

Per constitution, manual testing required:

1. **Table formatting**: Verify column alignment with Cyrillic text
2. **Abbreviated names**: Test 1, 2, 3, 4+ name parts
3. **Semicolons**: Verify all numeric values have suffix
4. **Filename generation**: Test Cyrillic names, various ages
5. **Window sizing**: Verify initial size 1080x900, test resize functionality
6. **Edge cases**: Missing data, long keywords, single-name individuals

## Dependencies

**No new dependencies required** - all changes use:
- Python standard library (`str` methods, `datetime`)
- Existing tkinter functionality
- Current project models and services

## Summary

All technical unknowns resolved. Implementation requires:
1. PersonalInformation model extension (full_name, age fields)
2. OutputGenerator refactor (table formatting, filename generation)
3. MainWindow configuration update (geometry, minsize removal)
4. No architectural changes, constitutional compliance maintained

Ready for Phase 1: Design & Contracts.
