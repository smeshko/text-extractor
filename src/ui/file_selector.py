"""FileSelector - File selection component with drag-and-drop support."""

import tkinter as tk
from tkinter import ttk, filedialog
import os
from ui.theme import AppTheme


class FileSelector(ttk.Frame):
    """File selection area with browse and drag-and-drop support.

    Features:
    - Browse button with file dialog (.pdf, .docx, .doc filter)
    - Multi-file selection support
    - Drag-and-drop support using tkinterdnd2
    - File path display with icon
    - Error display for invalid files
    """

    def __init__(self, parent):
        """Initialize file selector component.

        Args:
            parent: Parent tkinter widget
        """
        super().__init__(
            parent,
            padding=AppTheme.PADDING['large'],
            relief='solid',
            borderwidth=1
        )

        self._file_selected_callback = None
        self._current_files: list[str] = []
        self._build_ui()
        self._setup_drag_drop()

    def _build_ui(self):
        """Build the file selector UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Section label
        label = ttk.Label(self, text="Select Documents", style='Section.TLabel')
        label.grid(row=0, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['medium']))

        # File display frame
        self.file_frame = ttk.Frame(self, relief='solid', borderwidth=1)
        self.file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
        self.file_frame.columnconfigure(1, weight=1)
        # Apply subtle background color
        self.file_frame.configure(style='Section.TFrame')

        # File icon label
        self.icon_label = ttk.Label(
            self.file_frame,
            text="📄",
            font=AppTheme.FONTS['icon'],
            background=AppTheme.COLORS['bg_secondary']
        )
        self.icon_label.grid(row=0, column=0, padx=(AppTheme.PADDING['medium'], AppTheme.PADDING['medium']), pady=AppTheme.PADDING['medium'])

        # File path label
        self.path_label = ttk.Label(
            self.file_frame,
            text="Drag files here or click Browse",
            foreground=AppTheme.COLORS['text_muted'],
            background=AppTheme.COLORS['bg_secondary']
        )
        self.path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, AppTheme.PADDING['medium']), pady=AppTheme.PADDING['medium'])

        # Browse button
        self.browse_button = ttk.Button(
            self,
            text="Browse...",
            command=self._browse_file
        )
        self.browse_button.grid(row=2, column=0, sticky=tk.W)

        # Error label (hidden by default)
        self.error_label = ttk.Label(
            self,
            text="",
            foreground=AppTheme.COLORS['error'],
            wraplength=700
        )
        self.error_label.grid(row=3, column=0, sticky=tk.W, pady=(AppTheme.PADDING['medium'], 0))
        self.error_label.grid_remove()

    def _setup_drag_drop(self):
        """Setup drag-and-drop functionality using tkinterdnd2."""
        try:
            from tkinterdnd2 import DND_FILES
            
            # Check if drag-and-drop is available (requires TkinterDnD root)
            root = self.winfo_toplevel()
            if hasattr(root, 'drop_target_register'):
                # Make file_frame accept drops
                self.file_frame.drop_target_register(DND_FILES)
                self.file_frame.dnd_bind('<<Drop>>', self._handle_drop)
                self.file_frame.dnd_bind('<<DragEnter>>', self._handle_drag_enter)
                self.file_frame.dnd_bind('<<DragLeave>>', self._handle_drag_leave)
            else:
                # Drag-and-drop not available, browse button only
                pass

        except (ImportError, Exception):
            # tkinterdnd2 not available, drag-and-drop disabled
            pass

    def _browse_file(self):
        """Open file dialog for multi-file selection."""
        file_paths = filedialog.askopenfilenames(
            title="Select Documents",
            filetypes=[
                ("Supported Documents", "*.pdf *.docx *.doc"),
                ("PDF Files", "*.pdf"),
                ("Word Documents (DOCX)", "*.docx"),
                ("Word Documents (DOC)", "*.doc"),
                ("All Files", "*.*")
            ]
        )

        if file_paths:
            self._select_files(list(file_paths))

    def _handle_drop(self, event):
        """Handle file drop event.

        Args:
            event: Drop event with file data
        """
        # Parse dropped files (may be multiple)
        files = self._parse_drop_data(event.data)

        if files:
            # Accept all dropped files
            self._select_files(files)

        # Reset background
        self.file_frame.configure(style='TFrame')

    def _handle_drag_enter(self, event):
        """Handle drag enter event."""
        # Highlight drop zone
        self.file_frame.configure(relief=tk.SOLID)

    def _handle_drag_leave(self, event):
        """Handle drag leave event."""
        # Remove highlight
        self.file_frame.configure(relief=tk.SUNKEN)

    def _parse_drop_data(self, data: str) -> list[str]:
        """Parse dropped file data.

        Args:
            data: Raw drop data string

        Returns:
            List of file paths
        """
        # Drop data may be space-separated or have curly braces
        files = []

        # Handle curly brace wrapped paths
        if data.startswith('{'):
            # Split by } { pattern
            parts = data.split('} {')
            for part in parts:
                part = part.strip('{}').strip()
                if part:
                    files.append(part)
        else:
            # Simple space-separated
            files = [f.strip() for f in data.split() if f.strip()]

        return files

    def _select_file(self, file_path: str):
        """Handle single file selection (backward compatibility).

        Args:
            file_path: Path to selected file
        """
        self._select_files([file_path])

    def _select_files(self, file_paths: list[str]):
        """Handle multi-file selection.

        Args:
            file_paths: List of file paths to select
        """
        print(f"DEBUG FileSelector._select_files called with {len(file_paths)} files")

        valid_files = []
        errors = []

        for file_path in file_paths:
            # Validate file exists
            if not os.path.exists(file_path):
                errors.append(f"File not found: {os.path.basename(file_path)}")
                continue

            # Check extension
            ext = os.path.splitext(file_path)[1].lower()
            if ext not in ('.pdf', '.docx', '.doc'):
                errors.append(f"Unsupported file type: {os.path.basename(file_path)}")
                continue

            valid_files.append(file_path)

        if errors and not valid_files:
            # All files invalid
            self.show_error("; ".join(errors))
            return

        if errors:
            # Some files invalid - show warning but continue with valid ones
            self.show_error(f"Skipped: {'; '.join(errors)}")
        else:
            self.clear_error()

        # Update display and state
        self._current_files = valid_files
        self._update_display_multi(valid_files)

        # Notify callback with list of valid files
        print(f"DEBUG FileSelector: callback registered = {self._file_selected_callback is not None}")
        if self._file_selected_callback:
            print(f"DEBUG FileSelector: calling callback with {len(valid_files)} files")
            self._file_selected_callback(valid_files)

    def _update_display(self, file_path: str):
        """Update file display for single file (backward compatibility).

        Args:
            file_path: Path to display
        """
        self._update_display_multi([file_path])

    def _update_display_multi(self, file_paths: list[str]):
        """Update file display for multiple files.

        Args:
            file_paths: List of file paths to display
        """
        if not file_paths:
            return

        if len(file_paths) == 1:
            # Single file - show filename
            filename = os.path.basename(file_paths[0])
            ext = os.path.splitext(file_paths[0])[1].lower()
            icon = "📄"  # PDF icon
            if ext == '.docx':
                icon = "📝"  # DOCX icon

            self.icon_label.configure(text=icon)
            self.path_label.configure(
                text=filename,
                foreground=AppTheme.COLORS['text']
            )
        else:
            # Multiple files - show count
            self.icon_label.configure(text="📚")  # Multiple files icon
            self.path_label.configure(
                text=f"{len(file_paths)} files selected",
                foreground=AppTheme.COLORS['text']
            )

    def set_file(self, file_path: str):
        """Set current file (backward compatibility).

        Args:
            file_path: File path to set
        """
        self.set_files([file_path])

    def set_files(self, file_paths: list[str]):
        """Set current files (called from controller).

        Args:
            file_paths: List of file paths to set
        """
        self._current_files = file_paths
        self._update_display_multi(file_paths)

    def clear(self):
        """Clear file selection."""
        self._current_files = []
        self.icon_label.configure(text="📄")
        self.path_label.configure(
            text="Drag files here or click Browse",
            foreground=AppTheme.COLORS['text_muted']
        )
        self.clear_error()

    def show_error(self, message: str):
        """Show error message.

        Args:
            message: Error message to display
        """
        self.error_label.configure(text=f"❌ {message}")
        self.error_label.grid()

    def clear_error(self):
        """Clear error message."""
        self.error_label.configure(text="")
        self.error_label.grid_remove()

    def on_file_selected(self, callback):
        """Register file selected callback.

        Args:
            callback: Function(file_paths: list[str]) -> None
        """
        self._file_selected_callback = callback

    def get_file(self) -> str | None:
        """Get current file path (backward compatibility).

        Returns:
            First file path or None if no files selected
        """
        return self._current_files[0] if self._current_files else None

    def get_files(self) -> list[str]:
        """Get all current file paths.

        Returns:
            List of current file paths
        """
        return self._current_files
