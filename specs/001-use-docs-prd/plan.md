
# Implementation Plan: Document Data Extraction Tool

**Branch**: `001-use-docs-prd` | **Date**: September 30, 2025 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-use-docs-prd/spec.md`

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
A desktop application that extracts keyword-associated numerical values and personal information from PDF and DOCX documents. The tool provides a single-screen GUI for non-technical users to select files, enter keywords, and generate plain text output files with extracted data and location references (page/line numbers). Built with Python 3.10+ and tkinter, distributed as a standalone Windows executable requiring no Python installation.

## Technical Context
**Language/Version**: Python 3.10+
**Primary Dependencies**: tkinter (built-in), tkinterdnd2 0.3.0+, PyMuPDF 1.23.0+ (PDF parsing), python-docx 1.1.0+ (DOCX parsing), PyInstaller 5.13+ (executable packaging)
**Storage**: JSON configuration file (config.json) for settings and keyword history persistence
**Testing**: Manual validation against representative documents (no automated testing per constitution)
**Target Platform**: Windows 10/11 (64-bit) runtime, macOS development environment
**Project Type**: single (desktop application)
**Performance Goals**: <30 seconds processing time for typical documents (up to 50 pages), <10 seconds preferred for standard documents
**Constraints**: Single executable <100MB, no Python installation required, responsive UI during processing (dual-thread architecture), full Unicode support (Cyrillic + Latin)
**Scale/Scope**: 2 end users, 5-10 keywords per extraction, single file processing, simple tool (no complex testing infrastructure)

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### User-First Simplicity
- [x] Single-screen GUI workflow maintained - tkinter single window with all controls
- [x] No technical knowledge required for operation - Browse, drag-and-drop, Extract buttons only
- [x] Complex operations hidden behind simple controls - Settings panel for advanced options

### Graceful Degradation
- [x] Error handling continues processing on failures - Non-blocking processing strategy (section 6.5)
- [x] All errors collected and reported at end - Error accumulation in results object
- [x] Partial results prioritized over complete failure - Mark missing data as "Not found", continue

### Unicode-First
- [x] Full Cyrillic and Latin character support verified - UTF-8 encoding throughout, FR-020 to FR-024
- [x] Mixed script handling implemented - Personal info extraction handles mixed character sets
- [x] Character encoding preserved throughout pipeline - Plain text UTF-8 output

### Keyword History Persistence
- [x] Keyword storage mechanism defined - JSON config file with keyword array (section 7.2)
- [x] History persists across sessions - Config saved on app close and settings change
- [x] Multi-select from history supported - FR-011, FR-012: select historical + new keywords

### Human-Readable Output
- [x] Plain text format with clear labels - Plain text output structure defined (section 7.3)
- [x] Metadata included (filename, timestamp) - FR-028, FR-029
- [x] Page/line numbers for each extraction - FR-017, FR-018, FR-033, FR-034

### Distribution Requirements
- [x] PyInstaller --onefile configuration - Section 11.2: --onefile flag specified
- [x] Windows 10/11 compatibility verified - Target platform explicitly defined
- [x] No external Python/dependencies required - Single .exe, no installer (section 11.3)

**Initial Constitution Check: PASS** ✅

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
├── models/              # Data structures (Document, Keyword, ExtractionMatch, PersonalInfo, OutputReport)
├── parsers/             # Document parsing (PDFParser, DOCXParser, ParserFactory)
├── extractors/          # Extraction logic (KeywordMatcher, NumberExtractor, PersonalInfoExtractor)
├── ui/                  # GUI components (MainWindow, FileSelector, KeywordPanel, ProgressBar, SettingsPanel)
├── controllers/         # Application control (AppController, StateManager, ThreadCoordinator)
├── services/            # Business logic (OutputGenerator, ConfigurationManager)
└── main.py             # Application entry point

config.json             # Runtime configuration (generated at first run)
requirements.txt        # Python dependencies
build.spec              # PyInstaller configuration
```

**Structure Decision**: Single-project MVC architecture for desktop application. No test directory per constitution (manual validation only). All source under `src/` organized by responsibility layer (models, parsers, extractors, ui, controllers, services). Config file at root for easy user access.

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

