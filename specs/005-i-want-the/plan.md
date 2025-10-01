
# Implementation Plan: Grid-Based Keyword History Display

**Branch**: `005-i-want-the` | **Date**: October 1, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/A1E6E98/Developer/kris-extractor/specs/005-i-want-the/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Replace the space-inefficient list-based keyword history display with a responsive grid layout that flows and wraps based on available width. Single-click on grid items immediately adds keywords to the active list, eliminating the selection state and "Add Selected from History" button. This change improves space efficiency (2x more keywords visible) while simplifying the user workflow.

## Technical Context
**Language/Version**: Python 3.10+ (pyproject.toml targets py310)  
**Primary Dependencies**: tkinter (GUI framework), tkinterdnd2 (drag-and-drop), PyMuPDF/python-docx (document parsing)  
**Storage**: JSON file for keyword history persistence (KeywordHistory model)  
**Testing**: None (per Constitution Section "Testing Policy" - manual validation only)  
**Target Platform**: Windows 10/11 desktop (packaged as single .exe via PyInstaller)
**Project Type**: Single project (desktop GUI application)  
**Performance Goals**: Smooth grid rendering up to 1000 historical keywords without lag  
**Constraints**: Must maintain single-screen workflow, no horizontal scrolling, minimum touch target size for grid items  
**Scale/Scope**: 2 users, ~10-50 keywords typical, grid layout affects keyword_panel.py only (lines 72-117)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### User-First Simplicity
- [x] Single-screen GUI workflow maintained (grid replaces list in same keyword panel location)
- [x] No technical knowledge required for operation (single-click adds keyword - simpler than select-then-add)
- [x] Complex operations hidden behind simple controls (grid layout complexity hidden behind click interaction)

### Graceful Degradation
- [x] Error handling continues processing on failures (N/A for UI layout change - no error conditions)
- [x] All errors collected and reported at end (N/A for UI layout change)
- [x] Partial results prioritized over complete failure (N/A for UI layout change)

### Unicode-First
- [x] Full Cyrillic and Latin character support verified (inherits from existing KeywordHistory model - no encoding changes)
- [x] Mixed script handling implemented (tkinter Label widgets already support Unicode)
- [x] Character encoding preserved throughout pipeline (no text processing changes)

### Keyword History Persistence
- [x] Keyword storage mechanism defined (uses existing KeywordHistory model - no changes to persistence)
- [x] History persists across sessions (existing mechanism unchanged)
- [x] Multi-select from history supported (single-click immediate add replaces multi-select - simplified UX per spec)

### Human-Readable Output
- [x] Plain text format with clear labels (N/A - feature affects input UI only, not output generation)
- [x] Metadata included (filename, timestamp) (N/A - no output changes)
- [x] Page/line numbers for each extraction (N/A - no output changes)

### Distribution Requirements
- [x] PyInstaller --onefile configuration (no new dependencies - uses standard tkinter)
- [x] Windows 10/11 compatibility verified (tkinter Frame/Label widgets are cross-platform standard)
- [x] No external Python/dependencies required (no new dependencies added)

**Status**: PASS - All constitutional requirements satisfied or not applicable. Feature simplifies existing workflow without introducing complexity.

*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*

## Project Structure

### Documentation (this feature)
```
specs/[###-feature]/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/
│   ├── keyword_history.py      # KeywordHistory model (persistence layer)
│   └── keyword.py              # Keyword model
├── ui/
│   ├── keyword_panel.py        # [MODIFIED] Grid layout replaces listbox (lines 72-117)
│   └── theme.py                # Theme constants for grid styling
├── controllers/
│   └── app_controller.py       # Orchestrates keyword panel callbacks
└── main.py                     # Application entry point
```

**Structure Decision**: Single project (desktop GUI application). This feature modifies only the UI layer (`keyword_panel.py`) to replace the listbox-based history display with a responsive grid layout. No changes to models, controllers, or business logic - purely a presentation layer enhancement.

## Phase 0: Outline & Research

**Status**: ✅ COMPLETE

**Approach**:
1. Analyzed current listbox implementation (lines 72-117 in keyword_panel.py)
2. Researched tkinter layout approaches for flow/wrap behavior
3. Evaluated widget options (Canvas vs Grid vs Pack managers)
4. Documented technical decisions for grid implementation

**Output**: ✅ `research.md` created with 7 key decisions documented:
- Canvas + Frame with flow/wrap logic (Decision 1)
- Label widget styling approach (Decision 2)
- Horizontal accumulation wrapping algorithm (Decision 3)
- Single-click event handling (Decision 4)
- Resize debouncing for performance (Decision 5)
- Dynamic height with 200px maximum (Decision 6)
- Integration scope limited to keyword_panel.py (Decision 7)

**Key Finding**: No new dependencies required - pure tkinter implementation compatible with PyInstaller single-executable packaging.

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETE

