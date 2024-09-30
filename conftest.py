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


def randomstring(min_length=4, max_length=15):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(random.randint(min_length, max_length)))


def admin_login(driver):
    driver.get(f"{base_url}/login")
    driver.find_element(By.XPATH, "//input[@id='username']").send_keys("admin")
    driver.find_element(By.XPATH, "//input[@id='password']").send_keys("password123")
    driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


def date_generation():
    return datetime.now().strftime("%m%d%Y")


@pytest.fixture
def assertion_handling():
    errors = []

    def sa(condition, error_message):
        if not condition:
            errors.append(error_message)

    return sa, errors

@pytest.hookimpl(tryfirst=True)
def pytest_sessionstart(session):
    with open(RESULTS_FILE_PATH, 'w',  encoding='utf-8') as f:
        f.write("=" * 128 + "\n")
        f.write(f"                                             📊Test Results📊\n")
        f.write("="*128 + "\n")


@pytest.fixture
def log_results(request):
    test_name = request.node.name
    test_description = request.node.function.__doc__

    def log(status, errors=None):
        with open(RESULTS_FILE_PATH, 'a',  encoding='utf-8') as f:
            status_emoji = "✔️PASSED✔️" if status == "passed" else "❌FAILED❌"
            f.write(f"🔷 Test Case {request.node.nodeid} 🔷:\n")
            if test_description:
                f.write(f"{status_emoji}\n📄Test Description📄:\n{test_description.strip()}\n")
            else:
                f.write(f"{status_emoji}\n📄Test Description📄:\n🔴 Not provided 🔴\n")
            if errors:
                f.write(f"❗Errors List❗:\n")
                for i, error in enumerate(errors, 1):
                    f.write(f"      ⚠️ {i}. {error}\n")
                f.write("\n")
            else:
                f.write("❎No Errors❎\n\n")
    return log


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    with open(RESULTS_FILE_PATH, 'a',  encoding='utf-8') as f:
        f.write("=" * 128 + "\n")
        f.write(f"                                             🚩All tests finished🚩\n")
        f.write("="*128 + "\n")
