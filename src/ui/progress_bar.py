"""ProgressBar - Progress indicator and Extract button."""

import tkinter as tk
from tkinter import ttk
from ui.theme import AppTheme


class ProgressBar(ttk.Frame):
    """Progress bar and Extract button component.

    Features:
    - Extract button (enabled/disabled based on state)
    - Indeterminate progress bar during processing
    - Status message label
    - States: Ready, Processing, Complete, Error
    """

    def __init__(self, parent):
        """Initialize progress bar component.

        Args:
            parent: Parent tkinter widget
        """
        super().__init__(
            parent,
            padding=AppTheme.PADDING['large'],
            relief='solid',
            borderwidth=1
        )

        self._extract_clicked_callback = None
        self._state = 'ready'

        self._build_ui()

    def _build_ui(self):
        """Build the progress bar UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Extract button (centered, large)
        button_frame = ttk.Frame(self)
        button_frame.grid(row=0, column=0, pady=(0, AppTheme.PADDING['large']))

        self.extract_button = ttk.Button(
            button_frame,
            text="Extract Data",
            style='Primary.TButton',
            command=self._handle_extract_clicked,
            width=20
        )
        self.extract_button.pack()
        self.extract_button.state(['disabled'])  # Start disabled

        # Progress bar
        self.progress_bar = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=400
        )
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
        self.progress_bar.grid_remove()  # Hidden by default

        # Status message
        self.status_label = ttk.Label(
            self,
            text="Select a file and add keywords to begin",
            foreground=AppTheme.COLORS['text_muted']
        )
        self.status_label.grid(row=2, column=0)

    def _handle_extract_clicked(self):
        """Handle extract button click."""
        if self._extract_clicked_callback:
            self._extract_clicked_callback()

    def set_ready(self):
        """Set state to ready (can extract)."""
        self._state = 'ready'
        self.extract_button.state(['!disabled'])
        self.extract_button.configure(text="Extract Data")
        self.progress_bar.grid_remove()
        self.progress_bar.stop()
        self.status_label.configure(
            text="Ready to extract",
            foreground=AppTheme.COLORS['success']
        )

    def set_processing(self, message: str = "Processing..."):
        """Set state to processing.

        Args:
            message: Status message to display
        """
        self._state = 'processing'
        self.extract_button.state(['disabled'])
        self.extract_button.configure(text="Processing...")
        self.progress_bar.grid()
        self.progress_bar.start(10)  # Animation speed
        self.status_label.configure(
            text=message,
            foreground=AppTheme.COLORS['primary']
        )

    def set_complete(self, message: str = "Extraction complete!"):
        """Set state to complete.

        Args:
            message: Success message to display
        """
        self._state = 'complete'
        self.extract_button.state(['!disabled'])
        self.extract_button.configure(text="Extract Data")
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.status_label.configure(
            text=message,
            foreground=AppTheme.COLORS['success']
        )

    def set_error(self, message: str = "Extraction failed"):
        """Set state to error.

        Args:
            message: Error message to display
        """
        self._state = 'error'
        self.extract_button.state(['!disabled'])
        self.extract_button.configure(text="Try Again")
        self.progress_bar.stop()
        self.progress_bar.grid_remove()
        self.status_label.configure(
            text=message,
            foreground=AppTheme.COLORS['error']
        )

    def update_status(self, message: str):
        """Update status message (during processing).

        Args:
            message: Status message
        """
        if self._state == 'processing':
            self.status_label.configure(text=message)

    def enable_extract(self):
        """Enable extract button."""
        if self._state != 'processing':
            self.extract_button.state(['!disabled'])

    def disable_extract(self):
        """Disable extract button."""
        self.extract_button.state(['disabled'])

    def on_extract_clicked(self, callback):
        """Register extract button callback.

        Args:
            callback: Function() -> None
        """
        self._extract_clicked_callback = callback

    def get_state(self) -> str:
        """Get current state.

        Returns:
            Current state ('ready', 'processing', 'complete', 'error')
        """
        return self._state
    
    def update_state(self, state):
        """Update UI based on application state.
        
        Args:
            state: ApplicationState object
        """
        from models.application_state import ProcessingStatus
        
        print(f"DEBUG ProgressBar.update_state: doc={state.current_document is not None}, keywords={len(state.active_keywords)}, processing={state.is_processing}, status={state.processing_status}")
        
        # Update state based on processing status
        if state.is_processing:
            self.set_processing()
        elif state.processing_status == ProcessingStatus.ERROR:
            # Handle error state (from exception or extraction errors)
            error_msg = state.error_messages[-1] if state.error_messages else "Extraction failed"
            self.set_error(error_msg)
        elif state.extraction_results:
            if state.extraction_results.has_errors():
                self.set_error("Extraction completed with errors")
            else:
                self.set_complete()
        
        # Enable extract button if we have document and keywords and not processing
        if state.current_document and len(state.active_keywords) > 0:
            if not state.is_processing:
                self.enable_extract()
                if state.processing_status not in (ProcessingStatus.PROCESSING, ProcessingStatus.ERROR):
                    self.status_label.configure(
                        text="Ready to extract",
                        foreground=AppTheme.COLORS['success']
                    )
        else:
            self.disable_extract()
            if not state.current_document:
                self.status_label.configure(
                    text="Select a file and add keywords to begin",
                    foreground=AppTheme.COLORS['text_muted']
                )
            elif len(state.active_keywords) == 0:
                self.status_label.configure(
                    text="Add keywords to begin",
                    foreground=AppTheme.COLORS['text_muted']
                )