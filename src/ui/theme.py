"""Theme - Centralized styling and color palette for the application."""

from tkinter import ttk


class AppTheme:
    """Application theme with color palette and style definitions."""

    # Color Palette
    COLORS = {
        # Primary colors
        'primary': '#4A90E2',           # Soft blue
        'primary_dark': '#357ABD',      # Darker blue for hover
        'primary_light': '#E8F2FC',     # Very light blue

        # Status colors
        'success': '#5CB85C',           # Green
        'success_bg': '#DFF0D8',        # Light green background
        'warning': '#F0AD4E',           # Orange
        'warning_bg': '#FCF8E3',        # Light yellow background
        'error': '#D9534F',             # Red
        'error_bg': '#F2DEDE',          # Light red background

        # Neutrals
        'text': '#333333',              # Dark gray text
        'text_muted': '#6C757D',        # Muted gray text
        'border': '#D1D5DB',            # Light gray border
        'border_light': '#E5E7EB',      # Very light gray border
        'bg': '#FFFFFF',                # White background
        'bg_secondary': '#F8F9FA',      # Light gray background
        'bg_hover': '#F0F0F0',          # Hover background
    }

    # Typography
    FONTS = {
        'title': ('Segoe UI', 14, 'bold'),
        'section': ('Segoe UI', 11, 'bold'),
        'body': ('Segoe UI', 10),
        'body_bold': ('Segoe UI', 10, 'bold'),
        'small': ('Segoe UI', 9),
        'icon': ('Segoe UI', 16),
        'icon_large': ('Segoe UI', 20),
    }

    # Spacing
    PADDING = {
        'small': 5,
        'medium': 10,
        'large': 15,
        'xlarge': 20,
    }

    @classmethod
    def configure_styles(cls, root):
        """Configure ttk styles for the application.

        Args:
            root: Root Tk window
        """
        style = ttk.Style()

        # Try to use native theme as base
        try:
            style.theme_use('vista')  # Windows
        except:
            try:
                style.theme_use('aqua')  # macOS
            except:
                style.theme_use('default')

        # Title label
        style.configure(
            'Title.TLabel',
            font=cls.FONTS['title'],
            foreground=cls.COLORS['text']
        )

        # Section label
        style.configure(
            'Section.TLabel',
            font=cls.FONTS['section'],
            foreground=cls.COLORS['text']
        )

        # Body label
        style.configure(
            'TLabel',
            font=cls.FONTS['body'],
            foreground=cls.COLORS['text']
        )

        # Muted label
        style.configure(
            'Muted.TLabel',
            font=cls.FONTS['body'],
            foreground=cls.COLORS['text_muted']
        )

        # Primary button
        style.configure(
            'Primary.TButton',
            font=cls.FONTS['body_bold'],
        )
        style.map(
            'Primary.TButton',
            foreground=[('!disabled', cls.COLORS['bg']), ('disabled', cls.COLORS['text_muted'])],
            background=[('!disabled', cls.COLORS['primary']), ('disabled', cls.COLORS['bg_secondary'])]
        )

        # Secondary button
        style.configure(
            'Secondary.TButton',
            font=cls.FONTS['body'],
        )

        # Panel frame with border
        style.configure(
            'Panel.TFrame',
            background=cls.COLORS['bg'],
            borderwidth=1,
            relief='solid'
        )

        # Section frame with background
        style.configure(
            'Section.TFrame',
            background=cls.COLORS['bg_secondary'],
            borderwidth=1,
            relief='solid'
        )

        # Success frame
        style.configure(
            'Success.TFrame',
            background=cls.COLORS['success_bg'],
            borderwidth=1,
            relief='solid'
        )

        # Warning frame
        style.configure(
            'Warning.TFrame',
            background=cls.COLORS['warning_bg'],
            borderwidth=1,
            relief='solid'
        )

        # Error frame
        style.configure(
            'Error.TFrame',
            background=cls.COLORS['error_bg'],
            borderwidth=1,
            relief='solid'
        )

        # Configure button disabled appearance
        style.map(
            'TButton',
            foreground=[('disabled', cls.COLORS['text_muted'])],
            background=[('disabled', cls.COLORS['bg_secondary'])]
        )

        # Entry styling
        style.configure(
            'TEntry',
            fieldbackground=cls.COLORS['bg'],
            borderwidth=1
        )

        # Combobox styling
        style.configure(
            'TCombobox',
            fieldbackground=cls.COLORS['bg'],
            borderwidth=1
        )

    @classmethod
    def get_panel_config(cls):
        """Get configuration dict for panel frames.

        Returns:
            Dict with frame configuration
        """
        return {
            'padding': cls.PADDING['large'],
            'relief': 'solid',
            'borderwidth': 1,
            'style': 'Panel.TFrame'
        }

    @classmethod
    def get_section_config(cls):
        """Get configuration dict for section frames.

        Returns:
            Dict with frame configuration
        """
        return {
            'padding': cls.PADDING['medium'],
            'relief': 'solid',
            'borderwidth': 1,
        }
