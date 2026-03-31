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
    
    expect(signup_page.get_success_message_locator()).to_be_visible()