# Tasks: Grid-Based Keyword History Display

**Feature**: Replace list-based keyword history with responsive grid layout  
**Branch**: `005-i-want-the`  
**Input**: Design documents from `/Users/A1E6E98/Developer/kris-extractor/specs/005-i-want-the/`  
**Prerequisites**: plan.md ✓, research.md ✓, data-model.md ✓, contracts/ui-contract.md ✓, quickstart.md ✓

## Execution Flow (main)
```
1. Load plan.md from feature directory ✓
   → Tech stack: Python 3.10+, tkinter (no new dependencies)
   → Structure: Single project (src/ui/keyword_panel.py modification)
2. Load design documents ✓
   → data-model.md: Zero model changes (UI-only feature)
   → contracts/ui-contract.md: 6 methods to implement
   → research.md: 7 technical decisions documented
   → quickstart.md: 13 validation test cases
3. Generate tasks by category:
   → Setup: Backup and code removal
   → Core: 6 method implementations (sequential - same file)
   → Validation: 13 test cases (can be parallel)
4. Apply task rules:
   → Same file (keyword_panel.py) = sequential (no [P])
   → Validation tasks = different scenarios = mark [P]
5. Number tasks sequentially (T001-T015)
6. Task output: 15 tasks total
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files or independent test scenarios)
- All implementation tasks target: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

---

## Phase 3.1: Setup & Preparation

### T001: [X] Backup current listbox implementation
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Create backup of lines 72-117 (history section with listbox)  
**Rationale**: Preserve current implementation for rollback if needed  
**Deliverable**: Comment block or separate backup file with original listbox code

**Implementation Notes**:
- Option 1: Create `keyword_panel.py.backup` with full file copy
- Option 2: Add comment block above line 72 with original implementation
- Verify backup contains: listbox creation (lines 89-103), "Add Selected" button (lines 112-117)

---

### T002: [X] Remove old listbox implementation
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Delete lines 89-117 (listbox, scrollbar, "Add Selected from History" button)  
**Dependencies**: T001 (backup must exist first)  
**Rationale**: Clear space for grid layout implementation

**Preserved**:
- Line 72-78: `if self._keyword_history:` conditional and "History:" label
- Line 106: `self._populate_history()` call (will be modified)
- Line 109: Double-click binding (will be removed in T007)

**Removed**:
- Lines 89-103: Listbox and scrollbar creation
- Lines 112-117: "Add Selected from History" button
- Update line count references in plan.md after deletion

---

## Phase 3.2: Core Implementation

**Note**: All tasks in this phase modify the same file (`keyword_panel.py`) sequentially. No [P] markers.

---

### T003: [X] Create grid layout structure method
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Implement `_create_grid_layout(parent: tk.Widget) -> None` method  
**Dependencies**: T002 (old code removed)  
**Reference**: contracts/ui-contract.md lines 11-30

**Implementation**:
```python
def _create_grid_layout(self, parent):
    """Initialize grid layout structure (Canvas + Frame + Scrollbar)."""
    # Container frame for canvas + scrollbar
    history_frame = ttk.Frame(parent)
    history_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), 
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
    self.grid_container.create_window((0, 0), window=self.grid_frame, anchor='nw')
    
    # Layout
    self.grid_container.grid(row=0, column=0, sticky=(tk.W, tk.E))
    scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
    
    # Bind resize event
    self.grid_container.bind('<Configure>', self._on_resize_grid)
    
    # Initialize state
    self.grid_items = []
    self._resize_job = None
```

**Postconditions**:
- `self.grid_container` (Canvas) is created
- `self.grid_frame` (Frame) is attached to Canvas
- Scrollbar is functional
- Resize event is bound

---

### T004: [X] Implement flow/wrap positioning algorithm
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Implement `_calculate_grid_positions() -> None` method  
**Dependencies**: T003 (grid structure exists)  
**Reference**: contracts/ui-contract.md lines 57-99, research.md Decision 3

**Implementation**:
```python
def _calculate_grid_positions(self):
    """Calculate and apply flow/wrap positions for all grid items."""
    if not self.grid_items or not self.grid_container.winfo_exists():
        return
    
    # Constants
    ITEM_SPACING = 8
    ROW_SPACING = 8
    MAX_GRID_HEIGHT = 200
    
    # Get container width (use winfo_width, fallback to reqwidth)
    container_width = self.grid_container.winfo_width()
    if container_width <= 1:
        container_width = self.grid_container.winfo_reqwidth()
    
    # Position calculation
    current_x = 0
    current_y = 0
    row_height = 0
    
    for label in self.grid_items:
        # Update geometry
        label.update_idletasks()
        item_width = label.winfo_reqwidth()
        item_height = label.winfo_reqheight()
        
        # Wrap to next row if needed
        if current_x + item_width > container_width and current_x > 0:
            current_x = 0
            current_y += row_height + ROW_SPACING
            row_height = 0
        
        # Place label
        label.place(x=current_x, y=current_y)
        
        # Update tracking
        current_x += item_width + ITEM_SPACING
        row_height = max(row_height, item_height)
    
    # Set canvas height
    actual_height = current_y + row_height
    canvas_height = min(actual_height, MAX_GRID_HEIGHT)
    self.grid_container.configure(height=canvas_height)
    
    # Update scroll region
    self.grid_container.configure(scrollregion=(0, 0, container_width, actual_height))
