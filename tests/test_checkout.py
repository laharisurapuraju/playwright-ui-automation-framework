import pytest
from playwright.sync_api import expect

from utils.config import PRODUCTS, TAX_RATE, VALID_USER


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize(
    "first, last, postal, message",
    [
        ("", "Rao", "560001", "First name is required"),
        ("Asha", "", "560001", "Last name is required"),
        ("Asha", "Rao", "", "Postal code is required"),
        ("", "", "", "First name is required"),
        ("   ", "Rao", "560001", "First name is required"),  # whitespace only
    ],
    ids=["no-first", "no-last", "no-postal", "all-empty", "whitespace-first"],
)
def test_checkout_information_validation(checkout_info, first, last, postal, message):
    checkout_info.fill_and_continue(first, last, postal)
    checkout_info.expect_error(message)
    checkout_info.expect_url_contains("/checkout")


@pytest.mark.regression
def test_overview_totals_are_calculated_correctly(inventory):
    chosen = [1, 3, 6]
    for pid in chosen:
        inventory.add_to_cart(pid)
    overview = inventory.open_cart().checkout().fill_and_continue("Asha", "Rao", "560001")

    expected_subtotal = round(sum(PRODUCTS[p][1] for p in chosen), 2)
    expected_tax = round(expected_subtotal * TAX_RATE, 2)
    subtotal, tax, total = overview.amounts()
    assert subtotal == expected_subtotal
    assert tax == expected_tax
    assert total == round(expected_subtotal + expected_tax, 2)
    expect(overview.items).to_have_count(len(chosen))


@pytest.mark.smoke
@pytest.mark.regression
def test_complete_purchase_journey(login_page):
    """End to end: login -> add two items -> checkout -> finish -> cart is empty."""
    inventory = login_page.login_as(VALID_USER)
    inventory.add_to_cart(2)
    inventory.add_to_cart(4)
    expect(inventory.cart_badge).to_have_text("2")

    overview = inventory.open_cart().checkout().fill_and_continue("Asha", "Rao", "560001")
    complete = overview.finish()

    expect(complete.header).to_have_text("Thank you for your order!")
    expect(complete.cart_badge).to_have_count(0)  # cart emptied after the order
    complete.cart_link.click()
    expect(complete.page.get_by_test_id("empty-cart")).to_be_visible()


@pytest.mark.regression
@pytest.mark.negative
def test_overview_cannot_be_reached_without_filling_information(inventory, page):
    inventory.add_to_cart(1)
    page.goto("/checkout/overview")
    page.wait_for_url("**/cart")
