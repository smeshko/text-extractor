"""Personal information extractor for identity data."""

import re
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from parsers.base import PageContent
from models.personal_information import PersonalInformation


class PersonalInfoExtractor:
    """Extract personal information from document.

    Features:
    - Cyrillic and Latin label support
    - First page priority with full document fallback
    - Character set detection
    - ID number: first 4 digits only
    """

    # First name patterns (Cyrillic and Latin labels)
    FIRST_NAME_PATTERNS = [
        re.compile(r'(?:First Name|Име|Name|Имя):\s*([А-Яа-яA-Za-z\s\-]+)', re.UNICODE),
        re.compile(r'(?:Given Name|Личное имя):\s*([А-Яа-яA-Za-z\s\-]+)', re.UNICODE),
    ]

    # Last name patterns
    LAST_NAME_PATTERNS = [
        re.compile(r'(?:Last Name|Фамилия|Surname|Фамилія):\s*([А-Яа-яA-Za-z\s\-]+)', re.UNICODE),
        re.compile(r'(?:Family Name):\s*([А-Яа-яA-Za-z\s\-]+)', re.UNICODE),
    ]

    # Middle name patterns
    MIDDLE_NAME_PATTERNS = [
        re.compile(r'(?:Middle Name|Отчество|Patronymic|По батькові):\s*([А-Яа-яA-Za-z\s\-]+)', re.UNICODE),
    ]

    # Age pattern: expects comma-separated format after name (e.g., "Name, 33")
    AGE_PATTERN = re.compile(r',\s*(\d{1,3})(?:\s|$)', re.UNICODE)

    # ID number pattern (extract first 4 digits only)
    ID_PATTERNS = [
        re.compile(r'(?:ID|ЕГН|ID Number|Номер):\s*(\d{4})\d*', re.UNICODE),
        re.compile(r'(?:Identification|Identifier):\s*(\d{4})\d*', re.UNICODE),
    ]

    def extract_personal_info(self, pages: list[PageContent]) -> PersonalInformation:
        """Extract personal information from document.

        Args:
            pages: Parsed document pages

        Returns:
            PersonalInformation with extracted fields or None values
        """
        if not pages:
            return PersonalInformation.empty()

        # Try first page first (most likely location)
        first_page = pages[0]
        result = self._extract_from_page(first_page)

        # If incomplete, search remaining pages
        if not result.is_complete and len(pages) > 1:
            for page in pages[1:]:
                if result.first_name is None:
                    first_name, fn_page = self._extract_first_name([page])
                    if first_name:
                        result.first_name = first_name
                        result.extraction_page = fn_page

                if result.last_name is None:
                    last_name, ln_page = self._extract_last_name([page])
                    if last_name:
                        result.last_name = last_name
                        if result.extraction_page is None:
                            result.extraction_page = ln_page

                if result.middle_name is None:
                    middle_name, mn_page = self._extract_middle_name([page])
                    if middle_name:
                        result.middle_name = middle_name
                        if result.extraction_page is None:
                            result.extraction_page = mn_page

                if result.id_number_prefix is None:
                    id_prefix, id_page = self._extract_id_number([page])
                    if id_prefix:
                        result.id_number_prefix = id_prefix
                        if result.extraction_page is None:
                            result.extraction_page = id_page

                if result.age is None:
                    age, age_page = self._extract_age([page])
                    if age:
                        result.age = age
                        if result.extraction_page is None:
                            result.extraction_page = age_page

                # Stop if complete
                if result.is_complete:
                    break

        # Detect character set from extracted names
        if result.first_name or result.last_name or result.middle_name:
            combined_text = f"{result.first_name or ''} {result.middle_name or ''} {result.last_name or ''}"
            result.character_set = self._detect_character_set(combined_text)

        # Update is_complete flag
        result.is_complete = all([
            result.first_name is not None,
            result.last_name is not None,
            result.id_number_prefix is not None
        ])

        return result

    def _extract_from_page(self, page: PageContent) -> PersonalInformation:
        """Extract all personal info from a single page.

        Args:
            page: Page to extract from

        Returns:
            PersonalInformation with extracted fields
        """
        first_name, _ = self._extract_first_name([page])
        last_name, _ = self._extract_last_name([page])
        middle_name, _ = self._extract_middle_name([page])
        id_prefix, _ = self._extract_id_number([page])
        age, _ = self._extract_age([page])

        character_set = 'unknown'
        if first_name or last_name or middle_name:
            combined = f"{first_name or ''} {middle_name or ''} {last_name or ''}"
            character_set = self._detect_character_set(combined)

        return PersonalInformation(
            first_name=first_name,
            last_name=last_name,
            middle_name=middle_name,
            id_number_prefix=id_prefix,
            age=age,
            character_set=character_set,
            extraction_page=page.page_number if (first_name or last_name or id_prefix) else None,
            is_complete=all([first_name, last_name, id_prefix])
        )

    def _extract_first_name(self, pages: list[PageContent]) -> tuple[str | None, int | None]:
        """Extract first name from pages.

        Returns:
            Tuple of (first_name, page_number) or (None, None)
        """
        for page in pages:
            page_text = page.text
            for pattern in self.FIRST_NAME_PATTERNS:
                match = pattern.search(page_text)
                if match:
                    name = match.group(1).strip()
                    return name, page.page_number
        return None, None

    def _extract_last_name(self, pages: list[PageContent]) -> tuple[str | None, int | None]:
        """Extract last name from pages.

        Returns:
            Tuple of (last_name, page_number) or (None, None)
        """
        for page in pages:
            page_text = page.text
            for pattern in self.LAST_NAME_PATTERNS:
                match = pattern.search(page_text)
                if match:
                    name = match.group(1).strip()
                    return name, page.page_number
        return None, None

    def _extract_middle_name(self, pages: list[PageContent]) -> tuple[str | None, int | None]:
        """Extract middle name from pages.

        Returns:
            Tuple of (middle_name, page_number) or (None, None)
        """
        for page in pages:
            page_text = page.text
            for pattern in self.MIDDLE_NAME_PATTERNS:
                match = pattern.search(page_text)
                if match:
                    name = match.group(1).strip()
                    return name, page.page_number
        return None, None

    def _extract_age(self, pages: list[PageContent]) -> tuple[int | None, int | None]:
        """Extract age from pages (comma-separated format after name).

        Looks for pattern: "Name, 33" or similar.

        Returns:
            Tuple of (age, page_number) or (None, None)
        """
        for page in pages:
            page_text = page.text
            match = self.AGE_PATTERN.search(page_text)
            if match:
                try:
                    age = int(match.group(1))
                    # Validate age range (0-150)
                    if 0 <= age <= 150:
                        return age, page.page_number
                except ValueError:
                    # Invalid age format, continue searching
                    pass
        return None, None

    def _extract_id_number(self, pages: list[PageContent]) -> tuple[str | None, int | None]:
        """Extract ID number (first 4 digits) from pages.

        Returns:
            Tuple of (id_prefix, page_number) or (None, None)
        """
        for page in pages:
            page_text = page.text
            for pattern in self.ID_PATTERNS:
                match = pattern.search(page_text)
                if match:
                    id_prefix = match.group(1)
                    return id_prefix, page.page_number
        return None, None

    def _detect_character_set(self, text: str) -> str:
        """Detect character set from text.

        Args:
            text: Text to analyze

        Returns:
            Character set: 'cyrillic', 'latin', 'mixed', or 'unknown'
        """
        has_cyrillic = bool(re.search(r'[А-Яа-я]', text))
        has_latin = bool(re.search(r'[A-Za-z]', text))

        if has_cyrillic and has_latin:
            return 'mixed'
        elif has_cyrillic:
            return 'cyrillic'
        elif has_latin:
            return 'latin'
        else:
            return 'unknown'
