"""SettingsPanel - Collapsible settings panel."""

import tkinter as tk
from tkinter import ttk, filedialog
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.configuration import Configuration


class SettingsPanel(ttk.Frame):
    """Collapsible settings panel.

    Features:
    - Output folder browser
    - Log directory browser
    - Number format dropdown (US/UK only)
    - Proximity rule dropdown (Next Number only)
    - Expand/collapse functionality
    """

    def __init__(self, parent, config: Configuration):
        """Initialize settings panel.

        Args:
            parent: Parent tkinter widget
            config: Application configuration
        """
        super().__init__(parent, padding="10", relief=tk.RIDGE, borderwidth=1)

        self.config = config
        self._is_expanded = False
        self._settings_changed_callback = None

        self._build_ui()

    def _build_ui(self):
        """Build the settings panel UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Content frame (collapsible)
        self.content_frame = ttk.Frame(self)

        # Output folder
        output_label = ttk.Label(self.content_frame, text="Output Folder:")
        output_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))

        output_row = ttk.Frame(self.content_frame)
        output_row.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        output_row.columnconfigure(0, weight=1)

        self.output_entry = ttk.Entry(output_row, width=50)
        self.output_entry.insert(0, self.config.output_folder)
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        output_browse = ttk.Button(
            output_row,
            text="Browse...",
            command=self._browse_output_folder
        )
        output_browse.grid(row=0, column=1)

        # Log directory
        log_label = ttk.Label(self.content_frame, text="Log Directory:")
        log_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))

        log_row = ttk.Frame(self.content_frame)
        log_row.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        log_row.columnconfigure(0, weight=1)

        self.log_entry = ttk.Entry(log_row, width=50)
        self.log_entry.insert(0, self.config.log_directory)
        self.log_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))

        log_browse = ttk.Button(
            log_row,
            text="Browse...",
            command=self._browse_log_directory
        )
        log_browse.grid(row=0, column=1)

        # Number format
        format_label = ttk.Label(self.content_frame, text="Number Format:")
        format_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))

        self.format_var = tk.StringVar(value=self.config.number_format)
        format_combo = ttk.Combobox(
            self.content_frame,
            textvariable=self.format_var,
            values=['us_uk'],
            state='readonly',
            width=20
        )
        format_combo.grid(row=5, column=0, sticky=tk.W, pady=(0, 10))
        format_combo.set('US/UK Format')  # Display name

        # Proximity rule
        proximity_label = ttk.Label(self.content_frame, text="Proximity Rule:")
        proximity_label.grid(row=6, column=0, sticky=tk.W, pady=(0, 5))

        self.proximity_var = tk.StringVar(value=self.config.proximity_rule)
        proximity_combo = ttk.Combobox(
            self.content_frame,
            textvariable=self.proximity_var,
            values=['next_number'],
            state='readonly',
            width=20
        )
        proximity_combo.grid(row=7, column=0, sticky=tk.W, pady=(0, 10))
        proximity_combo.set('Next Number')  # Display name

        # Save button
        save_button = ttk.Button(
            self.content_frame,
            text="Save Settings",
            command=self._save_settings
        )
        save_button.grid(row=8, column=0, sticky=tk.W)

    def _browse_output_folder(self):
        """Open folder browser for output folder."""
        folder = filedialog.askdirectory(
            title="Select Output Folder",
            initialdir=self.output_entry.get() or os.path.expanduser('~')
        )

        if folder:
            self.output_entry.delete(0, tk.END)
            self.output_entry.insert(0, folder)

    def _browse_log_directory(self):
        """Open folder browser for log directory."""
        folder = filedialog.askdirectory(
            title="Select Log Directory",
            initialdir=self.log_entry.get() or os.path.expanduser('~')
        )

        if folder:
            self.log_entry.delete(0, tk.END)
            self.log_entry.insert(0, folder)

    def _save_settings(self):
        """Save settings to configuration."""
        # Get values
        output_folder = self.output_entry.get().strip()
        log_directory = self.log_entry.get().strip()

        # Validate paths
        if not output_folder or not os.path.isabs(output_folder):
            self._show_error("Output folder must be an absolute path")
            return

        if not log_directory or not os.path.isabs(log_directory):
            self._show_error("Log directory must be an absolute path")
            return

        # Create directories if they don't exist
        try:
            os.makedirs(output_folder, exist_ok=True)
            os.makedirs(log_directory, exist_ok=True)
        except OSError as e:
            self._show_error(f"Cannot create directory: {e}")
            return

        # Update config
        self.config.output_folder = output_folder
        self.config.log_directory = log_directory
        self.config.number_format = 'us_uk'  # Only option for now
        self.config.proximity_rule = 'next_number'  # Only option for now

        # Notify callback
        if self._settings_changed_callback:
            self._settings_changed_callback(self.config)

        # Show success (brief)
        self._show_success()

    def _show_error(self, message: str):
        """Show error message."""
        # Create temporary error label
        error_label = ttk.Label(
            self.content_frame,
            text=f"❌ {message}",
            foreground='red'
        )
        error_label.grid(row=9, column=0, sticky=tk.W, pady=(5, 0))

        # Remove after 3 seconds
        self.after(3000, error_label.destroy)

    def _show_success(self):
        """Show success message."""
        success_label = ttk.Label(
            self.content_frame,
            text="✓ Settings saved",
            foreground='green'
        )
        success_label.grid(row=9, column=0, sticky=tk.W, pady=(5, 0))

        # Remove after 2 seconds
        self.after(2000, success_label.destroy)

    def expand(self):
        """Expand the settings panel."""
        if not self._is_expanded:
            self.content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            self._is_expanded = True

    def collapse(self):
        """Collapse the settings panel."""
        if self._is_expanded:
            self.content_frame.grid_remove()
            self._is_expanded = False

    def toggle(self):
        """Toggle expansion state."""
        if self._is_expanded:
            self.collapse()
        else:
            self.expand()

    def is_expanded(self) -> bool:
        """Check if panel is expanded.

        Returns:
            True if expanded, False if collapsed
        """
        return self._is_expanded

    def on_settings_changed(self, callback):
        """Register settings changed callback.

        Args:
            callback: Function(config: Configuration) -> None
        """
        self._settings_changed_callback = callback

    def get_config(self) -> Configuration:
        """Get current configuration.

        Returns:
            Current configuration
        """
        return self.config
