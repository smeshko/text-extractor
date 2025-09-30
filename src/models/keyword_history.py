"""Keyword history model for persistent keyword storage."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class KeywordHistory:
    """Persistent collection of previously used keywords across sessions.
    
    Attributes:
        keywords: Ordered list of unique keywords (most recent last)
        last_updated: Last modification timestamp
        max_size: Maximum number of keywords to retain (unlimited by default)
    """
    
    keywords: List[str] = field(default_factory=list)
    last_updated: Optional[datetime] = None
    max_size: int = 1000  # Practical limit
    
    def __post_init__(self):
        """Initialize timestamp if not set."""
        if self.last_updated is None:
            self.last_updated = datetime.now()
    
    def add(self, keyword: str) -> bool:
        """Add keyword to history if not already present.
        
        Case-insensitive duplicate check. If keyword exists, it's moved to end
        (most recent position).
        
        Args:
            keyword: Keyword to add
            
        Returns:
            True if keyword was added or moved, False if invalid
        """
        # Normalize and validate
        keyword = keyword.strip()
        if not keyword or len(keyword) > 100:
            return False
        
        keyword_lower = keyword.lower()
        
        # Check for duplicate (case-insensitive)
        existing = [kw for kw in self.keywords if kw.lower() == keyword_lower]
        
        if existing:
            # Remove existing (will re-add at end)
            self.keywords.remove(existing[0])
        
        # Add to end (most recent)
        self.keywords.append(keyword)
        
        # Enforce max size
        if len(self.keywords) > self.max_size:
            # Remove oldest (from beginning)
            self.keywords = self.keywords[-self.max_size:]
        
        # Update timestamp
        self.last_updated = datetime.now()
        
        return True
    
    def remove(self, keyword: str) -> bool:
        """Remove keyword from history (case-insensitive).
        
        Args:
            keyword: Keyword to remove
            
        Returns:
            True if keyword was removed, False if not found
        """
        keyword_lower = keyword.lower()
        
        # Find matching keyword (case-insensitive)
        matching = [kw for kw in self.keywords if kw.lower() == keyword_lower]
        
        if matching:
            self.keywords.remove(matching[0])
            self.last_updated = datetime.now()
            return True
        
        return False
    
    def contains(self, keyword: str) -> bool:
        """Check if keyword exists in history (case-insensitive).
        
        Args:
            keyword: Keyword to check
            
        Returns:
            True if keyword exists, False otherwise
        """
        keyword_lower = keyword.lower()
        return any(kw.lower() == keyword_lower for kw in self.keywords)
    
    def get_recent(self, count: int = 10) -> List[str]:
        """Get most recent keywords.
        
        Args:
            count: Number of recent keywords to return
            
        Returns:
            List of recent keywords (most recent last)
        """
        return self.keywords[-count:] if count < len(self.keywords) else self.keywords.copy()
    
    def clear(self) -> None:
        """Clear all keywords from history."""
        self.keywords.clear()
        self.last_updated = datetime.now()
    
    def select_multiple(self, keywords: List[str]) -> List[str]:
        """Select multiple keywords from history.
        
        Args:
            keywords: List of keyword texts to select
            
        Returns:
            List of keywords that exist in history
        """
        selected = []
        for keyword in keywords:
            keyword_lower = keyword.lower()
            # Find matching keyword (preserve original case from history)
            matching = [kw for kw in self.keywords if kw.lower() == keyword_lower]
            if matching:
                selected.append(matching[0])
        
        return selected
    
    def to_list(self) -> List[str]:
        """Get ordered list of all keywords.
        
        Returns:
            List of all keywords (most recent last)
        """
        return self.keywords.copy()
    
    def __len__(self) -> int:
        """Get number of keywords in history."""
        return len(self.keywords)
    
    def __contains__(self, keyword: str) -> bool:
        """Check if keyword exists in history (case-insensitive)."""
        return self.contains(keyword)
    
    def __iter__(self):
        """Iterate over keywords in order."""
        return iter(self.keywords)
    
    def __repr__(self) -> str:
        """Debug representation."""
        return (
            f"KeywordHistory(keywords={self.keywords!r}, "
            f"last_updated={self.last_updated!r}, max_size={self.max_size})"
        )