"""
UDISE+ Student Profile Automation
Automates repetitive dropdown selection across all students/classes.
Manual login required — script takes over after you log in.
"""

import time
import re
import sys
import os
import argparse
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PwTimeout

os.environ["PYTHONUNBUFFERED"] = "1"
from config import (
    CLASSES_TO_PROCESS, SECTION_NUM,
    FIELD_SELECTOR, FIELD_VALUE, FIELD_LABEL, SKIP_IF_ALREADY_SET, ALWAYS_SAVE, ONLY_INCOMPLETE,
    PAGE_LOAD_DELAY, SAVE_DELAY, BETWEEN_STUDENTS_DELAY, BACK_NAV_DELAY,
    PAGE_SIZE, LOGIN_WAIT_SECONDS,
)

BASE_URL = "https://sdms.udiseplus.gov.in"
LOGIN_URL = f"{BASE_URL}/p1/v1/login"

CLASS_NAMES = {
    -3: "Nursery/KG/PP3", -2: "LKG/KG1/PP2", -1: "UKG/KG2/PP1",
    1: "I", 2: "II", 3: "III", 4: "IV", 5: "V",
    6: "VI", 7: "VII", 8: "VIII", 9: "IX", 10: "X", 11: "XI", 12: "XII",
}

BLOOD_GROUP_LABELS = {
    "": "Empty",
    "1": "A+", "2": "A-", "3": "B+", "4": "B-",
    "5": "O+", "6": "O-", "7": "AB+", "8": "AB-",
    "9": "Under Investigation",
}


MAX_WAIT_FOR_ELEMENT = 30


def detect_school_id(page):
    for url in [page.url, page.evaluate("window.location.href")]:
        m = re.search(r'/school/(\d+)/', url)
        if m:
            return m.group(1)
    sid = page.evaluate("""() => {
        const hash = window.location.hash || '';
        const m = hash.match(/\\/school\\/(\\d+)\\//);
        return m ? m[1] : null;
    }""")
    return sid


def detect_classes(page):
    """Read the class dropdown on the student list page to discover available classes.
    Returns list of (value, label) tuples, e.g. [(-3, "Nursery/KG/PP3"), (1, "I"), ...]
    """
    result = page.evaluate("""() => {
        const selects = document.querySelectorAll('select:not(#Language)');
        for (const sel of selects) {
            const opts = [...sel.options];
            // The class dropdown has numeric values like -3, -2, 1, 2 ... 12
            // and labels like "Nursery/KG/PP3", "I", "VI", etc.
            const hasClassLike = opts.some(o => /^-?\\d+$/.test(o.value) && o.text.trim().length > 0);
            if (hasClassLike && opts.length >= 2) {
                return opts.map(o => ({ value: parseInt(o.value), label: o.text.trim() }));
            }
        }
        return null;
    }""")
    return result


def build_urls(school_id):
    return {
        "student_list": f"{BASE_URL}/g1/#/school/{school_id}/viewStudentDetails/cy/{{class_num}}",
        "student_gp": f"{BASE_URL}/g1/#/school/{school_id}/new-ac/{{class_num}}/{{section_num}}/{{student_id}}?formId=1&formEditFlag=1",
        "dashboard": f"{BASE_URL}/g1/#/school/{school_id}/schoolDashboard/cy",
    }


def wait(seconds):
    time.sleep(seconds)


