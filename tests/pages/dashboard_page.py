from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from tests.pages.base_page import BasePage


class DashboardPage(BasePage):
    """Page Object representing the CloudOps Dashboard."""

    # Locators
    DASHBOARD_TITLE = (By.ID, "dashboard-title")
    CURRENT_USER = (By.ID, "current-user")
    LOGOUT_BUTTON = (By.ID, "logout-btn")
    FLASH_ALERT = (By.ID, "flash-message")

    # Metrics
    STAT_TOTAL_ITEMS = (By.ID, "stat-total-items")
    STAT_IN_STOCK = (By.ID, "stat-in-stock")
    STAT_OUT_STOCK = (By.ID, "stat-out-stock")

    # Search & Filter
    SEARCH_INPUT = (By.ID, "search-input")
    CATEGORY_FILTER = (By.ID, "category-filter")
    FILTER_SUBMIT_BTN = (By.ID, "filter-submit-btn")
    CLEAR_FILTER_BTN = (By.ID, "clear-filter-btn")

    # Inventory Table
    INVENTORY_TABLE = (By.ID, "inventory-table")
    TABLE_ROWS = (By.CSS_SELECTOR, "#inventory-table-body tr")
    NO_ITEMS_MESSAGE = (By.ID, "no-items-message")

    # Add Item Modal Locators
    OPEN_ADD_MODAL_BTN = (By.ID, "open-add-modal-btn")
    MODAL_ITEM_NAME = (By.ID, "item-name")
    MODAL_ITEM_SKU = (By.ID, "item-sku")
    MODAL_ITEM_CATEGORY = (By.ID, "item-category")
    MODAL_ITEM_QUANTITY = (By.ID, "item-quantity")
    MODAL_ITEM_PRICE = (By.ID, "item-price")
    MODAL_SUBMIT_BTN = (By.ID, "modal-submit-btn")
    RESET_INVENTORY_BTN = (By.ID, "reset-inventory-btn")

    def __init__(self, driver, base_url="http://localhost:5000"):
        super().__init__(driver)
        self.base_url = base_url
        self.url = f"{self.base_url}/dashboard"

    def open(self):
        self.navigate_to(self.url)
        return self

    def is_dashboard_displayed(self):
        return self.is_visible(self.DASHBOARD_TITLE, timeout=8)

    def get_logged_in_username(self):
        return self.get_text(self.CURRENT_USER)

    def logout(self):
        self.click(self.LOGOUT_BUTTON)

    def get_flash_message(self):
        if self.is_visible(self.FLASH_ALERT):
            return self.get_text(self.FLASH_ALERT)
        return ""

    def get_total_stat_count(self):
        return int(self.get_text(self.STAT_TOTAL_ITEMS))

    def search(self, query):
        self.type_text(self.SEARCH_INPUT, query)
        self.click(self.FILTER_SUBMIT_BTN)

    def filter_by_category(self, category_name):
        select_element = self.find_clickable_element(self.CATEGORY_FILTER)
        Select(select_element).select_by_visible_text(category_name)
        self.click(self.FILTER_SUBMIT_BTN)

    def add_resource(self, name, sku, category="Compute", quantity=1, price=50.0):
        js_code = f"""
            document.getElementById('item-name').value = '{name}';
            document.getElementById('item-sku').value = '{sku}';
            document.getElementById('item-category').value = '{category}';
            document.getElementById('item-quantity').value = '{quantity}';
            document.getElementById('item-price').value = '{price}';
            document.getElementById('add-item-form').submit();
        """
        self.driver.execute_script(js_code)

    def get_row_by_sku(self, sku, timeout=5):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        locator = (By.CSS_SELECTOR, f"#inventory-table-body tr[data-sku='{sku.upper()}']")
        try:
            return WebDriverWait(self.driver, timeout).until(EC.presence_of_element_located(locator))
        except Exception:
            return None

    def delete_resource_by_sku(self, sku):
        row = self.get_row_by_sku(sku)
        if row:
            form = row.find_element(By.CSS_SELECTOR, "form")
            self.driver.execute_script("arguments[0].submit();", form)

    def wait_for_sku_disappeared(self, sku, timeout=10):
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.common.exceptions import TimeoutException

        locator = (By.CSS_SELECTOR, f"#inventory-table-body tr[data-sku='{sku.upper()}']")
        try:
            return WebDriverWait(self.driver, timeout).until(EC.invisibility_of_element_located(locator))
        except TimeoutException:
            return False

    def reset_inventory(self):
        self.click(self.RESET_INVENTORY_BTN)
