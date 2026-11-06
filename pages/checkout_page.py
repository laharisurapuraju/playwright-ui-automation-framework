from .base_page import BasePage


class CheckoutInfoPage(BasePage):
    path = "/checkout"

    def __init__(self, page):
        super().__init__(page)
        self.first_name = page.get_by_test_id("first-name")
        self.last_name = page.get_by_test_id("last-name")
        self.postal_code = page.get_by_test_id("postal-code")
        self.continue_button = page.get_by_test_id("continue")

    def fill_and_continue(self, first: str = "", last: str = "", postal: str = ""):
        self.first_name.fill(first)
        self.last_name.fill(last)
        self.postal_code.fill(postal)
        self.continue_button.click()
        return CheckoutOverviewPage(self.page)


class CheckoutOverviewPage(BasePage):
    path = "/checkout/overview"

    def __init__(self, page):
        super().__init__(page)
        self.items = page.get_by_test_id("overview-item")
        self.subtotal = page.get_by_test_id("subtotal")
        self.tax = page.get_by_test_id("tax")
        self.total = page.get_by_test_id("total")
        self.finish_button = page.get_by_test_id("finish")

    def amounts(self) -> tuple[float, float, float]:
        return (float(self.subtotal.inner_text()), float(self.tax.inner_text()),
                float(self.total.inner_text()))

    def finish(self):
        self.finish_button.click()
        return CheckoutCompletePage(self.page)


class CheckoutCompletePage(BasePage):
    path = "/checkout/complete"

    def __init__(self, page):
        super().__init__(page)
        self.header = page.get_by_test_id("complete-header")