```

**Postconditions**:
- Grid items are positioned in flow/wrap layout
- Canvas height is set (max 200px)
- Scroll region is updated

---

### T005: [X] Modify _populate_history for grid items
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Refactor `_populate_history()` to create grid Label widgets instead of listbox items  
**Dependencies**: T003, T004 (grid structure and positioning exist)  
**Reference**: contracts/ui-contract.md lines 33-54, research.md Decision 2

**Implementation**:
```python
def _populate_history(self):
    """Populate grid with keyword items from history."""
    if not hasattr(self, 'grid_frame') or not self.grid_frame.winfo_exists():
        return
    
    # Clear existing items
    for item in self.grid_items:
        item.destroy()
    self.grid_items.clear()
    
    # Get keywords, filter out active ones
    history_keywords = self._keyword_history.get_keywords()
    active_keyword_texts = [kw.text for kw in self.keywords]
    available_keywords = [kw for kw in history_keywords if kw not in active_keyword_texts]
    
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
    
    # Layout items
    self._calculate_grid_positions()
```

**Postconditions**:
- Grid items created for all non-active history keywords
- Hover states are functional
- Click bindings are set

---

### T006: [X] Implement single-click handler
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Implement `_on_grid_item_click(keyword_text: str) -> None` method  
**Dependencies**: T005 (grid items with bindings)  
**Reference**: contracts/ui-contract.md lines 101-123, spec.md FR-007, FR-008

**Implementation**:
```python
def _on_grid_item_click(self, keyword_text):
    """Handle single click on grid item (immediate add workflow)."""
    # Add to active keywords
    self._on_keyword_added(keyword_text)
    
    # Remove from grid display
    self._remove_from_history_display(keyword_text)
    
    # Optional: Notify controller
    if self._on_history_selected:
        self._on_history_selected([keyword_text])
```

**Postconditions**:
- Keyword is added to active keywords list
- Keyword is removed from grid display
- Grid reflows to fill gap

---

### T007: [X] Implement grid item removal method
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Implement `_remove_from_history_display(keyword_text: str) -> None` method  
**Dependencies**: T004 (positioning algorithm exists)  
**Reference**: contracts/ui-contract.md lines 125-142

**Implementation**:
```python
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
```

**Postconditions**:
- Specified keyword is removed from grid
- Remaining items reflow to fill space

---

### T008: [X] Implement resize debouncing
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Implement `_on_resize_grid(event: tk.Event) -> None` method  
**Dependencies**: T004 (positioning algorithm exists)  
**Reference**: contracts/ui-contract.md lines 144-159, research.md Decision 5

**Implementation**:
```python
def _on_resize_grid(self, event):
    """Handle Canvas resize event with debounce."""
    # Cancel previous resize job
    if self._resize_job:
        self.after_cancel(self._resize_job)
    
    # Schedule new layout calculation (100ms delay)
    self._resize_job = self.after(100, self._calculate_grid_positions)
```

**Postconditions**:
- Layout recalculation is debounced to 100ms
- Multiple rapid resizes trigger only one recalculation

---

### T009: [X] Update history section initialization
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Update the `if self._keyword_history:` section (around line 72) to call `_create_grid_layout` instead of creating listbox  
**Dependencies**: T003 (grid layout method exists)  
**Reference**: spec.md notes line 166

**Implementation**:
- Replace lines 81-117 with:
```python
# Create grid layout
self._create_grid_layout(self)

