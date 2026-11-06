"""Fixtures: live demo server, browser, page objects, screenshot-on-failure."""
import base64
import socket
import threading
from pathlib import Path

import pytest
from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from demo_app.shop import create_app
from pages.cart_page import CartPage
from pages.checkout_page import CheckoutInfoPage
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from utils.config import TIMEOUT_MS, VALID_USER

SCREENSHOT_DIR = Path("reports/screenshots")


def pytest_addoption(parser):
    parser.addoption("--browser-name", default="chromium",
                     choices=["chromium", "firefox", "webkit"], help="browser to run the tests in")
    parser.addoption("--headed", action="store_true", help="show the browser window")
    parser.addoption("--slowmo", type=int, default=0, help="slow every action by N ms")


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="session")
def base_url():
    """Start the demo app on a free port for the whole test session."""
    port = _free_port()
    server = make_server("127.0.0.1", port, create_app(), threaded=True)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{port}"
    server.shutdown()


@pytest.fixture(scope="session")
def browser(request):
    with sync_playwright() as pw:
        pw.selectors.set_test_id_attribute("data-test")  # our apps expose data-test hooks
        launcher = getattr(pw, request.config.getoption("--browser-name"))
        instance = launcher.launch(
            headless=not request.config.getoption("--headed"),
            slow_mo=request.config.getoption("--slowmo"),
        )
        yield instance
        instance.close()


@pytest.fixture()
def page(browser, base_url):
    """A fresh, isolated browser context per test: no shared cookies or cart."""
    context = browser.new_context(base_url=base_url, viewport={"width": 1280, "height": 800})
    context.set_default_timeout(TIMEOUT_MS)
    expect.set_options(timeout=TIMEOUT_MS)
    page = context.new_page()
    yield page
    context.close()


# ---- page-object fixtures -------------------------------------------------
@pytest.fixture()
def login_page(page):
    return LoginPage(page).open()


@pytest.fixture()
def inventory(login_page) -> InventoryPage:
    """Logged-in user sitting on the product list."""
    return login_page.login_as(VALID_USER)


@pytest.fixture()
def cart(inventory) -> CartPage:
    return inventory.open_cart()


@pytest.fixture()
def checkout_info(inventory) -> CheckoutInfoPage:
    """Logged in with one item in the cart, on the 'your information' step."""
    inventory.add_to_cart(1)
    return inventory.open_cart().checkout()


# ---- failure evidence -----------------------------------------------------
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    if report.when != "call" or not report.failed or "page" not in item.funcargs:
        return
    SCREENSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SCREENSHOT_DIR / f"{item.name.replace('/', '_')}.png"
    item.funcargs["page"].screenshot(path=str(path), full_page=True)
    try:
        from pytest_html import extras

        encoded = base64.b64encode(path.read_bytes()).decode()
        report.extras = getattr(report, "extras", []) + [extras.png(encoded, "Failure screenshot")]
    except ImportError:
        pass