**Prerequisites**: ✅ research.md complete

**Approach**:
1. Analyzed existing data models (no changes needed - UI-only feature)
2. Extracted UI component interface from research decisions
3. Generated validation scenarios from acceptance criteria
4. Updated agent context file with feature information

**Output**: ✅ All Phase 1 artifacts created:
- ✅ `data-model.md`: Documented GridLayoutState and data flow (zero model changes)
- ✅ `contracts/ui-contract.md`: Complete component interface with 6 public methods, visual specs, interaction contracts, and performance requirements
- ✅ `quickstart.md`: 13 manual validation test cases covering core functionality, edge cases, Unicode, and performance
- ✅ `CLAUDE.md`: Updated with current feature context via update-agent-context.sh script

**Key Insight**: This is a presentation-layer refactoring with zero data model changes. All complexity is in UI layout calculations and event handling.

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **Load base template**: `.specify/templates/tasks-template.md`

2. **Generate implementation tasks from contracts**:
   - From `contracts/ui-contract.md`:
     * Task: Create grid layout structure (`_create_grid_layout`)
     * Task: Implement flow/wrap layout algorithm (`_calculate_grid_positions`)
     * Task: Add grid item creation with styling (`_populate_history`)
     * Task: Implement single-click handler (`_on_grid_item_click`)
     * Task: Add resize debouncing (`_on_resize_grid`)
     * Task: Implement grid item removal (`_remove_from_history_display`)

3. **Generate refactoring tasks**:
   - Task: Remove listbox implementation (lines 89-103)
   - Task: Remove "Add Selected from History" button (lines 112-117)
   - Task: Update history section conditional logic

4. **Generate validation tasks from quickstart**:
   - Task: Manual validation - Test Cases 1-5 (core functionality)
   - Task: Manual validation - Test Cases 6-8 (interaction)
   - Task: Manual validation - Test Cases 9-11 (Unicode, filtering)
   - Task: Manual validation - Test Cases 12-13 (space efficiency, performance)

**Ordering Strategy**:

**Phase 2A: Preparation (Sequential)**
1. Backup current implementation
2. Remove old listbox code (lines 89-117)
3. Update conditional structure for history section

**Phase 2B: Core Implementation (Sequential - dependent steps)**
4. Create grid layout structure (Canvas + Frame + Scrollbar)
5. Implement flow/wrap positioning algorithm
6. Add grid item creation with hover states
7. Bind single-click event handler
8. Add resize debouncing

**Phase 2C: Integration (Sequential)**
9. Wire up callbacks to controller
10. Test with sample history data (5 keywords)
11. Fix any layout calculation issues

**Phase 2D: Validation (Can be parallelized)**
12. [P] Run Test Cases 1-5 (core functionality)
13. [P] Run Test Cases 6-8 (interaction)
14. [P] Run Test Cases 9-11 (Unicode, filtering)
15. [P] Run Test Cases 12-13 (space efficiency, performance)

**Parallelization Notes**:
- Implementation tasks are sequential (single file modification)
- Validation tasks can be parallelized (independent test scenarios)
- Use [P] marker for validation tasks only

**Estimated Output**: 15 tasks in tasks.md

**Dependencies**:
- No model changes (existing KeywordHistory model unchanged)
- No controller changes (existing callbacks compatible)
- No service changes (UI-only feature)
- Single file scope: `src/ui/keyword_panel.py`

**Risk Mitigation**:
- Keep backup of original listbox implementation
- Test incrementally after each core task
- Validate Unicode early (Test Case 9) before extensive testing

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**Status**: No violations detected ✅

This feature fully complies with all constitutional principles:
- User-First Simplicity: Simplifies workflow (single-click vs select-then-add)
- Graceful Degradation: N/A (UI-only change)
- Unicode-First: Inherits existing Unicode support
- Keyword History Persistence: No changes to persistence mechanism
- Human-Readable Output: N/A (affects input UI only)
- Distribution Requirements: No new dependencies (pure tkinter)


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) ✅
- [x] Phase 1: Design complete (/plan command) ✅
- [x] Phase 2: Task planning complete (/plan command - describe approach only) ✅
- [ ] Phase 3: Tasks generated (/tasks command) - READY
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅ (no violations)
- [x] Post-Design Constitution Check: PASS ✅ (no new violations)
- [x] All NEEDS CLARIFICATION resolved ✅ (Technical Context fully specified)
- [x] Complexity deviations documented ✅ (none - no violations)

**Artifacts Generated**:
- [x] research.md (7 technical decisions documented)
- [x] data-model.md (zero model changes - UI-only feature)
- [x] contracts/ui-contract.md (complete component interface)
- [x] quickstart.md (13 validation test cases)
- [x] CLAUDE.md updated (feature context added)
- [x] plan.md (this file - execution complete)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
