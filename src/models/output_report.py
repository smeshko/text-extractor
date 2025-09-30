"""OutputReport model for generated extraction output files."""

from dataclasses import dataclass
from .personal_information import PersonalInformation
from .extraction_match import ExtractionMatch


@dataclass
class OutputReport:
    """Plain text file containing all extraction results for a single document.

    Attributes:
        document_filename: Original document filename
        processing_timestamp: Date and time of extraction (ISO 8601 format)
        personal_info: Extracted personal information
        matches: All keyword-number matches
        errors: Collection of error messages
        warnings: Collection of warning messages
        output_path: Full path to generated output file
    """

    document_filename: str
    processing_timestamp: str
    personal_info: PersonalInformation
    matches: list[ExtractionMatch]
    errors: list[str]
    warnings: list[str]
    output_path: str

    def __post_init__(self):
        """Validate output report attributes after initialization."""
        if not self.document_filename:
            raise ValueError("Document filename must be non-empty")

        if not self.processing_timestamp:
            raise ValueError("Processing timestamp must be non-empty")

        if not self.output_path:
            raise ValueError("Output path must be non-empty")

    def get_filename_from_document(self, document_filename: str) -> str:
        """Generate output filename from document filename.

        Args:
            document_filename: Original document filename (with or without extension)

        Returns:
            Output filename in format: output_[original_filename].txt
        """
        # Remove extension if present
        if '.' in document_filename:
            base_name = document_filename.rsplit('.', 1)[0]
        else:
            base_name = document_filename

        return f"output_{base_name}.txt"

    def has_errors(self) -> bool:
        """Check if the report contains any errors.

        Returns:
            True if errors exist, False otherwise
        """
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if the report contains any warnings.

        Returns:
            True if warnings exist, False otherwise
        """
        return len(self.warnings) > 0

    def get_success_status(self) -> str:
        """Get overall success status of extraction.

        Returns:
            'complete' if no errors, 'partial_success' if some errors, 'error' if all failed
        """
        if not self.has_errors():
            return 'complete'

        # Check if any matches were successful
        successful_matches = [m for m in self.matches if m.status == 'found']
        if successful_matches:
            return 'partial_success'

        return 'error'
