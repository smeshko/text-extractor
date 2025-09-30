# UI Contract

**Component**: User Interface Components (MainWindow, Controllers)
**Purpose**: Single-screen GUI for file selection, keyword management, and extraction control

## Interface Definition

### MainWindow

```python
class MainWindow:
    """Main application window"""

    def __init__(self, config: Configuration):
        """
        Initialize main window

        Args:
            config: Application configuration
        """
        pass

    def show(self) -> None:
        """Display window and start event loop"""
        pass

    def on_file_selected(self, callback: Callable[[str], None]) -> None:
        """Register file selection callback"""
        pass

    def on_keyword_added(self, callback: Callable[[str], None]) -> None:
        """Register keyword added callback"""
        pass

    def on_extract_clicked(self, callback: Callable[[], None]) -> None:
        """Register extract button callback"""
        pass

    def update_state(self, state: ApplicationState) -> None:
        """Update UI based on application state"""
        pass
```

---

## UI Components

### 1. File Selection Area

**Purpose**: Allow user to select PDF or DOCX file

**Components**:
- Label: "Select Document"
- File path display (read-only text field)
- "Browse" button
- Drag-and-drop zone

**Behaviors**:
- Browse button opens file dialog (PDF and DOCX filter)
- Drag-and-drop accepts single file
- Display filename after selection
- Show file type icon (PDF/DOCX)
- Clear file on "Reset" or new selection

**Events**:
- `on_file_selected(file_path: str)` - User selected file via browse or drag-and-drop

**States**:
- Empty (no file selected): Placeholder text "Drag file here or click Browse"
- Selected: Show filename and file type
- Invalid: Show error message (unsupported type, file not found)

---

### 2. Keyword Management Panel

**Purpose**: Add, select, and manage keywords

**Components**:
- Label: "Keywords"
- Text input field for manual entry
- "Add" button
- Keyword history dropdown/list
- Active keywords display (chips/tags)
- "Clear All" button

**Behaviors**:
- Enter keyword in text field, click Add or press Enter
- Select from history dropdown (multi-select)
- Display active keywords as removable chips
- Click X on chip to remove keyword
- Clear All removes all active keywords
- History populated from config.json

**Events**:
- `on_keyword_added(keyword: str)` - User added keyword manually
- `on_keyword_selected_from_history(keyword: str)` - User selected from history
- `on_keyword_removed(keyword: str)` - User removed active keyword
- `on_keywords_cleared()` - User cleared all keywords

**States**:
- No keywords: "Add" button disabled, Extract button disabled
- Keywords active: Show count "N keywords selected"
- Max keywords (optional limit): Disable add until one removed

**Validation**:
- Keyword length: 1-100 characters
- No duplicate keywords (case-insensitive)
- Sanitize for regex injection

---

### 3. Settings Panel (Collapsible)

**Purpose**: Configure output folder, number format, proximity rule

**Components**:
- Settings button/icon (gear icon)
- Collapsible panel
- Output folder path input + browse button
- Log directory path input + browse button
- Number format dropdown (only "US/UK" option currently)
- Proximity rule dropdown (only "Next Number" option currently)

**Behaviors**:
- Click settings button to expand/collapse panel
- Browse buttons open folder selection dialog
- Changes saved to config.json immediately
- Validate paths are writable before saving

**Events**:
- `on_output_folder_changed(path: str)` - User changed output folder
- `on_log_directory_changed(path: str)` - User changed log directory
- `on_settings_changed(config: Configuration)` - Any setting changed

**States**:
- Collapsed (default): Show only settings icon
- Expanded: Show all settings controls

---

### 4. Extract Button & Progress

**Purpose**: Trigger extraction and show progress

**Components**:
- "Extract" button (primary action)
- Progress bar
- Status message label
- Cancel button (optional, for future)

**Behaviors**:
- Extract button enabled only when file and keywords selected
- Click Extract starts extraction in background thread
- Progress bar shows indeterminate progress during processing
- Status message updates: "Processing...", "Complete", "Error"
- Extract button disabled during processing

**Events**:
- `on_extract_clicked()` - User clicked Extract
- `on_cancel_clicked()` - (Optional) User cancelled extraction

