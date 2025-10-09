# Data Model: Keyword Presets

**Feature**: Keyword Presets Management
**Date**: 2025-10-09
**Status**: ✅ COMPLETED

---

## Entity: KeywordPreset

**Logical Representation**: A named collection of keywords saved for reuse

### Attributes

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| `name` | string | Max 50 chars, alphanumeric + spaces, unique (case-insensitive) | User-defined preset identifier |
| `keywords` | list[string] | Each keyword max 100 chars, no duplicates | Ordered list of keywords |

### Physical Storage

**Format**: JSON dictionary within Configuration model
```json
{
  "name": "Medical Report",
  "keywords": ["HTD", "RTP", "Temperature", "Pressure", "Volume"]
}
```

**Container**: `Configuration.keyword_presets: list[dict]`

### Validation Rules

1. **Name Validation**:
   - Length: 1-50 characters
   - Pattern: `^[a-zA-Z0-9 ]+$` (alphanumeric + spaces only)
   - Uniqueness: Case-insensitive comparison against existing preset names
   - Example valid names: "Medical Report", "Quality Check 2024", "Test Data"
   - Example invalid names: "Report@123" (special char), "A"*51 (too long), "" (empty)

2. **Keywords Validation**:
   - Each keyword: 1-100 characters (reuses existing keyword validation)
   - No duplicate keywords within preset (case-insensitive)
   - Preserves insertion order (critical for user workflow)

3. **Collection Validation**:
   - Preset names must be unique across all presets
   - No limit on number of presets (performance tested up to 100)
   - Empty keyword list allowed (edge case: user creates preset then removes all keywords)

### State Transitions

```
[Not Exists] --create--> [Saved]
[Saved] --load--> [Active in KeywordPanel]
[Saved] --edit--> [Modified] --save--> [Saved]
[Saved] --delete--> [Not Exists]
```

### Relationships

- **Independent of**: `Configuration.keyword_history` (separate collections)
- **Loaded into**: KeywordPanel active keywords (transient UI state)
- **Persisted by**: ConfigurationManager (JSON serialization)

---

## Model: Configuration (Extended)

**File**: `src/models/configuration.py`

### New Fields

```python
@dataclass
class Configuration:
    # Existing fields...
    keyword_history: list[str] = field(default_factory=list)

    # NEW FIELDS:
    keyword_presets: list[dict] = field(default_factory=list)
    presets_section_expanded: bool = False
```

### Field Specifications

#### `keyword_presets`

- **Type**: `list[dict]`
- **Default**: Empty list
- **Structure**: Each dict must contain `{"name": str, "keywords": list[str]}`
- **Validation**: Performed in `__post_init__` and CRUD methods
- **Max Size**: No hard limit (graceful degradation for large datasets)

#### `presets_section_expanded`

- **Type**: `bool`
- **Default**: `False` (collapsed by default per FR-021)
- **Purpose**: Remember user's collapsed/expanded preference
- **Persistence**: Saved to config.json, loaded on application start

### New Methods

#### Preset CRUD Operations

```python
def add_preset(self, name: str, keywords: list[str]) -> tuple[bool, str]:
    """Add new preset.

    Args:
        name: Preset name (validated)
        keywords: List of keywords (validated)

    Returns:
        (success: bool, error_message: str)
    """
    pass

def update_preset(self, old_name: str, new_name: str, keywords: list[str]) -> tuple[bool, str]:
    """Update existing preset.

    Args:
        old_name: Current preset name
        new_name: New preset name (can be same as old_name)
        keywords: Updated keyword list

    Returns:
        (success: bool, error_message: str)
    """
    pass

def delete_preset(self, name: str) -> bool:
    """Delete preset by name.

    Args:
        name: Preset name (case-insensitive)

    Returns:
        True if deleted, False if not found
    """
    pass

def get_preset_by_name(self, name: str) -> dict | None:
    """Retrieve preset by name.

    Args:
        name: Preset name (case-insensitive)

    Returns:
        Preset dict or None if not found
    """
    pass

def get_all_presets(self) -> list[dict]:
    """Get all presets (ordered by insertion).

    Returns:
        Copy of keyword_presets list
    """
    pass
```

### Validation Logic

**Added to `__post_init__`**:
```python
# Validate keyword_presets structure
for preset in self.keyword_presets:
    if not isinstance(preset, dict):
        raise ValueError("Invalid preset: must be dict")
    if 'name' not in preset or 'keywords' not in preset:
        raise ValueError("Preset missing required fields: name, keywords")
    if not isinstance(preset['keywords'], list):
        raise ValueError("Preset keywords must be list")

    # Validate preset name
    name = preset['name']
    if not name or len(name) > 50:
        raise ValueError(f"Preset name must be 1-50 chars: {name}")
    if not re.match(r'^[a-zA-Z0-9 ]+$', name):
        raise ValueError(f"Invalid characters in preset name: {name}")

    # Validate keywords
    for kw in preset['keywords']:
        if not kw or len(kw) > 100:
            raise ValueError(f"Invalid keyword in preset '{name}': {kw}")

# Check for duplicate preset names (case-insensitive)
names_lower = [p['name'].lower() for p in self.keyword_presets]
if len(names_lower) != len(set(names_lower)):
    raise ValueError("Duplicate preset names found")
```