# Populate grid
self._populate_history()
```

- Remove double-click binding (line 109 in original)
- Verify "History:" label (lines 73-78) remains unchanged

**Postconditions**:
- Grid layout is created when history exists
- History section is hidden when history is empty

---

### T010: [X] Add grid state cleanup on panel destroy
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Ensure grid items and resize jobs are cleaned up when panel is destroyed  
**Dependencies**: All implementation tasks (T003-T009)  
**Reference**: Best practice for tkinter resource management

**Implementation**:
- Add cleanup to `__init__` or add a `destroy` override:
```python
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
```

**Postconditions**:
- No memory leaks from pending after() jobs
- Grid items are properly destroyed

---

## Phase 3.3: Testing & Validation

**Status**: Implementation Complete - Ready for Manual Validation
**Note**: All validation tasks are independent test scenarios and can run in parallel [P].

---

### T011: [P] Manual validation - Core functionality
**Reference**: `/Users/A1E6E98/Developer/kris-extractor/specs/005-i-want-the/quickstart.md`  
**Test Cases**: 1-5 (Empty history, Single keyword, Flow/wrap, Window resize, Scrolling)  
**Dependencies**: All implementation tasks (T003-T010)

**Validation Steps**:
1. **Test Case 1**: Delete history file, verify section is hidden
2. **Test Case 2**: Create history with 1 keyword, verify layout is not broken
3. **Test Case 3**: Load 10 keywords, verify multi-row flow layout
4. **Test Case 4**: Resize window narrow/wide, verify reflow within 100ms
5. **Test Case 5**: Load 50 keywords, verify 200px height limit and scrolling

**Expected Results**:
- [ ] Empty history: Section hidden ✓
- [ ] Single keyword: Displays properly ✓
- [ ] 10 keywords: 2-4 rows, proper spacing ✓
- [ ] Resize: Reflow without horizontal scroll ✓
- [ ] 50 keywords: Scrollbar appears, smooth scrolling ✓

---

### T012: [P] Manual validation - Interaction
**Reference**: `/Users/A1E6E98/Developer/kris-extractor/specs/005-i-want-the/quickstart.md`  
**Test Cases**: 6-8 (Hover feedback, Click interaction, Remove/reappear)  
**Dependencies**: All implementation tasks (T003-T010)

**Validation Steps**:
1. **Test Case 6**: Hover over grid item, verify cursor change and background color change
2. **Test Case 7**: Click grid item, verify immediate add to active list and removal from grid
3. **Test Case 8**: Remove keyword from active list, verify it reappears in grid (left position)

**Expected Results**:
- [ ] Hover: Cursor changes to hand2, background changes to hover color ✓
- [ ] Click: Keyword added to active list, disappears from grid <50ms ✓
- [ ] Remove: Keyword reappears in grid at left position ✓
- [ ] "Add Selected from History" button is NOT present ✓

---

### T013: [P] Manual validation - Unicode & Filtering
**Reference**: `/Users/A1E6E98/Developer/kris-extractor/specs/005-i-want-the/quickstart.md`  
**Test Cases**: 9-11 (Cyrillic support, Long keywords, Active filtering)  
**Dependencies**: All implementation tasks (T003-T010)

**Validation Steps**:
1. **Test Case 9**: Load Cyrillic keywords, verify correct rendering and interaction
2. **Test Case 10**: Load 80+ character keyword, verify no horizontal scroll and text handling
3. **Test Case 11**: Add keywords to active list, verify they don't appear in history grid

**Test Data**:
```json
{
  "keywords": [
    "Температура", "Скорость", "Плотность",
    "This is a very long keyword with more than eighty characters to test text wrapping and truncation behavior in the grid layout"
  ]
}
```

**Expected Results**:
- [ ] Cyrillic: Renders correctly with Segoe UI font ✓
- [ ] Long keyword: Truncates or wraps without breaking grid ✓
- [ ] Filtering: Active keywords excluded from grid display ✓

---

### T014: [P] Manual validation - Space efficiency & Performance
**Reference**: `/Users/A1E6E98/Developer/kris-extractor/specs/005-i-want-the/quickstart.md`  
**Test Cases**: 12-13 (Space efficiency comparison, Large history performance)  
**Dependencies**: All implementation tasks (T003-T010)

**Validation Steps**:
1. **Test Case 12**: Compare grid vs old listbox (branch without feature)
   - Count visible keywords in 100px vertical space
   - Verify grid shows at least 2x more keywords than listbox

2. **Test Case 13**: Generate 1000 keywords, measure performance
   ```python
   # Test data generation
   import json
   keywords = [f"Keyword_{i:04d}" for i in range(1000)]
   with open('keyword_history.json', 'w') as f:
       json.dump({"keywords": keywords, "max_history": 1000}, f)
   ```
   - Measure initial render time (target: <200ms)
   - Test scrolling smoothness (60 FPS)
   - Test resize responsiveness (reflow within 100ms)

**Expected Results**:
- [ ] Space efficiency: Grid shows 2x more keywords than listbox ✓
- [ ] 1000 keywords render in <200ms ✓
- [ ] Scrolling is smooth (no lag or stuttering) ✓
- [ ] Resize triggers reflow within 100ms ✓

---

### T015: Final integration verification
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`  
**Action**: Run full application and verify grid integrates correctly with existing functionality  
**Dependencies**: All previous tasks (T001-T014)

