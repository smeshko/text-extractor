# Output Contract

**Component**: OutputGenerator, ProcessingLogger
**Purpose**: Generate plain text output files and processing logs

## Interface Definition

### OutputGenerator

```python
class OutputGenerator:
    """Generates plain text output files from extraction results"""

    def generate(self, results: ExtractionResults, config: Configuration) -> OutputResult:
        """
        Generate output file from extraction results

        Args:
            results: ExtractionResults from extraction engine
            config: Configuration with output folder path

        Returns:
            OutputResult with file path and status

        Raises:
            IOError: If output folder not writable
            OSError: If disk space insufficient
        """
        pass

    def format_output(self, results: ExtractionResults) -> str:
        """
        Format extraction results as plain text

        Args:
            results: ExtractionResults to format

        Returns:
            Formatted plain text string (UTF-8)
        """
        pass

    def generate_filename(self, document_filename: str) -> str:
        """
        Generate output filename from document filename

        Args:
            document_filename: Original document filename

        Returns:
            Output filename: 'output_[original_filename].txt'
        """
        pass
```

---

## Data Structures

### OutputResult

```python
@dataclass
class OutputResult:
    """Result of output generation"""

    success: bool
    output_path: str | None
    error_message: str | None = None
```

---

## Output Format Specification

### Structure

```
Document: [filename]
Processed: [timestamp]
Name: [first] [last]
ID: [4 digits]***

--- Keyword Extractions ---
[Keyword]: [value] (Page X, Line Y)
[Keyword]: [value] (Page X)
[Keyword]: Not found

--- Personal Information ---
First Name: [first name] | Not found
Last Name: [last name] | Not found
ID Number: [4 digits]*** | Not found

--- Processing Summary ---
Total keywords: [N]
Successful extractions: [N]
Not found: [N]
Processing time: [X.XX] seconds

--- Warnings ---
- [warning message 1]
- [warning message 2]

--- Errors ---
- [error message 1]
- [error message 2]
```

### Example Output

```
Document: medical_report_2024.pdf
Processed: 2025-09-30 14:30:22

--- Personal Information ---
First Name: Иван
Last Name: Петров
ID Number: 1234***
Character Set: Cyrillic

--- Keyword Extractions ---
HTD: 3.5 (Page 2, Line 15)
HTD: 4.2 (Page 5, Line 8)
HTD: 7.8 (Page 12, Line 3)
RTP: 125.5 (Page 3, Line 22)
BGN: Not found

--- Processing Summary ---
Total keywords: 3 (HTD, RTP, BGN)
Successful extractions: 4
Not found: 1
Processing time: 2.34 seconds

--- Warnings ---
- Number "1,234" on Page 3 could be ambiguous, interpreted as one thousand two hundred thirty-four

--- Errors ---
None
```

---

## Formatting Rules

### General
- UTF-8 encoding (FR-027, Constitution Principle III)
- Windows line endings (`\r\n`) for Windows compatibility
- Clear section headers with `---` separators
- Human-readable format (Constitution Principle V)

### Document Metadata
- Filename: Original document filename (no path)
- Timestamp: ISO 8601 format `YYYY-MM-DD HH:MM:SS`

### Personal Information
- Show all fields even if "Not found"
- First 4 digits of ID followed by `***` to indicate masking
- Character set indicator for transparency

### Keyword Extractions
- One line per match
- Format: `[Keyword]: [value] (Page X, Line Y)`
- If line number unavailable: `(Page X)`
- If not found: `[Keyword]: Not found`
- Group multiple occurrences of same keyword together

### Processing Summary
- Total keyword count and list
- Successful extraction count
- Not found count
- Processing time in seconds (2 decimal places)

### Warnings and Errors
- Bulleted list format (`- [message]`)
- If none: Show "None" instead of empty section
- Warnings: Non-critical issues (ambiguous formats, partial data)
- Errors: Serious problems (parsing failures, file access issues)

---

## File Naming Convention

### Pattern
```
output_[original_filename].txt
```

### Examples
- `report.pdf` → `output_report.txt`
- `medical_record_2024.docx` → `output_medical_record_2024.txt`
- `Документ.pdf` → `output_Документ.txt` (Unicode preserved)

### Collision Handling
If file already exists, append timestamp:
```
output_[original_filename]_[YYYYMMDD_HHMMSS].txt
```

Example: `output_report_20250930_143022.txt`

---

## ProcessingLogger

```python
class ProcessingLogger:
    """Generates processing log files"""

    def __init__(self, log_directory: str):
        """
        Initialize logger

        Args:
            log_directory: Directory for log files (from config)
        """
        pass

    def start_logging(self, document_filename: str, keywords: list[str]) -> str:
        """
        Start logging for extraction operation

        Args:
            document_filename: Document being processed
            keywords: Keywords to extract

        Returns:
            Log file path
        """
        pass

    def log_event(self, level: str, message: str, context: dict = None) -> None:
        """
        Log an event

        Args:
            level: 'INFO', 'WARNING', 'ERROR'
            message: Log message
            context: Optional context data
        """
        pass

    def finalize(self, status: str, results: ExtractionResults) -> None:
        """
        Finalize log with summary

        Args:
            status: 'success', 'partial_success', 'failure'
            results: ExtractionResults for summary
        """
        pass
```

