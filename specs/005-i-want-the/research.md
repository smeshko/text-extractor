# Research: Grid-Based Keyword History Display

**Feature**: Replace listbox with responsive grid layout for keyword history  
**Date**: October 1, 2025  
**Status**: Complete

## Overview

This research documents the technical approach for replacing the current `tk.Listbox` (lines 89-103 in `keyword_panel.py`) with a responsive flow/wrap grid layout using standard tkinter widgets.

## Technical Context

**Current Implementation**:
- `tk.Listbox` with `height=4`, `selectmode=tk.MULTIPLE`
- Scrollbar for vertical navigation
- "Add Selected from History" button
- Double-click or button to add selected keywords

**Target Implementation**:
- Responsive grid using `tk.Frame` with dynamic child `tk.Label` widgets
- Flow/wrap layout that adapts to window width
- Single-click immediate add (no selection state)
- Scrollable container when items exceed maximum height

## Decision 1: Grid Layout Implementation

**Chosen**: Canvas + Frame with flow/wrap logic

**Rationale**:
1. tkinter does not have native CSS flexbox-style flow/wrap
2. `tk.Canvas` with embedded `tk.Frame` provides scrolling capability
3. Manual positioning of Label widgets enables responsive reflow on window resize
4. Maintains compatibility with existing theme system

**Alternatives Considered**:
- **Grid manager (grid())**: Does not support flow/wrap - items stay in fixed rows/columns
- **Pack manager (pack())**: Does not provide precise control over wrapping behavior
- **Custom widget**: Unnecessary complexity for this use case

**Implementation Pattern**:
```python
# Container frame for canvas + scrollbar
container = ttk.Frame(parent)

# Canvas for scrolling
canvas = tk.Canvas(container, bg=AppTheme.COLORS['bg'])
scrollbar = ttk.Scrollbar(container, orient=tk.VERTICAL, command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

# Inner frame to hold grid items (attached to canvas window)
grid_frame = tk.Frame(canvas, bg=AppTheme.COLORS['bg'])
canvas.create_window((0, 0), window=grid_frame, anchor='nw')

# Populate with Label widgets positioned using place()
# Layout recalculated on <Configure> event
```

## Decision 2: Grid Item Styling

**Chosen**: tk.Label with rounded rectangle background simulation

**Rationale**:
1. User provided screenshot shows rounded chip/button style
2. tkinter Labels do not support border-radius natively
3. Simulate rounded appearance with padding, background color, and cursor feedback
4. Consistent with existing theme system (AppTheme.COLORS)

**Styling Approach**:
```python
label = tk.Label(
    parent,
    text=keyword_text,
    bg=AppTheme.COLORS['primary_light'],  # Light blue background
    fg=AppTheme.COLORS['text'],           # Dark text
    font=AppTheme.FONTS['body'],
    padx=AppTheme.PADDING['medium'],
    pady=AppTheme.PADDING['small'],
    cursor='hand2',                        # Clickable cursor
    relief='solid',                        # Border
    borderwidth=1
)

# Hover state bindings
label.bind('<Enter>', lambda e: label.configure(bg=AppTheme.COLORS['bg_hover']))
label.bind('<Leave>', lambda e: label.configure(bg=AppTheme.COLORS['primary_light']))
```

## Decision 3: Flow/Wrap Layout Algorithm

**Chosen**: Horizontal accumulation with width threshold wrapping

**Rationale**:
1. Measure each keyword Label width before placement
2. Accumulate labels horizontally until current row width exceeds available width
3. Wrap to next row when threshold exceeded
4. Recalculate on window resize (`<Configure>` event)

**Algorithm**:
```
Input: keywords list, container_width
Output: positioned Label widgets

1. Clear existing grid items
2. current_x = 0, current_y = 0, row_height = 0
3. For each keyword:
   a. Create Label widget
   b. Measure Label width (label.winfo_reqwidth())
   c. If current_x + label_width > container_width:
      - Wrap: current_x = 0, current_y += row_height + spacing
      - Reset row_height = 0
   d. Place label at (current_x, current_y)
   e. Update: current_x += label_width + spacing
   f. Update: row_height = max(row_height, label_height)
4. Update canvas scroll region
```

## Decision 4: Event Handling

**Chosen**: Single-click binding with immediate add callback

**Rationale**:
1. Spec requires immediate add on click (FR-007)
2. Removes complexity of selection state management
3. Each Label binds `<Button-1>` to callback with keyword data

