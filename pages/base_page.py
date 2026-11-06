"""Shared behaviour for every page object."""
import re

from playwright.sync_api import Locator, Page, expect


class BasePage:
    path = "/"

    def __init__(self, page: Page) -> None:
        self.page = page
        self.cart_badge = page.get_by_test_id("cart-badge")
        self.cart_link = page.get_by_test_id("cart-link")
        self.logout_link = page.get_by_test_id("logout")
        self.error = page.get_by_test_id("error")
        self.title = page.get_by_test_id("title")

    def open(self):
        self.page.goto(self.path)
        return self

    def by_test(self, test_id: str) -> Locator:
        return self.page.get_by_test_id(test_id)

    def expect_url_contains(self, fragment: str) -> None:
        """Assert the URL path ends with `fragment` (a query string is allowed)."""
        expect(self.page).to_have_url(re.compile(re.escape(fragment) + r"(\?.*)?$"))

    def expect_error(self, message: str) -> None:
        expect(self.error).to_have_text(message)

    def cart_count(self) -> int:
        """Items shown on the cart badge (0 when the badge is hidden)."""
        return int(self.cart_badge.inner_text()) if self.cart_badge.count() else 0

    def logout(self) -> None:
        self.logout_link.click()
