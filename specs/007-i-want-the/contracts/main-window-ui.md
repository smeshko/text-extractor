# Contract: MainWindow UI Component

**Module**: `src/ui/main_window.py`
**Version**: 2.0
**Feature**: Output Format and UI Enhancements

## Purpose

Main application window providing single-screen GUI for document extraction workflow. Version 2.0 introduces window resizability and reduced initial dimensions.

## Public Interface

### Class: MainWindow

#### Constructor: `__init__(config: Configuration)`

**Parameters**:
- `config: Configuration` - Application configuration

**Behavior** (CHANGED in v2.0):
1. Create tkinter root window (with TkinterDnD if available)
2. Set window title: "Document Data Extractor"
3. Set initial geometry: **1080x900** (v2.0: reduced from 1200x1000)
4. **REMOVED**: `minsize()` constraint (v2.0: window is fully resizable)
5. Configure styles and build UI layout
6. Register close handler for window size persistence

**Window Configuration Changes**:

**v1.0**:
```python
self.root.geometry(f"{config.window_width}x{config.window_height}")
self.root.minsize(1200, 1000)  # Prevents resizing below this
```

**v2.0**:
```python
self.root.geometry("1080x900")  # 10% smaller initial size
# minsize() removed - window is fully resizable
```

**Guarantees**:
- Window opens at 1080x900 pixels (unless config overrides)
- Window is resizable by dragging edges/corners
- UI components remain accessible at default size
- Window size persists across sessions via config

---

#### Method: `show()`

**Purpose**: Display window and start event loop

**Signature**: Unchanged from v1.0

**Behavior**:
- Calls `self.root.mainloop()`
- Blocks until window is closed
- No changes in v2.0

---

#### Method: `update_state(state: ApplicationState)`

**Purpose**: Update UI based on application state

**Signature**: Unchanged from v1.0

**Behavior**:
- Updates file selector, keyword panel, progress bar, results display
- No changes in v2.0

---

#### Window Close Handler: `_on_closing()`

**Purpose**: Handle window close event and persist configuration

**Behavior**:
1. Stop theme monitoring
2. **Capture current window size**: `config.window_width = self.root.winfo_width()`
3. **Capture current window height**: `config.window_height = self.root.winfo_height()`
4. Trigger settings_changed callback to save config
5. Destroy window

**Persistence**:
- User-adjusted window dimensions are saved to config.json
- On next launch, window opens at last saved size (or 1080x900 default)

---

## Window Sizing Behavior

### Initial Size (v2.0)
- **Width**: 1080 pixels (10% reduction from 1200)
- **Height**: 900 pixels (10% reduction from 1000)
- **Calculation**: 1200 × 0.9 = 1080, 1000 × 0.9 = 900

### Resizability (v2.0)
- **Horizontal**: User can drag left/right edges to resize width
- **Vertical**: User can drag top/bottom edges to resize height
- **Corners**: User can drag corners to resize both dimensions
- **Minimum Size**: None enforced (removed minsize constraint)
- **Maximum Size**: Limited by screen resolution

### Size Persistence
- **On Close**: Current window dimensions saved to `config.window_width` and `config.window_height`
- **On Launch**: Window opens at saved dimensions (or 1080x900 if no saved config)
- **Storage**: JSON file (config.json) via ConfigurationManager

---

## UI Layout

**Layout remains unchanged in v2.0** - only initial size and resizability modified

```
┌─────────────────────────────────────────┐
│ Document Data Extractor      [⚙ Settings]│
├─────────────────────────────────────────┤
│ [Settings Panel - Collapsible]          │
├─────────────────────────────────────────┤
│ File Selection Area                     │
├─────────────────────────────────────────┤
│ Keyword Panel (History + Active)        │
├─────────────────────────────────────────┤
│ [Extract Button] [Progress Bar]         │
├─────────────────────────────────────────┤
│ Results Display (Expandable)            │
│                                         │
│                                         │
└─────────────────────────────────────────┘
```

**Grid Weights** (responsive to resizing):
- Main container: `columnconfigure(0, weight=1)`, `rowconfigure(0, weight=1)`
- Results display: `rowconfigure(current_row, weight=1)` - expands vertically

---

## Configuration Integration

### Configuration Fields Used

```python
Configuration:
    window_width: int = 1080   # Default changed in v2.0 (was 1200)
    window_height: int = 900   # Default changed in v2.0 (was 1000)
    output_folder: str
    keyword_history: list[str]
```

**Default Values** (v2.0):
- `window_width`: 1080 (if not in config.json)
- `window_height`: 900 (if not in config.json)

**Persistence Flow**:
1. User resizes window → dimensions change
2. User closes window → `_on_closing()` captures dimensions
3. Dimensions saved to config.json → `{"window_width": 1200, "window_height": 950, ...}`
4. Next launch → reads config.json → opens at 1200x950

---

## Behavior Changes Summary

