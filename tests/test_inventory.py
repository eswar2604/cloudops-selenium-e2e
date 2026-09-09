import pytest
from selenium.webdriver.common.by import By
from tests.pages.login_page import LoginPage
from tests.pages.dashboard_page import DashboardPage


@pytest.mark.inventory
class TestInventoryManagement:
    """E2E Test Suite for Cloud Infrastructure Inventory Operations."""

    @pytest.fixture(autouse=True)
    def setup_authenticated_session(self, driver, base_url):
        """Automatically log in before running inventory tests and reset state after."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("admin", "Admin@123")
        assert dashboard_page.is_dashboard_displayed(), "Dashboard should be visible after login"

        yield dashboard_page

        # Clean up / reset state after each test
        try:
            dashboard_page.reset_inventory()
        except Exception:
            pass

    @pytest.mark.smoke
    def test_add_new_cloud_resource(self, driver, base_url):
        """Verify adding a new infrastructure item updates the inventory table and metric stats."""
        dashboard_page = DashboardPage(driver, base_url)

        initial_count = dashboard_page.get_total_stat_count()
        test_sku = "TEST-NODE-999"
        test_name = "Edge Gateway Cluster"

        dashboard_page.add_resource(
            name=test_name,
            sku=test_sku,
            category="Compute",
            quantity=3,
            price=199.99
        )

        assert "added successfully" in dashboard_page.get_flash_message()

        # Verify resource row is visible in table
        row = dashboard_page.get_row_by_sku(test_sku)
        assert row is not None, f"Item with SKU {test_sku} should exist in table"
        assert test_name in row.text

        # Verify total counter incremented
        new_count = dashboard_page.get_total_stat_count()
        assert new_count == initial_count + 1

    def test_add_duplicate_sku_validation(self, driver, base_url):
        """Verify adding a resource with an already existing SKU triggers a validation error."""
        dashboard_page = DashboardPage(driver, base_url)

        existing_sku = "SRV-001"
        initial_count = dashboard_page.get_total_stat_count()

        dashboard_page.submit_add_resource_form(
            name="Duplicate Server Instance",
            sku=existing_sku,
            category="Compute",
            quantity=1,
            price=50.0
        )

        flash_msg = dashboard_page.get_flash_message()
        assert f"An item with SKU '{existing_sku}' already exists." in flash_msg
        assert dashboard_page.get_total_stat_count() == initial_count

    def test_add_resource_missing_mandatory_fields(self, driver, base_url):
        """Verify attempting to add resource without name or SKU displays an error."""
        dashboard_page = DashboardPage(driver, base_url)

        dashboard_page.submit_add_resource_form(
            name="",
            sku="",
            category="Compute",
            quantity=1,
            price=50.0
        )

        flash_msg = dashboard_page.get_flash_message()
        assert "Item name and SKU are mandatory fields" in flash_msg

    def test_search_resources(self, driver, base_url):
        """Verify searching by SKU or name filters the table dynamically."""
        dashboard_page = DashboardPage(driver, base_url)

        # Search for known item
        dashboard_page.search("PostgreSQL")
        row = dashboard_page.get_row_by_sku("DB-002")
        assert row is not None, "PostgreSQL item should be displayed"
        assert "PostgreSQL" in row.text

        # Non-matching search query
        dashboard_page.search("NonExistentResourceXYZ")
        assert dashboard_page.is_visible(dashboard_page.NO_ITEMS_MESSAGE)

    def test_filter_by_category(self, driver, base_url):
        """Verify filtering by category shows only matching resources."""
        dashboard_page = DashboardPage(driver, base_url)

        # Filter by Database
        dashboard_page.filter_by_category("Database")
        rows = driver.find_elements(By.CSS_SELECTOR, "#inventory-table-body tr")
        assert len(rows) >= 1
        for r in rows:
            assert "Database" in r.text

        # Filter by Security
        dashboard_page.filter_by_category("Security")
        sec_row = dashboard_page.get_row_by_sku("SEC-003")
        assert sec_row is not None
        assert "Security" in sec_row.text

    def test_delete_resource(self, driver, base_url):
        """Verify deleting an existing resource removes it from the inventory table and decrements count."""
        dashboard_page = DashboardPage(driver, base_url)

        initial_count = dashboard_page.get_total_stat_count()
        target_sku = "SRV-001"

        dashboard_page.delete_resource_by_sku(target_sku)

        assert dashboard_page.get_row_by_sku(target_sku) is None, f"Item {target_sku} should disappear from table"
        assert dashboard_page.get_total_stat_count() == initial_count - 1

    def test_reset_inventory(self, driver, base_url):
        """Verify resetting inventory restores the default initial state."""
        dashboard_page = DashboardPage(driver, base_url)

        # Delete an item first to change state
        dashboard_page.delete_resource_by_sku("SRV-001")
        assert dashboard_page.get_row_by_sku("SRV-001") is None

        # Reset inventory
        dashboard_page.reset_inventory()

        assert "Inventory reset to default mock state" in dashboard_page.get_flash_message()
        assert dashboard_page.get_row_by_sku("SRV-001") is not None
        assert dashboard_page.get_total_stat_count() == 4
