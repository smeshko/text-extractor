"""Extraction engine orchestrating all extractors."""

import sys
import os
from datetime import datetime
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.base import PageContent
from extractors.base import ExtractionEngine as BaseEngine
from extractors.keyword_matcher import KeywordMatcher
from extractors.number_extractor import NumberExtractor
from extractors.personal_info_extractor import PersonalInfoExtractor
from models.extraction_results import ExtractionResults
from models.document import Document


class ExtractionEngine(BaseEngine):
    """Orchestrates all extraction operations.

    Flow:
    1. KeywordMatcher finds all keyword occurrences
    2. NumberExtractor finds numbers associated with keywords
    3. PersonalInfoExtractor finds personal information
    4. Combine into ExtractionResults with error collection
    """

    def __init__(self):
        """Initialize extraction engine with component extractors."""
        self.keyword_matcher = KeywordMatcher()
        self.number_extractor = NumberExtractor()
        self.personal_info_extractor = PersonalInfoExtractor()

    def extract(self, pages: list[PageContent], keywords: list[str],
                document: Document | None = None) -> ExtractionResults:
        """Extract data from parsed document pages.

        Args:
            pages: List of PageContent from parser
            keywords: List of keywords to search for
            document: Optional Document reference

        Returns:
            ExtractionResults with all matches, personal info, errors, warnings
        """
        start_time = time.time()

        # Create results container
        if document:
            results = ExtractionResults.create(document)
        else:
            # Create minimal document if not provided (should not happen in normal flow)
            # Use a placeholder absolute path to satisfy validation
            from models.document import Document as DocModel
            from pathlib import Path
            temp_doc = DocModel(
                file_path=str(Path.cwd() / 'unknown'),
                filename='unknown',
                file_type='pdf',
                page_count=len(pages),
                is_valid=True
            )
            results = ExtractionResults.create(temp_doc)

        try:
            # Step 1: Find keyword occurrences
            keyword_matches = []
            try:
                keyword_matches = self.keyword_matcher.find_keywords(pages, keywords)
            except Exception as e:
                results.add_error(
                    'keyword_matching_error',
                    f'Failed to match keywords: {str(e)}',
                    {'keywords': keywords}
                )

            # Step 2: Extract numbers for each keyword match
            try:
                extraction_matches = self.number_extractor.extract_numbers(keyword_matches)

                # Create a lookup of found matches by keyword
                matches_by_keyword = {}
                for match in extraction_matches:
                    if match.keyword not in matches_by_keyword:
                        matches_by_keyword[match.keyword] = []
                    matches_by_keyword[match.keyword].append(match)

                # Add matches in the original keyword order
                for keyword in keywords:
                    if keyword in matches_by_keyword:
                        # Add all matches for this keyword (in case of multiple matches)
                        for match in matches_by_keyword[keyword]:
                            results.add_match(match)

                            # Add warnings for ambiguous matches
                            if match.warning:
                                results.add_warning(match.warning)
                    else:
                        # Keyword not found - create "not found" entry
                        from models.extraction_match import ExtractionMatch
                        results.add_match(ExtractionMatch(
                            keyword=keyword,
                            value='Not found',
                            page_number=1,
                            line_number=None,
                            status='not_found',
                            warning=None
                        ))

            except Exception as e:
                results.add_error(
                    'number_extraction_error',
                    f'Failed to extract numbers: {str(e)}',
                    {}
                )

            # Step 3: Extract personal information
            try:
                personal_info = self.personal_info_extractor.extract_personal_info(pages)
                results.personal_info = personal_info

                # Add warnings for missing personal info fields
                if not personal_info.first_name:
                    results.add_warning('First name not found in document')
                # Last name warning disabled - often gives false positives
                # if not personal_info.last_name:
                #     results.add_warning('Last name not found in document')
                if not personal_info.id_number_prefix:
                    results.add_warning('ID number not found in document')

            except Exception as e:
                results.add_error(
                    'personal_info_extraction_error',
                    f'Failed to extract personal information: {str(e)}',
                    {}
                )
                # Use empty personal info
                from models.personal_information import PersonalInformation
                results.personal_info = PersonalInformation.empty()

        except Exception as e:
            # Catch-all for unexpected errors
            results.add_error(
                'extraction_error',
                f'Unexpected error during extraction: {str(e)}',
                {}
            )

        # Calculate processing time
        end_time = time.time()
        results.processing_time = end_time - start_time
        results.timestamp = datetime.now()

        return results
