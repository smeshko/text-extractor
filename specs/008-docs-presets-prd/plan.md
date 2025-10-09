# Implementation Plan: Keyword Presets Management

**Branch**: `008-docs-presets-prd` | **Date**: 2025-10-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/A1E6E98/Developer/kris-extractor/specs/008-docs-presets-prd/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → ✅ Loaded successfully
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → ✅ No NEEDS CLARIFICATION found
   → Project Type: Single Python desktop application
   → Structure Decision: Single project with src/ structure
3. Fill the Constitution Check section based on the content of the constitution document.
   → ✅ Constitution Check sections completed
4. Evaluate Constitution Check section below
   → ✅ No violations - feature extends existing persistence pattern
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → ✅ Completed - best practices for tkinter UI patterns and JSON persistence
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, CLAUDE.md
   → ✅ Completed - data model, UI contracts, validation checklist
7. Re-evaluate Constitution Check section
   → ✅ No new violations introduced
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
   → ✅ Completed - task generation strategy documented
9. STOP - Ready for /tasks command
   → ✅ Plan complete
```

**IMPORTANT**: The /plan command STOPS at step 9. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary

This feature adds a Keyword Presets system allowing users to save and manage collections of keywords for reuse across extraction sessions. Users frequently extract documents with the same keyword sets (e.g., medical reports requiring HTD, RTP, Temperature, Pressure, Volume) and must currently re-add these keywords manually each time. The preset feature eliminates this repetitive data entry by allowing users to:

1. Save current active keywords as a named preset (e.g., "Medical Report")
2. Load saved presets with one click, replacing current active keywords
3. Edit preset names and keyword lists
4. Delete presets with confirmation

The feature extends the existing KeywordPanel UI with a collapsible Presets section positioned above keyword history, and persists preset data in the existing config.json file alongside keyword history. The implementation follows existing patterns: Configuration model for persistence, ConfigurationManager for load/save, and KeywordPanel for UI rendering.

**Technical Approach**: Extend Configuration model with `keyword_presets` field (list of {name, keywords} dictionaries), add preset CRUD methods, update KeywordPanel with collapsible preset cards section, and wire preset actions through AppController to persist changes.

## Technical Context

**Language/Version**: Python 3.10+ (existing pyproject.toml target)
**Primary Dependencies**: tkinter (built-in), existing Configuration/ConfigurationManager infrastructure
**Storage**: JSON file (config.json) - extends existing configuration persistence
**Testing**: Manual validation per constitution (no automated testing required)
**Target Platform**: Windows 10/11 desktop (primary), macOS (development)
**Project Type**: Single desktop application
**Performance Goals**: UI responsiveness <100ms for preset operations, instant load/save
**Constraints**: Single-screen GUI workflow, no external dependencies, PyInstaller --onefile compatibility
**Scale/Scope**: Support 50+ presets with 10+ keywords each, graceful handling of corrupted preset data

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### User-First Simplicity
- [x] Single-screen GUI workflow maintained - Presets section integrates into existing KeywordPanel
- [x] No technical knowledge required for operation - Simple buttons: Create, Load, Edit, Delete
- [x] Complex operations hidden behind simple controls - Collapsible panel, clear card-based UI

### Graceful Degradation
- [x] Error handling continues processing on failures - Invalid presets skipped, valid ones loaded
- [x] All errors collected and reported at end - N/A for this feature (preset operations are atomic)
- [x] Partial results prioritized over complete failure - Load valid presets even if some corrupted

### Unicode-First
- [x] Full Cyrillic and Latin character support verified - Preset names and keywords support Unicode
- [x] Mixed script handling implemented - Uses existing keyword validation (already Unicode-compatible)
- [x] Character encoding preserved throughout pipeline - JSON persistence with ensure_ascii=False

### Keyword History Persistence
- [x] Keyword storage mechanism defined - Presets stored in config.json alongside keyword_history
- [x] History persists across sessions - Extends existing Configuration persistence
- [x] Multi-select from history supported - N/A (preset loads entire collection at once)

### Human-Readable Output
- [x] Plain text format with clear labels - N/A (feature affects input, not output)
- [x] Metadata included (filename, timestamp) - N/A (feature affects input, not output)
- [x] Page/line numbers for each extraction - N/A (feature affects input, not output)

### Distribution Requirements
- [x] PyInstaller --onefile configuration - No new dependencies, uses existing config.json persistence
- [x] Windows 10/11 compatibility verified - tkinter and JSON are cross-platform
- [x] No external Python/dependencies required - Zero new dependencies

*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*

**Initial Constitution Check**: ✅ PASS - No violations, follows existing patterns

## Project Structure

### Documentation (this feature)
```
specs/008-docs-presets-prd/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
│   ├── preset-ui.md     # UI component contract
│   └── config-api.md    # Configuration API contract
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
src/
├── models/
│   └── configuration.py          # [MODIFY] Add keyword_presets field + CRUD methods
├── services/
│   └── configuration_manager.py  # [MODIFY] Handle preset data migration
├── controllers/
│   └── app_controller.py         # [MODIFY] Wire preset callbacks to config persistence
└── ui/
    ├── keyword_panel.py          # [MODIFY] Add collapsible Presets section with cards
    └── theme.py                  # [REFERENCE] Use existing AppTheme constants
