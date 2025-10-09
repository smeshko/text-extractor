# Feature Specification: Keyword Presets Management

**Feature Branch**: `008-docs-presets-prd`
**Created**: 2025-10-09
**Status**: Draft
**Input**: User description: "@docs/presets_prd.md"

## Execution Flow (main)
```
1. Parse user description from Input
   → Loaded from docs/presets_prd.md
2. Extract key concepts from description
   → Identified: preset management, keyword collections, UI panel, persistence
3. For each unclear aspect:
   → All requirements clearly specified in PRD
4. Fill User Scenarios & Testing section
   → User flows defined for create/load/edit/delete operations
5. Generate Functional Requirements
   → Each requirement testable and derived from PRD specs
6. Identify Key Entities (if data involved)
   → KeywordPreset entity identified
7. Run Review Checklist
   → No implementation details in spec (removed from PRD)
   → All requirements testable
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

---

## User Scenarios & Testing

### Primary User Story
A user frequently extracts documents with the same set of keywords (e.g., medical reports requiring HTD, RTP, Temperature, Pressure, Volume). Currently, they must manually re-add these keywords for each extraction session. The user wants to save this collection as a "Medical Report" preset, then quickly load it with one click for future extractions, eliminating repetitive data entry.

### Acceptance Scenarios

1. **Given** I have active keywords "HTD, RTP, Temperature" in my workspace, **When** I click "Create New Preset" and enter name "Medical Report", **Then** a new preset card appears showing "Medical Report" with "HTD, RTP, Temperature" preview

2. **Given** I have a saved preset "Medical Report" with 5 keywords, **When** I click the [Load] button on that preset card, **Then** my active keywords are replaced with those 5 keywords in the exact saved order

3. **Given** I click [Load] on a preset while I have 3 active keywords, **When** the confirmation dialog appears, **Then** I see "Replace current keywords with preset 'Medical Report'?" with Replace/Cancel options

4. **Given** I have a preset "Quality Check" selected, **When** I click the [...] menu and select Edit, **Then** I can rename the preset and add/remove/reorder keywords in the edit dialog

5. **Given** I have 2 saved presets, **When** I close and reopen the application, **Then** both presets still appear in the Presets panel with their original names and keywords

6. **Given** the Presets section is expanded, **When** I click the "Presets ▲" header, **Then** the section collapses and shows "Presets ▼ (2 saved)"

7. **Given** I have no active keywords, **When** I view the Create New Preset button, **Then** it is disabled/non-clickable

8. **Given** I have a preset with 5 keywords, **When** the preset card renders, **Then** it shows the first 3 keywords followed by "+2 more"

9. **Given** I attempt to create a preset with name "Report@123", **When** validation runs, **Then** I see an error message because special characters are not allowed

10. **Given** I have a preset named "Medical", **When** I try to create another preset named "Medical", **Then** validation prevents duplicate names

### Edge Cases

- What happens when a user tries to create a preset with no active keywords? The Create New Preset button must be disabled in this state.
- How does the system handle a preset name exceeding 50 characters? Validation must reject the name and show an error message.
- What happens when loading a preset would replace 10+ active keywords? A confirmation dialog must appear regardless of the number being replaced.
- How does the preset panel behave when the user has 20+ saved presets? The preset card area scrolls vertically with a maximum height of 200px.
- What happens when no presets exist? Display message: "No presets saved. Create one from your active keywords."
- How does the system handle corrupted preset data on load? Invalid presets are skipped, and remaining valid presets load normally.

---

## Requirements

### Functional Requirements

#### Preset Creation
- **FR-001**: System MUST allow users to create a new preset from currently active keywords with a user-provided name
- **FR-002**: System MUST disable preset creation when no active keywords exist
- **FR-003**: System MUST validate preset names to be maximum 50 characters, alphanumeric characters plus spaces only, and unique across all presets
- **FR-004**: System MUST preserve the exact order of keywords as they appear in the active list when saving a preset

#### Preset Loading
- **FR-005**: System MUST replace all active keywords with preset keywords when user clicks [Load] button
- **FR-006**: System MUST show confirmation dialog "Replace current keywords with preset '[name]'?" when loading a preset while active keywords exist
- **FR-007**: System MUST load keywords in the exact order they were saved in the preset

#### Preset Editing
- **FR-008**: System MUST allow users to rename a preset while maintaining same validation rules (50 chars, alphanumeric + spaces, unique)
- **FR-009**: System MUST allow users to add, remove, and reorder keywords within an existing preset
- **FR-010**: System MUST preserve preset keyword order when edited

#### Preset Deletion
- **FR-011**: System MUST show confirmation dialog "Delete preset '[name]'?" before removing a preset
- **FR-012**: System MUST permanently remove the preset from saved list after user confirms deletion

#### Preset Display
- **FR-013**: System MUST display preset name in bold 14px font on each preset card
- **FR-014**: System MUST show first 3 keywords comma-separated, then "+N more" if additional keywords exist
- **FR-015**: System MUST provide [Load] button and [...] menu button on each preset card
- **FR-016**: System MUST display presets in a vertically scrollable area with maximum height of 200px

#### Panel Behavior
- **FR-017**: System MUST position Presets section above the existing keyword history section
- **FR-018**: System MUST allow users to collapse/expand the Presets section by clicking the header
- **FR-019**: System MUST display "Presets ▼ (N saved)" when collapsed and "Presets ▲" when expanded
- **FR-020**: System MUST remember the collapsed/expanded state between application sessions
- **FR-021**: System MUST default to collapsed state on first use

#### Empty State
- **FR-022**: System MUST display message "No presets saved. Create one from your active keywords." when no presets exist

#### Data Persistence
- **FR-023**: System MUST persist all presets across application restarts
- **FR-024**: System MUST save presets with structure containing preset name and keyword list
- **FR-025**: System MUST handle migration for existing configurations without preset data by initializing an empty preset list

#### Integration
- **FR-026**: System MUST NOT impact existing keyword history functionality
- **FR-027**: System MUST apply same keyword validation to preset keywords as to active keywords (max 100 characters)

### Key Entities

- **KeywordPreset**: Represents a saved collection of keywords with a user-defined name
  - Name: String identifier chosen by user (max 50 chars, alphanumeric + spaces, unique)
  - Keywords: Ordered list of keyword strings
  - Display order: Preserves insertion order for consistent user experience
  - Relationships: Independent from keyword history but shares same keyword validation rules

---

## Review & Acceptance Checklist

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked (none found)
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---
