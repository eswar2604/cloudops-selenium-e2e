import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-12345")

# In-memory mock database
USERS = {
    "admin": "Admin@123",
    "qa_tester": "Testing!2024",
    "demo_user": "Password123"
}

INITIAL_INVENTORY = [
    {"id": 1, "name": "Cloud Server Instance (t3.medium)", "sku": "SRV-001", "category": "Compute", "quantity": 12, "price": 45.50, "status": "In Stock"},
    {"id": 2, "name": "Managed PostgreSQL Database", "sku": "DB-002", "category": "Database", "quantity": 5, "price": 120.00, "status": "In Stock"},
    {"id": 3, "name": "SSL / TLS Wildcard Certificate", "sku": "SEC-003", "category": "Security", "quantity": 0, "price": 89.99, "status": "Out of Stock"},
    {"id": 4, "name": "CI/CD Pipeline Runner Node", "sku": "DEV-004", "category": "DevOps", "quantity": 8, "price": 60.00, "status": "In Stock"},
]

inventory_db = list(INITIAL_INVENTORY)
item_id_seq = 5


@app.route("/")
def index():
    if "user" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if "user" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "danger")
            return render_template("login.html", username=username)

        if username in USERS and USERS[username] == password:
            session["user"] = username
            flash(f"Welcome back, {username}! Login successful.", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password.", "danger")
            return render_template("login.html", username=username)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("You have been successfully logged out.", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    search_query = request.args.get("q", "").strip().lower()
    category_filter = request.args.get("category", "").strip()

    filtered_items = inventory_db
    if search_query:
        filtered_items = [
            item for item in filtered_items
            if search_query in item["name"].lower() or search_query in item["sku"].lower()
        ]

    if category_filter and category_filter != "All":
        filtered_items = [
            item for item in filtered_items
            if item["category"] == category_filter
        ]

    total_items = len(inventory_db)
    in_stock_items = sum(1 for item in inventory_db if item["quantity"] > 0)
    out_of_stock_items = total_items - in_stock_items

    return render_template(
        "dashboard.html",
        user=session["user"],
        items=filtered_items,
        total_items=total_items,
        in_stock_items=in_stock_items,
        out_of_stock_items=out_of_stock_items,
        search_query=search_query,
        selected_category=category_filter or "All"
    )


@app.route("/inventory/add", methods=["POST"])
def add_item():
    if "user" not in session:
        return redirect(url_for("login"))

    global item_id_seq
    name = request.form.get("name", "").strip()
    sku = request.form.get("sku", "").strip().upper()
    category = request.form.get("category", "Compute")
    quantity_raw = request.form.get("quantity", "0")
    price_raw = request.form.get("price", "0.0")

    if not name or not sku:
        flash("Item name and SKU are mandatory fields.", "danger")
        return redirect(url_for("dashboard"))

    # Check for duplicate SKU
    if any(item["sku"] == sku for item in inventory_db):
        flash(f"An item with SKU '{sku}' already exists.", "danger")
        return redirect(url_for("dashboard"))

    try:
        quantity = max(0, int(quantity_raw))
        price = max(0.0, float(price_raw))
    except ValueError:
        flash("Invalid quantity or price format.", "danger")
        return redirect(url_for("dashboard"))

    new_item = {
        "id": item_id_seq,
        "name": name,
        "sku": sku,
        "category": category,
        "quantity": quantity,
        "price": round(price, 2),
        "status": "In Stock" if quantity > 0 else "Out of Stock"
    }
    inventory_db.append(new_item)
    item_id_seq += 1

    flash(f"Resource '{name}' (SKU: {sku}) added successfully!", "success")
    return redirect(url_for("dashboard"))


@app.route("/inventory/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if "user" not in session:
        return redirect(url_for("login"))

    global inventory_db
    target_item = next((item for item in inventory_db if item["id"] == item_id), None)
    if target_item:
        inventory_db = [item for item in inventory_db if item["id"] != item_id]
        flash(f"Resource '{target_item['name']}' removed from inventory.", "info")
    else:
        flash("Item not found.", "warning")

    return redirect(url_for("dashboard"))


@app.route("/inventory/reset", methods=["POST"])
def reset_inventory():
    if "user" not in session:
        return redirect(url_for("login"))

    global inventory_db, item_id_seq
    inventory_db = list(INITIAL_INVENTORY)
    item_id_seq = 5
    flash("Inventory reset to default mock state.", "info")
    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return jsonify({
        "status": "healthy",
        "service": "devops-portal-app",
        "inventory_count": len(inventory_db)
    }), 200


@app.route("/api/inventory")
def api_inventory():
    return jsonify(inventory_db), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