**States**:
- Ready: Extract button enabled, no progress
- Processing: Extract button disabled, progress bar active
- Complete: Show success message, enable "Open Output" action
- Error: Show error message, enable "Try Again"

---

### 5. Results Display

**Purpose**: Show extraction results and provide output access

**Components**:
- Results message label
- "Open Output File" button
- "Open Output Folder" button
- "Open Log File" button
- Error/warning summary (expandable)

**Behaviors**:
- After successful extraction, show success message
- Action buttons open respective files/folders
- Error summary expandable: click to see details
- Warning count shown if present

**Events**:
- `on_open_output_file()` - User clicked Open Output File
- `on_open_output_folder()` - User clicked Open Output Folder
- `on_open_log_file()` - User clicked Open Log File

**States**:
- Hidden (before first extraction)
- Success: Green message, action buttons enabled
- Partial Success: Yellow message, show warnings, action buttons enabled
- Error: Red message, show error details, retry option

---

## Layout Specification

### Window Dimensions
- Minimum: 800x600 pixels
- Default: 800x600 pixels
- Resizable: Yes (maintain minimum)

### Layout Structure
```
+----------------------------------------------------------+
| Document Data Extractor                    [⚙ Settings]  |
+----------------------------------------------------------+
|                                                           |
|  Settings Panel (collapsible)                            |
|  +-----------------------------------------------------+  |
|  | Output Folder: [path]              [Browse]        |  |
|  | Log Directory: [path]              [Browse]        |  |
|  | Number Format: [US/UK ▼]                           |  |
|  | Proximity Rule: [Next Number ▼]                    |  |
|  +-----------------------------------------------------+  |
|                                                           |
|  +-----------------------------------------------------+  |
|  | Select Document                                     |  |
|  | +------------------------------------------------+  |  |
|  | | [📄 file icon] medical_report_2024.pdf         |  |  |
|  | +------------------------------------------------+  |  |
|  | [Browse]  (or drag and drop file here)           |  |
|  +-----------------------------------------------------+  |
|                                                           |
|  +-----------------------------------------------------+  |
|  | Keywords                                            |  |
|  | [enter keyword...] [Add]                           |  |
|  |                                                     |  |
|  | History: ▼ [HTD] [RTP] [BGN]                       |  |
|  |                                                     |  |
|  | Active: [HTD ×] [RTP ×] [BGN ×]      [Clear All]   |  |
|  +-----------------------------------------------------+  |
|                                                           |
|  +-----------------------------------------------------+  |
|  | [    Extract Data    ]                             |  |
|  |                                                     |  |
|  | Progress: [██████░░░░] Processing...               |  |
|  +-----------------------------------------------------+  |
|                                                           |
|  +-----------------------------------------------------+  |
|  | ✓ Extraction complete!                              |  |
|  |   4 keywords extracted, 1 not found                |  |
|  |   ⚠ 1 warning (view details)                       |  |
|  |                                                     |  |
|  | [Open Output File] [Open Output Folder] [Open Log] |  |
|  +-----------------------------------------------------+  |
|                                                           |
+----------------------------------------------------------+
```

---

## State Management

### Application States

```python
class UIState(Enum):
    IDLE = "idle"
    FILE_SELECTED = "file_selected"
    READY = "ready"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
    PARTIAL_SUCCESS = "partial_success"
```

### State Transitions & UI Updates

| From State | To State | Trigger | UI Updates |
|------------|----------|---------|------------|
| IDLE | FILE_SELECTED | File selected | Enable keywords section, show filename |
| FILE_SELECTED | READY | Keyword added | Enable Extract button |
| READY | PROCESSING | Extract clicked | Disable controls, show progress bar |
| PROCESSING | COMPLETE | Extraction success | Show results, enable action buttons |
| PROCESSING | ERROR | Extraction failed | Show error message, enable retry |
| PROCESSING | PARTIAL_SUCCESS | Some extractions failed | Show warnings, enable action buttons |
| Any | IDLE | New file selected | Reset all, clear results |

---

## Threading & UI Updates

### Main Thread (UI)
- All UI rendering and event handling
- NEVER blocks for I/O or processing
- Updates UI via state changes

### Worker Thread
- All document parsing and extraction
- Communicates via thread-safe queue
- Sends progress updates to main thread

### Communication Pattern

