"""PDF document parser using PyMuPDF (fitz)."""

import fitz  # PyMuPDF
from .base import (
    DocumentParser,
    ParseResult,
    PageContent,
    ValidationResult,
    ParsingError,
    PasswordProtectedError,
    ScannedPDFError
)


class PDFParser(DocumentParser):
    """Parse PDF documents using PyMuPDF (fitz).

    Features:
    - Extract text preserving page boundaries
    - Detect password-protected PDFs
    - Detect scanned PDFs (no extractable text)
    - UTF-8 encoding support for Cyrillic/Latin text
    """

    def parse(self, file_path: str) -> ParseResult:
        """Parse PDF and extract text content.

        Args:
            file_path: Absolute path to PDF file

        Returns:
            ParseResult with extracted pages

        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
            PasswordProtectedError: If PDF is password-protected (FR-052)
            ScannedPDFError: If PDF has no extractable text (FR-053)
            ParsingError: For other parsing failures
        """
        # Check file exists and is readable
        self._check_file_exists(file_path)

        try:
            # Open PDF document
            doc = fitz.open(file_path)

            # Check if password-protected
            if doc.is_encrypted:
                doc.close()
                raise PasswordProtectedError(
                    "Password-protected PDFs are not supported"
                )

            # Extract text from all pages
            pages = []
            warnings = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")

                # Split into lines
                lines = text.split('\n')

                pages.append(PageContent(
                    page_number=page_num + 1,  # 1-indexed
                    text=text,
                    lines=lines
                ))

            doc.close()

            # Check if scanned PDF (< 10 chars in first 3 pages)
            if len(pages) > 0:
                first_pages_text = ''.join(
                    p.text for p in pages[:3]
                )
                if len(first_pages_text.strip()) < 10:
                    raise ScannedPDFError(
                        "Scanned PDFs requiring OCR are not supported"
                    )

            # Check if empty
            if len(pages) == 0:
                warnings.append("Document has no pages")

            return ParseResult(
                success=True,
                pages=pages,
                page_count=len(pages),
                error_message=None,
                warnings=warnings
            )

        except PasswordProtectedError:
            raise
        except ScannedPDFError:
            raise
        except Exception as e:
            raise ParsingError(f"Failed to parse PDF: {str(e)}")

    def validate(self, file_path: str) -> ValidationResult:
        """Validate PDF without full parsing.

        Args:
            file_path: Absolute path to PDF file

        Returns:
            ValidationResult with validity status
        """
        try:
            # Check file exists
            self._check_file_exists(file_path)

            # Try to open document
            doc = fitz.open(file_path)

            # Check if password-protected
            if doc.is_encrypted:
                doc.close()
                return ValidationResult(
                    is_valid=False,
                    error_type='password_protected',
                    error_message='Password-protected PDFs are not supported'
                )

            # Check if scanned (sample first page)
            if len(doc) > 0:
                first_page_text = doc[0].get_text("text")
                if len(first_page_text.strip()) < 10:
                    # Check a couple more pages to be sure
                    total_text = first_page_text
                    for page_num in range(1, min(3, len(doc))):
                        total_text += doc[page_num].get_text("text")

                    if len(total_text.strip()) < 10:
                        doc.close()
                        return ValidationResult(
                            is_valid=False,
                            error_type='scanned_pdf',
                            error_message='Scanned PDFs requiring OCR are not supported'
                        )

            doc.close()

            return ValidationResult(
                is_valid=True,
                error_type=None,
                error_message=None
            )

        except FileNotFoundError:
            return ValidationResult(
                is_valid=False,
                error_type='file_not_found',
                error_message=f'File not found: {file_path}'
            )
        except PermissionError:
            return ValidationResult(
                is_valid=False,
                error_type='permission_denied',
                error_message=f'File is not readable: {file_path}'
            )
        except Exception as e:
            return ValidationResult(
                is_valid=False,
                error_type='corrupted',
                error_message=f'Failed to validate PDF: {str(e)}'
            )

    def get_page_count(self, file_path: str) -> int:
        """Get number of pages in PDF.

        Args:
            file_path: Absolute path to PDF file

        Returns:
            Number of pages (>= 1)

        Raises:
            ParsingError: If page count cannot be determined
        """
        try:
            self._check_file_exists(file_path)

            doc = fitz.open(file_path)
            page_count = len(doc)
            doc.close()

            return page_count

        except Exception as e:
            raise ParsingError(f"Failed to get page count: {str(e)}")
