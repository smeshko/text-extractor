# Contract: OutputGenerator Service

**Module**: `src/services/output_generator.py`
**Version**: 2.0
**Feature**: Output Format and UI Enhancements

## Purpose

Generates human-readable plain text output files from extraction results with table-like formatting, abbreviated name-based filenames, and semicolon-suffixed numeric values.

## Public Interface

### Class: OutputGenerator

#### Method: `generate(results: ExtractionResults, config: Configuration) -> OutputResult`

**Purpose**: Generate output file from extraction results

**Parameters**:
- `results: ExtractionResults` - Extraction results containing personal info, matches, document metadata
- `config: Configuration` - Application configuration with output_folder path

**Returns**: `OutputResult` with success status, file path, or error message

**Behavior**:
1. Validate output folder is writable
2. Generate filename from `results.personal_info` (CHANGED in v2.0)
3. Format output content with table-like structure (CHANGED in v2.0)
4. Write to file with UTF-8 encoding, Windows line endings (`\r\n`)
5. Return OutputResult with file path and status

**File Collision Handling** (CHANGED in v2.0):
- No collision handling per FR-009
- If file exists, it will be overwritten
- No timestamp suffix appended

**Error Handling**:
```python
# Output folder not writable
→ OutputResult(success=False, error_message="Output folder is not writable: {path}")

# Insufficient disk space
→ OutputResult(success=False, error_message="Insufficient disk space or I/O error: {error}")

# Generic failure
→ OutputResult(success=False, error_message="Failed to generate output: {error}")
```

**Examples**:
```python
generator = OutputGenerator()
result = generator.generate(extraction_results, config)

if result.success:
    print(f"Output file: {result.output_path}")  # e.g., "/output/ИЙТ-33.txt"
else:
    print(f"Error: {result.error_message}")
```

---

#### Method: `format_output(results: ExtractionResults) -> str` (CHANGED in v2.0)

**Purpose**: Format extraction results as plain text with table-like structure

**Parameters**:
- `results: ExtractionResults` - Extraction results to format

**Returns**: Formatted plain text string (UTF-8)

**Output Structure**:
```
Document: {filename}
Processed: {timestamp}

--- Personal Information ---
ИМЕ     ГОДИНИ
{abbrev} {age}

--- Keyword Extractions ---
{keyword1}    {keyword2}    {keyword3}
{value1};     {value2};     {value3};

--- Processing Summary ---
Total keywords: {count}
Successful extractions: {count}
Not found: {count}
Ambiguous: {count}
Processing time: {seconds}

--- Warnings ---
- {warning1}
- {warning2}

--- Errors ---
- {error1}
```

**Table Formatting Rules** (NEW in v2.0):
1. **Personal Information Section**:
   - Row 1 (headers): "ИМЕ" (left-aligned), "ГОДИНИ" (left-aligned)
   - Row 2 (values): abbreviated name (uppercase), age (numeric)
   - Column separator: 4+ spaces (dynamic based on max width)
   - If personal info missing: Display "Not found" messages (legacy format)

2. **Keyword Extractions Section**:
   - Row 1 (headers): Keyword names (left-aligned)
   - Row 2+ (values): Extracted values with semicolons
   - Numeric values: Append ";" immediately after (e.g., "1234;")
   - Non-numeric values: No semicolon
   - Status indicators:
     - "Not found" - No semicolon
     - "Ambiguous" values - Append ";" if numeric, add "[Ambiguous]" marker
   - Column separator: 4+ spaces (dynamic)
   - Columns expand to fit longest content (header or value)

3. **Column Width Calculation**:
   ```
   For each column:
     width = max(len(header), max(len(value) for value in column_values))
     padding = str.ljust(width + 4)  # 4 spaces minimum between columns
   ```

**Examples**:
```python
# Example output with table formatting:
"""
Document: report.pdf
Processed: 2025-10-09 14:30:22

--- Personal Information ---
ИМЕ     ГОДИНИ
ИЙТ     33

--- Keyword Extractions ---
HTD      MCV      RBC
3,5;     85,3;    4,12;

--- Processing Summary ---
Total keywords: 3 (HTD, MCV, RBC)
Successful extractions: 3
Not found: 0
Processing time: 1.23 seconds

--- Warnings ---
None

--- Errors ---
None
"""
```