---

## Model: ConfigurationManager (Extended)

**File**: `src/services/configuration_manager.py`

### Migration Logic

**Added to `load()` method**:
```python
# Load presets with migration support
keyword_presets = data.get('keyword_presets', [])

# Validate and filter corrupted presets
valid_presets = []
for preset in keyword_presets:
    if (isinstance(preset, dict) and
        'name' in preset and
        'keywords' in preset and
        isinstance(preset['keywords'], list)):
        valid_presets.append(preset)
    else:
        print(f"Skipping corrupted preset: {preset}")

config.keyword_presets = valid_presets

# Load UI state
config.presets_section_expanded = data.get('presets_section_expanded', False)
```

### Persistence Logic

**Added to `save()` method**:
```python
data = {
    # Existing fields...
    'keyword_history': config.keyword_history,

    # NEW FIELDS:
    'keyword_presets': config.keyword_presets,
    'presets_section_expanded': config.presets_section_expanded,

    'last_updated': config.last_updated
}
```

---

## Data Flow

### Create Preset Flow
```
User clicks "Create New Preset"
  → KeywordPanel shows dialog with current active keywords
  → User enters name "Medical Report"
  → KeywordPanel validates name
  → Calls Configuration.add_preset("Medical Report", ["HTD", "RTP", ...])
  → Configuration validates, appends to keyword_presets
  → AppController calls ConfigurationManager.save(config)
  → JSON written to config.json
  → KeywordPanel refreshes preset cards
```

### Load Preset Flow
```
User clicks [Load] on "Medical Report" card
  → KeywordPanel shows confirmation dialog (if active keywords exist)
  → User confirms
  → KeywordPanel calls Configuration.get_preset_by_name("Medical Report")
  → Returns {"name": "Medical Report", "keywords": ["HTD", "RTP", ...]}
  → KeywordPanel.set_active_keywords(["HTD", "RTP", ...])
  → UI updates: active chips rendered, history refreshed
```

### Edit Preset Flow
```
User clicks [...] menu → Edit
  → KeywordPanel shows edit dialog with current name and keywords
  → User modifies to "Medical Report 2024", adds "Humidity"
  → KeywordPanel validates new name
  → Calls Configuration.update_preset("Medical Report", "Medical Report 2024", [...])
  → Configuration updates preset in-place
  → AppController calls ConfigurationManager.save(config)
  → KeywordPanel refreshes preset cards
```

### Delete Preset Flow
```
User clicks [...] menu → Delete
  → KeywordPanel shows confirmation: "Delete preset 'Medical Report'?"
  → User confirms
  → Calls Configuration.delete_preset("Medical Report")
  → Configuration removes preset from list
  → AppController calls ConfigurationManager.save(config)
  → KeywordPanel refreshes preset cards (removed card disappears)
```

---

## Performance Considerations

### Expected Scale
- **Presets**: 10-50 typical, 100 maximum tested
- **Keywords per preset**: 5-10 typical, 20 maximum
- **Load time**: <50ms for 100 presets (JSON parsing)
- **Save time**: <100ms (atomic write)

### Optimizations
- **In-memory cache**: Configuration object held by AppController (no repeated disk reads)
- **Lazy rendering**: KeywordPanel renders only visible preset cards (scrollable area)
- **Debounced saves**: ConfigurationManager already uses atomic writes (no additional debouncing needed)

---

## Error Handling

### Graceful Degradation (Constitution Principle II)

1. **Corrupted preset data**: Skip invalid presets, load valid ones
2. **Missing preset field**: Default to empty list, continue loading
3. **Duplicate names**: Validation prevents creation, but load() filters duplicates if manually edited
4. **Invalid keywords**: Filtered during load, warning logged

### User-Facing Errors

| Error | User Message | Recovery |
|-------|-------------|----------|
| Preset name too long | "Name must be 1-50 characters" | User shortens name |
| Preset name has special chars | "Name can only contain letters, numbers, and spaces" | User removes special chars |
| Preset name already exists | "Preset name already exists" | User chooses different name |
| No active keywords | [Create button disabled] | User adds keywords first |

---

## Summary

**Data Model Additions**:
- `KeywordPreset` entity (logical, stored as dict)
- `Configuration.keyword_presets` field (list[dict])
- `Configuration.presets_section_expanded` field (bool)
- Configuration CRUD methods (add/update/delete/get)
- ConfigurationManager migration logic

**Next Phase**: [Contracts](./contracts/) - Define UI component and Configuration API contracts