```

**Structure Decision**: This is a single Python desktop application using src/ structure. The feature modifies existing components rather than adding new top-level directories. All changes integrate into the current architecture: Configuration model for data, ConfigurationManager for persistence, KeywordPanel for UI, and AppController for coordination.

## Phase 0: Outline & Research

**Status**: ✅ COMPLETED

No unknowns requiring research - feature extends existing patterns:
- Configuration persistence already established (keyword_history field)
- KeywordPanel UI patterns already defined (history grid, active chips)
- JSON serialization already configured (ensure_ascii=False for Unicode)

**Research Tasks Completed**:
1. ✅ Analyzed existing Configuration model pattern
2. ✅ Reviewed KeywordPanel layout and event callbacks
3. ✅ Verified tkinter collapsible section patterns (standard Frame + grid)
4. ✅ Confirmed JSON schema extension approach (add field, handle migration)

**Output**: [research.md](./research.md) with design decisions documented

## Phase 1: Design & Contracts

**Status**: ✅ COMPLETED

### Artifacts Generated:
1. **data-model.md** - KeywordPreset entity schema and Configuration model extensions
2. **contracts/preset-ui.md** - KeywordPanel UI component contract (methods, events, states)
3. **contracts/config-api.md** - Configuration CRUD API contract (add/update/delete/get presets)
4. **quickstart.md** - Manual validation checklist for testing preset workflows
5. **CLAUDE.md** - Updated with preset management feature context

### Design Summary:
- **Data Model**: `keyword_presets: list[dict]` in Configuration, each dict = `{name: str, keywords: list[str]}`
- **UI Components**: Collapsible PresetSection within KeywordPanel, PresetCard widgets, dialog windows
- **Validation**: Preset name (max 50 chars, alphanumeric + spaces, unique), keywords (existing validation)
- **Persistence**: ConfigurationManager handles migration (empty list default for missing field)

**Output**: All Phase 1 artifacts in specs/008-docs-presets-prd/

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs in dependency order
- Group by component: Configuration model → ConfigurationManager → KeywordPanel UI → AppController wiring
- Each contract method becomes an implementation task
- UI tasks split by sub-component (header, cards, dialogs)

**Task Breakdown Pattern**:
```
Configuration Model (2 tasks):
  1. Add keyword_presets field and validation
  2. Implement CRUD methods (add/update/delete/get)

ConfigurationManager (1 task):
  3. Handle preset data loading and migration

KeywordPanel UI (5 tasks):
  4. Create collapsible Presets section header
  5. Implement preset card rendering
  6. Add Create/Edit/Delete dialogs
  7. Wire preset callbacks (load/edit/delete)
  8. Handle empty state display

AppController Integration (1 task):
  9. Connect preset callbacks to configuration persistence

Validation (1 task):
  10. Execute manual validation checklist from quickstart.md
```

**Ordering Strategy**:
- **Sequential dependencies**: Model → Manager → UI → Controller → Validation
- **Parallel opportunities**: [P] marks tasks within same layer (e.g., multiple UI tasks)
- **Validation last**: Quickstart checklist executes after all implementation complete

**Estimated Output**: 10-12 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)
**Phase 4**: Implementation (execute tasks.md following constitutional principles)
**Phase 5**: Validation (execute quickstart.md manual validation checklist)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**No violations identified** - Feature follows existing patterns and maintains constitutional principles:
- Extends Configuration model (same pattern as keyword_history)
- Reuses ConfigurationManager persistence (same JSON approach)
- Integrates into KeywordPanel (same UI framework and theme)
- No new dependencies or architectural changes

## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [x] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (none existed)
- [x] Complexity deviations documented (none exist)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
