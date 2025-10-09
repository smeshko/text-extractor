# Manual Validation Checklist: Keyword Presets

**Feature**: Keyword Presets Management
**Date**: 2025-10-09
**Purpose**: Manual testing checklist for validating preset functionality

---

## Prerequisites

- [ ] Application builds successfully
- [ ] Application launches without errors
- [ ] config.json exists or is created with defaults
- [ ] KeywordPanel displays with existing keywords/history sections

---

## Test Suite 1: Preset Creation

### TC-001: Create Preset with Valid Name and Keywords

**Setup**:
1. Launch application
2. Add keywords: "HTD", "RTP", "Temperature"
3. Verify 3 active keywords displayed

**Steps**:
1. Click "+ Create New Preset" button
2. Enter preset name: "Medical Report"
3. Verify keywords shown: "HTD, RTP, Temperature" (read-only)
4. Click [Save]

**Expected**:
- ✅ Preset card appears in Presets section
- ✅ Card shows: "Medical Report" (bold), "HTD, RTP, Temperature"
- ✅ Card has [Load] and [⋮] buttons
- ✅ Active keywords remain: "HTD", "RTP", "Temperature"

---

### TC-002: Create Preset Button Disabled (No Active Keywords)

**Setup**:
1. Launch application
2. Ensure no active keywords (click Clear All if needed)

**Steps**:
1. Observe "+ Create New Preset" button

**Expected**:
- ✅ Button is disabled (grayed out, not clickable)

**Steps**:
1. Add keyword "HTD"
2. Observe button state

**Expected**:
- ✅ Button is now enabled (clickable)

---

### TC-003: Preset Name Validation - Too Long

**Setup**:
1. Add keywords: "HTD", "RTP"
2. Click "+ Create New Preset"

**Steps**:
1. Enter name: "A" repeated 51 times (51 characters)
2. Attempt to save

**Expected**:
- ✅ Error message: "Name must be 1-50 characters"
- ✅ Dialog remains open
- ✅ Save button disabled or error shown

---

### TC-004: Preset Name Validation - Special Characters

**Setup**:
1. Add keywords: "HTD", "RTP"
2. Click "+ Create New Preset"

**Steps**:
1. Enter name: "Report@123"
2. Attempt to save

**Expected**:
- ✅ Error message: "Name can only contain letters, numbers, and spaces"
- ✅ Dialog remains open

---

### TC-005: Preset Name Validation - Duplicate Name

**Setup**:
1. Create preset "Medical Report" with keywords "HTD", "RTP"
2. Add new keywords: "Volume", "Pressure"
3. Click "+ Create New Preset"

**Steps**:
1. Enter name: "Medical Report" (same as existing)
2. Attempt to save

**Expected**:
- ✅ Error message: "Preset name already exists"
- ✅ Dialog remains open

**Steps**:
1. Change name to: "medical report" (lowercase)
2. Attempt to save

**Expected**:
- ✅ Error message: "Preset name already exists" (case-insensitive check)

---

### TC-006: Preset with 5+ Keywords (Preview Formatting)

**Setup**:
1. Add keywords: "HTD", "RTP", "Temperature", "Pressure", "Volume"
2. Click "+ Create New Preset"

**Steps**:
1. Enter name: "Full Medical"
2. Save preset

**Expected**:
- ✅ Preset card shows: "HTD, RTP, Temperature, +2 more"
- ✅ First 3 keywords displayed, then "+2 more"

---

## Test Suite 2: Preset Loading

### TC-007: Load Preset (No Active Keywords)

**Setup**:
1. Create preset "Test Preset" with keywords "HTD", "RTP", "Temperature"
2. Clear all active keywords

**Steps**:
1. Click [Load] button on "Test Preset" card

**Expected**:
- ✅ No confirmation dialog (no active keywords to replace)
- ✅ Active keywords update to: "HTD", "RTP", "Temperature"
- ✅ Active chips displayed in order
- ✅ Keyword count shows "3 keywords"

---

### TC-008: Load Preset (With Active Keywords - Confirmation)

