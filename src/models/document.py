"""Document model for file representation and validation."""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional


class DocumentState(Enum):
    """Document processing states."""
    UNSELECTED = "unselected"
    SELECTED = "selected"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"


@dataclass
class Document:
    """Represents a PDF, DOCX, or DOC file submitted for processing.
    
    Attributes:
        file_path: Absolute path to the document file
        filename: Original filename without path
        file_type: Document type ("pdf", "docx", or "doc")
        page_count: Total number of pages in document
        is_valid: Whether document is accessible and parsable
        error_message: Error description if document is invalid
        state: Current processing state
    """
    
    file_path: str
    filename: str
    file_type: str
    page_count: int = 0
    is_valid: bool = False
    error_message: Optional[str] = None
    state: DocumentState = DocumentState.UNSELECTED
    
    def __post_init__(self):
        """Validate and normalize document attributes."""
        # Ensure file_path is absolute
        if not Path(self.file_path).is_absolute():
            raise ValueError(f"file_path must be absolute: {self.file_path}")
        
        # Normalize file_type to lowercase
        self.file_type = self.file_type.lower()
        
        # Validate file_type
        if self.file_type not in ("pdf", "docx", "doc"):
            raise ValueError(f"file_type must be 'pdf', 'docx', or 'doc', got: {self.file_type}")
    
    @classmethod
    def from_path(cls, file_path: str) -> "Document":
        """Create Document from file path.
        
        Args:
            file_path: Absolute path to document file
            
        Returns:
            Document instance
            
        Raises:
            ValueError: If file extension is not supported
        """
        path = Path(file_path)
        
        # Extract filename and file type
        filename = path.name
        extension = path.suffix.lower()
        
        # Map extension to file type
        if extension == ".pdf":
            file_type = "pdf"
        elif extension == ".docx":
            file_type = "docx"
        elif extension == ".doc":
            file_type = "doc"
        else:
            raise ValueError(f"Unsupported file extension: {extension}")
        
        return cls(
            file_path=str(path.absolute()),
            filename=filename,
            file_type=file_type,
            state=DocumentState.SELECTED
        )
    
    def validate_exists(self) -> bool:
        """Validate that file exists.
        
        Returns:
            True if file exists, False otherwise
        """
        return Path(self.file_path).exists()
    
    def validate_readable(self) -> bool:
        """Validate that file is readable.
        
        Returns:
            True if file is readable, False otherwise
        """
        path = Path(self.file_path)
        return path.exists() and path.is_file()
    
    def validate_size(self, max_size_mb: int = 50) -> bool:
        """Validate file size is reasonable.
        
        Args:
            max_size_mb: Maximum file size in megabytes
            
        Returns:
            True if file size is acceptable, False otherwise
        """
        path = Path(self.file_path)
        if not path.exists():
            return False
        
        size_mb = path.stat().st_size / (1024 * 1024)
        return size_mb <= max_size_mb
    
    def mark_valid(self, page_count: int) -> None:
        """Mark document as valid after successful validation.
        
        Args:
            page_count: Number of pages in document
        """
        self.is_valid = True
        self.page_count = page_count
        self.error_message = None
        self.state = DocumentState.VALID
    
    def mark_invalid(self, error_message: str) -> None:
        """Mark document as invalid with error message.
        
        Args:
            error_message: Description of validation error
        """
        self.is_valid = False
        self.error_message = error_message
        self.state = DocumentState.INVALID
    
    def transition_to(self, state: DocumentState) -> None:
        """Transition document to new state.
        
        Args:
            state: Target state
            
        Raises:
            ValueError: If transition is invalid
        """
        # Define valid state transitions
        valid_transitions = {
            DocumentState.UNSELECTED: {DocumentState.SELECTED},
            DocumentState.SELECTED: {DocumentState.VALIDATING},
            DocumentState.VALIDATING: {DocumentState.VALID, DocumentState.INVALID},
            DocumentState.VALID: {DocumentState.SELECTED},  # Re-validation
            DocumentState.INVALID: {DocumentState.SELECTED},  # Re-validation
        }
        
        if state not in valid_transitions.get(self.state, set()):
            raise ValueError(
                f"Invalid state transition: {self.state.value} -> {state.value}"
            )
        
        self.state = state