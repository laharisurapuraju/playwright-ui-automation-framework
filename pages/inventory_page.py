from .base_page import BasePage


class InventoryPage(BasePage):
    path = "/inventory"

    def __init__(self, page):
        super().__init__(page)
        self.sort_select = page.get_by_test_id("sort")
        self.product_names = page.get_by_test_id("product-name")
        self.product_prices = page.get_by_test_id("product-price")

    def names(self) -> list[str]:
        return self.product_names.all_inner_texts()

    def prices(self) -> list[float]:
        return [float(t.replace("$", "")) for t in self.product_prices.all_inner_texts()]

    def sort_by(self, value: str) -> None:
        self.sort_select.select_option(value)
        self.page.wait_for_url(f"**sort={value}")

    def add_to_cart(self, product_id: int) -> None:
        self.by_test(f"add-to-cart-{product_id}").click()

    def remove_from_cart(self, product_id: int) -> None:
        self.by_test(f"remove-{product_id}").click()

    def open_cart(self):
        from .cart_page import CartPage

        self.cart_link.click()
        return CartPage(self.page)
