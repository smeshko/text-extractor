"""Parser factory for creating appropriate parser based on file type."""

import os
from .base import DocumentParser, ParsingError
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .doc_parser import DOCParser


class ParserFactory:
    """Factory for creating document parsers based on file extension.

    Supported formats:
    - PDF (.pdf)
    - DOCX (.docx)
    - DOC (.doc)
    """

    # Supported extensions mapped to parser classes
    PARSER_MAP = {
        '.pdf': PDFParser,
        '.docx': DOCXParser,
        '.doc': DOCParser,
    }

    @classmethod
    def create(cls, file_path: str) -> DocumentParser:
        """Create appropriate parser for the given file.

        Args:
            file_path: Path to document file

        Returns:
            DocumentParser instance (PDFParser, DOCXParser, or DOCParser)

        Raises:
            ValueError: If file extension is not supported
            FileNotFoundError: If file doesn't exist
        """
        # Check file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Extract extension (case-insensitive)
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()

        # Get parser class
        parser_class = cls.PARSER_MAP.get(ext)

        if parser_class is None:
            supported = ', '.join(cls.PARSER_MAP.keys())
            raise ValueError(
                f"Unsupported file type: '{ext}'. Supported types: {supported}"
            )

        # Instantiate and return parser
        return parser_class()

    @classmethod
    def is_supported(cls, file_path: str) -> bool:
        """Check if file type is supported.

        Args:
            file_path: Path to document file

        Returns:
            True if file type is supported, False otherwise
        """
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        return ext in cls.PARSER_MAP

    @classmethod
    def get_supported_extensions(cls) -> list[str]:
        """Get list of supported file extensions.

        Returns:
            List of supported extensions (e.g., ['.pdf', '.docx'])
        """
        return list(cls.PARSER_MAP.keys())

    @classmethod
    def get_file_filter(cls) -> str:
        """Get file filter string for file dialogs.

        Returns:
            File filter string (e.g., "PDF and DOCX files (*.pdf *.docx)")
        """
        patterns = [f"*{ext}" for ext in cls.PARSER_MAP.keys()]
        return f"Supported Documents ({' '.join(patterns)})"