**Setup**:
1. Create preset "Preset A" with keywords "HTD", "RTP"
2. Clear active keywords
3. Add different keywords: "Volume", "Pressure"

**Steps**:
1. Click [Load] button on "Preset A" card

**Expected**:
- ✅ Confirmation dialog appears: "Replace current keywords with preset 'Preset A'?"
- ✅ [Replace] and [Cancel] buttons visible

**Steps**:
1. Click [Cancel]

**Expected**:
- ✅ Dialog closes
- ✅ Active keywords remain: "Volume", "Pressure" (unchanged)

**Steps**:
1. Click [Load] again
2. Click [Replace]

**Expected**:
- ✅ Active keywords update to: "HTD", "RTP"
- ✅ Previous keywords "Volume", "Pressure" removed

---

### TC-009: Loaded Keywords Appear in Insertion Order

**Setup**:
1. Create preset "Ordered" with keywords in specific order: "Zebra", "Apple", "Mango"

**Steps**:
1. Load preset "Ordered"

**Expected**:
- ✅ Active keywords display in exact order: "Zebra", "Apple", "Mango"
- ✅ NOT alphabetically sorted

---

## Test Suite 3: Preset Editing

### TC-010: Edit Preset Name

**Setup**:
1. Create preset "Old Name" with keywords "HTD", "RTP"

**Steps**:
1. Click [⋮] menu button on preset card
2. Select "Edit"
3. Change name to: "New Name"
4. Click [Save]

**Expected**:
- ✅ Preset card updates to show "New Name"
- ✅ Keywords remain "HTD", "RTP"
- ✅ Preset count unchanged

---

### TC-011: Edit Preset Keywords (Add/Remove)

**Setup**:
1. Create preset "Edit Test" with keywords "HTD", "RTP"

**Steps**:
1. Click [⋮] → Edit
2. Add keyword "Temperature" in dialog
3. Remove keyword "HTD" in dialog
4. Click [Save]

**Expected**:
- ✅ Preset card updates to show "RTP, Temperature"
- ✅ Name remains "Edit Test"

---

### TC-012: Edit Preset - Rename to Existing Name (Validation)

**Setup**:
1. Create preset "Preset A" with keywords "HTD"
2. Create preset "Preset B" with keywords "RTP"

**Steps**:
1. Click [⋮] → Edit on "Preset B"
2. Change name to: "Preset A" (already exists)
3. Attempt to save

**Expected**:
- ✅ Error message: "Preset name already exists"
- ✅ Dialog remains open

---

### TC-013: Edit Preset - Keep Same Name (No Conflict)

**Setup**:
1. Create preset "Unchanged" with keywords "HTD", "RTP"

**Steps**:
1. Click [⋮] → Edit on "Unchanged"
2. Keep name as "Unchanged"
3. Add keyword "Temperature"
4. Click [Save]

**Expected**:
- ✅ No error (same name allowed when editing same preset)
- ✅ Keywords updated to "HTD", "RTP", "Temperature"

---

## Test Suite 4: Preset Deletion

### TC-014: Delete Preset (Confirmation)

**Setup**:
1. Create preset "To Delete" with keywords "HTD"

**Steps**:
1. Click [⋮] menu button on preset card
2. Select "Delete"

**Expected**:
- ✅ Confirmation dialog: "Delete preset 'To Delete'?"
- ✅ [Delete] and [Cancel] buttons visible

**Steps**:
1. Click [Cancel]

**Expected**:
- ✅ Dialog closes
- ✅ Preset still visible in list

**Steps**:
1. Click [⋮] → Delete again
2. Click [Delete]

**Expected**:
- ✅ Preset card disappears from list
- ✅ Preset count decrements

---

### TC-015: Delete All Presets (Empty State)

**Setup**:
1. Create 2 presets: "Preset 1", "Preset 2"

**Steps**:
1. Delete "Preset 1" (confirm)
2. Delete "Preset 2" (confirm)

