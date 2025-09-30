# Parser Contract

**Component**: Document Parsers (PDFParser, DOCXParser)
**Purpose**: Extract text content from documents with page-level granularity

## Interface Definition

### DocumentParser (Abstract Base)

```python
class DocumentParser:
    """Abstract base class for document parsers"""

    def parse(self, file_path: str) -> ParseResult:
        """
        Parse document and extract text content

        Args:
            file_path: Absolute path to document file

        Returns:
            ParseResult with extracted content and metadata

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
            PasswordProtectedError: If PDF is password-protected
            ScannedPDFError: If PDF has no extractable text
            ParsingError: For other parsing failures
        """
        pass

    def validate(self, file_path: str) -> ValidationResult:
        """
        Validate document without full parsing

        Args:
            file_path: Absolute path to document file

        Returns:
            ValidationResult with is_valid flag and error message
        """
        pass

    def get_page_count(self, file_path: str) -> int:
        """
        Get number of pages in document

        Args:
            file_path: Absolute path to document file

        Returns:
            Number of pages (>= 1)

        Raises:
            ParsingError: If page count cannot be determined
        """
        pass
```

---

## Data Structures

### ParseResult

```python
@dataclass
class ParseResult:
    """Result of document parsing operation"""

    success: bool
    pages: list[PageContent]
    page_count: int
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)
```

### PageContent

```python
@dataclass
class PageContent:
    """Text content of a single page"""

    page_number: int  # 1-indexed
    text: str  # Full page text
    lines: list[str]  # Text split by line breaks
```

### ValidationResult

```python
@dataclass
class ValidationResult:
    """Result of document validation"""

    is_valid: bool
    error_type: str | None  # 'password_protected', 'scanned_pdf', 'corrupted', 'unsupported'
    error_message: str | None
```

---

## Implementations

### PDFParser

**Responsibilities**:
- Parse PDF documents using PyMuPDF (fitz)
- Extract text preserving page boundaries
- Detect password-protected PDFs
- Detect scanned PDFs (no extractable text)

**Behavior**:
- Opens PDF document using `fitz.open()`
- Iterates through pages sequentially
- Extracts text using `page.get_text("text")`
- Detects scanned PDFs: if first 3 pages have < 10 chars total
- Closes document after extraction

**Error Conditions**:
- Password-protected: Raise `PasswordProtectedError` with FR-052 message
- Scanned/OCR needed: Raise `ScannedPDFError` with FR-053 message
- Corrupted: Raise `ParsingError` with description
- Missing file: Raise `FileNotFoundError`

---

### DOCXParser

**Responsibilities**:
- Parse DOCX documents using python-docx
- Extract text maintaining paragraph structure
- Approximate page numbers using heuristics

**Behavior**:
- Opens document using `docx.Document()`
- Iterates through paragraphs
- Detects page breaks (section breaks, explicit page breaks)
- Approximates pages: ~500 words per page if no breaks
- Groups paragraphs into PageContent objects

**Error Conditions**:
- Corrupted DOCX: Raise `ParsingError`
- Missing file: Raise `FileNotFoundError`
- Invalid XML structure: Raise `ParsingError`

---

## Contract Guarantees

### Input Contracts

**parse()**:
- REQUIRES: `file_path` is absolute path to existing file
- REQUIRES: File extension is `.pdf` or `.docx`
- REQUIRES: File is readable

**validate()**:
- REQUIRES: `file_path` is absolute path
- ACCEPTS: Non-existent files (returns is_valid=False)

**get_page_count()**:
- REQUIRES: `file_path` is absolute path to valid, parseable document

---

### Output Contracts

**parse()**:
- ENSURES: If success=True, pages list is non-empty
- ENSURES: Page numbers are sequential starting from 1
- ENSURES: Text is UTF-8 compatible
- ENSURES: Lines are split on '\n' characters
- ENSURES: If success=False, error_message is populated

**validate()**:
- ENSURES: is_valid=False implies error_message is populated
- ENSURES: error_type is one of defined types or None

**get_page_count()**:
- ENSURES: Return value >= 1 for valid documents
- ENSURES: Raises exception for invalid documents

---

## Usage Example

```python
# Factory pattern for parser selection
parser = ParserFactory.create(file_path)  # Returns PDFParser or DOCXParser

# Validate before parsing
validation = parser.validate(file_path)
if not validation.is_valid:
    raise ExtractionError(validation.error_message)

# Parse document
result = parser.parse(file_path)
if not result.success:
    raise ParsingError(result.error_message)

# Process pages
for page in result.pages:
    print(f"Page {page.page_number}: {len(page.lines)} lines")
```

---

## Testing Checklist

- [ ] Valid PDF parsing extracts all pages correctly
- [ ] Valid DOCX parsing extracts all paragraphs
- [ ] Password-protected PDF raises PasswordProtectedError
- [ ] Scanned PDF raises ScannedPDFError
- [ ] Missing file raises FileNotFoundError
- [ ] Corrupted file raises ParsingError
- [ ] Unicode text (Cyrillic/Latin) preserved correctly
- [ ] Page numbers are 1-indexed and sequential
- [ ] Empty documents handled gracefully
- [ ] Large documents (50+ pages) parsed without memory issues
