# Quickstart: Grid-Based Keyword History Display

**Feature**: Replace list-based keyword history with responsive grid layout  
**Branch**: `005-i-want-the`  
**Target File**: `/src/ui/keyword_panel.py` (lines 72-117)

## Prerequisites

- Python 3.10+ installed
- Repository cloned and on branch `005-i-want-the`
- Dependencies installed: `pip install -r requirements.txt`
- Existing keyword history file (or create sample data)

## Quick Build and Run

### 1. Navigate to repository root

```bash
cd /Users/A1E6E98/Developer/kris-extractor
```

### 2. Run the application (development mode)

```bash
python src/main.py
```

### 3. Prepare test data (if no existing history)

**Option A**: Create sample history file manually

```bash
# Create config directory if needed
mkdir -p ~/AppData/Local/DocumentExtractor  # Windows
# or
mkdir -p ~/.config/document-extractor       # macOS/Linux

# Create sample history JSON
cat > ~/.config/document-extractor/keyword_history.json << 'EOF'
{
  "keywords": [
    "HTD",
    "Температура",
    "Pressure",
    "Скорость",
    "Volume",
    "Плотность",
    "Mass",
    "Время",
    "Distance",
    "Энергия",
    "This is a very long keyword with more than eighty characters to test text wrapping and truncation behavior in the grid layout",
    "Power",
    "Frequency",
    "Amplitude",
    "Resistance"
  ],
  "max_history": 100
}
EOF
```

**Option B**: Use the application to generate history naturally
1. Open application
2. Add keywords manually (e.g., "HTD", "Temperature", "Pressure")
3. Extract from a document
4. Close application (keywords are saved to history)
5. Restart application (history loads automatically)

---

## Manual Validation Checklist

### Test Case 1: Empty History

**Steps**:
1. Delete or rename keyword history file
2. Launch application
3. Observe keyword panel

**Expected**:
- [ ] History section is NOT displayed (entire section hidden)
- [ ] No "History:" label visible
- [ ] Active keywords section is visible and functional

**Reference**: FR-011, Acceptance Scenario 4

---

### Test Case 2: Single Keyword

**Steps**:
1. Create history file with one keyword: `["Keyword1"]`
2. Launch application
3. Observe keyword panel

**Expected**:
- [ ] History section is displayed
- [ ] Single grid item visible with text "Keyword1"
- [ ] Grid layout does not look broken or awkward
- [ ] Item has proper styling (light blue background, padding)

**Reference**: Edge Case (single keyword)

---

### Test Case 3: Multiple Keywords - Flow/Wrap

**Steps**:
1. Create history file with 10 keywords (mix of short and medium length)
2. Launch application with window at default width (~800px)
3. Observe grid layout

**Expected**:
- [ ] Keywords display in multiple rows (2-4 rows typical)
- [ ] Items flow left-to-right within each row
- [ ] Items wrap to next row when width is insufficient
- [ ] Spacing between items is consistent (8px horizontal, 8px vertical)
- [ ] No horizontal scrollbar appears

**Reference**: FR-001, FR-005, Acceptance Scenario 1

**Screenshot**: Compare with user-provided sample design

---

### Test Case 4: Window Resize

**Steps**:
1. Launch application with 10 keywords in history
2. Note current grid layout (e.g., 3 rows)
3. Resize window to be narrower (e.g., 400px width)
4. Observe grid layout reflow
5. Resize window to be wider (e.g., 1200px width)
6. Observe grid layout reflow

**Expected**:
- [ ] Grid layout recalculates within ~100ms of resize completion
- [ ] Items reflow to new row configuration
- [ ] Wider window: More items per row, fewer rows
- [ ] Narrower window: Fewer items per row, more rows
- [ ] Very narrow window: Single column layout (graceful degradation)
- [ ] No horizontal scrollbar at any width

**Reference**: FR-005, Edge Case (window resize)

---

### Test Case 5: Scrolling (Many Keywords)

**Steps**:
1. Create history file with 50 keywords
2. Launch application
3. Observe grid container height
4. Scroll within grid area

