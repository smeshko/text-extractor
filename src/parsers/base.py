"""Base classes and data structures for document parsers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


# Custom Exceptions
class ParsingError(Exception):
    """Base exception for parsing errors."""
    pass


class PasswordProtectedError(ParsingError):
    """Exception raised when PDF is password-protected."""
    pass


class ScannedPDFError(ParsingError):
    """Exception raised when PDF has no extractable text (scanned/OCR needed)."""
    pass


# Data Structures
@dataclass
class PageContent:
    """Text content of a single page.

    Attributes:
        page_number: Page number (1-indexed)
        text: Full page text
        lines: Text split by line breaks
    """

    page_number: int
    text: str
    lines: list[str]

    def __post_init__(self):
        """Validate page content after initialization."""
        if self.page_number < 1:
            raise ValueError(f"Page number must be >= 1, got: {self.page_number}")

        # Ensure lines are derived from text if not provided
        if not self.lines and self.text:
            self.lines = self.text.split('\n')


@dataclass
class ParseResult:
    """Result of document parsing operation.

    Attributes:
        success: Whether parsing succeeded
        pages: List of PageContent objects
        page_count: Total number of pages
        error_message: Error description if parsing failed
        warnings: List of warning messages
    """

    success: bool
    pages: list[PageContent]
    page_count: int
    error_message: str | None = None
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self):
        """Validate parse result after initialization."""
        if self.success and not self.pages:
            raise ValueError("Successful parse result must have non-empty pages list")

        if not self.success and not self.error_message:
            raise ValueError("Failed parse result must have error_message")

        if self.page_count < 0:
            raise ValueError(f"Page count must be >= 0, got: {self.page_count}")


@dataclass
class ValidationResult:
    """Result of document validation.

    Attributes:
        is_valid: Whether document is valid
        error_type: Type of error if invalid
        error_message: Error description if invalid
    """

    is_valid: bool
    error_type: str | None = None
    error_message: str | None = None

    def __post_init__(self):
        """Validate validation result after initialization."""
        if not self.is_valid and not self.error_message:
            raise ValueError("Invalid validation result must have error_message")


# Abstract Base Class
class DocumentParser(ABC):
    """Abstract base class for document parsers.

    Implementations must provide:
    - parse(): Extract text content from document
    - validate(): Check if document is valid without full parsing
    - get_page_count(): Get number of pages in document
    """

    @abstractmethod
    def parse(self, file_path: str) -> ParseResult:
        """Parse document and extract text content.

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

    @abstractmethod
    def validate(self, file_path: str) -> ValidationResult:
        """Validate document without full parsing.

        Args:
            file_path: Absolute path to document file

        Returns:
            ValidationResult with is_valid flag and error message
        """
        pass

    @abstractmethod
    def get_page_count(self, file_path: str) -> int:
        """Get number of pages in document.

        Args:
            file_path: Absolute path to document file

        Returns:
            Number of pages (>= 1)

        Raises:
            ParsingError: If page count cannot be determined
        """
        pass

    def _check_file_exists(self, file_path: str) -> None:
        """Check if file exists and is readable.

        Args:
            file_path: Path to check

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
        """
        import os

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.access(file_path, os.R_OK):
            raise PermissionError(f"File is not readable: {file_path}")

        if not os.path.isfile(file_path):
            raise ValueError(f"Path is not a file: {file_path}")
