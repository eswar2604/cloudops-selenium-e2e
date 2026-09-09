from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    TABLE_BODY = (By.ID, "inventory-table-body")
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
        try:
            old_body = self.driver.find_element(By.ID, "inventory-table-body")
        except Exception:
            old_body = None
        self.type_text(self.SEARCH_INPUT, query)
        self.click(self.FILTER_SUBMIT_BTN)
        if old_body:
            try:
                WebDriverWait(self.driver, 5).until(EC.staleness_of(old_body))
            except Exception:
                pass

    def filter_by_category(self, category_name):
        try:
            old_body = self.driver.find_element(By.ID, "inventory-table-body")
        except Exception:
            old_body = None
        select_element = self.find_clickable_element(self.CATEGORY_FILTER)
        Select(select_element).select_by_visible_text(category_name)
        self.click(self.FILTER_SUBMIT_BTN)
        if old_body:
            try:
                WebDriverWait(self.driver, 5).until(EC.staleness_of(old_body))
            except Exception:
                pass

    def submit_add_resource_form(self, name, sku, category="Compute", quantity=1, price=50.0):
        try:
            old_body = self.driver.find_element(By.ID, "inventory-table-body")
        except Exception:
            old_body = None
        js_code = f"""
            document.getElementById('item-name').value = '{name}';
            document.getElementById('item-sku').value = '{sku}';
            document.getElementById('item-category').value = '{category}';
            document.getElementById('item-quantity').value = '{quantity}';
            document.getElementById('item-price').value = '{price}';
            document.getElementById('add-item-form').submit();
        """
        self.driver.execute_script(js_code)
        if old_body:
            try:
                WebDriverWait(self.driver, 5).until(EC.staleness_of(old_body))
            except Exception:
                pass

    def add_resource(self, name, sku, category="Compute", quantity=1, price=50.0):
        self.submit_add_resource_form(name, sku, category, quantity, price)
        locator = (By.CSS_SELECTOR, f"#inventory-table-body tr[data-sku='{sku.upper()}']")
        WebDriverWait(self.driver, 8).until(EC.presence_of_element_located(locator))

    def get_row_by_sku(self, sku):
        rows = self.driver.find_elements(By.CSS_SELECTOR, f"#inventory-table-body tr[data-sku='{sku.upper()}']")
        return rows[0] if rows else None

    def delete_resource_by_sku(self, sku):
        row = self.get_row_by_sku(sku)
        if row:
            btn = row.find_element(By.CSS_SELECTOR, "button.delete-item-btn")
            self.driver.execute_script("arguments[0].click();", btn)
            locator = (By.CSS_SELECTOR, f"#inventory-table-body tr[data-sku='{sku.upper()}']")
            WebDriverWait(self.driver, 8).until(EC.invisibility_of_element_located(locator))

    def reset_inventory(self):
        try:
            old_body = self.driver.find_element(By.ID, "inventory-table-body")
        except Exception:
            old_body = None
        btn = self.find_element(self.RESET_INVENTORY_BTN)
        self.driver.execute_script("arguments[0].click();", btn)
        if old_body:
            try:
                WebDriverWait(self.driver, 5).until(EC.staleness_of(old_body))
            except Exception:
                pass
