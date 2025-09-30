# Extractor Contract

**Component**: Extraction Engines (KeywordMatcher, NumberExtractor, PersonalInfoExtractor)
**Purpose**: Extract keyword-number matches and personal information from parsed text

## Interface Definition

### ExtractionEngine (Abstract Base)

```python
class ExtractionEngine:
    """Abstract base for extraction operations"""

    def extract(self, pages: list[PageContent], keywords: list[str]) -> ExtractionResults:
        """
        Extract data from parsed document pages

        Args:
            pages: List of PageContent from parser
            keywords: List of keywords to search for

        Returns:
            ExtractionResults with all matches, personal info, errors, warnings
        """
        pass
```

---

## Data Structures

### ExtractionResults

```python
@dataclass
class ExtractionResults:
    """Results of extraction operation"""

    matches: list[ExtractionMatch]
    personal_info: PersonalInformation
    errors: list[dict]
    warnings: list[str]
    processing_time: float
    timestamp: datetime

    def add_match(self, match: ExtractionMatch) -> None:
        """Add successful extraction match"""

    def add_error(self, error_type: str, message: str, context: dict) -> None:
        """Add error with context"""

    def add_warning(self, message: str) -> None:
        """Add warning message"""

    def has_errors(self) -> bool:
        """Check if any errors occurred"""

    def has_warnings(self) -> bool:
        """Check if any warnings occurred"""

    def get_error_summary(self) -> str:
        """Get human-readable error summary"""
```

### ExtractionMatch

```python
@dataclass
class ExtractionMatch:
    """Single keyword-number match"""

    keyword: str
    value: str  # Numeric value as string
    page_number: int
    line_number: int | None
    status: str  # 'found', 'not_found', 'ambiguous'
    warning: str | None = None
```

### PersonalInformation

```python
@dataclass
class PersonalInformation:
    """Extracted personal identity data"""

    first_name: str | None
    last_name: str | None
    id_number_prefix: str | None  # First 4 digits
    character_set: str  # 'cyrillic', 'latin', 'mixed', 'unknown'
    extraction_page: int | None
    is_complete: bool
```

---

## Implementations

### KeywordMatcher

**Responsibilities**:
- Search for keywords in document text (case-insensitive)
- Find all occurrences of each keyword (FR-014)
- Record page and line numbers for each match

**Method Signature**:
```python
def find_keywords(self, pages: list[PageContent], keywords: list[str]) -> list[KeywordMatch]:
    """
    Find all keyword occurrences in document

    Args:
        pages: Parsed document pages
        keywords: List of keywords to search for

    Returns:
        List of KeywordMatch with location information
    """
```

**KeywordMatch Structure**:
```python
@dataclass
class KeywordMatch:
    """Keyword found in document"""

    keyword: str
    page_number: int
    line_number: int
    line_text: str  # Full line containing keyword
```

**Behavior**:
- Normalize keywords: lowercase, strip whitespace
- Create case-insensitive regex: `re.compile(re.escape(keyword), re.IGNORECASE | re.UNICODE)`
- Search each line of each page
- Record all matches (not just first)
- Use word boundaries to avoid partial matches (configurable)

**Error Handling**:
- If keyword not found in document: No error, return empty list
- Invalid regex patterns: Sanitize user input with `re.escape()`

---

### NumberExtractor

**Responsibilities**:
- Extract numerical values associated with keywords
- Use "next number after keyword" proximity rule (FR-015)
- Support US/UK number format (period decimal, comma thousands)
- Detect and flag ambiguous formats

**Method Signature**:
```python
def extract_numbers(self, keyword_matches: list[KeywordMatch]) -> list[ExtractionMatch]:
    """
    Extract numbers associated with keyword matches

    Args:
        keyword_matches: Keywords found in document

    Returns:
        List of ExtractionMatch with numbers or 'Not found' status
    """
```

**Number Format Pattern**:
```python
# US/UK format: period decimal, optional comma thousands
number_pattern = r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b'

# Matches:
# - Integers: 3, 42, 1234
# - Decimals: 3.5, 0.25
# - Thousands: 1,234, 1,234.56
# - Does NOT match: 3,5 (European format)
```

**Behavior**:
- For each KeywordMatch, search line_text after keyword
- Extract first number matching pattern
- If no number on same line, continue to next line (configurable distance)
- Store as string to preserve format
- Flag ambiguous: "3,500" could be 3.5 or 3500 (warn but interpret as 3500)

**Error Handling**:
- No number found after keyword: Create match with status='not_found', value='Not found'
- Ambiguous format: Create match with status='ambiguous', add warning
- Invalid number format: Add warning, attempt best-guess extraction

---

### PersonalInfoExtractor

**Responsibilities**:
- Extract first name, last name, ID number from labeled fields
- Support Cyrillic and Latin character sets
- Search first page primarily, fall back to full document
- Handle mixed scripts

**Method Signature**:
```python
def extract_personal_info(self, pages: list[PageContent]) -> PersonalInformation:
    """
    Extract personal information from document

    Args:
        pages: Parsed document pages

    Returns:
        PersonalInformation with extracted fields or None values
    """
```

