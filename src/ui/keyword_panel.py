"""KeywordPanel - Keyword management panel with history and active keywords."""

import tkinter as tk
from tkinter import ttk
from ui.theme import AppTheme


class KeywordPanel(ttk.Frame):
    """Keyword management panel.

    Features:
    - Text input field for manual entry
    - Add button (also triggered by Enter key)
    - Keyword history dropdown (multi-select)
    - Active keywords display as removable chips
    - Clear All button
    """

    def __init__(self, parent, keyword_history: list[str] = None):
        """Initialize keyword panel.

        Args:
            parent: Parent tkinter widget
            keyword_history: List of historical keywords
        """
        super().__init__(
            parent,
            padding=AppTheme.PADDING['large'],
            relief='solid',
            borderwidth=1
        )

        self._keyword_history = keyword_history or []
        self._active_keywords = []

        # Callbacks
        self._keyword_added_callback = None
        self._keyword_selected_from_history_callback = None
        self._keyword_removed_callback = None
        self._keywords_cleared_callback = None

        self._build_ui()

    def _build_ui(self):
        """Build the keyword panel UI."""
        # Configure grid
        self.columnconfigure(0, weight=1)

        # Section label
        label = ttk.Label(self, text="Keywords", style='Section.TLabel')
        label.grid(row=0, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['medium']))

        # Input row
        input_frame = ttk.Frame(self)
        input_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
        input_frame.columnconfigure(0, weight=1)

        # Keyword input
        self.keyword_entry = ttk.Entry(input_frame, width=40)
        self.keyword_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, AppTheme.PADDING['medium']))
        self.keyword_entry.bind('<Return>', lambda e: self._add_keyword())

        # Add button
        self.add_button = ttk.Button(
            input_frame,
            text="Add",
            command=self._add_keyword
        )
        self.add_button.grid(row=0, column=1)

        # History section
        if self._keyword_history:
            history_label = ttk.Label(
                self,
                text="History:",
                foreground=AppTheme.COLORS['text']
            )
            history_label.grid(row=2, column=0, sticky=tk.W, pady=(AppTheme.PADDING['medium'], AppTheme.PADDING['small']))

            # History listbox with scrollbar
            history_frame = ttk.Frame(self)
            history_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
            history_frame.columnconfigure(0, weight=1)

            # Scrollbar
            scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL)

            # Listbox
            self.history_listbox = tk.Listbox(
                history_frame,
                height=4,
                selectmode=tk.MULTIPLE,
                yscrollcommand=scrollbar.set,
                exportselection=False,
                borderwidth=1,
                relief='solid',
                bg=AppTheme.COLORS['bg'],
                fg=AppTheme.COLORS['text']
            )
            scrollbar.config(command=self.history_listbox.yview)

            self.history_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E))
            scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

            # Populate history
            self._populate_history()

            # Bind double-click to select
            self.history_listbox.bind('<Double-Button-1>', lambda e: self._select_from_history())

            # Select from history button
            select_button = ttk.Button(
                self,
                text="Add Selected from History",
                command=self._select_from_history
            )
            select_button.grid(row=4, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['medium']))
        else:
            self.history_listbox = None

        # Active keywords section
        active_label = ttk.Label(
            self,
            text="Active Keywords:",
            foreground=AppTheme.COLORS['text']
        )
        active_label.grid(row=5, column=0, sticky=tk.W, pady=(AppTheme.PADDING['medium'], AppTheme.PADDING['small']))

        # Active keywords frame (scrollable)
        self.active_frame = ttk.Frame(self, relief='solid', borderwidth=1)
        self.active_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
        self.active_frame.columnconfigure(0, weight=1)

        # Canvas for scrolling chips
        self.active_canvas = tk.Canvas(
            self.active_frame,
            height=70,
            bg=AppTheme.COLORS['bg'],
            highlightthickness=0
        )
        self.active_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Inner frame for chips
        self.chips_frame = ttk.Frame(self.active_canvas)
        self.chips_frame_id = self.active_canvas.create_window(
            (0, 0),
            window=self.chips_frame,
            anchor=tk.NW
        )

        # Bind resize
        self.chips_frame.bind('<Configure>', self._on_chips_configure)

        # Clear All button
        clear_frame = ttk.Frame(self)
        clear_frame.grid(row=7, column=0, sticky=(tk.W, tk.E))
        clear_frame.columnconfigure(0, weight=1)

        self.keyword_count_label = ttk.Label(
            clear_frame,
            text="0 keywords",
            foreground=AppTheme.COLORS['text']
        )
        self.keyword_count_label.grid(row=0, column=0, sticky=tk.W)

        self.clear_button = ttk.Button(
            clear_frame,
            text="Clear All",
            command=self._clear_keywords
        )
        self.clear_button.grid(row=0, column=1, sticky=tk.E)
        self.clear_button.state(['disabled'])

    def _populate_history(self):
        """Populate history listbox from keyword_history."""
        if not self.history_listbox:
            return

        self.history_listbox.delete(0, tk.END)

        # Add keywords in reverse order (most recent first)
        for keyword in reversed(self._keyword_history):
            # Don't show if already active
            if keyword not in self._active_keywords:
                self.history_listbox.insert(tk.END, keyword)

    def _add_keyword(self):
        """Add keyword from input field."""
        keyword = self.keyword_entry.get().strip()

        if not keyword:
            return

        # Validate length
        if len(keyword) > 100:
            self._show_error("Keyword too long (max 100 characters)")
            return

        # Check for duplicate (case-insensitive)
        if any(k.lower() == keyword.lower() for k in self._active_keywords):
            self._show_error("Keyword already added")
            return

        # Clear input
        self.keyword_entry.delete(0, tk.END)

        # Add to active keywords
        self._add_active_keyword(keyword)

        # Notify callback
        if self._keyword_added_callback:
            self._keyword_added_callback(keyword)

    def _select_from_history(self):
        """Add selected keywords from history."""
        if not self.history_listbox:
            return

        selected_indices = self.history_listbox.curselection()

        if not selected_indices:
            return

        # Get selected keywords
        for index in selected_indices:
            keyword = self.history_listbox.get(index)

            # Add to active
            self._add_active_keyword(keyword)

            # Notify callback
            if self._keyword_selected_from_history_callback:
                self._keyword_selected_from_history_callback(keyword)

        # Refresh history to remove added keywords
        self._populate_history()

    def _add_active_keyword(self, keyword: str):
        """Add keyword to active display.

        Args:
            keyword: Keyword to add
        """
        # Check for duplicate
        if keyword in self._active_keywords:
            return

        self._active_keywords.append(keyword)
        self._render_active_keywords()

    def _remove_active_keyword(self, keyword: str):
        """Remove keyword from active display.

        Args:
            keyword: Keyword to remove
        """
        if keyword in self._active_keywords:
            self._active_keywords.remove(keyword)
            self._render_active_keywords()

            # Notify callback
            if self._keyword_removed_callback:
                self._keyword_removed_callback(keyword)

            # Refresh history
            if self.history_listbox:
                self._populate_history()

    def _clear_keywords(self):
        """Clear all active keywords."""
        if not self._active_keywords:
            return

        self._active_keywords = []
        self._render_active_keywords()

        # Notify callback
        if self._keywords_cleared_callback:
            self._keywords_cleared_callback()

        # Refresh history
        if self.history_listbox:
            self._populate_history()

    def _render_active_keywords(self):
        """Render active keywords as chips."""
        # Clear existing chips
        for widget in self.chips_frame.winfo_children():
            widget.destroy()

        # Create chips
        for i, keyword in enumerate(self._active_keywords):
            chip = self._create_chip(keyword)
            chip.grid(row=0, column=i, padx=2, pady=2)

        # Update count label
        count = len(self._active_keywords)
        self.keyword_count_label.configure(
            text=f"{count} keyword{'s' if count != 1 else ''}"
        )

        # Enable/disable clear button
        if count > 0:
            self.clear_button.state(['!disabled'])
        else:
            self.clear_button.state(['disabled'])

        # Update canvas scroll region
        self.chips_frame.update_idletasks()

    def _create_chip(self, keyword: str) -> tk.Frame:
        """Create a removable keyword chip.

        Args:
            keyword: Keyword text

        Returns:
            Chip frame widget
        """
        # Use tk.Frame for better background color control
        chip = tk.Frame(
            self.chips_frame,
            relief='solid',
            borderwidth=1,
            bg=AppTheme.COLORS['primary_light'],
            highlightbackground=AppTheme.COLORS['border'],
            highlightthickness=1
        )

        # Keyword label
        label = tk.Label(
            chip,
            text=keyword,
            bg=AppTheme.COLORS['primary_light'],
            fg=AppTheme.COLORS['primary_dark'],
            font=AppTheme.FONTS['body'],
            padx=AppTheme.PADDING['medium'],
            pady=AppTheme.PADDING['small']
        )
        label.grid(row=0, column=0)

        # Remove button
        remove_btn = tk.Button(
            chip,
            text="×",
            bg=AppTheme.COLORS['primary_light'],
            fg=AppTheme.COLORS['error'],
            font=AppTheme.FONTS['body_bold'],
            relief='flat',
            borderwidth=0,
            padx=AppTheme.PADDING['small'],
            pady=0,
            cursor='hand2',
            command=lambda: self._remove_active_keyword(keyword)
        )
        remove_btn.grid(row=0, column=1, padx=(0, AppTheme.PADDING['small']))

        return chip

    def _on_chips_configure(self, event):
        """Handle chips frame resize."""
        # Update scroll region
        self.active_canvas.configure(scrollregion=self.active_canvas.bbox('all'))

    def _show_error(self, message: str):
        """Show validation error (temporary)."""
        # Flash the entry field background
        original_bg = self.keyword_entry.cget('style')
        # Note: ttk doesn't easily support background changes, so we just clear for now
        self.keyword_entry.delete(0, tk.END)

    # Public API
    def set_active_keywords(self, keywords: list[str]):
        """Set active keywords (from controller).

        Args:
            keywords: List of active keywords
        """
        self._active_keywords = keywords.copy()
        self._render_active_keywords()

        # Refresh history
        if self.history_listbox:
            self._populate_history()

    def get_active_keywords(self) -> list[str]:
        """Get active keywords.

        Returns:
            List of active keywords
        """
        return self._active_keywords.copy()

    def update_history(self, keywords: list[str]):
        """Update keyword history.

        Args:
            keywords: New history list
        """
        self._keyword_history = keywords
        if self.history_listbox:
            self._populate_history()

    # Event callbacks
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
