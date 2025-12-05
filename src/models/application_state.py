"""ApplicationState model for runtime application state."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Union
from .document import Document
from .keyword import Keyword
from .extraction_results import ExtractionResults
from .batch_extraction_results import BatchExtractionResults


class ProcessingStatus(Enum):
    """Application processing states."""
    IDLE = 'idle'
    FILE_SELECTED = 'file_selected'
    READY = 'ready'
    PROCESSING = 'processing'
    COMPLETE = 'complete'
    ERROR = 'error'
    PARTIAL_SUCCESS = 'partial_success'


@dataclass
class ApplicationState:
    """Runtime application state (not persisted).

    Attributes:
        current_documents: Currently selected documents (batch support)
        active_keywords: Keywords selected for extraction
        processing_status: Current processing state
        extraction_results: Results of last extraction (single or batch)
        error_messages: Current session errors
        is_processing: Whether extraction is currently running
    """

    current_documents: list[Document] = field(default_factory=list)
    active_keywords: list[Keyword] = field(default_factory=list)
    processing_status: ProcessingStatus = ProcessingStatus.IDLE
    extraction_results: Union[ExtractionResults, BatchExtractionResults, None] = None
    error_messages: list[str] = field(default_factory=list)
    is_processing: bool = False

    @property
    def current_document(self) -> Document | None:
        """Get first document for backward compatibility.

        Returns:
            First document or None if no documents selected
        """
        return self.current_documents[0] if self.current_documents else None

    def can_start_extraction(self) -> bool:
        """Check if extraction can be started.

        Returns:
            True if ready to extract, False otherwise
        """
        has_valid_documents = (
            len(self.current_documents) > 0
            and all(doc.is_valid for doc in self.current_documents)
        )
        return (
            has_valid_documents
            and len(self.active_keywords) > 0
            and not self.is_processing
            and self.processing_status in (
                ProcessingStatus.READY,
                ProcessingStatus.COMPLETE,
                ProcessingStatus.ERROR,
                ProcessingStatus.PARTIAL_SUCCESS
            )
        )

    def set_document(self, document: Document) -> None:
        """Set current document and update state (backward compatibility).

        Args:
            document: Document to set as current
        """
        self.set_documents([document])

    def set_documents(self, documents: list[Document]) -> None:
        """Set current documents and update state.

        Args:
            documents: List of documents to set
        """
        self.current_documents = documents

        # Update status based on validity
        all_valid = all(doc.is_valid for doc in documents) if documents else False
        if all_valid and len(documents) > 0:
            if len(self.active_keywords) > 0:
                self.processing_status = ProcessingStatus.READY
            else:
                self.processing_status = ProcessingStatus.FILE_SELECTED
        else:
            self.processing_status = ProcessingStatus.ERROR
            for doc in documents:
                if not doc.is_valid and doc.error_message:
                    self.error_messages.append(doc.error_message)

    def add_keyword(self, keyword: Keyword) -> None:
        """Add keyword to active keywords.

        Args:
            keyword: Keyword to add
        """
        # Check for duplicate (case-insensitive)
        keyword_lower = keyword.normalized
        if not any(k.normalized == keyword_lower for k in self.active_keywords):
            self.active_keywords.append(keyword)

            # Update status if documents are selected
            has_valid_docs = (
                len(self.current_documents) > 0
                and all(doc.is_valid for doc in self.current_documents)
            )
            if (has_valid_docs
                    and self.processing_status == ProcessingStatus.FILE_SELECTED):
                self.processing_status = ProcessingStatus.READY

    def remove_keyword(self, keyword_text: str) -> None:
        """Remove keyword from active keywords.

        Args:
            keyword_text: Text of keyword to remove
        """
        keyword_lower = keyword_text.lower()
        self.active_keywords = [
            k for k in self.active_keywords
            if k.normalized != keyword_lower
        ]

        # Update status if no keywords left
        if len(self.active_keywords) == 0:
            if len(self.current_documents) > 0:
                self.processing_status = ProcessingStatus.FILE_SELECTED
            else:
                self.processing_status = ProcessingStatus.IDLE

    def clear_keywords(self) -> None:
        """Clear all active keywords."""
        self.active_keywords = []

        if len(self.current_documents) > 0:
            self.processing_status = ProcessingStatus.FILE_SELECTED
        else:
            self.processing_status = ProcessingStatus.IDLE

    def start_processing(self) -> None:
        """Mark processing as started."""
        self.is_processing = True
        self.processing_status = ProcessingStatus.PROCESSING
        self.error_messages = []
        self.extraction_results = None

    def complete_processing(self, results: Union[ExtractionResults, BatchExtractionResults]) -> None:
        """Mark processing as complete with results.

        Args:
            results: Extraction results (single or batch)
        """
        self.is_processing = False
        self.extraction_results = results

        # Determine status based on results type
        if isinstance(results, BatchExtractionResults):
            # Batch results
            if results.has_warnings and not results.has_results:
                self.processing_status = ProcessingStatus.ERROR
            elif results.has_warnings:
                self.processing_status = ProcessingStatus.PARTIAL_SUCCESS
            else:
                self.processing_status = ProcessingStatus.COMPLETE
        else:
            # Single extraction results
            if results.has_errors():
                if any(m.status == 'found' for m in results.matches):
                    self.processing_status = ProcessingStatus.PARTIAL_SUCCESS
                else:
                    self.processing_status = ProcessingStatus.ERROR
            else:
                self.processing_status = ProcessingStatus.COMPLETE

    def fail_processing(self, error_message: str) -> None:
        """Mark processing as failed.

        Args:
            error_message: Error message describing failure
        """
        self.is_processing = False
        self.processing_status = ProcessingStatus.ERROR
        self.error_messages.append(error_message)

    def reset(self) -> None:
        """Reset state to initial values."""
        self.current_documents = []
        self.active_keywords = []
        self.processing_status = ProcessingStatus.IDLE
        self.extraction_results = None
        self.error_messages = []
        self.is_processing = False
