# Tasks: Keyword Presets Management

**Feature**: Keyword Presets Management
**Branch**: `008-docs-presets-prd`
**Input**: Design documents from `/Users/A1E6E98/Developer/kris-extractor/specs/008-docs-presets-prd/`
**Prerequisites**: plan.md, data-model.md, contracts/, research.md, quickstart.md

---

## Execution Flow
```
1. Load plan.md from feature directory
   → ✅ Tech stack: Python 3.10+, tkinter (built-in)
   → ✅ Libraries: No new dependencies
   → ✅ Structure: Single project with src/ structure
2. Load design documents:
   → ✅ data-model.md: KeywordPreset entity, Configuration extensions
   → ✅ contracts/config-api.md: Configuration CRUD methods
   → ✅ contracts/preset-ui.md: KeywordPanel UI components
   → ✅ research.md: Design decisions documented
   → ✅ quickstart.md: Manual validation checklist
3. Generate tasks by category:
   → Setup: None required (extends existing codebase)
   → Core: Configuration model, ConfigurationManager, KeywordPanel UI
   → Integration: AppController callback wiring
   → Validation: Manual testing checklist
4. Task ordering:
   → Models first (Configuration)
   → Persistence layer (ConfigurationManager)
   → UI components (KeywordPanel)
   → Integration (AppController)
   → Validation last
5. Apply parallelization:
   → [P] marks tasks in different files with no dependencies
   → Same file tasks are sequential
```

---

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- File paths are absolute and explicit
- Each task is independently executable

---

## Phase 3.1: Configuration Model & Persistence

### T001: Extend Configuration Model with Preset Fields
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/models/configuration.py`

**Description**: Add `keyword_presets` and `presets_section_expanded` fields to Configuration dataclass

**Requirements**:
- Add field: `keyword_presets: list[dict] = field(default_factory=list)`
- Add field: `presets_section_expanded: bool = False`
- Add `__post_init__` validation for preset structure (each dict must have 'name' and 'keywords' keys)
- Validate preset names: 1-50 chars, alphanumeric + spaces, case-insensitive uniqueness
- Validate keywords in presets: 1-100 chars each

**Reference**: 
- `specs/008-docs-presets-prd/data-model.md` lines 74-193
- `specs/008-docs-presets-prd/contracts/config-api.md` lines 218-235

**Acceptance**:
- [X] `keyword_presets` field exists with default empty list
- [X] `presets_section_expanded` field exists with default False
- [X] `__post_init__` validates preset dict structure
- [X] Invalid presets raise ValueError in `__post_init__`

---

### T002: Implement Configuration Preset CRUD Methods
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/models/configuration.py`

**Description**: Add preset management methods to Configuration model

**Requirements**:
- Implement `add_preset(name: str, keywords: list[str]) -> tuple[bool, str]`
- Implement `update_preset(old_name: str, new_name: str, keywords: list[str]) -> tuple[bool, str]`
- Implement `delete_preset(name: str) -> bool`
- Implement `get_preset_by_name(name: str) -> dict | None`
- Implement `get_all_presets() -> list[dict]`
- Implement `_validate_preset_name(name: str, exclude_name: str = None) -> tuple[bool, str]` (private helper)

**Validation Rules**:
- Name: 1-50 chars, regex `^[a-zA-Z0-9 ]+$`, case-insensitive uniqueness
- Keywords: Each 1-100 chars, no duplicates within preset
- Return `(False, error_message)` on validation failure, never raise exceptions in public API

**Reference**: 
- `specs/008-docs-presets-prd/contracts/config-api.md` lines 9-214
- `specs/008-docs-presets-prd/data-model.md` lines 104-193

**Acceptance**:
- [X] All 5 CRUD methods implemented
- [X] Name validation matches regex and uniqueness rules
- [X] Methods return `(bool, str)` tuple for add/update operations
- [X] `delete_preset` returns bool (no error messages)
- [X] `get_all_presets` returns copy of list (not reference)

**Dependencies**: T001

---

