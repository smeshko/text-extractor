# Phase 0: Research & Design Decisions

**Feature**: Keyword Presets Management
**Date**: 2025-10-09
**Status**: ✅ COMPLETED

## Research Summary

This feature extends existing patterns rather than introducing new technologies. All architectural decisions leverage established infrastructure from the codebase.

---

## Decision 1: Preset Data Structure

**Decision**: Use list of dictionaries in Configuration model
```python
keyword_presets: list[dict] = field(default_factory=list)
# Each dict: {"name": str, "keywords": list[str]}
```

**Rationale**:
- Matches existing `keyword_history: list[str]` pattern in Configuration model
- JSON-serializable without custom encoders (ConfigurationManager already uses json.dump)
- Supports ordered presets (insertion order preserved in Python 3.7+)
- Simple validation logic (check dict keys, validate types)

**Alternatives Considered**:
1. **Separate PresetModel class** - Rejected: Adds complexity, requires custom JSON serialization
2. **Flat structure with preset_names + preset_keywords arrays** - Rejected: Hard to maintain consistency, prone to index mismatches
3. **Nested object with PresetCollection** - Rejected: Violates constitution (excessive abstraction for 2-user project)

**Code Reference**: `src/models/configuration.py:28` (keyword_history field as template)

---

## Decision 2: UI Layout - Collapsible Section

**Decision**: Add collapsible Presets section to KeywordPanel using tkinter Frame + grid layout

**Rationale**:
- Existing KeywordPanel already uses grid layout (row-based sections)
- Collapsible pattern: Header Label with click binding + conditional frame visibility
- Preserves single-screen workflow (section collapses to save space)
- Follows AppTheme styling conventions (COLORS, FONTS, PADDING)

**Alternatives Considered**:
1. **Separate window/dialog** - Rejected: Violates single-screen GUI principle
2. **Tabs in KeywordPanel** - Rejected: Adds navigation complexity, less intuitive
3. **Always-expanded section** - Rejected: Consumes too much vertical space when user has many presets

**Code Reference**: `src/ui/keyword_panel.py:142-175` (grid layout pattern), `src/ui/theme.py` (AppTheme constants)

**Implementation Pattern**:
```python
# Header (row N)
header_label = ttk.Label(self, text="Presets ▼ (N saved)")
header_label.bind('<Button-1>', self._toggle_presets)

# Content frame (row N+1)
self.presets_frame = ttk.Frame(self)
self.presets_frame.grid(row=N+1, column=0, sticky=(tk.W, tk.E))
# Grid/forget to toggle visibility
```

---

## Decision 3: Preset Cards Rendering

**Decision**: Render each preset as a card Frame with name label, keywords preview, Load button, and menu button

