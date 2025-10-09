# Keyword Presets Feature - Product Requirements

**Version:** 1.0
**Status:** DRAFT
**Last Updated:** 2025-10-09
**Feature Type:** Enhancement

---

## Overview

Implement a Keyword Presets feature for the document extraction application that allows users to save and manage collections of keywords for reuse across multiple extraction runs.

---

## Feature Requirements

### UX Design (Option 3: Presets Panel)

Add a collapsible "Presets" section in the KeywordPanel component, positioned ABOVE the existing keyword history section. The section should:

#### 1. Header Section
- Display "Presets ▼" when collapsed (showing count: "Presets (3 saved)")
- Display "Presets ▲" when expanded
- Clickable to toggle expand/collapse state
- Default state: Collapsed on first use, remembers last state in config

#### 2. Preset Cards (when expanded)
Each preset displayed as a card showing:
- Preset name (bold, 14px)
- Keywords preview: Show first 3 keywords comma-separated, then "+N more" if additional keywords exist
- [Load] button on the right
- [...] menu button (⋮) for Edit/Delete actions

**Card Styling:**
- Light background (#F9FAFB)
- 1px border
- 8px border radius
- 8px spacing between cards
- Maximum height: 200px with vertical scrolling if needed

#### 3. Create New Preset Button
- Positioned at bottom of expanded presets section
- Text: "+ Create New Preset" (blue text, #2563EB)
- Opens preset creation dialog

#### 4. Preset Management Dialogs

**Create Dialog:**
- Simple modal with name input field
- Shows current active keywords (read-only)
- Save/Cancel buttons

**Edit Dialog:**
- Similar to create, but pre-populated with preset data
- Allows renaming and reordering keywords

**Delete Confirmation:**
- "Delete preset '[name]'?" with Delete/Cancel buttons

---

## Behavior Specifications

### Load Preset
- Clicking [Load] REPLACES all active keywords with the preset keywords (preserving order)
- Show confirmation dialog if active keywords exist: "Replace current keywords with preset '[name]'?"

### Create Preset
- Only enabled when at least 1 active keyword exists
- Saves current active keywords list with user-provided name

### Edit Preset
- Opens dialog to rename preset and modify keyword list (add/remove/reorder)

### Delete Preset
- Removes preset from saved list after confirmation

### Keyword Order
- Presets preserve the exact order keywords were in when saved

---

## Data Persistence

### Configuration Model Updates

Update the Configuration model (`src/models/configuration.py`):

**New Field:**
```python
keyword_presets: list[dict] = field(default_factory=list)
```

**Preset Structure:**
```python
{"name": str, "keywords": list[str]}
```

**Example config.json:**
```json
{
  "keyword_presets": [
    {
      "name": "Medical Report",
      "keywords": ["HTD", "RTP", "Temperature", "Pressure", "Volume"]
    },
    {
      "name": "Quality Check",
      "keywords": ["Volume", "Pressure", "Density"]
    }
  ],
  "keyword_history": [...],
  ...
}
```

### Validation Rules

- Preset names: Max 50 characters, alphanumeric + spaces only, must be unique
- Keywords: Same validation as existing keyword validation (max 100 chars)
- Presets saved to config.json alongside existing keyword_history

---

## Implementation Requirements

### 1. Update KeywordPanel
**File:** `src/ui/keyword_panel.py`

**Changes:**
- Add collapsible Presets section before history section (row 2)
- Implement preset card rendering with Load and menu buttons
- Add dialog windows for Create/Edit/Delete operations
- Wire up callbacks to notify controller of preset changes

### 2. Update Configuration Model
**File:** `src/models/configuration.py`

**Changes:**
- Add `keyword_presets` field with validation
- Add methods:
  - `add_preset(name: str, keywords: list[str]) -> bool`
  - `update_preset(old_name: str, new_name: str, keywords: list[str]) -> bool`
  - `delete_preset(name: str) -> bool`
  - `get_preset_by_name(name: str) -> dict | None`
  - `get_all_presets() -> list[dict]`
- Ensure presets are persisted when configuration is saved

### 3. Update ConfigurationManager
**File:** `src/services/configuration_manager.py`

**Changes:**
- Ensure preset data is loaded/saved correctly from config.json
- Handle migration for existing configs without presets field
- Add default empty list for `keyword_presets` if missing

### 4. Update AppController
**File:** `src/controllers/app_controller.py`

**Changes:**
- Add handlers for preset CRUD operations
- Connect KeywordPanel preset callbacks to configuration updates
- Ensure configuration is saved after preset modifications

---

## Visual Design Mockup

```
┌──────────────────────────────────────────────────────┐
│ Keywords                                             │
│                                                      │
│ [Enter keyword...                    ] [Add]        │
│                                                      │
│ ▼ Presets (2 saved)                                 │
│ ┌────────────────────────────────────────────────┐  │
│ │ Medical Report                   [Load] [⋮]    │  │
│ │ HTD, RTP, Temperature, +2 more                 │  │
│ ├────────────────────────────────────────────────┤  │
│ │ Quality Check                    [Load] [⋮]    │  │
│ │ Volume, Pressure, Density                      │  │
│ └────────────────────────────────────────────────┘  │
│ [+ Create New Preset]                               │
│                                                      │
│ History:                                             │
│ [HTD] [RTP] [Temperature] [Pressure] ...            │
│                                                      │
│ Active Keywords:                                     │
│ [HTD ×] [RTP ×]                                     │
│                                                      │
│ 2 keywords            [Clear All]                   │
└──────────────────────────────────────────────────────┘
```

---

## Acceptance Criteria

- [ ] User can create a preset from current active keywords with custom name
- [ ] User can load a preset, which replaces active keywords (with confirmation)
- [ ] User can edit preset name and keyword list
- [ ] User can delete presets (with confirmation)
- [ ] Presets section is collapsible and remembers state
- [ ] Presets persist across application restarts
- [ ] Preset names are validated (max 50 chars, unique, alphanumeric + spaces)
- [ ] Keywords in preset maintain their order
- [ ] UI matches existing application theme and styling (AppTheme)
- [ ] No impact to existing keyword history functionality
- [ ] Empty state shown when no presets exist: "No presets saved. Create one from your active keywords."

---

## Visual Design Notes

Follow the existing AppTheme constants (`src/ui/theme.py`) for:

- **Colors:** Use `COLORS['bg']`, `COLORS['primary_light']`, `COLORS['text']`, etc.
- **Fonts:** Use `FONTS['body']`, `FONTS['body_bold']`
- **Spacing:** Use `PADDING['small']`, `PADDING['medium']`, `PADDING['large']`
- **Border radius:** 8px for cards, consistent with existing design

---

## Future Enhancements (Out of Scope)

- Import/export presets to external files
- Share presets between users
- Preset categories/tagging
- Default preset selection
- Preset usage analytics

---

## Dependencies

- No new external dependencies required
- Uses existing tkinter components and styling
- Leverages existing configuration persistence infrastructure

---

**END OF DOCUMENT**
