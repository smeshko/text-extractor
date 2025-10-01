# Complete Guide: Building DocumentExtractor.exe on Windows

## Step 1: Downloads Required

Download these installers on your Windows PC:

1. **Python 3.10 or newer**
   - Go to: https://www.python.org/downloads/windows/
   - Download: "Windows installer (64-bit)" for Python 3.10 or later
   - File will be named like: `python-3.10.X-amd64.exe`

2. **Git for Windows**
   - Go to: https://git-scm.com/download/win
   - Download: "64-bit Git for Windows Setup"
   - File will be named like: `Git-2.XX.X-64-bit.exe`

---

## Step 2: Install Git

1. Run the Git installer (`Git-2.XX.X-64-bit.exe`)
2. Use **default settings** for everything (just keep clicking "Next")
3. Click "Install" and wait for completion
4. Click "Finish"

---

## Step 3: Install Python

1. Run the Python installer (`python-3.10.X-amd64.exe`)
2. **IMPORTANT**: Check the box "Add Python to PATH" at the bottom
3. Click "Install Now"
4. Wait for installation to complete
5. Click "Close"

---

## Step 4: Verify Installation

1. Press `Windows Key + R`
2. Type `cmd` and press Enter (opens Command Prompt)
3. Type these commands to verify:

```bash
python --version
git --version
```

You should see version numbers for both (e.g., "Python 3.10.X" and "git version 2.XX.X")

---

## Step 5: Clone Your Repository

In the Command Prompt:

1. Navigate to where you want the project (e.g., Documents):
```bash
cd %USERPROFILE%\Documents
```

2. Clone your repository:
```bash
git clone https://github.com/YOUR_USERNAME/kris-extractor.git
```

3. Enter the project folder:
```bash
cd kris-extractor
```

---

## Step 6: Create Virtual Environment

In the Command Prompt (still in `kris-extractor` folder):

```bash
python -m venv venv
```

This creates a virtual environment to isolate your project dependencies.

---

## Step 7: Activate Virtual Environment

```bash
venv\Scripts\activate
```

You should see `(venv)` appear at the start of your command line.

---

## Step 8: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages: tkinterdnd2, PyMuPDF, python-docx, PyInstaller, and olefile.

Wait for all packages to finish installing (may take 2-3 minutes).

---

## Step 9: Build the Executable

```bash
pyinstaller build.spec
```

This will:
- Read your `build.spec` configuration
- Collect all dependencies
- Create a single `DocumentExtractor.exe` file
- Takes 2-5 minutes

---

## Step 10: Locate Your Executable

The exe file will be created at:
```
kris-extractor\dist\DocumentExtractor.exe
```

To open the folder in Windows Explorer:
```bash
explorer dist
```

---

## Step 11: Test the Executable

1. Double-click `DocumentExtractor.exe` in the `dist` folder
2. The application should launch without a console window
3. Test basic functionality (drag/drop a document, add keywords, etc.)

---

## Step 12: Distribute the Executable

The `DocumentExtractor.exe` file is standalone and can be:
- Copied to any Windows 10/11 PC
- Shared with others
- No Python installation needed on target machines

---

## Troubleshooting

**If you get "python is not recognized":**
- Python wasn't added to PATH
- Reinstall Python and check "Add Python to PATH"

**If PyInstaller build fails:**
- Make sure you activated the virtual environment (Step 7)
- Try: `pip install --upgrade pyinstaller`

**If exe crashes on launch:**
- Run from Command Prompt to see error messages:
  ```bash
  cd dist
  DocumentExtractor.exe
  ```

**If you need to rebuild:**
- Delete `build` and `dist` folders
- Run `pyinstaller build.spec` again

---

## Quick Reference (After Initial Setup)

For future builds, you only need:

```bash
cd %USERPROFILE%\Documents\kris-extractor
venv\Scripts\activate
git pull
pyinstaller build.spec
```

Your exe will be in the `dist` folder.
