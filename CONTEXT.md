# UDISE+ Portal — Complete Technical Context for AI Automation

> **Purpose:** This file contains everything an AI model needs to understand the UDISE+ portal, its navigation, DOM structure, selectors, quirks, and the existing automation script — so it can extend the script for EP (Enrolment Profile), FP (Facility Profile), or any other section without needing to rediscover anything.

> **How this was built:** Every detail here was discovered interactively using Playwright MCP on a live UDISE+ session in June 2025. Nothing is assumed — every selector, URL, behavior was tested and confirmed on the real portal.

---

## Table of Contents

1. [Portal Overview](#1-portal-overview)
2. [Authentication & Session](#2-authentication--session)
3. [URL Structure & Routing](#3-url-structure--routing)
4. [School Dashboard](#4-school-dashboard)
5. [Student List Page](#5-student-list-page)
6. [Student Profile Tabs (GP / EP / FP)](#6-student-profile-tabs-gp--ep--fp)
7. [General Profile (GP) — Fully Mapped](#7-general-profile-gp--fully-mapped)
8. [Enrolment Profile (EP) — To Be Mapped](#8-enrolment-profile-ep--to-be-mapped)
9. [Facility Profile (FP) — To Be Mapped](#9-facility-profile-fp--to-be-mapped)
10. [SweetAlert2 Popups](#10-sweetalert2-popups)
11. [Angular SPA Quirks](#11-angular-spa-quirks)
12. [Navigation Patterns That Work](#12-navigation-patterns-that-work)
13. [Navigation Patterns That DON'T Work](#13-navigation-patterns-that-dont-work)
14. [GP/EP/FP Button Color System](#14-gpepfp-button-color-system)
15. [Pagination System](#15-pagination-system)
16. [Existing Script Architecture](#16-existing-script-architecture)
17. [Config Reference](#17-config-reference)
18. [Known Portal Behaviors & Edge Cases](#18-known-portal-behaviors--edge-cases)
19. [How to Extend for EP/FP](#19-how-to-extend-for-epfp)
20. [School-Specific Data (Test School)](#20-school-specific-data-test-school)

---

## 1. Portal Overview

- **Full Name:** Unified District Information System for Education Plus (UDISE+)
- **URL:** https://sdms.udiseplus.gov.in
- **Purpose:** National school management system. Schools enter student data (demographics, enrollment, facilities) yearly.
- **Frontend Framework:** Angular SPA (hash-based routing `#/...`)
- **Backend:** REST API (JSON payloads over HTTPS)
- **UI Library:** Angular Material (`mat-*` components — tables, paginators, dialogs, dropdowns)
- **Popup Library:** SweetAlert2 (`.swal2-*` classes) for success/error/confirmation dialogs
- **User Roles:** School User (one per school), Block/District/State admins
- **Academic Year:** 2026-27 (current as of June 2025 session)

---

## 2. Authentication & Session

### Login
- **Login URL:** `https://sdms.udiseplus.gov.in/p1/v1/login`
- Login form has UDISE Code, Username, Password, Captcha
- **Captcha:** Visual captcha that changes each time — cannot be automated
- **Approach:** User logs in manually, script takes over after

### Post-Login Flow
1. Login → lands on **Academic Year Selection** page
2. User clicks "Current Academic Year 2026-27" card
3. → Redirects to School Dashboard: `https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/schoolDashboard/cy`
4. Two popups may appear on dashboard load:
   - Transition notification popup
   - School information dialog
   - Both can be dismissed by clicking close buttons

### Session Behavior
- Sessions expire after inactivity (exact timeout unknown, estimated 15-30 min)
- When session expires, any navigation redirects to login page
- The script should detect this (check if URL contains `/login`) and prompt user to re-login

### School ID
- Embedded in every URL: `/school/{SCHOOL_ID}/...`
- Auto-detectable from URL regex: `/school/(\d+)/`
- The ID is internal to UDISE+ (NOT the UDISE code itself)
- Example: UDISE Code `09220905204` → Internal School ID `2184637`

---

## 3. URL Structure & Routing

### Base URLs
```
Login:         https://sdms.udiseplus.gov.in/p1/v1/login
App Root:      https://sdms.udiseplus.gov.in/g1/#/
School Root:   https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/
```

### Key Route Patterns
```
Dashboard:     /school/{SCHOOL_ID}/schoolDashboard/cy
Student List:  /school/{SCHOOL_ID}/viewStudentDetails/cy/{CLASS_NUM}
Student GP:    /school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=1&formEditFlag=1
Student EP:    /school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=2&formEditFlag=1
Student FP:    /school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=3&formEditFlag=1
Profile Preview: /school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=4&formEditFlag=1
Academic Year: /academic-choice
```

### Class Number Mapping
**Pre-primary classes use negative numbers. There is no Class 0.**

| Class | URL Number | Notes |
|-------|-----------|-------|
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

Not all schools have all classes. Use `--classes auto` or `detect_classes(page)` to discover
which classes are available for a given school.

### Section Number
- Section "All" = `-1`
- Section A = `1` (default, most schools have only one section)
- Section B = `2`, etc.
- Some schools (e.g., primary schools) have multiple sections per class

### Student ID
- Each student has a unique numeric ID used in URLs
- The ID is NOT the PEN (Permanent Education Number)
- Extracted from the GP/EP/FP button's link or the row click handler

---

## 4. School Dashboard

### URL
```
https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/schoolDashboard/cy
```

### Layout
- Shows a table/accordion of all classes with columns: Class, Boys, Girls, Total, Incomplete count
- Each class row is clickable → expands to show sections (e.g., "Section A") with a **View/Manage** button
- View/Manage → navigates to student list for that class

### Left Sidebar Menu (observed items)
- School Dashboard
- School Details
- Student Release Request Management
- Student Name Update
- List of All Students
- APAAR Module
- AADHAAR MBU Module
- Class/Section Shift
- Student Movement and Progression
- Reporting Module
- School Certification

### Dashboard Popups on Load
- Transition notification popup — dismiss via close button
- School information dialog — dismiss via close button
- These appear inconsistently (sometimes both, sometimes neither)

---

## 5. Student List Page

### URL
```
https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/viewStudentDetails/cy/{CLASS_NUM}
```

### Table Structure
```html
<table>
  <thead>
    <tr>
      <th>Class/Grade</th>    <!-- cells[0] -->
      <th>PEN</th>            <!-- cells[1] -->
      <th>Student Name</th>    <!-- cells[2] -->
      <th>Gender</th>          <!-- cells[3] -->
      <th>DOB</th>             <!-- cells[4] -->
      <th>Entry Status</th>    <!-- cells[5] — shows "In-Progress" or "Complete" for ALL forms combined -->
      <th>Last Updated</th>    <!-- cells[6] -->
      <th>Action</th>          <!-- cells[7] or last cell — contains GP / EP / FP buttons -->
    </tr>
  </thead>
  <tbody>
    <tr>...</tr>  <!-- one row per student -->
  </tbody>
</table>
```

### Cell Index Reference
| Index | Column | Example Value |
|-------|--------|---------------|
| 0 | Class/Grade | "VII-A" |
| 1 | PEN | "21356122578" |
| 2 | Student Name | "AAMAN ALI" |
| 3 | Gender | "Male" |
| 4 | DOB | "15/03/2012" |
| 5 | Entry Status | "In-Progress" (combined GP+EP+FP status) |
| 6 | Last Updated | "2025-06-15" |
| 7+ | Action | GP EP FP buttons (clickable `<a>` tags) |

### Dropdowns/Filters on Student List
- **Class dropdown:** combobox at top, options: VI, VII, VIII, IX, X, XI, XII
- **Section dropdown:** combobox, options: All, A (or A, B, etc. for multi-section schools)
- **Search bar:** text input for filtering by student name/PEN
- Changing the class dropdown reloads the student list (but doesn't change URL — Angular routing issue)

### GP/EP/FP Buttons (Action Column)
Located in the **last cell** of each row. Each is an `<a>` tag:

```html
<!-- Green (complete) -->
<a class="submit" style="background-color: rgb(28, 171, 130);">GP</a>

<!-- Red (incomplete) -->
<a class="incomplete" style="background-color: rgb(244, 134, 134);">GP</a>
```

**Important:** The Entry Status column (cells[5]) shows combined status for ALL three forms. To check individual GP/EP/FP completion, you MUST check the button color/class.

---

## 6. Student Profile Tabs (GP / EP / FP)

### Tab System
When you click GP/EP/FP, you land on a form page with **4 tabs**:

| Tab # | formId | Name | What It Contains |
|-------|--------|------|-----------------|
| 1 | 1 | General Profile (GP) | Demographics: name, DOB, gender, blood group, aadhaar, address, etc. |
| 2 | 2 | Enrolment Profile (EP) | Academic: stream, medium of instruction, subjects, previous year details |
| 3 | 3 | Facility Profile (FP) | Facilities: transport, scholarship, disability, etc. |
| 4 | 4 | Profile Preview | Read-only summary of all 3 profiles |

### URL Pattern
```
https://sdms.udiseplus.gov.in/g1/#/school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId={TAB_NUM}&formEditFlag=1
```

### Tab Navigation
- Clicking a tab changes `formId` in the URL
- The **"Next"** button at the bottom of each form moves to the NEXT TAB (not next student!)
  - GP → Next → lands on EP (formId=2)
  - EP → Next → lands on FP (formId=3)
- There is a **"Save"** button on each tab that saves ONLY that tab's data
- **"Back"** browser navigation (`page.go_back()`) returns to the student list

### How to Navigate Directly to EP or FP
Use the URL with the appropriate `formId`:
```
EP: ?formId=2&formEditFlag=1
FP: ?formId=3&formEditFlag=1
```

Or from the student list, click the EP or FP button directly (instead of GP).

---

## 7. General Profile (GP) — Fully Mapped

### URL
```
/school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=1&formEditFlag=1
```

### Key Fields Discovered

#### Blood Group (`#bloodGroup`)
- Element: `<select id="bloodGroup">`
- Type: Native HTML `<select>` dropdown (NOT Angular Material select)
- Options:

| Value | Label |
|-------|-------|
| `""` | Select (disabled, empty default) |
| `"1"` | A+ |
| `"2"` | A- |
| `"3"` | B+ |
| `"4"` | B- |
| `"5"` | O+ |
| `"6"` | O- |
| `"7"` | AB+ |
| `"8"` | AB- |
| `"9"` | Under Investigation - Result will be updated soon |

#### How to Set a `<select>` Value via JavaScript
```javascript
const el = document.querySelector('#bloodGroup');
el.value = '9';
el.dispatchEvent(new Event('change', { bubbles: true }));
```
The `change` event dispatch is **critical** — without it, Angular doesn't detect the value change and the form stays "pristine" (Save might not persist).

### Save Button
```javascript
const btn = [...document.querySelectorAll('button')].find(
    b => b.textContent.includes('Save')
);
btn.click();
```
- There's no unique ID/class on the Save button — found by text content matching
- After clicking Save, a SweetAlert2 popup appears (see section 10)

### Other Fields on GP (observed but not mapped in detail)
- Student Name (read-only)
- Father's Name, Mother's Name
- Date of Birth
- Gender
- Aadhaar Number
- Address fields
- Religion, Category, Caste
- Disability status
- Mother Tongue
- Many more dropdowns and text fields

> **To map EP/FP fields:** Use Playwright MCP to take a snapshot of the EP/FP form pages. Run `document.querySelectorAll('select, input, textarea')` to get all form fields with their IDs and types.

---

## 8. Enrolment Profile (EP) — To Be Mapped

### URL
```
/school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=2&formEditFlag=1
```

### What's Known
- Accessed via `formId=2` in URL or by clicking "EP" button on student list
- EP button color system works same as GP (green=complete, red=incomplete)
- Has its own Save button (same text-matching approach should work)
- Has its own SweetAlert2 success popup

### Fields to Discover
Use this JavaScript in Playwright MCP to discover all form fields on the EP page:
```javascript
async (page) => {
    const fields = await page.evaluate(() => {
        const selects = [...document.querySelectorAll('select')].map(el => ({
            tag: 'select',
            id: el.id,
            name: el.name,
            options: [...el.options].map(o => ({ value: o.value, text: o.text }))
        }));
        const inputs = [...document.querySelectorAll('input:not([type=hidden])')].map(el => ({
            tag: 'input',
            type: el.type,
            id: el.id,
            name: el.name,
            value: el.value
        }));
        return { selects, inputs };
    });
    return JSON.stringify(fields, null, 2);
}
```

---

## 9. Facility Profile (FP) — To Be Mapped

### URL
```
/school/{SCHOOL_ID}/new-ac/{CLASS_NUM}/{SECTION_NUM}/{STUDENT_ID}?formId=3&formEditFlag=1
```

### What's Known
- Same structure as GP/EP — form with fields + Save button
- FP button color in student list: same green/red system
- Access via `formId=3` or clicking "FP" button

### Discovery Approach
Same as EP — navigate to the FP page and run the field discovery JavaScript.

---

## 10. SweetAlert2 Popups

UDISE+ uses **SweetAlert2** for all success/error/confirmation dialogs.

### Success Popup (after Save)
```
Title/Text: "General data updated successfully."
           (or "Enrolment data updated successfully." for EP, etc.)
```

### Key Selectors
| Element | Selector | Purpose |
|---------|----------|---------|
| Popup container | `.swal2-popup` | The popup box itself |
| Title | `.swal2-title` | Heading text |
| HTML content | `.swal2-html-container` or `#swal2-html-container` | Body text |
| Close button (X) | `.swal2-close` | Top-right X button |
| Confirm button (OK) | `button.swal2-confirm` | Blue OK button |
| Cancel button | `button.swal2-cancel` | Cancel button (if shown) |

### How to Detect and Close
```javascript
// Wait for popup
const text = document.querySelector('.swal2-title, .swal2-html-container, #swal2-html-container');
if (text && text.textContent.includes('successfully')) {
    document.querySelector('.swal2-close').click();
}
```

### Popup Types Observed
1. **Save success:** "General data updated successfully." → just close it
2. **Validation error:** Shows field-specific error messages → close and log
3. **Confirmation dialog:** "Are you sure?" with OK/Cancel → not observed in normal GP flow

---

## 11. Angular SPA Quirks

This is an **Angular Single Page Application** with hash-based routing. This creates specific challenges:

### Hash Routing
- All routes are after `#/` in the URL
- Example: `https://sdms.udiseplus.gov.in/g1/#/school/2184637/viewStudentDetails/cy/7`
- The browser sees the base URL as `https://sdms.udiseplus.gov.in/g1/` — everything after `#` is handled by Angular's router

### `page.goto()` Doesn't Trigger Angular Route Changes
**CRITICAL BUG DISCOVERED:**
- If you're on `/viewStudentDetails/cy/6` and do `page.goto('/viewStudentDetails/cy/7')`, Angular does NOT re-render
- The URL in the address bar changes, but the page still shows Class VI data
- This is because `page.goto()` with only a hash change doesn't cause a full page reload

### The Working Fix: about:blank Bounce
```python
page.goto("about:blank")
time.sleep(0.5)
page.goto(target_url, wait_until="networkidle", timeout=30000)
```
Navigate to `about:blank` first, then to the target URL. This forces a full page load, causing Angular to bootstrap fresh and load the correct route.

### `page.goto(dashboard_url)` Redirects
- Navigating directly to the dashboard URL often redirects to `#/academic-choice` (the academic year selection page)
- This happens because Angular's route guards check for session state that only gets set during the normal login flow
- **Don't rely on direct dashboard navigation** — use the about:blank bounce approach for student list URLs instead

### `page.go_back()` Works Fine
- Browser back button works correctly for returning from GP form to student list
- After `go_back()`, Angular does re-render the student list properly
- But sometimes the table takes time to reload — always use `wait_for_table()` after `go_back()`

---

## 12. Navigation Patterns That Work

### ✅ Student List → GP Form → Student List (current flow)
```python
# 1. Navigate to student list (with about:blank bounce)
page.goto("about:blank")
time.sleep(0.5)
page.goto(student_list_url, wait_until="networkidle", timeout=30000)
wait_for_table(page)

# 2. Click GP button for a student (by row index)
page.evaluate("""(idx) => {
    const rows = document.querySelectorAll('table tbody tr');
    const row = rows[idx];
    const gpBtn = [...row.querySelectorAll('*')].find(e => e.textContent.trim() === 'GP');
    gpBtn.click();
}""", row_index)
time.sleep(3)

# 3. Do work on GP form...

# 4. Go back to student list
page.go_back(wait_until="networkidle", timeout=30000)
wait_for_table(page)
```

### ✅ Direct URL to EP/FP Form
```python
# Navigate directly to EP form for a specific student
ep_url = f"{BASE_URL}/g1/#/school/{school_id}/new-ac/{class_num}/{section_num}/{student_id}?formId=2&formEditFlag=1"
page.goto("about:blank")
time.sleep(0.5)
page.goto(ep_url, wait_until="networkidle", timeout=30000)
```

### ✅ Class-to-Class Navigation (about:blank bounce)
```python
# Navigate from Class VI student list to Class VII student list
page.goto("about:blank")
time.sleep(0.5)
page.goto(class_7_url, wait_until="networkidle", timeout=30000)
wait_for_table(page)
```

---

## 13. Navigation Patterns That DON'T Work

### ❌ Direct hash URL change between classes
```python
# DON'T DO THIS — Angular won't re-render
page.goto(f".../viewStudentDetails/cy/7")  # from cy/6
# Page still shows Class VI data!
```

### ❌ Dashboard button clicks after page.goto(dashboard_url)
```python
# DON'T DO THIS — redirects to academic-choice
page.goto(dashboard_url)
# Now you're on academic-choice page, not dashboard
# Class buttons don't exist here
```

### ❌ Using `page.select_option("select", ...)` for class dropdown
```python
# DON'T DO THIS — hits the Language dropdown instead
page.select_option("select", label="VII")
# Resolves to <select id="Language">, not the class dropdown
# Multiple <select> elements on page, Playwright picks the first one
```

---

## 14. GP/EP/FP Button Color System

Each student row has 3 buttons (GP, EP, FP) in the Action column. Their color indicates completion:

### Colors
| State | CSS Class | Background Color | Meaning |
|-------|-----------|-----------------|---------|
| Complete | `submit` | `rgb(28, 171, 130)` (green) | Form saved, all required fields filled |
| Incomplete | `incomplete` | `rgb(244, 134, 134)` (red) | Form not yet saved or missing required fields |

### How to Check
```javascript
// Get GP button state for a specific row
const rows = document.querySelectorAll('table tbody tr');
const row = rows[rowIndex];
const lastCell = row.querySelectorAll('td');
const actionCell = lastCell[lastCell.length - 1];
for (const el of actionCell.children) {
    if (el.textContent.trim() === 'GP') {
        const isDone = el.classList.contains('submit');
        // isDone = true means green, false means red
    }
    if (el.textContent.trim() === 'EP') {
        const isDone = el.classList.contains('submit');
    }
    if (el.textContent.trim() === 'FP') {
        const isDone = el.classList.contains('submit');
    }
}
```

### Important Notes
- The Entry Status column (cells[5]) shows **combined** status (all 3 forms)
- Entry Status = "Complete" only when GP + EP + FP are all green
- To check individual form status, you MUST check the button class
- The `ONLY_INCOMPLETE` config flag uses this to skip students whose GP is already green

---

## 15. Pagination System

### Component
- Angular Material paginator: `<mat-paginator>`
- Shows: "Items per page: 50" (FIXED — cannot be changed by user or script)
- Range label: "1 – 50 of 68" format

### Selectors
| Element | Selector | Purpose |
|---------|----------|---------|
| Range label | `.mat-mdc-paginator-range-label` | Text showing "X – Y of Z" |
| Next page button | `button[aria-label="Next page"]` | Click to go to next page |
| Previous page button | `button[aria-label="Previous page"]` | Click to go to previous page |
| Items per page | `.mat-mdc-paginator-page-size` | Shows 50 (not changeable) |

### Parsing Pagination
```javascript
const label = document.querySelector('.mat-mdc-paginator-range-label');
const text = label.textContent.trim(); // "1 – 50 of 68"
const match = text.match(/(\d+)\s*[–-]\s*(\d+)\s+of\s+(\d+)/);
// match[1] = start (1), match[2] = end (50), match[3] = total (68)
```

### Page Size
- Fixed at **50 students per page**
- Cannot be changed (no dropdown, no URL parameter)
- A class with 68 students → 2 pages (50 + 18)

### Next Page Click
```javascript
const btn = document.querySelector('button[aria-label="Next page"]');
if (btn && !btn.disabled) {
    btn.click();
    return true;
}
return false;
```
After clicking next page, always `wait_for_table()` — the table re-renders.

### Recovery After go_back()
If the table doesn't reload after `go_back()`, the script:
1. Re-navigates to the student list URL
2. Waits for table to load
3. Clicks "Next page" repeatedly to return to the correct page

---

## 16. Existing Script Architecture

### Files
```
Udise-Plus-Automation/
├── run.py              # Main automation script (~627 lines)
├── config.py           # All configuration (~80 lines)
├── requirements.txt    # playwright dependency
├── README.md           # User documentation with Mac/Win/PowerShell commands
├── CONTEXT.md          # This file — full technical reference
├── .gitignore
├── venv/               # Python virtual environment (created during setup)
└── reports/            # Auto-generated per-run (timestamped subdirectories)
    └── 2025-06-XX_HH-MM-SS/
        ├── summary.md              # Overall totals + per-class breakdown table
        ├── class_Nursery_KG_PP3.md # Every student in Nursery with action taken
        ├── class_LKG_KG1_PP2.md
        ├── class_VI.md
        ├── class_VII.md
        └── ...
```

### Key Functions in run.py

| Function | Purpose |
|----------|---------|
| `detect_school_id(page)` | Extract school ID from current URL via regex (checks `page.url`, `window.location.href`, `window.location.hash`) |
| `detect_classes(page)` | Read class dropdown on student list page → returns list of `{value, label}` for available classes |
| `build_urls(school_id)` | Return dict of URL templates for `student_list`, `student_gp`, `dashboard` |
| `wait_for_table(page, timeout)` | Poll for `table tbody tr` rows, up to timeout seconds |
| `wait_for_field(page, selector, timeout)` | Poll for a form field element to exist |
| `wait_for_swal(page, timeout)` | Poll for SweetAlert2 popup text (every 0.5s) |
| `navigate_to_class(page, class_num, urls)` | about:blank bounce → student list URL (forces Angular full reload) |
| `get_pagination_info(page)` | Parse "X – Y of Z" from `.mat-mdc-paginator-range-label` |
| `click_next_page(page)` | Click `button[aria-label="Next page"]` if not disabled |
| `click_gp_button(page, row_index)` | Find and click GP button (by text content "GP") in specific table row |
| `read_and_fill_field(page)` | Read current field value, set new value via JS + change event, click Save, handle popup |
| `process_class(page, class_num, urls)` | Full class processing: paginate, iterate students, check GP color, fill fields |
| `write_class_report(...)` | Generate per-class markdown report (summary table + every student row) |
| `write_summary_report(...)` | Generate overall summary report (grand totals + per-class breakdown + all errors) |
| `parse_args()` | Parse `--classes` CLI arg (supports integers, negative numbers, and "auto") |
| `main()` | Entry point: parse args, launch browser, login flow, auto-detect, iterate classes, generate reports |

### Flow of main()
```
1. Parse CLI args (--classes flag: specific numbers, "auto", or omit for config default)
2. Launch Chromium (headed, slow_mo=200, viewport 1280x900)
3. Navigate to login URL
4. input() — wait for user to log in, select academic year, reach dashboard, press ENTER
5. Detect school ID from URL (3 sources checked, fallback to manual input)
6. Build URL templates with school_id
7. If --classes auto: navigate to any student list page, call detect_classes(), populate CLASS_NAMES
8. Create timestamped reports directory
9. For each class:
   a. navigate_to_class() — about:blank bounce → student list URL
   b. process_class() — iterate students with pagination, check GP color, fill fields
   c. write_class_report() — per-class markdown with every student's action
10. write_summary_report() — grand totals + per-class table + all errors
11. Print final stats to terminal
12. input() — wait for user to close browser
```

### How process_class() Works (inner loop)
```
For each page of students (50 per page, fixed by UDISE+):
    Parse pagination (start, end, total) from mat-paginator
    For each row in table:
        Extract student info (name, PEN, gender, gp_done from GP button CSS class)
        If ONLY_INCOMPLETE and gp_done (button has class 'submit') → skip, log as "GP Already Done"
        Click GP button (by row index, text match 'GP')
        Wait for GP form to load (wait_for_field with FIELD_SELECTOR)
        read_and_fill_field():
            Check current value
            If SKIP_IF_ALREADY_SET and value non-empty and not ALWAYS_SAVE → skip
            If empty or not SKIP_IF_ALREADY_SET → set value via JS + dispatch change event
            If ALWAYS_SAVE and value already set → save anyway (marks profile complete)
            Click Save button (found by text content "Save")
            Wait for SweetAlert2 popup (wait_for_swal, polls every 0.5s)
            Check for "successfully" in popup text
            Close popup (.swal2-close)
        go_back() to student list (wait_until="networkidle")
        Wait for table to reload (wait_for_table)
        If table missing → re-navigate to student list URL + re-paginate to current page
    Click next page (if end < total)
```

### Report Generation Details

**Class Report (`write_class_report`):**
- Header: class name, timestamp, school ID, field selector, value
- Summary table: Total, Updated, Skipped (already set), GP Already Done, Errors
- Student details table: #, Name, PEN, Gender, Action, Previous Value, New Value
- Action values: "Updated", "Skipped", "GP Done", "Field N/A", "Error"
- Errors section: numbered list of any errors for that class

**Summary Report (`write_summary_report`):**
- Header: timestamp, school ID, field + value
- Grand totals: all stats summed across classes
- Per-class breakdown table: Class, Students, Updated, Skipped, GP Done, Errors, link to class report
- All errors: combined across classes with class prefix

### How read_and_fill_field() Sets a Dropdown Value
```javascript
// 1. Get current value
const el = document.querySelector('#bloodGroup');
const currentValue = el.value;

// 2. Set new value
el.value = '9';

// 3. CRITICAL: Dispatch change event so Angular detects the change
el.dispatchEvent(new Event('change', { bubbles: true }));

// 4. Click Save
[...document.querySelectorAll('button')].find(b => b.textContent.includes('Save')).click();
```

---

## 17. Config Reference

### config.py — Full Reference

```python
# ---------- CLASSES ----------
# Which classes to process (use URL numbers, see class mapping below)
# Full mapping (negative numbers for pre-primary):
#   -3 = Nursery/KG/PP3    1 = I       6 = VI      11 = XI
#   -2 = LKG/KG1/PP2       2 = II      7 = VII     12 = XII
#   -1 = UKG/KG2/PP1       3 = III     8 = VIII
#                           4 = IV      9 = IX
#                           5 = V      10 = X
# Tip: Use --classes auto on the command line to auto-detect from portal
CLASSES_TO_PROCESS = [6, 7, 8, 9, 10, 11, 12]

# Section (1 = A, 2 = B)
SECTION_NUM = 1

# ---------- FIELD TO SET ----------
# Target field CSS selector
FIELD_SELECTOR = "#bloodGroup"

# Value to set (the <option> value attribute)
FIELD_VALUE = "9"

# Human-readable label for logging
FIELD_LABEL = "Under Investigation - Result will be updated soon"

# ---------- SKIP LOGIC ----------
# Skip if field already has a non-empty value
SKIP_IF_ALREADY_SET = True

# Save even if field was already set (marks profile complete in UDISE+)
ALWAYS_SAVE = True

# Skip students whose GP button is green (already saved/complete)
ONLY_INCOMPLETE = True

# ---------- TIMING (seconds) ----------
PAGE_LOAD_DELAY = 3           # After page navigation
SAVE_DELAY = 3                # After Save click (fallback — wait_for_swal is primary)
BETWEEN_STUDENTS_DELAY = 1    # Breathing room between students
BACK_NAV_DELAY = 2            # After go_back() to student list

# ---------- PAGINATION ----------
PAGE_SIZE = 50                # Fixed by UDISE+ (cannot be changed)

# ---------- LOGIN ----------
LOGIN_WAIT_SECONDS = 120      # Legacy (replaced by input() prompt)
```

### Skip Logic Interaction

| ONLY_INCOMPLETE | SKIP_IF_ALREADY_SET | ALWAYS_SAVE | Behavior |
|:-:|:-:|:-:|---|
| True | True | True | **Default/Fastest.** Green GP → skip instantly. Red GP: empty → set + save, non-empty → save anyway. |
| True | True | False | Green GP → skip. Red GP: empty → set + save, non-empty → skip entirely. |
| False | True | True | Check every student's GP form. Empty → set + save. Non-empty → save anyway. |
| False | False | — | Set value on ALL students regardless of current value. |

### CLI Arguments

```bash
# Process classes from config.py (default)
python -u run.py

# Process specific classes (standard)
python -u run.py --classes 6 10 12

# Process pre-primary classes (negative numbers)
python -u run.py --classes -3 -2 -1

# Mix pre-primary and standard
python -u run.py --classes -3 -2 -1 1 2 3 6

# Auto-detect all classes from portal dropdown
python -u run.py --classes auto

# Single class
python -u run.py --classes 7
```

**Platform notes:**
- Mac/Linux: All forms work as-is
- Windows CMD: All forms work as-is
- Windows PowerShell: For negative numbers, use `--` separator: `python -u run.py --classes -- -3 -2 -1`

### Auto-Detect Classes (`--classes auto`)

When `--classes auto` is used:
1. Script navigates to the student list page for the first class in `CLASSES_TO_PROCESS` (or class 1)
2. Reads the class `<select>` dropdown options (excludes Language dropdown)
3. Returns list of `{value, label}` for all available classes
4. Populates `CLASS_NAMES` dict with any classes not in the hardcoded mapping
5. Processes all detected classes in order

This is useful when you don't know which classes a school offers (e.g., primary vs. secondary schools).

---

## 18. Known Portal Behaviors & Edge Cases

### Slow Loading
- UDISE+ can be very slow, especially during peak hours (Indian school hours)
- Pages sometimes take 10-15 seconds to load
- The script uses `wait_for_table()` and `wait_for_field()` with 30s timeouts
- If still too slow, increase `PAGE_LOAD_DELAY` in config

### Table Not Reloading After go_back()
- Sometimes `page.go_back()` returns to the student list URL but the table is empty
- Recovery: re-navigate to the student list URL and re-paginate
- The script handles this automatically

### SweetAlert2 Timing
- Popup appears 0.5-3 seconds after Save click
- `wait_for_swal()` polls every 0.5 seconds for up to 30 seconds
- If no popup appears, it's treated as an error

### Form Validation Errors
- If a required field is missing, Save shows an error popup instead of success
- The script checks for "successfully" in the popup text
- Non-success popups are logged as errors

### Student IDs Not Exposed in Table
- The student list table doesn't directly expose student IDs
- The GP/EP/FP buttons are `<a>` tags — their click handlers navigate to the form URL which contains the student ID
- The current script clicks the button (doesn't extract the URL/ID)
- If you need student IDs for direct URL navigation, you'd need to extract them from button `href` attributes or `onclick` handlers

### Angular Material `<mat-select>` vs Native `<select>`
- The Blood Group field (`#bloodGroup`) is a **native HTML `<select>`** element
- Some other fields on UDISE+ may use Angular Material's `<mat-select>` component
- `<mat-select>` requires different handling — you can't set `.value` directly
- For `<mat-select>`: click to open → click the option in the overlay panel
- Check the element type before deciding the fill strategy

### Multiple `<select>` Elements on Page
- Pages have multiple `<select>` elements (Language selector at top, form fields)
- Always use specific selectors (IDs like `#bloodGroup`) rather than generic `select`
- Playwright's `page.select_option("select", ...)` will match the FIRST `<select>` found (usually the Language dropdown)

---

## 19. How to Extend for EP/FP

### Step 1: Discover EP/FP Form Fields
Navigate to an EP or FP form in the browser and run:
```javascript
// Run this in browser console or via Playwright
const fields = {
    selects: [...document.querySelectorAll('select')].map(el => ({
        id: el.id,
        name: el.name,
        className: el.className,
        options: [...el.options].map(o => ({ value: o.value, text: o.text.trim() }))
    })),
    inputs: [...document.querySelectorAll('input:not([type=hidden])')].map(el => ({
        id: el.id,
        name: el.name,
        type: el.type,
        placeholder: el.placeholder
    })),
    textareas: [...document.querySelectorAll('textarea')].map(el => ({
        id: el.id,
        name: el.name
    })),
    matSelects: [...document.querySelectorAll('mat-select')].map(el => ({
        id: el.id,
        'aria-label': el.getAttribute('aria-label'),
        role: el.getAttribute('role')
    }))
};
console.log(JSON.stringify(fields, null, 2));
```

### Step 2: Check Button Color for EP/FP
The existing `click_gp_button` approach works for EP/FP too — just change the text match:
```javascript
// For EP button
const epBtn = [...row.querySelectorAll('*')].find(e => e.textContent.trim() === 'EP');
const epDone = epBtn.classList.contains('submit');
epBtn.click();

// For FP button
const fpBtn = [...row.querySelectorAll('*')].find(e => e.textContent.trim() === 'FP');
const fpDone = fpBtn.classList.contains('submit');
fpBtn.click();
```

### Step 3: Modify the Script
Options for extending:
1. **Simple:** Add a new `FORM_TYPE` config option (`"GP"`, `"EP"`, `"FP"`) that changes which button to click and which button color to check
2. **Advanced:** Process all 3 forms per student in sequence (GP → EP → FP) in a single pass
3. **Config-driven:** Add `EP_FIELD_SELECTOR`, `EP_FIELD_VALUE`, `FP_FIELD_SELECTOR`, `FP_FIELD_VALUE` to config

### Key Changes Needed
```python
# In config.py, add:
FORM_TYPE = "EP"  # or "GP" or "FP"
EP_FIELD_SELECTOR = "#someEPField"
EP_FIELD_VALUE = "someValue"

# In run.py, modify click_gp_button() to accept form_type parameter:
def click_form_button(page, row_index, form_type="GP"):
    return page.evaluate(f"""(idx) => {{
        const rows = document.querySelectorAll('table tbody tr');
        const row = rows[idx];
        const btn = [...row.querySelectorAll('*')].find(
            e => e.textContent.trim() === '{form_type}'
        );
        if (btn) {{ btn.click(); return true; }}
        return null;
    }}""", row_index)

# Modify button color check:
def is_form_complete(page, row_index, form_type="GP"):
    return page.evaluate(f"""(idx) => {{
        const rows = document.querySelectorAll('table tbody tr');
        const row = rows[idx];
        const lastCell = row.querySelectorAll('td');
        const actionCell = lastCell[lastCell.length - 1];
        for (const el of actionCell.children) {{
            if (el.textContent.trim() === '{form_type}') {{
                return el.classList.contains('submit');
            }}
        }}
        return false;
    }}""", row_index)
```

### Handling `<mat-select>` Fields (if EP/FP uses them)
```javascript
// 1. Click to open the mat-select
const matSelect = document.querySelector('#someMatSelectId');
matSelect.click();

// 2. Wait for overlay panel to appear
// ... poll for '.mat-mdc-select-panel' or '.cdk-overlay-pane'

// 3. Click the desired option
const options = document.querySelectorAll('mat-option');
const target = [...options].find(o => o.textContent.trim() === 'Desired Value');
target.click();
```

### Success Popup Text for EP/FP
- GP: "General data updated successfully."
- EP: Likely "Enrolment data updated successfully." (needs verification)
- FP: Likely "Facility data updated successfully." (needs verification)
- The script checks for "successfully" in the popup text, so it should work for all 3

---

## 20. School-Specific Data (Test Schools)

This automation was developed and tested against two schools:

### School 1: NAVODIT PUBLIC INTER COLLEGE (Secondary)

| Property | Value |
|----------|-------|
| School Name | NAVODIT PUBLIC INTER COLLEGE |
| UDISE Code | 09220905204 |
| Internal School ID | 2184637 |
| Type | Private Unaided |
| Classes | VI to XII |
| Total Students | 640 |
| User Account | JOLLY AGRAWAL (SCHOOL USER) |
| State | Uttar Pradesh (code 09) |

| Class | Number | Students |
|-------|--------|----------|
| VI    | 6      | 10       |
| VII   | 7      | 68       |
| VIII  | 8      | 55       |
| IX    | 9      | 72       |
| X     | 10     | 136      |
| XI    | 11     | 154      |
| XII   | 12     | 145      |

### School 2: NAVODIT PUBLIC SCHOOL KHUDAGANJ (Primary + Upper Primary)

| Property | Value |
|----------|-------|
| School Name | NAVODIT PUBLIC SCHOOL KHUDAGANJ |
| UDISE Code | 09220905203 |
| Internal School ID | 2107557 |
| Type | Primary with Upper Primary |
| Classes | Nursery through VIII |
| Total Students | 760 |
| User Account | MUKESH KUMAR GANGWAR (SCHOOL USER) |
| Sections | Some classes have A and B sections |

| Class | Number | Students |
|-------|--------|----------|
| Nursery | -3   | 21       |
| LKG     | -2   | 52       |
| UKG     | -1   | 126      |
| I       | 1    | 105      |
| II      | 2    | 118      |
| III     | 3    | 111      |
| IV      | 4    | 65       |
| V       | 5    | 80       |
| VI      | 6    | 59       |
| VII     | 7    | 7        |
| VIII    | 8    | 16       |

> This school was used to discover and test pre-primary class handling (negative class numbers) and the `--classes auto` feature.

### Students Tested During Development
- ANANYA CHAUHAN (School 1, Class VI) — Blood Group set to "Under Investigation"
- DEEPAK GANGWAR (School 1, Class VI) — Blood Group set to "Under Investigation"
- AAMAN ALI (School 1, Class VII) — Blood Group set to "Under Investigation"

---

## Appendix A: Complete JavaScript Snippets

### Get All Students on Current Page
```javascript
() => {
    const rows = document.querySelectorAll('table tbody tr');
    return [...rows].map((row, idx) => {
        const cells = row.querySelectorAll('td');
        const lastCell = cells[cells.length - 1];
        let gpDone = false, epDone = false, fpDone = false;
        if (lastCell) {
            for (const el of lastCell.children) {
                const text = el.textContent.trim();
                const done = el.classList.contains('submit');
                if (text === 'GP') gpDone = done;
                if (text === 'EP') epDone = done;
                if (text === 'FP') fpDone = done;
            }
        }
        return {
            index: idx,
            class_grade: cells[0]?.textContent?.trim(),
            pen: cells[1]?.textContent?.trim(),
            name: cells[2]?.textContent?.trim(),
            gender: cells[3]?.textContent?.trim(),
            dob: cells[4]?.textContent?.trim(),
            entry_status: cells[5]?.textContent?.trim(),
            last_updated: cells[6]?.textContent?.trim(),
            gp_done: gpDone,
            ep_done: epDone,
            fp_done: fpDone
        };
    });
}
```

### Get All Form Fields on Any Profile Tab
```javascript
() => {
    const result = { selects: [], inputs: [], matSelects: [], textareas: [] };

    document.querySelectorAll('select').forEach(el => {
        result.selects.push({
            id: el.id, name: el.name,
            value: el.value,
            options: [...el.options].map(o => ({
                value: o.value, text: o.text.trim(), selected: o.selected
            }))
        });
    });

    document.querySelectorAll('input:not([type=hidden])').forEach(el => {
        result.inputs.push({
            id: el.id, name: el.name, type: el.type,
            value: el.value, placeholder: el.placeholder,
            disabled: el.disabled, readOnly: el.readOnly
        });
    });

    document.querySelectorAll('mat-select').forEach(el => {
        result.matSelects.push({
            id: el.id,
            ariaLabel: el.getAttribute('aria-label'),
            value: el.querySelector('.mat-mdc-select-value-text')?.textContent?.trim()
        });
    });

    document.querySelectorAll('textarea').forEach(el => {
        result.textareas.push({
            id: el.id, name: el.name, value: el.value
        });
    });

    return result;
}
```

### Set Native `<select>` Value
```javascript
(selector, value) => {
    const el = document.querySelector(selector);
    if (!el) return false;
    el.value = value;
    el.dispatchEvent(new Event('change', { bubbles: true }));
    return true;
}
```

### Set `<mat-select>` Value (Angular Material)
```javascript
// This requires 2 steps with a delay between them
// Step 1: Click to open
async (page, selector, optionText) => {
    await page.click(selector);
    await page.waitForSelector('.mat-mdc-select-panel', { timeout: 5000 });
    const options = await page.$$('mat-option');
    for (const opt of options) {
        const text = await opt.textContent();
        if (text.trim() === optionText) {
            await opt.click();
            return true;
        }
    }
    return false;
}
```

### Click Save and Handle Popup
```javascript
// Click Save
() => {
    const btn = [...document.querySelectorAll('button')].find(
        b => b.textContent.includes('Save')
    );
    if (btn) { btn.click(); return true; }
    return false;
}

// Check popup
() => {
    const el = document.querySelector('.swal2-title, .swal2-html-container, #swal2-html-container');
    return el ? el.textContent.trim() : '';
}

// Close popup
() => {
    const close = document.querySelector('.swal2-close');
    if (close) { close.click(); return true; }
    const confirm = document.querySelector('button.swal2-confirm');
    if (confirm) { confirm.click(); return true; }
    return false;
}
```

---

## Appendix B: Playwright Python Patterns

### Launch Browser (headed mode, user sees it)
```python
with sync_playwright() as p:
    browser = p.chromium.launch(headless=False, slow_mo=200)
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
```

### Wait-and-Retry Pattern
```python
def wait_for_something(page, check_js, timeout=30):
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = page.evaluate(check_js)
        if result:
            return result
        time.sleep(1)
    return None
```

### Safe Navigation (about:blank bounce)
```python
def safe_navigate(page, url):
    page.goto("about:blank")
    time.sleep(0.5)
    page.goto(url, wait_until="networkidle", timeout=30000)
```

### Run with unbuffered output
```bash
python -u run.py  # -u flag ensures print() output appears immediately
```

---

*Last updated: June 2025*
*Portal version: UDISE+ SDMS (sdms.udiseplus.gov.in)*
*Discovered via interactive Playwright MCP sessions on two schools (secondary + primary)*
*Features: auto-detect school ID, auto-detect classes, GP button color check, markdown reports*
