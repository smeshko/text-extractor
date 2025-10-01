# UI Contract: Grid-Based Keyword History Component

**Component**: KeywordHistoryGrid (embedded in KeywordPanel)  
**File**: `/src/ui/keyword_panel.py`  
**Type**: Visual Component (tkinter-based)

## Component Interface

### Public Methods

#### `_create_grid_layout(parent: tk.Widget) -> None`

**Purpose**: Initialize the grid layout structure (Canvas + Frame)

**Preconditions**:
- Parent widget exists and is visible
- `self._keyword_history` is not None and contains keywords

**Behavior**:
1. Create container frame for Canvas and Scrollbar
2. Create Canvas widget with background color from AppTheme
3. Create Scrollbar and link to Canvas
4. Create inner Frame attached to Canvas window
5. Bind Canvas `<Configure>` event to resize handler

**Postconditions**:
- `self.grid_container` (Canvas) is created and gridded
- `self.grid_frame` (Frame) is created and attached to Canvas
- Scrollbar is visible and functional

---

#### `_populate_history() -> None`

**Purpose**: Populate grid with keyword items from history

**Preconditions**:
- Grid layout structure exists (`_create_grid_layout` called)
- `self._keyword_history.get_keywords()` returns valid list

**Behavior**:
1. Clear existing grid items (destroy all Label widgets)
2. Filter keywords: exclude those in active keywords list
3. For each keyword:
   - Create tk.Label with text, styling, and hover bindings
   - Bind `<Button-1>` to `_on_grid_item_click`
4. Call `_calculate_grid_positions()` to layout items
5. Update Canvas scroll region

**Postconditions**:
- All non-active keywords are displayed in grid
- Grid items are positioned in flow/wrap layout
- Each item is clickable and has hover feedback

---

#### `_calculate_grid_positions() -> None`

**Purpose**: Calculate and apply flow/wrap positions for all grid items

**Preconditions**:
- Grid items exist in `self.grid_items`
- Canvas width is known

**Algorithm**:
```
Input: self.grid_items (List[tk.Label])
Constants:
  ITEM_SPACING = 8  # pixels between items
  ROW_SPACING = 8   # pixels between rows

1. container_width = self.grid_container.winfo_width()
2. current_x = 0, current_y = 0, row_height = 0

3. For each label in self.grid_items:
   a. Update label (trigger geometry calculation)
   b. item_width = label.winfo_reqwidth()
   c. item_height = label.winfo_reqheight()
   
   d. If current_x + item_width > container_width AND current_x > 0:
      # Wrap to next row
      current_x = 0
      current_y += row_height + ROW_SPACING
      row_height = 0
   
   e. Place label at (current_x, current_y) using place()
   f. current_x += item_width + ITEM_SPACING
   g. row_height = max(row_height, item_height)

4. actual_height = current_y + row_height
5. Set Canvas height to min(actual_height, MAX_GRID_HEIGHT=200)
6. Update Canvas scrollregion to (0, 0, container_width, actual_height)
```

**Postconditions**:
- All grid items are positioned in flow/wrap layout
- Canvas scroll region matches actual content height
- Canvas height does not exceed 200px (scrolls if taller)

---

#### `_on_grid_item_click(keyword_text: str) -> None`

**Purpose**: Handle single-click on grid item (immediate add workflow)

**Parameters**:
- `keyword_text`: The keyword text to add to active keywords

**Behavior**:
1. Call `self._on_keyword_added(keyword_text)` (adds to active list)
2. Remove keyword from grid display via `_remove_from_history_display(keyword_text)`
3. Optionally call `self._on_history_selected([keyword_text])` (history callback)

**Postconditions**:
- Keyword is added to active keywords list
- Keyword is removed from grid display
- Grid layout recalculates to fill gap

---

#### `_remove_from_history_display(keyword_text: str) -> None`

**Purpose**: Remove specific keyword from grid display

**Parameters**:
- `keyword_text`: Keyword to remove

**Behavior**:
1. Find Label widget with matching text in `self.grid_items`
2. Destroy Label widget
3. Remove from `self.grid_items` list
4. Call `_calculate_grid_positions()` to reflow remaining items

**Postconditions**:
- Keyword is no longer visible in grid
- Remaining items reflow to fill space

