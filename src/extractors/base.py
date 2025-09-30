"""Base classes for extraction engines."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.base import PageContent
from models.extraction_results import ExtractionResults


@dataclass
class KeywordMatch:
    """Keyword found in document with location information.

    Attributes:
        keyword: The matched keyword text
        page_number: Page where keyword was found (1-indexed)
        line_number: Line number within page (1-indexed)
        line_text: Full line containing the keyword
    """

    keyword: str
    page_number: int
    line_number: int
    line_text: str

    def __post_init__(self):
        """Validate keyword match after initialization."""
        if self.page_number < 1:
            raise ValueError(f"Page number must be >= 1, got: {self.page_number}")

        if self.line_number < 1:
            raise ValueError(f"Line number must be >= 1, got: {self.line_number}")

        if not self.keyword:
            raise ValueError("Keyword must be non-empty")

        if not self.line_text:
            raise ValueError("Line text must be non-empty")


class ExtractionEngine(ABC):
    """Abstract base for extraction operations.

    Implementations must provide:
    - extract(): Extract all data from parsed document pages
    """

    @abstractmethod
    def extract(self, pages: list[PageContent], keywords: list[str]) -> ExtractionResults:
        """Extract data from parsed document pages.

        Args:
            pages: List of PageContent from parser
            keywords: List of keywords to search for

        Returns:
            ExtractionResults with all matches, personal info, errors, warnings
        """
        pass