**Verification Checklist**:
- [ ] Grid appears in keyword panel when history exists
- [ ] Grid is hidden when history is empty
- [ ] Click on grid item adds keyword to active list
- [ ] Remove from active list returns keyword to grid
- [ ] Window resize updates grid layout smoothly
- [ ] Theme changes (if applicable) update grid colors
- [ ] No console errors or warnings
- [ ] PyInstaller .exe builds successfully (Windows target)

**Integration Points to Verify**:
- `KeywordHistory.get_keywords()` integration
- `_on_keyword_added(keyword)` callback to controller
- `_on_history_selected([keyword])` callback (if used)
- Active keywords filtering
- AppTheme color integration (light/dark mode)

**Definition of Done**:
- [ ] All 13 validation test cases pass
- [ ] No regressions in existing keyword panel functionality
- [ ] Code follows existing style (ruff linting passes)
- [ ] Feature matches user-provided screenshot design
- [ ] Constitution principles satisfied (no violations)

---

## Dependencies Graph

```
T001 (Backup)
  ↓
T002 (Remove old code)
  ↓
T003 (Create grid structure)
  ↓
T004 (Positioning algorithm)
  ↓
T005 (Populate history) + T006 (Click handler) + T007 (Remove method) + T008 (Resize)
  ↓
T009 (Update initialization)
  ↓
T010 (Cleanup)
  ↓
T011-T014 (Validation - can run in parallel [P])
  ↓
T015 (Final integration)
```

**Critical Path**: T001 → T002 → T003 → T004 → T005 → T009 → T010 → T011-T014 → T015

**Parallelization Opportunities**:
- T011, T012, T013, T014 can run simultaneously (independent test scenarios)
- All implementation tasks (T003-T010) are sequential (same file)

---

## Parallel Execution Example

After T010 is complete, launch validation tasks in parallel:

```bash
# Terminal 1: Core functionality tests
# Run Test Cases 1-5 from quickstart.md

# Terminal 2: Interaction tests
# Run Test Cases 6-8 from quickstart.md

# Terminal 3: Unicode & filtering tests
# Run Test Cases 9-11 from quickstart.md

# Terminal 4: Performance tests
# Run Test Cases 12-13 from quickstart.md
```

Or use task agent commands:
```
Task: "Manual validation - Core functionality (Test Cases 1-5)"
Task: "Manual validation - Interaction (Test Cases 6-8)"
Task: "Manual validation - Unicode & Filtering (Test Cases 9-11)"
Task: "Manual validation - Space efficiency & Performance (Test Cases 12-13)"
```

---

## Notes

- **Single File Scope**: All implementation modifies `/src/ui/keyword_panel.py` only
- **No Model Changes**: Uses existing `KeywordHistory` and `Keyword` models unchanged
- **No New Dependencies**: Pure tkinter implementation (PyInstaller compatible)
- **Constitution Compliant**: No violations detected (simplifies UX, no complexity added)
- **Manual Validation**: Per constitution, no automated tests required
- **Commit Strategy**: Commit after each implementation task (T003-T010)
- **Rollback Plan**: Use T001 backup if issues arise

---

## Validation Checklist
*GATE: Checked before marking feature complete*

- [x] All contracts implemented (ui-contract.md: 6 methods ✓)
- [x] No new entities (data model unchanged ✓)
- [x] Parallel tasks are truly independent (validation tasks only ✓)
- [x] Each task specifies exact file path ✓
- [x] No task modifies same file as another [P] task ✓
- [x] Manual validation tasks included (T011-T014 ✓)
- [x] All quickstart test cases covered (13 cases in 4 validation tasks ✓)
- [x] Performance requirements validated (Test Case 13 ✓)
- [x] Constitution compliance verified (no violations ✓)

---

## Summary

**Total Tasks**: 15
- **Setup**: 2 tasks (T001-T002)
- **Core Implementation**: 8 tasks (T003-T010, sequential)
- **Validation**: 4 tasks (T011-T014, parallel)
- **Integration**: 1 task (T015)

**Estimated Effort**: 
- Implementation: 4-6 hours (sequential tasks, single file)
- Validation: 2-3 hours (can be parallelized)
- Total: 6-9 hours

**Risk Level**: Low (isolated UI change, no business logic impact)

**Ready for Execution**: ✅ All design artifacts complete, tasks are specific and actionable.

