from .base_page import BasePage


class CartPage(BasePage):
    path = "/cart"

    def __init__(self, page):
        super().__init__(page)
        self.items = page.get_by_test_id("cart-item")
        self.item_names = page.get_by_test_id("item-name")
        self.empty_message = page.get_by_test_id("empty-cart")
        self.continue_shopping = page.get_by_test_id("continue-shopping")
        self.checkout_button = page.get_by_test_id("checkout")

    def names(self) -> list[str]:
        return self.item_names.all_inner_texts()

    def remove(self, product_id: int) -> None:
        self.by_test(f"remove-{product_id}").click()

    def checkout(self):
        from .checkout_page import CheckoutInfoPage

        self.checkout_button.click()
        return CheckoutInfoPage(self.page)
