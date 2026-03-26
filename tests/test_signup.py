import pytest
from playwright.sync_api import Page, expect
from pages.signup_page import SignupPage

def test_successful_signup(page: Page):
    """
    Test case: Đăng ký thành công với user 'account_1' và pass '123456'.
    """
    signup_page = SignupPage(page)
    
    # 1. Navigate to the signup page
    signup_page.navigate()
    
    # 2. Define test data
    username = "account_1"
    password = "123456"
    
    # 3. Perform the signup action
    signup_page.signup(username, password)
    
    # 4. Assert successful registration
    # This assertion assumes that after a successful registration,
    # a visible text "Đăng ký thành công!" appears on the page.
    #
    # IMPORTANT: The actual success indicator might vary:
    # - If an alert/dialog appears, use page.on("dialog", ...) to handle it.
    # - If the page redirects, assert the new URL using expect(page).to_have_url(...).
    # - If a specific HTML element (e.g., a div) shows the message,
    #   update `success_message_locator` in `SignupPage` to target that element.
    expect(signup_page.get_success_message_locator()).to_be_visible()