---

#### `_on_resize_grid(event: tk.Event) -> None`

**Purpose**: Handle Canvas resize event with debounce

**Parameters**:
- `event`: tkinter Configure event (contains new width/height)

**Behavior**:
1. Cancel previous resize job if exists (`self._resize_job`)
2. Schedule new job: `self.after(100, self._calculate_grid_positions)`
3. Store job ID in `self._resize_job`

**Postconditions**:
- Layout recalculation is scheduled after 100ms
- Multiple rapid resizes trigger only one recalculation

---

## Visual Specifications

### Grid Item (tk.Label)

**Normal State**:
```python
{
    'text': keyword_text,
    'bg': AppTheme.COLORS['primary_light'],     # #E8F2FC (light blue)
    'fg': AppTheme.COLORS['text'],              # #333333 (dark gray)
    'font': AppTheme.FONTS['body'],             # ('Segoe UI', 10)
    'padx': AppTheme.PADDING['medium'],         # 10px
    'pady': AppTheme.PADDING['small'],          # 5px
    'cursor': 'hand2',                          # Hand pointer
    'relief': 'solid',
    'borderwidth': 1,
    'bordercolor': AppTheme.COLORS['border_light']  # Very light gray
}
```

**Hover State**:
```python
{
    'bg': AppTheme.COLORS['bg_hover']  # #F0F0F0 (light gray hover)
}
```

**Bindings**:
- `<Enter>`: Switch to hover state background
- `<Leave>`: Restore normal state background
- `<Button-1>`: Call `_on_grid_item_click(keyword_text)`

---

### Grid Container

**Canvas Configuration**:
```python
{
    'bg': AppTheme.COLORS['bg'],         # White background
    'highlightthickness': 0,             # No border highlight
    'height': dynamic (0-200px),         # Based on content
    'yscrollcommand': scrollbar.set
}
```

**Scrollbar**:
- Standard ttk.Scrollbar (vertical)
- Only visible when content height > 200px

---

## Layout Constraints

### Responsive Behavior (FR-001, FR-005)

**Window Width Change**:
- Grid items reflow to maximize horizontal space usage
- Wrapping occurs when next item would overflow container width
- No horizontal scrolling ever occurs

**Example**:
```
Container width: 400px
Item widths: [80, 80, 80, 80, 80] + spacing (8px each)

Layout at 400px:
Row 1: [Item1] [Item2] [Item3] [Item4]  (352px used)
Row 2: [Item5]

User resizes to 250px:
Row 1: [Item1] [Item2]  (176px used)
Row 2: [Item3] [Item4]  (176px used)
Row 3: [Item5]
```

### Height Behavior (FR-004)

**Dynamic Height**:
- Grid container grows to show all items up to 200px
- If content height < 200px: Canvas height = content height (no scrollbar)
- If content height > 200px: Canvas height = 200px (scrollbar appears)

**Minimum Height**: 30px (single row minimum)

---

## Interaction Contract

### Click Workflow (FR-007, FR-008)

**User Action**: Single left-click on grid item

**System Response**:
1. Keyword added to active keywords list (visible in active section)
2. Grid item disappears from history grid immediately
3. Remaining items reflow to fill gap
4. No confirmation or multi-step workflow

**Timing**: <50ms from click to visual update

---

### Hover Feedback (FR-002)

**User Action**: Mouse cursor enters grid item boundary

**System Response**:
1. Background color changes from `primary_light` to `bg_hover`
2. Cursor changes to `hand2` (pointing hand)
3. No delay (immediate on `<Enter>` event)

**User Action**: Mouse cursor leaves grid item boundary

**System Response**:
1. Background color restores to `primary_light`
2. Cursor restores to default
3. No delay (immediate on `<Leave>` event)

---

## Error Handling

### Empty History (FR-011)

**Condition**: `self._keyword_history` is None or `get_keywords()` returns empty list

**Behavior**: Grid layout section is not created (history section hidden)

**Validation**: Check `if self._keyword_history:` before calling `_create_grid_layout()`

---

### Long Keywords (FR-012, Edge Case)

**Condition**: Keyword text exceeds container width (80+ characters)

**Behavior Options**:
1. **Preferred**: Set `label['width']` to maximum characters, truncate with `...`
2. **Alternative**: Allow text wrapping (multi-line grid item)

