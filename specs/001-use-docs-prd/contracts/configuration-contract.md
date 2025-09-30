# Configuration Contract

**Component**: ConfigurationManager
**Purpose**: Persist and manage application settings across sessions

## Interface Definition

### ConfigurationManager

```python
class ConfigurationManager:
    """Manages application configuration persistence"""

    def __init__(self, config_path: str = "config.json"):
        """
        Initialize configuration manager

        Args:
            config_path: Path to config file (default: config.json in app directory)
        """
        pass

    def load(self) -> Configuration:
        """
        Load configuration from file

        Returns:
            Configuration object (uses defaults if file missing/corrupted)

        Raises:
            Never raises - uses defaults on error and logs warning
        """
        pass

    def save(self, config: Configuration) -> bool:
        """
        Save configuration to file

        Args:
            config: Configuration to persist

        Returns:
            True if successful, False otherwise
        """
        pass

    def get_default_config(self) -> Configuration:
        """
        Get default configuration

        Returns:
            Configuration with default values
        """
        pass

    def validate(self, config: Configuration) -> tuple[bool, list[str]]:
        """
        Validate configuration

        Args:
            config: Configuration to validate

        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass
```

---

## Data Structures

### Configuration

```python
@dataclass
class Configuration:
    """Application configuration"""

    # Output settings
    output_folder: str
    log_directory: str

    # Extraction settings
    number_format: str  # 'us_uk' (only supported format)
    proximity_rule: str  # 'next_number' (only supported rule)

    # Keyword history
    keyword_history: list[str]

    # Window settings
    window_width: int
    window_height: int

    # Metadata
    version: str = "1.0.0"
    last_updated: str = ""  # ISO 8601 timestamp
```

---

## Configuration Schema

### JSON Structure

```json
{
  "version": "1.0.0",
  "output_folder": "/Users/username/Documents/ExtractionOutput",
  "log_directory": "/Users/username/Documents/ExtractionOutput/logs",
  "number_format": "us_uk",
  "proximity_rule": "next_number",
  "keyword_history": [
    "HTD",
    "RTP",
    "BGN",
    "Temperature",
    "Pressure"
  ],
  "window_width": 800,
  "window_height": 600,
  "last_updated": "2025-09-30T14:30:22Z"
}
```

---

## Default Values

### Platform-Specific Paths

**Windows**:
```python
default_output_folder = os.path.join(
    os.environ.get('USERPROFILE', 'C:\\'),
    'Documents',
    'DocumentExtractor',
    'Output'
)

default_log_directory = os.path.join(
    os.environ.get('USERPROFILE', 'C:\\'),
    'Documents',
    'DocumentExtractor',
    'Logs'
)
```

**macOS (development)**:
```python
default_output_folder = os.path.join(
    os.path.expanduser('~'),
    'Documents',
    'DocumentExtractor',
    'Output'
)

default_log_directory = os.path.join(
    os.path.expanduser('~'),
    'Documents',
    'DocumentExtractor',
    'Logs'
)
```

### Complete Defaults

```python
DEFAULT_CONFIG = Configuration(
    output_folder=get_platform_default_output_folder(),
    log_directory=get_platform_default_log_directory(),
    number_format='us_uk',
    proximity_rule='next_number',
    keyword_history=[],
    window_width=800,
    window_height=600,
    version='1.0.0',
    last_updated=''
)
```

---

## Validation Rules

### Output Folder
- MUST be absolute path
- MUST exist or be creatable
- MUST be writable
- CAN be created if missing (with user permission)

**Validation**:
```python
def validate_output_folder(path: str) -> tuple[bool, str]:
    if not os.path.isabs(path):
        return False, "Output folder must be an absolute path"

    if not os.path.exists(path):
        try:
            os.makedirs(path, exist_ok=True)
            return True, ""
        except OSError as e:
            return False, f"Cannot create output folder: {e}"

    if not os.access(path, os.W_OK):
        return False, "Output folder is not writable"

    return True, ""
```

### Log Directory
- Same validation as output_folder
- Can be subdirectory of output_folder
- Default: `{output_folder}/logs`

### Number Format
- MUST be "us_uk" (only supported format in v1.0)
- Future: Could support "eu" (comma decimal)

