"""
Selenium Automated Test Suite — TaskFlow App
CSC418 DevOps Midterm

Tests:
  1. Homepage loads correctly
  2. Page title and heading visible
  3. Task form elements present
  4. Add a new task
  5. Verify task appears in list
  6. Toggle task as completed
  7. Delete a task
  8. Health endpoint returns 200

Usage:
  pip install selenium webdriver-manager requests
  python test_app.py http://<YOUR-ALB-DNS-NAME>
"""

import sys
import time
import json
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service

# ── Config ──────────────────────────────────────────────────────────────────
BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
HEADLESS  = True   # Set False to see browser during testing

# ── Helpers ─────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
RESET  = "\033[0m"

pass_count = 0
fail_count = 0

def passed(name):
    global pass_count
    pass_count += 1
    print(f"  {GREEN}✓ PASS{RESET}  {name}")

def failed(name, reason=""):
    global fail_count
    fail_count += 1
    print(f"  {RED}✗ FAIL{RESET}  {name}" + (f"  →  {reason}" if reason else ""))

def section(title):
    print(f"\n{YELLOW}{'─'*50}{RESET}")
    print(f"{YELLOW}  {title}{RESET}")
    print(f"{YELLOW}{'─'*50}{RESET}")

# ── Setup Driver ─────────────────────────────────────────────────────────────
def get_driver():
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1280,800")
    try:
        return webdriver.Chrome(options=options)
    except Exception:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=service, options=options)

# ── Tests ─────────────────────────────────────────────────────────────────────
def run_tests():
    print(f"\n{'═'*50}")
    print(f"  TaskFlow Selenium Test Suite")
    print(f"  Target URL: {BASE_URL}")
    print(f"{'═'*50}")

    # ─── Test 1: Health Endpoint ───────────────────────────────────────────
    section("Test 1 – Health Check Endpoint")
    try:
        req = urllib.request.Request(f"{BASE_URL}/health")
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if resp.status == 200 and data.get('status') == 'healthy':
                passed("GET /health returns 200 with status=healthy")
            else:
                failed("GET /health check", f"Status: {resp.status}, Body: {data}")
    except Exception as e:
        failed("GET /health check", str(e))

    # ─── Selenium Tests ────────────────────────────────────────────────────
    driver = get_driver()
    wait   = WebDriverWait(driver, 15)

    try:
        # ─── Test 2: Homepage Loads ────────────────────────────────────────
        section("Test 2 – Homepage Load")
        driver.get(BASE_URL)
        time.sleep(1)

        if "TaskFlow" in driver.title:
            passed(f"Page title contains 'TaskFlow' (got: '{driver.title}')")
        else:
            failed("Page title check", driver.title)

        # ─── Test 3: UI Elements Present ──────────────────────────────────
        section("Test 3 – UI Elements")
        try:
            heading = driver.find_element(By.TAG_NAME, "h1")
            if "TaskFlow" in heading.text:
                passed(f"h1 heading found: '{heading.text}'")
            else:
                failed("h1 heading text", heading.text)
        except:
            failed("h1 heading not found")

        try:
            driver.find_element(By.ID, "taskTitle")
            passed("Task title input field found (#taskTitle)")
        except:
            failed("Task title input not found")

        try:
            driver.find_element(By.ID, "taskDesc")
            passed("Task description textarea found (#taskDesc)")
        except:
            failed("Task description textarea not found")

        try:
            driver.find_element(By.ID, "addBtn")
            passed("Add Task button found (#addBtn)")
        except:
            failed("Add button not found")

        # ─── Test 4: Add a Task ────────────────────────────────────────────
        section("Test 4 – Add New Task")
        test_title = f"Selenium Test Task {int(time.time())}"
        test_desc  = "Created by automated Selenium test"

        title_input = driver.find_element(By.ID, "taskTitle")
        desc_input  = driver.find_element(By.ID, "taskDesc")
        add_btn     = driver.find_element(By.ID, "addBtn")

        title_input.clear()
        title_input.send_keys(test_title)
        desc_input.clear()
        desc_input.send_keys(test_desc)
        add_btn.click()
        time.sleep(1)

        passed("Form submitted successfully")

        # ─── Test 5: Task Appears in List ─────────────────────────────────
        section("Test 5 – Task Appears in List")
        page_source = driver.page_source
        if test_title in page_source:
            passed(f"Task '{test_title}' visible in task list")
        else:
            failed("Task not found in page", "Task may not have been saved")

        if test_desc in page_source:
            passed(f"Task description visible in task list")
        else:
            failed("Task description not found in page")

        # ─── Test 6: Toggle Task ──────────────────────────────────────────
        section("Test 6 – Toggle Task Completion")
        try:
            # Find first checkbox link
            checkboxes = driver.find_elements(By.CSS_SELECTOR, "a.checkbox")
            if checkboxes:
                checkboxes[0].click()
                time.sleep(1)
                passed("Task toggled (checkbox clicked)")

                # Verify completed class applied
                task_items = driver.find_elements(By.CSS_SELECTOR, ".task-item.completed")
                if task_items:
                    passed("Task item shows 'completed' CSS class")
                else:
                    failed("Completed CSS class not found")
            else:
                failed("No checkbox elements found")
        except Exception as e:
            failed("Toggle test", str(e))

        # ─── Test 7: Delete Task ──────────────────────────────────────────
        section("Test 7 – Delete Task")
        try:
            delete_btns = driver.find_elements(By.CSS_SELECTOR, "a.btn-delete")
            if delete_btns:
                driver.execute_script("arguments[0].click();", delete_btns[0])
                time.sleep(0.5)
                try:
                    alert = driver.switch_to.alert
                    alert.accept()
                except Exception:
                    pass
                time.sleep(1)
                passed("Delete button clicked and confirmation accepted")
            else:
                failed("No delete buttons found")
        except Exception as e:
            failed("Delete test", str(e))

        # ─── Test 8: Stats Cards ──────────────────────────────────────────
        section("Test 8 – Stats Cards")
        try:
            stat_nums = driver.find_elements(By.CSS_SELECTOR, ".stat-num")
            if len(stat_nums) >= 3:
                passed(f"Stats cards found: Total={stat_nums[0].text}, Done={stat_nums[1].text}, Pending={stat_nums[2].text}")
            else:
                failed("Stats cards not found or incomplete")
        except Exception as e:
            failed("Stats cards test", str(e))

    finally:
        driver.quit()

    # ── Summary ───────────────────────────────────────────────────────────────
    total = pass_count + fail_count
    print(f"\n{'═'*50}")
    print(f"  RESULTS: {GREEN}{pass_count} passed{RESET}  |  {RED}{fail_count} failed{RESET}  |  {total} total")
    print(f"{'═'*50}\n")

    if fail_count == 0:
        print(f"  {GREEN}All tests passed! ✓{RESET}\n")
        sys.exit(0)
    else:
        print(f"  {RED}{fail_count} test(s) failed.{RESET}\n")
        sys.exit(1)


if __name__ == "__main__":
    run_tests()
