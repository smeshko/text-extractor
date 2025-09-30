"""Keyword model for search term representation."""

import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Keyword:
    """A user-defined search term for locating numerical values in documents.
    
    Attributes:
        text: The keyword text (original case preserved)
        normalized: Lowercase version for case-insensitive matching
        is_historical: Whether from keyword history or newly entered
        is_active: Whether currently selected for extraction
    """
    
    text: str
    normalized: str = ""
    is_historical: bool = False
    is_active: bool = True
    
    def __post_init__(self):
        """Validate and normalize keyword attributes."""
        # Trim whitespace
        self.text = self.text.strip()
        
        # Validate length
        if not self.text or len(self.text) < 1:
            raise ValueError("Keyword cannot be empty or whitespace-only")
        
        if len(self.text) > 100:
            raise ValueError(f"Keyword length must be 1-100 characters, got {len(self.text)}")
        
        # Generate normalized version if not provided
        if not self.normalized:
            self.normalized = self.text.lower()
    
    @classmethod
    def from_text(cls, text: str, is_historical: bool = False) -> "Keyword":
        """Create Keyword from text string.
        
        Args:
            text: Keyword text
            is_historical: Whether from keyword history
            
        Returns:
            Keyword instance
            
        Raises:
            ValueError: If text is invalid
        """
        return cls(
            text=text.strip(),
            is_historical=is_historical,
            is_active=True
        )
    
    def sanitize_for_regex(self) -> str:
        """Sanitize keyword for safe regex use.
        
        Returns:
            Regex-escaped keyword suitable for pattern matching
        """
        return re.escape(self.text)
    
    def to_regex_pattern(
        self,
        case_insensitive: bool = True,
        unicode_support: bool = True,
        word_boundaries: bool = False
    ) -> re.Pattern:
        """Convert keyword to compiled regex pattern.
        
        Args:
            case_insensitive: Whether to match case-insensitively
            unicode_support: Whether to enable Unicode support
            word_boundaries: Whether to add word boundary markers
            
        Returns:
            Compiled regex pattern
        """
        # Escape keyword for regex
        pattern = self.sanitize_for_regex()
        
        # Add word boundaries if requested
        if word_boundaries:
            pattern = r'\b' + pattern + r'\b'
        
        # Build regex flags
        flags = 0
        if case_insensitive:
            flags |= re.IGNORECASE
        if unicode_support:
            flags |= re.UNICODE
        
        return re.compile(pattern, flags)
    
    def matches(self, other: "Keyword") -> bool:
        """Check if this keyword matches another (case-insensitive).
        
        Args:
            other: Keyword to compare
            
        Returns:
            True if keywords match (case-insensitive), False otherwise
        """
        return self.normalized == other.normalized
    
    def __eq__(self, other) -> bool:
        """Check equality based on normalized text."""
        if not isinstance(other, Keyword):
            return False
        return self.normalized == other.normalized
    
    def __hash__(self) -> int:
        """Hash based on normalized text for set/dict operations."""
        return hash(self.normalized)
    
    def __str__(self) -> str:
        """String representation showing original text."""
        return self.text
    
    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"Keyword(text={self.text!r}, normalized={self.normalized!r}, "
            f"is_historical={self.is_historical}, is_active={self.is_active})"
        )