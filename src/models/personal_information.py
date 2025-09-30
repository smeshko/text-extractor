"""PersonalInformation model for extracted identity data."""

from dataclasses import dataclass


@dataclass
class PersonalInformation:
    """Structured identity data extracted from document.

    Attributes:
        first_name: Extracted first name
        last_name: Extracted last name
        id_number_prefix: First 4 digits of ID number
        character_set: Character set detected ('cyrillic', 'latin', 'mixed', 'unknown')
        extraction_page: Page where information was found
        is_complete: Whether all fields were successfully extracted
    """

    first_name: str | None
    last_name: str | None
    id_number_prefix: str | None
    character_set: str
    extraction_page: int | None
    is_complete: bool

    def __post_init__(self):
        """Validate personal information attributes after initialization."""
        # Validate character set
        valid_character_sets = ('cyrillic', 'latin', 'mixed', 'unknown')
        if self.character_set not in valid_character_sets:
            raise ValueError(
                f"Invalid character_set: {self.character_set}. "
                f"Must be one of {valid_character_sets}"
            )

        # Validate extraction page if present
        if self.extraction_page is not None and self.extraction_page < 1:
            raise ValueError(
                f"Extraction page must be >= 1, got: {self.extraction_page}"
            )

        # Validate ID prefix format if present
        if self.id_number_prefix is not None:
            if len(self.id_number_prefix) != 4 or not self.id_number_prefix.isdigit():
                raise ValueError(
                    f"ID number prefix must be exactly 4 digits, "
                    f"got: '{self.id_number_prefix}'"
                )

        # Update is_complete based on field values
        self.is_complete = all([
            self.first_name is not None,
            self.last_name is not None,
            self.id_number_prefix is not None
        ])

    @classmethod
    def empty(cls):
        """Create an empty PersonalInformation instance with all fields as None.

        Returns:
            PersonalInformation with no extracted data
        """
        return cls(
            first_name=None,
            last_name=None,
            id_number_prefix=None,
            character_set='unknown',
            extraction_page=None,
            is_complete=False
        )