### T003: [P] Update ConfigurationManager for Preset Persistence
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/services/configuration_manager.py`

**Description**: Add preset field loading and saving to ConfigurationManager

**Requirements**:
- In `load()` method: Load `keyword_presets` with default empty list
- Filter corrupted presets (missing 'name' or 'keywords' keys)
- Load `presets_section_expanded` with default False
- In `save()` method: Persist `keyword_presets` and `presets_section_expanded` to JSON
- Use `ensure_ascii=False` for Unicode support (already configured)

**Migration Logic**:
```python
# In load() method
keyword_presets = data.get('keyword_presets', [])
valid_presets = [
    p for p in keyword_presets
    if isinstance(p, dict) and 'name' in p and 'keywords' in p and isinstance(p['keywords'], list)
]
config.keyword_presets = valid_presets
config.presets_section_expanded = data.get('presets_section_expanded', False)
```

**Reference**: 
- `specs/008-docs-presets-prd/data-model.md` lines 196-238
- `specs/008-docs-presets-prd/contracts/config-api.md` lines 242-261

**Acceptance**:
- [X] `load()` handles missing `keyword_presets` field (defaults to empty list)
- [X] Corrupted presets are filtered out during load
- [X] `presets_section_expanded` defaults to False if missing
- [X] `save()` persists both new fields to config.json
- [X] Existing configs load without errors (graceful migration)

**Dependencies**: T001 (requires Configuration fields to exist)

---

## Phase 3.2: KeywordPanel UI Components

### T004: Build Presets Section Header in KeywordPanel
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Add collapsible header for presets section

**Requirements**:
- Add `_build_presets_header()` method returning ttk.Label
- Header text: "Presets ▼ (N saved)" when collapsed, "Presets ▲" when expanded
- Bind click event to `_toggle_presets_section()`
- Add `_update_header_text()` to update preset count
- Store header as instance variable `self.presets_header_label`
- Grid at appropriate row (before keyword history section)
- Use `AppTheme.FONTS['body_bold']` and `AppTheme.COLORS['text']`

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 38-68
- `specs/008-docs-presets-prd/research.md` lines 36-64

**Acceptance**:
- [X] Header label displays with correct text format
- [X] Click on header toggles section (implement stub for now)
- [X] Header text updates with preset count
- [X] Positioned above keyword history section

**Dependencies**: T001 (needs to understand preset structure)

---

### T005: Build Preset Cards Container with Scrolling
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Create scrollable container for preset cards

**Requirements**:
- Add `_build_preset_cards_container()` returning (Canvas, Scrollbar, Frame)
- Canvas max height: 200px (per FR-016)
- Vertical scrollbar appears when content exceeds 200px
- Container grids below presets header
- Add `_show_empty_state()` for "No presets saved. Create one from your active keywords." message
- Store as instance variables: `self.presets_canvas`, `self.presets_scrollbar`, `self.presets_cards_frame`

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 133-166
- `specs/008-docs-presets-prd/data-model.md` lines 293-305

**Acceptance**:
- [X] Canvas with Frame and Scrollbar created
- [X] Max height 200px enforced
- [X] Scrolling works when content exceeds height
- [X] Empty state message displays when no presets
- [X] Container positioned in grid layout

**Dependencies**: T004 (needs header to exist for grid positioning)

---

### T006: Implement Preset Card Rendering
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Create preset card widgets and rendering logic

**Requirements**:
- Add `_create_preset_card(preset: dict) -> tk.Frame` method
- Card layout: Name (bold 14px), keywords preview, [Load] button, [⋮] menu button
- Add `_format_keywords_preview(keywords: list[str]) -> str` helper
  - First 3 keywords: "kw1, kw2, kw3"
  - More than 3: "kw1, kw2, kw3, +N more"
- Add `_render_preset_cards()` to populate cards container
- Card styling: Background #F9FAFB, 1px border, 8px border radius, 8px padding
- Bind [Load] button to load callback (stub for now)
- Bind [⋮] menu to show Edit/Delete options (stub for now)

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 72-131
- `specs/008-docs-presets-prd/research.md` lines 66-94

**Acceptance**:
- [X] Preset cards display with correct layout
- [X] Keywords preview formats correctly (3 vs >3 keywords)
- [X] Load and menu buttons present and styled
- [X] Cards render in scrollable container
- [X] Styling matches specification

**Dependencies**: T005 (needs container to render cards into)

---

### T007: Implement Create Preset Dialog
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Build modal dialog for creating new presets

**Requirements**:
- Add `_show_create_dialog()` method (modal Toplevel window)
- Dialog layout: Name Entry field, read-only keywords display, Save/Cancel buttons
- Display current active keywords (read-only label)
- Validate name on input change
- Show error message in red text below name field
- Disable Save button until validation passes
- On Save: Call `self._preset_create_callback(name, keywords)` if registered
- On Cancel: Close dialog
- Add "+ Create New Preset" button to main panel (calls `_show_create_dialog`)
- Add `_update_create_button_state()` to enable/disable based on active keywords

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 169-241
- `specs/008-docs-presets-prd/data-model.md` lines 242-255

**Acceptance**:
- [X] Dialog opens with name field and keywords display
- [X] Name validation shows error messages
- [X] Save button disabled until valid input
- [X] Create button in main panel positioned correctly
- [X] Create button disabled when no active keywords

**Dependencies**: T006 (needs card rendering for refresh after create)

---

### T008: Implement Edit Preset Dialog
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Build modal dialog for editing existing presets

**Requirements**:
- Add `_show_edit_dialog(preset_name: str)` method (modal Toplevel)
- Pre-fill name Entry with current preset name
- Display keywords as editable chips (add/remove capability)
- Validate name (exclude current preset from uniqueness check)
- Show error messages for invalid input
- On Save: Call `self._preset_edit_callback(old_name, new_name, keywords)`
- On Cancel: Close dialog
- Wire [⋮] menu button in cards to show Edit option

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 243-286
- `specs/008-docs-presets-prd/data-model.md` lines 268-278

**Acceptance**:
- [X] Dialog pre-fills with current preset data
- [X] Keywords are editable (add/remove chips)
- [X] Name validation excludes current preset
- [X] Save calls callback with updated data
- [X] Menu button opens Edit option

**Dependencies**: T007 (similar dialog pattern, reuse validation)

---

### T009: Implement Delete and Load Confirmation Dialogs
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Add confirmation dialogs for delete and load operations

**Requirements**:
- Add `_show_delete_confirmation(preset_name: str)` using messagebox.askyesno
  - Message: "Delete preset '{name}'?"
  - On Yes: Call `self._preset_delete_callback(name)`
- Add `_show_load_confirmation(preset_name: str) -> bool`
  - Message: "Replace current keywords with preset '{name}'?"
  - Only show if active keywords exist
  - Return True if confirmed, False if cancelled
- Wire [Load] button in cards to check for active keywords and show confirmation
- Wire [⋮] menu to show Delete option

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 288-351
- `specs/008-docs-presets-prd/data-model.md` lines 256-267, 280-289

**Acceptance**:
- [X] Delete confirmation shows and works
- [X] Load confirmation shows only when active keywords exist
- [X] Load proceeds without confirmation when no active keywords
- [X] Callbacks are called on confirmation

**Dependencies**: T008 (completes dialog implementations)

---

### T010: Wire Preset Callbacks and State Management
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/ui/keyword_panel.py`

