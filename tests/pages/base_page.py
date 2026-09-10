from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BasePage:
    """Base class for all Page Objects providing shared Selenium WebDriver utilities."""

    def __init__(self, driver, timeout=10):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(self.driver, self.timeout)

    def navigate_to(self, url):
        self.driver.get(url)

    def find_element(self, locator):
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible_element(self, locator):
        return self.wait.until(EC.visibility_of_element_located(locator))

    def find_clickable_element(self, locator):
        return self.wait.until(EC.element_to_be_clickable(locator))

    def find_elements(self, locator):
        try:
            return self.wait.until(EC.presence_of_all_elements_located(locator))
        except TimeoutException:
            return []

    def click(self, locator):
        element = self.find_clickable_element(locator)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            element.click()
        except Exception:
            self.driver.execute_script("arguments[0].click();", element)

    def type_text(self, locator, text, clear_first=True):
        element = self.find_visible_element(locator)
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        if clear_first:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator):
        element = self.find_visible_element(locator)
        return element.text.strip()

    def is_visible(self, locator, timeout=3):
        try:
            WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located(locator))
            return True
        except (TimeoutException, NoSuchElementException):
            return False

    def get_current_url(self):
        return self.driver.current_url

    def get_page_title(self):
        return self.driver.title

    def wait_for_url_contains(self, path_substring):
        return self.wait.until(EC.url_contains(path_substring))

    def wait_for_staleness(self, element, timeout=10):
        """Wait for an element to become stale, indicating a DOM replacement or page reload."""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.staleness_of(element))
        except (TimeoutException, NoSuchElementException):
            return False

    def wait_for_invisibility(self, locator, timeout=10):
        """Wait for an element matching locator to become invisible or absent from the DOM."""
        try:
            return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            return False
