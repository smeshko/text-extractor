"""PersonalInformation model for extracted identity data."""

from dataclasses import dataclass


@dataclass
class PersonalInformation:
    """Structured identity data extracted from document.

    Attributes:
        first_name: Extracted first name
        last_name: Extracted last name
        middle_name: Extracted middle name(s)
        id_number_prefix: First 4 digits of ID number
        age: Extracted age (from text after name, comma-separated)
        character_set: Character set detected ('cyrillic', 'latin', 'mixed', 'unknown')
        extraction_page: Page where information was found
        is_complete: Whether all fields were successfully extracted
    """

    first_name: str | None
    last_name: str | None
    middle_name: str | None
    id_number_prefix: str | None
    age: int | None
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

        # Validate age if present
        if self.age is not None:
            if not isinstance(self.age, int) or self.age < 0 or self.age > 150:
                raise ValueError(
                    f"Age must be between 0 and 150, got: {self.age}"
                )

        # Update is_complete based on field values
        self.is_complete = all([
            self.first_name is not None,
            self.last_name is not None,
            self.id_number_prefix is not None
        ])

    @property
    def full_name(self) -> str | None:
        """Combine all name parts into full name.

        Returns:
            Full name string or None if no name parts available

        Example:
            first_name="Иван", last_name="Петров" → "Иван Петров"
            first_name="Иван", middle_name="Йорданов", last_name="Тодоров"
                → "Иван Йорданов Тодоров"
        """
        name_parts = []
        if self.first_name:
            name_parts.append(self.first_name)
        if self.middle_name:
            name_parts.append(self.middle_name)
        if self.last_name:
            name_parts.append(self.last_name)

        return ' '.join(name_parts) if name_parts else None

    def get_abbreviated_name(self) -> str | None:
        """Generate abbreviated name from first letters.

        Returns:
            Uppercase abbreviated name or None if no full_name

        Example:
            "Иван Петров" → "ИП"
            "Иван Йорданов Тодоров" → "ИЙТ"
            "John" → "J"

        Rules:
            - Take first letter of each name part
            - Convert to uppercase
            - Preserve Cyrillic characters
            - Filter empty parts
        """
        if not self.full_name:
            return None

        parts = self.full_name.strip().split()
        return ''.join(part[0].upper() for part in parts if part)

    @classmethod
    def empty(cls):
        """Create an empty PersonalInformation instance with all fields as None.

        Returns:
            PersonalInformation with no extracted data
        """
        return cls(
            first_name=None,
            last_name=None,
            middle_name=None,
            id_number_prefix=None,
            age=None,
            character_set='unknown',
            extraction_page=None,
            is_complete=False
        )
