"""MainWindow - Main application window for Document Data Extractor."""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.configuration import Configuration
from models.application_state import ApplicationState
from ui.file_selector import FileSelector
from ui.keyword_panel import KeywordPanel
from ui.settings_panel import SettingsPanel
from ui.progress_bar import ProgressBar
from ui.results_display import ResultsDisplay
from ui.theme import AppTheme


class MainWindow:
    """Main application window.

    Single-screen 800x600 layout with:
    - File selection area
    - Keyword management panel
    - Settings panel (collapsible)
    - Extract button and progress
    - Results display
    """

    def __init__(self, config: Configuration):
        """Initialize main window.

        Args:
            config: Application configuration
        """
        self.config = config

        # Create main window - try TkinterDnD for drag-and-drop support
        try:
            from tkinterdnd2 import TkinterDnD
            self.root = TkinterDnD.Tk()
            self._has_dnd = True
        except (ImportError, Exception):
            # Fallback to regular Tk if TkinterDnD not available
            self.root = tk.Tk()
            self._has_dnd = False
        
        self.root.title("Document Data Extractor")
        self.root.geometry(f"{config.window_width}x{config.window_height}")
        self.root.minsize(1200, 1000)

        # Style configuration
        self._configure_styles()

        # Callbacks
        self._file_selected_callback = None
        self._keyword_added_callback = None
        self._keyword_selected_from_history_callback = None
        self._keyword_removed_callback = None
        self._keywords_cleared_callback = None
        self._extract_clicked_callback = None
        self._settings_changed_callback = None
        self._open_output_file_callback = None
        self._open_output_folder_callback = None
        self._open_log_file_callback = None

        # Build UI
        self._build_ui()

        # Track window size for persistence
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start monitoring system theme changes
        AppTheme.start_theme_monitoring()

    def _configure_styles(self):
        """Configure ttk styles."""
        # Apply centralized theme
        AppTheme.configure_styles(self.root)

    def _build_ui(self):
        """Build the complete UI layout."""
        # Main container with padding
        main_container = ttk.Frame(self.root, padding=AppTheme.PADDING['large'])
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(0, weight=1)

        current_row = 0

        # Title and settings button row
        header_frame = ttk.Frame(main_container)
        header_frame.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        header_frame.columnconfigure(0, weight=1)

        title_label = ttk.Label(
            header_frame,
            text="Document Data Extractor",
            style='Title.TLabel'
        )
        title_label.grid(row=0, column=0, sticky=tk.W)

        # Settings toggle button
        self.settings_button = ttk.Button(
            header_frame,
            text="⚙ Settings",
            command=self._toggle_settings
        )
        self.settings_button.grid(row=0, column=1, sticky=tk.E)

        current_row += 1

        # Settings Panel (collapsible)
        self.settings_panel = SettingsPanel(main_container, self.config)
        self.settings_panel.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        self.settings_panel.on_settings_changed(self._handle_settings_changed)
        self.settings_panel.collapse()  # Start collapsed

        current_row += 1

        # File Selection Area
        self.file_selector = FileSelector(main_container)
        self.file_selector.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        self.file_selector.on_file_selected(self._handle_file_selected)

        current_row += 1

        # Keyword Panel
        self.keyword_panel = KeywordPanel(main_container, self.config.keyword_history)
        self.keyword_panel.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        self.keyword_panel.on_keyword_added(self._handle_keyword_added)
        self.keyword_panel.on_keyword_selected_from_history(self._handle_keyword_from_history)
        self.keyword_panel.on_keyword_removed(self._handle_keyword_removed)
        self.keyword_panel.on_keywords_cleared(self._handle_keywords_cleared)

        current_row += 1

        # Progress Bar and Extract Button
        self.progress_bar = ProgressBar(main_container)
        self.progress_bar.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        self.progress_bar.on_extract_clicked(self._handle_extract_clicked)

        current_row += 1

        # Results Display
        self.results_display = ResultsDisplay(main_container)
        self.results_display.grid(row=current_row, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, AppTheme.PADDING['large']))
        self.results_display.on_open_output_file(self._handle_open_output_file)
        self.results_display.on_open_output_folder(self._handle_open_output_folder)
        self.results_display.on_open_log_file(self._handle_open_log_file)
        main_container.rowconfigure(current_row, weight=1)  # Results expand to fill

    def _toggle_settings(self):
        """Toggle settings panel visibility."""
        self.settings_panel.toggle()

    # Event handler registration
    def on_file_selected(self, callback):
        """Register file selection callback.

        Args:
            callback: Function(file_path: str) -> None
        """
        self._file_selected_callback = callback

    def on_keyword_added(self, callback):
        """Register keyword added callback.

        Args:
            callback: Function(keyword: str) -> None
        """
        self._keyword_added_callback = callback

    def on_keyword_selected_from_history(self, callback):
        """Register keyword from history callback.

        Args:
            callback: Function(keyword: str) -> None
        """
        self._keyword_selected_from_history_callback = callback

    def on_keyword_removed(self, callback):
        """Register keyword removed callback.

        Args:
            callback: Function(keyword: str) -> None
        """
        self._keyword_removed_callback = callback

    def on_keywords_cleared(self, callback):
        """Register keywords cleared callback.

        Args:
            callback: Function() -> None
        """
        self._keywords_cleared_callback = callback

    def on_extract_clicked(self, callback):
        """Register extract button callback.

        Args:
            callback: Function() -> None
        """
        self._extract_clicked_callback = callback

    def on_settings_changed(self, callback):
        """Register settings changed callback.

        Args:
            callback: Function(config: Configuration) -> None
        """
        self._settings_changed_callback = callback

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

    # Internal event handlers
    def _handle_file_selected(self, file_path: str):
        """Handle file selection event."""
        print(f"DEBUG MainWindow._handle_file_selected: {file_path}, callback={self._file_selected_callback is not None}")
        if self._file_selected_callback:
            self._file_selected_callback(file_path)

    def _handle_keyword_added(self, keyword: str):
        """Handle keyword added event."""
        if self._keyword_added_callback:
            self._keyword_added_callback(keyword)

    def _handle_keyword_from_history(self, keyword: str):
        """Handle keyword selected from history."""
        if self._keyword_selected_from_history_callback:
            self._keyword_selected_from_history_callback(keyword)

    def _handle_keyword_removed(self, keyword: str):
        """Handle keyword removed event."""
        if self._keyword_removed_callback:
            self._keyword_removed_callback(keyword)

    def _handle_keywords_cleared(self):
        """Handle keywords cleared event."""
        if self._keywords_cleared_callback:
            self._keywords_cleared_callback()

    def _handle_extract_clicked(self):
        """Handle extract button click."""
        if self._extract_clicked_callback:
            self._extract_clicked_callback()

    def _handle_settings_changed(self, config: Configuration):
        """Handle settings changed event."""
        self.config = config
        if self._settings_changed_callback:
            self._settings_changed_callback(config)

    def _handle_open_output_file(self):
        """Handle open output file click."""
        if self._open_output_file_callback:
            self._open_output_file_callback()

    def _handle_open_output_folder(self):
        """Handle open output folder click."""
        if self._open_output_folder_callback:
            self._open_output_folder_callback()

    def _handle_open_log_file(self):
        """Handle open log file click."""
        if self._open_log_file_callback:
            self._open_log_file_callback()

    def update_state(self, state: ApplicationState):
        """Update UI based on application state.

        Args:
            state: Current application state
        """
        # Update file selector
        if state.current_document:
            self.file_selector.set_file(state.current_document.file_path)
            if not state.current_document.is_valid:
                self.file_selector.show_error(state.current_document.error_message or "Invalid file")

        # Update keyword panel
        self.keyword_panel.set_active_keywords([kw.text for kw in state.active_keywords])

        # Update progress bar state
        if state.is_processing:
            self.progress_bar.set_processing()
        elif state.processing_status.value == 'complete':
            self.progress_bar.set_complete()
        elif state.processing_status.value == 'error':
            self.progress_bar.set_error()
        elif state.can_start_extraction():
            self.progress_bar.set_ready()
        else:
            self.progress_bar.set_ready()

        # Update results display
        if state.extraction_results:
            results = state.extraction_results

            if results.has_errors() and results.get_success_count() == 0:
                # Full error
                self.results_display.show_error(
                    results.get_error_summary(),
                    results.warnings
                )
            elif results.has_errors() or results.has_warnings():
                # Partial success
                self.results_display.show_partial_success(
                    results.get_status_summary(),
                    results.warnings,
                    results.get_error_summary()
                )
            else:
                # Full success
                self.results_display.show_success(
                    results.get_status_summary()
                )
        elif state.error_messages:
            # Show state-level errors
            self.results_display.show_error(
                '\n'.join(state.error_messages),
                []
            )

    def update_keyword_history(self, keywords: list[str]):
        """Update keyword history dropdown.

        Args:
            keywords: List of historical keywords
        """
        self.keyword_panel.update_history(keywords)

    def show(self):
        """Display window and start event loop."""
        self.root.mainloop()

    def _on_closing(self):
        """Handle window close event."""
        # Stop theme monitoring
        AppTheme.stop_theme_monitoring()
        
        # Save window size to config
        self.config.window_width = self.root.winfo_width()
        self.config.window_height = self.root.winfo_height()

        # Notify settings changed to save config
        if self._settings_changed_callback:
            self._settings_changed_callback(self.config)

        self.root.destroy()

    def after(self, ms: int, func):
        """Schedule function to run after delay.

        Args:
            ms: Milliseconds to wait
            func: Function to call

        Returns:
            Scheduled task identifier
        """
        return self.root.after(ms, func)

    def destroy(self):
        """Destroy the window."""
        self.root.destroy()
    
    def update_state(self, state: ApplicationState):
        """Update UI based on application state.
        
        Args:
            state: Current application state
        """
        # Update progress bar based on state
        if hasattr(self, 'progress_bar'):
            self.progress_bar.update_state(state)
        
        # Update results display based on state
        if hasattr(self, 'results_display'):
            if state.extraction_results:
                self.results_display.show_results(state.extraction_results)
    
    def show_error(self, message: str):
        """Show error message to user.
        
        Args:
            message: Error message to display
        """
        # Show in results display if available
        if hasattr(self, 'results_display'):
            self.results_display.show_error(message)
        
        # Also show in message box for critical errors
        from tkinter import messagebox
        messagebox.showerror("Error", message)
    
    def show_success(self, message: str):
        """Show success message to user.
        
        Args:
            message: Success message to display
        """
        # Show in results display if available
        if hasattr(self, 'results_display'):
            self.results_display.show_success(message)