**Expected**:
- ✅ Presets section shows: "No presets saved. Create one from your active keywords."
- ✅ Header shows: "Presets ▼ (0 saved)"
- ✅ "+ Create New Preset" button still visible

---

## Test Suite 5: Presets Section Collapse/Expand

### TC-016: Toggle Section State

**Setup**:
1. Create preset "Test"
2. Ensure Presets section is expanded (cards visible)

**Steps**:
1. Click "Presets ▲" header

**Expected**:
- ✅ Preset cards container hides
- ✅ Header text changes to: "Presets ▼ (1 saved)"

**Steps**:
1. Click "Presets ▼ (1 saved)" header

**Expected**:
- ✅ Preset cards container shows
- ✅ Header text changes to: "Presets ▲"

---

### TC-017: Section State Persists Across Restarts

**Setup**:
1. Create preset "Persist Test"
2. Expand Presets section (header shows "▲")

**Steps**:
1. Close application
2. Relaunch application

**Expected**:
- ✅ Presets section is expanded (same state as before close)
- ✅ Header shows "Presets ▲"

**Steps**:
1. Collapse section (header shows "▼")
2. Close and relaunch application

**Expected**:
- ✅ Presets section is collapsed
- ✅ Header shows "Presets ▼ (1 saved)"

---

### TC-018: Default State on First Launch

**Setup**:
1. Delete config.json (or use fresh install)
2. Launch application

**Steps**:
1. Create first preset "First"
2. Observe Presets section

**Expected**:
- ✅ Section is collapsed by default (header shows "▼")
- ✅ Header shows: "Presets ▼ (1 saved)"

---

## Test Suite 6: Data Persistence

### TC-019: Presets Persist Across Sessions

**Setup**:
1. Create 3 presets:
   - "Preset A" with keywords "HTD", "RTP"
   - "Preset B" with keywords "Volume", "Pressure"
   - "Preset C" with keywords "Temperature"

**Steps**:
1. Close application
2. Relaunch application

**Expected**:
- ✅ All 3 presets visible in Presets section
- ✅ Preset names and keywords match original
- ✅ Order preserved (insertion order)

---

### TC-020: Config File Contains Preset Data

**Setup**:
1. Create preset "File Test" with keywords "HTD", "RTP"

**Steps**:
1. Open config.json in text editor
2. Search for "keyword_presets"

**Expected**:
- ✅ Field exists: `"keyword_presets": [...]`
- ✅ Contains dict: `{"name": "File Test", "keywords": ["HTD", "RTP"]}`
- ✅ Field `"presets_section_expanded"` exists (true or false)

---

### TC-021: Corrupted Preset Data (Graceful Degradation)

**Setup**:
1. Create preset "Valid Preset" with keywords "HTD"
2. Close application
3. Manually edit config.json:
   - Add corrupted preset: `{"name": "Corrupted"}` (missing "keywords" field)
   - Keep "Valid Preset" intact

**Steps**:
1. Relaunch application

**Expected**:
- ✅ Application launches without crash
- ✅ "Valid Preset" loads and displays
- ✅ Corrupted preset is skipped (not displayed)
- ✅ Console warning: "Skipping corrupted preset: {...}"

---

## Test Suite 7: UI Layout and Scrolling

### TC-022: Scrolling with 20+ Presets

**Setup**:
1. Create 25 presets with names "Preset 01" through "Preset 25"

**Steps**:
1. Expand Presets section
2. Observe preset cards container

**Expected**:
- ✅ Container height is 200px (max height)
- ✅ Vertical scrollbar visible
- ✅ All 25 presets accessible via scroll

---

### TC-023: Preset Card Styling

**Setup**:
1. Create preset "Style Test" with 3 keywords

**Steps**:
1. Observe preset card appearance

