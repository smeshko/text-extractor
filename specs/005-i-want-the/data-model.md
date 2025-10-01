# Data Model: Grid-Based Keyword History Display

**Feature**: Replace listbox with responsive grid layout  
**Date**: October 1, 2025

## Overview

This feature is a **UI-only change** affecting the presentation layer. No changes to data models, persistence, or business logic are required.

## Existing Models (Unchanged)

### KeywordHistory

**Location**: `/src/models/keyword_history.py`

**Purpose**: Manages persistence and retrieval of keyword history across sessions

**Key Fields**:
- `keywords: List[str]` - Ordered list of historical keywords (most recent first)
- `max_history: int` - Maximum number of keywords to retain (default: 100)

**Key Methods**:
- `add_keyword(keyword: str)` - Add keyword to history
- `get_keywords() -> List[str]` - Retrieve all keywords
- `remove_keyword(keyword: str)` - Remove specific keyword
- `save()` - Persist to JSON file
- `load()` - Load from JSON file

**Storage Format**: JSON file at configured path

### Keyword

**Location**: `/src/models/keyword.py`

**Purpose**: Represents individual keyword for extraction

**Key Fields**:
- `text: str` - Keyword text (Cyrillic or Latin)
- `case_sensitive: bool` - Search behavior

**Usage**: Active keywords list (separate from history)

## UI State (New)

### GridLayoutState (Implicit)

**Purpose**: Manages runtime layout calculations for grid display

**Fields** (instance variables in KeywordPanel):
- `grid_items: List[tk.Label]` - References to all grid item widgets
- `grid_container: tk.Canvas` - Scrollable canvas container
- `grid_frame: tk.Frame` - Inner frame holding grid items
- `resize_job: Optional[str]` - Debounce timer ID for resize events

**Lifecycle**:
1. Created when history section is rendered (`if self._keyword_history:`)
2. Updated when keywords are added/removed from history
3. Recalculated on window resize events
4. Destroyed when history is empty

## Data Flow

### Display Flow (History → Grid)

```
KeywordHistory.get_keywords()
    ↓
Filter out keywords already in active list
    ↓
Create tk.Label for each keyword
    ↓
Calculate flow/wrap positions
    ↓
Render in Canvas
```

### Interaction Flow (Grid → Active Keywords)

```
User clicks grid item (keyword)
    ↓
_on_grid_item_click(keyword_text)
    ↓
_on_keyword_added(keyword_text) [callback to controller]
    ↓
Remove keyword from grid display
    ↓
_on_history_selected([keyword_text]) [callback to history manager]
```

### History Update Flow (Active Keywords → History)

```
User removes keyword from active list
    ↓
KeywordHistory.add_keyword(keyword_text)
    ↓
_populate_history() [refresh grid display]
    ↓
Keyword reappears in grid (left position, most recent)
```

## Validation Rules

### Display Filtering (FR-006)
- **Rule**: Grid MUST NOT display keywords already in active keywords list
- **Implementation**: Filter `KeywordHistory.get_keywords()` against active keywords before rendering
- **Check**: `keyword not in [kw.text for kw in active_keywords]`

### Order Constraint (FR-003)
- **Rule**: Keywords MUST appear in most-recent-first order (left-to-right, top-to-bottom)
- **Implementation**: Use `KeywordHistory.get_keywords()` directly (already ordered)
- **Verification**: First keyword in list = top-left grid position

### Text Length Handling (FR-012, Edge Case)
- **Rule**: Grid items MUST handle long keyword text (80+ chars) without breaking layout
- **Implementation**: Set max width on Label, truncate with ellipsis if needed
- **Fallback**: Tooltip (`<Enter>` binding) shows full text

## State Transitions

### Keyword Addition (from History)

```
State: Keyword in history grid, NOT in active list
    ↓ [User clicks grid item]
State: Keyword in active list, NOT in history grid
```

### Keyword Removal (from Active)

```
State: Keyword in active list, NOT in history grid
    ↓ [User removes from active keywords]
State: Keyword in history grid (left position), NOT in active list
```

### Window Resize

```
State: Grid items positioned for width W1
    ↓ [User resizes window to width W2]
State: Layout recalculated, items repositioned (flow/wrap adjusted)
```

## Performance Considerations

### Large History Sets (NFR: 1000 keywords)

**Challenge**: Rendering 1000 Label widgets may impact responsiveness

**Mitigations**:
1. **Lazy Rendering**: Only create visible widgets (within scroll region)
   - Deferred to implementation (optional optimization)
2. **Batch Operations**: Update layout once per resize (debounced)
3. **Virtualization**: Not implemented (deemed unnecessary for 1000 items)

**Benchmark Target**: <200ms initial render for 1000 keywords

## Integration Points

### KeywordPanel (`/src/ui/keyword_panel.py`)

**Modified Sections**:
- Lines 72-117: Replace listbox with grid layout

**Preserved Methods**:
- `_populate_history()`: Adapted to populate grid instead of listbox
- Callback integration: `_on_history_selected`, `_on_keyword_added`

**New Methods**:
- `_create_grid_layout()`: Build Canvas + Frame structure
- `_calculate_grid_positions()`: Flow/wrap algorithm
- `_on_grid_item_click(keyword)`: Handle single-click
- `_on_resize_grid(event)`: Debounced layout recalculation
- `_remove_from_history_display(keyword)`: Remove specific grid item

### AppController (`/src/controllers/app_controller.py`)

**No Changes Required**: Existing callbacks remain compatible

## Schema Changes

**None**: No database, API, or file format changes

## Compatibility

### Backward Compatibility
- **Keyword History JSON**: No format changes
- **Configuration**: No new settings required
- **Existing Workflows**: Click-to-add replaces select-then-add (behavioral change, not breaking)

### Forward Compatibility
- **Future Features**: Grid layout can be extended with:
  - Edit-in-place for keywords
  - Drag-and-drop reordering (requires history order persistence)
  - Categorization/tags (requires history model enhancement)

## Testing Data Requirements

### Minimal Test Set
1. Empty history: `[]`
2. Single keyword: `["Keyword"]`
3. Typical set: `["К1", "К2", "К3", "К4", "К5"]` (Cyrillic)
4. Large set: 100 keywords (auto-generated)
5. Long keyword: `["This is a very long keyword with more than eighty characters to test text wrapping behavior"]`

### Manual Validation Checklist
- [ ] Empty history hides section (FR-011)
- [ ] Single keyword displays without layout issues
- [ ] 10 keywords flow/wrap correctly on resize
- [ ] 50+ keywords scroll smoothly
- [ ] Long keywords truncate with ellipsis (or wrap)
- [ ] Cyrillic keywords render correctly (Unicode)
- [ ] Click adds keyword to active list
- [ ] Clicked keyword disappears from grid
- [ ] Removed active keyword reappears in grid (left position)
- [ ] Hover state provides visual feedback (FR-002)

## Summary

**Key Insight**: This is a presentation-layer refactoring with **zero data model changes**. All business logic (keyword persistence, history management, filtering) remains unchanged. The complexity lies entirely in UI layout calculations and event handling.

**Risk Assessment**: Low risk - isolated to single file (`keyword_panel.py`), no cascading changes.

