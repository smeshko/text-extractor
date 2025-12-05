"""MainWindow - Main application window for Document Data Extractor."""

import tkinter as tk
from tkinter import ttk
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.configuration import Configuration
from models.application_state import ApplicationState
from models.batch_extraction_results import BatchExtractionResults
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
        # Initial size 10% smaller than previous default (1200x1000 → 1080x900)
        self.root.geometry("1080x900")
        # Removed minsize constraint - window is fully resizable per FR-011

        # Style configuration
        self._configure_styles()

        # Callbacks
        self._file_selected_callback = None
        self._keyword_added_callback = None
        self._keyword_selected_from_history_callback = None
        self._keyword_removed_callback = None
        self._keywords_cleared_callback = None
        self._preset_create_callback = None
        self._preset_load_callback = None
        self._preset_edit_callback = None
        self._preset_delete_callback = None
        self._presets_section_toggle_callback = None
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
        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Create scrollable canvas
        self.main_canvas = tk.Canvas(
            self.root,
            bg=AppTheme.COLORS['bg'],
            highlightthickness=0
        )
        self.main_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create scrollbar
        self.main_scrollbar = ttk.Scrollbar(
            self.root,
            orient=tk.VERTICAL,
            command=self.main_canvas.yview
        )
        self.main_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.main_canvas.configure(yscrollcommand=self.main_scrollbar.set)
        
        # Main container inside canvas
        main_container = ttk.Frame(self.main_canvas, padding=AppTheme.PADDING['large'])
        self.canvas_window = self.main_canvas.create_window(
            (0, 0),
            window=main_container,
            anchor='nw'
        )
        
        # Configure container
        main_container.columnconfigure(0, weight=1)
        
        # Bind events to update scroll region
        main_container.bind('<Configure>', self._on_frame_configure)
        self.main_canvas.bind('<Configure>', self._on_canvas_configure)
        
        # Enable mousewheel scrolling
        self._bind_mousewheel()

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
        # Register preset callbacks
        self.keyword_panel.on_preset_create(self._handle_preset_create)
        self.keyword_panel.on_preset_load(self._handle_preset_load)
        self.keyword_panel.on_preset_edit(self._handle_preset_edit)
        self.keyword_panel.on_preset_delete(self._handle_preset_delete)
        self.keyword_panel.on_presets_section_toggled(self._handle_presets_section_toggle)
        # Initialize preset panel state
        self.keyword_panel.set_presets_expanded(self.config.presets_section_expanded)
        self.keyword_panel.refresh_presets(self.config.get_all_presets())

        current_row += 1

        # Progress Bar and Extract Button
        self.progress_bar = ProgressBar(main_container)
        self.progress_bar.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        self.progress_bar.on_extract_clicked(self._handle_extract_clicked)

        current_row += 1

        # Results Display
        self.results_display = ResultsDisplay(main_container)
        self.results_display.grid(row=current_row, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['large']))
        self.results_display.on_open_output_file(self._handle_open_output_file)
        self.results_display.on_open_output_folder(self._handle_open_output_folder)
        self.results_display.on_open_log_file(self._handle_open_log_file)

    def _toggle_settings(self):
        """Toggle settings panel visibility."""
        self.settings_panel.toggle()
    
    def _on_frame_configure(self, event=None):
        """Update scroll region when the main container size changes."""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox('all'))
    
    def _on_canvas_configure(self, event):
        """Update canvas window width to match canvas width."""
        canvas_width = event.width
        self.main_canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    def _bind_mousewheel(self):
        """Bind mousewheel scrolling to the canvas."""
        def _on_mousewheel(event):
            # Different platforms use different event deltas
            if sys.platform == 'darwin':  # macOS
                self.main_canvas.yview_scroll(int(-1 * (event.delta)), "units")
            else:  # Windows and Linux
                self.main_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        # Bind to canvas and all child widgets
        self.main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Also bind for Linux
        self.main_canvas.bind_all("<Button-4>", lambda e: self.main_canvas.yview_scroll(-1, "units"))
        self.main_canvas.bind_all("<Button-5>", lambda e: self.main_canvas.yview_scroll(1, "units"))

    # Event handler registration
    def on_file_selected(self, callback):
        """Register file selection callback.

        Args:
            callback: Function(file_paths: list[str]) -> None
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
    
    def on_preset_create(self, callback):
        """Register preset create callback.
        
        Args:
            callback: Function(name: str, keywords: list[str]) -> None
        """
        self._preset_create_callback = callback
    
    def on_preset_load(self, callback):
        """Register preset load callback.
        
        Args:
            callback: Function(preset_name: str) -> None
        """
        self._preset_load_callback = callback
    
    def on_preset_edit(self, callback):
        """Register preset edit callback.
        
        Args:
            callback: Function(old_name: str, new_name: str, keywords: list[str]) -> None
        """
        self._preset_edit_callback = callback
    
    def on_preset_delete(self, callback):
        """Register preset delete callback.
        
        Args:
            callback: Function(name: str) -> None
        """
        self._preset_delete_callback = callback
    
    def on_presets_section_toggled(self, callback):
        """Register presets section toggle callback.
        
        Args:
            callback: Function(expanded: bool) -> None
        """
        self._presets_section_toggle_callback = callback

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
    def _handle_file_selected(self, file_paths: list[str]):
        """Handle file selection event.

        Args:
            file_paths: List of selected file paths
        """
        print(f"DEBUG MainWindow._handle_file_selected: {len(file_paths)} files, callback={self._file_selected_callback is not None}")
        if self._file_selected_callback:
            self._file_selected_callback(file_paths)

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
    
    def _handle_preset_create(self, name: str, keywords: list[str]):
        """Handle preset create event."""
        if self._preset_create_callback:
            self._preset_create_callback(name, keywords)
            # Refresh presets display after creation
            self.keyword_panel.refresh_presets(self.config.get_all_presets())
    
    def _handle_preset_load(self, preset_name: str):
        """Handle preset load event."""
        print(f"DEBUG MainWindow: _handle_preset_load called for '{preset_name}'")
        print(f"DEBUG MainWindow: Callback registered: {self._preset_load_callback is not None}")
        if self._preset_load_callback:
            self._preset_load_callback(preset_name)
        else:
            print(f"DEBUG MainWindow: ERROR - No callback registered!")
    
    def _handle_preset_edit(self, old_name: str, new_name: str, keywords: list[str]):
        """Handle preset edit event."""
        if self._preset_edit_callback:
            self._preset_edit_callback(old_name, new_name, keywords)
            # Refresh presets display after edit
            self.keyword_panel.refresh_presets(self.config.get_all_presets())
    
    def _handle_preset_delete(self, name: str):
        """Handle preset delete event."""
        if self._preset_delete_callback:
            self._preset_delete_callback(name)
            # Refresh presets display after deletion
            self.keyword_panel.refresh_presets(self.config.get_all_presets())
    
    def _handle_presets_section_toggle(self, expanded: bool):
        """Handle presets section toggle event."""
        if self._presets_section_toggle_callback:
            self._presets_section_toggle_callback(expanded)

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
        print(f"DEBUG MainWindow: update_state called with {len(state.active_keywords)} active keywords")

        # Update file selector - handle both single document and multiple documents
        if state.current_documents:
            file_paths = [d.file_path for d in state.current_documents]
            self.file_selector.set_files(file_paths)
            # Show error for first invalid document (if any)
            for doc in state.current_documents:
                if not doc.is_valid:
                    self.file_selector.show_error(doc.error_message or "Invalid file")
                    break

        # Update keyword panel
        keyword_texts = [kw.text for kw in state.active_keywords]
        print(f"DEBUG MainWindow: Setting keywords in panel: {keyword_texts}")
        self.keyword_panel.set_active_keywords(keyword_texts)

        # Update progress bar state
        if hasattr(self, 'progress_bar'):
            self.progress_bar.update_state(state)

        # Update results display
        if state.extraction_results:
            results = state.extraction_results

            # Extract file paths from results
            output_file = getattr(results, 'output_path', None)
            log_file = getattr(results, 'log_path', None)
            output_folder = self.config.output_folder if output_file else None

            # Check if this is a batch result
            if isinstance(results, BatchExtractionResults):
                # Batch processing results
                doc_count = results.document_count
                warnings = results.warnings

                if not results.results and warnings:
                    # All documents failed
                    self.results_display.show_error(
                        f"Batch processing failed. {len(warnings)} error(s).",
                        warnings,
                        log_file
                    )
                elif warnings:
                    # Partial success
                    self.results_display.show_partial_success(
                        f"Processed {doc_count} file(s) with warnings.",
                        warnings,
                        None,
                        output_file,
                        output_folder,
                        log_file
                    )
                else:
                    # Full success
                    self.results_display.show_success(
                        f"Processed {doc_count} file(s) successfully.",
                        output_file,
                        output_folder,
                        log_file
                    )
            else:
                # Single document results (ExtractionResults)
                if results.has_errors() and results.get_success_count() == 0:
                    # Full error
                    self.results_display.show_error(
                        results.get_error_summary(),
                        results.warnings,
                        log_file
                    )
                elif results.has_errors() or results.has_warnings():
                    # Partial success
                    self.results_display.show_partial_success(
                        results.get_status_summary(),
                        results.warnings,
                        results.get_error_summary(),
                        output_file,
                        output_folder,
                        log_file
                    )
                else:
                    # Full success
                    self.results_display.show_success(
                        results.get_status_summary(),
                        output_file,
                        output_folder,
                        log_file
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
