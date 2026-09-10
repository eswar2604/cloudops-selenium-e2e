
import os
import pytest
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


# ============================================================
# PYTEST COMMAND-LINE OPTIONS
# ============================================================

def pytest_addoption(parser):
    parser.addoption(
        "--headless",
        action="store_true",
        default=True,
        help="Run browser in headless mode (default: True)"
    )

    parser.addoption(
        "--no-headless",
        action="store_false",
        dest="headless",
        help="Run browser with visible UI"
    )

    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        help="Browser type: chrome or firefox"
    )

    parser.addoption(
        "--base-url",
        action="store",
        default="http://localhost:5000",
        help="Base URL of application under test"
    )


# ============================================================
# BASE URL
# ============================================================

@pytest.fixture(scope="session")
def base_url(request):
    """Retrieve base URL from pytest CLI or environment."""

    env_url = os.environ.get("APP_BASE_URL")

    if env_url and env_url.strip():
        return env_url.strip()

    return request.config.getoption("--base-url") or "http://localhost:5000"


# ============================================================
# SELENIUM DRIVER
# ============================================================

@pytest.fixture(scope="function")
def driver(request):
    """Initialize Selenium WebDriver instance for each test."""

    headless = request.config.getoption("--headless")
    browser_type = request.config.getoption("--browser").lower()

    if browser_type == "chrome":

        options = ChromeOptions()

        # ----------------------------------------------------
        # HEADLESS MODE
        # ----------------------------------------------------

        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--start-maximized")

        # ----------------------------------------------------
        # CHROME SETTINGS
        # ----------------------------------------------------

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--disable-software-rasterizer")

        # ----------------------------------------------------
        # CHROME BINARY
        # ----------------------------------------------------

        chrome_bin = os.environ.get("CHROME_BIN")

        if chrome_bin and os.path.exists(chrome_bin):
            options.binary_location = chrome_bin

        elif os.path.exists("/usr/bin/chromium"):
            options.binary_location = "/usr/bin/chromium"

        # ----------------------------------------------------
        # CHROMEDRIVER
        # ----------------------------------------------------

        chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")

        if chromedriver_path and os.path.exists(chromedriver_path):

            service = ChromeService(
                executable_path=chromedriver_path
            )

            driver_instance = webdriver.Chrome(
                service=service,
                options=options
            )

        else:

            try:

                service = ChromeService(
                    ChromeDriverManager().install()
                )

                driver_instance = webdriver.Chrome(
                    service=service,
                    options=options
                )

            except Exception:

                driver_instance = webdriver.Chrome(
                    options=options
                )

    else:
        raise ValueError(
            f"Unsupported browser type: {browser_type}"
        )

    # --------------------------------------------------------
    # DRIVER CONFIGURATION
    # --------------------------------------------------------

    driver_instance.set_page_load_timeout(25)

    # Explicit waits are used in tests.
    driver_instance.implicitly_wait(0)

    driver_instance.maximize_window()

    # --------------------------------------------------------
    # TEST EXECUTION
    # --------------------------------------------------------

    yield driver_instance

    # ========================================================
    # FAILURE SCREENSHOT
    # ========================================================

    if (
        hasattr(request.node, "rep_call")
        and request.node.rep_call.failed
    ):

        reports_dir = os.path.join(
            os.getcwd(),
            "reports",
            "screenshots"
        )

        os.makedirs(
            reports_dir,
            exist_ok=True
        )

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        test_name = request.node.name

        screenshot_path = os.path.join(
            reports_dir,
            f"FAIL_{test_name}_{timestamp}.png"
        )

        try:

            driver_instance.save_screenshot(
                screenshot_path
            )

            # Store screenshot path on test item.
            # The pytest-html hook below will use this.
            request.node.failure_screenshot = screenshot_path

        except Exception as screenshot_error:

            print(
                f"Could not capture screenshot: "
                f"{screenshot_error}"
            )

    # --------------------------------------------------------
    # CLOSE BROWSER
    # --------------------------------------------------------

    driver_instance.quit()


# ============================================================
# CAPTURE TEST RESULT
# ============================================================

@pytest.hookimpl(
    tryfirst=True,
    hookwrapper=True
)
def pytest_runtest_makereport(item, call):
    """
    Store pytest test results on the test item.

    This allows other parts of conftest.py to know whether
    setup/call/teardown passed or failed.
    """

    outcome = yield

    rep = outcome.get_result()

    setattr(
        item,
        "rep_" + rep.when,
        rep
    )


# ============================================================
# PYTEST-HTML REPORT TITLE
# ============================================================

def pytest_html_report_title(report):
    """
    Change the browser tab/title of the HTML report.
    """

    report.title = "🚀 Selenium E2E Automation Report"


# ============================================================
# PYTEST-HTML ENVIRONMENT INFORMATION
# ============================================================

def pytest_configure(config):
    """
    Add useful environment information to the HTML report.
    """

    config._e2e_start_time = datetime.now()

    if hasattr(config, "_metadata"):

        config._metadata["Application"] = (
            os.environ.get(
                "APP_BASE_URL",
                config.getoption("--base-url")
            )
        )

        config._metadata["Browser"] = (
            config.getoption("--browser")
        )

        config._metadata["Headless"] = (
            "Yes"
            if config.getoption("--headless")
            else "No"
        )

        config._metadata["Execution"] = "Selenium + Pytest"

        config._metadata["Started"] = (
            config._e2e_start_time.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        )


# ============================================================
# PYTEST-HTML SUMMARY
# ============================================================

def pytest_html_results_summary(
    prefix,
    summary,
    postfix
):
    """
    Add a professional summary section to the report.
    """

    prefix.extend([
        """
        <div style="
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 10px;
            background: linear-gradient(
                135deg,
                #1f2937,
                #374151
            );
            color: white;
            font-family: Arial, sans-serif;
        ">

            <h1 style="
                margin: 0 0 8px 0;
                font-size: 26px;
            ">
                🚀 Selenium E2E Automation Report
            </h1>

            <p style="
                margin: 0;
                opacity: 0.85;
                font-size: 14px;
            ">
                Automated End-to-End Test Execution
            </p>

        </div>
        """
    ])


# ============================================================
# ADD SCREENSHOT TO FAILED TEST
# ============================================================

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport_html(item, call):
    """
    Attach failure screenshots to pytest-html.

    Note:
    pytest-html versions differ in how hooks are registered.
    The primary screenshot handling is also performed through
    pytest_runtest_makereport below.
    """

    outcome = yield
    rep = outcome.get_result()

    if rep.when != "call":
        return

    if not rep.failed:
        return

    screenshot_path = getattr(
        item,
        "failure_screenshot",
        None
    )

    if not screenshot_path:
        return

    # Screenshot path remains available as an artifact
    # even if the installed pytest-html version does not
    # support direct image injection.
    item.user_properties.append(
        (
            "Failure Screenshot",
            screenshot_path
        )
    )


# ============================================================
# FINAL REPORT INFORMATION
# ============================================================

def pytest_sessionfinish(session, exitstatus):
    """
    Store the overall execution completion time.
    """

    config = session.config

    start_time = getattr(
        config,
        "_e2e_start_time",
        None
    )

    if start_time:

        end_time = datetime.now()

        duration = end_time - start_time

        print(
            f"\nE2E execution completed in: "
            f"{duration}"
        )