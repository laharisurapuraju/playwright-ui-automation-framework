from .base_page import BasePage
from .inventory_page import InventoryPage


class LoginPage(BasePage):
    path = "/"

    def __init__(self, page):
        super().__init__(page)
        self.username = page.get_by_test_id("username")
        self.password = page.get_by_test_id("password")
        self.login_button = page.get_by_test_id("login-button")

    def login(self, username: str, password: str) -> None:
        self.username.fill(username)
        self.password.fill(password)
        self.login_button.click()

    def login_as(self, user: dict) -> InventoryPage:
        self.login(user["username"], user["password"])
        return InventoryPage(self.page)
