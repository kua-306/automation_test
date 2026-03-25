from pages.base_page import BasePage

class LoginPage(BasePage):
    def __init__(self,page):
        super().__init__(page)
        self.login_page = page.locator("#auth-section")
        self.username = self.login_page.get_by_role("textbox", name="Username")
        self.password = self.login_page.get_by_role("textbox", name="Password")
        self.login_btn = self.login_page.get_by_role("button", name="Đăng ký")
    def login(self,username,password):
        self.username.click()
        self.username.fill(username)
        self.password.click()
        self.password.fill(password)
        self.login_btn.click()
