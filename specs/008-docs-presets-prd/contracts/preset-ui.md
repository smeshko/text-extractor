# Preset UI Component Contract

**Component**: KeywordPanel (Presets Section)
**File**: `src/ui/keyword_panel.py`
**Purpose**: Render and manage keyword preset UI within KeywordPanel

---

## Component Structure

### Layout Hierarchy

```
KeywordPanel (existing)
  ├── Keywords label (row 0)
  ├── Input field + Add button (row 1)
  ├── PRESETS SECTION (row 2-4) ← NEW
  │   ├── Header (row 2)
  │   │   └── Collapsible label: "Presets ▼ (N saved)" or "Presets ▲"
  │   ├── Preset cards container (row 3)
  │   │   ├── Canvas (scrollable, max height 200px)
  │   │   │   └── Frame with preset cards
  │   │   │       ├── PresetCard 1
  │   │   │       ├── PresetCard 2
  │   │   │       └── ...
  │   │   └── Scrollbar (vertical)
  │   └── Create New Preset button (row 4)
  ├── History section (row 5) ← existing, renumbered
  ├── Active keywords (row 6-7) ← existing, renumbered
  └── Clear All button (row 8) ← existing, renumbered
```

---

## UI Components

### 1. Presets Section Header

**Widget Type**: `ttk.Label`

**States**:
- **Collapsed**: Text = "Presets ▼ (N saved)" where N = number of presets
- **Expanded**: Text = "Presets ▲"

**Behavior**:
- Click toggles expanded/collapsed state
- State persists via `Configuration.presets_section_expanded`
- Cursor changes to hand pointer on hover

**Styling**:
- Font: `AppTheme.FONTS['body_bold']`
- Color: `AppTheme.COLORS['text']`
- Padding: `AppTheme.PADDING['medium']` below

**Code Signature**:
```python
def _build_presets_header(self) -> ttk.Label:
    """Build collapsible header for presets section."""
    pass

def _toggle_presets_section(self, event=None):
    """Toggle presets section expanded/collapsed state."""
    pass

def _update_header_text(self):
    """Update header text with preset count."""
    pass
```

---

### 2. Preset Card

**Widget Type**: `tk.Frame`

**Layout**:
```
┌────────────────────────────────────────────────┐
│ Preset Name (bold 14px)      [Load]  [⋮]      │
│ HTD, RTP, Temperature, +2 more                 │
└────────────────────────────────────────────────┘
```

**Components**:
- Name label: Bold, 14px font
- Keywords preview: First 3 keywords + "+N more" if > 3
- Load button: Primary action
- Menu button (⋮): Opens Edit/Delete menu

**Styling** (per PRD):
- Background: `#F9FAFB` (light gray)
- Border: 1px solid `AppTheme.COLORS['border']`
- Border radius: 8px
- Padding: `AppTheme.PADDING['medium']`
- Spacing between cards: 8px

**States**:
- **Normal**: Default appearance
- **Hover**: Subtle background darkening
- **Active**: No special state (buttons handle their own hover)

**Code Signature**:
```python
def _create_preset_card(self, preset: dict) -> tk.Frame:
    """Create preset card widget.

    Args:
        preset: Preset dict {"name": str, "keywords": list[str]}

    Returns:
        Frame containing card layout
    """
    pass

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
```

---

### 3. Preset Cards Container

**Widget Type**: `tk.Canvas` with scrollable `Frame`

**Specifications**:
- Max height: 200px (per FR-016)
- Vertical scrollbar: Appears when content exceeds 200px
- Empty state: Show message "No presets saved. Create one from your active keywords."

**Behavior**:
- Renders all preset cards vertically
- Scrolling enabled when total height > 200px
- Cards update dynamically on preset CRUD operations

**Code Signature**:
```python
def _build_preset_cards_container(self) -> tuple[tk.Canvas, ttk.Scrollbar, tk.Frame]:
    """Build scrollable container for preset cards.

    Returns:
        (canvas, scrollbar, cards_frame)
    """
    pass

def _render_preset_cards(self):
    """Render all preset cards in container."""
    pass

def _show_empty_state(self):
    """Show empty state message when no presets exist."""
    pass
```

---

### 4. Create New Preset Button

**Widget Type**: `ttk.Button`

**Text**: "+ Create New Preset"
**Color**: Blue text (`#2563EB` per PRD)

**States**:
- **Enabled**: Active keywords exist (count > 0)
- **Disabled**: No active keywords (count = 0)

**Behavior**:
- Click opens Create Preset dialog
- Dialog shows current active keywords (read-only)
- User enters preset name
- Validates name, creates preset, refreshes cards

**Code Signature**:
```python
def _on_create_preset_clicked(self):
    """Handle Create New Preset button click."""
    pass

def _update_create_button_state(self):
    """Enable/disable Create button based on active keywords."""
    if len(self._active_keywords) > 0:
        self.create_preset_button.state(['!disabled'])
    else:
        self.create_preset_button.state(['disabled'])
```

---

## Dialogs

### Create Preset Dialog

**Type**: Modal dialog (tkinter Toplevel)

**Layout**:
```
┌─────────────────────────────────────┐
│ Create Preset                       │
│                                     │
│ Preset Name:                        │
│ [___________________________]       │
│                                     │
│ Keywords (current active):          │
│ HTD, RTP, Temperature               │
│                                     │
│           [Cancel]  [Save]          │
└─────────────────────────────────────┘
```

**Fields**:
- Name input: Entry field
- Keywords display: Read-only label (shows current active keywords)

**Validation**:
- Name length (1-50 chars)
- Name pattern (alphanumeric + spaces)
- Name uniqueness (case-insensitive)

**Actions**:
- Save: Calls `Configuration.add_preset()`, closes dialog, refreshes cards
- Cancel: Closes dialog without changes

