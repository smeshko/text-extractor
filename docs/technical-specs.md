# Document Data Extractor - Technical Requirements Document

**Version:** 1.0  
**Status:** Final for Implementation  
**Last Updated:** September 30, 2025  
**Owner:** Development Team

---

## Table of Contents
1. [Executive Summary](#1-executive-summary)
2. [System Architecture](#2-system-architecture)
3. [Technology Stack](#3-technology-stack)
4. [Core Components](#4-core-components)
5. [Data Flow](#5-data-flow)
6. [Processing Logic](#6-processing-logic)
7. [Storage & Persistence](#7-storage--persistence)
8. [User Interface Architecture](#8-user-interface-architecture)
9. [Error Handling Strategy](#9-error-handling-strategy)
10. [Build & Deployment](#10-build--deployment)
11. [Open Technical Questions](#11-open-technical-questions)

---

## 1. Executive Summary

### 1.1 Purpose
This document defines the technical architecture and implementation requirements for the Document Data Extractor application—a desktop tool that extracts keyword-associated numerical values and personal information from PDF and DOCX files.

### 1.2 Technical Scope
- Single-screen desktop application for Windows 10/11
- Developed in Python 3.10+ using tkinter for GUI
- Distributed as standalone executable (.exe)
- Processing 5-10 keywords across documents up to 50 pages
- Plain text output with structured formatting

### 1.3 Key Technical Constraints
- Must run on Windows without Python installation
- Development on macOS, deployment on Windows
- Single-file executable under 100MB
- Processing time under 30 seconds for typical documents
- Support for Cyrillic and Latin character sets

---

## 2. System Architecture

### 2.1 Architectural Pattern
**Model-View-Controller (MVC) Architecture**

The application separates concerns into three primary layers:

- **View Layer**: tkinter-based GUI components handling all user interactions
- **Controller Layer**: Application logic coordinating between UI and processing
- **Model Layer**: Data structures, file parsing, and extraction algorithms

### 2.2 Component Overview

**Four Major Subsystems:**

1. **User Interface Subsystem**
   - Window management and layout
   - File selection handlers
   - Keyword management interface
   - Progress indication
   - Results display

2. **Processing Subsystem**
   - Document parsing (PDF/DOCX)
   - Text extraction and normalization
   - Keyword matching engine
   - Personal information extraction
   - Number format detection

3. **Data Management Subsystem**
   - Configuration storage
   - Keyword history persistence
   - Output file generation
   - State management

4. **Control Subsystem**
   - Event handling and routing
   - Thread management for async operations
   - Error collection and reporting
   - Progress tracking

### 2.3 Threading Model

**Dual-Thread Architecture:**

- **Main Thread**: UI rendering and event handling (never blocks)
- **Worker Thread**: Document processing and extraction (spawned on demand)

Communication between threads uses thread-safe queues and callback mechanisms to update progress and completion status.

---

## 3. Technology Stack

### 3.1 Core Technologies

| Layer | Technology | Purpose | Version |
|-------|------------|---------|---------|
| **Language** | Python | Core development language | 3.10+ |
| **GUI Framework** | tkinter | Native UI components | Built-in |
| **Drag-and-Drop** | tkinterdnd2 | File drop functionality | 0.3.0+ |
| **PDF Parser** | PyMuPDF (fitz) | PDF text extraction | 1.23.0+ |
| **DOCX Parser** | python-docx | Word document parsing | 1.1.0+ |
| **Pattern Matching** | re (regex) | Text pattern recognition | Built-in |
| **Threading** | threading | Async processing | Built-in |
| **JSON** | json | Configuration storage | Built-in |
| **Packaging** | PyInstaller | Executable generation | 5.13+ |

### 3.2 Development vs. Runtime Environment

**Development:**
- macOS operating system
- Python 3.10+ with virtual environment
- All libraries installed via pip
- Git for version control

**Runtime (End User):**
- Windows 10/11 (64-bit)
- No Python installation required
- No library installations required
- Single .exe file execution

---

## 4. Core Components

### 4.1 Application Controller
**Responsibility:** Central coordination of all subsystems

**Key Functions:**
- Initialize application and load configuration
- Manage application lifecycle
- Route user actions to appropriate handlers
- Coordinate between UI and processing threads
- Handle shutdown and cleanup

### 4.2 State Manager
**Responsibility:** Centralized application state

**Managed State:**
- Currently selected file (path and type)
- Active keywords list
- Processing status (idle/processing/complete/error)
- Configuration settings
- Extraction results
- Error and warning collections

**State Transitions:**
- IDLE → PROCESSING (when Extract clicked)
- PROCESSING → COMPLETE (on successful extraction)
- PROCESSING → ERROR (on failure)
- Any state → IDLE (on reset/new file)

### 4.3 Document Parser Factory
**Responsibility:** Select and instantiate appropriate parser

**Logic:**
- Detect file type from extension (.pdf or .docx)
- Create corresponding parser instance
- Provide uniform interface for text extraction
- Handle parser-specific errors

**Parsers:**
- PDF Parser (uses PyMuPDF)
- DOCX Parser (uses python-docx)

### 4.4 Extraction Engine
**Responsibility:** Core extraction logic

**Capabilities:**
- Case-insensitive keyword matching
- Number format detection and extraction
- Proximity-based keyword-number association
- Personal information pattern matching
- Multi-occurrence handling
- Page and line number tracking

### 4.5 Output Generator
**Responsibility:** Format and write results

**Functions:**
- Convert extraction results to plain text format
- Apply consistent formatting
- Generate unique output filenames
- Write to configured output directory
- Handle file system errors

### 4.6 Configuration Manager
**Responsibility:** Settings persistence

**Managed Settings:**
- Output folder path
- Number format preference
- Keyword proximity rule
- Keyword history
- Window dimensions

**Storage Format:** JSON file in application directory

---

## 5. Data Flow

### 5.1 Standard Processing Flow

```
User Action: Select File
    ↓
File path stored in State
    ↓
UI updates to show selected file
    ↓
User Action: Add Keywords
    ↓
Keywords stored in State and History
    ↓
UI displays active keywords
    ↓
User Action: Click Extract
    ↓
Validation: File + Keywords present?
    ↓
Spawn Worker Thread
    ↓
Main Thread: Display progress bar
    ↓
Worker Thread: Parse Document
    ↓
Worker Thread: Extract Text by Page
    ↓
Worker Thread: Run Extraction Engine
    ↓
Worker Thread: Search for Keywords
    ↓
Worker Thread: Extract Numbers
    ↓
Worker Thread: Extract Personal Info
    ↓
Worker Thread: Compile Results
    ↓
Worker Thread: Generate Output File
    ↓
Worker Thread: Signal Completion
    ↓
Main Thread: Update UI with Success
    ↓
User Views/Opens Output
```

### 5.2 Data Transformations

**Stage 1: File → Raw Text**
- Binary document → Text strings per page
- Preserve page boundaries
- Maintain line breaks

**Stage 2: Raw Text → Structured Text**
- Split pages into lines
- Normalize whitespace
- Identify text blocks

**Stage 3: Structured Text → Matches**
- Apply keyword patterns
- Find associated numbers
- Record locations (page, line)
- Extract personal information

**Stage 4: Matches → Results Object**
- Group matches by keyword
- Compile personal information
- Collect errors and warnings
- Add metadata (filename, timestamp)

**Stage 5: Results Object → Output File**
- Format as plain text
- Apply consistent structure
- Write to file system

---

## 6. Processing Logic

### 6.1 Document Parsing Strategy

**PDF Documents:**
- Open document using PyMuPDF
- Iterate through pages sequentially
- Extract text using `get_text()` method
- Preserve page numbers (1-indexed)
- Close document after extraction

**DOCX Documents:**
- Open document using python-docx
- Iterate through paragraphs
- Detect page breaks (where available)
- Approximate page numbers if breaks absent
- Extract text maintaining paragraph structure

### 6.2 Keyword Matching Algorithm

**Process:**
1. Normalize keyword (lowercase, trim whitespace)
2. Create case-insensitive regex pattern
3. Search each line of text
4. Record all matches (not just first)
5. For each match, apply proximity rule

**Proximity Rules:**

**Option A: Same Line Only**
- Search for number on same line after keyword
- Stop at line end or next keyword

**Option B: Same Sentence**
- Identify sentence boundaries (. ! ?)
- Search within sentence containing keyword

**Option C: Within N Words**
- Count tokens after keyword
- Search within N token window

### 6.3 Number Extraction Logic

**Format Detection:**
- Check configured number format preference
- If "auto-detect", try multiple patterns
- Extract first matching number after keyword

**Supported Formats:**
- Comma as decimal: `3,5`
- Period as decimal: `3.5`
- Integers: `3`
- With thousands separators: `3 500` or `3,500`

**Ambiguity Handling:**
- Flag numbers that match multiple patterns
- Record as warning in results
- Include in output with warning indicator

### 6.4 Personal Information Extraction

**Status:** Algorithm TBD pending PRD answers (Q7, Q8)

**Planned Approach:**
- Focus extraction on first page (likely location)
- Search for name patterns (Cyrillic/Latin)
- Search for ID number patterns (4 digits)
- Use labeled field detection if available
- Handle mixed character sets

### 6.5 Error Accumulation Strategy

**Non-Blocking Processing:**
- Continue processing on errors
- Collect all errors in list
- Mark missing data as "Not found"
- Flag ambiguous extractions
- Report all issues at completion

---

## 7. Storage & Persistence

### 7.1 Configuration File

**Location:** Same directory as executable  
**Filename:** `config.json`  
**Format:** JSON

**Contents:**
- Output folder path (string)
- Number format preference (enum string)
- Proximity rule (enum string)
- Keyword history (array of strings)
- Window dimensions (width, height integers)

**Persistence:**
- Load on application start
- Save on application close
- Save when settings changed

### 7.2 Keyword History

**Storage:** Within configuration file  
**Structure:** Array of unique keyword strings  
**Max Size:** Unlimited (practical limit ~1000)

**Management:**
- Append new keywords on first use
- Maintain order (most recent last)
- No duplicates
- Persist across sessions

### 7.3 Output Files

**Location:** User-configurable output folder  
**Naming Convention:** `output_[original_filename].txt`  
**Format:** Plain text, UTF-8 encoding

**Example:** `output_report_2024.txt`

**Content Structure:**
```
Document: [filename]
Processed: [timestamp]
Name: [first] [last]
ID: [4 digits]***
[Keyword]: [value] (Page X, Line Y)
[Keyword]: [value] (Page X, Line Y)
...
```

### 7.4 No Logging Files

**Decision:** No persistent log files created  
**Rationale:** Simple tool for end-users, logging adds complexity  
**Alternative:** Errors displayed in UI and included in output file

---

## 8. User Interface Architecture

### 8.1 GUI Framework Structure

**Window Hierarchy:**
```
Root Window (tk.Tk)
├── Header Frame
│   ├── Title Label
│   └── Settings Button
├── Settings Panel Frame (collapsible)
│   ├── Output Path Input
│   ├── Number Format Dropdown
│   └── Proximity Rule Dropdown
├── Main Card Frame
│   ├── File Selection Area
│   ├── Keywords Section
│   │   ├── Input Field
│   │   ├── History Panel
│   │   └── Active Keywords Display
│   ├── Extract Button
│   ├── Progress Bar
│   └── Results Message
└── Footer Frame
```

### 8.2 Layout Strategy

**Primary Layout:** Grid-based positioning  
**Secondary Layout:** Pack within frames for components  
**Responsive:** Window resizable with minimum dimensions enforced

### 8.3 Event Handling

**User Events:**
- File selection (browse/drag-and-drop)
- Keyword input (add/remove)
- Settings changes
- Extract button click
- Results actions (open file/folder)

**System Events:**
- Processing progress updates (from worker thread)
- Completion notification
- Error notification
- Configuration changes

### 8.4 State-Driven UI Updates

**UI reflects state changes:**
- File selected → Show file info, enable keywords
- Keywords added → Enable Extract button
- Processing → Disable inputs, show progress
- Complete → Show results, enable actions
- Error → Show error message, enable retry

### 8.5 Styling Approach

**Constraints:** tkinter has limited native styling  
**Solution:** Custom widget classes with consistent styling

**Style Elements:**
- Color palette constants
- Font objects (predefined sizes and weights)
- Border and padding constants
- Hover state handlers
- Focus indicators

**Alternative Considered:** ttkbootstrap for modern styling (optional enhancement)

---

## 9. Error Handling Strategy

### 9.1 Error Categories

**File Errors:**
- File not found
- Unsupported file type
- Corrupted file
- Permission denied
- File locked by another process

**Processing Errors:**
- Keyword not found (warning, not error)
- Number format ambiguous (warning)
- Personal information missing (warning)
- Parsing failure (error)
- Invalid document structure (error)

**System Errors:**
- Output folder not writable
- Disk space insufficient
- Configuration file corrupted
- Thread communication failure

### 9.2 Error Handling Principles

1. **Graceful Degradation**: Continue processing when possible
2. **User-Friendly Messages**: Avoid technical jargon
3. **Actionable Information**: Tell user what they can do
4. **No Silent Failures**: Always inform user of issues
5. **Partial Success**: Report successful extractions even if some failed

### 9.3 Error Recovery Mechanisms

**Automatic Recovery:**
- Retry file operations once after delay
- Create output folder if missing
- Use default config if file corrupted

**User-Initiated Recovery:**
- "Try Again" button for transient errors
- "Choose Different File" for file errors
- "Select Different Folder" for write errors

### 9.4 Error Logging Strategy

**In-Memory Only:** Errors stored in results object  
**Output to File:** Errors written to output file  
**UI Display:** Error summary shown to user  

**No Persistent Logs:** Reduces complexity for end-users

---

## 10. Security Considerations

### 11.1 Input Validation

**File Selection:**
- Validate file extensions before processing
- Check file exists and is readable
- Prevent directory traversal attacks

**Keyword Input:**
- Sanitize user input for regex injection
- Limit keyword length (max 100 characters)
- Validate characters (alphanumeric + limited punctuation)

**Output Path:**
- Validate path is writable
- Prevent writing to system directories
- Sanitize output filenames

### 11.2 File System Safety

**Output Location:**
- Never overwrite existing files without confirmation
- Create unique filenames if collision detected
- Respect file system permissions

**Configuration:**
- Validate JSON structure before parsing
- Handle corrupted config gracefully
- Never execute code from config

### 11.3 Privacy Considerations

**No Network Communication:** Application is fully offline  
**No Telemetry:** No usage data collected or transmitted  
**Local Processing:** All data stays on user's machine  
**No Clipboard Access:** Except explicit user actions

### 11.4 Threat Model

**In Scope:**
- Malformed input files (fuzzing protection)
- Invalid configuration data
- File system errors

**Out of Scope:**
- Password-protected documents (not supported)
- Encrypted files (not supported)
- Malware scanning (OS responsibility)

---

## 12. Build & Deployment

### 11.1 Development Environment Setup

**Requirements:**
- macOS 10.15+ for development
- Python 3.10 or higher installed
- Virtual environment for dependencies
- Git for version control

**Setup Steps:**
1. Create virtual environment
2. Install requirements via pip
3. Configure IDE (VS Code/PyCharm)
4. Set up testing framework

### 11.2 Build Process

**PyInstaller Configuration:**
- Use `--onefile` flag for single executable
- Include hidden imports explicitly
- Set application icon
- Add version metadata
- Optimize with UPX compression

**Build Platforms:**
- Development builds on macOS (for testing)
- Production builds on Windows or Windows VM (for compatibility)

### 11.3 Distribution Package

**Contents:**
- Single .exe file
- README.txt with instructions
- LICENSE.txt (if applicable)

**Distribution Method:**
- Direct file transfer
- Cloud storage link
- USB drive

**No Installer:** Simple copy-and-run model

---

## 12. Open Technical Questions

### 12.1 Critical Blockers

**Q4 (Number Format):** Which formats must be supported?
- **Impact:** Core extraction algorithm design
- **Affects:** Phase 3 development
- **Required By:** End of Week 2

**Q6 (Keyword Proximity):** How to find associated numbers?
- **Impact:** Extraction algorithm complexity
- **Affects:** Phase 3 development
- **Required By:** End of Week 2

**Q7 (Personal Info Format):** Name and ID patterns?
- **Impact:** Personal information extraction
- **Affects:** Phase 4 development
- **Required By:** End of Week 3

**Q8 (Personal Info Location):** Where in document?
- **Impact:** Search optimization and accuracy
- **Affects:** Phase 4 development
- **Required By:** End of Week 3

**Q17 (Example Documents):** Sample files needed
- **Impact:** Testing and pattern development
- **Affects:** All extraction phases
- **Required By:** Beginning of Week 3

### 12.2 Important Clarifications

**Q9 (Document Templates):** Multiple document types?
- **Impact:** Architecture (single vs. multi-parser)
- **Decision Point:** End of Phase 2

**Q16 (Edge Cases):** Which special cases to support?
- **Impact:** Scope and complexity
- **Decision Point:** During Phase 6 (error handling)

---

**END OF TECHNICAL REQUIREMENTS DOCUMENT**