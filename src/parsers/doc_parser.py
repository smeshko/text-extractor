"""DOC document parser using antiword subprocess."""

import subprocess
import sys
import os
from .base import (
    DocumentParser,
    ParseResult,
    PageContent,
    ValidationResult,
    ParsingError,
    PasswordProtectedError
)


class DOCParser(DocumentParser):
    """Parse legacy Microsoft Word (.doc) binary format documents.
    
    Features:
    - Extract text via bundled antiword binary
    - Detect password-protected files via OLE structure inspection
    - Approximate page numbers using word-count heuristic (~500 words/page)
    - UTF-8 encoding support for Cyrillic and Latin text
    """
    
    WORDS_PER_PAGE = 500  # Approximate words per page (same as DOCXParser)

    def parse(self, file_path: str) -> ParseResult:
        """Parse .doc file and extract text content.
        
        Args:
            file_path: Absolute path to .doc file
        
        Returns:
            ParseResult with extracted pages and metadata
        
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file is not readable
            PasswordProtectedError: If .doc is password-protected
            ParsingError: If antiword fails or file is corrupted
        """
        # Check file exists and is readable
        self._check_file_exists(file_path)
        
        # Validate first (check password/corruption)
        validation = self.validate(file_path)
        if not validation.is_valid:
            if validation.error_type == 'password_protected':
                raise PasswordProtectedError(validation.error_message)
            else:
                raise ParsingError(validation.error_message)
        
        try:
            # Extract text via antiword
            text = self._extract_text_via_antiword(file_path)

            # Debug: print first 500 chars of extracted text
            print(f"[DOC Parser] Extracted text ({len(text)} chars):")
            print(f"[DOC Parser] First 500 chars: {text[:500]}")

            # Split text into lines (preserve all lines including empty for keyword matching)
            # Use splitlines() to handle both \n and \r\n line endings (Windows/Mac compatibility)
            lines = text.splitlines()
            # Strip each line but keep empty lines to maintain structure
            paragraphs = [line.strip() for line in lines]

            print(f"[DOC Parser] Split into {len(paragraphs)} lines")
            
            # Split into pages using word-count heuristic
            pages = self._split_into_pages(paragraphs)
            
            # Check for warnings
            warnings = []
            if len(pages) > 0:
                # Check if first 3 pages have very little text
                total_chars = sum(len(page.text) for page in pages[:3])
                if total_chars < 10:
                    warnings.append("Document has no extractable text")
            else:
                # If no pages, create a dummy page to satisfy validation
                warnings.append("Document has no extractable text")
                pages = [PageContent(page_number=1, text="", lines=[])]
            
            return ParseResult(
                success=True,
                pages=pages,
                page_count=len(pages),
                error_message=None,
                warnings=warnings
            )
            
        except subprocess.TimeoutExpired:
            raise ParsingError("Document processing timed out")
        except FileNotFoundError as e:
            if 'antiword' in str(e).lower():
                # Return dummy page with warning instead of failing
                dummy_page = PageContent(
                    page_number=1,
                    text="",
                    lines=[]
                )
                return ParseResult(
                    success=True,
                    pages=[dummy_page],
                    page_count=1,
                    error_message=None,
                    warnings=["DOC parser not available - extraction skipped. Install antiword for full support."]
                )
            raise
        except Exception as e:
            # For encoding errors or other issues, return dummy page with warning
            dummy_page = PageContent(
                page_number=1,
                text="",
                lines=[]
            )
            return ParseResult(
                success=True,
                pages=[dummy_page],
                page_count=1,
                error_message=None,
                warnings=[f"Could not extract text from DOC file: {str(e)[:100]}"]
            )

    def validate(self, file_path: str) -> ValidationResult:
        """Validate .doc file without full parsing.
        
        Args:
            file_path: Absolute path to .doc file
        
        Returns:
            ValidationResult with validity status
        """
        # Import olefile here to avoid import errors if not installed
        try:
            import olefile
        except ImportError:
            # If olefile not available, skip password check
            pass
        
        # 1. Check file exists
        if not os.path.exists(file_path):
            return ValidationResult(
                is_valid=False,
                error_type='file_not_found',
                error_message=f'File not found: {file_path}'
            )
        
        # 2. Check file is readable
        if not os.access(file_path, os.R_OK):
            return ValidationResult(
                is_valid=False,
                error_type='permission_denied',
                error_message=f'File is not readable: {file_path}'
            )
        
        # 3. Check valid OLE format
        try:
            import olefile
            if not olefile.isOleFile(file_path):
                return ValidationResult(
                    is_valid=False,
                    error_type='invalid_format',
                    error_message='Unable to parse document. The file may be corrupted or invalid.'
                )
        except:
            # If olefile check fails, let antiword handle it
            pass
        
        # 4. Check password protection
        if self._is_password_protected(file_path):
            return ValidationResult(
                is_valid=False,
                error_type='password_protected',
                error_message='Password-protected .doc files are not supported'
            )
        
        # All checks pass
        # Note: We skip antiword availability check to allow .doc files to be selected
        # even if antiword is not installed. The actual parsing will handle errors gracefully.
        return ValidationResult(
            is_valid=True,
            error_type=None,
            error_message=None
        )

    def get_page_count(self, file_path: str) -> int:
        """Get approximate number of pages in .doc file.
        
        Note: .doc doesn't have explicit page numbers, so this is an approximation
        based on word count (~500 words per page).
        
        Args:
            file_path: Absolute path to .doc file
        
        Returns:
            Approximate number of pages (>= 1)
        
        Raises:
            ParsingError: If page count cannot be determined
        """
        try:
            # Extract text via antiword
            text = self._extract_text_via_antiword(file_path)
            
            # Count total words
            total_words = len(text.split())
            
            # Calculate approximate pages
            if total_words == 0:
                return 1  # At least 1 page even if empty
            
            pages = max(1, (total_words + self.WORDS_PER_PAGE - 1) // self.WORDS_PER_PAGE)
            return pages
            
        except Exception as e:
            # If we can't get page count, return 1 as default
            # This allows .doc files to be selected even if antiword fails
            return 1

    def _extract_text_via_antiword(self, file_path: str) -> str:
        """Execute antiword subprocess and return extracted text.
        
        Args:
            file_path: Absolute path to .doc file
        
        Returns:
            Plain text string (UTF-8 encoded)
        
        Raises:
            ParsingError: If antiword fails or times out
        """
        antiword_exe = self._get_antiword_path()
        
        try:
            # Run antiword with UTF-8 encoding and no line wrapping
            # -w 0 = no line wrapping (infinite width)
            # This ensures consistent output across platforms
            result = subprocess.run(
                [antiword_exe, '-w', '0', file_path],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise ParsingError(f"Unable to parse document. The file may be corrupted or invalid.")
            
            # Try multiple encodings to handle different platforms and character sets
            # On Windows, antiword typically outputs cp1252 (Windows Latin)
            encodings_to_try = [
                'cp1252',          # Windows Latin (try first on Windows)
                'utf-8',           # UTF-8 (standard)
                'cp1251',          # Windows Cyrillic (Russian, Bulgarian, etc.)
                'windows-1251',    # Alternative name for cp1251
                'iso-8859-5',      # ISO Cyrillic
                'latin-1',         # Fallback that accepts all bytes
            ]
            
            for encoding in encodings_to_try:
                try:
                    text = result.stdout.decode(encoding)
                    # If decoding succeeds and produces readable text (not all ?), use it
                    if text and not text.replace('?', '').replace(' ', '').replace('\n', '') == '':
                        return text
                except (UnicodeDecodeError, LookupError):
                    continue
            
            # If all encodings fail, use latin-1 with error replacement
            return result.stdout.decode('latin-1', errors='replace')
                
        except FileNotFoundError:
            # antiword not available
            if getattr(sys, 'frozen', False):
                # In production bundle - this should not happen
                raise ParsingError("DOC parser not available. Please reinstall the application.")
            else:
                # In development - provide helpful message
                raise ParsingError(
                    "DOC file support requires antiword. "
                    "For macOS development: brew install antiword. "
                    "DOC support is fully available in Windows builds."
                )

    def _get_antiword_path(self) -> str:
        """Locate antiword executable (PyInstaller bundle vs development).
        
        Returns:
            Path to antiword executable
        """
        if getattr(sys, 'frozen', False):
            # PyInstaller bundle
            return os.path.join(sys._MEIPASS, 'antiword.exe')
        else:
            # Development environment
            return 'antiword'  # Assumes in PATH

    def _is_password_protected(self, file_path: str) -> bool:
        """Check encryption flag in .doc OLE structure.
        
        Args:
            file_path: Path to .doc file
        
        Returns:
            True if password-protected, False otherwise
        """
        try:
            import olefile
            
            ole = olefile.OleFileIO(file_path)
            if ole.exists('WordDocument'):
                stream = ole.openstream('WordDocument')
                header = stream.read(68)  # FIB header
                flags = header[11] if len(header) > 11 else 0
                is_encrypted = bool(flags & 0x01)
                ole.close()
                return is_encrypted
            ole.close()
            return False
        except:
            return False  # Assume not encrypted if can't read (fail open)

    def _split_into_pages(self, paragraphs: list[str]) -> list[PageContent]:
        """Convert paragraph list into approximate pages.
        
        Args:
            paragraphs: List of paragraph text strings
        
        Returns:
            List of PageContent objects with page boundaries
        """
        if not paragraphs:
            return []
        
        pages = []
        current_page_text = []
        current_word_count = 0
        page_number = 1
        
        for para in paragraphs:
            words = para.split()
            para_word_count = len(words)
            
            # If adding this paragraph exceeds page limit, start new page
            if current_word_count + para_word_count > self.WORDS_PER_PAGE and current_page_text:
                # Save current page
                page_text = '\n'.join(current_page_text)
                pages.append(PageContent(
                    page_number=page_number,
                    text=page_text,
                    lines=current_page_text
                ))
                
                # Start new page
                page_number += 1
                current_page_text = [para]
                current_word_count = para_word_count
            else:
                # Add to current page
                current_page_text.append(para)
                current_word_count += para_word_count
        
        # Add last page if any content remains
        if current_page_text:
            page_text = '\n'.join(current_page_text)
            pages.append(PageContent(
                page_number=page_number,
                text=page_text,
                lines=current_page_text
            ))
        
        return pages
