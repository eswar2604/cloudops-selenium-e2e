from selenium.webdriver.common.by import By
from tests.pages.base_page import BasePage


class LoginPage(BasePage):
    """Page Object representing the Login Page."""

    # Locators
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-submit-btn")
    FLASH_ALERT = (By.ID, "flash-message")
    LOGIN_HEADING = (By.ID, "login-heading")

    def __init__(self, driver, base_url="http://localhost:5000"):
        super().__init__(driver)
        self.base_url = base_url
        self.url = f"{self.base_url}/login"

    def open(self):
        self.navigate_to(self.url)
        return self

    def enter_username(self, username):
        self.type_text(self.USERNAME_INPUT, username)
        return self

    def enter_password(self, password):
        self.type_text(self.PASSWORD_INPUT, password)
        return self

    def click_login(self):
        self.click(self.LOGIN_BUTTON)

    def login(self, username, password):
        """Helper to perform complete login flow."""
        self.enter_username(username)
        self.enter_password(password)
        self.click_login()

    def get_flash_message(self):
        if self.is_visible(self.FLASH_ALERT):
            return self.get_text(self.FLASH_ALERT)
        return ""

    def open_root(self):
        self.navigate_to(self.base_url)
        return self

    def submit_bypassing_html5_validation(self, username="", password=""):
        """Submits the login form with HTML5 novalidate set to test backend validation."""
        self.driver.execute_script("document.getElementById('login-form').noValidate = true;")
        if username:
            self.enter_username(username)
        else:
            self.find_element(self.USERNAME_INPUT).clear()
        if password:
            self.enter_password(password)
        else:
            self.find_element(self.PASSWORD_INPUT).clear()
        self.click_login()

    def is_username_valid(self):
        element = self.find_element(self.USERNAME_INPUT)
        return self.driver.execute_script("return arguments[0].checkValidity();", element)

    def is_password_valid(self):
        element = self.find_element(self.PASSWORD_INPUT)
        return self.driver.execute_script("return arguments[0].checkValidity();", element)

    def is_login_page_displayed(self):
        return self.is_visible(self.LOGIN_HEADING, timeout=8) and self.is_visible(self.LOGIN_BUTTON, timeout=8)
