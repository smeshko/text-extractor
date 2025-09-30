"""ThreadCoordinator - Worker thread management for background processing."""

import threading
import queue
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.extraction_results import ExtractionResults


class ThreadCoordinator:
    """Manages worker threads for background document processing.

    Features:
    - Worker thread creation and management
    - Queue-based communication between threads
    - Main thread queue polling
    - Message types: 'progress', 'complete', 'error'
    """

    def __init__(self):
        """Initialize thread coordinator."""
        self._worker_thread = None
        self._message_queue = queue.Queue()
        self._is_running = False

    def start_extraction(self, extraction_func, *args, **kwargs) -> None:
        """Start extraction in background thread.

        Args:
            extraction_func: Function to run in background thread
            *args: Positional arguments for extraction_func
            **kwargs: Keyword arguments for extraction_func
        """
        # Don't start if already running
        if self._is_running:
            self.send_error("Extraction already in progress")
            return

        # Clear old messages
        self._clear_queue()

        # Create and start worker thread
        self._is_running = True
        self._worker_thread = threading.Thread(
            target=self._worker_wrapper,
            args=(extraction_func, args, kwargs),
            daemon=True
        )
        self._worker_thread.start()

    def _worker_wrapper(self, extraction_func, args, kwargs):
        """Wrapper for worker thread execution.

        Args:
            extraction_func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
        """
        try:
            # Execute extraction function
            result = extraction_func(*args, **kwargs)

            # Send completion message
            self.send_complete(result)

        except Exception as e:
            # Send error message
            self.send_error(str(e))

        finally:
            self._is_running = False

    def send_progress(self, message: str) -> None:
        """Send progress update from worker thread.

        Args:
            message: Progress message
        """
        self._message_queue.put({
            'type': 'progress',
            'message': message
        })

    def send_complete(self, results: ExtractionResults) -> None:
        """Send completion message from worker thread.

        Args:
            results: Extraction results
        """
        self._message_queue.put({
            'type': 'complete',
            'results': results
        })

    def send_error(self, error_message: str) -> None:
        """Send error message from worker thread.

        Args:
            error_message: Error message
        """
        self._message_queue.put({
            'type': 'error',
            'message': error_message
        })

    def check_messages(self) -> list[dict]:
        """Check for messages from worker thread (called from main thread).

        Returns:
            List of messages received
        """
        messages = []

        # Get all available messages
        while not self._message_queue.empty():
            try:
                msg = self._message_queue.get_nowait()
                messages.append(msg)
            except queue.Empty:
                break

        return messages

    def is_running(self) -> bool:
        """Check if worker thread is running.

        Returns:
            True if worker thread is active
        """
        return self._is_running

    def wait_for_completion(self, timeout: float = None) -> bool:
        """Wait for worker thread to complete.

        Args:
            timeout: Maximum time to wait in seconds

        Returns:
            True if thread completed, False if timeout
        """
        if self._worker_thread and self._worker_thread.is_alive():
            self._worker_thread.join(timeout)
            return not self._worker_thread.is_alive()

        return True

    def _clear_queue(self):
        """Clear all messages from queue."""
        while not self._message_queue.empty():
            try:
                self._message_queue.get_nowait()
            except queue.Empty:
                break


class ProgressReporter:
    """Helper class for reporting progress from worker thread."""

    def __init__(self, coordinator: ThreadCoordinator):
        """Initialize progress reporter.

        Args:
            coordinator: ThreadCoordinator instance
        """
        self.coordinator = coordinator

    def report(self, message: str):
        """Report progress message.

        Args:
            message: Progress message
        """
        self.coordinator.send_progress(message)

    def __call__(self, message: str):
        """Allow using reporter as a callable.

        Args:
            message: Progress message
        """
        self.report(message)
