import pytest
from playwright.sync_api import expect

from utils.config import PRODUCTS


@pytest.mark.regression
def test_cart_lists_the_chosen_items(inventory):
    inventory.add_to_cart(1)
    inventory.add_to_cart(5)
    cart = inventory.open_cart()
    assert sorted(cart.names()) == sorted([PRODUCTS[1][0], PRODUCTS[5][0]])
    expect(cart.items).to_have_count(2)


@pytest.mark.regression
def test_empty_cart_shows_message_and_hides_checkout(cart):
    expect(cart.empty_message).to_have_text("Your cart is empty.")
    expect(cart.checkout_button).to_have_count(0)


@pytest.mark.regression
def test_removing_item_from_cart_page(inventory):
    inventory.add_to_cart(1)
    inventory.add_to_cart(2)
    cart = inventory.open_cart()
    cart.remove(1)
    expect(cart.items).to_have_count(1)
    assert cart.names() == [PRODUCTS[2][0]]
    expect(cart.cart_badge).to_have_text("1")


@pytest.mark.regression
def test_continue_shopping_returns_to_products_with_cart_intact(inventory):
    inventory.add_to_cart(6)
    cart = inventory.open_cart()
    cart.continue_shopping.click()
    cart.expect_url_contains("/inventory")
    expect(cart.cart_badge).to_have_text("1")


@pytest.mark.regression
@pytest.mark.negative
def test_checkout_with_empty_cart_is_redirected_back(cart, page):
    page.goto("/checkout")
    page.wait_for_url("**/cart")
    expect(cart.empty_message).to_be_visible()
