"""ExtractionMatch model for keyword-number matches."""

from dataclasses import dataclass


@dataclass
class ExtractionMatch:
    """A single instance of a found keyword with its associated numerical value.

    Attributes:
        keyword: The matched keyword text
        value: Extracted numerical value (stored as string)
        page_number: Page where match was found (1-indexed)
        line_number: Line number within page (if available)
        status: Match status ('found', 'not_found', 'ambiguous')
        warning: Warning message if value is ambiguous
    """

    keyword: str
    value: str
    page_number: int
    line_number: int | None
    status: str
    warning: str | None = None

    def __post_init__(self):
        """Validate extraction match attributes after initialization."""
        # Validate status
        valid_statuses = ('found', 'not_found', 'ambiguous')
        if self.status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {self.status}. Must be one of {valid_statuses}"
            )

        # Validate page number
        if self.page_number < 1:
            raise ValueError(f"Page number must be >= 1, got: {self.page_number}")

        # Validate line number if present
        if self.line_number is not None and self.line_number < 1:
            raise ValueError(f"Line number must be >= 1, got: {self.line_number}")

        # Validate keyword is non-empty
        if not self.keyword or not self.keyword.strip():
            raise ValueError("Keyword must be non-empty")

        # Ensure value consistency with status
        if self.status == 'not_found' and self.value not in (None, 'Not found', ''):
            self.value = 'Not found'
