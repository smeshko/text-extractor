## TASK-003: Batch Processing Controller Logic

---
**Status:** COMPLETE
**Branch:** feature/multi-file-table-output
**Type:** IMPLEMENTATION
**Phase:** 1
**Depends On:** TASK-001, TASK-002
---

### Overview

Update AppController to handle multiple file selection and process documents in a batch loop. Aggregate results into BatchExtractionResults.

**Files:**
- `src/controllers/app_controller.py` (modify)
- `src/controllers/state_manager.py` (modify)

### Implementation Steps

**Commit 1: Implement batch processing in AppController**
- [x] Rename `on_file_selected()` to `on_files_selected(file_paths: list[str])`
- [x] Create and validate Document for each file path
- [x] Update `state_manager.set_document()` to `set_documents(documents: list[Document])`
- [x] Update `_perform_extraction()` to loop through all documents
- [x] Create `BatchExtractionResults` and add each `ExtractionResults` to it
- [x] Update progress reporting: "Processing file 2 of 5..."
- [x] Handle errors per document: skip failed document, continue processing others
- [x] Return `BatchExtractionResults` instead of single `ExtractionResults`

### Code Example

```python
# Current single-file extraction
# src/controllers/app_controller.py:429-487

def _perform_extraction(self, document: Document, keywords: list[Keyword]):
    """Perform extraction in worker thread."""
    parser = ParserFactory.create(document.file_path)
    parse_result = parser.parse(document.file_path)
    extraction_engine = ExtractionEngine()
    keyword_texts = [kw.text for kw in keywords]
    results = extraction_engine.extract(parse_result.pages, keyword_texts, document)
    output_result = self.output_generator.generate(results, self.config)
    return results

# New batch extraction:
def _perform_batch_extraction(self, documents: list[Document], keywords: list[Keyword]):
    """Perform extraction for multiple documents in worker thread."""
    reporter = ProgressReporter(self.thread_coordinator)
    batch_results = BatchExtractionResults(keywords=[kw.text for kw in keywords])

    for i, document in enumerate(documents):
        reporter.report(f'Processing file {i+1} of {len(documents)}: {document.filename}')
        try:
            parser = ParserFactory.create(document.file_path)
            parse_result = parser.parse(document.file_path)
            if not parse_result.success:
                batch_results.add_warning(f"Failed to parse: {document.filename}")
                continue

            extraction_engine = ExtractionEngine()
            keyword_texts = [kw.text for kw in keywords]
            results = extraction_engine.extract(parse_result.pages, keyword_texts, document)
            batch_results.add_result(results)

        except Exception as e:
            batch_results.add_warning(f"Error processing {document.filename}: {e}")

    # Generate batch output
    output_result = self.output_generator.generate_batch(batch_results, self.config)
    batch_results.output_path = output_result.output_path

    return batch_results
```

### Success Criteria

- [ ] Build succeeds with no errors
- [ ] Multiple documents are processed sequentially
- [ ] Progress shows current file number and name
- [ ] Failed documents don't stop batch processing
- [ ] All results aggregated into BatchExtractionResults
- [ ] Single file still works (batch of 1)

### Verification

```bash
cd src && python -c "from controllers.app_controller import AppController; print('OK')"
# Manual: Select 3 files, click Extract, verify all processed
```

### Notes

- Keep `on_extract_clicked()` similar but call `_perform_batch_extraction()`
- Error handling per document is important - don't fail entire batch
- Consider memory: process one document at a time, don't hold all parsed content