```python
# Worker thread sends updates
def worker_thread(file_path, keywords, result_queue):
    try:
        # Processing...
        result_queue.put({'type': 'progress', 'message': 'Parsing document...'})

        # More processing...
        result_queue.put({'type': 'progress', 'message': 'Extracting keywords...'})

        # Complete
        result_queue.put({'type': 'complete', 'results': extraction_results})
    except Exception as e:
        result_queue.put({'type': 'error', 'message': str(e)})

# Main thread checks queue
def check_queue():
    while not result_queue.empty():
        msg = result_queue.get()

        if msg['type'] == 'progress':
            update_progress_message(msg['message'])
        elif msg['type'] == 'complete':
            show_results(msg['results'])
        elif msg['type'] == 'error':
            show_error(msg['message'])

    # Check again in 100ms
    window.after(100, check_queue)
```

---

## Event Callbacks

### Controller Interface

The UI doesn't contain business logic. All user actions trigger callbacks to controller:

```python
class AppController:
    """Application controller coordinating UI and business logic"""

    def on_file_selected(self, file_path: str) -> None:
        """Handle file selection"""
        # Validate file
        # Update state
        # Update UI

    def on_keyword_added(self, keyword: str) -> None:
        """Handle keyword addition"""
        # Validate keyword
        # Add to active keywords
        # Update UI

    def on_extract_clicked(self) -> None:
        """Handle extract button click"""
        # Validate inputs
        # Start worker thread
        # Update UI to processing state

    def on_settings_changed(self, config: Configuration) -> None:
        """Handle settings change"""
        # Validate settings
        # Save config
        # Update state
```

---

## Error Handling & Validation

### User Input Validation

**File selection**:
- File exists: Check before accepting
- Supported type: .pdf or .docx only
- Readable: Check permissions
- Not password-protected: Validate before processing
- Has extractable text: Check for scanned PDFs

**Keyword input**:
- Non-empty: Trim whitespace first
- Length: 1-100 characters
- Valid characters: Alphanumeric + limited punctuation
- No duplicates: Case-insensitive check

**Settings paths**:
- Folder exists: Offer to create if missing
- Writable: Check permissions before saving
- Valid path: No invalid characters

### Error Display

**Inline errors** (next to input):
- Red text below input field
- Icon indicator
- Clear message

**Modal dialogs** (critical errors):
- Password-protected PDF: "This PDF is password-protected and cannot be processed"
- Scanned PDF: "This PDF appears to be scanned and requires OCR"
- File not found: "The selected file could not be found"

**Result errors** (after extraction):
- Error summary in results panel
- Expandable details
- Suggestions for resolution

---

## Accessibility

**Keyboard Navigation**:
- Tab order: File browse → Keywords → Settings → Extract
- Enter key: Submit keyword, trigger Extract
- Escape key: Collapse settings, clear error

**Screen Reader Support**:
- Labels for all input fields
- Status messages announced
- Progress updates announced
- Error messages announced

**Visual Indicators**:
- Focus indicators on all controls
- Color + text for status (not color alone)
- Sufficient contrast ratios

---

## Platform Considerations

### Windows Specifics
- Native file dialog (Windows Explorer style)
- System folder browser
- Default fonts: Segoe UI
- Window decorations: Standard Windows chrome

### macOS Development
- Test with macOS native dialogs during development
- Ensure cross-platform path handling (os.path)
- Use tkinter's cross-platform abstractions

---

## Testing Checklist

- [ ] File selection via Browse button works
- [ ] Drag-and-drop file selection works
- [ ] Only PDF and DOCX files accepted
- [ ] Keyword entry and Add button work
- [ ] Keywords from history can be selected
- [ ] Active keywords can be removed
- [ ] Extract button disabled until file + keywords ready
- [ ] Extract button triggers processing
- [ ] Progress bar shows during processing
- [ ] UI remains responsive during processing
- [ ] Results displayed after completion
- [ ] Open file/folder buttons work
- [ ] Settings save correctly
- [ ] Settings panel collapse/expand works
- [ ] Keyboard navigation works
- [ ] Tab order is logical
- [ ] Enter key submits forms
- [ ] Window resizing works (maintains minimum)
- [ ] Unicode text displays correctly
- [ ] Error messages display correctly
- [ ] State transitions occur correctly