**Validation**:
```python
VALID_NUMBER_FORMATS = ['us_uk']

def validate_number_format(format: str) -> bool:
    return format in VALID_NUMBER_FORMATS
```

### Proximity Rule
- MUST be "next_number" (only supported rule in v1.0)
- Future: Could support "same_line", "same_sentence", "within_n_words"

**Validation**:
```python
VALID_PROXIMITY_RULES = ['next_number']

def validate_proximity_rule(rule: str) -> bool:
    return rule in VALID_PROXIMITY_RULES
```

### Keyword History
- Each keyword: 1-100 characters
- Must be unique (case-insensitive)
- Max size: unlimited (practical limit ~1000)
- Order maintained (most recent last)

**Validation**:
```python
def validate_keyword_history(history: list[str]) -> tuple[bool, str]:
    seen = set()
    for keyword in history:
        if not keyword or len(keyword) > 100:
            return False, f"Invalid keyword length: '{keyword}'"

        keyword_lower = keyword.lower()
        if keyword_lower in seen:
            return False, f"Duplicate keyword: '{keyword}'"
        seen.add(keyword_lower)

    return True, ""
```

### Window Dimensions
- Width: >= 600, <= 3840 (4K max)
- Height: >= 400, <= 2160 (4K max)

**Validation**:
```python
MIN_WIDTH, MAX_WIDTH = 600, 3840
MIN_HEIGHT, MAX_HEIGHT = 400, 2160

def validate_window_size(width: int, height: int) -> tuple[bool, str]:
    if not (MIN_WIDTH <= width <= MAX_WIDTH):
        return False, f"Window width must be between {MIN_WIDTH} and {MAX_WIDTH}"

    if not (MIN_HEIGHT <= height <= MAX_HEIGHT):
        return False, f"Window height must be between {MIN_HEIGHT} and {MAX_HEIGHT}"

    return True, ""
```

### Version
- Semantic versioning format: MAJOR.MINOR.PATCH
- Used for config migration in future versions

---

## Lifecycle & Persistence

### Application Start
```python
1. ConfigurationManager.load()
   → If config.json exists: Parse and validate
   → If missing: Create with defaults
   → If corrupted: Log warning, use defaults, backup corrupted file

2. Validate loaded config
   → If invalid: Use defaults for invalid fields, log warnings

3. Create missing directories
   → output_folder if not exists
   → log_directory if not exists

4. Return Configuration to application
```

### During Runtime
```python
# Setting changed by user
def on_setting_changed(new_config: Configuration):
    # Validate
    is_valid, errors = config_manager.validate(new_config)
    if not is_valid:
        show_error(errors)
        return

    # Save immediately
    if config_manager.save(new_config):
        show_success("Settings saved")
    else:
        show_error("Failed to save settings")
```

### Application Close
```python
1. Save current configuration
   → Update last_updated timestamp
   → Write to config.json

2. If save fails: Log warning
   → Don't block shutdown
   → User's recent changes may be lost
```

---

## Keyword History Management

### Adding Keyword
```python
def add_keyword_to_history(config: Configuration, keyword: str) -> Configuration:
    """
    Add keyword to history (no duplicates, maintain order)

    Args:
        config: Current configuration
        keyword: Keyword to add

    Returns:
        Updated configuration
    """
    # Normalize
    keyword = keyword.strip()
    keyword_lower = keyword.lower()

    # Check for duplicate (case-insensitive)
    existing = [kw for kw in config.keyword_history if kw.lower() == keyword_lower]
    if existing:
        # Already in history, move to end (most recent)
        config.keyword_history.remove(existing[0])

    # Add to end
    config.keyword_history.append(keyword)

    # Optional: Limit size
    MAX_HISTORY_SIZE = 1000
    if len(config.keyword_history) > MAX_HISTORY_SIZE:
        config.keyword_history = config.keyword_history[-MAX_HISTORY_SIZE:]

    return config
```

### Removing Keyword
```python
def remove_keyword_from_history(config: Configuration, keyword: str) -> Configuration:
    """Remove keyword from history (case-insensitive)"""
    keyword_lower = keyword.lower()
    config.keyword_history = [
        kw for kw in config.keyword_history
        if kw.lower() != keyword_lower
    ]
    return config
```

