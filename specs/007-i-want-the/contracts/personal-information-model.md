# Contract: PersonalInformation Model

**Module**: `src/models/personal_information.py`
**Version**: 2.0
**Feature**: Output Format and UI Enhancements

## Purpose

Defines the data structure for personal information extracted from documents, including name parts, age, ID number, and derived properties for abbreviated names and full names.

## Public Interface

### Data Class

```python
@dataclass
class PersonalInformation:
    """Structured identity data extracted from document."""

    first_name: str | None
    last_name: str | None
    middle_name: str | None          # NEW in v2.0
    id_number_prefix: str | None
    age: int | None                  # NEW in v2.0
    character_set: str
    extraction_page: int | None
    is_complete: bool
```

### Properties

#### `full_name: str | None` (NEW in v2.0)

**Type**: Read-only property

**Returns**:
- Full name string combining all name parts (first, middle, last) separated by spaces
- `None` if all name parts are None

**Examples**:
```python
# Two-part name
PersonalInformation(first_name="Иван", last_name="Петров", middle_name=None, ...)
    .full_name → "Иван Петров"

# Three-part name
PersonalInformation(first_name="Иван", middle_name="Йорданов", last_name="Тодоров", ...)
    .full_name → "Иван Йорданов Тодоров"

# Single name
PersonalInformation(first_name="Иван", last_name=None, middle_name=None, ...)
    .full_name → "Иван"

# No name
PersonalInformation(first_name=None, last_name=None, middle_name=None, ...)
    .full_name → None
```

**Guarantees**:
- Non-None name parts are always included
- Order: first_name, middle_name, last_name
- No leading/trailing whitespace
- Single space separator between parts

### Methods

#### `get_abbreviated_name() -> str | None` (NEW in v2.0)

**Purpose**: Generate abbreviated name from first letters of all name parts

**Returns**:
- Uppercase string with first letter of each name part
- `None` if `full_name` is None

**Examples**:
```python
# Cyrillic three-part name
PersonalInformation(..., full_name="Иван Йорданов Тодоров")
    .get_abbreviated_name() → "ИЙТ"

# Latin two-part name
PersonalInformation(..., full_name="John Doe")
    .get_abbreviated_name() → "JD"

# Mixed scripts
PersonalInformation(..., full_name="John Иванов")
    .get_abbreviated_name() → "JI"

# Single name
PersonalInformation(..., full_name="Иван")
    .get_abbreviated_name() → "И"

# No name
PersonalInformation(..., full_name=None)
    .get_abbreviated_name() → None
```

**Guarantees**:
- Always uppercase output
- Cyrillic characters preserved (е → Е, и → И)
- Latin characters uppercased (a → A, z → Z)
- Empty name parts filtered out
- No whitespace in output

#### `empty() -> PersonalInformation` (classmethod, existing)

**Purpose**: Create empty instance with all fields as None

**Returns**: PersonalInformation with `is_complete=False`

**Signature**: No changes from v1.0

## Field Contracts

### `first_name: str | None`
- **Type**: String or None
- **Constraints**: Any Unicode string
- **Example**: "Иван", "John", None

### `last_name: str | None`
- **Type**: String or None
- **Constraints**: Any Unicode string
- **Example**: "Петров", "Doe", None

### `middle_name: str | None` (NEW)
- **Type**: String or None
- **Constraints**: Any Unicode string, can contain multiple middle names
- **Example**: "Йорданов", "Michael James", None

### `age: int | None` (NEW)
- **Type**: Integer or None
- **Constraints**: If not None, must be 0 ≤ age ≤ 150
- **Validation**: Enforced in `__post_init__`
- **Example**: 33, 25, 120, None
- **Extraction Source**: Text appearing after person's name, separated by comma

### `id_number_prefix: str | None`
- **Type**: String or None
- **Constraints**: If not None, exactly 4 digits
- **Validation**: Enforced in `__post_init__`
- **Example**: "1234", None

### `character_set: str`
- **Type**: String (required)
- **Constraints**: Must be one of: 'cyrillic', 'latin', 'mixed', 'unknown'
- **Validation**: Enforced in `__post_init__`
- **Example**: "cyrillic", "mixed"

### `extraction_page: int | None`
- **Type**: Integer or None
- **Constraints**: If not None, must be ≥ 1
- **Validation**: Enforced in `__post_init__`
- **Example**: 1, 5, None

### `is_complete: bool`
- **Type**: Boolean (required)
- **Computation**: Auto-updated in `__post_init__` based on:
  - v1.0: `first_name`, `last_name`, `id_number_prefix` all non-None
  - v2.0 (optional): Include `age` in completeness check
- **Example**: True, False

## Validation Rules

All validation occurs in `__post_init__`:

1. **character_set**: Must be in valid set, raises ValueError otherwise
2. **extraction_page**: If not None, must be ≥ 1, raises ValueError otherwise
3. **id_number_prefix**: If not None, must be exactly 4 digits, raises ValueError otherwise
4. **age**: If not None, must be 0 ≤ age ≤ 150, raises ValueError otherwise (NEW)
5. **is_complete**: Auto-computed from field values

## Error Handling

**Validation Failures**:
```python
# Invalid age
PersonalInformation(..., age=200)
    → ValueError: "Age must be between 0 and 150, got: 200"

PersonalInformation(..., age=-5)
    → ValueError: "Age must be between 0 and 150, got: -5"

# Invalid character_set
PersonalInformation(..., character_set='invalid')
    → ValueError: "Invalid character_set: invalid. Must be one of ..."
```

## Usage Examples

### Creating Instance
```python
# Complete personal info with age
person = PersonalInformation(
    first_name="Иван",
    middle_name="Йорданов",
    last_name="Тодоров",
    age=33,
    id_number_prefix="1234",
    character_set="cyrillic",
    extraction_page=1,
    is_complete=True  # Will be auto-updated
)

# Access new properties
assert person.full_name == "Иван Йорданов Тодоров"
assert person.get_abbreviated_name() == "ИЙТ"
```

### Graceful Degradation
```python
# Missing age - still valid
person = PersonalInformation(
    first_name="Иван",
    last_name="Петров",
    middle_name=None,
    age=None,  # Missing
    id_number_prefix="5678",
    character_set="cyrillic",
    extraction_page=2,
    is_complete=False
)

# Properties handle None gracefully
assert person.full_name == "Иван Петров"
assert person.get_abbreviated_name() == "ИП"
```

## Backward Compatibility

**Breaking Changes**: None for existing fields

**New Fields**:
- `middle_name`: Defaults to None, optional
- `age`: Defaults to None, optional

**Existing Code Impact**:
- Code accessing `first_name`, `last_name`, `id_number_prefix` unchanged
- Code creating instances must provide `middle_name=None, age=None` or use keyword args

**Migration**:
```python
# Old code (v1.0)
PersonalInformation(
    first_name="Иван",
    last_name="Петров",
    id_number_prefix="1234",
    character_set="cyrillic",
    extraction_page=1,
    is_complete=True
)

# New code (v2.0) - add new fields
PersonalInformation(
    first_name="Иван",
    last_name="Петров",
    middle_name=None,  # NEW
    id_number_prefix="1234",
    age=None,  # NEW
    character_set="cyrillic",
    extraction_page=1,
    is_complete=True
)
```

## Dependencies

**Imports**:
- `dataclasses.dataclass` (stdlib)

**No External Dependencies**: Constitution-compliant
