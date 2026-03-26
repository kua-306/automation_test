from playwright.sync_api import Page, Locator
import os

class SignupPage:
    """
    Page Object Model for the signup functionality.
    """
    def __init__(self, page: Page):
        self.page = page
        # Using file:/// for local file paths
        self.base_url = f"file://{os.getcwd()}/index.html"

        # Locators for elements
        self.username_input: Locator = page.locator("#username")
        self.password_input: Locator = page.locator("#password")
        # Locator for the 'Đăng ký' button, identified by its text
        self.signup_button: Locator = page.locator("button:has-text('Đăng ký')")
        
        # Assuming a success message will appear on the page with this text.
        # This locator might need adjustment based on the actual HTML structure
        # (e.g., a specific div with an ID or class for success messages).
        self.success_message_locator: Locator = page.locator("text=Đăng ký thành công!")

    def navigate(self):
        """Navigates to the signup page."""
        self.page.goto(self.base_url)

    def signup(self, username: str, password: str):
        """
        Fills the signup form and clicks the 'Đăng ký' button.
        """
        self.username_input.fill(username)
        self.password_input.fill(password)
        self.signup_button.click()

    def get_success_message_locator(self) -> Locator:
        """
        Returns the locator for the assumed success message element.
        """
        return self.success_message_locator