**Edge Cases**:
- Long keyword names (50+ chars): Column expands, no truncation
- Empty values: Display empty cell, maintain alignment
- Missing personal info: Show "Not found" (legacy format, not table)
- No keywords: "No keyword extractions performed"

---

#### Method: `generate_filename(personal_info: PersonalInformation) -> str` (CHANGED in v2.0)

**Purpose**: Generate output filename from personal information

**Parameters**:
- `personal_info: PersonalInformation` - Personal info with full_name and age

**Returns**: Filename string in format `{ABBREV}-{AGE}.txt`

**Signature Change**:
- **v1.0**: `generate_filename(document_filename: str) -> str`
- **v2.0**: `generate_filename(personal_info: PersonalInformation) -> str`

**Behavior**:
1. Call `personal_info.get_abbreviated_name()` to get abbreviated name
2. Access `personal_info.age` for age value
3. If either is None, fall back to timestamp format
4. Combine as `{abbrev}-{age}.txt`
5. No file collision handling (overwrite if exists)

**Filename Format**:
- Pattern: `{ABBREV}-{AGE}.txt`
- Abbreviated name: Uppercase first letters of all name parts
- Age: Integer value
- Extension: Always `.txt`

**Fallback Format** (when personal info unavailable):
- Pattern: `output_{YYYYMMDD_HHMMSS}.txt`
- Uses current timestamp
- Ensures unique filename when name/age missing

**Examples**:
```python
# Full personal info
personal_info = PersonalInformation(
    first_name="Иван", middle_name="Йорданов", last_name="Тодоров", age=33, ...
)
generate_filename(personal_info) → "ИЙТ-33.txt"

# Latin name
personal_info = PersonalInformation(
    first_name="John", last_name="Doe", age=25, ...
)
generate_filename(personal_info) → "JD-25.txt"

# Single name
personal_info = PersonalInformation(first_name="Иван", age=40, ...)
generate_filename(personal_info) → "И-40.txt"

# Missing age - fallback
personal_info = PersonalInformation(first_name="Иван", age=None, ...)
generate_filename(personal_info) → "output_20251009_143022.txt"

# Missing name - fallback
personal_info = PersonalInformation(first_name=None, age=33, ...)
generate_filename(personal_info) → "output_20251009_143022.txt"
```

**Guarantees**:
- Filename is always valid for Windows/macOS/Linux filesystems
- UTF-8 encoding supported (Cyrillic preserved)
- No path traversal characters (/, \\, ..)
- Always has .txt extension

---

## Helper Methods (Private)

### `_format_table_row(cells: list[str], widths: list[int]) -> str` (NEW)

**Purpose**: Format a single table row with column alignment

**Parameters**:
- `cells: list[str]` - Cell values for this row
- `widths: list[int]` - Column widths for alignment

**Returns**: Formatted row string with left-aligned cells

**Example**:
```python
_format_table_row(["ИМЕ", "ГОДИНИ"], [10, 8])
    → "ИМЕ        ГОДИНИ  "

_format_table_row(["ИЙТ", "33"], [10, 8])
    → "ИЙТ        33      "
```

### `_calculate_column_widths(headers: list[str], rows: list[list[str]]) -> list[int]` (NEW)

**Purpose**: Calculate optimal column widths for table formatting

**Parameters**:
- `headers: list[str]` - Column headers
- `rows: list[list[str]]` - Data rows (each row is list of cell values)

**Returns**: List of column widths (max of header and all values per column)

**Example**:
```python
_calculate_column_widths(
    ["Keyword1", "Keyword2"],
    [["12345", "67"], ["89", "10111213"]]
)
    → [8, 8]  # max("Keyword1"=8, "12345"=5, "89"=2), max("Keyword2"=8, "67"=2, "10111213"=8)
```

---

## Class: OutputResult

**Purpose**: Result object for output generation operations

**Fields**:
```python
@dataclass
class OutputResult:
    success: bool
    output_path: str | None = None
    error_message: str | None = None
```

**Guarantees**:
- If `success=True`, `output_path` is not None
- If `success=False`, `error_message` is not None