### Clearing History
```python
def clear_keyword_history(config: Configuration) -> Configuration:
    """Clear all keywords from history"""
    config.keyword_history = []
    return config
```

---

## Error Handling

### File Not Found
- Action: Create new config with defaults
- Log: "Config file not found, creating with defaults"
- User Impact: None (seamless)

### Corrupted JSON
- Action: Backup corrupted file, use defaults
- Log: "Config file corrupted, using defaults. Backup: config.json.bak"
- User Impact: Settings reset to defaults

**Backup Strategy**:
```python
def handle_corrupted_config(config_path: str):
    # Rename corrupted file
    backup_path = f"{config_path}.bak"
    os.rename(config_path, backup_path)

    # Create new config with defaults
    return get_default_config()
```

### Invalid Field Values
- Action: Use default for that field, keep valid fields
- Log: "Invalid {field_name}: {value}, using default: {default}"
- User Impact: Partial reset

### Save Failure
- Action: Retry once after 1 second delay
- If still fails: Show error to user, continue running
- User Impact: Recent setting changes lost on next startup

---

## Migration Strategy (Future)

### Version Compatibility
```python
def migrate_config(old_config: dict, old_version: str, new_version: str) -> Configuration:
    """
    Migrate config from old version to new version

    Args:
        old_config: Old configuration dict
        old_version: Old version string
        new_version: New version string

    Returns:
        Migrated Configuration object
    """
    # Example: v1.0.0 → v1.1.0
    if old_version == "1.0.0" and new_version == "1.1.0":
        # Add new fields with defaults
        old_config.setdefault('new_field', default_value)

    # Example: v1.1.0 → v2.0.0
    if old_version.startswith("1.") and new_version.startswith("2."):
        # Breaking changes: Transform old format to new
        old_config = transform_to_v2(old_config)

    return Configuration(**old_config)
```

---

## Contract Guarantees

### Input Contracts

**load()**:
- ACCEPTS: Missing config file (creates with defaults)
- ACCEPTS: Corrupted config file (uses defaults, creates backup)
- REQUIRES: File system access to app directory

**save()**:
- REQUIRES: Valid Configuration object
- REQUIRES: Writable file system

**validate()**:
- ACCEPTS: Any Configuration object
- RETURNS: Never raises exception

---

### Output Contracts

**load()**:
- ENSURES: Always returns valid Configuration
- ENSURES: Never raises exception (uses defaults on error)
- ENSURES: Creates missing directories if paths don't exist

**save()**:
- ENSURES: Returns True if file written successfully
- ENSURES: Returns False on failure (logs error)
- ENSURES: Updates last_updated timestamp
- ENSURES: Atomic write (tmp file + rename)

**validate()**:
- ENSURES: First element is boolean (is_valid)
- ENSURES: If is_valid=False, second element has error messages
- ENSURES: Validates all fields according to rules

---

## Usage Example

```python
# Initialize
config_manager = ConfigurationManager()

# Load at startup
config = config_manager.load()
print(f"Output folder: {config.output_folder}")
print(f"Keyword history: {config.keyword_history}")

# Update setting
config.output_folder = "/new/path"
is_valid, errors = config_manager.validate(config)
if is_valid:
    config_manager.save(config)
else:
    print(f"Invalid config: {errors}")

# Add keyword to history
config = add_keyword_to_history(config, "HTD")
config_manager.save(config)
```

---

## Testing Checklist

- [ ] Load creates new config if missing
- [ ] Load handles corrupted JSON gracefully
- [ ] Load validates all fields
- [ ] Save writes valid JSON
- [ ] Save is atomic (tmp file + rename)
- [ ] Validate catches invalid output folder
- [ ] Validate catches invalid window dimensions
- [ ] Validate catches invalid enum values
- [ ] Keyword history maintains order
- [ ] Keyword history prevents duplicates (case-insensitive)
- [ ] Keyword history limits size
- [ ] Default paths created if missing
- [ ] Windows paths handled correctly
- [ ] macOS paths handled correctly
- [ ] Unicode in paths preserved
- [ ] Backup created on corrupted config
- [ ] Config version tracked correctly