**Description**: Implement callback registration and state management

**Requirements**:
- Add callback registration methods:
  - `on_preset_create(callback)`
  - `on_preset_load(callback)`
  - `on_preset_edit(callback)`
  - `on_preset_delete(callback)`
  - `on_presets_section_toggled(callback)`
- Add public methods:
  - `refresh_presets(presets: list[dict])`
  - `set_presets_expanded(expanded: bool)`
- Implement `_toggle_presets_section()` to show/hide container and call toggle callback
- Add instance variables: `_presets`, `_presets_expanded`, callback variables
- Update `_update_create_button_state()` when active keywords change

**Reference**: 
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 353-473
- `specs/008-docs-presets-prd/data-model.md` lines 242-289

**Acceptance**:
- [X] All callback registration methods implemented
- [X] `refresh_presets()` updates card display
- [X] `set_presets_expanded()` updates visibility
- [X] Toggle works and persists state
- [X] Create button state updates with active keywords

**Dependencies**: T009 (needs all dialogs complete)

---

## Phase 3.3: Integration

### T011: Wire Preset Callbacks in AppController
**File**: `/Users/A1E6E98/Developer/kris-extractor/src/controllers/app_controller.py`

**Description**: Connect KeywordPanel preset callbacks to Configuration and persistence

**Requirements**:
- Add `on_preset_created(name: str, keywords: list[str])` method
  - Call `self.config.add_preset(name, keywords)`
  - If success: Save config, refresh KeywordPanel presets
  - If error: Show error message (implement error display)
- Add `on_preset_loaded(preset_name: str)` method
  - Get preset via `self.config.get_preset_by_name(preset_name)`
  - Call `self.keyword_panel.set_active_keywords(preset['keywords'])`
- Add `on_preset_updated(old_name: str, new_name: str, keywords: list[str])` method
  - Call `self.config.update_preset(old_name, new_name, keywords)`
  - If success: Save config, refresh KeywordPanel
- Add `on_preset_deleted(name: str)` method
  - Call `self.config.delete_preset(name)`
  - Save config, refresh KeywordPanel
- Add `on_presets_section_toggled(expanded: bool)` method
  - Update `self.config.presets_section_expanded = expanded`
  - Save config
- Register all callbacks in `__init__` or setup method
- Initialize KeywordPanel with presets on startup:
  - `keyword_panel.set_presets_expanded(config.presets_section_expanded)`
  - `keyword_panel.refresh_presets(config.get_all_presets())`

**Reference**: 
- `specs/008-docs-presets-prd/contracts/config-api.md` lines 263-293
- `specs/008-docs-presets-prd/contracts/preset-ui.md` lines 353-473

**Acceptance**:
- [X] All preset callbacks registered with KeywordPanel
- [X] Create/Update/Delete operations persist to config.json
- [X] Load operation updates active keywords
- [X] Toggle state persists across sessions
- [X] Presets load on application startup
- [X] Error messages display for validation failures

