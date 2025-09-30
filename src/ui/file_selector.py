"""FileSelector - File selection component with drag-and-drop support."""

import tkinter as tk
from tkinter import ttk, filedialog
import os


class FileSelector(ttk.Frame):
    """File selection area with browse and drag-and-drop support.

    Features:
    - Browse button with file dialog (.pdf, .docx filter)
    - Drag-and-drop support using tkinterdnd2
    - File path display with icon
    - Error display for invalid files
    """

    def __init__(self, parent):
        """Initialize file selector component.

        Args:
            parent: Parent tkinter widget
        """
        super().__init__(parent, padding="10", relief=tk.RIDGE, borderwidth=1)

        self._file_selected_callback = None
        self._current_file = None
        self._build_ui()
        self._setup_drag_drop()

    def _build_ui(self):
        """Build the file selector UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Section label
        label = ttk.Label(self, text="Select Document", style='Section.TLabel')
        label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        # File display frame
        self.file_frame = ttk.Frame(self, relief=tk.SUNKEN, borderwidth=1)
        self.file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.file_frame.columnconfigure(1, weight=1)

        # File icon label
        self.icon_label = ttk.Label(self.file_frame, text="📄", font=('Segoe UI', 16))
        self.icon_label.grid(row=0, column=0, padx=(5, 5), pady=5)

        # File path label
        self.path_label = ttk.Label(
            self.file_frame,
            text="Drag file here or click Browse",
            foreground='gray'
        )
        self.path_label.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5), pady=5)

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
            foreground='red',
            wraplength=700
        )
        self.error_label.grid(row=3, column=0, sticky=tk.W, pady=(5, 0))
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
        """Open file dialog for file selection."""
        file_path = filedialog.askopenfilename(
            title="Select Document",
            filetypes=[
                ("Supported Documents", "*.pdf *.docx"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("All Files", "*.*")
            ]
        )

        if file_path:
            self._select_file(file_path)

    def _handle_drop(self, event):
        """Handle file drop event.

        Args:
            event: Drop event with file data
        """
        # Parse dropped files (may be multiple)
        files = self._parse_drop_data(event.data)

        if files:
            # Only accept first file
            self._select_file(files[0])

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
        """Handle file selection.

        Args:
            file_path: Path to selected file
        """
        print(f"DEBUG FileSelector._select_file called with: {file_path}")
        
        # Validate file
        if not os.path.exists(file_path):
            self.show_error(f"File not found: {file_path}")
            return

        # Check extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ('.pdf', '.docx'):
            self.show_error(f"Unsupported file type: {ext}. Please select a PDF or DOCX file.")
            return

        # Clear error
        self.clear_error()

        # Update display
        self._current_file = file_path
        self._update_display(file_path)

        # Notify callback
        print(f"DEBUG FileSelector: callback registered = {self._file_selected_callback is not None}")
        if self._file_selected_callback:
            print(f"DEBUG FileSelector: calling callback with {file_path}")
            self._file_selected_callback(file_path)

    def _update_display(self, file_path: str):
        """Update file display.

        Args:
            file_path: Path to display
        """
        # Get filename
        filename = os.path.basename(file_path)

        # Update icon based on extension
        ext = os.path.splitext(file_path)[1].lower()
        icon = "📄"  # PDF icon
        if ext == '.docx':
            icon = "📝"  # DOCX icon

        self.icon_label.configure(text=icon)

        # Update path label
        self.path_label.configure(
            text=filename,
            foreground='black'
        )

    def set_file(self, file_path: str):
        """Set current file (called from controller).

        Args:
            file_path: File path to set
        """
        self._current_file = file_path
        self._update_display(file_path)

    def clear(self):
        """Clear file selection."""
        self._current_file = None
        self.icon_label.configure(text="📄")
        self.path_label.configure(
            text="Drag file here or click Browse",
            foreground='gray'
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
            callback: Function(file_path: str) -> None
        """
        self._file_selected_callback = callback

    def get_file(self) -> str | None:
        """Get current file path.

        Returns:
            Current file path or None
        """
        return self._current_file
