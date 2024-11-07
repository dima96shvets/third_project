import os
import time
import random
import string
import pytest
import emoji
from selenium.webdriver import ActionChains
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from app import app, db
from app import Game
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

chrome_options = Options()
chrome_options.add_experimental_option("detach", True)
service = Service(ChromeDriverManager().install())

base_url = "http://127.0.0.1:5000"
RESULTS_FILE_PATH = 'test_results.txt'

TEST_CYCLE_DIR = os.path.join(os.getcwd(), "Bugs", f"Test cycle from {datetime.now().strftime('%d-%m-%Y_%H-%M')}")
os.makedirs(TEST_CYCLE_DIR, exist_ok=True)

test_case_counter = 1


@pytest.fixture(scope="function", autouse=True)
def app_context():
    with app.app_context():
        yield


@pytest.fixture(scope="function")
def driver():
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(2)
    driver.maximize_window()
    driver.get(base_url)
    yield driver
    driver.quit()


@pytest.fixture
def wait(driver):
    wait = WebDriverWait(driver, 10)
    return wait


@pytest.fixture(scope="function")
def existence_checking():
    def ec(model, **filters):
        return db.session.query(model).filter_by(**filters).first() is not None

    return ec


def randomstring(min_length=4, max_length=15, length=None):
    if length:
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))
    else:
        return ''.join(
            random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(min_length, max_length)))


def admin_login(driver):
    driver.get(f"{base_url}/login")
    driver.find_element(By.XPATH, "//input[@id='username']").send_keys("admin")
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys("password123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def date_generation():
    return datetime.now().strftime("%m%d%Y")


def capture_screenshot(driver, test_class_name, test_name):
    test_dir = os.path.join(TEST_CYCLE_DIR, f"{test_class_name} - {test_name}")
    os.makedirs(test_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
    screenshot_path = os.path.join(test_dir, f"{test_name}_{timestamp}.jpg")

    driver.save_screenshot(screenshot_path)
    return screenshot_path


@pytest.fixture
def assertion_handling(driver, request):
    test_name = request.node.name
    test_class_name = request.node.cls.__name__
    errors = []

    def sa(condition, error_message):
        if not condition:
            errors.append(error_message)
            capture_screenshot(driver, test_class_name, test_name)

    return sa, errors


@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    with open(RESULTS_FILE_PATH, 'w', encoding='utf-8') as f:
        f.write("=" * 128 + "\n")
        f.write(f"                                            📊📊📊 Test Results 📊📊📊\n")
        f.write("=" * 128 + "\n")


@pytest.fixture
def log_results(request):
    test_name = request.node.name
    test_description = request.node.function.__doc__

    def log(status, errors=None):
        global test_case_counter
        with open(RESULTS_FILE_PATH, 'a', encoding='utf-8') as f:
            status_emoji = "✔️ ✔️ ✔️ PASSED ✔️ ✔️ ✔️" if status == "passed" else "❌ ❌ ❌ FAILED ❌ ❌ ❌"
            f.write(f"\n                             {test_case_counter}.💠💠💠{request.node.nodeid}💠💠💠:\n".upper())
            test_case_counter += 1
            if test_description:
                f.write(f"{status_emoji}\n        📄📄📄\n        Test case Description:\n        {test_description.strip()}\n        📄📄📄\n")
            else:
                f.write(f"{status_emoji}\n        📄📄📄\n        Test case Description:\n🔴 🔴 🔴 Not provided 🔴 "
                        f"🔴 🔴\n        📄📄📄\n")
            if errors:
                f.write(f"❗ ❗ ❗ ERRORS LIST ❗ ❗ ❗:\n")
                for i, error in enumerate(errors, 1):
                    f.write(f"        ⚠️⚠️⚠️ {i}. {error} ⚠️⚠️⚠️\n")
                f.write("\n")
            else:
                f.write("🟢 🟢 🟢 NO ERRORS 🟢 🟢 🟢\n\n")

    return log


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    with open(RESULTS_FILE_PATH, 'a', encoding='utf-8') as f:
        f.write("=" * 128 + "\n")
        f.write(f"                                          🚩🚩🚩 All tests finished 🚩🚩🚩\n")
        f.write("=" * 128 + "\n")


@pytest.fixture(scope="session", autouse=True)
def final_cleanup():
    """ Cleanup function to delete all games with ID higher than 8 after all tests have completed """
    yield
    with app.app_context():
        extra_games = Game.query.filter(Game.id > 8).all()
        for game in extra_games:
            db.session.delete(game)
        db.session.commit()


