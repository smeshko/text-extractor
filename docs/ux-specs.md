# Document Data Extractor - UX Specification

**Version:** 1.0  
**Date:** September 29, 2025  
**Status:** Final for Implementation

---

## Table of Contents
1. [Overview](#overview)
2. [Design Principles](#design-principles)
3. [Layout & Structure](#layout--structure)
4. [Component Specifications](#component-specifications)
5. [User Flow](#user-flow)
6. [States & Interactions](#states--interactions)
7. [Visual Design](#visual-design)
8. [Error States](#error-states)
9. [Implementation Notes](#implementation-notes)

---

## 1. Overview

### 1.1 Purpose
A single-screen desktop application for extracting keyword-associated numerical values and personal information from documents (PDF/DOCX).

### 1.2 Target Platform
- Windows 10/11 Desktop Application
- Minimum Resolution: 1024x768
- Optimal Resolution: 1280x720 or higher

### 1.3 Framework
- Python 3.10+ with tkinter
- Single executable deployment

---

## 2. Design Principles

### 2.1 Core Principles
1. **Simplicity First** - Single screen, linear workflow
2. **Visual Hierarchy** - Numbered steps guide the user
3. **Immediate Feedback** - All actions provide visual confirmation
4. **Forgiving UX** - Easy to undo/modify before extraction
5. **No Surprises** - Output location clearly visible before processing

### 2.2 Interaction Philosophy
- Drag-and-drop preferred over dialogs
- Progressive disclosure (settings hidden by default)
- Non-blocking UI during processing

---

## 3. Layout & Structure

### 3.1 Window Properties
```
Title: "Document Data Extractor"
Size: 900px width × 800px height (minimum)
Resizable: Yes (minimum enforced)
Background: Light gray (#F9FAFB)
```

### 3.2 Main Sections (Top to Bottom)

```
┌─────────────────────────────────────────────────────────┐
│  HEADER (Title + Settings Button)                       │
├─────────────────────────────────────────────────────────┤
│  [SETTINGS PANEL - Collapsible]                         │
├─────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────┐  │
│  │  MAIN CARD (White Background, Rounded, Shadow)    │  │
│  │                                                   │  │
│  │  1. FILE SELECTION AREA                           │  │
│  │     - Drag/Drop Zone or Selected File Display     │  │
│  │                                                   │  │
│  │  2. KEYWORD MANAGEMENT                            │  │
│  │     - Input Field                                 │  │
│  │     - Keyword History (Collapsible)               │  │
│  │     - Active Keywords Display                     │  │
│  │                                                   │  │
│  │  3. EXTRACT BUTTON                                │  │
│  │                                                   │  │
│  │  PROGRESS BAR (when processing)                   │  │
│  │                                                   │  │
│  │  RESULTS MESSAGE (when complete)                  │  │
│  └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│  FOOTER (Info Text)                                     │
└─────────────────────────────────────────────────────────┘
```

### 3.3 Spacing & Padding
- Window padding: 32px all sides
- Section spacing: 32px between major sections
- Component spacing: 16px between related elements
- Card padding: 32px all sides

---

## 4. Component Specifications

### 4.1 Header

#### Layout
```
┌────────────────────────────────────────────────────┐
│  Document Data Extractor              [Settings ⚙] │
│  Extract keyword-associated values...              │
└────────────────────────────────────────────────────┘
```

#### Specifications
- **Title Font**: 24px, Bold, Dark Gray (#111827)
- **Subtitle Font**: 14px, Regular, Medium Gray (#6B7280)
- **Settings Button**: 
  - Size: 40px × 40px
  - Icon: Gear/cog icon
  - Hover: Light gray background (#E5E7EB)
  - Corner: Top-right of header

---

### 4.2 Settings Panel

#### Visibility
- Hidden by default
- Toggle via Settings button in header
- Smooth expand/collapse animation (200ms)

#### Layout
```
┌──────────────────────────────────────────────────────────┐
│  Settings                                                │
│                                                          │
│  Output Folder Path                                      │
│  ┌────────────────────────────────────────┐  ┌────────┐  │
│  │ C:\Users\Documents\Extractions         │  │ Browse │  │
│  └────────────────────────────────────────┘  └────────┘  │
│  Extracted files will be automatically saved to this...  │
│                                                          │
│  Number Format                                           │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Comma as decimal (3,5)                      ▼    │    │
│  └──────────────────────────────────────────────────┘    │
│                                                          │
│  Keyword Proximity                                       │
│  ┌──────────────────────────────────────────────────┐    │
│  │ Same line only                              ▼    │    │
│  └──────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────┘
```

#### Components

**Output Folder Path**
- Input field: 70% width, editable
- Browse button: 25% width
- Help text: 11px, Gray (#6B7280)
- Browse button opens native folder picker dialog

**Number Format Dropdown**
- Options:
  1. Comma as decimal (3,5)
  2. Period as decimal (3.5)
  3. Auto-detect
- Default: Comma as decimal

**Keyword Proximity Dropdown**
- Options:
  1. Same line only
  2. Within same sentence
  3. Within 10 words
- Default: Same line only

---

### 4.3 File Selection Area

#### State 1: No File Selected (Empty State)

```
┌────────────────────────────────────────────────────────┐
│                        ↑                               │
│                     [Upload]                           │
│                                                        │
│          Drag and drop your document here              │
│                                                        │
│                        or                              │
│                                                        │
│                  [ Browse Files ]                      │
│                                                        │
│              Supports PDF and DOCX files               │
└────────────────────────────────────────────────────────┘
```

**Specifications:**
- Border: 2px dashed, Gray (#D1D5DB)
- Padding: 64px vertical, 32px horizontal
- Background: White
- Upload icon: 48px, Gray (#9CA3AF)
- Main text: 16px, Gray (#6B7280)
- "or" text: 14px, Light Gray (#9CA3AF)
- Browse button: Blue (#2563EB), 14px, Rounded
- Help text: 12px, Light Gray (#9CA3AF)

**Interactions:**
- Hover: Border changes to Blue (#2563EB)
- Drag over: Background changes to Light Blue (#EFF6FF), border Blue
- Browse button opens native file picker (filters: *.pdf, *.docx)

#### State 2: File Selected

```
┌────────────────────────────────────────────────────────┐
│  [📄]  report_2024.pdf                            [×]  │
│        Ready to process                                │
└────────────────────────────────────────────────────────┘
```

**Specifications:**
- Layout: Horizontal flex, centered
- Icon: 48px file icon, Blue background circle (#DBEAFE)
- Filename: 16px, Bold, Dark Gray (#111827)
- Status text: 14px, Regular, Medium Gray (#6B7280)
- Remove button (×): 32px, Hover: Light gray background
- Padding: 16px all sides

**Interactions:**
- Click remove (×) returns to empty state
- Drag new file replaces current file
- Click anywhere (except ×) opens file picker to replace

---

### 4.4 Keywords Section

#### Layout
```
2. Add Keywords to Extract

┌────────────────────────────────────────────┐  ┌──────┐
│ Enter keyword (e.g., HTD, Temperature)     │  │  Add │
└────────────────────────────────────────────┘  └──────┘

🔍 Show keyword history

Active Keywords (2):
┌─────────┐  ┌─────────┐
│ HTD  [×]│  │ RTP  [×]│
└─────────┘  └─────────┘
```

#### Keyword Input Field
- Width: 75%
- Height: 40px
- Placeholder: "Enter keyword (e.g., HTD, Temperature)"
- Font: 14px
- Border: 1px, Gray (#D1D5DB)
- Focus: 2px Blue ring (#2563EB)
- Enter key triggers Add button

#### Add Button
- Width: 20%
- Height: 40px
- Background: Blue (#2563EB)
- Text: "Add" with plus icon
- Disabled state: Gray (#D1D5DB) when input empty
- Hover: Darker Blue (#1E40AF)

#### Keyword History Toggle
- Text: "Show keyword history" / "Hide keyword history"
- Font: 12px, Blue (#2563EB)
- Icon: Search icon (16px)
- Hover: Underline

#### Keyword History Panel (When Expanded)
```
┌──────────────────────────────────────────────────────┐
│  Previously Used:                                    │
│  ┌───┐ ┌───┐ ┌───────────┐ ┌──────────┐ ┌────────┐   │
│  │HTD│ │RTP│ │Temperature│ │ Pressure │ │ Volume │   │
│  └───┘ └───┘ └───────────┘ └──────────┘ └────────┘   │
└──────────────────────────────────────────────────────┘
```

**Specifications:**
- Background: Light Gray (#F9FAFB)
- Padding: 16px
- Border radius: 8px
- Header: 12px, Bold, Dark Gray (#374151)
- History buttons:
  - Background: White
  - Border: 1px Gray (#D1D5DB)
  - Padding: 8px 12px
  - Font: 13px
  - Hover: Light Gray (#F3F4F6)
  - Disabled (already added): Opacity 50%, no hover

#### Active Keywords Display

**Header:**
- Text: "Active Keywords (N):" where N is count
- Font: 14px, Medium weight, Dark Gray (#374151)

**Keyword Chips:**
```
┌─────────────┐
│ HTD     [×] │
└─────────────┘
```

- Background: Light Blue (#DBEAFE)
- Text Color: Dark Blue (#1E3A8A)
- Padding: 8px 12px
- Border radius: 8px
- Font: 14px, Medium weight
- Remove button (×): 16px icon, Hover: Darker blue background
- Spacing: 8px between chips
- Wrap: Multiple rows if needed

**Empty State:**
- Text: "No keywords added yet"
- Font: 13px, Light Gray (#9CA3AF)

---

### 4.5 Extract Button

#### Layout
```
┌──────────────────────────────────────────────────────┐
│               3. Extract Data                        │
└──────────────────────────────────────────────────────┘
```

**Specifications:**
- Width: 100%
- Height: 48px
- Background: Green (#16A34A)
- Text: "3. Extract Data" (18px, Bold, White)
- Border radius: 8px
- Hover: Darker Green (#15803D)
- Disabled: Gray (#D1D5DB), cursor not-allowed

**Disabled Conditions:**
- No file selected
- No keywords added
- Currently processing

**Processing State:**
- Text changes to "Extracting..."
- Cannot click
- Shows progress bar below

---

### 4.6 Progress Bar

#### Layout
```
Processing document...                                75%

████████████████████████████░░░░░░░░░░
```

**Specifications:**
- Appears below Extract button when processing
- Label row:
  - Left: "Processing document..." (14px, Gray)
  - Right: Percentage (14px, Gray)
  - Margin bottom: 8px
- Bar:
  - Height: 8px
  - Background: Light Gray (#E5E7EB)
  - Fill: Blue (#2563EB)
  - Border radius: 4px (full pill shape)
  - Smooth animation (300ms transitions)

---

### 4.7 Results Message

#### Layout
```
┌────────────────────────────────────────────────────────┐
│  ✓ Extraction Complete!                                │
│                                                        │
│  File saved successfully:                              │
│  C:\Users\Documents\Extractions\output_report_2024.txt │
│                                                        │
│  [ Open Output File ]  [ Open Folder ]                 │
└────────────────────────────────────────────────────────┘
```

**Specifications:**
- Background: Light Green (#F0FDF4)
- Border: 1px Green (#86EFAC)
- Border radius: 8px
- Padding: 16px

**Success Icon (✓):**
- Color: Green (#16A34A)
- Size: Inline with text

**Title:**
- Text: "Extraction Complete!"
- Font: 16px, Bold, Dark Green (#166534)
- Margin bottom: 8px

**Path Label:**
- Text: "File saved successfully:"
- Font: 13px, Green (#15803D)
- Margin bottom: 4px

**File Path:**
- Background: White
- Border: 1px Light Green (#BBF7D0)
- Padding: 8px 12px
- Font: 13px, Monospace, Dark Green (#14532D)
- Border radius: 4px
- Margin bottom: 12px

**Action Buttons:**
- "Open Output File":
  - Background: Green (#16A34A)
  - Text: White, 13px
  - Hover: Darker Green (#15803D)
- "Open Folder":
  - Background: White
  - Border: 1px Green (#86EFAC)
  - Text: Green (#16A34A), 13px
  - Hover: Light Green background (#F0FDF4)
- Height: 36px
- Padding: 8px 16px
- Border radius: 8px
- Spacing: 8px between buttons

---

### 4.8 Footer

```
Extracts numerical values, names (Cyrillic/Latin), and ID numbers
```

**Specifications:**
- Text: 12px, Center aligned, Light Gray (#9CA3AF)
- Margin top: 24px
- Single line

---

## 5. User Flow

### 5.1 Happy Path

```
1. User opens application
   ↓
2. User drags PDF file onto drop zone
   OR clicks Browse and selects file
   ↓
3. File appears in selection area
   ↓
4. User types "HTD" and clicks Add
   ↓
5. "HTD" appears in Active Keywords
   ↓
6. User clicks "Show keyword history"
   ↓
7. User clicks "RTP" from history
   ↓
8. "RTP" appears in Active Keywords
   ↓
9. User clicks "Extract Data" button
   ↓
10. Progress bar appears and animates
    ↓
11. Success message appears with file path
    ↓
12. User clicks "Open Output File"
    ↓
13. Text file opens in default editor
```

### 5.2 Settings Configuration Flow

```
1. User clicks Settings icon (⚙)
   ↓
2. Settings panel expands
   ↓
3. User clicks Browse next to Output Path
   ↓
4. Folder picker dialog opens
   ↓
5. User selects folder
   ↓
6. Path updates in input field
   ↓
7. User changes Number Format dropdown
   ↓
8. User clicks Settings icon to close
   ↓
9. Settings panel collapses
   ↓
10. Settings saved automatically
```

---

## 6. States & Interactions

### 6.1 Application States

| State | Description | Visual Indicators |
|-------|-------------|-------------------|
| **Initial** | App just opened | Empty drop zone, no keywords, Extract disabled |
| **File Selected** | User has chosen a file | File info shown, drop zone replaced |
| **Keywords Added** | At least one keyword added | Keywords displayed as chips, Extract enabled |
| **Processing** | Extraction in progress | Progress bar visible, Extract disabled, "Extracting..." |
| **Complete** | Extraction finished | Green success message, action buttons |
| **Error** | Something went wrong | Red error message (see Error States) |

### 6.2 Interactive Elements

#### Buttons
- **Default**: Solid background, white text
- **Hover**: Darker shade of background (10-15%)
- **Active/Click**: Even darker shade (20%)
- **Disabled**: Gray (#D1D5DB), no hover effect, cursor: not-allowed
- **Focus**: 2px outline in button color at 50% opacity

#### Input Fields
- **Default**: 1px gray border
- **Hover**: Border darkens slightly
- **Focus**: 2px blue ring (#2563EB), no border
- **Error**: 2px red ring (#DC2626)
- **Disabled**: Gray background, no interaction

#### Dropdowns
- **Default**: Right-aligned chevron icon
- **Hover**: Light gray background
- **Open**: Dropdown menu appears below
- **Selected**: Checkmark next to selected option

### 6.3 Drag-and-Drop States

| State | Visual Change |
|-------|---------------|
| **Idle** | Dashed gray border |
| **Hover** | Border changes to solid blue |
| **Drag Over** | Light blue background, blue border |
| **Drop** | Flash animation, then show file |
| **Invalid File** | Red border flash, error message |

---

## 7. Visual Design

### 7.1 Color Palette

```
Primary Colors:
- Blue:       #2563EB (buttons, links, highlights)
- Green:      #16A34A (success, extract button)
- Red:        #DC2626 (errors, warnings)

Neutral Colors:
- Dark Gray:  #111827 (headings, main text)
- Gray:       #6B7280 (body text)
- Light Gray: #9CA3AF (secondary text, icons)
- Border:     #D1D5DB (dividers, outlines)
- Background: #F9FAFB (page background)
- White:      #FFFFFF (cards, inputs)

Accent Colors:
- Light Blue:  #DBEAFE (keyword chips background)
- Light Green: #F0FDF4 (success message background)
- Light Red:   #FEE2E2 (error message background)
```

### 7.2 Typography

```
Font Family: 
- Primary: System default (Segoe UI on Windows)
- Monospace: Consolas, Courier New (for file paths)

Font Sizes:
- H1 (Title):        24px, Bold
- H2 (Section):      18px, Semi-Bold
- Body Large:        16px, Regular
- Body:              14px, Regular
- Body Small:        13px, Regular
- Caption:           12px, Regular
- Tiny:              11px, Regular

Line Heights:
- Headings: 1.2
- Body: 1.5
- Compact elements: 1.3
```

### 7.3 Spacing System

```
Base Unit: 4px

Spacing Scale:
- xs:   4px   (tight spacing within elements)
- sm:   8px   (related items)
- md:   16px  (standard spacing)
- lg:   24px  (section spacing)
- xl:   32px  (major sections)
- 2xl:  48px  (rare, large gaps)
- 3xl:  64px  (very rare)
```

### 7.4 Border Radius

```
- sm: 4px  (small elements, progress bars)
- md: 8px  (buttons, inputs, cards)
- lg: 12px (large cards)
- full: 50% (pills, circular elements)
```

### 7.5 Shadows

```
- Card: 0 1px 3px rgba(0,0,0,0.1), 0 1px 2px rgba(0,0,0,0.06)
- Hover: 0 4px 6px rgba(0,0,0,0.1), 0 2px 4px rgba(0,0,0,0.06)
- Settings Panel: 0 10px 15px rgba(0,0,0,0.1), 0 4px 6px rgba(0,0,0,0.05)
```

---

## 8. Error States

### 8.1 Error Message Component

```
┌────────────────────────────────────────────────────────┐
│  ⚠ Error Processing Document                          │
│                                                        │
│  Could not extract data from file. The document may   │
│  be corrupted or password-protected.                   │
│                                                        │
│  [ Try Another File ]  [ View Details ]               │
└────────────────────────────────────────────────────────┘
```

**Specifications:**
- Background: Light Red (#FEE2E2)
- Border: 1px Red (#FCA5A5)
- Warning icon (⚠): Red (#DC2626)
- Text: Dark Red (#991B1B)
- Same layout as success message

### 8.2 Error Scenarios

| Error Type | Message | Actions |
|------------|---------|---------|
| **Invalid File Type** | "Unsupported file type. Please select a PDF or DOCX file." | "Choose Different File" |
| **File Not Found** | "Could not open file. It may have been moved or deleted." | "Select Another File" |
| **Corrupted File** | "Could not read document. The file may be corrupted." | "Try Another File" |
| **No Keywords Found** | "⚠ Warning: None of the keywords were found in the document." | "View Results Anyway", "Edit Keywords" |
| **Partial Success** | "✓ Extraction complete with warnings. Some keywords were not found." | "View Results", "View Details" |
| **Write Permission** | "Could not save output file. Check folder permissions." | "Choose Different Folder", "Retry" |

### 8.3 Inline Validation

**Keyword Input:**
- Show error under field if trying to add duplicate keyword
- Text: "This keyword is already added"
- Color: Red (#DC2626), 12px

**Output Path:**
- Show warning icon if path doesnt exist
- Text: "⚠ Folder will be created when saving"
- Color: Orange (#F59E0B), 12px

---

## Appendix A: Complete State Diagram

```
┌─────────┐
│ Initial │
└────┬────┘
     │ File Selected
     ▼
┌──────────────┐
│ File Loaded  │
└────┬─────────┘
     │ Keyword Added
     ▼
┌──────────────┐      Click Extract
│ Ready        │─────────────────────┐
└──────────────┘                     │
     ▲                               ▼
     │                          ┌──────────┐
     │         Complete         │Processing│
     │      ◄───────────────────└──────────┘
     │                               │
     │                               │ Error
     │                               ▼
┌────┴──────────┐                ┌───────┐
│ Results Shown │                │ Error │
└───────────────┘                └───────┘
```

---

## Appendix C: File Naming Convention

Output files follow this pattern:
```
output_[original_filename_without_extension].txt
```

Examples:
- Input: `report_2024.pdf` → Output: `output_report_2024.txt`
- Input: `Document.docx` → Output: `output_Document.txt`
- Input: `my file (copy).pdf` → Output: `output_my file (copy).txt`

Special characters in filenames are preserved. Invalid path characters are replaced with underscores.

---

**END OF UX SPECIFICATION**