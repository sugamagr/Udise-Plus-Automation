# UDISE+ Student Profile Automation

A Python script that automates filling in student profile fields on the UDISE+ portal (https://sdms.udiseplus.gov.in). Instead of manually opening each student's profile, selecting a dropdown value, saving, and moving to the next student — this script does it all for you across every student in every class.

---

## What Problem Does This Solve?

Schools on UDISE+ often need to set the **same dropdown value** (like Blood Group → "Under Investigation") for **hundreds of students**. Doing this manually means:

- Open student → Select value → Save → Close popup → Go back → Repeat

For a school with **640 students**, this takes **hours** of repetitive clicking. This script does it in minutes.

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
│   ✅ Done. Sit back and watch.                          │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  SCRIPT (automatic)                      │
│                                                         │
│   For each class (VI → VII → VIII → ... → XII):         │
│     For each student in that class:                     │
│       1. Open their General Profile (GP)                │
│       2. Check if the field is already filled           │
│       3. If empty → set the value → Save                │
│       4. Close the success popup                        │
│       5. Go back to student list                        │
│       6. Move to next student                           │
│                                                         │
│   📊 Print progress the whole time                      │
│   📋 Print final summary when done                      │
└─────────────────────────────────────────────────────────┘
```

---

## Step-by-Step Flow

Here's exactly what the script does after you press ENTER:

```
Class VI (10 students)
│
├── Page 1 (students 1-10)
│   ├── Student 1: ANANYA CHAUHAN
│   │   ├── Open GP form
│   │   ├── Blood Group is empty → Set to "Under Investigation"
│   │   ├── Click Save → ✅ "General data updated successfully."
│   │   └── Go back to student list
│   │
│   ├── Student 2: DEEPAK GANGWAR
│   │   ├── Open GP form
│   │   ├── Blood Group already set (A+) → ↩ Skip
│   │   └── Go back to student list
│   │
│   ├── Student 3 ... Student 10 (same process)
│   └── ✅ Class VI done
│
Class VII (68 students)
│
├── Page 1 (students 1-50)
│   ├── Student 1 ... Student 50
│   └── → Click "Next Page"
│
├── Page 2 (students 51-68)
│   ├── Student 51 ... Student 68
│   └── ✅ Class VII done
│
Class VIII ... Class XII (same process)
│
└── 🎉 ALL DONE! Final summary printed.
```

---

## What's In Each File

```
udise-automation/
│
├── run.py              ← The main script. Run this.
├── config.py           ← All settings. Edit this before running.
├── requirements.txt    ← Python dependency (playwright)
├── venv/               ← Python virtual environment (created during setup)
└── README.md           ← This file
```

| File | What It Does |
|------|-------------|
| **run.py** | The brain. Opens browser, waits for login, loops through students, fills fields, saves. |
| **config.py** | All the knobs you can turn — which classes, which field, what value, how fast. |
| **requirements.txt** | Tells Python to install Playwright (the browser automation library). |

---

## How to Run

### First Time Setup (once only)

```bash
cd "/Users/apple/Desktop/Talos QC/udise-automation"
python3 -m venv venv
source venv/bin/activate
pip install playwright
playwright install chromium
```

### Every Time You Want to Run

```bash
cd "/Users/apple/Desktop/Talos QC/udise-automation"
source venv/bin/activate
python -u run.py
```

Then:
1. A Chrome browser window opens → UDISE+ login page
2. **You log in** with your credentials
3. **You select** "Current Academic Year 2026-27"
4. **You reach the dashboard** (the page showing all classes)
5. Go back to the terminal and **press ENTER**
6. Watch the script work through all students

---

## Configuration — What You Can Change

Open `config.py` in any text editor. Here's what each setting controls:

### School Settings

| Setting | What It Means | Current Value |
|---------|--------------|---------------|
| `SCHOOL_ID` | Your school's ID from the UDISE+ URL | `2184637` |
| `CLASSES_TO_PROCESS` | Which classes to process | `[6, 7, 8, 9, 10, 11, 12]` |
| `SECTION_NUM` | Section number (A=1) | `1` |

### What Field to Fill

| Setting | What It Means | Current Value |
|---------|--------------|---------------|
| `FIELD_SELECTOR` | Which dropdown on the form | `#bloodGroup` |
| `FIELD_VALUE` | What value to select | `9` |
| `FIELD_LABEL` | Human-readable name (for logs) | `Under Investigation...` |
| `SKIP_IF_ALREADY_SET` | Skip students who already have a value? | `True` |

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

| Setting | What It Means | Current Value |
|---------|--------------|---------------|
| `PAGE_LOAD_DELAY` | Wait after a page loads | `3 seconds` |
| `SAVE_DELAY` | Wait after clicking Save | `3 seconds` |
| `BETWEEN_STUDENTS_DELAY` | Pause between students | `1 second` |
| `BACK_NAV_DELAY` | Wait after going back to student list | `2 seconds` |
| `LOGIN_WAIT_SECONDS` | How long to wait for you to log in | `120 seconds` |

**Tip:** If UDISE+ is slow, increase the delays. If it's fast, you can decrease them to speed things up.

---

## What the Terminal Output Looks Like

```
============================================================
UDISE+ Student Profile Automation
============================================================
School ID     : 2184637
Classes       : [6, 7, 8, 9, 10, 11, 12]
Field         : #bloodGroup
Value to set  : 9 (Under Investigation - Result will be updated soon)
Skip if set   : True
============================================================

👉  Log in, select Academic Year, and reach the dashboard.
    Then come back here and press ENTER to start...

✅  Starting automation...

============================================================
CLASS 6 — Loading student list
============================================================

  Page 1: students 1–10 of 10

  [1/10] ANANYA CHAUHAN (PEN: 21234567890)
    ✅ Saved → Under Investigation - Result will be updated soon

  [2/10] DEEPAK GANGWAR (PEN: 21345678901)
    ↩ Already set (value=1), skipping

  [3/10] KAVYA SHARMA (PEN: 21456789012)
    ✅ Saved → Under Investigation - Result will be updated soon

  ...

  Class 6 done: {'saved': 8, 'skipped': 2, 'error': 0, 'field_missing': 0}

============================================================
CLASS 7 — Loading student list
============================================================

  Page 1: students 1–50 of 68
  ...
  → Moving to page 2...
  Page 2: students 51–68 of 68
  ...

============================================================
ALL DONE!
============================================================
  Saved       : 580
  Skipped     : 55
  Errors      : 5
  Field N/A   : 0
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
        │  │ Class │ Boys │ Girls │ Total │ Action │    │
        │  │  VI   │   5  │   5   │  10   │  ▶    │    │
        │  │  VII  │  47  │  21   │  68   │  ▶    │    │
        │  │  VIII │  32  │  23   │  55   │  ▶    │    │
        │  │   IX  │  51  │  21   │  72   │  ▶    │    │
        │  │   X   │  64  │  72   │  136  │  ▶    │    │
        │  │  XI   │  83  │  71   │  154  │  ▶    │    │
        │  │  XII  │  78  │  67   │  145  │  ▶    │    │
        │  └──────────────────────────────────────┘    │
        │                                              │
        ▼                                              │
    Student List (per class)                           │
        │                                              │
        │  ┌──────────────────────────────────┐        │
        │  │ PEN        │ Name       │ GP EP FP│        │
        │  │ 2135612... │ AAMAN ALI  │ 🔵 ⚪ ⚪│        │
        │  │ 2157825... │ ABHAY SINGH│ 🔵 ⚪ ⚪│        │
        │  │ ...        │ ...        │ ...    │        │
        │  └──────────────────────────────────┘        │
        │       │                                      │
        │       │ Click GP                             │
        │       ▼                                      │
        │   General Profile Form                       │
        │       │                                      │
        │       │  ┌─────────────────────────┐         │
        │       │  │ Name: AAMAN ALI         │         │
        │       │  │ DOB: ...                │         │
        │       │  │ Blood Group: [▼ Select] │ ◄── Script fills this
        │       │  │ ...                     │         │
        │       │  │    [ Save ]             │ ◄── Script clicks this
        │       │  └─────────────────────────┘         │
        │       │           │                          │
        │       │           ▼                          │
        │       │   ┌──────────────────┐               │
        │       │   │ ✅ Saved!        │               │
        │       │   │    [ OK ]        │ ◄── Script closes this
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

Edit `config.py`:
```python
CLASSES_TO_PROCESS = [10, 12]
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

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Browser doesn't open | Make sure you ran `playwright install chromium` |
| Script says "No students found" | The page might be slow. Increase `PAGE_LOAD_DELAY` to 5 or more |
| Script errors on a student | It skips that student and continues. Check the error message in the terminal |
| Session expired mid-run | UDISE+ sessions timeout. Re-run the script and log in again |
| Want to stop the script | Press `Ctrl+C` in the terminal. Nothing bad happens — it just stops |

---

## Technical Details

- **Language:** Python 3
- **Browser automation:** Playwright (controls a real Chrome browser)
- **How it fills dropdowns:** Sets the `<select>` element's value via JavaScript and triggers a `change` event
- **How it detects success:** Looks for the SweetAlert2 popup saying "General data updated successfully."
- **Pagination:** UDISE+ shows 50 students per page (fixed). The script clicks "Next page" automatically
- **URL pattern for student list:** `https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/viewStudentDetails/cy/{CLASS_NUM}`
- **URL pattern for GP form:** `https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION}/{STUDENT_ID}?formId=1&formEditFlag=1`
