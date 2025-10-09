# Configuration API Contract

**Component**: Configuration Model
**File**: `src/models/configuration.py`
**Purpose**: Provide CRUD operations for keyword presets

---

## API Methods

### `add_preset(name: str, keywords: list[str]) -> tuple[bool, str]`

**Purpose**: Create new preset from active keywords

**Preconditions**:
- `name` is non-empty string
- `keywords` is non-empty list

**Parameters**:
- `name` (str): Preset name to create
- `keywords` (list[str]): Keywords to save

**Returns**:
- `(True, "")` on success
- `(False, error_message)` on validation failure

**Validation**:
1. Check name length (1-50 chars)
2. Check name pattern (alphanumeric + spaces only)
3. Check name uniqueness (case-insensitive)
4. Check each keyword length (1-100 chars)
5. Check no duplicate keywords in list

**Side Effects**:
- Appends `{"name": name, "keywords": keywords}` to `self.keyword_presets`
- Updates `self.last_updated` timestamp

**Error Cases**:
| Error | Return Value |
|-------|--------------|
| Name empty or > 50 chars | `(False, "Name must be 1-50 characters")` |
| Name contains special chars | `(False, "Name can only contain letters, numbers, and spaces")` |
| Name already exists | `(False, "Preset name already exists")` |
| Keyword > 100 chars | `(False, "Invalid keyword: {kw}")` |

**Example**:
```python
config = Configuration.get_default()
success, error = config.add_preset("Medical Report", ["HTD", "RTP", "Temperature"])
if success:
    print("Preset created")
else:
    print(f"Error: {error}")
```

---

### `update_preset(old_name: str, new_name: str, keywords: list[str]) -> tuple[bool, str]`

**Purpose**: Modify existing preset name and/or keywords

**Preconditions**:
- Preset with `old_name` exists

**Parameters**:
- `old_name` (str): Current preset name (case-insensitive match)
- `new_name` (str): New preset name (can be same as old_name)
- `keywords` (list[str]): Updated keyword list

**Returns**:
- `(True, "")` on success
- `(False, error_message)` on failure

**Validation**:
1. Find preset with `old_name` (case-insensitive)
2. If renaming, check `new_name` uniqueness (excluding old preset)
3. Validate `new_name` (length, pattern)
4. Validate `keywords` (length, no duplicates)

**Side Effects**:
- Updates preset dict in-place: `{"name": new_name, "keywords": keywords}`
- Updates `self.last_updated` timestamp

**Error Cases**:
| Error | Return Value |
|-------|--------------|
| Preset not found | `(False, "Preset '{old_name}' not found")` |
| New name invalid | `(False, "Name must be 1-50 characters")` or pattern error |
| New name exists (different preset) | `(False, "Preset name already exists")` |

**Example**:
```python
success, error = config.update_preset(
    "Medical Report",
    "Medical Report 2024",
    ["HTD", "RTP", "Temperature", "Humidity"]
)
```

---

### `delete_preset(name: str) -> bool`

**Purpose**: Remove preset by name

**Preconditions**: None (returns False if not found)

**Parameters**:
- `name` (str): Preset name to delete (case-insensitive)

**Returns**:
- `True` if preset found and deleted
- `False` if preset not found

**Side Effects**:
- Removes preset dict from `self.keyword_presets` list
- Updates `self.last_updated` timestamp

**Example**:
```python
if config.delete_preset("Medical Report"):
    print("Preset deleted")
else:
    print("Preset not found")
```

---

### `get_preset_by_name(name: str) -> dict | None`

**Purpose**: Retrieve preset data by name

**Preconditions**: None

**Parameters**:
- `name` (str): Preset name (case-insensitive)

**Returns**:
- Preset dict `{"name": str, "keywords": list[str]}` if found
- `None` if not found

**Side Effects**: None (read-only)

**Example**:
```python
preset = config.get_preset_by_name("Medical Report")
if preset:
    print(f"Keywords: {preset['keywords']}")
else:
    print("Preset not found")
```

---

### `get_all_presets() -> list[dict]`

**Purpose**: Retrieve all presets ordered by insertion

**Preconditions**: None

**Parameters**: None

**Returns**:
- Copy of `self.keyword_presets` list
- Empty list if no presets

**Side Effects**: None (returns copy, not reference)

**Example**:
```python
all_presets = config.get_all_presets()
for preset in all_presets:
    print(f"{preset['name']}: {len(preset['keywords'])} keywords")
```

