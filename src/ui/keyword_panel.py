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
        self._presets = []
        self._presets_expanded = False

        # Callbacks
        self._keyword_added_callback = None
        self._keyword_selected_from_history_callback = None
        self._keyword_removed_callback = None
        self._keywords_cleared_callback = None
        self._preset_create_callback = None
        self._preset_load_callback = None
        self._preset_edit_callback = None
        self._preset_delete_callback = None
        self._presets_section_toggle_callback = None

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

        # Presets section
        self._build_presets_section()

        # History section
        if self._keyword_history:
            history_label = ttk.Label(
                self,
                text="History:",
                foreground=AppTheme.COLORS['text']
            )
            history_label.grid(row=5, column=0, sticky=tk.W, pady=(AppTheme.PADDING['medium'], AppTheme.PADDING['small']))

            # Create grid layout
            self._create_grid_layout(self)
            
            # Populate grid
            self._populate_history()
            
            # Schedule a delayed recalculation to ensure canvas is rendered
            self.after(100, self._calculate_grid_positions)

        # Active keywords section
        active_label = ttk.Label(
            self,
            text="Active Keywords:",
            foreground=AppTheme.COLORS['text']
        )
        active_label.grid(row=7, column=0, sticky=tk.W, pady=(AppTheme.PADDING['medium'], AppTheme.PADDING['small']))

        # Active keywords frame (scrollable)
        self.active_frame = ttk.Frame(self, relief='solid', borderwidth=1)
        self.active_frame.grid(row=8, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
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
        clear_frame.grid(row=9, column=0, sticky=(tk.W, tk.E))
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

    def _build_presets_section(self):
        """Build the presets section with header, cards container, and create button."""
        # Presets header (row 2)
        self.presets_header_label = self._build_presets_header()
        self.presets_header_label.grid(
            row=2, 
            column=0, 
            sticky=tk.W, 
            pady=(AppTheme.PADDING['medium'], AppTheme.PADDING['small'])
        )
        
        # Container frame for canvas + scrollbar (row 3)
        presets_container = ttk.Frame(self)
        presets_container.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['small']))
        presets_container.columnconfigure(0, weight=1)
        
        # Preset cards container (inside the container frame)
        self.presets_canvas, self.presets_scrollbar, self.presets_cards_frame = self._build_preset_cards_container(presets_container)
        
        self.presets_canvas.grid(row=0, column=0, sticky=(tk.W, tk.E))
        self.presets_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Store container reference
        self.presets_container = presets_container
        
        # Initially hide the container (collapsed by default)
        if not self._presets_expanded:
            presets_container.grid_remove()
        
        # Create New Preset button (row 4)
        self.create_preset_button = ttk.Button(
            self,
            text="+ Create New Preset",
            command=self._on_create_preset_clicked
        )
        self.create_preset_button.grid(
            row=4, 
            column=0, 
            sticky=tk.W, 
            pady=(0, AppTheme.PADDING['medium'])
        )
        # Initially disabled (no active keywords)
        self.create_preset_button.state(['disabled'])

    def _build_presets_header(self) -> ttk.Label:
        """Build collapsible header for presets section."""
        header = ttk.Label(
            self,
            text=self._get_header_text(),
            foreground=AppTheme.COLORS['text'],
            font=AppTheme.FONTS['body_bold'],
            cursor='hand2'
        )
        header.bind('<Button-1>', self._toggle_presets_section)
        return header
    
    def _get_header_text(self) -> str:
        """Get header text based on expanded state and preset count."""
        preset_count = len(self._presets)
        if self._presets_expanded:
            return "Presets ▲"
        else:
            return f"Presets ▼ ({preset_count} saved)"
    
    def _update_header_text(self):
        """Update header text with preset count."""
        if hasattr(self, 'presets_header_label'):
            self.presets_header_label.configure(text=self._get_header_text())
    
    def _toggle_presets_section(self, event=None):
        """Toggle presets section expanded/collapsed state."""
        self._presets_expanded = not self._presets_expanded
        
        # Show/hide container
        if self._presets_expanded:
            self.presets_container.grid()
        else:
            self.presets_container.grid_remove()
        
        # Update header text
        self._update_header_text()
        
        # Notify controller to persist state
        if self._presets_section_toggle_callback:
            self._presets_section_toggle_callback(self._presets_expanded)
    
    def _build_preset_cards_container(self, parent) -> tuple[tk.Canvas, ttk.Scrollbar, tk.Frame]:
        """Build scrollable container for preset cards.
        
        Args:
            parent: Parent widget for the container
        
        Returns:
            (canvas, scrollbar, cards_frame)
        """
        # Canvas with max height 200px
        canvas = tk.Canvas(
            parent,
            bg=AppTheme.COLORS['bg'],
            highlightthickness=0,
            height=200
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Cards frame (attached to canvas)
        cards_frame = tk.Frame(canvas, bg=AppTheme.COLORS['bg'])
        self._canvas_window = canvas.create_window((0, 0), window=cards_frame, anchor='nw')
        
        # Bind resize events
        cards_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))
        canvas.bind('<Configure>', lambda e: self._on_canvas_resize(e))
        
        # Store reference to canvas for resize handling
        self._cards_canvas = canvas
        
        return canvas, scrollbar, cards_frame
    
    def _format_keywords_preview(self, keywords: list[str]) -> str:
        """Format keyword preview text.
        
        Args:
            keywords: List of keywords
            
        Returns:
            "kw1, kw2, kw3" or "kw1, kw2, kw3, +N more"
        """
        if len(keywords) <= 3:
            return ", ".join(keywords)
        else:
            first_three = ", ".join(keywords[:3])
            remaining = len(keywords) - 3
            return f"{first_three}, +{remaining} more"
    
    def _create_preset_card(self, preset: dict) -> tk.Frame:
        """Create preset card widget.
        
        Args:
            preset: Preset dict {"name": str, "keywords": list[str]}
            
        Returns:
            Frame containing card layout
        """
        # Card frame with styling
        card = tk.Frame(
            self.presets_cards_frame,
            bg=AppTheme.COLORS['bg_secondary'],
            relief='solid',
            borderwidth=1,
            padx=AppTheme.PADDING['medium'],
            pady=AppTheme.PADDING['medium']
        )
        card.columnconfigure(0, weight=1)
        
        # Top row: Name and buttons
        top_frame = tk.Frame(card, bg=AppTheme.COLORS['bg_secondary'])
        top_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        top_frame.columnconfigure(0, weight=1)
        
        # Name label (bold, 14px)
        name_label = tk.Label(
            top_frame,
            text=preset['name'],
            bg=AppTheme.COLORS['bg_secondary'],
            fg=AppTheme.COLORS['text'],
            font=AppTheme.FONTS['title'],
            anchor='w'
        )
        name_label.grid(row=0, column=0, sticky=tk.W)
        
        # Load button
        load_button = ttk.Button(
            top_frame,
            text="Load",
            command=lambda: self._on_load_preset_clicked(preset['name'])
        )
        load_button.grid(row=0, column=1, padx=(AppTheme.PADDING['small'], 0))
        
        # Menu button (⋮)
        menu_button = tk.Button(
            top_frame,
            text="⋮",
            bg=AppTheme.COLORS['bg_secondary'],
            fg=AppTheme.COLORS['text'],
            font=AppTheme.FONTS['body_bold'],
            relief='flat',
            borderwidth=0,
            cursor='hand2',
            command=lambda: self._show_preset_menu(preset['name'], menu_button)
        )
        menu_button.grid(row=0, column=2, padx=(AppTheme.PADDING['small'], 0))
        
        # Keywords preview
        preview_text = self._format_keywords_preview(preset['keywords'])
        preview_label = tk.Label(
            card,
            text=preview_text,
            bg=AppTheme.COLORS['bg_secondary'],
            fg=AppTheme.COLORS['text'],
            font=AppTheme.FONTS['body'],
            anchor='w',
            wraplength=220  # Allow text to wrap within card
        )
        preview_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(AppTheme.PADDING['small'], 0))
        
        return card
    
    def _render_preset_cards(self):
        """Render all preset cards in container with horizontal flow layout."""
        # Clear existing cards
        for widget in self.presets_cards_frame.winfo_children():
            widget.destroy()
        
        if not self._presets:
            # Show empty state
            self._show_empty_state()
        else:
            # Store preset cards for re-layout
            self._preset_card_widgets = []
            
            # Create all cards
            for preset in self._presets:
                card = self._create_preset_card(preset)
                self._preset_card_widgets.append(card)
            
            # Layout cards in grid (will be called again on resize)
            self._layout_preset_cards()
    
    def _layout_preset_cards(self):
        """Layout preset cards in a horizontal flow grid."""
        if not hasattr(self, '_preset_card_widgets') or not self._preset_card_widgets:
            return
        
        # Get canvas width (use stored canvas reference)
        canvas_width = getattr(self, '_cards_canvas', None)
        if canvas_width:
            canvas_width = canvas_width.winfo_width()
        else:
            canvas_width = 800  # Default fallback
        
        # Card width (approximate) - adjust based on your design
        # Each card is ~250px wide with padding
        card_width = 250
        padding = 8  # Padding between cards
        
        # Calculate number of columns that fit
        num_columns = max(1, int((canvas_width - 20) / (card_width + padding)))
        
        # Layout cards in grid
        row = 0
        col = 0
        for card in self._preset_card_widgets:
            card.grid(row=row, column=col, padx=4, pady=4, sticky=(tk.W, tk.E, tk.N))
            
            col += 1
            if col >= num_columns:
                col = 0
                row += 1
        
        # Configure column weights for equal distribution
        for i in range(num_columns):
            self.presets_cards_frame.columnconfigure(i, weight=1, minsize=card_width)
    
    def _on_canvas_resize(self, event):
        """Handle canvas resize to re-layout cards."""
        # Update canvas window width to match canvas width
        if hasattr(self, '_cards_canvas') and hasattr(self, '_canvas_window'):
            canvas_width = event.width
            self._cards_canvas.itemconfig(self._canvas_window, width=canvas_width)
        
        # Re-layout cards when canvas width changes
        if hasattr(self, '_preset_card_widgets') and self._preset_card_widgets:
            # Schedule re-layout to avoid too many updates
            if hasattr(self, '_layout_timer'):
                self.after_cancel(self._layout_timer)
            self._layout_timer = self.after(100, self._layout_preset_cards)
    
    def _show_empty_state(self):
        """Show empty state message when no presets exist."""
        empty_label = tk.Label(
            self.presets_cards_frame,
            text="No presets saved. Create one from your active keywords.",
            bg=AppTheme.COLORS['bg'],
            fg=AppTheme.COLORS['text'],
            font=AppTheme.FONTS['body'],
            pady=AppTheme.PADDING['large']
        )
        empty_label.pack()
    
    def _show_preset_menu(self, preset_name: str, button_widget):
        """Show preset menu (Edit/Delete) near the button."""
        import tkinter.messagebox as messagebox
        
        # Create popup menu
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Edit", command=lambda: self._show_edit_dialog(preset_name))
        menu.add_command(label="Delete", command=lambda: self._show_delete_confirmation(preset_name))
        
        # Show menu at button position
        try:
            x = button_widget.winfo_rootx()
            y = button_widget.winfo_rooty() + button_widget.winfo_height()
            menu.tk_popup(x, y)
        finally:
            menu.grab_release()
    
    def _on_create_preset_clicked(self):
        """Handle Create New Preset button click."""
        self._show_create_dialog()
    
    def _on_load_preset_clicked(self, preset_name: str):
        """Handle Load button click on preset card."""
        print(f"DEBUG KeywordPanel: Load clicked for preset '{preset_name}'")
        print(f"DEBUG KeywordPanel: Active keywords: {len(self._active_keywords)}")
        print(f"DEBUG KeywordPanel: Load callback registered: {self._preset_load_callback is not None}")
        
        # Check if there are active keywords
        if self._active_keywords:
            # Show confirmation
            print(f"DEBUG KeywordPanel: Showing confirmation dialog")
            if self._show_load_confirmation(preset_name):
                print(f"DEBUG KeywordPanel: Confirmation accepted, calling callback")
                # Load preset
                if self._preset_load_callback:
                    self._preset_load_callback(preset_name)
            else:
                print(f"DEBUG KeywordPanel: Confirmation cancelled")
        else:
            # No active keywords, load directly
            print(f"DEBUG KeywordPanel: No active keywords, loading directly")
            if self._preset_load_callback:
                self._preset_load_callback(preset_name)
            else:
                print(f"DEBUG KeywordPanel: ERROR - No callback registered!")
    
    def _update_create_button_state(self):
        """Enable/disable Create button based on active keywords."""
        if hasattr(self, 'create_preset_button'):
            if len(self._active_keywords) > 0:
                self.create_preset_button.state(['!disabled'])
            else:
                self.create_preset_button.state(['disabled'])
    
    def _show_create_dialog(self):
        """Show Create Preset dialog."""
        import tkinter.messagebox as messagebox
        
        # Create modal dialog
        dialog = tk.Toplevel(self)
        dialog.title("Create Preset")
        dialog.geometry("400x250")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content frame
        content = ttk.Frame(dialog, padding=AppTheme.PADDING['large'])
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)
        
        # Preset Name label and entry
        name_label = ttk.Label(content, text="Preset Name:")
        name_label.grid(row=0, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['small']))
        
        name_entry = ttk.Entry(content, width=40)
        name_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['small']))
        name_entry.focus()
        
        # Error label (initially empty)
        error_label = ttk.Label(content, text="", foreground='red')
        error_label.grid(row=2, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['medium']))
        
        # Keywords label
        kw_label = ttk.Label(content, text="Keywords (current active):")
        kw_label.grid(row=3, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['small']))
        
        # Keywords display (read-only)
        keywords_text = ", ".join(self._active_keywords)
        keywords_display = ttk.Label(
            content, 
            text=keywords_text,
            wraplength=350,
            justify=tk.LEFT
        )
        keywords_display.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
        
        # Validation function
        def validate_and_update():
            name = name_entry.get().strip()
            if not name:
                error_label.configure(text="")
                save_button.state(['disabled'])
                return
            
            # Validate via Configuration (we'll need to get config from callback)
            # For now, do basic validation here
            import re
            if len(name) > 50:
                error_label.configure(text="Name must be 1-50 characters")
                save_button.state(['disabled'])
            elif not re.match(r'^[a-zA-Z0-9 ]+$', name):
                error_label.configure(text="Name can only contain letters, numbers, and spaces")
                save_button.state(['disabled'])
            elif any(p['name'].lower() == name.lower() for p in self._presets):
                error_label.configure(text="Preset name already exists")
                save_button.state(['disabled'])
            else:
                error_label.configure(text="")
                save_button.state(['!disabled'])
        
        # Bind validation to entry changes
        name_entry.bind('<KeyRelease>', lambda e: validate_and_update())
        
        # Buttons frame
        buttons_frame = ttk.Frame(content)
        buttons_frame.grid(row=5, column=0, sticky=tk.E)
        
        # Cancel button
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.grid(row=0, column=0, padx=(0, AppTheme.PADDING['small']))
        
        # Save button
        def on_save():
            name = name_entry.get().strip()
            if name and self._preset_create_callback:
                self._preset_create_callback(name, self._active_keywords.copy())
            dialog.destroy()
        
        save_button = ttk.Button(
            buttons_frame,
            text="Save",
            command=on_save
        )
        save_button.grid(row=0, column=1)
        save_button.state(['disabled'])  # Initially disabled
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _show_edit_dialog(self, preset_name: str):
        """Show Edit Preset dialog.
        
        Args:
            preset_name: Name of preset to edit
        """
        import tkinter.messagebox as messagebox
        
        # Get preset data
        preset = None
        for p in self._presets:
            if p['name'].lower() == preset_name.lower():
                preset = p.copy()
                break
        
        if not preset:
            messagebox.showerror("Error", f"Preset '{preset_name}' not found")
            return
        
        # Create modal dialog
        dialog = tk.Toplevel(self)
        dialog.title("Edit Preset")
        dialog.geometry("400x350")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Dialog content frame
        content = ttk.Frame(dialog, padding=AppTheme.PADDING['large'])
        content.pack(fill=tk.BOTH, expand=True)
        content.columnconfigure(0, weight=1)
        
        # Preset Name label and entry
        name_label = ttk.Label(content, text="Preset Name:")
        name_label.grid(row=0, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['small']))
        
        name_entry = ttk.Entry(content, width=40)
        name_entry.insert(0, preset['name'])
        name_entry.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['small']))
        name_entry.focus()
        
        # Error label (initially empty)
        error_label = ttk.Label(content, text="", foreground='red')
        error_label.grid(row=2, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['medium']))
        
        # Keywords label
        kw_label = ttk.Label(content, text="Keywords:")
        kw_label.grid(row=3, column=0, sticky=tk.W, pady=(0, AppTheme.PADDING['small']))
        
        # Keywords frame with chips
        keywords_frame = ttk.Frame(content, relief='solid', borderwidth=1)
        keywords_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['small']))
        
        # Track keywords
        edit_keywords = preset['keywords'].copy()
        
        def render_keyword_chips():
            # Clear frame
            for widget in keywords_frame.winfo_children():
                widget.destroy()
            
            # Create chips
            chips_container = ttk.Frame(keywords_frame, padding=AppTheme.PADDING['small'])
            chips_container.pack(fill=tk.BOTH, expand=True)
            
            for i, kw in enumerate(edit_keywords):
                chip = tk.Frame(chips_container, relief='solid', borderwidth=1, bg=AppTheme.COLORS['primary_light'])
                chip.grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky=tk.W)
                
                label = tk.Label(chip, text=kw, bg=AppTheme.COLORS['primary_light'], padx=4, pady=2)
                label.pack(side=tk.LEFT)
                
                remove_btn = tk.Button(
                    chip, text="×", bg=AppTheme.COLORS['primary_light'],
                    fg=AppTheme.COLORS['error'], relief='flat', borderwidth=0,
                    command=lambda keyword=kw: remove_keyword(keyword)
                )
                remove_btn.pack(side=tk.LEFT, padx=(0, 4))
        
        def remove_keyword(keyword):
            if keyword in edit_keywords:
                edit_keywords.remove(keyword)
                render_keyword_chips()
                validate_and_update()
        
        render_keyword_chips()
        
        # Add keyword entry
        add_kw_frame = ttk.Frame(content)
        add_kw_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(0, AppTheme.PADDING['medium']))
        add_kw_frame.columnconfigure(0, weight=1)
        
        add_kw_entry = ttk.Entry(add_kw_frame)
        add_kw_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, AppTheme.PADDING['small']))
        
        def add_keyword():
            kw = add_kw_entry.get().strip()
            if kw and kw not in edit_keywords and len(kw) <= 100:
                edit_keywords.append(kw)
                add_kw_entry.delete(0, tk.END)
                render_keyword_chips()
                validate_and_update()
        
        add_kw_button = ttk.Button(add_kw_frame, text="+ Add", command=add_keyword)
        add_kw_button.grid(row=0, column=1)
        add_kw_entry.bind('<Return>', lambda e: add_keyword())
        
        # Validation function
        def validate_and_update():
            name = name_entry.get().strip()
            if not name:
                error_label.configure(text="")
                save_button.state(['disabled'])
                return
            
            if not edit_keywords:
                error_label.configure(text="Must have at least one keyword")
                save_button.state(['disabled'])
                return
            
            # Validate name
            import re
            if len(name) > 50:
                error_label.configure(text="Name must be 1-50 characters")
                save_button.state(['disabled'])
            elif not re.match(r'^[a-zA-Z0-9 ]+$', name):
                error_label.configure(text="Name can only contain letters, numbers, and spaces")
                save_button.state(['disabled'])
            elif name.lower() != preset['name'].lower() and any(p['name'].lower() == name.lower() for p in self._presets):
                error_label.configure(text="Preset name already exists")
                save_button.state(['disabled'])
            else:
                error_label.configure(text="")
                save_button.state(['!disabled'])
        
        # Bind validation to entry changes
        name_entry.bind('<KeyRelease>', lambda e: validate_and_update())
        
        # Buttons frame
        buttons_frame = ttk.Frame(content)
        buttons_frame.grid(row=6, column=0, sticky=tk.E)
        
        # Cancel button
        cancel_button = ttk.Button(
            buttons_frame,
            text="Cancel",
            command=dialog.destroy
        )
        cancel_button.grid(row=0, column=0, padx=(0, AppTheme.PADDING['small']))
        
        # Save button
        def on_save():
            new_name = name_entry.get().strip()
            if new_name and edit_keywords and self._preset_edit_callback:
                self._preset_edit_callback(preset['name'], new_name, edit_keywords.copy())
            dialog.destroy()
        
        save_button = ttk.Button(
            buttons_frame,
            text="Save",
            command=on_save
        )
        save_button.grid(row=0, column=1)
        
        # Initial validation
        validate_and_update()
        
        # Wait for dialog to close
        dialog.wait_window()
    
    def _show_delete_confirmation(self, preset_name: str):
        """Show delete confirmation dialog.
        
        Args:
            preset_name: Name of preset to delete
        """
        from tkinter import messagebox
        
        result = messagebox.askyesno(
            "Delete Preset",
            f"Delete preset '{preset_name}'?",
            icon='warning'
        )
        
        if result and self._preset_delete_callback:
            self._preset_delete_callback(preset_name)
    
    def _show_load_confirmation(self, preset_name: str) -> bool:
        """Show load confirmation dialog.
        
        Args:
            preset_name: Name of preset to load
            
        Returns:
            True if user confirmed, False if cancelled
        """
        from tkinter import messagebox
        
        return messagebox.askyesno(
            "Load Preset",
            f"Replace current keywords with preset '{preset_name}'?",
            icon='question'
        )

    def _create_grid_layout(self, parent):
        """Initialize grid layout structure (Canvas + Frame + Scrollbar)."""
        # Container frame for canvas + scrollbar
        history_frame = ttk.Frame(parent)
        history_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), 
                           pady=(0, AppTheme.PADDING['medium']))
        history_frame.columnconfigure(0, weight=1)
        
        # Canvas for scrolling
        self.grid_container = tk.Canvas(
            history_frame,
            bg=AppTheme.COLORS['bg'],
            highlightthickness=0
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL,
                                 command=self.grid_container.yview)
        self.grid_container.configure(yscrollcommand=scrollbar.set)
        
        # Grid frame (attached to canvas)
        self.grid_frame = tk.Frame(self.grid_container, bg=AppTheme.COLORS['bg'])
        self.grid_window = self.grid_container.create_window((0, 0), window=self.grid_frame, anchor='nw')
        
        # Layout
        self.grid_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Bind resize event
        self.grid_container.bind('<Configure>', self._on_resize_grid)
        
        # Initialize state
        self.grid_items = []
        self._resize_job = None

    def _calculate_grid_positions(self):
        """Calculate and apply flow/wrap positions for all grid items."""
        print(f"[DEBUG] _calculate_grid_positions called, items: {len(self.grid_items) if hasattr(self, 'grid_items') else 0}")
        if not self.grid_items or not self.grid_container.winfo_exists():
            print(f"[DEBUG] Returning early - no items or container doesn't exist")
            return
        
        # Constants
        ITEM_SPACING = 8
        ROW_SPACING = 8
        MAX_GRID_HEIGHT = 200
        MIN_CONTAINER_WIDTH = 200  # Minimum width to avoid layout issues
        
        # Get container width (use winfo_width, fallback to reqwidth)
        container_width = self.grid_container.winfo_width()
        if container_width <= 1:
            container_width = self.grid_container.winfo_reqwidth()
        
        # Fallback to parent width if still too small
        if container_width < MIN_CONTAINER_WIDTH:
            try:
                container_width = self.winfo_width() - 40  # Account for padding
                if container_width < MIN_CONTAINER_WIDTH:
                    container_width = 600  # Safe default
            except:
                container_width = 600
        
        # Position calculation
        current_x = 0
        current_y = 0
        row_height = 0
        
        for i, label in enumerate(self.grid_items):
            # Update geometry
            label.update_idletasks()
            item_width = label.winfo_reqwidth()
            item_height = label.winfo_reqheight()
            
            if i == 0:  # Debug first item
                print(f"[DEBUG] First item: width={item_width}, height={item_height}, text='{label.cget('text')}'")
            
            # Wrap to next row if needed
            if current_x + item_width > container_width and current_x > 0:
                current_x = 0
                current_y += row_height + ROW_SPACING
                row_height = 0
            
            # Place label
            label.place(x=current_x, y=current_y)
            
            if i == 0:  # Debug first item placement
                print(f"[DEBUG] First item placed at: x={current_x}, y={current_y}")
            
            # Update tracking
            current_x += item_width + ITEM_SPACING
            row_height = max(row_height, item_height)
        
        # Set canvas height (ensure minimum height if items exist)
        actual_height = current_y + row_height
        if actual_height < 30 and self.grid_items:  # Minimum height for one row
            actual_height = 30
        canvas_height = min(actual_height, MAX_GRID_HEIGHT)
        
        print(f"[DEBUG] Container width: {container_width}, actual_height: {actual_height}, canvas_height: {canvas_height}")
        
        self.grid_container.configure(height=canvas_height)
        
        # Update grid frame size to match content
        self.grid_frame.configure(width=container_width, height=actual_height)
        
        # Update scroll region
        self.grid_container.configure(scrollregion=(0, 0, container_width, actual_height))
        
        # Force update
        self.grid_frame.update_idletasks()
        self.grid_container.update_idletasks()

    def _populate_history(self):
        """Populate grid with keyword items from history."""
        print(f"[DEBUG] _populate_history called")
        print(f"[DEBUG] Has grid_frame: {hasattr(self, 'grid_frame')}")
        if hasattr(self, 'grid_frame'):
            print(f"[DEBUG] grid_frame exists: {self.grid_frame.winfo_exists()}")
        
        if not hasattr(self, 'grid_frame') or not self.grid_frame.winfo_exists():
            print(f"[DEBUG] Returning early - no grid_frame")
            return
        
        # Clear existing items
        for item in self.grid_items:
            item.destroy()
        self.grid_items.clear()
        
        # Get keywords, filter out active ones
        history_keywords = self._keyword_history
        active_keyword_texts = self._active_keywords
        available_keywords = [kw for kw in history_keywords if kw not in active_keyword_texts]
        
        print(f"[DEBUG] History keywords: {history_keywords}")
        print(f"[DEBUG] Active keywords: {active_keyword_texts}")
        print(f"[DEBUG] Available keywords: {available_keywords}")
        
        # Create grid items
        for keyword in available_keywords:
            label = tk.Label(
                self.grid_frame,
                text=keyword,
                bg=AppTheme.COLORS['primary_light'],
                fg=AppTheme.COLORS['text'],
                font=AppTheme.FONTS['body'],
                padx=AppTheme.PADDING['medium'],
                pady=AppTheme.PADDING['small'],
                cursor='hand2',
                relief='solid',
                borderwidth=1
            )
            
            # Hover bindings
            label.bind('<Enter>', lambda e, lbl=label: 
                       lbl.configure(bg=AppTheme.COLORS['bg_hover']))
            label.bind('<Leave>', lambda e, lbl=label: 
                       lbl.configure(bg=AppTheme.COLORS['primary_light']))
            
            # Click binding
            label.bind('<Button-1>', lambda e, kw=keyword: self._on_grid_item_click(kw))
            
            self.grid_items.append(label)
        
        print(f"[DEBUG] Created {len(self.grid_items)} grid items")
        
        # Layout items
        self._calculate_grid_positions()

    def _on_grid_item_click(self, keyword_text):
        """Handle single click on grid item (immediate add workflow)."""
        # Add to active keywords
        self._add_active_keyword(keyword_text)
        
        # Remove from grid display
        self._remove_from_history_display(keyword_text)
        
        # Optional: Notify controller
        if self._keyword_selected_from_history_callback:
            self._keyword_selected_from_history_callback(keyword_text)

    def _remove_from_history_display(self, keyword_text):
        """Remove specific keyword from grid display."""
        # Find and destroy matching label
        for label in self.grid_items[:]:  # Copy list to avoid modification during iteration
            if label.cget('text') == keyword_text:
                label.destroy()
                self.grid_items.remove(label)
                break
        
        # Reflow remaining items
        self._calculate_grid_positions()

    def _on_resize_grid(self, event):
        """Handle Canvas resize event with debounce."""
        # Cancel previous resize job
        if self._resize_job:
            self.after_cancel(self._resize_job)
        
        # Schedule new layout calculation (100ms delay)
        self._resize_job = self.after(100, self._calculate_grid_positions)

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
            if hasattr(self, 'grid_frame') and self.grid_frame:
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
        if hasattr(self, 'grid_frame') and self.grid_frame:
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

        # Update create preset button state
        self._update_create_button_state()

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

    def destroy(self):
        """Clean up grid resources."""
        # Cancel pending resize job
        if hasattr(self, '_resize_job') and self._resize_job:
            self.after_cancel(self._resize_job)
        
        # Destroy grid items
        if hasattr(self, 'grid_items'):
            for item in self.grid_items:
                item.destroy()
            self.grid_items.clear()
        
        # Call parent destroy
        super().destroy()

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
        if hasattr(self, 'grid_frame') and self.grid_frame:
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
        if hasattr(self, 'grid_frame') and self.grid_frame:
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
    
    # Preset callbacks
    def on_preset_create(self, callback):
        """Register callback for preset creation.
        
        Args:
            callback: Function(name: str, keywords: list[str]) -> None
        """
        self._preset_create_callback = callback
    
    def on_preset_load(self, callback):
        """Register callback for preset loading.
        
        Args:
            callback: Function(preset_name: str) -> None
        """
        self._preset_load_callback = callback
    
    def on_preset_edit(self, callback):
        """Register callback for preset editing.
        
        Args:
            callback: Function(old_name: str, new_name: str, keywords: list[str]) -> None
        """
        self._preset_edit_callback = callback
    
    def on_preset_delete(self, callback):
        """Register callback for preset deletion.
        
        Args:
            callback: Function(name: str) -> None
        """
        self._preset_delete_callback = callback
    
    def on_presets_section_toggled(self, callback):
        """Register callback for section toggle.
        
        Args:
            callback: Function(expanded: bool) -> None
        """
        self._presets_section_toggle_callback = callback
    
    # Preset public methods
    def refresh_presets(self, presets: list[dict]):
        """Update preset cards display.
        
        Args:
            presets: List of preset dicts from Configuration
        """
        self._presets = [preset.copy() for preset in presets]
        self._render_preset_cards()
        self._update_header_text()
    
    def set_presets_expanded(self, expanded: bool):
        """Set presets section expanded/collapsed.
        
        Args:
            expanded: True to expand, False to collapse
        """
        self._presets_expanded = expanded
        # Update visibility
        if hasattr(self, 'presets_container'):
            if self._presets_expanded:
                self.presets_container.grid()
            else:
                self.presets_container.grid_remove()
        self._update_header_text()
