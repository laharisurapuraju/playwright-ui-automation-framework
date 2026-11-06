"""ShopDemo - a small e-commerce web app used as the system under test.

It ships inside the repo so the whole suite is self-contained and deterministic:
no third-party site can change or go offline underneath the tests.
"""
from flask import Flask, redirect, render_template, request, session, url_for
from jinja2 import DictLoader

USERS = {
    "qa_user": {"password": "Test@1234", "locked": False},
    "locked_user": {"password": "Test@1234", "locked": True},
}
PRODUCTS = [
    {"id": 1, "name": "Trail Backpack", "price": 29.99, "desc": "Water-resistant 25L daypack."},
    {"id": 2, "name": "Bike Light", "price": 9.99, "desc": "USB-rechargeable front light."},
    {"id": 3, "name": "Cotton T-Shirt", "price": 15.99, "desc": "Soft everyday tee."},
    {"id": 4, "name": "Fleece Jacket", "price": 49.99, "desc": "Warm mid-layer."},
    {"id": 5, "name": "Onesie", "price": 7.99, "desc": "Snap-closure baby onesie."},
    {"id": 6, "name": "Red T-Shirt", "price": 15.99, "desc": "Classic red tee."},
]
TAX_RATE = 0.08
BY_ID = {p["id"]: p for p in PRODUCTS}

TEMPLATES = {
    "base.html": """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>ShopDemo</title>
<style>body{font-family:Arial,sans-serif;margin:0;background:#f6f7f9}header{background:#1f3864;color:#fff;padding:12px 24px;display:flex;justify-content:space-between;align-items:center}
header a{color:#fff;margin-left:16px}main{max-width:900px;margin:24px auto;padding:0 16px}.card{background:#fff;border:1px solid #ddd;border-radius:6px;padding:12px;margin:8px 0;display:flex;justify-content:space-between;align-items:center}
.error{background:#fdecea;color:#b71c1c;padding:10px;border-radius:4px;margin:10px 0}input,select,button{padding:8px;margin:4px 0}.badge{background:#e53935;border-radius:10px;padding:2px 8px;margin-left:4px}</style></head><body>
<header><strong>ShopDemo</strong>{% if session.get('user') %}<nav>
<a href="{{ url_for('inventory') }}" data-test="nav-products">Products</a>
<a href="{{ url_for('cart') }}" data-test="cart-link">Cart{% if cart_count %}<span class="badge" data-test="cart-badge">{{ cart_count }}</span>{% endif %}</a>
<a href="{{ url_for('logout') }}" data-test="logout">Logout</a></nav>{% endif %}</header>
<main>{% block body %}{% endblock %}</main></body></html>""",
    "login.html": """{% extends "base.html" %}{% block body %}<h1>Login</h1>
{% if error %}<div class="error" data-test="error">{{ error }}</div>{% endif %}
<form method="post" action="{{ url_for('login') }}">
<div><input name="username" placeholder="Username" data-test="username"></div>
<div><input name="password" type="password" placeholder="Password" data-test="password"></div>
<button type="submit" data-test="login-button">Login</button></form>{% endblock %}""",
    "inventory.html": """{% extends "base.html" %}{% block body %}<h1 data-test="title">Products</h1>
<form method="get"><label>Sort by
<select name="sort" data-test="sort" onchange="this.form.submit()">
{% for value,label in sort_options %}<option value="{{ value }}" {% if value==sort %}selected{% endif %}>{{ label }}</option>{% endfor %}
</select></label></form>
{% for p in products %}<div class="card" data-test="product-{{ p.id }}"><div>
<strong data-test="product-name">{{ p.name }}</strong><div>{{ p.desc }}</div><div data-test="product-price">${{ '%.2f'|format(p.price) }}</div></div>
<form method="post" action="{{ url_for('toggle_item', pid=p.id) }}"><input type="hidden" name="next" value="inventory">
{% if p.id in cart %}<button data-test="remove-{{ p.id }}">Remove</button>{% else %}<button data-test="add-to-cart-{{ p.id }}">Add to cart</button>{% endif %}</form></div>{% endfor %}{% endblock %}""",
    "cart.html": """{% extends "base.html" %}{% block body %}<h1 data-test="title">Your Cart</h1>
{% if not items %}<p data-test="empty-cart">Your cart is empty.</p>{% endif %}
{% for p in items %}<div class="card" data-test="cart-item"><div><strong data-test="item-name">{{ p.name }}</strong>
<div data-test="item-price">${{ '%.2f'|format(p.price) }}</div></div>
<form method="post" action="{{ url_for('toggle_item', pid=p.id) }}"><input type="hidden" name="next" value="cart"><button data-test="remove-{{ p.id }}">Remove</button></form></div>{% endfor %}
<a href="{{ url_for('inventory') }}" data-test="continue-shopping">Continue shopping</a>
{% if items %}<a href="{{ url_for('checkout') }}" data-test="checkout"><button>Checkout</button></a>{% endif %}{% endblock %}""",
    "checkout_info.html": """{% extends "base.html" %}{% block body %}<h1 data-test="title">Checkout: Your Information</h1>
{% if error %}<div class="error" data-test="error">{{ error }}</div>{% endif %}
<form method="post"><div><input name="first_name" placeholder="First name" data-test="first-name" value="{{ form.first_name }}"></div>
<div><input name="last_name" placeholder="Last name" data-test="last-name" value="{{ form.last_name }}"></div>
<div><input name="postal_code" placeholder="Postal code" data-test="postal-code" value="{{ form.postal_code }}"></div>
<button type="submit" data-test="continue">Continue</button></form>{% endblock %}""",
    "checkout_overview.html": """{% extends "base.html" %}{% block body %}<h1 data-test="title">Checkout: Overview</h1>
{% for p in items %}<div class="card" data-test="overview-item"><span data-test="item-name">{{ p.name }}</span><span>${{ '%.2f'|format(p.price) }}</span></div>{% endfor %}
<p>Item total: $<span data-test="subtotal">{{ '%.2f'|format(subtotal) }}</span></p>
<p>Tax: $<span data-test="tax">{{ '%.2f'|format(tax) }}</span></p>
<p><strong>Total: $<span data-test="total">{{ '%.2f'|format(total) }}</span></strong></p>
<form method="post"><button data-test="finish">Finish</button></form>{% endblock %}""",
    "complete.html": """{% extends "base.html" %}{% block body %}<h1 data-test="complete-header">Thank you for your order!</h1>
<p data-test="complete-text">Your order has been dispatched.</p>
<a href="{{ url_for('inventory') }}" data-test="back-home">Back to products</a>{% endblock %}""",
}

