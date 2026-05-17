# UDISE+ Student Profile Automation

A Python script that automates filling in student profile fields on the UDISE+ portal (https://sdms.udiseplus.gov.in). Instead of manually opening each student's profile, selecting a dropdown value, saving, and moving to the next student — this script does it all for you across every student in every class.

---

## What Problem Does This Solve?

Schools on UDISE+ often need to set the **same dropdown value** (like Blood Group → "Under Investigation") for **hundreds of students**. Doing this manually means:

- Open student → Select value → Save → Close popup → Go back → Repeat

For a school with **760 students**, this takes **hours** of repetitive clicking. This script does it in minutes.

---

## How It Works — The Big Picture

```
┌─────────────────────────────────────────────────────────┐
│                    YOU (one-time)                        │
│                                                         │
│   1. Open terminal                                      │
│   2. Run the script                                     │
│   3. Log into UDISE+ in the browser that opens          │
│   4. Select Academic Year                               │
│   5. Press ENTER in the terminal                        │
│                                                         │
│   Done. Sit back and watch.                             │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  SCRIPT (automatic)                      │
│                                                         │
│   1. Auto-detects your School ID from the URL           │
│   2. For each class (Nursery → LKG → ... → XII):       │
│     For each student in that class:                     │
│       a. Check GP button color (green = done, skip)     │
│       b. Open their General Profile (GP)                │
│       c. Check if the field is already filled           │
│       d. If empty → set the value → Save                │
│       e. Close the success popup                        │
│       f. Go back to student list                        │
│       g. Move to next student                           │
│                                                         │
│   3. Print progress the whole time                      │
│   4. Generate markdown reports per class + summary      │
└─────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Flow

Here's exactly what the script does after you press ENTER:

```
Class Nursery (21 students)
│
├── Page 1 (students 1-21)
│   ├── Student 1: AARAV SHARMA [GP 🔴]
│   │   ├── Open GP form
│   │   ├── Blood Group is empty → Set to "Under Investigation"
│   │   ├── Click Save → "General data updated successfully."
│   │   └── Go back to student list
│   │
│   ├── Student 2: ANANYA VERMA [GP ✅]
│   │   └── GP already green → Skip (no click needed)
│   │
│   ├── Student 3 ... Student 21 (same process)
│   └── Class Nursery done
│
Class LKG (52 students)
│
├── Page 1 (students 1-50)
│   ├── Student 1 ... Student 50
│   └── → Click "Next Page"
│
├── Page 2 (students 51-52)
│   ├── Student 51 ... Student 52
│   └── Class LKG done
│
Class UKG ... Class XII (same process)
│
└── ALL DONE! Summary report generated.
```

---

## What's In Each File

```
Udise-Plus-Automation/
│
├── run.py              ← The main script. Run this.
├── config.py           ← All settings. Edit this before running.
├── requirements.txt    ← Python dependency (playwright)
├── CONTEXT.md          ← Full technical reference (for developers/AI)
├── README.md           ← This file
├── .gitignore
├── venv/               ← Python virtual environment (created during setup)
└── reports/            ← Auto-generated after each run
    └── 2025-06-15_14-30-00/
        ├── summary.md
        ├── class_Nursery_KG_PP3.md
        ├── class_LKG_KG1_PP2.md
        ├── class_VI.md
        └── ...
```

| File | What It Does |
|------|-------------|
| **run.py** | The brain. Opens browser, waits for login, loops through students, fills fields, saves, generates reports. |
| **config.py** | All the knobs you can turn — which classes, which field, what value, skip logic, speed. |
| **requirements.txt** | Tells Python to install Playwright (the browser automation library). |
| **CONTEXT.md** | Complete technical deep-dive for developers or AI extending the script (1100+ lines). |

---

## How to Run

### First Time Setup (once only)

**Mac / Linux:**
```bash
git clone https://github.com/sugamagr/Udise-Plus-Automation.git
cd Udise-Plus-Automation
python3 -m venv venv
source venv/bin/activate
pip install playwright
playwright install chromium
```

**Windows (Command Prompt):**
```cmd
git clone https://github.com/sugamagr/Udise-Plus-Automation.git
cd Udise-Plus-Automation
python -m venv venv
venv\Scripts\activate
pip install playwright
playwright install chromium
```

**Windows (PowerShell):**
```powershell
git clone https://github.com/sugamagr/Udise-Plus-Automation.git
cd Udise-Plus-Automation
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install playwright
playwright install chromium
```

---

### Running the Script

#### Process all classes (from config.py)

**Mac / Linux:**
```bash
cd Udise-Plus-Automation
source venv/bin/activate
python -u run.py
```

**Windows (Command Prompt):**
```cmd
cd Udise-Plus-Automation
venv\Scripts\activate
python -u run.py
```

**Windows (PowerShell):**
```powershell
cd Udise-Plus-Automation
.\venv\Scripts\Activate.ps1
python -u run.py
```

> The `-u` flag ensures output appears in real-time (not buffered).

---

#### Process specific classes only (`--classes`)

```bash
# Standard classes (VI, X, XII)
python -u run.py --classes 6 10 12

# Pre-primary classes (Nursery, LKG, UKG)
python -u run.py --classes -3 -2 -1

# Mix of pre-primary and regular
python -u run.py --classes -3 -2 -1 1 2 3 4 5 6

# Just one class
python -u run.py --classes 7
```

#### Auto-detect all classes from portal (`--classes auto`)

```bash
python -u run.py --classes auto
```

This navigates to the student list page, reads the class dropdown, and processes every class available for your school. No need to know which classes exist beforehand.

---

### What Happens When You Run

1. A Chrome browser window opens → UDISE+ login page
2. **You log in** with your credentials (UDISE code, username, password, captcha)
3. **You select** "Current Academic Year 2026-27"
4. **You reach the dashboard** (the page showing all classes)
5. Go back to the terminal and **press ENTER**
6. Watch the script work through all students

---

## Class Number Reference

UDISE+ uses these numbers in URLs. Pre-primary classes use **negative** numbers.

| Class | Number | Notes |
|-------|--------|-------|
| Nursery/KG/PP3 | **-3** | Pre-primary |
| LKG/KG1/PP2 | **-2** | Pre-primary |
| UKG/KG2/PP1 | **-1** | Pre-primary |
| I | 1 | |
| II | 2 | |
| III | 3 | |
| IV | 4 | |
| V | 5 | |
| VI | 6 | |
| VII | 7 | |
| VIII | 8 | |
| IX | 9 | |
| X | 10 | |
| XI | 11 | |
| XII | 12 | |

> **Note:** There is no Class 0. Not all schools have all classes. Use `--classes auto` to detect automatically.

---

## Configuration — What You Can Change

Open `config.py` in any text editor. Here's what each setting controls:

### School Settings

| Setting | What It Means | Default |
|---------|--------------|---------|
| `CLASSES_TO_PROCESS` | Which classes to process | `[6, 7, 8, 9, 10, 11, 12]` |
| `SECTION_NUM` | Section number (A=1, B=2) | `1` |

> **School ID** is auto-detected from the URL after you log in — you don't set it in config.

### What Field to Fill

| Setting | What It Means | Default |
|---------|--------------|---------|
| `FIELD_SELECTOR` | CSS selector of the dropdown | `#bloodGroup` |
| `FIELD_VALUE` | Option value to select | `9` |
| `FIELD_LABEL` | Human-readable name (for logs) | `Under Investigation...` |

### Skip Logic

| Setting | What It Means | Default |
|---------|--------------|---------|
| `SKIP_IF_ALREADY_SET` | Skip students whose field already has a value? | `True` |
| `ALWAYS_SAVE` | Click Save even on students with pre-filled value (marks profile complete) | `True` |
| `ONLY_INCOMPLETE` | Skip students whose GP button is green (already done) | `True` |

**How skip logic works together:**

| ONLY_INCOMPLETE | SKIP_IF_ALREADY_SET | ALWAYS_SAVE | Behavior |
|:-:|:-:|:-:|---|
| True | True | True | **Fastest.** Skip green GP. For red GP: if field empty → set + save. If field set → save anyway. |
| True | True | False | Skip green GP. For red GP: if field empty → set + save. If field set → skip entirely. |
| False | True | True | Check every student. If field empty → set + save. If field set → save anyway. |
| False | False | — | Set value on ALL students regardless of current value. |

### Blood Group Value Reference

```
Value    Meaning
─────    ──────────────────────────────────────────────
  1      A+
  2      A-
  3      B+
  4      B-
  5      O+
  6      O-
  7      AB+
  8      AB-
  9      Under Investigation - Result will be updated soon
```

### Speed Settings

| Setting | What It Means | Default |
|---------|--------------|---------|
| `PAGE_LOAD_DELAY` | Wait after a page loads | `3 seconds` |
| `SAVE_DELAY` | Wait after clicking Save | `3 seconds` |
| `BETWEEN_STUDENTS_DELAY` | Pause between students | `1 second` |
| `BACK_NAV_DELAY` | Wait after going back to student list | `2 seconds` |

> **Tip:** If UDISE+ is slow, increase the delays. If it's fast, decrease them.

---

## Reports

The script auto-generates markdown reports after each run in the `reports/` folder.

### Folder Structure

```
reports/
└── 2025-06-15_14-30-00/          ← timestamp of run
    ├── summary.md                 ← overall totals + per-class table
    ├── class_Nursery_KG_PP3.md   ← every student in Nursery
    ├── class_LKG_KG1_PP2.md     ← every student in LKG
    ├── class_VI.md               ← every student in Class VI
    ├── class_VII.md
    └── ...
```

### Summary Report (`summary.md`)

Contains:

| Section | What's In It |
|---------|-------------|
| **Overall Totals** | Total students processed, Updated, Skipped, GP Already Done, Errors, Field Not Found |
| **Per-Class Breakdown** | Table with one row per class showing Students, Updated, Skipped, GP Done, Errors + link to class report |
| **All Errors** | Combined error list across all classes (if any) |

Example:

```markdown
## Overall Totals

| Metric | Count |
|--------|-------|
| Total Students Processed | 760 |
| Updated | 423 |
| Skipped (already set) | 12 |
| GP Already Done | 318 |
| Errors | 7 |

## Per-Class Breakdown

| Class | Students | Updated | Skipped | GP Done | Errors | Report |
|-------|----------|---------|---------|---------|--------|--------|
| Nursery/KG/PP3 | 21 | 15 | 0 | 6 | 0 | class_Nursery_KG_PP3.md |
| LKG/KG1/PP2 | 52 | 38 | 2 | 11 | 1 | class_LKG_KG1_PP2.md |
| ... | ... | ... | ... | ... | ... | ... |
```

### Class Report (`class_VI.md`)

Contains:

| Section | What's In It |
|---------|-------------|
| **Summary** | Total, Updated, Skipped, GP Already Done, Errors for that class |
| **Student Details** | Table with every student: #, Name, PEN, Gender, Action, Previous Value, New Value |
| **Errors** | Any errors for students in that class |

Example:

```markdown
| # | Student Name | PEN | Gender | Action | Previous Value | New Value |
|---|-------------|-----|--------|--------|----------------|-----------|
| 1 | ANANYA CHAUHAN | 2123456 | Female | Updated | Empty | Under Investigation... |
| 2 | DEEPAK GANGWAR | 2134567 | Male | Skipped | A+ (kept) | A+ (kept) |
| 3 | KAVYA SHARMA | 2145678 | Female | GP Done | — | — |
```

**Action values:**
- **Updated** — Field was empty, value set and saved
- **Skipped** — Field already had a value, no change
- **GP Done** — GP button was green (already complete), no click needed
- **Field N/A** — Field selector not found on the form
- **Error** — Something went wrong (see Errors section)

---

## What the Terminal Output Looks Like

```
============================================================
UDISE+ Student Profile Automation
============================================================
Classes       : ['Nursery/KG/PP3', 'LKG/KG1/PP2', ..., 'VIII']
Field         : #bloodGroup
Value to set  : 9 (Under Investigation - Result will be updated soon)
Skip if set   : True
============================================================

  Current URL: https://sdms.udiseplus.gov.in/g1/#/school/2107557/schoolDashboard/cy
  JS URL:      https://sdms.udiseplus.gov.in/g1/#/school/2107557/schoolDashboard/cy
  School ID   : 2107557

  Starting automation...

============================================================
CLASS Nursery/KG/PP3 (num=-3) — Loading student list
============================================================

  Page 1: students 1–21 of 21

  [1/21] AARAV SHARMA (PEN: 21234567890) [GP 🔴]
    → Set Empty → Under Investigation - Result will be updated soon
    Saved

  [2/21] ANANYA VERMA (PEN: 21345678901) [GP ✅]
    ↩ GP already green, skipping

  [3/21] DEEPAK GANGWAR (PEN: 21456789012) [GP 🔴]
    → Keeping existing value (A+), saving anyway
    Saved

  ...

  Class Nursery/KG/PP3 done: {'saved': 15, 'skipped': 0, 'gp_done': 6, 'error': 0}
  Report saved: reports/2025-06-15_14-30-00/class_Nursery_KG_PP3.md

============================================================
CLASS LKG/KG1/PP2 (num=-2) — Loading student list
============================================================
  ...

============================================================
ALL DONE!
============================================================
  Saved       : 423
  Skipped     : 12
  GP Done     : 318
  Errors      : 7
  Field N/A   : 0
  Reports     : reports/2025-06-15_14-30-00
============================================================

Press Enter to close the browser...
```

---

## How the Script Navigates UDISE+

```
                    UDISE+ Website Structure
                    ════════════════════════

    Login Page
        │
        ▼
    Academic Year Selection
        │
        ▼
    School Dashboard ──────────────────────────────────┐
        │                                              │
        │  Shows all classes:                          │
        │  ┌──────────────────────────────────────┐    │
        │  │ Class   │ Boys │ Girls │ Total │      │    │
        │  │ Nursery │  12  │   9   │  21   │  ▶  │    │
        │  │ LKG     │  30  │  22   │  52   │  ▶  │    │
        │  │ ...     │ ...  │  ...  │  ...  │  ▶  │    │
        │  │ XII     │  78  │  67   │  145  │  ▶  │    │
        │  └──────────────────────────────────────┘    │
        │                                              │
        ▼                                              │
    Student List (per class)                           │
        │                                              │
        │  ┌────────────────────────────────────┐      │
        │  │ PEN       │ Name       │ GP  EP  FP│      │
        │  │ 2135612.. │ AARAV      │ 🔴  ⚪  ⚪│      │
        │  │ 2157825.. │ ANANYA     │ 🟢  ⚪  ⚪│      │
        │  │ ...       │ ...        │ ...       │      │
        │  └────────────────────────────────────┘      │
        │       │                                      │
        │       │ Click GP (red button)                │
        │       ▼                                      │
        │   General Profile Form                       │
        │       │                                      │
        │       │  ┌─────────────────────────┐         │
        │       │  │ Name: AARAV             │         │
        │       │  │ DOB: ...                │         │
        │       │  │ Blood Group: [▼ Select] │ ← Script fills this
        │       │  │ ...                     │         │
        │       │  │    [ Save ]             │ ← Script clicks this
        │       │  └─────────────────────────┘         │
        │       │           │                          │
        │       │           ▼                          │
        │       │   ┌──────────────────┐               │
        │       │   │  Saved!          │               │
        │       │   │    [ OK ]        │ ← Script closes this
        │       │   └──────────────────┘               │
        │       │           │                          │
        │       │      Go Back                         │
        │       ▼                                      │
        │   Student List (next student)                │
        │       │                                      │
        │       ▼ ... repeat for all students ...      │
        │                                              │
        └──────────── next class ──────────────────────┘
```

---

## Common Scenarios

### "I only want to run it for Class X and XII"

**Option 1 — Command line (recommended):**
```bash
python -u run.py --classes 10 12
```

**Option 2 — Edit config.py:**
```python
CLASSES_TO_PROCESS = [10, 12]
```

### "I want to process Nursery, LKG, UKG only"

```bash
python -u run.py --classes -3 -2 -1
```

### "I don't know which classes my school has"

```bash
python -u run.py --classes auto
```

### "I want to set Blood Group to B+ instead"

Edit `config.py`:
```python
FIELD_VALUE = "3"
FIELD_LABEL = "B+"
```

### "The site is very slow today"

Edit `config.py`:
```python
PAGE_LOAD_DELAY = 5
SAVE_DELAY = 5
BACK_NAV_DELAY = 4
```

### "I want to re-run and overwrite existing values"

Edit `config.py`:
```python
SKIP_IF_ALREADY_SET = False
```

### "I want to skip students whose GP is already green (saved)"

This is ON by default. In `config.py`:
```python
ONLY_INCOMPLETE = True   # Already the default
```

### "I want to save every student (even if field is already set) to mark profiles complete"

This is ON by default. In `config.py`:
```python
ALWAYS_SAVE = True       # Already the default
```

---

## All Commands — Quick Reference

### Mac / Linux

| What | Command |
|------|---------|
| **First-time setup** | `python3 -m venv venv && source venv/bin/activate && pip install playwright && playwright install chromium` |
| **Activate venv** | `source venv/bin/activate` |
| **Run (all classes)** | `python -u run.py` |
| **Run (specific classes)** | `python -u run.py --classes 6 10 12` |
| **Run (pre-primary)** | `python -u run.py --classes -3 -2 -1` |
| **Run (auto-detect)** | `python -u run.py --classes auto` |
| **Stop script** | `Ctrl+C` |

### Windows (Command Prompt)

| What | Command |
|------|---------|
| **First-time setup** | `python -m venv venv && venv\Scripts\activate && pip install playwright && playwright install chromium` |
| **Activate venv** | `venv\Scripts\activate` |
| **Run (all classes)** | `python -u run.py` |
| **Run (specific classes)** | `python -u run.py --classes 6 10 12` |
| **Run (pre-primary)** | `python -u run.py --classes -3 -2 -1` |
| **Run (auto-detect)** | `python -u run.py --classes auto` |
| **Stop script** | `Ctrl+C` |

### Windows (PowerShell)

| What | Command |
|------|---------|
| **First-time setup** | `python -m venv venv; .\venv\Scripts\Activate.ps1; pip install playwright; playwright install chromium` |
| **Activate venv** | `.\venv\Scripts\Activate.ps1` |
| **Run (all classes)** | `python -u run.py` |
| **Run (specific classes)** | `python -u run.py --classes 6 10 12` |
| **Run (pre-primary)** | `python -u run.py --classes -- -3 -2 -1` |
| **Run (auto-detect)** | `python -u run.py --classes auto` |
| **Stop script** | `Ctrl+C` |

> **PowerShell note:** For negative class numbers, use `--` before the numbers so PowerShell doesn't misinterpret them: `python -u run.py --classes -- -3 -2 -1`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Browser doesn't open | Make sure you ran `playwright install chromium` |
| `command not found: playwright` | Activate your venv first: `source venv/bin/activate` (Mac) or `venv\Scripts\activate` (Windows) |
| Script says "No students found" | The page might be slow. Increase `PAGE_LOAD_DELAY` to 5 or more |
| Script errors on a student | It skips that student and continues. Check the error message in the terminal |
| Session expired mid-run | UDISE+ sessions timeout after inactivity. Re-run the script and log in again |
| "Could not detect School ID" | Make sure you're on the School Dashboard before pressing ENTER. The URL should contain `/school/XXXX/` |
| Want to stop the script | Press `Ctrl+C` in the terminal. Nothing bad happens — it just stops |
| Table doesn't reload after going back | The script handles this automatically — re-navigates and re-paginates |
| Wrong class data showing | The script uses `about:blank` navigation to avoid Angular caching issues |
| Captcha/login issues | The script cannot automate login (captcha). You must log in manually each time |
| PowerShell won't activate venv | Run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` first |

---

## Technical Details

- **Language:** Python 3
- **Browser automation:** Playwright (controls a real Chrome browser)
- **Mode:** Headed (you can see the browser) with `slow_mo=200` for stability
- **School ID:** Auto-detected from URL after login (regex: `/school/(\d+)/`)
- **Class detection:** Auto-detect available classes from portal dropdown (`--classes auto`)
- **How it fills dropdowns:** Sets the `<select>` element's value via JavaScript and triggers a `change` event (required for Angular to detect the change)
- **How it detects success:** Waits for SweetAlert2 popup containing "successfully"
- **How it checks completion:** GP button CSS class — `submit` = green (done), `incomplete` = red (needs work)
- **Pagination:** UDISE+ shows 50 students per page (fixed). Script clicks "Next page" automatically
- **Navigation:** Uses `about:blank` → target URL pattern to force full page reload (avoids Angular hash routing bug)
- **Reports:** Markdown files generated per class + summary, timestamped folders
- **URL pattern for student list:** `https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/viewStudentDetails/cy/{CLASS_NUM}`
- **URL pattern for GP form:** `https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION}/{STUDENT_ID}?formId=1&formEditFlag=1`