**Expected**:
- ✅ Background color: Light gray (#F9FAFB or similar)
- ✅ Border: 1px solid, visible
- ✅ Border radius: 8px (rounded corners)
- ✅ Padding: 8px around content
- ✅ Name is bold, 14px font
- ✅ [Load] button on right side
- ✅ [⋮] menu button far right

---

## Test Suite 8: Integration with Keyword History

### TC-024: Preset Loading Does Not Affect History

**Setup**:
1. Add keywords "HTD", "RTP" manually (adds to history)
2. Create preset "Test" with "Volume", "Pressure"
3. Clear active keywords

**Steps**:
1. Load preset "Test"
2. Observe keyword history section

**Expected**:
- ✅ Active keywords: "Volume", "Pressure"
- ✅ History still contains: "HTD", "RTP"
- ✅ History NOT affected by preset load

---

### TC-025: Creating Preset Does Not Modify History

**Setup**:
1. Clear keyword history (if possible, or use fresh config)
2. Add keywords "HTD", "RTP" via input field
3. Create preset "No History Change" with current keywords

**Steps**:
1. Observe keyword history

**Expected**:
- ✅ History contains: "HTD", "RTP" (from manual entry)
- ✅ Creating preset does NOT duplicate keywords in history

---

## Test Suite 9: Unicode Support

### TC-026: Preset Name with Cyrillic Characters

**Setup**:
1. Add keywords "HTD", "RTP"
2. Click "+ Create New Preset"

**Steps**:
1. Enter name: "Медицинский отчет" (Cyrillic)
2. Attempt to save

**Expected**:
- ✅ Error message: "Name can only contain letters, numbers, and spaces"
- ✅ Cyrillic not allowed per validation rules (alphanumeric = Latin only)

**Note**: Per PRD specification, preset names are alphanumeric + spaces (Latin characters). If Unicode support is required, update validation regex to `^[\w ]+$` and retest.

---

### TC-027: Keywords with Cyrillic (Existing Validation)

**Setup**:
1. Add keyword: "ГТД" (Cyrillic)
2. Add keyword: "РТП" (Cyrillic)
3. Create preset "Test Cyrillic"

**Steps**:
1. Save preset
2. Load preset

**Expected**:
- ✅ Cyrillic keywords preserved: "ГТД", "РТП"
- ✅ Display correctly in preset card preview
- ✅ Load correctly into active keywords

---

## Test Suite 10: Performance

### TC-028: Create 50 Presets (Performance)

**Setup**:
1. Use script or manual creation to create 50 presets

**Steps**:
1. Expand Presets section
2. Observe load time

**Expected**:
- ✅ Section expands in <200ms
- ✅ Scrolling is smooth (no lag)
- ✅ Cards render without visual glitches

---

### TC-029: Load Preset with 20 Keywords

**Setup**:
1. Create preset "Large" with 20 keywords

**Steps**:
1. Click [Load] on preset
2. Observe active keywords display

**Expected**:
- ✅ All 20 keywords load in <100ms
- ✅ Active chips render without lag
- ✅ Keyword count shows "20 keywords"

---

## Regression Tests

### TC-030: Existing Keyword History Functionality

**Verify**:
- ✅ Keyword history still displays
- ✅ Clicking history keyword adds to active keywords
- ✅ History persists across sessions
- ✅ History does NOT show keywords already in active list

### TC-031: Active Keywords Functionality

**Verify**:
- ✅ Active keywords display as chips
- ✅ Clicking [×] removes keyword
- ✅ Clear All button works
- ✅ Keyword count updates correctly

### TC-032: Manual Keyword Entry

**Verify**:
- ✅ Input field accepts text
- ✅ Add button adds keyword to active list
- ✅ Enter key adds keyword
- ✅ Duplicate validation works (case-insensitive)
- ✅ Max length validation (100 chars)

---

## Pass/Fail Criteria

**Pass**: All ✅ checkboxes marked in all test suites
**Fail**: Any test case fails, requires bug fix and retest

---

## Notes for Tester

- Test on Windows 10/11 (primary platform)
- Test on macOS (development platform)
- Manual testing only (no automated tests per constitution)
- Report any unexpected behavior or UI glitches
- Verify Unicode support for keywords (Cyrillic priority)

---

**Tester Name**: _______________
**Date**: _______________
**Result**: ☐ PASS  ☐ FAIL (with bug IDs: _______________)