| Aspect | v1.0 | v2.0 |
|--------|------|------|
| Initial width | 1200px | 1080px (-10%) |
| Initial height | 1000px | 900px (-10%) |
| Minimum size | 1200x1000 (enforced) | None (fully resizable) |
| Resizability | Limited (can't go below minsize) | Full (no constraints) |
| Size persistence | Yes | Yes (unchanged) |

---

## Edge Cases

### Very Small Window Sizes
- **Scenario**: User resizes window to very small dimensions (e.g., 400x300)
- **Behavior**: UI components may overlap or require scrolling
- **Mitigation**: None enforced (per spec FR-011 - resizable without hard limits)
- **Note**: Constitution principle allows graceful degradation

### Very Large Window Sizes
- **Scenario**: User resizes window to very large dimensions (e.g., 3840x2160)
- **Behavior**: UI components expand to fill space (grid weights handle this)
- **Mitigation**: None needed (tkinter grid layout scales appropriately)

### Screen Resolution Smaller Than 1080x900
- **Scenario**: User has screen resolution like 1024x768
- **Behavior**: Window may extend beyond screen bounds initially
- **Mitigation**: User can resize to fit screen, size persists
- **Note**: Typical modern screens are 1920x1080 or higher

---

## Validation Rules

**Window Dimensions**:
- Width and height must be positive integers
- No minimum enforced (user can resize arbitrarily)
- No maximum enforced (limited by OS/screen)

**Configuration Persistence**:
- Dimensions saved only on normal window close (not forced termination)
- Invalid dimensions in config.json → fallback to 1080x900

---

## Error Handling

**TkinterDnD Unavailable**:
```python
try:
    from tkinterdnd2 import TkinterDnD
    self.root = TkinterDnD.Tk()
except (ImportError, Exception):
    self.root = tk.Tk()  # Fallback to regular Tk
```
- No error raised, drag-and-drop disabled gracefully

**Invalid Window Geometry**:
- If config contains invalid dimensions → tkinter uses defaults
- No explicit validation in MainWindow (handled by Configuration)

---

## Performance

**Window Rendering**:
- Initial render: <50ms (typical)
- Resize operation: Real-time (handled by tkinter)
- UI update cycle: <16ms (60 FPS)

**No performance degradation expected from v2.0 changes**

---

## Dependencies

**Standard Library**:
- `tkinter` - GUI framework (built-in)
- `tkinter.ttk` - Themed widgets

**Optional**:
- `tkinterdnd2` - Drag-and-drop support (fallback if unavailable)

**Internal**:
- `models.configuration.Configuration`
- `models.application_state.ApplicationState`
- `ui.theme.AppTheme`
- UI components (FileSelector, KeywordPanel, SettingsPanel, ProgressBar, ResultsDisplay)

**No New Dependencies in v2.0**: Constitution-compliant

---

## Backward Compatibility

**Breaking Changes**: None

**Non-Breaking Changes**:
1. Initial window size reduced from 1200x1000 to 1080x900
   - **Impact**: Users see smaller initial window
   - **Mitigation**: Window is resizable, previous size persists if config exists

2. `minsize()` constraint removed
   - **Impact**: Users can resize window below 1200x1000
   - **Mitigation**: UI layout uses grid weights, degrades gracefully

**Migration**:
- Existing config.json with `window_width=1200, window_height=1000` → opens at saved size
- New installations → opens at 1080x900
- No code changes required for dependent modules

---

## Testing Checklist (Manual Validation)

Per constitution, manual testing required:

1. **Initial Size**:
   - [ ] Window opens at 1080x900 on first launch
   - [ ] All UI components visible and accessible

2. **Resizability**:
   - [ ] Horizontal resize works (drag left/right edges)
   - [ ] Vertical resize works (drag top/bottom edges)
   - [ ] Corner resize works (drag corners)
   - [ ] Can resize below 1080x900
   - [ ] Can resize above 1080x900

3. **Size Persistence**:
   - [ ] Resize window to custom size (e.g., 1300x1100)
   - [ ] Close application
   - [ ] Reopen → window opens at 1300x1100
   - [ ] config.json contains updated dimensions

4. **Edge Cases**:
   - [ ] Very small window (e.g., 500x400) - UI degrades gracefully
   - [ ] Very large window (e.g., 2000x1500) - UI scales appropriately
   - [ ] Screen smaller than 1080x900 - window can be resized to fit

5. **Backward Compatibility**:
   - [ ] Existing config with 1200x1000 → opens at saved size
   - [ ] Drag-and-drop still works (if TkinterDnD available)

---

## Usage Examples

### Creating MainWindow
```python
from ui.main_window import MainWindow
from models.configuration import Configuration

config = Configuration(window_width=1080, window_height=900)
window = MainWindow(config)
window.show()
```

### Size Persistence Flow
```python
# First launch (no config.json)
config = Configuration()  # Defaults: 1080x900
window = MainWindow(config)
window.show()  # Opens at 1080x900

# User resizes to 1400x1200, then closes
# → _on_closing() saves dimensions to config

# Second launch (config.json exists)
config = Configuration()  # Loads: 1400x1200 from file
window = MainWindow(config)
window.show()  # Opens at 1400x1200 (last saved size)
```

---

## Constitutional Compliance

### User-First Simplicity
- ✅ Single-screen workflow maintained
- ✅ Window resizing is standard UI interaction (no technical knowledge)
- ✅ No new controls added

### Graceful Degradation
- ✅ Very small window sizes degrade gracefully (UI may overlap but functional)
- ✅ Missing TkinterDnD → fallback to standard Tk

### Distribution Requirements
- ✅ No new dependencies (tkinter is built-in)
- ✅ PyInstaller --onefile compatibility maintained
