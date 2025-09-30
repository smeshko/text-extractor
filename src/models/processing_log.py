"""ProcessingLog model for timestamped extraction logs."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class LogEntry:
    """A single log entry with timestamp and context.

    Attributes:
        timestamp: When event occurred
        level: Log level ('INFO', 'WARNING', 'ERROR')
        message: Log message
        context: Additional context data
    """

    timestamp: datetime
    level: str
    message: str
    context: dict | None = None

    def __post_init__(self):
        """Validate log entry attributes after initialization."""
        valid_levels = ('INFO', 'WARNING', 'ERROR')
        if self.level not in valid_levels:
            raise ValueError(
                f"Invalid log level: {self.level}. Must be one of {valid_levels}"
            )

        if not self.message:
            raise ValueError("Log message must be non-empty")

    def format(self) -> str:
        """Format log entry as string.

        Returns:
            Formatted log entry string
        """
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        return f"{timestamp_str} [{self.level}] {self.message}"


@dataclass
class ProcessingLog:
    """Timestamped log file recording extraction events, warnings, and errors.

    Attributes:
        log_filename: Unique log filename with timestamp
        log_path: Full path to log file
        entries: Collection of log entries
        start_time: Extraction start timestamp
        end_time: Extraction end timestamp
        status: Overall status ('success', 'partial_success', 'failure')
    """

    log_filename: str
    log_path: str
    entries: list[LogEntry] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: datetime | None = None
    status: str = 'success'

    def __post_init__(self):
        """Validate processing log attributes after initialization."""
        if not self.log_filename:
            raise ValueError("Log filename must be non-empty")

        if not self.log_path:
            raise ValueError("Log path must be non-empty")

        valid_statuses = ('success', 'partial_success', 'failure')
        if self.status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {self.status}. Must be one of {valid_statuses}"
            )

    def add_entry(self, level: str, message: str, context: dict | None = None) -> None:
        """Add a log entry.

        Args:
            level: Log level ('INFO', 'WARNING', 'ERROR')
            message: Log message
            context: Optional context data
        """
        entry = LogEntry(
            timestamp=datetime.now(),
            level=level,
            message=message,
            context=context
        )
        self.entries.append(entry)

    def info(self, message: str, context: dict | None = None) -> None:
        """Add INFO level log entry."""
        self.add_entry('INFO', message, context)

    def warning(self, message: str, context: dict | None = None) -> None:
        """Add WARNING level log entry."""
        self.add_entry('WARNING', message, context)

    def error(self, message: str, context: dict | None = None) -> None:
        """Add ERROR level log entry."""
        self.add_entry('ERROR', message, context)

    def finalize(self, status: str) -> None:
        """Finalize log with end time and status.

        Args:
            status: Final status ('success', 'partial_success', 'failure')
        """
        self.end_time = datetime.now()
        self.status = status

        duration = (self.end_time - self.start_time).total_seconds()
        self.info(f"Processing complete. Duration: {duration:.2f} seconds")
        self.info(f"Final status: {status}")

    @classmethod
    def create(cls, log_directory: str, document_filename: str):
        """Create a new processing log for a document.

        Args:
            log_directory: Directory to store log files
            document_filename: Name of document being processed

        Returns:
            ProcessingLog instance
        """
        import os
        from datetime import datetime

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f"extraction_{timestamp}.log"
        log_path = os.path.join(log_directory, log_filename)

        log = cls(
            log_filename=log_filename,
            log_path=log_path,
            entries=[],
            start_time=datetime.now(),
            end_time=None,
            status='success'
        )

        log.info(f"Starting extraction: {document_filename}")
        return log
