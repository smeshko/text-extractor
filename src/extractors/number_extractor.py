"""Number extractor for finding numerical values near keywords."""

import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from extractors.base import KeywordMatch
from models.extraction_match import ExtractionMatch


class NumberExtractor:
    """Extract numbers associated with keywords.

    Features:
    - US/UK number format (period decimal, comma thousands)
    - "Next number after keyword" proximity rule
    - Ambiguous format detection
    - Graceful handling of not found cases
    """

    # US/UK format: period decimal, optional comma thousands
    # Matches: 3, 3.5, 1,234, 1,234.56
    NUMBER_PATTERN = re.compile(r'\b\d{1,3}(?:,\d{3})*(?:\.\d+)?\b')

    def extract_numbers(self, keyword_matches: list[KeywordMatch]) -> list[ExtractionMatch]:
        """Extract numbers associated with keyword matches.

        Args:
            keyword_matches: Keywords found in document

        Returns:
            List of ExtractionMatch with numbers or 'Not found' status
        """
        extraction_matches = []

        for kw_match in keyword_matches:
            # Find keyword position in line
            keyword_lower = kw_match.keyword.lower()
            line_lower = kw_match.line_text.lower()

            # Escape keyword for regex
            escaped_keyword = re.escape(keyword_lower)

            # Find keyword position (case-insensitive)
            keyword_pattern = re.compile(r'\b' + escaped_keyword + r'\b', re.IGNORECASE)
            match_obj = keyword_pattern.search(kw_match.line_text)

            if not match_obj:
                # Keyword not found in line (shouldn't happen, but handle gracefully)
                extraction_matches.append(ExtractionMatch(
                    keyword=kw_match.keyword,
                    value='Not found',
                    page_number=kw_match.page_number,
                    line_number=kw_match.line_number,
                    status='not_found',
                    warning=None
                ))
                continue

            # Search for number after keyword in the line
            keyword_end = match_obj.end()
            text_after_keyword = kw_match.line_text[keyword_end:]

            # Find first number after keyword
            number_match = self.NUMBER_PATTERN.search(text_after_keyword)

            if number_match:
                value = number_match.group()

                # Check for ambiguous format
                warning = None
                status = 'found'

                # Ambiguous: contains comma but no decimal point (could be thousands or unusual)
                if ',' in value and '.' not in value:
                    # Check if it looks like thousands separator
                    # Pattern: X,XXX or X,XXX,XXX (proper thousands)
                    if re.match(r'^\d{1,3}(?:,\d{3})+$', value):
                        # Proper thousands format
                        warning = (
                            f"Number '{value}' interpreted as thousands separator. "
                            f"If this is incorrect, please review the document."
                        )
                        status = 'ambiguous'
                    else:
                        # Unusual format
                        warning = f"Number '{value}' has unusual format and may be ambiguous"
                        status = 'ambiguous'

                extraction_matches.append(ExtractionMatch(
                    keyword=kw_match.keyword,
                    value=value,
                    page_number=kw_match.page_number,
                    line_number=kw_match.line_number,
                    status=status,
                    warning=warning
                ))
            else:
                # No number found after keyword on same line
                extraction_matches.append(ExtractionMatch(
                    keyword=kw_match.keyword,
                    value='Not found',
                    page_number=kw_match.page_number,
                    line_number=kw_match.line_number,
                    status='not_found',
                    warning=None
                ))

        return extraction_matches
