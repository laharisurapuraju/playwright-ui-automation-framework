# Playwright UI Automation Framework

An end-to-end **UI test automation framework** built with **Python, Playwright and Pytest** using the
**Page Object Model**. It tests *ShopDemo*, a small e-commerce web app (login, product list, cart,
checkout) that is **bundled in this repo**, so the whole suite is self-contained and gives the same
result every run, locally and in CI.

**32 automated tests** covering login, product browsing and sorting, cart behaviour, checkout
validation, price calculation and a full purchase journey.

## Why it is built this way

| Practice | How it is done here |
|---|---|
| Page Object Model | One class per page in `pages/`; tests never contain selectors |
| Stable locators | The app exposes `data-test` attributes; Playwright is configured to use them (`get_by_test_id`) |
| Test isolation | Every test gets a fresh browser context (no shared cookies, cart or login) |
| Auto-waiting assertions | Playwright `expect(...)` retries until the condition is met, with no `sleep()` calls |
| Data-driven tests | `pytest.mark.parametrize` for invalid logins, checkout validation and sorting |
| Test selection | Markers: `smoke` (4 fastest critical checks), `regression` (full suite), `negative` |
| Failure evidence | A full-page screenshot is taken on failure and embedded in the HTML report |
| Reporting | Self-contained HTML report in `reports/report.html` |
| CI/CD | GitHub Actions runs the regression suite on every push and uploads the report |

## Project structure

```
demo_app/shop.py        the web app under test (Flask)
pages/                  page objects: base, login, inventory, cart, checkout
tests/conftest.py       fixtures: live server, browser, page, screenshot-on-failure hook
tests/test_*.py         test files by feature
utils/config.py         test data and settings
.github/workflows/      CI pipeline
```

## Setup and run

```bash
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m playwright install chromium

pytest                          # everything (32 tests)
pytest -m smoke                 # quick critical-path check
pytest -m negative              # error-handling tests only
pytest --headed --slowmo 500    # watch the browser work
pytest --browser-name firefox   # other browsers (after: playwright install firefox)
```

Open `reports/report.html` after a run. Screenshots of failed tests are in `reports/screenshots/`.

To explore the app by hand: `python -m demo_app.shop`, then open http://127.0.0.1:5000
(user `qa_user`, password `Test@1234`).

## What is tested

| Area | Examples | Tests |
|---|---|---|
| Login | valid login; empty username/password; wrong password; unknown user; locked user; protected pages redirect when logged out; logout ends the session | 11 |
| Products | catalogue and prices; four sort orders; cart badge add/remove; selection survives sorting | 8 |
| Cart | items listed correctly; empty-cart message; remove item; continue shopping; empty-cart checkout is blocked | 5 |
| Checkout | required-field validation (incl. whitespace-only); subtotal, 8% tax and total; overview cannot be skipped; full purchase journey | 8 |

## Test approach

- **Risk first:** login and checkout are the revenue-critical journeys, so they get the most
  negative and boundary coverage and form the `smoke` set.
- **Business rules are asserted with computed expectations**, for example the total is checked
  against `subtotal + 8% tax` calculated independently in the test.
- **Negative and security-minded checks:** direct URL access without login, skipping checkout
  steps and whitespace-only input.
- **Maintainability:** if a page changes, only its page object changes.

## Possible next steps

- Visual regression snapshots
- Run tests in parallel (`pytest-xdist`)
- Run in Firefox and WebKit in the CI matrix
- Accessibility checks with axe-core
