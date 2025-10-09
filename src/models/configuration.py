"""Configuration model for application settings."""

from dataclasses import dataclass, field
from datetime import datetime
import os
import re


@dataclass
class Configuration:
    """Application configuration persisted across sessions.

    Attributes:
        output_folder: Default output file location
        log_directory: Log file storage location
        number_format: Number format preference ('us_uk')
        proximity_rule: Keyword-number association rule ('next_number')
        keyword_history: Historical keywords
        keyword_presets: Saved keyword presets (list of dicts with 'name' and 'keywords')
        presets_section_expanded: UI state for presets section (collapsed by default)
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
    keyword_presets: list[dict] = field(default_factory=list)
    presets_section_expanded: bool = False
    window_width: int = 1200
    window_height: int = 1000
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

        # Validate keyword_presets structure
        for preset in self.keyword_presets:
            if not isinstance(preset, dict):
                raise ValueError("Invalid preset: must be dict")
            if 'name' not in preset or 'keywords' not in preset:
                raise ValueError("Preset missing required fields: name, keywords")
            if not isinstance(preset['keywords'], list):
                raise ValueError("Preset keywords must be list")

            # Validate preset name
            name = preset['name']
            if not name or len(name) > 50:
                raise ValueError(f"Preset name must be 1-50 chars: {name}")
            if not re.match(r'^[a-zA-Z0-9 ]+$', name):
                raise ValueError(f"Invalid characters in preset name: {name}")

            # Validate keywords
            for kw in preset['keywords']:
                if not isinstance(kw, str) or not kw or len(kw) > 100:
                    raise ValueError(f"Invalid keyword in preset '{name}': {kw}")

        # Check for duplicate preset names (case-insensitive)
        names_lower = [p['name'].lower() for p in self.keyword_presets]
        if len(names_lower) != len(set(names_lower)):
            raise ValueError("Duplicate preset names found")

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
            keyword_presets=[],
            presets_section_expanded=False,
            window_width=1200,
            window_height=1000,
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

    def _validate_preset_name(self, name: str, exclude_name: str = None) -> tuple[bool, str]:
        """Validate preset name.

        Args:
            name: Preset name to validate
            exclude_name: Name to exclude from uniqueness check (for updates)

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Length check
        if not name or len(name) > 50:
            return False, "Name must be 1-50 characters"

        # Pattern check
        if not re.match(r'^[a-zA-Z0-9 ]+$', name):
            return False, "Name can only contain letters, numbers, and spaces"

        # Uniqueness check (case-insensitive)
        existing_names = [
            p['name'].lower() for p in self.keyword_presets
            if exclude_name is None or p['name'].lower() != exclude_name.lower()
        ]
        if name.lower() in existing_names:
            return False, "Preset name already exists"

        return True, ""

    def add_preset(self, name: str, keywords: list[str]) -> tuple[bool, str]:
        """Add new preset.

        Args:
            name: Preset name (validated)
            keywords: List of keywords (validated)

        Returns:
            (success: bool, error_message: str)
        """
        # Validate name
        is_valid, error_msg = self._validate_preset_name(name)
        if not is_valid:
            return False, error_msg

        # Validate keywords
        if not keywords:
            return False, "Keywords list cannot be empty"

        # Check for duplicate keywords (case-insensitive)
        keywords_lower = [kw.lower() for kw in keywords]
        if len(keywords_lower) != len(set(keywords_lower)):
            return False, "Duplicate keywords in preset"

        for kw in keywords:
            if not isinstance(kw, str) or not kw or len(kw) > 100:
                return False, f"Invalid keyword: {kw}"

        # Add preset
        self.keyword_presets.append({
            'name': name,
            'keywords': keywords.copy()
        })
        self.last_updated = datetime.now().isoformat()
        return True, ""

    def update_preset(self, old_name: str, new_name: str, keywords: list[str]) -> tuple[bool, str]:
        """Update existing preset.

        Args:
            old_name: Current preset name (case-insensitive match)
            new_name: New preset name (can be same as old_name)
            keywords: Updated keyword list

        Returns:
            (success: bool, error_message: str)
        """
        # Find preset (case-insensitive)
        preset_index = None
        for i, preset in enumerate(self.keyword_presets):
            if preset['name'].lower() == old_name.lower():
                preset_index = i
                break

        if preset_index is None:
            return False, f"Preset '{old_name}' not found"

        # Validate new name (excluding old name from uniqueness check)
        is_valid, error_msg = self._validate_preset_name(new_name, exclude_name=old_name)
        if not is_valid:
            return False, error_msg

        # Validate keywords
        if not keywords:
            return False, "Keywords list cannot be empty"

        # Check for duplicate keywords (case-insensitive)
        keywords_lower = [kw.lower() for kw in keywords]
        if len(keywords_lower) != len(set(keywords_lower)):
            return False, "Duplicate keywords in preset"

        for kw in keywords:
            if not isinstance(kw, str) or not kw or len(kw) > 100:
                return False, f"Invalid keyword: {kw}"

        # Update preset
        self.keyword_presets[preset_index] = {
            'name': new_name,
            'keywords': keywords.copy()
        }
        self.last_updated = datetime.now().isoformat()
        return True, ""

    def delete_preset(self, name: str) -> bool:
        """Delete preset by name.

        Args:
            name: Preset name (case-insensitive)

        Returns:
            True if preset found and deleted, False if not found
        """
        # Find preset (case-insensitive)
        for i, preset in enumerate(self.keyword_presets):
            if preset['name'].lower() == name.lower():
                del self.keyword_presets[i]
                self.last_updated = datetime.now().isoformat()
                return True
        return False

    def get_preset_by_name(self, name: str) -> dict | None:
        """Retrieve preset by name.

        Args:
            name: Preset name (case-insensitive)

        Returns:
            Preset dict or None if not found
        """
        for preset in self.keyword_presets:
            if preset['name'].lower() == name.lower():
                return preset.copy()
        return None

    def get_all_presets(self) -> list[dict]:
        """Get all presets (ordered by insertion).

        Returns:
            Copy of keyword_presets list
        """
        return [preset.copy() for preset in self.keyword_presets]
