import pytest
from playwright.sync_api import expect

from utils.config import LOCKED_USER, VALID_USER


@pytest.mark.smoke
@pytest.mark.regression
def test_valid_user_reaches_product_list(login_page):
    inventory = login_page.login_as(VALID_USER)
    inventory.expect_url_contains("/inventory")
    expect(inventory.title).to_have_text("Products")


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize(
    "username, password, message",
    [
        ("", "Test@1234", "Username is required"),
        ("qa_user", "", "Password is required"),
        ("qa_user", "wrong-password", "Username and password do not match any user"),
        ("nobody", "Test@1234", "Username and password do not match any user"),
        (LOCKED_USER["username"], LOCKED_USER["password"], "This user has been locked out"),
    ],
    ids=["no-username", "no-password", "wrong-password", "unknown-user", "locked-user"],
)
def test_invalid_login_shows_error(login_page, username, password, message):
    login_page.login(username, password)
    login_page.expect_error(message)
    login_page.expect_url_contains("/")
    expect(login_page.logout_link).to_have_count(0)  # still logged out


@pytest.mark.regression
@pytest.mark.negative
@pytest.mark.parametrize("path", ["/inventory", "/cart", "/checkout", "/checkout/complete"])
def test_protected_pages_redirect_to_login(page, path):
    page.goto(path)
    expect(page.get_by_test_id("login-button")).to_be_visible()
    expect(page.get_by_test_id("error")).to_have_text("You can only access this page when logged in")


@pytest.mark.regression
def test_logout_ends_the_session(inventory, page):
    inventory.logout()
    expect(page.get_by_test_id("login-button")).to_be_visible()
    page.goto("/inventory")  # back button / direct URL must not work any more
    expect(page.get_by_test_id("login-button")).to_be_visible()