**Code Signature**:
```python
def _show_create_dialog(self):
    """Show Create Preset dialog."""
    pass
```

---

### Edit Preset Dialog

**Type**: Modal dialog (tkinter Toplevel)

**Layout**:
```
┌─────────────────────────────────────┐
│ Edit Preset                         │
│                                     │
│ Preset Name:                        │
│ [Medical Report_______________]     │
│                                     │
│ Keywords:                           │
│ [HTD] [RTP] [Temperature] [+ Add]   │
│                                     │
│           [Cancel]  [Save]          │
└─────────────────────────────────────┘
```

**Fields**:
- Name input: Entry field (pre-filled with current name)
- Keywords: Chip display with add/remove capability

**Validation**:
- Name validation (same as Create)
- Keyword validation (max 100 chars, no duplicates)

**Actions**:
- Save: Calls `Configuration.update_preset()`, closes dialog, refreshes cards
- Cancel: Closes dialog without changes

**Code Signature**:
```python
def _show_edit_dialog(self, preset_name: str):
    """Show Edit Preset dialog.

    Args:
        preset_name: Name of preset to edit
    """
    pass
```

---

### Delete Confirmation Dialog

**Type**: Modal messagebox (tkinter.messagebox)

**Message**: "Delete preset '{name}'?"
**Buttons**: Delete, Cancel

**Actions**:
- Delete: Calls `Configuration.delete_preset()`, refreshes cards
- Cancel: Closes without action

**Code Signature**:
```python
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
    if result:
        # Call callback to delete preset
        pass
```

---

### Load Confirmation Dialog

**Type**: Modal messagebox (tkinter.messagebox)

**Trigger**: User clicks [Load] button when active keywords exist

**Message**: "Replace current keywords with preset '{name}'?"
**Buttons**: Replace, Cancel

**Actions**:
- Replace: Load preset keywords, replace active keywords
- Cancel: No action

**Code Signature**:
```python
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
```

---

## Event Callbacks

### Preset Callbacks

**Registered by AppController**:

```python
# In KeywordPanel
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
```

---

## Public API

### Refresh Presets

```python
def refresh_presets(self, presets: list[dict]):
    """Update preset cards display.

    Args:
        presets: List of preset dicts from Configuration
    """
    self._presets = presets.copy()
    self._render_preset_cards()
    self._update_header_text()
```

### Set Expanded State

```python
def set_presets_expanded(self, expanded: bool):
    """Set presets section expanded/collapsed.

    Args:
        expanded: True to expand, False to collapse
    """
    self._presets_expanded = expanded
    self._update_presets_visibility()
    self._update_header_text()
```

---

## State Management

### Internal State

```python
# In KeywordPanel.__init__
self._presets = []  # List of preset dicts
self._presets_expanded = False  # Collapsed by default
self._preset_create_callback = None
self._preset_load_callback = None
self._preset_edit_callback = None
self._preset_delete_callback = None
self._presets_section_toggle_callback = None
```

### State Sync

**On Initialization**:
```python
# In AppController initialization
keyword_panel.set_presets_expanded(config.presets_section_expanded)
keyword_panel.refresh_presets(config.get_all_presets())
```

**On Toggle**:
```python
def _toggle_presets_section(self, event=None):
    self._presets_expanded = not self._presets_expanded
    self._update_presets_visibility()
    self._update_header_text()

    # Notify controller to persist state
    if self._presets_section_toggle_callback:
        self._presets_section_toggle_callback(self._presets_expanded)
```

---

## Integration with Active Keywords

### Load Preset Flow

1. User clicks [Load] on preset card
2. If active keywords exist, show confirmation dialog
3. If confirmed (or no active keywords), load preset keywords
4. Call `self.set_active_keywords(preset['keywords'])`
5. UI updates: active chips rendered, history refreshed (removes loaded keywords from history display)

**No interaction with keyword history** - Preset loading only affects active keywords, not history persistence.

---

## Accessibility

**Keyboard Navigation**:
- Tab order: Input field → Add button → Presets header → Create button → History → Active keywords → Clear All
- Enter on header: Toggle section
- Enter on Load button: Load preset (with confirmation if needed)
- Menu button: Opens context menu via mouse click (keyboard nav not required per constitution)

**Screen Reader Support**: Not required per constitution (desktop app for sighted users)

---

## Performance

**Rendering Optimization**:
- Lazy card creation: Cards created only when visible (within scroll region)
- Debounced refresh: Batch updates when multiple presets modified
- Canvas scroll region updated only on card count change

**Expected Load Time**:
- 10 presets: <50ms
- 50 presets: <100ms
- 100 presets: <200ms (acceptable per constitution)

---

## Error Display

**Validation Errors**:
- Show error message in dialog (red text below input field)
- Keep dialog open, allow user to correct input
- Save button disabled until validation passes

**Example**:
```python
def _validate_preset_name_in_dialog(self, name: str) -> tuple[bool, str]:
    """Validate name and show error in dialog."""
    is_valid, error_msg = self._validate_preset_name(name)
    if not is_valid:
        self.error_label.configure(
            text=error_msg,
            foreground=AppTheme.COLORS['error']
        )
        self.save_button.state(['disabled'])
    else:
        self.error_label.configure(text="")
        self.save_button.state(['!disabled'])
    return is_valid, error_msg
```

---

## Testing Hooks (Manual Validation)

**Reference quickstart.md for full test scenarios**:
- Create preset with valid/invalid names
- Load preset with/without active keywords
- Edit preset name and keywords
- Delete preset
- Toggle section state (persists across restarts)
- Empty state display
- Scroll behavior with 20+ presets
- Keyword preview formatting (3 vs 5 keywords)