1. **From Data Model** (data-model.md):
   - Create Python dataclasses for each entity (Document, Keyword, ExtractionMatch, PersonalInformation, OutputReport, ProcessingLog, Configuration, ApplicationState, ExtractionResults)
   - Models → `src/models/` directory
   - Mark [P] where entities are independent

2. **From Parser Contract** (contracts/parser-contract.md):
   - Implement DocumentParser abstract base
   - Implement PDFParser using PyMuPDF
   - Implement DOCXParser using python-docx
   - Implement ParserFactory
   - Parsers → `src/parsers/` directory

3. **From Extractor Contract** (contracts/extractor-contract.md):
   - Implement ExtractionEngine
   - Implement KeywordMatcher
   - Implement NumberExtractor
   - Implement PersonalInfoExtractor
   - Extractors → `src/extractors/` directory

4. **From Output Contract** (contracts/output-contract.md):
   - Implement OutputGenerator
   - Implement ProcessingLogger
   - Services → `src/services/` directory

5. **From Configuration Contract** (contracts/configuration-contract.md):
   - Implement ConfigurationManager
   - Services → `src/services/` directory

6. **From UI Contract** (contracts/ui-contract.md):
   - Implement MainWindow (tkinter root)
   - Implement FileSelector component
   - Implement KeywordPanel component
   - Implement SettingsPanel component
   - Implement ProgressBar component
   - Implement ResultsDisplay component
   - UI → `src/ui/` directory

7. **Controllers & Integration**:
   - Implement AppController
   - Implement StateManager
   - Implement ThreadCoordinator
   - Controllers → `src/controllers/` directory

8. **Application Entry Point**:
   - Implement main.py
   - Wire all components together
   - Initialize config, UI, controllers

9. **Build Configuration**:
   - Create requirements.txt
   - Create build.spec for PyInstaller
   - Configure for --onefile build

10. **Manual Validation** (from quickstart.md):
    - Each validation scenario → validation task
    - Order: Basic → Edge Cases → Performance

**Ordering Strategy**:
1. Models first (foundation, all [P] parallel)
2. Parsers (depend on models only)
3. Extractors (depend on models and parsers)
4. Services (depend on models)
5. UI components (depend on models, can be [P] within UI)
6. Controllers (depend on all subsystems)
7. Main entry point (integrates everything)
8. Build configuration (after code complete)
9. Manual validation (after build)

**Dependency Graph**:
```
Models [P]
  ↓
Parsers, Services [P] → Extractors
  ↓
UI Components [P], Controllers
  ↓
Main Entry Point
  ↓
Build Configuration
  ↓
Manual Validation
```

**Estimated Output**: 35-40 numbered, ordered tasks in tasks.md
- 10 model tasks [P]
- 5 parser tasks
- 5 extractor tasks
- 3 service tasks (output, config)
- 6 UI component tasks [P]
- 3 controller tasks
- 1 main entry point task
- 2 build tasks
- 10-15 validation tasks

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

**No violations** - All constitutional principles satisfied by design:
- Single-screen GUI with tkinter
- Graceful degradation with error collection
- Full Unicode support via UTF-8 throughout
- JSON-based keyword history persistence
- Plain text human-readable output
- PyInstaller --onefile for Windows deployment


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command) - research.md created
- [x] Phase 1: Design complete (/plan command) - data-model.md, 5 contracts, quickstart.md, CLAUDE.md created
- [x] Phase 2: Task planning complete (/plan command - approach described, ready for /tasks)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS ✅
- [x] Post-Design Constitution Check: PASS ✅
- [x] All NEEDS CLARIFICATION resolved (via spec clarifications)
- [x] Complexity deviations documented (none - no violations)

**Artifacts Generated**:
- [x] research.md (Phase 0)
- [x] data-model.md (Phase 1)
- [x] contracts/parser-contract.md (Phase 1)
- [x] contracts/extractor-contract.md (Phase 1)
- [x] contracts/output-contract.md (Phase 1)
- [x] contracts/ui-contract.md (Phase 1)
- [x] contracts/configuration-contract.md (Phase 1)
- [x] quickstart.md (Phase 1)
- [x] CLAUDE.md (Phase 1)

**Next Step**: Run `/tasks` command to generate tasks.md from design artifacts

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
