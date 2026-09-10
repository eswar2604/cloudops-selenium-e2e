import os
import pytest
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


def pytest_addoption(parser):
    parser.addoption(
        "--headless", action="store_true", default=True, help="Run browser in headless mode (default: True)"
    )
    parser.addoption(
        "--no-headless", action="store_false", dest="headless", help="Run browser with visible UI"
    )
    parser.addoption(
        "--browser", action="store", default="chrome", help="Browser type: chrome or firefox"
    )
    parser.addoption(
        "--base-url", action="store", default="http://localhost:5000", help="Base URL of application under test"
    )


@pytest.fixture(scope="session")
def base_url(request):
    """Retrieve base URL from pytest CLI or environment."""
    env_url = os.environ.get("APP_BASE_URL")
    if env_url and env_url.strip():
        return env_url.strip()
    return request.config.getoption("--base-url") or "http://localhost:5000"


@pytest.fixture(scope="function")
def driver(request):
    """Initialize Selenium WebDriver instance for each test."""
    headless = request.config.getoption("--headless")
    browser_type = request.config.getoption("--browser").lower()

    if browser_type == "chrome":
        options = ChromeOptions()
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-software-rasterizer")

        # Set Chromium binary location if running in Linux container
        chrome_bin = os.environ.get("CHROME_BIN")
        if chrome_bin and os.path.exists(chrome_bin):
            options.binary_location = chrome_bin
        elif os.path.exists("/usr/bin/chromium"):
            options.binary_location = "/usr/bin/chromium"

        # Initialize ChromeDriver (handles containerized chromedriver and webdriver-manager)
        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
        if chromedriver_path and os.path.exists(chromedriver_path):
            service = ChromeService(executable_path=chromedriver_path)
            driver_instance = webdriver.Chrome(service=service, options=options)
        else:
            try:
                service = ChromeService(ChromeDriverManager().install())
                driver_instance = webdriver.Chrome(service=service, options=options)
            except Exception:
                driver_instance = webdriver.Chrome(options=options)

    else:
        raise ValueError(f"Unsupported browser type: {browser_type}")

    driver_instance.set_page_load_timeout(25)
    driver_instance.implicitly_wait(10)
    driver_instance.maximize_window()

    yield driver_instance

    # Teardown: capture screenshot if failed
    if hasattr(request.node, "rep_call") and request.node.rep_call.failed:
        reports_dir = os.path.join(os.getcwd(), "reports", "screenshots")
        os.makedirs(reports_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_name = request.node.name
        screenshot_path = os.path.join(reports_dir, f"FAIL_{test_name}_{timestamp}.png")
        driver_instance.save_screenshot(screenshot_path)

    driver_instance.quit()


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Hook to capture test execution status for screenshot capture on failure."""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)
