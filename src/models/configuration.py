"""Configuration model for application settings."""

from dataclasses import dataclass, field
from datetime import datetime
import os


@dataclass
class Configuration:
    """Application configuration persisted across sessions.

    Attributes:
        output_folder: Default output file location
        log_directory: Log file storage location
        number_format: Number format preference ('us_uk')
        proximity_rule: Keyword-number association rule ('next_number')
        keyword_history: Historical keywords
        window_width: Main window width (pixels)
        window_height: Main window height (pixels)
        version: Configuration version
        last_updated: Last modification timestamp (ISO 8601)
    """

    output_folder: str
    log_directory: str
    number_format: str = 'us_uk'
    proximity_rule: str = 'next_number'
    keyword_history: list[str] = field(default_factory=list)
    window_width: int = 800
    window_height: int = 600
    version: str = '1.0.0'
    last_updated: str = ''

    def __post_init__(self):
        """Validate configuration attributes after initialization."""
        # Validate number format
        if self.number_format not in ('us_uk',):
            raise ValueError(
                f"Invalid number_format: {self.number_format}. Must be 'us_uk'"
            )

        # Validate proximity rule
        if self.proximity_rule not in ('next_number',):
            raise ValueError(
                f"Invalid proximity_rule: {self.proximity_rule}. Must be 'next_number'"
            )

        # Validate window dimensions
        if self.window_width < 600 or self.window_width > 3840:
            raise ValueError(
                f"Window width must be between 600 and 3840, got: {self.window_width}"
            )

        if self.window_height < 400 or self.window_height > 2160:
            raise ValueError(
                f"Window height must be between 400 and 2160, got: {self.window_height}"
            )

        # Update last_updated if not set
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()

    @classmethod
    def get_default(cls):
        """Create configuration with default values.

        Returns:
            Configuration with platform-appropriate defaults
        """
        # Get user's home directory
        home = os.path.expanduser('~')

        # Create default paths
        default_output = os.path.join(home, 'Documents', 'DocumentExtractor', 'Output')
        default_logs = os.path.join(home, 'Documents', 'DocumentExtractor', 'Logs')

        return cls(
            output_folder=default_output,
            log_directory=default_logs,
            number_format='us_uk',
            proximity_rule='next_number',
            keyword_history=[],
            window_width=800,
            window_height=600,
            version='1.0.0',
            last_updated=datetime.now().isoformat()
        )

    def add_keyword_to_history(self, keyword: str) -> None:
        """Add keyword to history (no duplicates, maintain order).

        Args:
            keyword: Keyword to add to history
        """
        keyword = keyword.strip()
        keyword_lower = keyword.lower()

        # Remove existing occurrence (case-insensitive)
        self.keyword_history = [
            kw for kw in self.keyword_history
            if kw.lower() != keyword_lower
        ]

        # Add to end (most recent)
        self.keyword_history.append(keyword)

        # Limit size to 1000
        if len(self.keyword_history) > 1000:
            self.keyword_history = self.keyword_history[-1000:]

        # Update timestamp
        self.last_updated = datetime.now().isoformat()

    def remove_keyword_from_history(self, keyword: str) -> None:
        """Remove keyword from history (case-insensitive).

        Args:
            keyword: Keyword to remove
        """
        keyword_lower = keyword.lower()
        self.keyword_history = [
            kw for kw in self.keyword_history
            if kw.lower() != keyword_lower
        ]
        self.last_updated = datetime.now().isoformat()

    def clear_keyword_history(self) -> None:
        """Clear all keywords from history."""
        self.keyword_history = []
        self.last_updated = datetime.now().isoformat()

    def validate_paths(self) -> tuple[bool, list[str]]:
        """Validate that paths are writable.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Check output folder
        if not os.path.isabs(self.output_folder):
            errors.append("Output folder must be an absolute path")
        else:
            try:
                os.makedirs(self.output_folder, exist_ok=True)
                if not os.access(self.output_folder, os.W_OK):
                    errors.append(f"Output folder is not writable: {self.output_folder}")
            except OSError as e:
                errors.append(f"Cannot create output folder: {e}")

        # Check log directory
        if not os.path.isabs(self.log_directory):
            errors.append("Log directory must be an absolute path")
        else:
            try:
                os.makedirs(self.log_directory, exist_ok=True)
                if not os.access(self.log_directory, os.W_OK):
                    errors.append(f"Log directory is not writable: {self.log_directory}")
            except OSError as e:
                errors.append(f"Cannot create log directory: {e}")

        return len(errors) == 0, errors
