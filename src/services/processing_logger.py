"""Processing logger for timestamped extraction logs."""

import os
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.processing_log import ProcessingLog, LogEntry
from models.extraction_results import ExtractionResults


class ProcessingLogger:
    """Generates processing log files for extraction operations.

    Features:
    - One log file per extraction
    - Timestamped entries
    - Log levels: INFO, WARNING, ERROR
    - UTF-8 encoding
    - Automatic log file creation
    """

    def __init__(self, log_directory: str):
        """Initialize logger.

        Args:
            log_directory: Directory for log files (from config)
        """
        self.log_directory = log_directory
        self.current_log: ProcessingLog | None = None

        # Ensure log directory exists
        os.makedirs(log_directory, exist_ok=True)

    def start_logging(self, document_filename: str, keywords: list[str]) -> str:
        """Start logging for extraction operation.

        Args:
            document_filename: Document being processed
            keywords: Keywords to extract

        Returns:
            Log file path
        """
        # Create new processing log
        self.current_log = ProcessingLog.create(self.log_directory, document_filename)

        # Log initial information
        self.log_event('INFO', f"Keywords: {', '.join(keywords)}")

        return self.current_log.log_path

    def log_event(self, level: str, message: str, context: dict | None = None) -> None:
        """Log an event.

        Args:
            level: 'INFO', 'WARNING', 'ERROR'
            message: Log message
            context: Optional context data
        """
        if self.current_log is None:
            print(f"Warning: No active log. Message: [{level}] {message}")
            return

        self.current_log.add_entry(level, message, context)

    def info(self, message: str, context: dict | None = None) -> None:
        """Log INFO level message."""
        self.log_event('INFO', message, context)

    def warning(self, message: str, context: dict | None = None) -> None:
        """Log WARNING level message."""
        self.log_event('WARNING', message, context)

    def error(self, message: str, context: dict | None = None) -> None:
        """Log ERROR level message."""
        self.log_event('ERROR', message, context)

    def finalize(self, status: str, results: ExtractionResults | None = None) -> None:
        """Finalize log with summary.

        Args:
            status: 'success', 'partial_success', 'failure'
            results: ExtractionResults for summary (optional)
        """
        if self.current_log is None:
            return

        # Log summary information
        if results:
            self.info(f"Extraction complete: {results.get_success_count()} matches, "
                     f"{results.get_not_found_count()} not found")

            if results.has_warnings():
                self.info(f"Warnings: {len(results.warnings)}")

            if results.has_errors():
                self.info(f"Errors: {len(results.errors)}")

        # Finalize log
        self.current_log.finalize(status)

        # Write log to file
        self._write_log_file()

        # Clear current log
        self.current_log = None

    def _write_log_file(self) -> None:
        """Write current log to file."""
        if self.current_log is None:
            return

        try:
            with open(self.current_log.log_path, 'w', encoding='utf-8') as f:
                # Write all log entries
                for entry in self.current_log.entries:
                    f.write(entry.format() + '\n')

        except Exception as e:
            print(f"Failed to write log file: {e}")

    def get_log_path(self) -> str | None:
        """Get path to current log file.

        Returns:
            Log file path or None if no active log
        """
        if self.current_log:
            return self.current_log.log_path
        return None