**Dependencies**: T002 (Configuration CRUD), T003 (persistence), T010 (UI callbacks)

---

## Phase 3.4: Validation & Polish

### T012: Execute Manual Validation Checklist
**File**: `/Users/A1E6E98/Developer/kris-extractor/specs/008-docs-presets-prd/quickstart.md`

**Description**: Perform manual testing of all preset functionality

**Test Suites**:
1. **Preset Creation** (TC-001 to TC-006): Valid/invalid names, button states, preview formatting
2. **Preset Loading** (TC-007 to TC-009): Load with/without active keywords, confirmation, order preservation
3. **Preset Editing** (TC-010 to TC-013): Edit name, keywords, validation, same-name handling
4. **Preset Deletion** (TC-014 to TC-015): Confirmation, empty state
5. **Section Toggle** (TC-016 to TC-018): Expand/collapse, state persistence, default state
6. **Data Persistence** (TC-019 to TC-021): Session persistence, config file format, corrupted data handling
7. **UI Layout** (TC-022 to TC-023): Scrolling with 20+ presets, card styling
8. **Integration** (TC-024 to TC-025): History independence, no history modification
9. **Unicode Support** (TC-026 to TC-027): Cyrillic keywords (validation rules clarified)
10. **Performance** (TC-028 to TC-029): 50 presets load time, 20 keywords load time
11. **Regression** (TC-030 to TC-032): Existing keyword history, active keywords, manual entry

**Validation Process**:
- Test on Windows 10/11 (primary platform)
- Test on macOS (development platform)
- Check all ✅ items in quickstart.md
- Document any failures or unexpected behavior

**Reference**: 
- `specs/008-docs-presets-prd/quickstart.md` (entire file)
- `specs/008-docs-presets-prd/plan.md` lines 54-59 (testing requirements)

**Acceptance**:
- [X] All test cases in quickstart.md pass
- [X] No regressions in existing functionality
- [X] Presets persist correctly across sessions
- [X] UI renders correctly on both platforms
- [X] Performance meets targets (<100ms for preset operations)

**Dependencies**: T011 (all implementation complete)

---

## Dependencies Graph

```
T001 (Config fields)
  ├─→ T002 (CRUD methods)
  │    └─→ T011 (AppController)
  └─→ T003 [P] (ConfigurationManager)
       └─→ T011

T004 (Presets header)
  └─→ T005 (Cards container)
       └─→ T006 (Card rendering)
            └─→ T007 (Create dialog)
                 └─→ T008 (Edit dialog)
                      └─→ T009 (Confirmations)
                           └─→ T010 (Callbacks/state)
                                └─→ T011

T011 (AppController)
  └─→ T012 (Manual validation)
```

---

## Parallel Execution Examples

### Parallel Group 1: After T001 completes
```bash
# Launch T002 and T003 together (different files):
Task: "Configuration CRUD methods in src/models/configuration.py"
Task: "ConfigurationManager persistence in src/services/configuration_manager.py"
```

### Sequential Execution: T004-T010
```bash
# UI tasks in same file - must be sequential:
Task T004 → T005 → T006 → T007 → T008 → T009 → T010
```

---

## Notes

- **No new dependencies**: Feature uses only tkinter (built-in)
- **Graceful degradation**: Existing configs without preset fields load correctly
- **Unicode support**: Keywords support Cyrillic (validated via existing keyword validation)
- **Preset names**: Alphanumeric + spaces only (Latin characters per validation regex)
- **Performance target**: <100ms for all preset operations
- **Testing**: Manual validation only (per constitution, no automated tests)
- **Commit strategy**: Commit after each task completion
- **File conflicts**: T002 modifies same file as T001 (configuration.py) - must be sequential
- **UI tasks**: T004-T010 all modify keyword_panel.py - sequential execution required

---

## Validation Checklist
*GATE: Verify before marking feature complete*

- [X] All entities have model tasks: ✅ KeywordPreset (logical entity in Configuration)
- [X] All contracts implemented: ✅ config-api.md (T002), preset-ui.md (T004-T010)
- [X] Parallel tasks truly independent: ✅ Only T003 marked [P] (different file, minimal dependency)
- [X] Each task specifies exact file path: ✅ All tasks have absolute paths
- [X] No task modifies same file as another [P] task: ✅ T003 is only [P] task
- [X] Manual validation tasks included: ✅ T012 covers all test suites from quickstart.md
- [X] All design documents referenced: ✅ plan.md, data-model.md, contracts/, research.md, quickstart.md

---

**Feature Ready for Implementation**: ✅
**Total Tasks**: 12 (T001-T012)
**Estimated Completion Time**: 8-12 hours (based on UI complexity and manual testing)
**Risk Level**: Low (extends existing patterns, no new dependencies)

---

*Generated from `.specify/templates/tasks-template.md` based on Constitution v1.0.0*