---

## Validation Helper

### `_validate_preset_name(name: str, exclude_name: str = None) -> tuple[bool, str]`

**Purpose**: Internal validation for preset names

**Parameters**:
- `name` (str): Name to validate
- `exclude_name` (str, optional): Name to exclude from uniqueness check (for updates)

**Returns**:
- `(True, "")` if valid
- `(False, error_message)` if invalid

**Validation Logic**:
```python
import re

def _validate_preset_name(self, name: str, exclude_name: str = None) -> tuple[bool, str]:
    # Length check
    if not name or len(name) > 50:
        return False, "Name must be 1-50 characters"

    # Pattern check
    if not re.match(r'^[a-zA-Z0-9 ]+$', name):
        return False, "Name can only contain letters, numbers, and spaces"

    # Uniqueness check (case-insensitive)
    existing_names = [
        p['name'].lower() for p in self.keyword_presets
        if exclude_name is None or p['name'].lower() != exclude_name.lower()
    ]
    if name.lower() in existing_names:
        return False, "Preset name already exists"

    return True, ""
```

---

## Configuration Field Contracts

### `keyword_presets: list[dict]`

**Type**: List of dictionaries
**Default**: Empty list (`field(default_factory=list)`)
**Structure**: Each dict must have keys `"name"` and `"keywords"`
**Constraints**:
- All preset names unique (case-insensitive)
- Ordered by insertion (Python list preserves order)

### `presets_section_expanded: bool`

**Type**: Boolean
**Default**: `False` (collapsed by default)
**Purpose**: Remember UI state for presets section
**Persistence**: Saved to config.json

---

## Integration Points

### ConfigurationManager

**Load Logic** (in `load()` method):
```python
keyword_presets = data.get('keyword_presets', [])
valid_presets = [
    p for p in keyword_presets
    if isinstance(p, dict) and 'name' in p and 'keywords' in p
]
config.keyword_presets = valid_presets
config.presets_section_expanded = data.get('presets_section_expanded', False)
```

**Save Logic** (in `save()` method):
```python
data = {
    # ...existing fields...
    'keyword_presets': config.keyword_presets,
    'presets_section_expanded': config.presets_section_expanded,
    'last_updated': config.last_updated
}
```

### AppController

**Callback Wiring**:
```python
def on_preset_created(self, name: str, keywords: list[str]):
    success, error = self.config.add_preset(name, keywords)
    if success:
        self.config_manager.save(self.config)
        self.keyword_panel.refresh_presets(self.config.get_all_presets())
    else:
        self._show_error(error)

def on_preset_loaded(self, preset_name: str):
    preset = self.config.get_preset_by_name(preset_name)
    if preset:
        self.keyword_panel.set_active_keywords(preset['keywords'])

def on_preset_updated(self, old_name: str, new_name: str, keywords: list[str]):
    success, error = self.config.update_preset(old_name, new_name, keywords)
    if success:
        self.config_manager.save(self.config)
        self.keyword_panel.refresh_presets(self.config.get_all_presets())
    else:
        self._show_error(error)

def on_preset_deleted(self, name: str):
    if self.config.delete_preset(name):
        self.config_manager.save(self.config)
        self.keyword_panel.refresh_presets(self.config.get_all_presets())
```

---

## Error Handling Contract

**Principle**: Validation errors return `(False, message)`, never raise exceptions in public API

**Rationale**: Allows UI to display user-friendly error messages without try/catch

**Exception**: `__post_init__` raises `ValueError` for corrupted data (migration handled by ConfigurationManager)

---

## Thread Safety

**Assumption**: Single-threaded GUI application (tkinter main thread)
**No locking required**: All operations synchronous on main thread

---

## Testing Strategy (Manual per Constitution)

**Validation Scenarios**:
1. Create preset with valid name and keywords → Success
2. Create preset with existing name (case-insensitive) → Error
3. Create preset with name > 50 chars → Error
4. Create preset with special characters in name → Error
5. Update preset changing name to existing name → Error
6. Update preset with same name (rename not required) → Success
7. Delete existing preset → Success, preset removed
8. Delete non-existent preset → Returns False
9. Get preset by name (case-insensitive match) → Returns preset or None
10. Get all presets when empty → Returns empty list

**Reference**: [quickstart.md](../quickstart.md) for full test checklist
