"""Central test configuration and test data."""
import os

TIMEOUT_MS = int(os.getenv("UI_TIMEOUT_MS", "5000"))

VALID_USER = {"username": "qa_user", "password": "Test@1234"}
LOCKED_USER = {"username": "locked_user", "password": "Test@1234"}

# Product catalogue as shown on the page (name, price)
PRODUCTS = {
    1: ("Trail Backpack", 29.99),
    2: ("Bike Light", 9.99),
    3: ("Cotton T-Shirt", 15.99),
    4: ("Fleece Jacket", 49.99),
    5: ("Onesie", 7.99),
    6: ("Red T-Shirt", 15.99),
}
TAX_RATE = 0.08
