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

    @pytest.mark.smoke
    def test_login_new_user_arno(self, driver, base_url):
        """Verify newly added user 'arno' can log in and is greeted correctly."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("arno", "dorian")

        assert dashboard_page.is_dashboard_displayed(), "Dashboard should be visible for user arno"
        assert dashboard_page.get_logged_in_username() == "arno", "Greeting should display 'arno'"

    def test_login_demo_user(self, driver, base_url):
        """Verify demo_user credentials grant dashboard access."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("demo_user", "Password123")

        assert dashboard_page.is_dashboard_displayed()
        assert dashboard_page.get_logged_in_username() == "demo_user"

    def test_login_nonexistent_user(self, driver, base_url):
        """Verify error message is displayed when attempting login with unknown user."""
        login_page = LoginPage(driver, base_url)
        login_page.open()

        login_page.login("ghost_user_99", "RandomSecret#1")

        assert "Invalid username or password" in login_page.get_flash_message()
        assert login_page.is_login_page_displayed(), "User should stay on login page"

    def test_login_empty_credentials_server_validation(self, driver, base_url):
        """Verify submitting empty credentials triggers backend validation error."""
        login_page = LoginPage(driver, base_url)
        login_page.open()

        login_page.submit_bypassing_html5_validation("", "")

        assert "Username and password are required" in login_page.get_flash_message()
        assert login_page.is_login_page_displayed()

    def test_login_username_whitespace_handling(self, driver, base_url):
        """Verify usernames with leading and trailing whitespaces are trimmed and accepted."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("  admin  ", "Admin@123")

        assert dashboard_page.is_dashboard_displayed()
        assert dashboard_page.get_logged_in_username() == "admin"

    def test_authenticated_user_login_redirect(self, driver, base_url):
        """Verify an already authenticated user visiting /login is redirected to /dashboard."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        login_page.open()
        login_page.login("admin", "Admin@123")
        assert dashboard_page.is_dashboard_displayed()

        # Attempt to access /login directly while session is active
        login_page.open()

        assert dashboard_page.is_dashboard_displayed()
        assert "/dashboard" in driver.current_url

    def test_root_url_redirection(self, driver, base_url):
        """Verify root URL (/) redirects to /login unauthenticated, and /dashboard when authenticated."""
        login_page = LoginPage(driver, base_url)
        dashboard_page = DashboardPage(driver, base_url)

        # 1. Unauthenticated access to /
        login_page.open_root()
        assert login_page.is_login_page_displayed()
        assert "/login" in driver.current_url

        # 2. Login to create session
        login_page.login("admin", "Admin@123")
        assert dashboard_page.is_dashboard_displayed()

        # 3. Authenticated access to /
        login_page.open_root()
        assert dashboard_page.is_dashboard_displayed()
        assert "/dashboard" in driver.current_url
