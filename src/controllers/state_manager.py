"""StateManager - Thread-safe application state management."""

import threading
import sys
import os
from copy import deepcopy

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.application_state import ApplicationState, ProcessingStatus
from models.document import Document
from models.keyword import Keyword
from models.extraction_results import ExtractionResults


class StateManager:
    """Thread-safe manager for application state.

    Features:
    - Thread-safe state updates using locks
    - Immutable state pattern (returns copies)
    - State transition validation
    - Observer pattern for state change notifications
    """

    def __init__(self):
        """Initialize state manager."""
        self._state = ApplicationState()
        self._lock = threading.RLock()
        self._observers = []

    def get_state(self) -> ApplicationState:
        """Get current state (immutable copy).

        Returns:
            Copy of current application state
        """
        with self._lock:
            return deepcopy(self._state)

    def set_document(self, document: Document) -> None:
        """Set current document.

        Args:
            document: Document to set
        """
        with self._lock:
            self._state.set_document(document)
            self._notify_observers()

    def add_keyword(self, keyword: Keyword) -> None:
        """Add keyword to active keywords.

        Args:
            keyword: Keyword to add
        """
        with self._lock:
            self._state.add_keyword(keyword)
            self._notify_observers()

    def remove_keyword(self, keyword_text: str) -> None:
        """Remove keyword from active keywords.

        Args:
            keyword_text: Text of keyword to remove
        """
        with self._lock:
            self._state.remove_keyword(keyword_text)
            self._notify_observers()

    def clear_keywords(self) -> None:
        """Clear all active keywords."""
        with self._lock:
            self._state.clear_keywords()
            self._notify_observers()

    def start_processing(self) -> bool:
        """Start processing (if allowed).

        Returns:
            True if processing started, False if not allowed
        """
        with self._lock:
            if not self._state.can_start_extraction():
                return False

            self._state.start_processing()
            self._notify_observers()
            return True

    def complete_processing(self, results: ExtractionResults) -> None:
        """Complete processing with results.

        Args:
            results: Extraction results
        """
        with self._lock:
            self._state.complete_processing(results)
            self._notify_observers()

    def fail_processing(self, error_message: str) -> None:
        """Fail processing with error.

        Args:
            error_message: Error message
        """
        with self._lock:
            self._state.fail_processing(error_message)
            self._notify_observers()

    def reset(self) -> None:
        """Reset state to initial values."""
        with self._lock:
            self._state.reset()
            self._notify_observers()

    def can_start_extraction(self) -> bool:
        """Check if extraction can start.

        Returns:
            True if extraction can start
        """
        with self._lock:
            return self._state.can_start_extraction()

    def is_processing(self) -> bool:
        """Check if currently processing.

        Returns:
            True if processing
        """
        with self._lock:
            return self._state.is_processing

    def get_processing_status(self) -> ProcessingStatus:
        """Get current processing status.

        Returns:
            Current processing status
        """
        with self._lock:
            return self._state.processing_status

    def add_error(self, error_message: str) -> None:
        """Add error message to state.

        Args:
            error_message: Error message to add
        """
        with self._lock:
            self._state.error_messages.append(error_message)
            self._notify_observers()

    def clear_errors(self) -> None:
        """Clear all error messages."""
        with self._lock:
            self._state.error_messages = []
            self._notify_observers()

    # Observer pattern
    def add_observer(self, callback) -> None:
        """Add state change observer.

        Args:
            callback: Function(state: ApplicationState) -> None
        """
        with self._lock:
            if callback not in self._observers:
                self._observers.append(callback)

    def remove_observer(self, callback) -> None:
        """Remove state change observer.

        Args:
            callback: Observer callback to remove
        """
        with self._lock:
            if callback in self._observers:
                self._observers.remove(callback)

    def _notify_observers(self) -> None:
        """Notify all observers of state change."""
        # Create immutable copy for observers
        state_copy = deepcopy(self._state)

        # Call observers (outside lock to prevent deadlocks)
        observers = self._observers.copy()

        for observer in observers:
            try:
                observer(state_copy)
            except Exception as e:
                print(f"Error notifying observer: {e}")

    # Direct state updates (for complex state changes)
    def update_state(self, updater) -> None:
        """Update state using updater function.

        Args:
            updater: Function(state: ApplicationState) -> None
        """
        with self._lock:
            updater(self._state)
            self._notify_observers()