**Fallback**: Bind `<Enter>` event to display tooltip with full text

---

### Window Too Narrow

**Condition**: Container width < 100px (minimum for readable item)

**Behavior**: Grid items stack vertically (one per row), scrollbar provides vertical navigation

**No Error**: Graceful degradation (single-column layout)

---

## Integration Points

### Callbacks (Existing)

#### `self._on_keyword_added(keyword_text: str) -> None`

**Purpose**: Add keyword to active keywords list

**Provided By**: AppController (set during KeywordPanel initialization)

**Contract**: Callback MUST update active keywords model and UI

---

#### `self._on_history_selected(keywords: List[str]) -> None`

**Purpose**: Notify controller that keywords were selected from history

**Provided By**: AppController

**Contract**: Callback MAY update history statistics or logging

---

### Theme Integration

**AppTheme Dependency**:
- All colors MUST use `AppTheme.COLORS` dictionary
- All fonts MUST use `AppTheme.FONTS` dictionary
- All spacing MUST use `AppTheme.PADDING` dictionary

**Dark Mode Support**:
- Component automatically adapts to theme changes via AppTheme
- No hardcoded color values allowed

---

## Performance Contract

### Render Time (NFR)

**Target**: Grid MUST render 1000 keywords in <200ms

**Measurement Point**: Start of `_populate_history()` to end of `_calculate_grid_positions()`

**Optimization**: Debounce resize events to 100ms

---

### Scroll Performance

**Target**: Smooth scrolling (60 FPS) with 1000 keywords

**Implementation**: Use Canvas scrolling (native tkinter, hardware accelerated)

---

## Acceptance Criteria

### Visual Validation

- [ ] Grid items display in flowing layout (left-to-right, top-to-bottom)
- [ ] Items wrap to new row when container width is insufficient
- [ ] Hover state is visually distinct and immediate
- [ ] Scrollbar appears only when content exceeds 200px height
- [ ] No horizontal scrollbar ever appears
- [ ] Empty history hides entire section (consistent with current behavior)

### Interaction Validation

- [ ] Single click immediately adds keyword to active list
- [ ] Clicked keyword disappears from grid within 50ms
- [ ] Remaining keywords reflow to fill gap
- [ ] Window resize triggers layout recalculation within 100ms
- [ ] Hover feedback has no delay

### Unicode Validation

- [ ] Cyrillic keywords display correctly (e.g., "Ключевое слово")
- [ ] Latin keywords display correctly
- [ ] Mixed script keywords display correctly (e.g., "Keyword-Ключ")

### Edge Case Validation

- [ ] Single keyword displays without layout issues
- [ ] Long keyword (80+ chars) does not break grid layout
- [ ] Very narrow window (<150px) results in single-column layout
- [ ] 1000 keywords render in <200ms
- [ ] 1000 keywords scroll smoothly

---

## Migration Notes

### From Listbox to Grid

**Removed**:
- `tk.Listbox` widget (lines 89-103 in keyword_panel.py)
- `selectmode=tk.MULTIPLE` (no selection state in grid)
- `<Double-Button-1>` binding (replaced with `<Button-1>`)
- "Add Selected from History" button (lines 112-117)

**Added**:
- Canvas-based grid container
- Flow/wrap layout algorithm
- Single-click immediate add
- Hover state visual feedback
- Resize debouncing

**Behavioral Change**:
- **Old**: Select multiple keywords, click "Add Selected from History" button
- **New**: Click individual keywords to immediately add (simpler UX)

---

## Future Extensions (Out of Scope)

- Drag-and-drop reordering within grid
- Edit-in-place keyword text
- Keyword categorization/tagging
- Grid item context menu (right-click)
- Multi-select with Ctrl/Shift keys
- Search/filter within history grid

---

## Summary

This contract defines a responsive, flow/wrap grid layout for keyword history using standard tkinter widgets (Canvas, Frame, Label). The implementation replaces a vertical listbox with a space-efficient 2D grid that adapts to window width and provides immediate-add interaction on click. All visual styling derives from AppTheme for consistency and dark mode support.

**Key Constraint**: No external dependencies - pure tkinter implementation compatible with PyInstaller single-executable packaging.

