"""Keyword matcher for finding keywords in document text."""

import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.base import PageContent
from extractors.base import KeywordMatch


class KeywordMatcher:
    """Find keywords in document text.

    Features:
    - Case-insensitive matching
    - Find all occurrences (not just first)
    - Record page and line numbers
    - Unicode support for Cyrillic/Latin text
    """

    def find_keywords(self, pages: list[PageContent], keywords: list[str]) -> list[KeywordMatch]:
        """Find all keyword occurrences in document.

        Args:
            pages: Parsed document pages
            keywords: List of keywords to search for

        Returns:
            List of KeywordMatch with location information
        """
        matches = []

        for keyword in keywords:
            # Normalize keyword
            keyword_normalized = keyword.strip()

            # Escape special regex characters to prevent injection
            escaped_keyword = re.escape(keyword_normalized)

            # Create case-insensitive, Unicode-aware pattern
            # Use word boundaries to avoid partial matches
            pattern = re.compile(
                r'\b' + escaped_keyword + r'\b',
                re.IGNORECASE | re.UNICODE
            )

            # Search all pages
            for page in pages:
                for line_num, line_text in enumerate(page.lines, start=1):
                    # Find all matches in this line
                    if pattern.search(line_text):
                        matches.append(KeywordMatch(
                            keyword=keyword_normalized,
                            page_number=page.page_number,
                            line_number=line_num,
                            line_text=line_text
                        ))

        return matches
