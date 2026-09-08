import pytest
import time
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
        assert dashboard_page.is_dashboard_displayed()

        yield dashboard_page

        # Clean up / reset state
        try:
            dashboard_page.reset_inventory()
        except Exception:
            pass

    @pytest.mark.smoke
    def test_add_new_cloud_resource(self, driver, base_url):
        """Verify adding a new infrastructure item updates table and metrics."""
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

    def test_search_and_filter_resources(self, driver, base_url):
        """Verify searching by SKU or name filters the table dynamically."""
        dashboard_page = DashboardPage(driver, base_url)

        dashboard_page.search("PostgreSQL")
        row = dashboard_page.get_row_by_sku("DB-002")
        assert row is not None
        assert "PostgreSQL" in row.text

        # Non-matching search query
        dashboard_page.search("NonExistentItem999")
        assert dashboard_page.is_visible(dashboard_page.NO_ITEMS_MESSAGE)

    def test_delete_resource(self, driver, base_url):
        """Verify deleting an existing resource removes it from the inventory."""
        dashboard_page = DashboardPage(driver, base_url)

        initial_count = dashboard_page.get_total_stat_count()
        target_sku = "SRV-001"

        # Ensure item exists initially
        dashboard_page.delete_resource_by_sku(target_sku)

        assert dashboard_page.get_row_by_sku(target_sku) is None, f"Item {target_sku} should disappear from table"
        assert dashboard_page.get_total_stat_count() == initial_count - 1