---

## Input Contracts

### ExtractionResults
```python
ExtractionResults:
    personal_info: PersonalInformation  # Must have full_name and age for filename
    matches: list[ExtractionMatch]      # Keyword extraction results
    document: Document                  # Document metadata
    timestamp: datetime                 # Processing timestamp
    processing_time: float              # Time in seconds
    warnings: list[str]
    errors: list[dict]
```

### Configuration
```python
Configuration:
    output_folder: str  # Must be writable directory path
```

---

## Output Contracts

### File Format
- **Encoding**: UTF-8
- **Line Endings**: Windows CRLF (`\r\n`)
- **Extension**: `.txt`
- **Content**: Human-readable plain text with table-like formatting

### Table Format Specification
```
Personal Information Table:
  - 2 rows (header + values)
  - 2 columns (ИМЕ, ГОДИНИ)
  - Left-aligned cells
  - Minimum 4 spaces between columns

Keyword Extractions Table:
  - 2+ rows (header + value rows for each match)
  - N columns (one per keyword)
  - Left-aligned cells
  - Semicolons appended to numeric values
  - Minimum 4 spaces between columns
```

---

## Error Scenarios

| Scenario | Behavior |
|----------|----------|
| Output folder not writable | Return OutputResult(success=False, error_message) |
| Insufficient disk space | Return OutputResult(success=False, error_message) |
| Personal info missing (no name/age) | Use timestamp filename fallback |
| No keyword extractions | Display "No keyword extractions performed" |
| File already exists | Overwrite file (no collision handling in v2.0) |

---

## Validation Rules

**Input Validation**:
- `config.output_folder` must exist and be writable
- `results` must be valid ExtractionResults instance
- `personal_info` can have None fields (graceful degradation)

**Output Validation**:
- Generated filename must not contain path separators
- File must be writable to output folder
- UTF-8 encoding must succeed

---

## Performance Guarantees

- Column width calculation: O(N×M) where N=columns, M=rows
- String formatting: O(K) where K=total output length
- File writing: O(K) where K=content size
- Expected performance: <100ms for typical outputs (20 keywords, 5 pages)

---

## Backward Compatibility

**Breaking Changes**:
1. `generate_filename()` signature changed:
   - Old: `generate_filename(document_filename: str)`
   - New: `generate_filename(personal_info: PersonalInformation)`
   - **Impact**: Direct calls to this method must be updated
   - **Migration**: Pass `results.personal_info` instead of `results.document.filename`

2. File collision handling removed:
   - Old: Appended timestamp suffix on collision
   - New: Overwrites existing file
   - **Impact**: Multiple extractions of same person may overwrite files
   - **Mitigation**: Per spec FR-009, no collision handling required

**Non-Breaking Changes**:
- `format_output()` signature unchanged
- `generate()` signature unchanged
- OutputResult structure unchanged

---

## Dependencies

**Standard Library**:
- `os` - File path operations
- `datetime` - Timestamp generation
- `sys` - Path manipulation

**Internal Dependencies**:
- `models.extraction_results.ExtractionResults`
- `models.personal_information.PersonalInformation`
- `models.configuration.Configuration`

**No External Dependencies**: Constitution-compliant

---

## Usage Examples

### Complete Workflow
```python
from services.output_generator import OutputGenerator
from models.extraction_results import ExtractionResults
from models.configuration import Configuration

# Setup
generator = OutputGenerator()
config = Configuration(output_folder="/path/to/output")

# Generate output
result = generator.generate(extraction_results, config)

if result.success:
    print(f"✓ Output saved: {result.output_path}")
    # → "✓ Output saved: /path/to/output/ИЙТ-33.txt"
else:
    print(f"✗ Error: {result.error_message}")
```

### Table Formatting Example
```python
# With complete personal info and keyword extractions
"""
--- Personal Information ---
ИМЕ     ГОДИНИ
ИЙТ     33

--- Keyword Extractions ---
HTD      MCV      RBC      Hemoglobin
3,5;     85,3;    4,12;    140;
"""

# With long keyword names
"""
--- Keyword Extractions ---
VeryLongKeywordNameHere    Short    AnotherLongOne
1234;                      56;      7890;
"""
```
