"""ExtractionResults model for extraction operation results."""

from dataclasses import dataclass, field
from datetime import datetime
from .document import Document
from .personal_information import PersonalInformation
from .extraction_match import ExtractionMatch


@dataclass
class ExtractionResults:
    """Container for all results from a single extraction operation.

    Attributes:
        document: Processed document reference
        personal_info: Extracted personal data
        matches: All keyword matches
        errors: Structured error collection
        warnings: Warning messages
        processing_time: Seconds taken for extraction
        timestamp: When extraction was performed
    """

    document: Document
    personal_info: PersonalInformation
    matches: list[ExtractionMatch] = field(default_factory=list)
    errors: list[dict] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    processing_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def add_match(self, match: ExtractionMatch) -> None:
        """Add successful extraction match.

        Args:
            match: ExtractionMatch to add
        """
        self.matches.append(match)

    def add_error(self, error_type: str, message: str, context: dict | None = None) -> None:
        """Add error with context.

        Args:
            error_type: Type of error ('keyword_not_found', 'parsing_error', etc.)
            message: Human-readable error description
            context: Additional context data
        """
        error = {
            'type': error_type,
            'message': message,
            'context': context or {}
        }
        self.errors.append(error)

    def add_warning(self, message: str) -> None:
        """Add warning message.

        Args:
            message: Warning message
        """
        self.warnings.append(message)

    def has_errors(self) -> bool:
        """Check if any errors occurred.

        Returns:
            True if errors exist, False otherwise
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if any warnings occurred.

        Returns:
            True if warnings exist, False otherwise
        """
        return len(self.warnings) > 0

    def get_error_summary(self) -> str:
        """Get human-readable error summary.

        Returns:
            Formatted error summary string
        """
        if not self.has_errors():
            return "No errors"

        error_lines = []
        for error in self.errors:
            error_lines.append(f"- {error['message']}")

        return '\n'.join(error_lines)

    def is_complete(self) -> bool:
        """Check if all extractions were attempted.

        Returns:
            True if processing completed (with or without errors), False if interrupted
        """
        # If we have matches or errors, processing completed
        return len(self.matches) > 0 or len(self.errors) > 0

    def get_success_count(self) -> int:
        """Get count of successful extractions.

        Returns:
            Number of matches with status 'found'
        """
        return sum(1 for m in self.matches if m.status == 'found')

    def get_not_found_count(self) -> int:
        """Get count of keywords not found.

        Returns:
            Number of matches with status 'not_found'
        """
        return sum(1 for m in self.matches if m.status == 'not_found')

    def get_ambiguous_count(self) -> int:
        """Get count of ambiguous matches.

        Returns:
            Number of matches with status 'ambiguous'
        """
        return sum(1 for m in self.matches if m.status == 'ambiguous')

    def get_status_summary(self) -> str:
        """Get human-readable status summary.

        Returns:
            Summary string of extraction results
        """
        total = len(self.matches)
        success = self.get_success_count()
        not_found = self.get_not_found_count()
        ambiguous = self.get_ambiguous_count()

        parts = []
        if success > 0:
            parts.append(f"{success} successful")
        if not_found > 0:
            parts.append(f"{not_found} not found")
        if ambiguous > 0:
            parts.append(f"{ambiguous} ambiguous")

        return f"Total: {total} ({', '.join(parts)})"

    @classmethod
    def create(cls, document: Document):
        """Create new extraction results for a document.

        Args:
            document: Document being processed

        Returns:
            ExtractionResults instance
        """
        return cls(
            document=document,
            personal_info=PersonalInformation.empty(),
            matches=[],
            errors=[],
            warnings=[],
            processing_time=0.0,
            timestamp=datetime.now()
        )
