"""ResultsDisplay - Results display area with action buttons."""

import tkinter as tk
from tkinter import ttk
import subprocess
import platform
import os


class ResultsDisplay(ttk.Frame):
    """Results display component.

    Features:
    - Success/error/warning messages
    - "Open Output File", "Open Output Folder", "Open Log File" buttons
    - Expandable error details
    - States: Hidden, Success, Partial Success, Error
    """

    def __init__(self, parent):
        """Initialize results display component.

        Args:
            parent: Parent tkinter widget
        """
        super().__init__(parent, padding="10", relief=tk.RIDGE, borderwidth=1)

        self._open_output_file_callback = None
        self._open_output_folder_callback = None
        self._open_log_file_callback = None

        self._output_file_path = None
        self._output_folder_path = None
        self._log_file_path = None

        self._state = 'hidden'

        self._build_ui()
        self.hide()

    def _build_ui(self):
        """Build the results display UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Configure ttk style for disabled buttons
        style = ttk.Style()
        style.map('TButton',
                  foreground=[('disabled', '#9CA3AF')],  # Gray text when disabled
                  background=[('disabled', '#E5E7EB')])  # Gray background when disabled

        # Message frame
        self.message_frame = ttk.Frame(self)
        self.message_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.message_frame.columnconfigure(1, weight=1)

        # Icon label
        self.icon_label = ttk.Label(
            self.message_frame,
            text="",
            font=('Segoe UI', 16)
        )
        self.icon_label.grid(row=0, column=0, padx=(0, 10))

        # Message label
        self.message_label = ttk.Label(
            self.message_frame,
            text="",
            wraplength=650
        )
        self.message_label.grid(row=0, column=1, sticky=tk.W)

        # Details frame (expandable)
        self.details_frame = ttk.Frame(self)
        self.details_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.details_frame.columnconfigure(0, weight=1)
        self.details_frame.grid_remove()  # Hidden by default

        # Details label
        self.details_label = ttk.Label(
            self.details_frame,
            text="",
            wraplength=700,
            foreground='gray'
        )
        self.details_label.grid(row=0, column=0, sticky=tk.W)

        # Expand/collapse button
        self.expand_button = ttk.Button(
            self,
            text="Show Details",
            command=self._toggle_details
        )
        self.expand_button.grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.expand_button.grid_remove()  # Hidden by default

        # Action buttons
        self.actions_frame = ttk.Frame(self)
        self.actions_frame.grid(row=3, column=0, sticky=tk.W)

        self.open_file_button = ttk.Button(
            self.actions_frame,
            text="Open Output File",
            command=self._handle_open_file
        )
        self.open_file_button.grid(row=0, column=0, padx=(0, 5))
        self.open_file_button.state(['disabled'])  # Start disabled

        self.open_folder_button = ttk.Button(
            self.actions_frame,
            text="Open Output Folder",
            command=self._handle_open_folder
        )
        self.open_folder_button.grid(row=0, column=1, padx=(0, 5))
        self.open_folder_button.state(['disabled'])  # Start disabled

        self.open_log_button = ttk.Button(
            self.actions_frame,
            text="Open Log File",
            command=self._handle_open_log
        )
        self.open_log_button.grid(row=0, column=2)
        self.open_log_button.state(['disabled'])  # Start disabled

    def _toggle_details(self):
        """Toggle details visibility."""
        if self.details_frame.winfo_viewable():
            self.details_frame.grid_remove()
            self.expand_button.configure(text="Show Details")
        else:
            self.details_frame.grid()
            self.expand_button.configure(text="Hide Details")

    def _handle_open_file(self):
        """Handle open output file button."""
        # Check if button is disabled
        if 'disabled' in self.open_file_button.state():
            return

        if self._output_file_path and os.path.exists(self._output_file_path):
            self._open_file_with_default_app(self._output_file_path)
        elif self._open_output_file_callback:
            self._open_output_file_callback()

    def _handle_open_folder(self):
        """Handle open output folder button."""
        # Check if button is disabled
        if 'disabled' in self.open_folder_button.state():
            return

        if self._output_folder_path and os.path.exists(self._output_folder_path):
            self._open_file_with_default_app(self._output_folder_path)
        elif self._open_output_folder_callback:
            self._open_output_folder_callback()

    def _handle_open_log(self):
        """Handle open log file button."""
        # Check if button is disabled
        if 'disabled' in self.open_log_button.state():
            return

        if self._log_file_path and os.path.exists(self._log_file_path):
            self._open_file_with_default_app(self._log_file_path)
        elif self._open_log_file_callback:
            self._open_log_file_callback()

    def _open_file_with_default_app(self, path: str):
        """Open file or folder with default application.

        Args:
            path: File or folder path to open
        """
        try:
            system = platform.system()

            if system == 'Windows':
                os.startfile(path)
            elif system == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
        except Exception as e:
            print(f"Failed to open {path}: {e}")

    def show_success(self, message: str, output_file: str = None, output_folder: str = None, log_file: str = None):
        """Show success state.

        Args:
            message: Success message
            output_file: Path to output file
            output_folder: Path to output folder
            log_file: Path to log file
        """
        self._state = 'success'
        self._output_file_path = output_file
        self._output_folder_path = output_folder
        self._log_file_path = log_file

        self.icon_label.configure(text="✓", foreground='green')
        self.message_label.configure(text=message, foreground='green')

        self.details_frame.grid_remove()
        self.expand_button.grid_remove()

        # Enable/disable buttons based on available paths
        if output_file and os.path.exists(output_file):
            self.open_file_button.state(['!disabled'])
        else:
            self.open_file_button.state(['disabled'])

        if output_folder and os.path.exists(output_folder):
            self.open_folder_button.state(['!disabled'])
        else:
            self.open_folder_button.state(['disabled'])

        if log_file and os.path.exists(log_file):
            self.open_log_button.state(['!disabled'])
        else:
            self.open_log_button.state(['disabled'])

        self.grid()

    def show_partial_success(self, message: str, warnings: list[str] = None, errors: str = None, output_file: str = None, output_folder: str = None, log_file: str = None):
        """Show partial success state with warnings.

        Args:
            message: Status message
            warnings: List of warning messages
            errors: Error details
            output_file: Path to output file
            output_folder: Path to output folder
            log_file: Path to log file
        """
        self._state = 'partial_success'
        self._output_file_path = output_file
        self._output_folder_path = output_folder
        self._log_file_path = log_file

        self.icon_label.configure(text="⚠", foreground='orange')
        self.message_label.configure(text=message, foreground='orange')

        # Show details
        details_text = []
        if warnings:
            details_text.append("Warnings:")
            for warning in warnings:
                details_text.append(f"  - {warning}")

        if errors:
            details_text.append("\nErrors:")
            details_text.append(errors)

        if details_text:
            self.details_label.configure(text='\n'.join(details_text))
            self.expand_button.grid()
            self.details_frame.grid_remove()  # Collapsed by default
            self.expand_button.configure(text="Show Details")

        # Enable/disable buttons based on available paths
        if output_file and os.path.exists(output_file):
            self.open_file_button.state(['!disabled'])
        else:
            self.open_file_button.state(['disabled'])

        if output_folder and os.path.exists(output_folder):
            self.open_folder_button.state(['!disabled'])
        else:
            self.open_folder_button.state(['disabled'])

        if log_file and os.path.exists(log_file):
            self.open_log_button.state(['!disabled'])
        else:
            self.open_log_button.state(['disabled'])

        self.grid()

    def show_error(self, message: str, warnings: list[str] = None, log_file: str = None):
        """Show error state.

        Args:
            message: Error message
            warnings: List of warning messages
            log_file: Path to log file
        """
        self._state = 'error'
        self._output_file_path = None
        self._output_folder_path = None
        self._log_file_path = log_file

        self.icon_label.configure(text="❌", foreground='red')
        self.message_label.configure(text="Extraction failed", foreground='red')

        # Show error details
        details_text = [message]

        if warnings:
            details_text.append("\nWarnings:")
            for warning in warnings:
                details_text.append(f"  - {warning}")

        self.details_label.configure(text='\n'.join(details_text))
        self.expand_button.grid()
        self.details_frame.grid()  # Expanded by default for errors
        self.expand_button.configure(text="Hide Details")

        # Disable file/folder buttons (no output files on error)
        self.open_file_button.state(['disabled'])
        self.open_folder_button.state(['disabled'])

        # Enable log button only if log file exists
        if log_file and os.path.exists(log_file):
            self.open_log_button.state(['!disabled'])
        else:
            self.open_log_button.state(['disabled'])

        self.grid()

    def hide(self):
        """Hide results display."""
        self._state = 'hidden'
        self.grid_remove()

    def set_output_paths(self, output_file: str = None, output_folder: str = None, log_file: str = None):
        """Set paths for action buttons.

        Args:
            output_file: Path to output file
            output_folder: Path to output folder
            log_file: Path to log file
        """
        self._output_file_path = output_file
        self._output_folder_path = output_folder
        self._log_file_path = log_file

        # Enable/disable buttons based on availability
        if output_file and os.path.exists(output_file):
            self.open_file_button.state(['!disabled'])
        else:
            self.open_file_button.state(['disabled'])

        if output_folder and os.path.exists(output_folder):
            self.open_folder_button.state(['!disabled'])
        else:
            self.open_folder_button.state(['disabled'])

        if log_file and os.path.exists(log_file):
            self.open_log_button.state(['!disabled'])
        else:
            self.open_log_button.state(['disabled'])

    # Event callbacks
    def on_open_output_file(self, callback):
        """Register open output file callback.

        Args:
            callback: Function() -> None
        """
        self._open_output_file_callback = callback

    def on_open_output_folder(self, callback):
        """Register open output folder callback.

        Args:
            callback: Function() -> None
        """
        self._open_output_folder_callback = callback

    def on_open_log_file(self, callback):
        """Register open log file callback.

        Args:
            callback: Function() -> None
        """
        self._open_log_file_callback = callback

    def get_state(self) -> str:
        """Get current state.

        Returns:
            Current state ('hidden', 'success', 'partial_success', 'error')
        """
        return self._state

    def show_results(self, results):
        """Show extraction results.

        Args:
            results: ExtractionResults object
        """
        # Extract paths from results
        output_file = getattr(results, 'output_path', None)
        log_file = getattr(results, 'log_path', None)

        # Extract output folder from output file path
        output_folder = None
        if output_file:
            output_folder = os.path.dirname(output_file)

        # Determine which display method to call based on results
        if results.has_errors():
            if results.get_success_count() > 0:
                # Partial success - some matches found but with errors
                message = f"Extraction completed with warnings. {results.get_success_count()} matches found."
                self.show_partial_success(
                    message=message,
                    warnings=results.warnings,
                    errors=results.get_error_summary() if results.has_errors() else None,
                    output_file=output_file,
                    output_folder=output_folder,
                    log_file=log_file
                )
            else:
                # Error - no successful matches
                message = f"Extraction failed. {results.get_error_summary()}"
                self.show_error(
                    message=message,
                    warnings=results.warnings,
                    log_file=log_file
                )
        else:
            # Success - no errors
            message = f"Extraction successful! {results.get_success_count()} matches found."
            self.show_success(
                message=message,
                output_file=output_file,
                output_folder=output_folder,
                log_file=log_file
            )
