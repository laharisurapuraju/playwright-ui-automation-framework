import pytest
from playwright.sync_api import expect

from utils.config import PRODUCTS


@pytest.mark.smoke
@pytest.mark.regression
def test_all_products_are_listed_with_correct_prices(inventory):
    expected = sorted(PRODUCTS.values())  # default sort is name A-Z
    assert inventory.names() == [name for name, _ in expected]
    assert inventory.prices() == [price for _, price in expected]


@pytest.mark.regression
@pytest.mark.parametrize(
    "option, key, reverse",
    [("name_asc", lambda p: p[0], False), ("name_desc", lambda p: p[0], True),
     ("price_asc", lambda p: p[1], False), ("price_desc", lambda p: p[1], True)],
)
def test_sorting(inventory, option, key, reverse):
    inventory.sort_by(option)
    shown = list(zip(inventory.names(), inventory.prices()))
    assert [key(item) for item in shown] == sorted((key(i) for i in shown), reverse=reverse)


@pytest.mark.smoke
@pytest.mark.regression
def test_adding_items_updates_cart_badge(inventory):
    expect(inventory.cart_badge).to_have_count(0)  # empty cart shows no badge
    inventory.add_to_cart(1)
    expect(inventory.cart_badge).to_have_text("1")
    inventory.add_to_cart(2)
    expect(inventory.cart_badge).to_have_text("2")


@pytest.mark.regression
def test_removing_item_updates_badge_and_button(inventory):
    inventory.add_to_cart(3)
    expect(inventory.by_test("remove-3")).to_be_visible()
    inventory.remove_from_cart(3)
    expect(inventory.cart_badge).to_have_count(0)
    expect(inventory.by_test("add-to-cart-3")).to_be_visible()


@pytest.mark.regression
def test_cart_selection_survives_re_sorting(inventory):
    inventory.add_to_cart(4)
    inventory.sort_by("price_desc")
    expect(inventory.by_test("remove-4")).to_be_visible()
    assert inventory.cart_count() == 1