def wait_for_table(page, timeout=MAX_WAIT_FOR_ELEMENT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        count = page.evaluate(
            "() => document.querySelectorAll('table tbody tr').length"
        )
        if count > 0:
            return count
        time.sleep(1)
    return 0


def wait_for_field(page, selector, timeout=MAX_WAIT_FOR_ELEMENT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        found = page.evaluate(f"""() => {{
            const el = document.querySelector('{selector}');
            return el ? true : false;
        }}""")
        if found:
            return True
        time.sleep(1)
    return False


def wait_for_swal(page, timeout=MAX_WAIT_FOR_ELEMENT):
    deadline = time.time() + timeout
    while time.time() < deadline:
        text = page.evaluate("""() => {
            const el = document.querySelector(
                '.swal2-title, .swal2-html-container, #swal2-html-container'
            );
            return el ? el.textContent.trim() : '';
        }""")
        if text:
            return text
        time.sleep(0.5)
    return ""


def parse_args():
    parser = argparse.ArgumentParser(description="UDISE+ Student Profile Automation")
    parser.add_argument(
        "--classes", nargs="+", metavar="N",
        help="Class numbers to process (e.g. --classes 6 7 10, or --classes -3 -2 for Nursery/LKG). "
             "If omitted, auto-detects all classes from the portal."
    )
    return parser.parse_args()


def get_pagination_info(page):
    text = page.evaluate("""() => {
        const label = document.querySelector('.mat-mdc-paginator-range-label');
        return label ? label.textContent.trim() : '';
    }""")
    match = re.search(r"(\d+)\s*[–-]\s*(\d+)\s+of\s+(\d+)", text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    return 0, 0, 0


def click_next_page(page):
    return page.evaluate("""() => {
        const btn = document.querySelector('button[aria-label="Next page"]');
        if (btn && !btn.disabled) {
            btn.click();
            return true;
        }
        return false;
    }""")


def click_gp_button(page, row_index):
    return page.evaluate(f"""(idx) => {{
        const rows = document.querySelectorAll('table tbody tr');
        if (idx >= rows.length) return null;
        const row = rows[idx];
        const gpBtn = [...row.querySelectorAll('*')].find(
            e => e.textContent.trim() === 'GP'
        );
        if (gpBtn) {{
            gpBtn.click();
            return true;
        }}
        return null;
    }}""", row_index)


def read_and_fill_field(page):
    if not wait_for_field(page, FIELD_SELECTOR):
        print("    ⚠ Field not found after waiting, skipping")
        return "field_missing", None

    field_value = page.evaluate(f"""() => {{
        const el = document.querySelector('{FIELD_SELECTOR}');
        return el ? el.value : null;
    }}""")

    if field_value is None:
        print("    ⚠ Field not found on this form, skipping")
        return "field_missing", None

    old_label = BLOOD_GROUP_LABELS.get(field_value, f"Unknown({field_value})")

    if SKIP_IF_ALREADY_SET and field_value != "" and not ALWAYS_SAVE:
        print(f"    ↩ Already set ({old_label}), skipping")
        return "skipped", field_value

    if field_value == "" or not SKIP_IF_ALREADY_SET:
        page.evaluate(f"""() => {{
            const el = document.querySelector('{FIELD_SELECTOR}');
            el.value = '{FIELD_VALUE}';
            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
        }}""")
        print(f"    → Set {old_label} → {FIELD_LABEL}")
    else:
        print(f"    → Keeping existing value ({old_label}), saving anyway")

    page.evaluate("""() => {
        const btn = [...document.querySelectorAll('button')].find(
            b => b.textContent.includes('Save')
        );
        if (btn) btn.click();
    }""")

    swal_text = wait_for_swal(page)

    if "successfully" in swal_text.lower():
        page.evaluate("""() => {
            const close = document.querySelector('.swal2-close');
            if (close) close.click();
        }""")
        wait(0.5)
        print(f"    ✅ Saved")
        return "saved", field_value
    else:
        print(f"    ❌ Unexpected popup: {swal_text or '(no popup appeared)'}")
        page.evaluate("""() => {
            const close = document.querySelector('.swal2-close');
            if (close) close.click();
            const confirm = document.querySelector('button.swal2-confirm');
            if (confirm) confirm.click();
        }""")
        wait(0.5)
        return "error", field_value


def navigate_to_class(page, class_num, urls):
    target_url = urls["student_list"].format(class_num=class_num)
    page.goto("about:blank")
    wait(0.5)
    page.goto(target_url, wait_until="networkidle", timeout=30000)
    wait(PAGE_LOAD_DELAY)


def process_class(page, class_num, urls):
    class_name = CLASS_NAMES.get(class_num, str(class_num))
    print(f"\n{'='*60}")
    print(f"CLASS {class_name} (num={class_num}) — Loading student list")
    print(f"{'='*60}")

    navigate_to_class(page, class_num, urls)
    table_rows = wait_for_table(page)
    if table_rows == 0:
        wait(PAGE_LOAD_DELAY)
        table_rows = wait_for_table(page)

    stats = {"saved": 0, "skipped": 0, "error": 0, "field_missing": 0}
    student_records = []
    errors_log = []
    page_num = 1

    while True:
        start, end, total = get_pagination_info(page)
        if total == 0:
            print("  No students found on this page.")
            break

        print(f"\n  Page {page_num}: students {start}–{end} of {total}")

        row_count = page.evaluate(
            "() => document.querySelectorAll('table tbody tr').length"
        )

        for i in range(row_count):
            student_info = page.evaluate(f"""(idx) => {{
                const rows = document.querySelectorAll('table tbody tr');
                if (idx >= rows.length) return null;
                const cells = rows[idx].querySelectorAll('td');
                const lastCell = cells[cells.length - 1];
                let gpDone = false;
                if (lastCell) {{
                    for (const el of lastCell.children) {{
                        if (el.textContent.trim() === 'GP') {{
                            gpDone = el.classList.contains('submit');
                            break;
                        }}
                    }}
                }}
                return {{
                    name: cells[2]?.textContent?.trim() || 'Unknown',
                    pen: cells[1]?.textContent?.trim() || '',
                    gender: cells[3]?.textContent?.trim() || '',
                    gp_done: gpDone
                }};
            }}""", i)

            if not student_info:
                continue

            student_num = start + i
            gp_status = "GP ✅" if student_info["gp_done"] else "GP 🔴"
            print(f"\n  [{student_num}/{total}] {student_info['name']} (PEN: {student_info['pen']}) [{gp_status}]")

            if ONLY_INCOMPLETE and student_info["gp_done"]:
                print(f"    ↩ GP already green, skipping")
                stats["gp_done"] = stats.get("gp_done", 0) + 1
                student_records.append({
                    **student_info, "num": student_num,
                    "result": "skipped_complete", "old_value": None, "error": None
                })
                continue

            clicked = click_gp_button(page, i)
            if not clicked:
                print("    ⚠ Could not click GP button")
                stats["error"] += 1
                errors_log.append(f"[{student_info['name']}] Could not click GP button")
                student_records.append({
                    **student_info, "num": student_num,
                    "result": "error", "old_value": None, "error": "Could not click GP button"
                })
                continue

            wait(PAGE_LOAD_DELAY)
            wait_for_field(page, FIELD_SELECTOR)

            try:
                result, old_value = read_and_fill_field(page)
                stats[result] = stats.get(result, 0) + 1
                student_records.append({
                    **student_info, "num": student_num,
                    "result": result, "old_value": old_value, "error": None
                })
                if result == "error":
                    errors_log.append(f"[{student_info['name']}] Save failed or unexpected popup")
            except Exception as e:
                print(f"    ❌ Error: {e}")
                stats["error"] += 1
                errors_log.append(f"[{student_info['name']}] {e}")
                student_records.append({
                    **student_info, "num": student_num,
                    "result": "error", "old_value": None, "error": str(e)
                })

            page.go_back(wait_until="networkidle", timeout=30000)
            wait(BACK_NAV_DELAY)

            current_row_count = wait_for_table(page)
            if current_row_count == 0:
                print("    ⚠ Student list didn't reload, re-navigating...")
                list_url = urls["student_list"].format(class_num=class_num)
                page.goto(list_url, wait_until="networkidle", timeout=30000)
                wait_for_table(page)
                for _ in range(page_num - 1):
                    click_next_page(page)
                    wait_for_table(page)

            wait(BETWEEN_STUDENTS_DELAY)

        if end >= total:
            break

        print(f"\n  → Moving to page {page_num + 1}...")
        if not click_next_page(page):
            print("  ⚠ No next page button, stopping")
            break
        page_num += 1
        wait(PAGE_LOAD_DELAY)
        wait_for_table(page)

    print(f"\n  Class {class_name} done: {stats}")
    return stats, student_records, errors_log


def write_class_report(class_num, stats, student_records, errors_log, reports_dir, school_id=""):
    class_name = CLASS_NAMES.get(class_num, str(class_num))
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = os.path.join(reports_dir, f"class_{class_name}.md")

    saved_count = stats.get("saved", 0)
    skipped_count = stats.get("skipped", 0)
    error_count = stats.get("error", 0)
    total = len(student_records)

    gp_done_count = sum(1 for r in student_records if r["result"] == "skipped_complete")

    lines = [
        f"# Class {class_name} — Blood Group Update Report",
        f"",
        f"**Generated:** {timestamp}",
        f"**School ID:** {school_id}",
        f"**Field:** {FIELD_SELECTOR}",
        f"**Value Set:** {FIELD_VALUE} ({FIELD_LABEL})",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total Students | {total} |",
        f"| ✅ Updated | {saved_count} |",
        f"| ↩ Skipped (already set) | {skipped_count} |",
        f"| ✅ GP Already Done | {gp_done_count} |",
        f"| ❌ Errors | {error_count} |",
        f"",
        f"## Student Details",
        f"",
        f"| # | Student Name | PEN | Gender | Action | Previous Value | New Value |",
        f"|---|-------------|-----|--------|--------|----------------|-----------|",
    ]

    for rec in student_records:
        old_raw = rec["old_value"]
        old_label = BLOOD_GROUP_LABELS.get(old_raw, f"Unknown({old_raw})") if old_raw is not None else "—"
        had_previous = "Yes" if old_raw and old_raw != "" else "No"

        if rec["result"] == "saved":
            action = "✅ Updated"
            new_val = FIELD_LABEL
        elif rec["result"] == "skipped":
            action = "↩ Skipped"
            new_val = old_label + " (kept)"
        elif rec["result"] == "skipped_complete":
            action = "✅ GP Done"
            new_val = "—"
        elif rec["result"] == "field_missing":
            action = "⚠ Field N/A"
            new_val = "—"
        else:
            action = "❌ Error"
            new_val = "—"

        prev_col = f"{old_label}" if had_previous == "Yes" else "Empty"
        if old_raw is None:
            prev_col = "—"

        lines.append(
            f"| {rec['num']} | {rec['name']} | {rec['pen']} | {rec['gender']} "
            f"| {action} | {prev_col} | {new_val} |"
        )

    if errors_log:
        lines.extend([
            f"",
            f"## Errors",
            f"",
        ])
        for idx, err in enumerate(errors_log, 1):
            lines.append(f"{idx}. {err}")

    lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  📄 Report saved: {filename}")
    return filename


def write_summary_report(all_class_stats, reports_dir, school_id=""):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    filename = os.path.join(reports_dir, "summary.md")

    grand = {"saved": 0, "skipped": 0, "gp_done": 0, "error": 0, "field_missing": 0, "total": 0}
    for class_num, stats, _, _ in all_class_stats:
        for k in ["saved", "skipped", "gp_done", "error", "field_missing"]:
            grand[k] += stats.get(k, 0)
        grand["total"] += sum(stats.values())

    lines = [
        f"# UDISE+ Automation — Run Summary",
        f"",
        f"**Generated:** {timestamp}",
        f"**School ID:** {school_id}",
        f"**Field:** {FIELD_SELECTOR} → {FIELD_VALUE} ({FIELD_LABEL})",
        f"",
        f"## Overall Totals",
        f"",
        f"| Metric | Count |",
        f"|--------|-------|",
        f"| Total Students Processed | {grand['total']} |",
        f"| ✅ Updated | {grand['saved']} |",
        f"| ↩ Skipped (already set) | {grand['skipped']} |",
        f"| ✅ GP Already Done | {grand['gp_done']} |",
        f"| ❌ Errors | {grand['error']} |",
        f"| ⚠ Field Not Found | {grand['field_missing']} |",
        f"",
        f"## Per-Class Breakdown",
        f"",
        f"| Class | Students | Updated | Skipped | GP Done | Errors | Report |",
        f"|-------|----------|---------|---------|---------|--------|--------|",
    ]

    for class_num, stats, _, _ in all_class_stats:
        class_name = CLASS_NAMES.get(class_num, str(class_num))
        total = sum(stats.values())
        lines.append(
            f"| {class_name} | {total} | {stats.get('saved',0)} "
            f"| {stats.get('skipped',0)} | {stats.get('gp_done',0)} | {stats.get('error',0)} "
            f"| [class_{class_name}.md](class_{class_name}.md) |"
        )

    all_errors = []
    for class_num, _, _, errors_log in all_class_stats:
        class_name = CLASS_NAMES.get(class_num, str(class_num))
        for err in errors_log:
            all_errors.append(f"**Class {class_name}:** {err}")

    if all_errors:
        lines.extend([
            f"",
            f"## All Errors",
            f"",
        ])
        for idx, err in enumerate(all_errors, 1):
            lines.append(f"{idx}. {err}")

    lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n📋 Summary report saved: {filename}")
    return filename


def main():
    args = parse_args()

    if args.classes:
        # User specified classes explicitly — use those, no auto-detect
        classes = [int(c) for c in args.classes]
        auto_detect_classes = False
    else:
        # No --classes flag — auto-detect from portal (default behavior)
        classes = []
        auto_detect_classes = True

    print("=" * 60)
    print("UDISE+ Student Profile Automation")
    print("=" * 60)
    if not auto_detect_classes:
        print(f"Classes       : {[CLASS_NAMES.get(c, c) for c in classes]}")
    else:
        print(f"Classes       : auto-detect from portal")
    print(f"Field         : {FIELD_SELECTOR}")
    print(f"Value to set  : {FIELD_VALUE} ({FIELD_LABEL})")
    print(f"Skip if set   : {SKIP_IF_ALREADY_SET}")
    print("=" * 60)

    reports_dir = os.path.join(os.path.dirname(__file__), "reports",
                               datetime.now().strftime("%Y-%m-%d_%H-%M-%S"))
    os.makedirs(reports_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=200)
        context = browser.new_context(viewport={"width": 1280, "height": 900})
        page = context.new_page()

        page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)

        input("\n👉  Log in, select Academic Year, and reach the School Dashboard.\n    Then come back here and press ENTER to start...\n")

        print(f"  Current URL: {page.url}")
        print(f"  JS URL:      {page.evaluate('window.location.href')}")

        school_id = detect_school_id(page)
        if not school_id:
            print("  ⚠ Could not detect School ID from URL.")
            print("  Tip: Make sure you're on the dashboard (URL contains /school/XXXX/)")
            school_id = input("  Enter School ID manually: ").strip()

        urls = build_urls(school_id)
        print(f"  School ID   : {school_id}")

        if auto_detect_classes:
            print("\n  🔍 Auto-detecting classes from portal...")
            navigate_to_class(page, 1, urls)
            wait_for_table(page, timeout=15)

            detected = detect_classes(page)
            if detected:
                classes = [c["value"] for c in detected]
                for c in detected:
                    if c["value"] not in CLASS_NAMES:
                        CLASS_NAMES[c["value"]] = c["label"]
                print(f"  ✅ Found {len(classes)} classes: {[CLASS_NAMES.get(c, c) for c in classes]}")
            else:
                print("  ⚠ Could not detect classes. Falling back to config defaults.")
                classes = CLASSES_TO_PROCESS

        print("\n✅  Starting automation...\n")

        all_class_stats = []

        for class_num in classes:
            try:
                stats, records, errors = process_class(page, class_num, urls)
                all_class_stats.append((class_num, stats, records, errors))
                write_class_report(class_num, stats, records, errors, reports_dir, school_id)
            except Exception as e:
                print(f"\n❌ Class {class_num} failed: {e}")
                all_class_stats.append((class_num, {"error": 1}, [], [str(e)]))

        write_summary_report(all_class_stats, reports_dir, school_id)

        grand = {"saved": 0, "skipped": 0, "gp_done": 0, "error": 0, "field_missing": 0}
        for _, stats, _, _ in all_class_stats:
            for k in ["saved", "skipped", "gp_done", "error", "field_missing"]:
                grand[k] += stats.get(k, 0)

        print("\n" + "=" * 60)
        print("ALL DONE!")
        print("=" * 60)
        print(f"  Saved       : {grand['saved']}")
        print(f"  Skipped     : {grand['skipped']}")
        print(f"  GP Done     : {grand['gp_done']}")
        print(f"  Errors      : {grand['error']}")
        print(f"  Field N/A   : {grand['field_missing']}")
        print(f"  Reports     : {reports_dir}")
        print("=" * 60)

        input("\nPress Enter to close the browser...")
        browser.close()


if __name__ == "__main__":
    main()
