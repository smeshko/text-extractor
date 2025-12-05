## TASK-001: Batch Extraction Results Model

---
**Status:** COMPLETE
**Branch:** feature/multi-file-table-output
**Type:** IMPLEMENTATION
**Phase:** 1
**Depends On:** None
---

### Overview

Create data structures for batch processing: a `BatchExtractionResults` model to aggregate results from multiple documents, and update `ApplicationState` to store a list of documents instead of a single document.

**Files:**
- `src/models/batch_extraction_results.py` (create)
- `src/models/application_state.py` (modify)

### Implementation Steps

**Commit 1: Add batch extraction results model and update state**
- [x] Create `src/models/batch_extraction_results.py` with `BatchExtractionResults` dataclass
- [x] Add fields: `results: list[ExtractionResults]`, `timestamp: datetime`, `output_path: str | None`
- [x] Add helper methods: `add_result()`, `get_all_keywords()`, `document_count`
- [x] Update `ApplicationState.current_document` to `current_documents: list[Document]`
- [x] Add backward-compatible property `current_document` returning first item or None
- [x] Update `__init__.py` exports if needed

### Code Example

```python
# Pattern from existing ExtractionResults model
# src/models/extraction_results.py:10-34

@dataclass
class ExtractionResults:
    """Container for all results from a single extraction operation."""
    document: Document
    personal_info: PersonalInformation
    matches: list[ExtractionMatch] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)
    output_path: str | None = None

# New BatchExtractionResults follows same pattern:
@dataclass
class BatchExtractionResults:
    """Container for results from multiple document extractions."""
    results: list[ExtractionResults] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    output_path: str | None = None

    def add_result(self, result: ExtractionResults) -> None:
        self.results.append(result)

    @property
    def document_count(self) -> int:
        return len(self.results)
```

### Success Criteria

- [ ] Build succeeds with no errors
- [ ] `BatchExtractionResults` can store multiple `ExtractionResults`
- [ ] `ApplicationState.current_documents` holds list of documents
- [ ] Backward compatibility: `current_document` property works

### Verification

```bash
cd src && python -c "from models.batch_extraction_results import BatchExtractionResults; print('OK')"
cd src && python -c "from models.application_state import ApplicationState; print('OK')"
```

### Notes

- Keep the model simple - it's primarily a container
- The `keywords` field stores the keyword list used for all documents (same keywords for batch)