**Pattern Definitions**:
```python
# First name patterns (Cyrillic or Latin labels)
FIRST_NAME_PATTERNS = [
    r'(?:First Name|Име|Name|Имя):\s*([А-Яа-яA-Za-z\s\-]+)',
    r'(?:Given Name|Личное имя):\s*([А-Яа-яA-Za-z\s\-]+)',
]

# Last name patterns
LAST_NAME_PATTERNS = [
    r'(?:Last Name|Фамилия|Surname|Фамилія):\s*([А-Яа-яA-Za-z\s\-]+)',
    r'(?:Family Name):\s*([А-Яа-яA-Za-z\s\-]+)',
]

# ID number pattern (extract first 4 digits only)
ID_PATTERNS = [
    r'(?:ID|ЕГН|ID Number|Номер):\s*(\d{4})\d*',
    r'(?:Identification|Identifier):\s*(\d{4})\d*',
]
```

**Behavior**:
- Try each pattern on first page first
- If not found, search remaining pages
- Stop on first successful match for each field
- Detect character set: check if Cyrillic characters present
- Trim whitespace from extracted values
- Handle mixed scripts: both Cyrillic and Latin in same field

**Field Detection**:
- First name: Try all FIRST_NAME_PATTERNS, return first match
- Last name: Try all LAST_NAME_PATTERNS, return first match
- ID: Try all ID_PATTERNS, extract exactly 4 digits (ignore remaining)

**Character Set Detection**:
```python
def detect_character_set(text: str) -> str:
    has_cyrillic = bool(re.search(r'[А-Яа-я]', text))
    has_latin = bool(re.search(r'[A-Za-z]', text))

    if has_cyrillic and has_latin:
        return 'mixed'
    elif has_cyrillic:
        return 'cyrillic'
    elif has_latin:
        return 'latin'
    else:
        return 'unknown'
```

**Error Handling**:
- Field not found: Set field to None, mark is_complete=False
- No personal info found: Return PersonalInformation with all None fields
- Multiple matches: Use first match only
- Invalid pattern: Add warning, continue with other patterns

---

## Contract Guarantees

### Input Contracts

**extract()**:
- REQUIRES: `pages` list is non-empty
- REQUIRES: Each PageContent has valid page_number >= 1
- REQUIRES: `keywords` list contains valid, non-empty strings

**find_keywords()**:
- REQUIRES: Same as extract()

**extract_numbers()**:
- REQUIRES: `keyword_matches` contains valid KeywordMatch objects

**extract_personal_info()**:
- REQUIRES: `pages` list is non-empty

---

### Output Contracts

**find_keywords()**:
- ENSURES: Returns empty list if no matches found (not an error)
- ENSURES: All KeywordMatch objects have valid page/line numbers
- ENSURES: line_text is non-empty

**extract_numbers()**:
- ENSURES: Returns ExtractionMatch for each KeywordMatch (even if not found)
- ENSURES: If status='found', value is valid number string
- ENSURES: If status='not_found', value is 'Not found'
- ENSURES: If status='ambiguous', warning is populated

**extract_personal_info()**:
- ENSURES: Always returns PersonalInformation object
- ENSURES: If field is None, is_complete=False
- ENSURES: character_set is one of defined values
- ENSURES: If extraction_page is set, it's valid (>= 1)

---

## Usage Example

```python
# Parse document
parser = ParserFactory.create(file_path)
parse_result = parser.parse(file_path)

# Create extraction engine
extractor = ExtractionEngine()

# Extract all data
results = extractor.extract(parse_result.pages, keywords=['HTD', 'RTP', 'BGN'])

# Access results
for match in results.matches:
    if match.status == 'found':
        print(f"{match.keyword}: {match.value} (Page {match.page_number})")
    elif match.status == 'not_found':
        print(f"{match.keyword}: Not found")

print(f"Name: {results.personal_info.first_name} {results.personal_info.last_name}")
print(f"ID: {results.personal_info.id_number_prefix}***")

if results.has_warnings():
    print(f"Warnings: {', '.join(results.warnings)}")
```

---

## Extraction Pipeline

```
1. KeywordMatcher.find_keywords()
   → List of KeywordMatch (keyword locations)

2. NumberExtractor.extract_numbers(keyword_matches)
   → List of ExtractionMatch (keyword + number + location)

3. PersonalInfoExtractor.extract_personal_info(pages)
   → PersonalInformation (name, ID)

4. Combine into ExtractionResults
   → Add matches, personal_info, errors, warnings
```

---

## Testing Checklist

- [ ] Case-insensitive keyword matching works
- [ ] All keyword occurrences found (not just first)
- [ ] Numbers extracted correctly (integers, decimals, thousands)
- [ ] "Not found" status when keyword exists but no number follows
- [ ] "Not found" status when keyword doesn't exist
- [ ] Ambiguous numbers flagged with warning
- [ ] Personal info extracted from Cyrillic labels
- [ ] Personal info extracted from Latin labels
- [ ] Mixed Cyrillic/Latin names handled
- [ ] ID number: only first 4 digits extracted
- [ ] Missing personal info fields marked as None
- [ ] First page searched first, then full document
- [ ] Multiple same keywords on same page handled
- [ ] Page and line numbers recorded correctly
- [ ] Unicode text preserved throughout extraction
