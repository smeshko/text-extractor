
# Implementation Plan: Output Format and UI Enhancements

**Branch**: `007-i-want-the` | **Date**: 2025-10-09 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/Users/A1E6E98/Developer/kris-extractor/specs/007-i-want-the/spec.md`

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
This feature enhances the output formatting and user interface of the document extraction tool. It transforms the output file structure to use table-like formatting for both keyword extractions and personal information sections, adds semicolon separators after numeric values, implements abbreviated name-based filename generation (e.g., "IYT-33.txt"), and reduces the initial window size by 10% while making it resizable. These changes improve readability and usability for users processing document extractions.

## Technical Context
**Language/Version**: Python 3.10+
**Primary Dependencies**: tkinter (built-in), tkinterdnd2 0.3.0+, PyMuPDF 1.23.0+, python-docx 1.1.0+, olefile 0.46+
**Storage**: JSON files (config.json for keyword history persistence)
**Testing**: Manual validation (per constitution - no automated testing required)
**Target Platform**: Windows 10/11 (PyInstaller --onefile distribution), developed on macOS
**Project Type**: Single project (desktop GUI application)
**Performance Goals**: Instant UI response (<100ms), document processing depends on size
**Constraints**: Single executable deployment, no external dependencies, Unicode/Cyrillic support required
**Scale/Scope**: 2 users, single-screen workflow, processes PDF/DOCX documents

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### User-First Simplicity
- [x] Single-screen GUI workflow maintained - Changes only affect output formatting and window sizing, no workflow changes
- [x] No technical knowledge required for operation - Formatting is automatic, window resizing is standard UI interaction
- [x] Complex operations hidden behind simple controls - No new controls added, existing extraction workflow unchanged

### Graceful Degradation
- [x] Error handling continues processing on failures - Changes to output format don't affect error handling logic
- [x] All errors collected and reported at end - Existing error collection mechanisms remain intact
- [x] Partial results prioritized over complete failure - Output formatting changes support partial results

### Unicode-First
- [x] Full Cyrillic and Latin character support verified - Table formatting and abbreviated names preserve Cyrillic characters
- [x] Mixed script handling implemented - Abbreviated name generation works with Cyrillic/Latin mix
- [x] Character encoding preserved throughout pipeline - No changes to encoding handling, filenames support Cyrillic

### Keyword History Persistence
- [x] Keyword storage mechanism defined - No changes to keyword history mechanism
- [x] History persists across sessions - Unaffected by this feature
- [x] Multi-select from history supported - Unaffected by this feature

### Human-Readable Output
- [x] Plain text format with clear labels - Enhanced table-like format improves human readability
- [x] Metadata included (filename, timestamp) - Metadata sections remain, formatting improved
- [x] Page/line numbers for each extraction - Existing location tracking preserved

### Distribution Requirements
- [x] PyInstaller --onefile configuration - No new dependencies, changes are Python stdlib compatible
- [x] Windows 10/11 compatibility verified - tkinter window resizing is cross-platform standard
- [x] No external Python/dependencies required - All changes use existing dependencies

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
├── models/                    # Data models and business entities
│   ├── personal_information.py   # Personal info model (abbreviated name generation)
│   ├── output_report.py          # Output report model (table formatting)
│   └── ...
├── services/                  # Business logic and services
│   ├── output_generator.py       # Output file generation (table formatting, semicolons)
│   └── ...
├── ui/                        # User interface components
│   ├── main_window.py            # Main window (resizable, 10% smaller initial size)
│   └── ...
├── extractors/               # Extraction logic
├── parsers/                  # Document parsers
└── controllers/              # Application controllers

tests/                         # Manual validation per constitution (no automated tests)
```

**Structure Decision**: This is a single-project desktop application. The feature impacts three main areas:
1. **Output formatting** - Changes to `services/output_generator.py` for table-like format and semicolons
2. **Personal information** - Changes to `models/personal_information.py` for abbreviated name generation
3. **UI configuration** - Changes to `ui/main_window.py` for window sizing and resizability

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Extract validation scenarios** from user stories:
   - Each story → manual validation checklist
   - Quickstart = story validation steps

4. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, quickstart.md (with validation checklist), agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:

1. **Model Extension Tasks** (from data-model.md):
   - Task: Extend PersonalInformation model with middle_name and age fields
   - Task: Implement full_name property in PersonalInformation
   - Task: Implement get_abbreviated_name() method in PersonalInformation
   - Task: Update PersonalInfoExtractor to parse age from comma-separated format

2. **Service Refactoring Tasks** (from output-generator-service.md contract):
   - Task: Create table formatting helper methods (_format_table_row, _calculate_column_widths)
   - Task: Refactor format_output() to use table layout for personal info section
   - Task: Refactor format_output() to use table layout for keyword extractions section
   - Task: Add semicolon suffix logic to numeric values in format_output()
   - Task: Update generate_filename() signature to accept PersonalInformation
   - Task: Implement abbreviated name-based filename logic in generate_filename()
   - Task: Update generate() method to pass PersonalInformation to generate_filename()
   - Task: Remove file collision handling logic from generate()

3. **UI Configuration Tasks** (from main-window-ui.md contract):
   - Task: Update MainWindow geometry initialization to 1080x900
   - Task: Remove minsize() constraint from MainWindow

4. **Validation Tasks** (from quickstart.md):
   - Task: Manual validation - Personal info table formatting
   - Task: Manual validation - Keyword extractions table formatting
   - Task: Manual validation - Semicolon suffixes on numeric values
   - Task: Manual validation - Abbreviated name-based filenames
   - Task: Manual validation - Window initial size and resizability
   - Task: Manual validation - Character encoding (Cyrillic preservation)
   - Task: Manual validation - Edge cases and integration test

**Ordering Strategy**:
1. **Phase 1 - Model Extensions** (Foundation):
   - PersonalInformation model changes [P]
   - PersonalInfoExtractor updates (depends on model)

2. **Phase 2 - Service Refactoring** (Core Logic):
   - Table formatting helpers [P]
   - format_output() refactor (depends on helpers)
   - generate_filename() refactor (depends on PersonalInformation model)
   - generate() method updates (depends on generate_filename)

3. **Phase 3 - UI Configuration** (Presentation):
   - MainWindow configuration changes [P]

4. **Phase 4 - Validation** (Quality Assurance):
   - All manual validation tasks (depends on all implementation tasks)

**Parallelization**:
- [P] Model extension and PersonalInfoExtractor can run in parallel
- [P] Table formatting helpers are independent
- [P] UI configuration is independent of output formatting
- All validation tasks run after implementation complete

**Estimated Output**: 18-20 numbered, dependency-ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved (Technical Context fully specified)
- [x] Complexity deviations documented (None - all principles satisfied)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
