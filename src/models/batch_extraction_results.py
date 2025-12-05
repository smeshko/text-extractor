"""BatchExtractionResults model for batch extraction operation results."""

from dataclasses import dataclass, field
from datetime import datetime
from .extraction_results import ExtractionResults


@dataclass
class BatchExtractionResults:
    """Container for results from multiple document extractions.

    Attributes:
        results: List of ExtractionResults from each document
        keywords: Keywords used for all documents in the batch
        timestamp: When batch extraction was performed
        output_path: Path to generated batch output file
        warnings: Batch-level warnings (e.g., skipped files)
    """

    results: list[ExtractionResults] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    output_path: str | None = None
    warnings: list[str] = field(default_factory=list)

    def add_result(self, result: ExtractionResults) -> None:
        """Add extraction result from a document.

        Args:
            result: ExtractionResults from a single document
        """
        self.results.append(result)

    def add_warning(self, message: str) -> None:
        """Add a batch-level warning.

        Args:
            message: Warning message
        """
        self.warnings.append(message)

    @property
    def document_count(self) -> int:
        """Get count of successfully processed documents.

        Returns:
            Number of documents with results
        """
        return len(self.results)

    @property
    def has_results(self) -> bool:
        """Check if any documents were successfully processed.

        Returns:
            True if at least one document has results
        """
        return len(self.results) > 0

    @property
    def has_warnings(self) -> bool:
        """Check if any batch-level warnings occurred.

        Returns:
            True if warnings exist
        """
        return len(self.warnings) > 0

    def has_errors(self) -> bool:
        """Check if batch had critical errors (no documents processed).

        Returns:
            True if no documents were successfully processed but warnings exist
        """
        return not self.results and len(self.warnings) > 0

    def get_total_processing_time(self) -> float:
        """Get total processing time for all documents.

        Returns:
            Sum of processing times in seconds
        """
        return sum(r.processing_time for r in self.results)

    def get_success_count(self) -> int:
        """Get count of documents with at least one successful extraction.

        Returns:
            Number of documents with found matches
        """
        return sum(1 for r in self.results if r.get_success_count() > 0)

    def get_status_summary(self) -> str:
        """Get human-readable status summary.

        Returns:
            Summary string of batch results
        """
        total = self.document_count
        success = self.get_success_count()
        warnings = len(self.warnings)

        parts = [f"{total} documents processed"]
        if success > 0:
            parts.append(f"{success} with matches")
        if warnings > 0:
            parts.append(f"{warnings} warnings")

        return ", ".join(parts)
