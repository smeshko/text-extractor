## TASK-002: Multi-File Selection UI

---
**Status:** COMPLETE
**Branch:** feature/multi-file-table-output
**Type:** IMPLEMENTATION
**Phase:** 1
**Depends On:** TASK-001
---

### Overview

Update the FileSelector component to allow selection of multiple files via browse dialog and drag-and-drop. Update the display to show file count when multiple files are selected.

**Files:**
- `src/ui/file_selector.py` (modify)

### Implementation Steps

**Commit 1: Enable multi-file selection in FileSelector**
- [x] Change `_browse_file()` to use `filedialog.askopenfilenames()` (plural) instead of `askopenfilename()`
- [x] Update `_current_file` to `_current_files: list[str]` to store multiple paths
- [x] Update `_select_file()` to `_select_files(file_paths: list[str])`
- [x] Update `_handle_drop()` to process all dropped files instead of just first
- [x] Update `_update_display()` to show "N files selected" when multiple, or filename when single
- [x] Update callback signature: `_file_selected_callback(file_paths: list[str])`
- [x] Update `get_file()` to `get_files() -> list[str]`
- [x] Add backward-compatible `get_file()` returning first file or None

### Code Example

```python
# Current single-file selection
# src/ui/file_selector.py:110-124

def _browse_file(self):
    """Open file dialog for file selection."""
    file_path = filedialog.askopenfilename(
        title="Select Document",
        filetypes=[...]
    )
    if file_path:
        self._select_file(file_path)

# New multi-file selection:
def _browse_files(self):
    """Open file dialog for multi-file selection."""
    file_paths = filedialog.askopenfilenames(
        title="Select Documents",
        filetypes=[
            ("Supported Documents", "*.pdf *.docx *.doc"),
            ("PDF Files", "*.pdf"),
            ("Word Documents (DOCX)", "*.docx"),
            ("Word Documents (DOC)", "*.doc"),
            ("All Files", "*.*")
        ]
    )
    if file_paths:
        self._select_files(list(file_paths))  # tuple to list
```

```python
# Display update for multiple files
def _update_display(self, file_paths: list[str]):
    """Update file display for selected files."""
    if len(file_paths) == 1:
        filename = os.path.basename(file_paths[0])
        self.path_label.configure(text=filename, ...)
    else:
        self.path_label.configure(
            text=f"{len(file_paths)} files selected",
            foreground=AppTheme.COLORS['text']
        )
```

### Success Criteria

- [ ] Build succeeds with no errors
- [ ] Browse dialog allows selecting multiple files (Ctrl/Cmd+click)
- [ ] Drag-and-drop accepts multiple files
- [ ] Display shows "N files selected" for multiple files
- [ ] Display shows filename for single file
- [ ] Callback receives list of file paths

### Verification

```bash
cd src && python -c "from ui.file_selector import FileSelector; print('OK')"
# Manual: Run app, select multiple files, verify display
```

### Notes

- `askopenfilenames()` returns a tuple, convert to list
- Keep backward compatibility for single-file workflows
- Icon can stay as document icon regardless of count