SORTS = {
    "name_asc": ("Name (A to Z)", lambda p: p["name"]),
    "name_desc": ("Name (Z to A)", lambda p: p["name"]),
    "price_asc": ("Price (low to high)", lambda p: p["price"]),
    "price_desc": ("Price (high to low)", lambda p: p["price"]),
}


def create_app() -> Flask:
    app = Flask(__name__)
    app.secret_key = "demo-only-secret"
    app.jinja_loader = DictLoader(TEMPLATES)

    @app.context_processor
    def inject_cart_count():
        return {"cart_count": len(session.get("cart", []))}

    def logged_in() -> bool:
        return "user" in session

    @app.get("/")
    def login_page():
        error = "You can only access this page when logged in" if request.args.get("error") == "auth" else None
        return render_template("login.html", error=error)

    @app.post("/")
    def login():
        username, password = request.form.get("username", ""), request.form.get("password", "")
        error = None
        if not username:
            error = "Username is required"
        elif not password:
            error = "Password is required"
        elif username not in USERS or USERS[username]["password"] != password:
            error = "Username and password do not match any user"
        elif USERS[username]["locked"]:
            error = "This user has been locked out"
        if error:
            return render_template("login.html", error=error), 401
        session.clear()
        session["user"] = username
        session["cart"] = []
        return redirect(url_for("inventory"))

    @app.get("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login_page"))

    @app.get("/inventory")
    def inventory():
        if not logged_in():
            return redirect(url_for("login_page", error="auth"))
        sort = request.args.get("sort", "name_asc")
        sort = sort if sort in SORTS else "name_asc"
        products = sorted(PRODUCTS, key=SORTS[sort][1], reverse=sort.endswith("desc"))
        return render_template(
            "inventory.html", products=products, sort=sort, cart=session.get("cart", []),
            sort_options=[(k, v[0]) for k, v in SORTS.items()],
        )

    @app.post("/cart/toggle/<int:pid>")
    def toggle_item(pid: int):
        if not logged_in():
            return redirect(url_for("login_page", error="auth"))
        cart = session.get("cart", [])
        if pid in BY_ID:
            cart.remove(pid) if pid in cart else cart.append(pid)
        session["cart"] = cart
        return redirect(url_for("cart" if request.form.get("next") == "cart" else "inventory"))

    @app.get("/cart")
    def cart():
        if not logged_in():
            return redirect(url_for("login_page", error="auth"))
        return render_template("cart.html", items=[BY_ID[i] for i in session.get("cart", [])])

    @app.route("/checkout", methods=["GET", "POST"])
    def checkout():
        if not logged_in():
            return redirect(url_for("login_page", error="auth"))
        if not session.get("cart"):
            return redirect(url_for("cart"))
        form = {"first_name": "", "last_name": "", "postal_code": ""}
        if request.method == "POST":
            form = {k: request.form.get(k, "").strip() for k in form}
            error = next(
                (msg for key, msg in [("first_name", "First name is required"),
                                      ("last_name", "Last name is required"),
                                      ("postal_code", "Postal code is required")] if not form[key]),
                None,
            )
            if error:
                return render_template("checkout_info.html", error=error, form=form), 400
            session["checkout"] = form
            return redirect(url_for("overview"))
        return render_template("checkout_info.html", error=None, form=form)

    @app.route("/checkout/overview", methods=["GET", "POST"])
    def overview():
        if not logged_in():
            return redirect(url_for("login_page", error="auth"))
        if not session.get("cart") or not session.get("checkout"):
            return redirect(url_for("cart"))
        if request.method == "POST":
            session["cart"] = []
            session.pop("checkout", None)
            return redirect(url_for("complete"))
        items = [BY_ID[i] for i in session["cart"]]
        subtotal = round(sum(p["price"] for p in items), 2)
        tax = round(subtotal * TAX_RATE, 2)
        return render_template("checkout_overview.html", items=items, subtotal=subtotal,
                               tax=tax, total=round(subtotal + tax, 2))

    @app.get("/checkout/complete")
    def complete():
        if not logged_in():
            return redirect(url_for("login_page", error="auth"))
        return render_template("complete.html")

    return app


if __name__ == "__main__":
    create_app().run(port=5000, debug=False)
