# ============================================================
# UDISE+ Automation — Configuration
# ============================================================
# Edit the values below before running the script.
# ============================================================

# School ID as it appears in the UDISE+ URL
# Example URL: https://sdms.udiseplus.gov.in/g1/#/school/2184637/...
SCHOOL_ID = "2184637"

# Which classes to process (use the number that appears in the URL)
# Class VI=6, VII=7, VIII=8, IX=9, X=10, XI=11, XII=12
CLASSES_TO_PROCESS = [6, 7, 8, 9, 10, 11, 12]

# Section number (1 = Section A, which is the default/only section for most schools)
SECTION_NUM = 1

# ---------- DROPDOWN FIELD TO SET ----------
# The CSS selector of the <select> dropdown to fill
FIELD_SELECTOR = "#bloodGroup"

# The VALUE attribute of the <option> to select.
# Blood Group options:
#   "" = Select (empty/default)
#   "1" = A+
#   "2" = A-
#   "3" = B+
#   "4" = B-
#   "5" = O+
#   "6" = O-
#   "7" = AB+
#   "8" = AB-
#   "9" = Under Investigation - Result will be updated soon
FIELD_VALUE = "9"

# Human-readable label (for logging only)
FIELD_LABEL = "Under Investigation - Result will be updated soon"

# ---------- SKIP LOGIC ----------
# If True, skip students whose field already has a non-empty value
SKIP_IF_ALREADY_SET = True

# ---------- TIMING (seconds) ----------
# Delay after page loads (student list or GP form)
PAGE_LOAD_DELAY = 3

# Delay after clicking Save (wait for success popup)
SAVE_DELAY = 3

# Delay between students (breathing room to avoid rate limits)
BETWEEN_STUDENTS_DELAY = 1

# Delay after navigating back to student list
BACK_NAV_DELAY = 2

# ---------- PAGINATION ----------
# UDISE+ shows 50 students per page (fixed, cannot be changed)
PAGE_SIZE = 50

# ---------- LOGIN ----------
# The script opens the browser and waits for you to log in manually.
# Set how many seconds to wait for manual login.
LOGIN_WAIT_SECONDS = 120

# ---------- BASE URL ----------
BASE_URL = "https://sdms.udiseplus.gov.in"
STUDENT_LIST_URL = f"{BASE_URL}/g1/#/school/{SCHOOL_ID}/viewStudentDetails/cy/{{class_num}}"
STUDENT_GP_URL = f"{BASE_URL}/g1/#/school/{SCHOOL_ID}/new-ac/{{class_num}}/{{section_num}}/{{student_id}}?formId=1&formEditFlag=1"
LOGIN_URL = f"{BASE_URL}/p1/v1/login"
DASHBOARD_URL = f"{BASE_URL}/g1/#/school/{SCHOOL_ID}/schoolDashboard/cy"