**Card Structure**:
- Background: AppTheme.COLORS['bg_light'] (#F9FAFB per PRD)
- Border: 1px solid, 8px border radius
- Layout: Grid with name (bold), preview (small), Load button (right), menu button (far right)

**Keywords Preview Logic**:
```python
def _format_preview(keywords: list[str]) -> str:
    if len(keywords) <= 3:
        return ", ".join(keywords)
    else:
        first_three = ", ".join(keywords[:3])
        remaining = len(keywords) - 3
        return f"{first_three}, +{remaining} more"
```

**Rationale**:
- Matches existing chip/card pattern in active keywords display
- Preview prevents horizontal overflow while showing useful context
- Load button provides one-click access (primary action)
- Menu button (⋮) for secondary actions (Edit/Delete) reduces clutter

**Code Reference**: `src/ui/keyword_panel.py:444-491` (chip creation as template)

---

## Decision 4: Persistence & Migration

**Decision**: ConfigurationManager handles preset field migration with empty list default

**Migration Logic**:
```python
# In ConfigurationManager.load()
keyword_presets = data.get('keyword_presets', [])  # Default to empty list
# Validate each preset dict has required keys
valid_presets = [
    p for p in keyword_presets
    if isinstance(p, dict) and 'name' in p and 'keywords' in p
]
```

**Rationale**:
- Existing configs lack `keyword_presets` field → graceful degradation required
- Empty list default aligns with constitution (partial results > failure)
- Validation filters corrupted presets while loading valid ones
- No breaking changes to existing config.json files

**Alternatives Considered**:
1. **Require config schema version bump** - Rejected: Breaks existing installations
2. **Separate presets.json file** - Rejected: Splits configuration, complicates persistence
3. **Prompt user to initialize presets** - Rejected: Adds friction, violates simplicity principle

**Code Reference**: `src/services/configuration_manager.py:74-84` (existing field loading pattern)

---

## Decision 5: Validation Rules

**Decision**: Preset name validation reuses existing keyword validation logic + adds uniqueness check

**Validation Rules**:
- **Max length**: 50 characters (preset names) vs 100 (keywords)
- **Character set**: Alphanumeric + spaces only (regex: `^[a-zA-Z0-9 ]+$`)
- **Uniqueness**: Case-insensitive name comparison across all presets
- **Keywords**: Apply existing keyword validation (max 100 chars, no duplicates)

**Rationale**:
- Shorter name limit prevents UI overflow in preset cards
- Alphanumeric restriction avoids special characters breaking JSON/UI
- Case-insensitive uniqueness matches user expectations ("Medical" == "medical")
- Keyword validation reuse ensures consistency with active keywords

**Code Reference**: `src/ui/keyword_panel.py:350-358` (existing keyword validation)

**Implementation**:
```python
import re

def validate_preset_name(name: str, existing_presets: list[dict]) -> tuple[bool, str]:
    if not name or len(name) > 50:
        return False, "Name must be 1-50 characters"
    if not re.match(r'^[a-zA-Z0-9 ]+$', name):
        return False, "Name can only contain letters, numbers, and spaces"
    existing_names = [p['name'].lower() for p in existing_presets]
    if name.lower() in existing_names:
        return False, "Preset name already exists"
    return True, ""
```

---

## Decision 6: State Persistence (Collapsed/Expanded)

**Decision**: Store presets section collapsed state in Configuration model

**New Configuration Field**:
```python
presets_section_expanded: bool = False  # Default: collapsed
```

**Rationale**:
- Configuration already stores UI state (window_width, window_height)
- Remembering state reduces friction for users who frequently use presets
- Default collapsed state prevents overwhelming new users (per FR-021)
- Persists across sessions via existing config.json save/load

**Code Reference**: `src/models/configuration.py:29-30` (window dimensions as template)

---

## Research Artifacts

### Existing Code Patterns Analyzed:
1. ✅ Configuration model dataclass pattern (`src/models/configuration.py`)
2. ✅ ConfigurationManager JSON persistence (`src/services/configuration_manager.py`)
3. ✅ KeywordPanel grid layout and callbacks (`src/ui/keyword_panel.py`)
4. ✅ AppTheme constants usage (`src/ui/theme.py`)
5. ✅ AppController callback wiring (`src/controllers/app_controller.py`)

### External Resources:
- **None required** - All patterns exist in codebase

### Technical Risks Identified:
1. **Risk**: Preset cards with many keywords may overflow vertically
   - **Mitigation**: Scrollable preset container (max height 200px per FR-016)

2. **Risk**: Load confirmation dialog blocks UI thread
   - **Mitigation**: tkinter messagebox.askyesno is non-blocking modal (acceptable UX)

3. **Risk**: Corrupted preset data crashes application
   - **Mitigation**: Validation in ConfigurationManager.load() filters invalid entries

---

## Conclusion

All design decisions leverage existing infrastructure. No new libraries, frameworks, or architectural patterns required. Implementation proceeds to Phase 1 (contracts and data model).

**Next Phase**: [Phase 1: Design & Contracts](./data-model.md)