### Log Format

```
2025-09-30 14:30:20 [INFO] Starting extraction: medical_report_2024.pdf
2025-09-30 14:30:20 [INFO] Keywords: HTD, RTP, BGN
2025-09-30 14:30:21 [INFO] Document parsed successfully: 15 pages
2025-09-30 14:30:21 [INFO] Searching for keyword: HTD
2025-09-30 14:30:21 [INFO] Found HTD on page 2, line 15: value 3.5
2025-09-30 14:30:21 [INFO] Found HTD on page 5, line 8: value 4.2
2025-09-30 14:30:21 [INFO] Found HTD on page 12, line 3: value 7.8
2025-09-30 14:30:22 [INFO] Searching for keyword: RTP
2025-09-30 14:30:22 [INFO] Found RTP on page 3, line 22: value 125.5
2025-09-30 14:30:22 [INFO] Searching for keyword: BGN
2025-09-30 14:30:22 [WARNING] Keyword BGN not found in document
2025-09-30 14:30:22 [INFO] Extracting personal information
2025-09-30 14:30:22 [INFO] Found first name: Иван (page 1)
2025-09-30 14:30:22 [INFO] Found last name: Петров (page 1)
2025-09-30 14:30:22 [INFO] Found ID: 1234*** (page 1)
2025-09-30 14:30:22 [WARNING] Number "1,234" could be ambiguous
2025-09-30 14:30:22 [INFO] Extraction complete: 4 matches, 1 not found
2025-09-30 14:30:22 [INFO] Output written to: C:/Users/.../output_medical_report_2024.txt
2025-09-30 14:30:22 [INFO] Processing time: 2.34 seconds
2025-09-30 14:30:22 [INFO] Status: success
```

---

## Contract Guarantees

### Input Contracts

**generate()**:
- REQUIRES: `results` is valid ExtractionResults object
- REQUIRES: `config.output_folder` is writable directory
- REQUIRES: `results.document.filename` is non-empty

**format_output()**:
- REQUIRES: `results` is valid ExtractionResults object

**generate_filename()**:
- REQUIRES: `document_filename` is non-empty string
- ACCEPTS: Unicode characters in filename

---

### Output Contracts

**generate()**:
- ENSURES: If success=True, output_path exists and contains valid UTF-8 text
- ENSURES: If success=False, error_message explains why
- ENSURES: File created with unique name (no overwrites without warning)
- ENSURES: All results included in output (matches, personal info, errors, warnings)

**format_output()**:
- ENSURES: Returns valid UTF-8 string
- ENSURES: Follows format specification exactly
- ENSURES: All required sections present
- ENSURES: Human-readable format (Constitution Principle V)

**generate_filename()**:
- ENSURES: Returns filename with `output_` prefix and `.txt` extension
- ENSURES: Original filename preserved (including Unicode)
- ENSURES: No path separators in output (filename only)

---

## Error Handling

### File System Errors

**Output folder not writable**:
- Detect before writing: `os.access(folder, os.W_OK)`
- Error message: "Output folder is not writable: [path]"
- Suggest user action: "Please select a different output folder in Settings"

**Disk space insufficient**:
- Catch `OSError` during write
- Error message: "Insufficient disk space to write output file"
- Suggest user action: "Free up disk space and try again"

**File already exists**:
- Append timestamp to filename
- Log warning: "Output file already exists, using timestamped filename"

### Character Encoding Errors

**Non-UTF-8 characters**:
- Handle during format: `text.encode('utf-8', errors='replace')`
- Log warning if replacements made
- Ensure output is always valid UTF-8

---

## Usage Example

```python
# Generate output
generator = OutputGenerator()
output_result = generator.generate(extraction_results, config)

if output_result.success:
    print(f"Output saved to: {output_result.output_path}")
else:
    print(f"Failed to generate output: {output_result.error_message}")

# Processing log
logger = ProcessingLogger(config.log_directory)
log_path = logger.start_logging(document.filename, keywords)

logger.log_event('INFO', f'Starting extraction: {document.filename}')
# ... extraction operations ...
logger.log_event('WARNING', 'Keyword BGN not found in document')

logger.finalize('success', extraction_results)
print(f"Processing log saved to: {log_path}")
```

---

## Testing Checklist

- [ ] Output file generated with correct filename
- [ ] UTF-8 encoding preserved for Cyrillic text
- [ ] All sections present in output
- [ ] Timestamp formatted correctly
- [ ] Personal information formatted with masking (4 digits***)
- [ ] Keyword matches show page and line numbers
- [ ] "Not found" keywords displayed
- [ ] Warnings section populated correctly
- [ ] Errors section populated correctly
- [ ] File collision handled with timestamp
- [ ] Output folder not writable error caught
- [ ] Processing log contains all events
- [ ] Log file unique per extraction
- [ ] Summary statistics correct
- [ ] Windows line endings used