**Implementation**:
```python
def _on_grid_item_click(keyword_text):
    """Handle single click on grid item."""
    # Add to active keywords
    self._on_keyword_added(keyword_text)
    # Remove from history display
    self._remove_from_history_display(keyword_text)
    # Trigger history update callback
    if self._on_history_selected:
        self._on_history_selected([keyword_text])

# Bind to each label
label.bind('<Button-1>', lambda e, kw=keyword: _on_grid_item_click(kw))
```

## Decision 5: Performance Optimization

**Chosen**: Batch layout recalculation with debounce on resize

**Rationale**:
1. Window resize generates many `<Configure>` events
2. Recalculating layout on every event is inefficient
3. Debounce: delay layout recalculation by 100ms after last resize event

**Implementation**:
```python
self._resize_job = None

def _on_resize(event):
    """Handle window resize with debounce."""
    if self._resize_job:
        self.after_cancel(self._resize_job)
    self._resize_job = self.after(100, self._recalculate_layout)
```

## Decision 6: Maximum Height and Scrolling

**Chosen**: Dynamic height up to 200px maximum, then scrollable

**Rationale**:
1. Spec requires grid to grow dynamically (FR-004)
2. Prevent grid from dominating entire panel
3. 200px allows ~6-8 rows at typical item height (~25-30px per row)

**Implementation**:
```python
# After layout calculation, measure actual grid height
actual_height = current_y + row_height
max_height = 200

if actual_height <= max_height:
    canvas.configure(height=actual_height)
else:
    canvas.configure(height=max_height)
    
# Update scroll region
canvas.configure(scrollregion=canvas.bbox('all'))
```

## Decision 7: Integration with Existing Code

**Modification Scope**: Lines 72-117 in `keyword_panel.py`

**Preserved**:
- KeywordHistory model integration (no changes)
- `_populate_history()` method pattern (adapted for grid)
- History visibility logic (`if self._keyword_history:`)
- Callback integration (`_on_history_selected`, `_on_keyword_added`)

**Removed**:
- `tk.Listbox` creation (lines 89-103)
- "Add Selected from History" button (lines 112-117)
- Double-click binding (line 109)

**Added**:
- Canvas + scrollbar container
- Flow/wrap layout calculation
- Grid item Label creation with hover states
- Single-click binding
- Window resize handler

## Unicode Compatibility

**Verification**: tkinter Label widgets support full Unicode by default
- Test cases: Cyrillic keywords (Кириллица), Latin keywords (Latin), mixed (Смешанный-Mixed)
- No encoding changes required
- AppTheme.FONTS['body'] = ('Segoe UI', 10) supports full Unicode range

## Performance Benchmarks

**Target**: 1000 keywords without lag (per spec NFR)

**Estimated Performance**:
- Label creation: ~0.1ms per widget = 100ms for 1000 labels
- Layout calculation: O(n) = ~10ms for 1000 items
- Total: ~110ms initial render (acceptable)
- Resize recalculation: Same O(n) but debounced (smooth UX)

## Dependencies

**No New Dependencies**: All implementation uses standard tkinter widgets
- `tk.Canvas` - built-in
- `tk.Frame` - built-in  
- `tk.Label` - built-in
- `ttk.Scrollbar` - built-in

## Testing Strategy

**Manual Validation** (per Constitution):
1. Empty history: Verify section is hidden
2. 1 keyword: Verify single item displays without layout issues
3. 5-10 keywords: Verify flow/wrap behavior on resize
4. 50+ keywords: Verify scrolling and performance
5. Long keywords (80+ chars): Verify text wrapping or truncation
6. Cyrillic keywords: Verify Unicode rendering
7. Click interaction: Verify immediate add and removal from grid
8. Hover state: Verify visual feedback

## Open Questions

**Resolved**:
- ✅ Grid columns: Responsive flow/wrap (no fixed columns)
- ✅ Selection behavior: Immediate add on click (no selection state)
- ✅ Hover feedback: Yes (bg_hover color)
- ✅ Height: Dynamic up to max, then scrollable
- ✅ Order: Most recent first (left-to-right, top-to-bottom)
- ✅ Button removal: Yes (remove "Add Selected from History")

**No Outstanding Questions**

## References

- Feature Spec: `/specs/005-i-want-the/spec.md`
- Current Implementation: `/src/ui/keyword_panel.py` lines 72-117
- Theme System: `/src/ui/theme.py`
- Keyword History Model: `/src/models/keyword_history.py`

## Next Steps

Proceed to Phase 1: Design & Contracts
- Create UI contract for grid component
- Document data model (no changes needed - uses existing KeywordHistory)
- Generate quickstart validation checklist

