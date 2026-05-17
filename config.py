# ============================================================
# UDISE+ Automation — Configuration
# ============================================================
# Edit the values below before running the script.
# ============================================================

# School ID is auto-detected from the URL after you log in.
# No need to set it here!

# Which classes to process (use the number that appears in the URL)
#
# Full mapping (negative numbers for pre-primary):
#   -3 = Nursery/KG/PP3    1 = I       6 = VI      11 = XI
#   -2 = LKG/KG1/PP2       2 = II      7 = VII     12 = XII
#   -1 = UKG/KG2/PP1       3 = III     8 = VIII
#                           4 = IV      9 = IX
#                           5 = V      10 = X
#
# Tip: Use --classes auto on the command line to auto-detect from portal
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

# If True, click Save on every student even if the field was already set
# (useful when UDISE+ needs a Save click to mark the profile as complete)
ALWAYS_SAVE = True

# If True, skip students whose GP button is green (already saved).
# Checks the button CSS class (submit=done, incomplete=needs work).
ONLY_INCOMPLETE = True

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