**Expected**:
- [ ] Grid container height is 200px (maximum)
- [ ] Vertical scrollbar is visible and functional
- [ ] Scrolling is smooth (no lag or jitter)
- [ ] All 50 keywords are accessible via scrolling

**Reference**: FR-004, Acceptance Scenario 3

---

### Test Case 6: Hover Interaction

**Steps**:
1. Launch application with history keywords
2. Move mouse cursor over a grid item (do not click)
3. Observe visual feedback
4. Move cursor away from item
5. Observe visual feedback

**Expected**:
- [ ] Cursor changes to pointing hand (`hand2`) when over item
- [ ] Background color changes to hover state (light gray #F0F0F0)
- [ ] Hover feedback is immediate (no delay)
- [ ] Background restores to normal state when cursor leaves
- [ ] Hover state is visually distinct from normal state

**Reference**: FR-002, Acceptance Scenario 5

---

### Test Case 7: Click Interaction (Immediate Add)

**Steps**:
1. Launch application with history keywords (e.g., "HTD", "Temperature", "Pressure")
2. Note current active keywords list (should be empty initially)
3. Single-click on "HTD" grid item
4. Observe both history grid and active keywords list

**Expected**:
- [ ] "HTD" appears in active keywords list immediately
- [ ] "HTD" disappears from history grid immediately (<50ms)
- [ ] Remaining grid items reflow to fill gap
- [ ] No confirmation dialog or intermediate step
- [ ] **"Add Selected from History" button is NOT present** (removed per FR-009)

**Reference**: FR-007, FR-008, FR-009, Acceptance Scenario 2

---

### Test Case 8: Remove from Active → Reappear in History

**Steps**:
1. Launch application with keywords in history
2. Click "Temperature" grid item to add to active keywords
3. Observe "Temperature" is now in active list, not in grid
4. Remove "Temperature" from active keywords list (click "×" or Remove button)
5. Observe history grid

**Expected**:
- [ ] "Temperature" reappears in history grid
- [ ] "Temperature" appears in left-most position (most recent)
- [ ] Grid layout recalculates to accommodate returning keyword

**Reference**: FR-010, Acceptance Scenario 6

---

### Test Case 9: Unicode (Cyrillic) Support

**Steps**:
1. Create history file with Cyrillic keywords:
   ```json
   ["Температура", "Скорость", "Плотность", "Энергия", "Время"]
   ```
2. Launch application
3. Observe grid display
4. Click on a Cyrillic keyword to add to active list

**Expected**:
- [ ] Cyrillic text renders correctly (no garbled characters)
- [ ] Font supports Unicode (Segoe UI default is compatible)
- [ ] Hover and click interactions work identically to Latin keywords
- [ ] Keyword is added to active list with correct Cyrillic text

**Reference**: Constitution Principle III (Unicode-First)

---

### Test Case 10: Long Keyword Handling

**Steps**:
1. Create history file with one long keyword (80+ characters):
   ```json
   ["This is a very long keyword with more than eighty characters to test text wrapping and truncation behavior in the grid layout"]
   ```
2. Launch application
3. Observe grid item display

**Expected**:
- [ ] Long keyword does NOT cause horizontal scrolling
- [ ] Text is either:
   - Truncated with ellipsis ("This is a very long keyword..."), OR
   - Wrapped to multiple lines within grid item
- [ ] Grid layout does not break or overflow container
- [ ] (Optional) Hover shows tooltip with full keyword text

**Reference**: FR-012, FR-013, Edge Case (long keyword)

---

### Test Case 11: Filtering (Exclude Active Keywords)

**Steps**:
1. Create history file with keywords: `["HTD", "Temperature", "Pressure", "Volume"]`
2. Launch application
3. Manually add "Temperature" and "Volume" to active keywords (not via history click)
4. Observe history grid

**Expected**:
- [ ] History grid displays only "HTD" and "Pressure"
- [ ] "Temperature" and "Volume" are NOT displayed in grid (already active)
- [ ] Grid layout adjusts to show only non-active keywords

**Reference**: FR-006

---

### Test Case 12: Space Efficiency Comparison

**Steps**:
1. Launch PREVIOUS version (branch without grid feature)
2. Load 20 keywords into history
3. Observe listbox: Count visible keywords without scrolling
4. Launch CURRENT version (branch `005-i-want-the`)
5. Load same 20 keywords into history
6. Observe grid: Count visible keywords without scrolling

**Expected**:
- [ ] Grid displays at LEAST 2x more keywords than listbox in same vertical space
- [ ] Example: Listbox shows 4 keywords (height=4), Grid shows 8-12 keywords in ~100px

**Reference**: FR-014, NFR (Space Efficiency)

---

### Test Case 13: Performance (Large History)

**Steps**:
1. Generate history file with 1000 keywords:
   ```python
   # Quick script to generate test data
   import json
   keywords = [f"Keyword_{i:04d}" for i in range(1000)]
   with open('keyword_history.json', 'w') as f:
       json.dump({"keywords": keywords, "max_history": 1000}, f)
   ```
2. Launch application
3. Measure time from window open to grid fully rendered
4. Scroll through grid
5. Resize window

**Expected**:
- [ ] Initial render completes in <200ms
- [ ] Scrolling is smooth (60 FPS, no stuttering)
- [ ] Resize triggers reflow within 100ms
- [ ] Application remains responsive (no freezing)

**Reference**: NFR (Performance)

---

## Common Issues and Troubleshooting

### Issue: History section not appearing

**Cause**: History file is empty or missing

**Solution**:
1. Check history file location (configured in `config.json`)
2. Verify file contains valid JSON with non-empty `keywords` array
3. Add keywords manually via application and restart

---

### Issue: Grid items overlap or misaligned

**Cause**: Layout calculation error or window size too small

**Solution**:
1. Verify `_calculate_grid_positions()` algorithm logic
2. Check Canvas width is measured correctly (`winfo_width()`)
3. Ensure labels have updated geometry (`label.update()` before measuring)

---

### Issue: Hover state not working

**Cause**: Event bindings not set correctly

**Solution**:
1. Verify `<Enter>` and `<Leave>` bindings on each Label
2. Check AppTheme.COLORS['bg_hover'] is defined
3. Test with simple print statement in binding to confirm event fires

---

### Issue: Click does not add keyword

**Cause**: `<Button-1>` binding missing or callback not set

**Solution**:
1. Verify `label.bind('<Button-1>', ...)` is called for each grid item
2. Confirm `self._on_keyword_added` callback is set during initialization
3. Add debug print in `_on_grid_item_click()` to confirm method is called

---

### Issue: Scrollbar not appearing

**Cause**: Canvas height not exceeding 200px or scrollregion not set

**Solution**:
1. Check actual content height calculation in `_calculate_grid_positions()`
2. Verify `canvas.configure(scrollregion=...)` is called after layout
3. Ensure scrollbar is gridded correctly and `yscrollcommand` is set

---

## Validation Summary

**Total Test Cases**: 13  
**Critical Path**: Cases 1, 3, 4, 7, 8, 11 (core functionality)  
**Edge Cases**: Cases 2, 10 (single keyword, long keyword)  
**Performance**: Case 13 (1000 keywords)  
**Unicode**: Case 9 (Cyrillic support)

**Definition of Done**:
- [ ] All 13 test cases pass manual validation
- [ ] No horizontal scrollbar appears in any test case
- [ ] Performance meets NFR (<200ms for 1000 keywords)
- [ ] Space efficiency improvement verified (2x more keywords visible)

---

## Next Steps

After validation passes:
1. Update CLAUDE.md with feature context
2. Generate tasks.md using `/tasks` command
3. Proceed with implementation following tasks
4. Re-run validation checklist after implementation
5. Test Windows build (PyInstaller .exe)

---

## Related Documentation

- Feature Spec: `specs/005-i-want-the/spec.md`
- Research: `specs/005-i-want-the/research.md`
- Data Model: `specs/005-i-want-the/data-model.md`
- UI Contract: `specs/005-i-want-the/contracts/ui-contract.md`
- Plan: `specs/005-i-want-the/plan.md`

