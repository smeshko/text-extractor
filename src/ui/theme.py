"""Theme - Centralized styling and color palette for the application."""

from tkinter import ttk
import sys
import platform


class AppTheme:
    """Application theme with color palette and style definitions."""

    # Track current theme state
    _current_dark_mode = False
    _root_window = None
    _theme_check_job = None

    # Light mode color palette
    COLORS_LIGHT = {
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
        'text_disabled': '#9CA3AF',     # Very light gray text for disabled state
        'border': '#D1D5DB',            # Light gray border
        'border_light': '#E5E7EB',      # Very light gray border
        'bg': '#FFFFFF',                # White background
        'bg_secondary': '#F8F9FA',      # Light gray background
        'bg_disabled': '#E5E7EB',       # Disabled background (more obvious)
        'bg_hover': '#F0F0F0',          # Hover background
    }

    # Dark mode color palette
    COLORS_DARK = {
        # Primary colors
        'primary': '#5BA3F5',           # Brighter blue for dark mode
        'primary_dark': '#4A90E2',      # Medium blue for hover
        'primary_light': '#2D3748',     # Dark blue-gray

        # Status colors
        'success': '#68D391',           # Brighter green
        'success_bg': '#2C5F2D',        # Dark green background
        'warning': '#F6AD55',           # Brighter orange
        'warning_bg': '#5F4C1F',        # Dark yellow background
        'error': '#FC8181',             # Brighter red
        'error_bg': '#5F2120',          # Dark red background

        # Neutrals
        'text': '#E2E8F0',              # Light gray text
        'text_muted': '#A0AEC0',        # Muted light gray text
        'text_disabled': '#718096',     # Disabled text (lighter for better contrast)
        'border': '#4A5568',            # Medium gray border
        'border_light': '#2D3748',      # Dark gray border
        'bg': '#1A202C',                # Dark background
        'bg_secondary': '#2D3748',      # Darker gray background
        'bg_disabled': '#374151',       # Disabled background
        'bg_hover': '#374151',          # Hover background
    }

    # Active color palette (will be set based on system theme)
    COLORS = COLORS_LIGHT.copy()

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
    def _detect_dark_mode(cls, root):
        """Detect if system is in dark mode.
        
        Args:
            root: Root Tk window
            
        Returns:
            bool: True if dark mode is detected, False otherwise
        """
        try:
            # macOS dark mode detection
            if platform.system() == 'Darwin':
                try:
                    import subprocess
                    result = subprocess.run(
                        ['defaults', 'read', '-g', 'AppleInterfaceStyle'],
                        capture_output=True,
                        text=True,
                        timeout=1
                    )
                    # In light mode, the key doesn't exist (returncode != 0)
                    # In dark mode, the key exists and contains "Dark"
                    if result.returncode == 0 and 'Dark' in result.stdout:
                        return True
                    return False
                except Exception:
                    # If command fails, check tkinter appearance
                    pass
            
            # Windows dark mode detection
            elif platform.system() == 'Windows':
                try:
                    import winreg
                    registry = winreg.ConnectRegistry(None, winreg.HKEY_CURRENT_USER)
                    key = winreg.OpenKey(registry, r'Software\Microsoft\Windows\CurrentVersion\Themes\Personalize')
                    value, _ = winreg.QueryValueEx(key, 'AppsUseLightTheme')
                    winreg.CloseKey(key)
                    # AppsUseLightTheme: 0 = dark mode, 1 = light mode
                    return value == 0
                except Exception:
                    pass
            
            # Fallback: Check if tkinter is using a dark theme
            # This is a last resort and may not be reliable
            try:
                # On macOS, check the system appearance through tkinter
                if platform.system() == 'Darwin':
                    # Try to call tk::unsupported::MacWindowStyle
                    result = root.tk.call('tk::unsupported::MacWindowStyle', 'isdark', root)
                    return bool(result)
            except Exception:
                pass
                
        except Exception:
            pass
        
        # Default to light mode if detection fails
        return False

    @classmethod
    def _update_colors(cls, is_dark_mode):
        """Update the active color palette.
        
        Args:
            is_dark_mode: Whether to use dark mode colors
        """
        if is_dark_mode:
            cls.COLORS = cls.COLORS_DARK.copy()
        else:
            cls.COLORS = cls.COLORS_LIGHT.copy()

    @classmethod
    def configure_styles(cls, root):
        """Configure ttk styles for the application.

        Args:
            root: Root Tk window
        """
        # Store root window reference
        cls._root_window = root
        
        # Detect and apply color scheme
        is_dark_mode = cls._detect_dark_mode(root)
        cls._current_dark_mode = is_dark_mode
        cls._update_colors(is_dark_mode)
        
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
            font=cls.FONTS['body_bold']
        )
        style.map(
            'Primary.TButton',
            foreground=[
                ('disabled', cls.COLORS['text_disabled']),
                ('pressed', 'white'),
                ('active', 'white'),
                ('!disabled', 'white')
            ],
            background=[
                ('pressed', cls.COLORS['primary_dark']),
                ('active', cls.COLORS['primary_dark']),
                ('!disabled', cls.COLORS['primary']),
                ('disabled', cls.COLORS['bg_disabled'])
            ]
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
            foreground=[('disabled', cls.COLORS['text_disabled'])],
            background=[('disabled', cls.COLORS['bg_disabled'])]
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
    def _apply_styles(cls):
        """Apply/reapply all ttk styles with current colors."""
        style = ttk.Style()
        
        # Title label
        style.configure('Title.TLabel', foreground=cls.COLORS['text'])
        style.configure('Section.TLabel', foreground=cls.COLORS['text'])
        style.configure('TLabel', foreground=cls.COLORS['text'])
        style.configure('Muted.TLabel', foreground=cls.COLORS['text_muted'])
        
        # Buttons
        style.map(
            'Primary.TButton',
            foreground=[
                ('disabled', cls.COLORS['text_disabled']),
                ('pressed', 'white'),
                ('active', 'white'),
                ('!disabled', 'white')
            ],
            background=[
                ('pressed', cls.COLORS['primary_dark']),
                ('active', cls.COLORS['primary_dark']),
                ('!disabled', cls.COLORS['primary']),
                ('disabled', cls.COLORS['bg_disabled'])
            ]
        )
        style.map(
            'TButton',
            foreground=[('disabled', cls.COLORS['text_disabled'])],
            background=[('disabled', cls.COLORS['bg_disabled'])]
        )
        
        # Frames
        style.configure('Panel.TFrame', background=cls.COLORS['bg'])
        style.configure('Section.TFrame', background=cls.COLORS['bg_secondary'])
        style.configure('Success.TFrame', background=cls.COLORS['success_bg'])
        style.configure('Warning.TFrame', background=cls.COLORS['warning_bg'])
        style.configure('Error.TFrame', background=cls.COLORS['error_bg'])
        
        # Entry and Combobox
        style.configure('TEntry', fieldbackground=cls.COLORS['bg'])
        style.configure('TCombobox', fieldbackground=cls.COLORS['bg'])

    @classmethod
    def _check_theme_change(cls):
        """Periodically check if system theme has changed."""
        if cls._root_window is None:
            return
            
        try:
            # Check if theme changed
            current_is_dark = cls._detect_dark_mode(cls._root_window)
            
            if current_is_dark != cls._current_dark_mode:
                # Theme changed! Update everything
                cls._current_dark_mode = current_is_dark
                cls._update_colors(current_is_dark)
                cls._apply_styles()
                
                # Trigger a complete UI refresh
                cls._refresh_ui(cls._root_window)
        except Exception:
            pass
        
        # Schedule next check (every 1 second)
        if cls._root_window:
            cls._theme_check_job = cls._root_window.after(1000, cls._check_theme_change)

    @classmethod
    def _refresh_ui(cls, widget):
        """Recursively refresh all widgets with new colors.
        
        Args:
            widget: Widget to refresh
        """
        try:
            # Update tk.Label widgets
            if isinstance(widget, __import__('tkinter').Label):
                current_fg = widget.cget('foreground')
                current_bg = widget.cget('background')
                
                # Map old colors to new colors
                if current_fg in (cls.COLORS_LIGHT['text'], cls.COLORS_DARK['text']):
                    widget.configure(foreground=cls.COLORS['text'])
                elif current_fg in (cls.COLORS_LIGHT['text_muted'], cls.COLORS_DARK['text_muted']):
                    widget.configure(foreground=cls.COLORS['text_muted'])
                elif current_fg in (cls.COLORS_LIGHT['success'], cls.COLORS_DARK['success']):
                    widget.configure(foreground=cls.COLORS['success'])
                elif current_fg in (cls.COLORS_LIGHT['warning'], cls.COLORS_DARK['warning']):
                    widget.configure(foreground=cls.COLORS['warning'])
                elif current_fg in (cls.COLORS_LIGHT['error'], cls.COLORS_DARK['error']):
                    widget.configure(foreground=cls.COLORS['error'])
                elif current_fg in (cls.COLORS_LIGHT['primary_dark'], cls.COLORS_DARK['primary_dark']):
                    widget.configure(foreground=cls.COLORS['primary_dark'])
                    
                if current_bg in (cls.COLORS_LIGHT['bg_secondary'], cls.COLORS_DARK['bg_secondary']):
                    widget.configure(background=cls.COLORS['bg_secondary'])
                elif current_bg in (cls.COLORS_LIGHT['primary_light'], cls.COLORS_DARK['primary_light']):
                    widget.configure(background=cls.COLORS['primary_light'])
                elif current_bg in (cls.COLORS_LIGHT['success_bg'], cls.COLORS_DARK['success_bg']):
                    widget.configure(background=cls.COLORS['success_bg'])
                elif current_bg in (cls.COLORS_LIGHT['warning_bg'], cls.COLORS_DARK['warning_bg']):
                    widget.configure(background=cls.COLORS['warning_bg'])
                elif current_bg in (cls.COLORS_LIGHT['error_bg'], cls.COLORS_DARK['error_bg']):
                    widget.configure(background=cls.COLORS['error_bg'])
            
            # Update tk.Frame widgets
            elif isinstance(widget, __import__('tkinter').Frame):
                current_bg = widget.cget('background')
                if current_bg in (cls.COLORS_LIGHT['success_bg'], cls.COLORS_DARK['success_bg']):
                    widget.configure(background=cls.COLORS['success_bg'])
                elif current_bg in (cls.COLORS_LIGHT['warning_bg'], cls.COLORS_DARK['warning_bg']):
                    widget.configure(background=cls.COLORS['warning_bg'])
                elif current_bg in (cls.COLORS_LIGHT['error_bg'], cls.COLORS_DARK['error_bg']):
                    widget.configure(background=cls.COLORS['error_bg'])
                elif current_bg in (cls.COLORS_LIGHT['primary_light'], cls.COLORS_DARK['primary_light']):
                    widget.configure(background=cls.COLORS['primary_light'])
            
            # Update tk.Canvas widgets
            elif isinstance(widget, __import__('tkinter').Canvas):
                current_bg = widget.cget('background')
                if current_bg in (cls.COLORS_LIGHT['bg'], cls.COLORS_DARK['bg']):
                    widget.configure(background=cls.COLORS['bg'])
                elif current_bg in (cls.COLORS_LIGHT['bg_secondary'], cls.COLORS_DARK['bg_secondary']):
                    widget.configure(background=cls.COLORS['bg_secondary'])
            
            # Update tk.Listbox widgets
            elif isinstance(widget, __import__('tkinter').Listbox):
                widget.configure(
                    background=cls.COLORS['bg'],
                    foreground=cls.COLORS['text']
                )
            
            # Update tk.Button widgets (for chip remove buttons)
            elif isinstance(widget, __import__('tkinter').Button):
                current_bg = widget.cget('background')
                current_fg = widget.cget('foreground')
                if current_bg in (cls.COLORS_LIGHT['primary_light'], cls.COLORS_DARK['primary_light']):
                    widget.configure(background=cls.COLORS['primary_light'])
                if current_fg in (cls.COLORS_LIGHT['error'], cls.COLORS_DARK['error']):
                    widget.configure(foreground=cls.COLORS['error'])
            
            # Recursively update children
            for child in widget.winfo_children():
                cls._refresh_ui(child)
                
        except Exception:
            pass

    @classmethod
    def start_theme_monitoring(cls):
        """Start monitoring system theme changes."""
        if cls._root_window and cls._theme_check_job is None:
            cls._check_theme_change()

    @classmethod
    def stop_theme_monitoring(cls):
        """Stop monitoring system theme changes."""
        if cls._theme_check_job:
            cls._root_window.after_cancel(cls._theme_check_job)
            cls._theme_check_job = None

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
