import pytest
from tests.pages.login_page import LoginPage
from tests.pages.dashboard_page import DashboardPage


@pytest.mark.auth
class TestAuthentication:
    """E2E Test Suite for User Authentication and Session Management."""

    @pytest.mark.smoke
    def test_successful_login(self, driver, base_url):
        """Verify that a valid user can log in and is redirected to the dashboard."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("admin", "Admin@123")

        # Verify redirection and UI state
        assert dashboard_page.is_dashboard_displayed(), "Dashboard should be visible after successful login"
        assert dashboard_page.get_logged_in_username() == "admin", "Greeting should show logged in username 'admin'"

    def test_invalid_credentials(self, driver, base_url):
        """Verify error banner is displayed for incorrect credentials."""
        login_page = LoginPage(driver, base_url)
        login_page.open()

        login_page.login("admin", "WrongPassword!")

        assert "Invalid username or password" in login_page.get_flash_message()
        assert login_page.is_login_page_displayed(), "User should remain on the login page"

    def test_unauthenticated_dashboard_access(self, driver, base_url):
        """Verify unauthenticated user cannot directly navigate to /dashboard."""
        dashboard_page = DashboardPage(driver, base_url)
        login_page = LoginPage(driver, base_url)

        dashboard_page.open()

        # Should be redirected back to login page
        assert login_page.is_login_page_displayed()
        assert "Please log in" in login_page.get_flash_message()

    @pytest.mark.smoke
    def test_user_logout(self, driver, base_url):
        """Verify user can logout successfully and session is cleared."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("qa_tester", "Testing!2024")
        assert dashboard_page.is_dashboard_displayed()

        dashboard_page.logout()

        assert login_page.is_login_page_displayed()
        assert "successfully logged out" in login_page.get_flash_message()
