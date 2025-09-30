<!--
SYNC IMPACT REPORT
==================
Version Change: [NEW] → 1.0.0
Modified Principles: N/A (initial version)
Added Sections:
  - Core Principles (5 principles)
  - Distribution Requirements
  - Governance
Removed Sections: N/A
Templates Requiring Updates:
  ✅ .specify/templates/plan-template.md - Updated Constitution Check section reference
  ✅ .specify/templates/spec-template.md - Aligned with user-focused requirements
  ✅ .specify/templates/tasks-template.md - Removed test-first requirements per constitution
Follow-up TODOs:
  - Ratification date set to 2025-09-30 (today) as initial adoption
-->

# Document Data Extraction Tool Constitution

## Core Principles

### I. User-First Simplicity

The application MUST maintain a single-screen GUI workflow accessible to non-technical users. All interactions MUST be intuitive without requiring technical knowledge or documentation. Complex operations MUST be hidden behind simple controls (Browse, Extract, Settings).

**Rationale**: Target users are document creators with minimal technical expertise; complexity creates adoption barriers.

### II. Graceful Degradation

The system MUST continue processing when encountering errors. Keyword not found, ambiguous number formats, or missing personal information MUST NOT halt execution. All errors MUST be collected and reported together at the end of processing. Partial results are preferable to complete failure.

**Rationale**: Documents are often imperfect; users need maximum data extraction even from flawed inputs.

### III. Unicode-First

All text processing MUST fully support Unicode character sets, with primary support for Cyrillic and secondary support for Latin scripts. The system MUST handle mixed Cyrillic/Latin text within the same document. File names, keywords, personal information, and output MUST preserve original character encoding.

**Rationale**: Target documents are primarily in Cyrillic; character corruption renders results unusable.

### IV. Keyword History Persistence

Keywords used in previous sessions MUST be persisted and made available for reuse. Users MUST be able to select multiple historical keywords alongside new manual entries. The keyword history MUST survive application restarts and system reboots.

**Rationale**: Users work with recurring document types; re-entering 5-10 keywords per session creates friction.

### V. Human-Readable Output

Output files MUST use plain text format optimized for human parsing, not machine processing. Each extraction MUST include keyword name, value, page number, and line number (if available) in a flat structure. Document metadata (filename, timestamp) and personal information MUST be clearly labeled.

**Example**:
```
Document: report_2024.pdf
Processed: 2024-09-29 10:30
Name: Иван Петров (Ivan Petrov)
ID: 1234***
HTD: 3,5 (Page 2, Line 15)
HTD: 4,2 (Page 5, Line 8)
```

**Rationale**: Users manually review and process extraction results; structured formats (JSON, CSV) require additional tools.

## Distribution Requirements

### Single Executable Deployment

The application MUST be packaged as a single Windows executable (.exe) file using PyInstaller with the `--onefile` flag. The executable MUST run on Windows 10/11 without requiring Python installation or additional dependencies. Development on macOS MUST NOT compromise Windows compatibility.

**Rationale**: Target users cannot install Python or manage dependencies; distribution complexity prevents deployment.

### Testing Policy

The project explicitly EXCLUDES automated testing. No unit tests, integration tests, or test-first development practices are required. Validation relies on manual testing against representative documents.

**Rationale**: Project scope (2 users, solo development) does not justify testing infrastructure overhead; manual validation is sufficient.

## Governance

### Amendment Process

Constitution changes require:
1. Documented justification referencing PRD requirements or user feedback
2. Review of impact on existing implementation
3. Update of version number following semantic versioning (MAJOR.MINOR.PATCH)
4. Synchronization of dependent templates (plan, spec, tasks)

### Compliance Review

Features and implementation decisions MUST align with constitutional principles. Violations require explicit justification in the Complexity Tracking section of plan.md. Unjustified complexity MUST be simplified before proceeding.

### Version Control

This constitution supersedes all other development practices and preferences. When conflicts arise between this document and external guidance, constitution principles take precedence.

**Version**: 1.0.0 | **Ratified**: 2025-09-30 | **Last Amended**: 2025-09-30
