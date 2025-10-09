"""Configuration manager for persistent application settings."""

import json
import os
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.configuration import Configuration


class ConfigurationManager:
    """Manages application configuration persistence.

    Features:
    - Load/save configuration from/to JSON file
    - Validate paths and create directories if needed
    - Use defaults if file missing or corrupted
    - Atomic writes for safe persistence
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize configuration manager.

        Args:
            config_path: Path to config file (default: config.json in app directory)
        """
        if config_path is None:
            # Default to config.json in user-writable location
            if getattr(sys, 'frozen', False):
                # Running as compiled executable - use user's AppData on Windows
                if sys.platform == 'win32':
                    # Windows: %APPDATA%\DocumentExtractor\config.json
                    app_dir = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'DocumentExtractor')
                else:
                    # Other platforms: same directory as executable
                    app_dir = os.path.dirname(sys.executable)
            else:
                # Running as script - use project root
                app_dir = os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__)
                )))

            # Ensure config directory exists
            os.makedirs(app_dir, exist_ok=True)
            config_path = os.path.join(app_dir, 'config.json')

        self.config_path = config_path

    def load(self) -> Configuration:
        """Load configuration from file.

        Returns:
            Configuration object (uses defaults if file missing/corrupted)

        Note: Never raises exceptions - uses defaults on error and logs warning
        """
        # If file doesn't exist, create with defaults
        if not os.path.exists(self.config_path):
            print(f"Config file not found at {self.config_path}, creating with defaults")
            config = Configuration.get_default()
            self.save(config)
            return config

        # Try to load existing config
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load presets with migration support
            keyword_presets = data.get('keyword_presets', [])
            
            # Validate and filter corrupted presets
            valid_presets = []
            for preset in keyword_presets:
                if (isinstance(preset, dict) and
                    'name' in preset and
                    'keywords' in preset and
                    isinstance(preset['keywords'], list)):
                    valid_presets.append(preset)
                else:
                    print(f"Skipping corrupted preset: {preset}")
            
            # Create Configuration from loaded data
            config = Configuration(
                output_folder=data.get('output_folder', ''),
                log_directory=data.get('log_directory', ''),
                number_format=data.get('number_format', 'us_uk'),
                proximity_rule=data.get('proximity_rule', 'next_number'),
                keyword_history=data.get('keyword_history', []),
                keyword_presets=valid_presets,
                presets_section_expanded=data.get('presets_section_expanded', False),
                window_width=data.get('window_width', 800),
                window_height=data.get('window_height', 600),
                version=data.get('version', '1.0.0'),
                last_updated=data.get('last_updated', '')
            )

            # Validate loaded config
            is_valid, errors = self.validate(config)
            if not is_valid:
                print(f"Config validation errors: {errors}")
                print("Using defaults for invalid fields")

                # Use defaults for any validation failures
                defaults = Configuration.get_default()
                if not config.output_folder or not os.path.isabs(config.output_folder):
                    config.output_folder = defaults.output_folder
                if not config.log_directory or not os.path.isabs(config.log_directory):
                    config.log_directory = defaults.log_directory

            # Ensure directories exist
            os.makedirs(config.output_folder, exist_ok=True)
            os.makedirs(config.log_directory, exist_ok=True)

            return config

        except json.JSONDecodeError:
            print(f"Config file corrupted, backing up and using defaults")
            self._backup_corrupted_config()
            config = Configuration.get_default()
            self.save(config)
            return config

        except Exception as e:
            print(f"Error loading config: {e}, using defaults")
            config = Configuration.get_default()
            return config

    def save(self, config: Configuration) -> bool:
        """Save configuration to file.

        Args:
            config: Configuration to persist

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate before saving
            is_valid, errors = self.validate(config)
            if not is_valid:
                print(f"Cannot save invalid config: {errors}")
                return False

            # Update last_updated timestamp
            from datetime import datetime
            config.last_updated = datetime.now().isoformat()

            # Prepare data for JSON
            data = {
                'version': config.version,
                'output_folder': config.output_folder,
                'log_directory': config.log_directory,
                'number_format': config.number_format,
                'proximity_rule': config.proximity_rule,
                'keyword_history': config.keyword_history,
                'keyword_presets': config.keyword_presets,
                'presets_section_expanded': config.presets_section_expanded,
                'window_width': config.window_width,
                'window_height': config.window_height,
                'last_updated': config.last_updated
            }

            # Atomic write: write to temp file, then rename
            temp_path = self.config_path + '.tmp'

            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Rename temp file to actual config file
            if os.path.exists(self.config_path):
                os.remove(self.config_path)
            os.rename(temp_path, self.config_path)

            return True

        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def get_default_config(self) -> Configuration:
        """Get default configuration.

        Returns:
            Configuration with default values
        """
        return Configuration.get_default()

    def validate(self, config: Configuration) -> tuple[bool, list[str]]:
        """Validate configuration.

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate paths
        path_valid, path_errors = config.validate_paths()
        errors.extend(path_errors)

        # Validate keyword history
        for keyword in config.keyword_history:
            if not keyword or len(keyword) > 100:
                errors.append(f"Invalid keyword in history: '{keyword}'")

        # Check for duplicate keywords (case-insensitive)
        seen = set()
        for keyword in config.keyword_history:
            keyword_lower = keyword.lower()
            if keyword_lower in seen:
                errors.append(f"Duplicate keyword in history: '{keyword}'")
            seen.add(keyword_lower)

        return len(errors) == 0, errors

    def _backup_corrupted_config(self) -> None:
        """Backup corrupted config file."""
        try:
            if os.path.exists(self.config_path):
                backup_path = self.config_path + '.bak'
                # Remove old backup if exists
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                os.rename(self.config_path, backup_path)
                print(f"Corrupted config backed up to: {backup_path}")
        except Exception as e:
            print(f"Failed to backup corrupted config: {e}")
